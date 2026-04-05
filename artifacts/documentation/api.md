# API Reference

**Base URL:** `http://localhost:8080` (via Nginx) or `http://localhost:5000` (direct to Flask)

All endpoints require HTTP/1.1. Responses are JSON unless otherwise specified.

---

## Quick API Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **System Health** |||
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check (dependency status) |
| GET | `/metrics` | Prometheus metrics export |
| **URL Management** |||
| POST | `/urls` | Create shortened link |
| GET | `/urls` | List all URLs |
| GET | `/urls/<url_id>` | Get specific URL details |
| PUT | `/urls/<url_id>` | Update URL metadata |
| DELETE | `/urls/<url_id>` | Soft-delete (deactivate) URL |
| **Redirects** |||
| GET | `/<code>` | Follow short link (redirect) |
| **Events/Analytics** |||
| GET | `/events` | List click events |
| POST | `/events` | Record click event |
| **User Management** |||
| POST | `/users` | Create user account |
| GET | `/users` | List all users |
| GET | `/users/<user_id>` | Get user details |
| PUT | `/users/<user_id>` | Update user |
| DELETE | `/users/<user_id>` | Delete user |
| POST | `/users/bulk` | Bulk import users |

---

## Authentication

Currently, Vybe has no authentication layer. All endpoints are public. For future deployments, add API key validation in Nginx or as middleware before service layer.

---

## URL Management

### Create URL (Shortened Link)

Generate a shortened link from a long URL.

**Request**

```http
POST /urls
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
  "short_url": "http://localhost:8080/launch",
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

**400 Bad Request** - Invalid URL or parameters

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

### List URLs

Retrieve all shortened URLs.

**Request**

```http
GET /urls
```

**Query Parameters**

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `limit` | integer | 100 | Max results per page |
| `offset` | integer | 0 | Pagination offset |

**Response (200 OK)**

```json
{
  "urls": [
    {
      "id": 1,
      "code": "launch",
      "short_url": "http://localhost:8080/launch",
      "original_url": "https://example.com/products/launch-2026",
      "is_active": true,
      "click_count": 42,
      "created_at": "2026-04-05T10:00:00+00:00",
      "updated_at": "2026-04-05T10:15:00+00:00",
      "expires_at": "2026-12-31T23:59:59+00:00",
      "last_accessed_at": "2026-04-05T12:30:00+00:00"
    },
    {
      "id": 2,
      "code": "demo",
      "short_url": "http://localhost:8080/demo",
      "original_url": "https://github.com",
      "is_active": true,
      "click_count": 5,
      "created_at": "2026-04-01T14:00:00+00:00",
      "updated_at": "2026-04-01T14:00:00+00:00",
      "expires_at": null,
      "last_accessed_at": "2026-04-05T09:00:00+00:00"
    }
  ],
  "total": 42,
  "limit": 100,
  "offset": 0
}
```

---

### Get URL

Retrieve specific URL metadata and statistics.

**Request**

```http
GET /urls/1
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `url_id` | integer | Yes | URL ID (path parameter) |

**Response (200 OK)**

```json
{
  "id": 1,
  "code": "launch",
  "short_url": "http://localhost:8080/launch",
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

**404 Not Found** - URL does not exist

```json
{
  "error": "not_found",
  "message": "URL with ID 999 not found",
  "request_id": "req-abc123def456"
}
```

---

### Update URL

Modify URL metadata (status, expiration).

**Request**

```http
PUT /urls/1
Content-Type: application/json

