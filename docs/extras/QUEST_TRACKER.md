# 🎮 Vybe Production Engineering Quest Tracker

**MLH Hackathon - Production Engineering Quests**

Use this document to track progress on all 4 quest tracks. Check off items as they're completed!

---

## 🛡️ Quest: Reliability Engineering

**Mission:** Build a service that refuses to die easily.  
**Difficulty:** ⭐⭐ | **Status:** 🔴 Not Started

### Tier 1: Bronze (The Shield)
*Objective: Prove your code works before you ship it.*

- [ ] **Write Unit Tests** — Create a test suite using pytest. Test individual functions in isolation.
- [ ] **Automate Defense** — Set up GitHub Actions to run tests on every commit.
- [ ] **Pulse Check** — Create a /health endpoint that returns 200 OK.

**Verification:**
- [ ] CI Logs showing green/passing tests.
- [ ] A working GET /health endpoint.

---

### Tier 2: Silver (The Fortress)
*Objective: Stop bad code from ever reaching production.*

- [ ] **50% Coverage** — Use pytest-cov. Ensure half your code lines are hit by tests.
- [ ] **Integration Testing** — Write tests that hit the API (e.g., POST to /urls → Check DB).
- [ ] **The Gatekeeper** — Configure CI so deployment **fails** if tests fail.
- [ ] **Error Handling** — Document how your app handles 404s and 500s.

**Verification:**
- [ ] Coverage report showing >50%.
- [ ] Screenshot of a blocked deploy due to a failed test.

---

### Tier 3: Gold (The Immortal)
*Objective: Break it on purpose. Watch it survive.*

- [ ] **70% Coverage** — High confidence in code stability.
- [ ] **Graceful Failure** — Send bad inputs. The app must return clean errors (JSON), not crash.
- [ ] **Chaos Mode** — Kill the app process or container while it's running. Show it restarts automatically (e.g., Docker restart policy).
- [ ] **Failure Manual** — Document exactly what happens when things break (Failure Modes).

**Verification:**
- [ ] Live Demo: Kill the container → Watch it resurrect.
- [ ] Live Demo: Send garbage data → Get a polite error.
- [ ] Link to "Failure Mode" documentation.

---

## 🚀 Quest: Scalability Engineering

**Mission:** Make it handle the entire internet.  
**Difficulty:** ⭐⭐⭐ | **Status:** 🔴 Not Started

### Tier 1: Bronze (The Baseline)
*Objective: Stress test your system.*

- [ ] **Load Test** — Install k6 or Locust.
- [ ] **The Crowd** — Simulate **50 concurrent users** hitting your service.
- [ ] **Record Stats** — Document your Response Time (Latency) and Error Rate.

**Verification:**
- [ ] Screenshot of terminal output showing 50 concurrent users.
- [ ] Documented baseline p95 response time.

---

### Tier 2: Silver (The Scale-Out)
*Objective: One server isn't enough. Build a fleet.*

- [ ] **The Horde** — Ramp up to **200 concurrent users**.
- [ ] **Clone Army** — Run 2+ instances of your app (containers) using Docker Compose.
- [ ] **Traffic Cop** — Put a Load Balancer (Nginx) in front to split traffic between instances.
- [ ] **Speed Limit** — Keep response times under 3 seconds.

**Verification:**
- [ ] `docker ps` showing multiple app containers + 1 Nginx container.
- [ ] Load test results showing success with 200 users.

---

### Tier 3: Gold (The Speed of Light)
*Objective: Optimization and Caching.*

- [ ] **The Tsunami** — Handle **500+ concurrent users** (or 100 req/sec).
- [ ] **Cache It** — Implement Redis. Store results in memory so you don't hit the DB every time.
- [ ] **Bottleneck Analysis** — Find out what was slow before, and explain how you fixed it.
- [ ] **Stability** — Error rate must stay under 5% during the tsunami.

**Verification:**
- [ ] Evidence of Caching (headers, logs, or speed comparison).
- [ ] Load test results: 500 users with <5% errors.
- [ ] "Bottleneck Report" (2-3 sentences on what you fixed).

---

## 🚨 Quest: Incident Response

**Mission:** Be the one who knows when it breaks.  
**Difficulty:** ⭐⭐⭐ | **Status:** 🔴 Not Started

### Tier 1: Bronze (The Watchtower)
*Objective: Stop using print statements.*

- [ ] **Structured Logging** — Configure JSON logs. Include timestamps and log levels (INFO, WARN, ERROR).
- [ ] **Metrics** — Expose a /metrics endpoint (or similar) showing CPU/RAM usage.
- [ ] **Manual Check** — Have a way to view logs without SSH-ing into the server.

**Verification:**
- [ ] Screenshot of clean JSON logs.
- [ ] Screenshot of a /metrics page with data.

---

### Tier 2: Silver (The Alarm)
*Objective: Wake up the on-call engineer.*

