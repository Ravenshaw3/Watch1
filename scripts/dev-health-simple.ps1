#!/usr/bin/env pwsh
# Watch1 v3.0.1 - Simple Development Environment Health Check

Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "Watch1 v3.0.1 - Development Environment Health Check" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host ""

# Check Docker
try {
    docker version | Out-Null
    Write-Host "[✓] Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "[✗] Docker is not running" -ForegroundColor Red
    exit 1
}

# Check containers
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
Write-Host "-" * 40

$containers = @(
    @{Name="watch1-db-dev"; Service="Database"; Port="5432"},
    @{Name="watch1-redis-dev"; Service="Redis"; Port="6379"},
    @{Name="watch1-backend-dev"; Service="Backend API"; Port="8000"},
    @{Name="watch1-frontend-dev"; Service="Frontend"; Port="3000"}
)

$allHealthy = $true

foreach ($container in $containers) {
    try {
        $status = docker inspect $container.Name --format='{{.State.Status}}' 2>$null
        $health = docker inspect $container.Name --format='{{.State.Health.Status}}' 2>$null
        
        if ($status -eq "running") {
            if ($health -eq "healthy" -or $health -eq "<no value>") {
                Write-Host "[✓] $($container.Service) ($($container.Name))" -ForegroundColor Green
                Write-Host "    Status: Running, Port: $($container.Port)" -ForegroundColor Gray
            } else {
                Write-Host "[⚠] $($container.Service) ($($container.Name))" -ForegroundColor Yellow
                Write-Host "    Status: Running but unhealthy" -ForegroundColor Gray
                $allHealthy = $false
            }
        } else {
            Write-Host "[✗] $($container.Service) ($($container.Name))" -ForegroundColor Red
            Write-Host "    Status: $status" -ForegroundColor Gray
            $allHealthy = $false
        }
    }
    catch {
        Write-Host "[✗] $($container.Service) ($($container.Name))" -ForegroundColor Red
        Write-Host "    Status: Not found" -ForegroundColor Gray
        $allHealthy = $false
    }
}

# Check service endpoints
Write-Host ""
Write-Host "Service Endpoints:" -ForegroundColor Cyan
Write-Host "-" * 40

$endpoints = @(
    @{Name="Frontend"; URL="http://localhost:3000"},
    @{Name="Backend API"; URL="http://localhost:8000"},
    @{Name="Backend Health"; URL="http://localhost:8000/api/v1/users/me"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.URL -Method GET -TimeoutSec 5 -UseBasicParsing 2>$null
        Write-Host "[✓] $($endpoint.Name): $($endpoint.URL)" -ForegroundColor Green
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 422) {
            # 401/422 means the endpoint exists but requires auth - that's good
            Write-Host "[✓] $($endpoint.Name): $($endpoint.URL)" -ForegroundColor Green
        } else {
            Write-Host "[✗] $($endpoint.Name): $($endpoint.URL)" -ForegroundColor Red
            Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
            $allHealthy = $false
        }
    }
}

# Summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor $(if ($allHealthy) { "Green" } else { "Red" })
if ($allHealthy) {
    Write-Host "✓ All services are healthy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to use:" -ForegroundColor Cyan
    Write-Host "• Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "• Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "• Login:    test@example.com / testpass123" -ForegroundColor White
} else {
    Write-Host "⚠ Some services have issues!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running: .\scripts\dev-start-simple.ps1" -ForegroundColor Yellow
}
Write-Host "=" * 60 -ForegroundColor $(if ($allHealthy) { "Green" } else { "Red" })
