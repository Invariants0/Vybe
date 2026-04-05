# Runbook: Database Down

## Alert Details
- **Alert Name:** PostgresDown
- **Severity:** Critical
- **Threshold:** PostgreSQL unreachable for 1 minute
- **Duration:** 1 minute

## Symptoms
- Discord alert: "[FIRING] PostgresDown"
- All application requests failing with 503
- Readiness check failing
- Logs show: "could not connect to database"
- Grafana shows `up{job="postgres"} == 0`

## Investigation Steps

### 1. Check Database Container Status
```bash
# Check if container is running
docker compose ps db

# Check container details
docker ps -a | grep vybe_db

# Look for:
# - Exited status
# - Restarting status
# - Unhealthy status
```

### 2. Check Database Logs
```bash
# View recent logs
docker logs vybe_db --tail 100

# Follow logs in real-time
docker logs vybe_db -f

# Look for:
# - Crash messages
# - Corruption errors
# - Out of memory
# - Disk space issues
# - Connection errors
```

### 3. Check Database Connectivity
```bash
# Test from host
docker exec vybe_db pg_isready -U postgres

# Test from app container
docker exec vybe_app1 nc -zv db 5432

# Try to connect
docker exec vybe_db psql -U postgres -d hackathon_db -c "SELECT 1;"
```

### 4. Check System Resources
```bash
# Check container resources
docker stats vybe_db --no-stream

# Check disk space
df -h

# Check database volume
docker volume inspect vybe_postgres_data
```

### 5. Check Recent Events
```bash
# Check Docker events
docker events --since 10m --until now | grep vybe_db

# Check restart count
docker inspect vybe_db | grep RestartCount
```

## Common Causes & Fixes

### Cause 1: Database Container Crashed
**Symptoms:**
- Container status: Exited
- Logs show crash or fatal error
- May have restarted automatically

**Fix:**
```bash
# Check exit code
docker inspect vybe_db | grep ExitCode

# View crash logs
docker logs vybe_db --tail 200

# Restart database
docker restart vybe_db

# Wait for startup (can take 10-30 seconds)
sleep 15

# Verify recovery
docker exec vybe_db pg_isready -U postgres

# Check app connectivity
curl http://localhost/ready
```

### Cause 2: Out of Memory (OOM)
**Symptoms:**
- Container killed by OOM killer
- Logs show memory allocation failures
- Docker inspect shows OOMKilled: true

**Fix:**
```bash
# Check OOM status
docker inspect vybe_db | grep OOMKilled

# Check memory usage
docker stats vybe_db --no-stream

# Restart database
docker restart vybe_db

# Consider increasing memory limits in docker-compose.yml
# Or tune PostgreSQL memory settings (shared_buffers, work_mem)
```

### Cause 3: Disk Space Full
**Symptoms:**
- Logs show: "No space left on device"
- Cannot write to database
- Transaction log full

**Fix:**
```bash
# Check disk space
df -h

# Check database volume size
docker exec vybe_db du -sh /var/lib/postgresql/data

# Clean up Docker resources
docker system prune -f

# Remove old logs
docker logs vybe_db --tail 0

# If critical, remove old backups or unused data

# Restart database
docker restart vybe_db
```

### Cause 4: Database Corruption
**Symptoms:**
- Logs show: "invalid page header" or "corrupted"
- Database won't start
- Specific tables inaccessible

**Fix:**
```bash
# Check database integrity
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT datname, pg_database_size(datname) 
FROM pg_database;"

# Try to start in recovery mode
# (requires manual intervention)

# If corruption is severe:
# 1. Stop database
docker stop vybe_db

# 2. Backup current data
docker run --rm -v vybe_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data

# 3. Restore from last known good backup
# (requires backup strategy in place)

# 4. Restart database
docker start vybe_db
```

### Cause 5: Too Many Connections
**Symptoms:**
- Logs show: "too many connections"
- New connections rejected
- Database running but not accepting connections

**Fix:**
```bash
# Check current connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;"

# Check max connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SHOW max_connections;"

# Kill idle connections
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < now() - interval '5 minutes';"

# Restart app instances to reset connection pools
docker restart vybe_app1 vybe_app2

# Consider increasing max_connections or reducing DB_MAX_CONNECTIONS
```

