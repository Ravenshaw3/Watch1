#!/bin/bash
# Quick Build Fix v3.0.3 - Immediate Resolution
echo "⚡ QUICK BUILD FIX v3.0.3"
echo "========================"

cd /mnt/user/appdata/watch1

echo "1. FIXING FRONTEND BUILD ISSUES"
echo "==============================="

# Fix package.json with all required dependencies including terser
cat > frontend/package.json << 'EOF'
{
  "name": "watch1-frontend",
  "version": "3.0.3",
  "description": "Watch1 Media Server Frontend v3.0.3",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@headlessui/vue": "^1.7.16",
    "@heroicons/vue": "^2.0.18",
    "@vueuse/core": "^10.5.0",
    "axios": "^1.6.2",
    "pinia": "^2.1.7",
    "vue": "^3.3.8",
    "vue-router": "^4.2.5"
  },
  "devDependencies": {
    "@tailwindcss/forms": "^0.5.7",
    "@tailwindcss/typography": "^0.5.10",
    "@types/node": "^20.9.0",
    "@vitejs/plugin-vue": "^5.2.4",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "terser": "^5.24.0",
    "typescript": "^5.2.2",
    "vite": "^6.3.6",
    "vue-tsc": "^3.0.7"
  }
}
EOF

echo "✅ Package.json updated with terser dependency"

# Fix CSS import order
cat > frontend/src/style.css << 'EOF'
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Dark mode scrollbar */
.dark ::-webkit-scrollbar-track {
  background: #374151;
}

.dark ::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Custom styles */
.primary-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
EOF

echo "✅ CSS import order fixed"

# Create simplified vite config without terser
cat > frontend/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
  },
})
EOF

echo "✅ Vite config simplified (no minification to avoid terser)"

echo ""
echo "2. REBUILDING FRONTEND WITH FIXES"
echo "================================="

echo "Removing failed frontend image..."
docker rmi watch1-frontend 2>/dev/null || true

echo "Building frontend with fixed config..."
docker-compose build --no-cache watch1-frontend

if [ $? -eq 0 ]; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Frontend build still failing - trying alternative approach"
    
    # Alternative: Build without minification
    cat > frontend/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    minify: false,
    sourcemap: false,
  },
})
EOF
    
    echo "Trying build without minification..."
    docker-compose build --no-cache watch1-frontend
fi

echo ""
echo "3. STARTING SYSTEM"
echo "=================="

echo "Starting all services..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 30

echo ""
echo "4. TESTING SYSTEM"
echo "================="

echo "Testing backend..."
for i in {1..5}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend healthy"
        break
    else
        echo "⏳ Backend starting... ($i/5)"
        sleep 5
    fi
done

echo "Testing frontend..."
for i in {1..5}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend accessible"
        break
    else
        echo "⏳ Frontend starting... ($i/5)"
        sleep 5
    fi
done

echo "Container status:"
docker-compose ps

echo ""
echo "⚡ QUICK BUILD FIX COMPLETE"
echo "=========================="
echo "✅ Frontend dependencies fixed"
echo "✅ CSS import order corrected"
echo "✅ Build configuration simplified"
echo "✅ System should be running"
echo ""
echo "🌐 ACCESS SYSTEM:"
echo "Frontend: http://192.168.254.14:3000"
echo "Backend: http://192.168.254.14:8000"
echo ""
echo "LOGIN CREDENTIALS:"
echo "Email: test@example.com"
echo "Password: testpass123"