{
  "is_active": false,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `is_active` | boolean | No | Enable/disable link. Disabled links return 410 Gone on redirect. |
| `expires_at` | ISO 8601 | No | Set new expiration time. Use `null` to clear expiration. |

**Response (200 OK)**

```json
{
  "id": 1,
  "code": "launch",
  "short_url": "http://localhost:8080/launch",
  "original_url": "https://example.com/products/launch-2026",
  "is_active": false,
  "click_count": 42,
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T13:00:00+00:00",
  "expires_at": "2026-12-31T23:59:59+00:00",
  "last_accessed_at": "2026-04-05T12:30:00+00:00"
}
```

**Error Responses**

**404 Not Found** - URL does not exist

---

### Delete URL (Soft Delete)

Deactivate a shortened link. Does not delete database record, only marks inactive.

**Request**

```http
DELETE /urls/1
```

**Response (204 No Content)**

Empty body. Link is now inactive.

**Error Responses**

**404 Not Found** - URL does not exist

```json
{
  "error": "not_found",
  "message": "URL with ID 999 not found"
}
```

---

## Link Redirect

### Follow Short Link

When a user accesses a short link, the system redirects to the original URL.

**Request**

```http
GET /{code}
```

**Example**

```http
GET /launch
```

**Response (302 Found)**

```http
HTTP/1.1 302 Found
Location: https://example.com/products/launch-2026
X-Request-ID: req-abc123def456
```

The browser automatically follows the redirect to the original URL.

**Behavior**

- If link is inactive (`is_active=false`), returns 410 Gone
- If link is expired (`expires_at` is in the past), returns 410 Gone
- Otherwise, records visit event (if enabled) and returns 302 redirect
- Visit recording is sampled by `EVENT_LOG_SAMPLE_RATE` (default 100%, configurable)
- Redirect status code configurable via `DEFAULT_REDIRECT_STATUS_CODE` (default 302)

**Error Responses**

**404 Not Found** - Link does not exist

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "not_found",
  "message": "Link not found or inactive",
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
  "reason": "inactive|expired",
  "request_id": "req-abc123def456"
}
```

---

## Events & Analytics

### List Events

Retrieve click events from all or specific shortened links.

**Request**

```http
GET /events?limit=25&offset=0
```

**Query Parameters**

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `limit` | integer | 100 | Max results per page |
| `offset` | integer | 0 | Pagination offset |
| `url_id` | integer | (optional) | Filter by specific URL |

**Response (200 OK)**

```json
{
  "events": [
    {
      "id": 101,
      "url_id": 1,
      "code": "launch",
      "timestamp": "2026-04-05T12:30:00+00:00",
      "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/90.0",
      "referrer": "https://twitter.com",
      "ip_address": "203.0.113.42"
    },
    {
      "id": 100,
      "url_id": 1,
      "code": "launch",
      "timestamp": "2026-04-05T11:45:00+00:00",
      "user_agent": "curl/7.64.1",
      "referrer": null,
      "ip_address": "203.0.113.41"
    }
  ],
  "total": 42,
  "limit": 25,
  "offset": 0
}
```

---

### Create Event (Record Click)

Manually record a click event for a shortened link. Usually called automatically on redirect, but available for custom tracking.

**Request**

```http
POST /events
Content-Type: application/json

{
  "url_id": 1,
  "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/90.0",
  "referrer": "https://twitter.com",
  "ip_address": "203.0.113.42"
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `url_id` | integer | Yes | ID of the shortened URL |
| `user_agent` | string | No | Visitor's User-Agent header |
| `referrer` | string | No | Referrer URL |
| `ip_address` | string | No | Visitor's IP address |

**Response (201 Created)**

```json
{
  "id": 102,
  "url_id": 1,
  "code": "launch",
  "timestamp": "2026-04-05T14:15:00+00:00",
  "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/90.0",
  "referrer": "https://twitter.com",
  "ip_address": "203.0.113.42"
}
```

**Error Responses**

**404 Not Found** - URL does not exist

```json
{
  "error": "not_found",
  "message": "URL with ID 999 not found",
  "request_id": "req-abc123def456"
}
```

---

## User Management

### Create User

Create a new user account.

**Request**

```http
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `username` | string | Yes | Unique username |
| `email` | string | No | Email address |

**Response (201 Created)**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T10:00:00+00:00"
}
```

**Error Responses**

**409 Conflict** - Username already exists

```json
{
  "error": "conflict",
  "message": "Username 'john_doe' already exists",
  "request_id": "req-abc123def456"
}
```

---

### List Users

Retrieve all user accounts.

**Request**

```http
GET /users?limit=50&offset=0
```

**Query Parameters**

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `limit` | integer | 100 | Max results per page |
| `offset` | integer | 0 | Pagination offset |

**Response (200 OK)**

```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-04-05T10:00:00+00:00",
      "updated_at": "2026-04-05T10:00:00+00:00"
    },
    {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com",
      "created_at": "2026-04-04T12:00:00+00:00",
      "updated_at": "2026-04-04T12:00:00+00:00"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

### Get User

Retrieve user details.

**Request**

```http
GET /users/1
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `user_id` | integer | Yes | User ID (path parameter) |

**Response (200 OK)**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T10:00:00+00:00"
}
```

**Error Responses**

**404 Not Found** - User does not exist

```json
{
  "error": "not_found",
  "message": "User with ID 999 not found",
  "request_id": "req-abc123def456"
}
```

---

### Update User

Modify user details.

**Request**

```http
PUT /users/1
Content-Type: application/json

