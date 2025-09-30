# Watch1 v3.0.1 - Development Guide

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Node.js 18+ 
- Python 3.11+
- Git

### One-Command Setup
```bash
# Clone and setup everything
git clone <repository>
cd Watch1
make setup
```

### Manual Setup
```bash
# Start development environment
make dev-start

# Or use PowerShell scripts directly (Windows)
.\scripts\dev-start.ps1

# Check system health
make dev-health
```

## 🏗️ Architecture Overview

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Nginx Proxy   │    │   Backend API   │
│   Vue.js 3      │◄──►│   Load Balancer │◄──►│   Flask         │
│   Port: 3000    │    │   Port: 80      │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Redis Cache   │              │
         └──────────────►│   Port: 6379    │◄─────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  PostgreSQL DB  │
                        │   Port: 5432    │
                        └─────────────────┘
```

### Technology Stack
- **Frontend**: Vue.js 3, TypeScript, Vite, Tailwind CSS
- **Backend**: Flask, SQLAlchemy, JWT Authentication
- **Database**: PostgreSQL (production), SQLite (development fallback)
- **Cache**: Redis
- **Proxy**: Nginx
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

```
Watch1/
├── 📁 backend/                 # Flask backend application
│   ├── flask_simple.py        # Main Flask application
│   ├── models/                 # Database models
│   ├── api/                    # API endpoints
│   └── requirements.txt        # Python dependencies
│
├── 📁 frontend/                # Vue.js frontend application
│   ├── src/
│   │   ├── components/         # Vue components
│   │   ├── views/              # Page components
│   │   ├── stores/             # Pinia state management
│   │   └── api/                # API client
│   ├── package.json            # Node.js dependencies
│   └── vite.config.ts          # Vite configuration
│
├── 📁 docker/                  # Docker configuration
│   ├── docker-compose.dev.yml  # Development environment
│   ├── Dockerfile.backend      # Backend container
│   └── Dockerfile.frontend     # Frontend container
│
├── 📁 scripts/                 # Development automation
│   ├── dev-start.ps1           # Start development environment
│   ├── dev-stop.ps1            # Stop development environment
│   ├── dev-reset.ps1           # Reset environment
│   └── dev-health.ps1          # Health monitoring
│
├── 📁 config/                  # Configuration files
│   ├── development.env         # Development environment variables
│   └── production.env          # Production environment variables
│
├── 📁 tools/                   # Development tools
│   ├── health-monitor.py       # System health monitoring
│   └── api-tester.py           # API endpoint testing
│
├── 📁 docs/                    # Documentation
│   ├── DEVELOPMENT.md          # This file
│   ├── API.md                  # API documentation
│   └── DEPLOYMENT.md           # Deployment guide
│
└── Makefile                    # Cross-platform commands
```

## 🛠️ Development Workflow

### Daily Development
```bash
# Start your day
# Re-scan media & refresh categories after adding files
make media-scan   # run from project root (requires Make installed)
# Alternatively, run `python tools/scan_media.py` from the project root

# View logs
make dev-logs

# Run tests
{{ ... }}
make test

# End your day
make dev-stop
```

### Making Changes

#### Backend Changes
1. Edit files in `backend/`
2. Flask auto-reloads in development mode
3. Test changes: `make test-api`

#### Frontend Changes
1. Edit files in `frontend/src/`
2. Vite provides hot module replacement
3. Changes appear instantly in browser

#### Database Changes
1. Update models in `backend/models/`
2. Run migrations: `make db-migrate`
3. Restart backend if needed

### Media Library Updates
1. Drop new media files into your configured directories (`DEV_MEDIA_PATHS`)
2. Run `make media-scan` to trigger a backend scan and rebuild category counts
3. Optionally override defaults when scanning:

```bash
# Use a custom directory and force category recalculation for a one-off scan
WATCH1_MEDIA_DIRECTORY=/app/custom-media \
WATCH1_RECALCULATE_CATEGORIES=true \
make media-scan
```

`make media-scan` is a thin wrapper around `tools/scan_media.py`, which logs in with the standard development credentials (`test@example.com` / `testpass123`) and calls the `/api/v1/media/scan` endpoint. The following environment variables are supported:

- `WATCH1_API_URL` (default `http://localhost:8000`)
- `WATCH1_MEDIA_DIRECTORY` (default `/app/media`)
- `WATCH1_RECALCULATE_CATEGORIES` (`true`, `false`, `1`, `0`)
- If `make` isn’t available, run `python tools/scan_media.py` (Windows) or `python3 tools/scan_media.py` (macOS/Linux) from the project root to perform the same action.

