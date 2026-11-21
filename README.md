# Perceptra: Content-Based Image Retrieval (CBIR)

### Group 13 | Feature Relevance Estimation (FRE)
**Institution:** Faculté des Sciences et Techniques de Tanger  
**Academic Year:** 2026–2027  
**Dataset:** GHIM-10K  

---

## 📌 Executive Summary & Architecture Overview

**Perceptra** is a full-stack, enterprise-grade Content-Based Image Retrieval (CBIR) platform engineered with a high-performance **Python/Flask REST API** backend and a modern **SvelteKit + Tailwind CSS + bits-ui** frontend.

The system bypasses keyword search in favor of deep visual descriptor extraction across color and texture spaces. For interactive relevance refinement, Perceptra implements the assigned **Group 13: Feature Relevance Estimation (FRE)** algorithm, dynamically adjusting feature weights based on user feedback to drastically elevate retrieval precision.

```
                              ┌──────────────────────────────────┐
                              │  SvelteKit Modern Web Frontend   │
                              │ (Paraglide i18n, Lucide/Tabler)  │
                              └─────────────────┬────────────────┘
                                                │ REST API (JWT)
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Flask Application Engine                                     │
├─────────────────────┬──────────────────────┬──────────────────────┬────────────────────────────┤
│     Auth & Users    │  Categories & Tree   │  Images & Lineage    │    Descriptors & Engine    │
│  (Bcrypt, JWT Auth) │ (Adjacency List API) │ (Storage, Transforms)│ (Color & Texture Spaces)   │
├─────────────────────┴──────────────────────┴──────────────────────┴────────────────────────────┤
│                             Query & Feature Relevance Engine                                   │
│            Cosine, Euclidean, Dispersion-based FRE (Group 13), Session Caching                 │
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                     ┌──────────────────────────┴──────────────────────────┐
                     ▼                                                     ▼
      ┌─────────────────────────────┐                       ┌─────────────────────────────┐
      │     SQLAlchemy + SQLite     │                       │     fsspec Storage Engine   │
      │  WAL Mode, Foreign Keys ON  │                       │  (users/, derived/, dataset)│
      └─────────────────────────────┘                       └─────────────────────────────┘
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Python**: `>= 3.13` (managed via [`uv`](https://docs.astral.sh/uv/))
- **Node.js / Bun**: `>= 18` (for the SvelteKit frontend in `web/`)

### 1. Backend Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Perceptra

# 2. Configure environment variables
cp .env.example .env

# 3. Install dependencies using uv
uv sync

# 4. Initialize and apply database migrations
uv run db-upgrade

# 5. Run the development server (port 7000)
uv run dev
# Or production Gunicorn:
uv run start
```

### 2. Frontend Setup

```bash
cd web
bun install   # or: npm install
bun run dev   # or: npm run dev
```
Access the application at `http://localhost:5173`.

### 3. Dataset Ingestion (GHIM-10K)

Perceptra provides built-in multithreaded dataset ingestion with automatic category hierarchy creation and simultaneous extraction of all 5 visual descriptors:

```bash
# Ingest dataset images and compute features
uv run perceptra dataset ingest /path/to/ghim-10k --workers 4

# Inspect database and descriptor indexing status
uv run perceptra dataset status
```

### 4. Running Tests

```bash
uv run pytest
```
*Current test suite: 64 passing unit and integration tests.*

---

## 📋 Complete Functionalities Checklist

This checklist tracks every feature across **Task 1**, **Task 2**, the assigned **Group 13 FRE algorithm**, and supporting full-stack infrastructure.

**Legend:**
- `[M]` **Mandatory**: Explicitly required by the academic assignment.
- `[R]` **Recommended**: Needed for a complete, production-grade application.
- `[A]` **Advanced**: High-value additional features that enhance the platform.

Status Indicators:
- `[x]` **Completed & Tested**
- `[ ]` **Pending / Planned**

---

### 1. Authentication and User Management

- [x] `[M]` **User registration:** `/api/v1/auth/register` with email validation and Bcrypt password hashing.
- [x] `[M]` **User login:** `/api/v1/auth/login` returning JWT access and refresh tokens.
- [x] `[M]` **JWT authentication:** Protected routes guarded by `@jwt_required()` with token expiry and secret verification.
- [x] `[M]` **Logout:** Frontend session purging and client-side token discard.
- [x] `[R]` **Display authenticated user's profile:** `/api/v1/auth/me` providing identity and account creation timestamps.
- [ ] `[R]` **Update username and profile information.**
- [ ] `[R]` **Change password.**
- [x] `[R]` **Protect private API endpoints:** Strict user scoping on all gallery, categories, and query endpoints.
- [x] `[R]` **Associate uploaded images with their owners:** `images.owner_id` explicitly linked to the active user.
- [x] `[R]` **Prevent users from accessing other users' private images:** Foreign key isolation returning `404 Not Found` (avoids `403` UUID enumeration leaks).
- [x] `[R]` **Handle expired or invalid access tokens:** Centralized error handling and automatic token refresh via `/api/v1/auth/refresh`.
- [ ] `[A]` **Account deletion.**

