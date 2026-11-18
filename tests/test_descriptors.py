import io
import pytest
from PIL import Image as PILImage
from tests.test_categories import get_auth_token
from src.services.descriptor_engine import (
    DescriptorEngine,
    InvalidImageStreamError,
    UnsupportedFeatureTypeError,
)


def create_test_image_bytes(size=(64, 64), color="red") -> bytes:
    buf = io.BytesIO()
    img = PILImage.new("RGB", size, color=color)
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ============================================================================
# 1. DescriptorEngine Unit Tests
# ============================================================================

def test_engine_color_histogram():
    img_bytes = create_test_image_bytes(color="green")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_color_histogram(rgb_arr)

    assert params["color_space"] == "HSV"
    assert params["bins"] == {"h": 256, "s": 256, "v": 256}
    assert params["normalization"] == "L1"

    channels = f_vals["channels"]
    assert len(channels["h"]) == 256
    assert len(channels["s"]) == 256
    assert len(channels["v"]) == 256

    # Each channel sums approximately to 1.0
    assert abs(sum(channels["h"]) - 1.0) < 0.01
    assert abs(sum(channels["s"]) - 1.0) < 0.01
    assert abs(sum(channels["v"]) - 1.0) < 0.01

    assert len(f_vals["vector"]) == 768


def test_engine_color_moments():
    img_bytes = create_test_image_bytes(color="blue")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_color_moments(rgb_arr)

    assert params["color_space"] == "HSV"
    assert params["moments"] == ["mean", "std", "skewness"]

    channels = f_vals["channels"]
    for ch in ("h", "s", "v"):
        assert "mean" in channels[ch]
        assert "std" in channels[ch]
        assert "skewness" in channels[ch]

    assert len(f_vals["vector"]) == 9


def test_engine_dominant_colors():
    img_bytes = create_test_image_bytes(color="yellow")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_dominant_colors(rgb_arr, k=5)

    assert params["k"] == 5
    assert params["color_space"] == "RGB"

    clusters = f_vals["clusters"]
    assert len(clusters) == 5
    for rank, cl in enumerate(clusters, start=1):
        assert cl["rank"] == rank
        assert len(cl["rgb"]) == 3
        assert cl["hex"].startswith("#")
        assert 0.0 <= cl["percentage"] <= 100.0

    # Total percentage sums approximately to 100%
    total_pct = sum(cl["percentage"] for cl in clusters)
    assert abs(total_pct - 100.0) < 1.0

    assert len(f_vals["vector"]) == 20


def test_engine_glcm():
    img_bytes = create_test_image_bytes(color="purple")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_glcm(rgb_arr, levels=32)

    assert params["levels"] == 32
    assert params["distances"] == [1]
    assert params["angles_deg"] == [0, 45, 90, 135]

    summary = f_vals["summary"]
    for metric in ("contrast", "correlation", "energy", "homogeneity"):
        assert metric in summary

    by_angle = f_vals["by_angle"]
    for ang in ("0", "45", "90", "135"):
        assert ang in by_angle
        for metric in ("contrast", "correlation", "energy", "homogeneity"):
            assert metric in by_angle[ang]

    assert len(f_vals["vector"]) == 4


def test_engine_lbp_histogram():
    img_bytes = create_test_image_bytes(color="orange")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_lbp_histogram(rgb_arr, p=8, r=1)

    assert params["P"] == 8
    assert params["R"] == 1
    assert params["method"] == "uniform"
    assert params["bins"] == 10

    bins = f_vals["bins"]
    assert len(bins) == 10
    assert abs(sum(bins) - 1.0) < 0.01

    labels = f_vals["labels"]
    assert len(labels) == 10
    assert labels[-1] == "non-uniform"

    assert len(f_vals["vector"]) == 10


def test_engine_corrupted_image_raises():
    with pytest.raises(InvalidImageStreamError):
        DescriptorEngine.decode_image_rgb(b"not-an-image-data")


def test_engine_unsupported_feature_type_raises():
    img_bytes = create_test_image_bytes()
    with pytest.raises(UnsupportedFeatureTypeError):
        DescriptorEngine.extract(img_bytes, ["invalid_descriptor_type"])


# ============================================================================
# 2. Flask-RESTful API Integration Tests
# ============================================================================

