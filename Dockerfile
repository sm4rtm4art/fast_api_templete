# Build stage
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -sSf https://install.determinate.systems/uv | sh -s -- --yes

# Set up workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies with UV
RUN /root/.cargo/bin/uv pip install --no-cache-dir --system -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Create non-root user
RUN groupadd -r app && useradd -r -g app app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose the application port
EXPOSE ${PORT}

# Run the application in production mode
CMD ["uvicorn", "fast_api_template.app:app", "--host=0.0.0.0", "--port=${PORT}", "--workers=4"] 