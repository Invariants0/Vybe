# Monitoring Stack

This directory contains the complete observability stack for the Vybe URL shortener application.

## Components

### Prometheus (Metrics Collection)
- **Version:** v2.52.0
- **Port:** 9090
- **Purpose:** Collects and stores time-series metrics
- **Config:** `prometheus/prometheus.yml`
- **Alerts:** `prometheus/alerts.yml`

### Grafana (Visualization)
- **Version:** 10.4.2
- **Port:** 3000
- **Credentials:** admin/admin
- **Purpose:** Visualizes metrics in dashboards
- **Dashboard:** `grafana/dashboards/system-dashboard.json`

### Alertmanager (Alerting)
- **Version:** v0.27.0
- **Port:** 9093
- **Purpose:** Manages and routes alerts
- **Config:** `alertmanager/alertmanager.yml`
- **Notifications:** Discord webhook

### Exporters

#### Node Exporter (System Metrics)
- **Version:** v1.8.0
- **Port:** 9100
- **Purpose:** Host-level metrics (CPU, memory, disk, network)

#### cAdvisor (Container Metrics)
- **Version:** v0.49.1
- **Port:** 8080
- **Purpose:** Per-container resource usage

#### PostgreSQL Exporter (Database Metrics)
- **Version:** v0.15.0
- **Port:** 9187
- **Purpose:** Database connections, queries, performance

#### Redis Exporter (Cache Metrics)
- **Version:** v1.58.0
- **Port:** 9121
- **Purpose:** Cache hit rate, memory usage, evictions

## Quick Start

### 1. Configure Environment Variables

Edit `backend/.env`:
```bash
# Required: Discord webhook for alerts
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# Optional: Sentry for error tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
```

### 2. Start the Stack

```bash
# Start all services
docker compose up -d

# Wait for services to be healthy (30-60 seconds)
docker compose ps

# Verify all services are running
```

### 3. Access Dashboards

- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

### 4. Verify Metrics Collection

```bash
# Check Prometheus targets
open http://localhost:9090/targets

# All targets should be UP:
# - vybe (2 app instances)
# - node_exporter
# - cadvisor
# - postgres
# - redis
# - prometheus
```

### 5. View Dashboard

1. Open Grafana: http://localhost:3000
2. Navigate to: Dashboards → Vybe System Dashboard
3. Verify all panels show data

## Metrics Available

### Application Metrics
- `http_requests_total` - Total HTTP requests
- `http_errors_total` - Total HTTP errors (4xx, 5xx)
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Current in-flight requests

### System Metrics
- `container_cpu_usage_seconds_total` - CPU usage per container
- `container_memory_usage_bytes` - Memory usage per container
- `container_last_seen` - Container restart tracking

### Database Metrics
- `pg_stat_database_numbackends` - Active database connections
- `pg_settings_max_connections` - Max connection limit
- `pg_stat_database_tup_fetched` - Rows fetched
- `pg_stat_database_tup_returned` - Rows returned

### Cache Metrics
- `redis_memory_used_bytes` - Redis memory usage
- `redis_memory_max_bytes` - Redis memory limit
- `redis_keyspace_hits_total` - Cache hits
- `redis_keyspace_misses_total` - Cache misses
- `redis_evicted_keys_total` - Evicted keys

## Alerts

### Application Alerts
- **HighErrorRate** - Error rate > 5% for 2 minutes
- **High5xxRate** - 5xx error rate > 2% for 2 minutes
- **HighLatency** - P95 latency > 1s for 5 minutes
- **InstanceDown** - Instance unreachable for 1 minute

### System Alerts
- **HighCPUUsage** - CPU > 80% for 5 minutes
- **HighMemoryUsage** - Memory > 85% for 5 minutes
- **ContainerRestarting** - Container restarting frequently

### Database Alerts
- **PostgresTooManyConnections** - Connections > 80% for 5 minutes
- **PostgresDown** - Database unreachable for 1 minute
- **PostgresSlowQueries** - Query efficiency low for 10 minutes

### Cache Alerts
- **RedisDown** - Redis unreachable for 1 minute
- **RedisHighMemoryUsage** - Memory > 90% for 5 minutes
- **RedisHighEvictionRate** - Evicting > 10 keys/sec for 5 minutes

## Testing Alerts

See `docs/runbooks/test-scenarios.md` for complete test procedures.

Quick test:
```bash
# Stop an instance to trigger InstanceDown alert
docker stop vybe_app1

# Wait 90 seconds
sleep 90

# Check Alertmanager
open http://localhost:9093

# Check Discord for notification

# Restore instance
docker start vybe_app1
```

