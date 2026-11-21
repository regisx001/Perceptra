import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_

from src.extensions import db
from src.models.category import Category
from src.models.image import Image
from src.models.image_feature import ImageFeature
from src.models.retrieval import (
    RetrievalQuery,
    RetrievalIteration,
    RetrievalResult,
    RelevanceFeedback,
)
from src.services.descriptor_engine import (
    DescriptorEngine,
    EXTRACTOR_VERSION,
    InvalidImageStreamError,
    SUPPORTED_FEATURE_TYPES,
)
from src.services.relevance_feedback import FeatureRelevanceEstimator
from src.services.similarity_engine import SimilarityEngine
from src.services.storage import Storage

logger = logging.getLogger(__name__)

# In-memory query session cache for interactive relevance feedback iterations
# Evicted after 2 hours or when max capacity is reached
_QUERY_SESSIONS: Dict[str, Dict[str, Any]] = {}
MAX_CACHED_SESSIONS = 500


class QueryServiceError(Exception):
    """Base exception for query service errors."""
    status_code = 400

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class QueryService:
    """
    Coordinates multi-descriptor image retrieval, scope filtering, on-the-fly feature
    extraction, similarity ranking, and Group 13 relevance feedback iterations.
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    def search(
        self,
        user_id: str,
        query_bytes: Optional[bytes] = None,
        query_image_id: Optional[str] = None,
        scope: str = "both",
        category_id: Optional[str] = None,
        top_k: int = 12,
        metric: str = "cosine",
        normalization: str = "none",
        descriptors: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an initial visual query and returns ranked nearest neighbors.
        """
        t_start = time.perf_counter()

        # Validate inputs
        top_k = max(1, min(50, int(top_k)))
        if metric not in {"cosine", "euclidean"}:
            metric = "cosine"
        if normalization not in {"none", "minmax", "standard"}:
            normalization = "none"

        active_descriptors = [d for d in (descriptors or list(SUPPORTED_FEATURE_TYPES)) if d in SUPPORTED_FEATURE_TYPES]
        if not active_descriptors:
            active_descriptors = list(SUPPORTED_FEATURE_TYPES)

        # 1. Resolve Query Features
        t_extract_start = time.perf_counter()
        query_features: Dict[str, List[float]] = {}
        query_img_meta: Dict[str, Any] = {}

        if query_bytes:
            try:
                extracted = DescriptorEngine.extract(query_bytes, feature_types=active_descriptors)
                for ft, (params, fvalues) in extracted.items():
                    query_features[ft] = fvalues["vector"]
                query_img_meta = {
                    "source": "upload",
                    "filename": "query_upload.jpg",
                }
            except Exception as e:
                raise QueryServiceError(f"Failed to process uploaded query image: {str(e)}", status_code=422)

        elif query_image_id:
            ref_image = Image.query.filter_by(id=query_image_id).first()
            if not ref_image:
                raise QueryServiceError(f"Query image ID '{query_image_id}' not found.", status_code=404)

            # Check existing features in DB
            db_features = ImageFeature.query.filter_by(image_id=query_image_id).all()
            for f in db_features:
                if f.feature_type in active_descriptors and "vector" in f.feature_values:
                    query_features[f.feature_type] = f.feature_values["vector"]

            # If any active descriptor is missing, extract from storage
            missing = [d for d in active_descriptors if d not in query_features]
            if missing:
                try:
                    raw_bytes = self.storage.read_bytes(ref_image.storage_key)
                    extracted = DescriptorEngine.extract(raw_bytes, feature_types=missing)
                    for ft, (params, fvalues) in extracted.items():
                        query_features[ft] = fvalues["vector"]
                        # Persist for next queries
                        new_feat = ImageFeature(
                            image_id=ref_image.id,
                            feature_type=ft,
                            extractor_version=EXTRACTOR_VERSION,
                            feature_values=fvalues,
                            parameters=params,
                        )
                        db.session.add(new_feat)
                    db.session.commit()
                except Exception as e:
                    logger.warning(f"Could not extract missing descriptors for image {query_image_id}: {e}")

            query_img_meta = {
                "source": "existing",
                "id": ref_image.id,
                "filename": ref_image.filename,
                "category_id": ref_image.category_id,
                "category_name": ref_image.category.name if ref_image.category else None,
                "width": ref_image.width,
                "height": ref_image.height,
            }
        else:
            raise QueryServiceError("Either query_bytes or query_image_id must be provided.", status_code=400)

        t_extract = (time.perf_counter() - t_extract_start) * 1000.0

        # Default weights
        if not weights:
            active_weights = {d: round(1.0 / len(active_descriptors), 4) for d in active_descriptors}
        else:
            total_w = sum(weights.get(d, 0.0) for d in active_descriptors) or 1.0
            active_weights = {d: round(weights.get(d, 0.0) / total_w, 4) for d in active_descriptors}

        # 2. Candidate Filtering
        t_sim_start = time.perf_counter()
        img_query = Image.query

        # Scope filter
        if scope == "ghim10k":
            img_query = img_query.filter(or_(Image.source_type == "dataset", Image.owner_id.is_(None)))
        elif scope == "my_images":
            img_query = img_query.filter(Image.owner_id == user_id)
        else:  # both
            img_query = img_query.filter(
                or_(
                    Image.source_type == "dataset",
                    Image.owner_id.is_(None),
                    Image.owner_id == user_id,
                )
            )

        # Category filter
        if category_id and category_id.strip() and category_id != "all":
            img_query = img_query.filter(Image.category_id == category_id.strip())

        # Exclude self if query was an existing image
        if query_image_id:
            img_query = img_query.filter(Image.id != query_image_id)

        candidate_images = img_query.all()
        candidate_ids = [img.id for img in candidate_images]

        if not candidate_ids:
            t_total = (time.perf_counter() - t_start) * 1000.0
            return {
                "success": True,
                "session_id": str(uuid.uuid4()),
                "query_image": query_img_meta,
                "execution_time_ms": {
                    "extraction_ms": round(t_extract, 2),
                    "similarity_ms": 0.0,
                    "total_ms": round(t_total, 2),
                },
                "active_weights": active_weights,
                "results": [],
                "total_candidates": 0,
            }

        # 3. Fetch candidate feature vectors in bulk
        features_records = ImageFeature.query.filter(
            ImageFeature.image_id.in_(candidate_ids),
            ImageFeature.feature_type.in_(active_descriptors),
        ).all()

        candidate_features_map: Dict[str, Dict[str, List[float]]] = {}
        for rec in features_records:
            if "vector" in rec.feature_values:
                if rec.image_id not in candidate_features_map:
                    candidate_features_map[rec.image_id] = {}
                candidate_features_map[rec.image_id][rec.feature_type] = rec.feature_values["vector"]

        # 4. Compute similarity and rank
        scored_candidates: List[Dict[str, Any]] = []
        image_dict = {img.id: img for img in candidate_images}

        for img_id, c_feats in candidate_features_map.items():
            overall_sim, color_sim, texture_sim, feature_scores = (
                SimilarityEngine.aggregate_multi_feature_similarity(
                    query_features=query_features,
                    candidate_features=c_feats,
                    weights=active_weights,
                    metric=metric,
                    normalization=normalization,
                )
            )

            img_obj = image_dict.get(img_id)
            if img_obj:
                scored_candidates.append({
                    "image_id": img_id,
                    "filename": img_obj.filename,
                    "category_id": img_obj.category_id,
                    "category": img_obj.category.name if img_obj.category else "Uncategorized",
                    "source_type": img_obj.source_type,
                    "dimensions": f"{img_obj.width}x{img_obj.height}" if img_obj.width and img_obj.height else "Unknown",
                    "file_size": img_obj.file_size,
                    "overall_similarity": overall_sim,
                    "color_similarity": color_sim,
                    "texture_similarity": texture_sim,
                    "feature_scores": feature_scores,
                })

        # Rank descending by overall similarity
        scored_candidates.sort(key=lambda x: x["overall_similarity"], reverse=True)
        top_results = scored_candidates[:top_k]

        # Assign rank 1..K
        for idx, item in enumerate(top_results, start=1):
            item["rank"] = idx

        t_sim = (time.perf_counter() - t_sim_start) * 1000.0
        t_total = (time.perf_counter() - t_start) * 1000.0

        # 5. Persist Retrieval Query, Iteration 0, and Results in Database
        session_id = str(uuid.uuid4())
        query_record_id = session_id  # Align query record ID with session ID for seamless linking
        query_storage_key = None

        if query_bytes:
            # Save query image in queries/<user_id>/<query_id>.jpg
            try:
                query_storage_key = f"queries/{user_id}/{query_record_id}.jpg"
                self.storage.save(query_storage_key, query_bytes, content_type="image/jpeg", overwrite=True)
            except Exception as e:
                logger.warning(f"Could not persist uploaded query image to storage: {e}")

        try:
            now_utc = datetime.now(timezone.utc)
            db_query = RetrievalQuery(
                id=query_record_id,
                user_id=user_id,
                query_image_id=query_image_id,
                query_storage_key=query_storage_key,
                query_source="upload" if query_bytes else "gallery",
                search_scope=scope,
                configuration={
                    "top_k": top_k,
                    "metric": metric,
                    "normalization": normalization,
                    "descriptors": active_descriptors,
                    "category_id": category_id,
                },
                status="completed",
                created_at=now_utc,
                completed_at=now_utc,
            )
            db.session.add(db_query)

            db_iteration_0 = RetrievalIteration(
                id=str(uuid.uuid4()),
                query_id=query_record_id,
                iteration_number=0,
                retrieval_method="initial",
                feature_weights=active_weights,
                updated_query_vector=query_features,
                feedback_count=0,
                execution_time_ms=int(t_total),
                total_candidates=len(candidate_features_map),
                results_count=len(top_results),
                created_at=now_utc,
            )
            db.session.add(db_iteration_0)
            db.session.flush()

            for item in top_results:
                db_res = RetrievalResult(
                    id=str(uuid.uuid4()),
                    iteration_id=db_iteration_0.id,
                    image_id=item["image_id"],
                    rank=item["rank"],
                    similarity_score=float(item["overall_similarity"]),
                    feature_scores=item.get("feature_scores"),
                    created_at=now_utc,
                )
                db.session.add(db_res)

            db.session.commit()
            iter_0_id = db_iteration_0.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to persist retrieval query in DB: {e}", exc_info=True)
            iter_0_id = None

        # 6. Create In-Memory Query Session for Fast Relevance Feedback iterations
        cls = self.__class__
        cls._store_session(
            session_id=session_id,
            data={
                "session_id": session_id,
                "query_record_id": query_record_id,
                "latest_iteration_id": iter_0_id,
                "user_id": user_id,
                "query_image": query_img_meta,
                "query_features": query_features,
                "active_descriptors": active_descriptors,
                "weights": active_weights,
                "metric": metric,
                "normalization": normalization,
                "scope": scope,
                "category_id": category_id,
                "top_k": top_k,
                "candidate_features_map": candidate_features_map,
                "image_dict": {
                    k: {
                        "id": v.id,
                        "filename": v.filename,
                        "category_id": v.category_id,
                        "category": v.category.name if v.category else "Uncategorized",
                        "source_type": v.source_type,
                        "dimensions": f"{v.width}x{v.height}" if v.width and v.height else "Unknown",
                        "file_size": v.file_size,
                    }
                    for k, v in image_dict.items()
                },
                "iterations": 0,
                "created_at": time.time(),
            },
        )

        return {
            "success": True,
            "session_id": session_id,
            "query_image": query_img_meta,
            "execution_time_ms": {
                "extraction_ms": round(t_extract, 2),
                "similarity_ms": round(t_sim, 2),
                "total_ms": round(t_total, 2),
            },
            "active_weights": active_weights,
            "results": top_results,
            "total_candidates": len(candidate_features_map),
        }

    def feedback(
        self,
        user_id: str,
        session_id: str,
        relevant_ids: List[str],
        irrelevant_ids: List[str],
        iteration: int = 1,
    ) -> Dict[str, Any]:
        """
        Applies Group 13 Feature Relevance Estimation on collected feedback,
        re-estimates descriptor weights, updates the query centroid, and recalculates ranking.
        """
        t_start = time.perf_counter()
        session = self._get_session(session_id)
        if not session:
            raise QueryServiceError("Search session expired or not found. Please run a new visual query.", status_code=404)

        if session["user_id"] != user_id:
            raise QueryServiceError("Unauthorized session access.", status_code=403)

        query_features = session["query_features"]
        candidate_features_map = session["candidate_features_map"]
        image_dict = session["image_dict"]
        prior_weights = session["weights"]
        metric = session["metric"]
        normalization = session["normalization"]
        top_k = session["top_k"]

        # Collect features for relevant and irrelevant examples
        relevant_features = [
            candidate_features_map[rid]
            for rid in relevant_ids
            if rid in candidate_features_map
        ]
        irrelevant_features = [
            candidate_features_map[iid]
            for iid in irrelevant_ids
            if iid in candidate_features_map
        ]

        # Apply Group 13 Feature Relevance Estimation
        updated_weights, refined_query_features, diagnostics = (
            FeatureRelevanceEstimator.estimate_weights(
                query_features=query_features,
                relevant_features=relevant_features,
                irrelevant_features=irrelevant_features,
                prior_weights=prior_weights,
            )
        )

        # Recalculate similarities for all candidates with updated weights & refined centroid
        scored_candidates: List[Dict[str, Any]] = []
        for img_id, c_feats in candidate_features_map.items():
            overall_sim, color_sim, texture_sim, feature_scores = (
                SimilarityEngine.aggregate_multi_feature_similarity(
                    query_features=refined_query_features,
                    candidate_features=c_feats,
                    weights=updated_weights,
                    metric=metric,
                    normalization=normalization,
                )
            )

            img_data = image_dict.get(img_id, {})
            scored_candidates.append({
                "image_id": img_id,
                "filename": img_data.get("filename", "unknown"),
                "category_id": img_data.get("category_id"),
                "category": img_data.get("category", "Uncategorized"),
                "source_type": img_data.get("source_type", "dataset"),
                "dimensions": img_data.get("dimensions", "Unknown"),
                "file_size": img_data.get("file_size", 0),
                "overall_similarity": overall_sim,
                "color_similarity": color_sim,
                "texture_similarity": texture_sim,
                "feature_scores": feature_scores,
            })

        # Rank descending
        scored_candidates.sort(key=lambda x: x["overall_similarity"], reverse=True)
        top_results = scored_candidates[:top_k]

        for idx, item in enumerate(top_results, start=1):
            item["rank"] = idx

        # Calculate Precision@K based on user relevance feedback
        rel_set = set(relevant_ids)
        top_k_ids = [item["image_id"] for item in top_results]
        relevant_in_top_k = sum(1 for tid in top_k_ids if tid in rel_set)
        precision_at_k = round(relevant_in_top_k / max(1, len(top_results)), 4) if rel_set else None

        t_total = (time.perf_counter() - t_start) * 1000.0

        # Update session
        session["weights"] = updated_weights
        session["query_features"] = refined_query_features
        session["iterations"] = iteration

        # Persist feedback judgments and refined iteration in DB
        query_record_id = session.get("query_record_id")
        previous_iteration_id = session.get("latest_iteration_id")
        now_utc = datetime.now(timezone.utc)

        try:
            # 1. Save or update judgments in relevance_feedback table against previous_iteration_id
            if previous_iteration_id:
                for rid in relevant_ids:
                    fb = RelevanceFeedback.query.filter_by(
                        iteration_id=previous_iteration_id, image_id=rid
                    ).first()
                    if fb:
                        fb.judgment = "relevant"
                        fb.updated_at = now_utc
                    else:
                        db.session.add(
                            RelevanceFeedback(
                                id=str(uuid.uuid4()),
                                iteration_id=previous_iteration_id,
                                image_id=rid,
                                judgment="relevant",
                                created_at=now_utc,
                                updated_at=now_utc,
                            )
                        )

                for iid in irrelevant_ids:
                    fb = RelevanceFeedback.query.filter_by(
                        iteration_id=previous_iteration_id, image_id=iid
                    ).first()
                    if fb:
                        fb.judgment = "irrelevant"
                        fb.updated_at = now_utc
                    else:
                        db.session.add(
                            RelevanceFeedback(
                                id=str(uuid.uuid4()),
                                iteration_id=previous_iteration_id,
                                image_id=iid,
                                judgment="irrelevant",
                                created_at=now_utc,
                                updated_at=now_utc,
                            )
                        )

            # 2. Insert new iteration record (iteration >= 1)
            new_iter = RetrievalIteration(
                id=str(uuid.uuid4()),
                query_id=query_record_id,
                iteration_number=iteration,
                retrieval_method="fre",
                feature_weights=updated_weights,
                updated_query_vector=refined_query_features,
                feedback_count=len(relevant_ids) + len(irrelevant_ids),
                execution_time_ms=int(t_total),
                total_candidates=len(candidate_features_map),
                results_count=len(top_results),
                created_at=now_utc,
            )
            db.session.add(new_iter)
            db.session.flush()

            # 3. Insert refined results for this iteration
            for item in top_results:
                db.session.add(
                    RetrievalResult(
                        id=str(uuid.uuid4()),
                        iteration_id=new_iter.id,
                        image_id=item["image_id"],
                        rank=item["rank"],
                        similarity_score=float(item["overall_similarity"]),
                        feature_scores=item.get("feature_scores"),
                        created_at=now_utc,
                    )
                )

            db.session.commit()
            session["latest_iteration_id"] = new_iter.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to persist feedback iteration in DB: {e}", exc_info=True)

        return {
            "success": True,
            "session_id": session_id,
            "iteration": iteration,
            "execution_time_ms": round(t_total, 2),
            "updated_weights": updated_weights,
            "prior_weights": prior_weights,
            "diagnostics": diagnostics,
            "precision_at_k": precision_at_k,
            "results": top_results,
        }

    @classmethod
    def _store_session(cls, session_id: str, data: Dict[str, Any]):
        if len(_QUERY_SESSIONS) >= MAX_CACHED_SESSIONS:
            # Simple eviction: drop oldest 100 sessions
            keys = list(_QUERY_SESSIONS.keys())[:100]
            for k in keys:
                _QUERY_SESSIONS.pop(k, None)
        _QUERY_SESSIONS[session_id] = data

    @classmethod
    def _get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        return _QUERY_SESSIONS.get(session_id)
