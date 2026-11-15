import io
import pytest
from PIL import Image as PILImage

from src.services.transform_engine import (
    InvalidTransformParamsError,
    TransformEngine,
)


def make_test_image(format="PNG", size=(100, 80), color="blue") -> bytes:
    buf = io.BytesIO()
    img = PILImage.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_crop_valid():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "crop",
        {"x": 10, "y": 10, "width": 50, "height": 40},
    )
    assert res.width == 50
    assert res.height == 40
    assert res.format == "PNG"
    assert res.file_size > 0


def test_crop_out_of_bounds_raises():
    img_bytes = make_test_image(size=(100, 80))
    with pytest.raises(InvalidTransformParamsError):
        TransformEngine.apply_transform(
            img_bytes,
            "crop",
            {"x": 90, "y": 10, "width": 50, "height": 40},
        )


def test_resize_scale_and_dimensions():
    img_bytes = make_test_image(size=(100, 80))

    # Test scale
    res_scale = TransformEngine.apply_transform(
        img_bytes,
        "resize",
        {"scale": 0.5},
    )
    assert res_scale.width == 50
    assert res_scale.height == 40

    # Test explicit dimensions with aspect ratio
    res_dim = TransformEngine.apply_transform(
        img_bytes,
        "resize",
        {"width": 50, "height": 50, "keep_aspect_ratio": True},
    )
    assert res_dim.width == 50
    assert res_dim.height == 40


def test_rotate_expand():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "rotate",
        {"angle": 90, "expand": True},
    )
    assert res.width == 80
    assert res.height == 100


def test_flip_horizontal_and_vertical():
    img_bytes = make_test_image(size=(100, 80))
    res_h = TransformEngine.apply_transform(
        img_bytes,
        "flip",
        {"direction": "horizontal"},
    )
    assert res_h.width == 100
    assert res_h.height == 80

    res_v = TransformEngine.apply_transform(
        img_bytes,
        "flip",
        {"direction": "vertical"},
    )
    assert res_v.width == 100
    assert res_v.height == 80


def test_shear_with_expansion():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "shear",
        {"shear_x": 0.25, "shear_y": 0.0, "expand": True, "fill_color": "#FFFFFF"},
    )
    # With shear_x=0.25, new_w = 100 + 0.25*80 = 120
    assert res.width == 120
    assert res.height == 80


def test_shear_singular_or_zero_raises():
    img_bytes = make_test_image(size=(100, 80))
    with pytest.raises(InvalidTransformParamsError):
        TransformEngine.apply_transform(
            img_bytes,
            "shear",
            {"shear_x": 0.0, "shear_y": 0.0},
        )


def test_compute_output_dimensions():
    # Crop
    w, h = TransformEngine.compute_output_dimensions(100, 80, "crop", {"x": 10, "y": 10, "width": 50, "height": 40})
    assert (w, h) == (50, 40)

    # Resize scale
    w, h = TransformEngine.compute_output_dimensions(100, 80, "resize", {"scale": 0.5})
    assert (w, h) == (50, 40)

    # Rotate 90 with expand
    w, h = TransformEngine.compute_output_dimensions(100, 80, "rotate", {"angle": 90, "expand": True})
    assert (w, h) == (80, 100)

    # Flip
    w, h = TransformEngine.compute_output_dimensions(100, 80, "flip", {"direction": "horizontal"})
    assert (w, h) == (100, 80)

    # Shear
    w, h = TransformEngine.compute_output_dimensions(100, 80, "shear", {"shear_x": 0.25, "shear_y": 0.0, "expand": True})
    assert (w, h) == (120, 80)

    # Affine identity
    w, h = TransformEngine.compute_output_dimensions(100, 80, "affine", {"matrix": [1, 0, 0, 0, 1, 0], "expand": True})
    assert (w, h) == (100, 80)

    # Affine scale 2x with expand
    w, h = TransformEngine.compute_output_dimensions(100, 80, "affine", {"matrix": [2, 0, 0, 0, 2, 0], "expand": True})
    assert (w, h) == (200, 160)

    # Affine without expand
    w, h = TransformEngine.compute_output_dimensions(100, 80, "affine", {"matrix": [2, 0, 0, 0, 2, 0], "expand": False})
    assert (w, h) == (100, 80)


def test_affine_identity():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "affine",
        {"matrix": [1, 0, 0, 0, 1, 0], "expand": True},
    )
    assert res.width == 100
    assert res.height == 80
    assert res.format == "PNG"


def test_affine_scale_with_expansion():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "affine",
        {"matrix": [1.5, 0, 0, 0, 1.5, 0], "expand": True},
    )
    assert res.width == 150
    assert res.height == 120


def test_affine_decomposed_params():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "affine",
        {"scale_x": 2.0, "scale_y": 1.0, "expand": True},
    )
    assert res.width == 200
    assert res.height == 80


def test_affine_singular_matrix_raises():
    img_bytes = make_test_image(size=(100, 80))
    with pytest.raises(InvalidTransformParamsError):
        TransformEngine.apply_transform(
            img_bytes,
            "affine",
            {"matrix": [1, 1, 0, 1, 1, 0]},  # det = 1*1 - 1*1 = 0
        )

