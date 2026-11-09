# VISUAL IMAGE RETRIEVAL

# Testing, Evaluation and Deliverables

Cahier des charges | Group 13 | Academic Year 2026-2027

## 1. Testing objectives

Testing shall verify that the application meets its functional requirements, that the image-analysis service returns valid descriptors, and that the retrieval and feedback processes behave as specified.

Testing shall cover normal inputs, invalid inputs, boundary cases, and failures between application components.

## 2. Functional testing

| Authentication | Verify successful login, failed login, logout, and access restrictions. |
| --- | --- |
| Image upload | Verify single and multiple uploads, supported formats, invalid files, corrupted files, and duplicate handling if defined. |
| Image download and deletion | Verify individual and batch operations and ensure that users cannot access or delete another user's private images. |
| Categories | Verify category creation, nesting, renaming, deletion, and image assignment. |
| Transformations | Verify crop, resize, and scaling outputs; confirm that the original remains unchanged. |
| Descriptor extraction | Verify that all required color and texture descriptors are returned for valid images. |
| Visualization | Verify that displayed charts and values correspond to the returned descriptor data. |
| Simple retrieval | Verify ranking, result count, and handling of query images. |
| Relevance feedback | Verify feedback collection, session association, feature relevance estimation, and updated ranking. |

## 3. Descriptor validation

Use a small set of known images to inspect whether descriptor outputs are valid, finite, and consistent.

Verify histogram dimensions and normalization behavior.

Verify color-moment output dimensions and channel definitions.

Verify the number and representation of dominant colors.

Verify that GLCM outputs include contrast, correlation, energy, and homogeneity for the configured distances and angles.

Verify LBP histogram dimensions and normalization.

Record descriptor parameters so that results can be reproduced.

## 4. Retrieval evaluation

Evaluate simple retrieval and Feature Relevance Estimation using the same reference collection and comparable query set.

Report Precision@K and Recall@K for selected values of K.

Report F1-score where appropriate.

Measure execution time for initial retrieval and feedback iterations.

Present results using tables and charts, and discuss cases where feedback improves or does not improve the ranking.

Define a consistent relevance ground truth. Do not claim objective retrieval accuracy based only on subjective feedback labels.

## 5. Non-functional testing

Measure response times for representative image-management and retrieval operations.

Check behavior when the analysis service is unavailable.

Check handling of large image files and batch uploads within the limits selected by the team.

Verify that unauthorized requests are rejected.

Verify that errors do not expose passwords, private file paths, or other sensitive information.

## 6. Acceptance criteria

The application supports the required image-management operations.

Images can be organized using hierarchical categories.

Cropping and resizing create derived images without modifying originals.

The Flask-RESTful service extracts all required color and texture descriptors.

The application displays the extracted descriptors in suitable visual forms.

Simple retrieval returns a ranked list of visually similar images.

Users can label results as relevant or irrelevant.

Group 13's Feature Relevance Estimation implementation follows the assigned scientific paper.

The project includes a quantitative comparison of simple retrieval and relevance-feedback retrieval.

The final source code is commented and the academic report is delivered in DOC or PDF format.

## 7. Final deliverables

| Web application | A working application for image management, visual analysis, and image retrieval. |
| --- | --- |
| Source code | Commented application source code, Flask-RESTful analysis service, descriptor extraction, indexing, retrieval, and Feature Relevance Estimation implementation. |
| Academic report | A DOC or PDF report explaining the problem, background, methods, architecture, implementation, experiments, results, limitations, and conclusion. |
| Documentation | Instructions for configuring, running, and testing the application, including any required dataset preparation and indexing steps. |

## 8. Submission exclusions

The GHIM-10K image dataset directory must not be included in the submitted project folder.

Generated temporary directories and regenerable intermediate files must not be included.

Configuration examples may be included, but credentials, passwords, and private secrets must not be committed.

## 9. Proposed project phases

| Phase 1: Requirements and literature review | Confirm requirements and study the assigned Feature Relevance Estimation paper. |
| --- | --- |
| Phase 2: Dataset preparation | Inspect GHIM-10K and define preprocessing and indexing rules. |
| Phase 3: Descriptor extraction | Implement and validate color and texture descriptors. |
| Phase 4: Simple retrieval | Implement feature comparison, ranking, and baseline evaluation. |
| Phase 5: Relevance feedback | Implement the exact Group 13 method and feedback workflow. |
| Phase 6: Application development | Implement image management, categories, transformations, and descriptor visualization. |
| Phase 7: Integration | Connect the web application to the Flask-RESTful service. |
| Phase 8: Testing and evaluation | Run functional tests and retrieval experiments. |
| Phase 9: Documentation | Prepare the technical documentation and academic report. |

## 10. Open decisions to resolve

Which frontend framework will be used?

Will Flask also serve the main application backend, or will a separate backend be used?

Which database and image-storage strategy will be selected?

What image formats and maximum upload sizes will be supported?

Which color space, histogram bins, and dominant-color parameters will be used?

What GLCM distances, angles, and gray-level quantization will be used?

What LBP radius, neighborhood size, and histogram configuration will be used?

What distance function and feature-combination strategy will be used for baseline retrieval?

What exact Feature Relevance Estimation equations and parameters are specified in the assigned paper?

How will ground-truth relevance be established for the evaluation?
