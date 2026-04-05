# Runbooks: Operational Incident Guides

Each runbook is a step-by-step guide for responding to specific alerts or symptoms. Use these during incidents to diagnose and resolve problems quickly.

---

## Alert to Runbook Mapping

When you receive an alert, use this table to find the right runbook:

| Alert Name | Trigger | Runbook | Priority |
|-----------|---------|---------|----------|
| InstanceDown | App instance unreachable | [Application Instance Down](#application-instance-down) | Critical |
| HighErrorRate | Error rate >5% for 2 min | [High Error Rate](#high-error-rate) | High |
| HighLatency | P95 response >1s for 2 min | [High Latency](#high-latency) | High |
| PostgresDown | Database connection failures | [Database Down](#database-down) | Critical |
| RedisDown | Cache connection failures | [Redis Down](#redis-down) | Low |
| HighMemoryUsage | Container memory >85% | [Out of Memory](#out-of-memory) | High |
| HighCPUUsage | Container CPU >80% | [CPU Exhaustion](#cpu-exhaustion) | High |

---

## Application Instance Down

### Symptoms

- Nginx returns 503 Service Unavailable
- Alert: `InstanceDown` for vybe_app1 or vybe_app2
- Grafana shows one app instance offline while other is up

### Initial Assessment (1 minute)

1. Check which instances are affected:

```bash
docker compose ps | grep vybe_app
```

Expected: Both app1 and app2 show `healthy`. If one shows `error` or `restarting`, proceed.

2. Check app logs:

```bash
docker compose logs --tail=50 vybe_app1
```

Look for:
- Connection refused (database)
- Out of memory errors
- Segmentation faults
- Error on startup

3. Assess impact:

If one instance down: System runs at 50% capacity but is operational.
If both down: System is completely unavailable.

### Diagnosis (2-3 minutes)

1. Try to start the failed container:

```bash
docker compose restart vybe_app1
```

Wait 20 seconds for startup.

2. Check if it comes online:

```bash
curl http://localhost:8000/ready
```

If returns 200, instance recovered. Incident resolution complete (see "Follow-up" below).

3. If still failing, check database connection:

```bash
docker compose exec vybe_app1 curl http://db:5432 -v 2>&1 | grep -i connected || echo "DB unreachable"
```

If database is unreachable, this is database issue, not app issue. Jump to [Database Down](#database-down).

4. Check container logs for actual error:

```bash
docker compose logs vybe_app1 | grep -i error | tail -20
```

Common errors:
- **"Out of memory"** - Jump to [Out of Memory](#out-of-memory)
- **"Connection pool exhausted"** - Jump to [High Error Rate](#high-error-rate)
- **"Segmentation fault"** - Likely library issue, restart and monitor

### Resolution (3-5 minutes)

#### Option A: Container Restart (Most Common)

```bash
docker compose restart vybe_app1
```

This kills and restarts container. State is lost, but data is in database.

Verify recovery:
```bash
curl http://localhost:8000/ready
docker compose ps | grep vybe_app1
```

Expected: healthy status after 90 seconds startup period.

#### Option B: Container Rebuild + Restart (If Restart Fails)

```bash
docker compose up -d --no-deps --build vybe_app1
```

This rebuilds image and restarts. Takes 2-3 minutes.

#### Option C: Full Service Restart (If App isn't the Issue)

If restarting app doesn't help:

```bash
docker compose down
docker compose up -d
```

This restarts all services. Takes 5-10 minutes but clears any cascading issues.

### Follow-up (During Next 2 Hours)

1. Monitor error rate and CPU:

```bash
# In Prometheus UI, watch:
rate(requests_total{status="500"}[5m])
container_cpu_usage_seconds_total
```

2. Check logs for root cause:

```bash
docker compose logs vybe_app1 | grep -i warn | head -20
```

3. If instance crashes again within 1 hour, investigate root cause (likely OOM or C library issue).

4. Inform your team in incident channel with:
   - What happened (instance crashed)
   - What was the cause (if known)
   - What was done (container restarted)
   - Whether issue has recurred

---

## High Error Rate

### Symptoms

- Grafana shows error rate spike (red line above baseline)
- Alert: `HighErrorRate` if >5% for 2+ minutes
- Users report "something is broken"
- Logs show many 5xx errors (500, 503)

### Initial Assessment (1 minute)

1. Check error rate:

```bash
curl http://localhost:9090/api/v1/query?query=rate(requests_total%7Bstatus%3D%22500%22%7D%5B5m%5D)
```

Or in Prometheus UI, query:
```promql
rate(requests_total{status="500"}[5m])
```

If >0.05 (>5%), confirm high error rate.

2. Check app logs for error type:

```bash
docker compose logs vybe_app1 | grep -i error | head -30
```

Look for pattern:
- All errors same type (database error, validation error)?
- Random mix of errors?
- Specific endpoint failing?

3. Check if specific endpoint is broken:

```bash
curl -X POST http://localhost:8000/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Test each critical endpoint. If one returns 500 consistently, it's broken.

### Diagnosis (2-5 minutes)

1. Check database connectivity:

```bash
docker compose exec vybe_app1 psql postgresql://postgres:postgres@db/hackathon_db -c "SELECT 1"
```

If fails, jump to [Database Down](#database-down).

2. Check connection pool status:

```bash
docker compose exec db psql -d hackathon_db -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
```

If near DB_MAX_CONNECTIONS (default 20), pool exhausted.

3. Check memory usage:

```bash
docker stats vybe_app1 | grep MEMORY
```

If >80% of container limit (1GB default), jump to [Out of Memory](#out-of-memory).

4. Check CPU usage:

```bash
docker stats vybe_app1 | grep CPU
```

If >90%, jump to [CPU Exhaustion](#cpu-exhaustion).

5. Check recent deployments:

```bash
git log --oneline -10
```

Did error rate spike after recent code push? If so, likely new bug.

### Resolution (5-10 minutes)

#### Option A: Restart App Instances (If Transient)

```bash
docker compose restart vybe_app1 vybe_app2
```

This often clears transient issues (connection pool stuck, memory leak).

Wait 2 minutes and re-check error rate:
```bash
curl http://localhost:9090/api/v1/query?query=rate(requests_total%7Bstatus%3D%22500%22%7D%5B5m%5D)
```

If error rate drops to <1%, incident resolved.

#### Option B: Rollback Recent Deployment

If error rate spiked after recent code change:

```bash
# View recent git history
git log --oneline -5

# Revert to last good commit
git revert HEAD

# Rebuild and restart
docker compose up -d --build
```

This should restore previous behavior.

Monitor for 5 minutes to confirm error rate recovers.

#### Option C: Scale Up (If Overload)

If error rate is high but no specific error type found, system may be overloaded:

```bash
# Add 2 more app instances (total 4)
# Update docker-compose.yml to add vybe_app3, vybe_app4
# Then:
docker compose up -d
```

Nginx load balances across all instances, reducing per-instance load.

### Follow-up (Next 1 Hour)

1. Root cause analysis:

```bash
# What specifically was throwing errors?
docker compose logs --since=10m vybe_app1 | grep "500\|error\|traceback"

# Are those errors resolved?
curl http://localhost:8000/metrics | grep requests_total | grep 500
```

2. Update error-handling code if validation issue.

3. Notify team with incident summary:
   - Error rate spike (when, how long)
   - Root cause (if known)
   - Resolution taken (restart, rollback, scale up)
   - Preventive measures for next time

---

## High Latency

### Symptoms

- Grafana P95 latency line climbs above 1s threshold
- Alert: `HighLatency` if P95 >1s for 2+ minutes
- Users report "API is slow"
- Some requests succeed quickly, others hang

### Initial Assessment (1 minute)

1. Check current latency:

```bash
curl http://localhost:9090/api/v1/query?query=histogram_quantile%280.95%2Crate%28request_latency_seconds_bucket%5B5m%5D%29%29
```

Or in Prometheus UI:
```promql
histogram_quantile(0.95, rate(request_latency_seconds_bucket[5m]))
```

If >1, confirm high latency.

2. Check which endpoints are slow:

```bash
docker compose logs vybe_app1 --since=5m | grep "duration_ms" | sort -t= -k3 -nr | head -10
```

Look for requests taking >1000ms.

3. Check database query times:

```bash
docker compose logs db --since=5m | grep "duration:" | sort -t= -k2 -nr | head -10
```

If queries >500ms, database is the bottleneck.

### Diagnosis (2-5 minutes)

1. Check database connection pool:

```bash
docker compose exec db psql -d hackathon_db -c "SELECT count(*) FROM pg_stat_activity"
```

If connections > DB_MAX_CONNECTIONS * 0.8 (>16 for default 20), pool is full.

2. Check index usage:

For slow GET requests, verify indexes exist:

```bash
# Connect to database
docker compose exec db psql -d hackathon_db

# List indexes on critical tables
\d urls
\d events

# Look for index on frequently queried column (e.g., id, code, user_id)
```

If critical column has no index, that's likely cause.

3. Check CPU usage:

```bash
docker stats | grep vybe_app
```

If CPU >50%, query processing or serialization may be slow.

4. Check Redis cache hit rate (if enabled):

```bash
curl http://localhost:9090/api/v1/query?query=redis_keyspace_hits_total
curl http://localhost:9090/api/v1/query?query=redis_keyspace_misses_total
```

If hit rate <50%, cache not helping. Increase TTL or cache more patterns.

### Resolution (5-15 minutes)

#### Option A: Enable Caching (If Disabled)

If REDIS_ENABLED=false, many queries hit database:

```bash
# Check if Redis running
docker compose ps redis

# If not, start it
docker compose up -d redis

# Enable in .env
REDIS_ENABLED=true

# Restart app
docker compose restart vybe_app1 vybe_app2
```

Monitor latency drop over 2 minutes. Repeat requests to allow cache to populate.

#### Option B: Add Missing Index

If database queries are slow without index:

```bash
# Connect to database
docker compose exec db psql -d hackathon_db

# Create missing index (e.g., on short code)
CREATE INDEX idx_urls_code ON urls(code);

# Verify index is used
EXPLAIN SELECT * FROM urls WHERE code = 'abc123';
```

Re-run slow query. Should complete in <100ms now.

#### Option C: Scale Up Workers

If all instances CPU high, increase workers per instance:

```bash
# In .env
WORKERS=4  # increase from default 2

# Restart app
docker compose restart vybe_app1 vybe_app2
```

Monitor latency. More workers allow parallel handling of more requests.

#### Option D: Add Application Instances

If single instance can't keep up:

```bash
# Add vybe_app3, vybe_app4 to docker-compose.yml
docker compose up -d
```

Nginx balances load across all instances.

### Follow-up (Next 30 Minutes)

1. Monitor latency trend:

```bash
# In Prometheus UI, graph for 1 hour
histogram_quantile(0.95, rate(request_latency_seconds_bucket[5m]))
```

Should trend back to <500ms.

2. Identify if latency is consistent or spiky:

- Consistent high latency = system overloaded, need more resources
- Spiky latency = intermittent issue (file I/O, GC pause, network), less urgent

3. Update monitoring to catch root cause:

If database was cause, add metric to alert on slow query count:
```promql
rate(pg_slow_queries_total[5m]) > 10
```

---

## Database Down

### Symptoms

- Nginx returns 503 Service Unavailable for all requests
- Alert: `PostgresDown`
- App logs show "Failed to connect to database" repeatedly
- `/ready` endpoint returns 503

### Critical: Assess Availability (30 seconds)

Calculate impact:
- System offline? Yes
- Data loss risk? Check backup age
- ETA to restore? Depends on root cause

If this is production, wake up on-call team and open incident channel.

### Initial Assessment (1 minute)

1. Check if database container is running:

```bash
docker compose ps db
```

Status shows:
- `healthy` = database running and healthy
- `starting` = database initializing, wait 30 seconds
- `unhealthy` = database running but failing health check
- Not listed = database container down

2. If not running, try to start:

```bash
docker compose up -d db
```

Wait 30 seconds for startup.

3. Verify database is accessible:

```bash
docker compose exec db pg_isready -U postgres
```

Expected: `accepting connections`

4. Check database logs:

```bash
docker compose logs db | tail -30
```

Common issues:
- **"FATAL: could not create file"** = disk full, permissions issue
- **"PANIC: could not write"** = storage failure
- **"ERROR: ENOENT"** = data directory corrupted

### Diagnosis (2-5 minutes)

1. Test connection from app:

```bash
docker compose exec vybe_app1 psql postgresql://postgres:postgres@db/hackathon_db -c "SELECT 1"
```

If connects, issue is app config, not database.

2. Check disk space:

```bash
docker exec vybe_db df -h
```

If usage >90%, disk is full. Database cannot write new data.

3. Check data directory:

```bash
docker exec vybe_db ls -la /var/lib/postgresql/data
```

Should show files like `base`, `global`, `pg_wal`.

If missing or corrupted, database is damaged.

4. Check PostgreSQL logs for specific error:

```bash
docker compose logs db | grep ERROR | head -20
```

### Resolution (5-30 minutes, depending on severity)

#### Option A: Restart PostgreSQL (Most Common)

```bash
docker compose restart db
```

Wait 60 seconds for startup.

Verify recovery:
```bash
docker compose exec vybe_app1 psql postgresql://postgres:postgres@db/hackathon_db -c "SELECT COUNT(*) FROM urls"
```

If this returns a number, database is back online.

Restart the app to clear connection pool:
```bash
docker compose restart vybe_app1 vybe_app2
```

#### Option B: Free Disk Space (If Disk Full)

If df showed >90% usage:

```bash
# Delete old logs
docker exec vybe_db rm /var/log/postgresql/*.log

# Check space again
docker exec vybe_db df -h

# Restart database
docker compose restart db
```

#### Option C: Restore from Backup (If Database Corrupted)

If logs show data corruption:

1. Stop the database:

```bash
docker compose stop db
docker compose rm db
```

2. Delete corrupted data:

```bash
docker volume rm vybe_postgres_data
```

3. Restore from backup:

```bash
# Download backup
aws s3 cp s3://backups/vybe/vybe_backup_20260404.sql.gz ./

# Decompress
gunzip vybe_backup_20260404.sql.gz

# Start database fresh
docker compose up -d db

# Wait for initialization
sleep 30

# Restore data
docker compose exec -T db psql -U postgres < vybe_backup_20260404.sql
```

4. Verify data:

```bash
docker compose exec db psql -d hackathon_db -c "SELECT COUNT(*) FROM urls"
```

Should return pre-backup count.

5. Restart app:

```bash
docker compose restart vybe_app1 vybe_app2
```

#### Option D: Migrate to Backup Database (If Self-Hosted)

If primary database is destroyed (hardware failure):

1. Provision new PostgreSQL instance
2. Restore latest backup to new instance
3. Update DATABASE_HOST in .env to point to new instance
4. Restart about:

```bash
export DATABASE_HOST=new-db-host.example.com
docker compose restart vybe_app1 vybe_app2
```

### Follow-up (Next 30-60 Minutes)

1. Verify data integrity:

```bash
# Count records match expectations
docker compose exec db psql -d hackathon_db << EOF
SELECT 'users' as table_name, COUNT(*) FROM users
UNION
SELECT 'urls', COUNT(*) FROM urls
UNION
SELECT 'events', COUNT(*) FROM events;
EOF
```

2. Check for data loss:

Compare record counts with backup timestamp. Any significant difference = data loss. Investigate.

3. Update monitoring:

Add alert for disk usage:
```yaml
- alert: PostgresDiskFull
  expr: node_filesystem_avail_bytes{mountpoint="/var/lib/postgresql"} / node_filesystem_size_bytes < 0.10
```

4. Review backup strategy:

- Was backup recent enough? (ideally <4 hours old)
- Are backups being tested (restore tested)?
- Is backup location secure and redundant?

---

## Redis Down

### Symptoms

- Alert: `RedisDown`
- App logs show "Redis connection failed"
- But `/ready` still returns 200 (Redis optional)
- Request latency increases slightly

### Initial Assessment (1 minute)

Redis failure is low priority because app falls back to database. Check if REDIS_ENABLED=true:

```bash
grep REDIS_ENABLED backend/.env
```

If `false`, Redis isn't being used. Ignore alert.

If `true`, continue diagnosis.

### Diagnosis (2 minutes)

1. Check Redis container:

```bash
docker compose ps redis
```

Status shows:
- `healthy` = Redis running
- `unhealthy` = Redis running but health check failing
- Not listed = Redis not running

2. Test connection:

```bash
docker compose exec redis redis-cli ping
```

Expected: `PONG`

3. Check Redis logs:

```bash
docker compose logs redis | tail -20
```

Look for errors like:
- "Out of memory" (dataset exceeded max memory)
- "Disk full" (storage issue)
- "Connection refused" (port issue)

### Resolution (2-5 minutes)

#### Option A: Restart Redis

```bash
docker compose restart redis
```

Wait 5 secondes for startup:
```bash
docker compose exec redis redis-cli ping
```

#### Option B: Check Memory Limits

If Redis shows out of memory:

```bash
docker compose exec redis redis-cli INFO memory
```

Look at `used_memory_bytes` vs `maxmemory`.

If at limit, either:
a) Increase Redis memory in docker-compose.yml
b) Reduce cache TTL (keys expire faster)
c) Disable caching if not essential

#### Option C: Clear Cache (Aggressive)

If Redis is stuck or corrupted:

```bash
docker compose exec redis redis-cli FLUSHALL
```

This deletes all cached data. App will recompute cache on next requests.

### Impact While Redis Down

- Requests take 50-100ms longer (direct database queries)
- Error rate doesn't increase (no cascading failures)
- System is fully functional, just slower

No urgency to restore immediately. Can be scheduled for next maintenance window.

---

## Out of Memory

### Symptoms

- Container killed unexpectedly
- Alert: `HighMemoryUsage` if >85% for 1 minute
- Logs show "Cannot allocate memory"
- App container goes from `healthy` to `exited`

### Initial Assessment (1 minute)

1. Check current memory usage:

```bash
docker stats vybe_app1 | grep MEMORY
```

Example output: `1GiB / 1GiB` = at 100% limit, will be killed.

2. Check memory trend in Prometheus:

```promql
container_memory_usage_bytes{name="vybe_app1"}
```

If line trending up and hitting ceiling, memory leak.

3. Check available system memory:

```bash
free -h
```

If system memory also low (<10%), node is overloaded.

### Diagnosis (2-3 minutes)

1. Check what's consuming memory:

Inside container:
```bash
docker compose exec vybe_app1 top -b -n1 | head -20
```

Look for process using >500MB.

2. Check for memory leak in Python:

```bash
# If app was running a long time before OOM:
docker compose logs vybe_app1 | tail -50 | grep -i "memory\|gc"
```

If app was stable for days then suddenly OOM = memory leak.

3. Check database connection pool:

Large number of open connections = large memory. Check:

```bash
docker compose exec db psql -d hackathon_db -c "SELECT COUNT(*) FROM pg_stat_activity"
```

If connections > DB_MAX_CONNECTIONS * 0.9, pool badly configured.

### Resolution (5-10 minutes)

#### Option A: Increase Container Memory Limit

In docker-compose.yml:

```yaml
vybe_app1:
  deploy:
    resources:
      limits:
        memory: 2G  # Increase from 1G
```

Restart:
```bash
docker compose up -d
```

This buys time but doesn't fix root cause if there's a leak.

#### Option B: Reduce Cache TTL (If Redis)

In .env:
```bash
REDIS_DEFAULT_TTL_SECONDS=60  # Reduce from 300
```

Smaller cache = less memory. Restart app.

#### Option C: Reduce Connection Pool

In .env:
```bash
DB_MAX_CONNECTIONS=10  # Reduce from 20
```

Fewer connections = less memory overhead. Restart app.

#### Option D: Deploy to More Instances

If single instance can't hold cache/connections:

```bash
# Add vybe_app3, vybe_app4
docker compose up -d
```

Nginx distributes memory load across instances.

#### Option E: Identify and Fix Memory Leak

If memory steadily climbs:

1. Add memory profiling to app (add `memory_profiler` library)
2. Run under controlled load and capture memory snapshots at intervals
3. Identify which function/library is accumulating objects
4. File bug or update code

### Follow-up (Immediate + Next 1 Hour)

1. Monitor memory over next hour:

```bash
for i in {1..60}; do docker stats vybe_app1 | grep MEMORY; sleep 60; done
```

Should stabilize at ~50-70% if fix worked.

2. Gradually load test to verify stability under realistic traffic.

3. If OOM recurs, implement more aggressive fix (memory limits, profile code).

---

## CPU Exhaustion

### Symptoms

- Alert: `HighCPUUsage` if >80% for 2 minutes
- Request latency spikes
- System feels slow/unresponsive
- Grafana CPU graph shows sustained high usage

### Initial Assessment (1 minute)

1. Check CPU usage:

```bash
docker stats | grep vybe_app
```

Example: `50% / 200%` (1 of 2 CPUs maxed).

2. Is this permanent or spiky?

Watch for 30 seconds:
```bash
watch docker stats
```

If consistently >80%, problem. If spikes to 90% occasionally, normal.

3. Check what's causing high CPU:

Inside container:
```bash
docker compose exec vybe_app1 ps aux | grep -E "python|gunicorn" | head -5
```

Usually Gunicorn processes using CPU.

### Diagnosis (2-5 minutes)

1. Check request rate:

```promql
# In Prometheus
rate(requests_total[1m])
```

If 10x higher than normal, high traffic = expected CPU spike.

2. Check slow endpoint:

```bash
# Find endpoint with highest latency
docker compose logs vybe_app1 | grep "duration_ms" | sort -t= -k3 -nr | head -5
```

Very slow endpoint = CPU heavy operation.

3. Check database query performance:

```bash
docker compose logs db | grep "duration:" | sort -t= -k2 -nr | head -5
```

If queries slow, CPU waiting for I/O. This is different problem.

4. Check for infinite loops or bad algorithms:

Look at recent code changes:
```bash
git log -p --since="1 day ago" -- backend/app/services
```

Look for new loops or N+1 queries.

### Resolution (5-15 minutes)

#### Option A: Scale Up (Add Workers)

```bash
# In .env
WORKERS=4  # increase from 2

# Restart
docker compose restart vybe_app1 vybe_app2
```

Load balances computation across more processes.

#### Option B: Scale Horizontally (Add Instances)

```bash
# Add vybe_app3, vybe_app4 to docker-compose.yml
docker compose up -d
```

Nginx distributes requests across more app instances.

#### Option C: Identify and Optimize Slow Endpoint

If specific endpoint causing spike:

1. Get detailed logs:

```bash
docker compose logs vybe_app1 | grep "endpoint-name" | tail -10
```

2. Add profiling:

```python
# In app code, wrap slow operation
import cProfile
profiler = cProfile.Profile()
profiler.enable()
result = slow_function()
profiler.disable()
profiler.print_stats()
```

3. Optimize (cache results, use index, break into smaller queries).

#### Option D: Reduce Load Temporarily (If Critical)

Enable rate limiting or gracefully degrade:

```yaml
# In nginx config
limit_req zone=api burst=10 nodelay;
```

This throttles requests to prevent overload.

### Follow-up (Next 1 Hour)

1. Monitor if CPU returns to normal:

```bash
# Watch for 5 minutes
watch -n 10 "docker stats | grep vybe_app | awk '{print \$3}'"
```

Should drop to <50%.

2. If CPU stays high, likely sustained high traffic. Plan to scale permanently.

3. Review optimization opportunities:
   - Add missing indexes
   - Cache more aggressively
   - Rewrite slow algorithm
   - Split into async jobs (if applicable)

---

## Incident Command

During a serious incident:

1. **Declare incident:** "We have an incident affecting [service]. Severity: [critical/high/medium]"
2. **Gather team:** Wake up on-call engineers
3. **Assign roles:**
   - Incident Commander (orchestrates resolution)
   - Technical Lead (diagnosis)
   - Communications (updates status)
4. **Use runbook:** Follow relevant guide above
5. **Document:** Copy exact steps taken, timestamps, outcomes
6. **Resolved:** When `/ready` returns 200 and system stable for 5 minutes
7. **Post-incident:** Within 24 hours, write blameless incident report

---

## Escalation

If incident not resolving in 10 minutes:

1. Escalate to infrastructure team
2. Prepare for database restore (have backup ready)
3. Prepare for failover (route traffic to standby if exists)
4. Communicate with product/business stakeholders

If incident not resolved in 30 minutes:

1. Escalate to CTO/leadership
2. Prepare public status communication
3. Begin manual recovery procedures
4. Consider switching to read-only mode if applicable

