FROM python:3.13-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels \
    flask flask-limiter gunicorn psycopg2-binary redis prometheus-client pydantic python-dotenv sentry-sdk[flask] peewee email-validator faker pytest pytest-cov testcontainers

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV FLASK_ENV=production
ENV WORK_DIR=/app

WORKDIR ${WORK_DIR}

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

COPY --from=builder /build/wheels /wheels
RUN pip install --upgrade pip && \
    pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

COPY backend ./backend
COPY README.md ./README.md
COPY run.py ./run.py
COPY scripts ./scripts

RUN chmod +x /app/scripts/docker-entrypoint.sh
# Make entrypoint executable
RUN sed -i 's/\r$//' /app/scripts/docker-entrypoint.sh && chmod +x /app/scripts/docker-entrypoint.sh

# Switch to non-root user
RUN chown -R appuser:appuser ${WORK_DIR}
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=30s \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--threads", "2", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "run:app"]
