# =============================================================================
# Stage 1: Build SvelteKit static SPA with Bun
# =============================================================================
FROM oven/bun:1-alpine AS frontend-builder

WORKDIR /app

# Copy production environment so Vite envDir resolves root .env.production
COPY .env.production .env.example ./

WORKDIR /app/web

# Copy package descriptors and project.inlang needed for prepare script
COPY web/package.json web/bun.lock ./
COPY web/project.inlang ./project.inlang
RUN bun install --frozen-lockfile

# Copy frontend source files
COPY web/ ./

# Build static production bundle into /app/web/build
RUN bun run build

# =============================================================================
# Stage 2: Production Python Runtime with uv, Gunicorn, and Nginx Reverse Proxy
# =============================================================================
FROM python:3.13-slim AS runtime

# Install system dependencies required for OpenCV, NumPy, SciPy, Pillow, and Nginx
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation and runtime defaults
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=80 \
    GUNICORN_BIND=127.0.0.1:5555 \
    FRONTEND_DIST_DIR=/app/web_dist \
    STORAGE_BASE_PATH=/app/storage \
    DATABASE_URL=sqlite:////app/instance/perceptra.db

# Cache dependencies layer
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application backend source code, migrations, configs, and entrypoint
COPY README.md ./
COPY .env.production .env.example ./
COPY src/ src/
COPY migrations/ migrations/
COPY gunicorn.conf.py ./
COPY docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

# Copy Nginx template configuration
RUN mkdir -p /etc/nginx/templates
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Complete project installation with uv
RUN uv sync --frozen --no-dev

# Copy compiled static frontend SPA assets from Stage 1
COPY --from=frontend-builder /app/web/build /app/web_dist

# Create volume mount directories
RUN mkdir -p /app/storage /app/instance /run/nginx /var/log/nginx /var/cache/nginx

# Healthcheck targeting the Nginx reverse proxy endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-80}/api/v1/version || exit 1

EXPOSE 80

ENTRYPOINT ["/app/docker-entrypoint.sh"]
