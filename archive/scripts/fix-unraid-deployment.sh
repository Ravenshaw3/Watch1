#!/bin/bash
# Fix Unraid Deployment Script
# Run this on your Unraid server to fix the build issues

echo "🔧 Fixing Unraid deployment..."

cd /mnt/user/appdata/watch1

# Create the corrected docker-compose.yml with build contexts
cat > docker-compose.yml << 'EOF'
services:
  watch1-backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    image: watch1-backend:latest
    container_name: watch1-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - /mnt/user/media:/app/media
      - /mnt/user/media:/app/T:ro
      - /mnt/user/appdata/watch1/thumbnails:/app/thumbnails
      - /mnt/user/appdata/watch1/data:/app/data
      - /mnt/user/appdata/watch1/logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - FLASK_ENV=production
      - MEDIA_ROOT=/app/media
      - THUMBNAILS_ROOT=/app/thumbnails
      - DATA_ROOT=/app/data
      - JWT_SECRET_KEY=prod-jwt-secret-key-change-this
      - CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://watch1-frontend:3000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - watch1-network

  watch1-frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    image: watch1-frontend:latest
    container_name: watch1-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
      - NODE_ENV=production
    depends_on:
      - watch1-backend
    networks:
      - watch1-network

networks:
  watch1-network:
    driver: bridge
EOF

echo "✅ Fixed docker-compose.yml with build contexts"

# Create directories
mkdir -p data logs thumbnails
chmod 755 data logs thumbnails

echo "✅ Created required directories"

# Clean up any failed containers
docker-compose down --remove-orphans 2>/dev/null || true

echo "🚀 Starting deployment..."

# Build and deploy
docker-compose up -d --build

echo "📊 Checking status..."
sleep 5
docker-compose ps

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Access your media server at: http://192.168.254.14:3000"
echo "🔑 Login with: test@example.com / testpass123"
echo ""
echo "📋 To check logs: docker-compose logs -f"
