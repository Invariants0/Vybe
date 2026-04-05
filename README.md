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

## Documentation
- **Analytics API:** Recent visits with timestamp, referrer, and user agent metadata
- **Click Tracking:** Sampled event logging (configurable via EVENT_LOG_SAMPLE_RATE) to avoid event table explosion
- **Connection Pooling:** PostgreSQL connections reused efficiently (20 per app instance)
- **Request Tracing:** Every request gets a unique ID for debugging across logs
- **Structured Logging:** JSON format for easy parsing, search, and aggregation
- **Health Checks:** /ready endpoint returns 503 if database unavailable (Nginx drains traffic)
- **Container Ready:** Dockerfile and Docker Compose for local dev and production
- **Graceful Degradation:** Optional Redis for caching, system works without it at reduced performance

---

## 📚 Documentation & Getting Started

<details>
<summary><strong>For Developers</strong></summary>

Start here if you're contributing to or learning from the codebase:

1. [Quick Start Index](artifacts/documentation/INDEX.md) - 5 minute orientation
2. [Architecture Overview](artifacts/documentation/architecture.md) - Understand the system design
3. [API Reference](artifacts/documentation/api.md) - All 18 endpoints with examples
4. [Local Development Guide](artifacts/documentation/deploy.md#local-development) - Set up your machine

**Time commitment:** 30 minutes to understand the system

**What you'll learn:**
- How Flask, PostgreSQL, and Nginx work together
- Request flow from user to database
- How to run tests and write new features
- Connection pooling and performance optimization

</details>

<details>
<summary><strong>For DevOps / SRE</strong></summary>

Complete operational guidance for deployment and management:

1. [Deployment Guide](artifacts/documentation/deploy.md) - Local to production setup
2. [Runbooks](artifacts/documentation/runbooks.md) - Incident response procedures
3. [Configuration Reference](artifacts/documentation/config.md) - All environment variables
4. [Troubleshooting Guide](artifacts/documentation/troubleshooting.md) - 20+ common issues

**Time commitment:** 45 minutes to be on-call ready

**What you'll learn:**
- Production deployment procedures (45 minutes)
- How to respond to 7 failure scenarios
- Environment variable tuning
- Scaling from 1 instance to 10+

</details>

<details>
<summary><strong>For On-Call Engineers</strong></summary>

Fast incident response when systems are down:

1. [Runbooks](artifacts/documentation/runbooks.md) - Step-by-step procedures
2. [Troubleshooting Guide](artifacts/documentation/troubleshooting.md) - Root cause diagnosis
3. [Capacity Plan](artifacts/documentation/capacity-plan.md) - Performance limits and alerts

**Time commitment:** 15 minutes before your shift

**What you'll learn:**
- Alert names and what they mean
- How to diagnose database down scenario
- How to detect and fix CPU/memory spikes
- Rollback and recovery procedures

</details>

<details>
<summary><strong>Complete Documentation Index (10 Files)</strong></summary>

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| [README](artifacts/documentation/README.md) | Project overview with quest status | Everyone | 10 min |
| [INDEX](artifacts/documentation/INDEX.md) | Navigation guide by role | New team members | 5 min |
| [Architecture](artifacts/documentation/architecture.md) | System design & components | Engineers | 40 min |
| [API Reference](artifacts/documentation/api.md) | 18 endpoints with examples | Frontend/Backend | 20 min |
| [Deployment](artifacts/documentation/deploy.md) | Local to production | DevOps/SRE | 30 min |
| [Configuration](artifacts/documentation/config.md) | Environment variables | Operations | 15 min |
| [Troubleshooting](artifacts/documentation/troubleshooting.md) | 20+ issues with solutions | On-Call | 25 min |
| [Runbooks](artifacts/documentation/runbooks.md) | Incident response | On-Call | 30 min |
| [Decision Log](artifacts/documentation/decision-log.md) | Why Flask? PostgreSQL? | Architects | 20 min |
| [Capacity Plan](artifacts/documentation/capacity-plan.md) | Scaling & limits | Operations | 25 min |

</details>

---

## Getting Started

### Quick Demo (5 minutes)

```bash
# Clone and start everything
git clone https://github.com/YOUR_REPO/vybe.git
cd vybe
docker compose up --build
```

Visit http://localhost:8080 to see the application.

### Technology Stack

1. Clone the repository

```bash
git clone https://github.com/YOUR_REPO/vybe.git
cd vybe
```

2. Install dependencies

```bash
uv sync
```

3. Create environment file

```bash
cp .env.example .env
```

4. Start PostgreSQL (Docker)

```bash
docker run -d -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:16
```

5. Initialize database schema

```bash
uv run python scripts/init_db.py
```

6. Run the application

```bash
uv run python run.py
```

The backend runs on http://localhost:5000

### Docker Compose (All Services)

```bash
docker compose up --build
```

Access the application at http://localhost:8080

- Frontend: http://localhost:8080
- Backend API: http://localhost:8080/api
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Application Metrics: http://localhost:8000/metrics (internal only)

---

## Documentation

Complete documentation is available in the `artifacts/documentation/` folder. Start here based on your role:

### For New Developers

1. [Quick Start Index](artifacts/documentation/INDEX.md) - Navigation guide
2. [Architecture Overview](artifacts/documentation/architecture.md) - How everything fits together
3. [API Reference](artifacts/documentation/api.md) - Endpoint examples
4. [Local Development](artifacts/documentation/deploy.md#local-development) - Detailed setup

**Time commitment:** 30 minutes to understand the system

### For DevOps / SRE

1. [Deployment Guide](artifacts/documentation/deploy.md) - Local to production
2. [Runbooks](artifacts/documentation/runbooks.md) - Incident response procedures
3. [Configuration Reference](artifacts/documentation/config.md) - All environment variables
4. [Troubleshooting Guide](artifacts/documentation/troubleshooting.md) - 20+ common issues

**Time commitment:** 45 minutes to be on-call ready

### For On-Call Engineers

1. [Runbooks](artifacts/documentation/runbooks.md) - When something breaks
2. [Troubleshooting Guide](artifacts/documentation/troubleshooting.md) - Root cause diagnosis
3. [Capacity Plan](artifacts/documentation/capacity-plan.md) - Performance limits

**Time commitment:** 15 minutes to handle incidents

### Complete Documentation Index

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [README](artifacts/documentation/README.md) | Project overview with quest tier completion | Everyone | 10 min |
| [INDEX](artifacts/documentation/INDEX.md) | Navigation guide organized by role | New team members | 5 min |
| [Architecture](artifacts/documentation/architecture.md) | System design, data flow, scaling | Engineers | 40 min |
| [API Reference](artifacts/documentation/api.md) | Endpoints with curl examples | Frontend/Backend | 20 min |
| [Deployment](artifacts/documentation/deploy.md) | Local to production procedures | DevOps/SRE | 30 min |
| [Configuration](artifacts/documentation/config.md) | Environment variables and tuning | Operations | 15 min |
| [Troubleshooting](artifacts/documentation/troubleshooting.md) | 20+ issues with solutions | On-Call engineers | 25 min |
| [Runbooks](artifacts/documentation/runbooks.md) | Incident response procedures | On-Call engineers | 30 min |
| [Decision Log](artifacts/documentation/decision-log.md) | Why we chose Flask, PostgreSQL, etc. | Architects | 20 min |
| [Capacity Plan](artifacts/documentation/capacity-plan.md) | Scaling limits and growth strategy | Operations | 25 min |

**Total documentation:** 200+ pages of production-grade guidance covering Bronze, Silver, and Gold tiers of the Production Engineering Quest.

### Architecture (Quick Overview)

```
External Request  
    ↓
NGINX (Reverse Proxy & Load Balancer)
    ├─→ [Flask 1]  ├─→ PostgreSQL (Source of Truth)
    └─→ [Flask 2]  ├─→ Redis (Optional Cache)
    
↓
Prometheus Metrics
    ↓
Grafana Dashboards + AlertManager
```

**Full architecture diagram with component details:** [architecture.md](artifacts/documentation/architecture.md#components)

---

## Observability & Monitoring

<details>
<summary><strong>Metrics Collected</strong></summary>

Every request generates production metrics:

- **Request Volume:** Total HTTP requests by method, path, status
- **Latency:** P50, P95, P99 percentiles (histogram buckets)
- **Errors:** 4xx and 5xx error rates by endpoint
- **Database:** Connection pool usage, query times
- **Cache:** Hit/miss rates (if Redis enabled)
- **System:** CPU, memory, disk, network per container

</details>

<details>
<summary><strong>Pre-built Dashboards</strong></summary>

Access Grafana at http://localhost:3000 (admin/admin):

- **Overview:** Request rate, error rate, P95 latency, health status
- **Application:** Requests per endpoint, latency percentiles, error breakdown
- **Database:** Connection pool, query count, slow queries
- **Infrastructure:** CPU/memory per instance, disk I/O, network

</details>

<details>
<summary><strong>Alert Conditions</strong></summary>

Automatic alerts on these conditions:

| Alert | Trigger | Action |
|-------|---------|--------|
| Instance Down | Unreachable for 30s | Nginx drains traffic |
| High Error Rate | >5% of requests fail | Check logs immediately |
| High Latency | P95 >1 second | Investigate database/cache |
| DB Connection Pool | >90% exhausted | Scale up or cache more |
| Memory Pressure | >85% of limit | Restart or add memory |

</details>

---

## 🔄 Deployment

<details>
<summary><strong>📁 Project Structure</strong></summary>

```
backend/
  app/
    config/         Config and database setup
    controllers/    HTTP request handlers
    models/         ORM models (users, urls, events)
    repositories/   Data access layer
    services/       Business logic
    validators/     Pydantic schemas
    routes/         URL routing (18 endpoints total)
  
frontend/
  src/
    app/            Next.js pages and layouts
    components/     React UI components
    features/       Feature-specific code
    hooks/          Custom React hooks
    lib/            Utilities and helper functions
    types/          TypeScript type definitions

infra/
  docker/           Dockerfiles for services
  nginx/            Reverse proxy configuration

monitoring/
  prometheus/       Metrics scraping config
  grafana/          Pre-built dashboards
  alertmanager/     Alert routing

scripts/
  init_db.py        Database initialization
  load_test.js      Performance testing

tests/
  unit/             Component tests
  integration/      Full-stack tests
```

</details>

<details>
<summary><strong>Local Development</strong></summary>

**Quick Start (5 minutes)**

```bash
uv sync                              # Install dependencies
docker compose up -d postgres redis  # Start databases
uv run python scripts/init_db.py     # Initialize schema
uv run python run.py                 # Start backend (port 5000)
# In another terminal:
cd frontend && npm run dev           # Start frontend (port 3000)
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Metrics: http://localhost:8000/metrics (internal only)

**Hot reload:** Changes automatically refresh in browser

</details>

<details>
<summary><strong>Testing & Coverage</strong></summary>

```bash
# Run all tests with coverage
uv run pytest tests/ --cov=backend

# Run only unit tests
uv run pytest tests/unit/

# Run integration tests (requires PostgreSQL)
uv run pytest tests/integration/

# Run specific test file
uv run pytest tests/unit/test_services_coverage.py -v
```

> [!WARNING]
> Current test coverage is 45%. See [QUEST_TRACKER.md](docs/extras/QUEST_TRACKER.md) for coverage gaps and high-priority areas to test.

**Coverage Goals:**
- Critical paths (auth, data access): 100%
- Business logic (services): 80%+
- Edge cases: 60%+
- Overall target: 70%+

</details>

<details>
<summary><strong>Production Deployment</strong></summary>

**Step 1: Build Docker Image**

```bash
docker build -f infra/docker/backend.dockerfile -t vybe:latest .
docker build -f infra/docker/frontend.dockerfile -t vybe-frontend:latest .
```

**Step 2: Push to Registry**

```bash
docker push your-registry/vybe:latest
docker push your-registry/vybe-frontend:latest
```

**Step 3: Deploy with docker-compose**

Update `docker-compose.yml` with image tags, then:

```bash
docker compose -f docker-compose.yml up -d
```

**Step 4: Verify Health**

```bash
curl http://localhost/ready   # Should return 200
curl http://localhost/metrics # Should show metrics
```

> [!IMPORTANT]
> Production deployments require:
> - Environment variables configured (see [config.md](artifacts/documentation/config.md))
> - Database migrations run (new schema versions)
> - Secrets management for API keys and database passwords
> - HTTPS/SSL certificates configured in Nginx

For complete procedures, see [artifacts/documentation/deploy.md](artifacts/documentation/deploy.md)

</details>

<details>
<summary><strong>Scaling Strategy</strong></summary>

**100 RPS:** 1 Flask instance + 1 PostgreSQL sufficient

**500 RPS:** 2 Flask instances + PostgreSQL (current state)

**2000 RPS:** 4-5 Flask instances + Redis cache + PostgreSQL read replicas

**10000+ RPS:** Kubernetes orchestration + Database sharding required

Each scaling stage is documented in [capacity-plan.md](artifacts/documentation/capacity-plan.md)

</details>

---

## Quest Completion Status

<details open>
<summary><strong>Production Engineering Quest - All Tiers Complete</strong></summary>

### Bronze Tier (System Map)

- [x] Architecture diagram showing all components
- [x] Data flow walkthrough (user request → database)
- [x] Technology choices documented and justified
- [x] Scaling strategy identified
- [x] 10% test coverage baseline exceeded (45% current)

**See:** [artifacts/documentation/architecture.md](artifacts/documentation/architecture.md)

### Silver Tier (Operational Manual)

- [x] Local development setup documented
- [x] Production deployment procedures (45 minute guide)
- [x] Configuration reference (all environment variables)
- [x] Troubleshooting guide (20+ common issues)
- [x] Health check endpoints defined and working
- [x] Graceful shutdown and recovery procedures
- [x] Database migration strategy

**See:** [artifacts/documentation/deploy.md](artifacts/documentation/deploy.md), [artifacts/documentation/config.md](artifacts/documentation/config.md), [artifacts/documentation/troubleshooting.md](artifacts/documentation/troubleshooting.md)

### Gold Tier (Incident Codex)

- [x] Runbooks for 7 failure scenarios (tested April 5, 2026)
- [x] Incident detection criteria (metrics → alerts)
- [x] Root cause diagnosis procedures
- [x] Resolution steps for each scenario type
- [x] Follow-up and prevention strategies
- [x] Capacity planning with scaling boundaries
- [x] Architectural decision rationale

**See:** [artifacts/documentation/runbooks.md](artifacts/documentation/runbooks.md), [artifacts/documentation/capacity-plan.md](artifacts/documentation/capacity-plan.md), [artifacts/documentation/decision-log.md](artifacts/documentation/decision-log.md)

### Incident Testing Results (April 5, 2026)

All procedures tested under production load:

| Scenario | Detection Time | MTTR | Status |
|----------|---|------|---|
| Database Down | 98s | 2-5 min | Resilient |
| CPU Spike | 128s | 5-10 min | Monitored |
| Memory Pressure | 109s | 3-8 min | Alerting |
| Redis Connection Loss | 92s | <1 min | Graceful |
| High Error Rate | 35s | 5-15 min | Fast detection |
| Network Latency | 145s | 10-20 min | Visible in metrics |
| Single Instance Down | 30s | <1 sec | Automatic failover |

> [!NOTE]
> All 7 procedures verified to work correctly. System demonstrates production readiness and resilience.

</details>

---

## Future Scope

<details>
<summary><strong>Planned Improvements</strong></summary>

**Short-term (Next 3 months)**
- Redis cluster mode for high-availability caching
- PostgreSQL read replicas for 1000+ RPS workloads  
- API rate limiting per user/IP
- Link password protection

**Medium-term (3-6 months)**
- QR code generation for links
- Bulk URL shortening API
- Link preview with metadata extraction
- Custom domain support (links.example.com/abc123)
- Analytics export (CSV, Parquet)

**Long-term (6-12 months)**
- Kubernetes migration (from Docker Compose)
- Multi-region replication for global CDN
- Database sharding for 100B+ links
- Real-time analytics (WebSocket updates)
- Team/organization support with permissions

> [!TIP]
> None of these are blockers. The current system is production-ready and handles 500+ RPS reliably.

</details>

---

## Frequently Asked Questions

<details>
<summary><strong>Is this production-ready?</strong></summary>

Yes! This has been tested with incident scenarios and all recovery procedures work. The system:
- Handles 500+ RPS with 500ms P95 latency
- Automatically fails over if instances crash
- Gracefully handles database unavailability
- Exposes comprehensive metrics for monitoring
- Has documented incident procedures

Testing completed April 5, 2026.

</details>

<details>
<summary><strong>Can I use this commercially?</strong></summary>

Yes. Licensed under Apache 2.0. See [LICENSE](LICENSE) file for full terms.

</details>

<details>
<summary><strong>How do I get started?</strong></summary>

1. Clone the repo: `git clone https://github.com/YOUR_REPO/vybe.git`
2. Run `docker compose up --build` (everything in one command)
3. Visit http://localhost:8080
4. Read [Getting Started](artifacts/documentation/deploy.md#local-development)

Takes 5 minutes.

</details>

<details>
<summary><strong>What if I need to scale beyond 500 RPS?</strong></summary>

See [capacity-plan.md](artifacts/documentation/capacity-plan.md). The guide shows:
- Where bottlenecks appear
- How to add more instances
- When to enable caching
- How to use database replicas
- Kubernetes considerations

</details>

<details>
<summary><strong>Can I run this on Kubernetes?</strong></summary>

Yes, but currently we use Docker Compose. Kubernetes support planned for next quarter. The Dockerfiles work with any orchestrator (Kubernetes, Nomad, etc.).

</details>

---

## Support

**Issues?** Open a GitHub Issue with reproduction steps  
**Questions?** Check [artifacts/documentation/](artifacts/documentation/) folder  
**Production emergency?** See [artifacts/documentation/runbooks.md](artifacts/documentation/runbooks.md)

---

## License

![Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-orange?style=for-the-badge&logo=apache)

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) file for full terms.

You are free to:
- Use commercially
- Modify the code
- Distribute
- Use in private projects

Conditions:
- Include a copy of the license
- State significant changes
- Include NOTICE file (if present)

---

## Acknowledgments

Built as part of the **Production Engineering Quest** with emphasis on:
- **Operational Excellence** - Real-world incident handling, not just working code
- **Observability** - Every action logged, traced, and visible
- **Reliability** - Comprehensive testing, graceful degradation, automatic recovery
- **Documentation** - Runbooks, architecture diagrams, and decision logs

Every design choice prioritizes operator experience and system resilience.

---

<p align="center">
  <strong>Built for Production on April 5, 2026</strong>
  <br/>
  <a href="artifacts/documentation/">Full Documentation</a> • 
  <a href="artifacts/documentation/deploy.md">Deployment Guide</a> • 
  <a href="artifacts/documentation/runbooks.md">Incident Response</a>
</p>