- [ ] **Set Traps** — Configure alerts for "Service Down" and "High Error Rate."
- [ ] **Fire Drill** — Connect alerts to a channel (Slack, Discord, Email).
- [ ] **Speed** — Trigger must fire within 5 minutes of the failure.

**Verification:**
- [ ] **Live Demo:** Break the app → Phone/Laptop goes "Bing!" with a notification.
- [ ] Show the configuration (YAML/Code) for the alert logic.

---

### Tier 3: Gold (The Command Center)
*Objective: Total situational awareness.*

- [ ] **The Dashboard** — Build a visual board (Grafana/Datadog) tracking 4+ metrics (Latency, Traffic, Errors, Saturation).
- [ ] **The Runbook** — Write a "In Case of Emergency" guide. What do we do when the alert fires?
- [ ] **Sherlock Mode** — Diagnose a fake issue using *only* your dashboard and logs.

**Verification:**
- [ ] Screenshot of a beautiful, data-filled Dashboard.
- [ ] Link to the Runbook.
- [ ] Explanation of how you found a root cause using the dashboard.

---

## 📜 Bonus Quest: Documentation

**Mission:** The difference between a script and a product.  
**Reward:** Bonus Points + Eternal Glory | **Status:** 🔴 Not Started

### Bronze: The Map
- [ ] **README** — Setup instructions so clear a freshman could run your app.
- [ ] **Diagram** — Draw the architecture. Boxes and arrows showing App → DB.
- [ ] **API Docs** — List your endpoints (GET/POST) and what they do.

### Silver: The Manual
- [ ] **Deploy Guide** — How do we get this live? How do we rollback?
- [ ] **Troubleshooting** — "If X happens, try Y." Record the bugs you hit today and how you fixed them.
- [ ] **Config** — List all Environment Variables (DATABASE_URL, etc.) needed to run.

### Gold: The Codex
- [ ] **Runbooks** — Step-by-step guides for specific alerts (Required for Incident Response Gold).
- [ ] **Decision Log** — Why did you choose Redis? Why Nginx? Document your technical choices.
- [ ] **Capacity Plan** — How many users *can* we handle? Where is the limit?

---

## 📊 Progress Summary

| Quest | Bronze | Silver | Gold | Status |
|-------|--------|--------|------|--------|
| 🛡️ Reliability Engineering | ⬜ | ⬜ | ⬜ | 🔴 0/3 |
| 🚀 Scalability Engineering | ⬜ | ⬜ | ⬜ | 🔴 0/3 |
| 🚨 Incident Response | ⬜ | ⬜ | ⬜ | 🔴 0/3 |
| 📜 Documentation (Bonus) | ⬜ | ⬜ | ⬜ | 🔴 0/3 |

**Legend:**
- 🔴 Not Started (0 tiers)
- 🟡 In Progress (1-2 tiers)
- 🟢 Complete (3 tiers)

---

## 🛠️ Recommended Loadout

**Reliability Engineering:**
- pytest, pytest-cov, GitHub Actions

**Scalability Engineering:**
- k6 (or Locust), Nginx, Docker Compose, Redis

**Incident Response:**
- Prometheus, Grafana, Alertmanager, Discord Webhooks

**Documentation:**
- Markdown, Mermaid diagrams, README templates

---

## 📝 Notes

### Current Project Status
- **Backend Framework:** Flask + Peewee ORM
- **Database:** PostgreSQL 16
- **Infrastructure:** Docker Compose, Nginx reverse proxy
- **Monitoring Setup:** Prometheus, Grafana, AlertManager (already configured)
- **Architecture:** 4-layer design (Routes → Controllers → Services → Repositories)

### Key Dependencies Already in Place
- ✅ Docker & Docker Compose running
- ✅ Nginx load balancing configured
- ✅ Prometheus scraping @ 15s intervals
- ✅ Grafana dashboards available
- ✅ Structured logging with request IDs
- ✅ /health and /ready endpoints

### Immediate Next Steps (Recommendations)
1. **Phase 1 (Reliability Bronze):** Add pytest unit tests and validate /health endpoint
2. **Phase 2 (Reliability Silver-Gold):** Achieve 50%+ coverage, integration tests, graceful error handling
3. **Phase 3 (Documentation):** Parallel track - document as you build
4. **Phase 4 (Incident Response):** Leverage existing Prometheus/Grafana setup
5. **Phase 5 (Scalability):** Load test with k6, scale containers, add Redis caching

---

## 🎯 Acceptance Criteria Template (Copy-paste for issues)

```markdown
### Acceptance Criteria
- [ ] All checkboxes in the quest tier complete
- [ ] Verification requirements met
- [ ] Screenshots/evidence provided in comments
- [ ] Code merged to main branch
- [ ] QUEST_TRACKER.md updated with current status
```

---

**Last Updated:** April 4, 2026  
**Team:** Vybe Backend Engineers  
**Hackathon:** MLH Production Engineering
