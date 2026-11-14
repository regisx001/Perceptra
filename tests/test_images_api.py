import io
from PIL import Image as PILImage
from tests.test_categories import get_auth_token


def create_sample_png(size=(32, 32), color="blue") -> bytes:
    buf = io.BytesIO()
    img = PILImage.new("RGB", size, color=color)
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_upload_image_success_and_category(client):
    token, user_id = get_auth_token(client, "img_uploader@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    cat_res = client.post("/api/v1/categories", json={"name": "Vacation"}, headers=headers)
    assert cat_res.status_code == 201
    cat_id = cat_res.get_json()["category"]["id"]

    # Upload image with category
    img_data = create_sample_png()
    data = {
        "file": (io.BytesIO(img_data), "vacation.png"),
        "category_id": cat_id,
    }
    upload_res = client.post("/api/v1/images", data=data, content_type="multipart/form-data", headers=headers)
    assert upload_res.status_code == 201
    img_obj = upload_res.get_json()["image"]
    assert img_obj["filename"] == "vacation.png"
    assert img_obj["category_id"] == cat_id
    assert img_obj["processing_status"] == "pending"
    assert img_obj["width"] == 32
    assert img_obj["height"] == 32
    assert img_obj["storage_key"].startswith(f"users/{user_id}/")

    image_id = img_obj["id"]

    # Fetch single image metadata
    get_res = client.get(f"/api/v1/images/{image_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.get_json()["image"]["id"] == image_id

    # Fetch file content
    file_res = client.get(f"/api/v1/images/{image_id}/file", headers=headers)
    assert file_res.status_code == 200
    assert file_res.data == img_data

    # Fetch file content using query parameter token
    file_query_res = client.get(f"/api/v1/images/{image_id}/file?token={token}")
    assert file_query_res.status_code == 200
    assert file_query_res.data == img_data


def test_upload_invalid_category_fails(client):
    token, _ = get_auth_token(client, "bad_cat_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    img_data = create_sample_png()
    data = {
        "file": (io.BytesIO(img_data), "vacation.png"),
        "category_id": "00000000-0000-0000-0000-000000000000",
    }
    res = client.post("/api/v1/images", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 404
    assert "category does not exist" in res.get_json()["error"]


def test_upload_corrupted_file_fails(client):
    token, _ = get_auth_token(client, "corrupt_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "file": (io.BytesIO(b"not an image at all"), "bad.png"),
    }
    res = client.post("/api/v1/images", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 400
    assert "Invalid or corrupted image" in res.get_json()["error"]


def test_list_images_and_filters(client):
    token, _ = get_auth_token(client, "gallery_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Upload uncategorized image
    img_data1 = create_sample_png(color="red")
    client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(img_data1), "uncat.png")},
        content_type="multipart/form-data",
        headers=headers,
    )

    # Create category and upload categorized image
    c_res = client.post("/api/v1/categories", json={"name": "Nature"}, headers=headers)
    cat_id = c_res.get_json()["category"]["id"]

    img_data2 = create_sample_png(color="green")
    client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(img_data2), "cat.png"), "category_id": cat_id},
        content_type="multipart/form-data",
        headers=headers,
    )

    # List all
    list_all = client.get("/api/v1/images", headers=headers)
    assert list_all.status_code == 200
    assert len(list_all.get_json()["images"]) == 2

    # List uncategorized only
    list_uncat = client.get("/api/v1/images?uncategorized=true", headers=headers)
    assert list_uncat.status_code == 200
    assert len(list_uncat.get_json()["images"]) == 1
    assert list_uncat.get_json()["images"][0]["filename"] == "uncat.png"

    # List by category
    list_cat = client.get(f"/api/v1/images?category_id={cat_id}", headers=headers)
    assert list_cat.status_code == 200
    assert len(list_cat.get_json()["images"]) == 1
    assert list_cat.get_json()["images"][0]["filename"] == "cat.png"


def test_image_category_assignment_and_bulk_operations(client):
    token, _ = get_auth_token(client, "bulk_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    c1 = client.post("/api/v1/categories", json={"name": "Folder1"}, headers=headers).get_json()["category"]["id"]

    i1 = client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(create_sample_png()), "i1.png")},
        content_type="multipart/form-data",
        headers=headers,
    ).get_json()["image"]["id"]

    i2 = client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(create_sample_png()), "i2.png")},
        content_type="multipart/form-data",
        headers=headers,
    ).get_json()["image"]["id"]

    # Single PATCH category
    patch_res = client.patch(f"/api/v1/images/{i1}", json={"category_id": c1}, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.get_json()["image"]["category_id"] == c1

    # Bulk assign
    bulk_assign = client.post(
        "/api/v1/images/bulk-assign",
        json={"image_ids": [i1, i2], "category_id": None},
        headers=headers,
    )
    assert bulk_assign.status_code == 200
    assert bulk_assign.get_json()["updated_count"] == 2

    # Bulk delete
    bulk_del = client.post(
        "/api/v1/images/bulk-delete",
        json={"image_ids": [i1, i2]},
        headers=headers,
    )
    assert bulk_del.status_code == 200
    assert bulk_del.get_json()["deleted_count"] == 2

    # Confirm deleted
    assert client.get(f"/api/v1/images/{i1}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/images/{i2}", headers=headers).status_code == 404
