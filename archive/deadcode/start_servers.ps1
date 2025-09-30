# Watch1 v3.0.1 Production Server Startup Script
# Cleans up existing processes and starts fresh production servers

Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host ("=" * 59) -ForegroundColor Green
Write-Host "WATCH1 v3.0.1 - PRODUCTION SERVER STARTUP" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host ("=" * 59) -ForegroundColor Green
Write-Host ""

# Function to log messages
function Write-Log {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Status) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Status] $Message" -ForegroundColor $color
}

# Function to kill processes on a specific port
function Stop-ProcessesOnPort {
    param([int]$Port)
    
    Write-Log "Checking for processes on port $Port..."
    
    try {
        $connections = netstat -ano | Select-String ":$Port\s" | Where-Object { $_ -match "LISTENING" }
        
        if ($connections) {
            foreach ($connection in $connections) {
                if ($connection -match "\s+(\d+)$") {
                    $pid = $Matches[1]
                    try {
                        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                        if ($process) {
                            Write-Log "Killing process $($process.ProcessName) (PID: $pid)" "WARNING"
                            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                            Start-Sleep -Milliseconds 500
                        }
                    }
                    catch {
                        Write-Log "Could not kill process PID $pid" "WARNING"
                    }
                }
            }
        }
        else {
            Write-Log "Port $Port is free" "SUCCESS"
        }
    }
    catch {
        Write-Log "Error checking port $Port`: $($_.Exception.Message)" "ERROR"
    }
}

# Function to kill Node.js processes that might be Watch1 related
function Stop-NodeProcesses {
    Write-Log "Checking for Node.js processes..."
    
    try {
        $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
        
        if ($nodeProcesses) {
            Write-Log "Found $($nodeProcesses.Count) Node.js process(es), stopping them..." "WARNING"
            foreach ($proc in $nodeProcesses) {
                try {
                    Write-Log "Stopping Node.js process (PID: $($proc.Id))" "WARNING"
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                }
                catch {
                    Write-Log "Could not stop Node.js process PID $($proc.Id)" "WARNING"
                }
            }
            Start-Sleep -Seconds 2
        }
        else {
            Write-Log "No Node.js processes found" "SUCCESS"
        }
    }
    catch {
        Write-Log "Error checking Node.js processes: $($_.Exception.Message)" "WARNING"
    }
}

# Function to test if a URL is accessible
function Test-ServerUrl {
    param([string]$Url, [string]$Name)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Log "$Name test: OK (HTTP $($response.StatusCode))" "SUCCESS"
            return $true
        }
        else {
            Write-Log "$Name test: FAILED (HTTP $($response.StatusCode))" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "$Name test: FAILED ($($_.Exception.Message))" "ERROR"
        return $false
    }
}

# Main execution
try {
    # Step 1: Clean up existing processes
    Write-Log "Cleaning up existing server processes..."
    Stop-ProcessesOnPort 8000  # Backend
    Stop-ProcessesOnPort 3000  # Frontend
    Stop-NodeProcesses
    
    # Wait for processes to fully terminate
    Write-Log "Waiting for processes to terminate..."
    Start-Sleep -Seconds 3
    
    # Step 2: Verify directories exist
    if (-not (Test-Path "backend\flask_simple.py")) {
        Write-Log "Backend file not found: backend\flask_simple.py" "ERROR"
        exit 1
    }
    
    if (-not (Test-Path "frontend\package.json")) {
        Write-Log "Frontend file not found: frontend\package.json" "ERROR"
        exit 1
    }
    
    # Step 3: Start backend server
    Write-Log "Starting Flask backend server..."
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location backend
        python flask_simple.py
    }
    
    # Wait for backend to start
    Start-Sleep -Seconds 3
    
    # Step 4: Start frontend server
    Write-Log "Starting Vue.js frontend server..."
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location frontend
        npm run dev
    }
    
    # Wait for frontend to initialize
    Write-Log "Waiting for servers to initialize..."
    Start-Sleep -Seconds 8
    
    # Step 5: Test servers
    Write-Log "Testing server connectivity..."
    
    $backendOk = Test-ServerUrl "http://localhost:8000/api/v1/version" "Backend"
    $frontendOk = Test-ServerUrl "http://localhost:3000" "Frontend"
    
    if ($backendOk -and $frontendOk) {
        Write-Host ""
        Write-Host "=" -ForegroundColor Green -NoNewline
        Write-Host ("=" * 59) -ForegroundColor Green
        Write-Log "PRODUCTION SERVERS SUCCESSFULLY STARTED!" "SUCCESS"
        Write-Host "=" -ForegroundColor Green -NoNewline
        Write-Host ("=" * 59) -ForegroundColor Green
        Write-Host ""
        Write-Host "Backend:  " -NoNewline -ForegroundColor White
        Write-Host "http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Frontend: " -NoNewline -ForegroundColor White
        Write-Host "http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "=" -ForegroundColor Green -NoNewline
        Write-Host ("=" * 59) -ForegroundColor Green
        Write-Host ""
        Write-Log "Press Ctrl+C to stop all servers" "INFO"
        
        # Keep running until interrupted
        try {
            while ($true) {
                Start-Sleep -Seconds 1
                
                # Check if jobs are still running
                if ($backendJob.State -ne "Running") {
                    Write-Log "Backend server stopped unexpectedly!" "ERROR"
                    break
                }
                if ($frontendJob.State -ne "Running") {
                    Write-Log "Frontend server stopped unexpectedly!" "ERROR"
                    break
                }
            }
        }
        catch {
            Write-Log "Shutting down servers..." "INFO"
        }
    }
    else {
        Write-Log "Server startup failed!" "ERROR"
    }
}
catch {
    Write-Log "Startup error: $($_.Exception.Message)" "ERROR"
}
finally {
    # Cleanup
    Write-Log "Cleaning up background jobs..." "INFO"
    
    if ($backendJob) {
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
    }
    
    if ($frontendJob) {
        Stop-Job $frontendJob -ErrorAction SilentlyContinue
        Remove-Job $frontendJob -ErrorAction SilentlyContinue
    }
    
    # Final cleanup of any remaining processes
    Stop-ProcessesOnPort 8000
    Stop-ProcessesOnPort 3000
    Stop-NodeProcesses
    
    Write-Log "Cleanup complete" "SUCCESS"
}

