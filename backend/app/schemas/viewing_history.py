"""
Viewing history schemas for Watch1 Media Server
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ViewingHistoryCreate(BaseModel):
    """Create viewing history request"""
    media_id: str
    watch_duration: int = 0
    current_position: int = 0
    progress_percentage: float = 0.0
    completed: str = "false"  # "true", "false", "partial"
    device_info: Optional[str] = None
    quality: Optional[str] = None

class ViewingHistoryUpdate(BaseModel):
    """Update viewing history request"""
    watch_duration: Optional[int] = None
    current_position: Optional[int] = None
    progress_percentage: Optional[float] = None
    completed: Optional[str] = None
    device_info: Optional[str] = None
    quality: Optional[str] = None

class ViewingHistoryResponse(BaseModel):
    """Viewing history response"""
    id: str
    user_id: str
    media_id: str
    started_at: datetime
    last_watched_at: datetime
    watch_duration: int
    progress_percentage: float
    current_position: int
    completed: str
    device_info: Optional[str] = None
    quality: Optional[str] = None

    class Config:
        from_attributes = True

class ViewingStats(BaseModel):
    """Viewing statistics"""
    total_watch_time: int  # Total seconds watched
    total_videos: int
    completed_videos: int
    weekly_watch_time: int
    completion_rate: float  # Percentage

class MostWatchedContent(BaseModel):
    """Most watched content item"""
    media_id: str
    filename: str
    total_watch_time: int
    watch_count: int
    max_progress: float
    category: str
    file_size: int
