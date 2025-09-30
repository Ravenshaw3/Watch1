# CLEAN ALL CODE AND UPDATE TO v3.0.3 - Complete Repository Update
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

if (-not $env:ALLOW_V303_SCRIPTS) {
    Write-Error "[Watch1] Deprecated script detected (clean-and-update-v303.ps1)."
    Write-Error "[Watch1] This automation targets v3.0.3 and will not run against v3.0.4."
    Write-Error "[Watch1] Set ALLOW_V303_SCRIPTS=1 to override explicitly."
    exit 1
}

Write-Host "CLEAN ALL CODE AND UPDATE TO v3.0.3" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red
Write-Host "Complete cleanup and repository update solution" -ForegroundColor Yellow
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "COMPREHENSIVE CLEANUP AND UPDATE:" -ForegroundColor Green
Write-Host "✅ Clean all code and directories" -ForegroundColor White
Write-Host "✅ Update all code to version 3.0.3" -ForegroundColor White
Write-Host "✅ Prepare Docker Hub updates" -ForegroundColor White
Write-Host "✅ Prepare Git repository updates" -ForegroundColor White
Write-Host "✅ Clean architecture implementation" -ForegroundColor White
Write-Host "✅ PostgreSQL-only production system" -ForegroundColor White
Write-Host ""

Write-Host "COPYING CLEANUP AND UPDATE SCRIPT..." -ForegroundColor Yellow
scp clean-and-update-v303.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "✅ CLEANUP SCRIPT COPIED" -ForegroundColor Green
Write-Host ""

Write-Host "EXECUTE THE COMPLETE CLEANUP AND UPDATE:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x clean-and-update-v303.sh" -ForegroundColor White
Write-Host "./clean-and-update-v303.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow

Write-Host ""
Write-Host "WHAT THIS COMPLETE SOLUTION DOES:" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "CLEANUP PHASE:" -ForegroundColor Cyan
Write-Host "- Stop and remove all containers and images" -ForegroundColor White
Write-Host "- Clean Docker system and remove orphans" -ForegroundColor White
Write-Host "- Remove temporary files, logs, and build artifacts" -ForegroundColor White
Write-Host "- Clean node_modules and Python cache" -ForegroundColor White
Write-Host ""
Write-Host "UPDATE PHASE:" -ForegroundColor Cyan
Write-Host "- Update frontend package.json to v3.0.3" -ForegroundColor White
Write-Host "- Update backend flask_simple.py to v3.0.3" -ForegroundColor White
Write-Host "- Update VersionInfo.vue to display v3.0.3" -ForegroundColor White
Write-Host "- Update all Docker configurations" -ForegroundColor White
Write-Host "- Create repository update scripts" -ForegroundColor White
Write-Host ""
Write-Host "BUILD PHASE:" -ForegroundColor Cyan
Write-Host "- Rebuild all containers with --no-cache" -ForegroundColor White
Write-Host "- Start clean v3.0.3 system" -ForegroundColor White
Write-Host "- Verify version and health endpoints" -ForegroundColor White
Write-Host "- Test PostgreSQL connections" -ForegroundColor White
Write-Host ""
Write-Host "REPOSITORY UPDATE SCRIPTS:" -ForegroundColor Cyan
Write-Host "- update-docker-hub-v303.sh (Docker Hub update)" -ForegroundColor White
Write-Host "- update-git-repos-v303.sh (Git repository update)" -ForegroundColor White

Write-Host ""
Write-Host "SUCCESS INDICATORS:" -ForegroundColor Yellow
Write-Host "✅ 'All code cleaned and updated to v3.0.3'" -ForegroundColor Green
Write-Host "✅ 'Version 3.0.3 confirmed'" -ForegroundColor Green
Write-Host "✅ 'System health verified'" -ForegroundColor Green
Write-Host "✅ 'PostgreSQL connection verified'" -ForegroundColor Green
Write-Host "✅ 'CLEAN v3.0.3 SYSTEM COMPLETE'" -ForegroundColor Green

Write-Host ""
Write-Host "AFTER COMPLETION:" -ForegroundColor Yellow
Write-Host "- Frontend: http://192.168.254.14:3000 (v3.0.3)" -ForegroundColor Cyan
Write-Host "- Backend: http://192.168.254.14:8000 (v3.0.3)" -ForegroundColor Cyan
Write-Host "- Database: PostgreSQL Production Only" -ForegroundColor Cyan
Write-Host "- Architecture: Clean Industrial Grade" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS AFTER CLEANUP:" -ForegroundColor Yellow
Write-Host "1. Run: ./update-docker-hub-v303.sh" -ForegroundColor White
Write-Host "2. Run: ./update-git-repos-v303.sh" -ForegroundColor White
Write-Host ""
Write-Host "THIS IS THE COMPLETE SOLUTION - CLEAN SLATE v3.0.3" -ForegroundColor Red
