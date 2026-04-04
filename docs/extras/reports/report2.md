# K6 Load Test Report 2

Date: 2026-04-04
Run: k6 run scripts/load_test.js
Target: 500 VUs (Gold Tier)
Base URL: http://localhost (default)

## Summary
- Result: Thresholds passed for observed duration
- p95 latency: 297.59ms (threshold p95 < 500ms passed)
- http_req_failed: 0.00% (passed)
- error_rate (custom): 0.00% (passed)

## Does This Satisfy Quest Requirements?
Partially. The run met the p95 and error thresholds, but the test was interrupted at 3m03s (not a full 6m run). A full-duration run is still needed for final Gold-tier proof.

## Thresholds (Raw Output)
```
¦ THRESHOLDS

  error_rate
  ? 'rate<0.05' rate=0.00%

  http_req_duration
  ? 'p(95)<500' p(95)=297.59ms

  http_req_failed
  ? 'rate<0.05' rate=0.00%
```

## Total Results (Raw Output)
```
¦ TOTAL RESULTS

  checks_total.......: 137520  751.124356/s
  checks_succeeded...: 100.00% 137520 out of 137520
  checks_failed......: 0.00%   0 out of 137520

  ? health status 200
  ? health body ok
  ? create link 201
  ? redirect 302

  CUSTOM
  error_rate.....................: 0.00%  0 out of 68783
  redirect_latency...............: avg=85.139702 min=1.1295   med=47.37555 max=816.0594 p(90)=225.7138  p(95)=282.279295
  request_latency................: avg=79.066984 min=0.5363   med=38.4858  max=755.1944 p(90)=216.09006 p(95)=272.86272

  HTTP
  http_req_duration..............: avg=93.15ms   min=536.29µs med=56.05ms  max=868.33ms p(90)=238.4ms   p(95)=297.59ms
    { expected_response:true }...: avg=93.15ms   min=536.29µs med=56.05ms  max=868.33ms p(90)=238.4ms   p(95)=297.59ms
  http_req_failed................: 0.00%  0 out of 103084
  http_reqs......................: 103084 563.037399/s

  EXECUTION
  iteration_duration.............: avg=583.62ms  min=312.33ms med=529.03ms max=1.99s    p(90)=940.32ms  p(95)=1.05s

  iterations.....................: 34252  187.081962/s
  vus............................: 229    min=2           max=229
  vus_max........................: 500    min=500         max=500

  NETWORK
  data_received..................: 43 MB  237 kB/s
  data_sent......................: 13 MB  69 kB/s
```

## Notes
- Redirect checks pass (302).
- Latency meets the Gold-tier SLA in the observed window.
- The run was interrupted at 3m03s; full 6m run is still needed for final proof.

## Redis Cache Proof (Validated)
Collected during load:
```
# Keyspace
+db0:keys=21818,expires=21818,avg_ttl=249605,subexpiry=0
+keyspace_hits:21874
+keyspace_misses:0
```
Interpretation:
- Redis is actively storing keys and serving cache hits.
- Cache layer is working.

## CPU Snapshot (During Load)
From the provided image at ~200 VUs:
- vybe_app1: ~340% CPU
- vybe_app2: ~328% CPU
- vybe_db: ~145% CPU
- vybe_nginx: ~58% CPU
- vybe_redis: ~13% CPU

## Quest 2 Compliance Check (Scalability)
- 500 VU test: Started and passed thresholds, but interrupted early.
- Redis caching: Verified with keyspace and hits.
- Evidence: Screenshot and Redis stats captured.

## Remaining Actions for Final Gold Proof
- Run full 6m test without interruption.
- Capture terminal screenshot at completion.
- Capture Grafana dashboard screenshot with live traffic.
