import pytest
import io
import json
from src.models.user import User
from src.models.image import Image
from src.models.image_feature import ImageFeature
from src.models.retrieval import RetrievalQuery, RetrievalIteration, RetrievalResult, RelevanceFeedback
from src.services.descriptor_engine import EXTRACTOR_VERSION


@pytest.fixture
def auth_client_and_user(app, client):
    with app.app_context():
        user = User(email="retrieval_tester@example.com")
        user.set_password("SecurePass123!")
        from src.extensions import db
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "retrieval_tester@example.com", "password": "SecurePass123!"},
    )
    token = res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return client, headers, user_id


def test_retrieval_history_and_analytics_flow(app, auth_client_and_user):
    client, headers, user_id = auth_client_and_user

    # 1. Seed two images with color_histogram features
    with app.app_context():
        from src.extensions import db
        img1 = Image(
            filename="ghim_chair_01.jpg",
            storage_key="dataset/chair_01.jpg",
            source_type="dataset",
            mime_type="image/jpeg",
            file_size=1024,
            width=100,
            height=100,
            checksum="chk1",
        )
        img2 = Image(
            filename="ghim_chair_02.jpg",
            storage_key="dataset/chair_02.jpg",
            source_type="dataset",
            mime_type="image/jpeg",
            file_size=1024,
            width=100,
            height=100,
            checksum="chk2",
        )
        db.session.add_all([img1, img2])
        db.session.commit()

        # Dummy normalized vectors
        f1 = ImageFeature(
            image_id=img1.id,
            feature_type="color_histogram",
            extractor_version=EXTRACTOR_VERSION,
            feature_values={"vector": [0.5, 0.5]},
        )
        f2 = ImageFeature(
            image_id=img2.id,
            feature_type="color_histogram",
            extractor_version=EXTRACTOR_VERSION,
            feature_values={"vector": [0.6, 0.4]},
        )
        db.session.add_all([f1, f2])
        db.session.commit()
        ref_id = img1.id
        cand_id = img2.id

    # 2. Perform a search using existing image
    search_payload = {
        "image_id": ref_id,
        "descriptors": ["color_histogram"],
        "top_k": 5,
        "scope": "both",
    }
    res = client.post("/api/v1/query/search", json=search_payload, headers=headers)
    assert res.status_code == 200
    search_data = res.get_json()
    assert search_data["success"] is True
    session_id = search_data["session_id"]

    # 3. Submit Relevance Feedback
    feedback_payload = {
        "session_id": session_id,
        "relevant_ids": [cand_id],
        "irrelevant_ids": [],
        "iteration": 1,
    }
    fb_res = client.post("/api/v1/query/feedback", json=feedback_payload, headers=headers)
    assert fb_res.status_code == 200
    fb_data = fb_res.get_json()
    assert fb_data["iteration"] == 1

    # 4. Check Retrieval History list endpoint
    hist_res = client.get("/api/v1/retrieval-history", headers=headers)
    assert hist_res.status_code == 200
    hist_json = hist_res.get_json()
    assert len(hist_json["items"]) >= 1
    query_item = hist_json["items"][0]
    assert query_item["id"] == session_id
    assert query_item["iterations_count"] == 2  # iteration 0 + iteration 1

    # 5. Check Detailed Query history
    detail_res = client.get(f"/api/v1/retrieval-history/{session_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_json = detail_res.get_json()["query"]
    assert len(detail_json["iterations"]) == 2
    assert detail_json["iterations"][0]["iteration_number"] == 0
    assert detail_json["iterations"][1]["iteration_number"] == 1
    assert len(detail_json["iterations"][0]["feedback"]) == 1
    assert detail_json["iterations"][0]["feedback"][0]["judgment"] == "relevant"

    # 6. Check Analytics Endpoints
    overview_res = client.get("/api/v1/analytics/overview", headers=headers)
    assert overview_res.status_code == 200
    ov_data = overview_res.get_json()
    assert ov_data["total_searches"] >= 1
    assert ov_data["feedback_sessions"] >= 1
    assert ov_data["relevant_judgments"] >= 1

    activity_res = client.get("/api/v1/analytics/activity", headers=headers)
    assert activity_res.status_code == 200
    act_data = activity_res.get_json()
    assert len(act_data["activity_timeline"]) >= 1

    feedback_res = client.get("/api/v1/analytics/feedback", headers=headers)
    assert feedback_res.status_code == 200
    fb_analytics = feedback_res.get_json()
    assert fb_analytics["relevant_count"] >= 1

    performance_res = client.get("/api/v1/analytics/performance", headers=headers)
    assert performance_res.status_code == 200
    perf_data = performance_res.get_json()
    assert "average_ms" in perf_data
    assert "stage_breakdown" in perf_data
    assert "extraction_ms" in perf_data["stage_breakdown"]
    assert "db_fetch_ms" in perf_data["stage_breakdown"]
    assert "similarity_ms" in perf_data["stage_breakdown"]
    assert "reranking_ms" in perf_data["stage_breakdown"]
    assert len(perf_data["stage_breakdown"]["stages"]) == 4

    # 7. Delete Search history
    del_res = client.delete(f"/api/v1/retrieval-history/{session_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify 404 after delete
    check_del = client.get(f"/api/v1/retrieval-history/{session_id}", headers=headers)
    assert check_del.status_code == 404
