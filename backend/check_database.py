#!/usr/bin/env python3
"""
Database checker for Watch1 media server
"""

import sqlite3
import os

def check_database(db_path='watch1.db'):
    print(f"🔍 Checking database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check media_files table
        if any('media_files' in table for table in tables):
            cursor.execute("SELECT COUNT(*) FROM media_files")
            count = cursor.fetchone()[0]
            print(f"📁 Media files: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, original_filename FROM media_files LIMIT 5")
                samples = cursor.fetchall()
                print("📄 Sample files:")
                for sample in samples:
                    print(f"   - ID: {sample[0]}, File: {sample[1]}")
            else:
                print("⚠️  No media files found in database")
        else:
            print("❌ media_files table not found")
        
        # Check users table
        if any('users' in table for table in tables):
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Users: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, email FROM users LIMIT 3")
                users = cursor.fetchall()
                print("👤 Sample users:")
                for user in users:
                    print(f"   - ID: {user[0]}, Email: {user[1]}")
        
        conn.close()
        return count > 0 if 'count' in locals() else True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Watch1 Database Checker")
    print("=" * 30)
    
    # Check both database files
    for db_file in ['watch1.db', 'watch1_dev.db']:
        if os.path.exists(db_file):
            print(f"\n📂 Checking {db_file}:")
            check_database(db_file)
        else:
            print(f"\n📂 {db_file}: Not found")
    
    print("\n✅ Database check complete!")
