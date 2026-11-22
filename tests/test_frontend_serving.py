import os
from pathlib import Path
from src.app import create_app
from tests.conftest import TestConfig


def test_static_frontend_serving(tmp_path):
    # Create mock frontend dist directory
    dist_dir = tmp_path / "web_dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<!doctype html><html><body><h1>Perceptra SPA</h1></body></html>")
    (dist_dir / "app.js").write_text("console.log('Perceptra');")

    class FrontendConfig(TestConfig):
        FRONTEND_DIST_DIR = str(dist_dir)
        STORAGE_BASE_PATH = str(tmp_path / "storage")

    app = create_app(config_class=FrontendConfig)
    client = app.test_client()

    # Requesting root returns index.html
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert b"<h1>Perceptra SPA</h1>" in res_root.data

    # Requesting a static asset directly
    res_asset = client.get("/app.js")
    assert res_asset.status_code == 200
    assert b"console.log('Perceptra');" in res_asset.data

    # Requesting arbitrary SPA route falls back to index.html
    res_spa = client.get("/dashboard/query")
    assert res_spa.status_code == 200
    assert b"<h1>Perceptra SPA</h1>" in res_spa.data

    # API routes are preserved and not intercepted
    res_api = client.get("/api/v1/version")
    assert res_api.status_code == 200
    assert res_api.get_json()["api_version"] == "v1"

    # Bad API routes return 404 JSON, not SPA index.html
    res_bad_api = client.get("/api/v1/non-existent-endpoint")
    assert res_bad_api.status_code == 404
    assert res_bad_api.is_json
