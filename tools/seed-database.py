#!/usr/bin/env python3
"""
Database seeding tool for Watch1 structured backend
Creates tables and initial data for development/testing
"""

import sys
import os
import hashlib
from datetime import datetime

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from postgres_config import get_db_connection
    print("✅ Database connection module loaded")
except ImportError as e:
    print(f"❌ Failed to import database module: {e}")
    sys.exit(1)

def create_tables():
    """Create all required database tables"""
    print("📋 Creating database tables...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_superuser BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Users table created")
        
        # Media files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id VARCHAR(255) PRIMARY KEY,
                filename VARCHAR(500) NOT NULL,
                file_path TEXT NOT NULL,
                file_size BIGINT,
                duration_seconds INTEGER,
                category VARCHAR(100),
                title VARCHAR(500),
                year INTEGER,
                rating DECIMAL(3,1),
                plot TEXT,
                director VARCHAR(255),
                genre VARCHAR(255),
                cast_list TEXT,
                runtime_minutes INTEGER,
                is_deleted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Media files table created")
        
        # Playlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                is_public BOOLEAN DEFAULT FALSE,
                owner_id INTEGER REFERENCES users(id),
                is_deleted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Playlists table created")
        
        # Playlist items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_items (
                id SERIAL PRIMARY KEY,
                playlist_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE,
                media_id VARCHAR(255) REFERENCES media_files(id),
                position INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Playlist items table created")
        
        conn.commit()
        print("✅ All tables created successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_test_user():
    """Create test user for development"""
    print("👤 Creating test user...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", ("test@example.com",))
        if cursor.fetchone():
            print("  ℹ️ Test user already exists")
            return
        
        # Create password hash (SHA256 to match existing system)
        password_hash = hashlib.sha256("testpass123".encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (email, password_hash, is_active, is_superuser)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, ("test@example.com", password_hash, True, True))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"  ✅ Test user created with ID: {user_id}")
        print(f"     Email: test@example.com")
        print(f"     Password: testpass123")
        print(f"     Superuser: Yes")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating test user: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_sample_media():
    """Create sample media entries for testing"""
    print("🎬 Creating sample media entries...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sample_movies = [
            {
                'id': 'sample_movie_1',
                'filename': 'The Matrix (1999).mkv',
                'file_path': '/app/media/movies/The Matrix (1999).mkv',
                'file_size': 2147483648,  # 2GB
                'duration_seconds': 8160,  # 2h 16m
                'category': 'movies',
                'title': 'The Matrix',
                'year': 1999,
                'rating': 8.7,
                'plot': 'A computer programmer discovers reality is a simulation.',
                'director': 'The Wachowskis',
                'genre': 'Action, Sci-Fi',
                'runtime_minutes': 136
            },
            {
                'id': 'sample_movie_2', 
                'filename': 'Inception (2010).mp4',
                'file_path': '/app/media/movies/Inception (2010).mp4',
                'file_size': 1610612736,  # 1.5GB
                'duration_seconds': 8880,  # 2h 28m
                'category': 'movies',
                'title': 'Inception',
                'year': 2010,
                'rating': 8.8,
                'plot': 'A thief enters dreams to plant ideas.',
                'director': 'Christopher Nolan',
                'genre': 'Action, Thriller, Sci-Fi',
                'runtime_minutes': 148
            },
            {
                'id': 'sample_tv_1',
                'filename': 'Breaking Bad S01E01.mkv',
                'file_path': '/app/media/tv/Breaking Bad/Season 1/Breaking Bad S01E01.mkv',
                'file_size': 1073741824,  # 1GB
                'duration_seconds': 2760,  # 46m
                'category': 'tv_shows',
                'title': 'Breaking Bad - Pilot',
                'year': 2008,
                'rating': 9.5,
                'plot': 'A chemistry teacher starts cooking meth.',
                'director': 'Vince Gilligan',
                'genre': 'Crime, Drama, Thriller',
                'runtime_minutes': 46
            }
        ]
        
        for movie in sample_movies:
            # Check if already exists
            cursor.execute("SELECT id FROM media_files WHERE id = %s", (movie['id'],))
            if cursor.fetchone():
                continue
                
            cursor.execute("""
                INSERT INTO media_files (
                    id, filename, file_path, file_size, duration_seconds, category,
                    title, year, rating, plot, director, genre, runtime_minutes
                ) VALUES (
                    %(id)s, %(filename)s, %(file_path)s, %(file_size)s, %(duration_seconds)s, %(category)s,
                    %(title)s, %(year)s, %(rating)s, %(plot)s, %(director)s, %(genre)s, %(runtime_minutes)s
                )
            """, movie)
        
        conn.commit()
        print(f"  ✅ Created {len(sample_movies)} sample media entries")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating sample media: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_sample_playlist():
    """Create a sample playlist"""
    print("📋 Creating sample playlist...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get test user ID
        cursor.execute("SELECT id FROM users WHERE email = %s", ("test@example.com",))
        user = cursor.fetchone()
        if not user:
            print("  ❌ Test user not found, skipping playlist creation")
            return
        
        user_id = user[0]
        
        # Check if playlist exists
        cursor.execute("SELECT id FROM playlists WHERE name = %s AND owner_id = %s", ("Favorites", user_id))
        if cursor.fetchone():
            print("  ℹ️ Sample playlist already exists")
            return
        
        # Create playlist
        cursor.execute("""
            INSERT INTO playlists (name, description, is_public, owner_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, ("Favorites", "My favorite movies and shows", True, user_id))
        
        playlist_id = cursor.fetchone()[0]
        
        # Add sample media to playlist
        cursor.execute("SELECT id FROM media_files LIMIT 2")
        media_files = cursor.fetchall()
        
        for i, media in enumerate(media_files):
            cursor.execute("""
                INSERT INTO playlist_items (playlist_id, media_id, position)
                VALUES (%s, %s, %s)
            """, (playlist_id, media[0], i + 1))
        
        conn.commit()
        print(f"  ✅ Sample playlist created with {len(media_files)} items")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating sample playlist: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Main seeding function"""
    print("🌱 Watch1 Database Seeding Tool")
    print("=" * 40)
    
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"📊 Connected to: {version}")
        cursor.close()
        conn.close()
        
        # Create schema and data
        create_tables()
        create_test_user()
        create_sample_media()
        create_sample_playlist()
        
        print("\n" + "=" * 40)
        print("✅ Database seeding completed successfully!")
        print("\n🔑 Login credentials:")
        print("   Email: test@example.com")
        print("   Password: testpass123")
        print("\n📊 Sample data created:")
        print("   - 3 media files (movies & TV)")
        print("   - 1 playlist with 2 items")
        
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
