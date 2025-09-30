# Watch1 v3.0.1 - Server Startup Scripts

## 🚀 Quick Start

### Option 1: Batch File (Recommended for Windows)
```bash
# Double-click or run from command prompt
start_servers.bat
```

### Option 2: PowerShell Script
```powershell
# Run from PowerShell
powershell -ExecutionPolicy Bypass -File start_servers.ps1
```

### Option 3: Python Script
```bash
# Run from command prompt
python start_production_servers.py
```

## 🧹 What These Scripts Do

### Automatic Cleanup:
- ✅ **Kill existing processes** on ports 8000 and 3000
- ✅ **Stop lingering Node.js processes** that might be old frontend instances
- ✅ **Clean up old FastAPI servers** (if any are running)
- ✅ **Wait for ports to be released** before starting new servers

### Server Startup:
- ✅ **Start Flask backend** (flask_simple.py) on port 8000
- ✅ **Start Vue.js frontend** (npm run dev) on port 3000
- ✅ **Test connectivity** to ensure both servers are responding
- ✅ **Provide status feedback** with colored output

## 📋 Server Details

### Backend (Flask v3.0.1)
- **File**: `backend/flask_simple.py`
- **Port**: 8000
- **URL**: http://localhost:8000
- **Features**: All advanced player features, subtitle support, authentication

### Frontend (Vue.js v3.0.1)
- **Directory**: `frontend/`
- **Port**: 3000
- **URL**: http://localhost:3000
- **Features**: Advanced video player with all new capabilities

## 🎬 Advanced Player Features Included

- ✅ **Subtitle Support** (.srt, .vtt, .ass, .ssa, .sub)
- ✅ **Enhanced Playback Speed** (0.25x to 2x)
- ✅ **Picture-in-Picture Mode** with browser compatibility
- ✅ **Multiple Audio Tracks** detection
- ✅ **Auto-Advance with Countdown** for playlists
- ✅ **Comprehensive Keyboard Shortcuts**

## 🔧 Troubleshooting

### If servers don't start:
1. **Check file paths**: Ensure you're running from the Watch1 root directory
2. **Check dependencies**: Run `npm install` in frontend directory if needed
3. **Check Python**: Ensure Python and required packages are installed
4. **Check ports**: Manually verify ports 3000 and 8000 are free

### Manual cleanup if needed:
```bash
# Kill processes on specific ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Kill all Node.js processes
taskkill /IM node.exe /F
```

### Manual server start:
```bash
# Backend
cd backend
python flask_simple.py

# Frontend (in new terminal)
cd frontend
npm run dev
```

## 📊 Expected Output

### Successful Startup:
```
============================================================
WATCH1 v3.0.1 - PRODUCTION SERVER STARTUP
============================================================

[09:22:35] [INFO] Cleaning up existing server processes...
[09:22:35] [SUCCESS] Port 8000 is free
[09:22:35] [SUCCESS] Port 3000 is free
[09:22:35] [INFO] Starting Flask backend server...
[09:22:38] [SUCCESS] Backend server started
[09:22:38] [INFO] Starting Vue.js frontend server...
[09:22:46] [SUCCESS] Frontend server started
[09:22:46] [INFO] Testing server connectivity...
[09:22:47] [SUCCESS] Backend test: OK (HTTP 200)
[09:22:48] [SUCCESS] Frontend test: OK (HTTP 200)

============================================================
[09:22:48] [SUCCESS] PRODUCTION SERVERS SUCCESSFULLY STARTED!
============================================================

Backend:  http://localhost:8000
Frontend: http://localhost:3000
============================================================
```

## 🎯 Benefits

- **No More Multiple Instances**: Automatically cleans up old processes
- **No More Version Confusion**: Only runs the correct v3.0.1 servers
- **No More Manual Cleanup**: Handles all process management automatically
- **Reliable Startup**: Tests connectivity before declaring success
- **Production Ready**: Uses the correct Flask backend with all features

## 🚀 Ready for Development

Once the servers are running, you can:
- Access the frontend at http://localhost:3000
- Test the API at http://localhost:8000/api/v1/version
- Use all advanced player features
- Develop with hot-reload on both frontend and backend
