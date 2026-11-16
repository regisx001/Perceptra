from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Api, Resource

from src.services.descriptor_service import (
    DescriptorService,
    DescriptorServiceError,
)
from src.services.storage import Storage

descriptors_bp = Blueprint("descriptors", __name__)
api = Api(descriptors_bp)


def get_descriptor_service() -> DescriptorService:
    cfg = current_app.config
    storage = Storage(
        root_dir=cfg.get("STORAGE_BASE_PATH", "storage"),
        protocol=cfg.get("STORAGE_PROTOCOL", "file"),
    )
    return DescriptorService(storage=storage)


class SingleImageDescriptorResource(Resource):
    @jwt_required()
    def post(self, image_id: str):
        """
        POST /api/v1/descriptors/extract/<image_id>
        Extracts requested or all visual descriptors for a single image.
        """
        user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        feature_types = data.get("feature_types")
        force = bool(data.get("force", False))

        service = get_descriptor_service()
        try:
            result = service.extract_for_image(
                image_id=image_id,
                user_id=user_id,
                feature_types=feature_types,
                force=force,
            )
            return result, 200
        except DescriptorServiceError as exc:
            return {"success": False, "error": str(exc)}, exc.status_code
        except Exception as exc:
            return {"success": False, "error": f"Extraction error: {exc}"}, 500


class BatchDescriptorResource(Resource):
    @jwt_required()
    def post(self):
        """
        POST /api/v1/descriptors/extract-batch
        Batch extracts descriptors for up to 50 images in a single request.
        """
        user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        image_ids = data.get("image_ids")
        if not image_ids or not isinstance(image_ids, list):
            return {
                "success": False,
                "error": "'image_ids' must be a non-empty list of string IDs.",
            }, 400

        feature_types = data.get("feature_types")
        force = bool(data.get("force", False))

        service = get_descriptor_service()
        try:
            result = service.extract_batch(
                image_ids=image_ids,
                user_id=user_id,
                feature_types=feature_types,
                force=force,
            )
            return result, 200
        except DescriptorServiceError as exc:
            return {"success": False, "error": str(exc)}, exc.status_code
        except Exception as exc:
            return {"success": False, "error": f"Batch extraction error: {exc}"}, 500


class ImageDescriptorViewResource(Resource):
    @jwt_required()
    def get(self, image_id: str):
        """
        GET /api/v1/images/<image_id>/descriptors
        Retrieves stored descriptors and extraction processing status for an image.
        """
        user_id = get_jwt_identity()
        service = get_descriptor_service()
        try:
            result = service.get_descriptors(image_id=image_id, user_id=user_id)
            return result, 200
        except DescriptorServiceError as exc:
            return {"success": False, "error": str(exc)}, exc.status_code
        except Exception as exc:
            return {"success": False, "error": f"Retrieval error: {exc}"}, 500


api.add_resource(
    SingleImageDescriptorResource,
    "/descriptors/extract/<image_id>",
)
api.add_resource(
    BatchDescriptorResource,
    "/descriptors/extract-batch",
)
api.add_resource(
    ImageDescriptorViewResource,
    "/images/<image_id>/descriptors",
)
