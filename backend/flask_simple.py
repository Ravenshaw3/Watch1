"""
Watch1 Media Server v3.0.3 - PostgreSQL Production Stack
Complete API implementation with async maintenance jobs and frontend polling
- Async maintenance job queue with worker health endpoints
- Comprehensive authentication and media streaming support
- Vue 3 frontend with real-time maintenance dashboard integration
- HLS generation support with FFmpeg, including manifest and segment routes
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
# SQLite removed - using PostgreSQL only
import bcrypt
import os
import uuid
import io
import mimetypes
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from routes import register_blueprints
from hls_utils import authorize_optional_token, cleanup_stale_outputs, ensure_hls_manifest, HLS_OUTPUT_ROOT
from config_loader import load_media_config, ConfigError

# Create Flask app
load_dotenv()

try:
    MEDIA_CONFIG = load_media_config()
except ConfigError as config_error:
    raise RuntimeError(f"Failed to load media configuration: {config_error}") from config_error

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 2048  # 2GB uploads
app.config['MEDIA_CATALOG'] = MEDIA_CONFIG

jwt_secret = os.getenv('JWT_SECRET_KEY')
if not jwt_secret or len(jwt_secret) < 32:
    raise RuntimeError('JWT_SECRET_KEY environment variable must be set to a secure value of at least 32 characters')

app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=8)

# Initialize extensions
default_cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:4173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4173"
]

CORS(
    app,
    resources={r"/api/*": {"origins": default_cors_origins}},
    supports_credentials=True,
    expose_headers=[
        'Content-Type',
        'Content-Length',
        'Accept-Ranges',
        'Content-Range',
        'Range'
    ],
    allow_headers=[
        'Authorization',
        'Content-Type',
        'Range',
        'Origin',
        'X-Requested-With'
    ],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)

@app.after_request
def add_security_headers(response):
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), browsing-topics=(), interest-cohort=()'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

jwt = JWTManager(app)

# Import PostgreSQL database configuration
from postgres_config import get_db_connection, test_db_connection
from maintenance import tasks as maintenance_tasks

register_blueprints(app)

# ===== AUTHENTICATION ROUTES =====


@app.route('/api/v1/auth/login/access-token', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            email = data.get('username') or data.get('email')  # Accept both username and email
            password = data.get('password')
        else:
            email = request.form.get('username') or request.form.get('email')  # Accept both
            password = request.form.get('password')

        if not email or not password:
            return jsonify({"detail": "Email and password required"}), 400

        # Simple authentication check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"detail": "User not found"}), 400

        stored_hash = user.get('password_hash') or user.get('hashed_password')
        if not stored_hash:
            return jsonify({"detail": "User password not configured"}), 400

        import hashlib
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if stored_hash != password_hash:
            return jsonify({"detail": "Incorrect password"}), 400

        # Create access token
        access_token = create_access_token(identity=user['id'])

        return jsonify({
            "access_token": access_token,
            "token_type": "bearer"
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"detail": f"Login error: {str(e)}"}), 500

@app.route('/api/v1/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        print(f"Looking up user with ID: {user_id}")  # Debug log
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print(f"User not found in database for ID: {user_id}")  # Debug log
            return jsonify({"detail": "User not found"}), 404
        
        user_email = user.get('email')
        print(f"User found: {user_email}")  # Debug log

        return jsonify({
            "id": user['id'],
            "username": user_email,
            "email": user_email,
            "full_name": user_email,
            "is_superuser": bool(user.get('is_superuser', False)),
            "is_active": bool(user.get('is_active', False))
        })
        
    except Exception as e:
        print(f"User lookup error: {e}")
        return jsonify({"detail": f"User error: {str(e)}"}), 500

# ===== SETTINGS ROUTES (THE MAIN FOCUS!) =====

@app.route('/api/v1/settings/test', methods=['GET'])
def settings_test():
    """Test settings endpoint"""
    return jsonify({
        "message": "Settings router is working in Flask!",
        "status": "success",
        "framework": "Flask",
        "timestamp": "2025-09-17"
    })

@app.route('/api/v1/settings/', methods=['GET'])
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
            "database": {
                "auto_backup_enabled": True,
                "backup_interval_hours": 168,
                "backup_retention_days": 30,
                "auto_cleanup_enabled": True,
                "cleanup_interval_hours": 24,
                "auto_vacuum_enabled": True,
                "vacuum_interval_hours": 168
            },
            "ui": {
                "default_page_size": 24,
                "max_page_size": 100,
                "default_sort_order": "alphabetical",
                "show_file_sizes": True,
                "show_duration": True,
                "show_ratings": True,
                "theme": "dark"
            },
            "streaming": {
                "default_quality": "original",
                "enable_transcoding": False,
                "transcode_quality": "medium",
                "cache_enabled": True,
                "cache_size_gb": 10,
                "max_concurrent_streams": 5
            }
        }
        
        return jsonify(settings)
        
    except Exception as e:
        print(f"Settings error: {e}")
        return jsonify({"detail": f"Settings error: {str(e)}"}), 500

@app.route('/api/v1/settings/', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update settings"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT is_superuser FROM users WHERE id = %s',
                (user_id,),
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        settings_data = request.get_json()
        
        # For now, just return success - we'll implement actual saving later
        return jsonify({
            "message": "Settings updated successfully",
            "status": "success"
        })
        
    except Exception as e:
        print(f"Update settings error: {e}")
        return jsonify({"detail": f"Update error: {str(e)}"}), 500

@app.route('/api/v1/settings/initialize', methods=['POST'])
@jwt_required()
def initialize_settings():
    """Initialize settings"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT is_superuser FROM users WHERE id = %s',
                (user_id,),
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        return jsonify({
            "message": "Settings initialized successfully",
            "status": "success",
            "initialized_categories": [
                "media_locations",
                "scanning",
                "database", 
                "ui",
                "streaming"
            ]
        })
        
    except Exception as e:
        print(f"Initialize error: {e}")
        return jsonify({"detail": f"Initialize error: {str(e)}"}), 500

