# === Stage: UV ===
FROM ghcr.io/astral-sh/uv:0.6.6 AS uv

# === Stage: Builder ===
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy UV from the UV stage
COPY --from=uv /uv /usr/local/bin/uv
COPY --from=uv /uvx /usr/local/bin/uvx

# Set up workdir
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies with UV
RUN uv pip install --system -e .

# Runtime stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Copy UV from the UV stage
COPY --from=uv /uv /usr/local/bin/uv
COPY --from=uv /uvx /usr/local/bin/uvx

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r app && useradd -r -g app app

# Create app directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/

# Create an entrypoint script
RUN echo '#!/bin/bash\nif [ "$1" = "api" ]; then\n  exec uvicorn fast_api_template.app:app --host 0.0.0.0 --port ${PORT} --workers=4\nelse\n  exec "$@"\nfi' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose the application port
EXPOSE ${PORT}

# Use the flexible entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
