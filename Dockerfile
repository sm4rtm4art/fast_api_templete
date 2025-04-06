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

# (Optional) Verify UV installation.
RUN echo "UV location: $(which uv)" && uv --version

# Copy only pyproject.toml first for dependency resolution
COPY pyproject.toml ./

# Generate requirements.txt with only runtime dependencies.
# --no-deps might be too restrictive if the base package has deps not explicitly listed.
# Let's try compiling without --no-deps first. We exclude extras.
# --no-strip-extras is needed if pyproject.toml specifies extras, but we want *only* base deps.
# Let's explicitly install the base package '.' and then freeze.
RUN uv venv /app/.venv && \
    /app/.venv/bin/uv pip install --no-cache . && \
    /app/.venv/bin/uv pip freeze > requirements.txt

# Copy the rest of the project files
COPY . .

# Create a non-root user and adjust file ownership.
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# === Stage 2: Final Runtime Image ===
FROM python:3.12-slim AS final

WORKDIR /app

# Set runtime environment variables.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    INITIALIZE_DB=1

# Install minimal runtime dependencies and clean up.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt from builder stage
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Install runtime dependencies from requirements.txt into system site-packages
RUN uv pip install --no-cache --system -r /app/requirements.txt && \
    rm /app/requirements.txt # Clean up requirements file

# Copy only the necessary files from the builder stage.
COPY --from=builder /app/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY --from=builder /app/pyproject.toml /app/
COPY --from=builder /app/LICENSE /app/
COPY --from=builder /app/fast_api_template /app/fast_api_template

# Create a non-root user for runtime and set proper ownership.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Add a health check.
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE 8000

# Set entrypoint and default command.
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
