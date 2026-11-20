import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file located at the project root
load_dotenv(BASE_DIR / ".env")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() in {"true", "1", "yes"}
    )

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Security & JWT configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))  # seconds
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30 * 86400))  # seconds (30 days)
    JWT_TOKEN_LOCATION = ["headers", "query_string"]
    JWT_QUERY_STRING_NAME = "token"

    # Storage configuration using fsspec
    STORAGE_PROTOCOL = os.getenv("STORAGE_PROTOCOL", "file")
    STORAGE_BASE_PATH = os.getenv("STORAGE_BASE_PATH", str(BASE_DIR / "storage"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 32 * 1024 * 1024))  # 32MB default
    ALLOWED_EXTENSIONS = {
        ext.strip().lower()
        for ext in os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,webp,bmp,tiff,gif").split(",")
        if ext.strip()
    }