### Cause 6: Network Issues
**Symptoms:**
- Container running but unreachable
- Network connectivity problems
- DNS resolution failures

**Fix:**
```bash
# Check Docker network
docker network inspect vybe_network

# Test connectivity
docker exec vybe_app1 ping -c 3 db

# Recreate network if needed
docker compose down
docker compose up -d

# Or restart just database
docker restart vybe_db
```

### Cause 7: Configuration Error
**Symptoms:**
- Database won't start
- Logs show configuration validation errors
- Invalid postgresql.conf settings

**Fix:**
```bash
# Check configuration
docker exec vybe_db cat /var/lib/postgresql/data/postgresql.conf

# Check environment variables
docker exec vybe_db env | grep POSTGRES

# Fix configuration and restart
docker restart vybe_db

# Or recreate with correct config
docker compose down db
docker compose up -d db
```

## Verification Steps

After applying fix:

1. **Check database status:**
```bash
docker compose ps db

# Should show "healthy"
```

2. **Verify connectivity:**
```bash
docker exec vybe_db pg_isready -U postgres

# Should return: "accepting connections"
```

3. **Test database queries:**
```bash
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT count(*) FROM pg_stat_activity;"

# Should return connection count
```

4. **Check application health:**
```bash
curl http://localhost/ready

# Should return 200 OK with status: "ready"
```

5. **Generate test traffic:**
```bash
# Create a test user
curl -X POST http://localhost/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com"}'

# Should succeed
```

6. **Monitor logs:**
```bash
docker logs vybe_db -f --tail 20

# Should show normal operation, no errors
```

7. **Check Prometheus metrics:**
```bash
open http://localhost:9090
# Query: up{job="postgres"}
# Should show 1

# Query: pg_stat_database_numbackends
# Should show active connections
```

8. **Wait for alert resolution:**
- Check Alertmanager: http://localhost:9093
- Should see "[RESOLVED]" in Discord within 2-3 minutes

## Emergency Procedures

### Complete Database Failure
```bash
# 1. Stop all app instances to prevent connection attempts
docker stop vybe_app1 vybe_app2

# 2. Stop database
docker stop vybe_db

# 3. Backup current state (if possible)
docker run --rm -v vybe_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_emergency_$(date +%Y%m%d_%H%M%S).tar.gz /data

# 4. Try to start database
docker start vybe_db

# 5. If won't start, check logs
docker logs vybe_db --tail 200

# 6. If corruption detected, restore from backup
# (requires backup strategy)

# 7. Start app instances
docker start vybe_app1 vybe_app2

# 8. Monitor recovery
docker compose logs -f
```

### Database Won't Start
```bash
# 1. Remove container (keeps data)
docker rm -f vybe_db

# 2. Recreate from docker-compose
docker compose up -d db

# 3. Monitor startup
docker logs vybe_db -f

# 4. If still fails, check data volume
docker volume inspect vybe_postgres_data

# 5. Consider restoring from backup
```

## Data Recovery

### Restore from Backup
```bash
# 1. Stop database
docker stop vybe_db

# 2. Remove old data volume
docker volume rm vybe_postgres_data

# 3. Recreate volume
docker volume create vybe_postgres_data

# 4. Restore backup
docker run --rm -v vybe_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup_YYYYMMDD_HHMMSS.tar.gz -C /

# 5. Start database
docker start vybe_db

# 6. Verify data
docker exec vybe_db psql -U postgres -d hackathon_db -c "
SELECT count(*) FROM users;"
```

## Escalation

If database cannot be recovered within 15 minutes:
1. Assess data loss risk
2. Check backup availability and age
3. Consider restoring from last known good backup
4. Notify stakeholders of potential data loss
5. Escalate to database administrator
6. Consider failover to replica (if available)
7. Document incident for post-mortem

## Prevention

- Regular automated backups (daily minimum)
- Test backup restoration regularly
- Monitor disk space proactively
- Set appropriate connection limits
- Implement connection pooling
- Monitor database performance metrics
- Set up database replication for HA
- Regular database maintenance (VACUUM, ANALYZE)
- Monitor slow queries
- Implement proper indexing strategy
- Set up database monitoring alerts
- Document recovery procedures

## Related Alerts
- InstanceDown
- HighErrorRate
- PostgresTooManyConnections
- PostgresSlowQueries
- HighLatency
