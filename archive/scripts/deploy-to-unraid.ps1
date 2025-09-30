# Enhanced deployment script for Unraid server (PowerShell version)
# This script builds locally and deploys to Unraid for testing

param(
    [switch]$Quick = $false
)

# Configuration
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

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Check if SSH key exists
if (-not (Test-Path $SSH_KEY)) {
    Write-Error "SSH key not found at $SSH_KEY"
    exit 1
}

Write-Status "Starting Watch1 deployment to Unraid server..."

# Step 1: Build Docker images locally
Write-Status "Building Docker images locally..."
docker-compose -f docker-compose.prod.yml build --no-cache

if ($LASTEXITCODE -eq 0) {
    Write-Success "Local build completed successfully"
} else {
    Write-Error "Local build failed"
    exit 1
}

# Step 2: Save Docker images as tar files
Write-Status "Saving Docker images..."
docker save watch1-backend:latest -o watch1-backend.tar
docker save watch1-frontend:latest -o watch1-frontend.tar

Write-Success "Docker images saved"

# Step 3: Copy files to Unraid server
Write-Status "Copying files to Unraid server..."

# Copy Docker images
scp -i $SSH_KEY watch1-backend.tar root@${UNRAID_IP}:${UNRAID_PATH}/
scp -i $SSH_KEY watch1-frontend.tar root@${UNRAID_IP}:${UNRAID_PATH}/

# Copy updated source code
scp -i $SSH_KEY -r backend/ root@${UNRAID_IP}:${UNRAID_PATH}/
scp -i $SSH_KEY -r frontend/ root@${UNRAID_IP}:${UNRAID_PATH}/

# Copy docker-compose file
scp -i $SSH_KEY unraid-docker-compose.yml root@${UNRAID_IP}:${UNRAID_PATH}/docker-compose.yml

Write-Success "Files copied to Unraid server"

# Step 4: Deploy on Unraid server
Write-Status "Deploying on Unraid server..."

$deployScript = @"
cd $UNRAID_PATH

# Load Docker images
docker load -i watch1-backend.tar
docker load -i watch1-frontend.tar

# Stop existing services
docker-compose down

# Start services with new images
docker-compose up -d --build

# Wait for services to start
sleep 10

# Check status
docker-compose ps
"@

ssh -i $SSH_KEY root@$UNRAID_IP $deployScript

if ($LASTEXITCODE -eq 0) {
    Write-Success "Deployment completed successfully"
} else {
    Write-Error "Deployment failed"
    exit 1
}

# Step 5: Test deployment
Write-Status "Testing deployment..."

# Test backend health
$backendHealth = ssh -i $SSH_KEY root@$UNRAID_IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health"
if ($backendHealth -eq "200") {
    Write-Success "Backend health check passed"
} else {
    Write-Warning "Backend health check failed (HTTP $backendHealth)"
}

# Test frontend
$frontendHealth = ssh -i $SSH_KEY root@$UNRAID_IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000"
if ($frontendHealth -eq "200") {
    Write-Success "Frontend health check passed"
} else {
    Write-Warning "Frontend health check failed (HTTP $frontendHealth)"
}

# Clean up local tar files
Remove-Item -Force watch1-backend.tar, watch1-frontend.tar -ErrorAction SilentlyContinue

Write-Success "🎉 Deployment complete!"
Write-Host ""
Write-Host "📱 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://$UNRAID_IP`:3000" -ForegroundColor White
Write-Host "   Backend API: http://$UNRAID_IP`:8000" -ForegroundColor White
Write-Host "   Nginx (if configured): http://$UNRAID_IP`:8083" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default Login:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""

# Show final status
Write-Status "Final service status:"
ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker-compose ps"
