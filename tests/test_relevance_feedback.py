import pytest
from src.services.relevance_feedback import FeatureRelevanceEstimator


def test_relevance_feedback_weight_estimation():
    # Query has 2 features: 'color_histogram' and 'glcm'
    query_feats = {
        "color_histogram": [0.5, 0.5],
        "glcm": [0.2, 0.8],
    }

    # Relevant samples agree tightly on 'color_histogram', but vary wildly on 'glcm'
    relevant_feats = [
        {"color_histogram": [0.51, 0.49], "glcm": [0.1, 0.9]},
        {"color_histogram": [0.49, 0.51], "glcm": [0.8, 0.2]},
        {"color_histogram": [0.50, 0.50], "glcm": [0.4, 0.6]},
    ]

    new_weights, new_q, stats = FeatureRelevanceEstimator.estimate_weights(
        query_features=query_feats,
        relevant_features=relevant_feats,
        irrelevant_features=[],
        prior_weights={"color_histogram": 0.5, "glcm": 0.5},
    )

    # Weights must sum to 1.0 (approx due to rounding)
    assert abs(sum(new_weights.values()) - 1.0) < 0.01

    # Because color_histogram has much smaller dispersion, its weight must be higher than glcm!
    assert new_weights["color_histogram"] > new_weights["glcm"]
    assert stats["color_histogram"]["intra_dispersion_r"] < stats["glcm"]["intra_dispersion_r"]


def test_relevance_feedback_with_negative_examples():
    query_feats = {
        "color_histogram": [1.0, 0.0],
        "glcm": [0.0, 1.0],
    }
    relevant_feats = [
        {"color_histogram": [0.95, 0.05], "glcm": [0.1, 0.9]},
    ]
    irrelevant_feats = [
        {"color_histogram": [0.1, 0.9], "glcm": [0.1, 0.9]},
    ]

    new_weights, new_q, stats = FeatureRelevanceEstimator.estimate_weights(
        query_features=query_feats,
        relevant_features=relevant_feats,
        irrelevant_features=irrelevant_feats,
    )

    # color_histogram cleanly separates relevant from irrelevant, glcm does not
    assert new_weights["color_histogram"] > new_weights["glcm"]
