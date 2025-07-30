@echo off
echo Sending shutdown request to Flask server...

REM Send shutdown request
curl -X POST http://localhost:5000/shutdown >nul 2>&1

REM Wait briefly to allow Flask to shut down
timeout /t 2 >nul

REM Check if Flask is still running using tasklist
tasklist | findstr /I "python.exe" >nul
IF %ERRORLEVEL% EQU 0 (
    echo Error: Flask server did not shut down properly.
    exit /b 1
)

echo Flask server stopped successfully.
exit /b 0