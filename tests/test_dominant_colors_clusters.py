import io
import pytest
from PIL import Image as PILImage
from tests.test_categories import get_auth_token
from src.services.descriptor_engine import DescriptorEngine, SUPPORTED_FEATURE_TYPES


def create_test_image_bytes(size=(64, 64), color="blue") -> bytes:
    buf = io.BytesIO()
    img = PILImage.new("RGB", size, color=color)
    img.save(buf, format="JPEG")
    return buf.getvalue()


def upload_sample_image(client, headers) -> str:
    img_data = create_test_image_bytes(size=(48, 48), color="teal")
    data = {
        "file": (io.BytesIO(img_data), "sample_cluster_test.jpg"),
    }
    res = client.post("/api/v1/images", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 201
    return res.get_json()["image"]["id"]


# ============================================================================
# 1. DescriptorEngine K-Means Cluster Unit Tests (k=5, k=10, k=20)
# ============================================================================

def test_engine_dominant_colors_k5():
    img_bytes = create_test_image_bytes(color="magenta")
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

    total_pct = sum(cl["percentage"] for cl in clusters)
    assert abs(total_pct - 100.0) < 1.0

    # 5 clusters * 4 (r, g, b, weight) = 20-dim feature vector
    assert len(f_vals["vector"]) == 20


def test_engine_dominant_colors_k10():
    img_bytes = create_test_image_bytes(color="cyan")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_dominant_colors(rgb_arr, k=10)

    assert params["k"] == 10
    assert params["color_space"] == "RGB"

    clusters = f_vals["clusters"]
    assert len(clusters) == 10
    for rank, cl in enumerate(clusters, start=1):
        assert cl["rank"] == rank
        assert len(cl["rgb"]) == 3
        assert cl["hex"].startswith("#")
        assert 0.0 <= cl["percentage"] <= 100.0

    total_pct = sum(cl["percentage"] for cl in clusters)
    assert abs(total_pct - 100.0) < 1.0

    # 10 clusters * 4 (r, g, b, weight) = 40-dim feature vector
    assert len(f_vals["vector"]) == 40


def test_engine_dominant_colors_k20():
    img_bytes = create_test_image_bytes(color="gold")
    rgb_arr = DescriptorEngine.decode_image_rgb(img_bytes)
    params, f_vals = DescriptorEngine.extract_dominant_colors(rgb_arr, k=20)

    assert params["k"] == 20
    assert params["color_space"] == "RGB"

    clusters = f_vals["clusters"]
    assert len(clusters) == 20
    for rank, cl in enumerate(clusters, start=1):
        assert cl["rank"] == rank
        assert len(cl["rgb"]) == 3
        assert cl["hex"].startswith("#")
        assert 0.0 <= cl["percentage"] <= 100.0

    total_pct = sum(cl["percentage"] for cl in clusters)
    assert abs(total_pct - 100.0) < 1.0

    # 20 clusters * 4 (r, g, b, weight) = 80-dim feature vector
    assert len(f_vals["vector"]) == 80


def test_engine_extract_all_cluster_variations():
    assert "dominant_colors" in SUPPORTED_FEATURE_TYPES
    assert "dominant_colors_10" in SUPPORTED_FEATURE_TYPES
    assert "dominant_colors_20" in SUPPORTED_FEATURE_TYPES

    img_bytes = create_test_image_bytes(color="coral")
    results = DescriptorEngine.extract(img_bytes, ["dominant_colors", "dominant_colors_10", "dominant_colors_20"])

    assert "dominant_colors" in results
    assert "dominant_colors_10" in results
    assert "dominant_colors_20" in results

    assert len(results["dominant_colors"][1]["clusters"]) == 5
    assert len(results["dominant_colors"][1]["vector"]) == 20

    assert len(results["dominant_colors_10"][1]["clusters"]) == 10
    assert len(results["dominant_colors_10"][1]["vector"]) == 40

    assert len(results["dominant_colors_20"][1]["clusters"]) == 20
    assert len(results["dominant_colors_20"][1]["vector"]) == 80


# ============================================================================
# 2. REST API Integration Tests
# ============================================================================

def test_extract_k10_k20_api(client):
    token, _ = get_auth_token(client, "cluster_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    image_id = upload_sample_image(client, headers)

    res = client.post(
        f"/api/v1/descriptors/extract/{image_id}",
        json={"feature_types": ["dominant_colors_10", "dominant_colors_20"]},
        headers=headers,
    )
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True

    descriptors = json_data["descriptors"]
    assert "dominant_colors_10" in descriptors
    assert "dominant_colors_20" in descriptors

    assert len(descriptors["dominant_colors_10"]["clusters"]) == 10
    assert len(descriptors["dominant_colors_20"]["clusters"]) == 20


def test_query_config_includes_cluster_descriptors(client):
    res = client.get("/api/v1/query/config")
    assert res.status_code == 200
    json_data = res.get_json()

    descs = json_data["supported_descriptors"]
    assert "dominant_colors" in descs
