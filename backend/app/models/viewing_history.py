"""
Viewing history model for Watch1 Media Server
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class ViewingHistory(Base):
    """Viewing history for media files"""
    __tablename__ = "viewing_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    media_id = Column(String, ForeignKey("media_files.id"), nullable=False)
    
    # Viewing details
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_watched_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    watch_duration = Column(Integer, default=0)  # Total seconds watched
    progress_percentage = Column(Float, default=0.0)  # 0.0 to 100.0
    current_position = Column(Integer, default=0)  # Current position in seconds
    completed = Column(String, default="false")  # "true", "false", "partial"
    
    # Additional metadata
    device_info = Column(Text)  # Browser, device type, etc.
    quality = Column(String)  # Video quality watched
    
    # Relationships
    user = relationship("User", back_populates="viewing_history")
    media = relationship("MediaFile", back_populates="viewing_history")
    
    def __repr__(self):
        return f"<ViewingHistory(user_id={self.user_id}, media_id={self.media_id}, progress={self.progress_percentage}%)>"
