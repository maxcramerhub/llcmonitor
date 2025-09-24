@echo off
echo Creating project backup...

REM Set backup location (change this to your preferred backup location)
set BACKUP_ROOT=C:\ProjectBackups
set PROJECT_NAME=LLCMonitor
set TIMESTAMP=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=%BACKUP_ROOT%\%PROJECT_NAME%_%TIMESTAMP%

REM Create backup directory
if not exist "%BACKUP_ROOT%" mkdir "%BACKUP_ROOT%"
mkdir "%BACKUP_DIR%"

REM Copy project files (excluding cache and temporary files)
echo Copying project files...
xcopy "%~dp0*" "%BACKUP_DIR%\" /E /I /H /Y /EXCLUDE:%~dp0backup_exclude.txt

REM Create exclude file if it doesn't exist
if not exist "%~dp0backup_exclude.txt" (
    echo __pycache__\ > "%~dp0backup_exclude.txt"
    echo *.pyc >> "%~dp0backup_exclude.txt"
    echo *.log >> "%~dp0backup_exclude.txt"
    echo .git\ >> "%~dp0backup_exclude.txt"
)

REM Keep only last 10 backups (cleanup old ones)
echo Cleaning up old backups...
for /f "skip=10 delims=" %%i in ('dir "%BACKUP_ROOT%\%PROJECT_NAME%_*" /ad /o-d /b') do (
    rmdir /s /q "%BACKUP_ROOT%\%%i"
)

echo Backup created: %BACKUP_DIR%
echo.
pause

