FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY backend ./backend
COPY README.md ./README.md
COPY run.py ./run.py
COPY scripts ./scripts

RUN pip install --upgrade pip && pip install ./backend

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "4", "run:app"]
