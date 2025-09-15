"""
Pydantic schemas for playlist-related models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlaylistBase(BaseModel):
    """Base playlist schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    is_smart: bool = False
    smart_filters: Optional[Dict[str, Any]] = None


class PlaylistCreate(PlaylistBase):
    """Schema for creating a playlist"""
    pass


class PlaylistUpdate(BaseModel):
    """Schema for updating a playlist"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_smart: Optional[bool] = None
    smart_filters: Optional[Dict[str, Any]] = None


class PlaylistItemBase(BaseModel):
    """Base playlist item schema"""
    media_file_id: int
    position: int


class PlaylistItemCreate(PlaylistItemBase):
    """Schema for creating a playlist item"""
    pass


class PlaylistItem(PlaylistItemBase):
    """Schema for playlist item response"""
    id: int
    playlist_id: int
    added_at: datetime
    
    class Config:
        from_attributes = True


class Playlist(PlaylistBase):
    """Schema for playlist response"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PlaylistItem] = []
    
    class Config:
        from_attributes = True


class PlaylistResponse(Playlist):
    """Schema for playlist response with items"""
    pass
