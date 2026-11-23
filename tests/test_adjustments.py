import io
import pytest
from PIL import Image as PILImage

from src.services.transform_engine import (
    InvalidTransformParamsError,
    TransformEngine,
)


def make_test_image(format="PNG", size=(80, 60), color="blue") -> bytes:
    buf = io.BytesIO()
    img = PILImage.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_adjustments_light_brightness_contrast():
    img_bytes = make_test_image(size=(80, 60))
    res = TransformEngine.apply_transform(
        img_bytes,
        "adjust",
        {
            "brightness": 25,
            "contrast": 15,
            "exposure": 10,
            "highlights": -10,
            "shadows": 20,
            "whites": 5,
            "blacks": -5,
        },
    )
    assert res.width == 80
    assert res.height == 60
    assert res.format == "PNG"
    assert res.file_size > 0


def test_adjustments_color_temperature_saturation():
    img_bytes = make_test_image(size=(80, 60))
    res = TransformEngine.apply_transform(
        img_bytes,
        "adjust",
        {
            "saturation": 30,
            "vibrance": 20,
            "hue": 45,
            "temperature": 15,
            "tint": -10,
        },
    )
    assert res.width == 80
    assert res.height == 60
    assert res.format == "PNG"


def test_adjustments_detail_sharpness_blur_clarity():
    img_bytes = make_test_image(size=(80, 60))
    res = TransformEngine.apply_transform(
        img_bytes,
        "adjust",
        {
            "sharpness": 35,
            "clarity": 20,
            "blur": 2,
        },
    )
    assert res.width == 80
    assert res.height == 60
    assert res.format == "PNG"


def test_adjustments_nested_structure():
    img_bytes = make_test_image(size=(80, 60))
    res = TransformEngine.apply_transform(
        img_bytes,
        "adjust",
        {
            "light": {"brightness": 20, "contrast": 10},
            "color": {"saturation": 15, "temperature": 5},
            "detail": {"sharpness": 20},
        },
    )
    assert res.width == 80
    assert res.height == 60


def test_geometric_with_stacked_adjustments():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "crop",
        {
            "x": 10,
            "y": 10,
            "width": 50,
            "height": 40,
            "adjustments": {
                "brightness": 15,
                "saturation": 25,
                "sharpness": 30,
            },
        },
    )
    assert res.width == 50
    assert res.height == 40
    assert res.format == "PNG"


def test_pipeline_multi_step_stacking():
    img_bytes = make_test_image(size=(100, 80))
    res = TransformEngine.apply_transform(
        img_bytes,
        "pipeline",
        {
            "steps": [
                {
                    "operation": "adjust",
                    "params": {"brightness": 10, "saturation": 20},
                },
                {
                    "operation": "crop",
                    "params": {"x": 10, "y": 10, "width": 60, "height": 50},
                },
                {
                    "operation": "rotate",
                    "params": {"angle": 90, "expand": True},
                },
            ]
        },
    )
    assert res.width == 50
    assert res.height == 60
    assert res.format == "PNG"


def test_pipeline_empty_steps_raises():
    img_bytes = make_test_image(size=(100, 80))
    with pytest.raises(InvalidTransformParamsError):
        TransformEngine.apply_transform(
            img_bytes,
            "pipeline",
            {"steps": []},
        )
