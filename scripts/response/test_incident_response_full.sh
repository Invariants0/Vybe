#!/bin/bash
# Full Incident Response Test Suite
# Tests: 3 (DB Down), 4 (CPU Spike), 5 (Memory Pressure), 6 (Redis Failure)

set -e

echo "🧪 INCIDENT RESPONSE TEST SUITE - FULL"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
wait_and_prompt() {
    local test_name=$1
    local wait_time=$2
    echo -e "${YELLOW}⏱  Waiting ${wait_time}s for alerts to fire...${NC}"
    sleep $wait_time
    echo ""
    echo "Check:"
    echo "  - Discord notifications"
    echo "  - Grafana dashboards"
    echo "  - Alert manager"
    echo ""
    read -p "Did the test PASS? (y/n): " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

restore_service() {
    local service=$1
    echo "🔄 Restoring $service..."
    docker start $service
    sleep 5
}

echo "📋 Prerequisites Check"
echo "----------------------"
docker compose ps
echo ""
read -p "Are all services running? (y/n): " ready
if [[ ! "$ready" =~ ^[Yy]$ ]]; then
    echo "Please start services with: docker compose up -d"
    exit 1
fi
echo ""

# TEST 3: Database Down
echo "🧪 TEST 3: Database Down (Critical)"
echo "===================================="
echo "🔥 Stopping database..."
docker stop vybe_db
echo ""
echo "⏱  Expected within 90s:"
echo "  - Alert: PostgresDown"
echo "  - Alert: HighErrorRate"
echo "  - Grafana: Errors spike, DB connections = 0"
echo ""
echo "🔍 Debug commands:"
echo "  docker logs vybe_app1 --tail 50"
echo ""
wait_and_prompt "TEST 3: Database Down" 90
restore_service "vybe_db"
sleep 10

# TEST 4: CPU Spike
echo "🧪 TEST 4: CPU Spike"
echo "===================="
echo "🔥 Creating CPU load..."
docker exec -d vybe_app1 sh -c "timeout 120 yes > /dev/null 2>&1 || true" &
echo ""
echo "⏱  Expected within 2-5 min:"
echo "  - Alert: HighCPUUsage"
echo "  - Grafana: CPU panel spikes"
echo "  - Possible latency increase"
echo ""
echo "🔍 Debug commands:"
echo "  docker stats --no-stream"
echo ""
wait_and_prompt "TEST 4: CPU Spike" 150
echo "⏳ Waiting for CPU to normalize..."
sleep 30

# TEST 5: Memory Pressure
echo "🧪 TEST 5: Memory Pressure"
echo "=========================="
echo "🔥 Creating memory pressure..."
docker exec -d vybe_app1 python -c "import time; a=[0]*10**8; time.sleep(120)" 2>/dev/null || true &
echo ""
echo "⏱  Expected within 2-5 min:"
echo "  - Alert: HighMemoryUsage"
echo "  - Possible: container restart, latency increase"
echo ""
echo "🔍 Debug commands:"
echo "  docker stats --no-stream"
echo "  docker logs vybe_app1 --tail 50"
echo ""
wait_and_prompt "TEST 5: Memory Pressure" 150
echo "⏳ Waiting for memory to normalize..."
sleep 30

# TEST 6: Redis Failure
echo "🧪 TEST 6: Redis Failure"
echo "========================"
echo "🔥 Stopping Redis..."
docker stop vybe_redis
echo ""
echo "⏱  Expected within 90s:"
echo "  - Alert: RedisDown"
echo "  - Possible latency increase"
echo "  - Cache hit rate drops"
echo ""
echo "🔍 Debug commands:"
echo "  docker logs vybe_app1 --tail 50"
echo ""
wait_and_prompt "TEST 6: Redis Failure" 90
restore_service "vybe_redis"

# Final Report
echo ""
echo "📊 FINAL RESULTS"
echo "================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo ""
    
    if [ $SUCCESS_RATE -ge 90 ]; then
        echo -e "${GREEN}🎯 VERDICT: Production-ready incident response (≥90%)${NC}"
    elif [ $SUCCESS_RATE -ge 75 ]; then
        echo -e "${YELLOW}⚠️  VERDICT: Needs improvement (75-89%)${NC}"
    else
        echo -e "${RED}❌ VERDICT: Not production-ready (<75%)${NC}"
    fi
fi

echo ""
echo "✅ Test suite completed!"
