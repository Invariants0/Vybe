# System Architecture

The Vybe system is composed of five distinct layers that work together to create a reliable, observable URL shortening service. This architecture prioritizes operational visibility, fault tolerance, and horizontal scalability while maintaining simplicity at each layer.

The system design philosophy is straightforward: keep concerns separated, make failures visible, design for graceful degradation, and document every architectural decision. This document explains how each component works, how they interact, what happens when they fail, and how the system scales as demand grows.

---

## Architecture Philosophy

Vybe's architecture is built on five foundational principles:

**1. Layered Separation of Concerns**
Each layer (ingress, application, data, observability) has distinct responsibilities. The ingress layer handles routing. The application layer handles business logic. The data layer handles persistence. The observability layer handles visibility. Changes in one layer do not ripple through others.

**2. Explicit Over Implicit**
The codebase prioritizes clarity over cleverness. Every database query is visible (no magic ORMs). Every network call is observable. Every failure scenario is addressed. New team members can understand the system by reading code, not by reading developer tribal knowledge.

**3. Fail Observable, Not Silent**
Every component exposes metrics. Every error is logged. Every failure is both detectable and debuggable. The system is built assuming something will fail (because something always does). The question is not whether it will fail, but whether someone will know it failed.

**4. Graceful Degradation**
Optional components (Redis) do not block critical paths. If Redis is down, the system works (slower, but works). If one app instance crashes, traffic shifts to the other (50% capacity, but operational). If alerts misfire, humans can reason about the problem using logs.

**5. Horizontal First, Vertical Later**
The system is designed to scale by adding more instances of components, not by making existing instances larger. Add more app instances, not more CPU per instance. Add read replicas, not bigger database. This approach is simpler operationally and more cost-efficient at scale.

---

## Architecture Layers

Vybe follows a traditional layered architecture pattern with five distinct tiers:

**1. Ingress Layer (Nginx)** - All external traffic flows through a single reverse proxy that handles routing to appropriate backend services.

**2. Application Layer (Flask)** - Request processing, validation, and orchestration. Business logic lives here (but calls into service layer). Multiple instances run behind the ingress for redundancy and load distribution.

**3. Service Layer (Business Logic)** - URL creation, user management, event tracking. These services are stateless and call repositories for data access.

**4. Data Layer (PostgreSQL + Redis)** - Durable storage in PostgreSQL, optional hot-data caching in Redis. All state lives here.

**5. Observability Layer (Prometheus + Grafana + AlertManager)** - Metrics collection, visualization, and alerting. No business logic, purely visibility.

The key insight: each layer can fail or be replaced independently. If your database system changes, only the repository layer changes. If you need different ingress (Kubernetes ingress controller instead of Nginx), only the ingress layer changes. This separation makes the system maintainable.

## Component Overview

This section explains each component in detail: what it does, how it works, what happens when it fails, and when it becomes the bottleneck.

### Nginx (Reverse Proxy & Load Balancer)

**Purpose**

Nginx serves as the single entry point for all external traffic. Its job is to:
- Accept incoming HTTP/HTTPS connections on ports 80 and 443
- Route requests to appropriate backend services based on URL path
- Load balance requests across multiple app instances
- Collect HTTP metrics (response times, status codes)
- Handle SSL/TLS termination if HTTPS is configured
- Serve the frontend (Next.js) from a separate route

Nginx is stateless and fast. It does not store data, does not call databases, and does not perform business logic. Its sole responsibility is routing and load balancing.

**How It Works**

When a request arrives at Nginx:

```
1. Request arrives on port 80 or 443
2. Nginx reads the URL path
3. If path starts with /api/v1, route to Flask (round-robin between app instances)
4. If path is /, route to Next.js frontend
5. Add request tracing headers (X-Request-ID)
6. Forward request to selected backend
7. Collect response time and status code for metrics
8. Return response to client
```

All of this happens in milliseconds (typically <5ms added latency).

**Configuration**

Nginx is configured via `infra/nginx/nginx.conf`. Key settings:

- **Worker processes:** Auto (one per CPU core)
- **Max connections per worker:** 1024 (can be increased)
- **Keepalive:** Enabled (HTTP connections reused)
- **Upstream pool:** Two app instances (can add more)
- **Health check path:** /ready (used to detect unhealthy instances)

**Failure Mode**

If Nginx crashes or becomes unavailable:
- All external traffic is blocked (system completely unavailable)
- This is a SPOF (single point of failure)
- Recovery: The orchestrator (Kubernetes, Docker Swarm, systemd) restarts Nginx
- Prevention: Deploy multiple Nginx instances behind a cloud load balancer

**Cannot become a bottleneck** with current configuration because:
- Modern Nginx can handle 10,000+ RPS on modest hardware
- We're well below that for single instance deployments
- If you outgrow single Nginx, deploy multiple instances behind a cloud LB

