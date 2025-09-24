# Fix PostgreSQL and Authentication Issues for v3.0.2
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "Fix PostgreSQL and Authentication Issues" -ForegroundColor Red
Write-Host "=======================================" -ForegroundColor Red
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "ISSUES IDENTIFIED:" -ForegroundColor Red
Write-Host "- PostgreSQL test failed: users not exist" -ForegroundColor Yellow
Write-Host "- 401 errors in media API" -ForegroundColor Yellow
Write-Host "- 401 errors in categories API" -ForegroundColor Yellow
Write-Host ""

Write-Host "ROOT CAUSES:" -ForegroundColor Yellow
Write-Host "1. PostgreSQL database creation failed" -ForegroundColor Gray
Write-Host "2. Test user was not created properly" -ForegroundColor Gray
Write-Host "3. Authentication system cannot find users" -ForegroundColor Gray
Write-Host "4. Backend may not be connecting to correct database" -ForegroundColor Gray
Write-Host ""

Write-Host "THIS FIX WILL:" -ForegroundColor Cyan
Write-Host "1. Recreate PostgreSQL database from scratch" -ForegroundColor White
Write-Host "2. Create proper schema with error handling" -ForegroundColor White
Write-Host "3. Add test user with correct bcrypt hash" -ForegroundColor White
Write-Host "4. Synchronize SQLite database with same data" -ForegroundColor White
Write-Host "5. Test authentication with JWT tokens" -ForegroundColor White
Write-Host "6. Verify API endpoints work with authentication" -ForegroundColor White
Write-Host ""

# Copy the fix script
Write-Host "Copying PostgreSQL and authentication fix..." -ForegroundColor Yellow
scp fix-postgres-auth-v302.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "Fix script copied!" -ForegroundColor Green
Write-Host ""

Write-Host "SSH to Unraid and run the fix:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x fix-postgres-auth-v302.sh" -ForegroundColor White
Write-Host "./fix-postgres-auth-v302.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow

Write-Host ""
Write-Host "EXPECTED RESULTS:" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host "After running the fix:" -ForegroundColor White
Write-Host ""
Write-Host "DATABASE STATUS:" -ForegroundColor Cyan
Write-Host "- PostgreSQL database recreated successfully" -ForegroundColor Green
Write-Host "- Test user created: test@example.com / testpass123" -ForegroundColor Green
Write-Host "- 7 sample media files added" -ForegroundColor Green
Write-Host "- SQLite database synchronized with same data" -ForegroundColor Green
Write-Host ""
Write-Host "AUTHENTICATION STATUS:" -ForegroundColor Cyan
Write-Host "- Login endpoint returns 200 OK" -ForegroundColor Green
Write-Host "- JWT token generated successfully" -ForegroundColor Green
Write-Host "- No more 401 authentication errors" -ForegroundColor Green
Write-Host ""
Write-Host "API STATUS:" -ForegroundColor Cyan
Write-Host "- Media API returns 200 OK with authentication" -ForegroundColor Green
Write-Host "- Categories API returns 200 OK with authentication" -ForegroundColor Green
Write-Host "- All endpoints working properly" -ForegroundColor Green

Write-Host ""
Write-Host "AFTER THE FIX:" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Yellow
Write-Host "1. Go to http://192.168.254.14:3000" -ForegroundColor Cyan
Write-Host "2. Login with test@example.com / testpass123" -ForegroundColor Cyan
Write-Host "3. Navigation tabs (Settings, Analytics) should appear" -ForegroundColor Green
Write-Host "4. Library should show 7 media files" -ForegroundColor Green
Write-Host "5. No more 401 authentication errors" -ForegroundColor Green
Write-Host "6. All API endpoints working" -ForegroundColor Green

Write-Host ""
Write-Host "TROUBLESHOOTING:" -ForegroundColor Yellow
Write-Host "If issues persist after the fix:" -ForegroundColor Gray
Write-Host "- Check backend logs: docker-compose logs -f watch1-backend" -ForegroundColor Gray
Write-Host "- Verify which database backend is using" -ForegroundColor Gray
Write-Host "- Test API directly: curl http://192.168.254.14:8000/api/v1/health" -ForegroundColor Gray
