# Test script to verify PowerShell scripts work correctly
# Run this to test the fixed scripts before using them

Write-Host "Testing Watch1 PowerShell Scripts..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Test 1: Check if we can navigate to project root
Write-Host "`n1. Testing directory navigation..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.PSCommandPath
$projectRoot = Split-Path -Parent $scriptDir
Write-Host "Script directory: $scriptDir" -ForegroundColor Gray
Write-Host "Project root: $projectRoot" -ForegroundColor Gray

if (Test-Path "$projectRoot\docker-compose.dev.yml") {
    Write-Host "✓ Found docker-compose.dev.yml" -ForegroundColor Green
} else {
    Write-Host "✗ docker-compose.dev.yml not found" -ForegroundColor Red
}

# Test 2: Check Docker availability
Write-Host "`n2. Testing Docker availability..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✓ Docker is available: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker not found or not running" -ForegroundColor Red
    }
}
catch {
    Write-Host "✗ Docker test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check Docker Compose availability
Write-Host "`n3. Testing Docker Compose availability..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Host "✓ Docker Compose is available: $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker Compose not found" -ForegroundColor Red
    }
}
catch {
    Write-Host "✗ Docker Compose test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Test PowerShell functions
Write-Host "`n4. Testing PowerShell functions..." -ForegroundColor Yellow

# Test color function
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Test-WriteLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = if ($Colors.ContainsKey($Level)) { $Colors[$Level] } else { "White" }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

try {
    Test-WriteLog "Testing log function" "Info"
    Test-WriteLog "Testing success message" "Success"
    Test-WriteLog "Testing warning message" "Warning"
    Test-WriteLog "Testing error message" "Error"
    Write-Host "✓ PowerShell functions work correctly" -ForegroundColor Green
}
catch {
    Write-Host "✗ PowerShell function test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Check if scripts exist
Write-Host "`n5. Checking script files..." -ForegroundColor Yellow
$scripts = @("dev-start.ps1", "dev-stop.ps1", "dev-health.ps1", "dev-reset.ps1")

foreach ($script in $scripts) {
    $scriptPath = Join-Path $scriptDir $script
    if (Test-Path $scriptPath) {
        Write-Host "✓ Found $script" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing $script" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Script Test Complete!" -ForegroundColor Cyan
Write-Host "`nIf all tests passed, you can now run:" -ForegroundColor Yellow
Write-Host "  .\scripts\dev-start.ps1" -ForegroundColor White
Write-Host "`nIf tests failed, check:" -ForegroundColor Yellow
Write-Host "  - Docker Desktop is running" -ForegroundColor White
Write-Host "  - PowerShell execution policy allows scripts" -ForegroundColor White
Write-Host "  - You're in the correct directory" -ForegroundColor White
