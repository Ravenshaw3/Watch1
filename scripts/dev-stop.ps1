# Watch1 v3.0.1 - Development Environment Stop Script
# Gracefully stops all development services

param(
    [switch]$Clean,      # Remove containers and volumes
    [switch]$Logs,       # Show logs before stopping
    [switch]$Force       # Force stop without confirmation
)

$ComposeFile = "docker-compose.dev.yml"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) {
        "Success" { "Green" }
        "Error" { "Red" }
        "Warning" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Magenta
    Write-Host $Title -ForegroundColor Magenta
    Write-Host "=" * 60 -ForegroundColor Magenta
    Write-Host ""
}

Write-Header "Watch1 v3.0.1 - Stopping Development Environment"

# Show logs if requested
if ($Logs) {
    Write-Log "Showing recent logs..." "Info"
    docker-compose -f $ComposeFile logs --tail=50
    Write-Host ""
}

# Confirmation for clean stop
if ($Clean -and -not $Force) {
    Write-Log "Clean stop will remove all containers and volumes!" "Warning"
    $confirmation = Read-Host "Are you sure? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Log "Operation cancelled" "Info"
        exit 0
    }
}

# Get current container status
Write-Log "Getting current container status..." "Info"
$containers = docker-compose -f $ComposeFile ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}"
Write-Host $containers

Write-Host ""

# Stop services
Write-Log "Stopping services..." "Info"

if ($Clean) {
    Write-Log "Performing clean stop (removing containers and volumes)..." "Warning"
    docker-compose -f $ComposeFile down -v --remove-orphans
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Clean stop completed successfully" "Success"
        
        # Clean up unused Docker resources
        Write-Log "Cleaning up unused Docker resources..." "Info"
        docker system prune -f
        Write-Log "Docker cleanup completed" "Success"
    } else {
        Write-Log "Clean stop failed" "Error"
        exit 1
    }
} else {
    Write-Log "Performing graceful stop..." "Info"
    docker-compose -f $ComposeFile stop
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Services stopped successfully" "Success"
        Write-Log "Containers are preserved. Use 'dev-start.ps1' to restart" "Info"
    } else {
        Write-Log "Stop operation failed" "Error"
        exit 1
    }
}

# Final status
Write-Log "Verifying all services are stopped..." "Info"
$runningContainers = docker-compose -f $ComposeFile ps -q
if ($runningContainers) {
    Write-Log "Some containers are still running" "Warning"
    docker-compose -f $ComposeFile ps
} else {
    Write-Log "All services stopped successfully" "Success"
}

Write-Header "Development Environment Stopped"
Write-Log "Use '.\scripts\dev-start.ps1' to restart the environment" "Info"
