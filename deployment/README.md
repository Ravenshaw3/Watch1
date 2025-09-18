# Watch1 Media Server - Unraid Deployment

This folder contains all the files needed to deploy Watch1 Media Server to your Unraid server.

## Files Included

- `watch1-backend.tar` - Pre-built backend Docker image
- `watch1-frontend.tar` - Pre-built frontend Docker image  
- `docker-compose.unraid.yml` - Docker Compose configuration for Unraid
- `nginx.conf` - Nginx reverse proxy configuration
- `deploy-images.sh` - Deployment script

## Deployment Instructions

1. **Transfer files to Unraid server:**
   - Copy this entire `deployment` folder to your Unraid server
   - Place it in `/mnt/user/appdata/watch1/`

2. **SSH into your Unraid server:**
   ```bash
   ssh root@192.168.254.14
   ```

3. **Navigate to the deployment directory:**
   ```bash
   cd /mnt/user/appdata/watch1/deployment
   ```

4. **Make the deployment script executable:**
   ```bash
   chmod +x deploy-images.sh
   ```

5. **Run the deployment script:**
   ```bash
   ./deploy-images.sh
   ```

## What the deployment script does:

1. Loads the pre-built Docker images
2. Creates necessary directories (`/mnt/user/appdata/watch1/thumbnails`, `/mnt/user/appdata/watch1/data`)
3. Sets proper permissions
4. Starts the Watch1 Media Server using Docker Compose
5. Shows access URLs and management commands

## Access Information

After deployment, you can access:

- **Frontend:** http://192.168.254.14/
- **Backend API:** http://192.168.254.14/api/v1/
- **Default Login:** admin / admin123

## Media Directory

The server will scan media from: `/mnt/user/media`

Make sure your media files are in this directory before running the initial scan.

## Management Commands

```bash
# Stop the server
docker-compose -f /mnt/user/appdata/watch1/docker-compose.unraid.yml down

# Start the server
docker-compose -f /mnt/user/appdata/watch1/docker-compose.unraid.yml up -d

# View logs
docker-compose -f /mnt/user/appdata/watch1/docker-compose.unraid.yml logs -f

# Check status
docker-compose -f /mnt/user/appdata/watch1/docker-compose.unraid.yml ps
```

## Troubleshooting

If you encounter issues:

1. Check Docker is running: `docker info`
2. Check container logs: `docker-compose logs -f`
3. Verify media directory exists: `ls -la /mnt/user/media`
4. Check permissions: `ls -la /mnt/user/appdata/watch1/`
