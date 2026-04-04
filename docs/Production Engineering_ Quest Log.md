# 🛡️ Quest: Reliability Engineering

# **← Check the Document Tabs for your Quest Options\!**

# **🛡️ Quest: Reliability Engineering**

### ***Build a service that refuses to die easily.***

**The Mission:** In the real world, code breaks. Your job is to build a safety net so strong that even when things go wrong, the service keeps running.  
**Difficulty:** ⭐⭐ (Good starting point)

 Hidden Reliability Score (Bonus up to +50)  
For this quest, some additional evaluator checks are intentionally not shown during development. These broadly reward resilient behavior under edge cases, such as rejecting bad input, preserving data consistency, enforcing uniqueness, handling invalid or inactive resources correctly, and maintaining expected behavior across core flows. Your hidden-check completion rate maps to a bonus tier of +10, +20, +35, or +50.

---

## **🥉 Tier 1: Bronze (The Shield)**

*Objective: Prove your code works before you ship it.*

### **⚔️ Main Objectives**

- [ ] **Write Unit Tests:** Create a test suite using pytest. Test individual functions in isolation.  
- [ ] **Automate Defense:** Set up GitHub Actions (or similar CI) to run tests on every commit.  
- [ ] **Pulse Check:** Create a /health endpoint that returns 200 OK.

### **💡 Intel**

**Unit Tests?** Don't test the whole app. Just test that *Input A* leads to *Output B*.  
**Health Check?** Load balancers use this to know if your app is alive. If this fails, no traffic for you.

### **✅ Verification (Loot)**

- [ ] CI Logs showing green/passing tests.  
- [ ] A working GET /health endpoint.

---

## **🥈 Tier 2: Silver (The Fortress)**

*Objective: Stop bad code from ever reaching production.*

### **⚔️ Main Objectives**

- [ ] **50% Coverage:** Use pytest-cov. Ensure half your code lines are hit by tests.  
- [ ] **Integration Testing:** Write tests that hit the API (e.g., POST to /shorten  → Check DB).  
- [ ] **The Gatekeeper:** Configure CI so deployment **fails** if tests fail.  
- [ ] **Error Handling:** Document how your app handles 404s and 500s.

### **💡 Intel**

**Blocking Deploys:** This is the \#1 rule of SRE. Never ship broken code.  
**Integration vs Unit:** Unit tests check the engine; integration tests check if the car drives.

### **✅ Verification (Loot)**

- [ ] Coverage report showing \>50%.  
- [ ] A screenshot of a blocked deploy due to a failed test.

---

## **🥇 Tier 3: Gold (The Immortal)**

*Objective: Break it on purpose. Watch it survive.*

### **⚔️ Main Objectives**

- [ ] **70% Coverage:** High confidence in code stability.  
- [ ] **Graceful Failure:** Send bad inputs. The app must return clean errors (JSON), not crash.  
- [ ] **Chaos Mode:** Kill the app process or container while it's running. Show it restarts automatically (e.g., Docker restart policy).  
- [ ] **Failure Manual:** Document exactly what happens when things break (Failure Modes).

### **💡 Intel**

**Chaos Engineering:** Don't wait for a crash at 3 AM. Cause the crash at 2 PM and fix it.  
**Graceful:** A user should see "Service Unavailable," not a Python stack trace.

### **✅ Verification (Loot)**

- [ ] Live Demo: Kill the container→Watch it resurrect.  
- [ ] Live Demo: Send garbage data→Get a polite error.  
- [ ] Link to "Failure Mode" documentation.

---

**🧰 Recommended Loadout:** pytest, pytest-cov, GitHub Actions

# 🚀 Quest: Scalability Engineering

# **🚀 Quest: Scalability Engineering**

### ***Make it handle the entire internet.***

**The Mission:** Your app works for one user. What happens when 500 people hit it at once? Find the breaking point and push past it.  
**Difficulty:** ⭐⭐⭐ (Requires system resources)

---

## **🥉 Tier 1: Bronze (The Baseline)**

*Objective: Stress test your system.*

### **⚔️ Main Objectives**

- [ ] **Load Test:** Install k6 or Locust.  
- [ ] **The Crowd:** Simulate **50 concurrent users** hitting your service.  
- [ ] **Record Stats:** Document your Response Time (Latency) and Error Rate.

### **💡 Intel**

**Concurrent Users:** This isn't total hits. This is 50 people clicking *at the exact same second*.  
**Baseline:** You can't improve what you don't measure.

### **✅ Verification (Loot)**

- [ ] Screenshot of terminal output showing 50 concurrent users.  
- [ ] Documented baseline p95 response time.

---

## **🥈 Tier 2: Silver (The Scale-Out)**

*Objective: One server isn't enough. Build a fleet.*

### **⚔️ Main Objectives**

- [ ] **The Horde:** Ramp up to **200 concurrent users**.  
- [ ] **Clone Army:** Run 2+ instances of your app (containers) using Docker Compose.  
- [ ] **Traffic Cop:** Put a Load Balancer (Nginx) in front to split traffic between instances.  
- [ ] **Speed Limit:** Keep response times under 3 seconds.

### **💡 Intel**

**Horizontal Scaling:** Don't make the server stronger (Vertical). Just add *more* servers (Horizontal).  
**Load Balancer:** The entry point. It decides which container does the work.

### **✅ Verification (Loot)**

- [ ] docker ps showing multiple app containers \+ 1 Nginx container.  
- [ ] Load test results showing success with 200 users.

