import json
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.services.descriptor_engine import SUPPORTED_FEATURE_TYPES
from src.services.query_service import QueryService, QueryServiceError
from src.services.storage import Storage

query_bp = Blueprint("query", __name__)


def get_query_service() -> QueryService:
    cfg = current_app.config
    storage = Storage(
        root_dir=cfg.get("STORAGE_BASE_PATH", "storage"),
        protocol=cfg.get("STORAGE_PROTOCOL", "file"),
    )
    return QueryService(storage=storage)


@query_bp.errorhandler(QueryServiceError)
def handle_query_error(err: QueryServiceError):
    return jsonify({"success": False, "error": str(err)}), err.status_code


@query_bp.route("/config", methods=["GET"])
def get_config():
    """
    Returns available descriptors, parameters, metrics, and default options for Visual Query.
    """
    return jsonify({
        "success": True,
        "supported_descriptors": sorted(list(SUPPORTED_FEATURE_TYPES)),
        "color_descriptors": ["color_histogram", "color_moments", "dominant_colors", "dominant_colors_10", "dominant_colors_20"],
        "texture_descriptors": ["glcm", "lbp_histogram"],
        "similarity_metrics": [
            {"id": "cosine", "label": "Cosine Similarity", "default": True},
            {"id": "euclidean", "label": "Euclidean Distance (Inverted)"},
        ],
        "normalization_methods": [
            {"id": "none", "label": "None (Raw Extracted Vector)", "default": True},
            {"id": "minmax", "label": "Min-Max Scaling [0, 1]"},
            {"id": "standard", "label": "Standardization (Z-Score)"},
        ],
        "search_scopes": [
            {"id": "both", "label": "All Images (Dataset + User Library)", "default": True},
            {"id": "ghim10k", "label": "GHIM-10K Reference Dataset"},
            {"id": "my_images", "label": "My Uploaded Images Only"},
        ],
        "default_top_k": 12,
        "max_top_k": 50,
        "descriptor_defaults": {
            "color_histogram": {"color_space": "HSV", "bins": 256, "channels": ["H", "S", "V"]},
            "color_moments": {"color_space": "HSV", "moments": ["mean", "std", "skewness"]},
            "dominant_colors": {"clusters": 5, "color_space": "RGB"},
            "glcm": {"levels": 32, "distances": [1], "angles": [0, 45, 90, 135]},
            "lbp_histogram": {"P": 8, "R": 1, "bins": 256, "method": "default"},
        },
    }), 200


@query_bp.route("/search", methods=["POST"])
@jwt_required()
def search():
    """
    Executes visual similarity search using uploaded file or existing image ID.
    Supports multipart/form-data and application/json.
    """
    user_id = str(get_jwt_identity())
    service = get_query_service()

    query_bytes = None
    query_image_id = None
    scope = "both"
    category_id = None
    top_k = 12
    metric = "cosine"
    normalization = "none"
    descriptors = None
    weights = None

    if request.is_json:
        data = request.get_json(silent=True) or {}
        query_image_id = data.get("image_id") or data.get("query_image_id")
        scope = data.get("scope", "both")
        category_id = data.get("category_id")
        top_k = data.get("top_k", 12)
        metric = data.get("metric", "cosine")
        normalization = data.get("normalization", "none")
        descriptors = data.get("descriptors")
        weights = data.get("weights")
    else:
        # Multipart / Form data
        if "file" in request.files:
            file_obj = request.files["file"]
            if file_obj and file_obj.filename:
                query_bytes = file_obj.read()

        query_image_id = request.form.get("image_id") or request.form.get("query_image_id")
        scope = request.form.get("scope", "both")
        category_id = request.form.get("category_id")
        top_k = request.form.get("top_k", 12)
        metric = request.form.get("metric", "cosine")
        normalization = request.form.get("normalization", "none")

        raw_desc = request.form.get("descriptors")
        if raw_desc:
            try:
                descriptors = json.loads(raw_desc)
            except Exception:
                descriptors = [d.strip() for d in raw_desc.split(",") if d.strip()]

        raw_weights = request.form.get("weights")
        if raw_weights:
            try:
                weights = json.loads(raw_weights)
            except Exception:
                weights = None

    result = service.search(
        user_id=user_id,
        query_bytes=query_bytes,
        query_image_id=query_image_id,
        scope=scope,
        category_id=category_id,
        top_k=int(top_k),
        metric=metric,
        normalization=normalization,
        descriptors=descriptors,
        weights=weights,
    )

    return jsonify(result), 200


@query_bp.route("/feedback", methods=["POST"])
@jwt_required()
def feedback():
    """
    Submits user relevance feedback (relevant vs. irrelevant) and runs Group 13
    Feature Relevance Estimation to update weights and re-rank results.
    """
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"success": False, "error": "session_id is required"}), 400

    relevant_ids = data.get("relevant_ids") or []
    irrelevant_ids = data.get("irrelevant_ids") or []
    iteration = int(data.get("iteration", 1))

    service = get_query_service()
    result = service.feedback(
        user_id=user_id,
        session_id=session_id,
        relevant_ids=relevant_ids,
        irrelevant_ids=irrelevant_ids,
        iteration=iteration,
    )

    return jsonify(result), 200
