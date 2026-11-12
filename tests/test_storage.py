import io
import pytest
from pathlib import Path
from src.services.storage import (
    LocalStorage,
    InvalidStorageKeyError,
    StorageNotFoundError,
    StorageWriteError,
)


@pytest.fixture
def temp_storage(tmp_path):
    return LocalStorage(root_dir=tmp_path / "images")


def test_generate_key(temp_storage):
    key = temp_storage.generate_key("users/42", ".jpg")
    assert key.startswith("users/42/")
    assert key.endswith(".jpg")
    filename = key.split("/")[-1]
    uuid_part = filename[:-4]
    assert len(uuid_part) == 36


def test_save_and_exists_and_open(temp_storage):
    content = b"fake-binary-image-data-test"
    stream = io.BytesIO(content)

    key = temp_storage.save(stream, directory="users/100", extension=".png")
    assert temp_storage.exists(key) is True

    # Test open
    with temp_storage.open(key) as f:
        read_data = f.read()
    assert read_data == content

    # Test get_path
    abs_path = temp_storage.get_path(key)
    assert isinstance(abs_path, Path)
    assert abs_path.is_file()
    assert abs_path.read_bytes() == content


def test_get_path_missing_file_raises(temp_storage):
    with pytest.raises(StorageNotFoundError):
        temp_storage.get_path("users/99/missing.jpg")


def test_path_traversal_prevention(temp_storage):
    with pytest.raises(InvalidStorageKeyError):
        temp_storage.get_path("../../etc/passwd")

    with pytest.raises(InvalidStorageKeyError):
        temp_storage.open("../secret.txt")

    with pytest.raises(InvalidStorageKeyError):
        temp_storage.delete("../../some_file")


def test_delete_idempotent_and_cleans_empty_dir(temp_storage):
    content = b"temp-file"
    key = temp_storage.save(io.BytesIO(content), directory="temp/subfolder", extension=".jpg")
    path = temp_storage.get_path(key)
    parent_dir = path.parent

    assert temp_storage.exists(key) is True
    assert parent_dir.exists() is True

    # First delete
    temp_storage.delete(key)
    assert temp_storage.exists(key) is False
    assert not path.exists()
    # Empty subdirectories should be cleaned up
    assert not parent_dir.exists()

    # Second delete should be idempotent without error
    temp_storage.delete(key)
