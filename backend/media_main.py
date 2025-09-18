"""
Watch1 Media Server - Backend with Full Media Management
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uvicorn
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os
import shutil
from pathlib import Path
import mimetypes

# Simple in-memory storage for demo (replace with database in production)
users_db = {}
tokens_db = {}
media_db = {}

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
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    uploaded_by: str

class MediaList(BaseModel):
    media: List[MediaFile]
    total: int
    page: int
    page_size: int

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

# Create FastAPI app
app = FastAPI(
    title="Watch1 Media Server",
    description="Media server with full media management",
    version="1.0.0",
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
MEDIA_ROOT = Path("/app/media")
THUMBNAILS_ROOT = Path("/app/thumbnails")
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
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "Watch1 Media Server"}

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

@app.get("/api/v1/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    """Get all users (admin only for now)"""
    users = []
    for user_data in users_db.values():
        user_response = user_data.copy()
        del user_response["password_hash"]
        users.append(User(**user_response))
    return users

# Media endpoints
@app.get("/api/v1/media/", response_model=MediaList)
async def get_media_files(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get media files with pagination"""
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    media_list = list(media_db.values())
    total = len(media_list)
    
    # Sort by creation date (newest first)
    media_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    paginated_media = media_list[start_idx:end_idx]
    
    return MediaList(
        media=[MediaFile(**media) for media in paginated_media],
        total=total,
        page=page,
        page_size=page_size
    )

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
    
    return MediaFile(**media_db[media_id])

@app.post("/api/v1/media/upload", response_model=MediaFile)
async def upload_media_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a media file"""
    
    # Validate file type
    allowed_types = [
        'video/mp4', 'video/avi', 'video/mkv', 'video/mov', 'video/wmv',
        'video/flv', 'video/webm', 'video/m4v',
        'audio/mp3', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg',
        'image/jpeg', 'image/png', 'image/gif', 'image/webp'
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
        
        # Create media record
        media_record = {
            "id": file_id,
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "mime_type": file.content_type,
            "duration": None,  # TODO: Extract from video/audio files
            "width": None,     # TODO: Extract from video/image files
            "height": None,    # TODO: Extract from video/image files
            "created_at": datetime.utcnow(),
            "uploaded_by": current_user.username
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

# Create default admin user on startup
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
            "id": "sample1",
            "filename": "sample_video.mp4",
            "original_filename": "Sample Video.mp4",
            "file_path": "/app/media/sample_video.mp4",
            "file_size": 1024000,
            "mime_type": "video/mp4",
            "duration": 120.5,
            "width": 1920,
            "height": 1080,
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin"
        },
        {
            "id": "sample2",
            "filename": "sample_audio.mp3",
            "original_filename": "Sample Audio.mp3",
            "file_path": "/app/media/sample_audio.mp3",
            "file_size": 512000,
            "mime_type": "audio/mp3",
            "duration": 180.0,
            "width": None,
            "height": None,
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin"
        },
        {
            "id": "sample3",
            "filename": "sample_image.jpg",
            "original_filename": "Sample Image.jpg",
            "file_path": "/app/media/sample_image.jpg",
            "file_size": 256000,
            "mime_type": "image/jpeg",
            "duration": None,
            "width": 1920,
            "height": 1080,
            "created_at": datetime.utcnow(),
            "uploaded_by": "admin"
        }
    ]
    
    for media in sample_media:
        if media["id"] not in media_db:
            media_db[media["id"]] = media
    
    print(f"✅ Created {len(sample_media)} sample media files")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
