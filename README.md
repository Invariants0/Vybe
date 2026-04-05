# Vybe 🔗

**Vybe** is a high-performance, **production-grade URL shortener** built to handle the unexpected. Designed for the **MLH Production Engineering Hackathon 2026**, it combines a resilient microservices architecture with deep observability and proactive incident response, ensuring that even when the pressure is on, your links stay live and your engineers stay sleeping.

![Vybe Banner](https://i.postimg.cc/zvcfX1km/image.png)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python">
  &nbsp;
  <img src="https://img.shields.io/badge/Backend-Flask-000000?logo=flask&logoColor=white" alt="Flask">
  &nbsp;
  <img src="https://img.shields.io/badge/Frontend-Next.js-000000?logo=nextdotjs&logoColor=white" alt="Frontend">
  &nbsp;
  <img src="https://img.shields.io/badge/Infra-Docker%20%7C%20Nginx-2496ED?logo=docker&logoColor=white" alt="Infra">
  &nbsp;
  <img src="https://img.shields.io/badge/Observability-Prometheus%20%7C%20Grafana-E6522C" alt="Observability">
  &nbsp;
  <img src="https://img.shields.io/badge/Scale%20Tested-~25K%20Concurrent%20Users-success" alt="Scale Tested">
</p>

<p align="center">
  <img src="https://github.com/Invariants0/Vybe/actions/workflows/ci.yml/badge.svg" alt="CI">
  &nbsp;
  <img src="https://github.com/Invariants0/Vybe/actions/workflows/docker-publish.yml/badge.svg" alt="Docker Build & Publish">
</p>

---

## 🚀 Quick Start & Getting Started

> [!IMPORTANT]  
> Make sure you have `docker`, `docker-compose`, [overmind](https://github.com/DarthSim/overmind) and [just](https://github.com/casey/just) installed on your system before proceeding.

Getting `Vybe` up and running locally only requires two steps:

```bash
git clone https://github.com/Invariants0/Vybe.git
cd Vybe
just dev-up
```

Verify your services are running perfectly:
- **API Health:** [http://localhost:5000/health/live](http://localhost:5000/health/live)
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Grafana Monitoring:** [http://localhost:3001](http://localhost:3001) *(login with `admin` / `admin`)*
- **Prometheus:** [http://localhost:9090](http://localhost:9090)

> [!TIP]
> If you wish to run backend tests after setup, use the `just test` command natively.

---

## 🏗️ Architecture

```mermaid
graph TD
    %% Define Styles
    classDef client fill:#f9f,stroke:#333,stroke-width:2px,color:#000;
    classDef proxy fill:#f96,stroke:#333,stroke-width:2px,color:#000;
    classDef app fill:#82cbf3,stroke:#333,stroke-width:2px,color:#000;
    classDef db fill:#f39c12,stroke:#333,stroke-width:2px,color:#000;
    classDef cache fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff;
    classDef obs fill:#9b59b6,stroke:#333,stroke-width:2px,color:#fff;

    User([External Client Request]):::client -->|Port 80/443| Nginx[NGINX Reverse Proxy]:::proxy
    
    subgraph Edge Application
        Nginx -->|Round Robin Load Balancing| App1[Flask Gunicorn Worker 1]:::app
        Nginx -->|Round Robin Load Balancing| App2[Flask Gunicorn Worker 2]:::app
    end

    subgraph Internal Data Layer
        App1 -->|Strict Connection Pooling| Postgres[(PostgreSQL 16)]:::db
        App2 -->|Strict Connection Pooling| Postgres
        App1 -.->|Active TTL Lookups| Redis[(Redis 7 Cache)]:::cache
        App2 -.->|Active TTL Lookups| Redis
    end

    subgraph Observability Mesh
        App1 & App2 & Postgres & Redis -->|Scrape /metrics| Prometheus[Prometheus]:::obs
        Prometheus --> Grafana[Grafana + AlertManager]:::obs
    end
```

---

## 📚 Documentation Hub

<details>
<summary>👨‍💻 <b>For Developers</b></summary>
<br/>

Understand the codebase and start contributing:
<br/><br/>

1. [**Quick Start Index**](docs/Vybe-PRD.md) - Orientation (5m)
2. [**Architecture Guide**](docs/Production%20Engineering_%20Quest%20Log.md) - Deep dive (15m)
3. [**API Reference**](#🔌-system-api-endpoints-evaluator-compatible) - All 18 endpoints
4. [**Local Dev Setup**](.tracks/deployInstructions.md) - Environment config
<br/>
</details>

<details>
<summary>🛠️ <b>For DevOps / SRE</b></summary>
<br/>

Operational guidance for production:
<br/><br/>

1. [**Deployment Guide**](.tracks/deployInstructions.md) - Local to Cloud
2. [**Config Reference**](#⚙️-configuration-environment-variables) - Env var tuning
3. [**Capacity Plan**](#📈-capacity-plan) - Scaling limits
4. [**Runbooks**](docs/runbooks/) - Incident procedures
<br/>
</details>

<details>
<summary>🚨 <b>For On-Call Engineers</b></summary>
<br/>

Fast response when things break:
<br/><br/>

1. [**Incident Runbooks**](docs/runbooks/test-scenarios.md) - Step-by-step fixes
2. [**Troubleshooting Guide**](docs/runbooks/) - Root cause diagnosis
3. [**Alert Definitions**](monitoring/README.md#alerts) - What each alert means
<br/>
</details>

<details>
<summary>📄 <b>Complete Documentation Index</b></summary>
<br/>

| Document | Audience | Time |
|----------|----------|------|
| [Architecture](docs/Production%20Engineering_%20Quest%20Log.md) | Engineers | 40m |
| [API Reference](#🔌-system-api-endpoints-evaluator-compatible) | Devs | 20m |
| [Deployment](.tracks/deployInstructions.md) | SRE | 30m |
| [Troubleshooting](docs/runbooks/test-scenarios.md) | On-Call | 25m |
| [Runbooks](docs/runbooks/) | On-Call | 30m |
| [Decision Log](#🧠-decision-log--architecture-choices) | Architects | 20m |
<br/>
</details>

---

<details>
<summary><b>🔌 System API Endpoints (Evaluator Compatible)</b></summary>
<br/>

Vybe follows the strict RESTful specifications required for the MLH Automated Test Suite.
<br/><br/>

#### Infrastructure & Health
- `GET /health` - Core health probe. Returns `200 OK` with `{"status": "ok"}`.
- `GET /ready` - Readiness probe. Verifies active database and cache connectivity.

#### User Management
- `POST /users` - Create a new user account. Returns `201 Created`.
- `GET /users` - List all users (Supports pagination `?page=x&per_page=y`).
- `GET /users/<id>` - Retrieve metadata for a specific user.
- `PUT /users/<id>` - Update user profile attributes.
- `POST /users/bulk` - Bulk import users via `multipart/form-data` CSV upload.

#### URL Engine
- `POST /urls` - Shorten a new original URL. Returns `201 Created` with a `short_code`.
- `GET /urls` - List generated links (Supports filtering `?user_id=1`).
- `GET /urls/<id>` - Retrieve deep metadata for a specific short link.
- `PUT /urls/<id>` - Update link status (`is_active`) or title.
- `GET /<short_code>` - The high-performance redirect route. Returns `302 Found`.

#### Analytics & Events
- `GET /events` - Stream high-density click logs and metadata for observability.
<br/>
</details>

<details>
<summary><b>⚙️ Configuration (Environment Variables)</b></summary>
<br/>

**ⓘ NOTE**
Create a `.env` file in the root before spinning up independent instances manually. If omitted, docker compose defaults will govern gracefully.
<br/><br/>

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | Single connection string (Preferred over individual components). |
| `DATABASE_NAME` | `hackathon_db` | Fallback PostgreSQL database name. |
| `DATABASE_HOST` | `db` | Fallback PostgreSQL host inside Docker network. |
| `DATABASE_PASSWORD` | `postgres` | Secure credential entry (MUST change in production). |
| `DB_MAX_CONNECTIONS` | `20` | Concurrent database connection pool limit. |
| `REDIS_URL` | `redis://...` | In-memory cache cluster endpoint. |
| `REDIS_ENABLED` | `true` | Master toggle for caching and rate-limiting storage. |
| `EVENT_LOG_SAMPLE_RATE`| `1.0` | Probabilistic sampling ceiling (0.0 to 1.0) to prevent storage bloat. |
| `SENTRY_DSN` | `https://...` | Error tracking and tracing sink for the production environment. |
| `LOG_LEVEL` | `INFO` | Application verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `SECRET_KEY` | `change-me` | Used for secure session signing and cryptographic hashes. |
| `FLASK_DEBUG` | `false` | Development verbosity toggle. MUST be false in `prod`. |
| `BASE_URL` | `http://...` | The public-facing URL used for generating shortened links correctly. |

</details>

<details>
<summary><b>🌐 Deployment Guide (DigitalOcean + Cloudflare)</b></summary>

### Cloudflare Edge Configuration
1. **DNS & Proxying:** Map your root domain (`A` record) to the targeted load balancer IP. Ensure the `Proxy status` is **Proxied (Orange Cloud)** to inherit Cloudflare's native DDoS protections globally.
2. **SSL/TLS Mode:** Configure encryption logic strictly to **Full (Strict)**.
3. **Edge Rules:** Enforce strict Rate Limiting (`Rate Limiting Rules`) on the `/auth/login` and `/links/create` routes to prevent brute-force PgSQL exhaustion before traffic physically reaches your Droplets.

### DigitalOcean Droplet Provisioning

1. **Provision 3 Isolated Droplets (Ubuntu 24.04 LTS):**
   - **App Droplet 1:** (Backend + Nginx)
   - **App Droplet 2:** (Backend + Nginx)
   - **Observability Droplet:** (Prometheus, Grafana, Loki, Alertmanager, OpenTelemetry)

2. **Network Integrity (Cloud Firewalls):**
   - Lock ingress traffic tightly. *Only* whitelist trusted Cloudflare IP ranges to access Port `80` / `443` on App Droplets. 
   - Open ports `3000/9090` temporarily strictly bridging to the Observability VPN hub. 

### Managed Services Integration
1. Provision a DigitalOcean **Managed PostgreSQL Cluster** and **Managed Redis Instance**.
2. Isolate them inside a localized **VPC Network**. Guarantee that only your specifically authenticated App Droplets own the VPC Private IPs to communicate. 

### Build & Deploy Execution (On App Droplets)
```bash
# 1. Clone & Set Boundaries
git clone https://github.com/Invariants0/Vybe.git && cd Vybe
cp .env.example .env 
# (Strictly define DO_HOST_1, DO_HOST_2, DB endpoints)

# 2. Spin Clusters
docker compose -f docker-compose.prod.yml up -d --build

# 3. Validation Checkout
curl http://localhost/health/ready
```
</details>

<details>
<summary><b>🛡️ Core Engineering Patterns</b></summary>

Vybe implements robust architectural blueprints resolving the *Reliability* and *Scalability* metrics natively:

- **Graceful Degradation (Silent Fails):** If the external analytics database fails to mount, the `/urls/:code` redirect continues flawlessly. Rather than throwing a `500 Internal Server Error`, the execution securely wraps telemetry dumps inside detached `try/except` logic ensuring primary flow features operate untouched.
- **Pydantic Hardening:** All JSON payload requests are universally restricted (e.g., `title` parameters bounded safely strictly under 255 chars). This decisively defends against structural data poisoning rendering `422 Unprocessable` instead of manipulating the runtime into unbounded memory exhaustion.
- **Strict Boundaries (404 vs 409):** The controller layers dynamically verify explicit Foreign Keys (`user_id` presence via `get_or_none`) before engaging active DB `IntegrityError` cascades. This translates structural constraints securely into expected REST protocol `404 Not Found` messages preventing hard DB lock-ups.
- **Zero Race Conditions:** Generating unique shortened codes doesn't strictly rely on sequential `find()` checks (which continuously yield Check-Then-Act failures across async nodes). Vybe aggressively pushes iterative hooks via a `peewee.IntegrityError` looped safety net to definitively guarantee 100% collision resolution asynchronously.
</details>

---

## 🚨 Incident Response & Deep Debugging

When production scales to thousands of hits, things will fail. Vybe is engineered to degrade gracefully.
<br/>

<details>
<summary><b>🩺 Troubleshooting Limits</b></summary>

### Services Hang Upon Startup
- Validate that `docker daemon` is operating without memory ceilings.
- Ensure ports `5000` (API) and `3001` (Grafana) aren't historically occupied. Execute `sudo lsof -i :5000`.

### Database Connection Exceptions
- Verify `.env` values correctly define `$DATABASE_HOST`. If operating `local`, ensure it reads `localhost` instead of the compose alias `db`.
- Check pg logs: `docker compose ps db` OR `docker logs vybe-db`.

### Log Serialization Faults
- If logs aren't emitting to Loki / JSON sinks, check the Gunicorn mount volume access rights (`chmod 644 logs/app.log`).
- Inspect the output: A proper log includes `ts`, `level`, `logger`, `event`, and `service`.

</details>

<details>
<summary><b>📖 Runbooks & Triggers</b></summary>

**⚠️ WARNING**  
Never perform manual `DELETE` operations on the PostgreSQL `urls` table in production. This drastically alters cache mapping consistency.

**Scenario: Postgres Database Goes Down**
> **Symptom:** P95 latency spikes massively and `500` metrics trigger.
> **Response:** Vybe utilizes *silent fails*. Secondary metrics and tracking mechanisms will be bypassed entirely to aggressively keep raw `302` redirects executing optimally. Wait for automatic container restarts or force `docker compose restart db`.

**Scenario: Foreign Key Integrations Fail**
> **Symptom:** Creation endpoints start tossing `409 Conflict`.
> **Response:** Ensure API invocations accurately check `user_id` context. 

</details>

---

## 🧠 Decision Log & Architecture Choices

| Component | Choice | Reason |
| :--- | :--- | :--- |
| **Shortening Alg** | **Base62 Generation** | Overwhelmingly scalable. We bypassed XOR-hashing strictly because generating isolated Base62 identities efficiently prevents a secondary DB lookup index bottleneck under intense scaling. |
| **Authentication** | **Redis Session Tokens** | Instead of fully stateless JWTs (which make instant revocation incredibly difficult and prone to replay attacks), localized session tokens aggressively mapped to Redis buffers deliver supreme security without querying core PgSQL tables. |
| **Telemetry Layer** | **Prometheus + OpenTelemetry** | The absolute industry standard. Rather than heavy agents like ELK/Datadog, piping native Golden Signals (Latency, Traffic, Errors, Saturation) into pure Prometheus guarantees near-zero active node overhead. |
| **Caching Core** | **Redis 7** | Replaced default dictionary/Memcached tiers. Native `TTL` policies safely evict rogue keys globally preventing split-brain caching discrepancies across duplicate `gunicorn` horizontal nodes. |
| **De-duplication** | **Organic Filtering** | Hashing identically tracked URLs continuously triggers our deduplication layer. Vybe immediately maps duplicates back to the original cached key, providing native massive resilience against automated bot/DDoS botnet attacks attempting to bloat PgSQL allocations. |
| **Hosting Model** | **Droplet Horizontal Pods** | Relying on instances arrays with managed backing engines ensures if an individual target Gunicorn instance encounters memory leaks, upstream Nginx simply actively drains the node and redirects. |

---

## 📈 Capacity Plan

Our load balancing configuration was brutally benchmarked executing realistic, massive `k6/stress-test.js` spikes natively balancing reads (redirects) vs writes (creations). 

* **Sustained Ceiling (Current):** `~2,500+ Req/Second` reliably mapped and proxied.
* **Concurrent Capacity:** `~25,000 parallel active connections` maintained securely before the `gunicorn` workers queue backs-up.
* **Bottleneck Constraints:** Relational limits. The database connection block (`20 per worker`) and network boundary I/O bandwidth limitations.

### Scale Strategy & Upgrade Segments
- **Tier 1 (100 RPS):** Single robust Node execution + Managed generic Postgres.
- **Tier 2 (2,500 RPS - Current State):** Active horizontal clustering across 3 isolated endpoints, Redis actively fronting 85% of standard cache-read lookups, massive Gunicorn instances bound purely to local IO processing.
- **Tier 3 (50,000+ RPS):** Full migration to orchestrated engines (EKS/Kubernetes). Implementing DB Sharding uniquely by hashing user identification pools. Utilizing full Global CDN edge-caching arrays directly returning the 302 URLs off-site without touching physical backend logic containers.

---

## 🏆 Quest Status

- [x] **Bronze:** Architecture & Data Flow comprehensively documented.
- [x] **Silver:** Deployment patterns mapped.
- [x] **Gold:** 7 parallel failure simulations dynamically handled (April 2026).

---

## 📄 License & Contact

License: [**Apache 2.0**](LICENSE). Please review the [COMMERCIAL_USE_NOTICE](COMMERCIAL_USE_NOTICE.md) for more information.

If an anomaly is spotted externally, submit a Pull Request or follow Runbooks attached above. 
