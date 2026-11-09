# Visual Image Retrieval

### Content-Based Image Retrieval (CBIR) with Feature Relevance Estimation

**Group 13 | Feature Relevance Estimation**

## Overview

Visual Image Retrieval is a web-based application designed to manage, analyze, and retrieve images based on their visual content.

Instead of relying on filenames, tags, or textual descriptions, the application analyzes the visual characteristics of images to identify and retrieve visually similar content.

The system uses Content-Based Image Retrieval (CBIR) techniques, combining color and texture descriptors with similarity measurements and relevance feedback.

## Project Objectives

The main objectives are:

- Manage a personal image gallery.
- Upload, download, and delete individual images or multiple images.
- Organize images using hierarchical categories.
- Apply image transformations such as cropping and resizing.
- Extract and visualize visual features.
- Search for visually similar images.
- Improve search results using user relevance feedback.

## Dataset

The project uses the GHIM-10K dataset, containing approximately 10,000 images.

Dataset: https://www.kaggle.com/datasets/mcpython/ghim-10k

The dataset serves as the reference collection for feature extraction, similarity computation, and retrieval evaluation.

## Visual Feature Extraction

The system analyzes images using two main categories of visual descriptors.

### 1. Color Descriptors

Color features represent the distribution and composition of colors in an image.

- Color Histograms: Represent the distribution of color intensities.
- Color Moments: Describe color distributions using statistical measurements such as mean, standard deviation, and skewness.
- Dominant Colors: Identify the main colors present in an image.

### 2. Texture Descriptors

Texture features describe the local patterns and structural properties of images.

- GLCM (Gray-Level Co-occurrence Matrix): Extracts texture measurements such as contrast, correlation, energy, and homogeneity.
- LBP (Local Binary Patterns): Describes local texture patterns through binary comparisons between neighboring pixels.

The extracted descriptors are combined into feature representations used by the retrieval engine.

## Image Retrieval

The application provides two retrieval approaches.

### 1. Simple Image Retrieval

Users select a query image, and the system retrieves the most visually similar images from the dataset.

The retrieval process consists of:

1. Extracting the query image descriptors.
2. Comparing them with previously extracted dataset descriptors.
3. Computing similarity or distance scores.
4. Ranking the results.
5. Displaying the most similar images.

### 2. Relevance Feedback: Feature Relevance Estimation

**Assigned Method: Feature Relevance Estimation (Group 13).**

Relevance Feedback allows users to improve retrieval results by providing feedback on previously retrieved images.

Instead of treating every visual feature as equally important, Feature Relevance Estimation aims to identify which features are more useful for distinguishing relevant images from irrelevant ones.

The general process is:

1. The user submits an image query.
2. The system retrieves an initial set of similar images.
3. The user identifies relevant and irrelevant results.
4. The system analyzes the feedback to estimate the relevance of individual features.
5. Feature importance is adjusted according to the estimated relevance.
6. The system performs a new retrieval using the updated feature importance.
7. Improved results are presented to the user.

This process can be repeated across multiple iterations to progressively improve retrieval quality.

The exact mathematical formulation and feature-weight estimation strategy must follow the scientific paper assigned to the project.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Web technologies |
| Backend | Python |
| REST API | Flask + Flask-RESTful |
| Image Processing | OpenCV, Pillow |
| Numerical Computing | NumPy |
| Texture Analysis | scikit-image |
| Similarity Computation | scikit-learn |
| Data Storage | Database technology to be determined |

The database technology will be selected during the design phase based on the application's requirements for image metadata, categories, extracted visual descriptors, and retrieval operations.

## Expected Results

The final application should demonstrate:

- A functional image management platform.
- Successful extraction and visualization of color and texture descriptors.
- Accurate similarity-based image retrieval.
- An implementation of Feature Relevance Estimation.
- Improved retrieval results after user feedback.
- An experimental comparison between simple retrieval and relevance-feedback retrieval.

## Evaluation

The retrieval engine should be evaluated using quantitative metrics, including:

- Precision@K: Proportion of relevant images among the K retrieved results.
- Recall@K: Proportion of relevant images retrieved among the first K results.
- Retrieval performance before and after relevance feedback.
- Execution time of feature extraction and retrieval.

The evaluation should demonstrate whether Feature Relevance Estimation improves retrieval quality compared with the initial search.

## Project Scope

This project focuses on combining traditional computer vision techniques with interactive image retrieval.

The primary research objective is to investigate how user feedback can improve image retrieval by estimating the relevance of visual features.

## Academic Information

**Project:** Content-Based Image Retrieval (CBIR)

**Group:** 13

**Assigned Relevance Feedback Method:** Feature Relevance Estimation

**Dataset:** GHIM-10K

**Institution:** Faculté des Sciences et Techniques de Tanger

**Academic Year:** 2026-2027