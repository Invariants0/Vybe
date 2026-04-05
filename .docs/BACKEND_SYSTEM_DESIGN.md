# Vybe Backend System Design

**Framework:** Flask + Peewee + PostgreSQL  
**Date:** April 4, 2026  
**Purpose:** Design backend infrastructure beyond core URL shortening feature

---

## 1. REQUIREMENTS GATHERING

### Functional Requirements (Non-Core Features)
- ✅ User management (CRUD, authentication if needed)
- ✅ Event logging (track API usage, link visits)
- ✅ Bulk import/export (CSV users, URLs)
- ✅ API monitoring via Prometheus/Grafana
- ✅ Error tracking via Sentry
- ✅ Request tracing (X-Request-Id correlation)

### Non-Functional Requirements

| Requirement | Target | Reasoning |
|-------------|--------|-----------|
| **Latency** | P95 < 200ms for URL creation | User-facing operation; expects fast redirect |
| **Availability** | 99.5% uptime (SLA) | MLH evaluator will test; brief downtime acceptable |
| **Throughput** | 1,000 req/sec sustained | Hackathon scale; not production volume |
| **Data Consistency** | ACID on user/URL/event operations | Prevent duplicate short codes, lost visits |
| **Error Recovery** | Automatic retry on transient failures | Polly/Circuit breaker pattern |
| **Observability** | <5min MTTR for critical issues | Sentry alerts + Prometheus dashboards |
| **Security** | Rate limiting on public endpoints | Prevent abuse of shortener |

### Constraints
- **Team:** 1-2 engineers (self-explanatory code required)
- **Timeline:** Hackathon (days to weeks)
- **Tech Stack:** Python/Flask (locked; no change)
- **Deployment:** Docker Compose locally; Cloud Run for prod (optional)
- **Database:** PostgreSQL 16 with connection pooling

---

## 2. HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                    (MLH Evaluator Tests)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────────────────┐
│                   NGINX REVERSE PROXY                            │
│           (Load Balancing, SSL, Compression)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    FLASK APPLICATION                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Routes Layer      (Thin → delegate to controllers)         │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ Controller Layer  (Request coordination + error handling)  │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ Service Layer     (Business logic isolation)               │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ Repository Layer  (Data access abstraction)                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│  ┌────────────────────────┼────────────────────────────────────┐ │
│  │ Optional: Fast Path    │                                    │ │
│  │ ┌──────────────────────▼─────────────────────────────────┐ │ │
│  │ │  Redis Cache (Link metadata, user profiles)           │ │ │
│  │ └──────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌──────────┐  ┌────────────┐
   │PostgreSQL  │  Redis   │  │ Sentry API │
   │(Persistent)│(Optional)│  │(Errors)    │
   └─────────┘  └──────────┘  └────────────┘

Observability Stack (Outside App):
  Prometheus → Scrapes /metrics @ 15s intervals
  Grafana    → Visualizes system health
  AlertMgr   → Fires alerts on threshold breach
```

### Data Flow: Create Short URL

```
1. POST /api/v1/urls
   ↓
2. Routes → URLController.create_short_url()
   ↓
3. Validate input (Pydantic Schema)
   ↓
4. URLService.create_short_url(original_url, ...)
   ├─ Call URLRepository.find_by_code(code) → check collision
   ├─ Generate unique code
   └─ Call URLRepository.create(url_obj)
   ↓
5. Repository.create() → Peewee Model.save()
   ├─ Transaction START
   ├─ INSERT into short_urls
   ├─ INSERT audit event
   └─ Transaction COMMIT
   ↓
6. Return 201 + short_url object
   ↓
7. After-request middleware
   ├─ Log: "POST /api/v1/urls -> 201 (45ms)"
   ├─ Send latency metric to Prometheus
   └─ Extract X-Request-Id → Sentry context
   ↓
