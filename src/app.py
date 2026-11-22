import logging
import os
import sys
import time
from flask import Flask, g, request, send_from_directory
from flask_cors import CORS
from src.config import Config
from src.extensions import db, migrate, bcrypt, jwt
from src.models import dummy, user, category, image, image_feature, retrieval, favorite
from src.routes.auth import auth_bp
from src.routes.categories import categories_bp
from src.routes.descriptors import descriptors_bp
from src.routes.images import images_bp
from src.routes.query import query_bp
from src.routes.analytics import history_bp, analytics_bp


def configure_logging(app: Flask):
    """
    Integrate Flask application logs with Gunicorn loggers if running under Gunicorn,
    or configure stdout logging otherwise. Also logs all HTTP incoming requests and durations.
    """
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger.handlers:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    else:
        log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            stream=sys.stdout,
        )
        app.logger.setLevel(log_level)

    @app.before_request
    def record_start_time():
        g.request_start_time = time.perf_counter()

    @app.after_request
    def log_request_info(response):
        duration_ms = 0.0
        if hasattr(g, "request_start_time"):
            duration_ms = (time.perf_counter() - g.request_start_time) * 1000

        # Don't log spammy healthchecks or static preflights unless in debug mode
        app.logger.info(
            f"{request.remote_addr} - \"{request.method} {request.path}\" "
            f"{response.status_code} in {duration_ms:.2f}ms"
        )
        return response


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Logging
    configure_logging(app)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register API v1 Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(categories_bp, url_prefix="/api/v1/categories")
    app.register_blueprint(images_bp, url_prefix="/api/v1/images")
    app.register_blueprint(descriptors_bp, url_prefix="/api/v1")
    app.register_blueprint(query_bp, url_prefix="/api/v1/query")
    app.register_blueprint(history_bp, url_prefix="/api/v1/retrieval-history")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")

    @app.route("/api/v1/version")
    def api_version():
        return {
            "api_version": "v1",
            "version": "1.0.0",
            "supported_versions": ["v1"],
            "status": "active",
        }

    # Static Frontend SPA Serving (fallback when static build is present)
    frontend_dist = app.config.get("FRONTEND_DIST_DIR")
    if frontend_dist and os.path.isdir(frontend_dist) and os.path.exists(os.path.join(frontend_dist, "index.html")):
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend_spa(path):
            # Don't intercept API routes or API versions
            if path.startswith("api/") or path == "api":
                return {"error": "API route not found"}, 404

            target_file = os.path.join(frontend_dist, path)
            if path != "" and os.path.exists(target_file) and not os.path.isdir(target_file):
                return send_from_directory(frontend_dist, path)

            return send_from_directory(frontend_dist, "index.html")
    else:
        @app.route("/")
        def index():
            return {
                "status": "ok",
                "message": "Backend initialized with SQLAlchemy, Flask-Migrate, and Auth",
                "version": "1.0.0",
                "active_api_versions": ["v1"],
                "endpoints": {
                    "v1": "/api/v1",
                },
            }

    app.logger.info("Flask application initialized successfully.")
    return app


app = create_app()
