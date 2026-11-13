import pytest
from src.models.user import User
from src.models.category import Category
from src.models.image import Image


def get_auth_token(client, email="catuser@example.com", password="password123"):
    res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    if res.status_code == 201:
        return res.get_json()["access_token"], res.get_json()["user"]["id"]
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return res.get_json()["access_token"], res.get_json()["user"]["id"]


def test_create_category_success_and_validation(client):
    token, user_id = get_auth_token(client, "alice@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Missing name
    res = client.post("/api/v1/categories", json={}, headers=headers)
    assert res.status_code == 400

    # Empty name
    res = client.post("/api/v1/categories", json={"name": "   "}, headers=headers)
    assert res.status_code == 400

    # Overly long name (>100 chars)
    res = client.post("/api/v1/categories", json={"name": "a" * 101}, headers=headers)
    assert res.status_code == 400

    # Valid root category
    res = client.post("/api/v1/categories", json={"name": "Nature"}, headers=headers)
    assert res.status_code == 201
    nature_id = res.get_json()["category"]["id"]
    assert res.get_json()["category"]["name"] == "Nature"
    assert res.get_json()["category"]["parent_id"] is None

    # Subcategory under Nature
    res = client.post("/api/v1/categories", json={"name": "Landscapes", "parent_id": nature_id}, headers=headers)
    assert res.status_code == 201
    landscapes_id = res.get_json()["category"]["id"]
    assert res.get_json()["category"]["parent_id"] == nature_id

    # Conflict on duplicate sibling under Nature
    res = client.post("/api/v1/categories", json={"name": "Landscapes", "parent_id": nature_id}, headers=headers)
    assert res.status_code == 409

    # Non-existent parent_id
    res = client.post("/api/v1/categories", json={"name": "Mountains", "parent_id": "00000000-0000-0000-0000-000000000000"}, headers=headers)
    assert res.status_code == 404


def test_cross_user_isolation(client):
    token1, _ = get_auth_token(client, "user1@test.com")
    token2, _ = get_auth_token(client, "user2@test.com")

    # User 1 creates category
    res = client.post("/api/v1/categories", json={"name": "User1 Folder"}, headers={"Authorization": f"Bearer {token1}"})
    cat1_id = res.get_json()["category"]["id"]

    # User 2 tries to access User 1's category -> must return 404
    res = client.get(f"/api/v1/categories/{cat1_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 404

    # User 2 tries to create subcategory with User 1's parent_id -> 404
    res = client.post("/api/v1/categories", json={"name": "Sub", "parent_id": cat1_id}, headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 404

    # User 2 tries to update User 1's category -> 404
    res = client.patch(f"/api/v1/categories/{cat1_id}", json={"name": "Hacked"}, headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 404

    # User 2 tries to delete User 1's category -> 404
    res = client.delete(f"/api/v1/categories/{cat1_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 404


def test_list_categories_flat_and_tree(client):
    token, _ = get_auth_token(client, "bob@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create root
    r1 = client.post("/api/v1/categories", json={"name": "Root 1"}, headers=headers)
    root1_id = r1.get_json()["category"]["id"]

    # Create subcategory
    r2 = client.post("/api/v1/categories", json={"name": "Child 1", "parent_id": root1_id}, headers=headers)
    child1_id = r2.get_json()["category"]["id"]

    # Flat list
    res_flat = client.get("/api/v1/categories", headers=headers)
    assert res_flat.status_code == 200
    flat_cats = res_flat.get_json()["categories"]
    assert len(flat_cats) == 2

    # Tree list
    res_tree = client.get("/api/v1/categories?tree=true", headers=headers)
    assert res_tree.status_code == 200
    tree_cats = res_tree.get_json()["categories"]
    assert len(tree_cats) == 1
    assert tree_cats[0]["id"] == root1_id
    assert len(tree_cats[0]["children"]) == 1
    assert tree_cats[0]["children"][0]["id"] == child1_id


def test_update_and_move_category_cycle_prevention(client):
    token, _ = get_auth_token(client, "charlie@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    c_a = client.post("/api/v1/categories", json={"name": "A"}, headers=headers).get_json()["category"]["id"]
    c_b = client.post("/api/v1/categories", json={"name": "B", "parent_id": c_a}, headers=headers).get_json()["category"]["id"]
    c_c = client.post("/api/v1/categories", json={"name": "C", "parent_id": c_b}, headers=headers).get_json()["category"]["id"]

    # Rename
    res = client.patch(f"/api/v1/categories/{c_a}", json={"name": "A_renamed"}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()["category"]["name"] == "A_renamed"

    # Self-parenting rejected
    res = client.patch(f"/api/v1/categories/{c_a}", json={"parent_id": c_a}, headers=headers)
    assert res.status_code == 400

    # Moving A under its descendant B (or C) rejected to prevent cycle
    res = client.patch(f"/api/v1/categories/{c_a}", json={"parent_id": c_b}, headers=headers)
    assert res.status_code == 400

    res = client.patch(f"/api/v1/categories/{c_a}", json={"parent_id": c_c}, headers=headers)
    assert res.status_code == 400

    # Move C back to root
    res = client.patch(f"/api/v1/categories/{c_c}", json={"parent_id": None}, headers=headers)
    assert res.status_code == 200
    assert res.get_json()["category"]["parent_id"] is None


def test_delete_category_promotes_children_and_nulls_images(client, db_session):
    token, user_id = get_auth_token(client, "dan@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    root = client.post("/api/v1/categories", json={"name": "ParentFolder"}, headers=headers).get_json()["category"]["id"]
    child = client.post("/api/v1/categories", json={"name": "ChildFolder", "parent_id": root}, headers=headers).get_json()["category"]["id"]

    # Assign an image to root
    img = Image(
        owner_id=user_id,
        category_id=root,
        filename="test.jpg",
        storage_key="test/sample_img_123.jpg",
        source_type="upload",
        mime_type="image/jpeg",
        file_size=1000,
        width=100,
        height=100,
        checksum="abcd1234567890",
    )
    db_session.add(img)
    db_session.commit()

    # Delete parent folder
    res = client.delete(f"/api/v1/categories/{root}", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["message"] == "Category deleted"

    # Parent category is gone
    assert client.get(f"/api/v1/categories/{root}", headers=headers).status_code == 404

    # Child category was promoted to root (parent_id is None)
    child_res = client.get(f"/api/v1/categories/{child}", headers=headers)
    assert child_res.status_code == 200
    assert child_res.get_json()["category"]["parent_id"] is None

    # Image was not deleted, but its category_id is set to None
    db_session.refresh(img)
    assert img.category_id is None