8. MLH Evaluator receives response
```

---

## 3. DEEP DIVES

### 3.1 Error Handling Strategy

**Current State:** ❌ Routes handle errors manually; no Sentry integration.

**Design:**

```
┌─────────────────────────────────────────┐
│ 1. Route Handler (Thin)                 │
├─────────────────────────────────────────┤
│ def create_url():                       │
│     try:                                │
│         return url_controller.handle()  │
│     except ErrorHandler catches all     │
└─────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────┐
│ 2. Controller (Coordination)             │
├─────────────────────────────────────────┤
│ def create(self, req):                  │
│     try:                                │
│         service.create(...)             │
│     except AppError as e:               │
│         Sentry.capture_exception()      │
│         return error_response(e)        │
│     except Exception as e:              │
│         Sentry.capture_exception()      │
│         return generic_error()          │
└─────────────────────────────────────────┘
```

**Error Categories:**

| Category | HTTP Code | Sentry Severity | Retry |
|----------|-----------|-----------------|-------|
| **ValidationError** | 400 | INFO | No |
| **NotFoundError** | 404 | DEBUG | No |
| **ConflictError** (duplicate code) | 409 | INFO | No |
| **DatabaseError** (connection lost) | 503 | ERROR | Yes (exponential backoff) |
| **TransactionAborted** | 503 | ERROR | Yes (new transaction) |
| **Unexpected Exception** | 500 | CRITICAL | Manual investigation |

**Implementation:**

```python
# backend/app/config/errors.py
class AppError(Exception):
    status_code = 400
    error_code = "app_error"
    sentry_severity = "info"

class DatabaseError(AppError):
    status_code = 503
    error_code = "database_error"
    sentry_severity = "error"

# backend/app/controllers/base_controller.py
import sentry_sdk

class BaseController:
    def handle_error(self, error, operation_name):
        if isinstance(error, AppError):
            sentry_sdk.capture_exception(
                error,
                tags={"operation": operation_name},
                level=error.sentry_severity
            )
            return jsonify(
                error=error.error_code,
                message=str(error),
                request_id=g.request_id
            ), error.status_code
        else:
            sentry_sdk.capture_exception(
                error,
                tags={"operation": operation_name},
                level="critical"
            )
            return jsonify(
                error="internal_server_error",
                message="An unexpected error occurred",
                request_id=g.request_id
            ), 500
```

### 3.2 API Design Standards

**Endpoint Structure:**

All endpoints follow RESTful conventions with versioning:
- Base: `/api/v1/<resource>`
- Methods: `GET`, `POST`, `PUT`, `DELETE`
- Status codes: 200, 201, 204, 400, 404, 409, 500

**Request/Response Contract (Pydantic):**

```python
# backend/app/validators/schemas.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class CreateShortURLSchema(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = Field(None, max_length=32)
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://github.com/octocat/Hello-World",
                "custom_alias": "gh-repo",
                "expires_at": "2026-04-11T23:59:59Z"
            }
        }

class ShortURLResponseSchema(BaseModel):
    id: int
    short_code: str
    original_url: str
    custom_alias: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    visit_count: int
    short_url: str  # computed: BASE_URL + short_code
```

**Example Endpoints (18 from MLH spec):**

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/health` | GET | Service liveness | `{status: "ok"}` |
| `/ready` | GET | Service readiness (DB check) | `{status: "ready"}` |
| `/users` | POST | Create user | `{id, username, email, created_at}` |
| `/users` | GET | List users (paginated) | `{data: [...], total, page, per_page}` |
| `/users/<id>` | GET | Get user by ID | `{id, username, email, ...}` |
| `/users/<id>` | PUT | Update user | User object |
| `/users/import` | POST | Bulk CSV import | `{count_imported, errors: [...]}` |
| `/urls` | POST | Create short URL | ShortURLResponseSchema |
| `/urls` | GET | List URLs (paginated) | `{data: [...], total}` |
| `/urls/<id>` | GET | Get URL details + visits | `{...url, visits: [{ip, timestamp}, ...]}` |
| `/urls/<id>` | PUT | Update URL | URL object |
| `/urls/<id>` | DELETE | Delete URL | `{success: true}` |
| `/events` | GET | List events (paginated) | `{data: [...], total}` |
| `/metrics` | GET | Prometheus metrics | Text format (auto) |

**Request ID Propagation:**

Every request gets `X-Request-Id` header (UUID if not present):

