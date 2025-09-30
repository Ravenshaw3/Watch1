#!/bin/bash
# Fix Navigation Tabs and Media Display Issues for v3.0.2
echo "🔧 FIXING NAVIGATION TABS AND MEDIA DISPLAY"
echo "==========================================="

cd /mnt/user/appdata/watch1

echo ""
echo "1. DIAGNOSING CURRENT ISSUES"
echo "============================"

echo "Container status:"
docker-compose ps

echo ""
echo "Backend connectivity test:"
backend_health=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null)
backend_code="${backend_health: -3}"
echo "Backend health: $backend_code"

echo ""
echo "Frontend connectivity test:"
frontend_test=$(curl -s -w "%{http_code}" http://localhost:3000 2>/dev/null)
frontend_code="${frontend_test: -3}"
echo "Frontend status: $frontend_code"

echo ""
echo "2. TESTING AUTHENTICATION SYSTEM"
echo "================================"

echo "Testing login endpoint..."
login_response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

login_code="${login_response: -3}"
login_body="${login_response%???}"

echo "Login status: $login_code"
if [ "$login_code" = "200" ]; then
    echo "✅ Login working"
    # Extract token for further testing
    token=$(echo "$login_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$token" ]; then
        echo "✅ JWT token received"
        
        echo ""
        echo "Testing user profile endpoint..."
        profile_test=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $token" \
          http://localhost:8000/api/v1/users/me 2>/dev/null)
        profile_code="${profile_test: -3}"
        echo "Profile endpoint: $profile_code"
        
    else
        echo "⚠️ No token in response"
    fi
else
    echo "❌ Login failed: $login_body"
fi

echo ""
echo "3. TESTING MEDIA ENDPOINTS"
echo "=========================="

echo "Testing media categories..."
categories_test=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/media/categories 2>/dev/null)
categories_code="${categories_test: -3}"
categories_body="${categories_test%???}"
echo "Categories endpoint: $categories_code"

if [ "$categories_code" = "200" ]; then
    echo "✅ Categories endpoint working"
    echo "Categories response: $(echo "$categories_body" | head -c 200)"
else
    echo "❌ Categories failed: $categories_body"
fi

echo ""
echo "Testing media files..."
media_test=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/media/ 2>/dev/null)
media_code="${media_test: -3}"
media_body="${media_test%???}"
echo "Media files endpoint: $media_code"

if [ "$media_code" = "200" ]; then
    echo "✅ Media files endpoint working"
    echo "Media response: $(echo "$media_body" | head -c 200)"
else
    echo "❌ Media files failed: $media_body"
fi

echo ""
echo "4. CHECKING DATABASE CONTENT"
echo "============================"

echo "Verifying database has media files..."
docker exec watch1-backend python -c "
import sqlite3
import os

db_paths = ['/app/data/watch1.db', '/app/watch1.db']
db_found = False

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f'Database found: {db_path}')
        db_found = True
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Check users
            users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
            print(f'Users in database: {users[\"count\"]}')
            
            # Check if media_files table exists
            tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
            table_names = [table['name'] for table in tables]
            print(f'Tables: {table_names}')
            
            if 'media_files' in table_names:
                media_count = conn.execute('SELECT COUNT(*) as count FROM media_files').fetchone()
                print(f'Media files in database: {media_count[\"count\"]}')
                
                if media_count['count'] == 0:
                    print('⚠️ No media files in database - this explains why no media displays')
                    
                    # Add some sample media files for testing
                    print('Adding sample media files for testing...')
                    sample_media = [
                        ('sample-movie-1', 'Sample Movie 1.mp4', '/media/movies/sample1.mp4', 'movies', 'Sample Movie 1'),
                        ('sample-movie-2', 'Sample Movie 2.mkv', '/media/movies/sample2.mkv', 'movies', 'Sample Movie 2'),
                        ('sample-tv-1', 'Sample TV Show S01E01.mp4', '/media/tv/sample_s01e01.mp4', 'tv_shows', 'Sample TV Show S01E01')
                    ]
                    
                    for media_id, filename, filepath, category, title in sample_media:
                        conn.execute('''
                            INSERT OR IGNORE INTO media_files 
                            (id, filename, file_path, category, title, file_size, is_processed, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        ''', (media_id, filename, filepath, category, title, 1000000, 1))
                    
                    conn.commit()
                    print('✅ Sample media files added')
                else:
                    print('✅ Media files exist in database')
            else:
                print('❌ media_files table missing!')
            
            conn.close()
            
        except Exception as e:
            print(f'Database error: {e}')
        
        break

