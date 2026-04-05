# Deployment Guide

This guide covers deploying Vybe from local development through production, including rollback procedures and monitoring integration.

---

## Local Development

### Prerequisites

- Docker and Docker Compose (2.20+)
- Git
- RAM: 2GB minimum
- Disk: 500MB free

### Setup

1. Clone repository:

```bash
git clone https://github.com/Invariants0/Vybe.git
cd Vybe
```

2. Create environment file:

```bash
cp backend/.env.example backend/.env
```

3. Review and adjust defaults in `.env`:

```bash
cat backend/.env
```

Expected variables:
```
FLASK_ENV=development
FLASK_DEBUG=true
DATABASE_NAME=hackathon_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
AUTO_CREATE_TABLES=true
LOG_LEVEL=DEBUG
REDIS_ENABLED=false
```

4. Start all services:

```bash
docker compose up --build
```

This builds images and starts:
- Flask app (2 instances on port 5000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Nginx (port 8080)
- Prometheus (port 9090)
- Grafana (port 3000)

5. Verify health:

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{"status": "healthy"}
```

6. Access services:

- **Frontend:** http://localhost:8080
- **API (via Nginx):** http://localhost:8080/api/v1/links
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)

### First Request

Create a short link:

```bash
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com/very/long/url/that/needs/shortening",
    "custom_alias": "demo"
  }'
```

Expected response (201 Created):
```json
{
  "id": 1,
  "code": "demo",
  "short_url": "http://localhost:8080/demo",
  "original_url": "https://www.example.com/very/long/url/that/needs/shortening",
  "is_active": true,
  "click_count": 0,
  "created_at": "2026-04-05T10:00:00+00:00"
}
```

### Stopping Services

```bash
docker compose down
```

To remove volumes (database data):

```bash
docker compose down -v
```

---

## Container Image Build

### Build Images Manually

Frontend image:

```bash
docker build \
  -f infra/docker/frontend.dockerfile \
  -t vybe-frontend:latest .
```

Backend image:

```bash
docker build \
  -f infra/docker/backend.dockerfile \
  -t vybe-backend:latest .
```

Or let docker-compose build them:

```bash
docker compose build --no-cache
```

### Push to Registry

After building, push to Docker Hub, ECR, or other registry:

```bash
# Docker Hub example
docker tag vybe-backend:latest myusername/vybe-backend:latest
docker tag vybe-frontend:latest myusername/vybe-frontend:latest

docker login

docker push myusername/vybe-backend:latest
docker push myusername/vybe-frontend:latest
```

For GitHub Container Registry:

```bash
docker tag vybe-backend:latest ghcr.io/myusername/vybe-backend:latest
docker tag vybe-frontend:latest ghcr.io/myusername/vybe-frontend:latest

echo $GITHUB_TOKEN | docker login ghcr.io -u myusername --password-stdin

docker push ghcr.io/myusername/vybe-backend:latest
docker push ghcr.io/myusername/vybe-frontend:latest
```

---

## Production Deployment

### Prerequisites

- Docker and Docker Compose on target VM/server
- PostgreSQL 16 (managed service or self-hosted) with DNS endpoint
- Redis 7 (managed service or self-hosted) with DNS endpoint, or disabled
- Persistent volume for PostgreSQL data (if self-hosted)
- SSL/TLS certificates for HTTPS (if required)
- Network security groups allowing inbound 443 (HTTPS) and 80 (HTTP, redirect only)
- Monitor infrastructure: Prometheus instance (can be same server or separate)

### Pre-Deployment Checklist

Before deploying to production:

- [ ] Database backups tested (restore procedure documented and verified)
- [ ] Container images pushed to registry with version tags (`v1.0.0`, not `latest`)
- [ ] Environment variables prepared:
  - [ ] DATABASE_URL (production PostgreSQL connection string)
  - [ ] REDIS_URL (production Redis connection string, if enabled)
  - [ ] SECRET_KEY (strong random value, different from development)
  - [ ] BASE_URL (production domain, e.g., `https://links.example.com`)
  - [ ] LOG_LEVEL (INFO or WARNING, not DEBUG)
  - [ ] FLASK_ENV=production
  - [ ] FLASK_DEBUG=false
  - [ ] All other production-specific settings reviewed
- [ ] SSL/TLS certificates installed on Nginx (or use cloud load balancer)
- [ ] Monitoring credentials prepared (Prometheus scrape auth, if required)
- [ ] Alerting configured (webhook URLs for Discord, PagerDuty, etc.)
- [ ] Architecture reviewed (load balancer, database backup, recovery strategy)
- [ ] Incident runbooks distributed to on-call team

### Step 1: Configure External Database

If using managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.):

1. Create database instance:
   - Engine: PostgreSQL 16
   - Publicly accessible: No (only from app VPC)
   - Backup retention: 30 days minimum
   - Multi-AZ failover: If SLA requires >99.5% uptime

2. Create database and user:

```sql
CREATE DATABASE vybe;
CREATE USER vybe_user WITH PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE vybe TO vybe_user;
```

3. Record connection string:

```
postgres://vybe_user:strong-password-here@db.example.com:5432/vybe
```

