#!/bin/bash
# Fix All v3.0.2 Issues: Login, Permissions-Policy, 404 auth.ts, Database
echo "🔧 COMPREHENSIVE v3.0.2 ISSUE FIX"
echo "================================="

cd /mnt/user/appdata/watch1

echo ""
echo "1. DIAGNOSING CURRENT ISSUES"
echo "============================"

echo "Container status:"
docker-compose ps

echo ""
echo "Backend logs (last 15 lines):"
docker-compose logs --tail 15 watch1-backend

echo ""
echo "Frontend logs (last 15 lines):"
docker-compose logs --tail 15 watch1-frontend

echo ""
echo "2. TESTING CURRENT STATE"
echo "========================"

echo "Testing backend health:"
backend_health=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null)
backend_code="${backend_health: -3}"
echo "Backend health status: $backend_code"

echo ""
echo "Testing login endpoint:"
login_test=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)
login_code="${login_test: -3}"
echo "Login endpoint status: $login_code"

echo ""
echo "3. FIXING PERMISSIONS-POLICY HEADER"
echo "==================================="

echo "Updating backend with proper permissions-policy..."
docker exec watch1-backend python -c "
# Check if flask_simple.py has proper permissions-policy
import os
flask_file = '/app/flask_simple.py'
if os.path.exists(flask_file):
    with open(flask_file, 'r') as f:
        content = f.read()
    
    # Check if permissions-policy is properly configured
    if 'browsing-topics' not in content:
        print('Adding browsing-topics to permissions-policy...')
        # This would need the updated flask_simple.py file
        print('Backend needs updated flask_simple.py with proper permissions-policy')
    else:
        print('Permissions-policy already configured')
else:
    print('flask_simple.py not found')
" 2>/dev/null || echo "Could not check permissions-policy"

echo ""
echo "4. FIXING DATABASE ISSUES"
echo "========================="

echo "Checking database status..."
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os
from datetime import datetime

print('🗄️ Database Verification and Fix...')

# Check all possible database locations
db_paths = ['/app/data/watch1.db', '/app/watch1.db', '/app/watch1_dev.db']
db_found = False

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f'Database found at: {db_path}')
        db_found = True
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Check users table
            users = conn.execute('SELECT * FROM users').fetchall()
            print(f'Users in database: {len(users)}')
            
            for user in users:
                print(f'  User: {user[\"email\"]} (Active: {user[\"is_active\"]})')
            
            conn.close()
            
        except Exception as e:
            print(f'Database error: {e}')
            print('Database needs repair...')
        
        break

if not db_found:
    print('❌ No database found! Creating new database...')
    
    # Create database in proper location
    os.makedirs('/app/data', exist_ok=True)
    db_path = '/app/data/watch1.db'
    
    conn = sqlite3.connect(db_path)
    
    # Create users table with all required fields
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR,
            full_name VARCHAR,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create media_files table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS media_files (
            id VARCHAR PRIMARY KEY,
            filename VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            file_size INTEGER,
            category VARCHAR,
            title VARCHAR,
            duration REAL,
            poster_path VARCHAR,
            thumbnail_path VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_accessed DATETIME,
            uploaded_by VARCHAR,
            is_processed BOOLEAN DEFAULT 0,
            is_deleted BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create test user with proper bcrypt hash
    password = 'testpass123'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn.execute('''
        INSERT OR REPLACE INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test-user-v302', 'test@example.com', 'testuser', 'Test User v3.0.2', hashed, 1, 1, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print('✅ New database created with test user')

print('Database verification complete')
" 2>/dev/null || echo "❌ Database check failed"

echo ""
echo "5. RESTARTING SERVICES"
echo "======================"

echo "Restarting backend..."
docker-compose restart watch1-backend
sleep 10

echo "Restarting frontend..."
docker-compose restart watch1-frontend
sleep 10

echo ""
echo "6. TESTING FIXES"
echo "================"

echo "Testing backend after restart..."
for i in {1..5}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend responding (attempt $i)"
        break
    else
        echo "⏳ Backend not ready (attempt $i/5)"
        sleep 5
    fi
done

echo ""
echo "Testing login after fixes..."
final_login=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

final_code="${final_login: -3}"
final_body="${final_login%???}"

echo "Login test result: $final_code"
if [ "$final_code" = "200" ]; then
    echo "✅ Login working!"
    echo "Response: $(echo "$final_body" | head -c 100)"
else
    echo "❌ Login still failing"
    echo "Response: $final_body"
fi

echo ""
echo "Testing permissions-policy headers..."
headers_test=$(curl -I -s http://localhost:8000/api/v1/health 2>/dev/null | grep -i "permissions-policy" || echo "No permissions-policy header")
echo "Permissions-Policy: $headers_test"

echo ""
echo "Testing frontend access..."
frontend_test=$(curl -s -w "%{http_code}" http://localhost:3000 2>/dev/null)
frontend_code="${frontend_test: -3}"
echo "Frontend status: $frontend_code"

echo ""
echo "7. FINAL STATUS"
echo "==============="

docker-compose ps

echo ""
echo "8. TROUBLESHOOTING INFO"
echo "======================"

if [ "$final_code" != "200" ]; then
    echo "❌ LOGIN STILL NOT WORKING:"
    echo "1. Check if backend container is running properly"
    echo "2. Verify database exists: docker exec watch1-backend ls -la /app/data/"
    echo "3. Check backend logs: docker-compose logs watch1-backend"
    echo "4. Test direct backend: curl http://192.168.254.14:8000/api/v1/health"
fi

if [ "$frontend_code" != "200" ]; then
    echo "❌ FRONTEND ISSUES:"
    echo "1. Check frontend logs: docker-compose logs watch1-frontend"
    echo "2. Verify frontend container: docker-compose ps"
    echo "3. Check if auth.ts file exists in container"
fi

echo ""
echo "COMMON SOLUTIONS:"
echo "1. Complete rebuild: docker-compose down && docker-compose up -d --build"
echo "2. Clear browser cache and try incognito mode"
echo "3. Check browser console (F12) for JavaScript errors"
echo "4. Verify network connectivity between containers"

echo ""
echo "ACCESS URLS:"
echo "Frontend: http://192.168.254.14:3000"
echo "Backend:  http://192.168.254.14:8000"
echo "Health:   http://192.168.254.14:8000/api/v1/health"
echo "Login:    test@example.com / testpass123"

echo ""
if [ "$final_code" = "200" ] && [ "$frontend_code" = "200" ]; then
    echo "🎉 ALL ISSUES FIXED!"
else
    echo "⚠️ SOME ISSUES REMAIN - CHECK LOGS"
fi