{
  "email": "john.doe@example.com"
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `email` | string | No | New email address |
| `username` | string | No | New username (must be unique) |

**Response (200 OK)**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "created_at": "2026-04-05T10:00:00+00:00",
  "updated_at": "2026-04-05T10:30:00+00:00"
}
```

---

### Delete User

Delete a user account.

**Request**

```http
DELETE /users/1
```

**Response (204 No Content)**

Empty body. User is deleted.

---

### Bulk Import Users

Import multiple users from CSV/JSON data.

**Request**

```http
POST /users/bulk
Content-Type: application/json

{
  "users": [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"}
  ]
}
```

**Parameters**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `users` | array | Yes | Array of user objects |

**Response (201 Created)**

```json
{
  "imported": 2,
  "failed": 0,
  "results": [
    {"id": 10, "username": "user1", "status": "created"},
    {"id": 11, "username": "user2", "status": "created"}
  ]
}
```

---

## System Health & Readiness

## System Health & Readiness

### Liveness Check

Returns 200 if the application process is running. Use this for container orchestration liveness probes (Kubernetes, Docker healthcheck).

**Request**

```http
GET /health
```

**Response (200 OK)**

```json
{
  "status": "ok",
  "service": "vybe"
}
```

This endpoint always returns 200 as long as the process is running. It does NOT check dependencies.

---

### Readiness Check

Returns 200 only if all critical dependencies are available (database, optional Redis). Use this for load balancer health checks and Nginx routing decisions.

**Request**

```http
GET /ready
```

**Response (200 OK) - Ready**

```json
{
  "status": "ready",
  "service": "vybe"
}
```

**Response (503 Service Unavailable) - Not Ready**

If the database or other critical service is down:

```json
{
  "status": "not ready",
  "error": "Connection to database failed: timeout after 5s",
  "service": "vybe"
}
```

**Behavior**

- Checks database connectivity (ping query)
- Checks Redis connectivity (if enabled)
- Returns 503 if any critical dependency fails
- Used by Nginx health check to drain traffic from unhealthy instances
- Timeout for readiness check: 5 seconds

---

## Metrics & Monitoring

### Prometheus Metrics Endpoint

Exports application metrics in Prometheus text format. Available on port 8000 (internal only, not exposed via Nginx).

**Request**

```http
GET /metrics
```

**Response (200 OK)**

```prometheus
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/urls",method="POST",status="201"} 150.0
http_requests_total{endpoint="/urls",method="GET",status="200"} 3420.0
http_requests_total{endpoint="/<code>",method="GET",status="302"} 12500.0
http_requests_total{endpoint="/<code>",method="GET",status="404"} 45.0

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/urls",method="POST",le="0.005"} 85.0
http_request_duration_seconds_bucket{endpoint="/urls",method="POST",le="0.01"} 125.0
http_request_duration_seconds_bucket{endpoint="/urls",method="POST",le="1.0"} 148.0
http_request_duration_seconds_bucket{endpoint="/urls",method="POST",le="+Inf"} 150.0
http_request_duration_seconds_sum{endpoint="/urls",method="POST"} 2.5
http_request_duration_seconds_count{endpoint="/urls",method="POST"} 150.0

# HELP http_requests_in_progress Number of HTTP requests currently being processed
# TYPE http_requests_in_progress gauge
http_requests_in_progress 3.0

