# Runbook: High Error Rate

## Alert Details
- **Alert Name:** HighErrorRate / High5xxRate
- **Severity:** Warning (HighErrorRate) / Critical (High5xxRate)
- **Threshold:** >5% error rate (HighErrorRate) or >2% 5xx rate (High5xxRate)
- **Duration:** 2 minutes

## Symptoms
- Discord alert: "[FIRING] HighErrorRate" or "[FIRING] High5xxRate"
- Grafana dashboard shows spike in error rate panel
- Increased error counters in metrics
- Users reporting failures or 500 errors

## Investigation Steps

### 1. Check Current Error Rate
```bash
# View real-time metrics
curl http://localhost/metrics | grep http_errors_total

# Query Prometheus
open http://localhost:9090
# Query: rate(http_errors_total[5m])
# Query: rate(http_errors_total{status=~"5.."}[5m])
```

### 2. Check Application Logs
```bash
# View recent errors from both instances
docker logs vybe_app1 --tail 100 | grep ERROR
docker logs vybe_app2 --tail 100 | grep ERROR

# Follow logs in real-time
docker logs vybe_app1 -f | grep -E "(ERROR|WARNING)"
```

### 3. Check Grafana Dashboard
```bash
open http://localhost:3000
# Navigate to: Vybe System Dashboard
# Look at:
# - Error Rate panel (which instance?)
# - Request Latency (correlated spike?)
# - In-Flight Requests (overload?)
# - Database connections (exhausted?)
```

### 4. Identify Error Pattern
Look for patterns in logs:
- **Database errors:** "connection refused", "too many connections", "timeout"
- **Redis errors:** "connection refused", "READONLY"
- **Application errors:** Stack traces, specific error messages
- **Request IDs:** Track specific failing requests

### 5. Check Dependencies
```bash
# Check database health
docker exec vybe_db pg_isready -U postgres

# Check Redis health
docker exec vybe_redis redis-cli ping

# Check all container status
docker compose ps
```

## Common Causes & Fixes

### Cause 1: Database Connection Pool Exhausted
**Symptoms:**
- Logs show: "connection pool exhausted" or "too many connections"
- Prometheus: `pg_stat_database_numbackends` near `pg_settings_max_connections`

**Fix:**
```bash
# Check current connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "SELECT count(*) FROM pg_stat_activity;"

# Restart app instances to reset connection pools
docker restart vybe_app1 vybe_app2

# If persistent, increase DB_MAX_CONNECTIONS in backend/.env
```

### Cause 2: Database Down
**Symptoms:**
- Logs show: "could not connect to server"
- All requests failing with 503

**Fix:**
```bash
# Check database status
docker ps | grep vybe_db

# Restart database
docker restart vybe_db

# Wait for health check
sleep 15

# Verify recovery
curl http://localhost/ready
```

### Cause 3: Redis Down (Cache Failures)
**Symptoms:**
- Logs show: "Redis connection refused"
- Increased latency + errors

**Fix:**
```bash
# Check Redis status
docker ps | grep vybe_redis

# Restart Redis
docker restart vybe_redis

# App should gracefully degrade without cache
```

### Cause 4: Application Bug / Code Issue
**Symptoms:**
- Specific endpoint failing consistently
- Stack traces in logs
- Errors in Sentry dashboard

**Fix:**
```bash
# Check Sentry for error details
# (if SENTRY_DSN configured)

# Identify failing endpoint from logs
docker logs vybe_app1 --tail 200 | grep ERROR

# Rollback to previous version if recent deployment
# Or apply hotfix and redeploy
```

### Cause 5: Resource Exhaustion
**Symptoms:**
- High CPU or memory usage
- Slow responses + errors
- Container restarts

**Fix:**
```bash
# Check container resources
docker stats vybe_app1 vybe_app2

# If memory exhausted, restart containers
docker restart vybe_app1 vybe_app2

# Check for memory leaks in Grafana
# Consider scaling horizontally (add more instances)
```

## Verification Steps

After applying fix:

1. **Check error rate drops:**
```bash
# Prometheus query
rate(http_errors_total[1m])
```

2. **Verify health endpoints:**
```bash
curl http://localhost/health
curl http://localhost/ready
```

3. **Generate test traffic:**
```bash
for i in {1..20}; do curl http://localhost/health; sleep 1; done
```

4. **Wait for alert resolution:**
- Check Alertmanager: http://localhost:9093
- Should see "[RESOLVED]" notification in Discord within 5 minutes

5. **Monitor dashboard:**
- Error rate should return to <1%
- Latency should normalize
- No new errors in logs

## Escalation

If issue persists after 15 minutes:
1. Check if this is a known issue (check recent deployments)
2. Consider rolling back recent changes
3. Scale down traffic if possible (rate limiting)
4. Escalate to on-call engineer
5. Consider maintenance mode if critical

## Prevention

- Set up proper connection pooling limits
- Implement circuit breakers for external dependencies
- Add retry logic with exponential backoff
- Monitor error rates proactively
- Regular load testing to identify limits
- Implement graceful degradation

## Related Alerts
- InstanceDown
- HighLatency
- PostgresTooManyConnections
- PostgresDown
- RedisDown
