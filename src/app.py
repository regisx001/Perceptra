import logging
import sys
import time
from flask import Flask, g, request
from flask_cors import CORS
from src.config import Config
from src.extensions import db, migrate, bcrypt, jwt
from src.models import dummy, user
from src.routes.auth import auth_bp
from src.routes.files import files_bp


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
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth", name="auth_v1")
    app.register_blueprint(files_bp, url_prefix="/api/v1/files", name="files_v1")

    # Backwards compatibility: alias to default active version (v1)
    app.register_blueprint(auth_bp, url_prefix="/api/auth", name="auth_default")
    app.register_blueprint(files_bp, url_prefix="/api/files", name="files_default")

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

    @app.route("/api/version")
    @app.route("/api/v1/version")
    def api_version():
        return {
            "api_version": "v1",
            "version": "1.0.0",
            "supported_versions": ["v1"],
            "status": "active",
        }

    app.logger.info("Flask application initialized successfully.")
    return app


app = create_app()
