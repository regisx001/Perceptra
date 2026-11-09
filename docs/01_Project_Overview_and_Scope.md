# VISUAL IMAGE RETRIEVAL

# Project Overview and Scope

Cahier des charges | Group 13 | Academic Year 2026-2027

## Document information

| Project | Visual Image Retrieval: Content-Based Image Retrieval (CBIR) |
| --- | --- |
| Group | Group 13 |
| Assigned relevance-feedback method | Feature Relevance Estimation |
| Institution | Faculty of Sciences and Techniques of Tangier, Abdelmalek Essaâdi University |
| Academic year | 2026-2027 |
| Reference dataset | GHIM-10K |

## 1. Introduction

Visual Image Retrieval is a web application for managing, analyzing, and searching image collections based on their visual content. It combines image-management capabilities with computer-vision techniques and content-based image retrieval.

Traditional image search often depends on filenames, keywords, tags, or manually written descriptions. These approaches are insufficient when users want to find images based on what the images actually look like. This project addresses that limitation by extracting numerical visual descriptors and comparing them to retrieve similar images.

The application also includes relevance feedback. Users can mark retrieved images as relevant or irrelevant, and the system uses this feedback to improve subsequent results. Group 13 is assigned the Feature Relevance Estimation method.

## 2. Problem statement

How can a web application manage image collections and retrieve visually similar images using color and texture information, while improving retrieval results through user feedback?

## 3. Project objectives

Provide authenticated access to an image-management application.

Support individual and batch image upload, download, and deletion.

Organize images using hierarchical categories.

Create transformed images through operations such as cropping and resizing while preserving the original.

Extract and display color and texture descriptors.

Retrieve visually similar images from an indexed collection.

Implement Feature Relevance Estimation for relevance-feedback retrieval.

Evaluate retrieval quality before and after relevance feedback.

## 4. Project scope

The project includes user authentication, image collection management, category management, image transformations, visual feature extraction, descriptor visualization, simple image retrieval, relevance feedback, and experimental evaluation.

The reference collection is the GHIM-10K dataset: https://www.kaggle.com/datasets/mcpython/ghim-10k.

The final submission includes commented source code and an academic report in DOC or PDF format. The dataset directory and generated temporary directories must be excluded from the submitted project folder.

## 5. Out of scope and decisions left open

The assignment does not mandate a frontend framework, a primary backend framework, a database engine, or a file-storage technology. These choices must be made during technical design and documented.

The exact mathematical formulation of Feature Relevance Estimation must come from the scientific paper assigned by the instructor. A generic weighting method must not be presented as the assigned algorithm unless the paper specifies it.

Deep-learning embeddings, cloud hosting, public sharing, and collaborative multi-user galleries are not required by the stated assignment unless the project team explicitly adds them.

## 6. Main expected outcome

The expected outcome is a working web application that manages image collections, exposes visual descriptors, retrieves similar images, and demonstrates whether Feature Relevance Estimation improves retrieval quality.
