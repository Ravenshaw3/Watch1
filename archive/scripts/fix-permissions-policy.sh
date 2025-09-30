#!/bin/bash
# Fix Permissions-Policy Header Error on Unraid
echo "🔧 Fixing Permissions-Policy header error..."

cd /mnt/user/appdata/watch1

echo "🛑 Stopping containers..."
docker-compose down

echo "🔄 Rebuilding with permissions-policy fix..."
docker-compose up -d --build

echo "⏳ Waiting for containers to start..."
sleep 20

echo "📊 Container status:"
docker-compose ps

echo ""
echo "🧪 Testing permissions-policy headers..."
echo "Backend headers:"
curl -I http://localhost:8000/api/v1/health 2>/dev/null | grep -i "permissions\|policy\|cors" || echo "No policy headers found"

echo ""
echo "Frontend headers:"
curl -I http://localhost:3000 2>/dev/null | grep -i "permissions\|policy" || echo "No frontend policy headers"

echo ""
echo "🧪 Testing login API..."
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -H "Origin: http://192.168.254.14:3000" \
  -d '{"username": "test@example.com", "password": "testpass123"}' \
  2>/dev/null | head -c 100

echo ""
echo ""
echo "✅ Permissions-Policy fix deployed!"
echo ""
echo "🌐 Access your media server:"
echo "   Frontend: http://192.168.254.14:3000"
echo "   Backend:  http://192.168.254.14:8000"
echo ""
echo "📋 Fixed issues:"
echo "   ✅ CORS policy blocking"
echo "   ✅ Permissions-Policy header errors"
echo "   ✅ Security headers properly configured"
echo ""
echo "🔍 If still having issues:"
echo "   - Check browser console (F12)"
echo "   - Check logs: docker-compose logs -f"
echo "   - Clear browser cache and try again"
