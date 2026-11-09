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
