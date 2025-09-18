"""
Subtitle management endpoints for Watch1 Media Server
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import mimetypes
from pathlib import Path

from app.core.database import get_db
from app.models.media import MediaFile
from app.schemas.subtitle import SubtitleInfo, SubtitleUpload
from app.core.exceptions import Watch1Exception

router = APIRouter()

# Supported subtitle formats
SUPPORTED_SUBTITLE_FORMATS = {'.srt', '.vtt', '.ass', '.ssa', '.sub'}

@router.get("/media/{media_id}/subtitles", response_model=List[SubtitleInfo])
async def get_media_subtitles(
    media_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all subtitles for a media file"""
    try:
        # Get media file
        media_file = await db.get(MediaFile, media_id)
        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media file not found"
            )
        
        # Look for subtitle files in the same directory
        media_path = Path(media_file.file_path)
        subtitle_dir = media_path.parent
        subtitle_files = []
        
        # Find subtitle files with matching base name
        base_name = media_path.stem
        for subtitle_file in subtitle_dir.glob(f"{base_name}*"):
            if subtitle_file.suffix.lower() in SUPPORTED_SUBTITLE_FORMATS:
                subtitle_info = SubtitleInfo(
                    id=str(subtitle_file),
                    filename=subtitle_file.name,
                    language=extract_language_from_filename(subtitle_file.name),
                    format=subtitle_file.suffix.lower(),
                    size=subtitle_file.stat().st_size,
                    url=f"/api/v1/media/{media_id}/subtitles/{subtitle_file.name}"
                )
                subtitle_files.append(subtitle_info)
        
        return subtitle_files
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subtitles: {str(e)}"
        )

@router.get("/media/{media_id}/subtitles/{subtitle_filename}")
async def get_subtitle_file(
    media_id: str,
    subtitle_filename: str,
    db: AsyncSession = Depends(get_db)
):
    """Serve subtitle file"""
    try:
        # Get media file
        media_file = await db.get(MediaFile, media_id)
        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media file not found"
            )
        
        # Construct subtitle file path
        media_path = Path(media_file.file_path)
        subtitle_path = media_path.parent / subtitle_filename
        
        if not subtitle_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtitle file not found"
            )
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(subtitle_path))
        if not mime_type:
            if subtitle_path.suffix.lower() == '.vtt':
                mime_type = 'text/vtt'
            elif subtitle_path.suffix.lower() == '.srt':
                mime_type = 'text/plain'
            else:
                mime_type = 'text/plain'
        
        return FileResponse(
            path=str(subtitle_path),
            media_type=mime_type,
            filename=subtitle_filename,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve subtitle: {str(e)}"
        )

@router.post("/media/{media_id}/subtitles", response_model=SubtitleInfo)
async def upload_subtitle(
    media_id: str,
    file: UploadFile = File(...),
    language: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload subtitle file for a media file"""
    try:
        # Get media file
        media_file = await db.get(MediaFile, media_id)
        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media file not found"
            )
        
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in SUPPORTED_SUBTITLE_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported subtitle format. Supported formats: {', '.join(SUPPORTED_SUBTITLE_FORMATS)}"
            )
        
        # Construct subtitle file path
        media_path = Path(media_file.file_path)
        subtitle_dir = media_path.parent
        
        # Generate filename
        base_name = media_path.stem
        if language:
            subtitle_filename = f"{base_name}.{language}{file_extension}"
        else:
            subtitle_filename = f"{base_name}{file_extension}"
        
        subtitle_path = subtitle_dir / subtitle_filename
        
        # Save subtitle file
        content = await file.read()
        with open(subtitle_path, 'wb') as f:
            f.write(content)
        
        # Create subtitle info
        subtitle_info = SubtitleInfo(
            id=str(subtitle_path),
            filename=subtitle_filename,
            language=language or extract_language_from_filename(subtitle_filename),
            format=file_extension,
            size=len(content),
            url=f"/api/v1/media/{media_id}/subtitles/{subtitle_filename}"
        )
        
        return subtitle_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload subtitle: {str(e)}"
        )

@router.delete("/media/{media_id}/subtitles/{subtitle_filename}")
async def delete_subtitle(
    media_id: str,
    subtitle_filename: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete subtitle file"""
    try:
        # Get media file
        media_file = await db.get(MediaFile, media_id)
        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media file not found"
            )
        
        # Construct subtitle file path
        media_path = Path(media_file.file_path)
        subtitle_path = media_path.parent / subtitle_filename
        
        if not subtitle_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtitle file not found"
            )
        
        # Delete subtitle file
        subtitle_path.unlink()
        
        return {"message": "Subtitle deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subtitle: {str(e)}"
        )

def extract_language_from_filename(filename: str) -> str:
    """Extract language code from filename"""
    # Common language patterns in filenames
    import re
    
    # Pattern for language codes like .en.srt, .eng.srt, .english.srt
    patterns = [
        r'\.([a-z]{2,3})\.(srt|vtt|ass|ssa|sub)$',  # .en.srt
        r'\.([a-z]{2,3})\.(srt|vtt|ass|ssa|sub)$',  # .eng.srt
        r'\.(english|spanish|french|german|italian|portuguese|russian|chinese|japanese|korean)\.(srt|vtt|ass|ssa|sub)$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            return match.group(1)
    
    return 'unknown'
