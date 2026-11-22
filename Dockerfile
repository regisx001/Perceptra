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
# Stage 2: Production Python Runtime with uv and Gunicorn
# =============================================================================
FROM python:3.13-slim AS runtime

# Install system dependencies required for OpenCV, NumPy, SciPy, and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation and use standalone venv managed by uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5555 \
    GUNICORN_BIND=0.0.0.0:5555 \
    FRONTEND_DIST_DIR=/app/web_dist \
    STORAGE_BASE_PATH=/app/storage \
    DATABASE_URL=sqlite:////app/instance/perceptra.db

# Cache dependencies layer
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application backend source code, readme, migrations, and unified env configuration
COPY README.md ./
COPY .env.production .env.example ./
COPY src/ src/
COPY migrations/ migrations/
COPY gunicorn.conf.py ./
COPY docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

# Complete project installation with uv
RUN uv sync --frozen --no-dev

# Copy compiled static frontend SPA assets from Stage 1
COPY --from=frontend-builder /app/web/build /app/web_dist

# Create volume mount directories
RUN mkdir -p /app/storage /app/instance

EXPOSE 5555

ENTRYPOINT ["/app/docker-entrypoint.sh"]
