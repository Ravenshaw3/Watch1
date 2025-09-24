# Watch1 v3.0.1 - Development Environment Reset Script
# Complete environment reset with database migration and fresh start

param(
    [switch]$KeepData,      # Keep database data during reset
    [switch]$Force,         # Skip confirmations
    [switch]$Migrate        # Run database migrations after reset
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

Write-Header "Watch1 v3.0.1 - Development Environment Reset"

# Confirmation
if (-not $Force) {
    Write-Log "This will completely reset the development environment!" "Warning"
    if (-not $KeepData) {
        Write-Log "ALL DATA WILL BE LOST including database and uploaded files!" "Error"
    }
    $confirmation = Read-Host "Are you sure you want to continue? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Log "Reset cancelled" "Info"
        exit 0
    }
}

# Step 1: Stop all services
Write-Log "Stopping all services..." "Info"
docker-compose -f $ComposeFile down --remove-orphans

# Step 2: Clean up containers and images
Write-Log "Cleaning up Docker resources..." "Info"
if ($KeepData) {
    # Keep volumes but remove containers
    docker-compose -f $ComposeFile down --remove-orphans
    Write-Log "Containers removed, data volumes preserved" "Success"
} else {
    # Remove everything including volumes
    docker-compose -f $ComposeFile down -v --remove-orphans
    Write-Log "All containers and volumes removed" "Success"
}

# Step 3: Clean up Docker system
Write-Log "Performing Docker system cleanup..." "Info"
docker system prune -f
docker image prune -f

# Step 4: Clean up application files
Write-Log "Cleaning up application files..." "Info"

# Remove log files
if (Test-Path "logs") {
    Remove-Item -Path "logs\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Log "Log files cleaned" "Success"
}

# Remove temporary files
$tempPaths = @("backend\__pycache__", "backend\*.pyc", "frontend\node_modules\.cache", "frontend\dist")
foreach ($path in $tempPaths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Log "Temporary files cleaned" "Success"

# Step 5: Rebuild everything
Write-Log "Rebuilding development environment..." "Info"
docker-compose -f $ComposeFile build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Log "Build failed!" "Error"
    exit 1
}

Write-Log "Build completed successfully" "Success"

# Step 6: Start services
Write-Log "Starting services..." "Info"
docker-compose -f $ComposeFile up -d

if ($LASTEXITCODE -ne 0) {
    Write-Log "Failed to start services!" "Error"
    exit 1
}

# Step 7: Wait for services to be ready
Write-Log "Waiting for services to initialize..." "Info"
Start-Sleep -Seconds 30

# Step 8: Database migration (if requested or if data was reset)
if ($Migrate -or -not $KeepData) {
    Write-Log "Running database migrations..." "Info"
    
    # Wait for database to be ready
    $maxAttempts = 30
    $attempt = 0
    do {
        $dbReady = docker-compose -f $ComposeFile exec -T database pg_isready -U watch1_user -d watch1_dev
        if ($LASTEXITCODE -eq 0) {
            break
        }
        Start-Sleep -Seconds 2
        $attempt++
        Write-Host "." -NoNewline -ForegroundColor Yellow
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Log "Database failed to start!" "Error"
        exit 1
    }
    
    Write-Host ""
    Write-Log "Database is ready, running migrations..." "Info"
    
    # Run database initialization
    docker-compose -f $ComposeFile exec backend python -c "
from flask_simple import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Database migrations completed" "Success"
    } else {
        Write-Log "Database migrations failed" "Warning"
    }
}

# Step 9: Health check
Write-Log "Performing health check..." "Info"
& ".\scripts\dev-health.ps1"

# Step 10: Create default admin user (if data was reset)
if (-not $KeepData) {
    Write-Log "Creating default admin user..." "Info"
    
    docker-compose -f $ComposeFile exec backend python -c "
from flask_simple import app, db
from werkzeug.security import generate_password_hash
import sqlite3

with app.app_context():
    try:
        conn = sqlite3.connect('watch1.db')
        cursor = conn.cursor()
        
        # Create admin user
        hashed_password = generate_password_hash('testpass123')
        cursor.execute('''
            INSERT OR REPLACE INTO users (email, hashed_password, is_superuser, is_active)
            VALUES (?, ?, ?, ?)
        ''', ('test@example.com', hashed_password, True, True))
        
        conn.commit()
        conn.close()
        print('Default admin user created: test@example.com / testpass123')
    except Exception as e:
        print(f'Failed to create admin user: {e}')
"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Default admin user created" "Success"
    } else {
        Write-Log "Failed to create admin user" "Warning"
    }
}

Write-Header "Reset Complete!"

Write-Log "Development environment has been reset successfully" "Success"
Write-Log "Frontend: http://localhost:3000" "Info"
Write-Log "Backend API: http://localhost:8000/api/v1" "Info"
Write-Log "Nginx Proxy: http://localhost" "Info"

if (-not $KeepData) {
    Write-Log "Default login: test@example.com / testpass123" "Info"
}

Write-Log "Use '.\scripts\dev-health.ps1 -Detailed' for detailed status" "Info"