---

### 2. Dashboard and Overview

- [x] `[R]` **Display total number of images:** Live analytics card reporting indexed collection count.
- [x] `[R]` **Display total number of categories:** Category distribution and hierarchy counter.
- [x] `[R]` **Display recently uploaded images:** Gallery preview of newest user additions.
- [x] `[R]` **Display recently transformed images:** Filterable derived lineage view.
- [x] `[R]` **Display recent visual searches:** Recent session queries and matching results.
- [x] `[R]` **Display image storage usage:** Byte quota and storage size accounting.
- [x] `[R]` **Display dataset indexing status:** Ingestion telemetry via CLI (`uv run perceptra dataset status`) and web dashboard.
- [ ] `[A]` **Display retrieval statistics:** Precision/Recall telemetry charts.
- [ ] `[A]` **Display recent activity history.**

---

### 3. Image Gallery Management

#### Image Upload
- [x] `[M]` **Upload a single image:** Dedicated `POST /api/v1/images` endpoint with category association.
- [x] `[M]` **Upload multiple images:** Bulk batch processing with per-file status reports.
- [x] `[R]` **Drag-and-drop upload:** Full drag-and-drop zone in SvelteKit upload interface.
- [x] `[R]` **Preview images before uploading:** Client-side object URL preview prior to upload dispatch.
- [x] `[R]` **Validate image formats:** Restricts files to PNG, JPEG, WEBP, and BMP.
- [x] `[R]` **Validate maximum file size:** Enforces configurable 32MB payload limit.
- [x] `[R]` **Validate actual image content:** Pillow `img.verify()` inspection detecting corrupted bitstreams or spoofed extensions.
- [x] `[R]` **Display upload progress:** Visual progress bars per file during network dispatch.
- [x] `[R]` **Cancel an upload:** AbortController support in upload client.
- [x] `[R]` **Retry failed uploads:** Individual retry controls for failed queue items.
- [x] `[R]` **Display upload success and failure states:** Color-coded badges and toast alerts.
- [x] `[R]` **Automatically extract image metadata:** Dimensions (`width`, `height`), `file_size`, `mime_type`, and SHA-256 `checksum`.
- [x] `[R]` **Optionally select a category during upload:** Category dropdown selector embedded in upload modal.

#### Image Browsing and Management
- [x] `[M]` **Display all accessible images:** Paginated gallery view (`GET /api/v1/images?page=1&per_page=24`).
- [x] `[M]` **Preview an image:** High-resolution preview dialog and responsive detail viewer.
- [x] `[M]` **Download an individual image:** Direct binary stream (`GET /api/v1/images/<id>/file?download=true`).
- [x] `[M]` **Delete an individual image:** Atomic removal from SQLite and underlying filesystem storage.
- [x] `[M]` **Download multiple selected images:** Multi-select individual downloads.
- [x] `[M]` **Delete multiple selected images:** `POST /api/v1/images/bulk-delete` with transaction rollback safety.
- [x] `[R]` **Select all images:** One-click selection toggle on gallery grid.
- [x] `[R]` **Search images by filename:** Client-side and server-side text filtering.
- [x] `[R]` **Filter images by category:** Category filter pill selector and `?category_id=<uuid>` API support.
- [x] `[R]` **Filter images by upload date:** Date range filtering.
- [x] `[R]` **Sort by name, date, and size:** Dynamic sorting dropdown.
- [x] `[R]` **Display image metadata:** Full inspection drawer showing resolution, aspect ratio, storage key, and checksum.
- [x] `[R]` **Display original image dimensions:** Native width $\times$ height display.
- [x] `[R]` **Display image format and file size:** Format badge (JPEG, PNG, etc.) and humanized file sizes (KB/MB).
- [x] `[R]` **Display image ownership:** Ownership tags separating personal uploads from dataset references.
- [x] `[R]` **Display image source:** Distinct badges for `upload`, `dataset`, and `derived`.
- [ ] `[A]` **Favorite images.**
- [ ] `[A]` **Download selected images as a ZIP archive.**

---

### 4. Hierarchical Category Management

- [x] `[M]` **Create categories:** `POST /api/v1/categories` supporting root categories and parent folder assignment.
- [x] `[M]` **Rename categories:** `PATCH /api/v1/categories/<id>` with sibling uniqueness validation.
- [x] `[M]` **Delete categories:** `DELETE /api/v1/categories/<id>` with graceful image preservation.
- [x] `[M]` **Create subcategories:** Nested child creation via `parent_id` foreign key.
- [x] `[M]` **Display categories in a hierarchical tree:** Recursive nested tree endpoint (`GET /api/v1/categories?tree=true`).
- [x] `[M]` **Assign images to categories:** Direct image update (`PATCH /api/v1/images/<id>`) and upload tagging.
- [x] `[M]` **Move images between categories:** `POST /api/v1/images/bulk-assign` cross-category folder migration.
- [x] `[R]` **Move categories under other categories:** Reparenting with automated cycle and descendant-move detection.
- [x] `[R]` **Display images belonging to a category:** Filtered gallery browsing by folder.
- [x] `[R]` **Display the number of images in each category:** Aggregated counts via `?include_counts=true`.
- [x] `[R]` **Search categories:** Fast recursive name filtering.
- [x] `[R]` **Validate category ownership:** Cross-user isolation ensuring users cannot mutate foreign folders.
- [x] `[R]` **Handle deletion of categories containing images:** Images set to `NULL` (`uncategorized`) via database constraints.
- [x] `[R]` **Handle deletion of categories containing subcategories:** Direct children promoted to root categories.
- [x] `[A]` **Support multiple levels of nested categories:** Arbitrary tree depth with breadcrumb navigation.

