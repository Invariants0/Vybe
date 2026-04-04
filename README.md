# Vybe URL Shortener

Production-oriented URL shortener built on the existing Flask + Peewee + PostgreSQL stack.

## Stack

- Flask 3
- Peewee ORM
- PostgreSQL
- Gunicorn
- Nginx and Docker assets under `infra/`

## Folder structure

```text
app/
  config.py
  database.py
  errors.py
  middleware/
  models/
  routes/
  services/
  utils/
docs/
  api.md
infra/
  db/
  docker/
  nginx/
logs/
scripts/
  init_db.py
run.py
```

## Features

- Short-link creation with optional custom aliases
- Redirect handling with click tracking
- Link expiry and soft deactivation
- Stats and recent visit APIs
- Pooled PostgreSQL connections
- Structured request logging with request IDs
- Container-ready deployment assets

## Local development

1. Install dependencies:

```powershell
uv sync
```

2. Create `.env` from `.env.example`.

3. Start PostgreSQL locally.

4. Initialize tables:

```powershell
uv run python scripts/init_db.py
```

5. Run the app:

```powershell
uv run python run.py
```

The service will be available at `http://localhost:5000`.

If you want startup-driven schema creation in local development, set `AUTO_CREATE_TABLES=true`.

## API overview

- `POST /api/v1/links`
- `GET /api/v1/links/{code}`
- `GET /api/v1/links/{code}/visits`
- `PATCH /api/v1/links/{code}`
- `DELETE /api/v1/links/{code}`
- `GET /{code}`

Detailed examples: [docs/api.md](docs/api.md)

## Docker

Build and run with compose:

```powershell
docker compose -f infra/docker/docker-compose.yml up --build
```

Nginx will expose the service on `http://localhost:8080`.
