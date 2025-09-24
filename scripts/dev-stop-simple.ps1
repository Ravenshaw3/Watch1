#!/usr/bin/env pwsh
# Watch1 v3.0.1 - Simple Development Environment Stop Script

Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "Watch1 v3.0.1 - Stopping Development Environment" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "[INFO] Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker is not running. Nothing to stop." -ForegroundColor Red
    exit 0
}

# Stop all containers
Write-Host "[INFO] Stopping all containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml down

# Verify containers are stopped
Write-Host "[INFO] Verifying containers are stopped..." -ForegroundColor Cyan
$runningContainers = docker ps --filter "name=watch1-" --format "table {{.Names}}\t{{.Status}}"

if ($runningContainers -match "watch1-") {
    Write-Host "[WARNING] Some containers are still running:" -ForegroundColor Yellow
    Write-Host $runningContainers
} else {
    Write-Host "[SUCCESS] All containers stopped successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Development Environment Stopped" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Use '.\scripts\dev-start-simple.ps1' to restart the environment" -ForegroundColor Cyan
