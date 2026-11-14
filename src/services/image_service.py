import hashlib
import io
from dataclasses import dataclass
from typing import BinaryIO, Optional

from PIL import Image as PILImage, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import db
from src.models.category import Category
from src.models.image import Image
from src.services.storage import StorageBackend, StorageError


class ImageServiceError(Exception):
    """Base domain exception for image operations."""
    status_code = 400


class InvalidImageError(ImageServiceError):
    """Raised when uploaded file is empty, unsupported, or corrupted."""
    status_code = 400


class ResourceNotFoundError(ImageServiceError):
    """Raised when an image or category does not exist or is not owned by the user."""
    status_code = 404


# Map Pillow format identifiers to canonical (extension, mime_type)
SUPPORTED_IMAGE_FORMATS: dict[str, tuple[str, str]] = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
    "BMP": (".bmp", "image/bmp"),
}


@dataclass(frozen=True)
class ValidatedImageMetadata:
    width: int
    height: int
    extension: str
    mime_type: str
    file_size: int
    checksum: str


class ImageService:
    def __init__(self, storage: StorageBackend, max_file_size: Optional[int] = 32 * 1024 * 1024):
        self.storage = storage
        self.max_file_size = max_file_size or (32 * 1024 * 1024)

    def _validate_image_bytes(self, raw_bytes: bytes) -> ValidatedImageMetadata:
        if not raw_bytes:
            raise InvalidImageError("Uploaded file is empty.")

        file_size = len(raw_bytes)
        if file_size > self.max_file_size:
            raise InvalidImageError(
                f"File size ({file_size} bytes) exceeds maximum limit ({self.max_file_size} bytes)."
            )

        try:
            with PILImage.open(io.BytesIO(raw_bytes)) as img:
                img.verify()

            # Re-open after verify() to safely inspect dimensions and format
            with PILImage.open(io.BytesIO(raw_bytes)) as img:
                width, height = img.size
                detected_format = (img.format or "").upper()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("Invalid or corrupted image file.") from exc

        if detected_format not in SUPPORTED_IMAGE_FORMATS:
            allowed = ", ".join(SUPPORTED_IMAGE_FORMATS.keys())
            raise InvalidImageError(
                f"Unsupported image format '{detected_format or 'UNKNOWN'}'. Supported: {allowed}."
            )

        if width <= 0 or height <= 0:
            raise InvalidImageError("Image dimensions must be positive.")

        extension, mime_type = SUPPORTED_IMAGE_FORMATS[detected_format]
        checksum = hashlib.sha256(raw_bytes).hexdigest()

        return ValidatedImageMetadata(
            width=width,
            height=height,
            extension=extension,
            mime_type=mime_type,
            file_size=file_size,
            checksum=checksum,
        )

    def _verify_category_ownership(self, user_id: str, category_id: Optional[str]) -> Optional[str]:
        if not category_id:
            return None

        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            raise ResourceNotFoundError("Target category does not exist.")
        return category.id

    def upload_image(
        self,
        user_id: str,
        raw_bytes: bytes,
        original_filename: str,
        category_id: Optional[str] = None,
    ) -> Image:
        # 1. Verify category ownership before writing anything to disk
        verified_category_id = self._verify_category_ownership(user_id, category_id)

        # 2. Validate binary content and derive true format/dimensions
        meta = self._validate_image_bytes(raw_bytes)

        # 3. Store physically under users/{user_id}/{uuid}.{ext}
        user_directory = f"users/{user_id}"
        try:
            storage_key = self.storage.save(
                file=io.BytesIO(raw_bytes),
                directory=user_directory,
                extension=meta.extension,
            )
        except StorageError as exc:
            raise ImageServiceError(f"Failed to persist image file: {exc}") from exc

        # 4. Persist metadata in SQLite with compensating disk rollback on failure
        safe_filename = (original_filename or f"upload{meta.extension}")[:255]
        image_record = Image(
            owner_id=user_id,
            category_id=verified_category_id,
            filename=safe_filename,
            storage_key=storage_key,
            source_type="upload",
            mime_type=meta.mime_type,
            file_size=meta.file_size,
            width=meta.width,
            height=meta.height,
            checksum=meta.checksum,
            processing_status="pending",
        )

        try:
            db.session.add(image_record)
            db.session.commit()
            return image_record
        except SQLAlchemyError as exc:
            db.session.rollback()
            self.storage.delete(storage_key)
            raise ImageServiceError("Database error while saving image metadata.") from exc

    def list_user_images(
        self,
        user_id: str,
        category_id: Optional[str] = None,
        uncategorized_only: bool = False,
        page: int = 1,
        per_page: int = 24,
    ):
        query = Image.query.filter_by(owner_id=user_id)

        if uncategorized_only:
            query = query.filter(Image.category_id.is_(None))
        elif category_id:
            self._verify_category_ownership(user_id, category_id)
            query = query.filter_by(category_id=category_id)

        return query.order_by(Image.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def get_user_image(self, user_id: str, image_id: str) -> Image:
        image = Image.query.filter_by(id=image_id, owner_id=user_id).first()
        if not image:
            raise ResourceNotFoundError("Image not found.")
        return image

    def open_image_stream(self, user_id: str, image_id: str) -> tuple[Image, BinaryIO]:
        image = self.get_user_image(user_id, image_id)
        try:
            stream = self.storage.open(image.storage_key)
            return image, stream
        except StorageError as exc:
            raise ResourceNotFoundError("Physical image file missing from storage.") from exc

    def assign_category(
        self, user_id: str, image_ids: list[str], category_id: Optional[str]
    ) -> int:
        verified_category_id = self._verify_category_ownership(user_id, category_id)
        images = Image.query.filter(
            Image.owner_id == user_id,
            Image.id.in_(image_ids),
        ).all()

        for img in images:
            img.category_id = verified_category_id

        db.session.commit()
        return len(images)

    def delete_image(self, user_id: str, image_id: str) -> None:
        image = self.get_user_image(user_id, image_id)
        storage_key = image.storage_key

        db.session.delete(image)
        db.session.commit()
        self.storage.delete(storage_key)

    def bulk_delete_images(self, user_id: str, image_ids: list[str]) -> int:
        images = Image.query.filter(
            Image.owner_id == user_id,
            Image.id.in_(image_ids),
        ).all()

        storage_keys = [img.storage_key for img in images]
        deleted_count = len(images)

        for img in images:
            db.session.delete(img)
        db.session.commit()

        for key in storage_keys:
            self.storage.delete(key)

        return deleted_count
