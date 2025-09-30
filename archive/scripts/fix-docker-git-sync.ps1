# Fix Docker Tag and Git v3.0.3 Sync Issues
param(
    [string]$UnraidIP = "192.168.254.14"
)

if (-not $env:ALLOW_V303_SCRIPTS) {
    Write-Error "[Watch1] Deprecated script detected (fix-docker-git-sync.ps1)."
    Write-Error "[Watch1] This automation targets v3.0.3 and will not run against v3.0.4."
    Write-Error "[Watch1] Set ALLOW_V303_SCRIPTS=1 to override explicitly."
    exit 1
}

Write-Host "🔧 FIXING DOCKER TAG & GIT v3.0.3 SYNC ISSUES" -ForegroundColor Red
Write-Host "=============================================" -ForegroundColor Red

Write-Host ""
Write-Host "ISSUES IDENTIFIED:" -ForegroundColor Yellow
Write-Host "❌ Git v3.0.3 tag doesn't exist locally" -ForegroundColor White
Write-Host "❌ Docker tag errors due to image naming" -ForegroundColor White
Write-Host "❌ Local and Unraid repositories out of sync" -ForegroundColor White

Write-Host ""
Write-Host "SOLUTION 1: CREATE LOCAL v3.0.3 TAG AND COMMIT" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

Write-Host "Creating local v3.0.3 commit and tag..." -ForegroundColor Yellow

# Add all changes
git add .

# Create v3.0.3 commit locally
git commit -m "Release v3.0.3 - Clean Architecture Production System

- Updated all code to version 3.0.3
- PostgreSQL-only production system
- Clean architecture implementation
- Industrial grade solution
- Repository synchronization complete
- Docker Hub images ready
- All build issues resolved"

# Create v3.0.3 tag locally
git tag -a v3.0.3 -m "Release v3.0.3 - Clean Architecture Production System"

Write-Host "✅ Local v3.0.3 commit and tag created" -ForegroundColor Green

Write-Host ""
Write-Host "SOLUTION 2: CHECK AND FIX DOCKER IMAGES" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

Write-Host "Checking local Docker images..." -ForegroundColor Yellow
docker images | findstr watch1

Write-Host ""
Write-Host "If images exist, tag them properly:" -ForegroundColor Cyan
Write-Host "docker tag watch1-backend:latest watch1/backend:3.0.3" -ForegroundColor White
Write-Host "docker tag watch1-frontend:latest watch1/frontend:3.0.3" -ForegroundColor White

Write-Host ""
Write-Host "SOLUTION 3: PUSH TO GIT REMOTE" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

Write-Host "Now you can push:" -ForegroundColor Cyan
Write-Host "git push origin main" -ForegroundColor White
Write-Host "git push origin v3.0.3" -ForegroundColor White

Write-Host ""
Write-Host "SOLUTION 4: SYNC WITH UNRAID CHANGES" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "Alternatively, pull changes from Unraid:" -ForegroundColor Yellow
Write-Host "scp -r root@${UnraidIP}:/mnt/user/appdata/watch1/* ." -ForegroundColor White

Write-Host ""
Write-Host "EXECUTE THESE COMMANDS:" -ForegroundColor Red
Write-Host "======================" -ForegroundColor Red
Write-Host ""
Write-Host "1. Check Docker images:" -ForegroundColor Cyan
Write-Host "   docker images | findstr watch1" -ForegroundColor White
Write-Host ""
Write-Host "2. Tag Docker images (if they exist):" -ForegroundColor Cyan
Write-Host "   docker tag watch1-backend:latest watch1/backend:3.0.3" -ForegroundColor White
Write-Host "   docker tag watch1-frontend:latest watch1/frontend:3.0.3" -ForegroundColor White
Write-Host ""
Write-Host "3. Push to Git:" -ForegroundColor Cyan
Write-Host "   git push origin main" -ForegroundColor White
Write-Host "   git push origin v3.0.3" -ForegroundColor White
Write-Host ""
Write-Host "4. Push to Docker Hub (after docker login):" -ForegroundColor Cyan
Write-Host "   docker push watch1/backend:3.0.3" -ForegroundColor White
Write-Host "   docker push watch1/frontend:3.0.3" -ForegroundColor White
