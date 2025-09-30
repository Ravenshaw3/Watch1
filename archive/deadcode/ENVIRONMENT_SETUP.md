# Watch1 v3.0.1 - Environment Configuration

## 🔧 Why .gitignore Blocks .env Files

The `.gitignore` file blocks `.env` files for **security reasons**:

### **Security Best Practices:**
- ✅ **Prevent Secret Exposure**: API keys, passwords, tokens shouldn't be in version control
- ✅ **Environment Separation**: Different settings for development, staging, production
- ✅ **Team Safety**: Prevents accidental commits of sensitive data

### **Standard Industry Practice:**
- `.env` files contain **sensitive configuration**
- `.env.example` files show **structure without secrets**
- Developers copy `.env.example` to `.env` and fill in real values

## 📁 Current Environment Files

### **Frontend (`/frontend/.env`)**
```bash
# Watch1 Frontend Environment Configuration
VITE_API_URL=http://localhost:8000/api/v1

# Application Configuration
VITE_APP_NAME=Watch1 Media Server
VITE_APP_VERSION=3.0.1

# Development Settings
VITE_DEBUG=true
VITE_LOG_LEVEL=debug

# Media Configuration
VITE_MAX_FILE_SIZE=5368709120
VITE_SUPPORTED_VIDEO_FORMATS=mp4,mkv,avi,mov,wmv,flv,webm
VITE_SUPPORTED_SUBTITLE_FORMATS=srt,vtt,ass,ssa,sub
```

### **Backend (`/backend/.env`)**
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///watch1.db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Advanced Features
ENABLE_SUBTITLES=true
ENABLE_ANALYTICS=true
```

## 🚀 How to Use Environment Files

### **For Development (Current Setup):**
1. **Temporarily disabled** `.env` blocking in `.gitignore`
2. **Created actual** `.env` files for both frontend and backend
3. **Added example files** (`.env.example`) for reference

### **For Production:**
1. **Re-enable** `.env` blocking in `.gitignore`
2. **Use example files** as templates
3. **Set environment variables** on production server
4. **Never commit** actual `.env` files with secrets

## 🔄 Switching Between Modes

### **Development Mode (Current):**
```bash
# .gitignore (lines 2-4 commented out)
# .env
# .env.local
# .env.production
```

### **Production Mode:**
```bash
# .gitignore (lines 2-4 active)
.env
.env.local
.env.production
```

## ⚙️ Environment Variable Usage

### **Frontend (Vite):**
- Variables must start with `VITE_`
- Accessible via `import.meta.env.VITE_VARIABLE_NAME`
- Built into the application at build time

### **Backend (Flask):**
- Load with `python-dotenv` or similar
- Accessible via `os.environ.get('VARIABLE_NAME')`
- Runtime configuration

## 🛡️ Security Recommendations

### **For Development:**
- ✅ Use placeholder secrets in development `.env`
- ✅ Keep example files updated
- ✅ Document all required variables

### **For Production:**
- ✅ Use strong, unique secrets
- ✅ Set environment variables on server
- ✅ Enable `.env` blocking in `.gitignore`
- ✅ Use environment-specific configuration

## 📋 Current Status

- **Frontend .env**: ✅ Created with development settings
- **Backend .env**: ✅ Created with development settings  
- **Example files**: ✅ Created for both frontend and backend
- **Gitignore**: ⚠️ Temporarily disabled for development
- **Security**: ⚠️ Re-enable .env blocking before production

**The environment files are now accessible for development, but remember to re-enable .env blocking before deploying to production!**
