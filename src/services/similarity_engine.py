import math
from typing import Dict, List, Optional, Tuple
import numpy as np

COLOR_FEATURE_TYPES = {"color_histogram", "color_moments", "dominant_colors"}
TEXTURE_FEATURE_TYPES = {"glcm", "lbp_histogram"}


class SimilarityEngine:
    """
    Computes vector distances, normalizations, and multi-feature similarity aggregations.
    """

    @staticmethod
    def normalize_vector(vec: np.ndarray, method: str = "none") -> np.ndarray:
        """
        Applies feature scaling/normalization to a numeric vector.
        Methods: 'none', 'minmax', 'standard'
        """
        arr = np.asarray(vec, dtype=np.float64)
        if arr.size == 0 or method == "none":
            return arr

        if method == "minmax":
            v_min = float(np.min(arr))
            v_max = float(np.max(arr))
            spread = v_max - v_min
            if spread > 1e-9:
                return (arr - v_min) / spread
            return np.zeros_like(arr)

        if method == "standard":
            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr))
            if std_val > 1e-9:
                return (arr - mean_val) / std_val
            return arr - mean_val

        return arr

    @classmethod
    def compute_similarity(
        cls,
        vec_q: List[float],
        vec_c: List[float],
        metric: str = "cosine",
        normalization: str = "none",
    ) -> float:
        """
        Computes similarity in [0, 1] between query vector and candidate vector.
        Higher score = more visually similar.
        """
        q = cls.normalize_vector(np.asarray(vec_q, dtype=np.float64), method=normalization)
        c = cls.normalize_vector(np.asarray(vec_c, dtype=np.float64), method=normalization)

        if q.size == 0 or c.size == 0 or q.shape != c.shape:
            return 0.0

        if metric == "cosine":
            norm_q = float(np.linalg.norm(q))
            norm_c = float(np.linalg.norm(c))
            if norm_q < 1e-12 or norm_c < 1e-12:
                return 0.0
            dot = float(np.dot(q, c))
            cos_val = dot / (norm_q * norm_c)
            # Clip numerical precision errors
            cos_val = max(-1.0, min(1.0, cos_val))
            # Map [-1, 1] to [0, 1]
            return round((1.0 + cos_val) / 2.0, 4)

        if metric == "euclidean":
            dist = float(np.linalg.norm(q - c))
            # Invert Euclidean distance to similarity in [0, 1]
            sim = 1.0 / (1.0 + dist)
            return round(max(0.0, min(1.0, sim)), 4)

        # Fallback to cosine
        norm_q = float(np.linalg.norm(q))
        norm_c = float(np.linalg.norm(c))
        if norm_q < 1e-12 or norm_c < 1e-12:
            return 0.0
        return round(float(np.dot(q, c) / (norm_q * norm_c)), 4)

    @classmethod
    def aggregate_multi_feature_similarity(
        cls,
        query_features: Dict[str, List[float]],
        candidate_features: Dict[str, List[float]],
        weights: Dict[str, float],
        metric: str = "cosine",
        normalization: str = "none",
    ) -> Tuple[float, float, float, Dict[str, float]]:
        """
        Aggregates individual descriptor scores using convex weights:
        S(q, i) = sum(w_j * S_j(q, i))

        Returns:
            (overall_similarity, color_similarity, texture_similarity, per_feature_scores)
        """
        feature_scores: Dict[str, float] = {}
        active_weights: Dict[str, float] = {}

        # 1. Compute individual descriptor similarities for all common features
        for ftype, q_vec in query_features.items():
            if ftype in candidate_features and ftype in weights:
                c_vec = candidate_features[ftype]
                sim = cls.compute_similarity(q_vec, c_vec, metric=metric, normalization=normalization)
                feature_scores[ftype] = sim
                active_weights[ftype] = max(0.0, float(weights.get(ftype, 0.0)))

        # Normalize active weights to sum to 1.0
        total_w = sum(active_weights.values())
        if total_w > 1e-9:
            norm_weights = {k: v / total_w for k, v in active_weights.items()}
        else:
            n = len(feature_scores) or 1
            norm_weights = {k: 1.0 / n for k in feature_scores}

        # 2. Overall similarity = weighted sum
        overall_sim = sum(norm_weights[k] * feature_scores[k] for k in norm_weights)

        # 3. Family breakdowns: Color & Texture
        color_scores = [feature_scores[k] for k in feature_scores if k in COLOR_FEATURE_TYPES]
        texture_scores = [feature_scores[k] for k in feature_scores if k in TEXTURE_FEATURE_TYPES]

        color_sim = float(np.mean(color_scores)) if color_scores else overall_sim
        texture_sim = float(np.mean(texture_scores)) if texture_scores else overall_sim

        return (
            round(overall_sim, 4),
            round(color_sim, 4),
            round(texture_sim, 4),
            {k: round(v, 4) for k, v in feature_scores.items()},
        )
