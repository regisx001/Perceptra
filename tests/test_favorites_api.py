import pytest
from src.models.user import User
from src.models.image import Image
from src.models.favorite import FavoriteImage


@pytest.fixture
def auth_client_and_user(app, client):
    with app.app_context():
        user = User(email="fav_tester@example.com")
        user.set_password("SecurePass123!")
        from src.extensions import db
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "fav_tester@example.com", "password": "SecurePass123!"},
    )
    token = res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return client, headers, user_id


def test_favorite_image_flow(app, auth_client_and_user):
    client, headers, user_id = auth_client_and_user

    # Seed an image owned by the user
    with app.app_context():
        from src.extensions import db
        img = Image(
            owner_id=user_id,
            filename="my_fav_cat.jpg",
            storage_key=f"uploads/{user_id}/cat.jpg",
            source_type="upload",
            mime_type="image/jpeg",
            file_size=2048,
            width=200,
            height=200,
            checksum="chkfav1",
        )
        db.session.add(img)
        db.session.commit()
        img_id = img.id

    # 1. Initial check: is_favorite should be False
    res = client.get(f"/api/v1/images/{img_id}", headers=headers)
    assert res.status_code == 200
    assert res.get_json()["image"]["is_favorite"] is False

    # 2. Toggle favorite: mark as favorite
    res_toggle = client.post(f"/api/v1/images/{img_id}/favorite", headers=headers)
    assert res_toggle.status_code == 200
    data = res_toggle.get_json()
    assert data["success"] is True
    assert data["is_favorite"] is True

    # Check detail endpoint reflects favorite
    res_after = client.get(f"/api/v1/images/{img_id}", headers=headers)
    assert res_after.get_json()["image"]["is_favorite"] is True

    # 3. Filter by favorites: list images with favorites=true
    res_fav_list = client.get("/api/v1/images?favorites=true", headers=headers)
    assert res_fav_list.status_code == 200
    fav_images = res_fav_list.get_json()["images"]
    assert len(fav_images) == 1
    assert fav_images[0]["id"] == img_id
    assert fav_images[0]["is_favorite"] is True

    # 4. Toggle again: remove from favorites
    res_unfav = client.post(f"/api/v1/images/{img_id}/favorite", headers=headers)
    assert res_unfav.status_code == 200
    assert res_unfav.get_json()["is_favorite"] is False

    # Filter by favorites should now be empty
    res_empty_favs = client.get("/api/v1/images?favorites=true", headers=headers)
    assert res_empty_favs.status_code == 200
    assert len(res_empty_favs.get_json()["images"]) == 0
