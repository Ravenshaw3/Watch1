# Watch1 v3.0.1 - Cross-Platform Development Commands
# Provides consistent commands across Windows, macOS, and Linux

.PHONY: help dev-start dev-stop dev-reset dev-health dev-logs dev-clean media-scan test build deploy

# Default target
help:
	@echo "Watch1 v3.0.1 - Development Environment Commands"
	@echo "=================================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  dev-start     Start development environment"
	@echo "  dev-stop      Stop development environment"
	@echo "  dev-reset     Reset development environment"
	@echo "  dev-health    Check system health"
	@echo "  dev-logs      Show service logs"
	@echo "  dev-clean     Clean up Docker resources"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests"
	@echo "  test-api      Run API tests"
	@echo "  test-e2e      Run end-to-end tests"
	@echo ""
	@echo "Build Commands:"
	@echo "  build         Build all services"
	@echo "  build-backend Build backend only"
	@echo "  build-frontend Build frontend only"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  deploy-dev    Deploy to development"
	@echo "  deploy-prod   Deploy to production"
	@echo ""

# Development Environment Commands
dev-start:
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File ".\scripts\dev-start.ps1"
else
	@./scripts/dev-start.sh
endif

dev-stop:
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File ".\scripts\dev-stop.ps1"
else
	@./scripts/dev-stop.sh
endif

dev-reset:
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File ".\scripts\dev-reset.ps1"
else
	@./scripts/dev-reset.sh
endif

dev-health:
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File ".\scripts\dev-health.ps1"
else
	@python3 tools/health-monitor.py
endif

media-scan:
ifeq ($(OS),Windows_NT)
	@echo "Triggering media scan & category refresh..."
	@python tools\\scan_media.py
	@echo "Media scan request submitted."
else
	@echo "Triggering media scan & category refresh..."
	@python3 tools/scan_media.py
	@echo "Media scan request submitted."
endif

dev-logs:
	@docker-compose -f docker-compose.dev.yml logs -f

dev-clean:
{{ ... }}

# Testing Commands
test:
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File ".\scripts\dev-test.ps1"
else
	@./scripts/dev-test.sh
endif

test-unit:
	@docker-compose -f docker-compose.dev.yml exec backend python -m pytest tests/unit/ -v

test-api:
	@python tools/api-tester.py

test-e2e:
	@docker-compose -f docker-compose.dev.yml exec frontend npm run test:e2e

# Build Commands
build:
	@docker-compose -f docker-compose.dev.yml build --no-cache

build-backend:
	@docker-compose -f docker-compose.dev.yml build --no-cache backend

build-frontend:
	@docker-compose -f docker-compose.dev.yml build --no-cache frontend

# Database Commands
db-migrate:
	@docker-compose -f docker-compose.dev.yml exec backend python -c "from flask_simple import app, db; app.app_context().push(); db.create_all(); print('Database migrated')"

db-seed:
	@docker-compose -f docker-compose.dev.yml exec backend python tools/seed-database.py

db-backup:
	@docker-compose -f docker-compose.dev.yml exec database pg_dump -U watch1_user watch1_dev > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Deployment Commands
deploy-dev:
	@echo "Deploying to development environment..."
	@docker-compose -f docker-compose.dev.yml up -d --build

deploy-prod:
	@echo "Deploying to production environment..."
	@docker-compose -f docker-compose.prod.yml up -d --build

# Utility Commands
install-deps:
ifeq ($(OS),Windows_NT)
	@echo "Installing Windows dependencies..."
	@where docker >nul 2>nul || (echo "Please install Docker Desktop" && exit 1)
	@where node >nul 2>nul || (echo "Please install Node.js" && exit 1)
	@where python >nul 2>nul || (echo "Please install Python 3.11+" && exit 1)
else
	@echo "Installing Unix dependencies..."
	@command -v docker >/dev/null 2>&1 || (echo "Please install Docker" && exit 1)
	@command -v node >/dev/null 2>&1 || (echo "Please install Node.js" && exit 1)
	@command -v python3 >/dev/null 2>&1 || (echo "Please install Python 3.11+" && exit 1)
endif

setup:
	@echo "Setting up Watch1 development environment..."
	@make install-deps
	@make build
	@make db-migrate
	@make dev-start
	@echo "Setup complete! Access the application at http://localhost:3000"

# Monitoring Commands
monitor:
	@python tools/health-monitor.py --continuous

status:
	@docker-compose -f docker-compose.dev.yml ps
	@echo ""
	@python tools/health-monitor.py

# Maintenance Commands
update:
	@git pull origin main
	@make build
	@make dev-reset

backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@make db-backup
	@tar -czf backups/watch1_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz backend/ frontend/ docker/ config/
	@echo "Backup created in backups/ directory"

# Development Shortcuts
quick-start: dev-clean dev-start
quick-reset: dev-stop dev-clean dev-start
full-reset: dev-stop dev-clean build dev-start
