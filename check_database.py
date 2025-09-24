#!/usr/bin/env python3
"""
Quick database check to see if our data is still there
"""

import sqlite3
import os

def check_database():
    db_path = 'backend/watch1.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print(f"✅ Database file exists: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📋 Tables in database ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n📊 Record counts:")
        
        # Check each table
        table_counts = {}
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_counts[table_name] = count
                print(f"  {table_name}: {count} records")
            except Exception as e:
                print(f"  {table_name}: Error - {e}")
        
        # Check specific important data
        print("\n🔍 Detailed checks:")
        
        # Check users
        if 'users' in table_counts:
            cursor.execute("SELECT email FROM users LIMIT 3")
            users = cursor.fetchall()
            print(f"  Users: {[user[0] for user in users]}")
        
        # Check media sample
        if 'media' in table_counts and table_counts['media'] > 0:
            cursor.execute("SELECT original_filename FROM media LIMIT 3")
            media = cursor.fetchall()
            print(f"  Sample media: {[m[0] for m in media]}")
        
        # Check settings
        if 'settings' in table_counts:
            cursor.execute("SELECT key, value FROM settings LIMIT 5")
            settings = cursor.fetchall()
            print(f"  Sample settings: {dict(settings)}")
        
        conn.close()
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"  Total media files: {table_counts.get('media', 0)}")
        print(f"  Total playlists: {table_counts.get('playlists', 0)}")
        print(f"  Total users: {table_counts.get('users', 0)}")
        
        if table_counts.get('media', 0) > 0:
            print("✅ Your data is still there!")
        else:
            print("⚠️  No media data found - might need to rescan")
            
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()
