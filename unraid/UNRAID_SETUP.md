# Watch1 Unraid Development Setup

Complete guide to set up Watch1 development environment directly on Unraid server with native Docker performance and direct media access.

## 🎯 Benefits of Unraid Development

- **Direct Media Access**: No Docker Desktop mount issues - direct access to 18,509+ media files
- **Native Performance**: Docker runs natively on Unraid, not virtualized
- **Production Environment**: Develop on actual deployment target
- **Real Data**: Test with actual media library, not sample files
- **Better Resource Usage**: No Windows virtualization overhead

## 🚀 Quick Setup

### Step 1: Copy Setup Script to Unraid
```bash
# Copy the setup script to your Unraid server
scp unraid/setup-ssh-dev.sh root@YOUR_UNRAID_IP:/tmp/
```

### Step 2: Run Setup on Unraid
```bash
# SSH into Unraid as root
ssh root@YOUR_UNRAID_IP

# Run the setup script
chmod +x /tmp/setup-ssh-dev.sh
/tmp/setup-ssh-dev.sh
```

### Step 3: Configure VS Code Remote-SSH
```bash
# Add to your ~/.ssh/config
Host watch1-unraid
    HostName YOUR_UNRAID_IP
    User watch1dev
    IdentityFile ~/.ssh/watch1_unraid_key
    LocalForward 3000 localhost:3000
    LocalForward 8000 localhost:8000
```

### Step 4: Start Development
```bash
# SSH into development environment
ssh watch1-unraid

# Start Watch1 development stack
./start-watch1-dev.sh
```

## 📋 What Gets Installed

### Development User
- **User**: `watch1dev`
- **Home**: `/mnt/user/appdata/watch1-dev`
- **SSH**: Configured with key-based authentication

### Directory Structure
```
/mnt/user/appdata/watch1-dev/
├── Watch1/                    # Git repository
├── .ssh/                      # SSH keys
├── start-watch1-dev.sh        # Development startup script
└── logs/                      # Development logs

/mnt/user/appdata/watch1/
├── postgres_data/             # PostgreSQL data
├── redis_data/                # Redis data
├── thumbnails/                # Generated thumbnails
└── logs/                      # Application logs
```

### Services
- **PostgreSQL**: Native database with persistent storage
- **Redis**: Caching and session storage
- **Frontend**: Vue.js development server
- **Backend**: FastAPI with direct media access
- **Nginx**: Reverse proxy (production)

## 🔧 Development Workflow

### Daily Development
```bash
# Connect to Unraid development environment
ssh watch1-unraid

# Navigate to project
cd /mnt/user/appdata/watch1-dev/Watch1

# Pull latest changes
git pull origin main

# Start development stack
./start-watch1-dev.sh

# View logs
docker-compose -f docker-compose.unraid.yml logs -f
```

### VS Code Integration
1. Install "Remote - SSH" extension
2. Connect to `watch1-unraid`
3. Open folder: `/mnt/user/appdata/watch1-dev/Watch1`
4. Develop with full IntelliSense and debugging

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it watch1-db psql -U watch1_user -d watch1_dev

# Run media scanner
python unraid/unraid-media-scanner.py

# View media files
SELECT category, COUNT(*) FROM media_files GROUP BY category;
```

## 📊 Media Scanner

The Unraid media scanner provides direct access to your media library:

```bash
# Run full media scan
python unraid/unraid-media-scanner.py

# Expected output:
# 📁 Scanning: /mnt/user/media
# 📁 Scanning: /mnt/user/Movies
# 📁 Scanning: /mnt/user/TV Shows
# ✅ Successfully scanned 18,509 media files
```

### Supported Media Types
- **Video**: mp4, mkv, avi, mov, wmv, flv, webm, m4v
- **Audio**: mp3, flac, wav, aac, ogg, m4a, wma
- **Images**: jpg, jpeg, png, gif, bmp, webp, tiff

### Auto-Categorization
- **Movies**: `/mnt/user/Movies`, files with "movie", "film", "cinema"
- **TV Shows**: `/mnt/user/TV Shows`, files with "tv", "series", "episode"
- **Kids**: `/mnt/user/Kids`, files with "kid", "child", "family", "disney"
- **Music**: `/mnt/user/Music`, audio files and "music", "album"
- **Documentaries**: Files with "documentary", "doc"

## 🌐 Access Points

After setup, access Watch1 at:
- **Frontend**: http://YOUR_UNRAID_IP:3000
- **API**: http://YOUR_UNRAID_IP:8000
- **API Docs**: http://YOUR_UNRAID_IP:8000/docs

## 🔒 Security

### SSH Security
- Key-based authentication only
- Dedicated development user (not root)
- Restricted to development directories

### Network Security
- Services bound to Unraid network
- Firewall rules can be applied
- Optional VPN access

## 🛠️ Troubleshooting

### Common Issues

**Permission Errors**
```bash
# Fix ownership
sudo chown -R watch1dev:watch1dev /mnt/user/appdata/watch1-dev
sudo chown -R watch1dev:watch1dev /mnt/user/appdata/watch1
```

**Database Connection**
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.unraid.yml ps
docker-compose -f docker-compose.unraid.yml logs watch1-db
```

**Media Access**
```bash
# Verify media directories
ls -la /mnt/user/media
ls -la /mnt/user/Movies
```

### Performance Optimization

**Docker Resources**
```yaml
# In docker-compose.unraid.yml
services:
  watch1-backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

**Database Tuning**
```sql
-- PostgreSQL optimization for media server
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

## 📈 Monitoring

### System Monitoring
```bash
# Container status
docker-compose -f docker-compose.unraid.yml ps

# Resource usage
docker stats

# Logs
docker-compose -f docker-compose.unraid.yml logs -f --tail=100
```

### Application Monitoring
- **Health Checks**: Built into docker-compose
- **API Monitoring**: `/api/v1/health` endpoint
- **Database Monitoring**: PostgreSQL logs and metrics

## 🚀 Production Deployment

When ready for production:

1. **Update Environment**: Change to production settings
2. **SSL Certificates**: Configure HTTPS with Let's Encrypt
3. **Backup Strategy**: Automated database and config backups
4. **Monitoring**: Full application and infrastructure monitoring
5. **Updates**: Automated container updates via Watchtower

## 📞 Support

For issues with Unraid development setup:
1. Check logs: `docker-compose -f docker-compose.unraid.yml logs`
2. Verify permissions: `/mnt/user/appdata/watch1*`
3. Test database: `docker exec -it watch1-db psql -U watch1_user -d watch1_dev`
4. Check media access: `ls -la /mnt/user/media`

---

**Ready to develop Watch1 with native Unraid performance and direct access to your entire media library!** 🎬🎵📺
