# API Reference

Base URL: `/api/v1`

All endpoints require HTTP/1.1. Responses are JSON unless otherwise specified.

---

## Authentication

Currently, Vybe has no authentication layer. All endpoints are public. For future deployments, add API key validation in Nginx or as middleware before service layer.

---

## Link Management

### Create Link

Generate a shortened link from a long URL.

**Request**

```http
POST /api/v1/links
Content-Type: application/json

{
  "url": "https://example.com/products/launch-2026",
  "custom_alias": "launch",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `url` | string | Yes | Must be valid HTTP/HTTPS URL (max 2048 chars) |
| `custom_alias` | string | No | Custom short code (max 32 chars, alphanumeric + dash/underscore). If omitted, auto-generated (7 chars). |
| `expires_at` | ISO 8601 | No | Link expiration time. If omitted, link never expires. |

**Response (201 Created)**

```json
{
  "id": 1,
  "code": "launch",
  "short_url": "http://localhost:5000/launch",
  "original_url": "https://example.com/products/launch-2026",
  "is_active": true,
  "click_count": 0,
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T10:00:00+00:00",
  "expires_at": "2026-12-31T23:59:59+00:00",
  "last_accessed_at": null
}
```

**Error Responses**

**400 Bad Request** - Invalid URL or alias format

```json
{
  "error": "validation_error",
  "message": "Invalid URL format",
  "details": {
    "field": "url",
    "reason": "must start with http:// or https://"
  },
  "request_id": "req-abc123def456"
}
```

**409 Conflict** - Custom alias already exists

```json
{
  "error": "alias_already_exists",
  "message": "The alias 'launch' is already taken",
  "request_id": "req-abc123def456"
}
```

**500 Internal Server Error** - Database unavailable

```json
{
  "error": "database_error",
  "message": "Database temporarily unavailable",
  "request_id": "req-abc123def456"
}
```

---

### Get Link

Retrieve link metadata and stats.

**Request**

```http
GET /api/v1/links/{code}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `code` | string | Yes | Short code (URL parameter) |

**Response (200 OK)**

```json
{
  "id": 1,
  "code": "launch",
  "short_url": "http://localhost:5000/launch",
  "original_url": "https://example.com/products/launch-2026",
  "is_active": true,
  "click_count": 42,
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T10:15:00+00:00",
  "expires_at": "2026-12-31T23:59:59+00:00",
  "last_accessed_at": "2026-04-05T12:30:00+00:00"
}
```

**Error Responses**

**404 Not Found** - Link does not exist

```json
{
  "error": "not_found",
  "message": "Link 'launch' not found",
  "request_id": "req-abc123def456"
}
```

---

### List Links (Optional, Future)

List all user's links. Requires authentication (not yet implemented).

**Request**

```http
GET /api/v1/links?limit=25&offset=0
```

**Response (200 OK)**

```json
{
  "links": [
    {
      "id": 1,
      "code": "launch",
      "short_url": "http://localhost:5000/launch",
      "original_url": "https://example.com/products/launch-2026",
      "is_active": true,
      "click_count": 42,
      "created_at": "2026-04-05T10:00:00+00:00",
      "updated_at": "2026-04-05T10:15:00+00:00",
      "expires_at": "2026-12-31T23:59:59+00:00",
      "last_accessed_at": "2026-04-05T12:30:00+00:00"
    }
  ],
  "total": 1,
  "limit": 25,
  "offset": 0
}
```

---

### Update Link

Modify link metadata (status, expiration).

**Request**

```http
PATCH /api/v1/links/{code}
Content-Type: application/json

{
  "is_active": false,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `is_active` | boolean | No | Enable/disable link. Disabled links return 410 Gone. |
| `expires_at` | ISO 8601 | No | Set new expiration time. Use `null` to clear expiration. |

**Response (200 OK)**

```json
{
  "id": 1,
  "code": "launch",
  "short_url": "http://localhost:5000/launch",
  "original_url": "https://example.com/products/launch-2026",
  "is_active": false,
  "click_count": 42,
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T13:00:00+00:00",
  "expires_at": "2026-12-31T23:59:59+00:00",
  "last_accessed_at": "2026-04-05T12:30:00+00:00"
}
```

---

### Delete Link (Soft Delete)

Deactivate a link. Does not delete database record.

**Request**

```http
DELETE /api/v1/links/{code}
```

**Response (204 No Content)**

Empty body. Link is now inactive (soft deleted).

**Error Responses**

**404 Not Found** - Link does not exist

---

## Visit Tracking

### Record Visit / Redirect

When a user accesses `/{code}`, the short link redirects and records a visit event.

**Request**

```http
GET /{code}
```

**Response (302 Found)**

```http
HTTP/1.1 302 Found
Location: https://example.com/products/launch-2026
```

The browser automatically follows the redirect to the original URL.

**Behavior**

- If link is inactive (`is_active=false`), returns 410 Gone
- If link is expired (`expires_at` is past), returns 410 Gone
- Otherwise, records visit event and returns 302 redirect
- Visit recording is sampled by `EVENT_LOG_SAMPLE_RATE` (configurable, default 100%)

**Error Responses**

**404 Not Found** - Link does not exist

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "not_found",
  "message": "Link not found",
  "request_id": "req-abc123def456"
}
```

**410 Gone** - Link is inactive or expired

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": "gone",
  "message": "Link is no longer available",
  "reason": "inactive"
}
```

---

### Get Recent Visits

Retrieve recent click events for a link.

**Request**

```http
GET /api/v1/links/{code}/visits?limit=25
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `limit` | integer | No | Max results (default 25, max 100) |

