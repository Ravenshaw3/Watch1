# Simple Watch1 Startup Script
Write-Host "Starting Watch1 Media Server..." -ForegroundColor Green

# Stop containers
docker-compose -f docker-compose.dev.yml down

# Start backend directly
Write-Host "Starting backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python flask_simple.py"

# Wait and start frontend
Start-Sleep -Seconds 2
Write-Host "Starting frontend..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d frontend db redis

Write-Host "Done! Frontend: http://localhost:3000" -ForegroundColor Green
