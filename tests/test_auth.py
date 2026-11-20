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


def test_auth_refresh_tokens(client):
    # Register user
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "refreshtest@example.com", "password": "password123"},
    )
    assert reg.status_code == 201
    reg_json = reg.get_json()
    assert "access_token" in reg_json
    assert "refresh_token" in reg_json
    refresh_token = reg_json["refresh_token"]

    # 1. Refresh via Authorization header
    ref_res = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert ref_res.status_code == 200
    ref_data = ref_res.get_json()
    assert ref_data["success"] is True
    assert "access_token" in ref_data
    assert "refresh_token" in ref_data
    new_access_token = ref_data["access_token"]

    # Use new access token on protected route
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.get_json()["user"]["email"] == "refreshtest@example.com"

    # 2. Refresh via JSON body
    ref_res2 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ref_data["refresh_token"]},
    )
    assert ref_res2.status_code == 200
    assert ref_res2.get_json()["success"] is True

    # 3. Reject access token used at refresh endpoint
    bad_res = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert bad_res.status_code == 401

    # 4. Reject invalid token
    invalid_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.jwt.token"},
    )
    assert invalid_res.status_code == 401


def test_auth_invalid_credentials(client):
    # Missing fields
    res = client.post("/api/v1/auth/login", json={"email": ""})
    assert res.status_code == 400

    # Nonexistent user
    res = client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "pwd"})
    assert res.status_code == 401
