# === Stage: UV ===
FROM ghcr.io/astral-sh/uv:0.6.6 AS uv

# === Stage 1: Builder ===
FROM python:3.12-slim AS builder

# Environment variables for performance and to avoid .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_DEFAULT_TIMEOUT=600 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build dependencies and clean up.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy UV binaries from the UV stage into /usr/local/bin.
COPY --from=uv /uv /usr/local/bin/uv
COPY --from=uv /uvx /usr/local/bin/uvx

# Verify UV installation.
RUN echo "UV location: $(which uv)" && uv --version

# Copy all project files first
COPY . .

# Generate requirements.txt with only runtime dependencies, excluding the project itself
RUN uv venv .venv && \
    uv pip install --no-cache . && \
    uv pip freeze | grep -v "fast-api-template" > requirements.txt

# Create a non-root user for better security
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# === Stage 2: Development Runtime Image ===
FROM builder AS development

WORKDIR /app

# Install dev dependencies for hot reloading
RUN uv pip install --system -e .[dev,lint,test]

# Set development environment variables
ENV PORT=8000 \
    FAST_API_TEMPLATE_ENV=DEVELOPMENT \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONBREAKPOINT=0

# The app directory will be mounted as a volume in development mode
# to enable hot reloading, so we don't need to copy files here

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose application port
EXPOSE ${PORT}

# Use uvicorn with --reload for development
CMD ["uvicorn", "fast_api_template.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# === Stage 3: Final Production Runtime Image ===
FROM python:3.12-slim AS final

WORKDIR /app

# Set runtime environment variables.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app

# Install minimal runtime dependencies and clean up.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy essential project files for metadata
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/README.md /app/README.md
COPY --from=builder /app/LICENSE /app/LICENSE
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Install runtime dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    rm /app/requirements.txt

# Copy application code and scripts
COPY --from=builder /app/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY --from=builder /app/fast_api_template /app/fast_api_template

# Create a non-root user and set proper ownership.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Add a health check.
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE 8000

# Set entrypoint and default command.
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