@app.route('/api/v1/settings/media-directories', methods=['GET'])
@jwt_required()
def get_media_directories():
    """Get media directories for scanning"""
    try:
        directories = [
            "/app/T/Movies",
            "/app/T/TV Shows", 
            "/app/T/Music",
            "/app/T/Videos",
            "/app/T/Music Videos",
            "/app/T/Kids"
        ]
        
        return jsonify({
            "directories": directories,
            "settings": {
                "movies": "/app/T/Movies",
                "tv_shows": "/app/T/TV Shows",
                "music": "/app/T/Music",
                "videos": "/app/T/Videos",
                "music_videos": "/app/T/Music Videos",
                "kids": "/app/T/Kids"
            },
            "total_directories": len(directories)
        })
        
    except Exception as e:
        print(f"Media directories error: {e}")
        return jsonify({"detail": f"Media directories error: {str(e)}"}), 500

# ===== MEDIA ROUTES =====

@app.route('/api/v1/media/', methods=['GET'])
@jwt_required()
def get_media():
    """Get media files with pagination"""
    try:
        page = int(request.args.get('page', 1) or 1)
        # Support both limit and page_size query params for compatibility
        raw_limit = request.args.get('limit') or request.args.get('page_size') or 24
        limit = max(int(raw_limit), 1)

        category = request.args.get('category')
        search_term = request.args.get('search')
        sort_by_param = (request.args.get('sort_by') or 'filename').lower()
        sort_order_param = (request.args.get('sort_order') or 'asc').lower()

        sort_columns = {
            'filename': 'filename',
            'created_at': 'created_at',
            'file_size': 'file_size',
            'duration': 'duration_seconds'
        }
        sort_column = sort_columns.get(sort_by_param, 'filename')
        sort_direction = 'DESC' if sort_order_param == 'desc' else 'ASC'

        filters = ['is_deleted = FALSE']
        params = []

        if category:
            filters.append('category = %s')
            params.append(category)

        if search_term:
            filters.append('(' \
                           'filename ILIKE %s OR ' \
                           'COALESCE(filename, \'\') ILIKE %s OR ' \
                           'COALESCE(title, \'\') ILIKE %s' \
                           ')')
            like_term = f"%{search_term}%"
            params.extend([like_term, like_term, like_term])

        where_clause = ' AND '.join(filters)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Get total count
            count_query = f'SELECT COUNT(*) AS count FROM media_files WHERE {where_clause}'
            cursor.execute(count_query, tuple(params))
            count_row = cursor.fetchone()
            total_count = count_row['count'] if count_row else 0

            # Get paginated media files
            offset = (page - 1) * limit
            data_query = f'''
                SELECT id, filename, title, file_path, category, file_size,
                       duration_seconds, poster_path, poster_content_type,
                       poster_data, thumbnail_path, created_at
                FROM media_files
                WHERE {where_clause}
                ORDER BY {sort_column} {sort_direction}
                LIMIT %s OFFSET %s
            '''
            cursor.execute(data_query, tuple(params + [limit, offset]))
            media_files = cursor.fetchall()

            # Convert to list of dicts
            items = []
            for media in media_files:
                # Clean up the filename to create a proper title
                title = media['filename']
                if title.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm')):
                    # Remove file extension
                    title = title.rsplit('.', 1)[0]

                # Clean up common patterns in movie filenames
                import re
                # Remove quality indicators
                title = re.sub(r'\b(720p|1080p|4K|BluRay|BRRip|DVDRip|WEBRip|HDTV)\b', '', title, flags=re.IGNORECASE)
                # Remove codec info
                title = re.sub(r'\b(x264|x265|H264|H265|HEVC|DivX|XviD)\b', '', title, flags=re.IGNORECASE)
                # Remove group tags
                title = re.sub(r'\[.*?\]', '', title)
                # Clean up extra spaces and dashes
                title = re.sub(r'[-_\s]+', ' ', title).strip()

                poster_data = media.get('poster_data')
                poster_base64 = None
                if poster_data:
                    import base64
                    poster_base64 = base64.b64encode(poster_data).decode('utf-8')

                items.append({
                    "id": media['id'],
                    "title": title,
                    "filename": media['filename'],
                    "file_path": media['file_path'],
                    "category": media['category'],
                    "file_size": media['file_size'],
                    "duration": media.get('duration_seconds'),
                    "poster_path": media['poster_path'],
                    "poster_content_type": media.get('poster_content_type'),
                    "poster_inline": poster_base64,
                    "thumbnail_path": media['thumbnail_path'],
                    "created_at": media['created_at']
                })

            # Get categories count for frontend compatibility
            categories_count = {}
            try:
                cursor.execute('''
                    SELECT category, COUNT(*) AS count
                    FROM media_files 
                    GROUP BY category
                ''')
                category_rows = cursor.fetchall()

                print(f"Categories query returned {len(category_rows)} rows")
                for row in category_rows:
                    category_key = row['category'] or 'other'
                    categories_count[category_key] = row['count']
                    print(f"Category: {category_key} = {row['count']}")
            except Exception as e:
                print(f"Categories query error: {e}")
                categories_count = {"movies": total_count}  # Fallback
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({
            "items": items,
            "total": total_count,
            "page": page,
            "page_size": limit,
            "total_pages": (total_count + limit - 1) // limit,
            "categories": categories_count
        })
        
    except Exception as e:
        print(f"Media error: {e}")
        return jsonify({"detail": f"Media error: {str(e)}"}), 500

