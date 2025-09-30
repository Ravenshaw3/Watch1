# Fix Frontend Build and Add Database Info to Analytics v3.0.2
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "Fix Frontend Build + Add Database Info" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "ISSUES TO RESOLVE:" -ForegroundColor Red
Write-Host "- Frontend build failed" -ForegroundColor Yellow
Write-Host "- Need database type display on Analytics page" -ForegroundColor Yellow
Write-Host "- Show PostgreSQL vs SQLite usage" -ForegroundColor Yellow
Write-Host "- Display database locations and status" -ForegroundColor Yellow
Write-Host ""

Write-Host "COMPREHENSIVE SOLUTION:" -ForegroundColor Cyan
Write-Host "1. Diagnose and fix frontend build failure" -ForegroundColor White
Write-Host "2. Add database info API endpoint to backend" -ForegroundColor White
Write-Host "3. Enhance Analytics page with database information" -ForegroundColor White
Write-Host "4. Rebuild frontend container with fixes" -ForegroundColor White
Write-Host "5. Test database info display" -ForegroundColor White
Write-Host ""

# Copy the build fix and database info script
Write-Host "Copying build fix and database info script..." -ForegroundColor Yellow
scp fix-build-add-db-info-v302.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "Script copied!" -ForegroundColor Green
Write-Host ""

Write-Host "SSH to Unraid and run the fix:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x fix-build-add-db-info-v302.sh" -ForegroundColor White
Write-Host "./fix-build-add-db-info-v302.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow

Write-Host ""
Write-Host "WHAT THIS FIX DOES:" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""
Write-Host "BUILD FIXES:" -ForegroundColor Cyan
Write-Host "- Diagnoses frontend build failure causes" -ForegroundColor White
Write-Host "- Removes problematic frontend image" -ForegroundColor White
Write-Host "- Fixes TypeScript compilation issues" -ForegroundColor White
Write-Host "- Rebuilds container with --no-cache flag" -ForegroundColor White
Write-Host ""
Write-Host "DATABASE INFO FEATURES:" -ForegroundColor Cyan
Write-Host "- Adds /api/v1/system/database-info endpoint" -ForegroundColor White
Write-Host "- Shows PostgreSQL vs SQLite status" -ForegroundColor White
Write-Host "- Displays database locations and paths" -ForegroundColor White
Write-Host "- Shows connection status and record counts" -ForegroundColor White
Write-Host "- Identifies which database is currently active" -ForegroundColor White
Write-Host ""
Write-Host "ANALYTICS PAGE ENHANCEMENTS:" -ForegroundColor Cyan
Write-Host "- Database Information section added" -ForegroundColor White
Write-Host "- Visual status indicators (connected/error/disconnected)" -ForegroundColor White
Write-Host "- Record counts per database" -ForegroundColor White
Write-Host "- Database location paths displayed" -ForegroundColor White
Write-Host "- Active database highlighted" -ForegroundColor White

Write-Host ""
Write-Host "EXPECTED SUCCESS INDICATORS:" -ForegroundColor Yellow
Write-Host "============================" -ForegroundColor Yellow
Write-Host "✅ 'Frontend container rebuilt successfully'" -ForegroundColor Green
Write-Host "✅ 'Database info endpoint working'" -ForegroundColor Green
Write-Host "✅ 'Analytics page enhanced with database information'" -ForegroundColor Green
Write-Host "✅ 'BUILD FIXED AND DATABASE INFO ADDED!'" -ForegroundColor Green

Write-Host ""
Write-Host "AFTER THE FIX:" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Yellow
Write-Host "1. Go to http://192.168.254.14:3000" -ForegroundColor Cyan
Write-Host "2. Login with test@example.com / testpass123" -ForegroundColor Cyan
Write-Host "3. Navigate to Analytics page" -ForegroundColor Green
Write-Host "4. See 'Database Information' section at top" -ForegroundColor Green
Write-Host "5. View database type (PostgreSQL/SQLite)" -ForegroundColor Green
Write-Host "6. See database locations and connection status" -ForegroundColor Green
Write-Host "7. Check which database is currently active" -ForegroundColor Green
Write-Host "8. View record counts per database" -ForegroundColor Green

Write-Host ""
Write-Host "DATABASE INFO DISPLAYED:" -ForegroundColor Yellow
Write-Host "- Database Type: PostgreSQL or SQLite" -ForegroundColor Gray
Write-Host "- Location: Full path or connection string" -ForegroundColor Gray
Write-Host "- Status: Connected, Disconnected, or Error" -ForegroundColor Gray
Write-Host "- Records: Number of media files in each database" -ForegroundColor Gray
Write-Host "- Active: Which database is currently being used" -ForegroundColor Gray
