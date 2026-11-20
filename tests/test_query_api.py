import io
import pytest
from PIL import Image as PILImage
from src.models.image import Image
from src.models.image_feature import ImageFeature
from src.services.descriptor_engine import DescriptorEngine, EXTRACTOR_VERSION


def create_test_image_bytes(color=(255, 0, 0)) -> bytes:
    img = PILImage.new("RGB", (64, 64), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_query_config_endpoint(client):
    res = client.get("/api/v1/query/config")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "color_descriptors" in data
    assert "texture_descriptors" in data
    assert "similarity_metrics" in data


def test_visual_query_and_feedback(client, db_session, app):
    # Register test user to get auth token
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "querytester@example.com", "password": "password123"},
    )
    assert reg.status_code == 201
    token = reg.get_json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 1. Create candidate images with extracted features in DB
    raw1 = create_test_image_bytes((255, 0, 0))  # Red
    raw2 = create_test_image_bytes((0, 255, 0))  # Green

    img1 = Image(
        id="cand-img-1",
        filename="red.jpg",
        storage_key="test/red.jpg",
        source_type="dataset",
        mime_type="image/jpeg",
        file_size=len(raw1),
        width=64,
        height=64,
        checksum="chk-red",
    )
    img2 = Image(
        id="cand-img-2",
        filename="green.jpg",
        storage_key="test/green.jpg",
        source_type="dataset",
        mime_type="image/jpeg",
        file_size=len(raw2),
        width=64,
        height=64,
        checksum="chk-green",
    )
    db_session.add_all([img1, img2])

    # Extract features for both
    for img_obj, raw in [(img1, raw1), (img2, raw2)]:
        ext = DescriptorEngine.extract(raw)
        for ft, (params, fvalues) in ext.items():
            feat = ImageFeature(
                image_id=img_obj.id,
                feature_type=ft,
                extractor_version=EXTRACTOR_VERSION,
                feature_values=fvalues,
                parameters=params,
            )
            db_session.add(feat)
    db_session.commit()

    # 2. Query with another Red image via file upload
    query_red = create_test_image_bytes((240, 10, 10))
    res = client.post(
        "/api/v1/query/search",
        headers=auth_headers,
        data={
            "file": (io.BytesIO(query_red), "query_red.jpg"),
            "scope": "both",
            "top_k": 5,
            "metric": "cosine",
        },
        content_type="multipart/form-data",
    )

    assert res.status_code == 200
    search_data = res.get_json()
    assert search_data["success"] is True
    assert "session_id" in search_data
    assert len(search_data["results"]) == 2

    # Red image (cand-img-1) must be ranked #1
    top_result = search_data["results"][0]
    assert top_result["image_id"] == "cand-img-1"
    assert top_result["rank"] == 1
    assert top_result["overall_similarity"] > search_data["results"][1]["overall_similarity"]

    session_id = search_data["session_id"]

    # 3. Submit Relevance Feedback
    fb_res = client.post(
        "/api/v1/query/feedback",
        headers=auth_headers,
        json={
            "session_id": session_id,
            "relevant_ids": ["cand-img-1"],
            "irrelevant_ids": ["cand-img-2"],
            "iteration": 1,
        },
    )

    assert fb_res.status_code == 200
    fb_data = fb_res.get_json()
    assert fb_data["success"] is True
    assert "updated_weights" in fb_data
    assert fb_data["iteration"] == 1
    assert fb_data["results"][0]["image_id"] == "cand-img-1"
