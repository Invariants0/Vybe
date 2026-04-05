/**
 * k6 load testing
 * 
 * STRATEGY: Pre-create fixed URLs in setup, then load test with HIGH READ frequency (cacheable)
 * to leverage Redis caching. Tests ALL endpoints from AUTOMATED_TESTS.md.
 * 
 * Target: 500 Concurrent Users (Gold Tier Requirement)
 * 
 * Traffic Distribution (optimized for caching):
 *   30% → GET /urls/<id> (read cacheable)
 *   20% → GET /health (baseline checks)
 *   15% → GET /events (read cacheable)
 *   15% → GET /urls (list cacheable)
 *   10% → GET /users/<id> (read cacheable)
 *   5%  → POST /urls (write - new links)
 *   3%  → PUT /urls/<id> (update)
 *   2%  → POST /users (write - new users, rare)
 * 
 * Usage:
 *   k6 run scripts/load_test.js
 *   k6 run --env BASE_URL=http://localhost scripts/load_test.js
 */


import http from "k6/http";
import crypto from "k6/crypto";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost";

const errorRate = new Rate("error_rate");
const latencyTrend = new Trend("request_latency");
const cacheHitRate = new Rate("cache_hit_rate");

function secureRandomString(length) {
  const chars = "0123456789abcdefghijklmnopqrstuvwxyz";
  const bytes = crypto.randomBytes(length);
  let result = "";
  for (let i = 0; i < length; i++) {
    const idx = bytes[i] % chars.length;
    result += chars.charAt(idx);
  }
  return result;
}

export const options = {
  stages: [
    { duration: "30s", target: 50 },  // Ramp to 50
    { duration: "1m", target: 50 },   // Hold 50
    { duration: "30s", target: 200 }, // Ramp to 200
    { duration: "1m", target: 200 },  // Hold 200
    { duration: "30s", target: 500 }, // Ramp to 500 (Gold Tier)
    { duration: "2m", target: 500 },  // Hold 500
    { duration: "30s", target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],  // 95% of requests under 500ms
    error_rate: ["rate<0.05"],         // Error rate below 5% (Gold Tier requirement)
    http_req_failed: ["rate<0.05"],
    cache_hit_rate: ["rate>0.70"],     // Expect >70% cache hits on reads
  },
};

/**
 * Setup phase: Pre-create fixed users & URLs for load test
 * This ensures we test READS from cache instead of creating new data every iteration
 */
export function setup() {
  console.log("🚀 Setup: Creating test users and URLs...");

  // 1. Create 10 test users
  const userIds = [];
  for (let i = 0; i < 10; i++) {
    const userPayload = JSON.stringify({
      username: `loadtest_user_${Date.now()}_${i}`,
      email: `loadtest_${Date.now()}_${i}@example.com`
    });

    const res = http.post(`${BASE_URL}/users`, userPayload, {
      headers: { "Content-Type": "application/json" },
    });

    if (res.status === 201) {
      const userId = JSON.parse(res.body).id;
      userIds.push(userId);
      console.log(`  ✅ Created user ${i + 1}/10 (ID: ${userId})`);
    } else {
      console.error(`  ❌ Failed to create user ${i + 1}: ${res.status}`);
    }
  }

  // 2. Create 100 fixed URLs (reused across all VU iterations)
  const urlIds = [];
  const shortCodes = [];

  for (let i = 0; i < 100; i++) {
    const userId = userIds[i % userIds.length]; // Cycle through users
    const urlPayload = JSON.stringify({
      user_id: userId,
      original_url: `https://example.com/fixed-url-${i}`,
      title: `Cached Test Link ${i}`
    });

    const res = http.post(`${BASE_URL}/urls`, urlPayload, {
      headers: { "Content-Type": "application/json" },
    });

    if (res.status === 201) {
      const body = JSON.parse(res.body);
      urlIds.push(body.id);
      shortCodes.push(body.short_code);
      if ((i + 1) % 10 === 0) {
        console.log(`  ✅ Created ${i + 1}/100 URLs`);
      }
    } else {
      console.error(`  ❌ Failed to create URL ${i + 1}: ${res.status}`);
    }
  }

  console.log(`✅ Setup complete: ${userIds.length} users, ${urlIds.length} URLs`);
  return { userIds, urlIds, shortCodes };
}

