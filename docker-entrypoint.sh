#!/bin/bash
set -e

export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-80}
export GUNICORN_BIND=${GUNICORN_BIND:-127.0.0.1:5555}

echo "==> [Perceptra] Preparing runtime storage and cache directories..."
mkdir -p /app/storage /app/instance /run/nginx /var/log/nginx /var/cache/nginx

echo "==> [Perceptra] Running database schema migrations..."
uv run flask --app src.app:create_app db upgrade

echo "==> [Perceptra] Configuring Nginx reverse proxy (listening on port ${PORT})..."
mkdir -p /etc/nginx/conf.d
if [ -f /etc/nginx/templates/default.conf.template ]; then
    envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
fi
rm -f /etc/nginx/sites-enabled/default

echo "==> [Perceptra] Starting Gunicorn WSGI server on ${GUNICORN_BIND}..."
uv run gunicorn --config gunicorn.conf.py --bind "${GUNICORN_BIND}" "src.app:create_app()" &
GUNICORN_PID=$!

# Wait for Gunicorn backend to be ready before starting Nginx
echo "==> [Perceptra] Awaiting Gunicorn backend initialization..."
for i in $(seq 1 30); do
    if curl -s -f "http://127.0.0.1:5555/api/v1/version" > /dev/null 2>&1; then
        echo "==> [Perceptra] Gunicorn backend is responsive."
        break
    fi
    sleep 0.5
done

echo "==> [Perceptra] Testing Nginx configuration..."
nginx -t

echo "==> [Perceptra] Starting Nginx edge server..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Graceful termination handler
cleanup() {
    echo "==> [Perceptra] Received shutdown signal. Terminating services..."
    kill -TERM "$GUNICORN_PID" 2>/dev/null || true
    kill -QUIT "$NGINX_PID" 2>/dev/null || true
    wait "$GUNICORN_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
    exit 0
}

trap cleanup TERM INT

# Wait for either process to terminate
wait -n "$GUNICORN_PID" "$NGINX_PID"
