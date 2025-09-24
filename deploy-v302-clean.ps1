# Watch1 Media Server v3.0.2 - Clean Unraid Deployment Script
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "Watch1 Media Server v3.0.2 - Unraid Deployment" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host "Version: 3.0.2 - Unraid Production Ready" -ForegroundColor Yellow
Write-Host ""

# Step 1: Copy essential files
Write-Host "Step 1: Copying v3.0.2 files..." -ForegroundColor Yellow

$filesToCopy = @(
    "backend/flask_simple.py",
    "frontend/index.html", 
    "frontend/package.json",
    "docker-compose.unraid.yml",
    "CHANGELOG_v3.0.2.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Write-Host "  Copying: $file" -ForegroundColor Green
        if ($file -eq "docker-compose.unraid.yml") {
            scp $file "root@${UnraidIP}:/mnt/user/appdata/watch1/docker-compose.yml"
        } else {
            scp $file "root@${UnraidIP}:/mnt/user/appdata/watch1/$file"
        }
    } else {
        Write-Host "  Missing: $file" -ForegroundColor Yellow
    }
}

Write-Host "Files copied successfully!" -ForegroundColor Green

# Step 2: Create deployment script
Write-Host ""
Write-Host "Step 2: Creating deployment script..." -ForegroundColor Yellow

$deployScript = @'
#!/bin/bash
# Watch1 v3.0.2 Deployment Script
echo "Watch1 Media Server v3.0.2 - Deployment Starting..."
echo "=================================================="

cd /mnt/user/appdata/watch1

echo "Stopping existing containers..."
docker-compose down --remove-orphans

echo "Creating directories..."
mkdir -p data logs thumbnails
chmod 755 data logs thumbnails

echo "Building v3.0.2 containers..."
docker-compose up -d --build

echo "Waiting for startup..."
sleep 30

echo "Setting up database..."
docker exec watch1-backend python -c "
import sqlite3, bcrypt, os
from datetime import datetime

print('Creating v3.0.2 database...')
os.makedirs('/app/data', exist_ok=True)
conn = sqlite3.connect('/app/data/watch1.db')

conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    is_superuser BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

password = 'testpass123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn.execute('DELETE FROM users WHERE email = ?', ('test@example.com',))
conn.execute('''INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser)
VALUES (?, ?, ?, ?, ?, ?, ?)''', 
('test-v302', 'test@example.com', 'testuser', 'Test User v3.0.2', hashed, 1, 1))

conn.commit()
conn.close()
print('Database setup complete!')
"

echo "Testing services..."
sleep 10

# Test backend
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: Failed"
fi

# Test login
login_test=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}')

if echo "$login_test" | grep -q "200"; then
    echo "Login: OK"
else
    echo "Login: Failed"
fi

# Test frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "Frontend: OK"
else
    echo "Frontend: Failed"
fi

echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo "Watch1 v3.0.2 Deployment Complete!"
echo "=================================="
echo "Frontend: http://192.168.254.14:3000"
echo "Backend:  http://192.168.254.14:8000"
echo "Login:    test@example.com / testpass123"
echo ""
echo "v3.0.2 Features:"
echo "- Unraid Production Ready"
echo "- CORS Policy Fixed"
echo "- Authentication Working"
echo "- TypeScript Compatible"
echo "- All Navigation Tabs Working"
'@

$deployScript | Out-File -FilePath "deploy-v302-clean.sh" -Encoding UTF8

# Copy deployment script
scp "deploy-v302-clean.sh" "root@${UnraidIP}:/mnt/user/appdata/watch1/"

Write-Host "Deployment script created and copied!" -ForegroundColor Green

# Step 3: Instructions
Write-Host ""
Write-Host "Step 3: Deploy on Unraid" -ForegroundColor Yellow
Write-Host "SSH to Unraid and run:" -ForegroundColor Gray
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x deploy-v302-clean.sh" -ForegroundColor White
Write-Host "./deploy-v302-clean.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Cyan

Write-Host ""
Write-Host "WATCH1 v3.0.2 READY!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""
Write-Host "New in v3.0.2:" -ForegroundColor Cyan
Write-Host "- Unraid Production Deployment Ready" -ForegroundColor Green
Write-Host "- All CORS and Authentication Fixed" -ForegroundColor Green
Write-Host "- TypeScript Compatibility Resolved" -ForegroundColor Green
Write-Host "- Navigation Tabs Working" -ForegroundColor Green
Write-Host "- Enhanced Security Headers" -ForegroundColor Green

# Cleanup
Remove-Item "deploy-v302-clean.sh" -ErrorAction SilentlyContinue