@app.route('/api/v1/media/<media_id>', methods=['GET'])
@jwt_required()
def get_media_by_id(media_id):
    """Get individual media file by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM media_files WHERE id = %s', (media_id,))
        media = cursor.fetchone()
        conn.close()
        
        if not media:
            return jsonify({"detail": "Media not found"}), 404
        
        # Convert to dict and return
        media_dict = dict(media)
        return jsonify(media_dict)
        
    except Exception as e:
        print(f"Get media by ID error: {e}")
        return jsonify({"detail": f"Get media by ID error: {str(e)}"}), 500

@app.route('/api/v1/media/<media_id>/stream', methods=['GET', 'HEAD', 'OPTIONS'])
@jwt_required(optional=True)  # Allow token in query parameter
def stream_media(media_id):
    """Stream media file with range request support"""
    try:
        token = request.args.get('token')
        if token:
            from flask_jwt_extended import decode_token
            try:
                decode_token(token)
            except Exception:
                return jsonify({"detail": "Invalid token"}), 401

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM media_files WHERE id = %s', (media_id,))
            media = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not media:
            return jsonify({"detail": "Media not found"}), 404

        file_path = media.get('file_path') if isinstance(media, dict) else media['file_path']
        if not file_path:
            return jsonify({"detail": "Media file path is missing."}), 500

        if file_path.startswith('T:'):
            file_path = file_path.replace('T:', '/app/T').replace('\\', '/')
        elif file_path.startswith('C:'):
            file_path = file_path.replace('C:', '/app/C').replace('\\', '/')
        else:
            file_path = file_path.replace('\\', '/')

        if not os.path.exists(file_path):
            return jsonify({"detail": f"File not found: {file_path}"}), 404

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            lower_path = file_path.lower()
            if lower_path.endswith(('.mkv', '.mk3d')):
                mime_type = 'video/x-matroska'
            elif lower_path.endswith('.avi'):
                mime_type = 'video/x-msvideo'
            elif lower_path.endswith('.mov'):
                mime_type = 'video/quicktime'
            elif lower_path.endswith('.webm'):
                mime_type = 'video/webm'
            else:
                mime_type = 'video/mp4'

        if request.method == 'HEAD':
            response = app.response_class()
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Length'] = str(os.path.getsize(file_path))
            response.headers['Content-Type'] = mime_type
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Vary'] = 'Origin'
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Expose-Headers'] = 'Accept-Ranges, Content-Length, Content-Type'
            response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
            return response

        if request.method == 'OPTIONS':
            response = app.response_class()
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Range, Authorization, Content-Type'
            response.headers['Access-Control-Expose-Headers'] = 'Accept-Ranges, Content-Length, Content-Type'
            response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
            return response

        response = send_file(
            file_path,
            as_attachment=False,
            conditional=True,
            mimetype=mime_type,
            download_name=os.path.basename(file_path)
        )
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Type'] = mime_type
        response.headers['Access-Control-Expose-Headers'] = 'Accept-Ranges, Content-Length, Content-Type'
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
        return response

    except Exception as e:
        print(f"Stream error: {e}")
        return jsonify({"detail": f"Media error: {str(e)}"}), 500
@app.route('/api/v1/media/<media_id>/hls/master.m3u8', methods=['GET'])
@jwt_required(optional=True)
def hls_manifest(media_id: str):
    """Serve or generate HLS manifest for the requested media."""
    try:
        token = request.args.get('token')
        is_valid, error_detail = authorize_optional_token(token)
        if not is_valid:
            return jsonify({"detail": f"Invalid token: {error_detail}"}), 401

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM media_files WHERE id = %s', (media_id,))
            media = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not media:
            return jsonify({"detail": "Media not found"}), 404

        file_path = media.get('file_path') if isinstance(media, dict) else media['file_path']
        if not file_path:
            return jsonify({"detail": "Media file path is missing."}), 500

        normalized_path = file_path.replace('\\', '/')
        if normalized_path.startswith('T:'):
            normalized_path = normalized_path.replace('T:', '/app/T')
        elif normalized_path.startswith('C:'):
            normalized_path = normalized_path.replace('C:', '/app/C')

        if not os.path.exists(normalized_path):
            return jsonify({"detail": f"File not found: {normalized_path}"}), 404

        manifest_path = ensure_hls_manifest(media_id, normalized_path)
        cleanup_stale_outputs()

        response = send_file(
            manifest_path,
            mimetype='application/vnd.apple.mpegurl',
            as_attachment=False,
            conditional=False
        )
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type'
        response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
        return response

    except RuntimeError as gen_error:
        return jsonify({"detail": str(gen_error)}), 500
    except Exception as e:
        print(f"HLS manifest error: {e}")
        return jsonify({"detail": f"HLS error: {str(e)}"}), 500


@app.route('/api/v1/media/<media_id>/hls/<path:resource>', methods=['GET'])
@jwt_required(optional=True)
def hls_resource(media_id: str, resource: str):
    """Serve HLS segment or auxiliary resource."""
    try:
        token = request.args.get('token')
        is_valid, error_detail = _authorize_optional_token(token)
        if not is_valid:
            return jsonify({"detail": f"Invalid token: {error_detail}"}), 401

        resource_root = (HLS_OUTPUT_ROOT / media_id).resolve()
        requested_path = (resource_root / resource).resolve()

        if not str(requested_path).startswith(str(resource_root)):
            return jsonify({"detail": "Invalid resource path"}), 400

        if not requested_path.exists():
            return jsonify({"detail": "Segment not found"}), 404

        mimetype = 'application/octet-stream'
        if requested_path.suffix == '.ts':
            mimetype = 'video/mp2t'
        elif requested_path.suffix in {'.m3u8', '.m3u'}:
            mimetype = 'application/vnd.apple.mpegurl'

        response = send_file(
            requested_path,
            mimetype=mimetype,
            as_attachment=False,
            conditional=False
        )
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type'
        response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
        return response

    except Exception as e:
        print(f"HLS resource error: {e}")
        return jsonify({"detail": f"HLS resource error: {str(e)}"}), 500


@app.route('/api/v1/media/categories', methods=['GET'])
@jwt_required()
def get_media_categories():
    """Get media categories with counts"""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM media_files
                WHERE is_deleted = FALSE
                GROUP BY category
                ORDER BY category
            ''')
            categories = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        
        category_list = []
        for cat in categories:
            category_name = cat['category'] or 'other'
            category_list.append({
                "name": category_name,
                "display_name": category_name.title(),
                "count": cat['count']
            })
        
        return jsonify({"categories": category_list})
        
    except Exception as e:
        print(f"Scan info error: {e}")
        return jsonify({"detail": f"Scan info error: {str(e)}"}), 500

# ===== PLAYLIST ROUTES =====

@app.route('/api/v1/playlists/', methods=['GET'])
@jwt_required()
def get_playlists():
    """Get user's playlists"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM playlists 
                WHERE created_by = %s OR is_public = TRUE
                ORDER BY created_at DESC
            ''', (user_id,))
            playlists = cursor.fetchall()

            items = []
            for playlist in playlists:
                cursor.execute('''
                    SELECT COUNT(*) AS item_count
                    FROM playlist_items 
                    WHERE playlist_id = %s
                ''', (playlist['id'],))
                count_row = cursor.fetchone()
                item_count = count_row['item_count'] if count_row else 0

                items.append({
                    "id": playlist['id'],
                    "name": playlist['name'],
                    "description": playlist['description'],
                    "is_public": bool(playlist['is_public']),
                    "owner_id": playlist['created_by'],  # Map created_by to owner_id for frontend compatibility
                    "created_at": playlist['created_at'],
                    "updated_at": playlist['updated_at'],
                    "items": [{"count": item_count}] * item_count  # Mock items array for count
                })
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({"playlists": items, "total": len(items)})
        
    except Exception as e:
        print(f"Playlists error: {e}")
        return jsonify({"detail": f"Playlists error: {str(e)}"}), 500

@app.route('/api/v1/playlists/', methods=['POST'])
@jwt_required()
def create_playlist():
    """Create new playlist"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        is_public = data.get('is_public', False)
        
        if not name:
            return jsonify({"detail": "Playlist name is required"}), 400
        
        # Generate simple ID
        playlist_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO playlists (id, name, description, is_public, created_by, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            ''', (playlist_id, name, description, is_public, user_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({
            "id": playlist_id,
            "name": name,
            "description": description,
            "is_public": is_public,
            "owner_id": user_id,  # Return as owner_id for frontend compatibility
            "message": "Playlist created successfully"
        })
        
    except Exception as e:
        print(f"Create playlist error: {e}")
        return jsonify({"detail": f"Create playlist error: {str(e)}"}), 500

@app.route('/api/v1/playlists/<playlist_id>/items', methods=['POST'])
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
        try:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM playlists 
                WHERE id = %s AND (created_by = %s OR is_public = TRUE)
            ''', (playlist_id, user_id))
            playlist = cursor.fetchone()

            if not playlist:
                return jsonify({"detail": "Playlist not found or access denied"}), 404

            cursor.execute('SELECT id FROM media_files WHERE id = %s', (media_id,))
            media = cursor.fetchone()
            if not media:
                return jsonify({"detail": "Media not found"}), 404

            cursor.execute('''
                SELECT id FROM playlist_items 
                WHERE playlist_id = %s AND media_id = %s
            ''', (playlist_id, media_id))
            existing = cursor.fetchone()

            if existing:
                return jsonify({"detail": "Item already in playlist"}), 400

            item_id = str(uuid.uuid4())
            cursor.execute('''
                SELECT COALESCE(MAX(position), 0) + 1 AS next_position
                FROM playlist_items 
                WHERE playlist_id = %s
            ''', (playlist_id,))
            pos_row = cursor.fetchone()
            position = pos_row['next_position'] if pos_row else 1

            cursor.execute('''
                INSERT INTO playlist_items (id, playlist_id, media_id, position, added_by, added_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            ''', (item_id, playlist_id, media_id, position, user_id))

            cursor.execute('''
                UPDATE playlists SET updated_at = NOW() 
                WHERE id = %s
            ''', (playlist_id,))

            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({
            "id": item_id,
            "playlist_id": playlist_id,
            "media_id": media_id,
            "position": position,
            "message": "Item added to playlist successfully"
        })
        
    except Exception as e:
        print(f"Add playlist item error: {e}")
        return jsonify({"detail": f"Add playlist item error: {str(e)}"}), 500

@app.route('/api/v1/playlists/<playlist_id>/items', methods=['GET'])
@jwt_required()
def get_playlist_items(playlist_id):
    """Get playlist items"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM playlists
                WHERE id = %s AND (created_by = %s OR is_public = 1)
            ''', (playlist_id, user_id))
            playlist = cursor.fetchone()

            if not playlist:
                return jsonify({"detail": "Playlist not found or access denied"}), 404

            cursor.execute('''
                SELECT pi.id, pi.position, pi.added_at,
                       mf.id as media_id, mf.filename, mf.title, mf.duration,
                       mf.category, mf.file_size
                FROM playlist_items pi
                JOIN media_files mf ON pi.media_id = mf.id
                WHERE pi.playlist_id = %s
                ORDER BY pi.position
            ''', (playlist_id,))
            items = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        
        media_items = []
        for item in items:
            # Clean up the filename to create a proper title
            title = item['filename']
            if title.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm')):
                # Remove file extension
                title = title.rsplit('.', 1)[0]
            
            # Clean up common patterns in movie filenames
            import re
            # Remove quality indicators
            title = re.sub(r'\b(720p|1080p|4K|BluRay|BRRip|DVDRip|WEBRip|HDTV)\b', '', title, flags=re.IGNORECASE)
            # Remove codec info
            title = re.sub(r'\b(x264|x265|H264|H265|HEVC|DivX|XviD)\b', '', title, flags=re.IGNORECASE)
            # Remove group tags
            title = re.sub(r'\[.*?\]', '', title)
            # Clean up extra spaces and dashes
            title = re.sub(r'[-_\s]+', ' ', title).strip()
            
            media_items.append({
                "id": item['media_id'],
                "filename": item['filename'],
                "title": title,
                "duration": item['duration'],
                "category": item['category'],
                "file_size": item['file_size'],
                "position": item['position'],
                "added_at": item['added_at']
            })
        
        return jsonify({
            "playlist_id": playlist_id,
            "media": media_items,
            "total": len(media_items)
        })
        
    except Exception as e:
        print(f"Get playlist items error: {e}")
        return jsonify({"detail": f"Get playlist items error: {str(e)}"}), 500

# ===== ANALYTICS ROUTES =====

@app.route('/api/v1/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_analytics_dashboard():
    """Get analytics dashboard data"""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) AS count FROM media_files WHERE is_deleted = FALSE')
            media_row = cursor.fetchone()
            total_media = media_row['count'] if media_row else 0

            cursor.execute('SELECT COUNT(*) AS count FROM users WHERE is_active = TRUE')
            users_row = cursor.fetchone()
            total_users = users_row['count'] if users_row else 0

            cursor.execute('SELECT COUNT(*) AS count FROM playlists')
            playlists_row = cursor.fetchone()
            total_playlists = playlists_row['count'] if playlists_row else 0

            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM media_files 
                WHERE is_deleted = FALSE 
                GROUP BY category
            ''')
            categories = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        
        category_stats = {}
        for cat in categories:
            category_stats[cat['category']] = cat['count']
        
        return jsonify({
            "total_media_files": total_media,
            "total_users": total_users,
            "total_playlists": total_playlists,
            "media_by_category": category_stats,
            "recent_activity": [],  # Placeholder
            "storage_usage": {
                "total_size_gb": 0,  # Placeholder
                "available_space_gb": 0  # Placeholder
            }
        })
        
    except Exception as e:
        print(f"Analytics error: {e}")
        return jsonify({"detail": f"Analytics error: {str(e)}"}), 500

# ===== VERSION & HEALTH ROUTES =====

@app.route('/api/v1/version', methods=['GET'])
def get_version():
    """Version endpoint"""
    return jsonify({
        "version": "3.0.3",
        "framework": "Flask",
        "build_date": "2025-09-25",
        "api_version": "v1",
        "features": [
            "Unraid Production Deployment Ready",
            "CORS Policy Fixes for Cross-Origin Requests",
            "Permissions-Policy Headers Configured",
            "TypeScript Interface Compatibility Resolved",
            "Enhanced JWT Authentication System",
            "Complete CRUD Operations for Media & Playlists",
            "Advanced Video Streaming with Range Requests",
            "Real-time Media Library Management",
            "Secure User Authentication & Authorization",
            "RESTful API with Comprehensive Testing",
            "SQLite Database with Full Schema",
            "CORS-enabled Cross-Origin Support",
            "Comprehensive Error Handling & Logging",
            "Vue.js 3 Frontend with TypeScript",
            "Mobile App Foundation (React Native)",
            "Advanced Player Features",
            "Subtitle Support (.srt, .vtt, .ass, .ssa, .sub)",
            "Picture-in-Picture Mode",
            "Multiple Audio Tracks",
            "Auto-Advance with Countdown"
        ]
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Watch1 Media Server v3.0.3 - Unraid Production Deployment Ready!",
        "version": "3.0.3",
        "framework": "Flask",
        "status": "healthy"
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "version": "3.0.3",
        "framework": "Flask",
        "database": "SQLite"
    })

# ===== CORS HANDLERS =====

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Flask-CORS handles after_request automatically

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"detail": "Internal Server Error"}), 500

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"detail": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"detail": "Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"detail": "Authorization token is required"}), 401

# ============================================================================
# SUBTITLE ENDPOINTS
# ============================================================================

@app.route('/api/v1/media/<media_id>/subtitles', methods=['GET'])
@jwt_required()
def get_media_subtitles(media_id):
    """Get all subtitles for a media file"""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT file_path FROM media_files WHERE id = %s', (media_id,))
            media = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not media:
            return jsonify({"detail": "Media file not found"}), 404

        file_path = media['file_path']
        media_path = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        subtitles = []
        supported_formats = ['.srt', '.vtt', '.ass', '.ssa', '.sub']
        
        # Look for subtitle files
        if os.path.exists(media_path):
            for filename in os.listdir(media_path):
                if filename.startswith(base_name):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in supported_formats:
                        subtitle_path = os.path.join(media_path, filename)
                        if os.path.exists(subtitle_path):
                            # Extract language from filename
                            language = extract_language_from_filename(filename)
                            
                            subtitle_info = {
                                "id": filename,
                                "filename": filename,
                                "language": language,
                                "format": file_ext,
                                "size": os.path.getsize(subtitle_path),
                                "url": f"/api/v1/media/{media_id}/subtitles/{filename}"
                            }
                            subtitles.append(subtitle_info)
        
        return jsonify(subtitles)
        
    except Exception as e:
        return jsonify({"detail": f"Failed to get subtitles: {str(e)}"}), 500

@app.route('/api/v1/media/<media_id>/subtitles/<subtitle_filename>', methods=['GET'])
@jwt_required()
def get_subtitle_file(media_id, subtitle_filename):
    """Serve subtitle file"""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT file_path FROM media_files WHERE id = %s', (media_id,))
            media = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if not media:
            return jsonify({"detail": "Media file not found"}), 404

        file_path = media['file_path']
        media_path = os.path.dirname(file_path)
        subtitle_path = os.path.join(media_path, subtitle_filename)
        
        if not os.path.exists(subtitle_path):
            return jsonify({"detail": "Subtitle file not found"}), 404
        
        # Determine MIME type
        file_ext = os.path.splitext(subtitle_filename)[1].lower()
        if file_ext == '.vtt':
            mime_type = 'text/vtt'
        elif file_ext == '.srt':
            mime_type = 'text/plain; charset=utf-8'
        else:
            mime_type = 'text/plain; charset=utf-8'
        
        return send_file(
            subtitle_path,
            mimetype=mime_type,
            as_attachment=False,
            download_name=subtitle_filename
        )
        
    except Exception as e:
        return jsonify({"detail": f"Failed to serve subtitle: {str(e)}"}), 500

def extract_language_from_filename(filename):
    """Extract language code from filename"""
    import re
    
    # Common language patterns in filenames
    patterns = [
        r'\.([a-z]{2,3})\.(srt|vtt|ass|ssa|sub)$',  # .en.srt
        r'\.(english|spanish|french|german|italian|portuguese|russian|chinese|japanese|korean)\.(srt|vtt|ass|ssa|sub)$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            lang = match.group(1)
            # Convert full language names to codes
            lang_map = {
                'english': 'en', 'spanish': 'es', 'french': 'fr', 
                'german': 'de', 'italian': 'it', 'portuguese': 'pt',
                'russian': 'ru', 'chinese': 'zh', 'japanese': 'ja', 'korean': 'ko'
            }
            return lang_map.get(lang, lang)
    
    return 'unknown'

@app.route('/api/v1/media/scan-info', methods=['GET'])
@jwt_required()
def get_scan_info():
    """Get media scan information"""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) AS count FROM media_files WHERE is_deleted = FALSE')
            files_row = cursor.fetchone()
            total_files = files_row['count'] if files_row else 0

            cursor.execute('SELECT SUM(file_size) AS total_size FROM media_files WHERE is_deleted = FALSE')
            size_row = cursor.fetchone()
            total_size = size_row['total_size'] or 0 if size_row else 0

            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM media_files 
                WHERE is_deleted = FALSE 
                GROUP BY category
            ''')
            categories = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        
        category_stats = {}
        for cat in categories:
            category_name = cat['category'] or 'other'
            category_stats[category_name] = cat['count']
        
        return jsonify({
            "total_files": total_files,
            "total_size": total_size,
            "categories": category_stats,
            "last_scan": "Never",  # Placeholder
            "scan_status": "idle"
        })
        
    except Exception as e:
        print(f"Scan info error: {e}")
        return jsonify({"detail": f"Scan info error: {str(e)}"}), 500

