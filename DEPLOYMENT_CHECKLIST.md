# Watch1 Structured Backend - Production Deployment Checklist

## Pre-Deployment Checklist

### ✅ System Requirements
- [ ] **Docker**: Version 20.10+ installed
- [ ] **Docker Compose**: Version 2.0+ installed
- [ ] **Storage**: Minimum 10GB available for application data
- [ ] **Memory**: Minimum 2GB RAM available
- [ ] **Network**: Ports 80, 443, 3000, 8000 available
- [ ] **Media Storage**: Accessible media directory with proper permissions

### ✅ Configuration Preparation
- [ ] **JWT Secret**: Generated secure JWT secret key (32+ characters)
- [ ] **CORS Origins**: Updated with your domain/IP addresses
- [ ] **Media Paths**: Verified media directory paths are correct
- [ ] **SSL Certificates**: Prepared SSL certificates if using HTTPS
- [ ] **Backup Strategy**: Planned database backup procedure

### ✅ Environment Setup
- [ ] **Application Directories**: Created `/mnt/user/appdata/watch1/` directories
- [ ] **Permissions**: Set proper file permissions (755 for directories)
- [ ] **Media Access**: Verified media files are accessible
- [ ] **Network Configuration**: Configured firewall rules if needed

## Deployment Steps

### Step 1: Repository Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/Watch1.git
cd Watch1

# Verify structured backend files exist
ls -la backend/main.py
ls -la backend/app/api/v1/endpoints/
```
- [ ] Repository cloned successfully
- [ ] Structured backend files present

### Step 2: Configuration
```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Update these critical settings:
# - JWT_SECRET_KEY: your-secure-random-string
# - CORS_ORIGINS: https://yourdomain.com
# - Volume paths: /mnt/user/media:/app/media
```
- [ ] JWT secret key updated (minimum 32 characters)
- [ ] CORS origins configured with your domain
- [ ] Volume paths configured for your system
- [ ] Flask environment set to 'production'
- [ ] Flask debug set to 'false'

### Step 3: Deploy Services
```bash
# Start services
docker-compose up -d

# Check service status
docker-compose ps

# Verify all services are healthy
docker-compose logs --tail=20
```
- [ ] All containers started successfully
- [ ] Backend container is healthy
- [ ] Frontend container is healthy
- [ ] No error messages in logs

### Step 4: Database Initialization
```bash
# Initialize database with admin user
docker-compose exec watch1-backend python tools/seed-database.py

# Verify database creation
docker-compose exec watch1-backend ls -la /app/data/
```
- [ ] Database initialized successfully
- [ ] Admin user created (test@example.com / testpass123)
- [ ] Database file exists in data directory

### Step 5: Validation Testing
```bash
# Run comprehensive validation
python tools/validate-production-deployment.py

# Test frontend-backend integration
python tools/test-frontend-backend-integration.py

# Test structured backend endpoints
python tools/test-structured-backend.py
```
- [ ] Production validation passed (95%+ success rate)
- [ ] Frontend-backend integration working (100% success)
- [ ] All critical endpoints responding correctly

## Post-Deployment Verification

### ✅ Service Health Checks
```bash
# Test backend health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "3.0.4"}

# Test frontend accessibility
curl http://localhost:3000
# Expected: HTTP 200 response

