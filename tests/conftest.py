import os
import sys

# If pytest was invoked using a system Python outside .venv, forward to .venv pytest
_venv_pytest = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "pytest"))
_venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "python"))
if os.path.exists(_venv_python) and os.path.realpath(sys.executable) != os.path.realpath(_venv_python):
    import subprocess
    cmd = [_venv_pytest] + sys.argv[1:] if os.path.exists(_venv_pytest) else [_venv_python, "-m", "pytest"] + sys.argv[1:]
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

import pytest
from src.app import create_app
from src.extensions import db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes-long!"
    JWT_SECRET_KEY = "test-jwt-secret-key-that-is-at-least-32-bytes-long!"
    JWT_TOKEN_LOCATION = ["headers", "query_string"]
    JWT_QUERY_STRING_NAME = "token"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STORAGE_PROTOCOL = "file"
    FRONTEND_DIST_DIR = None


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
