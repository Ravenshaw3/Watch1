"""Shared utility helpers for Flask route blueprints."""
from __future__ import annotations

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from postgres_config import get_db_connection


def ensure_superuser() -> int:
    """Ensure the current JWT identity represents a superuser."""
    user_id = get_jwt_identity()
    if not user_id:
        raise PermissionError("Authentication required")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT is_superuser FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not result or not result.get('is_superuser'):
        raise PermissionError("Not enough permissions")

    return user_id


def handle_permission_error(error: PermissionError):
    """Serialize permission errors to JSON responses."""
    return jsonify({"detail": str(error)}), 403
