# Automated Test Specifications

**Source:** MLH Production Engineering Hackathon Evaluation  
**Date:** April 4, 2026  
**Author:** Hugo Castro

## Overview

Once your submission is sent for evaluation, your app will be tested against automated tests to ensure compliance with basic URL shortener features. These tests **do not replace** team-developed tests but help you work towards the reliability quest.

> **Note:** Some tests have hidden input/output to challenge edge case handling. Pass hidden tests by robustly handling edge cases. Hints will be shared as the hackathon progresses.

---

## Test Categories

### 1. Health

**Purpose:** Ensure the API is running and ready to accept requests.

| Aspect | Details |
|--------|---------|
| **Endpoint** | `GET /health` |
| **Input** | None |
| **Expected Status** | 200 OK |
| **Response Format** | JSON object with status field |

**Expected Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Users

#### 2.1 Bulk Load Users (CSV Import)

| Aspect | Details |
|--------|---------|
| **Endpoint** | `POST /users/bulk` |
| **Input** | `multipart/form-data` with `file` field containing `users.csv` |
| **Expected Status** | 200 OK or 201 Created |
| **Response Format** | JSON indicating number of imported users |

**Acceptable Response Formats:**
```json
{ "count": 2 }
```
or
```json
{ "imported": 2 }
```
or simply return an array of imported user objects.

---

#### 2.2 List Users

| Aspect | Details |
|--------|---------|
| **Endpoint** | `GET /users` |
| **Input** | None (optional: `?page=x&per_page=y` for pagination) |
| **Expected Status** | 200 OK |
| **Response Format** | JSON array or paginated envelope |

**Expected Response:**
```json
[
  {
    "id": 1,
    "username": "silvertrail15",
    "email": "silvertrail15@hackstack.io",
    "created_at": "2025-09-19T22:25:05"
  },
  {
    "id": 2,
    "username": "urbancanyon36",
    "email": "urbancanyon36@opswise.net",
    "created_at": "2024-04-09T02:51:03"
  }
]
```

---

#### 2.3 Get User by ID

| Aspect | Details |
|--------|---------|
| **Endpoint** | `GET /users/<id>` |
| **Input** | None |
| **Expected Status** | 200 OK |
| **Response Format** | Single JSON user object |

**Expected Response:**
```json
{
  "id": 1,
  "username": "silvertrail15",
  "email": "silvertrail15@hackstack.io",
  "created_at": "2025-09-19T22:25:05"
}
```

---

#### 2.4 Create User

| Aspect | Details |
|--------|---------|
| **Endpoint** | `POST /users` |
| **Input** | JSON user object |
| **Expected Status** | 201 Created |
| **Error Status** | 400 Bad Request or 422 Unprocessable Entity for invalid schema |
| **Response Format** | Created user object |

**Request Payload:**
```json
{
  "username": "testuser",
  "email": "testuser@example.com"
}
```

**Expected Response:**
```json
{
  "id": 3,
  "username": "testuser",
  "email": "testuser@example.com",
  "created_at": "2026-04-03T12:00:00"
}
```

**Error Handling:**
- Reject invalid data schemas (e.g., integer for username)
- Return 400 Bad Request or 422 Unprocessable Entity with error dictionary

---

#### 2.5 Update User

| Aspect | Details |
|--------|---------|
| **Endpoint** | `PUT /users/<id>` |
| **Input** | JSON object with fields to update |
| **Expected Status** | 200 OK |
| **Response Format** | Updated user object |

**Request Payload:**
```json
{
  "username": "updated_username"
}
```

**Expected Response:**
```json
{
  "id": 1,
  "username": "updated_username",
  "email": "silvertrail15@hackstack.io",
  "created_at": "2025-09-19T22:25:05"
}
```

---

### 3. URLs

#### 3.1 Create URL

| Aspect | Details |
|--------|---------|
| **Endpoint** | `POST /urls` |
| **Input** | JSON URL object |
| **Expected Status** | 201 Created |
| **Response Format** | URL object with generated short_code |

**Request Payload:**
```json
{
  "user_id": 1,
  "original_url": "https://example.com/test",
  "title": "Test URL"
}
```