**Response (200 OK)**

```json
{
  "code": "launch",
  "visits": [
    {
      "id": 101,
      "timestamp": "2026-04-05T12:30:00+00:00",
      "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/90.0",
      "referrer": "https://twitter.com",
      "ip_address": "203.0.113.42"
    },
    {
      "id": 100,
      "timestamp": "2026-04-05T11:45:00+00:00",
      "user_agent": "curl/7.64.1",
      "referrer": null,
      "ip_address": "203.0.113.41"
    }
  ],
  "total_count": 42,
  "returned": 2
}
```

**Error Responses**

**404 Not Found** - Link does not exist

---

## Health & Readiness

### Liveness Check

Always returns 200 if the application process is running. Use this for container orchestration liveness probes.

**Request**

```http
GET /health
```

**Response (200 OK)**

```json
{
  "status": "healthy"
}
```

---

### Readiness Check

Returns 200 only if all critical dependencies are available (database, cache if enabled). Use this for load balancer health checks.

**Request**

```http
GET /ready
```

**Response (200 OK)**

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

**Response (503 Service Unavailable)**

If any critical dependency is down:

```json
{
  "status": "not_ready",
  "checks": {
    "database": "failed: connection timeout",
    "redis": "ok"
  }
}
```

---

## Metrics (Prometheus)

### Prometheus Metrics Endpoint

All metrics exposed on port 8000 (internal only, not exposed via Nginx).

**Request**

```http
GET /metrics
```

**Response (200 OK)**

```
# HELP requests_total Total HTTP requests
# TYPE requests_total counter
requests_total{method="GET",path="/api/v1/links/launch",status="200"} 42.0

# HELP request_latency_seconds HTTP request latency
# TYPE request_latency_seconds histogram
request_latency_seconds_bucket{le="0.1"} 35.0
request_latency_seconds_bucket{le="1.0"} 40.0
request_latency_seconds_bucket{le="+Inf"} 42.0
request_latency_seconds_sum 8.5
request_latency_seconds_count 42.0

# HELP database_pool_size Current database connection pool size
# TYPE database_pool_size gauge
database_pool_size{instance="app1"} 15.0

# HELP redis_operations_total Total Redis operations
# TYPE redis_operations_total counter
redis_operations_total{operation="GET"} 1000.0
redis_operations_total{operation="SET"} 500.0
```

---

## Error Codes & Meanings

| Code | Meaning | Cause | Action |
|------|---------|-------|--------|
| 200 | OK | Request succeeded | None |
| 201 | Created | Resource created successfully | None |
| 204 | No Content | Request succeeded, no response body | None |
| 302 | Found | Redirect to original URL | Follow redirect |
| 400 | Bad Request | Invalid input (malformed JSON, invalid field values) | Check request format and field values |
| 404 | Not Found | Resource does not exist | Verify URL path and code |
| 409 | Conflict | Resource already exists (duplicate alias) | Choose different alias |
| 410 | Gone | Link is inactive or expired | Link no longer available |
| 500 | Internal Server Error | Unhandled server error | Check logs, contact support |
| 503 | Service Unavailable | Database or critical service down | Wait and retry, check status page |

---

## Rate Limiting

Currently not implemented. All users can make unlimited requests. This will be added in future versions.

---

## Pagination

Endpoints supporting multiple results use limit/offset pagination:

```http
GET /api/v1/links?limit=25&offset=0
GET /api/v1/links?limit=25&offset=25  # Next page
```

---

## Request/Response Format

### Headers

**Request**

```http
Content-Type: application/json
Accept: application/json
```

**Response**

```http
Content-Type: application/json
X-Request-ID: req-abc123def456
```

The `X-Request-ID` header is added to all responses. Use this ID to correlate logs if issues occur.

### Timestamp Format

All timestamps are ISO 8601 format with timezone:

```
2026-04-05T10:00:00+00:00
```

---

## Example Client Code

### cURL

```bash
# Create link
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/long/url",
    "custom_alias": "short"
  }'

# Get link stats
curl http://localhost:8080/api/v1/links/short

# Get recent visits
curl http://localhost:8080/api/v1/links/short/visits

# Update link (disable)
curl -X PATCH http://localhost:8080/api/v1/links/short \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'

# Delete link
curl -X DELETE http://localhost:8080/api/v1/links/short
```

### Python (Requests Library)

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

# Create link
response = requests.post(
    f"{BASE_URL}/links",
    json={
        "url": "https://example.com/long/url",
        "custom_alias": "short"
    }
)
link = response.json()
print(f"Short URL: {link['short_url']}")

# Get recent visits
response = requests.get(f"{BASE_URL}/links/short/visits")
visits = response.json()
print(f"Click count: {len(visits['visits'])}")
```

### JavaScript (Fetch API)

```javascript
const BASE_URL = "http://localhost:8080/api/v1";

// Create link
async function createLink(url, alias) {
  const response = await fetch(`${BASE_URL}/links`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url: url,
      custom_alias: alias
    })
  });
  return response.json();
}

// Get recent visits
async function getVisits(code) {
  const response = await fetch(`${BASE_URL}/links/${code}/visits`);
  return response.json();
}

// Usage
const link = await createLink("https://example.com/long", "short");
console.log(`Short URL: ${link.short_url}`);

const visits = await getVisits("short");
console.log(`Clicks: ${visits.total_count}`);
```

---

## Versioning

This is API v1 (`/api/v1`). Future backwards-incompatible changes will be released under `/api/v2`, with v1 supported for at least 12 months.

Current API is stable and suitable for production use.

