from src.models.user import User


def test_user_password_hashing(db_session):
    user = User(email="test@example.com")
    user.set_password("securepassword123")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.password_hash != "securepassword123"
    assert user.check_password("securepassword123") is True
    assert user.check_password("wrongpassword") is False


def test_auth_register_and_login(client):
    # Register via /api/v1/auth/register
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "newuser@example.com"

    # Duplicate registration
    dup_res = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert dup_res.status_code == 409

    # Login via /api/v1/auth/login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["success"] is True
    token = login_data["access_token"]

    # Access protected route /api/v1/auth/me
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.get_json()["user"]["email"] == "newuser@example.com"


def test_auth_invalid_credentials(client):
    # Missing fields
    res = client.post("/api/v1/auth/login", json={"email": ""})
    assert res.status_code == 400

    # Nonexistent user
    res = client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "pwd"})
    assert res.status_code == 401
