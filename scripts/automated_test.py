#!/usr/bin/env python3
"""
Usage:
    python scripts/automated_test.py [BASE_URL]

    BASE_URL defaults to http://localhost:80
    For Cloudflare: python scripts/automated_test.py https://planners-sandra-commonwealth-hope.trycloudflare.com
"""

import io
import os
import sys
import time
import requests

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:80"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "backend", "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")

PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"

results = []


def req(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    try:
        resp = requests.request(method, url, timeout=15, **kwargs)
        return resp
    except Exception as e:
        print(f"       [REQUEST ERROR] {e}")
        return None


def has_response(resp):
    return resp is not None


def check(name, passed, details=""):
    status = PASS if passed else FAIL
    results.append((name, passed, details))
    print(f"  {status}  {name}")
    if not passed and details:
        print(f"         → {details}")


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


section("HEALTH")

r = req("GET", "/health")
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else {}
    check("test_health_check",
          ok and body.get("status") == "ok" and body.get("service") == "vybe-shortener",
          f"status={r.status_code}, body={r.text[:200]}")
else:
    check("test_health_check", False, "No response")


section("USERS")

print(f"\n  [INFO] Using real CSV: {USERS_CSV}")
if not os.path.exists(USERS_CSV):
    print(f"  [ERROR] users.csv not found at {USERS_CSV}")
    sys.exit(1)

with open(USERS_CSV, "rb") as f:
    csv_bytes = f.read()

# Count rows (minus header)
row_count = csv_bytes.count(b"\n") - 1
print(f"  [INFO] CSV row count: {row_count}")

r = req("POST", "/users/bulk",
        files={"file": ("users.csv", io.BytesIO(csv_bytes), "text/csv")})
bulk_ok = False
if has_response(r):
    bulk_ok = r.status_code in (200, 201)
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    check("test_load_users_csv",
          bulk_ok,
          f"status={r.status_code}, body={r.text[:300]}")
else:
    check("test_load_users_csv", False, "No response")

r = req("GET", "/users")
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    has_items = isinstance(body, list) and len(body) >= 1
    check("test_get_users_list",
          ok and has_items,
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_users_list", False, "No response")

r = req("GET", "/users", params={"page": 1, "per_page": 10})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    has_10 = isinstance(body, list) and len(body) == 10
    check("test_get_users_pagination",
          ok and has_10,
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'} (need exactly 10)")
else:
    check("test_get_users_pagination", False, "No response")

r = req("GET", "/users/1")
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else {}
    check("test_get_user_by_id",
          ok and body.get("id") == 1,
          f"status={r.status_code}, id={body.get('id')}, username={body.get('username')}")
else:
    check("test_get_user_by_id", False, "No response")

user_suffix = int(time.time() * 1000)
create_username = f"testuser_create_{user_suffix}"
create_email = f"{create_username}@example.com"
r = req("POST", "/users",
        json={"email": create_email, "username": create_username})
created_user_id = None
if has_response(r):
    ok = r.status_code == 201
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    created_user_id = body.get("id")
    match = (body.get("email") == create_email
             and body.get("username") == create_username)
    check("test_create_user",
          ok and match,
          f"status={r.status_code}, body={r.text[:300]}")
else:
    check("test_create_user", False, "No response")

r = req("PUT", "/users/1", json={"username": "updated_username"})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else {}
    check("test_update_user",
          ok and body.get("username") == "updated_username",
          f"status={r.status_code}, username={body.get('username')}")
else:
    check("test_update_user", False, "No response")

r = req("DELETE", "/users/200")
if has_response(r):
    check("test_delete_user",
          r.status_code in (200, 204),
          f"status={r.status_code}, body={r.text[:200]}")
else:
    check("test_delete_user", False, "No response")

r = req("GET", "/users/99999")
if has_response(r):
    check("test_get_nonexistent_user",
          r.status_code == 404,
          f"status={r.status_code}, body={r.text[:200]}")
else:
    check("test_get_nonexistent_user", False, "No response")


#  URLS --------- >>>
section("URLS")

# test_create_url — user_id=1 (quietpioneer19 from CSV)
r = req("POST", "/urls",
        json={"original_url": "https://example.com/test-create", "title": "Test Create URL", "user_id": 1})
created_url_id = None
created_short_code = None
if has_response(r):
    ok = r.status_code == 201
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    created_url_id = body.get("id")
    created_short_code = body.get("short_code")
    check("test_create_url",
          ok and bool(body.get("short_code")),
          f"status={r.status_code}, short_code={body.get('short_code')}, body={r.text[:300]}")
else:
    check("test_create_url", False, "No response")

r = req("GET", "/urls")
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_urls_list",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_urls_list", False, "No response")

target_url_id = created_url_id or 1
r = req("GET", f"/urls/{target_url_id}")
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else {}
    check("test_get_url_by_id",
          ok and body.get("id") == target_url_id,
          f"status={r.status_code}, id={body.get('id')}")
else:
    check("test_get_url_by_id", False, "No response")

r = req("GET", "/urls", params={"user_id": 1})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_urls_by_user",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_urls_by_user", False, "No response")

r = req("POST", "/urls",
        json={"original_url": "https://example.com/redirect-target", "title": "Redirect Test", "user_id": 1})
if has_response(r) and r.status_code == 201:
    redirect_code = r.json().get("short_code")
    check("test_redirect_short_code (create)", bool(redirect_code), f"short_code={redirect_code}")
    r2 = req("GET", f"/{redirect_code}", allow_redirects=False)
    if has_response(r2):
        check("test_redirect_short_code (redirect)",
              r2.status_code in (301, 302),
              f"status={r2.status_code}, location={r2.headers.get('Location')}")
    else:
        check("test_redirect_short_code (redirect)", False, "No response")
else:
    check("test_redirect_short_code", False,
          f"Create failed: status={r.status_code if r else 'no response'}")

# test_update_url — PUT /urls/<id>
url_id_to_update = created_url_id or 1
r = req("PUT", f"/urls/{url_id_to_update}", json={"title": "Updated Title"})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else {}
    check("test_update_url",
          ok and body.get("title") == "Updated Title",
          f"status={r.status_code}, title={body.get('title')}")
else:
    check("test_update_url", False, "No response")

# test_deactivate_url — PUT /urls/<id> with is_active=false
r = req("PUT", f"/urls/{url_id_to_update}", json={"is_active": False})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else {}
    check("test_deactivate_url",
          ok and body.get("is_active") is False,
          f"status={r.status_code}, is_active={body.get('is_active')}")
else:
    check("test_deactivate_url", False, "No response")

# test_get_active_urls — GET /urls?is_active=true
r = req("GET", "/urls", params={"is_active": "true"})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_active_urls",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_active_urls", False, "No response")