---

### 5. Image Transformation Engine

#### Transformation Operations
- [x] `[M]` **Crop an image:** Sub-rectangle extraction `[x, y, x + width, y + height]`.
- [x] `[M]` **Resize an image:** High-fidelity resampling via `PIL.Image.Resampling.LANCZOS`.
- [x] `[R]` **Rotate by 90 degrees:** Orthogonal 90° rotation.
- [x] `[R]` **Rotate by 180 degrees:** Inversion 180° rotation.
- [x] `[R]` **Rotate by 270 degrees:** Orthogonal 270° rotation.
- [x] `[R]` **Rotate by a custom angle:** Arbitrary angle rotation in `[-360, 360]` with bicubic interpolation.
- [x] `[R]` **Flip horizontally:** Exact pixel reflection via `ImageOps.mirror`.
- [x] `[R]` **Flip vertically:** Exact pixel reflection via `ImageOps.flip`.
- [x] `[A]` **Apply affine transformations:** 2D matrix transformation engine.
- [x] `[A]` **Apply shear transformations:** Slanted affine transformation with automatic canvas expansion math ($W_{\text{new}}, H_{\text{new}}$).

#### Transformation Interface & Architecture
- [x] `[R]` **Upload or select an existing image:** Studio launcher from existing gallery or fresh upload.
- [x] `[R]` **Display the original image on the canvas:** Responsive interactive transformation workbench.
- [x] `[R]` **Interactive crop selection:** Visual bounding box selection handles.
- [x] `[R]` **Aspect ratio presets:** 1:1 (Square), 4:3, 16:9, and Freeform.
- [x] `[R]` **Custom crop dimensions:** Numeric pixel coordinate overrides.
- [x] `[R]` **Width and height configuration for resizing:** Direct dimension inputs.
- [x] `[R]` **Maintain aspect ratio:** Proportional locking toggle.
- [x] `[R]` **Preview transformations before saving:** Sub-millisecond math validation (`POST /api/v1/images/<id>/transform-validate`) and lightweight JPEG preview (`?preview=true`).
- [x] `[R]` **Undo and redo operations:** Transformation history stack on the frontend.
- [x] `[R]` **Reset transformations:** Revert canvas to original image state.
- [x] `[R]` **Display original and resulting dimensions:** Real-time before/after pixel dimension indicator.
- [x] `[R]` **Download transformed images:** Direct client-side export.
- [x] `[M]` **Save transformed images as new images:** `POST /api/v1/images/<id>/transform` creates a new `derived` image.
- [x] `[R]` **Preserve the original image:** Parent file and database record remain untouched.
- [x] `[R]` **Associate derived images with their parent images:** Foreign key linkage (`parent_image_id`) establishing audit lineage.
- [x] `[R]` **Extract descriptors again for derived images:** Transformed images receive `processing_status="pending"` for full CBIR re-indexing.

---

### 6. Visual Descriptor Extraction

#### A. Color Descriptors
- [x] `[M]` **Color histogram extraction:** 3D HSV color space histogram (8 Hue $\times$ 4 Saturation $\times$ 4 Value = 128 bins) normalized to unit sum.
- [x] `[M]` **Color moments extraction:** First 3 central moments (Mean, Standard Deviation, Skewness) computed across HSV channels (9-dimensional vector).
- [x] `[M]` **Dominant colors extraction:** K-Means clustering ($k=5$) in CIE-Lab color space extracting centroid coordinates and cluster proportions.
- [x] `[R]` **Display color histograms as charts:** Interactive frequency distribution charts in image detail view.
- [x] `[R]` **Display color moments numerically:** Formatted table of Mean, Variance/Std, and Skew per channel.
- [x] `[R]` **Display dominant colors as a palette:** Hex color swatches rendered on UI.
- [x] `[R]` **Display the proportion of each dominant color:** Percentage breakdown tags (e.g. 42% `#345a8a`).
- [x] `[R]` **Configure histogram bins and color channels:** Parameterized extraction pipeline.
- [x] `[R]` **Configure color space:** Automatic RGB $\rightarrow$ HSV and RGB $\rightarrow$ CIE-Lab transformations.

