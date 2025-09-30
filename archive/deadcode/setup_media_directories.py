#!/usr/bin/env python3
"""
Setup script to create media directories and populate databases with sample data
"""

import os
import sqlite3
import uuid
import random
from datetime import datetime, timedelta

# Media categories and sample data
MEDIA_CATEGORIES = {
    'movies': {
        'titles': [
            'The Matrix (1999)', 'Inception (2010)', 'Interstellar (2014)', 'The Dark Knight (2008)',
            'Pulp Fiction (1994)', 'The Shawshank Redemption (1994)', 'Fight Club (1999)', 
            'Goodfellas (1990)', 'The Godfather (1972)', 'Forrest Gump (1994)'
        ],
        'extensions': ['.mkv', '.mp4', '.avi'],
        'sizes': [1500000000, 2500000000, 3500000000, 4500000000],  # 1.5GB to 4.5GB
        'durations': [7200, 8400, 9600, 10800]  # 2-3 hours
    },
    'tv_shows': {
        'titles': [
            'Breaking Bad S01E01', 'Game of Thrones S01E01', 'The Office S01E01', 'Friends S01E01',
            'Stranger Things S01E01', 'The Crown S01E01', 'Westworld S01E01', 'Lost S01E01',
            'House of Cards S01E01', 'Better Call Saul S01E01'
        ],
        'extensions': ['.mkv', '.mp4'],
        'sizes': [800000000, 1200000000, 1600000000],  # 800MB to 1.6GB
        'durations': [2400, 2700, 3000, 3600]  # 40-60 minutes
    },
    'documentaries': {
        'titles': [
            'Planet Earth (2006)', 'Free Solo (2018)', 'Won\'t You Be My Neighbor (2018)',
            'The Social Dilemma (2020)', 'My Octopus Teacher (2020)', 'Blackfish (2013)',
            'An Inconvenient Truth (2006)', 'March of the Penguins (2005)', 
            'Bowling for Columbine (2002)', 'Fahrenheit 9/11 (2004)'
        ],
        'extensions': ['.mkv', '.mp4'],
        'sizes': [1000000000, 1800000000, 2200000000],  # 1GB to 2.2GB
        'durations': [5400, 6600, 7800]  # 1.5-2 hours
    },
    'music_videos': {
        'titles': [
            'Bohemian Rhapsody - Queen', 'Thriller - Michael Jackson', 'Smells Like Teen Spirit - Nirvana',
            'Billie Jean - Michael Jackson', 'Sweet Child O Mine - Guns N Roses', 'Hotel California - Eagles',
            'Stairway to Heaven - Led Zeppelin', 'Imagine - John Lennon', 'Like a Rolling Stone - Bob Dylan',
            'Hey Jude - The Beatles'
        ],
        'extensions': ['.mp4', '.mkv'],
        'sizes': [150000000, 250000000, 350000000],  # 150MB to 350MB
        'durations': [180, 240, 300, 360]  # 3-6 minutes
    }
}

def generate_uuid():
    """Generate a URL-safe UUID"""
    return str(uuid.uuid4()).replace('-', '')[:22]

def create_media_directories():
    """Create media directory structure"""
    base_path = "p:/Watch1/media"
    
    print("📁 Creating media directory structure...")
    
    for category in MEDIA_CATEGORIES.keys():
        category_path = os.path.join(base_path, category)
        os.makedirs(category_path, exist_ok=True)
        print(f"   ✅ Created: {category_path}")
        
        # Create some sample files (empty files for demonstration)
        for i, title in enumerate(MEDIA_CATEGORIES[category]['titles']):
            extension = random.choice(MEDIA_CATEGORIES[category]['extensions'])
            # Clean filename for filesystem compatibility
            clean_title = title.replace('/', '-').replace('\\', '-').replace(':', '-')
            filename = f"{clean_title}{extension}"
            filepath = os.path.join(category_path, filename)
            
            # Create empty file
            try:
                with open(filepath, 'w') as f:
                    f.write('')
                print(f"      📄 Created sample file: {filename}")
            except Exception as e:
                print(f"      ❌ Failed to create {filename}: {e}")

