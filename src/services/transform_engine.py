import hashlib
import io
import math
import re
from dataclasses import dataclass
from typing import Any, Tuple

from PIL import Image as PILImage, ImageColor, ImageOps, UnidentifiedImageError

# Map Pillow format identifiers to canonical (extension, mime_type)
SUPPORTED_IMAGE_FORMATS: dict[str, tuple[str, str]] = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
    "BMP": (".bmp", "image/bmp"),
}


class TransformError(Exception):
    """Base exception for transformation engine failures."""
    pass


class InvalidTransformParamsError(TransformError):
    """Raised when parameters fail boundary or schema validation."""
    pass


@dataclass(frozen=True)
class TransformedImageResult:
    data: bytes
    format: str
    extension: str
    mime_type: str
    width: int
    height: int
    file_size: int
    checksum: str


HEX_COLOR_REGEX = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8}|[A-Fa-f0-9]{3})$")


def _parse_fill_color(color_str: str, has_alpha: bool) -> Tuple[int, ...]:
    """Parse hex color string into RGBA or RGB tuple."""
    if not isinstance(color_str, str) or not HEX_COLOR_REGEX.match(color_str):
        raise InvalidTransformParamsError(f"Invalid hex fill_color: '{color_str}'. Example: '#FFFFFF'.")

    try:
        rgba = ImageColor.getcolor(color_str, "RGBA")
    except ValueError as exc:
        raise InvalidTransformParamsError(f"Invalid fill_color: {exc}") from exc

    if has_alpha:
        return rgba
    return rgba[:3]


def _parse_affine_matrix(params: dict[str, Any]) -> Tuple[float, float, float, float, float, float]:
    """Parse affine transformation coefficients [a, b, c, d, e, f]."""
    if "matrix" in params:
        m = params["matrix"]
        if not isinstance(m, (list, tuple)) or len(m) != 6:
            raise InvalidTransformParamsError("Affine 'matrix' must be a list or tuple of 6 numbers [a, b, c, d, e, f].")
        try:
            return tuple(float(v) for v in m)  # type: ignore[return-value]
        except (ValueError, TypeError) as exc:
            raise InvalidTransformParamsError("Affine matrix elements must be numbers.") from exc

    if any(k in params for k in ("a", "b", "c", "d", "e", "f")):
        try:
            a = float(params.get("a", 1.0))
            b = float(params.get("b", 0.0))
            c = float(params.get("c", 0.0))
            d = float(params.get("d", 0.0))
            e = float(params.get("e", 1.0))
            f = float(params.get("f", 0.0))
            return (a, b, c, d, e, f)
        except (ValueError, TypeError) as exc:
            raise InvalidTransformParamsError("Affine parameters a, b, c, d, e, f must be numbers.") from exc

    if any(k in params for k in ("scale_x", "scale_y", "rotation", "shear_x", "shear_y", "translation_x", "translation_y")):
        try:
            sx = float(params.get("scale_x", 1.0))
            sy = float(params.get("scale_y", 1.0))
            angle = float(params.get("rotation", 0.0))
            shx = float(params.get("shear_x", 0.0))
            shy = float(params.get("shear_y", 0.0))
            tx = float(params.get("translation_x", 0.0))
            ty = float(params.get("translation_y", 0.0))
        except (ValueError, TypeError) as exc:
            raise InvalidTransformParamsError("Decomposed affine parameters must be numbers.") from exc

        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        m00 = sx
        m01 = shx * sy
        m10 = shy * sx
        m11 = sy
        a = cos_a * m00 - sin_a * m10
        b = cos_a * m01 - sin_a * m11
        d = sin_a * m00 + cos_a * m10
        e = sin_a * m01 + cos_a * m11
        c = tx
        f = ty
        return (a, b, c, d, e, f)

    return (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)


