FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libpq-dev curl netcat-openbsd \
	&& rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY backend ./backend
COPY README.md ./README.md
COPY run.py ./run.py
COPY scripts ./scripts

RUN pip install --upgrade pip && pip install .

COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "8", "--timeout", "120", "--worker-tmp-dir", "/dev/shm", "--keep-alive", "5", "run:app"]
