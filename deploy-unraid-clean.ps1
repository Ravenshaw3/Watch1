# Clean deployment script for Unraid server
param(
    [switch]$UseDockerHub = $false
)

$UNRAID_IP = "192.168.254.14"
$UNRAID_PATH = "/mnt/user/appdata/watch1"
$SSH_KEY = "~/.ssh/unraid_key"

function Write-Status {
    param([string]$Message)
    Write-Host "--- $Message ---" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

Write-Status "Deploying Watch1 to Unraid server..."

if ($UseDockerHub) {
    Write-Status "Using Docker Hub images..."
    # Copy docker-compose file that uses Docker Hub images
    scp -i $SSH_KEY docker-compose.prod.yml root@${UNRAID_IP}:${UNRAID_PATH}/docker-compose.yml
} else {
    Write-Status "Building and deploying local images..."
    
    # Build images locally
    Write-Status "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed"
        exit 1
    }
    
    # Save images
    Write-Status "Saving Docker images..."
    docker save watch1-backend:latest -o watch1-backend.tar
    docker save watch1-frontend:latest -o watch1-frontend.tar
    
    # Copy images to Unraid
    Write-Status "Copying Docker images to Unraid..."
    scp -i $SSH_KEY watch1-backend.tar root@${UNRAID_IP}:${UNRAID_PATH}/
    scp -i $SSH_KEY watch1-frontend.tar root@${UNRAID_IP}:${UNRAID_PATH}/
    
    # Copy source code (backend only - frontend is built into image)
    Write-Status "Copying backend source code..."
    scp -i $SSH_KEY -r backend/ root@${UNRAID_IP}:${UNRAID_PATH}/
    
    # Copy docker-compose file
    scp -i $SSH_KEY unraid-docker-compose.yml root@${UNRAID_IP}:${UNRAID_PATH}/docker-compose.yml
    
    # Cleanup local tar files
    Remove-Item -Force watch1-backend.tar, watch1-frontend.tar -ErrorAction SilentlyContinue
}

# Deploy on Unraid server using individual commands to avoid line ending issues
Write-Status "Deploying on Unraid server..."

# Stop existing services
Write-Status "Stopping existing services..."
ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker-compose down"

# Load Docker images if using local build
if (-not $UseDockerHub) {
    Write-Status "Loading Docker images..."
    ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker load -i watch1-backend.tar"
    ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker load -i watch1-frontend.tar"
}

# Start services
Write-Status "Starting services..."
ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker-compose up -d"

# Wait for services to start
Write-Status "Waiting for services to start..."
Start-Sleep -Seconds 15

# Check status
Write-Status "Checking service status..."
ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker-compose ps"

# Test deployment
Write-Status "Testing deployment..."

# Test backend health
$backendHealth = ssh -i $SSH_KEY root@$UNRAID_IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo '000'"
if ($backendHealth -eq "200") {
    Write-Success "Backend health check passed"
} else {
    Write-Host "⚠️  Backend health check: HTTP $backendHealth" -ForegroundColor Yellow
}

# Test frontend
$frontendHealth = ssh -i $SSH_KEY root@$UNRAID_IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo '000'"
if ($frontendHealth -eq "200") {
    Write-Success "Frontend health check passed"
} else {
    Write-Host "⚠️  Frontend health check: HTTP $frontendHealth" -ForegroundColor Yellow
}

Write-Success "🎉 Deployment complete!"
Write-Host ""
Write-Host "📱 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://$UNRAID_IP`:3000" -ForegroundColor White
Write-Host "   Backend API: http://$UNRAID_IP`:8000" -ForegroundColor White
Write-Host "   API Docs: http://$UNRAID_IP`:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default Login:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
