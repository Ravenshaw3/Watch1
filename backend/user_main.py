"""
Watch1 Media Server - Backend with User Management
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uvicorn
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os

# Simple in-memory storage for demo (replace with database in production)
users_db = {}
tokens_db = {}

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

class TokenData(BaseModel):
    username: Optional[str] = None

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
    description="Media server with user authentication",
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

@app.get("/api/v1/media/")
async def get_media(current_user: User = Depends(get_current_user)):
    """Get media files (placeholder)"""
    return {
        "media": [],
        "message": "Media endpoint working",
        "user": current_user.username
    }

# Create default admin user on startup
@app.on_event("startup")
async def startup_event():
    """Create default admin user"""
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
