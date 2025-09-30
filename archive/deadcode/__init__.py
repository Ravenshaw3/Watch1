"""Flask route blueprints for the Watch1 backend."""
from __future__ import annotations

from flask import Flask

try:
    from .admin import admin_bp
except ModuleNotFoundError as error:
    admin_bp = None  # type: ignore[assignment]
    missing_dependency = error.name
else:
    missing_dependency = None


def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the given Flask application."""
    if admin_bp is not None:
        app.register_blueprint(admin_bp)
    else:
        app.logger.warning(
            "Skipping admin routes registration; missing optional dependency '%s'.",
            missing_dependency,
        )
