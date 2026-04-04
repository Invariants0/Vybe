# K6 Load Test Report 4 - Gold Tier Assessment

**Date:** April 4, 2026  
**Test Duration:** 6m0s (full run)  
**Target:** 500 Concurrent VUs (Gold Tier Requirement)  
**Base URL:** http://localhost (default)  
**Traffic Pattern:** 30% GET /urls/{id}, 20% GET /health, 15% GET /events, 15% GET /urls, 10% GET /users/{id}, 5% POST /urls, 3% PUT /urls/{id}, 2% POST /users

---

## 🎯 Executive Summary

**Status:** ⚠️ **PARTIAL PASS — High Latency + Poor Cache Hit Rate**

| Metric | Result | Threshold | Status |
|--------|--------|-----------|--------|
| **p95 Latency** | 4.96s | <500ms | ❌ FAILED |
| **Error Rate** | 0.00% | <5% | ✅ PASSED |
| **HTTP Failures** | 0.00% | <5% | ✅ PASSED |
| **Cache Hit Rate** | 10.87% | >70% | ❌ FAILED |
| **Total Requests** | 50,276 | - | - |
| **Iterations** | 50,166 | - | - |
| **Avg Latency** | 1.84s | <200ms target | ❌ FAILED |

---

## 📊 Detailed Metrics Breakdown

### Performance Metrics

```
HTTP Requests Latency (ms):
├─ Average.........: 1,854 ms
├─ Median.........: 1,381 ms
├─ P90............: 4,296 ms
├─ P95............: 4,968 ms (threshold: <500ms)
├─ Min............: 1.86 ms
└─ Max............: 7,583 ms

Request Volume:
├─ Total Requests.....: 50,276
├─ Requests/sec.......: 139.07/s
├─ Iterations.........: 50,166
├─ Iterations/sec....: 138.77/s
└─ Duration..........: 360.1s

Errors & Failures:
├─ Error Rate.........: 0.00% ✅
├─ HTTP Failed........: 0.00% ✅
├─ Check Success.....: 87.99% (86,920/98,781)
└─ Check Failures....: 12.00% (11,861/98,781)

Data Transfer:
├─ Received..........: 332 MB
├─ Sent.............: 4.4 MB
└─ Rate.............: 919 kB/s (RX)
```

### Redis Cache Performance

**Result: ❌ POOR**

```
Custom Metrics:
├─ cache_hit_rate.....: 10.87% (3,836/35,261) — Expected >70%, GOT 10.87%
├─ request_latency....: avg=1,851.45ms, p95=4,968.54ms
└─ Iteration Duration.: avg=1.95s

Check Results:
├─ health 200.........: ✅ 100% pass
├─ get url 200........: ✅ 100% pass
├─ cached response....: ❌ 21% pass (expected 70%+)
└─ other checks.......: ✅ 100% pass
```

---

## 🚨 Critical Issues Identified

### Issue 1: **Latency WAY Too High** (4.96s p95 vs 500ms threshold)

**Root Cause Analysis:**

```
Expected Flow (with cache):
  GET /urls/123 → Redis HIT (1-5ms) → Return cached JSON → Done

Actual Flow (observed):
  GET /urls/123 → Slow query (1-5s) → Return data → MISS cache

✗ Most requests taking 1-5 seconds
✗ No benefit from Redis cache layer
✗ Backend queries are bottleneck
```

**Possible Causes:**
1. ⚠️ **Cache not implemented on GET endpoints** — Backend may not be caching responses
2. ⚠️ **Database query performance** — Queries taking 1-5s (N+1 queries, missing indexes)
3. ⚠️ **Redis not being used** — Cache layer configured but not wired to routes
4. ⚠️ **No cache-control headers** — Responses not marked as cacheable

---

### Issue 2: **Cache Hit Rate 10.87% (Expected >70%)**

**Analysis:**

