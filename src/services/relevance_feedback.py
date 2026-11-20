from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class FeatureRelevanceEstimator:
    """
    Group 13 Assignment: Feature Relevance Estimation.
    Estimates descriptor relevance from user feedback (relevant vs. irrelevant examples)
    using dispersion analysis and discriminative variance ratios.
    """

    EPSILON = 1e-4

    @classmethod
    def estimate_weights(
        cls,
        query_features: Dict[str, List[float]],
        relevant_features: List[Dict[str, List[float]]],
        irrelevant_features: List[Dict[str, List[float]]],
        prior_weights: Optional[Dict[str, float]] = None,
        alpha_query: float = 0.7,
        beta_prior: float = 0.3,
    ) -> Tuple[Dict[str, float], Dict[str, List[float]], Dict[str, Any]]:
        """
        Estimates new feature weights and refined query centroid.

        Args:
            query_features: Dict of {feature_type: vector} for original query
            relevant_features: List of {feature_type: vector} for images marked relevant
            irrelevant_features: List of {feature_type: vector} for images marked irrelevant
            prior_weights: Current weight configuration (defaults to equal weights)
            alpha_query: Momentum for query centroid update (0.7 original, 0.3 relevant mean)
            beta_prior: Smoothing factor to blend prior weights (0.3 prior, 0.7 new estimate)

        Returns:
            (updated_weights, updated_query_features, diagnostic_stats)
        """
        active_features = list(query_features.keys())
        if not active_features:
            return {}, query_features, {}

        # Default prior weights to uniform distribution if not provided
        if not prior_weights:
            prior_weights = {ft: 1.0 / len(active_features) for ft in active_features}
        else:
            total_prior = sum(prior_weights.get(ft, 0.0) for ft in active_features) or 1.0
            prior_weights = {ft: prior_weights.get(ft, 0.0) / total_prior for ft in active_features}

        # If no relevant items were provided, return current weights and query untouched
        if not relevant_features:
            return prior_weights, query_features, {"message": "No relevant feedback provided."}

        raw_relevance_scores: Dict[str, float] = {}
        diagnostic_stats: Dict[str, Any] = {}
        updated_query_features: Dict[str, List[float]] = {}

        for ft in active_features:
            q_vec = np.asarray(query_features[ft], dtype=np.float64)

            # Collect relevant vectors for feature ft
            r_vecs = [
                np.asarray(img_feats[ft], dtype=np.float64)
                for img_feats in relevant_features
                if ft in img_feats and len(img_feats[ft]) == len(q_vec)
            ]

            # Collect irrelevant vectors for feature ft
            irr_vecs = [
                np.asarray(img_feats[ft], dtype=np.float64)
                for img_feats in irrelevant_features
                if ft in img_feats and len(img_feats[ft]) == len(q_vec)
            ]

            if not r_vecs:
                raw_relevance_scores[ft] = prior_weights.get(ft, 1.0 / len(active_features))
                updated_query_features[ft] = query_features[ft]
                continue

            r_mat = np.vstack(r_vecs)
            mu_r = np.mean(r_mat, axis=0)

            # Compute intra-class dispersion among relevant samples
            if len(r_vecs) > 1:
                # Average Euclidean distance from relevant mean
                diffs = r_mat - mu_r
                intra_variance = float(np.mean(np.sum(diffs ** 2, axis=1)))
                dispersion_r = np.sqrt(max(0.0, intra_variance))
            else:
                # If only 1 relevant sample, measure distance to query vector
                dispersion_r = float(np.linalg.norm(r_vecs[0] - q_vec))

            # Incorporate irrelevant samples if available for separability
            if irr_vecs:
                irr_mat = np.vstack(irr_vecs)
                mu_irr = np.mean(irr_mat, axis=0)
                between_distance = float(np.linalg.norm(mu_r - mu_irr))

                diffs_irr = irr_mat - mu_irr
                dispersion_irr = np.sqrt(max(0.0, float(np.mean(np.sum(diffs_irr ** 2, axis=1))))) if len(irr_vecs) > 1 else float(np.linalg.norm(irr_vecs[0] - q_vec))

                # Fisher-style criterion: between-class distance / within-class dispersion
                relevance_val = (between_distance + cls.EPSILON) / (dispersion_r + dispersion_irr + cls.EPSILON)
            else:
                between_distance = 0.0
                # Inverse-variance model: low dispersion -> high relevance
                relevance_val = 1.0 / (dispersion_r + cls.EPSILON)

            raw_relevance_scores[ft] = max(0.0, float(relevance_val))

            # Refine query centroid towards mean of relevant feedback
            refined_q = alpha_query * q_vec + (1.0 - alpha_query) * mu_r
            updated_query_features[ft] = [round(float(v), 6) for v in refined_q]

            diagnostic_stats[ft] = {
                "relevant_count": len(r_vecs),
                "irrelevant_count": len(irr_vecs),
                "intra_dispersion_r": round(dispersion_r, 4),
                "between_distance": round(between_distance, 4),
                "raw_relevance": round(relevance_val, 4),
            }

        # Normalize raw relevance scores
        total_raw = sum(raw_relevance_scores.values())
        if total_raw > 1e-9:
            norm_estimated = {ft: score / total_raw for ft, score in raw_relevance_scores.items()}
        else:
            norm_estimated = {ft: 1.0 / len(active_features) for ft in active_features}

        # Blend with prior weights using beta parameter for stability
        blended_weights: Dict[str, float] = {}
        for ft in active_features:
            prior_w = prior_weights.get(ft, 1.0 / len(active_features))
            est_w = norm_estimated[ft]
            blended = beta_prior * prior_w + (1.0 - beta_prior) * est_w
            blended_weights[ft] = blended

        total_blended = sum(blended_weights.values()) or 1.0
        final_weights = {ft: round(v / total_blended, 4) for ft, v in blended_weights.items()}

        # Record weight updates in diagnostics
        for ft in active_features:
            if ft in diagnostic_stats:
                diagnostic_stats[ft]["prior_weight"] = round(prior_weights.get(ft, 0.0), 4)
                diagnostic_stats[ft]["final_weight"] = final_weights[ft]
                diagnostic_stats[ft]["weight_shift"] = round(final_weights[ft] - prior_weights.get(ft, 0.0), 4)

        return final_weights, updated_query_features, diagnostic_stats
