#!/usr/bin/env python3
"""
Unraid Media Scanner for Watch1
Direct access to Unraid media shares with PostgreSQL integration
Designed to run natively on Unraid server
"""

import os
import sys
import psycopg2
import hashlib
from pathlib import Path
from datetime import datetime
import mimetypes
import json

class UnraidMediaScanner:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://watch1_user:watch1_dev_password@localhost:5432/watch1_dev')
        self.media_root = os.getenv('MEDIA_ROOT', '/mnt/user/media')
        
        # Media type mappings
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
        self.audio_extensions = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        
        # Category detection patterns
        self.category_patterns = {
            'movies': ['movie', 'film', 'cinema', 'movies'],
            'tv_shows': ['tv', 'series', 'show', 'episode', 'season', 'tv shows'],
            'kids': ['kid', 'child', 'family', 'disney', 'cartoon', 'kids'],
            'music': ['music', 'song', 'audio', 'album', 'artist'],
            'music_videos': ['music video', 'music_video', 'musicvideo', 'music videos'],
            'documentaries': ['documentary', 'documentaries', 'doc'],
            'videos': ['video', 'videos', 'home video', 'personal']
        }

    def get_file_id(self, file_path):
        """Generate unique ID for file based on path"""
        return hashlib.md5(str(file_path).encode()).hexdigest()

    def detect_category(self, file_path):
        """Detect category based on file path and name"""
        path_lower = str(file_path).lower()
        
        # Check each category pattern
        for category, patterns in self.category_patterns.items():
            if any(pattern in path_lower for pattern in patterns):
                return category
        
        # Default based on file type
        extension = Path(file_path).suffix.lower()
        if extension in self.video_extensions:
            return 'videos'
        elif extension in self.audio_extensions:
            return 'music'
        elif extension in self.image_extensions:
            return 'photos'
        else:
            return 'other'

    def get_media_info(self, file_path):
        """Extract media information from file"""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime)
            }
        except Exception as e:
            print(f"Warning: Could not get file info for {file_path}: {e}")
            return {'size': 0, 'modified': datetime.now(), 'created': datetime.now()}

    def scan_directory(self, directory):
        """Scan a directory for media files"""
        print(f"📁 Scanning: {directory}")
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return []
        
        media_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['@eaDir', 'Thumbs.db']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    file_path = Path(root) / file
                    extension = file_path.suffix.lower()
                    
                    # Check if it's a media file
                    if extension in (self.video_extensions | self.audio_extensions | self.image_extensions):
                        try:
                            file_info = self.get_media_info(file_path)
                            category = self.detect_category(file_path)
                            
                            media_file = {
                                'id': self.get_file_id(file_path),
                                'filename': file,
                                'file_path': str(file_path),
                                'file_size': file_info['size'],
                                'category': category,
                                'file_type': extension[1:],  # Remove the dot
                                'relative_path': str(file_path.relative_to(self.media_root)),
                                'modified_at': file_info['modified'],
                                'created_at': file_info['created']
                            }
                            
                            media_files.append(media_file)
                            
                        except Exception as e:
                            print(f"⚠️ Error processing {file_path}: {e}")
                            continue
                            
        except Exception as e:
            print(f"❌ Error scanning directory {directory}: {e}")
            
        return media_files

    def update_database(self, media_files):
        """Update PostgreSQL database with media files"""
        print(f"💾 Updating database with {len(media_files)} files...")
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media_files (
                    id VARCHAR(32) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size BIGINT,
                    category VARCHAR(50),
                    file_type VARCHAR(10),
                    relative_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMP,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Clear existing entries for fresh scan
            cursor.execute('DELETE FROM media_files')
            print("🗑️ Cleared existing database entries")
            
            # Insert new entries
            insert_query = '''
                INSERT INTO media_files 
                (id, filename, file_path, file_size, category, file_type, relative_path, modified_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            for media_file in media_files:
                cursor.execute(insert_query, (
                    media_file['id'],
                    media_file['filename'],
                    media_file['file_path'],
                    media_file['file_size'],
                    media_file['category'],
                    media_file['file_type'],
                    media_file['relative_path'],
                    media_file['modified_at'],
                    media_file['created_at']
                ))
            
            conn.commit()
            
            # Show results
            cursor.execute('SELECT category, COUNT(*) FROM media_files GROUP BY category ORDER BY category')
            categories = cursor.fetchall()
            
            print(f"✅ Database updated successfully!")
            print("📊 Categories:")
            total_files = 0
            for category, count in categories:
                print(f"  📁 {category}: {count} files")
                total_files += count
            
            print(f"📈 Total: {total_files} media files")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
            
        return True

    def scan_all_media(self):
        """Scan all media directories on Unraid"""
        print("🚀 Starting Unraid Media Scan")
        print("=" * 50)
        print(f"📍 Media Root: {self.media_root}")
        print(f"🗄️ Database: {self.db_url.split('@')[1] if '@' in self.db_url else 'localhost'}")
        print("")
        
        all_media_files = []
        
        # Common Unraid media directories
        media_dirs = [
            self.media_root,
            '/mnt/user/Movies',
            '/mnt/user/TV Shows',
            '/mnt/user/Music',
            '/mnt/user/Videos',
            '/mnt/user/Kids',
            '/mnt/user/Documentaries'
        ]
        
        # Scan each directory that exists
        for media_dir in media_dirs:
            if os.path.exists(media_dir):
                files = self.scan_directory(media_dir)
                all_media_files.extend(files)
                print(f"  ✅ Found {len(files)} files in {media_dir}")
            else:
                print(f"  ⏭️ Skipping {media_dir} (not found)")
        
        print(f"\n📊 Scan Summary: {len(all_media_files)} total media files found")
        
        # Update database
        if all_media_files:
            success = self.update_database(all_media_files)
            if success:
                print("\n🎉 Unraid media scan completed successfully!")
                return len(all_media_files)
        else:
            print("\n⚠️ No media files found to process")
            
        return 0

def main():
    """Main function"""
    scanner = UnraidMediaScanner()
    
    try:
        total_files = scanner.scan_all_media()
        
        if total_files > 0:
            print(f"\n✅ Successfully scanned {total_files} media files")
            print("🌐 Ready for Watch1 frontend access!")
        else:
            print("\n❌ No media files were processed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