@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serve thumbnail/poster images"""
    try:
        # Try thumbnails directory first
        thumbnail_path = os.path.join('/app/thumbnails', filename)
        if os.path.exists(thumbnail_path):
            return send_file(thumbnail_path)

        # If not found, try to find poster in media directories
        # This is a fallback for when thumbnails aren't generated yet
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT poster_path, thumbnail_path FROM media_files 
                WHERE poster_path LIKE %s OR thumbnail_path LIKE %s
            """, (f'%{filename}%', f'%{filename}%'))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if result:
            row = result if isinstance(result, dict) else dict(result)
            for key in ('poster_path', 'thumbnail_path'):
                file_path = row.get(key)
                if not file_path:
                    continue

                normalized_path = file_path.replace('\\', '/')
                if normalized_path.startswith('/thumbnails/'):
                    candidate = os.path.join('/app', normalized_path.lstrip('/'))
                    if os.path.exists(candidate):
                        print(f"Serving thumbnail from: {candidate}")
                        return send_file(candidate)

                if os.path.exists(file_path):
                    print(f"Serving image from: {file_path}")
                    return send_file(file_path)

        # Return 404 if not found
        return jsonify({'error': 'Thumbnail not found'}), 404

    except Exception as e:
        print(f"Error serving thumbnail {filename}: {e}")
        return jsonify({'error': 'Failed to serve thumbnail'}), 500

