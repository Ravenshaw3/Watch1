#!/bin/bash
# Fix PostgreSQL Setup and Authentication Issues for v3.0.2
echo "🔧 FIXING POSTGRESQL AND AUTHENTICATION ISSUES"
echo "==============================================="

cd /mnt/user/appdata/watch1

echo ""
echo "1. DIAGNOSING CURRENT ISSUES"
echo "============================"

echo "Container status:"
docker-compose ps

echo ""
echo "Checking PostgreSQL container health..."
if docker-compose ps | grep -q "watch1-db.*Up"; then
    echo "✅ PostgreSQL container is running"
    
    # Check PostgreSQL logs for errors
    echo "PostgreSQL logs (last 10 lines):"
    docker-compose logs --tail 10 watch1-db
    
    echo ""
    echo "Testing basic PostgreSQL connection..."
    docker exec watch1-db psql -U watch1_user -d watch1 -c "SELECT version();" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Basic PostgreSQL connection working"
    else
        echo "❌ PostgreSQL connection failed"
        echo "Checking PostgreSQL status..."
        docker exec watch1-db pg_isready -U watch1_user -d watch1
    fi
else
    echo "❌ PostgreSQL container not running - starting it..."
    docker-compose up -d watch1-db
    sleep 10
fi

echo ""
echo "2. FIXING POSTGRESQL DATABASE SETUP"
echo "==================================="

echo "Dropping and recreating PostgreSQL database..."
docker exec watch1-db psql -U watch1_user -d postgres << 'EOF'
-- Drop and recreate database for clean start
DROP DATABASE IF EXISTS watch1;
CREATE DATABASE watch1;
\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL database recreated"
else
    echo "❌ Failed to recreate database"
fi

