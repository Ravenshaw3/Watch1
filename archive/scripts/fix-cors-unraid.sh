#!/bin/bash
# Fix CORS Policy Issues on Unraid
echo "🔧 Fixing CORS policy blocking on Unraid..."

cd /mnt/user/appdata/watch1

echo "🛑 Stopping current containers..."
docker-compose down

echo "🔄 Rebuilding with CORS fix..."
docker-compose up -d --build

echo "⏳ Waiting for containers to start..."
sleep 15

echo "📊 Container status:"
docker-compose ps

echo "🧪 Testing CORS fix..."
echo "Testing backend health endpoint:"
curl -v http://localhost:8000/api/v1/health 2>&1 | grep -E "(HTTP|Access-Control|CORS)" || echo "Backend not responding"

echo ""
echo "Testing login endpoint with CORS headers:"
curl -X OPTIONS http://localhost:8000/api/v1/auth/login/access-token \
  -H "Origin: http://192.168.254.14:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v 2>&1 | grep -E "(HTTP|Access-Control)" || echo "CORS test failed"

echo ""
echo "✅ CORS fix deployed!"
echo ""
echo "🌐 Try accessing your media server again:"
echo "   Frontend: http://192.168.254.14:3000"
echo "   Backend:  http://192.168.254.14:8000"
echo "   Login:    test@example.com / testpass123"
echo ""
echo "📋 If still having issues, check browser console for errors"
echo "📊 Check logs: docker-compose logs -f watch1-backend"
