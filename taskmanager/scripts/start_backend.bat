@echo off
echo Checking if Flask is already running on port 5000...

REM Check if port 5000 is occupied
netstat -ano | findstr :5000 >nul
IF %ERRORLEVEL% EQU 0 (
    echo Error: Flask server is already running on port 5000.
    exit /b 0
)

echo Starting Flask server...
cd backend
CALL run_task.bat python app.py