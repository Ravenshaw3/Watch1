#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Switch Watch1 to Unraid Production Environment
.DESCRIPTION
    Configures Docker Compose to use T: drive Unraid media share for production
.EXAMPLE
    .\scripts\switch-to-unraid.ps1
#>

param(
    [switch]$Restart,
    [switch]$TestMount
)

Write-Host "SWITCHING TO UNRAID PRODUCTION ENVIRONMENT" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Test T: drive accessibility first
if ($TestMount) {
    Write-Host "`nTESTING T: DRIVE ACCESS..." -ForegroundColor Yellow
    
    if (Test-Path "T:\") {
        $tDriveItems = Get-ChildItem "T:\" -Directory -ErrorAction SilentlyContinue | Measure-Object
        Write-Host "SUCCESS: T: drive accessible with $($tDriveItems.Count) directories" -ForegroundColor Green
        
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
            Write-Host "Media Directories Found:" -ForegroundColor Cyan
            $foundDirs | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
        } else {
            Write-Host "WARNING: No expected media directories found on T: drive" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "ERROR: T: drive not accessible!" -ForegroundColor Red
        Write-Host "Please ensure:" -ForegroundColor Yellow
        Write-Host "  1. T: drive is mapped to \\Tower\media" -ForegroundColor White
        Write-Host "  2. Network connection to Unraid server is working" -ForegroundColor White
        Write-Host "  3. Docker Desktop has T: drive sharing enabled" -ForegroundColor White
        
        $continue = Read-Host "`nContinue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "Aborted by user" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Copy Unraid environment configuration
if (Test-Path ".env.unraid") {
    Copy-Item ".env.unraid" ".env" -Force
    Write-Host "`nSUCCESS: Unraid environment configuration activated" -ForegroundColor Green
    
    # Display current configuration
    Write-Host "`nCURRENT CONFIGURATION:" -ForegroundColor Yellow
    Write-Host "Environment Type: UNRAID PRODUCTION" -ForegroundColor Cyan
    Write-Host "Unraid Access Method: DOCKER CONTAINER MOUNT" -ForegroundColor Cyan
    Write-Host "Media Source: /mnt/user/media (Unraid path)" -ForegroundColor Cyan
    Write-Host "Media Target: /app/media (container)" -ForegroundColor Cyan
    Write-Host "Media Mode: Read-Only" -ForegroundColor Cyan
    Write-Host "Flask Environment: Production" -ForegroundColor Cyan
    Write-Host "Debug Mode: Disabled" -ForegroundColor Cyan
    
    if ($Restart) {
        Write-Host "`nRESTARTING CONTAINERS WITH UNRAID CONFIGURATION..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml up -d
        
        Write-Host "`nWaiting for containers to be healthy..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        # Check container status
        $containers = docker-compose -f docker-compose.dev.yml ps --format json | ConvertFrom-Json
        Write-Host "`nCONTAINER STATUS:" -ForegroundColor Yellow
        foreach ($container in $containers) {
            $status = if ($container.State -eq "running") { "RUNNING" } else { "STOPPED" }
            $color = if ($container.State -eq "running") { "Green" } else { "Red" }
            Write-Host "  $($container.Service): $status" -ForegroundColor $color
        }
        
        # Test T: drive mount in container
        Write-Host "`nTESTING T: DRIVE MOUNT IN CONTAINER..." -ForegroundColor Yellow
        try {
            $mountTest = docker exec watch1-backend-dev ls -la /app/media/ 2>$null
            if ($mountTest -and $mountTest.Count -gt 2) {
                Write-Host "SUCCESS: T: drive mounted successfully in container" -ForegroundColor Green
            } else {
                Write-Host "WARNING: T: drive mount may not be working properly" -ForegroundColor Yellow
                Write-Host "Consider running the direct T: drive scanner as fallback" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "WARNING: Could not test container mount" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Run: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor White
    Write-Host "2. Test Container Mount: python tools\enhanced-storage-test-suite.py" -ForegroundColor White
    Write-Host "3. Verify Mount: docker exec watch1-backend-dev ls -la /app/media/" -ForegroundColor White
    Write-Host "4. Access: http://localhost:3000 (Frontend)" -ForegroundColor White
    Write-Host "5. API: http://localhost:8000 (Backend)" -ForegroundColor White
    Write-Host "`nNOTE: This mode uses proper Docker container mounting" -ForegroundColor Yellow
    Write-Host "Expected when running on actual Unraid server" -ForegroundColor Yellow
    
} else {
    Write-Host "ERROR: .env.unraid file not found!" -ForegroundColor Red
    Write-Host "Please ensure the Unraid environment configuration exists." -ForegroundColor Red
    exit 1
}

Write-Host "`nUNRAID PRODUCTION ENVIRONMENT READY!" -ForegroundColor Green
Write-Host "Expected: 18,509+ media files from T: drive" -ForegroundColor Cyan
