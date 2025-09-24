# Watch1 v3.0.1 - Development Environment Health Monitor
# Comprehensive health checking and diagnostics

param(
    [switch]$Continuous,    # Continuous monitoring mode
    [switch]$Detailed,      # Show detailed information
    [switch]$Fix,          # Attempt to fix issues automatically
    [int]$Interval = 30     # Monitoring interval in seconds
)

$ComposeFile = "docker-compose.dev.yml"

# Colors
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
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
}

function Test-ContainerHealth {
    param([string]$ServiceName)
    
    try {
        $container = docker-compose -f $ComposeFile ps --format json | ConvertFrom-Json | Where-Object { $_.Service -eq $ServiceName }
        
        if (-not $container) {
            return @{ Status = "Not Found"; Health = "Unknown"; Uptime = "N/A" }
        }
        
        $health = if ($container.Health) { $container.Health } else { "No Health Check" }
        $status = $container.State
        
        # Get uptime
        $inspect = docker inspect $container.Name | ConvertFrom-Json
        $startTime = [DateTime]::Parse($inspect[0].State.StartedAt)
        $uptime = (Get-Date) - $startTime
        $uptimeStr = "{0:dd}d {0:hh}h {0:mm}m" -f $uptime
        
        return @{
            Status = $status
            Health = $health
            Uptime = $uptimeStr
            Container = $container.Name
        }
    }
    catch {
        return @{ Status = "Error"; Health = "Unknown"; Uptime = "N/A"; Error = $_.Exception.Message }
    }
}

function Test-EndpointHealth {
    param([string]$Url, [string]$Name, [int]$TimeoutSec = 5)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSec -UseBasicParsing
        $responseTime = (Measure-Command { Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSec -UseBasicParsing }).TotalMilliseconds
        
        return @{
            Name = $Name
            Status = "Healthy"
            StatusCode = $response.StatusCode
            ResponseTime = [math]::Round($responseTime, 2)
            Url = $Url
        }
    }
    catch {
        return @{
            Name = $Name
            Status = "Unhealthy"
            StatusCode = "N/A"
            ResponseTime = "N/A"
            Url = $Url
            Error = $_.Exception.Message
        }
    }
}

function Get-SystemResources {
    try {
        $cpu = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1
        $memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $disk = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        
        $cpuUsage = [math]::Round(100 - $cpu.CounterSamples[0].CookedValue, 2)
        $memoryUsage = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
        $diskUsage = [math]::Round((($disk[0].Size - $disk[0].FreeSpace) / $disk[0].Size) * 100, 2)
        
        return @{
            CPU = "$cpuUsage%"
            Memory = "$memoryUsage%"
            Disk = "$diskUsage%"
        }
    }
    catch {
        return @{
            CPU = "N/A"
            Memory = "N/A"
            Disk = "N/A"
        }
    }
}

function Get-DockerStats {
    try {
        $stats = docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
        return $stats
    }
    catch {
        return "Unable to get Docker stats"
    }
}

