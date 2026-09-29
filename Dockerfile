# ═══════════════════════════════════════════════════════════════════
# CP2 — Containerization
# Multi-stage build: builder → runtime
# ═══════════════════════════════════════════════════════════════════


# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy dependency trước để tận dụng Docker cache
COPY requirements.txt .

# Tạo virtual environment và cài dependency
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy environment đã cài dependency từ builder
COPY --from=builder /opt/venv /opt/venv

# Copy source code sau khi dependency đã được cài
COPY app ./app
COPY utils ./utils

# Tạo user thường, không chạy bằng root
RUN useradd --create-home --shell /bin/bash appuser

# Sử dụng Python trong virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Container chạy bằng user thường
USER appuser

# Port mặc định để document
EXPOSE 8000

# Health check endpoint /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8000') + '/health')" || exit 1

# PORT do cloud/environment cung cấp, mặc định 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]