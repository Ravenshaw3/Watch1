"""
Flask-compatible system and maintenance endpoints
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from postgres_config import get_db_connection
import os
from datetime import datetime

router = Blueprint('system', __name__)

@router.route('/version', methods=['GET'])
def get_version():
    """Version endpoint"""
    return jsonify({
        "version": "3.0.4",
        "framework": "Flask",
        "build_date": "2025-09-29",
        "api_version": "v1",
        "architecture": "Structured Backend",
        "features": [
            "Structured Backend Architecture",
            "Modular Flask Blueprint Design",
            "PostgreSQL Database Integration",
            "JWT Authentication System",
            "CORS Policy Configuration",
            "Production Ready Deployment"
        ]
    })

@router.route('/database-info', methods=['GET'])
@jwt_required()
def get_database_info():
    """Get database information and statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        # Get database statistics
        stats = {}
        
        # Table counts
        cursor.execute("SELECT COUNT(*) as count FROM users")
        stats['users'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM media_files WHERE is_deleted = FALSE")
        stats['media_files'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM playlists WHERE is_deleted = FALSE")
        stats['playlists'] = cursor.fetchone()['count']
        
        # Database table info (simplified)
        cursor.execute("""
            SELECT 
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        table_stats = cursor.fetchall()
        
        # Database version
        cursor.execute("SELECT version() as version")
        db_version = cursor.fetchone()['version']
        
        return jsonify({
            "database_type": "PostgreSQL",
            "database_version": db_version,
            "connection_status": "healthy",
            "table_counts": stats,
            "tables": [dict(row) for row in table_stats] if table_stats else [],
            "environment": os.getenv('FLASK_ENV', 'production')
        })
        
    except Exception as e:
        print(f"Database info error: {e}")
        return jsonify({"detail": f"Database info error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.route('/health-detailed', methods=['GET'])
def get_health_detailed():
    """Detailed health check with system information"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        db_test = cursor.fetchone()['test']
        cursor.close()
        conn.close()
        
        # System information
        health_info = {
            "status": "healthy",
            "version": "3.0.4",
            "framework": "Flask",
            "architecture": "Structured Backend",
            "database": {
                "status": "connected" if db_test == 1 else "error",
                "type": "PostgreSQL"
            },
            "environment": {
                "flask_env": os.getenv('FLASK_ENV', 'production'),
                "debug_mode": os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
            },
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
        return jsonify(health_info)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@router.route('/maintenance/reset-database', methods=['POST'])
@jwt_required()
def reset_database():
    """Reset database (superuser only) - DANGEROUS"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        # This is a dangerous operation - just return info for now
        return jsonify({
            "message": "Database reset functionality not implemented for safety",
            "suggestion": "Use docker-compose down && docker volume rm watch1_postgres_data && docker-compose up -d",
            "warning": "This would delete all data permanently"
        })
        
    except Exception as e:
        print(f"Reset database error: {e}")
        return jsonify({"detail": f"Reset error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.route('/maintenance/seed-sample-data', methods=['POST'])
@jwt_required()
def seed_sample_data():
    """Add sample data for testing (superuser only)"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is superuser
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user or not user['is_superuser']:
            return jsonify({"detail": "Not enough permissions"}), 403
        
        # Add sample media files
        sample_media = [
            {
                'id': 'sample_movie_matrix',
                'filename': 'The Matrix (1999).mkv',
                'file_path': '/app/media/movies/The Matrix (1999).mkv',
                'file_size': 2147483648,
                'duration_seconds': 8160,
                'category': 'movies',
                'title': 'The Matrix',
                'year': 1999,
                'rating': 8.7
            },
            {
                'id': 'sample_movie_inception',
                'filename': 'Inception (2010).mp4',
                'file_path': '/app/media/movies/Inception (2010).mp4',
                'file_size': 1610612736,
                'duration_seconds': 8880,
                'category': 'movies',
                'title': 'Inception',
                'year': 2010,
                'rating': 8.8
            }
        ]
        
        added_count = 0
        for media in sample_media:
            cursor.execute("SELECT id FROM media_files WHERE id = %s", (media['id'],))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO media_files (
                        id, filename, file_path, file_size, duration_seconds, 
                        category, title, year, rating
                    ) VALUES (
                        %(id)s, %(filename)s, %(file_path)s, %(file_size)s, 
                        %(duration_seconds)s, %(category)s, %(title)s, %(year)s, %(rating)s
                    )
                """, media)
                added_count += 1
        
        conn.commit()
        
        return jsonify({
            "message": f"Sample data seeding completed",
            "added_media_files": added_count,
            "total_sample_files": len(sample_media)
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Seed sample data error: {e}")
        return jsonify({"detail": f"Seed error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
