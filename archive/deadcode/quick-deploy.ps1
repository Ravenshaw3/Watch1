# Quick deployment script - only copies essential files
param(
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false
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

Write-Status "Quick deployment to Unraid server..."

# Build images locally
Write-Status "Building Docker images..."
if ($BackendOnly) {
    docker-compose -f docker-compose.prod.yml build backend
} elseif ($FrontendOnly) {
    docker-compose -f docker-compose.prod.yml build frontend
} else {
    docker-compose -f docker-compose.prod.yml build
}

# Save images
Write-Status "Saving Docker images..."
docker save watch1-backend:latest -o watch1-backend.tar
docker save watch1-frontend:latest -o watch1-frontend.tar

# Copy only essential files (no node_modules)
Write-Status "Copying essential files..."

# Copy Docker images
scp -i $SSH_KEY watch1-backend.tar root@${UNRAID_IP}:${UNRAID_PATH}/
scp -i $SSH_KEY watch1-frontend.tar root@${UNRAID_IP}:${UNRAID_PATH}/

# Copy source code (excluding node_modules and other large directories)
if (-not $FrontendOnly) {
    Write-Status "Copying backend source..."
    scp -i $SSH_KEY -r backend/ root@${UNRAID_IP}:${UNRAID_PATH}/
}

if (-not $BackendOnly) {
    Write-Status "Copying frontend source..."
    # Create a temporary directory with only essential frontend files
    $tempDir = "temp-frontend"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    # Copy essential files only
    Copy-Item -Path "frontend/src" -Destination "$tempDir/src" -Recurse
    Copy-Item -Path "frontend/public" -Destination "$tempDir/public" -Recurse
    Copy-Item -Path "frontend/package.json" -Destination "$tempDir/"
    Copy-Item -Path "frontend/vite.config.ts" -Destination "$tempDir/"
    Copy-Item -Path "frontend/tsconfig.json" -Destination "$tempDir/"
    Copy-Item -Path "frontend/tailwind.config.js" -Destination "$tempDir/"
    Copy-Item -Path "frontend/postcss.config.js" -Destination "$tempDir/"
    Copy-Item -Path "frontend/index.html" -Destination "$tempDir/"
    Copy-Item -Path "frontend/Dockerfile" -Destination "$tempDir/"
    
    scp -i $SSH_KEY -r $tempDir/ root@${UNRAID_IP}:${UNRAID_PATH}/frontend/
    
    # Cleanup temp directory
    Remove-Item -Path $tempDir -Recurse -Force
}

# Copy docker-compose file
scp -i $SSH_KEY unraid-docker-compose.yml root@${UNRAID_IP}:${UNRAID_PATH}/docker-compose.yml

# Deploy on Unraid
Write-Status "Deploying on Unraid server..."
$deployScript = @"
cd $UNRAID_PATH
docker load -i watch1-backend.tar
docker load -i watch1-frontend.tar
docker-compose down
docker-compose up -d --build
sleep 5
docker-compose ps
"@

ssh -i $SSH_KEY root@$UNRAID_IP $deployScript

# Cleanup
Remove-Item -Force watch1-backend.tar, watch1-frontend.tar -ErrorAction SilentlyContinue

Write-Success "🎉 Quick deployment complete!"
Write-Host "Access at: http://$UNRAID_IP`:3000" -ForegroundColor Cyan
