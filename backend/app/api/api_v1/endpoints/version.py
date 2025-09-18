"""
Version endpoints for Watch1 Media Server
"""

from typing import Any
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/version")
def get_version() -> Any:
    """
    Get version information
    """
    return {
        "version": settings.VERSION,
        "build_date": "2024-12-17",
        "features": [
            "Production-Ready Flask Backend Architecture",
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
            "Mobile App Foundation (React Native)"
        ]
    }
