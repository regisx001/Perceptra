import hashlib
import io
import logging
import os
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PIL import Image as PILImage, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import db
from src.models.category import Category
from src.models.image import Image
from src.models.image_feature import ImageFeature
from src.models.user import User
from src.services.descriptor_engine import (
    DescriptorEngine,
    EXTRACTOR_VERSION,
    SUPPORTED_FEATURE_TYPES,
)
from src.services.image_service import SUPPORTED_IMAGE_FORMATS

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass
class IngestionStats:
    total_scanned: int = 0
    ingested: int = 0
    skipped: int = 0
    failed: int = 0
    features_computed: int = 0
    duration_seconds: float = 0.0
    categories: Dict[str, int] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = {}
        if self.errors is None:
            self.errors = []


class DatasetIngestionService:
    def __init__(self, storage_root: Optional[str] = None):
        self.storage_root = Path(storage_root or "storage").resolve()

    def find_target_user(self, email: Optional[str] = None) -> User:
        """
        Locates the target user for category ownership and dataset association.
        Falls back to the first user in the database if email is not provided.
        """
        if email:
            user = User.query.filter_by(email=email.strip().lower()).first()
            if not user:
                raise ValueError(f"User with email '{email}' does not exist.")
            return user

        user = User.query.order_by(User.created_at.asc()).first()
        if not user:
            raise ValueError("No users found in database. Please register a user first.")
        return user

    def scan_folder(self, folder_path: Path) -> Dict[str, List[Path]]:
        """
        Scans a dataset directory.
        If subdirectories exist with images, returns mapping: category_name -> [image_paths].
        If images exist directly in root, maps root name -> [image_paths].
        """
        folder_path = folder_path.resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            raise FileNotFoundError(f"Dataset path '{folder_path}' does not exist or is not a directory.")

        categories_map: Dict[str, List[Path]] = {}

        # 1. Check for subdirectories
        subdirs = [p for p in folder_path.iterdir() if p.is_dir() and not p.name.startswith(".")]

        for subdir in sorted(subdirs, key=lambda p: p.name.lower()):
            files = [
                f for f in subdir.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS and not f.name.startswith(".")
            ]
            if files:
                categories_map[subdir.name] = sorted(files, key=lambda p: p.name)

        # 2. Check for root-level image files
        root_files = [
            f for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS and not f.name.startswith(".")
        ]
        if root_files:
            root_cat_name = folder_path.name
            if root_cat_name in categories_map:
                categories_map[root_cat_name].extend(sorted(root_files, key=lambda p: p.name))
            else:
                categories_map[root_cat_name] = sorted(root_files, key=lambda p: p.name)

        return categories_map

    def ensure_categories(
        self,
        user_id: Optional[str],
        dataset_name: str,
        category_names: List[str],
        create_parent: bool = True,
    ) -> Dict[str, Category]:
        """
        Ensures category hierarchy exists in SQLite.
        If user_id is None, creates global dataset categories that do not clutter any user's library.
        If create_parent is True, creates a parent category with dataset_name,
        and makes category_names children of this parent.
        """
        cat_lookup: Dict[str, Category] = {}
        parent_category: Optional[Category] = None

        if create_parent and dataset_name:
            if user_id:
                parent_category = Category.query.filter_by(
                    user_id=user_id,
                    name=dataset_name,
                    parent_id=None,
                ).first()
            else:
                parent_category = Category.query.filter(
                    Category.user_id.is_(None),
                    Category.name == dataset_name,
                    Category.parent_id.is_(None),
                ).first()

            if not parent_category:
                parent_category = Category(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=dataset_name,
                    parent_id=None,
                )
                db.session.add(parent_category)
                db.session.flush()

        parent_id = parent_category.id if parent_category else None

        for cat_name in category_names:
            if user_id:
                category = Category.query.filter_by(
                    user_id=user_id,
                    name=cat_name,
                    parent_id=parent_id,
                ).first()
            else:
                category = Category.query.filter(
                    Category.user_id.is_(None),
                    Category.name == cat_name,
                    Category.parent_id == parent_id,
                ).first()

            if not category:
                category = Category(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=cat_name,
                    parent_id=parent_id,
                )
                db.session.add(category)
                db.session.flush()

            cat_lookup[cat_name] = category

        db.session.commit()
        return cat_lookup

    @staticmethod
    def _inspect_and_extract(
        file_path: Path,
        compute_features: bool = True,
    ) -> Tuple[bytes, str, int, int, str, Optional[Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]]]]:
        """
        Reads file bytes, computes SHA-256 checksum, detects true image dimensions and format,
        and optionally extracts all 5 visual descriptors using DescriptorEngine.
        """
        raw_bytes = file_path.read_bytes()
        if not raw_bytes:
            raise ValueError(f"File '{file_path}' is empty.")

        checksum = hashlib.sha256(raw_bytes).hexdigest()

        with PILImage.open(io.BytesIO(raw_bytes)) as img:
            width, height = img.size
            raw_fmt = (img.format or "").upper()

        if width <= 0 or height <= 0:
            raise ValueError(f"Image '{file_path}' has non-positive dimensions ({width}x{height}).")

        # Fallback to file extension mapping if format is unrecognized
        if raw_fmt in SUPPORTED_IMAGE_FORMATS:
            _, mime_type = SUPPORTED_IMAGE_FORMATS[raw_fmt]
        else:
            ext = file_path.suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
            }
            mime_type = mime_map.get(ext, "image/jpeg")

        features_data = None
        if compute_features:
            features_data = DescriptorEngine.extract(raw_bytes)

        return raw_bytes, checksum, width, height, mime_type, features_data

    def ingest_dataset(
        self,
        folder_path: Path,
        dataset_name: Optional[str] = None,
        user_email: Optional[str] = None,
        batch_size: int = 50,
        limit: Optional[int] = None,
        compute_features: bool = True,
        skip_existing: bool = True,
        create_parent_category: bool = True,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[int, int, str, str], None]] = None,
    ) -> IngestionStats:
        """
        Ingests all images from the folder into storage and SQLite with full feature computation.
        """
        t0 = time.time()
        folder_path = folder_path.resolve()
        dataset_name = dataset_name or folder_path.name
        stats = IngestionStats()

        # 1. Target user (None for global datasets, isolated from user personal library)
        target_user = self.find_target_user(user_email) if user_email else None
        user_id = target_user.id if target_user else None

        # 2. Scan categories and image files
        categories_map = self.scan_folder(folder_path)
        if not categories_map:
            stats.duration_seconds = time.time() - t0
            return stats

        # Count total scanned items
        all_items: List[Tuple[str, Path]] = []
        for cat_name, file_paths in categories_map.items():
            for p in file_paths:
                all_items.append((cat_name, p))

        stats.total_scanned = len(all_items)
        if limit and limit > 0:
            all_items = all_items[:limit]

        # 3. Create or fetch categories
        unique_categories = sorted(list(categories_map.keys()))
        cat_lookup = self.ensure_categories(
            user_id=user_id,
            dataset_name=dataset_name,
            category_names=unique_categories,
            create_parent=create_parent_category,
        )

        # 4. Process in batches with multithreaded extraction
        total_to_process = len(all_items)
        processed_count = 0

        for i in range(0, total_to_process, batch_size):
            chunk = all_items[i : i + batch_size]
            pending_db_images: List[Image] = []
            pending_db_features: List[ImageFeature] = []

            # Multi-threaded file read and feature extraction
            tasks = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for cat_name, file_path in chunk:
                    future = executor.submit(
                        self._inspect_and_extract,
                        file_path=file_path,
                        compute_features=compute_features,
                    )
                    tasks.append((cat_name, file_path, future))

                for cat_name, file_path, future in tasks:
                    processed_count += 1
                    status_text = f"Processing {file_path.name}"
                    if progress_callback:
                        progress_callback(processed_count, total_to_process, file_path.name, cat_name)

                    try:
                        raw_bytes, checksum, width, height, mime_type, features_data = future.result()
                    except Exception as exc:
                        stats.failed += 1
                        err_msg = f"Failed to read/extract {file_path}: {exc}"
                        logger.warning(err_msg)
                        stats.errors.append(err_msg)
                        continue

                    # Storage key relative path: datasets/{dataset_name}/{category_name}/{filename}
                    safe_cat_dir = cat_name.replace("/", "_").replace("\\", "_")
                    safe_ds_dir = dataset_name.replace("/", "_").replace("\\", "_")
                    storage_key = f"datasets/{safe_ds_dir}/{safe_cat_dir}/{file_path.name}"
                    dest_path = self.storage_root / storage_key

                    # Check existing image in DB by storage_key or checksum
                    existing_image = Image.query.filter(
                        (Image.storage_key == storage_key) | (Image.checksum == checksum)
                    ).first()

                    if existing_image:
                        if skip_existing:
                            # If features missing and compute_features is requested, backfill features
                            if compute_features and features_data:
                                existing_feat_types = {
                                    f.feature_type for f in ImageFeature.query.filter_by(
                                        image_id=existing_image.id,
                                        extractor_version=EXTRACTOR_VERSION,
                                    ).all()
                                }
                                missing_types = set(SUPPORTED_FEATURE_TYPES) - existing_feat_types
                                if missing_types:
                                    for ft, (params, fvalues) in features_data.items():
                                        if ft in missing_types:
                                            feat = ImageFeature(
                                                id=str(uuid.uuid4()),
                                                image_id=existing_image.id,
                                                feature_type=ft,
                                                extractor_version=EXTRACTOR_VERSION,
                                                feature_values=fvalues,
                                                parameters=params,
                                            )
                                            pending_db_features.append(feat)
                                            stats.features_computed += 1
                                    existing_image.processing_status = "indexed"

                            stats.skipped += 1
                            continue
                        else:
                            # Overwrite existing image record
                            image_record = existing_image
                            image_record.width = width
                            image_record.height = height
                            image_record.file_size = len(raw_bytes)
                            image_record.mime_type = mime_type
                            image_record.processing_status = "indexed" if features_data else "pending"
                    else:
                        # Copy file physically to storage if not already there
                        try:
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            if not dest_path.exists() or dest_path.resolve() != file_path.resolve():
                                shutil.copy2(file_path, dest_path)
                        except Exception as exc:
                            stats.failed += 1
                            err_msg = f"Failed to copy '{file_path}' to '{dest_path}': {exc}"
                            logger.error(err_msg)
                            stats.errors.append(err_msg)
                            continue

                        category_record = cat_lookup.get(cat_name)
                        new_img_id = str(uuid.uuid4())
                        image_record = Image(
                            id=new_img_id,
                            owner_id=user_id,
                            category_id=category_record.id if category_record else None,
                            filename=file_path.name,
                            storage_key=storage_key,
                            source_type="dataset",
                            processing_status="indexed" if features_data else "pending",
                            mime_type=mime_type,
                            file_size=len(raw_bytes),
                            width=width,
                            height=height,
                            checksum=checksum,
                        )
                        pending_db_images.append(image_record)

                    # Create ImageFeature records
                    if features_data:
                        for ft, (params, fvalues) in features_data.items():
                            feat = ImageFeature(
                                id=str(uuid.uuid4()),
                                image_id=image_record.id,
                                feature_type=ft,
                                extractor_version=EXTRACTOR_VERSION,
                                feature_values=fvalues,
                                parameters=params,
                            )
                            pending_db_features.append(feat)
                            stats.features_computed += 1

                    stats.ingested += 1
                    stats.categories[cat_name] = stats.categories.get(cat_name, 0) + 1

            # Commit batch to database
            try:
                for img in pending_db_images:
                    db.session.add(img)
                db.session.flush()

                for feat in pending_db_features:
                    db.session.add(feat)

                db.session.commit()
            except SQLAlchemyError as exc:
                db.session.rollback()
                stats.failed += len(chunk)
                err_msg = f"Database batch commit failed: {exc}"
                logger.error(err_msg)
                stats.errors.append(err_msg)

        stats.duration_seconds = time.time() - t0
        return stats

    def remove_dataset(
        self,
        dataset_name: Optional[str] = None,
        remove_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Removes dataset images, descriptors, categories, and physical files.
        - dataset_name: specific dataset to remove (e.g. 'GHIM-10K').
        - remove_all: if True, removes all images where source_type == 'dataset'.
        User uploads and user accounts are preserved.
        """
        from src.models.category import Category
        from src.models.favorite import FavoriteImage
        from src.models.image import Image
        from src.models.image_feature import ImageFeature
        from src.models.retrieval import RetrievalQuery, RetrievalResult

        stats = {
            "images_deleted": 0,
            "features_deleted": 0,
            "categories_deleted": 0,
            "files_removed": False,
        }

        # 1. Identify target images and categories
        target_categories: List[Category] = []
        if remove_all:
            images = Image.query.filter_by(source_type="dataset").all()
            root_dataset_cats = Category.query.filter(
                Category.parent_id.is_(None), Category.user_id.is_(None)
            ).all()
            for root_cat in root_dataset_cats:
                target_categories.append(root_cat)
                target_categories.extend(root_cat.subcategories)
        elif dataset_name:
            safe_ds_dir = dataset_name.replace("/", "_").replace("\\", "_")
            images = Image.query.filter(
                Image.source_type == "dataset",
                Image.storage_key.like(f"datasets/{safe_ds_dir}/%"),
            ).all()
            root_cat = Category.query.filter(
                Category.name == dataset_name, Category.parent_id.is_(None)
            ).first()
            if root_cat:
                target_categories.append(root_cat)
                target_categories.extend(root_cat.subcategories)
        else:
            raise ValueError("Must specify either dataset_name or remove_all=True")

        image_ids = [img.id for img in images]
        stats["images_deleted"] = len(image_ids)

        # 2. Delete linked records and images in batches
        if image_ids:
            for k in range(0, len(image_ids), 500):
                chunk_ids = image_ids[k : k + 500]
                # Break FK references from queries
                RetrievalQuery.query.filter(
                    RetrievalQuery.query_image_id.in_(chunk_ids)
                ).update({RetrievalQuery.query_image_id: None}, synchronize_session=False)

                # Delete results & favorites referencing these images
                RetrievalResult.query.filter(
                    RetrievalResult.image_id.in_(chunk_ids)
                ).delete(synchronize_session=False)
                FavoriteImage.query.filter(
                    FavoriteImage.image_id.in_(chunk_ids)
                ).delete(synchronize_session=False)

                # Delete feature vectors
                feat_count = ImageFeature.query.filter(
                    ImageFeature.image_id.in_(chunk_ids)
                ).delete(synchronize_session=False)
                stats["features_deleted"] += feat_count

                # Delete images
                Image.query.filter(Image.id.in_(chunk_ids)).delete(
                    synchronize_session=False
                )

        # 3. Clean up categories (children first, then root parents)
        children = [c for c in target_categories if c.parent_id is not None]
        parents = [c for c in target_categories if c.parent_id is None]

        for cat in children:
            remaining = Image.query.filter_by(category_id=cat.id).count()
            if remaining == 0:
                db.session.delete(cat)
                stats["categories_deleted"] += 1
        db.session.flush()

        for cat in parents:
            remaining = Image.query.filter_by(category_id=cat.id).count()
            if remaining == 0:
                db.session.delete(cat)
                stats["categories_deleted"] += 1

        db.session.commit()

        # 4. Clean up disk files in storage/datasets
        if remove_all:
            datasets_dir = self.storage_root / "datasets"
            if datasets_dir.exists():
                shutil.rmtree(datasets_dir, ignore_errors=True)
                datasets_dir.mkdir(parents=True, exist_ok=True)
                stats["files_removed"] = True
        elif dataset_name:
            safe_ds_dir = dataset_name.replace("/", "_").replace("\\", "_")
            ds_dir = self.storage_root / "datasets" / safe_ds_dir
            if ds_dir.exists():
                shutil.rmtree(ds_dir, ignore_errors=True)
                stats["files_removed"] = True

        return stats