4. Test connection from app server:

```bash
psql -h db.example.com -U vybe_user -d vybe -c "SELECT 1"
```

### Step 2: Prepare Environment Variables

Create `.env.production` file on target server:

```bash
cat > /opt/vybe/.env.production << 'EOF'
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=use-strong-random-value-here-min-32-chars
DATABASE_URL=postgres://vybe_user:password@db.example.com:5432/vybe
DATABASE_NAME=vybe
DATABASE_USER=vybe_user
DATABASE_PASSWORD=password
DATABASE_HOST=db.example.com
DATABASE_PORT=5432
DB_MAX_CONNECTIONS=20
LOG_LEVEL=INFO
BASE_URL=https://links.example.com
REDIS_ENABLED=true
REDIS_URL=redis://redis.example.com:6379
REDIS_PASSWORD=strong-redis-password
AUTO_CREATE_TABLES=false
EVENT_LOG_SAMPLE_RATE=0.1
EOF
```

Secure the file:

```bash
chmod 600 /opt/vybe/.env.production
```

### Step 3: Deploy with Docker Compose

1. Clone repository on target server:

```bash
git clone https://github.com/Invariants0/Vybe.git /opt/vybe
cd /opt/vybe
```

2. Update docker-compose.yml to use images from registry (optional):

Edit the `image` fields to point to your registry instead of building locally:

```yaml
services:
  vybe_app1:
    image: ghcr.io/myusername/vybe-backend:v1.0.0
    env_file:
      - ./backend/.env.production
    # ... rest of config

  vybe_frontend:
    image: ghcr.io/myusername/vybe-frontend:v1.0.0
    # ... rest of config
```

3. Load environment variables:

```bash
export $(cat /opt/vybe/.env.production | xargs)
```

4. Start services:

```bash
docker compose up -d
```

5. Verify all containers started:

```bash
docker compose ps
```

Expected output:
```
CONTAINER      STATUS
vybe_app1      healthy
vybe_app2      healthy
vybe_db        N/A (external)
vybe_redis     healthy
vybe_frontend  running
vybe_nginx     running
prometheus     running
grafana        running
```

6. Test API health:

```bash
curl https://links.example.com/health
```

Expected response: `{"status": "healthy"}`

7. Test readiness:

```bash
curl https://links.example.com/ready
```

Expected response: `{"status": "ready", "checks": {"database": "ok", "redis": "ok"}}`

### Step 4: Initialize Database (First Deploy Only)

If this is the first deployment and database is empty:

1. Connect to database:

```bash
docker exec vybe_app1 bash
```

2. Run migrations:

```bash
python scripts/init_db.py
```

This creates all tables. If `AUTO_CREATE_TABLES=true` in Flask config, tables are created on first request.

3. Verify tables created:

```bash
psql -h db.example.com -U vybe_user -d vybe

\dt

# Expected output: shows tables like 'users', 'urls', 'events'
```

### Step 5: Configure Monitoring

1. Update Prometheus to scrape production endpoints:

Edit `monitoring/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'vybe_app'
    static_configs:
      - targets: ['links.example.com:8000']
    scheme: https  # If using HTTPS for metrics endpoint
```

2. Restart Prometheus:

```bash
docker compose restart prometheus
```

3. Verify scraping in Prometheus UI:

```
http://prometheus.example.com:9090/targets
```

All targets should show "UP".

### Step 6: Configure Alerts

1. Update AlertManager webhook URLs:

Edit `monitoring/alertmanager/alertmanager.yml`:

```yaml
routes:
  - match:
      alertname: InstanceDown
    receiver: 'pagerduty'
    repeat_interval: 15m
  - match:
      alertname: HighErrorRate
    receiver: 'discord'
    repeat_interval: 30m
```

2. Add receivers:

```yaml
receivers:
  - name: 'discord'
    webhook_configs:
      - url: 'https://discordapp.com/api/webhooks/...'
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
```

3. Restart AlertManager:

```bash
docker compose restart alertmanager
```

### Step 7: Configure TLS/SSL

If not using cloud load balancer:

