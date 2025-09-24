@echo off
echo Starting Django Development Server...
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Quick backup before running (optional)
REM call backup_project.bat

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if manage.py exists
if not exist "manage.py" (
    echo Error: manage.py not found in current directory
    echo Make sure you're running this script from the Django project root
    pause
    exit /b 1
)

REM Run Django migrations
echo Running migrations...
py manage.py migrate
echo.

REM Start the development server
echo Starting Django server on http://127.0.0.1:8000/
echo Opening Chrome in fullscreen after server starts...
echo Press Ctrl+C to stop the server
echo.

REM Start Django server in background
start /b py manage.py runserver

REM Wait a moment for server to start
timeout /t 4 /nobreak >nul

REM Open Chrome in fullscreen mode
echo Opening Chrome in fullscreen...
start chrome --start-fullscreen http://localhost:8000

REM Keep the console window open and show server output
echo.
echo Chrome should now be open in fullscreen mode.
echo The Django server is running in the background.
echo Press Ctrl+C in this window to stop the server.
echo.
pause

REM Keep the window open if there's an error
if errorlevel 1 (
    echo.
    echo Server stopped with an error. Check the output above.
    pause
)
