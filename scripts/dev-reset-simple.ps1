#!/usr/bin/env pwsh
# Watch1 v3.0.1 - Simple Development Environment Reset Script

param(
    [switch]$Force,
    [switch]$KeepData
)

Write-Host "=" * 60 -ForegroundColor Red
Write-Host "Watch1 v3.0.1 - Development Environment Reset" -ForegroundColor Red
Write-Host "=" * 60 -ForegroundColor Red
Write-Host ""

if (-not $Force) {
    Write-Host "WARNING: This will stop all containers and remove them!" -ForegroundColor Yellow
    Write-Host "This will also remove:"
    Write-Host "• All container data (unless -KeepData is used)"
    Write-Host "• Docker networks"
    Write-Host "• Docker images (optional)"
    Write-Host ""
    $confirm = Read-Host "Are you sure? Type 'yes' to continue"
    if ($confirm -ne "yes") {
        Write-Host "Reset cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "[INFO] Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker is not running." -ForegroundColor Red
    exit 1
}

# Stop and remove containers
Write-Host "[INFO] Stopping and removing containers..." -ForegroundColor Cyan
if ($KeepData) {
    docker-compose -f docker-compose.dev.yml down
    Write-Host "[INFO] Containers stopped (data preserved)" -ForegroundColor Green
} else {
    docker-compose -f docker-compose.dev.yml down -v
    Write-Host "[INFO] Containers and volumes removed" -ForegroundColor Green
}

# Remove images (optional)
Write-Host ""
$removeImages = Read-Host "Remove Docker images as well? (y/N)"
if ($removeImages -eq "y" -or $removeImages -eq "Y") {
    Write-Host "[INFO] Removing Docker images..." -ForegroundColor Cyan
    docker rmi watch1-backend watch1-frontend 2>$null
    Write-Host "[INFO] Images removed" -ForegroundColor Green
}

# Clean up dangling resources
Write-Host "[INFO] Cleaning up dangling resources..." -ForegroundColor Cyan
docker system prune -f | Out-Null

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Development Environment Reset Complete" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Use '.\scripts\dev-start-simple.ps1' to start fresh" -ForegroundColor Cyan
