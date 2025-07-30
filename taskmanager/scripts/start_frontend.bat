@echo off
echo Checking if port 5001 is already in use...

REM Check if port 5001 is occupied
netstat -ano | findstr :5001 >nul
IF %ERRORLEVEL% EQU 0 (
    echo Frontend server is already running on port 5001.
    exit /b 0
)

echo Starting frontend server...
cd frontend
set VITE_LIVE_RELOAD=false
npm run dev -- --port=5001
exit /b 0