function Test-DatabaseConnection {
    try {
        $result = docker-compose -f $ComposeFile exec -T database pg_isready -U watch1_user -d watch1_dev
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Test-RedisConnection {
    try {
        $result = docker-compose -f $ComposeFile exec -T redis redis-cli ping
        return $result -eq "PONG"
    }
    catch {
        return $false
    }
}

function Repair-Service {
    param([string]$ServiceName)
    
    Write-Log "Attempting to repair $ServiceName..." "Warning"
    
    try {
        # Restart the service
        docker-compose -f $ComposeFile restart $ServiceName
        
        # Wait for it to come back up
        Start-Sleep -Seconds 10
        
        $health = Test-ContainerHealth $ServiceName
        if ($health.Status -eq "running") {
            Write-Log "$ServiceName repaired successfully" "Success"
            return $true
        } else {
            Write-Log "$ServiceName repair failed" "Error"
            return $false
        }
    }
    catch {
        Write-Log "Failed to repair ${ServiceName}: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Show-HealthReport {
    Clear-Host
    Write-Header "Watch1 v3.0.1 - Development Environment Health Report"
    
    # Container health
    Write-Host "🐳 Container Health:" -ForegroundColor Cyan
    $services = @("database", "redis", "backend", "frontend", "nginx")
    $healthyCount = 0
    
    foreach ($service in $services) {
        $health = Test-ContainerHealth $service
        $statusIcon = switch ($health.Status) {
            "running" { if ($health.Health -eq "healthy" -or $health.Health -eq "No Health Check") { "✅" } else { "⚠️" } }
            default { "❌" }
        }
        
        if ($health.Status -eq "running") { $healthyCount++ }
        
        Write-Host "  $statusIcon $service" -NoNewline
        Write-Host " ($($health.Status))" -ForegroundColor $(if ($health.Status -eq "running") { "Green" } else { "Red" })
        
        if ($Detailed) {
            Write-Host "    Health: $($health.Health), Uptime: $($health.Uptime)" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    
    # Endpoint health
    Write-Host "🌐 Endpoint Health:" -ForegroundColor Cyan
    $endpoints = @(
        @{ Url = "http://localhost:8000/api/v1/version"; Name = "Backend API" },
        @{ Url = "http://localhost:3000"; Name = "Frontend" },
        @{ Url = "http://localhost/health"; Name = "Nginx Proxy" }
    )
    
    $healthyEndpoints = 0
    foreach ($endpoint in $endpoints) {
        $health = Test-EndpointHealth $endpoint.Url $endpoint.Name
        $statusIcon = if ($health.Status -eq "Healthy") { "✅"; $healthyEndpoints++ } else { "❌" }
        
        Write-Host "  $statusIcon $($health.Name)" -NoNewline
        Write-Host " ($($health.StatusCode))" -ForegroundColor $(if ($health.Status -eq "Healthy") { "Green" } else { "Red" })
        
        if ($Detailed -and $health.ResponseTime -ne "N/A") {
            Write-Host "    Response time: $($health.ResponseTime)ms" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    
    # Database and Redis
    Write-Host "💾 Data Services:" -ForegroundColor Cyan
    $dbHealth = Test-DatabaseConnection
    $redisHealth = Test-RedisConnection
    
    Write-Host "  $(if ($dbHealth) { '✅' } else { '❌' }) PostgreSQL Database" -ForegroundColor $(if ($dbHealth) { "Green" } else { "Red" })
    Write-Host "  $(if ($redisHealth) { '✅' } else { '❌' }) Redis Cache" -ForegroundColor $(if ($redisHealth) { "Green" } else { "Red" })
    
    Write-Host ""
    
    # System resources
    if ($Detailed) {
        Write-Host "💻 System Resources:" -ForegroundColor Cyan
        $resources = Get-SystemResources
        Write-Host "  CPU: $($resources.CPU), Memory: $($resources.Memory), Disk: $($resources.Disk)" -ForegroundColor Gray
        
        Write-Host ""
        Write-Host "📊 Docker Container Stats:" -ForegroundColor Cyan
        $dockerStats = Get-DockerStats
        Write-Host $dockerStats -ForegroundColor Gray
        Write-Host ""
    }
    
    # Overall status
    $overallHealth = if ($healthyCount -eq $services.Count -and $healthyEndpoints -eq $endpoints.Count -and $dbHealth -and $redisHealth) {
        "🟢 HEALTHY"
    } elseif ($healthyCount -gt ($services.Count / 2)) {
        "🟡 DEGRADED"
    } else {
        "🔴 UNHEALTHY"
    }
    
    Write-Host "Overall Status: $overallHealth" -ForegroundColor $(
        if ($overallHealth.Contains("HEALTHY")) { "Green" }
        elseif ($overallHealth.Contains("DEGRADED")) { "Yellow" }
        else { "Red" }
    )
    
    Write-Host ""
    Write-Host "Last updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
    # Auto-repair if enabled
    if ($Fix) {
        $unhealthyServices = $services | Where-Object { 
            $health = Test-ContainerHealth $_
            $health.Status -ne "running"
        }
        
        if ($unhealthyServices) {
            Write-Host ""
            Write-Log "Auto-repair mode: Found $($unhealthyServices.Count) unhealthy services" "Warning"
            foreach ($service in $unhealthyServices) {
                Repair-Service $service
            }
        }
    }
}

# Main execution
if ($Continuous) {
    Write-Log "Starting continuous health monitoring (Ctrl+C to stop)..." "Info"
    Write-Log "Monitoring interval: $Interval seconds" "Info"
    
    try {
        while ($true) {
            Show-HealthReport
            
            if (-not $Continuous) { break }
            
            Write-Host ""
            Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor Yellow
            Start-Sleep -Seconds $Interval
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Log "Monitoring stopped by user" "Info"
    }
} else {
    Show-HealthReport
}
