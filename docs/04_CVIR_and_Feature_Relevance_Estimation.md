# VISUAL IMAGE RETRIEVAL

# CBIR and Feature Relevance Estimation

Cahier des charges | Group 13 | Academic Year 2026-2027

## 1. Purpose

This document describes the image-representation, retrieval, and relevance-feedback requirements. It focuses on the academic and algorithmic contribution assigned to Group 13.

## 2. Content-Based Image Retrieval

Content-Based Image Retrieval (CBIR) retrieves images by comparing visual information extracted from the images themselves. In this project, visual information is represented using color and texture descriptors.

The same descriptor-extraction configuration must be applied to query images and reference images. The resulting representations are compared using a documented similarity or distance function.

## 3. Required color descriptors

| Color histograms | Describe the distribution of color values. The implementation must define the color space, channels, and histogram bins. |
| --- | --- |
| Color moments | Describe color distributions using at least mean, standard deviation, and skewness. |
| Dominant colors | Represent the principal colors in an image. A clustering approach such as K-Means may be used, with the number of clusters and other parameters documented. |

## 4. Required texture descriptors

| GLCM | The Gray-Level Co-occurrence Matrix describes spatial relationships between gray-level values. Required measurements are contrast, correlation, energy, and homogeneity. The implementation must define gray-level quantization, pixel distances, and directions. |
| --- | --- |
| LBP | Local Binary Patterns encode local texture by comparing a pixel with neighboring pixels. The resulting patterns are summarized in a histogram. The implementation must document neighborhood size, radius, and histogram configuration. |

## 5. Combined image representation

An image representation shall combine the required color and texture descriptors. Conceptually, it contains the color histogram, color moments, dominant-color representation, GLCM measurements, and LBP histogram.

Before combining feature families, the implementation shall normalize or otherwise calibrate their scales. The selected normalization and feature-combination strategy must be justified and documented.

The final representation shall be deterministic for a given image and descriptor configuration.

## 6. Simple retrieval process

1. Step 1: The user selects or uploads a query image.
1. Step 2: The system obtains the query descriptors using the same extraction configuration as the indexed collection.
1. Step 3: The retrieval engine compares the query representation with reference-image representations.
1. Step 4: The engine computes distances or similarity scores.
1. Step 5: Candidate images are ranked.
1. Step 6: The application displays the top K results.
Smaller distance values indicate greater similarity when a distance-based measure is used. The chosen measure and ranking convention must be documented.

## 7. Relevance feedback concept

Initial retrieval may not match the user's intention. Relevance feedback allows the user to label retrieved images as relevant or irrelevant and uses those labels to improve the next retrieval.

A feedback iteration consists of an initial or updated ranking, user judgments, analysis of those judgments, an update to the retrieval process, and a new ranking.

The application should associate feedback with the query and iteration so that the process can be evaluated and reproduced.

## 8. Group 13 method: Feature Relevance Estimation

Group 13 is assigned Feature Relevance Estimation. The method aims to estimate the usefulness or importance of visual features based on the user's relevance judgments.

The general workflow is to collect relevant and irrelevant examples, analyze their feature values, estimate feature relevance according to the assigned algorithm, and use the resulting estimates in a subsequent retrieval.

The exact mathematical definition, estimation formula, parameter settings, and update procedure must be taken from the scientific paper provided by the instructor. The paper is authoritative for the implementation.

The team must not silently substitute Query Vector Modification, Re-weighting Type-1, Rocchio, or another relevance-feedback method for the assigned Feature Relevance Estimation technique.

## 9. Feedback interaction requirements

The user shall be able to mark retrieved images as relevant or irrelevant.

The interface shall make the current feedback state clear.

The system shall validate that feedback refers to images returned for the corresponding search session.

The user shall be able to submit feedback and request an updated ranking.

The system should support repeated feedback iterations.

The application should preserve the initial ranking and subsequent rankings for evaluation.

## 10. Evaluation methodology

Evaluation shall compare simple retrieval with retrieval after Feature Relevance Estimation.

Precision@K shall measure the fraction of the first K results that are relevant.

Recall@K shall measure the fraction of all relevant items that appear in the first K results.

F1-score may be reported as a combined precision-recall measure.

Execution time should be measured for feature extraction, initial retrieval, and feedback-based retrieval.

The team must define how relevance ground truth is established. Dataset category labels may be used only if they are available, appropriate, and consistent with the retrieval task. User feedback and ground-truth evaluation should be distinguished.

Experiments should report the chosen K values, number of feedback iterations, number of relevant and irrelevant judgments, descriptor settings, and retrieval configuration.

## 11. Experimental questions

Does Feature Relevance Estimation improve Precision@K compared with simple retrieval?

How does retrieval quality change over successive feedback iterations?

Which descriptor families contribute most to retrieval quality?

How sensitive are results to descriptor normalization and retrieval parameters?

What is the computational cost of the feedback-based retrieval process?
