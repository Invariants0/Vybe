# Configuration Reference

All Vybe configuration is controlled through environment variables. This document lists every variable, its purpose, default value, and production recommendations.

---

## Environment Variables

### Flask Application

**FLASK_ENV**
- Description: Deployment environment
- Values: `development`, `production`
- Default: `development`
- Required: Yes
- Production: `production`
- Notes: Controls logging verbosity, debug features, and error messages

**FLASK_DEBUG**
- Description: Enable/disable debug mode
- Values: `true`, `false`
- Default: `false`
- Required: No
- Production: `false`
- Notes: If true, app reloads on code changes (for development only). Never true in production.

**SECRET_KEY**
- Description: Secret for session/token signing
- Values: Any random string (minimum 32 characters)
- Default: `change-me` (INSECURE)
- Required: Yes
- Production: Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Notes: Used for signing cookies and tokens. Must be random and unique per deployment.

**APP_NAME**
- Description: Application identifier
- Values: Any string
- Default: `vybe-shortener`
- Required: No
- Production: `vybe-shortener` (or custom name)
- Notes: Used in logs and monitoring labels

**BASE_URL**
- Description: Public URL prefix for generated short links
- Values: Full URL with protocol (http:// or https://)
- Default: `http://localhost:5000`
- Required: Yes
- Production: `https://links.example.com` (your domain)
- Notes: When user creates link, `short_url` is `{BASE_URL}/{code}`

**LOG_LEVEL**
- Description: Minimum logging level
- Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Default: `INFO`
- Required: No
- Production: `INFO` (or `WARNING` if very high volume)
- Notes: DEBUG logs internal state (slow on high throughput)

---

### Database Configuration

**DATABASE_HOST**
- Description: PostgreSQL server hostname/IP
- Values: Hostname or IP address
- Default: `localhost`
- Required: Yes
- Production: Your managed database endpoint (e.g., `db-instance.c.us-east-1.rds.amazonaws.com`)
- Notes: Must be network accessible from app containers

**DATABASE_PORT**
- Description: PostgreSQL server port
- Values: Integer 1-65535
- Default: `5432`
- Required: No (5432 is standard)
- Production: `5432`
- Notes: Standard PostgreSQL port

**DATABASE_USER**
- Description: PostgreSQL user login
- Values: Username string
- Default: `postgres`
- Required: Yes
- Production: Create dedicated user (not `postgres`), e.g., `vybe_user`
- Notes: User must have CREATE, SELECT, INSERT, UPDATE, DELETE on database

**DATABASE_PASSWORD**
- Description: PostgreSQL user password
- Values: String
- Default: `postgres`
- Required: Yes
- Production: Generate strong password: `openssl rand -base64 32`
- Notes: Never use default password in production

**DATABASE_NAME**
- Description: PostgreSQL database name
- Values: Database identifier
- Default: `hackathon_db`
- Required: Yes
- Production: `vybe` or similar
- Notes: Database must exist before app starts

**DATABASE_URL** (Alternative to individual DATABASE_* vars)
- Description: Full PostgreSQL connection string
- Values: `postgresql://user:password@host:port/database`
- Default: None (falls back to individual vars)
- Required: No
- Production: Use this if your deployment platform provides it (Heroku, etc.)
- Example: `postgresql://vybe_user:secure-pass@db.example.com:5432/vybe`
- Notes: If set, overrides individual DATABASE_* variables

**DB_MAX_CONNECTIONS**
- Description: Maximum database connections per app instance
- Values: Integer (10-50)
- Default: `20`
- Required: No
- Production: `20` (conservative) or `30` if handling >1000 RPS
- Notes: Each app instance has its own pool. 2 instances = 40 total connections. Total must be < PostgreSQL `max_connections` (default 100)

**DB_STALE_TIMEOUT_SECONDS**
- Description: Time before idle connection is considered stale
- Values: Integer (60-3600)
- Default: `300` (5 minutes)
- Required: No
- Production: `300`
- Notes: Prevents keeping dead connections. Set equal to your database's `idle_in_transaction_session_timeout`

**DB_CONNECTION_TIMEOUT_SECONDS**
- Description: Time to wait for database connection
- Values: Integer (2-30)
- Default: `10`
- Required: No
- Production: `10`
- Notes: If database doesn't respond in this time, connection fails

**AUTO_CREATE_TABLES**
- Description: Automatically create database tables on startup
- Values: `true`, `false`
- Default: `false`
- Required: No
- Production: `false`
- Notes: Set to `true` only for local development. In production, run migrations manually before startup.

---

### URL Shortening Configuration

**DEFAULT_SHORT_CODE_LENGTH**
- Description: Length of auto-generated short codes
- Values: Integer (4-20)
- Default: `7`
- Required: No
- Production: `7`
- Notes: Longer codes = lower collision probability, but reduced branding appeal. 7 chars gives ~223 trillion unique codes.

**MAX_CUSTOM_ALIAS_LENGTH**
- Description: Maximum length of custom alias
- Values: Integer (5-50)
- Default: `32`
- Required: No
- Production: `32`
- Notes: Balances URL length with user flexibility

**MAX_URL_LENGTH**
- Description: Maximum length of original URL to shorten
- Values: Integer (100-4096)
- Default: `2048`
- Required: No
- Production: `2048`
- Notes: Most browsers support URLs up to 2048 chars. Increase if needed, but HTTP servers may reject longer URLs.

**DEFAULT_REDIRECT_STATUS_CODE**
- Description: HTTP status code for redirects
- Values: `301` (permanent), `302` (temporary), `307` (temporary with method preservation)
- Default: `302`
- Required: No
- Production: `302`
- Notes: Use `301` if short links permanent. Use `302` if planning to change targets.

---

### Caching Configuration

**REDIS_ENABLED**
- Description: Enable/disable Redis caching
- Values: `true`, `false`
- Default: `false`
- Required: No
- Production: `true` if throughput >100 RPS
- Notes: System works fine without Redis (falls back to database). Optional for graceful degradation.

**REDIS_URL**
- Description: Redis connection string
- Values: `redis://[:password]@host:port/db` format
- Default: Empty (Redis disabled)
- Required: Only if REDIS_ENABLED=true
- Production: `redis://:password@redis.example.com:6379/0`
- Example: `redis://:myredispassword@cache.example.com:6379/0`
- Notes: If left empty and REDIS_ENABLED=true, connection fails. Ensure password is URL-encoded if it contains special characters.

**REDIS_PASSWORD**
- Description: Redis authentication password (if using simple config)
- Values: String
- Default: Empty
- Required: Only if Redis requires password
- Production: Generate strong password: `openssl rand -base64 32`
- Notes: Use REDIS_URL instead if that format is clearer

**REDIS_DEFAULT_TTL_SECONDS**
- Description: Time-to-live for cached values
- Values: Integer (60-7200)
- Default: `300` (5 minutes)
- Required: No
- Production: `300`
- Notes: After this time, cache expires and next query hits database

---

### Monitoring & Observability

**Event Logging**

**EVENT_LOG_SAMPLE_RATE**
- Description: Fraction of events to log to database
- Values: Float 0.0-1.0
- Default: `1.0` (log all)
- Required: No
- Production: `0.1` (10%) at >1000 RPS, `1.0` at lower traffic
- Notes: Reduce from 1.0 to prevent database from filling with events on high traffic. At 0.1, you'll still get representative data but 10x less storage.

---

### Optional Integrations (Future)

**SENTRY_DSN** (Planned)
- Description: Sentry error tracking endpoint
- Values: Sentry DSN URL
- Default: None
- Required: No
- Production: Your Sentry project DSN if using error tracking
- Example: `https://examplePublicKey@o0.ingest.sentry.io/0`

**DISCORD_WEBHOOK_URL** (Planned)
- Description: Discord webhook for alerts
- Values: Discord webhook URL
- Default: None
- Required: No
- Production: Your Discord webhook URL for alert routing
- Example: `https://discordapp.com/api/webhooks/123456789/...`

---

## Configuration Files

### backend/.env (Development)

```bash
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev-secret-not-for-production
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=hackathon_db
AUTO_CREATE_TABLES=true
LOG_LEVEL=DEBUG
BASE_URL=http://localhost:5000
REDIS_ENABLED=false
DEFAULT_SHORT_CODE_LENGTH=7
EVENT_LOG_SAMPLE_RATE=1.0
```

### backend/.env.production (Production Template)

```bash
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=<generate-random-32-char-string>
DATABASE_HOST=db.example.com
DATABASE_PORT=5432
DATABASE_USER=vybe_user
DATABASE_PASSWORD=<generate-strong-password>
DATABASE_NAME=vybe
DB_MAX_CONNECTIONS=20
DB_CONNECTION_TIMEOUT_SECONDS=10
AUTO_CREATE_TABLES=false
LOG_LEVEL=INFO
BASE_URL=https://links.example.com
REDIS_ENABLED=true
REDIS_URL=redis://<password>@redis.example.com:6379/0
REDIS_DEFAULT_TTL_SECONDS=300
DEFAULT_SHORT_CODE_LENGTH=7
EVENT_LOG_SAMPLE_RATE=0.1
```

---

## Loading Environment Variables

### Local Development

1. Create backend/.env file
2. docker-compose automatically loads it via `env_file:`

```yaml
# In docker-compose.yml
services:
  vybe_app1:
    env_file:
      - ./backend/.env
```

### Production

Option 1: File-based (simple)

```bash
# On production server
cp backend/.env.production /opt/vybe/.env.production
export $(cat /opt/vybe/.env.production | xargs)
docker compose up -d
```

Option 2: Secrets manager (recommended)

Use your cloud provider's secrets manager:
- AWS Secrets Manager
- Google Cloud Secret Manager
- HashiCorp Vault

Retrieve secrets at deploy time:
```bash
# Example with AWS
SECRET=$(aws secretsmanager get-secret-value --secret-id vybe/DATABASE_PASSWORD --query SecretString)
export DATABASE_PASSWORD=$SECRET
```

Option 3: Kubernetes secrets (if using K8s)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vybe-secrets
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded>
  REDIS_PASSWORD: <base64-encoded>

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vybe-app
spec:
  containers:
    - name: vybe
      env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vybe-secrets
              key: DATABASE_PASSWORD
```

---

## Configuration Precedence

Variables are loaded in this order (later overrides earlier):

1. Hardcoded defaults in code (backend/app/config/settings.py)
2. Environment variables in .env file
3. Environment variables passed at runtime
4. Command-line arguments (if implemented)

Example:

```bash
# In .env file
DATABASE_POOL=20

# At runtime, override
export DATABASE_POOL=30
docker compose up -d

# App will use DATABASE_POOL=30
```

---

## Validation & Defaults

| Variable | Type | Validation | Default | Error if Invalid |
|----------|------|-----------|---------|-----------------|
| FLASK_ENV | Enum | Must be `development` or `production` | `development` | App starts with wrong config |
| LOG_LEVEL | Enum | Must be valid level | `INFO` | Logging doesn't work |
| DATABASE_PORT | Integer | 1-65535 | `5432` | Connection refused |
| DB_MAX_CONNECTIONS | Integer | 5-100 | `20` | Pool too small or too large |
| DEFAULT_SHORT_CODE_LENGTH | Integer | 4-20 | `7` | Generated codes invalid |
| REDIS_DEFAULT_TTL_SECONDS | Integer | 60-7200 | `300` | Cache behavior incorrect |
| EVENT_LOG_SAMPLE_RATE | Float | 0.0-1.0 | `1.0` | Data loss or excess logging |

---

## Secret Management Best Practices

### Never

- Never commit .env files to git (add to .gitignore)
- Never log sensitive values
- Never hardcode secrets in Docker images
- Never share .env files over email or chat
- Never use default passwords (postgres/postgres)

### Always

- Use strong, random secrets (minimum 32 characters)
- Rotate secrets every 90 days minimum
- Store secrets in a secrets manager (Vault, AWS Secrets Manager, etc.)
- Audit who accessed secrets and when
- Use different secrets for each environment (dev, staging, prod)
- Enable encryption at rest for secrets storage

### Generate Secrets

```bash
# PostgreSQL password
openssl rand -base64 32

# Redis password
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Performance Tuning

### For High Traffic (>1000 RPS)

```bash
DB_MAX_CONNECTIONS=30
REDIS_ENABLED=true
REDIS_DEFAULT_TTL_SECONDS=600
EVENT_LOG_SAMPLE_RATE=0.1
LOG_LEVEL=WARNING
```

### For Development/Testing

```bash
DB_MAX_CONNECTIONS=5
REDIS_ENABLED=false
EVENT_LOG_SAMPLE_RATE=1.0
LOG_LEVEL=DEBUG
AUTO_CREATE_TABLES=true
```

### For Compliance/High Audit

```bash
LOG_LEVEL=INFO
EVENT_LOG_SAMPLE_RATE=1.0
REDIS_ENABLED=false
```

---

## Troubleshooting Configuration

### "Connection refused" for database

Check:
```bash
echo $DATABASE_HOST
echo $DATABASE_PORT
# Verify host is reachable from app container
docker exec vybe_app1 nc -zv $DATABASE_HOST $DATABASE_PORT
```

### "Invalid log level"

Check:
```bash
echo $LOG_LEVEL
# Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### "Redis not configured"

If REDIS_ENABLED=true but REDIS_URL not set:

```bash
# Either disable Redis
export REDIS_ENABLED=false

# Or provide Redis URL
export REDIS_URL=redis://localhost:6379/0
```

### "Secret key too short"

Check:
```bash
echo $SECRET_KEY | wc -c
# Must be at least 32 characters
```

---

## Configuration Versioning

Keep track of configuration changes:

```bash
# Document what changed and when
git log --oneline -- backend/.env.example

# Diff configurations between deployments
diff /opt/vybe/.env.prod-v1.0 /opt/vybe/.env.prod-v1.1
```

This helps trace configuration-related incidents.

