"""
Watch1 Media Server - Enhanced Backend with Media Scanning and Categorization
Version: 2.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import uvicorn
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os
import shutil
from pathlib import Path
import mimetypes
import re
import asyncio
import math
import base64
import io
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import colorsys

# Simple in-memory storage for demo (replace with database in production)
users_db = {}
tokens_db = {}
media_db = {}
categories_db = {}
user_preferences_db = {}
playlists_db = {}

# Version information
VERSION = "2.0.0"
BUILD_DATE = datetime.utcnow().isoformat()

# Media categories
class MediaCategory(str, Enum):
    MOVIES = "movies"
    TV_SHOWS = "tv_shows"
    KIDS = "kids"
    MUSIC_VIDEOS = "music_videos"
    AUDIO = "audio"
    IMAGES = "images"
    OTHER = "other"

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class MediaFile(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    category: MediaCategory
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    container_format: Optional[str] = None
    thumbnail_path: Optional[str] = None
    poster_path: Optional[str] = None
    artwork: Optional[str] = None  # Base64 encoded artwork
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    uploaded_by: str
    last_accessed: Optional[datetime] = None

class MediaList(BaseModel):
    media: List[MediaFile]
    total: int
    page: int
    page_size: int
    categories: Dict[str, int]

class MediaScanResult(BaseModel):
    scanned_files: int
    new_files: int
    updated_files: int
    errors: List[str]
    categories: Dict[str, int]

class VersionInfo(BaseModel):
    version: str
    build_date: str
    features: List[str]

class ColorPalette(BaseModel):
    primary: str = "#3B82F6"
    secondary: str = "#6B7280"
    accent: str = "#F59E0B"
    background: str = "#FFFFFF"
    surface: str = "#F9FAFB"
    text: str = "#111827"
    text_secondary: str = "#6B7280"
    border: str = "#E5E7EB"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"

class UserPreferences(BaseModel):
    user_id: str
    color_palette: ColorPalette
    theme: str = "light"  # light, dark, auto
    layout: str = "grid"  # grid, list
    items_per_page: int = 20
    auto_scan: bool = True
    show_thumbnails: bool = True
    created_at: datetime
    updated_at: datetime

class UserPreferencesUpdate(BaseModel):
    color_palette: Optional[ColorPalette] = None
    theme: Optional[str] = None
    layout: Optional[str] = None
    items_per_page: Optional[int] = None
    auto_scan: Optional[bool] = None
    show_thumbnails: Optional[bool] = None

class PlaylistItem(BaseModel):
    media_id: str
    position: int
    added_at: datetime

class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    items: List[PlaylistItem] = []
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class PlaylistItemAdd(BaseModel):
    media_id: str
    position: Optional[int] = None

# Security
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

def create_access_token(username: str) -> str:
    """Create access token"""
    token = secrets.token_urlsafe(32)
    tokens_db[token] = {
        "username": username,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    return token

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from token"""
    token = credentials.credentials
    
    if token not in tokens_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = tokens_db[token]
    if datetime.utcnow() > token_data["expires_at"]:
        del tokens_db[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = token_data["username"]
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = users_db[username]
    return User(**user_data)

def detect_media_category(filename: str, mime_type: str) -> MediaCategory:
    """Detect media category based on filename and mime type"""
    filename_lower = filename.lower()
    
    # Kids content detection
    kids_keywords = ['kids', 'children', 'cartoon', 'animated', 'disney', 'pixar', 'nickelodeon', 'cartoon network']
    if any(keyword in filename_lower for keyword in kids_keywords):
        return MediaCategory.KIDS
    
    # TV Shows detection
    tv_patterns = [
        r's\d{2}e\d{2}',  # S01E01
        r'season\s*\d+',  # Season 1
        r'episode\s*\d+', # Episode 1
        r's\d{2}',        # S01
        r'e\d{2}',        # E01
    ]
    if any(re.search(pattern, filename_lower) for pattern in tv_patterns):
        return MediaCategory.TV_SHOWS
    
    # Music videos detection
    music_keywords = ['music video', 'mv', 'concert', 'live', 'performance']
    if any(keyword in filename_lower for keyword in music_keywords):
        return MediaCategory.MUSIC_VIDEOS
    
    # Movies detection (default for video files)
    if mime_type.startswith('video/'):
        return MediaCategory.MOVIES
    
    # Audio files
    if mime_type.startswith('audio/'):
        return MediaCategory.AUDIO
    
    # Images
    if mime_type.startswith('image/'):
        return MediaCategory.IMAGES
    
    return MediaCategory.OTHER

def extract_tv_series_info(filename: str) -> dict:
    """Extract TV series information from filename"""
    filename_lower = filename.lower()
    
    # Extract season and episode numbers
    season_match = re.search(r's(\d{2})', filename_lower)
    episode_match = re.search(r'e(\d{2})', filename_lower)
    
    season = int(season_match.group(1)) if season_match else None
    episode = int(episode_match.group(1)) if episode_match else None
    
    # Extract series name (everything before season/episode info)
    series_name = filename
    if season_match:
        series_name = filename[:season_match.start()].strip()
    elif episode_match:
        series_name = filename[:episode_match.start()].strip()
    
    # Clean up series name
    series_name = re.sub(r'[._-]', ' ', series_name).strip()
    
    return {
        "series_name": series_name,
        "season": season,
        "episode": episode,
        "series_key": f"{series_name.lower()}_s{season:02d}" if season else series_name.lower()
    }

def extract_media_metadata(filename: str, mime_type: str) -> Dict[str, Any]:
    """Extract metadata from filename"""
    metadata = {}
    
    # Extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', filename)
    if year_match:
        metadata['year'] = int(year_match.group())
    
    # Extract quality/resolution
    quality_patterns = {
        '4K': r'\b(4k|2160p|uhd)\b',
        '1080p': r'\b(1080p|fhd)\b',
        '720p': r'\b(720p|hd)\b',
        '480p': r'\b(480p|sd)\b'
    }
    
    for quality, pattern in quality_patterns.items():
        if re.search(pattern, filename.lower()):
            metadata['quality'] = quality
            break
    
    # Extract codec
    codec_patterns = {
        'H.264': r'\b(h264|x264)\b',
        'H.265': r'\b(h265|x265|hevc)\b',
        'VP9': r'\b(vp9)\b',
        'AV1': r'\b(av1)\b'
    }
    
    for codec, pattern in codec_patterns.items():
        if re.search(pattern, filename.lower()):
            metadata['codec'] = codec
            break
    
    return metadata

def format_file_size(bytes: int) -> str:
    """Format file size in human readable format"""
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if bytes == 0:
        return '0 Bytes'
    i = int(math.floor(math.log(bytes) / math.log(1024)))
    return f"{bytes / math.pow(1024, i):.2f} {sizes[i]}"

def generate_artwork(filename: str, category: MediaCategory, mime_type: str) -> str:
    """Generate artwork/thumbnail for media files"""
    try:
        # Create a 300x400 image (3:4 aspect ratio)
        width, height = 300, 400
        image = Image.new('RGB', (width, height), color='#1F2937')
        draw = ImageDraw.Draw(image)
        
        # Define colors based on category
        category_colors = {
            MediaCategory.MOVIES: ('#DC2626', '#FEF2F2'),  # Red
            MediaCategory.TV_SHOWS: ('#2563EB', '#EFF6FF'),  # Blue
            MediaCategory.KIDS: ('#059669', '#ECFDF5'),  # Green
            MediaCategory.MUSIC_VIDEOS: ('#7C3AED', '#F3E8FF'),  # Purple
            MediaCategory.AUDIO: ('#EA580C', '#FFF7ED'),  # Orange
            MediaCategory.IMAGES: ('#0891B2', '#ECFEFF'),  # Cyan
            MediaCategory.OTHER: ('#6B7280', '#F9FAFB')  # Gray
        }
        
        primary_color, light_color = category_colors.get(category, category_colors[MediaCategory.OTHER])
        
        # Create gradient background
        for y in range(height):
            ratio = y / height
            r1, g1, b1 = tuple(int(primary_color[i:i+2], 16) for i in (1, 3, 5))
            r2, g2, b2 = tuple(int(light_color[i:i+2], 16) for i in (1, 3, 5))
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add category icon/emoji
        category_icons = {
            MediaCategory.MOVIES: '🎬',
            MediaCategory.TV_SHOWS: '📺',
            MediaCategory.KIDS: '🧸',
            MediaCategory.MUSIC_VIDEOS: '🎵',
            MediaCategory.AUDIO: '🎧',
            MediaCategory.IMAGES: '🖼️',
            MediaCategory.OTHER: '📁'
        }
        
        icon = category_icons.get(category, '📁')
        
        # Try to use a font, fallback to default
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw icon
        icon_bbox = draw.textbbox((0, 0), icon, font=font_large)
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_height = icon_bbox[3] - icon_bbox[1]
        icon_x = (width - icon_width) // 2
        icon_y = (height - icon_height) // 2 - 40
        draw.text((icon_x, icon_y), icon, fill='white', font=font_large)
        
        # Draw category name
        category_name = category.value.replace('_', ' ').title()
        cat_bbox = draw.textbbox((0, 0), category_name, font=font_medium)
        cat_width = cat_bbox[2] - cat_bbox[0]
        cat_x = (width - cat_width) // 2
        cat_y = icon_y + icon_height + 20
        draw.text((cat_x, cat_y), category_name, fill='white', font=font_medium)
        
        # Draw filename (truncated)
        display_name = filename
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        
        name_bbox = draw.textbbox((0, 0), display_name, font=font_small)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (width - name_width) // 2
        name_y = cat_y + 40
        draw.text((name_x, name_y), display_name, fill='white', font=font_small)
        
        # Draw file type
        file_ext = Path(filename).suffix.upper()
        if file_ext:
            ext_bbox = draw.textbbox((0, 0), file_ext, font=font_small)
            ext_width = ext_bbox[2] - ext_bbox[0]
            ext_x = (width - ext_width) // 2
            ext_y = name_y + 25
            draw.text((ext_x, ext_y), file_ext, fill='white', font=font_small)
        
        # Save to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Error generating artwork: {e}")
        # Return a simple colored rectangle as fallback
        return generate_simple_artwork(category)

def generate_simple_artwork(category: MediaCategory) -> str:
    """Generate a simple colored rectangle as fallback artwork"""
    try:
        width, height = 300, 400
        image = Image.new('RGB', (width, height), color='#1F2937')
        draw = ImageDraw.Draw(image)
        
        # Simple colored rectangle
        category_colors = {
            MediaCategory.MOVIES: '#DC2626',
            MediaCategory.TV_SHOWS: '#2563EB',
            MediaCategory.KIDS: '#059669',
            MediaCategory.MUSIC_VIDEOS: '#7C3AED',
            MediaCategory.AUDIO: '#EA580C',
            MediaCategory.IMAGES: '#0891B2',
            MediaCategory.OTHER: '#6B7280'
        }
        
        color = category_colors.get(category, '#6B7280')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        # Draw colored rectangle
        draw.rectangle([50, 50, width-50, height-50], fill=(r, g, b))
        
        # Save to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Error generating simple artwork: {e}")
        return ""

def get_user_preferences(user_id: str) -> UserPreferences:
    """Get user preferences, create default if not exists"""
    if user_id not in user_preferences_db:
        default_prefs = UserPreferences(
            user_id=user_id,
            color_palette=ColorPalette(),
            theme="light",
            layout="grid",
            items_per_page=20,
            auto_scan=True,
            show_thumbnails=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_preferences_db[user_id] = default_prefs.dict()
    
    return UserPreferences(**user_preferences_db[user_id])

# Create FastAPI app
app = FastAPI(
    title="Watch1 Media Server",
    description="Enhanced Media Server with Scanning and Categorization",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create media directories
MEDIA_ROOT = Path("./media")
THUMBNAILS_ROOT = Path("./thumbnails")
MEDIA_ROOT.mkdir(exist_ok=True)
THUMBNAILS_ROOT.mkdir(exist_ok=True)

# Mount static files
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")
app.mount("/thumbnails", StaticFiles(directory=str(THUMBNAILS_ROOT)), name="thumbnails")

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Watch1 Media Server is running!",
        "version": VERSION,
        "docs": "/api/docs"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "Watch1 Media Server", "version": VERSION}

@app.get("/api/v1/version", response_model=VersionInfo)
async def get_version():
    """Get version information"""
    return VersionInfo(
        version=VERSION,
        build_date=BUILD_DATE,
        features=[
            "Media Scanning and Categorization",
            "Movies, TV Shows, Kids, Music Videos Support",
            "Advanced Media Player",
            "Large Library Pagination",
            "File Upload and Management",
            "User Authentication",
            "Thumbnail Generation",
            "Metadata Extraction"
        ]
    )

@app.post("/api/v1/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email is already used
    for existing_user in users_db.values():
        if existing_user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create user
    user_id = secrets.token_urlsafe(16)
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "password_hash": hashed_password
    }
    
    users_db[user_data.username] = user
    
    # Return user without password
    user_response = user.copy()
    del user_response["password_hash"]
    return User(**user_response)

@app.post("/api/v1/auth/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Login user"""
    if login_data.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    user = users_db[login_data.username]
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    access_token = create_access_token(login_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/v1/user/preferences", response_model=UserPreferences)
async def get_user_preferences_endpoint(current_user: User = Depends(get_current_user)):
    """Get user preferences"""
    return get_user_preferences(current_user.id)

@app.put("/api/v1/user/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences"""
    current_prefs = get_user_preferences(current_user.id)
    
    # Update only provided fields
    update_data = preferences_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(current_prefs, key):
            setattr(current_prefs, key, value)
    
    current_prefs.updated_at = datetime.utcnow()
    
    # Save to database
    user_preferences_db[current_user.id] = current_prefs.dict()
    
    return current_prefs

@app.get("/api/v1/user/preferences/color-palettes")
async def get_color_palettes():
    """Get available color palettes"""
    return {
        "palettes": [
            {
                "name": "Default Blue",
                "colors": {
                    "primary": "#3B82F6",
                    "secondary": "#6B7280",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF",
                    "surface": "#F9FAFB",
                    "text": "#111827",
                    "text_secondary": "#6B7280",
                    "border": "#E5E7EB",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444"
                }
            },
            {
                "name": "Dark Theme",
                "colors": {
                    "primary": "#8B5CF6",
                    "secondary": "#9CA3AF",
                    "accent": "#F59E0B",
                    "background": "#111827",
                    "surface": "#1F2937",
                    "text": "#F9FAFB",
                    "text_secondary": "#D1D5DB",
                    "border": "#374151",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444"
                }
            },
            {
                "name": "Green Nature",
                "colors": {
                    "primary": "#059669",
                    "secondary": "#6B7280",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF",
                    "surface": "#F0FDF4",
                    "text": "#111827",
                    "text_secondary": "#6B7280",
                    "border": "#D1FAE5",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444"
                }
            },
            {
                "name": "Purple Royal",
                "colors": {
                    "primary": "#7C3AED",
                    "secondary": "#6B7280",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF",
                    "surface": "#FAF5FF",
                    "text": "#111827",
                    "text_secondary": "#6B7280",
                    "border": "#E9D5FF",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444"
                }
            },
            {
                "name": "Orange Sunset",
                "colors": {
                    "primary": "#EA580C",
                    "secondary": "#6B7280",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF",
                    "surface": "#FFF7ED",
                    "text": "#111827",
                    "text_secondary": "#6B7280",
                    "border": "#FED7AA",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444"
                }
            }
        ]
    }

# Media endpoints
@app.get("/api/v1/media/", response_model=MediaList)
async def get_media_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[MediaCategory] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|filename|file_size|duration)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user)
):
    """Get media files with advanced filtering and pagination"""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Filter media files
    filtered_media = list(media_db.values())
    
    # Apply category filter
    if category:
        filtered_media = [m for m in filtered_media if m["category"] == category]
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        filtered_media = [
            m for m in filtered_media 
            if search_lower in m["original_filename"].lower() or 
               search_lower in m["filename"].lower()
        ]
    
    # Sort media files
    reverse = sort_order == "desc"
    if sort_by == "created_at":
        filtered_media.sort(key=lambda x: x["created_at"], reverse=reverse)
    elif sort_by == "filename":
        filtered_media.sort(key=lambda x: x["original_filename"].lower(), reverse=reverse)
    elif sort_by == "file_size":
        filtered_media.sort(key=lambda x: x["file_size"], reverse=reverse)
    elif sort_by == "duration":
        filtered_media.sort(key=lambda x: x.get("duration", 0), reverse=reverse)
    
    total = len(filtered_media)
    paginated_media = filtered_media[start_idx:end_idx]
    
    # Count by category
    category_counts = {}
    for media in media_db.values():
        cat = media["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return MediaList(
        media=[MediaFile(**{k: v for k, v in media.items() if k in MediaFile.__fields__}) for media in paginated_media],
        total=total,
        page=page,
        page_size=page_size,
        categories=category_counts
    )

@app.get("/api/v1/media/categories")
async def get_media_categories(current_user: User = Depends(get_current_user)):
    """Get media categories with counts"""
    category_counts = {}
    for media in media_db.values():
        cat = media["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "categories": [
            {"name": cat.value, "count": count, "display_name": cat.value.replace("_", " ").title()}
            for cat, count in category_counts.items()
        ]
    }

@app.get("/api/v1/media/tv-series")
async def get_tv_series(current_user: User = Depends(get_current_user)):
    """Get all TV series with episodes grouped by season"""
    tv_series = {}
    
    for media in media_db.values():
        if media["category"] == MediaCategory.TV_SHOWS:
            series_info = extract_tv_series_info(media["filename"])
            series_key = series_info["series_key"]
            
            if series_key not in tv_series:
                tv_series[series_key] = {
                    "series_name": series_info["series_name"],
                    "seasons": {}
                }
            
            season = series_info["season"] or 1
            episode = series_info["episode"] or 1
            
            if season not in tv_series[series_key]["seasons"]:
                tv_series[series_key]["seasons"][season] = []
            
            tv_series[series_key]["seasons"][season].append({
                "id": media["id"],
                "filename": media["filename"],
                "episode": episode,
                "file_path": media["file_path"],
                "duration": media.get("duration"),
                "artwork": media.get("artwork")
            })
    
    # Sort episodes within each season
    for series in tv_series.values():
        for season in series["seasons"].values():
            season.sort(key=lambda x: x["episode"])
    
    return {"series": list(tv_series.values())}

@app.get("/api/v1/media/tv-series/{series_key}/episodes")
async def get_tv_series_episodes(
    series_key: str,
    season: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Get episodes for a specific TV series, optionally filtered by season"""
    episodes = []
    
    for media in media_db.values():
        if media["category"] == MediaCategory.TV_SHOWS:
            series_info = extract_tv_series_info(media["filename"])
            if series_info["series_key"] == series_key:
                if season is None or series_info["season"] == season:
                    episodes.append({
                        "id": media["id"],
                        "filename": media["filename"],
                        "season": series_info["season"] or 1,
                        "episode": series_info["episode"] or 1,
                        "file_path": media["file_path"],
                        "duration": media.get("duration"),
                        "artwork": media.get("artwork")
                    })
    
    # Sort by season and episode
    episodes.sort(key=lambda x: (x["season"], x["episode"]))
    
    return {"episodes": episodes}

# Playlist endpoints
@app.get("/api/v1/playlists", response_model=List[Playlist])
async def get_playlists(current_user: User = Depends(get_current_user)):
    """Get all playlists for the current user"""
    user_playlists = []
    for playlist in playlists_db.values():
        if playlist["created_by"] == current_user.id or playlist["is_public"]:
            user_playlists.append(Playlist(**playlist))
    return user_playlists

@app.post("/api/v1/playlists", response_model=Playlist)
async def create_playlist(
    playlist_data: PlaylistCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new playlist"""
    playlist_id = secrets.token_urlsafe(16)
    playlist = Playlist(
        id=playlist_id,
        name=playlist_data.name,
        description=playlist_data.description,
        items=[],
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_public=playlist_data.is_public
    )
    
    playlists_db[playlist_id] = playlist.dict()
    return playlist

@app.get("/api/v1/playlists/{playlist_id}", response_model=Playlist)
async def get_playlist(
    playlist_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific playlist"""
    if playlist_id not in playlists_db:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = playlists_db[playlist_id]
    if playlist["created_by"] != current_user.id and not playlist["is_public"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Playlist(**playlist)

@app.put("/api/v1/playlists/{playlist_id}", response_model=Playlist)
async def update_playlist(
    playlist_id: str,
    playlist_data: PlaylistUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a playlist"""
    if playlist_id not in playlists_db:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = playlists_db[playlist_id]
    if playlist["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update only provided fields
    update_data = playlist_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        playlist[key] = value
    
    playlist["updated_at"] = datetime.utcnow()
    playlists_db[playlist_id] = playlist
    
    return Playlist(**playlist)

@app.delete("/api/v1/playlists/{playlist_id}")
async def delete_playlist(
    playlist_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a playlist"""
    if playlist_id not in playlists_db:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = playlists_db[playlist_id]
    if playlist["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del playlists_db[playlist_id]
    return {"message": "Playlist deleted successfully"}

@app.post("/api/v1/playlists/{playlist_id}/items")
async def add_playlist_item(
    playlist_id: str,
    item_data: PlaylistItemAdd,
    current_user: User = Depends(get_current_user)
):
    """Add an item to a playlist"""
    if playlist_id not in playlists_db:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = playlists_db[playlist_id]
    if playlist["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if media file exists
    if item_data.media_id not in media_db:
        raise HTTPException(status_code=404, detail="Media file not found")
    
    # Check if item already exists in playlist
    for item in playlist["items"]:
        if item["media_id"] == item_data.media_id:
            raise HTTPException(status_code=400, detail="Item already in playlist")
    
    # Add item to playlist
    position = item_data.position or len(playlist["items"])
    new_item = PlaylistItem(
        media_id=item_data.media_id,
        position=position,
        added_at=datetime.utcnow()
    )
    
    playlist["items"].append(new_item.dict())
    playlist["updated_at"] = datetime.utcnow()
    playlists_db[playlist_id] = playlist
    
    return {"message": "Item added to playlist successfully"}

@app.delete("/api/v1/playlists/{playlist_id}/items/{media_id}")
async def remove_playlist_item(
    playlist_id: str,
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove an item from a playlist"""
    if playlist_id not in playlists_db:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = playlists_db[playlist_id]
    if playlist["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Remove item from playlist
    playlist["items"] = [item for item in playlist["items"] if item["media_id"] != media_id]
    playlist["updated_at"] = datetime.utcnow()
    playlists_db[playlist_id] = playlist
    
    return {"message": "Item removed from playlist successfully"}

@app.get("/api/v1/playlists/{playlist_id}/media")
async def get_playlist_media(
    playlist_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get media files in a playlist"""
    if playlist_id not in playlists_db:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    playlist = playlists_db[playlist_id]
    if playlist["created_by"] != current_user.id and not playlist["is_public"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get media files for playlist items
    media_files = []
    for item in playlist["items"]:
        if item["media_id"] in media_db:
            media_files.append(MediaFile(**media_db[item["media_id"]]))
    
    return {"media": media_files}

@app.get("/api/v1/media/{media_id}/stream")
async def stream_media(
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stream media file"""
    if media_id not in media_db:
        raise HTTPException(status_code=404, detail="Media file not found")
    
    media = media_db[media_id]
    file_path = Path(media["file_path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Media file not found on disk")
    
    # Update last accessed time
    media_db[media_id]["last_accessed"] = datetime.utcnow()
    
    # Return file path for streaming (in production, use proper streaming)
    return {"stream_url": f"/api/v1/media/{media_id}/file"}

@app.get("/api/v1/media/{media_id}/file")
async def serve_media_file(
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    """Serve media file directly"""
    if media_id not in media_db:
        raise HTTPException(status_code=404, detail="Media file not found")
    
    media = media_db[media_id]
    file_path = Path(media["file_path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Media file not found on disk")
    
    # Update last accessed time
    media_db[media_id]["last_accessed"] = datetime.utcnow()
    
    # Return file response
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        media_type=media["mime_type"],
        filename=media["original_filename"]
    )

@app.get("/api/v1/media/scan-info")
async def get_scan_info(current_user: User = Depends(get_current_user)):
    """Get information about scan directories and current library stats"""
    scan_path = Path("./media")
    
    # Get directory info
    directory_info = {
        "scan_directory": str(scan_path),
        "scan_directory_exists": scan_path.exists(),
        "scan_directory_absolute": str(scan_path.absolute()) if scan_path.exists() else None
    }
    
    if scan_path.exists():
        # Count files in directory
        all_files = list(scan_path.rglob('*'))
        total_files = len([f for f in all_files if f.is_file()])
        
        # Supported extensions
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'}
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg'}
        all_extensions = video_extensions | audio_extensions | image_extensions
        
        media_files = [f for f in all_files if f.is_file() and f.suffix.lower() in all_extensions]
        
        directory_info.update({
            "total_files_in_directory": total_files,
            "media_files_in_directory": len(media_files),
            "supported_extensions": list(all_extensions)
        })
    
    # Get current library stats
    category_counts = {}
    total_size = 0
    for media in media_db.values():
        cat = media["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        total_size += media.get("file_size", 0)
    
    library_stats = {
        "total_media_files": len(media_db),
        "total_size_bytes": total_size,
        "total_size_formatted": format_file_size(total_size),
        "categories": {
            cat.value: {
                "count": count,
                "display_name": cat.value.replace("_", " ").title()
            }
            for cat, count in category_counts.items()
        }
    }
    
    return {
        "directory_info": directory_info,
        "library_stats": library_stats,
        "last_scan": "Not available"  # TODO: Track last scan time
    }

@app.get("/api/v1/media/{media_id}", response_model=MediaFile)
async def get_media_file(
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific media file"""
    if media_id not in media_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Update last accessed
    media_db[media_id]["last_accessed"] = datetime.utcnow()
    
    return MediaFile(**media_db[media_id])

@app.post("/api/v1/media/upload", response_model=MediaFile)
async def upload_media_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a media file with automatic categorization"""
    
    # Validate file type
    allowed_types = [
        'video/mp4', 'video/avi', 'video/mkv', 'video/mov', 'video/wmv',
        'video/flv', 'video/webm', 'video/m4v', 'video/3gp',
        'audio/mp3', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg', 'audio/m4a',
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported"
        )
    
    # Generate unique filename
    file_id = secrets.token_urlsafe(16)
    file_extension = Path(file.filename).suffix
    safe_filename = f"{file_id}{file_extension}"
    file_path = MEDIA_ROOT / safe_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Detect category and extract metadata
        category = detect_media_category(file.filename, file.content_type)
        metadata = extract_media_metadata(file.filename, file.content_type)
        
        # Create media record
        media_record = {
            "id": file_id,
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "mime_type": file.content_type,
            "category": category,
            "duration": None,  # TODO: Extract from video/audio files
            "width": None,     # TODO: Extract from video/image files
            "height": None,    # TODO: Extract from video/image files
            "bitrate": None,   # TODO: Extract from media files
            "codec": metadata.get("codec"),
            "container_format": file_extension[1:].upper(),
            "thumbnail_path": None,  # TODO: Generate thumbnails
            "poster_path": None,     # TODO: Generate posters
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "uploaded_by": current_user.username,
            "last_accessed": None
        }
        
        media_db[file_id] = media_record
        
        return MediaFile(**media_record)
        
    except Exception as e:
        # Clean up file if something went wrong
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@app.post("/api/v1/media/scan", response_model=MediaScanResult)
async def scan_media_directory(
    directory: str = "./media",
    current_user: User = Depends(get_current_user)
):
    """Scan directory for media files and add to database with detailed progress tracking"""
    scan_path = Path(directory)
    if not scan_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Directory does not exist: {directory}"
        )
    
    print(f"🔍 Starting media scan of: {scan_path}")
    print(f"📁 Scanning directory: {scan_path.absolute()}")
    
    scanned_files = 0
    new_files = 0
    updated_files = 0
    skipped_files = 0
    errors = []
    category_counts = {}
    directory_stats = {}
    
    # Supported file extensions
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg'}
    
    all_extensions = video_extensions | audio_extensions | image_extensions
    
    # Get all files to scan
    all_files = list(scan_path.rglob('*'))
    total_files = len([f for f in all_files if f.is_file()])
    media_files = [f for f in all_files if f.is_file() and f.suffix.lower() in all_extensions]
    
    print(f"📊 Found {total_files} total files, {len(media_files)} media files")
    
    for i, file_path in enumerate(media_files, 1):
        scanned_files += 1
        
        # Progress logging every 10 files
        if i % 10 == 0 or i == len(media_files):
            print(f"📈 Progress: {i}/{len(media_files)} files processed ({i/len(media_files)*100:.1f}%)")
        
        try:
            # Track directory stats
            parent_dir = str(file_path.parent.relative_to(scan_path))
            if parent_dir not in directory_stats:
                directory_stats[parent_dir] = {"files": 0, "size": 0}
            directory_stats[parent_dir]["files"] += 1
            directory_stats[parent_dir]["size"] += file_path.stat().st_size
            
            # Check if file already exists
            existing_file = None
            for media_id, media in media_db.items():
                if media["file_path"] == str(file_path):
                    existing_file = media_id
                    break
            
            if existing_file:
                # Update existing file
                old_size = media_db[existing_file]["file_size"]
                new_size = file_path.stat().st_size
                
                media_db[existing_file]["file_size"] = new_size
                media_db[existing_file]["last_accessed"] = datetime.utcnow()
                
                if old_size != new_size:
                    print(f"🔄 Updated: {file_path.name} (size changed: {old_size} -> {new_size})")
                
                updated_files += 1
            else:
                # Create new media record
                file_id = secrets.token_urlsafe(16)
                mime_type, _ = mimetypes.guess_type(str(file_path))
                
                # Handle common video formats that might not be detected properly
                if not mime_type:
                    file_ext = file_path.suffix.lower()
                    if file_ext in ['.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg']:
                        mime_type = "video/mp4"  # Use a generic video MIME type
                    elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']:
                        mime_type = "audio/mpeg"  # Use a generic audio MIME type
                    else:
                        mime_type = "application/octet-stream"
                
                category = detect_media_category(file_path.name, mime_type)
                metadata = extract_media_metadata(file_path.name, mime_type)
                
                # Generate artwork for the media file
                artwork = generate_artwork(file_path.name, category, mime_type)
                
                media_record = {
                    "id": file_id,
                    "filename": file_path.name,
                    "original_filename": file_path.name,
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "mime_type": mime_type,
                    "category": category,
                    "duration": None,
                    "width": None,
                    "height": None,
                    "bitrate": None,
                    "codec": metadata.get("codec"),
                    "container_format": file_path.suffix[1:].upper(),
                    "thumbnail_path": None,
                    "poster_path": None,
                    "artwork": artwork,
                    "metadata": metadata,
                    "created_at": datetime.utcnow(),
                    "uploaded_by": current_user.username,
                    "last_accessed": None
                }
                
                media_db[file_id] = media_record
                new_files += 1
                print(f"➕ Added: {file_path.name} ({category.value})")
            
            # Count categories
            category = detect_media_category(file_path.name, mime_type)
            category_counts[category] = category_counts.get(category, 0) + 1
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    # Print summary
    print(f"\n📊 SCAN COMPLETE:")
    print(f"   📁 Directory: {scan_path}")
    print(f"   🔍 Scanned: {scanned_files} media files")
    print(f"   ➕ New: {new_files} files")
    print(f"   🔄 Updated: {updated_files} files")
    print(f"   ❌ Errors: {len(errors)} files")
    print(f"   📂 Categories found:")
    for category, count in category_counts.items():
        print(f"      - {category.value}: {count} files")
    
    return MediaScanResult(
        scanned_files=scanned_files,
        new_files=new_files,
        updated_files=updated_files,
        errors=errors,
        categories=category_counts
    )

@app.delete("/api/v1/media/{media_id}")
async def delete_media_file(
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a media file"""
    if media_id not in media_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    media_record = media_db[media_id]
    
    # Only allow deletion by the uploader or admin
    if media_record["uploaded_by"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own files"
        )
    
    # Delete file from filesystem
    file_path = Path(media_record["file_path"])
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    del media_db[media_id]
    
    return {"message": "Media file deleted successfully"}

# Create default admin user and sample media on startup
@app.on_event("startup")
async def startup_event():
    """Create default admin user and sample media"""
    admin_username = "admin"
    admin_password = "admin123"
    
    if admin_username not in users_db:
        user_id = secrets.token_urlsafe(16)
        hashed_password = hash_password(admin_password)
        
        admin_user = {
            "id": user_id,
            "username": admin_username,
            "email": "admin@watch1.local",
            "full_name": "Administrator",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "password_hash": hashed_password
        }
        
        users_db[admin_username] = admin_user
        print(f"✅ Created default admin user: {admin_username} / {admin_password}")
    
    # Create sample media entries for demo
    sample_media = [
        {
            "id": "sample_movie",
            "filename": "sample_movie.mp4",
            "original_filename": "The Great Adventure (2023) 1080p.mp4",
            "file_path": "/app/media/sample_movie.mp4",
            "file_size": 2048000,
            "mime_type": "video/mp4",
            "category": MediaCategory.MOVIES,
            "duration": 7200.0,  # 2 hours
            "width": 1920,
            "height": 1080,
            "bitrate": 5000,
            "codec": "H.264",
            "container_format": "MP4",
            "thumbnail_path": None,
            "poster_path": None,
            "metadata": {"year": 2023, "quality": "1080p", "codec": "H.264"},
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin",
            "last_accessed": None
        },
        {
            "id": "sample_tv_show",
            "filename": "sample_tv_show.mp4",
            "original_filename": "Amazing Series S01E01.mp4",
            "file_path": "/app/media/sample_tv_show.mp4",
            "file_size": 1024000,
            "mime_type": "video/mp4",
            "category": MediaCategory.TV_SHOWS,
            "duration": 2700.0,  # 45 minutes
            "width": 1920,
            "height": 1080,
            "bitrate": 3000,
            "codec": "H.264",
            "container_format": "MP4",
            "thumbnail_path": None,
            "poster_path": None,
            "metadata": {"quality": "1080p", "codec": "H.264"},
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin",
            "last_accessed": None
        },
        {
            "id": "sample_kids",
            "filename": "sample_kids.mp4",
            "original_filename": "Kids Cartoon Adventure.mp4",
            "file_path": "/app/media/sample_kids.mp4",
            "file_size": 512000,
            "mime_type": "video/mp4",
            "category": MediaCategory.KIDS,
            "duration": 1800.0,  # 30 minutes
            "width": 1280,
            "height": 720,
            "bitrate": 2000,
            "codec": "H.264",
            "container_format": "MP4",
            "thumbnail_path": None,
            "poster_path": None,
            "metadata": {"quality": "720p", "codec": "H.264"},
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin",
            "last_accessed": None
        },
        {
            "id": "sample_music_video",
            "filename": "sample_music_video.mp4",
            "original_filename": "Awesome Song Music Video.mp4",
            "file_path": "/app/media/sample_music_video.mp4",
            "file_size": 256000,
            "mime_type": "video/mp4",
            "category": MediaCategory.MUSIC_VIDEOS,
            "duration": 240.0,  # 4 minutes
            "width": 1920,
            "height": 1080,
            "bitrate": 4000,
            "codec": "H.264",
            "container_format": "MP4",
            "thumbnail_path": None,
            "poster_path": None,
            "metadata": {"quality": "1080p", "codec": "H.264"},
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin",
            "last_accessed": None
        },
        {
            "id": "sample_audio",
            "filename": "sample_audio.mp3",
            "original_filename": "Great Song.mp3",
            "file_path": "/app/media/sample_audio.mp3",
            "file_size": 512000,
            "mime_type": "audio/mp3",
            "category": MediaCategory.AUDIO,
            "duration": 180.0,  # 3 minutes
            "width": None,
            "height": None,
            "bitrate": 320,
            "codec": "MP3",
            "container_format": "MP3",
            "thumbnail_path": None,
            "poster_path": None,
            "metadata": {"codec": "MP3"},
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin",
            "last_accessed": None
        }
    ]
    
    for media in sample_media:
        if media["id"] not in media_db:
            media_db[media["id"]] = media
    
    print(f"✅ Created {len(sample_media)} sample media files")
    print(f"✅ Watch1 Media Server v{VERSION} is ready!")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