```
Request:  POST /api/v1/urls
Header:   X-Request-Id: 550e8400-e29b-41d4-a716-446655440000

Middleware attaches to g.request_id for logging & correlation
Response: Same request ID echoed back for client tracking
Sentry:   Includes request_id in error context for correlation
```

### 3.3 Database Access Patterns

**Current Problem:** ❌ Routes/services access ORM models directly → hard to test, tight coupling.

**Solution: Repository Pattern**

```python
# backend/app/repositories/base_repository.py
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, model_class: T):
        self.model = model_class
    
    def create(self, **kwargs) -> T:
        """Create and return instance."""
        obj = self.model.create(**kwargs)
        return obj
    
    def find_by_id(self, id: int) -> Optional[T]:
        try:
            return self.model.get_by_id(id)
        except DoesNotExist:
            return None
    
    def find_one(self, **filters) -> Optional[T]:
        try:
            return self.model.get(**filters)
        except DoesNotExist:
            return None
    
    def find_all(self, skip=0, limit=100, **filters) -> List[T]:
        query = self.model.select()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return list(query.offset(skip).limit(limit))
    
    def update(self, id: int, **updates) -> Optional[T]:
        obj = self.find_by_id(id)
        if not obj:
            return None
        for key, value in updates.items():
            setattr(obj, key, value)
        obj.save()
        return obj
    
    def delete(self, id: int) -> bool:
        return self.model.delete_by_id(id) > 0

# backend/app/repositories/url_repository.py
class URLRepository(BaseRepository):
    def __init__(self):
        super().__init__(ShortURL)
    
    def find_by_code(self, code: str) -> Optional[ShortURL]:
        return self.find_one(short_code=code)
    
    def find_by_custom_alias(self, alias: str) -> Optional[ShortURL]:
        return self.find_one(custom_alias=alias)
    
    def get_recent_visits(self, url_id: int, limit: int = 100) -> List[LinkVisit]:
        return list(
            LinkVisit
            .select()
            .where(LinkVisit.short_url_id == url_id)
            .order_by(LinkVisit.visited_at.desc())
            .limit(limit)
        )
    
    def count_visits(self, url_id: int) -> int:
        return LinkVisit.select().where(LinkVisit.short_url_id == url_id).count()
    
    def get_all_with_visit_counts(self, skip=0, limit=100):
        """Optimized query with visit counts."""
        from peewee import fn
        
        query = (
            ShortURL
            .select(ShortURL, fn.COUNT(LinkVisit.id).alias('visit_count'))
            .join(LinkVisit, JOIN.LEFT_OUTER)
            .group_by(ShortURL.id)
            .offset(skip)
            .limit(limit)
        )
        return list(query)
```

**Service → Repository Injection:**

```python
# backend/app/services/url_shortener.py
class URLShortenerService:
    def __init__(
        self,
        config: AppConfig,
        url_repo: URLRepository = None,
        event_repo: EventRepository = None
    ):
        self.config = config
        self.url_repo = url_repo or URLRepository()
        self.event_repo = event_repo or EventRepository()
    
    def create_short_url(self, original_url, custom_alias=None, creator_ip=None):
        with db.transaction():
            # Check collision
            if custom_alias and self.url_repo.find_by_custom_alias(custom_alias):
                raise ConflictError(f"Alias '{custom_alias}' already taken")
            
            code = self._generate_code()
            while self.url_repo.find_by_code(code):
                code = self._generate_code()
            
            # Create URL
            url_obj = self.url_repo.create(
                short_code=code,
                custom_alias=custom_alias,
                original_url=original_url
            )
            
            # Log event
            self.event_repo.create(
                event_type="url_created",
                url_id=url_obj.id,
                metadata={"creator_ip": creator_ip}
            )
            
            return url_obj
```

**Transaction Management:**

```python
# backend/app/config/database.py

# At module level:
db = DatabaseProxy()

# In controller:
from backend.app.config import db

with db.transaction():
    url = url_repo.create(...)
    event = event_repo.create(...)
    # If any exception: ROLLBACK (automatic)
    # On success: COMMIT

# Or atomic decorator:
@db.atomic()
def create_url_with_audit(self, ...):
    ...
```

### 3.4 Caching Strategy

