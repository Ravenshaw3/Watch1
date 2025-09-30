'''
Watch1 Media Server v3.0.4 - Structured Backend
Production-ready Flask application with modular architecture
'''

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from datetime import timedelta
import os
from dotenv import load_dotenv

# Import Flask-compatible structured endpoints
try:
    from app.api.v1.endpoints.auth import router as auth_router
    from app.api.v1.endpoints.media_flask import router as media_router
    from app.api.v1.endpoints.playlists_flask import router as playlists_router
    from app.api.v1.endpoints.settings_flask import router as settings_router
    from app.api.v1.endpoints.analytics_flask import router as analytics_router
    from app.api.v1.endpoints.system_flask import router as system_router
    from app.api.v1.endpoints.admin_flask import router as admin_router
    STRUCTURED_ENDPOINTS_AVAILABLE = True
except ImportError as e:
    print(f"Structured endpoints not available: {e}")
    STRUCTURED_ENDPOINTS_AVAILABLE = False

from config_loader import load_media_config, ConfigError

def create_app():
    '''Application factory'''
    load_dotenv()
    
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 2048  # 2GB uploads
    
    # JWT Configuration
    jwt_secret = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production-minimum-32-chars')
    app.config['JWT_SECRET_KEY'] = jwt_secret
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=8)
    
    # Media Configuration
    try:
        media_config = load_media_config()
        app.config['MEDIA_CATALOG'] = media_config
    except ConfigError as e:
        print(f"Media config error: {e}")
        # Use fallback config
        from dataclasses import dataclass, field
        
        @dataclass(frozen=True)
        class FallbackCategory:
            key: str = "movies"
            label: str = "Movies"
            media_type: str = "video"
            storage_format: str = "collection"
            root_path: str = "/app/media/movies"
            default: bool = True
        
        @dataclass(frozen=True)
        class FallbackCatalog:
            version: int = 1
            categories: list = field(default_factory=lambda: [FallbackCategory()])
        
        app.config['MEDIA_CATALOG'] = FallbackCatalog()
    
    # CORS Configuration
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
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'],
        expose_headers=['Content-Type', 'Content-Length', 'Accept-Ranges', 'Content-Range', 'Range']
    )
    
    # Initialize extensions
    jwt = JWTManager(app)
    
    # Security headers (relaxed for development)
    @app.after_request
    def add_security_headers(response):
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), browsing-topics=(), interest-cohort=()'
        # Disable strict CORS policies for development
        if os.getenv('FLASK_ENV') == 'development':
            response.headers.pop('Cross-Origin-Embedder-Policy', None)
            response.headers.pop('Cross-Origin-Opener-Policy', None)
        else:
            response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
            response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        return response
    
    # Register structured endpoints if available
    if STRUCTURED_ENDPOINTS_AVAILABLE:
        app.register_blueprint(auth_router, url_prefix='/api/v1/auth')
        app.register_blueprint(media_router, url_prefix='/api/v1/media')
        app.register_blueprint(playlists_router, url_prefix='/api/v1/playlists')
        app.register_blueprint(settings_router, url_prefix='/api/v1/settings')
        app.register_blueprint(analytics_router, url_prefix='/api/v1/analytics')
        app.register_blueprint(system_router, url_prefix='/api/v1/system')
        app.register_blueprint(admin_router, url_prefix='/api/v1/admin')
        print("✅ Structured endpoints registered: auth, media, playlists, settings, analytics, system, admin")
    else:
        print("⚠️ Using basic endpoints only")
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            "message": "Watch1 Media Server v3.0.4 - Structured Backend",
            "version": "3.0.4",
            "status": "Production Ready",
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "version": "3.0.4"})
    # API v1 health endpoint
    @app.route('/api/v1/health')
    def api_health():
        return jsonify({
            "status": "healthy",
            "version": "3.0.4",
            "api": "v1"
        })
    
    # Legacy version endpoint for frontend compatibility
    @app.route('/api/v1/version')
    def api_version():
        return jsonify({
            "version": "3.0.4",
            "framework": "Flask",
            "architecture": "Structured Backend",
            "build_date": "2025-09-29",
            "api_version": "v1"
        })
    
    # Legacy users/me endpoint for frontend compatibility
    @app.route('/api/v1/users/me')
    @jwt_required()
    def legacy_users_me():
        from flask_jwt_extended import get_jwt_identity
        from postgres_config import get_db_connection
        
        try:
            user_id = get_jwt_identity()
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, is_active, is_superuser, created_at
                FROM users WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            if not user:
                return jsonify({"detail": "User not found"}), 404
            
            return jsonify({
                "id": user['id'],
                "email": user['email'],
                "is_active": user['is_active'],
                "is_superuser": user['is_superuser'],
                "created_at": user['created_at'].isoformat() if user['created_at'] else None,
                "full_name": user['email'],  # Use email as full_name for compatibility
                "username": user['email']    # Use email as username for compatibility
            })
            
        except Exception as e:
            print(f"Legacy users/me error: {e}")
            return jsonify({"detail": "Internal server error"}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
