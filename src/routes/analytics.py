import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func, desc

from src.extensions import db
from src.models.image import Image
from src.models.retrieval import (
    RetrievalQuery,
    RetrievalIteration,
    RetrievalResult,
    RelevanceFeedback,
)
from src.services.storage import Storage

logger = logging.getLogger(__name__)
history_bp = Blueprint("history", __name__)
analytics_bp = Blueprint("analytics", __name__)


def get_storage() -> Storage:
    cfg = current_app.config
    return Storage(
        root_dir=cfg.get("STORAGE_BASE_PATH", "storage"),
        protocol=cfg.get("STORAGE_PROTOCOL", "file"),
    )


# =========================================================================
# 1. Retrieval History Endpoints (/api/v1/retrieval-history)
# =========================================================================

@history_bp.route("", methods=["GET"])
@jwt_required()
def list_history():
    """
    List user's previous visual searches with pagination and query previews.
    """
    user_id = str(get_jwt_identity())
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 15))))
    status_filter = request.args.get("status")

    query = RetrievalQuery.query.filter_by(user_id=user_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(desc(RetrievalQuery.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = []
    for q in pagination.items:
        data = q.to_dict(include_iterations=False)
        # Include reference query image details if available
        if q.query_image:
            data["query_image"] = {
                "id": q.query_image.id,
                "filename": q.query_image.filename,
                "width": q.query_image.width,
                "height": q.query_image.height,
            }
        items.append(data)

    return jsonify({
        "success": True,
        "items": items,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        },
    }), 200


@history_bp.route("/<string:query_id>", methods=["GET"])
@jwt_required()
def get_history_detail(query_id: str):
    """
    Retrieve complete search history for a query, including its iterations, results, and feedback.
    """
    user_id = str(get_jwt_identity())
    retrieval_q = RetrievalQuery.query.filter_by(id=query_id, user_id=user_id).first()
    if not retrieval_q:
        return jsonify({"success": False, "error": "Retrieval query not found"}), 404

    data = retrieval_q.to_dict(include_iterations=True)
    if retrieval_q.query_image:
        data["query_image"] = {
            "id": retrieval_q.query_image.id,
            "filename": retrieval_q.query_image.filename,
            "width": retrieval_q.query_image.width,
            "height": retrieval_q.query_image.height,
        }
    return jsonify({"success": True, "query": data}), 200


@history_bp.route("/<string:query_id>/file", methods=["GET"])
@jwt_required()
def get_query_file(query_id: str):
    """
    Stream the uploaded query image bytes if it was an uploaded search.
    """
    user_id = str(get_jwt_identity())
    retrieval_q = RetrievalQuery.query.filter_by(id=query_id, user_id=user_id).first()
    if not retrieval_q:
        return jsonify({"success": False, "error": "Retrieval query not found"}), 404

    if not retrieval_q.query_storage_key:
        return jsonify({"success": False, "error": "No uploaded query image for this search"}), 404

    storage = get_storage()
    if not storage.exists(retrieval_q.query_storage_key):
        return jsonify({"success": False, "error": "Query image file missing from storage"}), 404

    stream = storage.open(retrieval_q.query_storage_key, mode="rb")
    return send_file(stream, mimetype="image/jpeg")


@history_bp.route("/<string:query_id>", methods=["DELETE"])
@jwt_required()
def delete_history_item(query_id: str):
    """
    Delete a search and its associated history, iterations, results, feedback, and storage key.
    """
    user_id = str(get_jwt_identity())
    retrieval_q = RetrievalQuery.query.filter_by(id=query_id, user_id=user_id).first()
    if not retrieval_q:
        return jsonify({"success": False, "error": "Retrieval query not found"}), 404

    try:
        # Delete temporary storage key if present
        if retrieval_q.query_storage_key:
            storage = get_storage()
            storage.delete(retrieq_key := retrieval_q.query_storage_key)

        db.session.delete(retrieval_q)
        db.session.commit()
        return jsonify({"success": True, "message": "Retrieval query deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete retrieval query: {e}")
        return jsonify({"success": False, "error": f"Failed to delete search: {str(e)}"}), 500


@history_bp.route("/<string:query_id>/iterations", methods=["GET"])
@jwt_required()
def list_iterations(query_id: str):
    """
    Retrieve all iterations for a given search query.
    """
    user_id = str(get_jwt_identity())
    retrieval_q = RetrievalQuery.query.filter_by(id=query_id, user_id=user_id).first()
    if not retrieval_q:
        return jsonify({"success": False, "error": "Retrieval query not found"}), 404

    iters = [it.to_dict(include_results=True, include_feedback=True) for it in retrieval_q.iterations]
    return jsonify({"success": True, "iterations": iters}), 200


@history_bp.route("/<string:query_id>/iterations/<string:iteration_id>", methods=["GET"])
@jwt_required()
def get_iteration_detail(query_id: str, iteration_id: str):
    """
    Retrieve detail of a single iteration.
    """
    user_id = str(get_jwt_identity())
    retrieval_q = RetrievalQuery.query.filter_by(id=query_id, user_id=user_id).first()
    if not retrieval_q:
        return jsonify({"success": False, "error": "Retrieval query not found"}), 404

    iter_rec = RetrievalIteration.query.filter_by(id=iteration_id, query_id=query_id).first()
    if not iter_rec:
        return jsonify({"success": False, "error": "Iteration not found"}), 404

    return jsonify({"success": True, "iteration": iter_rec.to_dict(include_results=True, include_feedback=True)}), 200


# =========================================================================
# 2. Analytics Endpoints (/api/v1/analytics)
# =========================================================================

@analytics_bp.route("/overview", methods=["GET"])
@jwt_required()
def analytics_overview():
    """
    General retrieval KPIs: total searches, feedback sessions, average iterations,
    average retrieval latency, and feedback counts.
    """
    user_id = str(get_jwt_identity())

    # Total searches
    total_searches = RetrievalQuery.query.filter_by(user_id=user_id).count()

    # Query IDs for this user
    user_query_ids = [q.id for q in RetrievalQuery.query.filter_by(user_id=user_id).with_entities(RetrievalQuery.id).all()]

    if not user_query_ids:
        return jsonify({
            "success": True,
            "total_searches": 0,
            "feedback_sessions": 0,
            "average_iterations": 0.0,
            "average_retrieval_time_ms": 0.0,
            "failed_retrievals": 0,
            "total_feedback_judgments": 0,
            "relevant_judgments": 0,
            "irrelevant_judgments": 0,
        }), 200

    # Iterations belonging to user queries
    iterations_stats = db.session.query(
        func.count(RetrievalIteration.id),
        func.avg(RetrievalIteration.execution_time_ms)
    ).filter(RetrievalIteration.query_id.in_(user_query_ids)).first()

    total_iterations = iterations_stats[0] or 0
    avg_latency = round(float(iterations_stats[1] or 0.0), 2)
    avg_iterations = round(total_iterations / max(1, total_searches), 2)

    # Searches with feedback (iterations > 1 or feedback_count > 0)
    feedback_sessions = db.session.query(RetrievalIteration.query_id).filter(
        RetrievalIteration.query_id.in_(user_query_ids),
        RetrievalIteration.iteration_number > 0
    ).distinct().count()

    # Failed queries
    failed_retrievals = RetrievalQuery.query.filter_by(user_id=user_id, status="failed").count()

    # Total judgments
    user_iter_ids = [i.id for i in RetrievalIteration.query.filter(RetrievalIteration.query_id.in_(user_query_ids)).with_entities(RetrievalIteration.id).all()]

    rel_count = 0
    irrel_count = 0
    if user_iter_ids:
        rel_count = RelevanceFeedback.query.filter(
            RelevanceFeedback.iteration_id.in_(user_iter_ids),
            RelevanceFeedback.judgment == "relevant"
        ).count()
        irrel_count = RelevanceFeedback.query.filter(
            RelevanceFeedback.iteration_id.in_(user_iter_ids),
            RelevanceFeedback.judgment == "irrelevant"
        ).count()

    return jsonify({
        "success": True,
        "total_searches": total_searches,
        "feedback_sessions": feedback_sessions,
        "average_iterations": avg_iterations,
        "average_retrieval_time_ms": avg_latency,
        "failed_retrievals": failed_retrievals,
        "total_feedback_judgments": rel_count + irrel_count,
        "relevant_judgments": rel_count,
        "irrelevant_judgments": irrel_count,
    }), 200


@analytics_bp.route("/activity", methods=["GET"])
@jwt_required()
def analytics_activity():
    """
    Search activity aggregated over time, scopes, and similarity metrics.
    """
    user_id = str(get_jwt_identity())
    queries = RetrievalQuery.query.filter_by(user_id=user_id).order_by(RetrievalQuery.created_at.asc()).all()

    # 1. Activity by date (YYYY-MM-DD)
    date_map: Dict[str, Dict[str, int]] = {}
    for q in queries:
        d_str = q.created_at.strftime("%Y-%m-%d") if q.created_at else "Unknown"
        if d_str not in date_map:
            date_map[d_str] = {"date": d_str, "searches": 0, "iterations": 0}
        date_map[d_str]["searches"] += 1
        date_map[d_str]["iterations"] += len(q.iterations)

    activity_timeline = list(date_map.values())

    # 2. Breakdown by scope
    scope_dist: Dict[str, int] = {}
    for q in queries:
        s = q.search_scope or "all"
        scope_dist[s] = scope_dist.get(s, 0) + 1

    # 3. Metric breakdown
    metric_dist: Dict[str, int] = {}
    for q in queries:
        cfg = q.configuration or {}
        m = cfg.get("metric", "cosine")
        metric_dist[m] = metric_dist.get(m, 0) + 1

    return jsonify({
        "success": True,
        "activity_timeline": activity_timeline,
        "scope_distribution": scope_dist,
        "metric_distribution": metric_dist,
    }), 200


@analytics_bp.route("/feedback", methods=["GET"])
@jwt_required()
def analytics_feedback():
    """
    Detailed relevance feedback statistics and FRE weight progressions.
    """
    user_id = str(get_jwt_identity())
    user_query_ids = [q.id for q in RetrievalQuery.query.filter_by(user_id=user_id).with_entities(RetrievalQuery.id).all()]

    if not user_query_ids:
        return jsonify({
            "success": True,
            "relevant_count": 0,
            "irrelevant_count": 0,
            "ratio": 0.0,
            "average_judgments_per_search": 0.0,
            "feature_weight_evolution": {},
            "recent_iterations_comparison": [],
        }), 200

    iterations = RetrievalIteration.query.filter(
        RetrievalIteration.query_id.in_(user_query_ids)
    ).order_by(RetrievalIteration.created_at.desc()).limit(100).all()

    iter_ids = [it.id for it in iterations]
    judgments = RelevanceFeedback.query.filter(RelevanceFeedback.iteration_id.in_(iter_ids)).all()

    rel_count = sum(1 for j in judgments if j.judgment == "relevant")
    irrel_count = sum(1 for j in judgments if j.judgment == "irrelevant")
    total_judgments = len(judgments)
    ratio = round(rel_count / max(1, irrel_count), 2)
    avg_judgments = round(total_judgments / max(1, len(user_query_ids)), 2)

    # Average feature weights by iteration number (0, 1, 2)
    weight_accum: Dict[str, Dict[str, List[float]]] = {}
    for it in iterations:
        it_key = f"Iteration {it.iteration_number}"
        if it_key not in weight_accum:
            weight_accum[it_key] = {}
        if it.feature_weights and isinstance(it.feature_weights, dict):
            for feat, val in it.feature_weights.items():
                if feat not in weight_accum[it_key]:
                    weight_accum[it_key][feat] = []
                weight_accum[it_key][feat].append(float(val))

    feature_weight_evolution = {}
    for it_key, feat_dict in weight_accum.items():
        feature_weight_evolution[it_key] = {
            feat: round(sum(vals) / len(vals), 4) for feat, vals in feat_dict.items()
        }

    return jsonify({
        "success": True,
        "relevant_count": rel_count,
        "irrelevant_count": irrel_count,
        "ratio": ratio,
        "average_judgments_per_search": avg_judgments,
        "feature_weight_evolution": feature_weight_evolution,
    }), 200


@analytics_bp.route("/descriptors", methods=["GET"])
@jwt_required()
def analytics_descriptors():
    """
    Descriptor usage, configuration preferences, and average latencies.
    """
    user_id = str(get_jwt_identity())
    queries = RetrievalQuery.query.filter_by(user_id=user_id).all()

    descriptor_usage: Dict[str, int] = {}
    color_searches = 0
    texture_searches = 0
    hybrid_searches = 0

    for q in queries:
        cfg = q.configuration or {}
        descs = cfg.get("descriptors") or []
        has_color = any(d in descs for d in ["color_histogram", "color_moments", "dominant_colors"])
        has_texture = any(d in descs for d in ["glcm", "lbp_histogram"])

        if has_color and has_texture:
            hybrid_searches += 1
        elif has_color:
            color_searches += 1
        elif has_texture:
            texture_searches += 1

        for d in descs:
            descriptor_usage[d] = descriptor_usage.get(d, 0) + 1

    return jsonify({
        "success": True,
        "descriptor_usage": descriptor_usage,
        "categories": {
            "hybrid": hybrid_searches,
            "color_only": color_searches,
            "texture_only": texture_searches,
        },
    }), 200


@analytics_bp.route("/performance", methods=["GET"])
@jwt_required()
def analytics_performance():
    """
    Retrieval latency distribution and candidate throughput.
    """
    user_id = str(get_jwt_identity())
    user_query_ids = [q.id for q in RetrievalQuery.query.filter_by(user_id=user_id).with_entities(RetrievalQuery.id).all()]

    if not user_query_ids:
        return jsonify({
            "success": True,
            "average_ms": 0,
            "min_ms": 0,
            "max_ms": 0,
            "recent_latencies": [],
        }), 200

    iterations = RetrievalIteration.query.filter(
        RetrievalIteration.query_id.in_(user_query_ids)
    ).order_by(RetrievalIteration.created_at.desc()).limit(30).all()

    times = [it.execution_time_ms for it in iterations if it.execution_time_ms is not None]

    return jsonify({
        "success": True,
        "average_ms": round(sum(times) / max(1, len(times)), 1) if times else 0,
        "min_ms": min(times) if times else 0,
        "max_ms": max(times) if times else 0,
        "recent_latencies": [
            {
                "iteration_id": it.id,
                "iteration_number": it.iteration_number,
                "execution_time_ms": it.execution_time_ms,
                "candidates": it.total_candidates,
                "results": it.results_count,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
            for it in iterations[:15]
        ],
    }), 200
