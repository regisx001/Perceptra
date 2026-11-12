import io
from PIL import Image


def create_sample_image(format="PNG", size=(64, 64), color="red") -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


def test_api_upload_single_image(client):
    img_data = create_sample_image("PNG")
    data = {
        "file": (io.BytesIO(img_data), "photo.png"),
        "folder": "gallery",
    }
    resp = client.post("/api/v1/files/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["success"] is True
    file_info = body["file"]
    assert file_info["is_image"] is True
    assert file_info["width"] == 64
    assert file_info["height"] == 64
    assert file_info["format"] == "PNG"

    storage_path = file_info["storage_path"]

    # Test Download
    dl_resp = client.get(f"/api/v1/files/download/{storage_path}")
    assert dl_resp.status_code == 200
    assert dl_resp.data == img_data

    # Test Stream
    stream_resp = client.get(f"/api/v1/files/stream/{storage_path}")
    assert stream_resp.status_code == 200
    assert stream_resp.data == img_data

    # Test Delete
    del_resp = client.delete(f"/api/v1/files/delete/{storage_path}")
    assert del_resp.status_code == 200

    # Confirm deleted
    assert client.get(f"/api/v1/files/download/{storage_path}").status_code == 404


def test_api_upload_invalid_file(client):
    data = {
        "file": (io.BytesIO(b"not an image"), "bad.png"),
    }
    resp = client.post("/api/v1/files/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_api_upload_batch_and_delete_batch(client):
    img1 = create_sample_image("PNG", color="blue")
    img2 = create_sample_image("JPEG", color="green")

    data = {
        "files": [
            (io.BytesIO(img1), "img1.png"),
            (io.BytesIO(img2), "img2.jpg"),
        ],
        "folder": "batch_test",
    }
    resp = client.post("/api/v1/files/upload-batch", data=data, content_type="multipart/form-data")
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["uploaded_count"] == 2
    paths = [f["storage_path"] for f in body["files"]]

    # Batch delete
    del_resp = client.post("/api/v1/files/delete-batch", json={"storage_paths": paths})
    assert del_resp.status_code == 200
    results = del_resp.get_json()["results"]
    for path in paths:
        assert results[path] == "deleted"
