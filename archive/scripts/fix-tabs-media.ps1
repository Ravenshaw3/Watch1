# Fix Missing Navigation Tabs and Media Display Issues
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "Fix Navigation Tabs and Media Display" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "The issues you're experiencing:" -ForegroundColor Yellow
Write-Host "- Settings and Analytics tabs missing" -ForegroundColor Red
Write-Host "- No media displays in Library" -ForegroundColor Red
Write-Host ""

Write-Host "Common causes:" -ForegroundColor Yellow
Write-Host "1. User not logged in (tabs require authentication)" -ForegroundColor Gray
Write-Host "2. Empty database (no media files to display)" -ForegroundColor Gray
Write-Host "3. Backend API not responding properly" -ForegroundColor Gray
Write-Host "4. Frontend authentication store issues" -ForegroundColor Gray
Write-Host ""

# Copy the diagnostic script
Write-Host "Copying diagnostic script..." -ForegroundColor Yellow
scp fix-navigation-media-v302.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "Script copied!" -ForegroundColor Green
Write-Host ""

Write-Host "SSH to Unraid and run the diagnostic:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x fix-navigation-media-v302.sh" -ForegroundColor White
Write-Host "./fix-navigation-media-v302.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow

Write-Host ""
Write-Host "WHAT THE SCRIPT WILL DO:" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "1. Test backend connectivity and authentication" -ForegroundColor White
Write-Host "2. Check if media API endpoints are working" -ForegroundColor White
Write-Host "3. Verify database has media files" -ForegroundColor White
Write-Host "4. Add sample media files if database is empty" -ForegroundColor White
Write-Host "5. Restart services for clean state" -ForegroundColor White
Write-Host "6. Provide troubleshooting guidance" -ForegroundColor White

Write-Host ""
Write-Host "EXPECTED RESULTS:" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host "After running the script:" -ForegroundColor White
Write-Host "1. Go to http://192.168.254.14:3000" -ForegroundColor Cyan
Write-Host "2. Login with: test@example.com / testpass123" -ForegroundColor Cyan
Write-Host "3. Navigation tabs should appear after login" -ForegroundColor Green
Write-Host "4. Media should display in Library section" -ForegroundColor Green

Write-Host ""
Write-Host "QUICK MANUAL TEST:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host "If script doesn't fix it, try:" -ForegroundColor White
Write-Host "1. Clear browser cache completely" -ForegroundColor Gray
Write-Host "2. Use incognito/private browsing mode" -ForegroundColor Gray
Write-Host "3. Check browser console (F12) for errors" -ForegroundColor Gray
Write-Host "4. Test direct API: http://192.168.254.14:8000/api/v1/health" -ForegroundColor Gray
