import hashlib
import io
import mimetypes
import os
import uuid
from dataclasses import dataclass
from typing import BinaryIO, Dict, Generator, List, Optional, Tuple, Union

import fsspec
from PIL import Image, UnidentifiedImageError


class FileServiceError(Exception):
    """Base exception for file service errors."""
    pass


class InvalidFileError(FileServiceError):
    """Raised when an uploaded file is invalid or corrupted."""
    pass


class FileNotFoundError(FileServiceError):
    """Raised when a requested file is not found in storage."""
    pass


class UnsupportedFormatError(FileServiceError):
    """Raised when file format is not supported."""
    pass


@dataclass
class StoredFileMetadata:
    storage_path: str
    original_filename: str
    content_type: str
    size_bytes: int
    sha256_hash: str
    is_image: bool = False
    width: Optional[int] = None
    height: Optional[int] = None
    image_format: Optional[str] = None


class FileService:
    """
    File and image management service powered by fsspec.
    
    Supports uploading, downloading, streaming, inspecting, validating,
    and deleting files and images locally or across any fsspec-supported backend (S3, GCS, Memory, etc.).
    """

    DEFAULT_ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"}
    DEFAULT_ALLOWED_IMAGE_MIMES = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/bmp",
        "image/tiff",
        "image/gif",
    }

    def __init__(
        self,
        base_path: str,
        protocol: str = "file",
        storage_options: Optional[Dict] = None,
        allowed_extensions: Optional[set] = None,
    ):
        self.protocol = protocol
        self.base_path = base_path.rstrip("/")
        self.storage_options = storage_options or {}
        self.allowed_extensions = allowed_extensions or self.DEFAULT_ALLOWED_IMAGE_EXTENSIONS

        # Obtain filesystem instance from fsspec
        self.fs = fsspec.filesystem(self.protocol, **self.storage_options)
        
        # Ensure base directory exists if supported by the filesystem
        if hasattr(self.fs, "makedirs"):
            try:
                self.fs.makedirs(self.base_path, exist_ok=True)
            except Exception:
                pass

    def get_full_path(self, relative_path: str) -> str:
        """Resolve full URI or filesystem path for a relative storage path."""
        rel = relative_path.lstrip("/")
        return f"{self.base_path}/{rel}"

    def exists(self, relative_path: str) -> bool:
        """Check if file exists at the given relative path."""
        full_path = self.get_full_path(relative_path)
        return self.fs.exists(full_path)

    def validate_image_stream(self, stream: BinaryIO) -> Tuple[int, int, str]:
        """
        Validate image content using Pillow.
        Returns (width, height, format_name).
        Raises InvalidFileError or UnsupportedFormatError if invalid.
        """
        initial_pos = stream.tell() if stream.seekable() else 0
        try:
            with Image.open(stream) as img:
                img.verify()
                fmt = (img.format or "").upper()
                width, height = img.size

            # Verify closes or invalidates the image pointer in some PIL versions; re-open to confirm readability
            if stream.seekable():
                stream.seek(initial_pos)
                with Image.open(stream) as img:
                    img.load()
            return width, height, fmt
        except (UnidentifiedImageError, OSError, SyntaxError) as e:
            raise InvalidFileError(f"File is not a valid or readable image: {e}") from e
        finally:
            if stream.seekable():
                stream.seek(initial_pos)

    def save_file(
        self,
        file_data: Union[BinaryIO, bytes],
        filename: str,
        subfolder: str = "uploads",
        validate_image: bool = True,
    ) -> StoredFileMetadata:
        """
        Save a file stream or bytes into storage via fsspec.
        
        Generates a collision-free UUID filename preserving original extension.
        Calculates SHA-256 hash and file size.
        If validate_image is True, verifies that the file is an authentic, readable image.
        """
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if validate_image and self.allowed_extensions and ext not in self.allowed_extensions:
            raise UnsupportedFormatError(
                f"File extension '.{ext}' is not permitted. Allowed: {sorted(list(self.allowed_extensions))}"
            )

        if isinstance(file_data, bytes):
            stream = io.BytesIO(file_data)
        else:
            stream = file_data

        if not stream.seekable():
            # Read fully into memory buffer if stream is not seekable
            stream = io.BytesIO(stream.read())

        stream.seek(0)

        # Image validation & dimensions
        is_image = False
        width, height, image_fmt = None, None, None
        if validate_image:
            width, height, image_fmt = self.validate_image_stream(stream)
            is_image = True

        # Compute hash and size
        stream.seek(0)
        hasher = hashlib.sha256()
        size_bytes = 0
        while chunk := stream.read(64 * 1024):
            hasher.update(chunk)
            size_bytes += len(chunk)
        sha256_hash = hasher.hexdigest()
        stream.seek(0)

        # Build unique relative storage path
        unique_name = f"{uuid.uuid4().hex}"
        if ext:
            unique_name = f"{unique_name}.{ext}"
        
        folder = subfolder.strip("/")
        relative_path = f"{folder}/{unique_name}" if folder else unique_name
        full_path = self.get_full_path(relative_path)

        # Ensure parent directory exists
        parent_dir = full_path.rsplit("/", 1)[0]
        if hasattr(self.fs, "makedirs"):
            self.fs.makedirs(parent_dir, exist_ok=True)

        # Write to storage via fsspec
        with self.fs.open(full_path, "wb") as f_out:
            while chunk := stream.read(64 * 1024):
                f_out.write(chunk)

        # Guess mime type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream" if not is_image else f"image/{(image_fmt or 'jpeg').lower()}"

        return StoredFileMetadata(
            storage_path=relative_path,
            original_filename=filename,
            content_type=mime_type,
            size_bytes=size_bytes,
            sha256_hash=sha256_hash,
            is_image=is_image,
            width=width,
            height=height,
            image_format=image_fmt,
        )

    def open_file(self, relative_path: str, mode: str = "rb"):
        """
        Open a file handle using fsspec.
        Returns a file-like object.
        """
        full_path = self.get_full_path(relative_path)
        if not self.fs.exists(full_path):
            raise FileNotFoundError(f"File not found in storage: {relative_path}")
        return self.fs.open(full_path, mode=mode)

    def read_bytes(self, relative_path: str) -> bytes:
        """Read and return all bytes of a stored file."""
        with self.open_file(relative_path, "rb") as f:
            return f.read()

    def stream_file(
        self, relative_path: str, chunk_size: int = 64 * 1024
    ) -> Generator[bytes, None, None]:
        """Stream chunks of a file for efficient streaming HTTP downloads."""
        with self.open_file(relative_path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    def delete_file(self, relative_path: str) -> bool:
        """Delete a file from storage. Returns True if deleted, False if not found."""
        full_path = self.get_full_path(relative_path)
        if self.fs.exists(full_path):
            self.fs.rm(full_path)
            return True
        return False

    def delete_batch(self, relative_paths: List[str]) -> Dict[str, bool]:
        """Delete multiple files from storage."""
        results = {}
        for path in relative_paths:
            results[path] = self.delete_file(path)
        return results

    def get_file_info(self, relative_path: str) -> Dict:
        """Return filesystem details (size, modified time, etc.) via fsspec."""
        full_path = self.get_full_path(relative_path)
        if not self.fs.exists(full_path):
            raise FileNotFoundError(f"File not found: {relative_path}")
        info = self.fs.info(full_path)
        return {
            "size": info.get("size", 0),
            "created": info.get("created"),
            "modified": info.get("mtime"),
            "name": info.get("name"),
            "storage_path": relative_path,
        }
