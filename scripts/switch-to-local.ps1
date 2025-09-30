#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Switch Watch1 to Local Development Environment
.DESCRIPTION
    Configures Docker Compose to use local media directory for development and testing
.EXAMPLE
    .\scripts\switch-to-local.ps1
#>

param(
    [switch]$Restart = $false
)

Write-Host "SWITCHING TO LOCAL DEVELOPMENT ENVIRONMENT" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Copy local environment configuration
if (Test-Path ".env.local") {
    Copy-Item ".env.local" ".env" -Force
    Write-Host "SUCCESS: Local environment configuration activated" -ForegroundColor Green
    
    # Display current configuration
    Write-Host "`nCURRENT CONFIGURATION:" -ForegroundColor Yellow
    Write-Host "Environment Type: LOCAL DEVELOPMENT" -ForegroundColor Cyan
    Write-Host "Unraid Access Method: DIRECT T: DRIVE SCANNER" -ForegroundColor Cyan
    Write-Host "T: Drive Path: T:\ (bypasses Docker mount)" -ForegroundColor Cyan
    Write-Host "Container Fallback: ./media (local directory)" -ForegroundColor Cyan
    Write-Host "Flask Environment: Development" -ForegroundColor Cyan
    Write-Host "Debug Mode: Enabled" -ForegroundColor Cyan
    
    # Show local media directory status
    if (Test-Path "media") {
        $mediaItems = Get-ChildItem "media" -Directory | Measure-Object
        Write-Host "Local Media Directories: $($mediaItems.Count) found" -ForegroundColor Cyan
        
        if ($mediaItems.Count -gt 0) {
            Write-Host "Available Categories:" -ForegroundColor Yellow
            Get-ChildItem "media" -Directory | ForEach-Object {
                $fileCount = (Get-ChildItem $_.FullName -Recurse -File | Measure-Object).Count
                Write-Host "  - $($_.Name): $fileCount files" -ForegroundColor White
            }
        }
    } else {
        Write-Host "WARNING: Local media directory not found - creating..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path "media" -Force | Out-Null
        @("Movies", "TV Shows", "Music", "Kids", "Documentaries", "Music Videos") | ForEach-Object {
            New-Item -ItemType Directory -Path "media\$_" -Force | Out-Null
        }
        Write-Host "SUCCESS: Local media directories created" -ForegroundColor Green
    }
    
    if ($Restart) {
        Write-Host "`nRESTARTING CONTAINERS WITH LOCAL CONFIGURATION..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml up -d
        
        Write-Host "`nWaiting for containers to be healthy..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        # Check container status
        $containers = docker-compose -f docker-compose.dev.yml ps --format json | ConvertFrom-Json
        Write-Host "`nCONTAINER STATUS:" -ForegroundColor Yellow
        foreach ($container in $containers) {
            $status = if ($container.State -eq "running") { "RUNNING" } else { "STOPPED" }
            $color = if ($container.State -eq "running") { "Green" } else { "Red" }
            Write-Host "  $($container.Service): $status" -ForegroundColor $color
        }
    }
    
    # Check T: drive accessibility for direct scanning
    Write-Host "`nUNRAID T: DRIVE STATUS:" -ForegroundColor Yellow
    if (Test-Path "T:\") {
        $tDriveItems = Get-ChildItem "T:\" -Directory -ErrorAction SilentlyContinue | Measure-Object
        Write-Host "T: Drive Accessible: $($tDriveItems.Count) directories found" -ForegroundColor Green
        
        # Check for expected media directories
        $expectedDirs = @("Movies", "TV Shows", "Music", "Kids")
        $foundDirs = @()
        
        foreach ($dir in $expectedDirs) {
            if (Test-Path "T:\$dir") {
                $fileCount = (Get-ChildItem "T:\$dir" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
                $foundDirs += "$dir ($fileCount files)"
            }
        }
        
        if ($foundDirs.Count -gt 0) {
            Write-Host "Unraid Media Available:" -ForegroundColor Cyan
            $foundDirs | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
        }
    } else {
        Write-Host "T: Drive Not Accessible - Direct scanner will not work" -ForegroundColor Red
    }

    Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Run: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor White
    Write-Host "2. Scan Unraid: python tools\direct-t-drive-scanner.py" -ForegroundColor White
    Write-Host "3. Test System: python tools\enhanced-storage-test-suite.py" -ForegroundColor White
    Write-Host "4. Access: http://localhost:3000 (Frontend)" -ForegroundColor White
    Write-Host "5. API: http://localhost:8000 (Backend)" -ForegroundColor White
    
} else {
    Write-Host "ERROR: .env.local file not found!" -ForegroundColor Red
    Write-Host "Please ensure the local environment configuration exists." -ForegroundColor Red
    exit 1
}

Write-Host "`nLOCAL DEVELOPMENT ENVIRONMENT READY!" -ForegroundColor Green
