#!/usr/bin/env python3
"""
Enhanced Media Scanner with Storage Format Support
Handles collection, series, group, and item storage formats
"""

import os
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MediaItem:
    """Represents a scanned media item"""
    id: str
    filename: str
    file_path: str
    file_size: int
    category: str
    title: str
    year: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ScanResult:
    """Results from scanning a directory"""
    category: str
    path: str
    files_found: int
    files_added: int
    items: List[MediaItem]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class EnhancedMediaScanner:
    """Enhanced media scanner with storage format support"""
    
    def __init__(self):
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
        self.audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.m4b'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}
        
        self.supported_extensions = self.video_extensions | self.audio_extensions | self.image_extensions
    
    def scan_directory(self, config: Dict[str, Any]) -> ScanResult:
        """Scan a directory based on its storage format configuration"""
        storage_format = config.get('storage_format', 'collection')
        
        if storage_format == 'collection':
            return self._scan_collection(config)
        elif storage_format == 'series':
            return self._scan_series(config)
        elif storage_format == 'group':
            return self._scan_group(config)
        elif storage_format == 'item':
            return self._scan_item(config)
        else:
            raise ValueError(f"Unsupported storage format: {storage_format}")
    
    def _scan_collection(self, config: Dict[str, Any]) -> ScanResult:
        """Scan collection format (flat structure with individual items)"""
        path = config['root_path']
        category = config['key']
        
        if not os.path.exists(path):
            return ScanResult(category, path, 0, 0, [])
        
        items = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(root, filename)
                item = self._process_file(file_path, category, config)
                if item:
                    items.append(item)
        
        return ScanResult(
            category=category,
            path=path,
            files_found=len(items),
            files_added=len(items),  # This would be calculated differently in real implementation
            items=items,
            metadata={'storage_format': 'collection'}
        )
    
    def _scan_series(self, config: Dict[str, Any]) -> ScanResult:
        """Scan series format (hierarchical: series/season/episode)"""
        path = config['root_path']
        category = config['key']
        hierarchy = config.get('hierarchy', {}).get('levels', [])
        
        if not os.path.exists(path):
            return ScanResult(category, path, 0, 0, [])
        
        items = []
        series_data = {}
        
        # Walk through directory structure
        for root, dirs, files in os.walk(path):
            rel_path = os.path.relpath(root, path)
            path_parts = rel_path.split(os.sep) if rel_path != '.' else []
            
            for filename in files:
                file_path = os.path.join(root, filename)
                item = self._process_file(file_path, category, config)
                if item:
                    # Extract series metadata from path structure
                    series_metadata = self._extract_series_metadata(path_parts, filename, hierarchy)
                    item.metadata.update(series_metadata)
                    items.append(item)
                    
                    # Track series information
                    series_name = series_metadata.get('series', 'Unknown')
                    if series_name not in series_data:
                        series_data[series_name] = {'episodes': 0, 'seasons': set()}
                    series_data[series_name]['episodes'] += 1
                    if 'season' in series_metadata:
                        series_data[series_name]['seasons'].add(series_metadata['season'])
        
        # Convert sets to counts for JSON serialization
        for series in series_data.values():
            series['seasons'] = len(series['seasons'])
        
        return ScanResult(
            category=category,
            path=path,
            files_found=len(items),
            files_added=len(items),
            items=items,
            metadata={
                'storage_format': 'series',
                'series_count': len(series_data),
                'series_data': series_data
            }
        )
    
    def _scan_group(self, config: Dict[str, Any]) -> ScanResult:
        """Scan group format (hierarchical: artist/album/track)"""
        path = config['root_path']
        category = config['key']
        hierarchy = config.get('hierarchy', {}).get('levels', [])
        
        if not os.path.exists(path):
            return ScanResult(category, path, 0, 0, [])
        
        items = []
        group_data = {}
        
        for root, dirs, files in os.walk(path):
            rel_path = os.path.relpath(root, path)
            path_parts = rel_path.split(os.sep) if rel_path != '.' else []
            
            for filename in files:
                file_path = os.path.join(root, filename)
                item = self._process_file(file_path, category, config)
                if item:
                    # Extract group metadata from path structure
                    group_metadata = self._extract_group_metadata(path_parts, filename, hierarchy)
                    item.metadata.update(group_metadata)
                    items.append(item)
                    
                    # Track group information (e.g., artist/album data)
                    group_key = group_metadata.get('artist', 'Unknown Artist')
                    album_key = group_metadata.get('album', 'Unknown Album')
                    
                    if group_key not in group_data:
                        group_data[group_key] = {'albums': {}, 'total_tracks': 0}
                    if album_key not in group_data[group_key]['albums']:
                        group_data[group_key]['albums'][album_key] = 0
                    
                    group_data[group_key]['albums'][album_key] += 1
                    group_data[group_key]['total_tracks'] += 1
        
        return ScanResult(
            category=category,
            path=path,
            files_found=len(items),
            files_added=len(items),
            items=items,
            metadata={
                'storage_format': 'group',
                'group_count': len(group_data),
                'group_data': group_data
            }
        )
    
    def _scan_item(self, config: Dict[str, Any]) -> ScanResult:
        """Scan item format (single items, no grouping)"""
        # Similar to collection but with different metadata handling
        return self._scan_collection(config)
    
    def _process_file(self, file_path: str, category: str, config: Dict[str, Any]) -> Optional[MediaItem]:
        """Process a single file and create MediaItem"""
        try:
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Check if file extension is supported
            include_patterns = config.get('include_patterns', [])
            if include_patterns:
                # If specific patterns are defined, check against them
                if not any(filename.lower().endswith(pattern.replace('**/*', '')) 
                          for pattern in include_patterns):
                    return None
            else:
                # Default extension check
                if file_ext not in self.supported_extensions:
                    return None
            
            # Get file stats
            stat = os.stat(file_path)
            file_size = stat.st_size
            
            # Generate unique ID
            file_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Extract title and metadata
            title, year = self._extract_title_and_year(filename)
            
            return MediaItem(
                id=file_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                category=category,
                title=title,
                year=year,
                metadata={
                    'file_extension': file_ext,
                    'media_type': self._get_media_type(file_ext)
                }
            )
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return None
    
    def _extract_title_and_year(self, filename: str) -> Tuple[str, Optional[int]]:
        """Extract title and year from filename"""
        # Remove extension
        title = os.path.splitext(filename)[0]
        
        # Clean up title
        title = title.replace('_', ' ').replace('.', ' ')
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Extract year
        year = None
        year_match = re.search(r'\((\d{4})\)', title)
        if year_match:
            year = int(year_match.group(1))
            title = title.replace(year_match.group(0), '').strip()
        
        return title, year
    
    def _extract_series_metadata(self, path_parts: List[str], filename: str, hierarchy: List[Dict]) -> Dict[str, Any]:
        """Extract series metadata from path structure"""
        metadata = {}
        
        # Map path parts to hierarchy levels
        for i, level_config in enumerate(hierarchy):
            if i < len(path_parts):
                level_name = level_config.get('name', f'level_{i}')
                metadata[level_name] = path_parts[i]
        
        # Try to extract episode information from filename
        episode_match = re.search(r'[Ss](\d+)[Ee](\d+)', filename)
        if episode_match:
            metadata['season_number'] = int(episode_match.group(1))
            metadata['episode_number'] = int(episode_match.group(2))
        
        return metadata
    
    def _extract_group_metadata(self, path_parts: List[str], filename: str, hierarchy: List[Dict]) -> Dict[str, Any]:
        """Extract group metadata from path structure"""
        metadata = {}
        
        # Map path parts to hierarchy levels
        for i, level_config in enumerate(hierarchy):
            if i < len(path_parts):
                level_name = level_config.get('name', f'level_{i}')
                metadata[level_name] = path_parts[i]
        
        # Try to extract track number from filename
        track_match = re.search(r'^(\d+)[\s\-\.]+', filename)
        if track_match:
            metadata['track_number'] = int(track_match.group(1))
        
        return metadata
    
    def _get_media_type(self, file_ext: str) -> str:
        """Determine media type from file extension"""
        if file_ext in self.video_extensions:
            return 'video'
        elif file_ext in self.audio_extensions:
            return 'audio'
        elif file_ext in self.image_extensions:
            return 'image'
        else:
            return 'unknown'

# Example usage and testing
if __name__ == "__main__":
    scanner = EnhancedMediaScanner()
    
    # Test configuration for different storage formats
    test_configs = [
        {
            'key': 'movies',
            'storage_format': 'collection',
            'root_path': '/app/T/Movies',
            'include_patterns': ['**/*.mp4', '**/*.mkv', '**/*.avi']
        },
        {
            'key': 'tv_shows',
            'storage_format': 'series',
            'root_path': '/app/T/TV Shows',
            'hierarchy': {
                'levels': [
                    {'name': 'series'},
                    {'name': 'season'},
                    {'name': 'episode'}
                ]
            }
        },
        {
            'key': 'music',
            'storage_format': 'group',
            'root_path': '/app/T/Music',
            'hierarchy': {
                'levels': [
                    {'name': 'artist'},
                    {'name': 'album'}
                ]
            }
        }
    ]
    
    for config in test_configs:
        print(f"\nTesting {config['key']} ({config['storage_format']}):")
        try:
            result = scanner.scan_directory(config)
            print(f"  Found {result.files_found} files")
            print(f"  Metadata: {result.metadata}")
        except Exception as e:
            print(f"  Error: {e}")
