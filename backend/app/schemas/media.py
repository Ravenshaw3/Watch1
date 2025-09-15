"""
Pydantic schemas for media-related models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MediaFileBase(BaseModel):
    """Base media file schema"""
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    media_type: str


class MediaFileCreate(MediaFileBase):
    """Schema for creating a media file"""
    file_path: str
    file_hash: str


class MediaFileUpdate(BaseModel):
    """Schema for updating a media file"""
    filename: Optional[str] = None
    is_available: Optional[bool] = None
    processing_status: Optional[str] = None


class MediaFile(MediaFileBase):
    """Schema for media file response"""
    id: int
    file_path: str
    file_hash: str
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    container_format: Optional[str] = None
    thumbnail_path: Optional[str] = None
    poster_path: Optional[str] = None
    is_processed: bool
    is_available: bool
    processing_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MediaInfoBase(BaseModel):
    """Base media information schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    director: Optional[str] = None
    cast: Optional[List[str]] = None
    rating: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    studio: Optional[str] = None
    tags: Optional[List[str]] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None


class MediaInfoCreate(MediaInfoBase):
    """Schema for creating media information"""
    media_file_id: int


class MediaInfoUpdate(MediaInfoBase):
    """Schema for updating media information"""
    pass


class MediaInfo(MediaInfoBase):
    """Schema for media information response"""
    id: int
    media_file_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MediaFileWithMetadata(MediaFile):
    """Schema for media file with metadata"""
    media_metadata: Optional[MediaInfo] = None


class TranscodedFileBase(BaseModel):
    """Base transcoded file schema"""
    quality: str
    format: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None


class TranscodedFileCreate(TranscodedFileBase):
    """Schema for creating a transcoded file"""
    original_file_id: int
    file_path: str


class TranscodedFile(TranscodedFileBase):
    """Schema for transcoded file response"""
    id: int
    original_file_id: int
    file_path: str
    is_ready: bool
    processing_progress: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MediaSearchRequest(BaseModel):
    """Schema for media search request"""
    query: Optional[str] = None
    media_type: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class MediaSearchResponse(BaseModel):
    """Schema for media search response"""
    items: List[MediaFileWithMetadata]
    total: int
    page: int
    page_size: int
    total_pages: int


class MediaUploadResponse(BaseModel):
    """Schema for media upload response"""
    file_id: int
    filename: str
    status: str
    message: str
