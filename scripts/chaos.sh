#!/usr/bin/env bash
# Vybe Resilience & Failure Simulation

set -euo pipefail

COMPONENT="${1:-app1}"
BASE_URL="http://localhost"
CONTAINER_NAME="vybe_${COMPONENT}"

echo "----------------------------------------------------"
echo "Resilience Testing: Targeting ${COMPONENT}"
echo "----------------------------------------------------"

case $COMPONENT in
  "garbage")
    echo "⚠️  Requirement: Graceful Failure (Gold Tier)"
    echo "📤 Sending invalid JSON to /urls..."
    RESPONSE=$(curl -s -X POST "${BASE_URL}/urls" \
      -H "Content-Type: application/json" \
      -d '{"this_is": "broken", "missing": "fields"}')
    
    echo "Response: ${RESPONSE}"
    if echo "$RESPONSE" | grep -q "error"; then
      echo "✅ SUCCESS: App returned a clean JSON error."
    else
      echo "❌ FAILURE: App did not return a structured error."
    fi
    exit 0
    ;;
  
  "app1"|"app2"|"db"|"redis")
    echo "Action: Terminating container ${CONTAINER_NAME}..."
    docker kill "${CONTAINER_NAME}"
    
    echo "Status: Awaiting Nginx propagation (5s)..."
    sleep 5
    
    echo "Action: Executing health check..."
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health")
    
    if [ "$COMPONENT" == "app1" ] || [ "$COMPONENT" == "app2" ]; then
      if [ "$HEALTH" == "200" ]; then
        echo "SUCCESS: High availability operational, system remains online."
      else
        echo "WARNING: System returned HTTP ${HEALTH}. Load balancer health check failure."
      fi
    else
      echo "Note: Degradation expected (HTTP ${HEALTH}) during ${COMPONENT} downtime."
    fi
    
    echo ""
    echo "Action: Restarting container ${CONTAINER_NAME}..."
    docker start "${CONTAINER_NAME}"
    
    echo "Status: Monitoring recovery..."
    for i in {1..10}; do
      RAW_STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null || echo "\"unknown\"")
      STATUS=$(echo "$RAW_STATUS" | tr -d '"')
      
      echo "  [$(date +%T)] Attempt $i: ${CONTAINER_NAME} is ${STATUS}"
      
      if [[ "${STATUS}" == "healthy" ]]; then
        echo "SUCCESS: Container ${COMPONENT} has recovered and is healthy."
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
echo "Final System Check:"
curl -sf "${BASE_URL}/health" && echo "System is fully operational." || echo "CRITICAL: System remains unstable."

