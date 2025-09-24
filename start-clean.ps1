# Watch1 Clean Startup Script
# This script starts the Watch1 media server with a clean slate

Write-Host "🎬 Watch1 Media Server - Clean Startup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Stop any running containers
Write-Host "🛑 Stopping any running containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down 2>$null

# Clean up Docker system (optional)
Write-Host "🧹 Cleaning Docker system..." -ForegroundColor Yellow
docker system prune -f 2>$null

# Start backend directly (bypassing Docker issues)
Write-Host "🚀 Starting Flask backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python flask_simple.py"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend container (this usually works)
Write-Host "🌐 Starting frontend container..." -ForegroundColor Green
docker-compose -f docker-compose.dev.yml up -d frontend

# Start database container
Write-Host "💾 Starting database container..." -ForegroundColor Green
docker-compose -f docker-compose.dev.yml up -d db

# Start Redis container
Write-Host "📦 Starting Redis container..." -ForegroundColor Green
docker-compose -f docker-compose.dev.yml up -d redis

Write-Host ""
Write-Host "✅ Startup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔍 Debug:    http://localhost:3000/debug" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Login credentials:" -ForegroundColor Yellow
Write-Host "   Email: test@example.com" -ForegroundColor White
Write-Host "   Password: testpass123" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Waiting 5 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if services are running
Write-Host "🔍 Checking service status..." -ForegroundColor Green

try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend: Not responding" -ForegroundColor Red
}

try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend: Not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "2. Login with the credentials above" -ForegroundColor White
Write-Host "3. Check the debug page if you have issues" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
