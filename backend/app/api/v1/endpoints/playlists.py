"""
Playlist management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.media import Playlist, PlaylistItem
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate, PlaylistResponse
from app.api.v1.endpoints.auth import get_current_user_from_token

router = APIRouter()


@router.get("/", response_model=List[PlaylistResponse])
async def get_user_playlists(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's playlists"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = select(Playlist).options(selectinload(Playlist.items)).where(
        Playlist.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    playlists = result.scalars().all()
    
    return playlists


@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a new playlist"""
    playlist = Playlist(
        name=playlist_data.name,
        description=playlist_data.description,
        owner_id=current_user.id,
        is_public=playlist_data.is_public,
        is_smart=playlist_data.is_smart,
        smart_filters=playlist_data.smart_filters
    )
    
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    
    return playlist


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific playlist"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = select(Playlist).options(selectinload(Playlist.items)).where(
        Playlist.id == playlist_id
    )
    result = await db.execute(stmt)
    playlist = result.scalar_one_or_none()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    # Check if user has access to this playlist
    if playlist.owner_id != current_user.id and not playlist.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this playlist"
        )
    
    return playlist


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    playlist_update: PlaylistUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """Update a playlist"""
    from sqlalchemy import select
    
    stmt = select(Playlist).where(Playlist.id == playlist_id)
    result = await db.execute(stmt)
    playlist = result.scalar_one_or_none()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    # Check if user owns this playlist
    if playlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only playlist owner can update this playlist"
        )
    
    # Update playlist fields
    if playlist_update.name is not None:
        playlist.name = playlist_update.name
    if playlist_update.description is not None:
        playlist.description = playlist_update.description
    if playlist_update.is_public is not None:
        playlist.is_public = playlist_update.is_public
    if playlist_update.is_smart is not None:
        playlist.is_smart = playlist_update.is_smart
    if playlist_update.smart_filters is not None:
        playlist.smart_filters = playlist_update.smart_filters
    
    await db.commit()
    await db.refresh(playlist)
    
    return playlist


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """Delete a playlist"""
    from sqlalchemy import select
    
    stmt = select(Playlist).where(Playlist.id == playlist_id)
    result = await db.execute(stmt)
    playlist = result.scalar_one_or_none()
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    
    # Check if user owns this playlist
    if playlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only playlist owner can delete this playlist"
        )
    
    await db.delete(playlist)
    await db.commit()
    
    return {"message": "Playlist deleted successfully"}