**When to Cache (Tradeoff Analysis):**

| Data | Cache? | TTL | Reason |
|------|--------|-----|--------|
| Short URL metadata (code→URL) | ✅ Yes | 1 hour | Frequently accessed; mostly immutable |
| User profile (user_id→name) | ✅ Yes | 30 min | Accessed on every event log; changes rarely |
| Visit count aggregates | ⚠️ Maybe | Real-time | Evaluator needs accuracy; cache stale for display only |
| List endpoints (pagination) | ❌ No | - | Changes with each request; hard to invalidate |

**Implementation (Redis Optional):**

```python
# If Redis available:
# backend/app/config/cache.py
import redis
from typing import Any, Optional

class CacheService:
    def __init__(self, redis_url: str = None):
        if redis_url:
            self.redis = redis.from_url(redis_url)
        else:
            self.redis = None  # Disabled, fallback to DB
    
    def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None
        import json
        data = self.redis.get(key)
        return json.loads(data) if data else None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        if not self.redis:
            return
        import json
        self.redis.setex(key, ttl_seconds, json.dumps(value))
    
    def delete(self, key: str):
        if self.redis:
            self.redis.delete(key)

# Usage in service:
class URLShortenerService:
    def __init__(self, config, cache_service: CacheService = None):
        self.cache = cache_service or CacheService()
    
    def get_short_url(self, code: str) -> Optional[ShortURL]:
        # Try cache first
        cache_key = f"url:{code}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached  # Reconstruct from dict if needed
        
        # Fallback to DB
        url = self.url_repo.find_by_code(code)
        if url:
            self.cache.set(cache_key, url_to_dict(url), ttl_seconds=3600)
        
        return url
    
    def invalidate_url_cache(self, code: str):
        self.cache.delete(f"url:{code}")
```

**Redis Deployment:**
- For MLH hackathon: Optional (docker-compose can add redis service)
- For production: Highly recommended
- Fallback: Always works without Redis (degrades to DB queries)

### 3.5 Observability & Monitoring

**Three Pillars:**

#### **Pillar 1: Structured Logging**

✅ Already implemented middleware:

```python
# Before request: Attach request_id to g
# After request: Log with duration
# Format: timestamp level logger request_id message

# Output example:
# 2026-04-04T10:30:45.123Z INFO backend.routes request_id=550e8400 POST /api/v1/urls -> 201 (45ms)
```

Enhance with Sentry integration:

```python
# backend/app/config/sentry.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

def init_sentry(app):
    sentry_sdk.init(
        dsn=app.config.get('SENTRY_DSN'),
        integrations=[
            FlaskIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
        ],
        traces_sample_rate=0.1,  # 10% of requests
        environment=app.config.get('FLASK_ENV')
    )

# In app factory:
if app.config.get('SENTRY_DSN'):
    from backend.app.config.sentry import init_sentry
    init_sentry(app)
```

Enrichment in controllers:

```python
with sentry_sdk.push_scope() as scope:
    scope.set_tag("operation", "create_short_url")
    scope.set_context("user", {"ip": request.remote_addr})
    scope.set_context("request", {"path": request.path, "method": request.method})
    # ... handle request
```

#### **Pillar 2: Metrics (Prometheus)**

✅ Already set up: Prometheus scrapes @ 15s intervals.

Add application metrics:

```python
# backend/app/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Counters
url_created_total = Counter(
    'urls_created_total',
    'Total URLs created',
    labelnames=['status']
)
url_visited_total = Counter(
    'urls_visited_total',
    'Total visits',
    labelnames=['short_code']
)

# Histograms (latency buckets)
request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    labelnames=['method', 'endpoint', 'status'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

# Gauges (current state)
db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Current DB connection pool size'
)

# In middleware:
request_latency.labels(
    method=request.method,
    endpoint=request.endpoint,
    status=response.status_code
).observe((time.perf_counter() - g.request_started_at))
```

Expose metrics endpoint:

```python
# In app/__init__.py
from prometheus_client import generate_latest, REGISTRY

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}
```

#### **Pillar 3: Dashboards (Grafana)**

✅ Already configured (monitoring/grafana/).