class TransformEngine:
    """
    Stateless processing engine for geometric image transformations.
    Converts raw image bytes + operation + params into TransformedImageResult.
    """

    MAX_DIMENSION = 8192
    MIN_DIMENSION = 16

    @classmethod
    def compute_output_dimensions(
        cls,
        width: int,
        height: int,
        operation: str,
        params: dict[str, Any],
    ) -> Tuple[int, int]:
        """
        Pure math helper that calculates exact output bounding-box dimensions
        using arithmetic alone without opening or decoding pixel buffers.
        """
        if width <= 0 or height <= 0:
            raise InvalidTransformParamsError("Width and height must be positive integers.")

        op = (operation or "").strip().lower()
        if op not in {"crop", "resize", "rotate", "flip", "shear", "affine"}:
            raise InvalidTransformParamsError(
                f"Unsupported operation '{operation}'. Supported operations: crop, resize, rotate, flip, shear, affine."
            )

        if not isinstance(params, dict):
            raise InvalidTransformParamsError("Parameters must be a dictionary.")

        if op == "crop":
            for req in ("x", "y", "width", "height"):
                if req not in params:
                    raise InvalidTransformParamsError(f"Crop requires '{req}' parameter.")

            try:
                x = int(params["x"])
                y = int(params["y"])
                crop_w = int(params["width"])
                crop_h = int(params["height"])
            except (ValueError, TypeError) as exc:
                raise InvalidTransformParamsError("Crop coordinates and dimensions must be integers.") from exc

            if x < 0 or y < 0:
                raise InvalidTransformParamsError("Crop origin coordinates (x, y) must be non-negative.")
            if crop_w < 1 or crop_h < 1:
                raise InvalidTransformParamsError("Crop dimensions (width, height) must be >= 1.")
            if x + crop_w > width or y + crop_h > height:
                raise InvalidTransformParamsError(
                    f"Crop rectangle [x={x}, y={y}, w={crop_w}, h={crop_h}] exceeds image boundaries ({width}x{height})."
                )
            return crop_w, crop_h

        elif op == "resize":
            keep_aspect_ratio = params.get("keep_aspect_ratio", True)
            scale = params.get("scale")
            target_w = params.get("width")
            target_h = params.get("height")

            if scale is not None:
                try:
                    scale_val = float(scale)
                except (ValueError, TypeError) as exc:
                    raise InvalidTransformParamsError("Scale multiplier must be a float.") from exc

                if not (0.05 <= scale_val <= 8.0):
                    raise InvalidTransformParamsError("Scale must be in range [0.05, 8.0].")

                new_w = max(1, int(round(width * scale_val)))
                new_h = max(1, int(round(height * scale_val)))
            elif target_w is not None or target_h is not None:
                try:
                    w_val = int(target_w) if target_w is not None else None
                    h_val = int(target_h) if target_h is not None else None
                except (ValueError, TypeError) as exc:
                    raise InvalidTransformParamsError("Target width and height must be integers.") from exc

                if w_val is not None and w_val <= 0:
                    raise InvalidTransformParamsError("Width must be positive.")
                if h_val is not None and h_val <= 0:
                    raise InvalidTransformParamsError("Height must be positive.")

                if keep_aspect_ratio:
                    if w_val is not None and h_val is not None:
                        ratio = min(w_val / width, h_val / height)
                        new_w = max(1, int(round(width * ratio)))
                        new_h = max(1, int(round(height * ratio)))
                    elif w_val is not None:
                        ratio = w_val / width
                        new_w = w_val
                        new_h = max(1, int(round(height * ratio)))
                    else:
                        ratio = h_val / height  # type: ignore[operator]
                        new_h = h_val  # type: ignore[assignment]
                        new_w = max(1, int(round(width * ratio)))
                else:
                    new_w = w_val if w_val is not None else width
                    new_h = h_val if h_val is not None else height
            else:
                raise InvalidTransformParamsError("Resize requires either 'scale' or 'width'/'height'.")

            if not (cls.MIN_DIMENSION <= new_w <= cls.MAX_DIMENSION) or not (
                cls.MIN_DIMENSION <= new_h <= cls.MAX_DIMENSION
            ):
                raise InvalidTransformParamsError(
                    f"Target dimensions ({new_w}x{new_h}) must be within [{cls.MIN_DIMENSION}, {cls.MAX_DIMENSION}]."
                )
            return new_w, new_h

        elif op == "rotate":
            if "angle" not in params:
                raise InvalidTransformParamsError("Rotate requires 'angle' parameter.")

            try:
                angle = float(params["angle"])
            except (ValueError, TypeError) as exc:
                raise InvalidTransformParamsError("Angle must be a number.") from exc

            if not (-360.0 <= angle <= 360.0):
                raise InvalidTransformParamsError("Angle must be in range [-360, 360].")

            expand = bool(params.get("expand", True))
            if not expand:
                return width, height

            rad = math.radians(abs(angle))
            cos_a = abs(math.cos(rad))
            sin_a = abs(math.sin(rad))

            new_w = int(math.ceil(width * cos_a + height * sin_a))
            new_h = int(math.ceil(width * sin_a + height * cos_a))

            if new_w > cls.MAX_DIMENSION or new_h > cls.MAX_DIMENSION:
                raise InvalidTransformParamsError(
                    f"Resulting rotated canvas ({new_w}x{new_h}) exceeds maximum allowed dimension ({cls.MAX_DIMENSION}px)."
                )
            return new_w, new_h

        elif op == "flip":
            direction = params.get("direction")
            if direction not in ("horizontal", "vertical"):
                raise InvalidTransformParamsError("Flip direction must be strictly 'horizontal' or 'vertical'.")
            return width, height

        elif op == "shear":
            try:
                sh_x = float(params.get("shear_x", 0.0))
                sh_y = float(params.get("shear_y", 0.0))
            except (ValueError, TypeError) as exc:
                raise InvalidTransformParamsError("Shear factors must be numbers.") from exc

            if sh_x == 0.0 and sh_y == 0.0:
                raise InvalidTransformParamsError("At least one of 'shear_x' or 'shear_y' must be non-zero.")

            if not (-2.0 <= sh_x <= 2.0) or not (-2.0 <= sh_y <= 2.0):
                raise InvalidTransformParamsError("Shear factors must be in range [-2.0, 2.0].")

            det = 1.0 - (sh_x * sh_y)
            if abs(det) < 1e-6:
                raise InvalidTransformParamsError("Singular shear transformation (shear_x * shear_y == 1).")

            expand = bool(params.get("expand", True))
            if not expand:
                return width, height

            corners = [
                (0.0, 0.0),
                (float(width), 0.0),
                (0.0, float(height)),
                (float(width), float(height)),
            ]
            trans_corners = [(x + sh_x * y, sh_y * x + y) for (x, y) in corners]
            min_x = min(pt[0] for pt in trans_corners)
            max_x = max(pt[0] for pt in trans_corners)
            min_y = min(pt[1] for pt in trans_corners)
            max_y = max(pt[1] for pt in trans_corners)

            new_w = int(math.ceil(max_x - min_x))
            new_h = int(math.ceil(max_y - min_y))

            if new_w > cls.MAX_DIMENSION or new_h > cls.MAX_DIMENSION:
                raise InvalidTransformParamsError(
                    f"Resulting sheared canvas ({new_w}x{new_h}) exceeds maximum allowed dimension ({cls.MAX_DIMENSION}px)."
                )
            return new_w, new_h

        elif op == "affine":
            a, b, c, d, e, f = _parse_affine_matrix(params)
            det = a * e - b * d
            if abs(det) < 1e-7:
                raise InvalidTransformParamsError("Singular affine transformation matrix (determinant is zero or near zero).")

            expand = bool(params.get("expand", True))
            if not expand:
                return width, height

            corners = [
                (0.0, 0.0),
                (float(width), 0.0),
                (0.0, float(height)),
                (float(width), float(height)),
            ]
            trans_corners = [(a * x + b * y + c, d * x + e * y + f) for (x, y) in corners]
            min_x = min(pt[0] for pt in trans_corners)
            max_x = max(pt[0] for pt in trans_corners)
            min_y = min(pt[1] for pt in trans_corners)
            max_y = max(pt[1] for pt in trans_corners)

            new_w = max(1, int(math.ceil(max_x - min_x)))
            new_h = max(1, int(math.ceil(max_y - min_y)))

            if new_w > cls.MAX_DIMENSION or new_h > cls.MAX_DIMENSION:
                raise InvalidTransformParamsError(
                    f"Resulting affine canvas ({new_w}x{new_h}) exceeds maximum allowed dimension ({cls.MAX_DIMENSION}px)."
                )
            return new_w, new_h

        raise InvalidTransformParamsError(f"Unknown operation: {op}")

    @classmethod
    def apply_transform(
        cls,
        image_bytes: bytes,
        operation: str,
        params: dict[str, Any],
    ) -> TransformedImageResult:
        if not image_bytes:
            raise InvalidTransformParamsError("Image data cannot be empty.")

        op = (operation or "").strip().lower()
        if op not in {"crop", "resize", "rotate", "flip", "shear", "affine"}:
            raise InvalidTransformParamsError(
                f"Unsupported operation '{operation}'. Supported operations: crop, resize, rotate, flip, shear, affine."
            )

        try:
            with PILImage.open(io.BytesIO(image_bytes)) as raw_img:
                raw_img.verify()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidTransformParamsError("Invalid or corrupted image data.") from exc

        # Reopen to get working image and normalize EXIF orientation
        with PILImage.open(io.BytesIO(image_bytes)) as source_img:
            detected_format = (source_img.format or "").upper()
            if detected_format not in SUPPORTED_IMAGE_FORMATS:
                raise InvalidTransformParamsError(
                    f"Unsupported image format: {detected_format}. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS.keys())}."
                )

            # Transpose according to EXIF orientation so pixel coordinates match visual display
            img = ImageOps.exif_transpose(source_img)
            if img is None:
                img = source_img.copy()

            if op == "crop":
                transformed = cls._crop(img, params)
            elif op == "resize":
                transformed = cls._resize(img, params)
            elif op == "rotate":
                transformed = cls._rotate(img, params, detected_format)
            elif op == "flip":
                transformed = cls._flip(img, params)
            elif op == "shear":
                transformed = cls._shear(img, params, detected_format)
            elif op == "affine":
                transformed = cls._affine(img, params, detected_format)
            else:
                raise InvalidTransformParamsError(f"Unknown operation: {op}")

            # Re-check output bounds
            w, h = transformed.size
            if w > cls.MAX_DIMENSION or h > cls.MAX_DIMENSION:
                raise InvalidTransformParamsError(
                    f"Resulting image dimensions ({w}x{h}) exceed maximum allowed dimension ({cls.MAX_DIMENSION}px)."
                )

            # Prepare for export in original format
            out_format = detected_format
            extension, mime_type = SUPPORTED_IMAGE_FORMATS[out_format]

            # If saving as JPEG, ensure mode has no alpha
            if out_format == "JPEG" and transformed.mode in ("RGBA", "LA", "P"):
                fill_color = params.get("fill_color", "#FFFFFF") if isinstance(params, dict) else "#FFFFFF"
                bg_color = _parse_fill_color(fill_color, has_alpha=False)
                bg = PILImage.new("RGB", transformed.size, bg_color)
                if transformed.mode == "RGBA":
                    bg.paste(transformed, mask=transformed.split()[3])
                else:
                    bg.paste(transformed.convert("RGBA"), mask=transformed.convert("RGBA").split()[3])
                transformed = bg
            elif transformed.mode not in ("RGB", "RGBA", "L"):
                transformed = transformed.convert("RGBA" if "A" in transformed.mode else "RGB")

            buffer = io.BytesIO()
            save_kwargs: dict[str, Any] = {"format": out_format}
            if out_format == "JPEG":
                save_kwargs["quality"] = 95
            elif out_format == "PNG":
                save_kwargs["optimize"] = True

            transformed.save(buffer, **save_kwargs)
            out_bytes = buffer.getvalue()
            checksum = hashlib.sha256(out_bytes).hexdigest()

            return TransformedImageResult(
                data=out_bytes,
                format=out_format,
                extension=extension,
                mime_type=mime_type,
                width=w,
                height=h,
                file_size=len(out_bytes),
                checksum=checksum,
            )

    @classmethod
    def _crop(cls, img: PILImage.Image, params: dict[str, Any]) -> PILImage.Image:
        for req in ("x", "y", "width", "height"):
            if req not in params:
                raise InvalidTransformParamsError(f"Crop requires '{req}' parameter.")

        try:
            x = int(params["x"])
            y = int(params["y"])
            width = int(params["width"])
            height = int(params["height"])
        except (ValueError, TypeError) as exc:
            raise InvalidTransformParamsError("Crop coordinates and dimensions must be integers.") from exc

        orig_w, orig_h = img.size

        if x < 0 or y < 0:
            raise InvalidTransformParamsError("Crop origin coordinates (x, y) must be non-negative.")
        if width < 1 or height < 1:
            raise InvalidTransformParamsError("Crop dimensions (width, height) must be >= 1.")
        if x + width > orig_w or y + height > orig_h:
            raise InvalidTransformParamsError(
                f"Crop rectangle [x={x}, y={y}, w={width}, h={height}] exceeds image boundaries ({orig_w}x{orig_h})."
            )

        return img.crop((x, y, x + width, y + height))

    @classmethod
    def _resize(cls, img: PILImage.Image, params: dict[str, Any]) -> PILImage.Image:
        orig_w, orig_h = img.size
        keep_aspect_ratio = params.get("keep_aspect_ratio", True)
        scale = params.get("scale")
        target_w = params.get("width")
        target_h = params.get("height")

        if scale is not None:
            try:
                scale_val = float(scale)
            except (ValueError, TypeError) as exc:
                raise InvalidTransformParamsError("Scale multiplier must be a float.") from exc

            if not (0.05 <= scale_val <= 8.0):
                raise InvalidTransformParamsError("Scale must be in range [0.05, 8.0].")

            new_w = max(1, int(round(orig_w * scale_val)))
            new_h = max(1, int(round(orig_h * scale_val)))
        elif target_w is not None or target_h is not None:
            try:
                w_val = int(target_w) if target_w is not None else None
                h_val = int(target_h) if target_h is not None else None
            except (ValueError, TypeError) as exc:
                raise InvalidTransformParamsError("Target width and height must be integers.") from exc

            if w_val is not None and w_val <= 0:
                raise InvalidTransformParamsError("Width must be positive.")
            if h_val is not None and h_val <= 0:
                raise InvalidTransformParamsError("Height must be positive.")

            if keep_aspect_ratio:
                if w_val is not None and h_val is not None:
                    # Fit within bounding box keeping aspect ratio
                    ratio = min(w_val / orig_w, h_val / orig_h)
                    new_w = max(1, int(round(orig_w * ratio)))
                    new_h = max(1, int(round(orig_h * ratio)))
                elif w_val is not None:
                    ratio = w_val / orig_w
                    new_w = w_val
                    new_h = max(1, int(round(orig_h * ratio)))
                else:
                    ratio = h_val / orig_h  # type: ignore[operator]
                    new_h = h_val  # type: ignore[assignment]
                    new_w = max(1, int(round(orig_w * ratio)))
            else:
                new_w = w_val if w_val is not None else orig_w
                new_h = h_val if h_val is not None else orig_h
        else:
            raise InvalidTransformParamsError("Resize requires either 'scale' or 'width'/'height'.")

        if not (cls.MIN_DIMENSION <= new_w <= cls.MAX_DIMENSION) or not (
            cls.MIN_DIMENSION <= new_h <= cls.MAX_DIMENSION
        ):
            raise InvalidTransformParamsError(
                f"Target dimensions ({new_w}x{new_h}) must be within [{cls.MIN_DIMENSION}, {cls.MAX_DIMENSION}]."
            )

        return img.resize((new_w, new_h), resample=PILImage.Resampling.LANCZOS)

    @classmethod
    def _rotate(cls, img: PILImage.Image, params: dict[str, Any], fmt: str) -> PILImage.Image:
        if "angle" not in params:
            raise InvalidTransformParamsError("Rotate requires 'angle' parameter.")

        try:
            angle = float(params["angle"])
        except (ValueError, TypeError) as exc:
            raise InvalidTransformParamsError("Angle must be a number.") from exc

        if not (-360.0 <= angle <= 360.0):
            raise InvalidTransformParamsError("Angle must be in range [-360, 360].")

        expand = bool(params.get("expand", True))
        fill_color_str = params.get("fill_color", "#FFFFFF")

        has_alpha = (fmt != "JPEG" and img.mode in ("RGBA", "LA", "P"))
        fill_color = _parse_fill_color(fill_color_str, has_alpha)

        # In PIL, positive angle in rotate() is counter-clockwise
        return img.rotate(
            angle,
            resample=PILImage.Resampling.BICUBIC,
            expand=expand,
            fillcolor=fill_color,
        )

    @classmethod
    def _flip(cls, img: PILImage.Image, params: dict[str, Any]) -> PILImage.Image:
        direction = params.get("direction")
        if direction not in ("horizontal", "vertical"):
            raise InvalidTransformParamsError("Flip direction must be strictly 'horizontal' or 'vertical'.")

        if direction == "horizontal":
            return ImageOps.mirror(img)
        return ImageOps.flip(img)

    @classmethod
    def _shear(cls, img: PILImage.Image, params: dict[str, Any], fmt: str) -> PILImage.Image:
        try:
            sh_x = float(params.get("shear_x", 0.0))
            sh_y = float(params.get("shear_y", 0.0))
        except (ValueError, TypeError) as exc:
            raise InvalidTransformParamsError("Shear factors must be numbers.") from exc

        if sh_x == 0.0 and sh_y == 0.0:
            raise InvalidTransformParamsError("At least one of 'shear_x' or 'shear_y' must be non-zero.")

        if not (-2.0 <= sh_x <= 2.0) or not (-2.0 <= sh_y <= 2.0):
            raise InvalidTransformParamsError("Shear factors must be in range [-2.0, 2.0].")

        expand = bool(params.get("expand", True))
        fill_color_str = params.get("fill_color", "#FFFFFF")

        has_alpha = (fmt != "JPEG" and img.mode in ("RGBA", "LA", "P"))
        fill_color = _parse_fill_color(fill_color_str, has_alpha)

        w, h = img.size

        if expand:
            # Map the 4 corners: (0,0), (w,0), (0,h), (w,h)
            corners = [
                (0.0, 0.0),
                (float(w), 0.0),
                (0.0, float(h)),
                (float(w), float(h)),
            ]
            trans_corners = [(x + sh_x * y, sh_y * x + y) for (x, y) in corners]
            min_x = min(pt[0] for pt in trans_corners)
            max_x = max(pt[0] for pt in trans_corners)
            min_y = min(pt[1] for pt in trans_corners)
            max_y = max(pt[1] for pt in trans_corners)

            new_w = int(math.ceil(max_x - min_x))
            new_h = int(math.ceil(max_y - min_y))

            if new_w > cls.MAX_DIMENSION or new_h > cls.MAX_DIMENSION:
                raise InvalidTransformParamsError(
                    f"Resulting sheared canvas ({new_w}x{new_h}) exceeds maximum allowed dimension ({cls.MAX_DIMENSION}px)."
                )

            # Offset so min_x and min_y are translated to canvas origin (0, 0)
            x_off = min_x
            y_off = min_y
        else:
            new_w = w
            new_h = h
            x_off = 0.0
            y_off = 0.0

        # PIL transform AFFINE takes the inverse affine matrix mapping output coords (X, Y) to source (x, y)
        det = 1.0 - (sh_x * sh_y)
        if abs(det) < 1e-6:
            raise InvalidTransformParamsError("Singular shear transformation (shear_x * shear_y == 1).")

        # Inverse matrix:
        a = 1.0 / det
        b = -sh_x / det
        c = (x_off - sh_x * y_off) / det
        d = -sh_y / det
        e = 1.0 / det
        f = (y_off - sh_y * x_off) / det

        mode = "RGBA" if has_alpha else "RGB"
        working_img = img.convert(mode)

        return working_img.transform(
            (new_w, new_h),
            PILImage.Transform.AFFINE,
            (a, b, c, d, e, f),
            resample=PILImage.Resampling.BICUBIC,
            fillcolor=fill_color,
        )

    @classmethod
    def _affine(cls, img: PILImage.Image, params: dict[str, Any], fmt: str) -> PILImage.Image:
        a, b, c, d, e, f = _parse_affine_matrix(params)
        det = a * e - b * d
        if abs(det) < 1e-7:
            raise InvalidTransformParamsError("Singular affine transformation matrix (determinant is zero or near zero).")

        expand = bool(params.get("expand", True))
        fill_color_str = params.get("fill_color", "#FFFFFF")

        has_alpha = (fmt != "JPEG" and img.mode in ("RGBA", "LA", "P"))
        fill_color = _parse_fill_color(fill_color_str, has_alpha)

        w, h = img.size

        if expand:
            corners = [
                (0.0, 0.0),
                (float(w), 0.0),
                (0.0, float(h)),
                (float(w), float(h)),
            ]
            trans_corners = [(a * x + b * y + c, d * x + e * y + f) for (x, y) in corners]
            min_x = min(pt[0] for pt in trans_corners)
            max_x = max(pt[0] for pt in trans_corners)
            min_y = min(pt[1] for pt in trans_corners)
            max_y = max(pt[1] for pt in trans_corners)

            new_w = max(1, int(math.ceil(max_x - min_x)))
            new_h = max(1, int(math.ceil(max_y - min_y)))

            if new_w > cls.MAX_DIMENSION or new_h > cls.MAX_DIMENSION:
                raise InvalidTransformParamsError(
                    f"Resulting affine canvas ({new_w}x{new_h}) exceeds maximum allowed dimension ({cls.MAX_DIMENSION}px)."
                )

            x_off = min_x
            y_off = min_y
        else:
            new_w = w
            new_h = h
            x_off = 0.0
            y_off = 0.0

        # Invert affine mapping from output canvas (X, Y) back to source image (x, y)
        a_pil = e / det
        b_pil = -b / det
        c_pil = (e * (x_off - c) - b * (y_off - f)) / det
        d_pil = -d / det
        e_pil = a / det
        f_pil = (-d * (x_off - c) + a * (y_off - f)) / det

        mode = "RGBA" if has_alpha else "RGB"
        working_img = img.convert(mode)

        return working_img.transform(
            (new_w, new_h),
            PILImage.Transform.AFFINE,
            (a_pil, b_pil, c_pil, d_pil, e_pil, f_pil),
            resample=PILImage.Resampling.BICUBIC,
            fillcolor=fill_color,
        )
