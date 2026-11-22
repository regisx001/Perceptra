import hashlib
import io
from dataclasses import dataclass
from typing import Any, BinaryIO, Optional

from PIL import Image as PILImage, ImageOps, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import db
from src.models.category import Category
from src.models.image import Image
from src.services.storage import StorageBackend, StorageError
from src.services.transform_engine import (
    InvalidTransformParamsError,
    TransformEngine,
    TransformError,
)


class ImageServiceError(Exception):
    """Base domain exception for image operations."""
    status_code = 400


class InvalidImageError(ImageServiceError):
    """Raised when uploaded file is empty, unsupported, or corrupted."""
    status_code = 400


class ResourceNotFoundError(ImageServiceError):
    """Raised when an image or category does not exist or is not owned by the user."""
    status_code = 404


# Map Pillow format identifiers to canonical (extension, mime_type)
SUPPORTED_IMAGE_FORMATS: dict[str, tuple[str, str]] = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
    "BMP": (".bmp", "image/bmp"),
}


@dataclass(frozen=True)
class ValidatedImageMetadata:
    width: int
    height: int
    extension: str
    mime_type: str
    file_size: int
    checksum: str


class ImageService:
    def __init__(self, storage: StorageBackend, max_file_size: Optional[int] = 32 * 1024 * 1024):
        self.storage = storage
        self.max_file_size = max_file_size or (32 * 1024 * 1024)

    def _validate_image_bytes(self, raw_bytes: bytes) -> ValidatedImageMetadata:
        if not raw_bytes:
            raise InvalidImageError("Uploaded file is empty.")

        file_size = len(raw_bytes)
        if file_size > self.max_file_size:
            raise InvalidImageError(
                f"File size ({file_size} bytes) exceeds maximum limit ({self.max_file_size} bytes)."
            )

        try:
            with PILImage.open(io.BytesIO(raw_bytes)) as img:
                img.verify()

            # Re-open after verify() to safely inspect dimensions and format
            with PILImage.open(io.BytesIO(raw_bytes)) as img:
                width, height = img.size
                detected_format = (img.format or "").upper()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("Invalid or corrupted image file.") from exc

        if detected_format not in SUPPORTED_IMAGE_FORMATS:
            allowed = ", ".join(SUPPORTED_IMAGE_FORMATS.keys())
            raise InvalidImageError(
                f"Unsupported image format '{detected_format or 'UNKNOWN'}'. Supported: {allowed}."
            )

        if width <= 0 or height <= 0:
            raise InvalidImageError("Image dimensions must be positive.")

        extension, mime_type = SUPPORTED_IMAGE_FORMATS[detected_format]
        checksum = hashlib.sha256(raw_bytes).hexdigest()

        return ValidatedImageMetadata(
            width=width,
            height=height,
            extension=extension,
            mime_type=mime_type,
            file_size=file_size,
            checksum=checksum,
        )

    def _verify_category_ownership(self, user_id: str, category_id: Optional[str]) -> Optional[str]:
        if not category_id:
            return None

        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            raise ResourceNotFoundError("Target category does not exist.")
        return category.id

    def upload_image(
        self,
        user_id: str,
        raw_bytes: bytes,
        original_filename: str,
        category_id: Optional[str] = None,
    ) -> Image:
        # 1. Verify category ownership before writing anything to disk
        verified_category_id = self._verify_category_ownership(user_id, category_id)

        # 2. Validate binary content and derive true format/dimensions
        meta = self._validate_image_bytes(raw_bytes)

        # 3. Store physically under users/{user_id}/{uuid}.{ext}
        user_directory = f"users/{user_id}"
        try:
            storage_key = self.storage.save(
                file=io.BytesIO(raw_bytes),
                directory=user_directory,
                extension=meta.extension,
            )
        except StorageError as exc:
            raise ImageServiceError(f"Failed to persist image file: {exc}") from exc

        # 4. Persist metadata in SQLite with compensating disk rollback on failure
        safe_filename = (original_filename or f"upload{meta.extension}")[:255]
        image_record = Image(
            owner_id=user_id,
            category_id=verified_category_id,
            filename=safe_filename,
            storage_key=storage_key,
            source_type="upload",
            mime_type=meta.mime_type,
            file_size=meta.file_size,
            width=meta.width,
            height=meta.height,
            checksum=meta.checksum,
            processing_status="pending",
        )

        try:
            db.session.add(image_record)
            db.session.commit()
            return image_record
        except SQLAlchemyError as exc:
            db.session.rollback()
            self.storage.delete(storage_key)
            raise ImageServiceError("Database error while saving image metadata.") from exc

    def transform_image(
        self,
        user_id: str,
        image_id: str,
        operation: str,
        params: dict[str, Any],
        filename: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> Image:
        """
        Execute a transformation on an owned image, creating a new derived child Image.
        """
        # 1. Fetch original parent image and verify ownership
        original = self.get_user_image(user_id, image_id)

        # 2. Verify target category if specified (defaults to parent's category_id)
        if category_id is not None:
            target_category_id = self._verify_category_ownership(user_id, category_id)
        else:
            target_category_id = original.category_id

        # 3. Read source image bytes from storage
        try:
            with self.storage.open(original.storage_key, "rb") as f_in:
                source_bytes = f_in.read()
        except StorageError as exc:
            raise ResourceNotFoundError(f"Source image file missing from storage: {exc}") from exc

        # 4. Apply transformation using TransformEngine
        try:
            res = TransformEngine.apply_transform(
                image_bytes=source_bytes,
                operation=operation,
                params=params,
            )
        except InvalidTransformParamsError as exc:
            raise ImageServiceError(str(exc)) from exc
        except TransformError as exc:
            raise ImageServiceError(f"Transformation failed: {exc}") from exc

        # 5. Persist derived image into derived/{user_id}/{uuid}.{ext}
        derived_directory = f"derived/{user_id}"
        try:
            storage_key = self.storage.save(
                file=io.BytesIO(res.data),
                directory=derived_directory,
                extension=res.extension,
            )
        except StorageError as exc:
            raise ImageServiceError(f"Failed to persist transformed image: {exc}") from exc

        # 6. Determine safe filename
        if filename and filename.strip():
            safe_filename = filename.strip()[:255]
        else:
            stem = original.filename.rsplit(".", 1)[0] if "." in original.filename else original.filename
            safe_filename = f"{stem}_{operation.lower()}{res.extension}"[:255]

        # 7. Persist child Image in database with compensating rollback
        derived_image = Image(
            owner_id=user_id,
            category_id=target_category_id,
            parent_image_id=original.id,
            filename=safe_filename,
            storage_key=storage_key,
            source_type="derived",
            mime_type=res.mime_type,
            file_size=res.file_size,
            width=res.width,
            height=res.height,
            checksum=res.checksum,
            transformation_params={
                "operation": operation.lower(),
                "params": params,
            },
            processing_status="pending",
        )

        try:
            db.session.add(derived_image)
            db.session.commit()
            return derived_image
        except SQLAlchemyError as exc:
            db.session.rollback()
            self.storage.delete(storage_key)
            raise ImageServiceError("Database error while recording transformed image.") from exc

    def list_derivatives(self, user_id: str, image_id: str) -> list[Image]:
        """
        List all derived versions of an image owned by the user.
        """
        # Ensure parent exists and belongs to user
        self.get_user_image(user_id, image_id)

        return (
            Image.query.filter_by(parent_image_id=image_id, owner_id=user_id)
            .order_by(Image.created_at.desc())
            .all()
        )

    def list_user_images(
        self,
        user_id: str,
        category_id: Optional[str] = None,
        uncategorized_only: bool = False,
        favorites_only: bool = False,
        source_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 24,
    ):
        query = Image.query
        if favorites_only:
            from src.models.favorite import FavoriteImage
            query = query.join(FavoriteImage, FavoriteImage.image_id == Image.id).filter(
                FavoriteImage.user_id == user_id
            )
        elif source_type == "dataset":
            query = query.filter(Image.source_type == "dataset")
        elif source_type == "all":
            query = query.filter((Image.owner_id == user_id) | (Image.source_type == "dataset"))
        else:
            # Default: strictly user's own library images (uploads & transforms)
            query = query.filter(Image.owner_id == user_id, Image.source_type.in_(["upload", "derived"]))

        if uncategorized_only:
            query = query.filter(Image.category_id.is_(None))
        elif category_id:
            cat = Category.query.filter_by(id=category_id).first()
            if not cat or (cat.user_id != user_id and cat.user_id is not None):
                raise ResourceNotFoundError("Target category does not exist.")
            query = query.filter_by(category_id=category_id)

        if favorites_only:
            from src.models.favorite import FavoriteImage
            return query.order_by(FavoriteImage.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )

        return query.order_by(Image.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def toggle_favorite(self, user_id: str, image_id: str) -> bool:
        """
        Toggle favorite status of an image for a user. Returns True if now favorited, False if unfavorited.
        """
        # Ensure image exists and user can access it (owned or dataset)
        self.get_user_image(user_id, image_id)

        from src.models.favorite import FavoriteImage
        fav = FavoriteImage.query.filter_by(user_id=user_id, image_id=image_id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return False
        else:
            new_fav = FavoriteImage(user_id=user_id, image_id=image_id)
            db.session.add(new_fav)
            db.session.commit()
            return True

    def get_user_image(self, user_id: str, image_id: str) -> Image:
        image = Image.query.filter(
            (Image.id == image_id)
            & (
                (Image.owner_id == user_id)
                | (Image.owner_id.is_(None))
                | (Image.source_type == "dataset")
            )
        ).first()
        if not image:
            raise ResourceNotFoundError("Image not found.")
        return image

    def open_image_stream(
        self,
        user_id: str,
        image_id: str,
        preview: bool = False,
        max_preview_edge: int = 800,
    ) -> tuple[Image, BinaryIO, str]:
        """
        Open image stream. If preview=True and image dimensions exceed max_preview_edge,
        downscale the stream in-memory via Pillow thumbnail into a lightweight JPEG (quality=80).
        Returns: (image_model, stream, mime_type)
        """
        image = self.get_user_image(user_id, image_id)
        try:
            stream = self.storage.open(image.storage_key)
        except StorageError as exc:
            raise ResourceNotFoundError("Physical image file missing from storage.") from exc

        if not preview or (image.width <= max_preview_edge and image.height <= max_preview_edge):
            return image, stream, image.mime_type

        # Generate lightweight downscaled preview in-memory
        try:
            with stream:
                raw_bytes = stream.read()

            with PILImage.open(io.BytesIO(raw_bytes)) as img:
                img = ImageOps.exif_transpose(img) or img
                if img.mode in ("RGBA", "LA", "P"):
                    # Flatten onto white background for JPEG
                    bg = PILImage.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        bg.paste(img, mask=img.split()[3])
                    else:
                        bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[3])
                    preview_img = bg
                elif img.mode != "RGB":
                    preview_img = img.convert("RGB")
                else:
                    preview_img = img.copy()

                preview_img.thumbnail((max_preview_edge, max_preview_edge), resample=PILImage.Resampling.LANCZOS)
                preview_buffer = io.BytesIO()
                preview_img.save(preview_buffer, format="JPEG", quality=80, optimize=True)
                preview_buffer.seek(0)
                return image, preview_buffer, "image/jpeg"
        except Exception as exc:
            # Fallback to original stream if thumbnail creation fails
            try:
                fallback_stream = self.storage.open(image.storage_key)
                return image, fallback_stream, image.mime_type
            except Exception:
                raise ImageServiceError(f"Failed to generate image preview: {exc}") from exc

    def validate_transform_dimensions(
        self,
        user_id: str,
        image_id: str,
        operation: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Pure math validation query using only SQLite width/height metadata.
        Does not touch physical storage or pixel buffers.
        """
        image = self.get_user_image(user_id, image_id)
        try:
            new_w, new_h = TransformEngine.compute_output_dimensions(
                width=image.width,
                height=image.height,
                operation=operation,
                params=params,
            )
        except InvalidTransformParamsError as exc:
            raise ImageServiceError(str(exc)) from exc

        aspect_ratio = round(new_w / new_h, 4) if new_h > 0 else 0.0

        return {
            "image_id": image.id,
            "original_width": image.width,
            "original_height": image.height,
            "new_width": new_w,
            "new_height": new_h,
            "aspect_ratio": aspect_ratio,
            "operation": (operation or "").strip().lower(),
            "params": params,
        }

    def assign_category(
        self, user_id: str, image_ids: list[str], category_id: Optional[str]
    ) -> int:
        verified_category_id = self._verify_category_ownership(user_id, category_id)
        images = Image.query.filter(
            Image.owner_id == user_id,
            Image.id.in_(image_ids),
        ).all()

        for img in images:
            img.category_id = verified_category_id

        db.session.commit()
        return len(images)

    def delete_image(self, user_id: str, image_id: str) -> None:
        image = self.get_user_image(user_id, image_id)
        storage_key = image.storage_key

        db.session.delete(image)
        db.session.commit()
        self.storage.delete(storage_key)

    def bulk_delete_images(self, user_id: str, image_ids: list[str]) -> int:
        images = Image.query.filter(
            Image.owner_id == user_id,
            Image.id.in_(image_ids),
        ).all()

        storage_keys = [img.storage_key for img in images]
        deleted_count = len(images)

        for img in images:
            db.session.delete(img)
        db.session.commit()

        for key in storage_keys:
            self.storage.delete(key)

        return deleted_count
