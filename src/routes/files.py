import hashlib
import io
import mimetypes
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    request,
    send_file,
)
from PIL import Image, UnidentifiedImageError

from src.services.storage import (
    InvalidStorageKeyError,
    Storage,
    StorageNotFoundError,
)

files_bp = Blueprint("files", __name__)


def get_storage() -> Storage:
    """Helper to instantiate Storage service using current app configuration."""
    cfg = current_app.config
    protocol = cfg.get("STORAGE_PROTOCOL", "file")
    base_path = cfg.get("STORAGE_BASE_PATH", "storage")
    return Storage(root_dir=base_path, protocol=protocol)


def validate_and_inspect_image(stream: io.BytesIO):
    """Inspects and validates an image file stream using Pillow."""
    try:
        stream.seek(0)
        with Image.open(stream) as img:
            img.verify()
            width, height = img.size
            img_format = img.format or "UNKNOWN"
            stream.seek(0)
            return True, width, height, img_format
    except (UnidentifiedImageError, OSError, ValueError):
        stream.seek(0)
        return False, None, None, None


@files_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Upload a single file or image.
    Form-data parameter: 'file'
    Optional form-data parameter: 'folder'
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    uploaded = request.files["file"]
    if not uploaded or uploaded.filename == "":
        return jsonify({"error": "No selected file"}), 400

    folder = request.form.get("folder", "uploads")
    validate_image = request.form.get("validate_image", "true").lower() in {"true", "1", "yes"}

    raw_bytes = uploaded.read()
    if not raw_bytes:
        return jsonify({"error": "Uploaded file is empty"}), 400

    original_filename = uploaded.filename
    ext = ("." + original_filename.rsplit(".", 1)[-1].lower()) if "." in original_filename else ""

    allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS")
    if allowed_exts:
        clean_ext = ext.lstrip(".").lower()
        if clean_ext not in [e.lower() for e in allowed_exts]:
            return jsonify({"error": f"File extension '{clean_ext}' is not allowed"}), 400

    is_img, width, height, img_fmt = False, None, None, None
    if validate_image:
        is_img, width, height, img_fmt = validate_and_inspect_image(io.BytesIO(raw_bytes))
        if not is_img:
            return jsonify({"error": "Invalid or corrupted image file"}), 400

    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    content_type = uploaded.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

    storage = get_storage()
    try:
        storage_key = storage.save(
            file=raw_bytes,
            directory=folder,
            extension=ext or ".bin",
        )
        return jsonify({
            "success": True,
            "file": {
                "storage_path": storage_key,
                "original_filename": original_filename,
                "content_type": content_type,
                "size_bytes": len(raw_bytes),
                "sha256_hash": sha256_hash,
                "is_image": is_img,
                "width": width,
                "height": height,
                "format": img_fmt,
            }
        }), 201
    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500


@files_bp.route("/upload-batch", methods=["POST"])
def upload_batch():
    """
    Upload multiple files or images in one request.
    Form-data parameter: 'files' (multiple entries)
    """
    uploaded_files = request.files.getlist("files")
    if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ""):
        return jsonify({"error": "No files provided"}), 400

    folder = request.form.get("folder", "uploads")
    validate_image = request.form.get("validate_image", "true").lower() in {"true", "1", "yes"}

    storage = get_storage()
    allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS")
    results = []
    errors = []

    for uploaded in uploaded_files:
        if not uploaded.filename:
            continue
        try:
            raw_bytes = uploaded.read()
            if not raw_bytes:
                raise ValueError("Uploaded file is empty")

            original_filename = uploaded.filename
            ext = ("." + original_filename.rsplit(".", 1)[-1].lower()) if "." in original_filename else ""

            if allowed_exts:
                clean_ext = ext.lstrip(".").lower()
                if clean_ext not in [e.lower() for e in allowed_exts]:
                    raise ValueError(f"File extension '{clean_ext}' is not allowed")

            is_img, width, height, img_fmt = False, None, None, None
            if validate_image:
                is_img, width, height, img_fmt = validate_and_inspect_image(io.BytesIO(raw_bytes))
                if not is_img:
                    raise ValueError("Invalid or corrupted image file")

            sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
            content_type = uploaded.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

            storage_key = storage.save(
                file=raw_bytes,
                directory=folder,
                extension=ext or ".bin",
            )
            results.append({
                "storage_path": storage_key,
                "original_filename": original_filename,
                "content_type": content_type,
                "size_bytes": len(raw_bytes),
                "sha256_hash": sha256_hash,
                "is_image": is_img,
                "width": width,
                "height": height,
                "format": img_fmt,
            })
        except Exception as e:
            errors.append({"filename": uploaded.filename, "error": str(e)})

    return jsonify({
        "success": len(errors) == 0,
        "files": results,
        "errors": errors,
        "uploaded_count": len(results),
    }), 201 if results else 400


@files_bp.route("/download/<path:filepath>", methods=["GET"])
def download_file(filepath: str):
    """
    Download a file from storage.
    Query parameter: as_attachment=true/false (defaults to false for inline display)
    """
    as_attachment = request.args.get("as_attachment", "false").lower() in {"true", "1", "yes"}
    storage = get_storage()

    try:
        content = storage.read_bytes(filepath)
        filename = filepath.rsplit("/", 1)[-1]
        return send_file(
            io.BytesIO(content),
            as_attachment=as_attachment,
            download_name=filename,
        )
    except (StorageNotFoundError, InvalidStorageKeyError):
        return jsonify({"error": f"File not found: {filepath}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@files_bp.route("/stream/<path:filepath>", methods=["GET"])
def stream_file(filepath: str):
    """
    Stream a file from storage.
    """
    storage = get_storage()
    try:
        if not storage.exists(filepath):
            return jsonify({"error": f"File not found: {filepath}"}), 404

        mime_type = "application/octet-stream"
        ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
        if ext in {"png", "jpg", "jpeg", "webp", "gif", "bmp"}:
            mime_type = f"image/{'jpeg' if ext == 'jpg' else ext}"

        return Response(
            storage.stream(filepath),
            mimetype=mime_type,
        )
    except (StorageNotFoundError, InvalidStorageKeyError):
        return jsonify({"error": f"File not found: {filepath}"}), 404


@files_bp.route("/delete/<path:filepath>", methods=["DELETE"])
def delete_file(filepath: str):
    """Delete a single file from storage."""
    storage = get_storage()
    if not storage.exists(filepath):
        return jsonify({"error": f"File not found: {filepath}"}), 404
    storage.delete(filepath)
    return jsonify({"success": True, "message": f"Deleted {filepath}"}), 200


@files_bp.route("/delete-batch", methods=["POST"])
def delete_batch():
    """Delete multiple files by storage_paths JSON array."""
    data = request.get_json() or {}
    paths = data.get("storage_paths", [])
    if not isinstance(paths, list) or not paths:
        return jsonify({"error": "storage_paths list is required"}), 400

    storage = get_storage()
    results = {}
    for path in paths:
        if storage.exists(path):
            storage.delete(path)
            results[path] = "deleted"
        else:
            results[path] = "not_found"
    return jsonify({"success": True, "results": results}), 200
