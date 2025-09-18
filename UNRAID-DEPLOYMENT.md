# Watch1 Media Server - Unraid Deployment Guide

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# SSH into your Unraid server
ssh root@192.168.254.14

# Download and run the setup script
curl -o unraid-setup.sh https://raw.githubusercontent.com/Ravenshaw3/Watch1/main/unraid-setup.sh
chmod +x unraid-setup.sh
./unraid-setup.sh
```

### Option 2: Manual Setup

1. **SSH into your Unraid server:**
   ```bash
   ssh root@192.168.254.14
   ```

2. **Create directories:**
   ```bash
   mkdir -p /mnt/user/appdata/watch1/{postgres,redis,data}
   mkdir -p /mnt/user/media
   chown -R nobody:users /mnt/user/appdata/watch1
   chown -R nobody:users /mnt/user/media
   ```

3. **Clone the repository:**
   ```bash
   cd /mnt/user/appdata/watch1
   git clone https://github.com/Ravenshaw3/Watch1.git
   cd Watch1
   ```

4. **Set up Docker Compose:**
   ```bash
   cp unraid-docker-compose.yml docker-compose.yml
   docker-compose up -d --build
   ```

## 🌐 Access Points

- **Frontend**: http://192.168.254.14:3000
- **Backend API**: http://192.168.254.14:8000
- **API Documentation**: http://192.168.254.14:8000/docs
- **Health Check**: http://192.168.254.14:8000/health

## 📁 Directory Structure

```
/mnt/user/appdata/watch1/
├── postgres/          # PostgreSQL data
├── redis/             # Redis data
├── data/              # Application data
└── Watch1/            # Source code

/mnt/user/media/       # Your media files
```

## 🔧 Management Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update Watch1
cd /mnt/user/appdata/watch1/Watch1
git pull origin main
docker-compose up -d --build

# Stop services
docker-compose down

# Start services
docker-compose up -d
```

## 🎬 Adding Media Files

1. Copy your media files to `/mnt/user/media/`
2. Access the web interface at http://192.168.254.14:3000
3. Use the upload feature or scan for existing files

## 🔒 Security Notes

- Change default passwords in production
- Consider setting up SSL/TLS certificates
- Configure firewall rules if needed
- Regular backups of `/mnt/user/appdata/watch1/`

## 🆘 Troubleshooting

### Services not starting:
```bash
docker-compose logs [service-name]
```

### Permission issues:
```bash
chown -R nobody:users /mnt/user/appdata/watch1
chown -R nobody:users /mnt/user/media
```

### Port conflicts:
Edit `docker-compose.yml` to change port mappings

## 📞 Support

- **GitHub**: https://github.com/Ravenshaw3/Watch1
- **Issues**: https://github.com/Ravenshaw3/Watch1/issues
