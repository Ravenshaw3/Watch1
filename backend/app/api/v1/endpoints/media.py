"""
Media management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import hashlib
import aiofiles
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.models.media import MediaFile, MediaMetadata
from app.schemas.media import (
    MediaFile as MediaFileSchema,
    MediaFileWithMetadata,
    MediaSearchRequest,
    MediaSearchResponse,
    MediaUploadResponse
)
from app.core.exceptions import MediaFileNotFound, UnsupportedMediaFormat

router = APIRouter()


@router.get("/", response_model=MediaSearchResponse)
async def get_media_files(
    query: Optional[str] = Query(None, description="Search query"),
    media_type: Optional[str] = Query(None, description="Media type filter"),
    genre: Optional[str] = Query(None, description="Genre filter"),
    year: Optional[int] = Query(None, description="Year filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """Get media files with optional filtering and pagination"""
    # This is a simplified implementation
    # In a real application, you would implement proper filtering and pagination
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    
    # Build query
    stmt = select(MediaFile).options(selectinload(MediaFile.media_metadata))
    
    # Apply filters
    if media_type:
        stmt = stmt.where(MediaFile.media_type == media_type)
    
    # Get total count
    count_stmt = select(func.count(MediaFile.id))
    if media_type:
        count_stmt = count_stmt.where(MediaFile.media_type == media_type)
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(stmt)
    media_files = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return MediaSearchResponse(
        items=media_files,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{file_id}", response_model=MediaFileWithMetadata)
async def get_media_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific media file by ID"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = select(MediaFile).options(selectinload(MediaFile.media_metadata)).where(MediaFile.id == file_id)
    result = await db.execute(stmt)
    media_file = result.scalar_one_or_none()
    
    if not media_file:
        raise MediaFileNotFound(str(file_id))
    
    return media_file


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new media file"""
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    supported_formats = (
        settings.SUPPORTED_VIDEO_FORMATS +
        settings.SUPPORTED_AUDIO_FORMATS +
        settings.SUPPORTED_IMAGE_FORMATS
    )
    
    if file_extension not in supported_formats:
        raise UnsupportedMediaFormat(file_extension)
    
    # Determine media type
    if file_extension in settings.SUPPORTED_VIDEO_FORMATS:
        media_type = "video"
    elif file_extension in settings.SUPPORTED_AUDIO_FORMATS:
        media_type = "audio"
    else:
        media_type = "image"
    
    # Create file path
    file_path = os.path.join(settings.MEDIA_ROOT, file.filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Calculate file hash
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check if file already exists
    from sqlalchemy import select
    existing_file = await db.execute(
        select(MediaFile).where(MediaFile.file_hash == file_hash)
    )
    if existing_file.scalar_one_or_none():
        # File already exists, delete the uploaded file
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File with this content already exists"
        )
    
    # Create database record
    media_file = MediaFile(
        filename=file.filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        file_hash=file_hash,
        mime_type=file.content_type or "application/octet-stream",
        media_type=media_type
    )
    
    db.add(media_file)
    await db.commit()
    await db.refresh(media_file)
    
    return MediaUploadResponse(
        file_id=media_file.id,
        filename=media_file.filename,
        status="uploaded",
        message="File uploaded successfully"
    )


@router.delete("/{file_id}")
async def delete_media_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a media file"""
    from sqlalchemy import select
    
    # Get media file
    stmt = select(MediaFile).where(MediaFile.id == file_id)
    result = await db.execute(stmt)
    media_file = result.scalar_one_or_none()
    
    if not media_file:
        raise MediaFileNotFound(str(file_id))
    
    # Delete physical file
    if os.path.exists(media_file.file_path):
        os.remove(media_file.file_path)
    
    # Delete database record
    await db.delete(media_file)
    await db.commit()
    
    return {"message": "Media file deleted successfully"}


@router.get("/{file_id}/stream")
async def stream_media_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Stream a media file"""
    from fastapi.responses import FileResponse
    from sqlalchemy import select
    
    # Get media file
    stmt = select(MediaFile).where(MediaFile.id == file_id)
    result = await db.execute(stmt)
    media_file = result.scalar_one_or_none()
    
    if not media_file:
        raise MediaFileNotFound(str(file_id))
    
    if not os.path.exists(media_file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found on disk"
        )
    
    return FileResponse(
        path=media_file.file_path,
        media_type=media_file.mime_type,
        filename=media_file.filename
    )
