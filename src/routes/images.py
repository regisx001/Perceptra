from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.services.image_service import ImageService, ImageServiceError
from src.services.storage import Storage

images_bp = Blueprint("images", __name__)


def get_image_service() -> ImageService:
    cfg = current_app.config
    storage = Storage(
        root_dir=cfg.get("STORAGE_BASE_PATH", "storage"),
        protocol=cfg.get("STORAGE_PROTOCOL", "file"),
    )
    max_size = cfg.get("MAX_CONTENT_LENGTH") or (32 * 1024 * 1024)
    return ImageService(storage=storage, max_file_size=int(max_size))


@images_bp.errorhandler(ImageServiceError)
def handle_image_service_error(err: ImageServiceError):
    return jsonify({"success": False, "error": str(err)}), err.status_code


@images_bp.route("", methods=["POST"])
@jwt_required()
def upload_image():
    user_id = str(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in request."}), 400

    uploaded = request.files["file"]
    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "error": "No selected file."}), 400

    category_id = request.form.get("category_id", "").strip() or None
    raw_bytes = uploaded.read()

    service = get_image_service()
    image = service.upload_image(
        user_id=user_id,
        raw_bytes=raw_bytes,
        original_filename=uploaded.filename,
        category_id=category_id,
    )

    return jsonify({"success": True, "image": image.to_dict()}), 201


@images_bp.route("", methods=["GET"])
@jwt_required()
def list_images():
    user_id = str(get_jwt_identity())
    category_id = request.args.get("category_id", "").strip() or None
    uncategorized = request.args.get("uncategorized", "false").lower() in {"true", "1", "yes"}
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 24, type=int)))

    service = get_image_service()
    pagination = service.list_user_images(
        user_id=user_id,
        category_id=category_id,
        uncategorized_only=uncategorized,
        page=page,
        per_page=per_page,
    )

    return jsonify({
        "success": True,
        "images": [img.to_dict() for img in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }), 200


@images_bp.route("/<image_id>", methods=["GET"])
@jwt_required()
def get_image(image_id: str):
    user_id = str(get_jwt_identity())
    service = get_image_service()
    image = service.get_user_image(user_id=user_id, image_id=image_id)
    return jsonify({"success": True, "image": image.to_dict()}), 200


@images_bp.route("/<image_id>/file", methods=["GET"])
@jwt_required()
def get_image_file(image_id: str):
    user_id = str(get_jwt_identity())
    as_attachment = request.args.get("download", "false").lower() in {"true", "1", "yes"}

    service = get_image_service()
    image, stream = service.open_image_stream(user_id=user_id, image_id=image_id)

    return send_file(
        stream,
        mimetype=image.mime_type,
        as_attachment=as_attachment,
        download_name=image.filename,
    )


@images_bp.route("/<image_id>", methods=["PATCH"])
@jwt_required()
def update_image_category(image_id: str):
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    if "category_id" not in data:
        return jsonify({"success": False, "error": "category_id field is required."}), 400

    category_id = data["category_id"] or None
    service = get_image_service()
    service.assign_category(user_id=user_id, image_ids=[image_id], category_id=category_id)
    updated = service.get_user_image(user_id=user_id, image_id=image_id)

    return jsonify({"success": True, "image": updated.to_dict()}), 200


@images_bp.route("/bulk-assign", methods=["POST"])
@jwt_required()
def bulk_assign_category():
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    image_ids = data.get("image_ids")
    if not isinstance(image_ids, list) or not image_ids:
        return jsonify({"success": False, "error": "image_ids non-empty list is required."}), 400

    category_id = data.get("category_id") or None
    service = get_image_service()
    updated_count = service.assign_category(
        user_id=user_id,
        image_ids=image_ids,
        category_id=category_id,
    )

    return jsonify({"success": True, "updated_count": updated_count}), 200


@images_bp.route("/<image_id>", methods=["DELETE"])
@jwt_required()
def delete_image(image_id: str):
    user_id = str(get_jwt_identity())
    service = get_image_service()
    service.delete_image(user_id=user_id, image_id=image_id)
    return jsonify({"success": True, "message": "Image deleted."}), 200


@images_bp.route("/bulk-delete", methods=["POST"])
@jwt_required()
def bulk_delete_images():
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    image_ids = data.get("image_ids")
    if not isinstance(image_ids, list) or not image_ids:
        return jsonify({"success": False, "error": "image_ids non-empty list is required."}), 400

    service = get_image_service()
    deleted_count = service.bulk_delete_images(user_id=user_id, image_ids=image_ids)
    return jsonify({"success": True, "deleted_count": deleted_count}), 200
