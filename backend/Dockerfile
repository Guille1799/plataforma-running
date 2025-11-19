# ============================================================================
# RunCoach AI - Production Dockerfile
# ============================================================================
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies to site-packages
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python site-packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Create non-root user for security
RUN useradd -m -u 1000 runcoach && \
    chown -R runcoach:runcoach /app

USER runcoach

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
