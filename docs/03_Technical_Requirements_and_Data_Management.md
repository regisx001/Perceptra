# VISUAL IMAGE RETRIEVAL

# Technical Requirements and Data Management

Cahier des charges | Group 13 | Academic Year 2026-2027

## 1. Technical architecture

The application shall separate the web interface, application-level image management, and image-analysis/retrieval responsibilities.

The image-analysis REST API must be implemented in Python using Flask and Flask-RESTful, as required by the assignment.

The frontend framework, main application backend framework, database engine, and image-storage strategy are not specified by the assignment and remain design decisions.

Communication between application components shall use documented interfaces. The application should handle service errors and invalid requests consistently.

## 2. Image-analysis service

The Flask-RESTful service shall expose operations for extracting visual descriptors from one image or a batch of images.

The service shall support color histograms, color moments, dominant colors, GLCM texture measurements, and LBP histograms.

The service shall return structured results that can be consumed by the web application.

Input validation shall cover missing files, unsupported formats, unreadable images, and invalid analysis parameters.

## 3. Proposed processing libraries

| OpenCV | Image loading, color-space conversion, and image-processing operations. |
| --- | --- |
| Pillow | Image format handling and common image transformations. |
| NumPy | Numerical arrays and descriptor representation. |
| scikit-image | GLCM and LBP-related image analysis. |
| SciPy | Scientific and numerical operations where required. |
| scikit-learn | Clustering or other classical machine-learning utilities, where appropriate. |

## 4. Data categories

| User data | Account identifiers and authentication-related information. |
| --- | --- |
| Image metadata | Image name, format, dimensions, size, timestamps, storage reference, owner, and category association. |
| Category data | Category identifiers, names, and parent-child relationships. |
| Transformation data | Source image, derived image, transformation type, parameters, and creation time. |
| Descriptor data | Color histograms, color moments, dominant colors, GLCM values, LBP histograms, descriptor configuration, and extraction version. |
| Search data | Query image, result list, ranking, similarity values, iteration, and timestamp. |
| Feedback data | Search session, image evaluated, relevance label, and feedback iteration. |

## 5. Data and image lifecycle

An uploaded image shall be validated before it is accepted.

After acceptance, the application shall store the image and its metadata.

Images included in the searchable collection shall have descriptors extracted and indexed.

When an image is transformed, the derived image shall be stored as a separate image and linked to its source.

When an image is replaced or its content changes, its descriptors shall be regenerated so that the index does not contain stale features.

When an image is deleted, associated metadata, descriptors, and references shall be handled consistently.

## 6. Indexing strategy

The GHIM-10K collection should be processed in an initial indexing phase.

Descriptors should be precomputed and persisted. Recomputing every reference image's descriptors for every query is inefficient and should be avoided.

Newly uploaded images intended for retrieval shall be added to the index.

The indexing process should be repeatable and should record the descriptor configuration and version used.

The project should provide a way to rebuild the index if descriptor parameters or extraction logic change.

## 7. Feature representation and normalization

Each image shall be represented by the required color and texture descriptors.

Descriptor families may have different dimensions and numerical ranges. The implementation shall define and document normalization before combining them.

The system shall document the color space, histogram binning, color-moment channels, dominant-color method and parameters, GLCM distances and angles, and LBP parameters.

The combined feature representation and similarity function shall be consistent between query processing and reference-image indexing.

## 8. Security and reliability

Passwords shall be securely hashed.

Private image resources shall require authorization.

Uploaded files shall be validated by content and not trusted solely based on their filename or extension.

File access shall be restricted to authorized users.

The application shall handle missing files, corrupted images, unavailable analysis services, and failed database operations without exposing sensitive implementation details.

Operations that modify or delete user data shall enforce ownership and authorization checks.

## 9. Performance and maintainability

The system shall be designed to process the GHIM-10K reference collection.

Precomputed descriptors shall be reused for retrieval.

Batch processing should be supported for dataset indexing.

Descriptor extraction and retrieval execution times should be measurable.

Components should have clear responsibilities and documented interfaces.

Configuration values such as descriptor parameters and retrieval settings should be explicit and reproducible.

## 10. Technology decisions not imposed by the assignment

No database engine is specified. The team must select one based on metadata, descriptor storage, query, and indexing requirements.

No frontend framework is specified.

No main application backend framework is specified. Flask is specifically required for the image-analysis REST API.

No cloud provider or deployment platform is specified.

All selected technologies and the reasons for choosing them shall be documented in the technical report.