#### B. Texture Descriptors
- [x] `[M]` **Generate Gray-Level Co-occurrence Matrix (GLCM):** Computed across 4 orientations ($0^\circ, 45^\circ, 90^\circ, 135^\circ$) with distance $d=1$.
- [x] `[M]` **Calculate GLCM contrast:** Intensity variation between pixels.
- [x] `[M]` **Calculate GLCM correlation:** Linear dependency of gray levels.
- [x] `[M]` **Calculate GLCM energy:** Angular second moment / uniformity.
- [x] `[M]` **Calculate GLCM homogeneity:** Closeness of element distribution to diagonal.
- [x] `[M]` **Calculate LBP (Local Binary Patterns):** Standard uniform LBP with radius $R=1, P=8$.
- [x] `[M]` **Generate LBP frequency histogram:** 256-bin normalized texture histogram.
- [x] `[R]` **Display GLCM measurements:** Numeric display across the 4 statistical properties.
- [x] `[R]` **Display LBP histogram:** Bar chart visualization of texture pattern occurrences.
- [x] `[R]` **Configure GLCM distances & angles:** Parameterized through extraction options.
- [x] `[R]` **Configure gray-level quantization:** 32/64/256 level quantization support.
- [x] `[R]` **Configure LBP radius & neighbors:** Configurable $(P, R)$ parameters.

#### C. Descriptor Management
- [x] `[M]` **Extract descriptors for one image:** `POST /api/v1/descriptors/<image_id>`.
- [x] `[M]` **Extract descriptors for multiple images:** `POST /api/v1/descriptors/batch`.
- [x] `[R]` **Store calculated descriptors in the database:** Persisted in `image_features` table with JSON payloads.
- [x] `[R]` **Display descriptor extraction status:** Indicator showing `pending`, `indexed`, or `failed`.
- [x] `[R]` **Detect missing descriptors:** Automated query identifying images lacking features.
- [x] `[R]` **Recalculate descriptors:** Force re-indexing endpoint with `force=true`.
- [x] `[R]` **Track extractor versions:** Version string tagging (e.g. `1.0.0`) on feature rows.
- [x] `[R]` **Store extraction parameters:** Full parameter snapshot stored alongside feature vectors.
- [x] `[R]` **Handle extraction errors:** Resilient exception handling preventing batch pipeline halts.
- [x] `[R]` **Display extraction execution time:** Benchmark timings returned in API responses.
- [x] `[R]` **Extract descriptors for derived images:** Automatic indexing capability for transformed derivatives.

#### D. Descriptor Inspection Page
- [x] `[R]` **Image preview:** High-res preview at `/dashboard/images/[id]`.
- [x] `[R]` **Image metadata:** Resolution, format, size, checksum, and storage key.
- [x] `[R]` **Color histogram visualization:** Interactive multi-channel bar charts.
- [x] `[R]` **Color moments values:** Data grid displaying moments per channel.
- [x] `[R]` **Dominant color visualization:** Color chips with hex labels and percentage proportions.
- [x] `[R]` **GLCM measurements:** Gauge/metric cards for contrast, correlation, energy, and homogeneity.
- [x] `[R]` **LBP histogram visualization:** Distribution of local micro-texture patterns.
- [x] `[R]` **Descriptor extraction date:** ISO timestamp of calculation.
- [x] `[R]` **Descriptor extraction parameters:** JSON parameters inspection drawer.

---

### 7. GHIM-10K Dataset Management

- [x] `[M]` **Import the GHIM-10K image dataset:** CLI ingestion pipeline (`uv run perceptra dataset ingest <path>`).
- [x] `[M]` **Process dataset images using the descriptor extraction API:** Concurrent worker threads generating all 5 descriptors during ingestion.
- [x] `[R]` **Register dataset images in the image database:** `images` records created with `source_type="dataset"` and `owner_id=NULL`.
- [x] `[R]` **Store dataset image metadata:** Native resolution, checksums, and mime types.
- [x] `[R]` **Extract color descriptors for dataset images:** Batch extraction of histogram, moments, and dominant colors.
- [x] `[R]` **Extract texture descriptors for dataset images:** Batch extraction of GLCM and LBP.
- [x] `[R]` **Store extracted descriptors:** Linked in `image_features` table.
- [x] `[R]` **Avoid duplicate dataset imports:** SHA-256 deduplication and `--skip-existing` flag.
- [x] `[R]` **Track indexing progress:** Rich terminal progress bar and throughput monitor.
- [x] `[R]` **Track failed image processing:** Error summary capturing corrupted or unreadable images.
- [x] `[R]` **Allow failed extractions to be retried:** Idempotent re-run capability.
- [x] `[R]` **Display the number of indexed images:** Ingestion summary (`3,133+ indexed images`).
- [x] `[R]` **Display the number of successfully extracted descriptors:** Count per feature type (`15,665+ total feature vectors`).
- [x] `[R]` **Make dataset images available for visual retrieval:** Global query collection scope.
- [x] `[R]` **Support shared dataset access without duplicating images:** Single copy in storage referenced across all user queries.

---

### 8. Visual Query: Simple Image Retrieval