# HELP http_errors_total Total number of HTTP errors (4xx and 5xx)
# TYPE http_errors_total counter
http_errors_total{endpoint="/urls",method="GET",status="404"} 12.0
http_errors_total{endpoint="/<code>",method="GET",status="410"} 8.0
http_errors_total{endpoint="/urls",method="POST",status="409"} 3.0
```

**Metrics Collected**

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency in seconds with percentile buckets |
| `http_requests_in_progress` | Gauge | Currently processing requests |
| `http_errors_total` | Counter | Total errors (4xx, 5xx) by method, endpoint, status |

**Labels**

All metrics include:
- `method` - HTTP method (GET, POST, PUT, DELETE)
- `endpoint` - Flask route pattern (/urls, /<code>, etc.)
- `status` - HTTP status code (201, 404, 500, etc.)

---

## HTTP Status Codes

| Code | Meaning | When It Occurs | Action |
|------|---------|----------------|--------|
| **2xx Success** ||||
| 200 | OK | Request succeeded, response has body | None |
| 201 | Created | Resource created successfully (POST) | None |
| 204 | No Content | Request succeeded, no response body (DELETE) | None |
| 302 | Found | Redirect to original URL | Follow redirect (automatic in browser) |
| **4xx Client Error** ||||
| 400 | Bad Request | Invalid JSON, missing required fields, validation error | Check request format and parameters |
| 404 | Not Found | Resource does not exist (wrong ID, URL code not found) | Verify URL path and parameters |
| 409 | Conflict | Resource already exists (duplicate username, alias taken) | Choose different value or check existing resources |
| 410 | Gone | Link is inactive or expired | Link no longer available, cannot be used |
| **5xx Server Error** ||||
| 500 | Internal Error | Unhandled exception, server bug | Check logs, contact support, wait and retry |
| 503 | Unavailable | Database down, critical dependency unavailable | Wait for recovery, check `/ready` endpoint |

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": "error_code",
  "message": "Human-readable error description",
  "details": {
    "field": "username",
    "reason": "must be 3-32 characters"
  },
  "request_id": "req-abc123def456"
}
```

**Fields**

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Machine-readable error code (validation_error, not_found, etc.) |
| `message` | string | Human-readable error description |
| `details` | object | (Optional) Additional context about the error |
| `request_id` | string | Unique request ID for debugging and logs |

**Use Request ID for Debugging**

When investigating errors, use the request ID to find all related logs:

```bash
# Search logs by request ID
grep "req-abc123def456" app.log | head -50

# Output shows complete request lifecycle:
# - Request received
# - Processing steps
# - Error occurred
# - Error returned to client
```

---

## Rate Limiting

Currently not implemented. All clients can make unlimited requests. Rate limiting will be added by HTTP method and endpoint in future versions if needed.

---

## Pagination

Endpoints supporting multiple results use limit/offset pagination:

```http
GET /urls?limit=50&offset=0      # First 50 results
GET /urls?limit=50&offset=50     # Next 50 results
GET /urls?limit=50&offset=100    # Third 50 results
```

**Parameters**

| Field | Type | Default | Max | Notes |
|-------|------|---------|-----|-------|
| `limit` | integer | 100 | 1000 | Results per page |
| `offset` | integer | 0 | (unbounded) | Skip N results |

**Response includes pagination metadata**

```json
{
  "urls": [...],
  "total": 1250,
  "limit": 50,
  "offset": 100
}
```

---

## Common Request/Response Patterns

### Request Headers

**Standard Headers**

```http
Content-Type: application/json
Accept: application/json
```

**Optional Headers**

```http
X-Request-ID: req-custom-id       # Override generated request ID (optional)
User-Agent: MyApp/1.0              # Your application name and version
```

### Response Headers

**Standard Headers**

```http
Content-Type: application/json
X-Request-ID: req-abc123def456     # Unique request ID in all responses
```

**Redirect Headers**

```http
Location: https://example.com      # Destination URL for 3xx responses
```

---

## Code Examples

### Create Short Link (cURL)

```bash
curl -X POST http://localhost:8080/urls \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/very-long-page",
    "custom_alias": "promo"
  }'

# Response:
# {
#   "id": 1,
#   "code": "promo",
#   "short_url": "http://localhost:8080/promo",
#   "original_url": "https://example.com/very-long-page",
#   "is_active": true,
#   ...
# }
```

### Create Short Link (Python)

```python
import requests

response = requests.post(
    "http://localhost:8080/urls",
    json={
        "url": "https://example.com/very-long-page",
        "custom_alias": "promo"
    }
)

data = response.json()
print(f"Short URL: {data['short_url']}")
```

### Create Short Link (JavaScript)

```javascript
fetch('http://localhost:8080/urls', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com/very-long-page',
    custom_alias: 'promo'
  })
})
.then(res => res.json())
.then(data => console.log(`Short URL: ${data.short_url}`));
```

### Get All URLs (cURL)

```bash
curl http://localhost:8080/urls?limit=10

# Response:
# {
#   "urls": [ ... ],
#   "total": 42,
#   "limit": 10,
#   "offset": 0
# }
```

### Check Readiness (cURL)

```bash
# Ready
curl http://localhost:8080/ready
# {"status": "ready", "service": "vybe"}

# Not ready
curl -i http://localhost:8080/ready  
# HTTP/1.1 503 Service Unavailable
# {"status": "not ready", "error": "Database timeout"}
```

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

