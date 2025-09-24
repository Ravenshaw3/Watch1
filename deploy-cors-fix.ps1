# Deploy CORS Fix to Unraid
# Run this script to copy all fixed files and deploy

$UnraidIP = "192.168.254.14"

Write-Host "🔧 Deploying CORS fix to Unraid..." -ForegroundColor Green

# Copy all necessary files
Write-Host "📤 Copying fixed files..." -ForegroundColor Yellow
scp backend/flask_simple.py root@${UnraidIP}:/mnt/user/appdata/watch1/backend/
scp docker-compose.unraid.yml root@${UnraidIP}:/mnt/user/appdata/watch1/docker-compose.yml
scp fix-cors-unraid.sh root@${UnraidIP}:/mnt/user/appdata/watch1/
scp fix-sqlite-login.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "✅ Files copied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next: SSH to Unraid and run:" -ForegroundColor Cyan
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x fix-cors-unraid.sh" -ForegroundColor White
Write-Host "./fix-cors-unraid.sh" -ForegroundColor White
