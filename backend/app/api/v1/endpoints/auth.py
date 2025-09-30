from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import bcrypt
import hashlib
from postgres_config import get_db_connection

router = Blueprint('auth', __name__)

@router.route('/login/access-token', methods=['POST'])
def login():
    '''Login endpoint'''
    try:
        # Handle both JSON and form data safely
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({"detail": "Username and password are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user by username or email
        cursor.execute(
            "SELECT id, email, password_hash, is_active, is_superuser FROM users WHERE email = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"detail": "Incorrect username or password"}), 401
        
        # Verify password using SHA256 (matching database format)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] != password_hash:
            return jsonify({"detail": "Incorrect username or password"}), 401
        
        if not user['is_active']:
            return jsonify({"detail": "Account is inactive"}), 401
        
        # Create access token
        access_token = create_access_token(
            identity=str(user['id']),
            expires_delta=timedelta(days=8)
        )
        
        return jsonify({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "is_superuser": user['is_superuser']
            }
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"detail": f"Login error: {str(e)}"}), 500

@router.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    '''Get current user info'''
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, email, is_active, is_superuser, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"detail": "User not found"}), 404
        
        return jsonify({
            "id": user['id'],
            "username": user['email'],  # Using email as username
            "email": user['email'],
            "full_name": user['email'],  # Using email as fallback
            "is_active": user['is_active'],
            "is_superuser": user['is_superuser'],
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        })
        
    except Exception as e:
        print(f"Get current user error: {e}")
        return jsonify({"detail": f"User error: {str(e)}"}), 500
