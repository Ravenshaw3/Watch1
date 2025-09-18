"""
Media file models for the media library
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class MediaFile(Base):
    """Media file model"""
    
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), unique=True, index=True)  # SHA-256 hash
    mime_type = Column(String(100), nullable=False)
    media_type = Column(String(20), nullable=False)  # video, audio, image
    
    # Media metadata
    duration = Column(Float)  # in seconds
    width = Column(Integer)
    height = Column(Integer)
    bitrate = Column(Integer)
    codec = Column(String(50))
    container_format = Column(String(20))
    
    # Thumbnail and poster
    thumbnail_path = Column(String(500))
    poster_path = Column(String(500))
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True))
    
    # Relationships
    media_metadata = relationship("MediaInfo", back_populates="media_file", uselist=False)
    transcoded_files = relationship("TranscodedFile", back_populates="original_file")
    watch_history = relationship("WatchHistory", back_populates="media_file")
    viewing_history = relationship("ViewingHistory", back_populates="media")
    ratings = relationship("Rating", back_populates="media_file")
    playlist_items = relationship("PlaylistItem", back_populates="media_file")


class MediaInfo(Base):
    """Media information model"""
    
    __tablename__ = "media_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    media_file_id = Column(Integer, ForeignKey("media_files.id"), unique=True)
    
    # Basic metadata
    title = Column(String(255))
    description = Column(Text)
    genre = Column(String(100))
    year = Column(Integer)
    director = Column(String(255))
    cast = Column(JSON)  # List of cast members
    rating = Column(String(10))  # MPAA rating
    
    # Additional metadata
    language = Column(String(50))
    country = Column(String(100))
    studio = Column(String(255))
    tags = Column(JSON)  # List of tags
    
    # External IDs
    imdb_id = Column(String(20))
    tmdb_id = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    media_file = relationship("MediaFile", back_populates="media_metadata")


class TranscodedFile(Base):
    """Transcoded media file model"""
    
    __tablename__ = "transcoded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    original_file_id = Column(Integer, ForeignKey("media_files.id"))
    file_path = Column(String(500), nullable=False)
    quality = Column(String(20), nullable=False)  # 720p, 1080p, 4k, etc.
    format = Column(String(20), nullable=False)  # mp4, webm, etc.
    file_size = Column(Integer)
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    bitrate = Column(Integer)
    
    # Status
    is_ready = Column(Boolean, default=False)
    processing_progress = Column(Integer, default=0)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    original_file = relationship("MediaFile", back_populates="transcoded_files")


class Playlist(Base):
    """Playlist model"""
    
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    is_smart = Column(Boolean, default=False)  # Smart playlist with filters
    smart_filters = Column(JSON)  # Filter criteria for smart playlists
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="playlists")
    items = relationship("PlaylistItem", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistItem(Base):
    """Playlist item model"""
    
    __tablename__ = "playlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    media_file_id = Column(Integer, ForeignKey("media_files.id"))
    position = Column(Integer, nullable=False)
    
    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    playlist = relationship("Playlist", back_populates="items")
    media_file = relationship("MediaFile", back_populates="playlist_items")


class WatchHistory(Base):
    """Watch history model"""
    
    __tablename__ = "watch_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    media_file_id = Column(Integer, ForeignKey("media_files.id"))
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    watch_duration = Column(Float)  # in seconds
    completion_percentage = Column(Float)  # 0-100
    resume_position = Column(Float)  # in seconds
    
    # Relationships
    user = relationship("User", back_populates="watch_history")
    media_file = relationship("MediaFile", back_populates="watch_history")


class Rating(Base):
    """Rating model"""
    
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    media_file_id = Column(Integer, ForeignKey("media_files.id"))
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    media_file = relationship("MediaFile", back_populates="ratings")
