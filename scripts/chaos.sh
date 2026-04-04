#!/usr/bin/env bash
# 🧪 chaos.sh – Vybe Resilience & Failure Simulation
#
# This script simulates various failure modes to verify Gold Tier Reliability.
# Usage: 
#   ./scripts/chaos.sh app1      (Kill node 1)
#   ./scripts/chaos.sh app2      (Kill node 2)
#   ./scripts/chaos.sh db        (Kill Database)
#   ./scripts/chaos.sh garbage   (Send invalid payload)

set -euo pipefail

COMPONENT="${1:-app1}"
BASE_URL="http://localhost"
CONTAINER_NAME="vybe_${COMPONENT}"

echo "----------------------------------------------------"
echo "🔥 Vybe Chaos Engineering: Targeting ${COMPONENT}"
echo "----------------------------------------------------"

case $COMPONENT in
  "garbage")
    echo "⚠️  Requirement: Graceful Failure (Gold Tier)"
    echo "📤 Sending invalid JSON to /urls..."
    RESPONSE=$(curl -s -X POST "${BASE_URL}/urls" \
      -H "Content-Type: application/json" \
      -d '{"this_is": "broken", "missing": "fields"}')
    
    echo "📥 Response: ${RESPONSE}"
    if echo "$RESPONSE" | grep -q "error"; then
      echo "✅ SUCCESS: App returned a clean JSON error."
    else
      echo "❌ FAILURE: App did not return a structured error."
    fi
    exit 0
    ;;
  
  "app1"|"app2"|"db"|"redis")
    echo "🔪 Killing container: ${CONTAINER_NAME}..."
    docker kill "${CONTAINER_NAME}"
    
    echo "⏳ Waiting 5 seconds for Nginx to detect failure..."
    sleep 5
    
    echo "📊 Performing Pulse Check (Health Check)..."
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health")
    
    if [ "$COMPONENT" == "app1" ] || [ "$COMPONENT" == "app2" ]; then
      if [ "$HEALTH" == "200" ]; then
        echo "✅ SUCCESS: System is still online (High Availability worked!)"
      else
        echo "⚠️  WARNING: System returned HTTP ${HEALTH}. Load balancer may be struggling."
      fi
    else
      echo "ℹ️  Expected: System should be down (HTTP ${HEALTH}) or degraded when DB/Redis is killed."
    fi
    
    echo ""
    echo "🔄 Restarting container: ${CONTAINER_NAME}..."
    docker start "${CONTAINER_NAME}"
    
    echo "⏳ Waiting for recovery..."
    for i in {1..10}; do
      # Use docker inspect to check health status
      RAW_STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null || echo "\"unknown\"")
      STATUS=$(echo "$RAW_STATUS" | tr -d '"')
      
      echo "  [$(date +%T)] Attempt $i: ${CONTAINER_NAME} is ${STATUS}"
      
      if [[ "${STATUS}" == "healthy" ]]; then
        echo "✅ RECOVERY SUCCESS: ${COMPONENT} is back in the fleet."
        break
      fi
      sleep 3
    done
    ;;
    
  *)
    echo "Usage: $0 [app1|app2|db|redis|garbage]"
    exit 1
    ;;
esac

echo ""
echo "📊 Final System Check:"
curl -sf "${BASE_URL}/health" && echo " ✅ Vybe is fully operational." || echo " ❌ System is still unstable."
