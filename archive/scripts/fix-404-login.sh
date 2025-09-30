#!/bin/bash
# Fix 404 Login Error on Unraid
echo "🔧 Fixing 404 login error..."

cd /mnt/user/appdata/watch1

echo "1. CHECKING CURRENT STATUS"
echo "-------------------------"
docker-compose ps

echo ""
echo "2. RESTARTING BACKEND"
echo "--------------------"
echo "Stopping backend..."
docker-compose stop watch1-backend

echo "Starting backend..."
docker-compose up -d watch1-backend

echo "Waiting for backend to start..."
sleep 10

echo ""
echo "3. TESTING BACKEND HEALTH"
echo "-------------------------"
for i in {1..5}; do
    echo "Attempt $i:"
    if curl -s http://localhost:8000/api/v1/health > /dev/null; then
        echo "✅ Backend is responding!"
        break
    else
        echo "❌ Backend not responding, waiting..."
        sleep 5
    fi
done

echo ""
echo "4. CREATING/FIXING DATABASE"
echo "---------------------------"
echo "Ensuring database and user exist..."
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os

# Ensure data directory exists
os.makedirs('/app/data', exist_ok=True)

# Create/connect to database
db_path = '/app/data/watch1.db'
conn = sqlite3.connect(db_path)

# Create users table
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        username VARCHAR,
        full_name VARCHAR,
        hashed_password VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_superuser BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create test user
password = 'testpass123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn.execute('''
    INSERT OR REPLACE INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('test-user-123', 'test@example.com', 'testuser', 'Test User', hashed, 1, 1))

conn.commit()
conn.close()
print('✅ Database and user created/updated')
"

echo ""
echo "5. TESTING LOGIN ENDPOINT"
echo "------------------------"
echo "Testing login API:"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}')

http_code="${response: -3}"
response_body="${response%???}"

echo "HTTP Status: $http_code"
if [ "$http_code" = "200" ]; then
    echo "✅ Login working!"
    echo "Response: $response_body" | head -c 100
else
    echo "❌ Login failed with status $http_code"
    echo "Response: $response_body"
fi

echo ""
echo ""
echo "6. FINAL STATUS"
echo "--------------"
docker-compose ps

echo ""
echo "🎯 TRY LOGGING IN NOW:"
echo "======================"
echo "URL: http://192.168.254.14:3000"
echo "Email: test@example.com"
echo "Password: testpass123"
echo ""
echo "If still getting 404, check backend logs:"
echo "docker-compose logs -f watch1-backend"
