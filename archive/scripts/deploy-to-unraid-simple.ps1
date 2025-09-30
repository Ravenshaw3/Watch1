# Watch1 Unraid Deployment Script - Simple Version
param(
    [Parameter(Mandatory=$true)]
    [string]$UnraidIP
)

Write-Host "🚀 Watch1 Unraid Deployment" -ForegroundColor Green
Write-Host "Unraid Server: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build images
Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
docker build -t watch1-backend:latest -f docker/Dockerfile.backend .
docker build -t watch1-frontend:latest -f docker/Dockerfile.frontend .

# Step 2: Save images
Write-Host "💾 Saving images..." -ForegroundColor Yellow
docker save watch1-backend:latest | gzip > watch1-backend.tar.gz
docker save watch1-frontend:latest | gzip > watch1-frontend.tar.gz

# Step 3: Create deployment directory
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
$deployDir = "watch1-unraid-deployment"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy files
Copy-Item "docker-compose.unraid.yml" "$deployDir/docker-compose.yml"
Copy-Item "UNRAID_DEPLOYMENT_GUIDE.md" "$deployDir/"
Copy-Item "watch1-backend.tar.gz" "$deployDir/"
Copy-Item "watch1-frontend.tar.gz" "$deployDir/"

# Create simple deployment script
$bashScript = @"
#!/bin/bash
echo "Deploying Watch1 Media Server..."

mkdir -p /mnt/user/appdata/watch1/data
mkdir -p /mnt/user/appdata/watch1/logs  
mkdir -p /mnt/user/appdata/watch1/thumbnails

docker load < watch1-backend.tar.gz
docker load < watch1-frontend.tar.gz

docker-compose up -d

echo "Deployment complete!"
echo "Access at: http://$UnraidIP:3000"
echo "Login: test@example.com / testpass123"
"@

$bashScript | Out-File -FilePath "$deployDir/deploy.sh" -Encoding UTF8

Write-Host "✅ Deployment package ready: $deployDir" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Copy the '$deployDir' folder to your Unraid server" -ForegroundColor White
Write-Host "2. SSH to Unraid: ssh root@$UnraidIP" -ForegroundColor White
Write-Host "3. Navigate: cd /mnt/user/appdata/watch1-unraid-deployment" -ForegroundColor White
Write-Host "4. Run: chmod +x deploy.sh" -ForegroundColor White
Write-Host "5. Deploy: ./deploy.sh" -ForegroundColor White
Write-Host "6. Access: http://$UnraidIP:3000" -ForegroundColor White

# Cleanup
Remove-Item "watch1-backend.tar.gz" -ErrorAction SilentlyContinue
Remove-Item "watch1-frontend.tar.gz" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🎉 Ready for Unraid deployment!" -ForegroundColor Green
