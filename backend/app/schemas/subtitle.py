"""
Subtitle schemas for Watch1 Media Server
"""

from pydantic import BaseModel
from typing import Optional

class SubtitleInfo(BaseModel):
    """Subtitle information"""
    id: str
    filename: str
    language: str
    format: str  # .srt, .vtt, .ass, etc.
    size: int
    url: str

class SubtitleUpload(BaseModel):
    """Subtitle upload request"""
    language: Optional[str] = None
    format: str
