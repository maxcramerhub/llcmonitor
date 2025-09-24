@echo off
echo Setting up project protection...
echo.

REM This script must be run as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator privileges confirmed.
) else (
    echo This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Get current directory
set PROJECT_DIR=%~dp0

echo Protecting project directory: %PROJECT_DIR%
echo.

REM Remove delete permissions for Users group, but keep read/execute
echo Removing delete permissions for standard users...
icacls "%PROJECT_DIR%" /deny "Users:(DE)"
icacls "%PROJECT_DIR%" /deny "Users:(DC)"

REM Protect critical files from modification
echo Protecting critical Python files...
icacls "%PROJECT_DIR%manage.py" /deny "Users:(W,D)"
icacls "%PROJECT_DIR%llcsite\*.py" /deny "Users:(W,D)" 2>nul
icacls "%PROJECT_DIR%monitor\*.py" /deny "Users:(W,D)" 2>nul

REM Protect the database
echo Protecting database...
icacls "%PROJECT_DIR%mydatabase.sqlite3" /deny "Users:(D)" 2>nul

REM Make the run script read-only for users
echo Protecting run script...
icacls "%PROJECT_DIR%run_server.bat" /deny "Users:(W,D)"

echo.
echo Protection setup complete!
echo Students can still:
echo - Run the application
echo - View files
echo - Access the web interface
echo.
echo Students CANNOT:
echo - Delete the project folder
echo - Modify core Python files
echo - Delete the database
echo.
pause

