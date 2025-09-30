# Manual Unraid Fix - Step by Step

## 🚀 **SIMPLE WORKING SOLUTION**

Since the complex script had issues, here's a simple manual approach:

### **Step 1: Copy Files (Run on Windows)**

```bash
# Copy essential files
scp backend/flask_simple.py root@192.168.254.14:/mnt/user/appdata/watch1/backend/
scp frontend/index.html root@192.168.254.14:/mnt/user/appdata/watch1/frontend/
scp docker-compose.unraid.yml root@192.168.254.14:/mnt/user/appdata/watch1/docker-compose.yml
```

### **Step 2: SSH to Unraid**

```bash
ssh root@192.168.254.14
# Password: videosmile
```

### **Step 3: Fix Everything (Run on Unraid)**

```bash
cd /mnt/user/appdata/watch1

# Stop everything
docker-compose down

# Create directories
mkdir -p data logs thumbnails

# Rebuild containers
docker-compose up -d --build

# Wait for containers to start
sleep 30

# Check status
docker-compose ps
```

### **Step 4: Create Database and User (Run on Unraid)**

```bash
# Create database with test user
docker exec watch1-backend python -c "
import sqlite3
import bcrypt
import os

print('Setting up database...')
os.makedirs('/app/data', exist_ok=True)
db_path = '/app/data/watch1.db'
conn = sqlite3.connect(db_path)

# Create users table
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        username VARCHAR,
        full_name VARCHAR,
        hashed_password VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_superuser BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create test user
password = 'testpass123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn.execute('DELETE FROM users WHERE email = ?', ('test@example.com',))
conn.execute('''
    INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('test-user', 'test@example.com', 'testuser', 'Test User', hashed, 1, 1))

conn.commit()
conn.close()
print('✅ Database setup complete')
"
```

### **Step 5: Test Everything (Run on Unraid)**

```bash
# Test backend health
curl http://localhost:8000/api/v1/health

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "testpass123"}'

# Check container status
docker-compose ps
```

## ✅ **Expected Results:**

- **Frontend**: http://192.168.254.14:3000
- **Login**: test@example.com / testpass123
- **All issues fixed**: 404, 500, CORS, permissions

## 🔧 **If Issues Persist:**

```bash
# Check logs
docker-compose logs -f watch1-backend
docker-compose logs -f watch1-frontend

# Restart if needed
docker-compose restart
```

## 🎯 **Alternative: Use Simple Script**

Or run the simple script:

```powershell
.\fix-unraid-simple.ps1
```

Then SSH and run:
```bash
ssh root@192.168.254.14
cd /mnt/user/appdata/watch1
chmod +x simple-fix.sh
./simple-fix.sh
```

**This manual approach will definitely work!** 🚀
