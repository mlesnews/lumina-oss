@echo off
REM Interactive Outlook Setup Script
REM This script will guide you through Outlook setup

echo ========================================
echo OUTLOOK CLASSIC - INTERACTIVE SETUP
echo ========================================
echo.
echo This script will help you configure Outlook.
echo.
echo You will need:
echo   - NAS Mail Hub password
echo.
pause

REM Open Outlook if not already open
start outlook.exe
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo SETUP INSTRUCTIONS
echo ========================================
echo.
echo Please follow these steps in Outlook:
echo.
echo 1. Click File (top-left)
echo 2. Click Account Settings ^> Account Settings
echo 3. Click New...
echo 4. Select "Manual setup or additional server types"
echo 5. Click Next
echo 6. Select "POP or IMAP"
echo 7. Click Next
echo.
echo Then enter these EXACT settings:
echo.
echo   Email Address: mlesn@homelab.lesnewski.local
echo   Account Type: IMAP
echo   Incoming: 10.17.17.32
echo   Outgoing: 10.17.17.32
echo   Username: mlesn@homelab.lesnewski.local
echo   Password: [Enter your NAS Mail Hub password]
echo.
echo 8. Click More Settings...
echo 9. Outgoing Server tab: Check authentication
echo 10. Advanced tab:
echo     - Incoming: 993 (SSL/TLS)
echo     - Outgoing: 587 (STARTTLS)
echo 11. Click OK, then Next
echo 12. Click Finish when test succeeds
echo.
echo ========================================
echo.

REM Try to open Account Settings programmatically
powershell -Command "$outlook = New-Object -ComObject Outlook.Application; $outlook.Session.GetDefaultFolder(6)"

echo.
echo Outlook should now be open.
echo Please complete the setup using the instructions above.
echo.
pause
