# Quick Unraid Debug and Fix
$UnraidIP = "192.168.254.14"

Write-Host "🔧 Quick Unraid Debug and Fix" -ForegroundColor Green

# Copy the fix script
Write-Host "📤 Copying debug script..." -ForegroundColor Yellow
scp fix-missing-tabs-login.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "✅ Script copied!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Now SSH to Unraid and run:" -ForegroundColor Cyan
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x fix-missing-tabs-login.sh" -ForegroundColor White
Write-Host "./fix-missing-tabs-login.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: videosmile" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 This will:" -ForegroundColor Cyan
Write-Host "  ✅ Check container status" -ForegroundColor Green
Write-Host "  ✅ Test backend/frontend connectivity" -ForegroundColor Green
Write-Host "  ✅ Fix database and user issues" -ForegroundColor Green
Write-Host "  ✅ Restart containers if needed" -ForegroundColor Green
Write-Host "  ✅ Test login functionality" -ForegroundColor Green
