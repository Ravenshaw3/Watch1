#!/bin/bash
# Fix Missing Navigation Tabs and Login Issues
echo "🔧 Fixing missing navigation tabs and login..."

cd /mnt/user/appdata/watch1

echo "1. CHECKING CURRENT STATUS"
echo "========================="
docker-compose ps
echo ""

echo "2. CHECKING BACKEND LOGS"
echo "========================"
echo "Backend logs (last 20 lines):"
docker-compose logs --tail 20 watch1-backend
echo ""

echo "3. CHECKING FRONTEND LOGS"
echo "========================="
echo "Frontend logs (last 20 lines):"
docker-compose logs --tail 20 watch1-frontend
echo ""

echo "4. TESTING BACKEND ENDPOINTS"
echo "============================"
echo "Testing health endpoint:"
curl -s http://localhost:8000/api/v1/health || echo "❌ Health endpoint failed"

echo ""
echo "Testing login endpoint:"
login_response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

http_code="${login_response: -3}"
response_body="${login_response%???}"

echo "Login HTTP Status: $http_code"
if [ "$http_code" = "200" ]; then
    echo "✅ Login API working"
else
    echo "❌ Login API failed: $response_body"
fi

echo ""
echo "5. CHECKING FRONTEND CONNECTIVITY"
echo "================================="
echo "Testing frontend access:"
frontend_status=$(curl -s -w "%{http_code}" http://localhost:3000 2>/dev/null)
frontend_code="${frontend_status: -3}"

if [ "$frontend_code" = "200" ]; then
    echo "✅ Frontend accessible"
else
    echo "❌ Frontend not accessible (Status: $frontend_code)"
fi

echo ""
echo "Testing frontend-backend connection:"
docker exec watch1-frontend curl -s http://watch1-backend:8000/api/v1/health || echo "❌ Frontend cannot reach backend"

echo ""
echo "6. FIXING ISSUES"
echo "================"

echo "Restarting backend with proper configuration..."
docker-compose restart watch1-backend
sleep 10

echo "Ensuring database exists with proper user..."
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os

print('Checking/creating database...')
os.makedirs('/app/data', exist_ok=True)
db_path = '/app/data/watch1.db'

try:
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
            is_superuser BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if user exists
    user = conn.execute('SELECT * FROM users WHERE email = ?', ('test@example.com',)).fetchone()
    
    if not user:
        print('Creating test user...')
        password = 'testpass123'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn.execute('''
            INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('test-user', 'test@example.com', 'testuser', 'Test User', hashed, 1, 1))
        
        conn.commit()
        print('✅ Test user created')
    else:
        print('✅ Test user already exists')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Database error: {e}')
" 2>/dev/null || echo "❌ Database setup failed"

echo ""
echo "Restarting frontend..."
docker-compose restart watch1-frontend
sleep 15

echo ""
echo "7. FINAL TESTING"
echo "================"

echo "Testing login after fixes:"
final_login=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

final_code="${final_login: -3}"
final_body="${final_login%???}"

echo "Final login status: $final_code"
if [ "$final_code" = "200" ]; then
    echo "✅ Login working!"
    echo "Token received: $(echo "$final_body" | grep -o "access_token" || echo "Token found")"
else
    echo "❌ Login still failing: $final_body"
fi

echo ""
echo "Container status:"
docker-compose ps

echo ""
echo "8. TROUBLESHOOTING INFO"
echo "======================"
echo "If navigation tabs are still missing:"
echo "1. Clear browser cache completely"
echo "2. Try incognito/private browsing mode"
echo "3. Check browser console (F12) for JavaScript errors"
echo ""
echo "If login still fails:"
echo "1. Check backend logs: docker-compose logs -f watch1-backend"
echo "2. Verify database: docker exec watch1-backend ls -la /app/data/"
echo "3. Test direct API: curl http://192.168.254.14:8000/api/v1/health"
echo ""
echo "Access URLs:"
echo "Frontend: http://192.168.254.14:3000"
echo "Backend:  http://192.168.254.14:8000"
echo "Login:    test@example.com / testpass123"
