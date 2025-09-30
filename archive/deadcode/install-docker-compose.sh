#!/bin/bash

# Docker Compose Installation Script for Unraid
# This script installs Docker Compose on your Unraid server

set -e

echo "🐳 Installing Docker Compose on Unraid..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first in Unraid."
    exit 1
fi

# Check if Docker Compose is already installed
if command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose is already installed:"
    docker-compose --version
    print_status "Skipping installation."
    exit 0
fi

# Get the latest version
print_status "Getting latest Docker Compose version..."
LATEST_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
print_status "Latest version: $LATEST_VERSION"

# Download Docker Compose
print_status "Downloading Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/${LATEST_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
print_status "Setting permissions..."
chmod +x /usr/local/bin/docker-compose

# Create symlink for docker-compose command
if [ ! -L /usr/bin/docker-compose ]; then
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Verify installation
print_status "Verifying installation..."
if docker-compose --version; then
    print_success "Docker Compose installed successfully!"
else
    print_error "Docker Compose installation failed!"
    exit 1
fi

# Test Docker Compose
print_status "Testing Docker Compose..."
if docker-compose --help > /dev/null 2>&1; then
    print_success "Docker Compose is working correctly!"
else
    print_error "Docker Compose test failed!"
    exit 1
fi

print_success "🎉 Docker Compose installation complete!"
echo ""
echo "You can now run:"
echo "  docker-compose --version"
echo "  ./deploy.sh"
echo ""

