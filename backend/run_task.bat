@echo off
REM Check if the virtual environment is already activated
IF "%VIRTUAL_ENV%"=="" (
    REM Activate the virtual environment
    CALL backend\venv\Scripts\activate
)

REM Execute the provided command argument
echo Running: %*
CALL %*

REM Capture exit status
IF %ERRORLEVEL% EQU 15 (
    echo Flask server exited gracefully with code 15.
    exit /b 0
) ELSE IF %ERRORLEVEL% NEQ 0 (
    echo Error: Task execution failed with code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
) ELSE (
    echo Task completed successfully.
    exit /b 0
)


REM Deactivate the virtual environment
CALL deactivate

REM Exit the script
exit /b %ERRORLEVEL%