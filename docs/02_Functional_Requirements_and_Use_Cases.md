# VISUAL IMAGE RETRIEVAL

# Functional Requirements and Use Cases

Cahier des charges | Group 13 | Academic Year 2026-2027

## 1. Actors

| Authenticated user | The primary actor. The user manages images and categories, transforms images, inspects descriptors, performs searches, and provides relevance feedback. |
| --- | --- |
| Image-analysis and retrieval services | Internal software components that extract descriptors, calculate similarity, rank results, and apply the assigned relevance-feedback method. |

## 2. Authentication and access control

The application shall allow users to create accounts if registration is included in the chosen design.

The application shall authenticate users and allow them to log out.

Private image collections and operations shall be accessible only to authorized users.

Passwords shall never be stored in plain text.

## 3. Image collection management

| FR-IMG-01 | The user shall be able to upload one image. |
| --- | --- |
| FR-IMG-02 | The user shall be able to upload multiple images in one operation. |
| FR-IMG-03 | The application shall validate uploaded files and reject unsupported or invalid image files. |
| FR-IMG-04 | The user shall be able to browse images in a gallery. |
| FR-IMG-05 | The user shall be able to download an individual image. |
| FR-IMG-06 | The user shall be able to download a selected collection of images. |
| FR-IMG-07 | The user shall be able to delete one image. |
| FR-IMG-08 | The user shall be able to delete multiple selected images. |
| FR-IMG-09 | The user shall be able to inspect an image's metadata and visual descriptors. |

## 4. Category management

The user shall be able to create, rename, and delete categories.

The user shall be able to create nested subcategories.

The user shall be able to assign images to categories and move images between categories.

The application shall display the category hierarchy and the images associated with a selected category.

Example hierarchy: Nature > Landscapes, Mountains, Forests; Architecture > Buildings, Monuments; Animals > Birds, Mammals.

## 5. Image transformations

The application shall support cropping, resizing, and scaling.

Each transformation shall produce a new image instance.

The original image shall remain unchanged.

The application should preserve the relationship between a derived image and its source image.

The application should retain relevant transformation parameters as metadata when practical.

## 6. Descriptor extraction and visualization

The user shall be able to request visual analysis for an image.

The system shall extract color histograms, color moments, dominant colors, GLCM features, and LBP histograms.

The system shall support processing an individual image and a collection of images through the image-analysis API.

The application shall display color histograms, color-moment values, dominant-color palettes, GLCM measurements, and LBP histograms in suitable visual forms.

## 7. Simple image retrieval

| FR-RET-01 | The user shall be able to select an image from the collection or provide a query image. |
| --- | --- |
| FR-RET-02 | The system shall obtain or calculate the query image's descriptors. |
| FR-RET-03 | The system shall compare the query representation with indexed image representations. |
| FR-RET-04 | The system shall rank candidate images according to a defined similarity or distance measure. |
| FR-RET-05 | The system shall display the top results in a gallery. |
| FR-RET-06 | The user should be able to specify the number of results to display. |

## 8. Relevance feedback

| FR-FB-01 | After an initial search, the user shall be able to mark retrieved images as relevant or irrelevant. |
| --- | --- |
| FR-FB-02 | The system shall associate feedback with the corresponding query and search iteration. |
| FR-FB-03 | The system shall apply Group 13's Feature Relevance Estimation method to the collected feedback. |
| FR-FB-04 | The system shall perform a new retrieval using the updated feature relevance information. |
| FR-FB-05 | The system shall display the updated ranking and allow further feedback iterations. |
| FR-FB-06 | The system should retain enough information to compare results across iterations. |

## 9. Use case: upload images

Precondition: The user is authenticated.

Main flow: The user opens the gallery, selects one or more image files, submits the upload, and receives the result. The system validates each file, stores accepted images, records their metadata, and makes them available in the gallery.

Alternative flow: If a file is invalid or unsupported, the system rejects that file and reports the reason. Valid files in the same batch may still be accepted.

## 10. Use case: inspect image descriptors

Precondition: The image is available to the user.

Main flow: The user opens an image and requests analysis. The application calls the Flask-RESTful analysis service. The service extracts the requested descriptors and returns the results. The application displays the measurements and visualizations.

## 11. Use case: simple retrieval

Precondition: The reference collection has been indexed, and the query image can be processed.

Main flow: The user selects a query image and a result count. The system obtains its descriptors, compares them with indexed descriptors, ranks the candidates, and displays the top results.

## 12. Use case: relevance-feedback retrieval

Precondition: An initial retrieval result is available.

Main flow: The user labels results as relevant or irrelevant. The system records the labels, estimates feature relevance using the assigned method, updates retrieval according to the scientific paper, and displays a new ranking. The process may be repeated.
