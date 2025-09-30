# Watch1 Media Server - Unraid Deployment Guide

## Overview
This guide will help you deploy the Watch1 Media Server on your Unraid server using Docker containers.

## Prerequisites
- Unraid 6.8+ with Docker support
- Docker Compose plugin installed
- At least 2GB RAM available
- Network access to your Unraid server

## Quick Start

### 1. Upload Files to Unraid
Upload the entire Watch1 project to your Unraid server. Recommended location:
```
/mnt/user/appdata/watch1/
```

### 2. Set Permissions
Make the scripts executable:
```bash
chmod +x /mnt/user/appdata/watch1/deploy.sh
chmod +x /mnt/user/appdata/watch1/update.sh
chmod +x /mnt/user/appdata/watch1/manage.sh
```

### 3. Deploy
Run the deployment script:
```bash
cd /mnt/user/appdata/watch1
./deploy.sh
```

## Directory Structure
```
/mnt/user/appdata/watch1/
├── backend/                 # Backend application
├── frontend/               # Frontend application
├── nginx/                  # Nginx configuration
├── docker-compose.yml      # Docker Compose configuration
├── deploy.sh              # Deployment script
├── update.sh              # Update script
├── manage.sh              # Management script
└── media/                 # Media files (created during deployment)
    ├── movies/
    ├── tv-shows/
    ├── kids/
    ├── music-videos/
    └── other/
```

## Access URLs
- **Main Application**: http://your-unraid-ip/
- **Backend API**: http://your-unraid-ip/api/v1/
- **Direct Backend**: http://your-unraid-ip:8000/

## Default Login
- **Username**: admin
- **Password**: admin123

**⚠️ Important**: Change the default password after first login!

## Management Commands

### Using the Management Script
```bash
./manage.sh [command]
```

Available commands:
- `start` - Start all services
- `stop` - Stop all services
- `restart` - Restart all services
- `status` - Show service status
- `logs` - Show all logs
- `logs-backend` - Show backend logs only
- `logs-frontend` - Show frontend logs only
- `logs-nginx` - Show nginx logs only
- `update` - Update to latest version
- `backup` - Backup data and configuration
- `restore` - Restore from backup
- `clean` - Clean up unused Docker resources
- `scan` - Scan media directory
- `health` - Check service health

### Using Docker Compose Directly
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

## Adding Media Files

### Method 1: Direct File Copy
Copy your media files to the appropriate directories:
```bash
# Movies
cp /path/to/your/movies/* /mnt/user/appdata/watch1/media/movies/

# TV Shows
cp /path/to/your/tv-shows/* /mnt/user/appdata/watch1/media/tv-shows/

# Kids Content
cp /path/to/your/kids/* /mnt/user/appdata/watch1/media/kids/

# Music Videos
cp /path/to/your/music-videos/* /mnt/user/appdata/watch1/media/music-videos/
```

### Method 2: Using Unraid File Manager
1. Open Unraid Web Interface
2. Go to "Main" → "Shares"
3. Navigate to your media share
4. Copy files to the appropriate Watch1 media directories

### Method 3: Network Mount
Mount your existing media shares:
```bash
# Add to docker-compose.yml under volumes
- /mnt/user/your-media-share:/app/media/external:ro
```

## Scanning Media
After adding media files, scan the directory:
```bash
./manage.sh scan
```

Or use the web interface:
1. Login to Watch1
2. Go to Library
3. Click "Scan Media" button

## Backup and Restore

### Backup
```bash
./manage.sh backup
```
This creates a timestamped backup in `/mnt/user/appdata/watch1/backups/`

### Restore
```bash
./manage.sh restore
```
Follow the prompts to select and restore from a backup.

## SSL/HTTPS Setup (Optional)

### 1. Generate SSL Certificates
```bash
# Create SSL directory
mkdir -p /mnt/user/appdata/watch1/nginx/ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /mnt/user/appdata/watch1/nginx/ssl/key.pem \
    -out /mnt/user/appdata/watch1/nginx/ssl/cert.pem
```

### 2. Enable HTTPS in nginx.conf
Uncomment the HTTPS server block in `nginx/nginx.conf`

### 3. Restart Services
```bash
./manage.sh restart
```

## Performance Optimization

### 1. Resource Limits
Add resource limits to `docker-compose.yml`:
```yaml
services:
  watch1-backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 2. Media Caching
The nginx configuration includes caching for media files and thumbnails.

### 3. Database Optimization
For production use, consider using PostgreSQL instead of in-memory storage.

## Troubleshooting

### Check Service Status
```bash
./manage.sh status
```

### View Logs
```bash
# All services
./manage.sh logs

# Specific service
./manage.sh logs-backend
./manage.sh logs-frontend
./manage.sh logs-nginx
```

### Check Health
```bash
./manage.sh health
```

### Common Issues

#### Services Won't Start
1. Check Docker is running
2. Check port conflicts (8000, 3000, 80)
3. Check disk space
4. View logs for specific errors

#### Media Not Loading
1. Check file permissions
2. Verify media files are in correct directories
3. Run media scan
4. Check backend logs

#### Frontend Not Accessible
1. Check nginx logs
2. Verify frontend container is running
3. Check network connectivity

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down -v

# Remove all images
docker rmi $(docker images -q)

# Clean up
docker system prune -a -f

# Redeploy
./deploy.sh
```

## Updates

### Automatic Update
```bash
./manage.sh update
```

### Manual Update
1. Download latest code
2. Replace existing files
3. Run update script
4. Restart services

## Security Considerations

1. **Change Default Password**: Immediately change the admin password
2. **Firewall**: Configure Unraid firewall to restrict access
3. **SSL**: Use HTTPS in production
4. **Backup**: Regular backups of configuration and data
5. **Updates**: Keep the system updated

## Support

For issues and support:
1. Check the logs first
2. Verify all prerequisites are met
3. Check the troubleshooting section
4. Review the GitHub issues page

## Advanced Configuration

### Custom Media Directories
Edit `docker-compose.yml` to add custom media directories:
```yaml
volumes:
  - /mnt/user/your-movies:/app/media/movies:ro
  - /mnt/user/your-tv-shows:/app/media/tv-shows:ro
```

### Environment Variables
Add custom environment variables in `docker-compose.yml`:
```yaml
environment:
  - CUSTOM_VAR=value
  - DEBUG=true
```

### Custom Nginx Configuration
Modify `nginx/nginx.conf` for custom routing or SSL configuration.

