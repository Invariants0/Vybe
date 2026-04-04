/**
 * load_test.js – Gold Tier k6 load testing script for Vybe
 * 
 * Target: 500 Concurrent Users (Gold Tier Requirement)
 * 
 * Usage:
 *   k6 run scripts/load_test.js
 *   k6 run --env BASE_URL=http://localhost scripts/load_test.js
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost";

// Custom metrics for Gold Tier observability
const errorRate = new Rate("error_rate");
const latencyTrend = new Trend("request_latency");
const redirectTrend = new Trend("redirect_latency");

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
  },
};

/**
 * Setup phase: Create a test user to use in the load test
 */
export function setup() {
  const userPayload = JSON.stringify({
    username: `loadtest_user_${Date.now()}`,
    email: `loadtest_${Date.now()}@example.com`
  });
  
  const res = http.post(`${BASE_URL}/users`, userPayload, {
    headers: { "Content-Type": "application/json" },
  });

  if (res.status !== 201) {
    console.error(`Setup failed: Could not create user. Status: ${res.status}`);
    return { userId: 1 }; // Fallback to a default ID
  }

  const userId = JSON.parse(res.body).id;
  console.log(`Setup complete: Created test user ID ${userId}`);
  return { userId: userId };
}

export default function (data) {
  const { userId } = data;

  // 1. Health check (Baseline)
  const healthRes = http.get(`${BASE_URL}/health`, {
    tags: { name: "GET /health" },
  });
  check(healthRes, {
    "health status 200": (r) => r.status === 200,
    "health body ok": (r) => JSON.parse(r.body).status === "ok",
  });
  errorRate.add(healthRes.status !== 200);
  latencyTrend.add(healthRes.timings.duration);

  sleep(0.1);

  // 2. Shorten a URL (Write Operation)
  const urlPayload = JSON.stringify({
    user_id: userId,
    original_url: `https://example.com/test/${Math.random().toString(36).substring(7)}`,
    title: `Load Test Link ${Date.now()}`
  });

  const createRes = http.post(`${BASE_URL}/urls`, urlPayload, {
    headers: { "Content-Type": "application/json" },
    tags: { name: "POST /urls" },
  });

  const createSuccess = check(createRes, {
    "create link 201": (r) => r.status === 201,
  });
  errorRate.add(!createSuccess);

  if (createSuccess) {
    const shortCode = JSON.parse(createRes.body).short_code;

  // 3. Resolve the link (Read/Redirect Operation - High Traffic Simulation)
  // We don't follow redirects during load test to measure the app's response time specifically
  // Backend route is GET /<code>, not /links/<code>
  const resolveRes = http.get(`${BASE_URL}/${shortCode}`, {
    redirects: 0,
    tags: { name: "GET /:code" },
  });

    check(resolveRes, {
      "redirect 302": (r) => r.status === 302,
    });
    
    redirectTrend.add(resolveRes.timings.duration);
  }

  sleep(0.2);
}