**Scaling consideration:** When you have 4+ app instances, consider deploying 2-3 Nginx instances behind a cloud load balancer (AWS ELB, GCP Load Balancer, etc.).

### Flask Application (Port 5000)

**Purpose**

Flask instances are the brain of the system. Each instance:
- Listens for HTTP requests from Nginx
- Validates input (using Pydantic schemas)
- Orchestrates business logic by calling services
- Accesses data through the repository layer
- Returns responses to clients
- Exposes metrics for monitoring

Each Flask instance is stateless (except for connection pool and in-process caches). State lives only in PostgreSQL.

**Internal Architecture**

Within each Flask process, requests flow through layers:

```
HTTP Request (from Nginx)
        |
        v
    Route Handler (/api/v1/links)
        |
        v
   Controller Layer (links_controller.py)
        - Validate JSON schema with Pydantic
        - Check for required fields
        - Sanitize inputs
        - Catch validation errors early
        |
        v
   Service Layer (url_service.py)
        - Business logic (generate short code if not provided)
        - Check if custom alias already exists
        - Create link record
        - Record event if configured
        |
        v
   Repository Layer (url_repository.py)
        - Build SQL query via Peewee ORM
        - Check connection pool availability
        - Execute query against PostgreSQL
        - Convert database row to Python object
        |
        v
   Service Returns (to controller)
        |
        v
   Controller Formats Response
        - Convert service response to JSON
        - Add correlation headers
        - Set HTTP status code (201 Created, 400 Bad Request, etc.)
        |
        v
   HTTP Response (to Nginx)
```

Each layer has a specific responsibility:
- **Controllers:** HTTP parsing, validation, response formatting
- **Services:** Business logic, orchestration, state management
- **Repositories:** Data access, database-specific code

This layering makes testing easier (test each layer independently) and makes changes easier (change a service without touching controllers).

**Concurrency Model**

Each Flask instance runs with 2 Gunicorn workers (configurable via WORKERS env var). Each worker:
- Runs Python code synchronously (not async/await)
- Handles one request at a time
- Blocks if database is slow
- Can queue requests (depends on Nginx)

With 2 instances and 2 workers each = 4 total parallel request handlers. This can handle:
- ~500 requests per second if each request takes 10ms
- ~50 requests per second if each request takes 200ms (typical with database round-trip)

**Connection Pool**

Each instance manages a pool of database connections (default 20). When a request needs to query the database:

```
1. Request arrives at service layer
2. Service calls repository method
3. Repository checks connection pool availability
4. If pool has free connection: grab it, execute query
5. If pool is full: wait up to 10 seconds for a connection to free up
6. After query: return connection to pool for reuse
```

Connections are expensive (they use memory and system resources), so pooling is critical. If you add too many app instances without increasing the database max_connections, the pool will exhaust and requests will wait or timeout.

**Memory**

Each worker process uses approximately:
- Base Python runtime: 80MB
- Flask + dependencies: 60MB
- Request-specific data: 10-50MB (depends on request)
- Cache data (in-process): if you maintain caches, they grow memory usage

Total per worker: 150-200MB typical. With 2 workers per instance = 300-400MB per instance.

**Metrics Exposed**

Each Flask instance exposes Prometheus metrics on port 8000 (internal, not accessible via Nginx):

```
/metrics endpoint

requests_total{method="POST",path="/api/v1/links",status="201"} 1000
request_latency_seconds_bucket{le="0.1"} 850
request_latency_seconds_bucket{le="1.0"} 990
request_latency_seconds_bucket{le="+Inf"} 1000
database_pool_current_size 15
database_pool_max_size 20
```

These metrics are scraped by Prometheus every 15 seconds and stored for trending, alerting, and debugging.

**Failure Mode**

If one Flask instance crashes:
- Nginx detects it via /ready health check (within 30 seconds max)
- Nginx stops routing new requests to it
- Existing requests on that instance are lost (client sees connection error)
- All new traffic routes to the healthy instance
- System operates at 50% capacity but remains operational

Recovery:
- Container orchestrator restarts the crashed instance
- After startup (90 seconds), Nginx routes traffic to it again
- System back to full capacity

Prevention:
- Monitor error rates and latency
- Review logs for memory leaks or crashes
- Test new code locally before deploying

**Scaling**

As traffic grows:
- 100 RPS: 1 instance sufficient
- 500 RPS: 2 instances
- 1000 RPS: 4 instances
- 2000 RPS: 8 instances

Add instances by updating docker-compose.yml (add vybe_app3, vybe_app4, etc.) or Kubernetes deployment replicas. Nginx automatically discovers new instances.

### PostgreSQL (Port 5432)

**Purpose**

