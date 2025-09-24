#!/bin/bash
# Fix SQLite Login on Unraid
echo "🔧 Fixing SQLite login on Unraid..."

cd /mnt/user/appdata/watch1

# Check backend logs first
echo "📊 Backend logs:"
docker-compose logs --tail 10 watch1-backend

# Copy your working database from development
echo "📋 Do you want to:"
echo "1. Create fresh database with test user"
echo "2. Copy database from development environment"

# Create fresh database with test user
echo "🗄️ Creating fresh database..."
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os

db_path = '/app/data/watch1.db'
os.makedirs('/app/data', exist_ok=True)

conn = sqlite3.connect(db_path)
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
print('✅ Database created with test user')
"

echo "🔄 Restarting backend..."
docker-compose restart watch1-backend

echo "⏳ Waiting for restart..."
sleep 5

echo "🧪 Testing login..."
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null

echo ""
echo "✅ Try logging in at: http://192.168.254.14:3000"
echo "📧 Email: test@example.com"
echo "🔑 Password: testpass123"
