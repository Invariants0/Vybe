# Architecture Decision Log

This document explains the key technical decisions that shaped Vybe's design, including the tradeoffs considered and why specific choices were made.

---

## Format

Each decision follows this structure:

**Status:** Accepted / Rejected / Deprecated  
**Date:** When decision was made  
**Context:** Why this decision mattered  
**Decision:** What was chosen  
**Rationale:** Why this choice over alternatives  
**Consequences:** Positive and negative outcomes  

---

## Decision 1: Flask as Web Framework vs. FastAPI

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need a Python web framework for a URL shortening API. Requirements:
- Handle 100-1000 RPS initially
- Simple request/response model (no streaming)
- Clear error handling and logging
- Mature ecosystem for production

### Decision

**Use Flask 3 with Gunicorn**

Flask was chosen over FastAPI, Django, Pyramid, and Tornado.

### Rationale

| Aspect | Flask | FastAPI | Django | Decision |
|--------|-------|---------|--------|----------|
| Learning curve | Low (explicit) | Low (async syntax) | High (batteries included) | Flask wins |
| Performance | 500-2000 RPS per worker | 1000-5000 RPS per worker | 500-2000 RPS per worker | FastAPI faster, but |
| Async support | Sync only (simple) | Full async/await | Async added later | Flask simpler |
| Production ecosystem | Mature | Becoming mature | Very mature | Flask sufficient |
| Team familiarity | High | Medium | Low | Flask wins |
| Simplicity of maintenance | Explicit code | Decorators + magic | Framework conventions | Flask wins |
| Scalability at v1 | Sufficient with pooling | Slightly better | Over-engineered | Flask sufficient |

**Tradeoff accepted:** We sacrificed maximum throughput (FastAPI might do 2x RPS) for maintainability and simplicity. At 100-1000 RPS, Flask is plenty fast. Gunicorn workers and horizontal scaling handle additional load.

### Consequences

**Positive:**
- Code is explicit and easy to understand (easy to debug in production)
- Small surface area (easy to audit for security)
- Fast development iteration
- Easy to add team members (Flask is well-known)
- Deployable on any Python 3.13+ environment

**Negative:**
- Can't leverage async/await for some I/O heavy operations
- If throughput needs exceed 10k RPS per instance, would need to refactor or switch to FastAPI
- Middleware and extensions require manual wiring vs. built-in features

**Migration path if needed:** If FastAPI becomes necessary:
1. Create FastAPI app alongside Flask routing
2. Migrate endpoints one-by-one
3. Use same ORM (Peewee) and service layer
4. Gradual switchover, not rewrite

---

## Decision 2: Peewee ORM vs. SQLAlchemy

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need an ORM to handle:
- User, URL, and events tables
- Queries: create/read/update/delete
- Connection pooling
- Multiple environments (dev/prod)

### Decision

**Use Peewee ORM**

Peewee was chosen over SQLAlchemy, Django ORM, Tortoise ORM, and raw SQL.

### Rationale

| Aspect | Peewee | SQLAlchemy | Django ORM | Decision |
|--------|--------|-----------|-----------|----------|
| API clarity | Very explicit | Flexible but complex | Magic query builder | Peewee wins |
| Learning curve | <1 day | 2-3 days | 1-2 days | Peewee wins |
| CRUD operations | Simple (2-3 lines) | Simple (3-5 lines) | Medium (1-2 lines) | Peewee simpler |
| Advanced queries | Possible but awkward | Powerful | Good | SQLAlchemy wins |
| Connection pooling | Built-in | Built-in | Built-in | Tie |
| Migration tools | Peewee Migrate | Alembic (great) | Django migrations (great) | SQLAlchemy/Django win |
| Performance at 1000 RPS | Sufficient | Slightly better | Slightly better | Peewee sufficient |
| Debugging ease | Easy (explicit SQL) | Medium | Medium | Peewee wins |
| Team expertise | Medium | High | High | Peewee acceptable |

**Tradeoff accepted:** We sacrificed some advanced query capabilities (complex joins, CTEs) for simplicity and ease of debugging. For our schema (3-4 tables), Peewee is plenty powerful.

### Consequences

