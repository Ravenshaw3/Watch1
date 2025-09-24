@echo off
title Watch1 v3.0.1 - Production Server Startup

echo ============================================================
echo WATCH1 v3.0.1 - PRODUCTION SERVER STARTUP
echo ============================================================
echo.

echo [%TIME%] [INFO] Cleaning up existing server processes...

REM Kill processes on port 8000 (Backend)
echo [%TIME%] [INFO] Checking backend port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo [%TIME%] [WARNING] Killing process PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill processes on port 3000 (Frontend)
echo [%TIME%] [INFO] Checking frontend port 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo [%TIME%] [WARNING] Killing process PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any Node.js processes
echo [%TIME%] [INFO] Cleaning up Node.js processes...
taskkill /IM node.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [%TIME%] [WARNING] Stopped Node.js processes
) else (
    echo [%TIME%] [SUCCESS] No Node.js processes found
)

REM Wait for processes to terminate
echo [%TIME%] [INFO] Waiting for processes to terminate...
timeout /t 3 /nobreak >nul

REM Check if required files exist
if not exist "backend\flask_simple.py" (
    echo [%TIME%] [ERROR] Backend file not found: backend\flask_simple.py
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [%TIME%] [ERROR] Frontend file not found: frontend\package.json
    pause
    exit /b 1
)

REM Start backend server
echo [%TIME%] [INFO] Starting Flask backend server...
cd /d "%~dp0backend"
start "Watch1 Backend" /min python flask_simple.py
cd /d "%~dp0"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo [%TIME%] [INFO] Starting Vue.js frontend server...
cd /d "%~dp0frontend"
start "Watch1 Frontend" /min npm run dev
cd /d "%~dp0"

REM Wait for frontend to initialize
echo [%TIME%] [INFO] Waiting for servers to initialize...
timeout /t 8 /nobreak >nul

REM Test servers
echo [%TIME%] [INFO] Testing server connectivity...

REM Test backend
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/version > temp_backend_test.txt 2>nul
set /p backend_status=<temp_backend_test.txt
del temp_backend_test.txt >nul 2>&1

if "%backend_status%"=="200" (
    echo [%TIME%] [SUCCESS] Backend test: OK ^(HTTP %backend_status%^)
    set backend_ok=1
) else (
    echo [%TIME%] [ERROR] Backend test: FAILED ^(HTTP %backend_status%^)
    set backend_ok=0
)

REM Test frontend
curl -s -o nul -w "%%{http_code}" http://localhost:3000 > temp_frontend_test.txt 2>nul
set /p frontend_status=<temp_frontend_test.txt
del temp_frontend_test.txt >nul 2>&1

if "%frontend_status%"=="200" (
    echo [%TIME%] [SUCCESS] Frontend test: OK ^(HTTP %frontend_status%^)
    set frontend_ok=1
) else (
    echo [%TIME%] [ERROR] Frontend test: FAILED ^(HTTP %frontend_status%^)
    set frontend_ok=0
)

REM Check overall status
if "%backend_ok%"=="1" if "%frontend_ok%"=="1" (
    echo.
    echo ============================================================
    echo [%TIME%] [SUCCESS] PRODUCTION SERVERS SUCCESSFULLY STARTED!
    echo ============================================================
    echo.
    echo Backend:  http://localhost:8000
    echo Frontend: http://localhost:3000
    echo.
    echo ============================================================
    echo.
    echo [%TIME%] [INFO] Both servers are running in separate windows
    echo [%TIME%] [INFO] Close those windows to stop the servers
    echo [%TIME%] [INFO] Press any key to exit this startup script
    pause >nul
) else (
    echo.
    echo [%TIME%] [ERROR] Server startup failed!
    echo [%TIME%] [INFO] Check the server windows for error details
    pause
)

echo.
echo [%TIME%] [INFO] Startup script completed