```
cache_hit_rate metric: 10.87% (3,836 hit checks / 35,261 total reads)

Why it's failing:

30% of test is GET /urls/{id}
├─ Should be cached in Redis
├─ First request: DB hit (slow) → Store in Redis
└─ Repeat requests: Redis HIT (fast)

But observed:
├─ Most GET requests taking 1-5s (no cache speed benefit)
├─ Cache hit rate detects response.timings.duration < 100ms
└─ Only 21% of responses fast enough → indicates MISS rate is 79%
```

**Evidence:**

```yaml
cached response check:
  ✓ 3,173 passes (21%) — <100ms responses
  ✗ 11,861 failures (79%) — >100ms responses (cache misses)
```

---

### Issue 3: **Setup Phase Created 100 Fixed URLs, But Cache Isn't Reusing Them**

```
Setup created:
  ✅ 10 test users
  ✅ 100 fixed URLs (IDs 1-100)

Runtime expected:
  Random VU picks URL from 1-100
  First access → DB query → Store in Redis
  Second access → Redis HIT (fast)
  
Observed:
  All accesses slow (1-5s) → No cache reuse happening
```

---

## 📋 Quest 2 Compliance Check (Scalability Engineering — Gold Tier)

### Gold Tier Requirement: "Implement Redis. Store results in memory so you don't hit the DB every time."

| Requirement | Expected | Actual | Status |
|-------------|----------|--------|--------|
| **Handle 500 concurrent users** | 500 VUs | 500 VUs reached | ✅ PASS |
| **Redis caching implemented** | Cache hit rate >70% | Cache hit rate 10.87% | ❌ **FAIL** |
| **Error rate <5%** | <5% | 0.00% | ✅ PASS |
| **Response time < 3s** | p95 <500ms | p95 4.96s | ❌ **FAIL** |
| **Bottleneck analysis documented** | Yes | Partial | ⚠️ PENDING |

**Verdict:** ❌ **Gold Tier NOT ACHIEVED** — Cache layer not working properly

---

## 🔧 Root Cause Deep Dive

### Hypothesis 1: Redis Not Wired to Routes

**Check:**
```bash
# Does the backend have cache decorators on GET routes?
grep -r "@cache" backend/app/routes/
grep -r "cache_get\|cached_response" backend/app/routes/
```

If empty → **Routes are NOT using Redis cache**

### Hypothesis 2: Cache Expiry Too Short

```
If cache.get() returns None on second request:
├─ TTL might be <1s (consumed before second VU hits)
└─ Or cache key mismatch (different key for same URL)
```

### Hypothesis 3: Load Is Distributed Across 2 Instances

```
Scenario:
  VU1 requests /urls/50 → app1 → Cache in Redis
  VU2 requests /urls/50 → app2 → Redis HIT (works)
  
But if:
  - Redis connection pool exhausted
  - Cache key collision
  - No cache invalidation strategy
  
Then both might do DB queries anyway.
```

---

## 📊 Throughput Analysis

```
Actual Performance:
├─ 50,166 iterations in 360s
├─ 138.77 iterations/sec
├─ 139.07 requests/sec
└─ Avg iteration time: 1.95s

Gold Tier expects:
├─ With Redis: 200+ req/sec (10-50ms per request)
├─ Actual: 139 req/sec (1,800ms per request)

Performance deficit:
  139 req/sec ÷ 200 = 69% of expected throughput
  (or 1.43x slower than target)
```

---

## ✅ What Passed

- ✅ **0% Error Rate** — No crashes, bad requests, or 500s
- ✅ **0% HTTP Failures** — All requests completed successfully
- ✅ **500 VUs Reached** — Load test ramped to target without breaking
- ✅ **Network Stable** — 332 MB data transferred without drops
- ✅ **Setup Worked** — 10 users and 100 URLs created successfully

---

## ❌ What Failed

1. ❌ **Cache Hit Rate 10.87% (Expected >70%)**
   - Most reads bypassing Redis
   - No performance benefit from caching layer

