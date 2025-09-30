#!/usr/bin/env python3
"""
Live Media Scanner for Watch1
Scans actual media directories and populates database with real files
"""

import os
import sqlite3
import hashlib
from pathlib import Path
import mimetypes

def get_file_id(file_path):
    """Generate unique ID for file based on path"""
    return hashlib.md5(str(file_path).encode()).hexdigest()[:22]

def get_category_from_path(file_path):
    """Determine category based on file path"""
    path_lower = str(file_path).lower()
    
    if any(x in path_lower for x in ['movie', 'film', 'cinema']):
        return 'movies'
    elif any(x in path_lower for x in ['tv', 'series', 'show', 'episode']):
        return 'tv_shows'
    elif any(x in path_lower for x in ['kid', 'child', 'family', 'disney', 'cartoon']):
        return 'kids'
    elif any(x in path_lower for x in ['music', 'song', 'audio', 'mp3', 'flac']):
        return 'music'
    else:
        return 'videos'

def scan_live_media():
    """Scan for live media files and populate database"""
    print("LIVE MEDIA SCANNER")
    print("=" * 40)
    
    # Database setup
    db_path = '/app/watch1_dev.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_files (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Clear existing entries
    cursor.execute('DELETE FROM media_files')
    
    # Common media directories to scan
    media_dirs = [
        '/app/media',
        '/data/media',
        '/media',
        '/mnt/media'
    ]
    
    # Media file extensions
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    audio_extensions = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a'}
    
    total_files = 0
    
    for media_dir in media_dirs:
        if os.path.exists(media_dir):
            print(f"Scanning: {media_dir}")
            
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = Path(root) / file
                    extension = file_path.suffix.lower()
                    
                    if extension in video_extensions or extension in audio_extensions:
                        try:
                            file_size = file_path.stat().st_size
                            file_id = get_file_id(file_path)
                            category = get_category_from_path(file_path)
                            
                            cursor.execute('''
                            INSERT INTO media_files (id, filename, file_path, file_size, category)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (file_id, file, str(file_path), file_size, category))
                            
                            total_files += 1
                            print(f"  Added: {file} ({category})")
                            
                        except Exception as e:
                            print(f"  Error processing {file}: {e}")
    
    # If no live files found, create minimal test data
    if total_files == 0:
        print("No live media found, creating minimal test data...")
        test_files = [
            ('test1', 'Sample Movie.mp4', '/app/media/Sample Movie.mp4', 1000000, 'movies'),
            ('test2', 'Test Show S01E01.mkv', '/app/media/Test Show S01E01.mkv', 800000, 'tv_shows'),
            ('test3', 'Kids Video.mp4', '/app/media/Kids Video.mp4', 600000, 'kids'),
            ('test4', 'Music Track.mp3', '/app/media/Music Track.mp3', 5000000, 'music'),
            ('test5', 'Home Video.mov', '/app/media/Home Video.mov', 1200000, 'videos')
        ]
        
        cursor.executemany('''
        INSERT INTO media_files (id, filename, file_path, file_size, category)
        VALUES (?, ?, ?, ?, ?)
        ''', test_files)
        
        total_files = len(test_files)
    
    conn.commit()
    
    # Show results
    cursor.execute('SELECT category, COUNT(*) FROM media_files GROUP BY category')
    categories = cursor.fetchall()
    
    print(f"\nScan complete: {total_files} files added")
    print("Categories:")
    for cat, count in categories:
        print(f"  {cat}: {count} files")
    
    conn.close()
    return total_files

if __name__ == "__main__":
    scan_live_media()
