#!/bin/bash
# Debug 404 Login Error on Unraid
echo "🔍 DEBUGGING 404 LOGIN ERROR"
echo "============================="

cd /mnt/user/appdata/watch1

echo "1. CONTAINER STATUS"
echo "-------------------"
docker-compose ps
echo ""

echo "2. BACKEND CONTAINER LOGS"
echo "-------------------------"
docker-compose logs --tail 20 watch1-backend
echo ""

echo "3. TESTING BACKEND CONNECTIVITY"
echo "-------------------------------"
echo "Testing if backend is responding:"
curl -v http://localhost:8000/ 2>&1 | head -10
echo ""

echo "Testing health endpoint:"
curl -v http://localhost:8000/api/v1/health 2>&1 | head -10
echo ""

echo "4. TESTING LOGIN ENDPOINT DIRECTLY"
echo "----------------------------------"
echo "Testing login endpoint availability:"
curl -v -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}' 2>&1 | head -15
echo ""

echo "5. CHECKING FLASK ROUTES"
echo "------------------------"
echo "Checking what routes Flask has registered:"
docker exec watch1-backend python -c "
from flask_simple import app
print('Registered routes:')
for rule in app.url_map.iter_rules():
    print(f'{rule.rule} -> {rule.methods}')
" 2>/dev/null || echo "Could not check Flask routes"
echo ""

echo "6. CHECKING DATABASE"
echo "--------------------"
echo "Checking if database exists and has users:"
docker exec watch1-backend python -c "
import sqlite3
import os

db_paths = ['/app/data/watch1.db', '/app/watch1.db', '/app/watch1_dev.db']
for db_path in db_paths:
    if os.path.exists(db_path):
        print(f'Database found: {db_path}')
        try:
            conn = sqlite3.connect(db_path)
            users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            print(f'Users in database: {users}')
            conn.close()
        except Exception as e:
            print(f'Database error: {e}')
        break
else:
    print('No database found!')
" 2>/dev/null || echo "Could not check database"
echo ""

echo "7. CHECKING FLASK APP STARTUP"
echo "-----------------------------"
echo "Checking if Flask app started properly:"
docker exec watch1-backend ps aux | grep python || echo "No Python processes found"
echo ""

echo "8. NETWORK CONNECTIVITY"
echo "-----------------------"
echo "Testing internal network connectivity:"
docker exec watch1-frontend curl -s http://watch1-backend:8000/api/v1/health || echo "Frontend cannot reach backend"
echo ""

echo "🔧 SUGGESTED FIXES:"
echo "==================="
echo "If backend is not running:"
echo "  docker-compose restart watch1-backend"
echo ""
echo "If database is missing:"
echo "  ./fix-sqlite-login.sh"
echo ""
echo "If routes are not registered:"
echo "  docker-compose down && docker-compose up -d --build"
echo ""
echo "If network issues:"
echo "  Check docker network: docker network ls"
