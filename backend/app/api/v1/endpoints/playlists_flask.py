"""
Flask-compatible playlist endpoints extracted from working flask_simple.py
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from postgres_config import get_db_connection

router = Blueprint('playlists', __name__)

@router.route('/', methods=['GET'])
@jwt_required()
def get_playlists():
    """Get user's playlists"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.is_public, p.created_at,
                   COUNT(pi.id) as item_count
            FROM playlists p
            LEFT JOIN playlist_items pi ON p.id = pi.playlist_id
            WHERE p.owner_id = %s AND p.is_deleted = FALSE
            GROUP BY p.id, p.name, p.description, p.is_public, p.created_at
            ORDER BY p.created_at DESC
        """, (user_id,))
        
        playlists = []
        for row in cursor.fetchall():
            playlist = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'is_public': row['is_public'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'item_count': row['item_count']
            }
            playlists.append(playlist)
        
        return jsonify(playlists)
        
    except Exception as e:
        print(f"Playlists error: {e}")
        return jsonify({"detail": f"Playlists error: {str(e)}"}), 500

@router.route('/', methods=['POST'])
@jwt_required()
def create_playlist():
    """Create new playlist"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        is_public = data.get('is_public', False)
        
        if not name:
            return jsonify({"detail": "Playlist name is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO playlists (name, description, is_public, owner_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, description, is_public, created_at
        """, (name, description, is_public, user_id))
        
        playlist = cursor.fetchone()
        conn.commit()
        
        return jsonify({
            'id': playlist['id'],
            'name': playlist['name'],
            'description': playlist['description'],
            'is_public': playlist['is_public'],
            'created_at': playlist['created_at'].isoformat() if playlist['created_at'] else None,
            'item_count': 0
        }), 201
        
    except Exception as e:
        print(f"Create playlist error: {e}")
        return jsonify({"detail": f"Create playlist error: {str(e)}"}), 500

@router.route('/<playlist_id>/items', methods=['POST'])
@jwt_required()
def add_playlist_item(playlist_id):
    """Add item to playlist"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        media_id = data.get('media_id')
        if not media_id:
            return jsonify({"detail": "media_id is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify playlist ownership
        cursor.execute("SELECT owner_id FROM playlists WHERE id = %s AND is_deleted = FALSE", (playlist_id,))
        playlist = cursor.fetchone()
        
        if not playlist:
            return jsonify({"detail": "Playlist not found"}), 404
        
        if playlist['owner_id'] != int(user_id):
            return jsonify({"detail": "Not authorized to modify this playlist"}), 403
        
        # Verify media exists
        cursor.execute("SELECT id FROM media_files WHERE id = %s AND is_deleted = FALSE", (media_id,))
        if not cursor.fetchone():
            return jsonify({"detail": "Media not found"}), 404
        
        # Check if already in playlist
        cursor.execute("SELECT id FROM playlist_items WHERE playlist_id = %s AND media_id = %s", 
                      (playlist_id, media_id))
        if cursor.fetchone():
            return jsonify({"detail": "Media already in playlist"}), 409
        
        # Get next position
        cursor.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM playlist_items WHERE playlist_id = %s", 
                      (playlist_id,))
        position = cursor.fetchone()[0]
        
        # Add to playlist
        cursor.execute("""
            INSERT INTO playlist_items (playlist_id, media_id, position)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (playlist_id, media_id, position))
        
        item_id = cursor.fetchone()['id']
        conn.commit()
        
        return jsonify({
            'id': item_id,
            'playlist_id': playlist_id,
            'media_id': media_id,
            'position': position
        }), 201
        
    except Exception as e:
        print(f"Add playlist item error: {e}")
        return jsonify({"detail": f"Add playlist item error: {str(e)}"}), 500

@router.route('/<playlist_id>/items', methods=['GET'])
@jwt_required()
def get_playlist_items(playlist_id):
    """Get playlist items"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify playlist access
        cursor.execute("""
            SELECT owner_id, is_public FROM playlists 
            WHERE id = %s AND is_deleted = FALSE
        """, (playlist_id,))
        playlist = cursor.fetchone()
        
        if not playlist:
            return jsonify({"detail": "Playlist not found"}), 404
        
        if not playlist['is_public'] and playlist['owner_id'] != int(user_id):
            return jsonify({"detail": "Not authorized to view this playlist"}), 403
        
        # Get playlist items with media details
        cursor.execute("""
            SELECT pi.id, pi.position, pi.added_at,
                   m.id as media_id, m.filename, m.title, m.duration_seconds,
                   m.category, m.file_size
            FROM playlist_items pi
            JOIN media_files m ON pi.media_id = m.id
            WHERE pi.playlist_id = %s AND m.is_deleted = FALSE
            ORDER BY pi.position
        """, (playlist_id,))
        
        items = []
        for row in cursor.fetchall():
            item = {
                'id': row['id'],
                'position': row['position'],
                'added_at': row['added_at'].isoformat() if row['added_at'] else None,
                'media': {
                    'id': row['media_id'],
                    'filename': row['filename'],
                    'title': row['title'],
                    'duration_seconds': row['duration_seconds'],
                    'category': row['category'],
                    'file_size': row['file_size']
                }
            }
            items.append(item)
        
        return jsonify({
            'playlist_id': playlist_id,
            'items': items,
            'total_items': len(items)
        })
        
    except Exception as e:
        print(f"Get playlist items error: {e}")
        return jsonify({"detail": f"Get playlist items error: {str(e)}"}), 500
