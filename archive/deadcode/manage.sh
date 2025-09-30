#!/bin/bash

# Watch1 Media Server Management Script for Unraid
# This script provides easy management commands for the Watch1 Media Server

set -e

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"
WATCH1_DIR="/mnt/user/appdata/watch1"

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

# Function to show usage
show_usage() {
    echo "Watch1 Media Server Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show service logs"
    echo "  logs-backend Show backend logs only"
    echo "  logs-frontend Show frontend logs only"
    echo "  logs-nginx  Show nginx logs only"
    echo "  update      Update to latest version"
    echo "  backup      Backup data and configuration"
    echo "  restore     Restore from backup"
    echo "  clean       Clean up unused Docker resources"
    echo "  scan        Scan media directory"
    echo "  health      Check service health"
    echo "  help        Show this help message"
    echo ""
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (use 'sudo' or run in Unraid terminal)"
        exit 1
    fi
}

# Function to check Docker
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker in Unraid."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install it in Unraid."
        exit 1
    fi
}

# Start services
start_services() {
    print_status "Starting Watch1 Media Server services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    print_success "Services started successfully"
}

# Stop services
stop_services() {
    print_status "Stopping Watch1 Media Server services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    print_success "Services stopped successfully"
}

# Restart services
restart_services() {
    print_status "Restarting Watch1 Media Server services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" restart
    print_success "Services restarted successfully"
}

# Show status
show_status() {
    print_status "Watch1 Media Server Status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
    print_status "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Show logs
show_logs() {
    print_status "Showing Watch1 Media Server logs (Press Ctrl+C to exit):"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
}

# Show backend logs
show_backend_logs() {
    print_status "Showing backend logs (Press Ctrl+C to exit):"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f watch1-backend
}

# Show frontend logs
show_frontend_logs() {
    print_status "Showing frontend logs (Press Ctrl+C to exit):"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f watch1-frontend
}

# Show nginx logs
show_nginx_logs() {
    print_status "Showing nginx logs (Press Ctrl+C to exit):"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f watch1-nginx
}

# Update services
update_services() {
    print_status "Updating Watch1 Media Server..."
    ./update.sh
}

# Backup data
backup_data() {
    print_status "Creating backup..."
    BACKUP_DIR="/mnt/user/appdata/watch1/backups"
    BACKUP_FILE="watch1-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
        -C "$WATCH1_DIR" \
        --exclude="backups" \
        --exclude="*.log" \
        .
    
    print_success "Backup created: $BACKUP_DIR/$BACKUP_FILE"
}

# Restore data
restore_data() {
    print_warning "This will restore data from a backup. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Available backups:"
        ls -la /mnt/user/appdata/watch1/backups/*.tar.gz 2>/dev/null || print_warning "No backups found"
        echo ""
        print_status "Enter backup filename:"
        read -r backup_file
        
        if [ -f "/mnt/user/appdata/watch1/backups/$backup_file" ]; then
            print_status "Restoring from backup: $backup_file"
            tar -xzf "/mnt/user/appdata/watch1/backups/$backup_file" -C "$WATCH1_DIR"
            print_success "Backup restored successfully"
        else
            print_error "Backup file not found: $backup_file"
        fi
    else
        print_status "Restore cancelled"
    fi
}

# Clean up Docker resources
clean_docker() {
    print_status "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    print_success "Docker cleanup completed"
}

# Scan media directory
scan_media() {
    print_status "Scanning media directory..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec watch1-backend python -c "
import requests
import json
try:
    response = requests.post('http://localhost:8000/api/v1/media/scan', 
                           json={'directory': '/app/media'},
                           headers={'Authorization': 'Bearer YOUR_TOKEN_HERE'})
    print('Scan completed:', response.json())
except Exception as e:
    print('Scan failed:', str(e))
"
}

# Check health
check_health() {
    print_status "Checking service health..."
    
    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend: Healthy"
    else
        print_error "Backend: Unhealthy"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend: Healthy"
    else
        print_error "Frontend: Unhealthy"
    fi
    
    # Check nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_success "Nginx: Healthy"
    else
        print_error "Nginx: Unhealthy"
    fi
}

# Main script logic
case "${1:-help}" in
    start)
        check_root
        check_docker
        start_services
        ;;
    stop)
        check_root
        check_docker
        stop_services
        ;;
    restart)
        check_root
        check_docker
        restart_services
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    logs-backend)
        check_docker
        show_backend_logs
        ;;
    logs-frontend)
        check_docker
        show_frontend_logs
        ;;
    logs-nginx)
        check_docker
        show_nginx_logs
        ;;
    update)
        check_root
        check_docker
        update_services
        ;;
    backup)
        check_root
        backup_data
        ;;
    restore)
        check_root
        restore_data
        ;;
    clean)
        check_root
        check_docker
        clean_docker
        ;;
    scan)
        check_docker
        scan_media
        ;;
    health)
        check_health
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac

