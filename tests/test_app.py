from src.app import create_app
from src.config import Config


def test_app_creation_default_config():
    app = create_app()
    assert app is not None
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///app.db"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False


def test_app_creation_custom_config():
    class CustomConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    app = create_app(config_class=CustomConfig)
    assert app.config["TESTING"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "Backend initialized" in data["message"]
    assert data["version"] == "1.0.0"
    assert "v1" in data["active_api_versions"]


def test_api_version_endpoints(client):
    # Test /api/v1/version
    res_v1 = client.get("/api/v1/version")
    assert res_v1.status_code == 200
    data_v1 = res_v1.get_json()
    assert data_v1["api_version"] == "v1"
    assert data_v1["status"] == "active"

    # Test alias /api/version
    res_alias = client.get("/api/version")
    assert res_alias.status_code == 200
    assert res_alias.get_json() == data_v1

    # Verify auth and files are accessible via /api/v1
    reg_res = client.post("/api/v1/auth/login", json={"email": "nonexistent@test.com", "password": "123"})
    assert reg_res.status_code == 401
