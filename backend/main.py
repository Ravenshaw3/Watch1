"""
Watch1 Media Server - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.exceptions import Watch1Exception


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Watch1 Media Server...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create media directories
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.THUMBNAILS_ROOT, exist_ok=True)
    os.makedirs(settings.TRANSCODED_ROOT, exist_ok=True)
    
    print("✅ Watch1 Media Server started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Watch1 Media Server...")


# Create FastAPI application
app = FastAPI(
    title="Watch1 Media Server",
    description="High-performance media server with advanced features",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files
app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")
app.mount("/thumbnails", StaticFiles(directory=settings.THUMBNAILS_ROOT), name="thumbnails")
app.mount("/transcoded", StaticFiles(directory=settings.TRANSCODED_ROOT), name="transcoded")

# Global exception handler
@app.exception_handler(Watch1Exception)
async def watch1_exception_handler(request, exc: Watch1Exception):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Watch1 Media Server",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Watch1 Media Server",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
