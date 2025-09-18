# Configuration Guide

This guide covers all configuration options available in Watch1 Media Server.

## Configuration Files

Watch1 uses several configuration files:

- `.env` - Environment variables
- `docker-compose.yml` - Docker services configuration
- `nginx/nginx.conf` - Nginx reverse proxy configuration
- `backend/app/core/config.py` - Backend application settings

## Environment Variables

### Application Settings

```env
# Application
APP_NAME=Watch1 Media Server
VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
```

### Database Configuration

```env
# PostgreSQL Database
DATABASE_URL=postgresql://username:password@host:port/database
DATABASE_ECHO=false  # Set to true for SQL query logging
```

### Redis Configuration

```env
# Redis Cache
REDIS_URL=redis://host:port/database
```

### Media Storage

```env
# Media Directories
MEDIA_ROOT=/app/media
THUMBNAILS_ROOT=/app/thumbnails
TRANSCODED_ROOT=/app/transcoded
MAX_FILE_SIZE=10737418240  # 10GB in bytes
```

### Supported Media Formats

```env
# Video Formats
SUPPORTED_VIDEO_FORMATS=.mp4,.avi,.mkv,.mov,.wmv,.flv,.webm,.m4v

# Audio Formats
SUPPORTED_AUDIO_FORMATS=.mp3,.wav,.flac,.aac,.ogg,.m4a,.wma

# Image Formats
SUPPORTED_IMAGE_FORMATS=.jpg,.jpeg,.png,.gif,.bmp,.webp,.tiff
```

### FFmpeg Settings

```env
# FFmpeg Paths
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe

# Thumbnail Settings
THUMBNAIL_SIZE=320,180
THUMBNAIL_QUALITY=85

# Transcoding Settings
TRANSCODE_QUALITY=medium  # low, medium, high
TRANSCODE_FORMAT=mp4
```

### Authentication

```env
# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
```

### CORS and Security

```env
# CORS
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Security Headers
X_FRAME_OPTIONS=SAMEORIGIN
X_CONTENT_TYPE_OPTIONS=nosniff
```

## Docker Configuration

### Docker Compose Services

The `docker-compose.yml` file defines the following services:

- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **backend**: FastAPI application
- **frontend**: Vue.js application
- **nginx**: Reverse proxy
- **celery-worker**: Background task worker
- **celery-beat**: Scheduled task scheduler

### Service Configuration

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://watch1:password@postgres:5432/watch1
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your-secret-key
    volumes:
      - ./backend:/app
      - media_files:/app/media
    ports:
      - "8000:8000"
```

### Volume Mounts

```yaml
volumes:
  postgres_data:    # Database data
  redis_data:       # Redis data
  media_files:      # Media files storage
```

## Nginx Configuration

### Reverse Proxy Settings

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}
```

### API Routes

```nginx
location /api/ {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Media Streaming

```nginx
location /media/ {
    proxy_pass http://backend;
    # Enable range requests for video streaming
    proxy_set_header Range $http_range;
    proxy_set_header If-Range $http_if_range;
    proxy_no_cache $http_range $http_if_range;
}
```

## Backend Configuration

### Database Models

Configure database models in `backend/app/models/`:

- `user.py` - User authentication and profiles
- `media.py` - Media files and metadata

### API Endpoints

API endpoints are defined in `backend/app/api/v1/endpoints/`:

- `auth.py` - Authentication endpoints
- `users.py` - User management
- `media.py` - Media file operations
- `playlists.py` - Playlist management

### Background Tasks

Configure Celery tasks in `backend/app/tasks/`:

```python
from celery import Celery

celery = Celery('watch1')

@celery.task
def process_media_file(file_id):
    # Media processing logic
    pass
```

## Frontend Configuration

### Vite Configuration

Configure the build system in `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### Environment Variables

Frontend environment variables in `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Watch1 Media Server
VITE_APP_VERSION=1.0.0
```

## Production Configuration

### Security Settings

For production deployment:

```env
# Security
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=generate-secure-random-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/watch1_prod

# SSL
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### Performance Tuning

```env
# Database
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_MAX_CONNECTIONS=100

# Media Processing
MAX_CONCURRENT_TRANSCODING=4
THUMBNAIL_BATCH_SIZE=10
```

### Monitoring

```env
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Metrics
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Configuration Validation

### Backend Validation

The backend validates configuration on startup:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
```

### Frontend Validation

Frontend validates environment variables:

```typescript
const config = {
  apiUrl: import.meta.env.VITE_API_URL || '/api/v1',
  appName: import.meta.env.VITE_APP_NAME || 'Watch1',
}
```

## Configuration Management

### Environment-Specific Configs

Create separate configuration files:

- `.env.development` - Development settings
- `.env.staging` - Staging settings
- `.env.production` - Production settings

### Configuration Override

Override settings using environment variables:

```bash
# Override specific settings
export SECRET_KEY=new-secret-key
export DEBUG=false

# Start application
docker-compose up -d
```

## Troubleshooting Configuration

### Common Issues

**Configuration not loading**
- Check file permissions
- Verify environment variable names
- Ensure proper file encoding (UTF-8)

**Database connection errors**
- Verify connection string format
- Check network connectivity
- Validate credentials

**Media processing failures**
- Verify FFmpeg installation
- Check file permissions
- Validate media format support

### Configuration Testing

Test configuration with:

```bash
# Backend configuration test
cd backend
python -c "from app.core.config import settings; print(settings.dict())"

# Frontend configuration test
cd frontend
npm run type-check
```

## Best Practices

1. **Use environment variables** for sensitive data
2. **Validate configuration** on startup
3. **Use separate configs** for different environments
4. **Document all settings** and their purposes
5. **Test configuration** before deployment
6. **Monitor configuration** changes
7. **Use secrets management** for production
8. **Regular configuration** backups