PostgreSQL is the source of truth. It stores:
- All user accounts and their metadata
- All shortened links and their targets
- All visit events (clicks on links)
- Timestamps, configurations, soft-delete flags

Every piece of application state lives in PostgreSQL. If it's not in the database, it doesn't exist (even if it's in memory elsewhere, it's temporary).

**Schema**

Three main tables:

```sql
users (id, created_at, updated_at)
  - User accounts

urls (id, code, original_url, user_id, is_active, created_at, updated_at,
      expires_at, last_accessed_at)
  - Short links with metadata

events (id, url_id, timestamp, user_agent, referrer, ip_address)
  - Analytics (click tracking)
```

Critical indexes:

```sql
CREATE INDEX idx_urls_code ON urls(code);           -- Fast lookup by short code
CREATE INDEX idx_urls_user_id ON urls(user_id);     -- Fast lookup by user
CREATE INDEX idx_events_url_id ON events(url_id);   -- Fast lookup of visits per link
CREATE INDEX idx_events_timestamp ON events(timestamp);  -- Analytics queries
```

Without these indexes, queries slow as table grows.

**Connection Pool**

Each Flask instance holds up to 20 database connections (configurable). Why pooling?

- Opening a connection is expensive (network round-trip, authentication, initialization)
- Reusing connections is efficient (already open, ready to query)
- Maximum pool size prevents database from resource exhaustion (connection states use memory)

With 2 app instances = 40 concurrent connections possible. PostgreSQL default allows 100 total, so headroom exists for monitoring and manual queries.

**Query Performance**

Typical query times with indexes:

- GET by short code: 1-5ms (index lookup)
- INSERT new link: 2-10ms (insert + index update)
- GET visit history: 50-200ms (scan events table, depends on volume)
- UPDATE link (deactivate): 2-5ms

Slow queries (>100ms) indicate:
- Missing index (most common)
- Table scan (query not using index)
- Slow disk (rare on modern hardware)
- Concurrent lock contention (multiple writers)

**Storage**

Current capacity:
- 100 million short links: ~10GB (100 bytes per row)
- 10 billion visit events: ~500GB (50 bytes per row)

With current setup:
- Storage: 100GB volume attached to container (can grow to 1TB)
- Actually used: ~5GB for typical deployments

If you approach storage limit:
1. Increase volume size (cloud provider simple, 30 second operation)
2. Archive old data (move events older than 1 year to cold storage)
3. Delete old data (if not needed for compliance)

**Failure Mode**

If PostgreSQL becomes unavailable:
- Flask /ready endpoint returns 503
- Nginx marking all instances as unhealthy
- All requests return 503 Service Unavailable
- System completely stopped

This is the most critical component. Its failure is a system-wide outage.

Recovery options:
1. If temporary (crashed container): Restart it (30 seconds)
2. If corruption: Restore from backup (~5-30 minutes depending on size)
3. If hardware failure (rare): Failover to read replica (if configured, <1 second)

