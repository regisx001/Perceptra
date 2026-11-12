import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import BinaryIO, Generator, List, Optional, Protocol, Union

import fsspec


class StorageError(Exception):
    """Base storage exception."""
    pass


class StorageNotFoundError(StorageError):
    """Requested file does not exist."""
    pass


class StorageWriteError(StorageError):
    """File cannot be saved."""
    pass


class StorageDeleteError(StorageError):
    """File cannot be deleted."""
    pass


class InvalidStorageKeyError(StorageError):
    """Key is invalid or attempts path traversal."""
    pass


class StorageBackend(Protocol):
    def save(
        self,
        file: BinaryIO,
        directory: str,
        extension: str,
    ) -> str:
        ...

    def open(
        self,
        key: str,
        mode: str = "rb",
    ) -> BinaryIO:
        ...

    def get_path(
        self,
        key: str,
    ) -> Path:
        ...

    def exists(
        self,
        key: str,
    ) -> bool:
        ...

    def delete(
        self,
        key: str,
    ) -> None:
        ...


class Storage:
    """
    Storage service powered by fsspec.
    
    Exposes a clean, independent API:
      - generate_key(directory, extension)
      - save(file, directory, extension)
      - open(key, mode="rb")
      - get_path(key)
      - exists(key)
      - delete(key)
    
    Supports local filesystem and remote filesystems via fsspec URL protocols.
    Prevents path traversal and validates containment against root_dir.
    """

    def __init__(
        self,
        root_dir: Union[str, Path] = "storage",
        protocol: str = "file",
        storage_options: Optional[dict] = None,
    ):
        self.protocol = protocol
        self.storage_options = storage_options or {}
        self.root_dir = Path(root_dir).resolve() if protocol == "file" else Path(str(root_dir))
        self.fs, self.fs_root = fsspec.core.url_to_fs(
            f"{self.protocol}://{self.root_dir.as_posix()}" if self.protocol != "file" else str(self.root_dir),
            **self.storage_options,
        )
        self.fs.makedirs(self.fs_root, exist_ok=True)

    def _validate_and_resolve_key(self, key: str, must_exist: bool = False) -> str:
        """
        Validate key format, protect against directory traversal, and return absolute fs path string.
        """
        if not key or not isinstance(key, str):
            raise InvalidStorageKeyError("Storage key must be a non-empty string.")

        clean_key = key.strip()
        if clean_key.startswith("/") or clean_key.startswith("\\"):
            clean_key = clean_key.lstrip("/\\")

        if not clean_key:
            raise InvalidStorageKeyError("Storage key cannot be empty or root.")

        # Path traversal checks
        if ".." in clean_key.split("/") or ".." in clean_key.split("\\"):
            raise InvalidStorageKeyError(f"Access denied: key '{key}' attempts directory traversal.")

        # Resolve path
        resolved_path = (self.root_dir / clean_key).resolve()

        if self.protocol == "file":
            try:
                resolved_path.relative_to(self.root_dir)
            except ValueError:
                raise InvalidStorageKeyError(f"Access denied: key '{key}' resolves outside storage root.")

            if resolved_path == self.root_dir:
                raise InvalidStorageKeyError("Storage key cannot point to the storage root.")

        fs_path = self.fs.sep.join([self.fs_root.rstrip(self.fs.sep), clean_key.replace("\\", "/")])

        if must_exist and not self.fs.isfile(fs_path):
            raise StorageNotFoundError(f"File not found for key: '{key}'")

        return fs_path

    def generate_key(self, directory: str, extension: str) -> str:
        """
        Generate a unique relative storage key using UUID4.
        """
        clean_dir = directory.strip().strip("/\\") if directory else ""
        ext = extension.strip()
        if ext and not ext.startswith("."):
            ext = f".{ext}"

        unique_filename = f"{uuid.uuid4()}{ext}"
        if clean_dir:
            return f"{clean_dir}/{unique_filename}"
        return unique_filename

    def save(
        self,
        file: Union[BinaryIO, bytes],
        directory: str,
        extension: str,
    ) -> str:
        """
        Saves an uploaded file stream or bytes using atomic write via fsspec.
        """
        key = self.generate_key(directory, extension)
        fs_target_path = self._validate_and_resolve_key(key, must_exist=False)

        parent_dir = self.fs._parent(fs_target_path)
        try:
            self.fs.makedirs(parent_dir, exist_ok=True)
        except Exception as exc:
            raise StorageWriteError(f"Failed to create directory '{parent_dir}': {exc}") from exc

        # Atomic write
        temp_path = f"{parent_dir}/.tmp_{uuid.uuid4()}{extension if extension.startswith('.') else '.' + extension}"
        try:
            with self.fs.open(temp_path, "wb") as f_out:
                if isinstance(file, (bytes, bytearray)):
                    f_out.write(file)
                else:
                    if hasattr(file, "seek"):
                        file.seek(0)
                    shutil.copyfileobj(file, f_out)

            # Move/rename temp file to final destination atomically
            self.fs.mv(temp_path, fs_target_path)
            return key
        except Exception as exc:
            if self.fs.exists(temp_path):
                try:
                    self.fs.rm(temp_path)
                except Exception:
                    pass
            raise StorageWriteError(f"Failed to save file for key '{key}': {exc}") from exc

    def open(
        self,
        key: str,
        mode: str = "rb",
    ) -> BinaryIO:
        """
        Opens a stored file for reading.
        """
        fs_path = self._validate_and_resolve_key(key, must_exist=True)
        try:
            return self.fs.open(fs_path, mode)
        except Exception as exc:
            raise StorageError(f"Failed to open file for key '{key}': {exc}") from exc

    def read_bytes(self, key: str) -> bytes:
        """Helper to read complete file bytes."""
        with self.open(key, "rb") as f:
            return f.read()

    def stream(self, key: str, chunk_size: int = 65536) -> Generator[bytes, None, None]:
        """Generator yielding file in chunks."""
        with self.open(key, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    def get_path(
        self,
        key: str,
    ) -> Path:
        """
        Returns the absolute filesystem path after validating existence and containment.
        """
        fs_path = self._validate_and_resolve_key(key, must_exist=True)
        return Path(fs_path).resolve()

    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Checks whether a stored file exists.
        """
        try:
            fs_path = self._validate_and_resolve_key(key, must_exist=False)
            return self.fs.isfile(fs_path)
        except InvalidStorageKeyError:
            return False

    def delete(
        self,
        key: str,
    ) -> None:
        """
        Deletes a stored file idempotently.
        Optionally removes empty parent directories up to storage root.
        """
        try:
            fs_path = self._validate_and_resolve_key(key, must_exist=False)
        except InvalidStorageKeyError:
            raise

        if not self.fs.exists(fs_path):
            return

        if not self.fs.isfile(fs_path):
            raise StorageDeleteError(f"Cannot delete non-file path for key '{key}'.")

        try:
            self.fs.rm(fs_path)
        except Exception as exc:
            raise StorageDeleteError(f"Failed to delete file for key '{key}': {exc}") from exc

        # Clean up empty parent directories up to storage root
        current_dir = self.fs._parent(fs_path)
        while current_dir and current_dir != self.fs_root:
            try:
                # Check if directory is empty
                contents = self.fs.ls(current_dir, detail=False)
                if not contents:
                    self.fs.rmdir(current_dir)
                    current_dir = self.fs._parent(current_dir)
                else:
                    break
            except Exception:
                break


# Alias LocalStorage to Storage for backwards compatibility
LocalStorage = Storage
