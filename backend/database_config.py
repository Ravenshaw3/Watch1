#!/usr/bin/env python3
"""
Global Database Configuration for Watch1 Media Server
Provides consistent database paths across all components
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

class DatabaseConfig:
    """Centralized database configuration and connection management"""
    
    def __init__(self):
        # Define database paths for each environment
        # PRIORITY: Use production database with existing data
        self.database_paths = {
            'development': [
                '/app/watch1.db',        # Production DB with data (priority)
                '/app/watch1_dev.db',    # Empty dev DB (fallback)
                './watch1.db',
                './watch1_dev.db',
                'watch1.db',
                'watch1_dev.db'
            ],
            'production': [
                '/app/data/watch1.db',
                '/data/watch1.db',
                '/app/watch1.db',
                './watch1.db',
                'watch1.db'
            ]
        }
        
        # Environment detection
        self.environment = self._detect_environment()
        
        # Find and set the active database path
        self.active_db_path = self._find_database_path()
        
        print(f"🔧 Database Config Initialized:")
        print(f"   Environment: {self.environment}")
        print(f"   Active DB Path: {self.active_db_path}")
    
    def _detect_environment(self) -> str:
        """Detect if we're in development or production"""
        # Check environment variables
        env = os.getenv('FLASK_ENV', os.getenv('ENVIRONMENT', 'development')).lower()
        
        # Check for development indicators
        if any([
            'dev' in env,
            'development' in env,
            os.path.exists('/app/watch1_dev.db'),
            os.path.exists('./watch1_dev.db')
        ]):
            return 'development'
        
        return 'production'
    
    def _find_database_path(self) -> str:
        """Find the first existing database or return the preferred path"""
        paths_to_check = self.database_paths[self.environment]
        
        # First, try to find existing database
        for db_path in paths_to_check:
            if os.path.exists(db_path):
                print(f"✅ Found existing database: {db_path}")
                return db_path
        
        # If no existing database found, return the first preferred path
        preferred_path = paths_to_check[0]
        print(f"📝 No existing database found, will use: {preferred_path}")
        return preferred_path
    
    def get_connection(self, row_factory: bool = True) -> sqlite3.Connection:
        """Get a database connection with consistent configuration"""
        try:
            # Ensure directory exists
            db_dir = os.path.dirname(self.active_db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Create connection
            conn = sqlite3.connect(self.active_db_path)
            
            # Set row factory for dict-like access
            if row_factory:
                conn.row_factory = sqlite3.Row
            
            # Enable foreign keys
            conn.execute('PRAGMA foreign_keys = ON')
            
            return conn
            
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            print(f"   Attempted path: {self.active_db_path}")
            raise
    
    def get_path(self) -> str:
        """Get the active database path"""
        return self.active_db_path
    
    def initialize_database(self) -> bool:
        """Initialize database with required tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if main tables exist
            tables_check = cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('users', 'media_files', 'playlists')
            """).fetchall()
            
            if len(tables_check) >= 3:
                print("✅ Database tables already exist")
                conn.close()
                return True
            
            # Create basic tables if they don't exist
            print("🔧 Creating database tables...")
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_superuser BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Media files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media_files (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    title TEXT,
                    file_path TEXT UNIQUE NOT NULL,
                    category TEXT,
                    file_size INTEGER,
                    duration INTEGER,
                    poster_path TEXT,
                    thumbnail_path TEXT,
                    poster_data BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0
                )
            """)
            
            # Playlists table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_public BOOLEAN DEFAULT 0,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """)
            
            # Playlist items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id TEXT NOT NULL,
                    media_id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
                    FOREIGN KEY (media_id) REFERENCES media_files (id) ON DELETE CASCADE,
                    UNIQUE(playlist_id, media_id)
                )
            """)
            
            # Create default admin user if none exists
            existing_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if existing_users == 0:
                print("👤 Creating default admin user...")
                import hashlib
                password_hash = hashlib.sha256("testpass123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, is_active, is_superuser)
                    VALUES ('admin-user-id', 'test@example.com', ?, 1, 1)
                """, (password_hash,))
            
            conn.commit()
            conn.close()
            
            print("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return False
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the current database"""
        if not backup_path:
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.active_db_path}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(self.active_db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise
    
    def get_database_info(self) -> dict:
        """Get information about the current database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get file size
            file_size = os.path.getsize(self.active_db_path) if os.path.exists(self.active_db_path) else 0
            
            # Get table counts
            tables = {}
            table_names = ['users', 'media_files', 'playlists', 'playlist_items']
            
            for table in table_names:
                try:
                    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    tables[table] = count
                except:
                    tables[table] = 0
            
            conn.close()
            
            return {
                'path': self.active_db_path,
                'environment': self.environment,
                'file_size': file_size,
                'exists': os.path.exists(self.active_db_path),
                'tables': tables,
                'readable': os.access(self.active_db_path, os.R_OK) if os.path.exists(self.active_db_path) else False,
                'writable': os.access(self.active_db_path, os.W_OK) if os.path.exists(self.active_db_path) else True
            }
            
        except Exception as e:
            return {
                'path': self.active_db_path,
                'environment': self.environment,
                'error': str(e)
            }

# Global database configuration instance
db_config = DatabaseConfig()

# Convenience functions for backward compatibility
def get_db_connection():
    """Get database connection - backward compatible function"""
    return db_config.get_connection()

def get_database_path():
    """Get the active database path"""
    return db_config.get_path()

def initialize_database():
    """Initialize the database with required tables"""
    return db_config.initialize_database()

# Auto-initialize database on import
if __name__ != "__main__":
    db_config.initialize_database()

if __name__ == "__main__":
    # Test the database configuration
    print("🧪 TESTING DATABASE CONFIGURATION")
    print("=" * 40)
    
    info = db_config.get_database_info()
    print(f"📊 Database Information:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test connection
    try:
        conn = db_config.get_connection()
        print("✅ Database connection successful")
        conn.close()
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