def upload_sample_image(client, headers) -> str:
    img_data = create_test_image_bytes(size=(48, 48), color="red")
    data = {
        "file": (io.BytesIO(img_data), "sample_descriptor.jpg"),
    }
    res = client.post("/api/v1/images", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 201
    return res.get_json()["image"]["id"]


def test_get_unindexed_descriptors(client):
    token, _ = get_auth_token(client, "desc_user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    image_id = upload_sample_image(client, headers)

    # Initially processing_status is pending, descriptors empty
    res = client.get(f"/api/v1/images/{image_id}/descriptors", headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert json_data["image_id"] == image_id
    assert json_data["processing_status"] == "pending"
    assert json_data["available_features"] == []
    assert json_data["descriptors"] == {}


def test_extract_single_image_all_descriptors(client):
    token, _ = get_auth_token(client, "desc_user2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    image_id = upload_sample_image(client, headers)

    # Extract all 5 descriptors
    res = client.post(f"/api/v1/descriptors/extract/{image_id}", json={}, headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert json_data["image_id"] == image_id
    assert json_data["processing_status"] == "indexed"

    descriptors = json_data["descriptors"]
    for ft in ("color_histogram", "color_moments", "dominant_colors", "glcm", "lbp_histogram"):
        assert ft in descriptors

    # Now GET descriptors should return all 5
    get_res = client.get(f"/api/v1/images/{image_id}/descriptors", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.get_json()
    assert get_data["processing_status"] == "indexed"
    assert len(get_data["available_features"]) == 5
    assert len(get_data["descriptors"]) == 5


def test_extract_cached_and_force(client):
    token, _ = get_auth_token(client, "desc_user3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    image_id = upload_sample_image(client, headers)

    # Extract only color_moments
    res1 = client.post(
        f"/api/v1/descriptors/extract/{image_id}",
        json={"feature_types": ["color_moments"]},
        headers=headers,
    )
    assert res1.status_code == 200
    assert "color_moments" in res1.get_json()["descriptors"]

    # Extract again without force: should use cache
    res2 = client.post(
        f"/api/v1/descriptors/extract/{image_id}",
        json={"feature_types": ["color_moments"], "force": False},
        headers=headers,
    )
    assert res2.status_code == 200
    assert res2.get_json()["descriptors"]["color_moments"] == res1.get_json()["descriptors"]["color_moments"]

    # Extract with force: re-extracts cleanly
    res3 = client.post(
        f"/api/v1/descriptors/extract/{image_id}",
        json={"feature_types": ["color_moments"], "force": True},
        headers=headers,
    )
    assert res3.status_code == 200
    assert "color_moments" in res3.get_json()["descriptors"]


def test_extract_invalid_feature_type_returns_400(client):
    token, _ = get_auth_token(client, "desc_user4@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    image_id = upload_sample_image(client, headers)

    res = client.post(
        f"/api/v1/descriptors/extract/{image_id}",
        json={"feature_types": ["unknown_feat"]},
        headers=headers,
    )
    assert res.status_code == 400
    assert res.get_json()["success"] is False


def test_extract_nonexistent_image_returns_404(client):
    token, _ = get_auth_token(client, "desc_user5@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/descriptors/extract/nonexistent-uuid", headers=headers)
    assert res.status_code == 404
    assert res.get_json()["success"] is False


def test_batch_extract_descriptors(client):
    token, _ = get_auth_token(client, "desc_batch@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    img_id1 = upload_sample_image(client, headers)
    img_id2 = upload_sample_image(client, headers)

    batch_payload = {
        "image_ids": [img_id1, img_id2, "nonexistent-3"],
        "feature_types": ["color_histogram", "glcm"],
        "force": False,
    }

    res = client.post("/api/v1/descriptors/extract-batch", json=batch_payload, headers=headers)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert json_data["total"] == 3
    assert json_data["indexed"] == 2
    assert json_data["failed"] == 1

    results = json_data["results"]
    assert results[0]["image_id"] == img_id1
    assert results[0]["status"] == "indexed"
    assert results[1]["image_id"] == img_id2
    assert results[1]["status"] == "indexed"
    assert results[2]["image_id"] == "nonexistent-3"
    assert results[2]["status"] == "failed"


def test_batch_extract_over_limit_returns_400(client):
    token, _ = get_auth_token(client, "desc_limit@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    too_many_ids = [f"uuid-{i}" for i in range(51)]
    res = client.post(
        "/api/v1/descriptors/extract-batch",
        json={"image_ids": too_many_ids},
        headers=headers,
    )
    assert res.status_code == 400
    assert res.get_json()["success"] is False
    assert "exceeds maximum limit" in res.get_json()["error"]
