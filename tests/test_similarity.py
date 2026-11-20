import numpy as np
import pytest
from src.services.similarity_engine import SimilarityEngine


def test_similarity_cosine():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert SimilarityEngine.compute_similarity(v1, v2, metric="cosine") == 1.0

    v3 = [0.0, 1.0, 0.0]
    # Orthogonal vectors: cos = 0 -> mapped to 0.5
    assert SimilarityEngine.compute_similarity(v1, v3, metric="cosine") == 0.5

    v_opp = [-1.0, 0.0, 0.0]
    # Opposite vectors: cos = -1 -> mapped to 0.0
    assert SimilarityEngine.compute_similarity(v1, v_opp, metric="cosine") == 0.0


def test_similarity_euclidean():
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    # Dist = 0 -> sim = 1.0
    assert SimilarityEngine.compute_similarity(v1, v2, metric="euclidean") == 1.0

    v3 = [2.0, 2.0, 3.0]
    # Dist = 1 -> sim = 1 / (1 + 1) = 0.5
    assert SimilarityEngine.compute_similarity(v1, v3, metric="euclidean") == 0.5


def test_vector_normalization():
    v = [10.0, 20.0, 30.0]
    minmax = SimilarityEngine.normalize_vector(v, method="minmax")
    assert np.allclose(minmax, [0.0, 0.5, 1.0])

    standard = SimilarityEngine.normalize_vector(v, method="standard")
    assert abs(float(np.mean(standard))) < 1e-6
    assert abs(float(np.std(standard)) - 1.0) < 1e-4


def test_multi_feature_aggregation():
    q_feats = {
        "color_histogram": [1.0, 0.0],
        "glcm": [0.5, 0.5],
    }
    c_feats = {
        "color_histogram": [1.0, 0.0],
        "glcm": [0.5, 0.5],
    }
    weights = {"color_histogram": 0.6, "glcm": 0.4}

    overall, color_sim, texture_sim, scores = (
        SimilarityEngine.aggregate_multi_feature_similarity(
            query_features=q_feats,
            candidate_features=c_feats,
            weights=weights,
            metric="cosine",
        )
    )

    assert overall == 1.0
    assert color_sim == 1.0
    assert texture_sim == 1.0
    assert scores["color_histogram"] == 1.0
    assert scores["glcm"] == 1.0
