@echo off
REM Execute Complete Outlook Setup
REM This batch file runs all setup steps

echo ========================================
echo OUTLOOK CLASSIC - COMPLETE SETUP
echo ========================================
echo.

cd /d "%~dp0\..\.."

echo Step 1: Opening Outlook...
python scripts/python/open_outlook_account_settings.py
echo.

echo Step 2: Running Outlook setup script...
cd config\outlook
call setup_outlook_nas_hub.bat
cd ..\..
echo.

echo Step 3: Verifying setup...
python scripts/python/verify_outlook_nas_hub_setup.py
echo.

echo ========================================
echo SETUP COMPLETE
echo ========================================
echo.
echo If Outlook account is not yet configured:
echo   1. Outlook should now be open
echo   2. Go to: File ^> Account Settings ^> Account Settings
echo   3. Click 'New...'
echo   4. Follow: config\outlook\OUTLOOK_QUICK_SETUP.md
echo.

pause