@app.route('/api/v1/media/<media_id>/poster')
@jwt_required(optional=True)
def serve_media_poster(media_id):
    """Serve poster/artwork for a specific media item"""
    try:
        # Check for token in query parameter (for image requests)
        token = request.args.get('token')
        if token:
            from flask_jwt_extended import decode_token
            try:
                decode_token(token)
            except:
                return jsonify({'error': 'Invalid token'}), 401
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT poster_path, thumbnail_path, poster_data, poster_content_type 
                FROM media_files 
                WHERE id = %s
            """, (media_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()

        if not result:
            conn.close()
            return jsonify({'error': 'Media not found'}), 404

        record = result if isinstance(result, dict) else dict(result)

        poster_blob = record.get('poster_data')
        if poster_blob:
            content_type = record.get('poster_content_type') or 'image/jpeg'
            conn.close()
            return send_file(io.BytesIO(poster_blob), mimetype=content_type)

        for path_key in ['poster_path', 'thumbnail_path']:
            file_path = record.get(path_key)
            if not file_path:
                continue

            print(f"Checking poster path: {file_path}")

            normalized_path = file_path.replace('\\', '/')
            if normalized_path.startswith('/thumbnails/'):
                thumbnail_candidate = os.path.join('/app', normalized_path.lstrip('/'))
                if os.path.exists(thumbnail_candidate):
                    print(f"Serving thumbnail from: {thumbnail_candidate}")
                    conn.close()
                    return send_file(thumbnail_candidate)

            if os.path.exists(file_path):
                print(f"Serving poster from: {file_path}")
                conn.close()
                return send_file(file_path)

            alt_cursor = conn.cursor()
            try:
                alt_cursor.execute("SELECT file_path FROM media_files WHERE id = %s", (media_id,))
                media_row = alt_cursor.fetchone()
            finally:
                alt_cursor.close()

            if media_row and media_row['file_path']:
                media_file_path = media_row['file_path'].replace('\\', '/')
                if media_file_path.startswith('T:'):
                    media_file_path = media_file_path.replace('T:', '/app/T')
                elif media_file_path.startswith('C:'):
                    media_file_path = media_file_path.replace('C:', '/app/C')

                media_dir = os.path.dirname(media_file_path)
                poster_jpg = os.path.join(media_dir, 'poster.jpg')
                print(f"Trying poster.jpg at: {poster_jpg}")
                if os.path.exists(poster_jpg):
                    print(f"Serving poster.jpg from: {poster_jpg}")
                    conn.close()
                    return send_file(poster_jpg)

        conn.close()
        return jsonify({'error': 'No poster available'}), 404

    except Exception as e:
        print(f"Error serving poster for {media_id}: {e}")
        return jsonify({'error': 'Failed to serve poster'}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint for container monitoring"""
    return jsonify({"status": "healthy", "service": "watch1-backend"})

if __name__ == '__main__':
    print("Starting Watch1 Flask Media Server (Simplified)...")
    print("Settings API will be available at:")
    print("  GET  /api/v1/settings/test")
    print("  GET  /api/v1/settings/")
    print("  POST /api/v1/settings/initialize")
    print("  GET  /api/v1/settings/media-directories")
    print("Access the server at: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
