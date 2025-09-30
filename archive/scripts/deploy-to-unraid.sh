#!/bin/bash

# Enhanced deployment script for Unraid server
# This script builds locally and deploys to Unraid for testing

set -e

# Configuration
UNRAID_IP="192.168.254.14"
UNRAID_PATH="/mnt/user/appdata/watch1"
SSH_KEY="~/.ssh/unraid_key"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_error "SSH key not found at $SSH_KEY"
    exit 1
fi

print_status "Starting Watch1 deployment to Unraid server..."

# Step 1: Build Docker images locally
print_status "Building Docker images locally..."
docker-compose -f docker-compose.prod.yml build --no-cache

if [ $? -eq 0 ]; then
    print_success "Local build completed successfully"
else
    print_error "Local build failed"
    exit 1
fi

# Step 2: Save Docker images as tar files
print_status "Saving Docker images..."
docker save watch1-backend:latest -o watch1-backend.tar
docker save watch1-frontend:latest -o watch1-frontend.tar

print_success "Docker images saved"

# Step 3: Copy files to Unraid server
print_status "Copying files to Unraid server..."

# Copy Docker images
scp -i $SSH_KEY watch1-backend.tar root@$UNRAID_IP:$UNRAID_PATH/
scp -i $SSH_KEY watch1-frontend.tar root@$UNRAID_IP:$UNRAID_PATH/

# Copy updated source code
scp -i $SSH_KEY -r backend/ root@$UNRAID_IP:$UNRAID_PATH/
scp -i $SSH_KEY -r frontend/ root@$UNRAID_IP:$UNRAID_PATH/

# Copy docker-compose file
scp -i $SSH_KEY unraid-docker-compose.yml root@$UNRAID_IP:$UNRAID_PATH/docker-compose.yml

print_success "Files copied to Unraid server"

# Step 4: Deploy on Unraid server
print_status "Deploying on Unraid server..."

ssh -i $SSH_KEY root@$UNRAID_IP << EOF
cd $UNRAID_PATH

# Load Docker images
docker load -i watch1-backend.tar
docker load -i watch1-frontend.tar

# Stop existing services
docker-compose down

# Start services with new images
docker-compose up -d --build

# Wait for services to start
sleep 10

# Check status
docker-compose ps
EOF

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully"
else
    print_error "Deployment failed"
    exit 1
fi

# Step 5: Test deployment
print_status "Testing deployment..."

# Test backend health
BACKEND_HEALTH=$(ssh -i $SSH_KEY root@$UNRAID_IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health")
if [ "$BACKEND_HEALTH" = "200" ]; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed (HTTP $BACKEND_HEALTH)"
fi

# Test frontend
FRONTEND_HEALTH=$(ssh -i $SSH_KEY root@$UNRAID_IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000")
if [ "$FRONTEND_HEALTH" = "200" ]; then
    print_success "Frontend health check passed"
else
    print_warning "Frontend health check failed (HTTP $FRONTEND_HEALTH)"
fi

# Clean up local tar files
rm -f watch1-backend.tar watch1-frontend.tar

print_success "🎉 Deployment complete!"
echo ""
echo "📱 Access URLs:"
echo "   Frontend: http://$UNRAID_IP:3000"
echo "   Backend API: http://$UNRAID_IP:8000"
echo "   Nginx (if configured): http://$UNRAID_IP:8083"
echo ""
echo "🔐 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Show final status
print_status "Final service status:"
ssh -i $SSH_KEY root@$UNRAID_IP "cd $UNRAID_PATH && docker-compose ps"