# Test API endpoints
curl http://localhost:8000/api/v1/system/version
# Expected: JSON with version information
```
- [ ] Backend health check returns 200
- [ ] Frontend returns 200
- [ ] API endpoints responding correctly

### ✅ Authentication Testing
```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"testpass123"}'
# Expected: JWT token response
```
- [ ] Login endpoint working
- [ ] JWT token generated successfully
- [ ] User profile accessible with token

### ✅ Web Interface Testing
- [ ] **Frontend Access**: Navigate to http://localhost:3000
- [ ] **Login Page**: Login form displays correctly
- [ ] **Authentication**: Can log in with test credentials
- [ ] **Media Library**: Media page loads without errors
- [ ] **Navigation**: All tabs (Library, Playlists, Analytics, Settings) work
- [ ] **API Communication**: No CORS errors in browser console

### ✅ Media Functionality
- [ ] **Media Detection**: Media files are detected and listed
- [ ] **Categories**: Media categories display correctly
- [ ] **Streaming**: Video/audio playback works
- [ ] **Thumbnails**: Thumbnail generation working (if configured)
- [ ] **Search**: Media search functionality working

## Security Verification

### ✅ Production Security
- [ ] **JWT Secret**: Strong, unique secret key configured
- [ ] **Debug Mode**: Flask debug disabled (FLASK_DEBUG=false)
- [ ] **CORS Origins**: Specific domains configured (no wildcards)
- [ ] **HTTPS**: SSL/TLS configured if using domain
- [ ] **File Permissions**: Proper directory permissions set
- [ ] **Network Security**: Firewall rules configured if needed

### ✅ Access Control
- [ ] **Admin Account**: Default credentials changed from test account
- [ ] **User Management**: Additional users created if needed
- [ ] **Superuser Access**: Admin functions restricted to superusers
- [ ] **Media Access**: Media files accessible but secure

## Monitoring Setup

### ✅ Health Monitoring
```bash
# Set up health check monitoring
# Add to crontab or monitoring system:
*/5 * * * * curl -f http://localhost:8000/health || echo "Backend down"
*/5 * * * * curl -f http://localhost:3000 || echo "Frontend down"
```
- [ ] Health check monitoring configured
- [ ] Log rotation configured
- [ ] Disk space monitoring set up
- [ ] Backup schedule established

### ✅ Log Management
```bash
# View logs
docker-compose logs -f watch1-backend
docker-compose logs -f watch1-frontend

# Configure log rotation in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```
- [ ] Log rotation configured
- [ ] Log monitoring set up
- [ ] Error alerting configured (optional)

## Backup and Maintenance

### ✅ Backup Procedures
```bash
# Database backup
docker-compose exec watch1-backend cp /app/data/watch1.db /app/data/backup_$(date +%Y%m%d).db

# Configuration backup
cp docker-compose.yml docker-compose.yml.backup
```
- [ ] Database backup procedure tested
- [ ] Configuration files backed up
- [ ] Backup schedule established
- [ ] Restore procedure documented

### ✅ Update Procedures
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f
```
- [ ] Update procedure documented
- [ ] Rollback plan established
- [ ] Testing procedure for updates

## Troubleshooting Reference

### Common Issues and Solutions

#### Backend Not Starting
```bash
# Check logs
docker-compose logs watch1-backend

# Common fixes:
# - Verify environment variables
# - Check database permissions
# - Ensure ports are available
```

#### Frontend Can't Connect
```bash
# Check network connectivity
docker-compose exec watch1-frontend curl http://watch1-backend:8000/health

# Common fixes:
# - Verify CORS configuration
# - Check API URL in frontend environment
# - Ensure backend is healthy
```

#### Authentication Issues
```bash
# Verify JWT configuration
docker-compose exec watch1-backend env | grep JWT_SECRET_KEY

# Reinitialize database if needed
docker-compose exec watch1-backend python tools/seed-database.py
```

#### Database Problems
```bash
# Check database file
docker-compose exec watch1-backend ls -la /app/data/

# Recreate database if corrupted
docker-compose exec watch1-backend rm /app/data/watch1.db
docker-compose exec watch1-backend python tools/seed-database.py
```

## Final Deployment Confirmation

### ✅ Deployment Complete Checklist
- [ ] All services running and healthy
- [ ] Authentication working correctly
- [ ] Media library accessible and functional
- [ ] Frontend-backend communication working
- [ ] Security configurations applied
- [ ] Monitoring and logging configured
- [ ] Backup procedures established
- [ ] Documentation reviewed and accessible

### ✅ Success Criteria Met
- [ ] **Endpoint Success Rate**: 95%+ (19/20 endpoints working)
- [ ] **Frontend Compatibility**: 100% (all integration tests pass)
- [ ] **Production Configuration**: All security settings applied
- [ ] **Performance**: Acceptable response times under normal load
- [ ] **Reliability**: Services restart automatically on failure

## 🎉 Deployment Complete!

Once all items in this checklist are completed, your Watch1 Media Server with structured backend is ready for production use!

### Support Resources
- **Architecture Documentation**: `docs/STRUCTURED_BACKEND.md`
- **Production Guide**: `docs/PRODUCTION_DEPLOYMENT.md`
- **Migration Summary**: `MIGRATION_COMPLETE.md`
- **Testing Tools**: `tools/` directory
- **Troubleshooting**: Check logs and run validation scripts

### Next Steps
1. **Monitor**: Keep an eye on logs and health checks
2. **Backup**: Establish regular backup routine
3. **Update**: Plan for future updates and maintenance
4. **Scale**: Consider additional features or performance optimizations

**Congratulations on successfully deploying Watch1 with structured backend architecture!** 🚀
