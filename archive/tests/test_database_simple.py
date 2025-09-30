#!/usr/bin/env python3
"""
Simple database test to check structure and add titles
"""

import sqlite3
import os

def test_database():
    print("TESTING DATABASE STRUCTURE")
    print("=" * 30)
    
    # Connect to database
    conn = sqlite3.connect('/app/watch1_dev.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check table structure
    cursor.execute("PRAGMA table_info(media_files)")
    columns = cursor.fetchall()
    
    print("Media files table columns:")
    for col in columns:
        print(f"  {col['name']}: {col['type']}")
    
    # Check if we have data
    cursor.execute("SELECT COUNT(*) FROM media_files")
    count = cursor.fetchone()[0]
    print(f"\nTotal media files: {count}")
    
    # Get a few sample records
    cursor.execute("SELECT id, filename, file_path FROM media_files LIMIT 3")
    samples = cursor.fetchall()
    
    print(f"\nSample records:")
    for sample in samples:
        print(f"  ID: {sample['id']}")
        print(f"  Filename: {sample['filename']}")
        print(f"  Path: {sample['file_path']}")
        print()
    
    # Try to add title column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE media_files ADD COLUMN title TEXT")
        print("✅ Added title column")
    except sqlite3.OperationalError as e:
        print(f"ℹ️  Title column: {e}")
    
    # Update a few records with proper titles
    print("\nUpdating titles for first 3 records...")
    for sample in samples:
        # Simple title extraction
        title = sample['filename']
        if title.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            title = title.rsplit('.', 1)[0]
        
        cursor.execute("UPDATE media_files SET title = ? WHERE id = ?", (title, sample['id']))
        print(f"  Updated: {title}")
    
    conn.commit()
    conn.close()
    print("✅ Database test completed")

if __name__ == "__main__":
    test_database()
