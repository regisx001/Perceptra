import logging
from typing import Any, Dict, List, Optional
from src.extensions import db
from src.models.image import Image
from src.models.image_feature import ImageFeature
from src.services.descriptor_engine import (
    DescriptorEngine,
    EXTRACTOR_VERSION,
    InvalidImageStreamError,
    SUPPORTED_FEATURE_TYPES,
    UnsupportedFeatureTypeError,
)
from src.services.storage import StorageBackend, StorageError

logger = logging.getLogger(__name__)


class DescriptorServiceError(Exception):
    """Base exception for descriptor service."""
    status_code = 500

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class ResourceNotFoundError(DescriptorServiceError):
    status_code = 404


class ValidationError(DescriptorServiceError):
    status_code = 400


class UnprocessableImageError(DescriptorServiceError):
    status_code = 422


class DescriptorService:
    """
    Coordinates storage retrieval, descriptor extraction, persistence in SQLite,
    and image processing_status lifecycle transitions.
    """

    MAX_BATCH_SIZE = 50

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def get_image(self, image_id: str, user_id: Optional[str] = None) -> Image:
        """
        Retrieves an Image record and validates user ownership/access.
        """
        query = Image.query.filter(Image.id == image_id)
        if user_id:
            query = query.filter((Image.owner_id == user_id) | (Image.owner_id.is_(None)))

        image = query.first()
        if not image:
            raise ResourceNotFoundError(f"Image '{image_id}' not found or access denied.")
        return image

    def get_descriptors(self, image_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves all currently stored visual descriptors for an image.
        """
        image = self.get_image(image_id, user_id)

        features = ImageFeature.query.filter_by(
            image_id=image.id,
            extractor_version=EXTRACTOR_VERSION,
        ).all()

        descriptors: Dict[str, Any] = {}
        for feat in features:
            descriptors[feat.feature_type] = feat.feature_values

        available_features = sorted(list(descriptors.keys()))

        return {
            "success": True,
            "image_id": image.id,
            "processing_status": image.processing_status,
            "available_features": available_features,
            "descriptors": descriptors,
        }

    def extract_for_image(
        self,
        image_id: str,
        user_id: Optional[str] = None,
        feature_types: Optional[List[str]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Extracts and persists requested visual descriptors for a single image.
        Skips already computed features if force=False.
        """
        image = self.get_image(image_id, user_id)

        requested = list(feature_types) if feature_types else sorted(list(SUPPORTED_FEATURE_TYPES))
        for ft in requested:
            if ft not in SUPPORTED_FEATURE_TYPES:
                raise ValidationError(
                    f"Unknown feature type '{ft}'. Supported: {', '.join(sorted(SUPPORTED_FEATURE_TYPES))}"
                )

        # Check existing features if force=False
        to_extract: List[str] = []
        cached_descriptors: Dict[str, Any] = {}

        if not force:
            existing_features = ImageFeature.query.filter(
                ImageFeature.image_id == image.id,
                ImageFeature.extractor_version == EXTRACTOR_VERSION,
                ImageFeature.feature_type.in_(requested),
            ).all()

            existing_map = {feat.feature_type: feat for feat in existing_features}
            for ft in requested:
                if ft in existing_map:
                    cached_descriptors[ft] = existing_map[ft].feature_values
                else:
                    to_extract.append(ft)
        else:
            to_extract = requested

        final_descriptors = dict(cached_descriptors)

        if to_extract:
            # 1. Read bytes from storage
            try:
                with self.storage.open(image.storage_key, "rb") as f_in:
                    image_bytes = f_in.read()
            except (StorageError, OSError, FileNotFoundError) as exc:
                image.processing_status = "failed"
                db.session.commit()
                raise UnprocessableImageError(f"Could not read physical image file from storage: {exc}") from exc

            # 2. Extract features via DescriptorEngine
            try:
                extraction_results = DescriptorEngine.extract(image_bytes, to_extract)
            except InvalidImageStreamError as exc:
                image.processing_status = "failed"
                db.session.commit()
                raise UnprocessableImageError(f"Corrupted or invalid image stream: {exc}") from exc
            except UnsupportedFeatureTypeError as exc:
                raise ValidationError(str(exc)) from exc

            # 3. Upsert into image_features table
            for ft, (params, f_vals) in extraction_results.items():
                existing = ImageFeature.query.filter_by(
                    image_id=image.id,
                    feature_type=ft,
                    extractor_version=EXTRACTOR_VERSION,
                ).first()

                if existing:
                    existing.parameters = params
                    existing.feature_values = f_vals
                else:
                    feat = ImageFeature(
                        image_id=image.id,
                        feature_type=ft,
                        extractor_version=EXTRACTOR_VERSION,
                        parameters=params,
                        feature_values=f_vals,
                    )
                    db.session.add(feat)

                final_descriptors[ft] = f_vals

        # 4. Transition processing status to indexed
        image.processing_status = "indexed"
        db.session.commit()

        return {
            "success": True,
            "image_id": image.id,
            "processing_status": image.processing_status,
            "descriptors": final_descriptors,
        }

    def extract_batch(
        self,
        image_ids: List[str],
        user_id: Optional[str] = None,
        feature_types: Optional[List[str]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Batch extracts descriptors for up to 50 images in a single request.
        """
        if not isinstance(image_ids, list):
            raise ValidationError("'image_ids' must be a list of string identifiers.")

        if len(image_ids) == 0:
            raise ValidationError("'image_ids' list cannot be empty.")

        if len(image_ids) > self.MAX_BATCH_SIZE:
            raise ValidationError(
                f"Batch size of {len(image_ids)} exceeds maximum limit of {self.MAX_BATCH_SIZE} images."
            )

        requested = list(feature_types) if feature_types else sorted(list(SUPPORTED_FEATURE_TYPES))
        for ft in requested:
            if ft not in SUPPORTED_FEATURE_TYPES:
                raise ValidationError(
                    f"Unknown feature type '{ft}'. Supported: {', '.join(sorted(SUPPORTED_FEATURE_TYPES))}"
                )

        results: List[Dict[str, Any]] = []
        indexed_count = 0
        failed_count = 0

        for img_id in image_ids:
            try:
                self.extract_for_image(
                    image_id=img_id,
                    user_id=user_id,
                    feature_types=requested,
                    force=force,
                )
                results.append({"image_id": img_id, "status": "indexed"})
                indexed_count += 1
            except Exception as exc:
                logger.warning(f"Batch extraction failed for image '{img_id}': {exc}")
                results.append({"image_id": img_id, "status": "failed", "error": str(exc)})
                failed_count += 1

        return {
            "success": True,
            "total": len(image_ids),
            "indexed": indexed_count,
            "failed": failed_count,
            "results": results,
        }