#### Query Configuration
- [x] `[M]` **Upload a query image:** Drag-and-drop or file upload directly on the visual search studio.
- [x] `[R]` **Select an existing image from the gallery as the query:** Modal picker selecting from user gallery or dataset.
- [x] `[R]` **Preview the query image:** Visual card displaying query image before running search.
- [x] `[R]` **Replace or remove the query image:** Instant clear/replace actions.
- [x] `[R]` **Select the search collection:** Radio selection: `dataset`, `user`, or `both`.
- [x] `[R]` **Search GHIM-10K:** Filter searching strictly the 10,000 dataset images.
- [x] `[R]` **Search personal images:** Scoped search strictly across authenticated user uploads.
- [x] `[R]` **Search both collections:** Combined retrieval across dataset and private library.
- [x] `[R]` **Filter by category:** Restrict search candidates to specific category sub-trees.
- [x] `[R]` **Configure the number of results (Top-K):** Adjustable slider/input ($K \in [1, 100]$, default 12).

#### Retrieval Configuration
- [x] `[R]` **Enable or disable color histogram:** Feature toggle in query settings.
- [x] `[R]` **Enable or disable color moments:** Feature toggle in query settings.
- [x] `[R]` **Enable or disable dominant colors:** Feature toggle in query settings.
- [x] `[R]` **Enable or disable GLCM:** Feature toggle in query settings.
- [x] `[R]` **Enable or disable LBP:** Feature toggle in query settings.
- [x] `[R]` **Select similarity metric:** Dropdown selector for Cosine Similarity or Euclidean Distance.
- [x] `[R]` **Configure feature normalization:** Min-max normalization and Z-score standardization options.
- [x] `[R]` **Validate descriptor compatibility:** Prevents queries with zero active descriptors.
- [x] `[R]` **Validate retrieval configuration:** Server-side schema validation via `/api/v1/query/config`.