**Expected Response:**
```json
{
  "id": 3,
  "user_id": 1,
  "short_code": "k8Jd9s",
  "original_url": "https://example.com/test",
  "title": "Test URL",
  "is_active": true,
  "created_at": "2026-04-03T12:00:00",
  "updated_at": "2026-04-03T12:00:00"
}
```

**Error Handling:**
- Handle missing user gracefully (return appropriate error)
- Validate constraints (e.g., URL format, required fields)

---

#### 3.2 List URLs

| Aspect | Details |
|--------|---------|
| **Endpoint** | `GET /urls` |
| **Input** | None (optional: `?user_id=1` for filtering) |
| **Expected Status** | 200 OK |
| **Response Format** | JSON array of URL objects |

**Expected Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "short_code": "ALQRog",
    "original_url": "https://opswise.net/harbor/journey/1",
    "title": "Service guide lagoon",
    "is_active": true,
    "created_at": "2025-06-04T00:07:00",
    "updated_at": "2025-11-19T03:17:29"
  }
]
```

---

#### 3.3 Get URL by ID

| Aspect | Details |
|--------|---------|
| **Endpoint** | `GET /urls/<id>` |
| **Input** | None |
| **Expected Status** | 200 OK |
| **Response Format** | Single URL object |

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "short_code": "ALQRog",
  "original_url": "https://opswise.net/harbor/journey/1",
  "title": "Service guide lagoon",
  "is_active": true,
  "created_at": "2025-06-04T00:07:00",
  "updated_at": "2025-11-19T03:17:29"
}
```

---

#### 3.4 Update URL Details

| Aspect | Details |
|--------|---------|
| **Endpoint** | `PUT /urls/<id>` |
| **Input** | JSON object with fields to update |
| **Expected Status** | 200 OK |
| **Response Format** | Updated URL object |

**Request Payload:**
```json
{
  "title": "Updated Title",
  "is_active": false
}
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "short_code": "ALQRog",
  "original_url": "https://opswise.net/harbor/journey/1",
  "title": "Updated Title",
  "is_active": false,
  "created_at": "2025-06-04T00:07:00",
  "updated_at": "2026-04-03T12:00:00"
}
```

---

### 4. Events / Analytics

#### 4.1 List Events

| Aspect | Details |
|--------|---------|
| **Endpoint** | `GET /events` |
| **Input** | None |
| **Expected Status** | 200 OK |
| **Response Format** | JSON array of Event objects |

**Expected Response:**
```json
[
  {
    "id": 1,
    "url_id": 1,
    "user_id": 1,
    "event_type": "created",
    "timestamp": "2025-06-04T00:07:00",
    "details": {
      "short_code": "ALQRog",
      "original_url": "https://opswise.net/harbor/journey/1"
    }
  }
]
```

---

## Implementation Checklist

- [ ] Health endpoint returns 200 with status=ok
- [ ] User bulk import endpoint accepts CSV and returns count/imported
- [ ] User list endpoint with optional pagination
- [ ] User get by ID endpoint
- [ ] User create endpoint with validation (400/422 for invalid data)
- [ ] User update endpoint
- [ ] URL create endpoint with short_code generation
- [ ] URL list endpoint with optional filtering
- [ ] URL get by ID endpoint
- [ ] URL update endpoint
- [ ] Events list endpoint with proper structure

---

## Edge Cases & Hidden Tests

Your app will be evaluated on robust handling of edge cases. Consider:

1. **Users:**
   - Duplicate usernames/emails
   - Invalid email formats
   - Missing required fields
   - Type mismatches (e.g., integer for username)

2. **URLs:**
   - Invalid URL formats
   - User ID validation (non-existent users)
   - Duplicate short codes
   - URL length constraints

3. **Events:**
   - Proper timestamp formatting
   - Event type validation
   - Associated user/URL validation

---

## Notes

- All datetime fields should use ISO 8601 format (e.g., `2026-04-03T12:00:00`)
- Ensure proper HTTP status codes for all scenarios
- Validate input data and return meaningful error messages
- Consider pagination for large result sets
- Maintain data consistency across related entities