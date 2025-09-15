#!/bin/bash

# Watch1 Media Server - Unraid Setup Script
# This script sets up Watch1 on your Unraid server

echo "🚀 Setting up Watch1 Media Server on Unraid..."

# Create directories
echo "📁 Creating directories..."
mkdir -p /mnt/user/appdata/watch1/{postgres,redis,data}
mkdir -p /mnt/user/media

# Set permissions
echo "🔐 Setting permissions..."
chown -R nobody:users /mnt/user/appdata/watch1
chown -R nobody:users /mnt/user/media
chmod -R 755 /mnt/user/appdata/watch1
chmod -R 755 /mnt/user/media

# Clone the repository
echo "📥 Cloning Watch1 repository..."
cd /mnt/user/appdata/watch1
if [ -d "Watch1" ]; then
    echo "Repository already exists, updating..."
    cd Watch1
    git pull origin main
else
    git clone https://github.com/Ravenshaw3/Watch1.git
    cd Watch1
fi

# Copy Unraid-specific docker-compose file
echo "📋 Setting up Docker Compose..."
cp unraid-docker-compose.yml docker-compose.yml

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose down
docker-compose build
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo "✅ Watch1 Media Server setup complete!"
echo "🌐 Access your media server at: http://192.168.254.14:3000"
echo "📚 API documentation at: http://192.168.254.14:8000/docs"
echo "❤️  Health check at: http://192.168.254.14:8000/health"
