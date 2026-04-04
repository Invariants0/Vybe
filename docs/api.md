# API Reference

Base path: `/api/v1`

## Create link

`POST /api/v1/links`

Request:

```json
{
  "url": "https://example.com/products/123",
  "custom_alias": "launch-2026",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

Response:

```json
{
  "id": 1,
  "code": "launch-2026",
  "short_url": "http://localhost:5000/launch-2026",
  "original_url": "https://example.com/products/123",
  "is_active": true,
  "click_count": 0,
  "created_at": "2026-04-04T10:00:00+00:00",
  "updated_at": "2026-04-04T10:00:00+00:00",
  "expires_at": "2026-12-31T23:59:59+00:00",
  "last_accessed_at": null
}
```

## Get link stats

`GET /api/v1/links/{code}`

Returns the short-link record plus `visit_count`.

## Get recent visits

`GET /api/v1/links/{code}/visits?limit=25`

Returns the most recent visit rows for the code.

## Update link

`PATCH /api/v1/links/{code}`

Request:

```json
{
  "is_active": false,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

Use `null` for `expires_at` to clear the expiry.

## Deactivate link

`DELETE /api/v1/links/{code}`

Soft-deletes a link by setting `is_active=false`.

## Redirect

`GET /{code}`

Redirects to the original URL and records analytics.

## Operational endpoints

- `GET /health`
- `GET /ready`
- `GET /api/v1/healthz`