def populate_database(db_path):
    """Populate database with sample media entries"""
    print(f"\n🗄️ Populating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if media_files table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media_files'")
    if not cursor.fetchone():
        print("❌ media_files table not found, skipping database population")
        conn.close()
        return
    
    total_added = 0
    
    for category, data in MEDIA_CATEGORIES.items():
        print(f"\n📂 Adding {category} entries...")
        
        for i, title in enumerate(data['titles']):
            media_id = generate_uuid()
            extension = random.choice(data['extensions'])
            # Clean filename for filesystem compatibility
            clean_title = title.replace('/', '-').replace('\\', '-').replace(':', '-')
            filename = f"{clean_title}{extension}"
            
            # Use both local path and T: drive path for compatibility
            local_path = f"p:/Watch1/media/{category}/{filename}"
            t_drive_path = f"T:/Media/{category}/{filename}"
            
            file_size = random.choice(data['sizes'])
            duration = random.choice(data['durations'])
            
            # Random creation date within last year
            days_ago = random.randint(1, 365)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            # Insert media file record
            cursor.execute('''
                INSERT INTO media_files (
                    id, original_filename, filename, file_path, category, 
                    file_size, duration, poster_path, thumbnail_path,
                    created_at, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                media_id,
                filename,
                filename,
                t_drive_path,  # Use T: drive path for compatibility with existing system
                category,
                file_size,
                duration,
                f"/thumbnails/{media_id}_poster.jpg",
                f"/thumbnails/{media_id}_thumb.jpg",
                created_at.isoformat(),
                0  # not deleted
            ))
            
            total_added += 1
            print(f"   ✅ Added: {filename} (ID: {media_id})")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Successfully added {total_added} media entries to database!")

def update_both_databases():
    """Update both local and container databases"""
    
    # Local database
    local_db = "p:/Watch1/backend/watch1.db"
    if os.path.exists(local_db):
        populate_database(local_db)
    else:
        print(f"❌ Local database not found: {local_db}")
    
    # Container database (copy updated local DB to container)
    print("\n🐳 Updating container database...")
    import subprocess
    try:
        result = subprocess.run([
            "docker", "cp", 
            "backend/watch1.db", 
            "watch1-backend-dev:/app/watch1.db"
        ], cwd="p:/Watch1", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Container database updated successfully!")
        else:
            print(f"❌ Failed to update container database: {result.stderr}")
    except Exception as e:
        print(f"❌ Error updating container database: {e}")

def create_sample_thumbnails():
    """Create sample thumbnail directories"""
    print("\n🖼️ Creating thumbnail directories...")
    
    thumbnail_dirs = [
        "p:/Watch1/backend/thumbnails",
        "p:/Watch1/media/thumbnails"
    ]
    
    for thumb_dir in thumbnail_dirs:
        os.makedirs(thumb_dir, exist_ok=True)
        print(f"   ✅ Created: {thumb_dir}")

def main():
    """Main setup function"""
    print("🎬 Watch1 Media Directory Setup")
    print("=" * 50)
    
    # Create media directories and sample files
    create_media_directories()
    
    # Create thumbnail directories
    create_sample_thumbnails()
    
    # Populate databases
    update_both_databases()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nMedia directories created:")
    for category in MEDIA_CATEGORIES.keys():
        print(f"   📁 p:/Watch1/media/{category} (10 sample files)")
    
    print(f"\nTotal media entries added: {len(MEDIA_CATEGORIES) * 10}")
    print("\nNext steps:")
    print("1. Restart the backend container to reload the database")
    print("2. Test the frontend to see the new media files")
    print("3. Update media paths if needed for your system")

if __name__ == "__main__":
    main()
