#!/bin/sh
set -e

export FLASK_ENV=${FLASK_ENV:-production}

echo "==> Ensuring required directories exist..."
mkdir -p /app/storage /app/instance

echo "==> Running database migrations..."
uv run flask --app src.app:create_app db upgrade

echo "==> Starting Gunicorn server on port ${PORT:-5555}..."
exec uv run gunicorn --config gunicorn.conf.py "src.app:create_app()"
