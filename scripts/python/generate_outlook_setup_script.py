#!/usr/bin/env python3
"""
Generate Outlook Setup Script
Creates a PowerShell script to automate Outlook configuration.

Tags: #OUTLOOK #EMAIL #AUTOMATION #SETUP
@JARVIS @LUMINA
"""

import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("generate_outlook_setup_script")


def generate_outlook_setup_script():
    """Generate PowerShell script for Outlook setup"""

    script_content = '''# Outlook MailStation Setup Script
# Generated: {timestamp}
# Purpose: Configure Outlook Desktop to connect to MailStation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Outlook MailStation Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$EmailAddress = "mlesn@<LOCAL_HOSTNAME>"
$DisplayName = "Company Email (MailStation)"
$IMAPServer = "<NAS_PRIMARY_IP>"
$IMAPPort = 993
$SMTPServer = "<NAS_PRIMARY_IP>"
$SMTPPort = 25

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Email: $EmailAddress"
Write-Host "  IMAP: $IMAPServer`:$IMAPPort (SSL/TLS)"
Write-Host "  SMTP: $SMTPServer`:$SMTPPort (STARTTLS)"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Manual Setup Required" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Outlook Desktop requires manual configuration through the UI." -ForegroundColor Yellow
Write-Host ""
Write-Host "Follow these steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Open Outlook Desktop" -ForegroundColor White
Write-Host "2. File → Account Settings → Account Settings" -ForegroundColor White
Write-Host "3. Click 'New...'" -ForegroundColor White
Write-Host "4. Select 'Manual setup or additional server types'" -ForegroundColor White
Write-Host "5. Click 'Next'" -ForegroundColor White
Write-Host "6. Select 'POP or IMAP'" -ForegroundColor White
Write-Host "7. Click 'Next'" -ForegroundColor White
Write-Host ""
Write-Host "Enter Account Information:" -ForegroundColor Green
Write-Host "  Your Name: $DisplayName" -ForegroundColor White
Write-Host "  Email Address: $EmailAddress" -ForegroundColor White
Write-Host "  Account Type: IMAP" -ForegroundColor White
Write-Host "  Incoming mail server: $IMAPServer" -ForegroundColor White
Write-Host "  Outgoing mail server (SMTP): $SMTPServer" -ForegroundColor White
Write-Host "  User Name: $EmailAddress" -ForegroundColor White
Write-Host "  Password: [Enter your MailStation password]" -ForegroundColor White
Write-Host ""
Write-Host "8. Click 'More Settings...'" -ForegroundColor White
Write-Host ""
Write-Host "Outgoing Server Tab:" -ForegroundColor Green
Write-Host "  ☑ Check 'My outgoing server (SMTP) requires authentication'" -ForegroundColor White
Write-Host "  ○ Select 'Use same settings as my incoming mail server'" -ForegroundColor White
Write-Host ""
Write-Host "Advanced Tab:" -ForegroundColor Green
Write-Host "  Incoming server (IMAP): $IMAPPort" -ForegroundColor White
Write-Host "  Use the following type of encrypted connection: SSL/TLS" -ForegroundColor White
Write-Host "  Outgoing server (SMTP): $SMTPPort" -ForegroundColor White
Write-Host "  Use the following type of encrypted connection: STARTTLS" -ForegroundColor White
Write-Host ""
Write-Host "9. Click 'OK'" -ForegroundColor White
Write-Host "10. Click 'Next'" -ForegroundColor White
Write-Host "11. Outlook will test the connection" -ForegroundColor White
Write-Host "12. Click 'Finish' when successful" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test connection
Write-Host "Testing connection to MailStation..." -ForegroundColor Yellow
$imapTest = Test-NetConnection -ComputerName $IMAPServer -Port $IMAPPort -WarningAction SilentlyContinue
$smtpTest = Test-NetConnection -ComputerName $SMTPServer -Port $SMTPPort -WarningAction SilentlyContinue

if ($imapTest.TcpTestSucceeded) {{
    Write-Host "  ✅ IMAP Port $IMAPPort: Open" -ForegroundColor Green
}} else {{
    Write-Host "  ❌ IMAP Port $IMAPPort: Closed or Unreachable" -ForegroundColor Red
}}

if ($smtpTest.TcpTestSucceeded) {{
    Write-Host "  ✅ SMTP Port $SMTPPort: Open" -ForegroundColor Green
}} else {{
    Write-Host "  ❌ SMTP Port $SMTPPort: Closed or Unreachable" -ForegroundColor Red
}}

Write-Host ""
Write-Host "If ports are closed, check:" -ForegroundColor Yellow
Write-Host "  1. MailStation is running in DSM" -ForegroundColor White
Write-Host "  2. Firewall allows ports $IMAPPort and $SMTPPort" -ForegroundColor White
Write-Host "  3. NAS IP address is correct: $IMAPServer" -ForegroundColor White
Write-Host ""
'''.format(timestamp=datetime.now().isoformat())

    return script_content


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        scripts_dir = project_root / "scripts" / "powershell"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_file = scripts_dir / "setup_outlook_mailstation.ps1"
        script_content = generate_outlook_setup_script()

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        print(f"✅ Outlook setup script generated: {script_file}")
        print(f"   Run with: powershell -ExecutionPolicy Bypass -File {script_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()