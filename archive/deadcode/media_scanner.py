#!/usr/bin/env python3
"""
Media Scanner with Automatic Poster Art Detection and Database Updates
"""

import os
import sqlite3
import hashlib
import re
from pathlib import Path
from datetime import datetime
import mimetypes

class MediaScanner:
    def __init__(self):
        # Import global database configuration
        try:
            from backend.database_config import db_config
            self.db_config = db_config
        except ImportError:
            # Fallback for direct execution
            import sys
            sys.path.append('/app')
            from database_config import db_config
            self.db_config = db_config
            
        self.supported_video_formats = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        self.supported_audio_formats = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        
        print(f"📡 MediaScanner initialized with database: {self.db_config.get_path()}")
        
    def get_db_connection(self):
        """Get database connection using global config"""
        return self.db_config.get_connection()
    
    def extract_movie_title(self, filename, file_path):
        """Extract proper movie title from filename or directory"""
        # Remove file extension
        title = filename
        if any(title.lower().endswith(ext) for ext in self.supported_video_formats):
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
    
    def load_poster_image(self, file_path):
        """Load poster.jpg from the same directory as the media file"""
        try:
            # Handle Windows paths in container
            if file_path.startswith('T:'):
                file_path = file_path.replace('T:', '/app/T')
            elif file_path.startswith('C:'):
                file_path = file_path.replace('C:', '/app/C')
                
            directory = os.path.dirname(file_path)
            
            # Try different poster file names
            poster_names = ['poster.jpg', 'poster.jpeg', 'poster.png', 'folder.jpg', 'cover.jpg']
            
            for poster_name in poster_names:
                poster_path = os.path.join(directory, poster_name)
                if os.path.exists(poster_path):
                    with open(poster_path, 'rb') as f:
                        return f.read()
        except Exception as e:
            print(f"Error loading poster for {file_path}: {e}")
        
        return None
    
    def get_file_info(self, file_path):
        """Get file information"""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime)
            }
        except:
            return None
    
    def categorize_file(self, file_path):
        """Categorize file based on directory structure"""
        path_lower = file_path.lower()
        
        if 'movies' in path_lower:
            return 'movies'
        elif 'tv' in path_lower or 'series' in path_lower:
            return 'tv_series'
        elif 'documentary' in path_lower or 'documentaries' in path_lower:
            return 'documentaries'
        elif 'music' in path_lower:
            return 'music_videos'
        elif 'kids' in path_lower or 'children' in path_lower:
            return 'kids'
        else:
            return 'other'
    
    def generate_media_id(self, file_path):
        """Generate unique media ID"""
        return hashlib.md5(file_path.encode()).hexdigest()[:22]
    
    def scan_directory(self, directory_path, progress_callback=None):
        """Scan a directory for media files"""
        print(f"🔍 Scanning directory: {directory_path}")
        
        if not os.path.exists(directory_path):
            print(f"❌ Directory not found: {directory_path}")
            return []
        
        media_files = []
        total_files = 0
        processed_files = 0
        
        # Count total files first
        for root, dirs, files in os.walk(directory_path):
            total_files += len(files)
        
        # Process files
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                processed_files += 1
                file_path = os.path.join(root, file)
                
                # Progress callback
                if progress_callback:
                    progress_callback(processed_files, total_files, file_path)
                
                # Check if it's a supported media file
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in self.supported_video_formats and file_ext not in self.supported_audio_formats:
                    continue
                
                # Get file info
                file_info = self.get_file_info(file_path)
                if not file_info:
                    continue
                
                # Generate media info
                media_id = self.generate_media_id(file_path)
                title = self.extract_movie_title(file, file_path)
                category = self.categorize_file(file_path)
                poster_data = self.load_poster_image(file_path)
                
                media_info = {
                    'id': media_id,
                    'filename': file,
                    'title': title,
                    'file_path': file_path,
                    'category': category,
                    'file_size': file_info['size'],
                    'duration': None,  # Could be extracted with ffprobe
                    'poster_data': poster_data,
                    'created_at': file_info['created'],
                    'modified_at': file_info['modified']
                }
                
                media_files.append(media_info)
        
        print(f"✅ Found {len(media_files)} media files in {directory_path}")
        return media_files
    
    def update_database(self, media_files):
        """Update database with scanned media files"""
        print(f"💾 Updating database with {len(media_files)} files...")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Ensure required columns exist
        try:
            cursor.execute("ALTER TABLE media_files ADD COLUMN title TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE media_files ADD COLUMN poster_data BLOB")
        except sqlite3.OperationalError:
            pass
        
        updated_count = 0
        new_count = 0
        poster_count = 0
        
        for media in media_files:
            # Check if file already exists
            existing = cursor.execute(
                'SELECT id, file_size, modified_at FROM media_files WHERE file_path = ?',
                (media['file_path'],)
            ).fetchone()
            
            if existing:
                # Update existing record if file was modified or poster is new
                needs_update = False
                
                # Check if file was modified
                if existing['file_size'] != media['file_size']:
                    needs_update = True
                
                # Check if we have new poster data
                if media['poster_data'] and not existing.get('poster_data'):
                    needs_update = True
                
                if needs_update:
                    cursor.execute('''
                        UPDATE media_files 
                        SET filename = ?, title = ?, file_size = ?, poster_data = ?, 
                            category = ?, modified_at = datetime('now')
                        WHERE file_path = ?
                    ''', (
                        media['filename'], media['title'], media['file_size'],
                        media['poster_data'], media['category'], media['file_path']
                    ))
                    updated_count += 1
                    if media['poster_data']:
                        poster_count += 1
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO media_files 
                    (id, filename, title, file_path, category, file_size, duration, 
                     poster_data, created_at, is_deleted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 0)
                ''', (
                    media['id'], media['filename'], media['title'], media['file_path'],
                    media['category'], media['file_size'], media['duration'], media['poster_data']
                ))
                new_count += 1
                if media['poster_data']:
                    poster_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database updated:")
        print(f"   📁 New files: {new_count}")
        print(f"   🔄 Updated files: {updated_count}")
        print(f"   🖼️  Posters loaded: {poster_count}")
        
        return {
            'new_files': new_count,
            'updated_files': updated_count,
            'posters_loaded': poster_count,
            'total_processed': len(media_files)
        }
    
    def scan_all_directories(self):
        """Scan all configured media directories"""
        directories = [
            "/app/T/Movies",
            "/app/T/TV Series", 
            "/app/T/Documentaries",
            "/app/T/Music Videos",
            "/app/T/Kids"
        ]
        
        all_media_files = []
        scan_results = {
            'directories_scanned': 0,
            'total_files_found': 0,
            'scan_start': datetime.now(),
            'scan_end': None,
            'errors': []
        }
        
        for directory in directories:
            try:
                if os.path.exists(directory):
                    media_files = self.scan_directory(directory)
                    all_media_files.extend(media_files)
                    scan_results['directories_scanned'] += 1
                    scan_results['total_files_found'] += len(media_files)
                else:
                    print(f"⚠️  Directory not found: {directory}")
            except Exception as e:
                error_msg = f"Error scanning {directory}: {e}"
                print(f"❌ {error_msg}")
                scan_results['errors'].append(error_msg)
        
        # Update database
        if all_media_files:
            db_results = self.update_database(all_media_files)
            scan_results.update(db_results)
        
        scan_results['scan_end'] = datetime.now()
        scan_results['scan_duration'] = (scan_results['scan_end'] - scan_results['scan_start']).total_seconds()
        
        return scan_results

def main():
    """Main scanning function"""
    print("🚀 STARTING MEDIA SCAN WITH POSTER ART UPDATE")
    print("=" * 50)
    
    scanner = MediaScanner()
    
    try:
        results = scanner.scan_all_directories()
        
        print(f"\n" + "=" * 50)
        print("📊 SCAN RESULTS")
        print("=" * 50)
        print(f"⏱️  Duration: {results['scan_duration']:.1f} seconds")
        print(f"📁 Directories scanned: {results['directories_scanned']}")
        print(f"📄 Total files found: {results['total_files_found']}")
        print(f"🆕 New files added: {results.get('new_files', 0)}")
        print(f"🔄 Files updated: {results.get('updated_files', 0)}")
        print(f"🖼️  Poster images loaded: {results.get('posters_loaded', 0)}")
        
        if results['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in results['errors']:
                print(f"   {error}")
        
        print(f"\n✅ Scan completed successfully!")
        return results
        
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        return None

if __name__ == "__main__":
    main()
