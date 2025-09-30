#!/bin/bash

# Watch1 Media Server Update Script for Unraid
# This script updates the Watch1 Media Server to the latest version

set -e

echo "🔄 Updating Watch1 Media Server..."

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use 'sudo' or run in Unraid terminal)"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker in Unraid."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it in Unraid."
    exit 1
fi

# Pull latest images
print_status "Pulling latest images..."
docker-compose -f "$DOCKER_COMPOSE_FILE" pull

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f "$DOCKER_COMPOSE_FILE" down

# Remove old images
print_status "Cleaning up old images..."
docker image prune -f

# Build and start containers with latest code
print_status "Building and starting updated containers..."
docker-compose -f "$DOCKER_COMPOSE_FILE" up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend service is healthy"
else
    print_warning "Backend service may not be ready yet"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend service is healthy"
else
    print_warning "Frontend service may not be ready yet"
fi

# Check nginx
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_success "Nginx reverse proxy is healthy"
else
    print_warning "Nginx reverse proxy may not be ready yet"
fi

print_success "🎉 Watch1 Media Server updated successfully!"

# Show container status
print_status "Container Status:"
docker-compose -f "$DOCKER_COMPOSE_FILE" ps