**Positive:**
- Models are simple and read like English
- Debugging: can easily see generated SQL (`model.query.sql()`)
- Fast to implement CRUD operations
- Small codebase (easy to audit)
- Connection pooling with configurable limits

**Negative:**
- Can't do some advanced SQL patterns without raw SQL fallback
- If schema grows to 20+ tables with complex relationships, SQLAlchemy would be better
- Fewer plugins/extensions compared to SQLAlchemy ecosystem
- If we need to migrate, it's a rewrite (Peewee and SQLAlchemy have incompatible DSLs)

**If migration needed:** Migrate to SQLAlchemy when:
- Schema has >15 tables
- Queries require CTEs or window functions regularly
- Team needs advanced ORM features

---

## Decision 3: PostgreSQL 16 as Primary Database

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need a database that:
- Handles 1000+ concurrent short links
- Provides ACID guarantees (data integrity critical)
- Supports connection pooling
- Can scale to millions of records

### Decision

**Use PostgreSQL 16**

PostgreSQL was chosen over MySQL 8, SQLite, MongoDB, and DynamoDB.

### Rationale

| Aspect | PostgreSQL | MySQL | SQLite | MongoDB | DynamoDB |
|--------|-----------|-------|--------|---------|----------|
| ACID guarantees | Full | Full | Full | Partial | Eventual |
| Connection pooling | Excellent | Good | N/A | Proxy (pgBouncer-like) | Serverless |
| Query language | Standard SQL | SQL | SQL | Document queries | Proprietary |
| Scalability (single node) | Up to 10M records | Up to 10M records | Up to 1M | Sharding needed | Managed scaling |
| Operational simplicity | Moderate | Moderate | Easy | Complex | Very easy (managed) |
| Cost (self-hosted) | Low | Low | Low | Medium | High (per query) |
| Cost (managed) | Medium (RDS) | Medium (RDS) | N/A | High (Atlas) | Very high (pay per request) |
| Full-text search | Excellent (GIN indexes) | Good | Poor | Native | No |
| JSON support | Excellent (JSONB) | Good | Limited | Native | No |
| Development speed | Fast | Fast | Fastest | Medium | Fastest (no schema) |

**Tradeoff accepted:** We sacrificed development speed (SQLite would be fastest) for durability and scalability.

### Consequences

**Positive:**
- ACID guarantees mean no data loss (critical for link tracking)
- Handles connection pooling at scale
- Can add read replicas if needed
- Can scale to millions of URLs and billions of events
- Standard SQL is portable (can migrate to other databases)
- Excellent observability (pg_stat_statements, slow query log)
- Open source with large community

**Negative:**
- Requires separate infrastructure (not embedded like SQLite)
- DevOps overhead for backups, replication, monitoring
- Slightly more complex setup than SQLite or managed MongoDB
- If database becomes bottleneck, need to shard (not automatic)

**Rationale for not choosing alternatives:**
- **SQLite:** Too small for production. No connection pooling. Single writer. Grows to 1-2M records before performance issues.
- **MySQL:** Equivalent to PostgreSQL but with weaker default isolation levels and less advanced features. Chose PostgreSQL for its superiority.
- **MongoDB:** Would require application redesign (document model vs. relational). JSON events could work, but Links/Users benefit from relational structure.
- **DynamoDB:** Too expensive at scale (pay-per-query). Better for write-heavy, time-series data. Not suited for relational queries.

**Migration path if needed:** 
- To scale further: Add PostgreSQL read replicas (RDS Multi-AZ), then shard (manually or via Citus extension)
- To swap database: Would need application rewrite (ORM change + query rewrite) if switching to MongoDB/DynamoDB

---

## Decision 4: Optional Redis Caching with Graceful Degradation

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need caching for:
- Recently accessed URLs (high query rate)
- User profiles (frequently accessed)
- Preventing N+1 queries

Want to:
- Stay simple initially (PostgreSQL only)
- Add caching later when needed
- Not require Redis for production (reduces ops burden)

### Decision

**Add Redis caching, but make it optional (REDIS_ENABLED=false by default)**

System works without Redis. When enabled, Redis handles hot data and reduces database load.

### Rationale

