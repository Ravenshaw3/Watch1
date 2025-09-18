"""
Main API router for v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import media, users, playlists, auth, subtitles, viewing_history

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
api_router.include_router(subtitles.router, prefix="/media", tags=["subtitles"])
api_router.include_router(viewing_history.router, prefix="/api/v1", tags=["viewing-history"])
