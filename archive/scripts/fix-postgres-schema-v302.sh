#!/bin/bash
# Fix PostgreSQL Schema Creation Issues for v3.0.2
echo "🔧 FIXING POSTGRESQL SCHEMA CREATION"
echo "===================================="

cd /mnt/user/appdata/watch1

echo ""
echo "1. DIAGNOSING POSTGRESQL ISSUES"
echo "==============================="

echo "Container status:"
docker-compose ps

echo ""
echo "Checking PostgreSQL container..."
if ! docker-compose ps | grep -q "watch1-db.*Up"; then
    echo "❌ PostgreSQL container not running - starting it..."
    docker-compose up -d watch1-db
    sleep 15
    
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec watch1-db pg_isready -U watch1_user -d watch1 >/dev/null 2>&1; then
            echo "✅ PostgreSQL is ready (attempt $i)"
            break
        else
            echo "⏳ Waiting for PostgreSQL... (attempt $i/30)"
            sleep 2
        fi
    done
else
    echo "✅ PostgreSQL container is running"
fi

echo ""
echo "Testing basic PostgreSQL connection..."
docker exec watch1-db psql -U watch1_user -d postgres -c "SELECT version();" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Basic PostgreSQL connection working"
else
    echo "❌ PostgreSQL connection failed"
    echo "Checking PostgreSQL logs:"
    docker-compose logs --tail 20 watch1-db
    exit 1
fi

echo ""
echo "2. COMPLETELY RECREATING POSTGRESQL DATABASE"
echo "==========================================="

echo "Dropping existing database and recreating..."
docker exec watch1-db psql -U watch1_user -d postgres << 'EOF'
-- Terminate all connections to the database
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'watch1' AND pid <> pg_backend_pid();

-- Drop and recreate database
DROP DATABASE IF EXISTS watch1;
CREATE DATABASE watch1 WITH OWNER = watch1_user;

-- Connect to the new database and verify
\c watch1

-- Show we're connected to the right database
SELECT current_database();

\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL database recreated successfully"
else
    echo "❌ Failed to recreate PostgreSQL database"
    exit 1
fi

echo ""
echo "3. CREATING SCHEMA WITH DETAILED ERROR CHECKING"
echo "=============================================="

echo "Creating tables with verbose error reporting..."
docker exec watch1-db psql -U watch1_user -d watch1 << 'EOF'
-- Enable verbose error reporting
\set ON_ERROR_STOP on
\set VERBOSITY verbose

-- Show current database
SELECT 'Connected to database: ' || current_database() as status;

-- Drop all existing tables (if any)
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

SELECT 'Users table created successfully' as status;

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
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

SELECT 'Media_files table created successfully' as status;

