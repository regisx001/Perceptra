import io
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    request,
    send_file,
)
from src.services.file_service import (
    FileService,
    FileNotFoundError,
    InvalidFileError,
    UnsupportedFormatError,
)

files_bp = Blueprint("files", __name__, url_prefix="/api/files")


def get_file_service() -> FileService:
    """Helper to instantiate FileService using current app configuration."""
    cfg = current_app.config
    protocol = cfg.get("STORAGE_PROTOCOL", "file")
    base_path = cfg.get("STORAGE_BASE_PATH", "storage")
    allowed_extensions = cfg.get("ALLOWED_EXTENSIONS")
    return FileService(
        base_path=base_path,
        protocol=protocol,
        allowed_extensions=allowed_extensions,
    )


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

    service = get_file_service()
    try:
        meta = service.save_file(
            file_data=uploaded.stream,
            filename=uploaded.filename,
            subfolder=folder,
            validate_image=validate_image,
        )
        return jsonify({
            "success": True,
            "file": {
                "storage_path": meta.storage_path,
                "original_filename": meta.original_filename,
                "content_type": meta.content_type,
                "size_bytes": meta.size_bytes,
                "sha256_hash": meta.sha256_hash,
                "is_image": meta.is_image,
                "width": meta.width,
                "height": meta.height,
                "format": meta.image_format,
            }
        }), 201
    except (InvalidFileError, UnsupportedFormatError) as e:
        return jsonify({"error": str(e)}), 400
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

    service = get_file_service()
    results = []
    errors = []

    for uploaded in uploaded_files:
        if not uploaded.filename:
            continue
        try:
            meta = service.save_file(
                file_data=uploaded.stream,
                filename=uploaded.filename,
                subfolder=folder,
                validate_image=validate_image,
            )
            results.append({
                "storage_path": meta.storage_path,
                "original_filename": meta.original_filename,
                "content_type": meta.content_type,
                "size_bytes": meta.size_bytes,
                "sha256_hash": meta.sha256_hash,
                "is_image": meta.is_image,
                "width": meta.width,
                "height": meta.height,
                "format": meta.image_format,
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
    service = get_file_service()

    try:
        content = service.read_bytes(filepath)
        filename = filepath.rsplit("/", 1)[-1]
        return send_file(
            io.BytesIO(content),
            as_attachment=as_attachment,
            download_name=filename,
        )
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {filepath}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@files_bp.route("/stream/<path:filepath>", methods=["GET"])
def stream_file(filepath: str):
    """
    Stream a file from storage (useful for large files / image serving).
    """
    service = get_file_service()
    try:
        if not service.exists(filepath):
            return jsonify({"error": f"File not found: {filepath}"}), 404

        mime_type = "application/octet-stream"
        ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
        if ext in {"png", "jpg", "jpeg", "webp", "gif", "bmp"}:
            mime_type = f"image/{'jpeg' if ext == 'jpg' else ext}"

        return Response(
            service.stream_file(filepath),
            mimetype=mime_type,
        )
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {filepath}"}), 404


@files_bp.route("/delete/<path:filepath>", methods=["DELETE"])
def delete_file(filepath: str):
    """Delete a single file from storage."""
    service = get_file_service()
    deleted = service.delete_file(filepath)
    if not deleted:
        return jsonify({"error": f"File not found: {filepath}"}), 404
    return jsonify({"success": True, "message": f"Deleted {filepath}"}), 200


@files_bp.route("/delete-batch", methods=["POST"])
def delete_batch():
    """Delete multiple files by storage_paths JSON array."""
    data = request.get_json() or {}
    paths = data.get("storage_paths", [])
    if not isinstance(paths, list) or not paths:
        return jsonify({"error": "storage_paths list is required"}), 400

    service = get_file_service()
    results = service.delete_batch(paths)
    return jsonify({"success": True, "results": results}), 200
