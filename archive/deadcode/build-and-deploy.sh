#!/bin/bash

# Build and Deploy Script for Watch1 Media Server
# This script builds Docker images locally and deploys them to Unraid

set -e

echo "🚀 Building Watch1 Media Server images locally..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
UNRAID_IP="192.168.254.14"
UNRAID_PATH="/mnt/user/appdata/watch1"
LOCAL_BUILD_DIR="./build"

# Create build directory
mkdir -p "$LOCAL_BUILD_DIR"

print_status "Building backend image..."
docker build -t watch1-backend:latest ./backend

print_status "Building frontend image..."
docker build -t watch1-frontend:latest ./frontend

print_status "Saving images to tar files..."
docker save watch1-backend:latest -o "$LOCAL_BUILD_DIR/watch1-backend.tar"
docker save watch1-frontend:latest -o "$LOCAL_BUILD_DIR/watch1-frontend.tar"

print_status "Copying images to Unraid server..."
scp -i ~/.ssh/unraid_key "$LOCAL_BUILD_DIR/watch1-backend.tar" root@$UNRAID_IP:/tmp/
scp -i ~/.ssh/unraid_key "$LOCAL_BUILD_DIR/watch1-frontend.tar" root@$UNRAID_IP:/tmp/

print_status "Loading images on Unraid server..."
ssh -i ~/.ssh/unraid_key root@$UNRAID_IP "docker load -i /tmp/watch1-backend.tar"
ssh -i ~/.ssh/unraid_key root@$UNRAID_IP "docker load -i /tmp/watch1-frontend.tar"

print_status "Cleaning up temporary files..."
ssh -i ~/.ssh/unraid_key root@$UNRAID_IP "rm /tmp/watch1-backend.tar /tmp/watch1-frontend.tar"

print_status "Starting services on Unraid..."
ssh -i ~/.ssh/unraid_key root@$UNRAID_IP "cd $UNRAID_PATH && docker-compose up -d"

print_success "🎉 Deployment complete!"
echo ""
echo "📱 Access URLs:"
echo "   Frontend: http://$UNRAID_IP/"
echo "   Backend API: http://$UNRAID_IP/api/v1/"
echo ""
echo "🔐 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Clean up local build files
rm -rf "$LOCAL_BUILD_DIR"
print_success "Local build files cleaned up"

