#!/bin/bash

# Deploy pre-built Docker images to Unraid server
# This script assumes the tar files are already on the Unraid server

set -e

WATCH1_DIR="/mnt/user/appdata/watch1"
MEDIA_SOURCE_DIR="/mnt/user/media"

print_status() {
    echo -e "\n\e[1;34m--- $1 ---\e[0m"
}

print_success() {
    echo -e "\e[1;32m✅ $1\e[0m"
}

print_error() {
    echo -e "\e[1;31m❌ $1\e[0m"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use 'sudo' or run in Unraid terminal)"
    exit 1
fi

print_status "Loading Docker images..."

# Load the backend image
if [ -f "$WATCH1_DIR/watch1-backend.tar" ]; then
    docker load -i "$WATCH1_DIR/watch1-backend.tar"
    print_success "Backend image loaded"
else
    print_error "Backend image file not found: $WATCH1_DIR/watch1-backend.tar"
    exit 1
fi

# Load the frontend image
if [ -f "$WATCH1_DIR/watch1-frontend.tar" ]; then
    docker load -i "$WATCH1_DIR/watch1-frontend.tar"
    print_success "Frontend image loaded"
else
    print_error "Frontend image file not found: $WATCH1_DIR/watch1-frontend.tar"
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p "$WATCH1_DIR/thumbnails"
mkdir -p "$WATCH1_DIR/data"
mkdir -p "$WATCH1_DIR/ssl"

# Set proper permissions
chmod 755 "$WATCH1_DIR"
chmod 755 "$WATCH1_DIR/thumbnails"
chmod 755 "$WATCH1_DIR/data"

# Check if media directory exists
if [ ! -d "$MEDIA_SOURCE_DIR" ]; then
    print_error "Media directory $MEDIA_SOURCE_DIR not found. Please create it first."
    exit 1
fi

print_success "Directories ready"

# Start the services
print_status "Starting Watch1 Media Server..."
cd "$WATCH1_DIR"

if docker-compose -f docker-compose.unraid.yml up -d; then
    print_success "Watch1 Media Server deployed successfully!"
else
    print_error "Failed to deploy Watch1 Media Server. Check logs for details."
    exit 1
fi

# Show status
print_status "Deployment Information"
echo " Watch1 Media Server is running!"
echo ""
echo "📱 Access URLs:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}')/"
echo "   Backend API: http://$(hostname -I | awk '{print $1}')/api/v1/"
echo ""
echo "🔐 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📁 Media Directory: $MEDIA_SOURCE_DIR"
echo "🖼️  Thumbnails Directory: $WATCH1_DIR/thumbnails"
echo "💾 Data Directory: $WATCH1_DIR/data"
echo ""
echo "🛠️  Management Commands:"
echo "   Stop: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml down"
echo "   Start: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml up -d"
echo "   Restart: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml restart"
echo "   Logs: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml logs -f"
echo "   Status: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml ps"
echo ""
print_success "Deployment complete!"
