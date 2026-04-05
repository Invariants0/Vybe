# Runbook: High Latency

## Alert Details
- **Alert Name:** HighLatency
- **Severity:** Warning
- **Threshold:** P95 latency > 1 second
- **Duration:** 5 minutes

## Symptoms
- Discord alert: "[FIRING] HighLatency"
- Grafana dashboard shows latency spike
- Users reporting slow page loads
- Requests taking longer than usual

## Investigation Steps

### 1. Check Current Latency
```bash
# View Prometheus metrics
open http://localhost:9090
# Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
# Query: histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
```

### 2. Check Grafana Dashboard
```bash
open http://localhost:3000
# Navigate to: Vybe System Dashboard
# Check:
# - Request Latency panel (P50 vs P95)
# - Which instance is slow?
# - CPU usage correlation
# - Memory usage correlation
# - Database connections
# - In-flight requests (queuing?)
```

### 3. Check Application Logs
```bash
# Look for slow requests (duration_ms > 1000)
docker logs vybe_app1 --tail 200 | grep -E '"duration_ms":[0-9]{4,}'
docker logs vybe_app2 --tail 200 | grep -E '"duration_ms":[0-9]{4,}'

# Check for database timeouts
docker logs vybe_app1 -f | grep -i timeout
```

### 4. Check Database Performance
```bash
# Check active queries
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT pid, now() - query_start as duration, state, query 
FROM pg_stat_activity 
WHERE state != 'idle' 
ORDER BY duration DESC 
LIMIT 10;"

# Check database connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;"

# Check for locks
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT * FROM pg_locks WHERE NOT granted;"
```

### 5. Check System Resources
```bash
# Check container CPU and memory
docker stats vybe_app1 vybe_app2 vybe_db vybe_redis --no-stream

# Check Prometheus for resource metrics
# Query: rate(process_cpu_seconds_total{job="vybe"}[5m]) * 100
# Query: container_memory_usage_bytes{name=~"vybe_app.*"}
```

### 6. Check Redis Performance
```bash
# Check Redis latency
docker exec vybe_redis redis-cli --latency

# Check Redis info
docker exec vybe_redis redis-cli info stats | grep -E "(hits|misses)"

# Check slow log
docker exec vybe_redis redis-cli slowlog get 10
```

## Common Causes & Fixes

### Cause 1: Database Slow Queries
**Symptoms:**
- High database connection count
- Long-running queries in pg_stat_activity
- Logs show high duration_ms for specific endpoints

**Fix:**
```bash
# Identify slow queries
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT query, calls, mean_exec_time, max_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;"

# Check for missing indexes
# Review query plans for N+1 queries
# Consider adding indexes or optimizing queries

# Temporary: Kill long-running queries
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' 
AND now() - query_start > interval '5 minutes';"
```

### Cause 2: High CPU Usage
**Symptoms:**
- CPU usage > 80% in docker stats
- All requests slow, not specific endpoints
- Container may be throttled

**Fix:**
```bash
# Check CPU usage
docker stats vybe_app1 vybe_app2 --no-stream

# Restart overloaded instance
docker restart vybe_app1

# Scale horizontally (add more instances)
# Or scale vertically (increase CPU limits)
```

### Cause 3: Memory Pressure / Swapping
**Symptoms:**
- Memory usage near limit
- Increased disk I/O
- Gradual performance degradation

**Fix:**
```bash
# Check memory usage
docker stats vybe_app1 vybe_app2 --no-stream

# Restart instances to clear memory
docker restart vybe_app1 vybe_app2

# Check for memory leaks in application code
# Consider increasing memory limits
```

### Cause 4: Redis Cache Miss / Down
**Symptoms:**
- Increased database load
- Cache hit rate drops
- Latency spike after Redis restart

**Fix:**
```bash
# Check Redis status
docker exec vybe_redis redis-cli ping

# Check cache hit rate
docker exec vybe_redis redis-cli info stats | grep keyspace

# Restart Redis if needed
docker restart vybe_redis

# Warm up cache
# Generate traffic to popular endpoints
```

### Cause 5: Database Connection Pool Exhausted
**Symptoms:**
- Requests queuing waiting for DB connections
- High in-flight requests
- Logs show connection wait times

**Fix:**
```bash
# Check connection pool usage
# (requires application metrics)

# Increase DB_MAX_CONNECTIONS in backend/.env
# Restart app instances
docker restart vybe_app1 vybe_app2

# Or reduce connection timeout
# DB_CONNECTION_TIMEOUT_SECONDS=5
```

### Cause 6: External Dependency Timeout
**Symptoms:**
- Specific endpoints slow
- Timeout errors in logs
- Third-party service issues

**Fix:**
```bash
# Check logs for external API calls
docker logs vybe_app1 --tail 100 | grep -i "timeout\|external"

# Implement circuit breaker
# Add timeouts to external calls
# Consider async processing for slow operations
```

### Cause 7: High Traffic / Load
**Symptoms:**
- High request rate
- All instances showing latency
- In-flight requests increasing

**Fix:**
```bash
# Check request rate
# Prometheus: rate(http_requests_total[1m])

# Scale horizontally (add more app instances)
# Implement rate limiting
# Enable caching for expensive operations
# Consider CDN for static content
```

## Verification Steps

After applying fix:

1. **Check latency drops:**
```bash
# Prometheus query
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1m]))
```

2. **Generate test traffic:**
```bash
# Test response times
for i in {1..20}; do
  time curl -s http://localhost/health > /dev/null
  sleep 1
done
```

3. **Monitor dashboard:**
- P95 latency should drop below 1s
- P50 latency should be <200ms
- No queuing (in-flight requests stable)

4. **Check logs:**
```bash
# Verify duration_ms is normal
docker logs vybe_app1 --tail 50 | grep duration_ms
```

5. **Wait for alert resolution:**
- Check Alertmanager: http://localhost:9093
- Should see "[RESOLVED]" in Discord within 10 minutes

## Escalation

If latency persists after 20 minutes:
1. Check for infrastructure issues (host CPU, disk I/O)
2. Review recent code deployments
3. Consider rolling back recent changes
4. Scale up resources (CPU, memory, instances)
5. Implement emergency caching
6. Escalate to on-call engineer

## Prevention

- Regular database query optimization
- Proper indexing strategy
- Connection pool tuning
- Implement caching layers
- Load testing before deployments
- Monitor P95/P99 latency proactively
- Set up auto-scaling based on latency
- Implement circuit breakers
- Use async processing for slow operations

## Related Alerts
- HighErrorRate
- HighCPUUsage
- HighMemoryUsage
- PostgresTooManyConnections
- PostgresSlowQueries
- RedisDown
