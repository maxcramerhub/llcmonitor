@echo off
echo Project Recovery Tool
echo.

REM Set backup location
set BACKUP_ROOT=C:\ProjectBackups
set PROJECT_NAME=LLCMonitor

REM Check if backups exist
if not exist "%BACKUP_ROOT%" (
    echo No backups found at %BACKUP_ROOT%
    echo Please check backup location or contact administrator
    pause
    exit /b 1
)

echo Available backups:
echo.
dir "%BACKUP_ROOT%\%PROJECT_NAME%_*" /ad /o-d /b

echo.
set /p BACKUP_CHOICE="Enter the backup folder name to restore (or press Enter for latest): "

if "%BACKUP_CHOICE%"=="" (
    REM Get the latest backup
    for /f "delims=" %%i in ('dir "%BACKUP_ROOT%\%PROJECT_NAME%_*" /ad /o-d /b') do (
        set BACKUP_CHOICE=%%i
        goto :found_backup
    )
)

:found_backup
set RESTORE_FROM=%BACKUP_ROOT%\%BACKUP_CHOICE%

if not exist "%RESTORE_FROM%" (
    echo Backup not found: %RESTORE_FROM%
    pause
    exit /b 1
)

echo.
echo WARNING: This will overwrite the current project!
set /p CONFIRM="Are you sure? (type YES to continue): "

if not "%CONFIRM%"=="YES" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo Restoring from: %RESTORE_FROM%
echo To: %~dp0

REM Clear current directory (except this script)
for /f "delims=" %%i in ('dir /b "%~dp0" ^| findstr /v "restore_project.bat"') do (
    if exist "%~dp0%%i\*" (
        rmdir /s /q "%~dp0%%i"
    ) else (
        del /q "%~dp0%%i"
    )
)

REM Restore files
xcopy "%RESTORE_FROM%\*" "%~dp0" /E /I /H /Y

echo.
echo Project restored successfully!
echo You can now run the server normally.
pause

