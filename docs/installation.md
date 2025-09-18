# Installation Guide

This guide will help you install and set up Watch1 Media Server on your system.

## Prerequisites

Before installing Watch1, make sure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)

### System Requirements

- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: At least 10GB free space for the application, plus space for your media files
- **CPU**: Multi-core processor recommended for media transcoding
- **Network**: Stable internet connection for initial setup

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest way to get Watch1 running:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Watch1
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit configuration**
   ```bash
   nano .env
   ```
   
   Update the following variables:
   - `SECRET_KEY`: Generate a secure secret key
   - `DATABASE_URL`: Database connection string
   - `REDIS_URL`: Redis connection string
   - `MEDIA_ROOT`: Path to your media files directory

4. **Start the services**
   ```bash
   docker-compose up -d
   ```

5. **Verify installation**
   ```bash
   docker-compose ps
   ```

### Method 2: Manual Installation

If you prefer to install components manually:

#### Backend Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb watch1
   
   # Run migrations
   alembic upgrade head
   ```

5. **Start the backend**
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://watch1:password@localhost:5432/watch1

# Redis
REDIS_URL=redis://localhost:6379

# Media Storage
MEDIA_ROOT=/path/to/your/media/files
THUMBNAILS_ROOT=/path/to/thumbnails
TRANSCODED_ROOT=/path/to/transcoded/files

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1

# FFmpeg
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe
```

### Media Directory Setup

1. **Create media directories**
   ```bash
   mkdir -p /path/to/media/{videos,audio,images}
   mkdir -p /path/to/thumbnails
   mkdir -p /path/to/transcoded
   ```

2. **Set permissions**
   ```bash
   chmod 755 /path/to/media
   chmod 755 /path/to/thumbnails
   chmod 755 /path/to/transcoded
   ```

## First Run

1. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

2. **Create admin user**
   ```bash
   # Using the API
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
          "username": "admin",
          "email": "admin@example.com",
          "password": "securepassword",
          "full_name": "Administrator"
        }'
   ```

3. **Upload your first media file**
   - Go to http://localhost:3000/upload
   - Select a media file to upload
   - Wait for processing to complete

## Troubleshooting

### Common Issues

**Docker containers not starting**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

**Database connection errors**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

**Media files not processing**
- Check FFmpeg installation
- Verify media file permissions
- Check processing logs

**Frontend not loading**
- Verify Node.js version (18+)
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Logs

View application logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Performance Tuning

For better performance with large media libraries:

1. **Increase Docker resources**
   - Allocate more RAM to Docker
   - Increase CPU cores

2. **Database optimization**
   - Add database indexes
   - Configure connection pooling

3. **Media processing**
   - Use SSD storage for media files
   - Configure transcoding quality settings

## Security Considerations

1. **Change default passwords**
2. **Use HTTPS in production**
3. **Configure firewall rules**
4. **Regular security updates**
5. **Backup your data**

## Next Steps

After successful installation:

1. Read the [Configuration Guide](configuration.md)
2. Explore the [API Documentation](api.md)
3. Check out [Frontend Development](frontend.md)
4. Learn about [Deployment](deployment.md)

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Search existing [GitHub issues](https://github.com/your-repo/issues)
3. Create a new issue with detailed information
4. Join our community discussions
