# Incident Response Test Scenarios

This document provides real, executable test scenarios to validate the incident response system. All tests use actual infrastructure - no mocks.

## Prerequisites

```bash
# Ensure system is running
docker compose up -d

# Wait for all services to be healthy
sleep 30
docker compose ps

# Verify baseline metrics
curl http://localhost/metrics
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana
open http://localhost:9093  # Alertmanager
```

---

## Test 1: High Error Rate (Application Failure)

### Objective
Trigger HighErrorRate alert by generating 404 errors.

### Expected Behavior
- Alert fires within 2-3 minutes
- Discord notification received
- Grafana shows error spike
- Logs show 404 errors with request IDs

### Execution
```bash
# Generate 404 errors rapidly
for i in {1..200}; do
  curl -s http://localhost/nonexistent-endpoint-$i &
done
wait

# Wait for alert (2 minutes + 30s group wait)
echo "Waiting for alert to fire..."
sleep 150

# Check Alertmanager
open http://localhost:9093
# Expected: HighErrorRate alert in FIRING state

# Check Discord #alerts channel
# Expected: [FIRING] HighErrorRate notification
```

### Verification
```bash
# Check metrics
curl http://localhost/metrics | grep http_errors_total

# Check logs
docker logs vybe_app1 --tail 50 | grep 404

# Check Grafana
open http://localhost:3000
# Navigate to Vybe System Dashboard
# Error Rate panel should show spike
```

### Cleanup
```bash
# Generate successful requests to clear alert
for i in {1..50}; do
  curl -s http://localhost/health
  sleep 1
done

# Wait for resolution
sleep 180

# Verify resolved
open http://localhost:9093
# Expected: Alert state = RESOLVED
```

---

## Test 2: High Latency (Database Overload)

### Objective
Trigger HighLatency alert by overloading the database.

### Expected Behavior
- P95 latency exceeds 1 second
- Alert fires within 5-7 minutes
- Grafana shows latency spike
- Database connection metrics increase

### Execution
```bash
# Install Apache Bench if not available
# sudo apt-get install apache2-utils  # Linux
# brew install httpd  # macOS

# Generate high load
ab -n 5000 -c 50 http://localhost/health

# Or use curl in parallel
for i in {1..500}; do
  curl -s http://localhost/health &
done
wait

# Wait for alert (5 minutes + 30s group wait)
echo "Waiting for latency alert..."
sleep 330
```

### Verification
```bash
# Check Prometheus latency
open http://localhost:9090
# Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Check Grafana
open http://localhost:3000
# Request Latency panel should show P95 > 1s

# Check Alertmanager
open http://localhost:9093
# Expected: HighLatency alert FIRING
```

### Cleanup
```bash
# Stop generating load
# Wait for system to recover
sleep 300

# Verify latency returns to normal
# Alert should auto-resolve
```

---

## Test 3: Instance Down (Container Failure)

### Objective
Trigger InstanceDown alert by stopping an app container.

### Expected Behavior
- Alert fires within 1.5 minutes
- Discord notification (CRITICAL severity)
- Grafana shows instance offline
- Remaining instance handles all traffic

### Execution
```bash
# Stop one instance
docker stop vybe_app1

# Wait for alert (1 minute + 30s group wait)
echo "Waiting for InstanceDown alert..."
sleep 90

# Check Alertmanager
open http://localhost:9093
# Expected: InstanceDown alert FIRING with severity=critical

# Check Discord
# Expected: [FIRING] InstanceDown notification
```

### Verification
```bash
# Check Prometheus
open http://localhost:9090
# Query: up{job="vybe"}
# Expected: vybe_app1:5000 = 0, vybe_app2:5000 = 1

# Check Grafana
open http://localhost:3000
# Instance Status panel should show one instance DOWN

# Verify traffic still works (via vybe_app2)
curl http://localhost/health
# Should return 200 OK
```

### Cleanup
```bash
# Restart instance
docker start vybe_app1

# Wait for health check
sleep 20

# Verify recovery
curl http://localhost/health
docker compose ps

# Wait for alert resolution
sleep 120

# Check Alertmanager
# Expected: Alert state = RESOLVED
```

---

## Test 4: Database Down (Critical Failure)

### Objective
Trigger PostgresDown alert and verify complete failure handling.

### Expected Behavior
- PostgresDown alert fires within 1.5 minutes
- All app requests return 503
- Readiness check fails
- High5xxRate alert also fires

### Execution
```bash
# Stop database
docker stop vybe_db

# Wait for alert
echo "Waiting for PostgresDown alert..."
sleep 90

# Check Alertmanager
open http://localhost:9093
# Expected: PostgresDown alert FIRING (critical)
# Expected: High5xxRate alert FIRING (critical)
```