---

## **🥇 Tier 3: Gold (The Speed of Light)**

*Objective: Optimization and Caching.*

### **⚔️ Main Objectives**

- [ ] **The Tsunami:** Handle **500+ concurrent users** (or 100 req/sec).  
- [ ] **Cache It:** Implement Redis. Store results in memory so you don't hit the DB every time.  
- [ ] **Bottleneck Analysis:** Find out what was slow before, and explain how you fixed it.  
- [ ] **Stability:** Error rate must stay under 5% during the tsunami.

### **💡 Intel**

**Caching:** The fastest query is the one you don't have to make.  
**Bottlenecks:** Is it the CPU? The Database? The Network? Find the weak link.

### **✅ Verification (Loot)**

- [ ] Evidence of Caching (headers, logs, or speed comparison).  
- [ ] Load test results: 500 users with \<5% errors.  
- [ ] "Bottleneck Report" (2-3 sentences on what you fixed).

---

**🧰 Recommended Loadout:** k6 (or Locust), Nginx, Docker Compose, Redis

---

# 

# 🚨 Quest: Incident Response

# **🚨 Quest: Incident Response**

### ***Be the one who knows when it breaks.***

**The Mission:** If a tree falls in the forest and no one logs it, did it make a sound? Build the eyes and ears of your infrastructure.  
**Difficulty:** ⭐⭐⭐ (Complex setup)

---

## **🥉 Tier 1: Bronze (The Watchtower)**

*Objective: Stop using print statements.*

### **⚔️ Main Objectives**

- [ ] **Structured Logging:** Configure JSON logs. Include timestamps and log levels (INFO, WARN, ERROR).  
- [ ] **Metrics:** Expose a /metrics endpoint (or similar) showing CPU/RAM usage.  
- [ ] **Manual Check:** Have a way to view logs without SSH-ing into the server.

### **💡 Intel**

**Structured Logs:** Computers can't read print("it broke"). They CAN read {"level": "ERROR", "component": "DB"}.  
**Metrics:** Logs tell you *what* happened. Metrics tell you *how much* is happening.

### **✅ Verification (Loot)**

- [ ] Screenshot of clean JSON logs.  
- [ ] Screenshot of a /metrics page with data.

---

## **🥈 Tier 2: Silver (The Alarm)**

*Objective: Wake up the on-call engineer.*

### **⚔️ Main Objectives**

- [ ] **Set Traps:** Configure alerts for "Service Down" and "High Error Rate."  
- [ ] **Fire Drill:** Connect alerts to a channel (Slack, Discord, Email).  
- [ ] **Speed:** Trigger must fire within 5 minutes of the failure.

### **💡 Intel**

**Alert Fatigue:** Don't alert on everything. Only alert if a human needs to wake up and fix it.  
**Thresholds:** "Alert if CPU \> 90% for 2 minutes."

### **✅ Verification (Loot)**

- [ ] **Live Demo:** Break the app→ Phone/Laptop goes "Bing\!" with a notification.  
- [ ] Show the configuration (YAML/Code) for the alert logic.

---

## **🥇 Tier 3: Gold (The Command Center)**

*Objective: Total situational awareness.*

### **⚔️ Main Objectives**

- [ ] **The Dashboard:** Build a visual board (Grafana/Datadog) tracking 4+ metrics (Latency, Traffic, Errors, Saturation).  
- [ ] **The Runbook:** Write a "In Case of Emergency" guide. What do we do when the alert fires?  
- [ ] **Sherlock Mode:** Diagnose a fake issue using *only* your dashboard and logs.

### **💡 Intel**

**The Runbook:** At 3 AM, you are not functioning. The Runbook does not sleep. Write instructions for your nonfunctional 3 AM self.  
**Golden Signals:** Latency, Traffic, Errors, Saturation.

### **✅ Verification (Loot)**

- [ ] Screenshot of a beautiful, data-filled Dashboard.  
- [ ] Link to the Runbook.  
- [ ] Explanation of how you found a root cause using the dashboard.

---

**🧰 Recommended Loadout:** Prometheus, Grafana, Alertmanager, Discord Webhooks

---

# 

# 📜 Bonus Quest: Documentation

# **📜 Bonus Quest: Documentation**

### ***The difference between a script and a product.***

**The Mission:** Write the manual. Good docs save lives (and sleep). You can do this alongside any other track.  
**Reward:** Bonus Points \+ Eternal Glory

---

## **🥉 Bronze: The Map**

- [ ] **README:** Setup instructions so clear a freshman could run your app.  
- [ ] **Diagram:** Draw the architecture. Boxes and arrows showing App→ DB.  
- [ ] **API Docs:** List your endpoints (GET/POST) and what they do.

## **🥈 Silver: The Manual**

- [ ] **Deploy Guide:** How do we get this live? How do we rollback?  
- [ ] **Troubleshooting:** "If X happens, try Y." Record the bugs you hit today and how you fixed them.  
- [ ] **Config:** List all Environment Variables (DATABASE\_URL, API\_KEY) needed to run.

## **🥇 Gold: The Codex**

- [ ] **Runbooks:** Step-by-step guides for specific alerts (Required for Incident Response Gold).  
- [ ] **Decision Log:** Why did you choose Redis? Why Nginx? Document your technical choices.  
- [ ] **Capacity Plan:** How many users *can* we handle? Where is the limit?

### **💡 Pro Tip**

Treat docs like code. Commit them to the repo. If it isn't written down, it doesn't exist.

