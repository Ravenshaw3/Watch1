# 🚀 Quick Setup Guide for Unraid

## Your Situation:
- ✅ Unraid server with Docker
- ❌ Docker Compose not installed
- ✅ Media files in `/mnt/user/media/`

## 🛠️ **Step-by-Step Setup**

### **Step 1: Install Docker Compose**

**Option A: Using the provided script**
```bash
# Upload the install-docker-compose.sh script to your Unraid server
# Then run:
chmod +x install-docker-compose.sh
./install-docker-compose.sh
```

**Option B: Manual installation**
```bash
# SSH into your Unraid server
ssh root@your-unraid-ip

# Download and install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify installation
docker-compose --version
```

### **Step 2: Upload Watch1 Files**

Upload the entire Watch1 project to your Unraid server:
```bash
# Recommended location
/mnt/user/appdata/watch1/
```

### **Step 3: Deploy Watch1**

```bash
# Navigate to the Watch1 directory
cd /mnt/user/appdata/watch1

# Make scripts executable
chmod +x deploy.sh update.sh manage.sh

# Deploy the application
./deploy.sh
```

## 📁 **Directory Structure After Deployment**

```
/mnt/user/
├── media/                          # Your existing media files
│   ├── movies/
│   ├── tv-shows/
│   ├── kids/
│   └── music-videos/
└── appdata/
    └── watch1/
        ├── backend/                # Backend application
        ├── frontend/               # Frontend application
        ├── nginx/                  # Nginx configuration
        ├── docker-compose.yml      # Docker Compose configuration
        ├── deploy.sh              # Deployment script
        ├── update.sh              # Update script
        ├── manage.sh              # Management script
        ├── thumbnails/            # Generated thumbnails
        └── data/                  # Application data
```

## 🌐 **Access Your Media Server**

Once deployed, access your Watch1 Media Server at:
- **Main Application**: http://your-unraid-ip/
- **Backend API**: http://your-unraid-ip/api/v1/

**Default Login:**
- Username: `admin`
- Password: `admin123`

## 🎬 **Add Your Media Files**

Your media files are already in `/mnt/user/media/`. The system will automatically:
1. **Scan** the media directory
2. **Generate** artwork and thumbnails
3. **Categorize** your media (movies, TV shows, kids, etc.)
4. **Make them available** in the web interface

## 🛠️ **Management Commands**

```bash
# Check status
./manage.sh status

# View logs
./manage.sh logs

# Scan media directory
./manage.sh scan

# Restart services
./manage.sh restart

# Update system
./manage.sh update

# Backup data
./manage.sh backup
```

## 🔧 **Troubleshooting**

### **Docker Compose Issues**
```bash
# Check if Docker Compose is installed
docker-compose --version

# If not found, reinstall
./install-docker-compose.sh
```

### **Port Conflicts**
If ports 80, 3000, or 8000 are in use:
1. Stop conflicting services
2. Or modify `docker-compose.yml` to use different ports

### **Permission Issues**
```bash
# Fix permissions
chmod -R 755 /mnt/user/appdata/watch1
chmod -R 755 /mnt/user/media
```

### **Check Logs**
```bash
# View all logs
./manage.sh logs

# View specific service logs
./manage.sh logs-backend
./manage.sh logs-frontend
./manage.sh logs-nginx
```

## ✅ **Verification**

After deployment, verify everything is working:

1. **Check services are running:**
   ```bash
   ./manage.sh status
   ```

2. **Check health:**
   ```bash
   ./manage.sh health
   ```

3. **Access the web interface:**
   - Open http://your-unraid-ip/
   - Login with admin/admin123
   - Go to Library and click "Scan Media"

## 🎉 **You're Ready!**

Your Watch1 Media Server should now be running on your Unraid server with access to all your existing media files in `/mnt/user/media/`!

**Next Steps:**
1. Change the default admin password
2. Scan your media directory
3. Create playlists
4. Enjoy your personal media server!

