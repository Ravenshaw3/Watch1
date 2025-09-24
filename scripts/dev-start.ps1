# Watch1 v3.0.1 - Professional Development Environment Startup
# This script provides a robust, one-command development environment

param(
    [switch]$Clean,      # Clean rebuild all containers
    [switch]$Logs,       # Show logs after startup
    [switch]$Monitor,    # Start with health monitoring
    [switch]$Tools       # Include development tools
)

# Configuration
$ProjectName = "Watch1"
$Version = "v3.0.1"
$ComposeFile = "docker-compose.dev.yml"
$HealthCheckTimeout = 120
$LogLevel = "INFO"

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = if ($Colors.ContainsKey($Level)) { $Colors[$Level] } else { "White" }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host $Title -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-ServiceHealth {
    param([string]$ServiceName)
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $psOutput = docker-compose -f $ComposeFile ps --format json 2>$null
            if ($psOutput) {
                $containers = $psOutput | ConvertFrom-Json
                $health = $containers | Where-Object { $_.Service -eq $ServiceName }
                
                if ($health -and ($health.Health -eq "healthy" -or $health.State -eq "running")) {
                    return $true
                }
            }
        }
        catch {
            # Continue trying
        }
        
        Start-Sleep -Seconds 2
        $attempt++
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
    
    return $false
}

function Start-DevelopmentEnvironment {
    Write-Header "$ProjectName $Version - Development Environment Startup"
    
    # Ensure we're in the right directory
    $scriptDir = Split-Path -Parent $MyInvocation.PSCommandPath
    $projectRoot = Split-Path -Parent $scriptDir
    Set-Location $projectRoot
    
    # Check prerequisites
    Write-Log "Checking prerequisites..." "Info"
    Write-Log "Working directory: $(Get-Location)" "Info"
    
    if (-not (Test-DockerRunning)) {
        Write-Log "Docker is not running. Please start Docker Desktop." "Error"
        exit 1
    }
    
    if (-not (Test-Path $ComposeFile)) {
        Write-Log "Docker Compose file not found: $ComposeFile" "Error"
        Write-Log "Current directory: $(Get-Location)" "Error"
        Write-Log "Looking for: $((Get-Location).Path)\$ComposeFile" "Error"
        exit 1
    }
    
    Write-Log "Prerequisites check passed" "Success"
    
    # Clean environment if requested
    if ($Clean) {
        Write-Log "Cleaning existing environment..." "Warning"
        docker-compose -f $ComposeFile down -v --remove-orphans
        docker system prune -f
        Write-Log "Environment cleaned" "Success"
    }
    
    # Build and start services
    Write-Log "Building and starting services..." "Info"
    
    try {
        if ($Tools) {
            Write-Log "Starting services with development tools..." "Info"
            docker-compose -f $ComposeFile --profile tools up -d --build
        } else {
            Write-Log "Starting core services..." "Info"
            docker-compose -f $ComposeFile up -d --build
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to start services (exit code: $LASTEXITCODE)" "Error"
            exit 1
        }
        
        Write-Log "Services started successfully" "Success"
    }
    catch {
        Write-Log "Failed to start services: $($_.Exception.Message)" "Error"
        exit 1
    }
    
    # Health checks
    Write-Log "Performing health checks..." "Info"
    
    $services = @("database", "redis", "backend", "frontend")
    $healthyServices = @()
    
    foreach ($service in $services) {
        Write-Host "Checking $service health" -NoNewline -ForegroundColor Cyan
        
        if (Test-ServiceHealth $service) {
            Write-Host " ✓" -ForegroundColor Green
            $healthyServices += $service
        } else {
            Write-Host " ✗" -ForegroundColor Red
            Write-Log "$service failed health check" "Warning"
        }
    }
    
    # Service status report
    Write-Header "Service Status Report"
    
    try {
        $containerStatus = docker-compose -f $ComposeFile ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}" 2>$null
        if ($containerStatus) {
            Write-Host $containerStatus
        } else {
            Write-Log "Unable to get container status" "Warning"
        }
    }
    catch {
        Write-Log "Error getting container status: $($_.Exception.Message)" "Warning"
    }
    
    # Access information
    Write-Header "Access Information"
    Write-Log "Frontend (Development): http://localhost:3000" "Info"
    Write-Log "Backend API: http://localhost:8000/api/v1" "Info"
    Write-Log "Nginx Proxy: http://localhost" "Info"
    Write-Log "Database: localhost:5432 (watch1_dev/watch1_user)" "Info"
    Write-Log "Redis: localhost:6379" "Info"
    
    # Quick API test
    Write-Log "Testing API connectivity..." "Info"
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/version" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Log "API is responding correctly" "Success"
        }
    }
    catch {
        Write-Log "API test failed - may still be starting up" "Warning"
    }
    
    # Development tips
    Write-Header "Development Tips"
    Write-Log "• Use 'docker-compose -f $ComposeFile logs -f [service]' to view logs" "Info"
    Write-Log "• Use '.\scripts\dev-stop.ps1' to stop the environment" "Info"
    Write-Log "• Use '.\scripts\dev-health.ps1' for health monitoring" "Info"
    Write-Log "• Use '.\scripts\dev-reset.ps1' to reset everything" "Info"
    
    # Show logs if requested
    if ($Logs) {
        Write-Log "Showing service logs (Ctrl+C to exit)..." "Info"
        docker-compose -f $ComposeFile logs -f
    }
    
    # Start monitoring if requested
    if ($Monitor) {
        Write-Log "Starting health monitoring..." "Info"
        & ".\scripts\dev-health.ps1" -Continuous
    }
    
    Write-Log "Development environment is ready!" "Success"
}

# Main execution
try {
    Start-DevelopmentEnvironment
}
catch {
    Write-Log "Startup failed: $($_.Exception.Message)" "Error"
    exit 1
}
