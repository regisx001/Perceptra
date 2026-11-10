from flask import Flask
from src.config import Config
from src.extensions import db, migrate
from src.models import dummy
from src.routes.files import files_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(files_bp)

    @app.route("/")
    def index():
        return {"status": "ok", "message": "Backend initialized with SQLAlchemy and Flask-Migrate"}

    return app



app = create_app()
