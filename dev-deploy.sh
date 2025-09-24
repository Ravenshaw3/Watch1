#!/bin/bash

# Quick development deployment script
# Use this for rapid testing during development

set -e

UNRAID_IP="192.168.254.14"
UNRAID_PATH="/mnt/user/appdata/watch1"
SSH_KEY="~/.ssh/unraid_key"

echo "🚀 Quick deploy to Unraid for testing..."

# Build and save images
echo "Building images..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker save watch1-backend:latest -o watch1-backend.tar
docker save watch1-frontend:latest -o watch1-frontend.tar

# Deploy to Unraid
echo "Deploying to Unraid..."
scp -i $SSH_KEY watch1-backend.tar watch1-frontend.tar root@$UNRAID_IP:$UNRAID_PATH/
scp -i $SSH_KEY -r backend/ frontend/ root@$UNRAID_IP:$UNRAID_PATH/
scp -i $SSH_KEY unraid-docker-compose.yml root@$UNRAID_IP:$UNRAID_PATH/docker-compose.yml

# Restart services on Unraid
ssh -i $SSH_KEY root@$UNRAID_IP << 'EOF'
cd /mnt/user/appdata/watch1
docker load -i watch1-backend.tar
docker load -i watch1-frontend.tar
docker-compose down
docker-compose up -d --build
EOF

# Cleanup
rm -f watch1-backend.tar watch1-frontend.tar

echo "✅ Deployed! Access at http://192.168.254.14:3000"
