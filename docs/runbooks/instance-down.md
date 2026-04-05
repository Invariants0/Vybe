# Runbook: Instance Down

## Alert Details
- **Alert Name:** InstanceDown
- **Severity:** Critical
- **Threshold:** Instance unreachable for 1 minute
- **Duration:** 1 minute

## Symptoms
- Discord alert: "[FIRING] InstanceDown"
- Grafana dashboard shows instance offline
- Prometheus shows `up{job="vybe"} == 0`
- Reduced capacity (only 1 instance handling traffic)
- Potential service degradation

## Investigation Steps

### 1. Identify Which Instance is Down
```bash
# Check container status
docker compose ps

# Look for:
# - Exited containers
# - Unhealthy containers
# - Restarting containers

# Check specific instances
docker ps -a | grep vybe_app
```

### 2. Check Container Logs
```bash
# View logs from the down instance
docker logs vybe_app1 --tail 100
docker logs vybe_app2 --tail 100

# Look for:
# - Crash messages
# - Out of memory errors
# - Unhandled exceptions
# - Database connection failures
```

### 3. Check Health Endpoint
```bash
# Try to access health endpoint directly
curl http://localhost/health

# Check if Nginx can reach instances
docker exec vybe_nginx cat /etc/nginx/nginx.conf
```

### 4. Check System Resources
```bash
# Check if container is running
docker inspect vybe_app1 | grep -E "(Status|Running)"

# Check resource usage
docker stats vybe_app1 vybe_app2 --no-stream

# Check host resources
df -h
free -h
```

### 5. Check Recent Events
```bash
# Check Docker events
docker events --since 10m --until now

# Check container restart count
docker inspect vybe_app1 | grep RestartCount
```

## Common Causes & Fixes

### Cause 1: Application Crash
**Symptoms:**
- Container status: Exited
- Logs show unhandled exception or error
- May have restarted automatically

**Fix:**
```bash
# Check exit code
docker inspect vybe_app1 | grep ExitCode

# View crash logs
docker logs vybe_app1 --tail 200

# Restart the instance
docker restart vybe_app1

# Wait for health check
sleep 15

# Verify recovery
curl http://localhost/health
docker compose ps
```

### Cause 2: Out of Memory (OOM)
**Symptoms:**
- Container killed by OOM killer
- Logs show: "Killed" or memory allocation errors
- Docker inspect shows OOMKilled: true

**Fix:**
```bash
# Check OOM status
docker inspect vybe_app1 | grep OOMKilled

# Check memory limits
docker inspect vybe_app1 | grep -A 5 Memory

# Restart with more memory (if needed)
# Edit docker-compose.yml to add memory limits
# Or restart existing instance
docker restart vybe_app1

# Monitor memory usage
docker stats vybe_app1 --no-stream
```

### Cause 3: Health Check Failing
**Symptoms:**
- Container running but marked unhealthy
- Health endpoint returns 503 or times out
- Database or Redis connection issues

**Fix:**
```bash
# Check health status
docker inspect vybe_app1 | grep -A 10 Health

# Test health endpoint directly
docker exec vybe_app1 curl -f http://localhost:5000/health
docker exec vybe_app1 curl -f http://localhost:5000/ready

# Check dependencies
docker exec vybe_db pg_isready -U postgres
docker exec vybe_redis redis-cli ping

# Restart if dependencies are healthy
docker restart vybe_app1
```

### Cause 4: Database Connection Failure
**Symptoms:**
- Logs show: "could not connect to database"
- Readiness check failing
- Container running but not serving traffic

**Fix:**
```bash
# Check database connectivity
docker exec vybe_app1 nc -zv db 5432

# Check database status
docker compose ps db

# Restart database if needed
docker restart vybe_db

# Wait for database to be ready
sleep 10

# Restart app instance
docker restart vybe_app1
```

### Cause 5: Port Conflict or Network Issue
**Symptoms:**
- Container starts but immediately exits
- Logs show: "address already in use"
- Network connectivity issues

**Fix:**
```bash
# Check port usage
netstat -tulpn | grep 5000

# Check Docker network
docker network inspect vybe_network

# Recreate network if needed
docker compose down
docker compose up -d

# Or restart specific instance
docker restart vybe_app1
```

### Cause 6: Configuration Error
**Symptoms:**
- Container exits immediately on start
- Logs show configuration validation errors
- Environment variable issues

**Fix:**
```bash
# Check environment variables
docker exec vybe_app1 env | grep -E "(DATABASE|REDIS|FLASK)"

# Verify .env file
cat backend/.env

# Fix configuration and restart
docker restart vybe_app1
```

### Cause 7: Disk Space Full
**Symptoms:**
- Cannot write logs
- Database writes failing
- Container cannot start

**Fix:**
```bash
# Check disk space
df -h

# Clean up Docker resources
docker system prune -f

# Remove old logs
docker logs vybe_app1 --tail 0

# Restart instance
docker restart vybe_app1
```

## Verification Steps

After applying fix:

1. **Check container status:**
```bash
docker compose ps

# All services should show "healthy" or "running"
```

2. **Verify health endpoints:**
```bash
curl http://localhost/health
curl http://localhost/ready

# Both should return 200 OK
```

3. **Check Prometheus metrics:**
```bash
open http://localhost:9090
# Query: up{job="vybe"}
# Should show 1 for both instances
```

4. **Generate test traffic:**
```bash
for i in {1..20}; do
  curl -s http://localhost/health
  sleep 1
done

# All requests should succeed
```

5. **Monitor logs:**
```bash
docker logs vybe_app1 -f --tail 20
docker logs vybe_app2 -f --tail 20

# Should see normal request logs
```

6. **Wait for alert resolution:**
- Check Alertmanager: http://localhost:9093
- Should see "[RESOLVED]" in Discord within 2-3 minutes

7. **Check Grafana dashboard:**
- Both instances should show in metrics
- Request rate should be distributed
- No error spikes

## Emergency Procedures

### If Both Instances Down (Complete Outage)
```bash
# 1. Check all dependencies first
docker compose ps

# 2. Restart entire stack if needed
docker compose restart

# 3. Or restart just app instances
docker restart vybe_app1 vybe_app2

# 4. Monitor recovery
watch -n 2 'docker compose ps'

# 5. Check logs for errors
docker compose logs -f vybe_app1 vybe_app2
```

### If Instance Won't Start
```bash
# 1. Stop the problematic instance
docker stop vybe_app1

# 2. Check and fix issues (logs, config, resources)

# 3. Remove container if corrupted
docker rm vybe_app1

# 4. Recreate from docker-compose
docker compose up -d vybe_app1

# 5. Monitor startup
docker logs vybe_app1 -f
```

## Escalation

If instance cannot be recovered within 10 minutes:
1. Check host system health (CPU, memory, disk)
2. Review recent deployments or changes
3. Consider rolling back to previous version
4. Check for infrastructure issues (cloud provider)
5. Scale up remaining instances to handle load
6. Escalate to on-call engineer
7. Consider maintenance mode if critical

## Prevention

- Implement proper health checks
- Set appropriate resource limits (CPU, memory)
- Monitor resource usage proactively
- Implement graceful shutdown
- Use circuit breakers for dependencies
- Regular load testing
- Automated recovery mechanisms
- Proper error handling in application
- Monitor container restart rates
- Set up auto-scaling

## Related Alerts
- HighErrorRate
- HighLatency
- ContainerRestarting
- HighMemoryUsage
- PostgresDown
- RedisDown
