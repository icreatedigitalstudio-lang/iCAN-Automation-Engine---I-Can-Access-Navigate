# Global Standards Production Dockerfile - Multi-stage, non-root, distroless-ready
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --upgrade pip
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN useradd -m -u 1000 appuser && mkdir -p /app/data /app/output && chown -R appuser:appuser /app
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .
USER appuser
ENV PYTHONPATH=/app/src
EXPOSE 8000 8765 9000 9001
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8000/health/live', timeout=3)"
CMD ["uvicorn", "icreate.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-config", "src/icreate/observability/logging_conf.yaml"]
