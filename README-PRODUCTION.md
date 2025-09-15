# Watch1 Media Server - Production Deployment

## 🚀 Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- Ports 3000 and 8000 available

### 1. Clone the Repository
```bash
git clone https://github.com/Ravenshaw3/Watch1.git
cd Watch1
```

### 2. Create Media Directories
```bash
mkdir -p media thumbnails
```

### 3. Start the Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

### 5. Default Login
- **Username**: `admin`
- **Password**: `admin123`

## 🐳 Docker Hub Images

The application is available as pre-built Docker images:

- **Backend**: `ravenshaw3/watch1-backend:latest`
- **Frontend**: `ravenshaw3/watch1-frontend:latest`

## 📁 Directory Structure

```
Watch1/
├── backend/                 # FastAPI backend
├── frontend/               # Vue.js frontend
├── media/                  # Media files storage
├── thumbnails/             # Thumbnail cache
├── docker-compose.prod.yml # Production deployment
└── README-PRODUCTION.md    # This file
```

## 🔧 Configuration

### Environment Variables

**Frontend**:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000/api/v1)

**Backend**:
- `PYTHONPATH`: Python path (default: /app)

### Volume Mounts

- `./media:/app/media` - Media files storage
- `./thumbnails:/app/thumbnails` - Thumbnail cache
- `postgres_data:/var/lib/postgresql/data` - Database persistence

## 🎬 Features

### ✅ Working Features
- **User Authentication**: Login/logout with JWT tokens
- **Media Management**: Upload, browse, and manage media files
- **File Types**: Support for video, audio, and image files
- **Media Browser**: Beautiful grid layout with file information
- **File Serving**: Direct access to media files
- **Responsive Design**: Works on desktop and mobile

### 📱 Supported File Types
- **Video**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- **Audio**: MP3, WAV, FLAC, AAC, OGG
- **Images**: JPEG, PNG, GIF, WebP

## 🔒 Security

- JWT-based authentication
- File type validation
- User-based file access control
- CORS protection

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Media Management
- `GET /api/v1/media/` - List media files (paginated)
- `GET /api/v1/media/{id}` - Get specific media file
- `POST /api/v1/media/upload` - Upload media file
- `DELETE /api/v1/media/{id}` - Delete media file

### File Serving
- `GET /media/{filename}` - Serve media files
- `GET /thumbnails/{filename}` - Serve thumbnails

## 🛠️ Development

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python media_main.py

# Frontend
cd frontend
npm install
npm run dev
```

### Building Images
```bash
# Backend
docker build -t ravenshaw3/watch1-backend:latest ./backend

# Frontend
docker build -t ravenshaw3/watch1-frontend:latest ./frontend
```

## 📝 Logs

View logs for troubleshooting:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

## 🔄 Updates

To update to the latest version:
```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Permission issues**: Check directory permissions for media folders
3. **File upload fails**: Verify file type is supported and size limits

### Health Checks
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/Ravenshaw3/Watch1/issues
- Docker Hub: https://hub.docker.com/r/ravenshaw3/watch1-backend