| Scenario | No Redis | With Redis |
|----------|----------|-----------|
| Throughput of /api/v1/links/{code} | ~500 RPS (DB limited) | ~5,000 RPS (cache hit dominant) |
| Setup complexity | Minimal (just PostgreSQL) | Medium (need Redis + monitoring) |
| Operational risk | Low | Medium (Redis crashes affect perf, not availability) |
| Cost | Lower (fewer resources) | Higher (need Redis infrastructure) |
| Use case fit | Dev, small deployments | Production, high traffic |

**Decision:** Make Redis optional so:
1. v1.0 ships with PostgreSQL only (simpler, proven)
2. v1.1 enables Redis when throughput requirements demand it
3. If Redis fails, app degrades gracefully (queries database, slower but works)

### Consequences

**Positive:**
- Reduced initial complexity and operational burden
- Graceful degradation (Redis outage doesn't break system)
- Clear upgrade path (local dev without cache, production with cache if needed)
- Avoids premature optimization
- Redis as optional insurance policy, not critical dependency

**Negative:**
- Without Redis, throughput capped at database limits (~1000 RPS)
- Need to test both code paths (with/without cache) = more testing burden
- Cache invalidation strategy required (when to flush cache)
- If cache strategy has bugs, can lead to stale data

**Traffic tier strategy:**
- <100 RPS: No Redis needed
- 100-1000 RPS: Optional Redis for peak smoothing
- >1000 RPS: Redis highly recommended, consider read replicas too

---

## Decision 5: Docker Compose for Local Dev + Multi-Container Production

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need deployment model for:
- Local development (easy onboarding)
- Production deployment (reliable, scalable)
- Same Docker images in all environments

### Decision

**Use Docker Compose for both local dev and production**

Docker Compose was chosen over:
- Bare VM + systemd (no Docker)
- Kubernetes (too complex for v1)
- Serverless (AWS Lambda limits, no local dev)

### Rationale

| Aspect | Docker Compose | Kubernetes | Bare VM | Serverless |
|--------|---------------|-----------|---------|-----------|
| Local dev experience | Excellent (docker compose up) | Poor (need Minikube) | Painful (manual setup) | Not applicable |
| Production readiness | Good (container orchestration basics) | Excellent (highly scalable) | Painful (manual ops) | Excellent (managed) |
| Operational complexity | Low (simple YAML) | High (many resources) | Medium (shell scripts) | Medium (cloud console) |
| Cost (dev) | Free (local) | Minikube cost | Free | Expensive |
| Cost (production) | Low (single VM/server) | Medium (cluster) | Low (single VM) | High (per execution) |
| Portability | Good (runs anywhere Docker runs) | Good (cloud-native) | Poor (tied to OS) | Poor (vendor locked) |
| Autoscaling | Manual | Automatic | Manual | Automatic |
| Learning curve | Gentle | Steep | Steep | Medium |
| Team expertise | Medium (Docker common) | Low (K8s less common) | Low | Medium (cloud-dependent) |

**Tradeoff accepted:** Docker Compose is simpler and learns faster. If deployment needs exceed what Compose can handle, upgrade path to Kubernetes exists.

### Consequences

**Positive:**
- Same docker-compose.yml works locally and in prod (20x easier to debug)
- Fast local development (instant setup with `docker compose up`)
- Explicit infrastructure (all in one YAML file, easy to review)
- Built-in logging, networking, service discovery
- Cheap to run pre-production environments
- Easy to tear down and recreate isolated test environments

**Negative:**
- No automatic scaling (manual adjustment to increment replicas)
- No automatic failover (if one instance dies, manual restart)
- Limited load balancing (Nginx only, no complex routing)
- Operational tasks (backup, restore, updates) are manual
- Not suitable for 100+ container orchestration

**Kubernetes upgrade path:**
- Convert docker-compose.yml to Kubernetes manifests (Kompose tool helps)
- Migrate services one-by-one to K8s cluster
- Use similar images and environment variables (reduces changes)

---

## Decision 6: Prometheus + Grafana for Observability

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need observability for:
- Performance monitoring (latency, throughput)
- Infrastructure visibility (CPU, memory, disk)
- Alerting for anomalies
- Historical trend analysis

### Decision

**Use Prometheus for metrics + Grafana for dashboards + AlertManager for alerts**

This stack was chosen over:
- Datadog (expensive, vendor-locked)
- New Relic (expensive, closed-source)
- ELK Stack (storage-heavy, complex)
- Cloud provider native (depends on cloud, not portable)

### Rationale

| Aspect | Prometheus Stack | Datadog | New Relic | ELK Stack | CloudWatch |
|--------|----------------|---------|-----------|-----------|-----------|
| Cost | Free (open-source) | High (>$10k/month at scale) | High (similar) | Low (storage) | Medium (depends on usage) |
| Setup complexity | Medium | Easy (managed) | Easy (managed) | High | Easy (managed) |
| Self-hosted | Yes, straightforward | No | No | Possible but complex | No (AWS only) |
| Alerting | AlertManager (good) | Built-in (excellent) | Built-in (excellent) | Missing (need ELK Stack + custom) | CloudWatch Alarms (good) |
| Visualization | Grafana (excellent) | Built-in (excellent) | Built-in (excellent) | Kibana (good) | CloudWatch (limited) |
| Team control | Full (open-source) | Limited (vendor) | Limited (vendor) | Full (ELK) | Limited (AWS) |
| Portability | Fully portable (any cloud/on-prem) | Vendor lock-in | Vendor lock-in | Portable but complex | Vendor lock-in (AWS) |
| Learning curve | Gentle (time-series DB) | Steep (new platform) | Steep | Complex (distributed logging) | Medium (AWS concepts) |
| Scaling (millions of metrics) | Simple (horizontal) | Auto (managed) | Auto (managed) | Complex (sharding) | Auto (managed) |

**Tradeoff accepted:** We invested upfront time to set up open-source stack for long-term flexibility and cost savings. Datadog/New Relic would be easier now but expensive long-term.

### Consequences

**Positive:**
- Zero recurring cost (significant savings as data grows)
- No vendor lock-in (can self-host anywhere)
- Full control over retention, sampling, alerting rules
- Excellent community support for troubleshooting
- Can integrate with any tool (open APIs)
- Can spin up multiple instances for testing/development
- Prometheus time-series model perfect for performance metrics

**Negative:**
- Need to manage infrastructure (storage, backups, upgrades)
- More operational burden than Datadog/New Relic (but learning curve pays off)
- AlertManager webhook routing less polished than Datadog
- Storage overhead (15 days retention = ~5GB)
- Need to manage Grafana users, permissions manually

**Upgrade path:**
- Keep Prometheus/Grafana for metrics as long as they work
- If complexity explodes: add Datadog/New Relic as primary, keep Prometheus as backup
- Or migrate to Thanos (distributed storage layer for Prometheus)

---

## Decision 7: GitHub Actions for CI/CD (Not GitLab, Jenkins)

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need CI/CD pipeline for:
- Run tests on pull requests
- Build Docker images
- Deploy to staging/production
- Run linting and security scans

### Decision

**Use GitHub Actions**

GitHub Actions was chosen over Jenkins, GitLab CI, CircleCI, and self-hosted solutions.

### Rationale

| Aspect | GitHub Actions | Jenkins | GitLab CI | CircleCI |
|--------|---------------|---------|-----------|----------|
| Cost | Free (included with GitHub) | Self-hosted (labor) | Free tier good | Free tier limited |
| Setup | Declarative YAML | Imperative + UI | YAML-based | Web UI |
| Learning curve | Easy | Steep (plugins) | Medium | Medium |
| Integration with GitHub | Native (tight) | Plugin required | Partial | Third-party |
| Secrets management | Built-in, good | External (Vault recommended) | Built-in, good | Built-in, good |
| Scalability | GitHub infrastructure | Depends on self-host | SaaS scaling | SaaS scaling |
| Community workflows | Huge (GitHub Marketplace) | Plugins (fragmented) | Good ecosystem | Good ecosystem |
| Workflow features | Matrix builds, concurrency | Powerful but complex | Powerful | Powerful |
| Vendor lock-in | GitHub lock-in | Self-hosted (avoid) | GitLab lock-in | CircleCI lock-in |

**Tradeoff accepted:** GitHub Actions is tightly coupled to GitHub, but since code is already on GitHub, the integration benefit outweighs lock-in risk.

### Consequences

**Positive:**
- Zero setup cost
- Instant workflow visibility in GitHub UI
- Thousands of public actions (dependencies, deploys, notifications)
- Native GitHub secrets integration
- Concurrent jobs spread across GitHub infrastructure
- Easy matrix builds (test multiple Python/OS versions)
- Great documentation and community examples

**Negative:**
- Coupled to GitHub (can't easily move to GitLab if needed)
- Build minutes limited (free tier: 2000/month)
- If heavy CI usage, need paid GitHub Actions minutes
- Some advanced features require paid GitHub Enterprise

**Migration path:**
- Keep GitHub Actions for as long as it fits
- If outgrow GitHub: export workflows to GitLab CI (similar YAML format) or CircleCI

---

## Decision 8: Two App Instances with Nginx Load Balancing

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need to:
- Handle at least 1000 RPS
- Survive failure of single app instance
- Use Nginx as reverse proxy

### Decision

**Deploy 2 app instances (vybe_app1, vybe_app2) behind Nginx load balancer**

Scale strategy:
- Dev: 1 app instance
- Staging: 2 app instances
- Production: Start with 2, scale to 3-5 as needed

### Rationale

- 2 instances = redundancy (if 1 down, 50% capacity remains)
- Nginx load balancing is proven, low-overhead
- Can scale horizontally by adding more instances
- Health checks separate live instances from failed ones
- Connection pooling per instance (20 connections each, 40 total possible)

### Consequences

**Positive:**
- Simple to reason about (2 instances, clear flow)
- Nginx handles routing transparently
- Each instance is independent (one crash doesn't affect other)
- Easy on-call troubleshooting

**Negative:**
- No automatic failover (need monitoring to detect)
- Manual scaling (update docker-compose.yml, redeploy)
- Not suitable for >100 RPS per instance (throughput ceiling)

---

## Decision 9: Structured Logging (JSON to stdout)

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need logging that:
- Works with Docker (stdout only)
- Is machine-readable (grep/parse)
- Includes context (request ID, user, etc.)
- Can be forwarded to centralized system

### Decision

**Use structured JSON logging to stdout**

Every log entry is JSON:
```json
{
  "timestamp": "2026-04-05T10:00:00Z",
  "level": "INFO",
  "request_id": "req-abc123",
  "message": "Link created",
  "duration_ms": 45
}
```

### Rationale

- Docker captures stdout automatically
- JSON is machine-readable (can parse and analyze)
- Request ID allows tracing across services
- Can be forwarded to ELK, Datadog, CloudWatch
- Deterministic format (consistent parsing)

### Consequences

**Positive:**
- Easy debugging (search by request_id)
- Correlate logs across services (same request_id in Flask + Nginx logs)
- Machine-readable for alerting on patterns
- Docker-native (works out of the box)

**Negative:**
- Slightly more verbose than text logs
- Need JSON parser to read logs (can't just tail)
- Need custom tooling for log aggregation (or integrate with external service)

---

## Decision 10: Health Checks Separated Into Liveness and Readiness

**Status:** Accepted  
**Date:** Q1 2026  
**Product Version:** v1.0

### Context

Need two types of health checks:
- Liveness: "Is app process running?"
- Readiness: "Is app ready to serve traffic?"

### Decision

**Implement two endpoints**
- `/health` - Liveness check (always 200 if running)
- `/ready` - Readiness check (200 only if DB connected)

### Rationale

| Pattern | Liveness | Readiness |
|---------|----------|-----------|
| Purpose | Kill container if stuck | Add to load balancer if healthy |
| Frequency | 10-30 seconds | 5-10 seconds |
| Failure response | Restart container | Remove from routing |
| DB down response | 200 (still running) | 503 (not ready) |

**Benefits:**
- Nginx uses /ready for load balancer (only routes to ready instances)
- Container orchestrator (K8s, etc.) uses /health for restart logic
- Graceful shutdown: can make /ready return 503 while existing requests complete

### Consequences

**Positive:**
- Clear separation of concerns
- Proper load balancer integration
- Can distinguish between "crashed" and "degraded"
- Supports graceful shutdown

---

## Reviewal Cadence

These decisions should be revisited when:
- Architecture changes proposed
- Bottleneck identified that current stack can't handle
- Team wants to adopt new technology
- Cost becomes prohibitive
- Operational burden grows unsustainable

Next review: Q3 2026 (after 6 months production experience)

