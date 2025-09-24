#!/usr/bin/env python3
"""
Preload poster.jpg files and extract proper movie titles into database
"""

import sqlite3
import os
import re
from pathlib import Path

def get_db_connection():
    """Get database connection"""
    # Try different possible database locations
    db_paths = ['/app/watch1_dev.db', '/app/database.db', '/app/watch1.db', './watch1_dev.db', './database.db', './watch1.db']
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Found database at: {db_path}")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    raise FileNotFoundError("Database not found in any expected location")

def extract_movie_title(filename, file_path):
    """Extract proper movie title from filename or directory"""
    # Remove file extension
    title = filename
    if title.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm')):
        title = title.rsplit('.', 1)[0]
    
    # Try to extract from directory name first (more accurate)
    directory = os.path.dirname(file_path)
    dir_name = os.path.basename(directory)
    
    # If directory looks like a movie title (contains year), use it
    if re.search(r'\(\d{4}\)', dir_name):
        title = dir_name
    
    # Clean up common patterns
    # Remove quality indicators
    title = re.sub(r'\b(720p|1080p|4K|BluRay|BRRip|DVDRip|WEBRip|HDTV)\b', '', title, flags=re.IGNORECASE)
    # Remove codec info
    title = re.sub(r'\b(x264|x265|H264|H265|HEVC|DivX|XviD)\b', '', title, flags=re.IGNORECASE)
    # Remove group tags
    title = re.sub(r'\[.*?\]', '', title)
    # Remove extra spaces and dashes
    title = re.sub(r'[-_\s]+', ' ', title).strip()
    
    return title

def load_poster_image(file_path):
    """Load poster.jpg from the same directory as the media file"""
    try:
        # Handle Windows paths in container
        if file_path.startswith('T:'):
            file_path = file_path.replace('T:', '/app/T')
        elif file_path.startswith('C:'):
            file_path = file_path.replace('C:', '/app/C')
            
        directory = os.path.dirname(file_path)
        poster_path = os.path.join(directory, 'poster.jpg')
        
        if os.path.exists(poster_path):
            with open(poster_path, 'rb') as f:
                return f.read()
    except Exception as e:
        # Don't print errors for every missing poster - too verbose
        pass
    
    return None

def preload_database():
    """Preload titles and poster images into database"""
    print("PRELOADING TITLES AND POSTER IMAGES")
    print("=" * 40)
    
    # First, add columns if they don't exist
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Add title column if it doesn't exist
        cursor.execute("ALTER TABLE media_files ADD COLUMN title TEXT")
        print("✅ Added title column")
    except sqlite3.OperationalError:
        print("ℹ️  Title column already exists")
    
    try:
        # Add poster_data column for binary data
        cursor.execute("ALTER TABLE media_files ADD COLUMN poster_data BLOB")
        print("✅ Added poster_data column")
    except sqlite3.OperationalError:
        print("ℹ️  Poster_data column already exists")
    
    # Get all media files
    media_files = cursor.execute('SELECT id, filename, file_path FROM media_files').fetchall()
    
    print(f"\nProcessing {len(media_files)} media files...")
    print("-" * 40)
    
    updated_count = 0
    poster_count = 0
    
    for media in media_files:
        media_id = media['id']
        filename = media['filename']
        file_path = media['file_path']
        
        # Extract proper title
        title = extract_movie_title(filename, file_path)
        
        # Load poster image
        poster_data = load_poster_image(file_path)
        
        # Update database
        cursor.execute('''
            UPDATE media_files 
            SET title = ?, poster_data = ?
            WHERE id = ?
        ''', (title, poster_data, media_id))
        
        updated_count += 1
        if poster_data:
            poster_count += 1
            print(f"✅ {title[:50]:<50} [Poster: {len(poster_data):,} bytes]")
        else:
            print(f"📄 {title[:50]:<50} [No poster]")
    
    conn.commit()
    conn.close()
    
    print(f"\n" + "=" * 40)
    print("PRELOAD SUMMARY")
    print("=" * 40)
    print(f"✅ Updated {updated_count} media files")
    print(f"🖼️  Loaded {poster_count} poster images")
    print(f"📊 Success rate: {poster_count/updated_count*100:.1f}%")
    
    return updated_count, poster_count

if __name__ == "__main__":
    try:
        preload_database()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("Available files in current directory:")
        for f in os.listdir('.'):
            if f.endswith('.db'):
                print(f"   {f}")
        print("\nRun this script inside the backend container:")
        print("   docker exec -it watch1-backend-dev python preload_posters_and_titles.py")
