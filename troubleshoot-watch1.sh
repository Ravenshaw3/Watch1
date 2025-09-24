#!/bin/bash

# Watch1 Media Server Troubleshooting Script
# Run this on your Unraid server to automatically diagnose and fix issues

set -e

WATCH1_DIR="/mnt/user/appdata/watch1"
DEPLOYMENT_DIR="$WATCH1_DIR/deployment"

print_status() {
    echo -e "\n\e[1;34m--- $1 ---\e[0m"
}

print_success() {
    echo -e "\e[1;32m✅ $1\e[0m"
}

print_error() {
    echo -e "\e[1;31m❌ $1\e[0m"
}

print_warning() {
    echo -e "\e[1;33m⚠️  $1\e[0m"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use 'sudo' or run in Unraid terminal)"
    exit 1
fi

print_status "Watch1 Media Server Troubleshooting Script"
echo "This script will diagnose and attempt to fix common issues."

# Step 1: Check current status
print_status "Step 1: Checking current container status"
cd "$WATCH1_DIR"
docker-compose -f docker-compose.unraid.yml ps

# Step 2: Check container logs
print_status "Step 2: Checking container logs"
echo "--- Nginx Logs ---"
docker logs watch1-nginx --tail 20 2>/dev/null || print_warning "Nginx container not found"

echo -e "\n--- Backend Logs ---"
docker logs watch1-backend --tail 20 2>/dev/null || print_warning "Backend container not found"

echo -e "\n--- Frontend Logs ---"
docker logs watch1-frontend --tail 20 2>/dev/null || print_warning "Frontend container not found"

# Step 3: Check if images are loaded
print_status "Step 3: Checking Docker images"
docker images | grep watch1 || print_warning "Watch1 images not found"

# Step 4: Complete reset
print_status "Step 4: Performing complete container reset"
docker-compose -f docker-compose.unraid.yml down
docker-compose -f docker-compose.unraid.yml rm -f
docker network rm watch1-network 2>/dev/null || true

# Step 5: Reload images if needed
print_status "Step 5: Ensuring images are loaded"
if [ -f "$DEPLOYMENT_DIR/watch1-backend.tar" ]; then
    docker load -i "$DEPLOYMENT_DIR/watch1-backend.tar"
    print_success "Backend image loaded"
else
    print_warning "Backend image file not found"
fi

if [ -f "$DEPLOYMENT_DIR/watch1-frontend.tar" ]; then
    docker load -i "$DEPLOYMENT_DIR/watch1-frontend.tar"
    print_success "Frontend image loaded"
else
    print_warning "Frontend image file not found"
fi

# Step 6: Start containers one by one
print_status "Step 6: Starting containers one by one"

echo "Starting backend..."
docker-compose -f docker-compose.unraid.yml up -d watch1-backend
sleep 30

echo "Checking backend status..."
if docker ps | grep -q watch1-backend; then
    print_success "Backend container is running"
    docker logs watch1-backend --tail 10
else
    print_error "Backend container failed to start"
    docker logs watch1-backend --tail 20
fi

echo -e "\nStarting frontend..."
docker-compose -f docker-compose.unraid.yml up -d watch1-frontend
sleep 30

echo "Checking frontend status..."
if docker ps | grep -q watch1-frontend; then
    print_success "Frontend container is running"
    docker logs watch1-frontend --tail 10
else
    print_error "Frontend container failed to start"
    docker logs watch1-frontend --tail 20
fi

echo -e "\nStarting nginx..."
docker-compose -f docker-compose.unraid.yml up -d watch1-nginx
sleep 10

echo "Checking nginx status..."
if docker ps | grep -q watch1-nginx; then
    print_success "Nginx container is running"
    docker logs watch1-nginx --tail 10
else
    print_error "Nginx container failed to start"
    docker logs watch1-nginx --tail 20
fi

# Step 7: Test connectivity
print_status "Step 7: Testing container connectivity"

echo "Testing backend connectivity..."
if docker exec watch1-nginx wget -qO- http://watch1-backend:8000/api/v1/version 2>/dev/null; then
    print_success "Backend is accessible from nginx"
else
    print_error "Backend is not accessible from nginx"
fi

echo "Testing frontend connectivity..."
if docker exec watch1-nginx wget -qO- http://watch1-frontend:3000 2>/dev/null; then
    print_success "Frontend is accessible from nginx"
else
    print_error "Frontend is not accessible from nginx"
fi

# Step 8: Final status
print_status "Step 8: Final container status"
docker-compose -f docker-compose.unraid.yml ps

# Step 9: Test external access
print_status "Step 9: Testing external access"
echo "Testing port 8083..."
if netstat -tulpn | grep -q :8083; then
    print_success "Port 8083 is listening"
else
    print_error "Port 8083 is not listening"
fi

# Summary
print_status "Troubleshooting Complete"
echo "Check the output above for any errors."
echo "If containers are running, try accessing: http://192.168.254.14:8083/"
echo ""
echo "If issues persist, check:"
echo "1. Docker logs: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml logs -f"
echo "2. Container status: docker-compose -f $WATCH1_DIR/docker-compose.unraid.yml ps"
echo "3. Network connectivity: docker network ls"

