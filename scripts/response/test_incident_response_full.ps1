# Full Incident Response Test Suite (Windows PowerShell)
# Tests: 3 (DB Down), 4 (CPU Spike), 5 (Memory Pressure), 6 (Redis Failure)

$ErrorActionPreference = "Stop"

Write-Host "🧪 INCIDENT RESPONSE TEST SUITE - FULL" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test results
$TestsPassed = 0
$TestsFailed = 0

# Helper function
function Wait-AndPrompt {
    param(
        [string]$TestName,
        [int]$WaitTime
    )
    
    Write-Host "⏱  Waiting $WaitTime seconds for alerts to fire..." -ForegroundColor Yellow
    Start-Sleep -Seconds $WaitTime
    Write-Host ""
    Write-Host "Check:"
    Write-Host "  - Discord notifications"
    Write-Host "  - Grafana dashboards"
    Write-Host "  - Alert manager"
    Write-Host ""
    
    $response = Read-Host "Did the test PASS? (y/n)"
    if ($response -match "^[Yy]$") {
        Write-Host "✅ $TestName PASSED" -ForegroundColor Green
        $script:TestsPassed++
    } else {
        Write-Host "❌ $TestName FAILED" -ForegroundColor Red
        $script:TestsFailed++
    }
    Write-Host ""
}

function Restore-Service {
    param([string]$Service)
    
    Write-Host "🔄 Restoring $Service..." -ForegroundColor Cyan
    docker start $Service
    Start-Sleep -Seconds 5
}

Write-Host "📋 Prerequisites Check" -ForegroundColor Cyan
Write-Host "----------------------" -ForegroundColor Cyan
docker compose ps
Write-Host ""
$ready = Read-Host "Are all services running? (y/n)"
if ($ready -notmatch "^[Yy]$") {
    Write-Host "Please start services with: docker compose up -d" -ForegroundColor Red
    exit 1
}
Write-Host ""

# TEST 3: Database Down
Write-Host "🧪 TEST 3: Database Down (Critical)" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🔥 Stopping database..."
docker stop vybe_db
Write-Host ""
Write-Host "⏱  Expected within 90s:"
Write-Host "  - Alert: PostgresDown"
Write-Host "  - Alert: HighErrorRate"
Write-Host "  - Grafana: Errors spike, DB connections = 0"
Write-Host ""
Write-Host "🔍 Debug commands:"
Write-Host "  docker logs vybe_app1 --tail 50"
Write-Host ""
Wait-AndPrompt -TestName "TEST 3: Database Down" -WaitTime 90
Restore-Service -Service "vybe_db"
Start-Sleep -Seconds 10

# TEST 4: CPU Spike
Write-Host "🧪 TEST 4: CPU Spike" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "🔥 Creating CPU load..."
Start-Job -ScriptBlock { docker exec vybe_app1 sh -c "timeout 120 yes > /dev/null 2>&1 || true" } | Out-Null
Write-Host ""
Write-Host "⏱  Expected within <=3 min:"
Write-Host "  - Alert: HighCPUUsage"
Write-Host "  - Grafana: CPU panel spikes"
Write-Host "  - Possible latency increase"
Write-Host ""
Write-Host "🔍 Debug commands:"
Write-Host "  docker stats --no-stream"
Write-Host ""
Wait-AndPrompt -TestName "TEST 4: CPU Spike" -WaitTime 150
Write-Host "⏳ Waiting for CPU to normalize..."
Start-Sleep -Seconds 30

# TEST 5: Memory Pressure
Write-Host "🧪 TEST 5: Memory Pressure" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host "🔥 Creating memory pressure..."
Start-Job -ScriptBlock { docker exec vybe_app1 python -c "import time; b=bytearray(900*1024*1024); time.sleep(120)" 2>$null } | Out-Null
Write-Host ""
Write-Host "⏱  Expected within <=3 min:"
Write-Host "  - Alert: HighMemoryUsage"
Write-Host "  - Possible: container restart, latency increase"
Write-Host ""
Write-Host "🔍 Debug commands:"
Write-Host "  docker stats --no-stream"
Write-Host "  docker logs vybe_app1 --tail 50"
Write-Host ""
Wait-AndPrompt -TestName "TEST 5: Memory Pressure" -WaitTime 150
Write-Host "⏳ Waiting for memory to normalize..."
Start-Sleep -Seconds 30

# TEST 6: Redis Failure
Write-Host "🧪 TEST 6: Redis Failure" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "🔥 Stopping Redis..."
docker stop vybe_redis
Write-Host ""
Write-Host "⏱  Expected within 90s:"
Write-Host "  - Alert: RedisDown"
Write-Host "  - Possible latency increase"
Write-Host "  - Cache hit rate drops"
Write-Host ""
Write-Host "🔍 Debug commands:"
Write-Host "  docker logs vybe_app1 --tail 50"
Write-Host ""
Wait-AndPrompt -TestName "TEST 6: Redis Failure" -WaitTime 90
Restore-Service -Service "vybe_redis"

# Final Report
Write-Host ""
Write-Host "📊 FINAL RESULTS" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host "Tests Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $TestsFailed" -ForegroundColor Red
Write-Host ""

$TotalTests = $TestsPassed + $TestsFailed
if ($TotalTests -gt 0) {
    $SuccessRate = [math]::Round(($TestsPassed / $TotalTests) * 100)
    Write-Host "Success Rate: $SuccessRate%"
    Write-Host ""
    
    if ($SuccessRate -ge 90) {
        Write-Host "🎯 VERDICT: Production-ready incident response (≥90%)" -ForegroundColor Green
    } elseif ($SuccessRate -ge 75) {
        Write-Host "⚠️  VERDICT: Needs improvement (75-89%)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ VERDICT: Not production-ready (<75%)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Test suite completed!"

