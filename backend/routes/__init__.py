"""Flask route blueprints for the Watch1 backend."""
from __future__ import annotations

from flask import Flask

from .admin import admin_bp


def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the given Flask application."""
    app.register_blueprint(admin_bp)
