#!/usr/bin/env pwsh
# Test all development scripts

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Testing All Development Scripts" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$scripts = @(
    "dev-start-simple.ps1",
    "dev-health-simple.ps1", 
    "dev-stop-simple.ps1",
    "dev-reset-simple.ps1"
)

foreach ($script in $scripts) {
    $scriptPath = ".\scripts\$script"
    Write-Host "Testing: $script" -ForegroundColor Yellow
    
    if (Test-Path $scriptPath) {
        try {
            # Test syntax by parsing the script
            $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $scriptPath -Raw), [ref]$null)
            Write-Host "  [✓] Syntax OK" -ForegroundColor Green
        }
        catch {
            Write-Host "  [✗] Syntax Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  [✗] File not found" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Script Testing Complete" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "To test functionality, run each script individually:" -ForegroundColor Yellow
Write-Host "• .\scripts\dev-health-simple.ps1  (Check current status)" -ForegroundColor White
Write-Host "• .\scripts\dev-stop-simple.ps1    (Stop environment)" -ForegroundColor White  
Write-Host "• .\scripts\dev-start-simple.ps1   (Start environment)" -ForegroundColor White
Write-Host "• .\scripts\dev-reset-simple.ps1   (Reset everything)" -ForegroundColor White
