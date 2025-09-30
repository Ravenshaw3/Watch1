"""
Flask-compatible media endpoints extracted from working flask_simple.py
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from postgres_config import get_db_connection
import os
import hashlib
import sys
from datetime import datetime
sys.path.append('/app')
from app.core.enhanced_scanner import EnhancedMediaScanner
from pathlib import Path

router = Blueprint('media', __name__)
@router.route('/', methods=['GET'])
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
            count_query = f"SELECT COUNT(*) as count FROM media_files WHERE {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()['count']

            # Get paginated results
            offset = (page - 1) * limit
            query = f"""
                SELECT id, filename, file_path, file_size, duration_seconds, 
                       category, created_at, title, year, rating, plot, 
                       director, genre, cast_list, runtime_minutes
                FROM media_files 
                WHERE {where_clause}
                ORDER BY {sort_column} {sort_direction}
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [limit, offset])
            rows = cursor.fetchall()

            # Convert to list of dicts
            media_items = []
            for row in rows:
                try:
                    item = {
                        'id': row['id'],
                        'filename': row['filename'],
                        'file_path': row['file_path'],
                        'file_size': row['file_size'],
                        'duration_seconds': row['duration_seconds'],
                        'category': row['category'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'title': row['title'],
                        'year': row['year'],
                        'rating': float(row['rating']) if row['rating'] else None,
                        'plot': row['plot'],
                        'director': row['director'],
                        'genre': row['genre'],
                        'cast_list': row['cast_list'],
                        'runtime_minutes': row['runtime_minutes']
                    }
                    media_items.append(item)
                except Exception as row_error:
                    print(f"Row processing error: {row_error}, Row: {dict(row)}")
                    continue

            # Get category counts
            cursor.execute("SELECT category, COUNT(*) as count FROM media_files WHERE is_deleted = FALSE GROUP BY category")
            category_rows = cursor.fetchall()
            categories = {row['category']: row['count'] for row in category_rows}

            return jsonify({
                'items': media_items,
                'total': total_count,
                'page': page,
                'page_size': limit,
                'categories': categories
            })
        finally:
            conn.close()

    except Exception as e:
        print(f"Media error: {e}")
        return jsonify({"detail": f"Media error: {str(e)}"}), 500

@router.route('/scan-info', methods=['GET'])
@jwt_required()
def get_scan_info():
    """Get media scan information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total files count
        cursor.execute("SELECT COUNT(*) as count FROM media_files WHERE is_deleted = FALSE")
        total_files = cursor.fetchone()['count']
        
        # Get total file size
        cursor.execute("SELECT SUM(file_size) as total_size FROM media_files WHERE is_deleted = FALSE")
        total_size_result = cursor.fetchone()['total_size']
        total_size = total_size_result if total_size_result else 0
        
        # Get category statistics
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM media_files 
            WHERE is_deleted = FALSE 
            GROUP BY category
        """)
        category_rows = cursor.fetchall()
        category_stats = {row['category']: row['count'] for row in category_rows}
        
        return jsonify({
            "total_files": total_files,
            "total_size": total_size,
            "categories": category_stats,
            "last_scan": "Never",
            "scan_status": "idle"
        })
        
    except Exception as e:
        print(f"Scan info error: {e}")
        return jsonify({"detail": f"Scan info error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    from datetime import datetime
    
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        # Get scan parameters
        data = request.get_json() or {}
        directory = data.get('directory', '/app/media')
        recalculate_categories = data.get('recalculate_categories', False)
        
        # Enhanced media directories configuration with storage formats
        # Now using direct Unraid mount at /app/media
        media_directories = [
            {
                'key': 'movies',
                'storage_format': 'collection',
                'root_path': '/app/media/Movies',
                'include_patterns': ['**/*.mp4', '**/*.mkv', '**/*.avi', '**/*.mov', '**/*.wmv']
            },
            {
                'key': 'tv_shows',
                'storage_format': 'series',
                'root_path': '/app/media/TV Shows',
                'hierarchy': {
                    'levels': [
                        {'name': 'series'},
                        {'name': 'season'},
                        {'name': 'episode'}
                    ]
                },
                'include_patterns': ['**/*.mp4', '**/*.mkv', '**/*.avi', '**/*.mov']
            },
            {
                'key': 'music',
                'storage_format': 'group',
                'root_path': '/app/media/Music',
                'hierarchy': {
                    'levels': [
                        {'name': 'artist'},
                        {'name': 'album'}
                    ]
                },
                'include_patterns': ['**/*.mp3', '**/*.flac', '**/*.wav', '**/*.m4a', '**/*.aac']
            },
            {
                'key': 'kids',
                'storage_format': 'collection',
                'root_path': '/app/media/Kids',
                'include_patterns': ['**/*.mp4', '**/*.mkv', '**/*.avi']
            },
            {
                'key': 'music_videos',
                'storage_format': 'collection',
                'root_path': '/app/media/Music Videos',
                'include_patterns': ['**/*.mp4', '**/*.mkv', '**/*.avi']
            },
            {
                'key': 'videos',
                'storage_format': 'collection',
                'root_path': '/app/media/Videos',
                'include_patterns': ['**/*.mp4', '**/*.mkv', '**/*.avi', '**/*.mov']
            }
        ]
        
        # Supported file extensions
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
        supported_extensions = video_extensions | audio_extensions
        
        total_files_found = 0
        files_added = 0
        files_updated = 0
        scan_results = {}
        
        # Initialize enhanced scanner
        scanner = EnhancedMediaScanner()
        
        # Scan each configured directory using enhanced scanner
        for dir_config in media_directories:
            category = dir_config['key']
            scan_path = dir_config['root_path']
            
            if not os.path.exists(scan_path):
                print(f"Directory does not exist: {scan_path}")
                continue
                
            print(f"Scanning directory: {scan_path} (category: {category}, format: {dir_config.get('storage_format', 'collection')})")
            
            try:
                # Use enhanced scanner
                result = scanner.scan_directory(dir_config)
                
                # Process scan results and update database
                dir_files_added = 0
                for item in result.items:
                    try:
                        # Check if file already exists in database
                        cursor.execute("SELECT id FROM media_files WHERE id = %s", (item.id,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing record with enhanced metadata
                            cursor.execute("""
                                UPDATE media_files 
                                SET file_size = %s, title = %s, year = %s, is_deleted = FALSE
                                WHERE id = %s
                            """, (item.file_size, item.title, item.year, item.id))
                            files_updated += 1
                        else:
                            # Insert new record with enhanced metadata
                            cursor.execute("""
                                INSERT INTO media_files (
                                    id, filename, file_path, file_size, category, title, year, is_deleted
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
                            """, (item.id, item.filename, item.file_path, item.file_size, item.category, item.title, item.year))
                            files_added += 1
                            dir_files_added += 1
                        
                        total_files_found += 1
                        
                    except Exception as file_error:
                        print(f"Error processing file {item.file_path}: {file_error}")
                        continue
                
                # Store enhanced scan results
                scan_results[category] = {
                    'path': scan_path,
                    'files_found': result.files_found,
                    'files_added': dir_files_added,
                    'storage_format': dir_config.get('storage_format', 'collection'),
                    'metadata': result.metadata
                }
                
            except Exception as scan_error:
                print(f"Error scanning directory {scan_path}: {scan_error}")
                scan_results[category] = {
                    'path': scan_path,
                    'files_found': 0,
                    'files_added': 0,
                    'error': str(scan_error)
                }
        
        # Commit all changes
        conn.commit()
        
        # Update scan timestamp
        scan_timestamp = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify({
            "message": "Live media scan completed successfully",
            "scan_timestamp": scan_timestamp,
            "total_files_found": total_files_found,
            "files_added": files_added,
            "files_updated": files_updated,
            "directories_scanned": len([d for d in media_directories if os.path.exists(d['root_path'])]),
            "scan_results": scan_results,
            "scan_status": "completed"
        })
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"Live media scan error: {e}")
        return jsonify({"detail": f"Live media scan error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.route('/<media_id>/stream', methods=['GET', 'HEAD', 'OPTIONS'])
@jwt_required(optional=True)  # Allow token in query parameter
def stream_media(media_id):
    """Stream media file with range request support"""
    try:
        token = request.args.get('token')
        if token:
            # Validate token from query parameter
            from flask_jwt_extended import decode_token
            try:
                decode_token(token)
            except Exception:
                return jsonify({"detail": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_path, filename FROM media_files WHERE id = %s AND is_deleted = FALSE", (media_id,))
        media = cursor.fetchone()
        
        if not media:
            return jsonify({"detail": "Media not found"}), 404
        
        file_path = Path(media['file_path'])
        if not file_path.exists():
            return jsonify({"detail": "Media file not found on disk"}), 404
        
        # Handle range requests for video seeking
        range_header = request.headers.get('Range')
        file_size = file_path.stat().st_size
        
        if range_header:
            # Parse range header
            byte_start = 0
            byte_end = file_size - 1
            
            if range_header.startswith('bytes='):
                range_match = range_header[6:].split('-')
                if range_match[0]:
                    byte_start = int(range_match[0])
                if range_match[1]:
                    byte_end = int(range_match[1])
            
            # Ensure valid range
            byte_start = max(0, byte_start)
            byte_end = min(file_size - 1, byte_end)
            content_length = byte_end - byte_start + 1
            
            # Read file chunk
            with open(file_path, 'rb') as f:
                f.seek(byte_start)
                data = f.read(content_length)
            
            response = send_file(
                io.BytesIO(data),
                mimetype=mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream',
                as_attachment=False
            )
            
            response.status_code = 206
            response.headers['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Length'] = str(content_length)
            
            return response
        else:
            # Full file response
            return send_file(
                file_path,
                mimetype=mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream',
                as_attachment=False
            )
            
    except Exception as e:
        print(f"Stream error: {e}")
        return jsonify({"detail": f"Media error: {str(e)}"}), 500

@router.route('/categories', methods=['GET'])
@jwt_required()
def get_media_categories():
    """Get media categories with counts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM media_files 
            WHERE is_deleted = FALSE 
            GROUP BY category 
            ORDER BY category
        """)
        
        categories = {}
        for row in cursor.fetchall():
            categories[row['category']] = row['count']
        
        return jsonify(categories)
        
    except Exception as e:
        print(f"Categories error: {e}")
        return jsonify({"detail": f"Categories error: {str(e)}"}), 500

@router.route('/scan-unraid', methods=['POST'])
@jwt_required()
def scan_unraid_media():
    """Scan Unraid media using direct T: drive access (bypasses Docker mount issues)"""
    try:
        # Check admin permissions
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT is_superuser FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        # Get request parameters
        data = request.get_json() or {}
        scan_method = data.get('scan_method', 'direct_t_drive')
        
        print(f"Starting Unraid scan with method: {scan_method}")
        
        # Import and run the unified Unraid scanner
        import subprocess
        import os
        
        # Run the unified scanner as a subprocess
        scanner_path = '/app/tools/unified-unraid-scanner.py'
        
        # Set environment variables for the scanner
        env = os.environ.copy()
        env['ENV_TYPE'] = 'local'
        env['UNRAID_ACCESS_METHOD'] = 'direct_scanner'
        env['T_DRIVE_PATH'] = 'T:\\'
        
        # Run the scanner with a timeout
        try:
            result = subprocess.run([
                'python', '/app/tools/unified-unraid-scanner.py'
            ], capture_output=True, text=True, timeout=300, env=env, cwd='/app')
            
            if result.returncode == 0:
                # Parse the output to extract scan results
                output_lines = result.stdout.strip().split('\n')
                
                # Look for the results summary
                total_files = 0
                categories_found = {}
                
                for line in output_lines:
                    if 'TOTAL FILES FOUND:' in line:
                        try:
                            total_files = int(line.split(':')[1].strip())
                        except:
                            pass
                    elif '|' in line and 'files |' in line:
                        # Parse category results like "movies | collection | 732 files | [MOUNT]"
                        parts = line.split('|')
                        if len(parts) >= 3:
                            category = parts[0].strip()
                            files_part = parts[2].strip()
                            if 'files' in files_part:
                                try:
                                    file_count = int(files_part.split()[0])
                                    categories_found[category] = file_count
                                except:
                                    pass
                
                return jsonify({
                    "message": "Unraid media scan completed successfully via direct T: drive access",
                    "scan_method": scan_method,
                    "total_files_found": total_files,
                    "files_added": 0,  # Scanner doesn't update DB directly
                    "files_updated": 0,
                    "directories_scanned": len(categories_found),
                    "scan_results": categories_found,
                    "scan_status": "completed",
                    "scanner_output": output_lines[-5:] if len(output_lines) > 5 else output_lines,
                    "note": "Files scanned from T: drive. Results show available media but are not imported to database."
                })
            else:
                return jsonify({
                    "detail": f"Unraid scanner failed with return code {result.returncode}",
                    "error_output": result.stderr[:500] if result.stderr else "No error output",
                    "scan_method": scan_method
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({
                "detail": "Unraid scan timed out (5 minutes)",
                "scan_method": scan_method
            }), 408
        except FileNotFoundError:
            return jsonify({
                "detail": "Unraid scanner script not found",
                "scan_method": scan_method,
                "note": "Direct T: drive scanner is not available in this container"
            }), 404
            
    except Exception as e:
        print(f"Unraid scan error: {e}")
        return jsonify({"detail": f"Unraid scan error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