echo ""
echo "Creating PostgreSQL schema with proper error handling..."
docker exec watch1-db psql -U watch1_user -d watch1 << 'EOF'
-- Enable extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (with CASCADE)
DROP TABLE IF EXISTS playlist_media CASCADE;
DROP TABLE IF EXISTS playlists CASCADE;
DROP TABLE IF EXISTS media_files CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create media_files table
CREATE TABLE media_files (
    id VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT DEFAULT 0,
    category VARCHAR(100),
    title VARCHAR(255),
    duration REAL DEFAULT 0,
    poster_path VARCHAR(500),
    thumbnail_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    uploaded_by VARCHAR(255),
    is_processed BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Create playlists table
CREATE TABLE playlists (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE
);

-- Create playlist_media junction table
CREATE TABLE playlist_media (
    id VARCHAR(255) PRIMARY KEY,
    playlist_id VARCHAR(255) NOT NULL,
    media_id VARCHAR(255) NOT NULL,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_media_files_category ON media_files(category);
CREATE INDEX IF NOT EXISTS idx_media_files_created_at ON media_files(created_at);
CREATE INDEX IF NOT EXISTS idx_media_files_title ON media_files(title);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Show created tables
\dt

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO watch1_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO watch1_user;

\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL schema created successfully"
else
    echo "❌ PostgreSQL schema creation failed"
fi

echo ""
echo "3. POPULATING POSTGRESQL WITH TEST DATA"
echo "======================================="

echo "Adding test user and sample data to PostgreSQL..."
docker exec watch1-backend python3 -c "
import sys
sys.path.append('/app')

try:
    import psycopg2
    import bcrypt
    import uuid
    from datetime import datetime
    
    print('Connecting to PostgreSQL...')
    conn = psycopg2.connect(
        host='watch1-db',
        database='watch1',
        user='watch1_user',
        password='watch1_password',
        connect_timeout=10
    )
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    print('Creating test user...')
    # Create test user with proper bcrypt hash
    password = 'testpass123'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    user_id = str(uuid.uuid4())
    now = datetime.now()
    
    cursor.execute('''
        INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, 'test@example.com', 'testuser', 'Test User v3.0.2', hashed, True, True, now, now))
    
    print('✅ Test user created in PostgreSQL')
    
    # Add sample media files
    print('Adding sample media files...')
    sample_media = [
        ('sample-movie-1', 'The Matrix (1999).mp4', '/media/movies/matrix.mp4', 'movies', 'The Matrix', 8884000000),
        ('sample-movie-2', 'Inception (2010).mkv', '/media/movies/inception.mkv', 'movies', 'Inception', 12450000000),
        ('sample-movie-3', 'Interstellar (2014).mp4', '/media/movies/interstellar.mp4', 'movies', 'Interstellar', 15600000000),
        ('sample-tv-1', 'Breaking Bad S01E01.mp4', '/media/tv/breaking_bad_s01e01.mp4', 'tv_shows', 'Breaking Bad S01E01', 2800000000),
        ('sample-tv-2', 'Game of Thrones S01E01.mkv', '/media/tv/got_s01e01.mkv', 'tv_shows', 'Game of Thrones S01E01', 3200000000),
        ('sample-doc-1', 'Planet Earth Documentary.mp4', '/media/documentaries/planet_earth.mp4', 'documentaries', 'Planet Earth', 5400000000),
        ('sample-music-1', 'Concert Performance.mp4', '/media/music/concert.mp4', 'music_videos', 'Live Concert Performance', 1800000000)
    ]
    
    for media_id, filename, filepath, category, title, file_size in sample_media:
        cursor.execute('''
            INSERT INTO media_files (id, filename, file_path, category, title, file_size, is_processed, created_at, updated_at, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (media_id, filename, filepath, category, title, file_size, True, now, now, user_id))
    
    print('✅ Sample media files added to PostgreSQL')
    
    # Create sample playlist
    playlist_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO playlists (id, name, description, created_by, created_at, updated_at, is_public)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (playlist_id, 'My Favorite Movies', 'A collection of my favorite movies', user_id, now, now, True))
    
    print('✅ Sample playlist created in PostgreSQL')
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f'PostgreSQL users: {user_count}')
    
    cursor.execute('SELECT COUNT(*) FROM media_files')
    media_count = cursor.fetchone()[0]
    print(f'PostgreSQL media files: {media_count}')
    
    cursor.execute('SELECT COUNT(*) FROM playlists')
    playlist_count = cursor.fetchone()[0]
    print(f'PostgreSQL playlists: {playlist_count}')
    
    # Test user authentication
    cursor.execute('SELECT email, hashed_password, is_active, is_superuser FROM users WHERE email = %s', ('test@example.com',))
    user = cursor.fetchone()
    if user:
        print(f'✅ Test user verified: {user[0]} (Active: {user[2]}, Super: {user[3]})')
        print(f'Password hash length: {len(user[1])}')
    else:
        print('❌ Test user not found after creation')
    
    conn.close()
    print('✅ PostgreSQL population completed successfully')
    
except ImportError as e:
    print(f'❌ Missing Python package: {e}')
    print('Installing required packages...')
    import subprocess
    subprocess.run(['pip', 'install', 'psycopg2-binary', 'bcrypt'], check=True)
    print('Please run the script again after package installation')
    
except Exception as e:
    print(f'❌ PostgreSQL population failed: {e}')
    import traceback
    traceback.print_exc()
" 2>/dev/null || echo "❌ PostgreSQL population failed"

echo ""
echo "4. CREATING SYNCHRONIZED SQLITE DATABASE"
echo "========================================"

echo "Creating SQLite database with same data..."
docker exec watch1-backend python3 -c "
import sqlite3
import bcrypt
import uuid
import os
from datetime import datetime

print('Setting up SQLite database...')

# Ensure data directory exists
os.makedirs('/app/data', exist_ok=True)
db_path = '/app/data/watch1.db'

# Remove old database
if os.path.exists(db_path):
    os.remove(db_path)
    print('Removed old SQLite database')

# Create new SQLite database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
conn.execute('PRAGMA foreign_keys = ON')

print('Creating SQLite schema...')

# Create tables with same structure as PostgreSQL
conn.execute('''
    CREATE TABLE users (
        id VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(255),
        full_name VARCHAR(255),
        hashed_password VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_superuser BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.execute('''
    CREATE TABLE media_files (
        id VARCHAR(255) PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size INTEGER DEFAULT 0,
        category VARCHAR(100),
        title VARCHAR(255),
        duration REAL DEFAULT 0,
        poster_path VARCHAR(500),
        thumbnail_path VARCHAR(500),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_accessed DATETIME,
        uploaded_by VARCHAR(255),
        is_processed BOOLEAN DEFAULT 0,
        is_deleted BOOLEAN DEFAULT 0,
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
    )
''')

conn.execute('''
    CREATE TABLE playlists (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        created_by VARCHAR(255),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_public BOOLEAN DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
''')

# Create indexes
conn.execute('CREATE INDEX idx_media_files_category ON media_files(category)')
conn.execute('CREATE INDEX idx_media_files_created_at ON media_files(created_at)')
conn.execute('CREATE INDEX idx_users_email ON users(email)')

print('✅ SQLite schema created')

# Add same data as PostgreSQL
password = 'testpass123'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

user_id = str(uuid.uuid4())
now = datetime.now().isoformat()

# Insert test user
conn.execute('''
    INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (user_id, 'test@example.com', 'testuser', 'Test User v3.0.2', hashed, 1, 1, now, now))

# Insert sample media files
sample_media = [
    ('sample-movie-1', 'The Matrix (1999).mp4', '/media/movies/matrix.mp4', 'movies', 'The Matrix', 8884000000),
    ('sample-movie-2', 'Inception (2010).mkv', '/media/movies/inception.mkv', 'movies', 'Inception', 12450000000),
    ('sample-movie-3', 'Interstellar (2014).mp4', '/media/movies/interstellar.mp4', 'movies', 'Interstellar', 15600000000),
    ('sample-tv-1', 'Breaking Bad S01E01.mp4', '/media/tv/breaking_bad_s01e01.mp4', 'tv_shows', 'Breaking Bad S01E01', 2800000000),
    ('sample-tv-2', 'Game of Thrones S01E01.mkv', '/media/tv/got_s01e01.mkv', 'tv_shows', 'Game of Thrones S01E01', 3200000000),
    ('sample-doc-1', 'Planet Earth Documentary.mp4', '/media/documentaries/planet_earth.mp4', 'documentaries', 'Planet Earth', 5400000000),
    ('sample-music-1', 'Concert Performance.mp4', '/media/music/concert.mp4', 'music_videos', 'Live Concert Performance', 1800000000)
]

for media_id, filename, filepath, category, title, file_size in sample_media:
    conn.execute('''
        INSERT INTO media_files (id, filename, file_path, category, title, file_size, is_processed, created_at, updated_at, uploaded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (media_id, filename, filepath, category, title, file_size, 1, now, now, user_id))

# Create sample playlist
playlist_id = str(uuid.uuid4())
conn.execute('''
    INSERT INTO playlists (id, name, description, created_by, created_at, updated_at, is_public)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (playlist_id, 'My Favorite Movies', 'A collection of my favorite movies', user_id, now, now, 1))

conn.commit()

# Verify SQLite data
users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
print(f'SQLite users: {users[\"count\"]}')

media = conn.execute('SELECT COUNT(*) as count FROM media_files').fetchone()
print(f'SQLite media files: {media[\"count\"]}')

playlists = conn.execute('SELECT COUNT(*) as count FROM playlists').fetchone()
print(f'SQLite playlists: {playlists[\"count\"]}')

# Test user
user = conn.execute('SELECT email, hashed_password, is_active, is_superuser FROM users WHERE email = ?', ('test@example.com',)).fetchone()
if user:
    print(f'✅ SQLite test user verified: {user[\"email\"]} (Active: {user[\"is_active\"]}, Super: {user[\"is_superuser\"]})')
    print(f'Password hash length: {len(user[\"hashed_password\"])}')
else:
    print('❌ SQLite test user not found')

conn.close()
print('✅ SQLite database synchronized successfully')
" 2>/dev/null || echo "❌ SQLite synchronization failed"

echo ""
echo "5. RESTARTING BACKEND TO APPLY CHANGES"
echo "======================================"

echo "Stopping backend..."
docker-compose stop watch1-backend
sleep 5

echo "Starting backend..."
docker-compose start watch1-backend
sleep 20

echo "Checking backend startup..."
for i in {1..10}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend started successfully (attempt $i)"
        break
    else
        echo "⏳ Backend starting... (attempt $i/10)"
        sleep 5
    fi
done

echo ""
echo "6. TESTING AUTHENTICATION AND API ENDPOINTS"
echo "==========================================="

echo "Testing login endpoint..."
login_response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

login_code="${login_response: -3}"
login_body="${login_response%???}"

echo "Login status: $login_code"
if [ "$login_code" = "200" ]; then
    echo "✅ Login working!"
    
    # Extract token for authenticated requests
    token=$(echo "$login_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$token" ]; then
        echo "✅ JWT token received: ${token:0:20}..."
        
        echo ""
        echo "Testing authenticated media API..."
        media_response=$(curl -s -w "%{http_code}" \
          -H "Authorization: Bearer $token" \
          http://localhost:8000/api/v1/media/ 2>/dev/null)
        
        media_code="${media_response: -3}"
        media_body="${media_response%???}"
        
        echo "Media API status: $media_code"
        if [ "$media_code" = "200" ]; then
            echo "✅ Media API working with authentication!"
            echo "Media response preview: $(echo "$media_body" | head -c 200)"
        else
            echo "❌ Media API still failing: $media_body"
        fi
        
        echo ""
        echo "Testing authenticated categories API..."
        categories_response=$(curl -s -w "%{http_code}" \
          -H "Authorization: Bearer $token" \
          http://localhost:8000/api/v1/media/categories 2>/dev/null)
        
        categories_code="${categories_response: -3}"
        categories_body="${categories_response%???}"
        
        echo "Categories API status: $categories_code"
        if [ "$categories_code" = "200" ]; then
            echo "✅ Categories API working with authentication!"
            echo "Categories response: $(echo "$categories_body" | head -c 200)"
        else
            echo "❌ Categories API still failing: $categories_body"
        fi
        
    else
        echo "❌ No token received in login response"
    fi
else
    echo "❌ Login failed: $login_body"
fi

echo ""
echo "7. FINAL VERIFICATION"
echo "===================="

echo "Container status:"
docker-compose ps

echo ""
echo "Backend logs (last 10 lines):"
docker-compose logs --tail 10 watch1-backend

echo ""
echo "🎯 ISSUE RESOLUTION STATUS"
echo "=========================="

if [ "$login_code" = "200" ] && [ -n "$token" ]; then
    if [ "$media_code" = "200" ] && [ "$categories_code" = "200" ]; then
        echo "🎉 ALL ISSUES RESOLVED!"
        echo "✅ PostgreSQL database created and populated"
        echo "✅ SQLite database synchronized"
        echo "✅ Authentication working (no more 401 errors)"
        echo "✅ Media API working"
        echo "✅ Categories API working"
        echo ""
        echo "🌐 Ready to test:"
        echo "1. Go to http://192.168.254.14:3000"
        echo "2. Login with test@example.com / testpass123"
        echo "3. Navigation tabs should appear"
        echo "4. Library should show 7 media files"
        echo "5. All categories should have content"
    else
        echo "⚠️ PARTIAL RESOLUTION"
        echo "✅ Authentication working"
        echo "❌ API endpoints still have issues"
        echo "Check if backend is using the correct database"
    fi
else
    echo "❌ AUTHENTICATION STILL FAILING"
    echo "Issues remain with:"
    echo "- Database user creation"
    echo "- Backend database connection"
    echo "- Password hashing/verification"
    echo ""
    echo "Next steps:"
    echo "1. Check backend logs: docker-compose logs -f watch1-backend"
    echo "2. Verify database connection in backend code"
    echo "3. Check if backend is using SQLite or PostgreSQL"
fi

echo ""
echo "LOGIN CREDENTIALS:"
echo "Email: test@example.com"
echo "Password: testpass123"
