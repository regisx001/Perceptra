import io
import pytest
from PIL import Image

from src.services.file_service import (
    FileService,
    FileNotFoundError,
    InvalidFileError,
    UnsupportedFormatError,
)


def create_sample_image(format="PNG", size=(64, 64), color="red") -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_file_service_save_and_read(tmp_path):
    storage_dir = str(tmp_path / "storage")
    service = FileService(base_path=storage_dir)

    img_bytes = create_sample_image("PNG")
    meta = service.save_file(img_bytes, filename="sample.png", subfolder="test")

    assert meta.storage_path.startswith("test/")
    assert meta.storage_path.endswith(".png")
    assert meta.is_image is True
    assert meta.width == 64
    assert meta.height == 64
    assert meta.image_format == "PNG"
    assert meta.size_bytes == len(img_bytes)

    # Read back
    read_data = service.read_bytes(meta.storage_path)
    assert read_data == img_bytes

    # Info
    info = service.get_file_info(meta.storage_path)
    assert info["size"] == len(img_bytes)

    # Delete
    assert service.delete_file(meta.storage_path) is True
    assert service.exists(meta.storage_path) is False


def test_file_service_invalid_image_fails(tmp_path):
    storage_dir = str(tmp_path / "storage")
    service = FileService(base_path=storage_dir)

    corrupted_data = b"NOT_A_REAL_IMAGE_DATA_12345"
    with pytest.raises(InvalidFileError):
        service.save_file(corrupted_data, filename="fake.png", validate_image=True)


def test_file_service_unsupported_extension(tmp_path):
    storage_dir = str(tmp_path / "storage")
    service = FileService(base_path=storage_dir)

    with pytest.raises(UnsupportedFormatError):
        service.save_file(b"some content", filename="script.exe", validate_image=True)


def test_file_service_non_image_upload(tmp_path):
    storage_dir = str(tmp_path / "storage")
    service = FileService(base_path=storage_dir)

    content = b"Plain text arbitrary file content"
    meta = service.save_file(content, filename="notes.txt", validate_image=False)
    assert meta.is_image is False
    assert service.read_bytes(meta.storage_path) == content


def test_file_service_batch_delete(tmp_path):
    storage_dir = str(tmp_path / "storage")
    service = FileService(base_path=storage_dir)

    img_bytes = create_sample_image("JPEG")
    meta1 = service.save_file(img_bytes, "a.jpg")
    meta2 = service.save_file(img_bytes, "b.jpg")

    results = service.delete_batch([meta1.storage_path, meta2.storage_path, "nonexistent.jpg"])
    assert results[meta1.storage_path] is True
    assert results[meta2.storage_path] is True
    assert results["nonexistent.jpg"] is False
