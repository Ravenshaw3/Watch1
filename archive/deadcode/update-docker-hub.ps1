# Script to update Docker Hub images
# Run this when you're ready to push to Docker Hub

Write-Host "🐳 Updating Docker Hub images..." -ForegroundColor Blue

# Tag the latest local images
Write-Host "Tagging images..." -ForegroundColor Yellow
docker tag watch1-backend:latest ravenshaw3/watch1-backend:latest
docker tag watch1-frontend:latest ravenshaw3/watch1-frontend:latest

Write-Host "✅ Images tagged successfully" -ForegroundColor Green

# Check if logged in
Write-Host "Checking Docker Hub login status..." -ForegroundColor Yellow
$loginStatus = docker system info | Select-String "Username"

if ($loginStatus) {
    Write-Host "✅ Already logged into Docker Hub" -ForegroundColor Green
    
    # Push images
    Write-Host "Pushing backend image..." -ForegroundColor Yellow
    docker push ravenshaw3/watch1-backend:latest
    
    Write-Host "Pushing frontend image..." -ForegroundColor Yellow
    docker push ravenshaw3/watch1-frontend:latest
    
    Write-Host "🎉 Docker Hub images updated successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Not logged into Docker Hub" -ForegroundColor Red
    Write-Host "Please run: docker login --username ravenshaw3" -ForegroundColor Yellow
    Write-Host "Then run this script again to push the images." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. If not logged in, run: docker login --username ravenshaw3" -ForegroundColor White
Write-Host "2. Run this script again to push images" -ForegroundColor White
Write-Host "3. Continue with Unraid deployment" -ForegroundColor White