# test_delete_url — DELETE /urls/999 (likely doesn't exist → accept idempotent delete or 404)
r = req("DELETE", "/urls/999")
if has_response(r):
    check("test_delete_url",
          r.status_code in (200, 204, 404),
          f"status={r.status_code}, body={r.text[:200]}")
else:
    check("test_delete_url", False, "No response")


# Events --------------------- >>>
section("EVENTS")

r = req("GET", "/events")
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_events_list",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_events_list", False, "No response")

# test_get_events_by_url — GET /events?url_id=1
r = req("GET", "/events", params={"url_id": created_url_id or 1})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_events_by_url",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_events_by_url", False, "No response")

# test_get_events_by_user — GET /events?user_id=1
r = req("GET", "/events", params={"user_id": 1})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_events_by_user",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_events_by_user", False, "No response")

# test_get_events_by_type — GET /events?event_type=click
r = req("GET", "/events", params={"event_type": "click"})
if has_response(r):
    ok = r.status_code == 200
    body = r.json() if ok else []
    check("test_get_events_by_type",
          ok and isinstance(body, list),
          f"status={r.status_code}, count={len(body) if isinstance(body, list) else 'n/a'}")
else:
    check("test_get_events_by_type", False, "No response")

# test_create_event — POST /events
url_id_for_event = created_url_id or 1
r = req("POST", "/events",
        json={
            "details": {"referrer": "https://google.com"},
            "event_type": "click",
            "url_id": url_id_for_event,
            "user_id": 1
        })
if has_response(r):
    ok = r.status_code == 201
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    check("test_create_event",
          ok and body.get("event_type") == "click",
          f"status={r.status_code}, event_type={body.get('event_type')}, body={r.text[:300]}")
else:
    check("test_create_event", False, "No response")


# Summary ------------------------------ >>>
total = len(results)
passed = sum(1 for _, ok, _ in results if ok)
failed = total - passed

print(f"\n{'='*60}")
print(f"  RESULTS: {passed}/{total} passed  ({failed} failed)")
print(f"  Target URL: {BASE_URL}")
print(f"{'='*60}")

if failed > 0:
    print("\n  FAILED TESTS:")
    for name, ok, details in results:
        if not ok:
            print(f"    ❌  {name}")
            if details:
                print(f"         {details}")

print()
sys.exit(0 if failed == 0 else 1)
