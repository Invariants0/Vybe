# Troubleshooting Guide

Common issues, their causes, and step-by-step solutions. Each section follows the pattern: Problem, Cause, Solution, Prevention.

---

## Setup & Local Development

### Issue: Port 8080 Already in Use

**Problem:** `docker compose up` fails with "Address already in use" for port 8080.

**Cause:** Another service is already running on port 8080 (previous Vybe instance, another app, etc.).

**Solution:**

1. Find what's using port 8080:

```bash
sudo lsof -i :8080
```

This shows the process ID (PID) and command.

2. Option A: Stop the conflicting service:

If it's a previous Vybe instance:
```bash
docker compose down
```

If it's another service, stop it with its own command or the process manager.

3. Option B: Use a different port for Nginx:

Edit docker-compose.yml:
```yaml
nginx:
  ports:
    - "8081:80"  # Changed from 8080 to 8081
```

Then access via `http://localhost:8081` instead.

4. Retry:

```bash
docker compose up
```

**Prevention:** Before running docker-compose, check if port is free:

```bash
lsof -i :8080 || echo "Port 8080 is free"
```

---

### Issue: Database Connection Fails on Start

**Problem:** App container logs show "Failed to connect to database" repeatedly.

**Cause:** PostgreSQL is not running, not ready, or connection parameters are wrong.

**Solution:**

1. Check if database container started:

```bash
docker compose ps db
```

Expected status: `Up` or `healthy`.

2. Check database logs:

```bash
docker compose logs db | tail -20
```

Look for error messages about initialization.

3. Verify connection parameters:

Check backend/.env:
```bash
cat backend/.env | grep DATABASE
```

Match with what's in docker-compose.yml:
```bash
grep -A5 "postgres:16" docker-compose.yml
```

4. Test connection manually:

```bash
docker compose exec db psql -U postgres -d hackathon_db -c "SELECT 1"
```

If this works, the database is fine. Issue is likely configuration or timing.

5. Increase startup time:

Add delay in docker-compose.yml:

```yaml
vybe_app1:
  depends_on:
    db:
      condition: service_healthy
  healthcheck:
    start_period: 120s  # Wait 2 minutes before first check
```

6. Retry:

```bash
docker compose restart
```

**Prevention:** Use `depends_on` with health checks to ensure database starts before app.

---

### Issue: Redis Connection Error (But App Works)

**Problem:** Logs show "Redis connection failed" but app still responds.

**Cause:** Redis is disabled or unavailable, which is expected behavior for optional caching.

**Solution:**

1. Check if Redis is enabled:

```bash
cat backend/.env | grep REDIS_ENABLED
```

2. If REDIS_ENABLED=false, this is normal. App works without cache (just slower).

3. If REDIS_ENABLED=true but Redis is down:

```bash
docker compose ps redis
```

If not running, start it:
```bash
docker compose up -d redis
```

4. Test Redis:

```bash
docker compose exec redis redis-cli ping
```

Expected: `PONG`

**Prevention:** REDIS_ENABLED=false is the safe default. Enable only when needed.

---

## API & Application

### Issue: POST /api/v1/links Returns 400 Bad Request

**Problem:** Link creation fails with validation error.

**Example Request:**
```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{"url": "invalid"}'
```

**Response:**
```json
{
  "error": "validation_error",
  "message": "Invalid URL format",
  "details": {
    "field": "url",
    "reason": "must start with http:// or https://"
  }
}
```

**Cause:** URL is not properly formatted (missing protocol or invalid format).

**Solution:**

1. Check URL format:
   - Must start with `http://` or `https://`
   - Must be valid URL syntax

2. Send valid request:

```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/page",
    "custom_alias": "demo"
  }'
```

3. Expected response (201 Created):

```json
{
  "code": "demo",
  "short_url": "http://localhost:8080/demo",
  "original_url": "https://example.com/page"
}
```

**Prevention:** Always validate input format. Use a tool like `jq` to validate JSON:

```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{...}' | jq '.'
```

---

### Issue: GET /{code} Returns 404 Not Found

**Problem:** Redirect for a short code that should exist returns 404.

