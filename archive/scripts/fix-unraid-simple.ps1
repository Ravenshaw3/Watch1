# Simple Unraid Fix Script - Working Version
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "🚀 Simple Unraid Fix Script" -ForegroundColor Green
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan

# Step 1: Copy essential files
Write-Host "📤 Copying files..." -ForegroundColor Yellow

scp backend/flask_simple.py root@${UnraidIP}:/mnt/user/appdata/watch1/backend/
scp frontend/index.html root@${UnraidIP}:/mnt/user/appdata/watch1/frontend/
scp docker-compose.unraid.yml root@${UnraidIP}:/mnt/user/appdata/watch1/docker-compose.yml

Write-Host "✅ Files copied!" -ForegroundColor Green

# Step 2: Create simple fix script
$fixScript = @'
#!/bin/bash
echo "🔧 Fixing Unraid Watch1..."
cd /mnt/user/appdata/watch1

echo "Stopping containers..."
docker-compose down

echo "Creating directories..."
mkdir -p data logs thumbnails

echo "Rebuilding containers..."
docker-compose up -d --build

echo "Waiting for startup..."
sleep 30

echo "Creating database and user..."
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os

os.makedirs('/app/data', exist_ok=True)
db_path = '/app/data/watch1.db'
conn = sqlite3.connect(db_path)

conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        username VARCHAR,
        full_name VARCHAR,
        hashed_password VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_superuser BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

password = 'testpass123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn.execute('DELETE FROM users WHERE email = ?', ('test@example.com',))
conn.execute('''
    INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('test-user', 'test@example.com', 'testuser', 'Test User', hashed, 1, 1))

conn.commit()
conn.close()
print('Database setup complete')
"

echo "Testing login..."
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}'

echo ""
echo "✅ Fix complete!"
echo "Frontend: http://192.168.254.14:3000"
echo "Login: test@example.com / testpass123"
'@

$fixScript | Out-File -FilePath "simple-fix.sh" -Encoding UTF8

scp simple-fix.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "✅ Fix script copied!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Now SSH to Unraid and run:" -ForegroundColor Yellow
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x simple-fix.sh" -ForegroundColor White
Write-Host "./simple-fix.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Cyan

Remove-Item "simple-fix.sh" -ErrorAction SilentlyContinue