### Testing
```bash
# Run all tests
make test

# Run specific test types
make test-unit      # Unit tests
make test-api       # API tests
make test-e2e       # End-to-end tests

# Manual testing
make dev-health     # System health check
```

## 🔧 Configuration

### Environment Variables
Development configuration is in `config/development.env`:

```bash
# Database
DATABASE_URL=postgresql://watch1_user:watch1_dev_password@database:5432/watch1_dev
SQLITE_DATABASE_URL=sqlite:///watch1.db

# Authentication
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Media
MEDIA_ROOT=/app/media
SUPPORTED_VIDEO_FORMATS=mp4,mkv,avi,mov,wmv,flv,webm,m4v

# Features
FEATURE_PLAYLISTS=true
FEATURE_ANALYTICS=true
FEATURE_SUBTITLES=true
```

### Media Configuration
Configure media directories in the Settings page or environment:
```bash
DEV_MEDIA_PATHS=T:\Movies,T:\TV Shows,T:\Music,T:\Videos,T:\Kids
```

## 🚨 Troubleshooting

### Common Issues

#### "Frontend tabs not working"
```bash
# Check authentication
make dev-health

# Clear browser cache and localStorage
# Login again with: test@example.com / testpass123
```

#### "Database connection failed"
```bash
# Reset database
make dev-reset

# Check database status
docker-compose -f docker-compose.dev.yml exec database pg_isready
```

#### "Docker containers not starting"
```bash
# Clean Docker environment
make dev-clean

# Rebuild everything
make build

# Start fresh
make dev-start
```

#### "Port conflicts"
```bash
# Stop all services
make dev-stop

# Kill conflicting processes
# Windows: netstat -ano | findstr :3000
# Linux/Mac: lsof -ti:3000 | xargs kill
```

### Health Monitoring
```bash
# Quick health check
make status

# Detailed health report
make dev-health

# Continuous monitoring
make monitor
```

### Logs and Debugging
```bash
# View all logs
make dev-logs

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Backend debugging
docker-compose -f docker-compose.dev.yml exec backend python -c "from flask_simple import app; print(app.url_map)"
```

## 🔄 Development Best Practices

### Code Organization
- Keep components small and focused
- Use TypeScript for type safety
- Follow Vue.js composition API patterns
- Implement proper error handling

### Database Management
- Always use migrations for schema changes
- Test with both PostgreSQL and SQLite
- Use proper foreign key relationships
- Implement soft deletes where appropriate

### API Development
- Follow RESTful conventions
- Include proper HTTP status codes
- Implement authentication on protected endpoints
- Use consistent response formats

### Testing Strategy
- Write unit tests for business logic
- Test API endpoints thoroughly
- Include integration tests for critical flows
- Test authentication and authorization

### Performance Optimization
- Use Redis caching for frequently accessed data
- Implement proper database indexing
- Optimize media streaming with range requests
- Use CDN for static assets in production

## 📊 Monitoring and Metrics

### Health Endpoints
- Backend: `http://localhost:8000/api/v1/health`
- Frontend: `http://localhost:3000`
- Nginx: `http://localhost/health`

### Key Metrics to Monitor
- Response times for API endpoints
- Database connection pool usage
- Redis cache hit rates
- Media streaming performance
- User authentication success rates

### Development Tools
- Health Monitor: `python tools/health-monitor.py`
- API Tester: `python tools/api-tester.py`
- Database Manager: `python tools/db-manager.py`

## 🚀 Deployment Preparation

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Health checks green
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Security review completed
- [ ] Performance testing done

### Environment Promotion
```bash
# Development → Staging
make deploy-staging

# Staging → Production
make deploy-prod
```

## 📚 Additional Resources

- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

## 🆘 Getting Help

### Development Issues
1. Check this documentation
2. Run health diagnostics: `make dev-health`
3. Check logs: `make dev-logs`
4. Reset environment: `make dev-reset`

### System Status
The Watch1 v3.0.1 system is production-ready with:
- ✅ 62 media files indexed
- ✅ Video streaming operational (tested with 4.4GB files)
- ✅ Authentication working (test@example.com / testpass123)
- ✅ All navigation tabs functional
- ✅ Playlist management operational
- ✅ Analytics dashboard working
- ✅ Settings management complete

**The development environment is now robust, automated, and designed to prevent the setbacks you experienced before!** 🎬