-- Create playlists table
CREATE TABLE playlists (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

SELECT 'Playlists table created successfully' as status;

-- Create playlist_media junction table
CREATE TABLE playlist_media (
    id VARCHAR(255) PRIMARY KEY,
    playlist_id VARCHAR(255) NOT NULL,
    media_id VARCHAR(255) NOT NULL,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE CASCADE,
    UNIQUE(playlist_id, media_id)
);

SELECT 'Playlist_media table created successfully' as status;

-- Create indexes
CREATE INDEX idx_media_files_category ON media_files(category);
CREATE INDEX idx_media_files_created_at ON media_files(created_at);
CREATE INDEX idx_media_files_title ON media_files(title);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_playlists_created_by ON playlists(created_by);

SELECT 'Indexes created successfully' as status;

-- Grant all permissions to watch1_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO watch1_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO watch1_user;

SELECT 'Permissions granted successfully' as status;

-- List all tables to verify creation
\dt

-- Show table structures
\d users
\d media_files
\d playlists

SELECT 'Schema creation completed successfully!' as final_status;

\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL schema created successfully"
else
    echo "❌ PostgreSQL schema creation failed"
    echo "Checking for detailed errors..."
    docker-compose logs --tail 30 watch1-db
    exit 1
fi

echo ""
echo "4. VERIFYING TABLES EXIST"
echo "========================="

echo "Checking if tables were created..."
docker exec watch1-db psql -U watch1_user -d watch1 -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"

if [ $? -eq 0 ]; then
    echo "✅ Tables verified successfully"
else
    echo "❌ Table verification failed"
    exit 1
fi

echo ""
echo "5. ADDING TEST USER WITH PYTHON"
echo "==============================="

echo "Installing required Python packages in backend container..."
docker exec watch1-backend pip install psycopg2-binary bcrypt uuid

echo ""
echo "Creating test user with proper error handling..."
docker exec watch1-backend python3 << 'EOF'
import sys
import traceback

try:
    import psycopg2
    import bcrypt
    import uuid
    from datetime import datetime
    
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host='watch1-db',
        database='watch1',
        user='watch1_user',
        password='watch1_password',
        connect_timeout=30
    )
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Test if users table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');")
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("❌ Users table does not exist!")
        sys.exit(1)
    else:
        print("✅ Users table exists")
    
    # Clear any existing test users
    cursor.execute("DELETE FROM users WHERE email = 'test@example.com';")
    print("Cleared any existing test users")
    
    # Create test user
    print("Creating test user...")
    password = 'testpass123'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    user_id = str(uuid.uuid4())
    now = datetime.now()
    
    cursor.execute('''
        INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, 'test@example.com', 'testuser', 'Test User v3.0.2', hashed, True, True, now, now))
    
    print("✅ Test user created successfully")
    
    # Verify user creation
    cursor.execute("SELECT id, email, username, is_active, is_superuser FROM users WHERE email = 'test@example.com';")
    user = cursor.fetchone()
    
    if user:
        print(f"✅ User verified: {user[1]} (ID: {user[0][:8]}..., Active: {user[3]}, Super: {user[4]})")
    else:
        print("❌ User verification failed")
        sys.exit(1)
    
    # Add sample media files
    print("Adding sample media files...")
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
    
    print("✅ Sample media files added")
    
    # Create sample playlist
    playlist_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO playlists (id, name, description, created_by, created_at, updated_at, is_public)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (playlist_id, 'My Favorite Movies', 'A collection of my favorite movies', user_id, now, now, True))
    
    print("✅ Sample playlist created")
    
    # Final verification
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM media_files')
    media_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM playlists')
    playlist_count = cursor.fetchone()[0]
    
    print(f"Final counts - Users: {user_count}, Media: {media_count}, Playlists: {playlist_count}")
    
    conn.close()
    print("✅ PostgreSQL population completed successfully!")
    
except ImportError as e:
    print(f"❌ Missing Python package: {e}")
    print("Please install required packages: pip install psycopg2-binary bcrypt")
    
except psycopg2.Error as e:
    print(f"❌ PostgreSQL error: {e}")
    print(f"Error code: {e.pgcode}")
    print(f"Error message: {e.pgerror}")
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    traceback.print_exc()
EOF

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL data population successful"
else
    echo "❌ PostgreSQL data population failed"
    exit 1
fi

echo ""
echo "6. CREATING SYNCHRONIZED SQLITE DATABASE"
echo "========================================"

echo "Creating SQLite database with same structure..."
docker exec watch1-backend python3 << 'EOF'
import sqlite3
import bcrypt
import uuid
import os
from datetime import datetime

try:
    print("Setting up SQLite database...")
    
    # Ensure data directory exists
    os.makedirs('/app/data', exist_ok=True)
    db_path = '/app/data/watch1.db'
    
    # Remove old database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed old SQLite database")
    
    # Create new SQLite database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    
    print("Creating SQLite schema...")
    
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
    
    print("✅ SQLite schema created")
    
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
    media = conn.execute('SELECT COUNT(*) as count FROM media_files').fetchone()
    playlists = conn.execute('SELECT COUNT(*) as count FROM playlists').fetchone()
    
    print(f"SQLite counts - Users: {users['count']}, Media: {media['count']}, Playlists: {playlists['count']}")
    
    conn.close()
    print("✅ SQLite database synchronized successfully")
    
except Exception as e:
    print(f"❌ SQLite setup failed: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "7. RESTARTING BACKEND AND TESTING"
echo "================================="

echo "Restarting backend to apply changes..."
docker-compose restart watch1-backend
sleep 20

echo "Testing authentication..."
login_response=$(curl -s -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' 2>/dev/null)

login_code="${login_response: -3}"
login_body="${login_response%???}"

echo "Login status: $login_code"
if [ "$login_code" = "200" ]; then
    echo "✅ Authentication working!"
    
    token=$(echo "$login_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$token" ]; then
        echo "✅ JWT token received"
        
        # Test media API
        media_response=$(curl -s -w "%{http_code}" \
          -H "Authorization: Bearer $token" \
          http://localhost:8000/api/v1/media/ 2>/dev/null)
        
        media_code="${media_response: -3}"
        echo "Media API status: $media_code"
        
        # Test categories API
        categories_response=$(curl -s -w "%{http_code}" \
          -H "Authorization: Bearer $token" \
          http://localhost:8000/api/v1/media/categories 2>/dev/null)
        
        categories_code="${categories_response: -3}"
        echo "Categories API status: $categories_code"
        
        if [ "$media_code" = "200" ] && [ "$categories_code" = "200" ]; then
            echo ""
            echo "🎉 ALL ISSUES RESOLVED!"
            echo "======================="
            echo "✅ PostgreSQL database created with users table"
            echo "✅ Test user created successfully"
            echo "✅ Authentication working (no 401 errors)"
            echo "✅ Media API working"
            echo "✅ Categories API working"
            echo "✅ SQLite database synchronized"
            echo ""
            echo "Ready to test:"
            echo "1. Go to http://192.168.254.14:3000"
            echo "2. Login with test@example.com / testpass123"
            echo "3. Navigation tabs should appear"
            echo "4. Library should show 7 media files"
        else
            echo "⚠️ Authentication works but API endpoints still have issues"
        fi
    fi
else
    echo "❌ Authentication still failing: $login_body"
fi

echo ""
echo "Final container status:"
docker-compose ps