Key dashboards:

1. **System Health**
   - Request rate (reqs/sec)
   - P50/P95/P99 latencies
   - Error rate (%)
   - DB connection pool utilization

2. **Business Metrics**
   - URLs created (daily trend)
   - Total visits
   - Top 10 short codes by visits
   - Average redirect latency

3. **Error Tracking**
   - Error rate by type (400, 404, 500)
   - Error rate by endpoint
   - Sentry critical alerts

---

## 4. SCALE & RELIABILITY

### Load Estimation

**Assumptions (Hackathon):**
- Peak traffic: 100-500 concurrent users
- Request mix: 40% POST (create), 60% GET (redirect/read)
- Peak QPS: ~200 req/sec
- Average response time: 50-100ms

**Capacity Planning:**

```
Flask worker processes: 4 (gunicorn on 4-core CPU)
Requests per worker/sec: 50
Total capacity: 4 × 50 = 200 req/sec ✅ Sufficient

DB connections: 20 (from config)
Connections per request: 1-2
Max concurrent requests: 20/2 = 10 (safe)
Scaling: If needed, use Docker Compose →scale: 2 instances + Nginx round-robin
```

### High Availability

**Database:**
- ✅ Single PostgreSQL instance (acceptable for hackathon)
- For production: Add read replicas, configure failover

**Application:**
- ✅ Docker Compose can run 2+ instances behind Nginx
- Nginx health check: `/ready` endpoint (pings DB)
- Automatic removal of unhealthy instances

**Nginx Configuration:**
```nginx
upstream app {
    server app1:5000 max_fails=3 fail_timeout=10s;
    server app2:5000 max_fails=3 fail_timeout=10s;
    keepalive 32;
}

server {
    location / {
        proxy_pass http://app;
        proxy_set_header X-Request-Id $http_x_request_id;
        proxy_connect_timeout 5s;
        proxy_read_timeout 10s;
    }
}
```

### Circuit Breaker Pattern (Polly-like)

For external calls (Sentry, Redis):

```python
# backend/app/utils/resilience.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_sentry(operation):
    try:
        sentry_sdk.capture_exception(...)
    except SentryException:
        # If Sentry is down, don't crash the app
        app.logger.warning("Sentry is down, continuing without error tracking")

# Usage:
call_sentry(exception)
```

### Alerting Rules

```yaml
# monitoring/prometheus/alerts.yml
groups:
  - name: backend_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        annotations:
          summary: "Error rate > 5% for 2+ minutes"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
        for: 5m
        annotations:
          summary: "P95 latency > 500ms"
      
      - alert: DatabaseDown
        expr: pg_up == 0
        for: 1m
        annotations:
          summary: "Database unreachable"
```

---

## 5. TRADE-OFF ANALYSIS

### Architecture Decisions

| Decision | Pros | Cons | Chosen? |
|----------|------|------|---------|
| **MVC (Model-View-Controller)** | Clear separation; testable | Extra layers; more files | ✅ YES |
| **Repository Pattern** | Decouples persistence; mockable | Slight overhead for simple CRUD | ✅ YES |
| **Dependency Injection** | Flexible testing; loose coupling | Boilerplate; small perf cost | ✅ YES |
| **Sentry Integration** | Captures all errors; alerts | External dependency; cost | ✅ YES (Free tier sufficient) |
| **Redis Caching** | 100x faster lookups | Extra infra; invalidation complexity | ⏳ OPTIONAL (implement after Phase 1-3) |
| **Queue (RabbitMQ/Celery)** | Async processing; resilience | Adds complexity; needs monitoring | ❌ NO (Not needed for hackathon scale) |

### Complexity vs. Benefit

```
High Benefit ──────────────────────> Low Benefit
      │
      │ Controllers (MUST)
      │ Repositories (MUST)
      │ Pydantic Validation (HIGH)
      │ Sentry Integration (HIGH)
      │ Rate Limiting (MEDIUM)
      │ Redis Cache (LOW)
      │ Async Jobs (LOW)
      │
Low Complexity
```

### Security Considerations

