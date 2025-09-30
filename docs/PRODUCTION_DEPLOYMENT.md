# Watch1 Structured Backend - Production Deployment Guide

## Overview

This guide covers deploying Watch1 Media Server with the new structured backend architecture to production environments, specifically optimized for Unraid servers.

## Prerequisites

### System Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Storage**: Minimum 10GB for application data
- **Memory**: Minimum 2GB RAM recommended
- **Network**: Ports 80, 443, 3000, 8000 available

### Media Storage
- **Unraid Path**: `/mnt/user/media` (or your media share path)
- **Supported Formats**: MP4, MKV, AVI, MOV, MP3, FLAC, etc.
- **Directory Structure**: Organized by category (Movies, TV Shows, Music, etc.)

## Production Configuration

### 1. Environment Variables

Update the following environment variables in `docker-compose.yml`:

```yaml
environment:
  # Flask Configuration
  - FLASK_ENV=production
  - FLASK_DEBUG=false
  
  # Database Configuration (SQLite for production)
  - DATABASE_URL=sqlite:///app/data/watch1.db
  
  # Security Configuration
  - JWT_SECRET_KEY=your-secure-jwt-secret-key-minimum-32-characters-long
  
  # CORS Configuration (update with your domain)
  - CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  
  # Media Paths
  - MEDIA_ROOT=/app/media
  - THUMBNAILS_ROOT=/app/thumbnails
  - DATA_ROOT=/app/data
```

### 2. Volume Mounts

Configure volume mounts for Unraid:

```yaml
volumes:
  # Media files (read-only recommended)
  - /mnt/user/media:/app/media:ro
  
  # Application data (read-write)
  - /mnt/user/appdata/watch1/data:/app/data
  
  # Thumbnails and cache (read-write)
  - /mnt/user/appdata/watch1/thumbnails:/app/thumbnails
```

### 3. Network Configuration

```yaml
networks:
  watch1-network:
    driver: bridge
```

## Deployment Steps

### Step 1: Prepare Environment

```bash
# Create application directories on Unraid
mkdir -p /mnt/user/appdata/watch1/data
mkdir -p /mnt/user/appdata/watch1/thumbnails
mkdir -p /mnt/user/appdata/watch1/logs

# Set proper permissions
chmod 755 /mnt/user/appdata/watch1/data
chmod 755 /mnt/user/appdata/watch1/thumbnails
```

### Step 2: Configure Security

```bash
# Generate secure JWT secret (32+ characters)
openssl rand -base64 32

# Update docker-compose.yml with the generated secret
# Replace: JWT_SECRET_KEY=your-secure-jwt-secret-key...
```

### Step 3: Deploy Services

```bash
# Navigate to Watch1 directory
cd /path/to/Watch1

# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f watch1-backend
```

### Step 4: Initialize Database

```bash
# Initialize database with admin user
docker-compose exec watch1-backend python tools/seed-database.py

# Or create custom admin user
docker-compose exec watch1-backend python -c "
from tools.seed_database import create_admin_user
create_admin_user('admin@yourdomain.com', 'your-secure-password')
"
```

### Step 5: Verify Deployment

```bash
# Test backend health
curl http://localhost:8000/health

# Test structured endpoints
curl http://localhost:8000/api/v1/system/version

# Test frontend
curl http://localhost:3000
```

## Health Monitoring

### Health Check Endpoints

The structured backend provides multiple health check endpoints:

```bash
# Basic health check
GET /health
Response: {"status": "healthy", "version": "3.0.4"}

# Detailed health check
GET /api/v1/system/health-detailed
Response: {
  "status": "healthy",
  "version": "3.0.4",
  "framework": "Flask",
  "architecture": "Structured Backend",
  "database": {"status": "connected", "type": "SQLite"},
  "environment": {"flask_env": "production", "debug_mode": false},
  "timestamp": "2025-09-29T18:47:01Z"
}

# System version information
GET /api/v1/system/version
Response: {
  "version": "3.0.4",
  "framework": "Flask",
  "architecture": "Structured Backend",
  "build_date": "2025-09-29",
  "api_version": "v1",
  "features": [...]
}
```

### Docker Health Checks

