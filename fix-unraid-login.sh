#!/bin/bash
# Fix Unraid Login Issues
# Run this on your Unraid server to fix login problems

echo "🔧 Fixing login issues on Unraid..."

cd /mnt/user/appdata/watch1

echo "📊 Checking current deployment status..."
docker-compose ps

echo ""
echo "🔍 Checking backend logs for errors..."
docker-compose logs --tail 20 watch1-backend

echo ""
echo "🗄️ Checking database status..."

# Check if database exists and has users
docker exec watch1-backend python -c "
import sqlite3
import os

# Check database paths
db_paths = ['/app/data/watch1.db', '/app/watch1.db', '/app/watch1_dev.db']
found_db = None

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f'✅ Database found at: {db_path}')
        found_db = db_path
        break
    else:
        print(f'❌ No database at: {db_path}')

if found_db:
    try:
        conn = sqlite3.connect(found_db)
        conn.row_factory = sqlite3.Row
        
        # Check users table
        users = conn.execute('SELECT * FROM users').fetchall()
        print(f'👥 Users in database: {len(users)}')
        
        if users:
            for user in users:
                print(f'   User: {user[\"email\"]} (Active: {user[\"is_active\"]})')
        else:
            print('⚠️ No users found in database!')
            
        conn.close()
    except Exception as e:
        print(f'❌ Database error: {e}')
else:
    print('❌ No database found!')
"

echo ""
echo "🔧 Creating test user if needed..."

# Create test user in database
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os
from datetime import datetime

# Find database
db_paths = ['/app/data/watch1.db', '/app/watch1.db']
db_path = None

for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    # Create new database
    db_path = '/app/data/watch1.db'
    print(f'📝 Creating new database at: {db_path}')

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Create users table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR,
            full_name VARCHAR,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if test user exists
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', ('test@example.com',)).fetchone()
    
    if not existing_user:
        # Create test user with bcrypt hash
        password = 'testpass123'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn.execute('''
            INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('test-user-id', 'test@example.com', 'testuser', 'Test User', hashed, 1, 1))
        
        conn.commit()
        print('✅ Created test user: test@example.com / testpass123')
    else:
        print('✅ Test user already exists')
    
    conn.close()
    print('✅ Database setup complete')
    
except Exception as e:
    print(f'❌ Database setup error: {e}')
"

echo ""
echo "🔄 Restarting backend to apply changes..."
docker-compose restart watch1-backend

echo ""
echo "⏳ Waiting for backend to start..."
sleep 10

echo ""
echo "🧪 Testing login API..."
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}' \
  2>/dev/null | python -m json.tool 2>/dev/null || echo "Login API test failed"

echo ""
echo "🎉 Login fix complete!"
echo ""
echo "📋 Try logging in again:"
echo "   URL: http://192.168.254.14:3000"
echo "   Email: test@example.com"
echo "   Password: testpass123"
echo ""
echo "📊 If still having issues, check logs:"
echo "   docker-compose logs -f watch1-backend"