**Cause:** Link was never created, or was deleted/deactivated.

**Solution:**

1. Verify link exists:

```bash
curl http://localhost:8080/api/v1/links/launch
```

If 404, link doesn't exist. Create it:

```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "custom_alias": "launch"
  }'
```

2. If link exists but redirect returns 404:

Check if link is active:

```bash
curl http://localhost:8080/api/v1/links/launch
```

Response should show `"is_active": true`.

3. If inactive, reactivate:

```bash
curl -X PATCH http://localhost:8080/api/v1/links/launch \
  -H "Content-Type: application/json" \
  -d '{"is_active": true}'
```

4. Check expiration:

If `expires_at` is in the past, link is expired (returns 410 Gone). Update expiration:

```bash
curl -X PATCH http://localhost:8080/api/v1/links/launch \
  -H "Content-Type: application/json" \
  -d '{"expires_at": null}'  # Clear expiration
```

**Prevention:** Keep track of created links. Use list endpoint (when available) to see all links.

---

### Issue: POST /api/v1/links Returns 409 Conflict

**Problem:** Custom alias creation fails with "alias already exists".

**Cause:** The custom alias is already in use by another link.

**Solution:**

1. Use a different alias:

```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "custom_alias": "launch-v2"  # Different alias
  }'
```

2. Or omit custom_alias to generate one:

```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
    # No custom_alias, auto-generated
  }'
```

3. Check existing aliases:

```bash
curl http://localhost:8080/api/v1/links
# (Returns list of all links when implemented)
```

**Prevention:** Use descriptive, unique aliases. Convention: `project-purpose` (e.g., `vybe-demo`, `vybe-launch`).

---

### Issue: API Returns 500 Internal Server Error

**Problem:** Request returns 500 with generic error message.

**Cause:** Unhandled exception in application code or external service failure.

**Solution:**

1. Check application logs for details:

```bash
docker compose logs vybe_app1 | tail -50
```

Look for stack trace or error message.

2. Common causes:

   a. **Database error:** Check database is healthy:
   ```bash
   docker compose exec db psql -U postgres -d hackathon_db -c "SELECT 1"
   ```

   b. **Invalid configuration:** Check environment variables:
   ```bash
   docker compose exec vybe_app1 env | grep -i error
   ```

   c. **Corrupted data:** Check database integrity:
   ```bash
   docker compose exec db psql -U postgres -d hackathon_db -c "SELECT COUNT(*) FROM urls"
   ```

