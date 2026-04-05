# Vybe URL Shortener

Production-grade URL shortener built for the Production Engineering Quest. Production-ready with observability, incident response, and reliability testing.

---

## Quick Start

```bash
git clone https://github.com/YOUR_REPO/vybe.git
cd vybe
docker compose up --build
```

Visit http://localhost:8080 - that's it!

---

## What You Get

- **Fast Redirects:** 45ms p95 latency at 500 RPS
- **Resilient:** Handles database down, cache failure, single instance crash
- **Observable:** Prometheus + Grafana dashboards, structured logging
- **Tested:** 7 failure scenarios verified, 45% code coverage  
- **Documented:** Full runbooks, architecture guides, incident procedures

---

## Setup Options

<details>
<summary><strong>Local Development (Python)</strong></summary>

```bash
# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Start PostgreSQL
docker run -d -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:16

# Initialize database
uv run python scripts/init_db.py

# Run backend
uv run python run.py  # http://localhost:5000

# Run frontend (different terminal)
cd frontend
npm run dev  # http://localhost:3000
```

</details>

<details>
<summary><strong>Docker Compose (All Services)</strong></summary>

```bash
docker compose up --build
```

Access at http://localhost:8080

Services:
- Frontend: http://localhost:8080
- API: http://localhost:8080/api
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

</details>

---

## Documentation

**Choose your path:**

| Role | Start Here | Time |
|------|-----------|------|
| Developer | [Quick Start](artifacts/documentation/INDEX.md) → [Architecture](artifacts/documentation/architecture.md) | 30 min |
| DevOps/On-Call | [Deployment](artifacts/documentation/deploy.md) → [Runbooks](artifacts/documentation/runbooks.md) | 45 min |
| See Everything | [artifacts/documentation/](artifacts/documentation/) folder | Varies |

<details>
<summary><strong>All Documentation (13 Files)</strong></summary>

**Core**
- [INDEX](artifacts/documentation/INDEX.md) - Role-based navigation
- [Architecture](artifacts/documentation/architecture.md) - System design & data flow
- [API Reference](artifacts/documentation/api.md) - 18 endpoints with examples

**Operations**
- [Deployment](artifacts/documentation/deploy.md) - Local to production
- [Configuration](artifacts/documentation/config.md) - Environment variables
- [Troubleshooting](artifacts/documentation/troubleshooting.md) - 20+ issues & solutions
- [Runbooks](artifacts/documentation/runbooks.md) - Incident response

**Architecture & Planning**
- [Decision Log](artifacts/documentation/decision-log.md) - Why Flask? PostgreSQL?
- [Capacity Plan](artifacts/documentation/capacity-plan.md) - Scaling & limits

**PE Hack Results**
- [Reliability](artifacts/documentation/Reliability/) - 35-hour sprint results
- [Scalability](artifacts/documentation/Scalability/) - Load testing & bottlenecks
- [Incident Response](artifacts/documentation/Incident-Response/) - IR procedures & testing

**Also**
- [README (Artifact)](artifacts/documentation/README.md) - Quest tier completion status

</details>

---

## Tech Stack

<details>
<summary><strong>Show Tech Details</strong></summary>

**Backend:** Python 3.13, Flask 3, Peewee ORM, PostgreSQL 16, Gunicorn  
**Frontend:** Next.js 15, React 19, TypeScript, Zustand  
**Infrastructure:** Docker, Docker Compose, Nginx  
**Observability:** Prometheus, Grafana, AlertManager, structured JSON logging  
**Testing:** pytest, k6 load testing, 45% code coverage

</details>

---

## Key Features

- Short link creation with optional custom aliases
- Fast redirects (45ms) with click tracking
- Link expiry and soft deactivation
- Analytics API with visitor metadata
- Connection pooling (20 per instance)
- Request tracing with unique IDs
- Structured JSON logging
- Graceful Redis cache (system works without it)
- Automatic health checks

---

## Production Status

**Certified:** April 5, 2026  
**Uptime Target:** 99.8%  
**Load Tested:** 500 RPS sustained, 700+ RPS burst  
**Incident Testing:** 7/7 scenarios passed  
**Code Coverage:** 45% (target: 10%)

---

## Quick Links

- API Docs: [artifacts/documentation/api.md](artifacts/documentation/api.md)
- Runbooks: [artifacts/documentation/runbooks.md](artifacts/documentation/runbooks.md)
- Troubleshooting: [artifacts/documentation/troubleshooting.md](artifacts/documentation/troubleshooting.md)

---

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

Built as part of the Production Engineering Quest with focus on operational excellence, reliability, and observability.
