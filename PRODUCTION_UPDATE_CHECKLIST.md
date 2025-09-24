# Watch1 Production Update Checklist

## 🎯 CHANGES MADE DURING DEVELOPMENT SESSION

### ✅ AUTHENTICATION FIXES
- **Fixed login error 500 "no item with that key"**
- Updated `flask_simple.py` to use correct database column names
- Fixed bcrypt password verification for production database
- Updated user profile endpoint to use correct columns

### ✅ DATABASE CONFIGURATION
- **Implemented global database configuration system**
- Created `database_config.py` for centralized database path management
- Updated `flask_simple.py` to use global database config
- Updated `media_scanner.py` to use global database config
- Created `database_manager.py` utility for database operations

### ✅ POSTER AND STREAMING FIXES
- **Fixed Windows path conversion issues**
- Updated streaming endpoint to convert `T:\` to `/app/T/` paths
- Updated poster endpoint to handle Windows backslashes
- Fixed MediaCardNew.vue image error handling

### ✅ MEDIA VOLUME MOUNTS
- **Updated docker-compose.unraid.yml**
- Added `/mnt/user/media:/app/T:ro` mount for Unraid media access
- Added logs volume mount
- Updated environment variables for production

## 📋 FILES TO COPY TO PRODUCTION

### Backend Files (Critical)
1. `backend/flask_simple.py` - Main Flask application with all fixes
2. `backend/database_config.py` - Global database configuration
3. `database_manager.py` - Database management utility
4. `media_scanner.py` - Updated media scanner

### Frontend Files
1. `frontend/src/components/MediaCardNew.vue` - Fixed image error handling

### Configuration Files
1. `docker-compose.unraid.yml` - Updated with new volume mounts and environment

## 🚀 PRODUCTION DEPLOYMENT STEPS

### Step 1: Stop Development Environment
```bash
docker-compose -f docker-compose.dev.yml down
```

### Step 2: Build Production Images
```bash
# Build backend image
docker build -t watch1-backend:latest -f docker/Dockerfile.backend .

# Build frontend image  
docker build -t watch1-frontend:latest -f docker/Dockerfile.frontend .
```

### Step 3: Deploy to Production
```bash
# Deploy with Unraid configuration
docker-compose -f docker-compose.unraid.yml up -d
```

### Step 4: Verify Database
```bash
# Check database is accessible
docker exec watch1-backend python database_manager.py info

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"testpass123"}'
```

### Step 5: Test Media Access
```bash
# Check if media files are accessible
docker exec watch1-backend ls -la /app/T/Movies/

# Test poster endpoint
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/media/<media-id>/poster

# Test streaming endpoint  
curl -I -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/media/<media-id>/stream
```

## 🎯 EXPECTED RESULTS

### ✅ What Should Work
- **Authentication**: Login with test@example.com / testpass123
- **Media Library**: Shows all 62 media files from database
- **Poster Display**: Shows poster.jpg files from movie directories
- **Video Streaming**: Plays movies directly from Unraid server
- **Database Access**: Uses production database with all data

### 🔧 Key Improvements
- **No more login errors**
- **Proper Unraid media path handling**
- **Fixed poster image loading**
- **Working video streaming**
- **Centralized database configuration**

## ⚠️ IMPORTANT NOTES

1. **Database Location**: Production will use `/app/data/watch1.db` or existing database
2. **Media Paths**: All `T:\Movies\...` paths will map to `/app/T/Movies/...`
3. **Authentication**: Uses bcrypt hashing (production standard)
4. **Environment**: Set to production mode with proper JWT secrets

## 🎉 SUCCESS CRITERIA

- ✅ Login works without errors
- ✅ Library shows all movies with posters
- ✅ Video playback works for all media files
- ✅ No 404 or 500 errors in browser console
- ✅ Database operations work correctly