## Troubleshooting

### Prometheus Not Scraping Targets

```bash
# Check Prometheus logs
docker logs vybe_prometheus

# Check target status
open http://localhost:9090/targets

# Verify network connectivity
docker exec vybe_prometheus wget -O- http://vybe_app1:5000/metrics
```

### Alerts Not Firing

```bash
# Check Alertmanager logs
docker logs vybe_alertmanager

# Verify alert rules loaded
open http://localhost:9090/alerts

# Check Alertmanager config
docker exec vybe_alertmanager cat /etc/alertmanager/config.yml
```

### Discord Notifications Not Working

```bash
# Verify webhook URL is set
docker exec vybe_alertmanager env | grep DISCORD

# Test webhook manually
curl -X POST "${DISCORD_WEBHOOK_URL}/slack" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test notification"}'

# Check Alertmanager logs
docker logs vybe_alertmanager | grep -i discord
```

### Grafana Dashboard Not Showing Data

```bash
# Check Grafana logs
docker logs vybe_grafana

# Verify datasource connection
# Grafana → Configuration → Data Sources → Prometheus
# Click "Test" button

# Check Prometheus is accessible
docker exec vybe_grafana wget -O- http://prometheus:9090/api/v1/query?query=up
```

### Exporters Not Working

```bash
# Check exporter logs
docker logs vybe_node_exporter
docker logs vybe_cadvisor
docker logs vybe_postgres_exporter
docker logs vybe_redis_exporter

# Test exporter endpoints
curl http://localhost:9100/metrics  # node_exporter
curl http://localhost:8080/metrics  # cadvisor
curl http://localhost:9187/metrics  # postgres_exporter
curl http://localhost:9121/metrics  # redis_exporter
```

## Configuration Files

### Prometheus
- `prometheus/prometheus.yml` - Main configuration
- `prometheus/alerts.yml` - Alert rules

### Grafana
- `grafana/provisioning/datasources/datasources.yml` - Datasource config
- `grafana/provisioning/dashboards/dashboards.yml` - Dashboard provisioning
- `grafana/dashboards/system-dashboard.json` - Main dashboard

### Alertmanager
- `alertmanager/alertmanager.yml` - Alert routing and receivers
- `alertmanager/entrypoint.sh` - Environment variable substitution

## Customization

### Adding New Alerts

1. Edit `prometheus/alerts.yml`
2. Add new alert rule:
```yaml
- alert: MyNewAlert
  expr: my_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Alert summary"
    description: "Alert description"
```
3. Restart Prometheus: `docker restart vybe_prometheus`

### Adding Dashboard Panels

1. Edit `grafana/dashboards/system-dashboard.json`
2. Add new panel configuration
3. Restart Grafana: `docker restart vybe_grafana`
4. Or use Grafana UI and export JSON

### Changing Alert Thresholds

1. Edit `prometheus/alerts.yml`
2. Modify `expr` or `for` values
3. Restart Prometheus: `docker restart vybe_prometheus`

## Maintenance

### Backup Prometheus Data

```bash
# Backup Prometheus data volume
docker run --rm -v vybe_prometheus_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus_backup_$(date +%Y%m%d).tar.gz /data
```

### Backup Grafana Dashboards

```bash
# Backup Grafana data volume
docker run --rm -v vybe_grafana_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana_backup_$(date +%Y%m%d).tar.gz /data
```

### Clean Up Old Data

```bash
# Prometheus retains data for 15 days by default
# To change retention, edit docker-compose.yml:
# command:
#   - "--storage.tsdb.retention.time=30d"
```

## Security Considerations

1. **Webhook URL:** Never commit `DISCORD_WEBHOOK_URL` to version control
2. **Grafana Password:** Change default admin password in production
3. **Network Exposure:** Monitoring ports should not be exposed to public internet
4. **Sentry DSN:** Keep `SENTRY_DSN` secret
5. **Database Credentials:** Use strong passwords in production

## Performance Impact

- **Prometheus:** ~100-200MB memory, minimal CPU
- **Grafana:** ~100-150MB memory, minimal CPU
- **Alertmanager:** ~50MB memory, minimal CPU
- **Node Exporter:** ~10MB memory, minimal CPU
- **cAdvisor:** ~100MB memory, minimal CPU
- **PostgreSQL Exporter:** ~20MB memory, minimal CPU
- **Redis Exporter:** ~10MB memory, minimal CPU

Total overhead: ~400-500MB memory

## Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Incident Response Runbooks](../docs/runbooks/)
- [Test Scenarios](../docs/runbooks/test-scenarios.md)
