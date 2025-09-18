"""
Viewing history endpoints for Watch1 Media Server
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.viewing_history import ViewingHistory
from app.models.media import MediaFile
from app.models.user import User
from app.schemas.viewing_history import (
    ViewingHistoryCreate, 
    ViewingHistoryUpdate, 
    ViewingHistoryResponse,
    ViewingStats,
    MostWatchedContent
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/viewing-history", response_model=ViewingHistoryResponse)
async def create_viewing_history(
    history_data: ViewingHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update viewing history"""
    try:
        # Check if viewing history already exists
        stmt = select(ViewingHistory).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.media_id == history_data.media_id
        )
        result = await db.execute(stmt)
        existing_history = result.scalar_one_or_none()
        
        if existing_history:
            # Update existing history
            existing_history.last_watched_at = datetime.utcnow()
            existing_history.watch_duration += history_data.watch_duration
            existing_history.current_position = history_data.current_position
            existing_history.progress_percentage = history_data.progress_percentage
            existing_history.completed = history_data.completed
            existing_history.device_info = history_data.device_info
            existing_history.quality = history_data.quality
            
            await db.commit()
            await db.refresh(existing_history)
            return ViewingHistoryResponse.from_orm(existing_history)
        else:
            # Create new history
            new_history = ViewingHistory(
                user_id=current_user.id,
                media_id=history_data.media_id,
                watch_duration=history_data.watch_duration,
                current_position=history_data.current_position,
                progress_percentage=history_data.progress_percentage,
                completed=history_data.completed,
                device_info=history_data.device_info,
                quality=history_data.quality
            )
            
            db.add(new_history)
            await db.commit()
            await db.refresh(new_history)
            return ViewingHistoryResponse.from_orm(new_history)
            
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create viewing history: {str(e)}"
        )

@router.get("/viewing-history", response_model=List[ViewingHistoryResponse])
async def get_user_viewing_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's viewing history"""
    try:
        stmt = select(ViewingHistory).where(
            ViewingHistory.user_id == current_user.id
        ).order_by(desc(ViewingHistory.last_watched_at)).offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        history_records = result.scalars().all()
        
        return [ViewingHistoryResponse.from_orm(record) for record in history_records]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get viewing history: {str(e)}"
        )

@router.get("/viewing-history/stats", response_model=ViewingStats)
async def get_viewing_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's viewing statistics"""
    try:
        # Total watch time
        total_watch_time_stmt = select(func.sum(ViewingHistory.watch_duration)).where(
            ViewingHistory.user_id == current_user.id
        )
        total_watch_time_result = await db.execute(total_watch_time_stmt)
        total_watch_time = total_watch_time_result.scalar() or 0
        
        # Total videos watched
        total_videos_stmt = select(func.count(ViewingHistory.id)).where(
            ViewingHistory.user_id == current_user.id
        )
        total_videos_result = await db.execute(total_videos_stmt)
        total_videos = total_videos_result.scalar() or 0
        
        # Completed videos
        completed_videos_stmt = select(func.count(ViewingHistory.id)).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.completed == "true"
        )
        completed_videos_result = await db.execute(completed_videos_stmt)
        completed_videos = completed_videos_result.scalar() or 0
        
        # Watch time this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_watch_time_stmt = select(func.sum(ViewingHistory.watch_duration)).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.last_watched_at >= week_ago
        )
        weekly_watch_time_result = await db.execute(weekly_watch_time_stmt)
        weekly_watch_time = weekly_watch_time_result.scalar() or 0
        
        return ViewingStats(
            total_watch_time=total_watch_time,
            total_videos=total_videos,
            completed_videos=completed_videos,
            weekly_watch_time=weekly_watch_time,
            completion_rate=(completed_videos / total_videos * 100) if total_videos > 0 else 0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get viewing stats: {str(e)}"
        )

@router.get("/viewing-history/most-watched", response_model=List[MostWatchedContent])
async def get_most_watched_content(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get most watched content"""
    try:
        stmt = select(
            ViewingHistory.media_id,
            func.sum(ViewingHistory.watch_duration).label('total_watch_time'),
            func.count(ViewingHistory.id).label('watch_count'),
            func.max(ViewingHistory.progress_percentage).label('max_progress')
        ).where(
            ViewingHistory.user_id == current_user.id
        ).group_by(
            ViewingHistory.media_id
        ).order_by(
            desc('total_watch_time')
        ).limit(limit)
        
        result = await db.execute(stmt)
        most_watched_data = result.all()
        
        # Get media file details
        most_watched_content = []
        for row in most_watched_data:
            media_stmt = select(MediaFile).where(MediaFile.id == row.media_id)
            media_result = await db.execute(media_stmt)
            media_file = media_result.scalar_one_or_none()
            
            if media_file:
                most_watched_content.append(MostWatchedContent(
                    media_id=row.media_id,
                    filename=media_file.original_filename,
                    total_watch_time=row.total_watch_time,
                    watch_count=row.watch_count,
                    max_progress=row.max_progress,
                    category=media_file.category,
                    file_size=media_file.file_size
                ))
        
        return most_watched_content
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get most watched content: {str(e)}"
        )

@router.put("/viewing-history/{history_id}", response_model=ViewingHistoryResponse)
async def update_viewing_history(
    history_id: str,
    history_data: ViewingHistoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update viewing history"""
    try:
        stmt = select(ViewingHistory).where(
            ViewingHistory.id == history_id,
            ViewingHistory.user_id == current_user.id
        )
        result = await db.execute(stmt)
        history_record = result.scalar_one_or_none()
        
        if not history_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Viewing history not found"
            )
        
        # Update fields
        for field, value in history_data.dict(exclude_unset=True).items():
            setattr(history_record, field, value)
        
        history_record.last_watched_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(history_record)
        return ViewingHistoryResponse.from_orm(history_record)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update viewing history: {str(e)}"
        )

@router.delete("/viewing-history/{history_id}")
async def delete_viewing_history(
    history_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete viewing history"""
    try:
        stmt = select(ViewingHistory).where(
            ViewingHistory.id == history_id,
            ViewingHistory.user_id == current_user.id
        )
        result = await db.execute(stmt)
        history_record = result.scalar_one_or_none()
        
        if not history_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Viewing history not found"
            )
        
        await db.delete(history_record)
        await db.commit()
        
        return {"message": "Viewing history deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete viewing history: {str(e)}"
        )
