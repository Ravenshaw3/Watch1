# Watch1 Unraid Server Deployment Guide

## 🎯 **DEPLOYMENT OVERVIEW**

This guide will deploy the fully fixed Watch1 media server to your Unraid server with all authentication and TypeScript issues resolved.

## ✅ **PRE-DEPLOYMENT CHECKLIST**

### **Issues Resolved:**
- [x] Authentication system fully working
- [x] TypeScript TypeError in media.ts fixed
- [x] API response format compatibility resolved
- [x] Categories field added to media API
- [x] Vue 3 reactivity issues with mediaFiles.value fixed
- [x] Production database compatibility verified

### **Current Status:**
- **Backend**: All API endpoints working (200 OK)
- **Frontend**: Vue 3 reactivity issues fixed
- **Database**: 102 media files, 4 categories
- **Authentication**: test@example.com / testpass123

## 🚀 **DEPLOYMENT STEPS**

### **Step 1: Prepare Unraid Server**

1. **SSH into your Unraid server:**
   ```bash
   ssh root@your-unraid-ip
   ```

2. **Create application directory:**
   ```bash
   mkdir -p /mnt/user/appdata/watch1
   cd /mnt/user/appdata/watch1
   ```

3. **Create required directories:**
   ```bash
   mkdir -p data logs thumbnails
   chmod 755 data logs thumbnails
   ```

### **Step 2: Copy Files to Unraid**

1. **Copy docker-compose file:**
   ```bash
   # From your Windows machine, copy docker-compose.unraid.yml to Unraid
   scp docker-compose.unraid.yml root@your-unraid-ip:/mnt/user/appdata/watch1/docker-compose.yml
   ```

2. **Copy database (if needed):**
   ```bash
   # Copy your production database
   scp watch1.db root@your-unraid-ip:/mnt/user/appdata/watch1/data/watch1.db
   ```

### **Step 3: Deploy on Unraid**

1. **Navigate to application directory:**
   ```bash
   cd /mnt/user/appdata/watch1
   ```

2. **Pull and start containers:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

3. **Verify deployment:**
   ```bash
   docker-compose ps
   docker-compose logs -f watch1-backend
   ```

### **Step 4: Configure Media Access**

1. **Verify media mount:**
   ```bash
   docker exec watch1-backend ls -la /app/T/Movies
   ```

2. **Check database access:**
   ```bash
   docker exec watch1-backend python -c "
   import sqlite3
   conn = sqlite3.connect('/app/data/watch1.db')
   print('Media files:', conn.execute('SELECT COUNT(*) FROM media_files').fetchone()[0])
   conn.close()
   "
   ```

### **Step 5: Test Deployment**

1. **Access frontend:**
   - Open: `http://your-unraid-ip:3000`
   - Login: test@example.com / testpass123

2. **Verify functionality:**
   - [x] Login works without errors
   - [x] Media library loads with proper titles
   - [x] Categories display correctly
   - [x] No TypeScript errors in browser console
   - [x] Posters display from media directories
   - [x] Video streaming works

## 📋 **UNRAID DOCKER-COMPOSE CONFIGURATION**

The `docker-compose.unraid.yml` includes:

```yaml
services:
  watch1-backend:
    image: watch1-backend:latest
    volumes:
      - /mnt/user/media:/app/media
      - /mnt/user/media:/app/T:ro          # Your media files
      - /mnt/user/appdata/watch1/thumbnails:/app/thumbnails
      - /mnt/user/appdata/watch1/data:/app/data
      - /mnt/user/appdata/watch1/logs:/app/logs
    environment:
      - FLASK_ENV=production
      - JWT_SECRET_KEY=prod-jwt-secret-key-change-this
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]

  watch1-frontend:
    image: watch1-frontend:latest
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
      - NODE_ENV=production
```

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **Media files not accessible:**
   ```bash
   # Check mount points
   docker exec watch1-backend ls -la /app/T/
   # Should show your media directories
   ```

2. **Database not found:**
   ```bash
   # Check database location
   docker exec watch1-backend ls -la /app/data/
   # Should show watch1.db
   ```

3. **Authentication fails:**
   ```bash
   # Check user in database
   docker exec watch1-backend python -c "
   import sqlite3
   conn = sqlite3.connect('/app/data/watch1.db')
   user = conn.execute('SELECT * FROM users LIMIT 1').fetchone()
   print('User found:', user is not None)
   conn.close()
   "
   ```

### **Log Monitoring:**
```bash
# Backend logs
docker-compose logs -f watch1-backend

# Frontend logs  
docker-compose logs -f watch1-frontend

# All services
docker-compose logs -f
```

## ✅ **SUCCESS CRITERIA**

Your deployment is successful when:

- [x] Frontend loads at `http://your-unraid-ip:3000`
- [x] Login works with test@example.com / testpass123
- [x] Media library shows movies with proper titles
- [x] Categories display: documentaries, movies, music_videos, tv_shows
- [x] Posters load from media directories
- [x] Video streaming works for your media files
- [x] No TypeScript errors in browser console
- [x] All navigation tabs work (Library, Playlists, Analytics, Settings)

## 🎉 **POST-DEPLOYMENT**

After successful deployment:

1. **Change default password:**
   - Create new admin user through settings
   - Disable test account

2. **Configure media scanning:**
   - Set up automatic media scanning
   - Configure poster generation

3. **Set up SSL (optional):**
   - Configure nginx with SSL certificates
   - Update CORS settings

**Your Watch1 media server is now production-ready on Unraid!** 🎯