| Concern | Mitigation | Implementation |
|---------|-----------|-----------------|
| **SQL Injection** | Use ORM (Peewee) | ✅ Already using Peewee |
| **Rate Limiting** | Throttle endpoints | Implement via middleware or nginx |
| **Authentication** | Not needed for hackathon | Skip unless evaluator requires |
| **CORS** | Restrict origins | Nginx config or Flask-CORS |
| **Input Validation** | Pydantic schemas | Implement in Phase 3 |
| **XSS / CSRF** | Not applicable (API-only) | - |

---

## 6. IMPLEMENTATION ROADMAP (Integrated with Backend Audit)

### Phase 1: Add Controller Layer (1-2 hours)
**Deliverables:**
- BaseController with error handling
- URLController with create/read/update/delete methods
- Update routes to delegate to controllers
- Test that existing endpoints still work

### Phase 2: Add Repository Pattern (1-2 hours)
**Deliverables:**
- BaseRepository (CRUD interface)
- URLRepository, EventRepository specializations
- Update services to inject repositories
- Unit test fixtures for mocking repositories

### Phase 3: Pydantic Schema Validation (1-2 hours)
**Deliverables:**
- Request schemas (CreateURLSchema, UpdateURLSchema, etc.)
- Response schemas (URLResponseSchema, EventResponseSchema, etc.)
- Validate all endpoints
- Document request/response examples

### Phase 4: Sentry Integration (30 mins)
**Deliverables:**
- Configure Sentry DSN in env
- Initialize Sentry in app factory
- Capture errors in controllers (context enrichment)
- Verify errors appear in Sentry dashboard

### Phase 5: Prometheus Metrics (1 hour)
**Deliverables:**
- Add counters (URLs created, visits)
- Add histograms (request latency)
- Export `/metrics` endpoint
- Verify Prometheus scrapes successfully

### Phase 6: Implement 18 Missing Endpoints (4-6 hours) ⏳ BLOCKER
**Deliverables:**
- Users CRUD (POST /users, GET /users, GET /users/<id>, PUT /users/<id>)
- Users bulk import (POST /users/bulk)
- Events list (GET /events)
- Full URLs endpoints (GET /urls, GET /urls/<id>, PUT /urls/<id>, DELETE /urls/<id>)
- Paginated responses
- Pass MLH evaluator tests

---

## 7. MONITORING CHECKLIST

After deployment, verify:

- [ ] Prometheus scrapes app @ 15s intervals
- [ ] Grafana dashboard shows request latency, error rate, database connections
- [ ] Sentry receives errors (test by triggering 500 error)
- [ ] AlertManager configured to fire on error rate > 5%
- [ ] Request IDs visible in logs and Sentry
- [ ] `/ready` endpoint returns 200 when healthy, 503 when DB down
- [ ] Rate limiting works (if implemented)

---

## 8. REVISIT POINTS (As Vybe Scales)

For production, revisit:

1. **Caching Strategy** → Add Redis for URL lookups (100x faster)
2. **Database** → Handle >10k QPS with read replicas + sharding by country
3. **Async Jobs** → Move event logging, analytics to Celery queue
4. **Authentication** → Add JWT tokens if multi-user features needed
5. **Rate Limiting** → Use Redis-backed sliding window counter
6. **Analytics Pipeline** → Stream events to BigQuery/Kafka for real-time dashboards
7. **Content Delivery** → Cache short URL redirects globally (CDN)

---

## Summary Table

| Aspect | Current | Recommended | Effort |
|--------|---------|------------|--------|
| **Architecture** | Routes → Services | Routes → Controllers → Services → Repositories | 2-3 hours |
| **Error Handling** | Manual | Controllers + Sentry | 30 min |
| **Validation** | Manual strings | Pydantic schemas | 1-2 hours |
| **Observability** | Logs only | Logs + Metrics + Sentry | 1.5 hours |
| **Testing** | Unit tests exist | Add controller/service fixtures | 1 hour |
| **API Completeness** | 6 endpoints | 18 endpoints (MLH spec) | 4-6 hours |
| **Caching** | None | Redis (optional) | 1-2 hours |
| **Security** | Basic | Rate limiting, CORS | 30 min |
| **Total Estimate** | - | **15-20 hours** | - |