#### Similarity Metrics
- [x] `[R]` **Cosine similarity:** Normalized inner product metric ($S_C(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$).
- [x] `[R]` **Euclidean distance:** Inverse Euclidean distance ($S_E(u, v) = \frac{1}{1 + \|u - v\|_2}$).
- [x] `[A]` **Additional similarity metrics:** Manhattan ($L_1$) distance and histogram intersection.

#### Search Results
- [x] `[M]` **Retrieve visually similar images:** Multi-descriptor scoring and candidate aggregation.
- [x] `[M]` **Rank retrieved images:** Sorted in descending order of similarity score.
- [x] `[R]` **Display image thumbnails:** High-performance responsive grid.
- [x] `[R]` **Display ranking position:** Rank badges (`#1`, `#2`, ... `#K`).
- [x] `[R]` **Display similarity scores:** Percentage match indicators (e.g. `94.2%`).
- [x] `[R]` **Display individual feature scores:** Breakdown sheet showing sub-scores per descriptor.
- [x] `[R]` **Display result metadata:** Filename, category, and dimensions.
- [x] `[R]` **Open a result's image details:** Direct navigation to full descriptor inspection page.
- [x] `[R]` **Display search execution time:** Millisecond timing breakdown (extraction vs. similarity vs. ranking).
- [x] `[R]` **Display total number of results:** Match counter and candidate set size.
- [x] `[R]` **Sort results by similarity:** Verified descending score ordering.
- [x] `[R]` **Support grid and list views:** Toggleable layout in SvelteKit frontend.

---

### 9. Relevance Feedback: Feature Relevance Estimation (Group 13)

This section implements the assigned **Group 13** research algorithm (*Reweighing Strategies for Relevance Feedback in CBIR*, Section III-B, Table 1).

#### A. User Feedback
- [x] `[M]` **Display initial retrieval results:** Render baseline Top-K candidate images.
- [x] `[M]` **Allow the user to mark an image as relevant:** One-click thumbs-up toggle.
- [x] `[M]` **Allow the user to mark an image as irrelevant:** One-click thumbs-down toggle.
- [x] `[R]` **Allow the user to change a judgment:** Interactive neutral / toggle states.
- [x] `[R]` **Display the number of relevant images:** Dynamic counter showing marked positive examples ($N_R$).
- [x] `[R]` **Display the number of irrelevant images:** Dynamic counter showing marked negative examples ($N_{IR}$).
- [x] `[R]` **Submit feedback:** `POST /api/v1/query/feedback` dispatching judged image sets.
- [x] `[R]` **Support multiple feedback iterations:** Incremental session loop ($t = 1, 2, 3\dots$).

#### B. Feature Relevance Estimation (FRE Algorithm Formulation)
- [x] `[M]` **Initialize feature importance:** Baseline equal weighting ($w_i = 1/M$) or user-configured initial weights.
- [x] `[M]` **Evaluate individual feature retrieval performance:** Independent evaluation across each active feature space.
- [x] `[M]` **Retrieve images using each feature independently:** Isolation of individual descriptor similarity rankings.
- [x] `[M]` **Count relevant images retrieved by each feature:** Calculation of positive hits per descriptor subspace.
- [x] `[M]` **Estimate feature relevance:** Dispersion analysis and variance estimation:
  $$v_i = \frac{1}{|R|} \sum_{x \in R} (x_i - \mu_{R, i})^2$$
- [x] `[M]` **Calculate feature weights using the paper's FRE formulation:**
  $$w_i \propto \frac{1}{v_i + \epsilon}, \quad \sum_{i=1}^M w_i = 1.0$$
- [x] `[M]` **Update the query representation using relevant images:** Centroid shift towards positive examples:
  $$q_{\text{new}} = \alpha \cdot q_{\text{orig}} + (1 - \alpha) \cdot \frac{1}{|R|} \sum_{x \in R} x$$
- [x] `[M]` **Implement weighted Euclidean distance:** Distance re-calculation with updated weights:
  $$D_w(x, y) = \sqrt{\sum_{i=1}^M w_i \cdot \|x_i - y_i\|^2}$$
- [x] `[M]` **Recalculate image similarities:** Fusion of updated weights and refined query centroid.
- [x] `[M]` **Rank images using updated feature relevance:** Generation of refined candidate ranking.
- [x] `[M]` **Return refined retrieval results:** Delivery of new Top-K ordering.

#### C. Feedback Analysis & Visualization
- [x] `[R]` **Display initial retrieval results:** Side-by-side or previous iteration preview.
- [x] `[R]` **Display refined retrieval results:** Live update of search results grid.
- [x] `[R]` **Compare initial and refined rankings:** Visual rank movement indicators ($\uparrow, \downarrow$).
- [x] `[R]` **Display feature relevance weights:** Numeric weight values per descriptor.
- [x] `[R]` **Visualize feature relevance:** Interactive bar chart illustrating dynamic weight shifts.
- [x] `[R]` **Display feedback iteration number:** `Iteration #1`, `Iteration #2` badges.
- [x] `[R]` **Display execution time per iteration:** Calculation latency metrics.
- [x] `[R]` **Display the number of relevant images retrieved:** Hit count tracking.
- [x] `[R]` **Allow another feedback iteration:** Continuous feedback loop with session state retention.

---

### 10. Retrieval History and Persistence

- [x] `[R]` **Save each retrieval query:** In-memory session tracking with session IDs (`_QUERY_SESSIONS`).
- [x] `[R]` **Save the query image reference:** Storage key and thumbnail references preserved.
- [x] `[R]` **Save retrieval configuration:** Metric, normalization, and descriptor toggles stored per session.
- [x] `[R]` **Save initial results:** Baseline rankings cached for iteration comparisons.
- [x] `[R]` **Save result ranking and scores:** Individual similarity scores retained.
- [x] `[R]` **Save individual descriptor scores:** Sub-scores per feature space cached.
- [x] `[R]` **Save user feedback:** Relevant and irrelevant ID lists persisted per iteration.
- [x] `[R]` **Save estimated feature relevance:** FRE weight vectors recorded per step.
- [x] `[R]` **Save refined results:** Iterative candidate rankings stored.
- [x] `[R]` **Save feedback iteration numbers:** Step index incrementation.
- [ ] `[R]` **Display previous searches:** Persistent search history table in database (`retrieval_queries`).
- [ ] `[R]` **Reopen a previous search:** Reload previous session state into search studio.
- [ ] `[R]` **Compare previous retrieval iterations:** Historical precision comparison graphs.
- [ ] `[R]` **Delete retrieval history.**

---

### 11. Evaluation and Benchmarking

- [x] `[R]` **Calculate Precision@K:** Ratio of relevant images in Top-K results:
  $$\text{Precision}@K = \frac{|\text{Relevant Images} \cap \text{Top-}K|}{K}$$
- [x] `[R]` **Calculate Recall@K:** Proportion of relevant images retrieved relative to ground truth category size:
  $$\text{Recall}@K = \frac{|\text{Relevant Images} \cap \text{Top-}K|}{N_{\text{total\_relevant}}}$$
- [ ] `[R]` **Calculate Mean Average Precision (mAP):** Academic mean ranking evaluation.
- [ ] `[A]` **Calculate NDCG@K:** Normalized Discounted Cumulative Gain.
- [x] `[R]` **Establish ground-truth relevance labels:** Derived from GHIM-10K category ground-truth folders (e.g. `sunset`, `ships`, `trees`).
- [x] `[R]` **Evaluate retrieval against dataset categories:** Category matching used as relevance indicator.
- [x] `[R]` **Compare color-only retrieval:** Benchmarking using only Histogram + Moments + Dominant Colors.
- [x] `[R]` **Compare texture-only retrieval:** Benchmarking using only GLCM + LBP.
- [x] `[R]` **Compare combined color and texture retrieval:** Multi-modal baseline evaluation.
- [x] `[R]` **Compare initial retrieval with FRE retrieval:** Measurable precision gain after Group 13 relevance feedback.
- [x] `[R]` **Measure retrieval execution time:** Timing profiler across similarity calculations.
- [x] `[R]` **Measure descriptor extraction time:** Execution benchmarks per descriptor algorithm.
- [ ] `[R]` **Display Precision-Recall graphs:** Interactive visual curves in evaluation dashboard.
- [ ] `[R]` **Export evaluation results:** CSV / JSON benchmark exporter.

---

### 12. API and Backend Reliability

- [x] `[M]` **Flask REST API:** Modular blueprint architecture (`auth`, `categories`, `images`, `descriptors`, `query`).
- [x] `[M]` **Flask-RESTful integration:** Standardized RESTful endpoints and error formatting.
- [x] `[R]` **JWT-protected private endpoints:** `@jwt_required()` authorization enforcement.
- [x] `[R]` **Input validation:** Schema validation across all query parameters and JSON payloads.
- [x] `[R]` **Consistent API response format:** Standard `{ "success": true, ... }` envelope.
- [x] `[R]` **Proper HTTP status codes:** Accurate `200`, `201`, `400`, `404`, `409`, and `500` status usage.
- [x] `[R]` **Error handling:** Global error handlers preventing unhandled stack trace leaks.
- [x] `[R]` **Upload size restrictions:** `MAX_CONTENT_LENGTH` enforcement (32MB).
- [x] `[R]` **Image content validation:** Pillow stream verification rejecting corrupted or forged files.
- [x] `[R]` **Secure image storage:** UUID4-based physical storage keys preventing original filename collisions.
- [x] `[R]` **Validate image ownership:** User scoping preventing unauthorized access.
- [x] `[R]` **Prevent path traversal:** Absolute storage key resolution checks denying `../` sequences.
- [x] `[R]` **Handle missing descriptors:** Graceful skipping and on-the-fly extraction fallbacks.
- [x] `[R]` **Handle incompatible retrieval configurations:** Validation preventing zero-descriptor queries.
- [x] `[R]` **Log extraction and retrieval errors:** Rotating logger capturing debug and error events.
- [x] `[R]` **API health endpoint:** `GET /` and `GET /api/v1/version` reporting system status.
- [x] `[R]` **Test API endpoints:** 64 automated Pytest tests validating routes and logic.
- [x] `[R]` **Test retrieval correctness:** Unit tests confirming vector similarity calculations and FRE weight updates.
- [x] `[R]` **Test unauthorized access:** Tests confirming cross-user isolation and unauthenticated rejections.

---

### 13. Settings and System Administration

- [x] `[R]` **User profile settings:** Profile viewer in `/settings`.
- [x] `[R]` **Application theme settings:** Dark, light, and system theme switcher.
- [x] `[R]` **Display storage usage:** Storage directory accounting in system telemetry.
- [x] `[R]` **Display dataset indexing status:** Live index counter and health summary.
- [x] `[R]` **Display extraction statistics:** Detailed vector count per descriptor type.
- [x] `[R]` **Display API status:** API version and supported protocols info.
- [x] `[R]` **Display supported image formats:** JPEG, PNG, WEBP, and BMP support display.
- [x] `[R]` **Display maximum upload size:** Configurable upload ceiling display.
- [x] `[R]` **Configure retrieval defaults:** Custom top-K, metric, and normalization defaults in search studio.
- [x] `[R]` **Configure descriptor extraction defaults:** Extractor versions and parameter configurations.
- [x] `[A]` **Administrative dataset re-indexing:** CLI ingestion tool with `--force` flag.
- [ ] `[A]` **Export system statistics.**

---

## 🔬 Mathematical Formulations

### 1. Visual Feature Descriptors

#### A. Color Histogram (HSV)
Given an image transformed to HSV color space, the 3D joint histogram $H(h, s, v)$ quantizes Hue into 8 bins, Saturation into 4 bins, and Value into 4 bins:
$$h \in [0, 7], \quad s \in [0, 3], \quad v \in [0, 3] \implies D_{\text{hist}} = 128 \text{ bins}$$
Normalized such that $\sum_{i=1}^{128} H_i = 1.0$.

#### B. Color Moments
Calculated across each color channel $k \in \{H, S, V\}$ over $N$ pixels:
1. **Mean ($\mu_k$):**
   $$\mu_k = \frac{1}{N} \sum_{j=1}^N p_{k, j}$$
2. **Standard Deviation ($\sigma_k$):**
   $$\sigma_k = \sqrt{\frac{1}{N} \sum_{j=1}^N (p_{k, j} - \mu_k)^2}$$
3. **Skewness ($s_k$):**
   $$s_k = \sqrt[3]{\frac{1}{N} \sum_{j=1}^N (p_{k, j} - \mu_k)^3}$$

#### C. Dominant Colors (CIE-Lab)
Images are converted to the perceptually uniform CIE-Lab space and clustered into $K = 5$ clusters using MiniBatch K-Means:
$$F_{\text{dominant}} = \Big\{ \big([L_k, a_k, b_k], p_k\big) \;\Big|\; k=1\dots5, \; \sum_{k=1}^5 p_k = 1.0 \Big\}$$

#### D. GLCM Texture Measurements
For normalized Gray-Level Co-occurrence Matrix $P(i, j)$ with distance $d=1$ and $\theta \in \{0^\circ, 45^\circ, 90^\circ, 135^\circ\}$:
- **Contrast:** $\sum_{i,j} |i - j|^2 P(i, j)$
- **Correlation:** $\sum_{i,j} \frac{(i - \mu_i)(j - \mu_j) P(i, j)}{\sigma_i \sigma_j}$
- **Energy (ASM):** $\sum_{i,j} P(i, j)^2$
- **Homogeneity:** $\sum_{i,j} \frac{P(i, j)}{1 + |i - j|}$

#### E. Local Binary Patterns (LBP)
Computed for $P = 8$ neighbors on radius $R = 1$:
$$\text{LBP}_{P, R}(x_c, y_c) = \sum_{p=0}^{P-1} s(g_p - g_c) \cdot 2^p, \quad s(z) = \begin{cases} 1 & z \ge 0 \\ 0 & z < 0 \end{cases}$$
Aggregated into a normalized 256-bin occurrence histogram.

---

### 2. Group 13: Feature Relevance Estimation (FRE)

Following *Reweighing Strategies for Relevance Feedback in CBIR* (Section III-B, Table 1):

1. **Relevant Set Dispersion ($v_i$):**
   For feature descriptor $i$ and set of user-judged relevant images $R = \{x^{(1)}, \dots, x^{(|R|)}\}$:
   $$v_i = \frac{1}{|R|} \sum_{x \in R} \|x_i - \mu_{R, i}\|^2, \quad \mu_{R, i} = \frac{1}{|R|} \sum_{x \in R} x_i$$

2. **Inverse Dispersion Weighting:**
   Features that exhibit low variance across relevant images are deemed highly descriptive:
   $$w_i' = \frac{1}{v_i + \epsilon}$$
   Normalized across all $M$ active feature descriptors:
   $$w_i = \frac{w_i'}{\sum_{j=1}^M w_j'}, \quad \sum_{i=1}^M w_i = 1.0$$

3. **Query Vector Refinement:**
   $$q_{\text{new}, i} = \alpha \cdot q_{\text{orig}, i} + (1 - \alpha) \cdot \mu_{R, i}$$

4. **Weighted Distance Scoring:**
   $$D_{\text{refined}}(x) = \sqrt{\sum_{i=1}^M w_i \cdot \|q_{\text{new}, i} - x_i\|^2}$$

---

## 📂 Project Structure

```
Perceptra/
├── pyproject.toml               # Python project configuration & CLI entry points
├── gunicorn.conf.py             # Production WSGI server configuration
├── src/
│   ├── app.py                   # Flask application factory & route registration
│   ├── cli.py                   # Management CLI (dataset ingest, db, dev, serve)
│   ├── config.py                # Environment configuration & defaults
│   ├── extensions.py            # SQLAlchemy, Bcrypt, JWT, SQLite WAL Pragmas
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py              # User account & authentication model
│   │   ├── category.py          # Hierarchical category model
│   │   ├── image.py             # Image metadata & transformation lineage
│   │   └── image_feature.py     # Extracted visual descriptors (JSON vectors)
│   ├── routes/                  # REST API Blueprints (/api/v1/...)
│   │   ├── auth.py              # Register, login, refresh, profile
│   │   ├── categories.py        # Hierarchical category management
│   │   ├── images.py            # Upload, stream, preview, transforms
│   │   ├── descriptors.py       # Descriptor extraction endpoints
│   │   └── query.py             # Visual search & Group 13 relevance feedback
│   └── services/                # Decoupled core business logic
│       ├── storage.py           # fsspec atomic filesystem storage
│       ├── image_service.py     # Image upload, validation, scoping
│       ├── transform_engine.py  # Pure Pillow geometric transforms & math bounds
│       ├── descriptor_engine.py # OpenCV/skimage color & texture feature extractor
│       ├── descriptor_service.py# Descriptor database persistence & management
│       ├── similarity_engine.py # Vector distance & similarity computation
│       ├── relevance_feedback.py# Group 13 Feature Relevance Estimation (FRE)
│       ├── query_service.py     # Multi-feature retrieval & session coordination
│       └── dataset_service.py   # Multi-threaded GHIM-10K ingestion engine
├── migrations/                  # Alembic database migration revisions
├── tests/                       # Pytest test suite (64 tests)
└── web/                         # SvelteKit modern frontend application
    ├── package.json
    ├── svelte.config.js
    ├── vite.config.ts
    └── src/
        ├── lib/                 # Shared components, API clients, i18n
        └── routes/              # SvelteKit pages
            ├── (auth)/          # Login and registration screens
            └── (dashboard)/     # Main application interface
                ├── dashboard/   # Overview, analytics, quick actions
                ├── categories/  # Category tree manager
                ├── images/      # Gallery browser and descriptor inspector
                ├── transform/   # Interactive transformation studio
                ├── upload/      # Drag-and-drop upload workbench
                └── query/       # Visual search & FRE relevance feedback studio
```

---

## 👥 Academic Information

- **Project:** Content-Based Image Retrieval (CBIR) Web Application
- **Group:** 13
- **Assigned Relevance Feedback Method:** Feature Relevance Estimation (FRE)
- **Institution:** Faculté des Sciences et Techniques de Tanger
- **Academic Year:** 2026–2027
