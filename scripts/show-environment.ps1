#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Show Current Watch1 Environment Configuration
.DESCRIPTION
    Displays the current environment settings and media mount configuration
.EXAMPLE
    .\scripts\show-environment.ps1
#>

Write-Host "WATCH1 ENVIRONMENT STATUS" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "`nREADING CURRENT CONFIGURATION..." -ForegroundColor Yellow
    
    # Parse .env file
    $envVars = @{}
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $envVars[$matches[1]] = $matches[2]
        }
    }
    
    # Display environment type
    $envType = $envVars["ENV_TYPE"]
    if ($envType -eq "local") {
        Write-Host "`nCURRENT ENVIRONMENT: LOCAL DEVELOPMENT" -ForegroundColor Cyan
        Write-Host "Configuration Source: .env.local" -ForegroundColor White
    } elseif ($envType -eq "unraid") {
        Write-Host "`nCURRENT ENVIRONMENT: UNRAID PRODUCTION" -ForegroundColor Cyan
        Write-Host "Configuration Source: .env.unraid" -ForegroundColor White
    } else {
        Write-Host "`nCURRENT ENVIRONMENT: UNKNOWN" -ForegroundColor Yellow
        Write-Host "Configuration Source: .env (custom)" -ForegroundColor White
    }
    
    # Display key configuration
    Write-Host "`nCONFIGURATION DETAILS:" -ForegroundColor Yellow
    Write-Host "Media Source: $($envVars['MEDIA_SOURCE'])" -ForegroundColor White
    Write-Host "Media Target: $($envVars['MEDIA_TARGET'])" -ForegroundColor White
    Write-Host "Media Mode: $($envVars['MEDIA_MODE'])" -ForegroundColor White
    Write-Host "Flask Environment: $($envVars['FLASK_ENV'])" -ForegroundColor White
    Write-Host "Debug Mode: $($envVars['FLASK_DEBUG'])" -ForegroundColor White
    Write-Host "Description: $($envVars['MEDIA_DESCRIPTION'])" -ForegroundColor White
    
} else {
    Write-Host "`nNO ENVIRONMENT CONFIGURATION FOUND" -ForegroundColor Red
    Write-Host "Using Docker Compose defaults" -ForegroundColor Yellow
}

# Check Docker container status
Write-Host "`nDOCKER CONTAINER STATUS:" -ForegroundColor Yellow
try {
    $containers = docker-compose -f docker-compose.dev.yml ps --format json 2>$null | ConvertFrom-Json
    if ($containers) {
        foreach ($container in $containers) {
            $status = if ($container.State -eq "running") { "RUNNING" } else { "STOPPED" }
            $color = if ($container.State -eq "running") { "Green" } else { "Red" }
            Write-Host "  $($container.Service): $status" -ForegroundColor $color
        }
    } else {
        Write-Host "  No containers running" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not check container status" -ForegroundColor Yellow
}

# Check media accessibility
Write-Host "`nMEDIA ACCESSIBILITY:" -ForegroundColor Yellow

# Check local media
if (Test-Path "media") {
    $localCount = (Get-ChildItem "media" -Directory | Measure-Object).Count
    Write-Host "  Local Media: $localCount directories available" -ForegroundColor Green
} else {
    Write-Host "  Local Media: Not available" -ForegroundColor Red
}

# Check T: drive
if (Test-Path "T:\") {
    try {
        $tDriveCount = (Get-ChildItem "T:\" -Directory -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "  T: Drive: $tDriveCount directories available" -ForegroundColor Green
        
        # Check for media directories
        $mediaDirs = @("Movies", "TV Shows", "Music", "Kids")
        $foundMedia = @()
        foreach ($dir in $mediaDirs) {
            if (Test-Path "T:\$dir") {
                $foundMedia += $dir
            }
        }
        if ($foundMedia.Count -gt 0) {
            Write-Host "  T: Media Dirs: $($foundMedia -join ', ')" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "  T: Drive: Access error" -ForegroundColor Yellow
    }
} else {
    Write-Host "  T: Drive: Not accessible" -ForegroundColor Red
}

# Show available commands
Write-Host "`nAVAILABLE COMMANDS:" -ForegroundColor Yellow
Write-Host "  Switch to Local: .\scripts\switch-to-local.ps1 -Restart" -ForegroundColor White
Write-Host "  Switch to Unraid: .\scripts\switch-to-unraid.ps1 -Restart" -ForegroundColor White
Write-Host "  Test System: python tools\enhanced-storage-test-suite.py" -ForegroundColor White
Write-Host "  Scan T: Drive: python tools\direct-t-drive-scanner.py" -ForegroundColor White

# Show service URLs
Write-Host "`nSERVICE URLS:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  Health Check: http://localhost:8000/api/v1/health" -ForegroundColor White

Write-Host "`nENVIRONMENT STATUS COMPLETE" -ForegroundColor Green