Services include built-in Docker health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## SSL/HTTPS Configuration

### Using Nginx Reverse Proxy

The included Nginx service provides SSL termination:

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /api/ {
        proxy_pass http://watch1-backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        proxy_pass http://watch1-frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Management

### SQLite Production Database

The structured backend uses SQLite for production simplicity:

```bash
# Database location
/mnt/user/appdata/watch1/data/watch1.db

# Backup database
docker-compose exec watch1-backend cp /app/data/watch1.db /app/data/watch1_backup_$(date +%Y%m%d_%H%M%S).db

# View database info (requires admin login)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/v1/system/database-info
```

### Database Initialization

```bash
# Seed with sample data
docker-compose exec watch1-backend python tools/seed-database.py

# Custom initialization
docker-compose exec watch1-backend python -c "
from postgres_config import get_db_connection
# Custom database setup code here
"
```

## Performance Optimization

### Resource Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  watch1-backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

### Caching Configuration

```yaml
environment:
  # Enable caching
  - CACHE_TYPE=simple
  - CACHE_DEFAULT_TIMEOUT=300
```

## Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check logs
docker-compose logs watch1-backend

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Port conflicts
```

#### 2. Frontend Can't Connect to Backend
```bash
# Check network connectivity
docker-compose exec watch1-frontend curl http://watch1-backend:8000/health

# Verify CORS configuration
# Check CORS_ORIGINS environment variable
```

#### 3. Database Issues
```bash
# Check database file permissions
ls -la /mnt/user/appdata/watch1/data/

# Recreate database
docker-compose exec watch1-backend rm /app/data/watch1.db
docker-compose exec watch1-backend python tools/seed-database.py
```

#### 4. Authentication Problems
```bash
# Verify JWT secret is set
docker-compose exec watch1-backend env | grep JWT_SECRET_KEY

# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"testpass123"}'
```

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```yaml
environment:
  - FLASK_DEBUG=true  # Only for debugging!
  - FLASK_ENV=development
```

**⚠️ Never use debug mode in production!**

## Maintenance

### Regular Tasks

```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f

# Backup database
docker-compose exec watch1-backend python -c "
import shutil
from datetime import datetime
backup_name = f'/app/data/watch1_backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db'
shutil.copy('/app/data/watch1.db', backup_name)
print(f'Backup created: {backup_name}')
"
```

### Log Management

```bash
# View recent logs
docker-compose logs --tail=100 watch1-backend

# Follow logs in real-time
docker-compose logs -f watch1-backend

# Log rotation (configure in docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Security Considerations

### Production Security Checklist

- [ ] **JWT Secret**: Use strong, unique JWT secret key (32+ characters)
- [ ] **CORS Origins**: Configure specific domains, not wildcards
- [ ] **HTTPS**: Enable SSL/TLS encryption
- [ ] **File Permissions**: Restrict access to data directories
- [ ] **Network**: Use Docker networks, not host networking
- [ ] **Updates**: Keep Docker images updated
- [ ] **Backups**: Regular database backups
- [ ] **Monitoring**: Set up health check monitoring
- [ ] **Logs**: Configure log rotation and monitoring

### User Management

```bash
# Create admin user
docker-compose exec watch1-backend python -c "
import hashlib
from postgres_config import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
password_hash = hashlib.sha256('your-secure-password'.encode()).hexdigest()
cursor.execute('''
    INSERT INTO users (email, password_hash, is_active, is_superuser)
    VALUES (%s, %s, %s, %s)
''', ('admin@yourdomain.com', password_hash, True, True))
conn.commit()
print('Admin user created')
"
```

## Monitoring and Alerts

### Health Check Monitoring

Set up external monitoring for:
- `/health` endpoint availability
- Response time monitoring
- Database connectivity
- Disk space usage
- Container resource usage

### Log Monitoring

Monitor logs for:
- Authentication failures
- Database errors
- High response times
- Resource exhaustion

## Conclusion

The structured backend provides a robust, production-ready foundation for Watch1 Media Server. This deployment guide ensures proper configuration for Unraid and other production environments while maintaining security and performance best practices.

For additional support or advanced configuration, refer to the structured backend documentation in `docs/STRUCTURED_BACKEND.md`.
