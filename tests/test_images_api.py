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


def test_image_transformation_and_derivatives_routes(client):
    token, user_id = get_auth_token(client, "transform_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Upload parent image
    raw_png = create_sample_png(size=(100, 80))
    upload_res = client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(raw_png), "parent.png")},
        content_type="multipart/form-data",
        headers=headers,
    )
    assert upload_res.status_code == 201
    parent_id = upload_res.get_json()["image"]["id"]

    # 1. Transform: crop
    crop_payload = {
        "operation": "crop",
        "params": {"x": 10, "y": 10, "width": 40, "height": 30},
        "filename": "cropped.png",
    }
    crop_res = client.post(f"/api/v1/images/{parent_id}/transform", json=crop_payload, headers=headers)
    assert crop_res.status_code == 201
    crop_data = crop_res.get_json()["image"]
    assert crop_data["parent_image_id"] == parent_id
    assert crop_data["source_type"] == "derived"
    assert crop_data["width"] == 40
    assert crop_data["height"] == 30
    assert crop_data["filename"] == "cropped.png"
    assert crop_data["storage_key"].startswith(f"derived/{user_id}/")
    assert crop_data["transformation_params"]["operation"] == "crop"

    crop_id = crop_data["id"]

    # 2. Chain transformation: shear the crop
    shear_payload = {
        "operation": "shear",
        "params": {"shear_x": 0.2, "shear_y": 0.0, "expand": True},
    }
    shear_res = client.post(f"/api/v1/images/{crop_id}/transform", json=shear_payload, headers=headers)
    assert shear_res.status_code == 201
    shear_data = shear_res.get_json()["image"]
    assert shear_data["parent_image_id"] == crop_id

    # 3. List derivatives of parent
    deriv_res = client.get(f"/api/v1/images/{parent_id}/derivatives", headers=headers)
    assert deriv_res.status_code == 200
    derivatives = deriv_res.get_json()["derivatives"]
    assert len(derivatives) == 1
    assert derivatives[0]["id"] == crop_id

    # 4. Out-of-bounds crop returns 400
    bad_crop = {
        "operation": "crop",
        "params": {"x": 200, "y": 200, "width": 50, "height": 50},
    }
    bad_res = client.post(f"/api/v1/images/{parent_id}/transform", json=bad_crop, headers=headers)
    assert bad_res.status_code == 400
    assert "exceeds image boundaries" in bad_res.get_json()["error"]


def test_transform_validate_route(client):
    token, _ = get_auth_token(client, "val_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    raw_png = create_sample_png(size=(1200, 800))
    upload_res = client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(raw_png), "big.png")},
        content_type="multipart/form-data",
        headers=headers,
    )
    img_id = upload_res.get_json()["image"]["id"]

    # Valid crop calculation
    val_res = client.post(
        f"/api/v1/images/{img_id}/transform-validate",
        json={"operation": "crop", "params": {"x": 100, "y": 100, "width": 600, "height": 400}},
        headers=headers,
    )
    assert val_res.status_code == 200
    body = val_res.get_json()
    assert body["success"] is True
    assert body["new_width"] == 600
    assert body["new_height"] == 400
    assert body["aspect_ratio"] == 1.5

    # Out of bounds crop
    bad_val = client.post(
        f"/api/v1/images/{img_id}/transform-validate",
        json={"operation": "crop", "params": {"x": 1000, "y": 700, "width": 600, "height": 400}},
        headers=headers,
    )
    assert bad_val.status_code == 400


def test_preview_delivery(client):
    token, _ = get_auth_token(client, "prev_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Upload large image (1600x1200)
    raw_png = create_sample_png(size=(1600, 1200))
    upload_res = client.post(
        "/api/v1/images",
        data={"file": (io.BytesIO(raw_png), "large.png")},
        content_type="multipart/form-data",
        headers=headers,
    )
    img_id = upload_res.get_json()["image"]["id"]

    # Request with ?preview=true
    prev_res = client.get(f"/api/v1/images/{img_id}/file?preview=true", headers=headers)
    assert prev_res.status_code == 200
    assert prev_res.mimetype == "image/jpeg"

    # Verify preview dimensions
    with PILImage.open(io.BytesIO(prev_res.data)) as p_img:
        w, h = p_img.size
        assert max(w, h) <= 800
        assert w == 800
        assert h == 600
