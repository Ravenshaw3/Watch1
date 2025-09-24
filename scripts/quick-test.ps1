Write-Host "Testing Development Scripts" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Checking if scripts exist..." -ForegroundColor Yellow
$scripts = @("dev-start-simple.ps1", "dev-health-simple.ps1", "dev-stop-simple.ps1", "dev-reset-simple.ps1")
foreach ($script in $scripts) {
    if (Test-Path ".\scripts\$script") {
        Write-Host "  [OK] $script exists" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $script missing" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "2. Checking Docker status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "  [OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Docker not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Checking containers..." -ForegroundColor Yellow
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "watch1-"
if ($containers) {
    Write-Host "  [OK] Watch1 containers found:" -ForegroundColor Green
    $containers | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  [INFO] No Watch1 containers running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test complete. You can now run individual scripts." -ForegroundColor Cyan