Backup strategy (production):
- Automated daily backups to cloud storage
- Backup tested weekly (actually restore and verify)
- RTO (Recovery Time Objective): 30 minutes (how long to restore)
- RPO (Recovery Point Objective): 24 hours (data loss if restored from yesterday's backup)

**Scaling**

Single PostgreSQL can typically handle:
- 100 million records
- 1000 read queries per second
- 100 write queries per second

Beyond that:
- Use read replicas for read-heavy load (Vybe is read-heavy)
- Shard by user_id or code prefix (complex, expensive)
- Switch to specialized solution (Spanner, CockroachDB)

Current deployment (single instance) is sufficient up to 500 concurrent app instances.

### Redis (Port 6379, Optional)

**Purpose**

Redis is an optional cache for frequently accessed data. Its job is to:
- Reduce load on PostgreSQL by serving hot data from memory
- Serve cached data in <1ms instead of 50ms database round-trip
- Reduce database CPU usage
- Improve P95 latency for common queries

It is NOT required (system works without it), but strongly recommended for >500 RPS.

**Cache Strategy**

Vybe uses Redis for:
- Recently accessed link targets (most redirects are repeat visitors)
- User profile data (fetched frequently)
- Popular short codes (if any)

Cache invalidation:
- TTL-based: Keys expire after 300 seconds by default
- Event-based: When you update a link, we delete the cache key immediately
- Full-cache clear: FLUSHALL command (if needed during debugging)

**Memory**

Redis stores the entire dataset in memory. Key question: how much memory needed?

- Cache hit rate: 70-80% typical
- Dataset size: If 1% of links are "hot" (frequently accessed)
  - 100M links * 0.01 = 1M hot links
  - 500 bytes per link cached = 500MB
  - With keys and metadata overhead: ~1GB

With default 512MB Redis limit:
- Can cache ~10M frequently accessed links
- If dataset grows beyond memory, eviction policy kicks in (LRU by default)

**Failure Mode**

If Redis becomes unavailable:
- Application detects connection error
- Falls back to database query
- Request succeeds but slower (~200ms instead of <1ms)
- No system outage, just degraded performance

This is the design: Redis is optional insurance, not critical path.

Recovery:
- Restart Redis: ~3 seconds
- Reconnect happens automatically (with backoff)
- Performance returns to normal as cache repopulates

**Scaling**

Single Redis instance handles:
- 100,000+ operations per second
- Terabytes of data (in theory)

Never the bottleneck in this architecture (unless you misconfigure it).

### Frontend (Next.js)

**Purpose**

The frontend is a web application that:
- Provides user interface for creating/sharing links
- Makes API calls to Flask backend
- Displays analytics
- Handles user authentication (future)

Built with Next.js 15 + React 19 + TypeScript.

**How it interacts with backend**

```
User visits http://localhost:8080
  |
  v
Nginx receives request, routes to Next.js (port 3000)
  |
  v
Next.js renders HTML + JavaScript
  |
  v
Browser executes JavaScript
  |
  v
User creates a link (clicks button)
  |
  v
JavaScript calls API: POST /api/v1/links (to Flask via Nginx)
  |
  v
Flask processes request, returns JSON
  |
  v
JavaScript displays result to user
```

**Failure Mode**

If frontend (Next.js) crashes:
- Nginx detects it (health check)
- Static pages still available
- API still works (in separate backend)
- Users can still use command-line API

Frontend failure != system failure. Backend continues operating normally.

---

## Data Flow

### Creating a Short Link (POST /api/v1/links)

This walkthrough shows the exact flow from user request to database update:

```
1. USER ACTION
   User submits form: URL="https://example.com", Alias="demo"

2. BROWSER
   JavaScript builds JSON request
   POST /api/v1/links
   Content-Type: application/json
   {
     "url": "https://example.com",
     "custom_alias": "demo"
   }

3. NGINX (INGRESS)
   - Receives request on port 8080
   - Parses URL path /api/v1/links
   - Selects Flask instance (Round-robin) - Flask instance 1
   - Adds X-Request-ID header: "req-abc123def456"
   - Forwards request to Flask:5000

4. FLASK CONTROLLER (links_controller.py)
   - Receives request with request ID
   - Validates JSON format (valid JSON? yes)
   - Uses Pydantic schema to validate fields:
     * url: is it a valid URL? yes
     * custom_alias: is it valid format? yes (alphanumeric + hyphens)
   - Extracts fields: url, custom_alias
   - Calls service layer

5. FLASK SERVICE (url_service.py)
   - Receives: url="https://example.com", custom_alias="demo"
   - Queries repository: "Is alias 'demo' already in use?"
   - Repository returns: Yes, it's taken (from database)
   - Service raises ValidationError (alias conflict)
   - Controller catches error, returns 409 Conflict response

ALTERNATIVE SCENARIO (if alias not taken):
   - Service generates short code = "demo" (from custom_alias)
   - Service calls repository.create_url(...)
   - Repository builds SQL: INSERT INTO urls (code, original_url...) VALUES(...)
   - Repository acquires database connection from pool
   - Sends INSERT to PostgreSQL
   - PostgreSQL inserts row, updates index on (code) column
   - PostgreSQL returns: insert_id=5, success=true
   - Repository returns URL object to service
   - Service returns URL to controller
   - Controller converts to JSON, sets status 201 Created
   - Response travels back through Nginx to browser

6. NGINX (RESPONSE)
   - Receives 201 response from Flask
   - Collects metrics (time=45ms, status=201)
   - Records to logs
   - Forwards response to client
   - Browser receives JSON with new short link

7. USER SEES
   Success message with short link: http://localhost:8080/demo
```

Key points:
- Request ID "req-abc123def456" exists in logs at every step (for debugging)
- Connection to database is acquired and released (pooling)
- All errors are caught early (validation before database)
- Metrics are automatically collected (Nginx + Flask)

### Redirecting Through a Link (GET /{code})

```
1. USER ACTION
   User clicks link: http://localhost:8080/demo

2. NGINX
   - Path doesn't start with /api, but it's also not root (/)
   - Flask has route for /demo
   - Routes to Flask

3. FLASK ROUTE HANDLER (links_routes.py)
   - Matches pattern: GET /{code}
   - Calls redirect handler
   - Extracts code="demo"

4. FLASK SERVICE
   - Queries repository: "Find URL with code='demo'"
   - Checks Redis cache first (if enabled)
     * Cache lookup: key="url:demo"
     * Cache miss (first time)
   - Falls back to database

5. REPOSITORY LAYER
   - Acquires database connection
   - Executes: SELECT original_url FROM urls WHERE code='demo'
   - Query uses index on (code) column (fast, <3ms)
   - Returns: {original_url: "https://example.com", is_active: true, ...}

6. SERVICE LAYER
   - Checks link is active and not expired
   - (If enabled) Stores in Redis cache with TTL=300 seconds
   - Records visit event (sampled by EVENT_LOG_SAMPLE_RATE)

7. FLASK RETURNS
   - HTTP 302 Found
   - Location: https://example.com

8. BROWSER
   - Automatically follows redirect
   - Visits https://example.com

Total time: <50ms typical (database + Flask overhead)
If cached: <2ms (memory lookup + return)
```

### Analytics Query (GET /api/v1/links/{code}/visits)

```
1. User requests: GET /api/v1/links/demo/visits

2. Flask routes to visits handler

3. Service layer:
   - Validates code exists
   - Queries repository for recent events

4. Repository:
   - SELECT * FROM events WHERE url_id={id} ORDER BY timestamp DESC LIMIT 25
   - Uses index on (url_id) column
   - Returns 25 most recent visit rows

5. Time varies:
   - 10 visits: <5ms
   - 1000 visits: <50ms
   - 1M visits: 200-500ms (table scan slower even with index)

6. Response is not cached
   - Analytics should be fresh
   - Every query hits database
```

---

## Error Handling

All errors flow through a consistent error handling pattern:

**Application Layer** (Flask)

```python
try:
    service.create_url(url, alias)
except ValidationError as e:
    return {"error": "validation_error", "message": str(e)} , 400
except DatabaseError as e:
    log.error(f"Database error: {e}", request_id=request_id)
    return {"error": "database_error", "message": "DB temporarily unavailable"}, 503
except Exception as e:
    log.error(f"Unhandled error: {e}", request_id=request_id, traceback=traceback.format_exc())
    return {"error": "internal_error", "message": "Something went wrong"}, 500
```

**Database Layer** (Peewee)

```python
def create_url(self, url, alias):
    try:
        return URLs.create(code=alias, original_url=url)
    except IntegrityError:  # Unique constraint violated
        raise ValidationError(f"Alias {alias} already exists")
    except OperationalError:  # Connection failed
        raise DatabaseConnectionError("Cannot reach database")
```

**Error Response Format**

```json
{
  "error": "validation_error",
  "message": "Invalid URL format",
  "request_id": "req-abc123def456",
  "details": {
    "field": "url",
    "reason": "must start with http:// or https://"
  }
}
```

Request ID is critical for debugging. When user reports error, you search logs:
```bash
grep "req-abc123def456" app.log | head -50
```

All related logs appear together.

---

## Observability Architecture

### Metrics Collection

Every component exposes metrics:

**Application Metrics** (Flask)

```
- Requests: Total count, by method/path/status
- Latency: Request duration in seconds (histogram)
- Database: Connection pool size, query times
- Cache: Hit/miss rates (if Redis enabled)
```

**Infrastructure Metrics** (Docker + Host)

```
- CPU: Percent utilization per container
- Memory: Bytes used / bytes available
- Disk: Free space on mounted volumes
- Network: Bytes sent/received
```

**Database Metrics** (PostgreSQL)

```
- Connections: Active, idle, total
- Queries: Count, duration, slow query log
- Transactions: Active, deadlocks
- Indexes: Usage, cache hit rates
```

**Cache Metrics** (Redis)

```
- Operations: Total GET/SET/DELETE operations
- Hit rate: Cache hits / (hits + misses)
- Memory: Used / max configured
- Evictions: How many keys removed due to memory limit
```

### Dashboards (Grafana)

Pre-built dashboards display these metrics visually:

**Overview Dashboard**
- Traffic volume (requests per second)
- Error rate (5xx errors)
- P95 latency
- Component health status

**Application Dashboard**
- Request latency percentiles (P50, P95, P99)
- Requests by endpoint
- Error rate by status code
- Database connection pool usage

**Database Dashboard**
- Query count and duration
- Connection count
- Transactions and deadlocks
- Slow queries (queries >100ms)

**Infrastructure Dashboard**
- CPU usage per instance
- Memory usage per instance
- Disk I/O and free space
- Network traffic

### Alerting (AlertManager)

When metrics cross thresholds, alerts fire:

**Critical Alerts** (wake up team)
- Instance down: Service unreachable
- Database down: No database connection
- High error rate: >5% of requests are 5xx errors

**Warning Alerts** (notify but not urgent)
- High latency: P95 >1 second
- High CPU: >80% sustained
- Low disk space: <10GB free
- Memory pressure: >85% of limit

Each alert includes:
- What happened (alert name)
- Why it happened (metric value)
- Which service is affected
- Link to runbook for investigation

---

## Scaling Boundaries

### Current Deployment (Single Instance)

| Component | Current Capacity | How to Detect Limit | Fix |
|-----------|-----------------|-------------------|-----|
| Nginx | >10,000 RPS | CPU >90%, dropped connections | Add LB + multiple Nginx |
| Flask | 500-1000 RPS per instance | Latency spike + CPU >80% | Add more instances |
| PostgreSQL | 1000+ RPS (read heavy) | Connection pool full | Enable caching, add replicas |
| Redis | 100,000+ ops/sec | Memory >80%, evictions | Larger instance or cluster |
| Disk | 100GB volume | df shows >90% usage | Increase volume size |

### Step-by-Step Scaling

**At 500 RPS** (Current state)
- 2 Flask instances
- No Redis
- Single PostgreSQL
- Single Nginx
- Works fine

**At 2000 RPS** (Requires upgrade)
- 4-5 Flask instances
- Enable Redis caching
- PostgreSQL with 1-2 read replicas
- 2-3 Nginx instances behind cloud LB
- Dedicated monitoring server

**At 10000 RPS** (Requires architecture change)
- 15-20 Flask instances
- Redis cluster (if needed)
- PostgreSQL with sharding
- Kubernetes orchestration
- Multi-region deployment

### Bottleneck Migration

As you scale, bottleneck shifts:

1. First: Application CPU (add app instances)
2. Second: Database connection pool (add RO replicas)
3. Third: Database CPU (enable caching more aggressively)
4. Fourth: Database I/O (shard or use different database)

Never fix the wrong bottleneck. Always measure first.

---

## Next Steps

- For deployment details, see [deploy.md](deploy.md)
- For troubleshooting, see [troubleshooting.md](troubleshooting.md)
- For scaling, see [capacity-plan.md](capacity-plan.md)
- For technical decisions, see [decision-log.md](decision-log.md)

**Purpose:** Accept external traffic, route to application instances, serve frontend, and collect HTTP metrics.

**Key Characteristics:**
- Listens on ports 80/443 (external-facing)
- Routes `/api/v1/*` to Flask instances (round-robin load balancing)
- Routes `/` to Next.js frontend
- Exposes `localhost:8000` for Prometheus metrics
- Logs every request in JSON format with upstream response times
- Handles SSL/TLS termination (if configured)

**Failure Mode:** If Nginx fails, external traffic cannot reach any backend service. Health check: curl `http://localhost:8080/health` returns 200 immediately if Nginx is responding.

**Scaling Consideration:** Nginx can handle thousands of concurrent connections. Not typically the bottleneck. If it becomes the bottleneck, deploy multiple Nginx instances behind a DNS load balancer or cloud load balancer.

### Flask Application (Port 5000)

**Purpose:** HTTP API handler, request validation, business logic orchestration, and database interaction.

**Architecture:**
```
HTTP Request
    |
    v
Router (routes/)
    |
    v
Controller (controllers/) - Validate input, call services
    |
    v
Service (services/) - Business logic, orchestration
    |
    v
Repository (repositories/) - Data access
    |
    v
Database
```

**Key Modules:**

- **Controllers** - HTTP layer, input validation via Pydantic schemas, response formatting
- **Services** - Business logic (URL creation, user management, analytics)
- **Repositories** - Data access abstraction, SQL query generation via Peewee
- **Models** - ORM definitions matching database schema
- **Validators** - Pydantic request/response schemas
- **Middleware** - Request ID injection, JSON logging, error handling
- **Utils** - Helper functions (URL normalization, caching, codec operations)

**Horizontal Scaling:** Two Flask instances run simultaneously, each with independent Gunicorn workers (configurable). Add more instances by increasing replicas in docker-compose.yml or Kubernetes deployment.

**Connection Management:** Each Flask instance maintains a connection pool to PostgreSQL (max 20 connections by default). Pool is shared across Gunicorn workers within that instance.

**Failure Mode:** If one Flask instance crashes, Nginx immediately detects via health check and routes to the other. System continues with 50% capacity.

### PostgreSQL (Port 5432)

**Purpose:** Durable storage for all application data (links, users, events).

**Key Characteristics:**
- Runs in separate container with persistent volume
- Database name: `hackathon_db` (configurable)
- Supports 20 concurrent connections per Flask instance
- Handles connection pooling via Peewee ORM
- Logs slow queries (log_min_duration_statement if configured)

**Schema:**
- `users` table - User accounts
- `urls` table - Short links with metadata
- `events` table - Analytics (click tracking, timestamps)
- Indexes on frequently queried columns (short_code, user_id, created_at)

**Connection Pool Behavior:**
- Each Flask instance reserves up to 20 connections
- With 2 app instances = 40 total connections possible
- Pool timeout: 10 seconds (configurable)
- Stale connection timeout: 300 seconds (configurable)

**Failure Mode:** If PostgreSQL becomes unavailable:
- Flask `/ready` endpoint returns 503
- Nginx health check catches this, marks instance unhealthy
- Load balancer removes unhealthy instance from rotation
- Existing requests fail with database error
- System is down until PostgreSQL recovers (see runbooks)

**Disaster Recovery:** Use PostgreSQL backup/restore procedures (document in separate runbook). No hot standby configured yet.

### Redis (Port 6379, Optional)

**Purpose:** Distributed cache for high-frequency queries. System works without it (graceful degradation).

**Key Characteristics:**
- Optional (controlled by REDIS_ENABLED environment flag)
- Default TTL: 300 seconds (5 minutes)
- Password protected (REDIS_PASSWORD env var)
- Runs with AOF persistence enabled (data survives container restarts)

**Cache Strategy:**
- Recent visits cached per link
- User profile data cached
- Popular short codes cached
- On cache miss, falls back to database query immediately

**Failure Mode:** If Redis becomes unavailable:
- Application catches connection errors gracefully
- Queries fall back to database
- Performance is degraded but system remains operational
- No cascading failures

**Scaling Consideration:** Single Redis instance can handle millions of operations per second. For very high-throughput scenarios, consider Redis Cluster (not yet implemented).

---

## Data Flow

### Creating a Short Link

```
1. User submits POST /api/v1/links with URL and optional alias
2. Nginx routes request to Flask instance 1 or 2
3. Flask controller validates input via Pydantic schema
4. Service layer generates short code (if no custom alias)
5. Service creates URL record and user association
6. Repository writes to PostgreSQL
7. PostgreSQL returns inserted record with ID
8. Service invalidates Redis cache (if enabled)
9. Flask returns URL record as JSON response
10. Nginx forwards response to user
```

### Redirecting Through Short Link

```
1. User/bot accesses GET /{short_code}
2. Nginx routes to Flask
3. Service queries PostgreSQL for URL record
4. (If Redis enabled and cache hit) - return from cache (fast)
5. (If Redis miss) - query database, cache result
6. Service records visit event to events table (sampled per EVENT_LOG_SAMPLE_RATE)
7. Flask returns 302 redirect to original URL
8. User's browser follows redirect to original URL
```

### Analytics Query

```
1. User requests GET /api/v1/links/{code}/visits
2. Flask queries events table filtered by short_code
3. PostgreSQL scans events table (index on short_code speeds this up)
4. Results returned and formatted in response
5. No caching (analytics should be fresh)
```

---

## Error Handling

### Application Layer Errors

All errors follow a consistent format:

```json
{
  "error": "validation_error",
  "message": "Invalid URL format",
  "details": {
    "field": "url",
    "reason": "must start with http:// or https://"
  },
  "request_id": "req-abc123def456"
}
```

Request ID allows tracing through all logs if error investigation needed.

### Database Errors

Connection errors are caught in repository layer and converted to application errors:

```python
try:
    result = db.execute_sql(query)
except PostgresqlError as e:
    log.error(f"Database error: {e}", request_id=request_id)
    raise DatabaseConnectionError("Database temporarily unavailable")
```

### External Service Errors

Redis failures do not cause application failures:

```python
try:
    cached = redis.get(key)
except RedisError as e:
    log.warning(f"Redis error: {e}, falling back to DB")
    cached = None
```

---

## Observability Architecture

### Metrics (Prometheus)

All components expose metrics on port 8000:

- **Application Metrics** - Request count, latency (p50/p95/p99), error rate
- **Database Metrics** - Connection pool usage, query latency, connection errors
- **Infrastructure Metrics** - CPU, memory, disk I/O per container
- **Cache Metrics** - Hit rate, evictions, memory usage

**Prometheus Configuration:**
- Scrapes every 15 seconds
- Retention: 15 days by default
- Storage: ~1GB per week depending on load
- Alerting rules evaluated every 30 seconds

### Logging (JSON to stdout)

All application logs are JSON structured for easy parsing:

```json
{
  "timestamp": "2026-04-05T10:30:45.123Z",
  "level": "INFO",
  "service": "vybe_app",
  "request_id": "req-abc123def456",
  "path": "/api/v1/links",
  "method": "POST",
  "status": 201,
  "duration_ms": 45,
  "message": "Link created successfully"
}
```

Docker captures logs and can forward to centralized logging system (ELK, Datadog, etc.).

### Dashboards (Grafana)

Pre-built dashboards display:

- **Overview** - Health status of all components
- **Application** - Request rate, latency, error rate
- **Database** - Connection pool usage, query times
- **Infrastructure** - CPU, memory, network per container
- **Cache** - Hit rates, evictions (if Redis enabled)

### Alerts (AlertManager)

Critical alerts trigger webhooks:

- **InstanceDown** - Application instance unreachable
- **DatabaseDown** - PostgreSQL connection failures
- **HighErrorRate** - Error rate exceeds threshold (configurable)
- **HighLatency** - P95 response time exceeds threshold
- **RedisDown** - Cache unavailable (warning only, not critical)

Each alert includes:
- Alert name
- Affected instance
- Detection time
- Link to relevant runbook

---

## Scaling Boundaries

### Current Limits (Single Deployment)

| Component | Limit | Throttling | Scaling Strategy |
|-----------|-------|-----------|------------------|
| Nginx | >10k RPS | CPU bottleneck | Add reverse proxy instances behind DNS LB |
| Flask (2 instances) | ~5k RPS per instance | CPU at 100% | Increase Gunicorn worker count, add app instances |
| PostgreSQL | ~10k RPS (read heavy) | Connection pool exhaustion | Increase pool size, add replicas, enable caching |
| Redis | >100k ops/sec | Memory if Dataset large | Switch to cluster, enable eviction policies |
| Disk I/O | ~500 MB/s | I/O bottleneck | Use faster storage (SSD), enable caching |

### Horizontal Scaling

To scale horizontally:

1. **Add Flask instances** - Deploy new app instances, register with load balancer
2. **Add Nginx replicas** - Deploy behind cloud load balancer or DNS failover
3. **Increase Gunicorn workers** - WORKERS environment variable controls concurrency per instance
4. **Database replicas** - For read-heavy workloads, add read replicas (not yet configured)

### Vertical Scaling (When Horizontal Hits Limits)

1. **Increase Flask container resources** - More CPU, more RAM for larger Gunicorn worker pool
2. **Increase PostgreSQL memory** - Larger shared buffers, effective_cache_size for faster queries
3. **Increase Redis memory** - For larger dataset caches
4. **Faster storage** - SSD instead of HDD for PostgreSQL data directory

---

## Failure Modes & Recovery

### Single Component Failures

**Flask Instance 1 Crashes**
- Nginx detects unhealthy via `/ready` endpoint
- Routes all traffic to Flask Instance 2
- System operates at 50% capacity
- Recovery: Restart container or redeploy
- Data loss: None (request was not yet persisted)

**PostgreSQL Unavailable**
- Flask `/ready` endpoint returns 503
- All instances marked unhealthy
- Nginx returns 503 Service Unavailable
- Recovery: Restore database from backup (see runooks)
- Data loss: Yes (any uncommitted transactions)

**Redis Unavailable**
- Application detects connection error
- Falls back to database queries
- Performance degradation but no errors
- Recovery: Restart Redis container
- Data loss: Cache data only (not critical)

### Multiple Component Failures

**Flask + PostgreSQL Down**
- System completely unavailable
- Recovery: Restore database, restart app instances
- Data loss: Any uncommitted transactions

**Distributed Failure (Network Partition)**
- If network split puts Flask and PostgreSQL on different sides
- Same as PostgreSQL unavailable (app can't reach DB)
- Recovery: Restore network connectivity

---

## Security Boundaries

### What This Architecture Does NOT Provide

- No encryption in transit between containers (all on internal Docker network)
- No encryption at rest for database (host-level dependent)
- No rate limiting per user
- No API key authentication (no per-user access control)
- No audit logging of who accessed what

### What This Architecture DOES Provide

- Database connection pooling prevents SQL injection vectors
- Input validation via Pydantic schemas
- Error messages do not leak sensitive information
- Request IDs enable correlation and forensics
- All requests logged with source, destination, and outcome

### To Deploy Securely

1. Run behind reverse proxy with TLS/SSL (Nginx configured but needs certs)
2. Store all secrets in secrets management system, not in code
3. Use VPC or private network for all container communication
4. Enable database encryption at rest and in transit
5. Implement rate limiting at proxy layer
6. Add authentication layer before API (API gateway or custom middleware)

---

## Development vs. Production Differences

### Local Development (docker-compose.yml)

- Single PostgreSQL container (no data persistence between runs)
- In-memory data by default (can add volume for persistence)
- All containers on same docker network (no security boundaries)
- Logging to stdout visible in `docker compose logs`
- No SSL/TLS (HTTP only)
- AlertManager sends webhooks to local webhook_proxy

### Production Deployment

- External managed PostgreSQL (RDS, CloudSQL, self-hosted)
- Persistent storage with backup procedures
- Network security groups, firewall rules, VPC isolation
- Centralized logging to ELK, CloudWatch, or similar
- SSL/TLS termination at Nginx or cloud load balancer
- AlertManager sends to production systems (PagerDuty, Discord webhook, email)

---

## Next Steps

- To deploy locally: See [deploy.md](deploy.md#local-development)
- To deploy to production: See [deploy.md](deploy.md#production-deployment)
- To understand capacity: See [capacity-plan.md](capacity-plan.md)
- To configure: See [config.md](config.md)
- To respond to incidents: See [runbooks.md](runbooks.md)