### Verification
```bash
# Test application endpoints
curl http://localhost/health
# Expected: 200 OK (health check doesn't require DB)

curl http://localhost/ready
# Expected: 503 Service Unavailable

# Check logs
docker logs vybe_app1 --tail 20
# Expected: Database connection errors

# Check Prometheus
open http://localhost:9090
# Query: up{job="postgres"}
# Expected: 0

# Check Grafana
# Error Rate panel should spike (5xx errors)
# Database Connections panel should show no data
```

### Cleanup
```bash
# Restart database
docker start vybe_db

# Wait for database to be ready
sleep 15

# Verify recovery
curl http://localhost/ready
# Expected: 200 OK

# Wait for alert resolution
sleep 180

# Check Alertmanager
# Expected: Both alerts RESOLVED
```

---

## Test 5: CPU Spike (Resource Exhaustion)

### Objective
Trigger HighCPUUsage alert by stressing the application.

### Expected Behavior
- CPU usage exceeds 80%
- Alert fires within 5-7 minutes
- Grafana shows CPU spike
- Potential latency increase

### Execution
```bash
# Generate CPU-intensive load
# Use stress tool or generate heavy traffic

# Option 1: Heavy traffic
for i in {1..10}; do
  ab -n 10000 -c 100 http://localhost/health &
done
wait

# Option 2: Stress test (if stress tool available)
# docker exec vybe_app1 stress --cpu 4 --timeout 300s
```

### Verification
```bash
# Check container CPU usage
docker stats vybe_app1 vybe_app2 --no-stream

# Check Prometheus
open http://localhost:9090
# Query: rate(process_cpu_seconds_total{job="vybe"}[5m]) * 100

# Check Grafana
# CPU Usage per Container panel should show spike

# Wait for alert
sleep 330

# Check Alertmanager
open http://localhost:9093
# Expected: HighCPUUsage alert FIRING
```

### Cleanup
```bash
# Stop load generation
# CPU should naturally decrease

# Or restart containers
docker restart vybe_app1 vybe_app2

# Wait for recovery
sleep 60
```

---

## Test 6: Memory Pressure (Memory Leak Simulation)

### Objective
Trigger HighMemoryUsage alert.

### Expected Behavior
- Memory usage exceeds 85%
- Alert fires within 5-7 minutes
- Potential OOM kill if severe

### Execution
```bash
# Note: This test is harder to simulate without modifying app code
# Real memory leaks would be detected over time

# Check current memory usage
docker stats vybe_app1 vybe_app2 --no-stream

# Monitor memory growth
watch -n 5 'docker stats vybe_app1 vybe_app2 --no-stream'

# Generate sustained load to increase memory
for i in {1..1000}; do
  curl -s http://localhost/health &
  sleep 0.1
done
```

### Verification
```bash
# Check Prometheus
open http://localhost:9090
# Query: container_memory_usage_bytes{name=~"vybe_app.*"} / container_spec_memory_limit_bytes{name=~"vybe_app.*"} * 100

# Check Grafana
# Memory Usage per Container panel

# If alert fires:
open http://localhost:9093
# Expected: HighMemoryUsage alert FIRING
```

### Cleanup
```bash
# Restart containers to clear memory
docker restart vybe_app1 vybe_app2

# Wait for recovery
sleep 30
```

---

## Test 7: Database Connection Exhaustion

### Objective
Trigger PostgresTooManyConnections alert.

### Expected Behavior
- Connection pool reaches 80% of max
- Alert fires within 5-7 minutes
- New connections may fail

### Execution
```bash
# Check current max connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "SHOW max_connections;"

# Check current connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "SELECT count(*) FROM pg_stat_activity;"

# Generate many concurrent requests to exhaust pool
for i in {1..100}; do
  curl -s http://localhost/health &
done

# Keep connections open
for i in {1..50}; do
  docker exec vybe_db psql -U postgres -d hackathon_db -c "SELECT pg_sleep(60);" &
done
```

### Verification
```bash
# Check connection count
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;"

# Check Prometheus
open http://localhost:9090
# Query: sum(pg_stat_database_numbackends) / pg_settings_max_connections * 100

# Check Grafana
# Database Connections panel
# DB Connection Usage % stat panel

# Wait for alert
sleep 330

# Check Alertmanager
open http://localhost:9093
# Expected: PostgresTooManyConnections alert FIRING
```

### Cleanup
```bash
# Kill idle connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle';"

# Restart app instances
docker restart vybe_app1 vybe_app2

# Wait for recovery
sleep 60
```

---

## Test 8: Redis Failure (Cache Down)

### Objective
Trigger RedisDown alert and verify graceful degradation.

### Expected Behavior
- RedisDown alert fires within 1.5 minutes
- Application continues to work (degraded performance)
- Cache hit rate drops to 0%

### Execution
```bash
# Stop Redis
docker stop vybe_redis

# Wait for alert
echo "Waiting for RedisDown alert..."
sleep 90

# Check Alertmanager
open http://localhost:9093
# Expected: RedisDown alert FIRING
```

### Verification
```bash
# Test application still works
curl http://localhost/health
# Expected: 200 OK

# Check logs for Redis errors
docker logs vybe_app1 --tail 20 | grep -i redis

# Check Prometheus
open http://localhost:9090
# Query: up{job="redis"}
# Expected: 0

# Check Grafana
# Redis Memory Usage panel should show no data
# Redis Hit Rate % should show N/A or 0%
```

### Cleanup
```bash
# Restart Redis
docker start vybe_redis

# Wait for recovery
sleep 10

# Verify recovery
docker exec vybe_redis redis-cli ping
# Expected: PONG

# Wait for alert resolution
sleep 120
```

---

## Test 9: Container Restart Loop

### Objective
Trigger ContainerRestarting alert.

### Expected Behavior
- Alert fires when container restarts frequently
- Indicates application crash loop

### Execution
```bash
# This test requires modifying the app to crash
# Or manually restarting containers repeatedly

# Simulate restart loop
for i in {1..5}; do
  docker restart vybe_app1
  sleep 30
done
```

### Verification
```bash
# Check restart count
docker inspect vybe_app1 | grep RestartCount

# Check Prometheus
open http://localhost:9090
# Query: rate(container_last_seen{name=~"vybe_app.*"}[5m])

# If alert fires:
open http://localhost:9093
# Expected: ContainerRestarting alert FIRING
```

### Cleanup
```bash
# Ensure container is stable
docker compose ps

# If needed, recreate container
docker compose up -d vybe_app1
```

---

## Test 10: Full System Test (Multiple Failures)

### Objective
Test multiple simultaneous failures and alert correlation.

### Expected Behavior
- Multiple alerts fire
- Alert inhibition rules work (critical suppresses warning)
- System remains partially operational

### Execution
```bash
# 1. Stop Redis (non-critical)
docker stop vybe_redis

# 2. Generate high error rate
for i in {1..100}; do
  curl -s http://localhost/nonexistent &
done
wait

# 3. Stop one app instance
docker stop vybe_app1

# Wait for alerts
sleep 150
```

### Verification
```bash
# Check Alertmanager
open http://localhost:9093
# Expected multiple alerts:
# - RedisDown (critical)
# - InstanceDown (critical)
# - HighErrorRate (warning) - may be inhibited

# Check Discord
# Should receive multiple notifications

# Verify system still partially works
curl http://localhost/health
# Should succeed via vybe_app2
```

### Cleanup
```bash
# Restore all services
docker start vybe_redis vybe_app1

# Wait for recovery
sleep 30

# Verify all healthy
docker compose ps

# Generate successful traffic
for i in {1..20}; do
  curl -s http://localhost/health
  sleep 1
done

# Wait for all alerts to resolve
sleep 300
```

---

## Continuous Monitoring Test

### Objective
Verify observability during normal operations.

### Execution
```bash
# Generate realistic traffic pattern
while true; do
  # Successful requests
  for i in {1..10}; do
    curl -s http://localhost/health
  done
  
  # Occasional error
  curl -s http://localhost/nonexistent
  
  sleep 5
done
```

### Verification
```bash
# Monitor Grafana dashboard
open http://localhost:3000

# Verify all panels updating:
# - Request Rate: ~2 req/s
# - Latency: P95 < 100ms
# - Error Rate: ~10% (1 error per 10 requests)
# - CPU Usage: stable
# - Memory Usage: stable
# - Database Connections: stable
# - Redis Hit Rate: increasing over time

# Check logs are structured
docker logs vybe_app1 -f --tail 20

# Verify request IDs present
# Verify duration_ms logged
# Verify status codes logged
```

---

## Success Criteria

All tests pass if:
- ✅ Alerts fire within expected timeframes
- ✅ Discord notifications received
- ✅ Grafana dashboards show accurate data
- ✅ Logs contain structured JSON with request IDs
- ✅ Metrics are accurate and queryable
- ✅ Alerts auto-resolve after issue fixed
- ✅ System remains partially operational during failures
- ✅ Root cause can be identified from logs + metrics alone

## Failure Scenarios

If tests fail:
1. Check Prometheus scrape targets: http://localhost:9090/targets
2. Check Alertmanager config: http://localhost:9093/#/status
3. Check Grafana datasource: http://localhost:3000/datasources
4. Review container logs for errors
5. Verify environment variables are set correctly
6. Check Discord webhook URL is valid
7. Ensure all exporters are running and healthy
