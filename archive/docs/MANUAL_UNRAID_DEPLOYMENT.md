# Manual Unraid Deployment - Simple Steps

## 🎯 **QUICK DEPLOYMENT FOR 192.168.254.14**

Since the automated script had issues, here's the simple manual approach:

### **Step 1: Copy Files to Unraid**

1. **Copy docker-compose file:**
   ```bash
   scp docker-compose.unraid.yml root@192.168.254.14:/mnt/user/appdata/watch1/docker-compose.yml
   ```

2. **Copy Docker images (if needed):**
   ```bash
   # If you have the .tar files
   scp watch1-backend.tar root@192.168.254.14:/mnt/user/appdata/watch1/
   scp watch1-frontend.tar root@192.168.254.14:/mnt/user/appdata/watch1/
   ```

### **Step 2: SSH to Unraid and Deploy**

1. **SSH to your Unraid server:**
   ```bash
   ssh root@192.168.254.14
   ```

2. **Create directories:**
   ```bash
   mkdir -p /mnt/user/appdata/watch1/{data,logs,thumbnails}
   cd /mnt/user/appdata/watch1
   ```

3. **Load images (if copied):**
   ```bash
   docker load < watch1-backend.tar
   docker load < watch1-frontend.tar
   ```

4. **OR Build images directly on Unraid:**
   ```bash
   # If you have the source code on Unraid
   docker build -t watch1-backend:latest -f docker/Dockerfile.backend .
   docker build -t watch1-frontend:latest -f docker/Dockerfile.frontend .
   ```

5. **Deploy:**
   ```bash
   docker-compose up -d
   ```

### **Step 3: Verify Deployment**

1. **Check status:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

2. **Access your media server:**
   - URL: http://192.168.254.14:3000
   - Login: test@example.com / testpass123

### **Alternative: Use Docker Hub (Recommended)**

If you want to avoid copying large image files:

1. **Push to Docker Hub (from Windows):**
   ```bash
   docker tag watch1-backend:latest yourusername/watch1-backend:latest
   docker tag watch1-frontend:latest yourusername/watch1-frontend:latest
   docker push yourusername/watch1-backend:latest
   docker push yourusername/watch1-frontend:latest
   ```

2. **Update docker-compose.yml on Unraid:**
   ```yaml
   services:
     watch1-backend:
       image: yourusername/watch1-backend:latest
     watch1-frontend:
       image: yourusername/watch1-frontend:latest
   ```

3. **Deploy on Unraid:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## ✅ **What's Fixed and Ready:**

- ✅ TypeScript `mediaFiles.value` errors resolved
- ✅ Authentication system working
- ✅ Categories field added to API response
- ✅ Production database compatibility verified
- ✅ All API endpoints returning 200 OK

## 🎯 **Expected Results:**

After deployment, you should have:
- Frontend at http://192.168.254.14:3000
- Login working with test@example.com / testpass123
- Media library showing 102 files across 4 categories
- No TypeScript errors in browser console
- Posters and streaming working (once media is properly mounted)

**Your Watch1 media server is ready for Unraid!** 🚀
