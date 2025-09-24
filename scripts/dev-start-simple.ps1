#!/usr/bin/env pwsh
# Watch1 v3.0.1 - Simple Development Environment Startup Script

Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "Watch1 v3.0.1 - Starting Development Environment" -ForegroundColor Magenta  
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "[INFO] Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "[INFO] Stopping existing containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml down

# Start the development environment
Write-Host "[INFO] Starting development environment..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml up -d

# Wait a moment for containers to start
Start-Sleep -Seconds 5

# Check container status
Write-Host "[INFO] Checking container status..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml ps

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Development Environment Started Successfully!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Services available at:" -ForegroundColor Cyan
Write-Host "• Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "• Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "• Database: localhost:5432" -ForegroundColor White
Write-Host "• Redis:    localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Cyan
Write-Host "• Email:    test@example.com" -ForegroundColor White
Write-Host "• Password: testpass123" -ForegroundColor White
Write-Host ""
Write-Host "Use '.\scripts\dev-stop.ps1' to stop the environment" -ForegroundColor Yellow