1. Obtain certificates (Let's Encrypt recommended):

```bash
# Using certbot with Docker
docker run --rm -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d links.example.com -d www.links.example.com
```

2. Update Nginx config to use certificates:

Edit `infra/nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl;
    server_name links.example.com;

    ssl_certificate /etc/letsencrypt/live/links.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/links.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name links.example.com;
    return 301 https://$server_name$request_uri;
}
```

3. Mount certificates in docker-compose.yml:

```yaml
nginx:
  volumes:
    - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

4. Restart Nginx:

```bash
docker compose restart nginx
```

---

## Verification Post-Deployment

### Health Checks

Run these checks after deployment:

```bash
# 1. Health endpointto
curl https://links.example.com/health
# Expected: {"status": "healthy"}

# 2. Readiness endpoint
curl https://links.example.com/ready
# Expected: {"status": "ready", ...}

# 3. Create test link
curl -X POST https://links.example.com/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_alias": "test"}'
# Expected: 201 with link details

# 4. Access test link
curl -L https://links.example.com/test
# Expected: 302 redirect to https://example.com

# 5. Monitor metrics
curl https://links.example.com/metrics | head -20
# Expected: Prometheus metrics output
```

### Monitoring Checks

1. Open Grafana: http://prometheus.example.com:3000
2. Check dashboard > Overview
3. All components should show green status
4. Check Prometheus > Targets: all should be "UP"
5. Create test alert to verify notification routing

---

## Scaling for Production

### Horizontal Scaling

To handle more traffic:

1. **Add Flask instances:**

Edit docker-compose.yml to add more app instances:

```yaml
  vybe_app3:
    image: ghcr.io/myusername/vybe-backend:v1.0.0
    depends_on: vybe_db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/ready"]

  vybe_app4:
    image: ghcr.io/myusername/vybe-backend:v1.0.0
    depends_on: vybe_db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/ready"]
```

2. Nginx automatically load balances to all healthy instances.

3. Restart:

```bash
docker compose up -d
```

### Vertical Scaling

To increase per-instance capacity:

1. Increase Gunicorn workers:

```bash
# In .env.production
WORKERS=8  # from default 2
```

2. Increase container resources in docker-compose.yml:

```yaml
vybe_app1:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

3. Restart:

```bash
docker compose up -d
```

---

## Rolling Update (Zero Downtime)

To deploy a new version without downtime:

1. Build new image:

```bash
docker build -f infra/docker/backend.dockerfile \
  -t ghcr.io/myusername/vybe-backend:v1.0.1 .
```

2. Push to registry:

```bash
docker push ghcr.io/myusername/vybe-backend:v1.0.1
```

3. Update docker-compose.yml:

```yaml
  vybe_app1:
    image: ghcr.io/myusername/vybe-backend:v1.0.1
  vybe_app2:
    image: ghcr.io/myusername/vybe-backend:v1.0.1
```

4. Restart services (Docker Compose restarts one at a time):

```bash
docker compose up -d
```

Nginx continues routing traffic to healthy instances while old containers are replaced.

5. Verify:

```bash
docker compose ps
# All should show healthy after 90 seconds
```

---

## Rollback Procedure

If a deployment causes issues:

1. Identify the issue:

```bash
docker compose logs vybe_app1 | tail -50
```

2. Revert docker-compose.yml to previous version:

```bash
git checkout HEAD^ -- docker-compose.yml
```

3. Restart with previous image:

```bash
docker compose up -d
```

4. Verify:

```bash
curl https://links.example.com/ready
```

5. Investigate root cause from logs before retrying new deployment.

---

## Database Migrations

For schema changes in future versions:

1. Create migration file:

```bash
touch scripts/migrations/001_add_user_preferences.sql
```

2. Define migration:

```sql
ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}';
CREATE INDEX idx_users_preferences ON users (preferences);
```

3. Apply migration:

```bash
psql -h db.example.com -U vybe_user -d vybe < scripts/migrations/001_add_user_preferences.sql
```

4. Update ORM models in Python to match schema.

5. Test changes locally before production deployment.

---

## Disaster Recovery

### Database Backup

Regular automated backups are essential:

```bash
# Manual backup (run weekly at minimum)
pg_dump -h db.example.com -U vybe_user vybe | gzip > vybe_backup_$(date +%Y%m%d).sql.gz

# Store backups in S3 or backup service
aws s3 cp vybe_backup_$(date +%Y%m%d).sql.gz s3://backups/vybe/
```

### Database Restore

If database is lost:

```bash
# Download backup
aws s3 cp s3://backups/vybe/vybe_backup_20260405.sql.gz .

# Decompress
gunzip vybe_backup_20260405.sql.gz

# Restore to empty database
psql -h db.example.com -U vybe_user -d vybe < vybe_backup_20260405.sql
```

This restores all links, users, and analytics data to the backup point in time.

### Container Loss

If containers are lost:

```bash
# Rebuild and restart
docker compose down
docker compose pull
docker compose up -d
```

All data is in database (PostgreSQL) and cache (Redis), so it persists across container restarts.

---

## Troubleshooting Deployment Issues

### Containers won't start

**Issue:** `docker compose up -d` fails

**Solution:**
```bash
# Check logs
docker compose logs

# Common causes:
# 1. Port already in use
sudo lsof -i :8080
# Kill process on port 8080

# 2. Insufficient disk space
df -h

# 3. Network issues
docker network ls
```

### Database connection fails

**Issue:** App shows "Database temporarily unavailable"

**Solution:**
```bash
# Verify database is accessible
psql -h db.example.com -U vybe_user -d vybe -c "SELECT 1"

# Check environment variables
docker compose exec vybe_app1 env | grep DATABASE

# Verify firewall allows connection
nc -zv db.example.com 5432
```

### Monitoring not scraping

**Issue:** Prometheus targets show "DOWN"

**Solution:**
```bash
# Verify metrics endpoint is accessible
curl http://vybe_app1:8000/metrics

# Check Prometheus config syntax
docker exec vybe_prometheus promtool check config /etc/prometheus/prometheus.yml

# Restart Prometheus
docker compose restart prometheus
```

For more troubleshooting steps, see [troubleshooting.md](troubleshooting.md).

