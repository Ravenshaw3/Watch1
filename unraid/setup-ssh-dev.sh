#!/bin/bash
# Watch1 Unraid SSH Development Setup
# Run this script on your Unraid server to setup development environment

set -e

echo "🚀 Setting up Watch1 Development Environment on Unraid"
echo "=================================================="

# Variables
DEV_USER="watch1dev"
DEV_HOME="/mnt/user/appdata/watch1-dev"
REPO_DIR="$DEV_HOME/Watch1"
SSH_KEY_FILE="$DEV_HOME/.ssh/authorized_keys"

# Create development user
echo "📝 Creating development user: $DEV_USER"
if ! id "$DEV_USER" &>/dev/null; then
    useradd -m -d "$DEV_HOME" -s /bin/bash "$DEV_USER"
    echo "✅ User $DEV_USER created"
else
    echo "✅ User $DEV_USER already exists"
fi

# Setup SSH directory
echo "🔑 Setting up SSH access"
mkdir -p "$DEV_HOME/.ssh"
chmod 700 "$DEV_HOME/.ssh"

# Generate SSH key if not exists
if [ ! -f "$DEV_HOME/.ssh/id_rsa" ]; then
    ssh-keygen -t rsa -b 4096 -f "$DEV_HOME/.ssh/id_rsa" -N "" -C "watch1-dev@unraid"
    echo "✅ SSH key generated"
fi

# Setup authorized_keys for remote access
touch "$SSH_KEY_FILE"
chmod 600 "$SSH_KEY_FILE"

# Create development directories
echo "📁 Creating development directories"
mkdir -p "$DEV_HOME/projects"
mkdir -p "$DEV_HOME/logs"
mkdir -p "/mnt/user/appdata/watch1"
mkdir -p "/mnt/user/appdata/watch1/postgres_data"
mkdir -p "/mnt/user/appdata/watch1/redis_data"
mkdir -p "/mnt/user/appdata/watch1/thumbnails"
mkdir -p "/mnt/user/appdata/watch1/logs"

# Set proper ownership
chown -R "$DEV_USER:$DEV_USER" "$DEV_HOME"
chown -R "$DEV_USER:$DEV_USER" "/mnt/user/appdata/watch1"

# Install development tools
echo "🛠️ Installing development tools"
# Update package manager (varies by Unraid version)
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y git curl wget nano vim htop
elif command -v yum &> /dev/null; then
    yum update -y
    yum install -y git curl wget nano vim htop
elif command -v pacman &> /dev/null; then
    pacman -Syu --noconfirm git curl wget nano vim htop
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Setup git configuration
echo "📋 Setting up git configuration"
su - "$DEV_USER" -c "
git config --global user.name 'Watch1 Developer'
git config --global user.email 'dev@watch1.local'
git config --global init.defaultBranch main
"

# Clone repository if it doesn't exist
if [ ! -d "$REPO_DIR" ]; then
    echo "📦 Cloning Watch1 repository"
    su - "$DEV_USER" -c "cd $DEV_HOME && git clone https://github.com/your-username/Watch1.git"
else
    echo "✅ Repository already exists"
fi

# Create development environment file
echo "⚙️ Creating Unraid environment configuration"
cat > "$REPO_DIR/.env.unraid.dev" << 'EOF'
# Unraid Development Environment
ENV_TYPE=unraid
ENVIRONMENT=development

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://watch1_user:watch1_dev_password@watch1-db:5432/watch1_dev
DB_HOST=watch1-db
DB_PORT=5432
DB_NAME=watch1_dev
DB_USER=watch1_user
DB_PASSWORD=watch1_dev_password

# Redis Configuration
REDIS_URL=redis://watch1-redis:6379/0

# Media Configuration (Direct Unraid Access)
MEDIA_ROOT=/mnt/user/media
THUMBNAILS_ROOT=/mnt/user/appdata/watch1/thumbnails
DATA_ROOT=/mnt/user/appdata/watch1/data

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=true
NODE_ENV=development
LOG_LEVEL=DEBUG

# Security
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.254.14:3000

# Unraid Specific
UNRAID_SERVER=true
DIRECT_MEDIA_ACCESS=true
PUID=99
PGID=100
EOF

chown "$DEV_USER:$DEV_USER" "$REPO_DIR/.env.unraid.dev"

# Create development startup script
echo "🚀 Creating development startup script"
cat > "$DEV_HOME/start-watch1-dev.sh" << 'EOF'
#!/bin/bash
cd /mnt/user/appdata/watch1-dev/Watch1

echo "🚀 Starting Watch1 Development Environment on Unraid"
echo "=================================================="

# Use Unraid development environment
export $(cat .env.unraid.dev | xargs)

# Start services
docker-compose -f docker-compose.unraid.yml up -d

echo "✅ Watch1 development environment started"
echo "🌐 Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "🔧 API: http://$(hostname -I | awk '{print $1}'):8000"
echo "📊 Logs: docker-compose -f docker-compose.unraid.yml logs -f"
EOF

chmod +x "$DEV_HOME/start-watch1-dev.sh"
chown "$DEV_USER:$DEV_USER" "$DEV_HOME/start-watch1-dev.sh"

# Display SSH connection info
echo ""
echo "🎉 Watch1 Development Environment Setup Complete!"
echo "=================================================="
echo "📍 Development Directory: $DEV_HOME"
echo "📦 Repository: $REPO_DIR"
echo "👤 Development User: $DEV_USER"
echo ""
echo "🔑 SSH Connection:"
echo "   ssh $DEV_USER@$(hostname -I | awk '{print $1}')"
echo ""
echo "🚀 To start development:"
echo "   1. SSH into the server"
echo "   2. Run: $DEV_HOME/start-watch1-dev.sh"
echo "   3. Access: http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "📋 Next Steps:"
echo "   1. Add your SSH public key to: $SSH_KEY_FILE"
echo "   2. Configure VS Code Remote-SSH"
echo "   3. Start developing with direct media access!"
echo ""

# Display public key for easy copying
echo "🔑 SSH Public Key (add this to your local SSH config):"
echo "=================================================="
cat "$DEV_HOME/.ssh/id_rsa.pub"
echo ""