2. ❌ **P95 Latency 4.96s (Expected <500ms)**
   - 10x slower than gold tier requirement
   - Caused by slow database queries or cache misses

3. ❌ **Cached Response Check 79% Failure Rate**
   - 79% of responses took >100ms
   - Indicates cache layer not reducing latency

---

## 🎯 Next Steps to Fix

### Priority 1: Verify Cache Wiring (CRITICAL)

```bash
# Check if backend routes have cache decorators
cat backend/app/routes/url_routes.py | grep -A 5 "@url_bp.route.*GET"

# Check if Redis is being used
docker exec vybe_redis redis-cli keys "*" | wc -l
docker exec vybe_redis redis-cli info stats
```

**Action:** Wire HTTP GET responses to Redis cache with:
```python
# On GET endpoint:
cache.set(f"url:{url_id}", json_response, ttl=300)

# On subsequent GET:
cached = cache.get(f"url:{url_id}")
if cached: return cached  # <1ms response
```

### Priority 2: Add Cache-Control Headers

```python
@app.after_request
def add_cache_headers(response):
    if request.method == "GET":
        response.headers["Cache-Control"] = "max-age=300, public"
    return response
```

### Priority 3: Run with Specific Metrics

```bash
# Run test with cache debugging
k6 run scripts/load_test.js --out json=results.json

# Analyze cache hits vs misses
grep "cache_hit_rate\|cached_response" results.json
```

### Priority 4: Load Test Again

Once cache is wired:
```bash
k6 run scripts/load_test.js
# Expected: p95 <500ms, cache_hit_rate >70%
```

---

## 📈 Performance Goals vs Actual

```
Metric                 | Target  | Actual    | Gap
─────────────────────────────────────────────────
p95 Latency           | 500ms   | 4,968ms   | -992% (10x slower)
Cache Hit Rate        | >70%    | 10.87%    | -85% (far below)
Error Rate            | <5%     | 0.00%     | ✅ Pass
Throughput            | 200/s   | 139/s     | -30%
Iteration Time        | <1s     | 1.95s     | -95%
```

---

## 📝 Lessons Learned

1. **Pre-creating test data is good**, but **cache must be actively used** to get the benefit
2. **Latency is the bottleneck**, not error rate — errors were 0% but latency failed
3. **Response time indicators** (e.g., <100ms check) revealed cache layer isn't working
4. **Load test worked without errors** — infrastructure is stable, just performance tuning needed

---

## 🔴 Blockers for Quest 2 Gold Tier

To achieve gold tier, we need:

- [ ] **Cache layer wired to GET endpoints** (reading from Redis on cache hit)
- [ ] **Cache hit rate >70%** on repeated reads of same URLs
- [ ] **P95 latency <500ms** (currently 4.96s)
- [ ] **Bottleneck report** documenting the fix

---

## 📎 Artifacts

**Test Files:**
- Load test script: `scripts/load_test.js`
- Prometheus config: `monitoring/prometheus/prometheus.yml`
- Grafana dashboard: `monitoring/grafana/dashboards/system-dashboard.json`

**Output Summary:**
```
Total Requests: 50,276
Total Iterations: 50,166
Duration: 6m0s
Avg Latency: 1,854ms
P95 Latency: 4,968ms
Error Rate: 0.00%
Cache Hit Rate: 10.87%
```

---

## 🚀 Recommendation

**Current Status:** Infrastructure is **stable** (0 errors) but **slow** (latency too high).

**Action:** 
1. Fix cache layer wiring (1-2 hours)
2. Run load test again
3. Should see p95 drop from 4.96s → <500ms
4. Cache hit rate should jump from 10.87% → >70%

**Timeline:** Can achieve gold tier within 1 day with proper caching implementation.

---

**Report Generated:** April 4, 2026  
**Next Run:** After cache layer debugging  
**Owner:** Vybe Backend Team