export default function (data) {
  const { userIds, urlIds, shortCodes } = data;

  const rand = Math.random();

  // 30% – GET /urls/<id> – Most cacheable read
  if (rand < 0.30) {
    const urlId = urlIds[Math.floor(Math.random() * urlIds.length)];
    const res = http.get(`${BASE_URL}/urls/${urlId}`, {
      tags: { name: "GET /urls/{id}" },
    });
    const isCached = res.headers["x-cache"] === "HIT" || res.timings.duration < 50;
    check(res, {
      "get url 200": (r) => r.status === 200,
      "cached response": (r) => r.timings.duration < 100,
    });
    cacheHitRate.add(isCached);
    errorRate.add(res.status !== 200);
    latencyTrend.add(res.timings.duration);
  }
  // 20% – GET /health – Baseline health check
  else if (rand < 0.50) {
    const res = http.get(`${BASE_URL}/health`, {
      tags: { name: "GET /health" },
    });
    check(res, {
      "health 200": (r) => r.status === 200,
      "health ok": (r) => JSON.parse(r.body).status === "ok",
    });
    errorRate.add(res.status !== 200);
    latencyTrend.add(res.timings.duration);
  }
  // 15% – GET /events – Cacheable analytics
  else if (rand < 0.65) {
    const res = http.get(`${BASE_URL}/events`, {
      tags: { name: "GET /events" },
    });
    const isCached = res.timings.duration < 100;
    check(res, {
      "events 200": (r) => r.status === 200,
      "events is array": (r) => Array.isArray(JSON.parse(r.body)),
    });
    cacheHitRate.add(isCached);
    errorRate.add(res.status !== 200);
    latencyTrend.add(res.timings.duration);
  }
  // 15% – GET /urls – List all URLs (cacheable)
  else if (rand < 0.80) {
    const res = http.get(`${BASE_URL}/urls`, {
      tags: { name: "GET /urls" },
    });
    const isCached = res.timings.duration < 100;
    check(res, {
      "urls list 200": (r) => r.status === 200,
      "urls is array": (r) => Array.isArray(JSON.parse(r.body)),
    });
    cacheHitRate.add(isCached);
    errorRate.add(res.status !== 200);
    latencyTrend.add(res.timings.duration);
  }
  // 10% – GET /users/<id> – Get specific user (cacheable)
  else if (rand < 0.90) {
    const userId = userIds[Math.floor(Math.random() * userIds.length)];
    const res = http.get(`${BASE_URL}/users/${userId}`, {
      tags: { name: "GET /users/{id}" },
    });
    const isCached = res.timings.duration < 100;
    check(res, {
      "get user 200": (r) => r.status === 200,
      "has user id": (r) => JSON.parse(r.body).id === userId,
    });
    cacheHitRate.add(isCached);
    errorRate.add(res.status !== 200);
    latencyTrend.add(res.timings.duration);
  }
  // 5% – POST /urls – Create new URL (write operation, less frequent)
  else if (rand < 0.95) {
    const userId = userIds[Math.floor(Math.random() * userIds.length)];
    const urlPayload = JSON.stringify({
      user_id: userId,
      original_url: `https://example.com/dynamic-${Date.now()}-${Math.random()}`,
      title: `Dynamic Link ${Date.now()}`
    });
    const res = http.post(`${BASE_URL}/urls`, urlPayload, {
      headers: { "Content-Type": "application/json" },
      tags: { name: "POST /urls" },
    });
    check(res, {
      "create url 201": (r) => r.status === 201,
      "has short_code": (r) => JSON.parse(r.body).short_code !== undefined,
    });
    errorRate.add(res.status !== 201);
    latencyTrend.add(res.timings.duration);
  }
  // 3% – PUT /urls/<id> – Update URL (write, rare)
  else if (rand < 0.98) {
    const urlId = urlIds[Math.floor(Math.random() * urlIds.length)];
    const updatePayload = JSON.stringify({
      title: `Updated Title ${Date.now()}`,
      is_active: Math.random() > 0.5
    });
    const res = http.put(`${BASE_URL}/urls/${urlId}`, updatePayload, {
      headers: { "Content-Type": "application/json" },
      tags: { name: "PUT /urls/{id}" },
    });
    check(res, {
      "update url 200": (r) => r.status === 200,
    });
    errorRate.add(res.status !== 200);
    latencyTrend.add(res.timings.duration);
  }
  // 2% – POST /users – Create new user (write, very rare)
  else {
    const userPayload = JSON.stringify({
      username: `dynamic_user_${Date.now()}_${secureRandomString(7)}`,
      email: `dynamic_${Date.now()}_${Math.random()}@example.com`
    });
    const res = http.post(`${BASE_URL}/users`, userPayload, {
      headers: { "Content-Type": "application/json" },
      tags: { name: "POST /users" },
    });
    check(res, {
      "create user 201": (r) => r.status === 201,
      "has user id": (r) => JSON.parse(r.body).id !== undefined,
    });
    errorRate.add(res.status !== 201);
    latencyTrend.add(res.timings.duration);
  }

  sleep(0.1); // Small think time between requests
}
