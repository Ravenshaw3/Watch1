"""
Configuration settings for Watch1 Media Server
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Watch1 Media Server"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://watch1:watch1_password@localhost:5432/watch1"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Media Storage
    MEDIA_ROOT: str = "/app/media"
    THUMBNAILS_ROOT: str = "/app/thumbnails"
    TRANSCODED_ROOT: str = "/app/transcoded"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 * 1024  # 10GB
    
    # Supported Media Formats
    SUPPORTED_VIDEO_FORMATS: List[str] = [
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"
    ]
    SUPPORTED_AUDIO_FORMATS: List[str] = [
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"
    ]
    SUPPORTED_IMAGE_FORMATS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"
    ]
    
    # FFmpeg Settings
    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"
    
    # Thumbnail Settings
    THUMBNAIL_SIZE: tuple = (320, 180)
    THUMBNAIL_QUALITY: int = 85
    
    # Transcoding Settings
    TRANSCODE_QUALITY: str = "medium"  # low, medium, high
    TRANSCODE_FORMAT: str = "mp4"
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
