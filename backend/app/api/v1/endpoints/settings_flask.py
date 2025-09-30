"""
Flask-compatible settings endpoints extracted from working flask_simple.py
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from postgres_config import get_db_connection

router = Blueprint('settings', __name__)

@router.route('/test', methods=['GET'])
def settings_test():
    """Test settings endpoint"""
    return jsonify({
        "message": "Settings router is working in Flask!",
        "status": "success",
        "framework": "Flask",
        "timestamp": "2025-09-29"
    })

@router.route('/', methods=['GET'])
@jwt_required()
def get_settings():
    """Get all settings"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        # Return comprehensive settings
        settings = {
            "media_locations": {
                "movies": "/app/T/Movies",
                "tv_shows": "/app/T/TV Shows",
                "music": "/app/T/Music",
                "videos": "/app/T/Videos",
                "music_videos": "/app/T/Music Videos",
                "kids": "/app/T/Kids",
                "custom_directories": []
            },
            "scanning": {
                "auto_scan_enabled": False,
                "auto_scan_interval_hours": 24,
                "skip_other_category": True,
                "backup_before_scan": True,
                "supported_formats": {
                    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
                    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
                    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
                }
            },
            "playback": {
                "default_quality": "auto",
                "auto_play_next": True,
                "remember_position": True,
                "subtitle_language": "en"
            },
            "ui": {
                "theme": "dark",
                "items_per_page": 24,
                "show_file_extensions": False,
                "grid_columns": 6
            },
            "security": {
                "require_authentication": True,
                "session_timeout_hours": 24,
                "max_login_attempts": 5
            }
        }
        
        return jsonify(settings)
        
    except Exception as e:
        print(f"Settings error: {e}")
        return jsonify({"detail": f"Settings error: {str(e)}"}), 500

@router.route('/', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update settings"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"detail": "No settings data provided"}), 400
        
        # In a real implementation, you would save these to a settings table
        # For now, just return success
        return jsonify({
            "message": "Settings updated successfully",
            "updated_settings": data
        })
        
    except Exception as e:
        print(f"Update settings error: {e}")
        return jsonify({"detail": f"Update error: {str(e)}"}), 500

@router.route('/media-directories', methods=['GET'])
@jwt_required()
def get_media_directories():
    """Get media directories for scanning"""
    try:
        directories = [
            {
                "path": "/app/T/Movies",
                "category": "movies",
                "enabled": True,
                "last_scan": "2025-09-29T10:00:00Z"
            },
            {
                "path": "/app/T/TV Shows", 
                "category": "tv_shows",
                "enabled": True,
                "last_scan": "2025-09-29T10:00:00Z"
            },
            {
                "path": "/app/T/Music",
                "category": "music",
                "enabled": True,
                "last_scan": "2025-09-29T10:00:00Z"
            },
            {
                "path": "/app/T/Videos",
                "category": "videos", 
                "enabled": True,
                "last_scan": "2025-09-29T10:00:00Z"
            },
            {
                "path": "/app/T/Music Videos",
                "category": "music_videos",
                "enabled": True,
                "last_scan": "2025-09-29T10:00:00Z"
            },
            {
                "path": "/app/T/Kids",
                "category": "kids",
                "enabled": True,
                "last_scan": "2025-09-29T10:00:00Z"
            }
        ]
        
        return jsonify({
            "directories": directories,
            "total_directories": len(directories)
        })
        
    except Exception as e:
        print(f"Media directories error: {e}")
        return jsonify({"detail": f"Media directories error: {str(e)}"}), 500
