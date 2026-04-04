# K6 Load Test Report

Date: 2026-04-04
Run: k6 run scripts/load_test.js
Target: 500 VUs (Gold Tier)
Base URL: http://localhost (default)

## Summary
- Result: Thresholds failed
- p95 latency: 1.16s (threshold p95 < 500ms failed)
- http_req_failed: 33.33% (threshold rate < 5% failed)
- error_rate (custom): 0.00% (passed)

## Does This Satisfy Quest Requirements?
No. The Quest/Gold-tier requirement in the test script expects p(95) < 500ms and failure rate < 5%. This run recorded p95 = 1.16s and http_req_failed = 33.33%, so it does not satisfy the requirement.

## Test Configuration (from scripts/load_test.js)
Stages:
- 30s -> 50 VUs
- 1m hold 50 VUs
- 30s -> 200 VUs
- 1m hold 200 VUs
- 30s -> 500 VUs
- 2m hold 500 VUs
- 30s ramp down

Requests per iteration:
- GET /health
- POST /urls
- GET /{short_code} (redirect check, redirects disabled)

Setup:
- POST /users to create a load-test user, reused for all iterations

## Key Findings
1) Redirect endpoint mismatch (fixed)
- The backend route is GET /{code} (root path).
- The load test previously called /links/{code}, which produced 404s and 0% redirect checks.
- Fixed in scripts/load_test.js to call /{code} and added k6 tags to reduce URL cardinality.

2) Metrics cardinality warnings
- k6 warned about >100k unique time series because each unique short code was treated as a separate URL tag.
- Added name tags (GET /health, POST /urls, GET /:code) to group metrics by endpoint.

3) Latency above p95 SLA
- p95 latency was ~1.16s at 500 VUs, above the 500ms threshold.
- Redirect path logs an event on every access, which adds a DB write per read and increases latency.

4) Grafana not showing metrics (root cause fixed)
- Prometheus scrape targets were set to app1/app2, but docker-compose service names are vybe_app1/vybe_app2.
- Updated monitoring/prometheus/prometheus.yml to scrape vybe_app1:5000 and vybe_app2:5000.

5) Redis not in use
- No backend code references Redis; there is no caching or Redis client configured.
- The Redis container stays mostly idle and logs show only startup and a security warning from invalid requests.

## Issues (Observed)
1) Redirect endpoint mismatch (root cause of 302 check failure)
- Load test called `/links/{code}` but backend route is `/{code}`.
- Result: redirect check failed 100% in the run (0/72,216).

2) High k6 metric cardinality
- k6 warned about >100k unique time series (short codes create unique URL tags).
- Risk: higher memory usage, noisy or distorted dashboards.

3) Latency above Gold-tier SLA
- `http_req_duration p95 = 1.16s` vs target `p(95) < 500ms`.
- Result: threshold failed.

4) Grafana not showing metrics
- Prometheus scrape targets were `app1/app2`, but compose service names are `vybe_app1/vybe_app2`.
- Result: Prometheus had no data to visualize in Grafana.

5) Redis not utilized
- Redis container running but no app code uses it (no cache, no client, no config).
- Result: idle resource; does not reduce DB load during read-heavy redirect traffic.

6) Grafana 401s in logs
- `/api/live/ws` and `/api/ds/query` returning 401 until authenticated.
- Result: dashboards show no data unless Grafana session/auth is established.

7) Redis security warning
- Redis logged a possible cross-protocol scripting attempt from `172.19.0.1`.
- Risk: Redis exposed on host port; should be internal-only or protected.

## Improvements (Recommended)
1) Fix redirect endpoint used by load test
- Already applied: `GET /{code}` and k6 endpoint tags in `scripts/load_test.js`.

2) Reduce k6 cardinality
- Keep `tags: { name: "GET /:code" }` for the redirect and fixed tags for `/health` and `/urls`.
- Consider disabling per-URL tags for dynamic paths if you add more.

3) Bring p95 under 500ms
- Add DB indexes on `ShortURL.short_code` and `Event.url_id` if missing.
- Avoid write-on-read at high load: make event logging async/sampled or queue-based.
- Consider caching short code lookups in Redis with short TTL.

4) Fix Prometheus scrape targets (Grafana visibility)
- Already applied: `vybe_app1:5000`, `vybe_app2:5000` in `monitoring/prometheus/prometheus.yml`.
- Restart Prometheus to reload config.

5) Secure Redis and internalize access
- Remove host port `6379:6379` unless needed externally.
- Bind to the internal network only; add auth if you must expose it.

6) Fix Grafana auth for dashboards
- Log in to Grafana (`admin` / `admin`) and confirm data source is connected.
- Ensure dashboards are provisioned and using the Prometheus datasource UID.

7) Re-run k6 after fixes
- Verify redirect check passes and `http_req_failed < 5%`.
- Re-check p95 latency after any caching/indexing/logging changes.

## Improvements Implemented (This Pass)
- Fixed load-test redirect path and added endpoint tags in `scripts/load_test.js`.
- Fixed Prometheus scrape targets in `monitoring/prometheus/prometheus.yml`.
- Added Redis cache support for short code resolution in `backend/app/services/url_service.py`.
- Added Redis configuration keys in `backend/app/config/settings.py` and `backend/.env`.
- Enabled event log sampling via `EVENT_LOG_SAMPLE_RATE` (set to 0.2 in `backend/.env`).
- Added Redis client dependency (`redis>=5.0.0`) in `pyproject.toml`.
- Removed Redis host port exposure in `docker-compose.yml`.
- Enabled Grafana anonymous viewer access in `docker-compose.yml` to prevent 401s on dashboards.

## Re-run Status
- Attempted `k6 run scripts/load_test.js`, but the command timed out at 2 minutes because the default test duration is ~6 minutes.
- Re-run is still required to capture final thresholds and latency after fixes.

## Thresholds (Raw Output)
```
█ THRESHOLDS

  error_rate
  ✓ 'rate<0.05' rate=0.00%

  http_req_duration
  ✗ 'p(95)<500' p(95)=1.16s

  http_req_failed
  ✗ 'rate<0.05' rate=33.33%
```

## Total Results (Raw Output)
```
█ TOTAL RESULTS

  checks_total.......: 288864 801.821489/s
  checks_succeeded...: 75.00% 216648 out of 288864
  checks_failed......: 25.00% 72216 out of 288864

  ✓ health status 200
  ✓ health body ok
  ✓ create link 201
  ✗ redirect 302
    ↳  0% — ✓ 0 / ✗ 72216

  CUSTOM
  error_rate.....................: 0.00%  0 out of 144432
  redirect_latency...............: avg=331.376427 min=1.5505   med=182.33575 max=3155.1442 p(90)=862.4246 p(95)=1141.811475
  request_latency................: avg=332.201697 min=1.0604   med=186.30425 max=3137.5875 p(90)=862.8273 p(95)=1133.138275

  HTTP
  http_req_duration..............: avg=348.77ms   min=1.06ms   med=203.54ms  max=3.22s     p(90)=883.96ms p(95)=1.16s
    { expected_response:true }...: avg=357.46ms   min=1.06ms   med=214.02ms  max=3.22s     p(90)=893.52ms p(95)=1.17s
  http_req_failed................: 33.33% 72216 out of 216649
  http_reqs......................: 216649 601.368893/s

  EXECUTION
  iteration_duration.............: avg=1.35s      min=317.15ms med=1.04s     max=6.85s     p(90)=2.68s    p(95)=3.14s
  iterations.....................: 72216  200.455372/s
  vus............................: 5      min=2               max=500
  vus_max........................: 500    min=500             max=500

  NETWORK
  data_received..................: 76 MB  210 kB/s
  data_sent......................: 27 MB  75 kB/s
```

## Infrastructure Snapshot (500 VU load)
From the provided screenshot:
- vybe: ~910% CPU
- vybe_db: ~152% CPU
- vybe_redis: ~1% CPU
- vybe_alertmanager: ~0.24% CPU
- vybe_prometheus: ~0.14% CPU
- vybe_app1: ~343% CPU
- vybe_app2: ~339% CPU
- vybe_grafana: ~0.11% CPU
- vybe_nginx: ~74% CPU

## Action Items
- Re-run k6 after the path fix and verify redirect 302 checks pass.
- Confirm Prometheus scraping and Grafana dashboards load after updating targets.
- Evaluate caching strategy if Redis is required by the quest (e.g., cache short_code lookups or recently used links).
- Investigate p95 latency hotspots (DB write on redirect, DB indexing, Nginx upstream limits).

## Files Updated
- scripts/load_test.js
- monitoring/prometheus/prometheus.yml