3. If error is consistent, check the full stack trace in logs and consult [runbooks.md](runbooks.md#high-error-rate).

**Prevention:** Monitor error rate in Grafana. Alert when error rate exceeds threshold (see [architecture.md](architecture.md#alerts-alertmanager)).

---

## Database & Persistence

### Issue: "Database Temporarily Unavailable"

**Problem:** Every API request fails with database unavailable error.

**Cause:** PostgreSQL is down, unreachable, or connection pool is exhausted.

**Solution:**

1. Check if database is running:

```bash
docker compose ps db
```

Status should be `healthy`.

2. If database is down, start it:

```bash
docker compose up -d db
```

3. Verify database is accepting connections:

```bash
docker compose exec vybe_app1 curl http://db:5432 -v 2>&1 | grep -i connected || echo "Connection failed"
```

Or use pg_isready:

```bash
docker compose exec db pg_isready -U postgres
```

4. Check connection pool state:

```bash
docker compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity"
```

If this number is near DB_MAX_CONNECTIONS (default 20), pool is exhausted.

5. Increase connection pool size:

Edit backend/.env:
```bash
DB_MAX_CONNECTIONS=30  # Increase from 20
```

Restart app:
```bash
docker compose restart vybe_app1 vybe_app2
```

6. Check for connection leaks:

If pool exhausts frequently, there might be code not closing connections. Check repository layer commits are called.

**Prevention:** Monitor connection pool usage in Prometheus. Alert when pool > 80% full.

This indicates need to scale (add more app instances).

---

### Issue: Links Disappear After Docker Restart

**Problem:** Created links are lost after `docker compose restart`.

**Cause:** PostgreSQL volume not persisting data (using in-memory or temporary storage).

**Solution:**

1. Check docker-compose.yml volume configuration:

```bash
grep -A10 "volumes:" docker-compose.yml | grep postgres
```

Should show:
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

2. Verify named volume exists:

```bash
docker volume ls | grep vybe
```

Expected: `vybe_postgres_data` listed.

3. Use persistent volume:

Ensure docker-compose.yml includes:

```yaml
volumes:
  postgres_data:  # Named volume, persists between runs

services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Mount named volume
```

4. Do full restart to test persistence:

```bash
docker compose down
# Data is still in named volume
docker compose up -d
# Data comes back
curl http://localhost:8080/api/v1/links/demo
# Link should exist
```

**Prevention:** Always use named volumes for databases. Never use temporary storage for production data.

---

## Performance & Monitoring

### Issue: API Responses Are Slow (>1 second)

**Problem:** Requests that should be fast (e.g., link redirect) take >1 second.

**Cause:** Database query slow, cache missing, or system under load.

**Solution:**

1. Check system load:

```bash
docker stats
```

Look for CPU or memory high usage.

2. Check database query time:

```bash
docker compose logs db | grep "duration:"
```

If query time is >100ms, issue is database query performance.

3. Enable Redis caching (if acceptable for your use case):

Edit backend/.env:
```bash
REDIS_ENABLED=true
```

Restart:
```bash
docker compose restart vybe_app1 vybe_app2
```

Repeat request (should be faster):
```bash
time curl http://localhost:8080/demo
```

4. Check if query is hitting index:

For most used queries, verify indexes exist in `backend/models/`.

5. Monitor in Grafana:

Open http://localhost:3000 > Application dashboard.

Check:
- Request latency p50/p95/p99
- Database query time
- CPU usage

**Prevention:** Monitor P95 latency. Alert when P95 > 1 second. This indicates need to scale or optimize queries.

---

### Issue: Prometheus Not Scraping Metrics

**Problem:** Prometheus shows no data or targets are DOWN.

**Cause:** Metrics endpoint unreachable, firewall blocking, or configuration error.

**Solution:**

1. Verify metrics endpoint is running:

```bash
curl http://localhost:8000/metrics | head -10
```

Should show Prometheus format output.

2. Check Prometheus configuration:

```bash
docker exec vybe_prometheus cat /etc/prometheus/prometheus.yml
```

Should include scrape config for Flask metrics.

3. Check Prometheus targets UI:

Open http://localhost:9090 > Status > Targets

If status is "DOWN", check error message.

4. Common fixes:

   a. **Endpoint not accessible:** Verify Docker network:
   ```bash
   docker network ls | grep vybe
   docker network inspect vybe_network | grep Containers
   ```

   b. **Port wrong:** Metrics on port 8000, not 5000:
   ```bash
   curl http://vybe_app1:8000/metrics
   ```

   c. **Config syntax:** Validate YAML:
   ```bash
   docker exec vybe_prometheus promtool check config /etc/prometheus/prometheus.yml
   ```

5. Force rescrape:

```bash
docker compose restart prometheus
```

Wait 30 seconds, then check targets again.

**Prevention:** Always test metrics endpoint after deployment:

```bash
curl http://localhost:8000/metrics -o /dev/null -w "%{http_code}\n"
```

Expected: 200

---

### Issue: Grafana Dashboard Shows "No data"

**Problem:** Grafana panels are empty even though metrics are flowing.

**Cause:** Prometheus data source not configured, query has wrong label, or time range is too far in past.

**Solution:**

1. Check Prometheus datasource:

In Grafana > Configuration > Data Sources.

Verify:
- URL is correct (http://prometheus:9090)
- Status shows green checkmark

2. Check query in dashboard:

Click on panel > Edit.

Verify query labels match actual metrics:

```promql
# Wrong:
requests_total{service="vybe"}  # label 'service' doesn't exist

# Right:
requests_total{job="vybe_app"}  # labels as they exist in Prometheus
```

3. Adjust time range:

If dashboard time range is before metrics collection started, no data will show.

In top right: select "Last 1 hour" or later.

4. Create new panel if existing one broken:

Dashboard > Add panel > choose metric > save.

**Prevention:** After deploying new version, re-verify all Grafana queries are valid. Label changes break dashboards.

---

## Monitoring & Alerts

### Issue: Alerts Are Not Firing

**Problem:** Container clearly has issue but Prometheus alert never fires.

**Cause:** Alert rule not configured correctly, evaluation window too long, or metrics not being collected.

**Solution:**

1. Check alert rules are loaded:

```bash
docker exec vybe_prometheus promtool check rules /etc/prometheus/alerts.yml
```

Output should list all rules.

2. Check if metric exists:

In Prometheus UI, execute query for the metric in the alert:

```promql
# If alert is for high CPU:
container_cpu_usage_seconds_total

# Should return results if metric is being collected
```

If no results, metrics aren't coming in. Check scrape config (previous issue).

3. Check evaluation settings:

Alert might be configured with long evaluation window. Edit alert:

```yaml
groups:
  - name: vybe_alerts
    interval: 30s  # Evaluate every 30 seconds
    rules:
      - alert: HighCPUUsage
        expr: container_cpu > 0.8
        for: 2m  # Must be high FOR 2 minutes before firing
```

If `for:` is very long (e.g., 1h), alert won't fire until issue persists that long.

4. Manually test alert rule:

In Prometheus UI > Alerts, see if alert is "PENDING" or "FIRING".

Click the alert to see evaluation result.

5. Check AlertManager is receiving alerts:

```bash
curl http://localhost:9093/api/v1/alerts
```

Should return JSON list of alerts (empty if none firing).

**Prevention:** Test alert routing after deployment:

```bash
# In AlertManager config, add a test rule:
- alert: TestAlert
  expr: up == 1
  for: 1m
```

This alert should fire immediately. Remove after testing.

---

### Issue: Alert Fired But No Notification Received

**Problem:** Alert is firing in Prometheus, but webhook not called.

**Cause:** AlertManager not routing alert, webhook URL wrong, or receiver not configured.

**Solution:**

1. Check AlertManager is running:

```bash
docker compose ps alertmanager
```

Should be running.

2. Check alert routing config:

```bash
docker exec vybe_alertmanager cat /etc/alertmanager/alertmanager.yml
```

Verify:
- Routes are defined
- Receivers are configured with correct webhook URLs

3. Test webhook manually:

```bash
curl -X POST https://discord.com/api/webhooks/... \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test notification"
  }'
```

If this fails, webhook URL is wrong or service is down.

4. Check AlertManager logs:

```bash
docker compose logs alertmanager | tail -20
```

Look for errors about failed webhook delivery.

5. Update webhook URL:

Edit `monitoring/alertmanager/alertmanager.yml`:

```yaml
receivers:
  - name: 'discord'
    webhook_configs:
      - url: 'https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID'
```

Restart AlertManager:

```bash
docker compose restart alertmanager
```

**Prevention:** After configuring alerts, fire a test alert and verify notification is received. Never rely on untested alert routing.

---

## Related Resources

- For database-specific issues, see [runbooks.md#database-down](runbooks.md#database-down)
- For high error rate issues, see [runbooks.md#high-error-rate](runbooks.md#high-error-rate)
- For latency issues, see [runbooks.md#high-latency](runbooks.md#high-latency)
- For configuration questions, see [config.md](config.md)
- For deployment issues not covered here, see [deploy.md](deploy.md#troubleshooting-deployment-issues)

---

## Getting Help

If your issue isn't covered here:

1. Check application logs:

```bash
docker compose logs vybe_app1 | grep -i error | tail -20
```

2. Check database logs:

```bash
docker compose logs db | tail -20
```

3. Extract request ID from error and search logs:

```bash
# Error shows: "request_id": "req-abc123def456"
docker compose logs | grep "req-abc123def456"
```

4. Check Prometheus metrics for anomalies:

In Prometheus UI, find metric and see if it correlates with error time.

5. Consult [runbooks.md](runbooks.md) for incident response procedures.