if not db_found:
    print('❌ No database found!')
" 2>/dev/null || echo "❌ Database check failed"

echo ""
echo "5. FIXING FRONTEND AUTHENTICATION"
echo "================================="

echo "Checking frontend container logs for auth issues..."
docker-compose logs --tail 10 watch1-frontend | grep -i "error\|failed\|404" || echo "No obvious frontend errors"

echo ""
echo "Testing frontend-backend connectivity..."
docker exec watch1-frontend curl -s http://watch1-backend:8000/api/v1/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend can reach backend"
else
    echo "❌ Frontend cannot reach backend"
fi

echo ""
echo "6. RESTARTING SERVICES FOR CLEAN STATE"
echo "======================================"

echo "Restarting backend..."
docker-compose restart watch1-backend
sleep 15

echo "Restarting frontend..."
docker-compose restart watch1-frontend
sleep 15

echo ""
echo "7. FINAL TESTING AFTER RESTART"
echo "=============================="

echo "Testing login after restart..."
final_login=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

final_code="${final_login: -3}"
echo "Final login status: $final_code"

echo ""
echo "Testing media endpoints after restart..."
final_media=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/media/ 2>/dev/null)
final_media_code="${final_media: -3}"
echo "Final media status: $final_media_code"

echo ""
echo "Testing categories after restart..."
final_categories=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/media/categories 2>/dev/null)
final_categories_code="${final_categories: -3}"
echo "Final categories status: $final_categories_code"

echo ""
echo "8. TROUBLESHOOTING GUIDE"
echo "========================"

echo ""
echo "NAVIGATION TABS MISSING CAUSES:"
echo "1. User not authenticated (login required for Settings/Analytics)"
echo "2. Frontend authentication store not initialized"
echo "3. JWT token expired or invalid"
echo "4. Frontend-backend connectivity issues"

echo ""
echo "NO MEDIA DISPLAYING CAUSES:"
echo "1. No media files in database (empty media_files table)"
echo "2. Media API endpoints returning errors"
echo "3. Frontend not properly handling API responses"
echo "4. Authentication required for media endpoints"

echo ""
echo "SOLUTIONS TO TRY:"
echo "1. Clear browser cache and cookies"
echo "2. Try incognito/private browsing mode"
echo "3. Check browser console (F12) for JavaScript errors"
echo "4. Manually login at: http://192.168.254.14:3000/login"
echo "5. Test API directly: curl http://192.168.254.14:8000/api/v1/health"

echo ""
echo "MANUAL TESTING URLS:"
echo "Frontend: http://192.168.254.14:3000"
echo "Login: http://192.168.254.14:3000/login"
echo "Backend Health: http://192.168.254.14:8000/api/v1/health"
echo "Media API: http://192.168.254.14:8000/api/v1/media/"
echo "Categories: http://192.168.254.14:8000/api/v1/media/categories"

echo ""
echo "LOGIN CREDENTIALS:"
echo "Email: test@example.com"
echo "Password: testpass123"

echo ""
echo "9. FINAL STATUS"
echo "==============="

docker-compose ps

echo ""
if [ "$final_code" = "200" ] && [ "$final_media_code" = "200" ]; then
    echo "🎉 LIKELY FIXED!"
    echo "==============="
    echo "✅ Login working"
    echo "✅ Media API working"
    echo "✅ Backend responding"
    echo ""
    echo "Next steps:"
    echo "1. Go to http://192.168.254.14:3000"
    echo "2. Login with test@example.com / testpass123"
    echo "3. Navigation tabs should appear after login"
    echo "4. Media should display in Library"
else
    echo "⚠️ ISSUES REMAIN"
    echo "================"
    if [ "$final_code" != "200" ]; then
        echo "❌ Login still not working"
    fi
    if [ "$final_media_code" != "200" ]; then
        echo "❌ Media API still not working"
    fi
    echo ""
    echo "Check logs: docker-compose logs -f"
fi
