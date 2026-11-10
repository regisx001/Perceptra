import pytest
from src.app import create_app
from src.extensions import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STORAGE_PROTOCOL = "file"


@pytest.fixture
def app(tmp_path):
    class AppTestConfig(TestConfig):
        STORAGE_BASE_PATH = str(tmp_path / "storage")

    app = create_app(config_class=AppTestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
