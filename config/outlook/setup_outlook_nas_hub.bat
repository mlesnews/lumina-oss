@echo off
echo ========================================
echo OUTLOOK CLASSIC - NAS MAIL HUB SETUP
echo ========================================
echo.

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "setup_outlook_nas_hub.ps1"

pause
