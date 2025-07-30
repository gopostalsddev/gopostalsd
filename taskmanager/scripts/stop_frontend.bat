@echo off
setlocal enabledelayedexpansion

echo Finding process running on port 5001...

REM Reset PID variable
set "PID="

REM Get the PID of the process using port 5001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
    set "PID=%%a"
)

REM Check if PID was found
if "!PID!"=="" (
    echo No process found running on port 5001...
    exit /b 0
)

REM Ensure PID is a valid number
echo Stopping frontend server with PID !PID!...
if "!PID!"=="0" (
    echo No process found running on port 5001...
    exit /b 0
)

taskkill /F /PID !PID!

REM ✅ Add a short delay to ensure process fully exits
timeout /t 2 >nul

echo Frontend server stopped successfully.
exit /b 0