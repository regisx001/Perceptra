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
    favorites = request.args.get("favorites", "false").lower() in {"true", "1", "yes"}
    source_type = request.args.get("source_type", "").strip() or None
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 24, type=int)))

    service = get_image_service()
    pagination = service.list_user_images(
        user_id=user_id,
        category_id=category_id,
        uncategorized_only=uncategorized,
        favorites_only=favorites,
        source_type=source_type,
        page=page,
        per_page=per_page,
    )

    return jsonify({
        "success": True,
        "images": [img.to_dict(user_id=user_id) for img in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }), 200


@images_bp.route("/<image_id>/favorite", methods=["POST"])
@jwt_required()
def toggle_image_favorite(image_id: str):
    user_id = str(get_jwt_identity())
    service = get_image_service()
    is_favorite = service.toggle_favorite(user_id=user_id, image_id=image_id)
    return jsonify({
        "success": True,
        "image_id": image_id,
        "is_favorite": is_favorite,
        "message": "Image marked as favorite" if is_favorite else "Image removed from favorites",
    }), 200


@images_bp.route("/<image_id>", methods=["GET"])
@jwt_required()
def get_image(image_id: str):
    user_id = str(get_jwt_identity())
    service = get_image_service()
    image = service.get_user_image(user_id=user_id, image_id=image_id)
    return jsonify({"success": True, "image": image.to_dict(user_id=user_id)}), 200


@images_bp.route("/<image_id>/file", methods=["GET"])
@jwt_required()
def get_image_file(image_id: str):
    user_id = str(get_jwt_identity())
    as_attachment = request.args.get("download", "false").lower() in {"true", "1", "yes"}
    preview = request.args.get("preview", "false").lower() in {"true", "1", "yes"}

    service = get_image_service()
    image, stream, mime_type = service.open_image_stream(
        user_id=user_id,
        image_id=image_id,
        preview=preview,
    )

    download_name = image.filename
    if preview and mime_type == "image/jpeg" and not download_name.lower().endswith((".jpg", ".jpeg")):
        download_name = f"{download_name.rsplit('.', 1)[0]}_preview.jpg"

    return send_file(
        stream,
        mimetype=mime_type,
        as_attachment=as_attachment,
        download_name=download_name,
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


@images_bp.route("/<image_id>/transform-validate", methods=["POST"])
@jwt_required()
def transform_validate_route(image_id: str):
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    operation = data.get("operation")
    if not operation or not isinstance(operation, str):
        return jsonify({"success": False, "error": "operation field is required."}), 400

    params = data.get("params")
    if not isinstance(params, dict):
        return jsonify({"success": False, "error": "params object is required."}), 400

    service = get_image_service()
    result = service.validate_transform_dimensions(
        user_id=user_id,
        image_id=image_id,
        operation=operation,
        params=params,
    )

    return jsonify({"success": True, **result}), 200


@images_bp.route("/<image_id>/transform", methods=["POST"])
@jwt_required()
def transform_image_route(image_id: str):
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    operation = data.get("operation")
    if not operation or not isinstance(operation, str):
        return jsonify({"success": False, "error": "operation field is required."}), 400

    params = data.get("params")
    if not isinstance(params, dict):
        return jsonify({"success": False, "error": "params object is required."}), 400

    filename = data.get("filename")
    category_id = data.get("category_id")

    service = get_image_service()
    derived = service.transform_image(
        user_id=user_id,
        image_id=image_id,
        operation=operation,
        params=params,
        filename=filename,
        category_id=category_id,
    )

    return jsonify({"success": True, "image": derived.to_dict()}), 201


@images_bp.route("/<image_id>/derivatives", methods=["GET"])
@jwt_required()
def list_derivatives_route(image_id: str):
    user_id = str(get_jwt_identity())
    service = get_image_service()
    derivatives = service.list_derivatives(user_id=user_id, image_id=image_id)

    return jsonify({
        "success": True,
        "parent_image_id": image_id,
        "derivatives": [d.to_dict() for d in derivatives],
    }), 200
