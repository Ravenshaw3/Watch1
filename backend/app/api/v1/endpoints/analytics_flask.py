"""
Flask-compatible analytics endpoints extracted from working flask_simple.py
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from postgres_config import get_db_connection

router = Blueprint('analytics', __name__)

@router.route('/dashboard', methods=['GET'])
@jwt_required()
def get_analytics_dashboard():
    """Get analytics dashboard data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total media count
        cursor.execute("SELECT COUNT(*) as count FROM media_files WHERE is_deleted = FALSE")
        total_media = cursor.fetchone()['count']
        
        # Get media by category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM media_files 
            WHERE is_deleted = FALSE 
            GROUP BY category
        """)
        categories = {}
        for row in cursor.fetchall():
            categories[row['category']] = row['count']
        
        # Get total file size
        cursor.execute("SELECT SUM(file_size) as total_size FROM media_files WHERE is_deleted = FALSE")
        total_size_result = cursor.fetchone()['total_size']
        total_size = total_size_result if total_size_result else 0
        
        # Get total duration
        cursor.execute("SELECT SUM(duration_seconds) as total_duration FROM media_files WHERE is_deleted = FALSE AND duration_seconds IS NOT NULL")
        total_duration_result = cursor.fetchone()['total_duration']
        total_duration = total_duration_result if total_duration_result else 0
        
        # Get recent additions (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as count FROM media_files 
            WHERE is_deleted = FALSE 
            AND created_at >= NOW() - INTERVAL '30 days'
        """)
        recent_additions = cursor.fetchone()['count']
        
        # Get playlist count
        cursor.execute("SELECT COUNT(*) as count FROM playlists WHERE is_deleted = FALSE")
        total_playlists = cursor.fetchone()['count']
        
        return jsonify({
            "overview": {
                "total_media_files": total_media,
                "total_playlists": total_playlists,
                "total_storage_bytes": total_size,
                "total_duration_seconds": total_duration,
                "recent_additions_30_days": recent_additions
            },
            "categories": categories,
            "storage": {
                "total_bytes": total_size,
                "formatted_size": f"{total_size / (1024**3):.2f} GB" if total_size > 0 else "0 GB"
            },
            "activity": {
                "recent_additions": recent_additions,
                "avg_file_size": total_size // total_media if total_media > 0 else 0
            }
        })
        
    except Exception as e:
        print(f"Analytics error: {e}")
        return jsonify({"detail": f"Analytics error: {str(e)}"}), 500
