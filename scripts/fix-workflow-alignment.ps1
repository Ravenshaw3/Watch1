param(
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'

Write-Host "Watch1 Workflow Alignment Analysis" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$issues = @()

# Check for broken imports
$backendFile = "backend\flask_simple.py"
if (Test-Path $backendFile) {
    $content = Get-Content $backendFile -Raw
    if ($content -match "from routes import") {
        $issues += [PSCustomObject]@{
            Type = "BrokenImport"
            File = $backendFile
            Issue = "Imports from archived 'routes' module"
            Fix = "Remove or update import statement"
        }
    }
}

# Check for missing tools referenced in Makefile
$missingTools = @(
    'scripts\dev-test.ps1',
    'tools\api-tester.py', 
    'tools\seed-database.py',
    'tools\health-monitor.py'
)

foreach ($tool in $missingTools) {
    if (-not (Test-Path $tool)) {
        $issues += [PSCustomObject]@{
            Type = "MissingTool"
            File = $tool
            Issue = "Referenced in Makefile but doesn't exist"
            Fix = "Create missing tool or update Makefile"
        }
    }
}

# Check for architecture inconsistencies
if ((Test-Path "backend\app") -and (Get-Content "backend\flask_simple.py" -Raw).Length -gt 50000) {
    $issues += [PSCustomObject]@{
        Type = "ArchitectureInconsistency"
        File = "backend\"
        Issue = "Both monolithic flask_simple.py (57KB) and structured app/ exist"
        Fix = "Choose one architecture pattern"
    }
}

if (-not $issues) {
    Write-Host "No workflow alignment issues found!" -ForegroundColor Green
    return
}

Write-Host "`nFound $($issues.Count) workflow alignment issues:" -ForegroundColor Yellow

$issues | Group-Object Type | ForEach-Object {
    Write-Host "`n$($_.Name) Issues:" -ForegroundColor Red
    $_.Group | ForEach-Object {
        Write-Host "  File: $($_.File)" -ForegroundColor Gray
        Write-Host "  Issue: $($_.Issue)" -ForegroundColor Gray
        Write-Host "  Fix: $($_.Fix)" -ForegroundColor Yellow
        Write-Host ""
    }
}

if (-not $Execute) {
    Write-Host "Use -Execute to apply automatic fixes where possible" -ForegroundColor Cyan
    return
}

Write-Host "Applying fixes..." -ForegroundColor Green

# Fix broken imports
foreach ($issue in $issues | Where-Object { $_.Type -eq "BrokenImport" }) {
    if ($issue.File -eq "backend\flask_simple.py") {
        $content = Get-Content $issue.File -Raw
        $content = $content -replace "from routes import register_blueprints", "# from routes import register_blueprints  # Archived"
        $content = $content -replace "register_blueprints\(app\)", "# register_blueprints(app)  # Archived"
        Set-Content -Path $issue.File -Value $content -NoNewline
        Write-Host "Fixed broken import in $($issue.File)" -ForegroundColor Green
    }
}

# Create missing development tools
$toolsDir = "tools"
if (-not (Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir | Out-Null
}

# Create basic health monitor
$healthMonitor = @"
#!/usr/bin/env python3
"""Basic health monitor for Watch1 development"""
import sys
import requests
import argparse

def check_health():
    services = {
        'Backend': 'http://localhost:8000/health',
        'Frontend': 'http://localhost:3000'
    }
    
    all_healthy = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: Unhealthy (HTTP {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: Unreachable ({e})")
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--continuous', action='store_true')
    args = parser.parse_args()
    
    if args.continuous:
        import time
        while True:
            check_health()
            time.sleep(30)
    else:
        healthy = check_health()
        sys.exit(0 if healthy else 1)
"@

Set-Content -Path "tools\health-monitor.py" -Value $healthMonitor
Write-Host "Created tools\health-monitor.py" -ForegroundColor Green

# Create basic API tester
$apiTester = @"
#!/usr/bin/env python3
"""Basic API tester for Watch1"""
import requests
import sys

def test_api():
    base_url = 'http://localhost:8000/api/v1'
    
    tests = [
        ('Health Check', f'{base_url}/health', 'GET'),
        ('Media List', f'{base_url}/media', 'GET'),
    ]
    
    passed = 0
    for name, url, method in tests:
        try:
            response = requests.request(method, url, timeout=10)
            if response.status_code < 400:
                print(f"✅ {name}: PASS")
                passed += 1
            else:
                print(f"❌ {name}: FAIL (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: ERROR ({e})")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
"@

Set-Content -Path "tools\api-tester.py" -Value $apiTester
Write-Host "Created tools\api-tester.py" -ForegroundColor Green

# Create missing dev-test script
$devTest = @"
param()

Write-Host "Running Watch1 Development Tests" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Run health check
Write-Host "`nHealth Check:" -ForegroundColor Yellow
python tools\health-monitor.py

# Run API tests  
Write-Host "`nAPI Tests:" -ForegroundColor Yellow
python tools\api-tester.py

Write-Host "`nDevelopment tests complete!" -ForegroundColor Green
"@

Set-Content -Path "scripts\dev-test.ps1" -Value $devTest
Write-Host "Created scripts\dev-test.ps1" -ForegroundColor Green

Write-Host "`nWorkflow alignment fixes applied!" -ForegroundColor Green
Write-Host "Backend should now start without import errors." -ForegroundColor Cyan
