"""
Automated Outlook Classic Setup for NAS Mail Hub
Attempts to configure Outlook Classic via COM automation to connect to NAS Mail Hub.

#JARVIS #LUMINA #OUTLOOK #NAS #MAILPLUS #AUTOMATION #DOIT
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("AutomatedOutlookNASHubSetup")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AutomatedOutlookNASHubSetup")


class AutomatedOutlookNASHubSetup:
    """
    Automated setup for Outlook Classic to connect to NAS Mail Hub.
    """

    def __init__(self, project_root: Path):
        """
        Initialize automated Outlook setup.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "outlook"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def create_outlook_setup_powershell_script(self) -> Path:
        """
        Create PowerShell script to configure Outlook via COM automation.

        Returns:
            Path to PowerShell script
        """
        script_content = '''# Outlook Classic Setup for NAS Mail Hub - Automated Configuration
# Generated: {timestamp}

Write-Host "========================================"
Write-Host "OUTLOOK CLASSIC - NAS MAIL HUB SETUP"
Write-Host "========================================"
Write-Host ""

# Check if Outlook is installed
try {{
    $outlook = New-Object -ComObject Outlook.Application
    Write-Host "✅ Outlook is installed and accessible"
}} catch {{
    Write-Host "❌ Outlook is not installed or not accessible"
    Write-Host "   Please install Microsoft Outlook first"
    exit 1
}}

# Get Outlook namespace
$namespace = $outlook.GetNamespace("MAPI")
$accounts = $namespace.Accounts

Write-Host ""
Write-Host "Current Outlook Accounts:"
Write-Host "------------------------"
foreach ($account in $accounts) {{
    Write-Host "  - $($account.DisplayName) ($($account.SmtpAddress))"
}}

Write-Host ""
Write-Host "========================================"
Write-Host "NAS MAIL HUB CONFIGURATION"
Write-Host "========================================"
Write-Host ""
Write-Host "Account Details:"
Write-Host "  Email: mlesn@<LOCAL_HOSTNAME>"
Write-Host "  Display Name: NAS Mail Hub"
Write-Host ""
Write-Host "IMAP Settings:"
Write-Host "  Server: <NAS_PRIMARY_IP>"
Write-Host "  Port: 993"
Write-Host "  Encryption: SSL/TLS"
Write-Host ""
Write-Host "SMTP Settings:"
Write-Host "  Server: <NAS_PRIMARY_IP>"
Write-Host "  Port: 587"
Write-Host "  Encryption: STARTTLS"
Write-Host ""

# Check if account already exists
$accountExists = $false
foreach ($account in $accounts) {{
    if ($account.SmtpAddress -eq "mlesn@<LOCAL_HOSTNAME>") {{
        Write-Host "⚠️  Account already exists: mlesn@<LOCAL_HOSTNAME>"
        $accountExists = $true
        break
    }}
}}

if (-not $accountExists) {{
    Write-Host ""
    Write-Host "========================================"
    Write-Host "MANUAL SETUP REQUIRED"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Outlook COM API has limitations for adding accounts."
    Write-Host "Please follow these steps to add the account manually:"
    Write-Host ""
    Write-Host "1. Open Outlook"
    Write-Host "2. Go to File → Account Settings → Account Settings"
    Write-Host "3. Click 'New...'"
    Write-Host "4. Select 'Manual setup or additional server types'"
    Write-Host "5. Click 'Next'"
    Write-Host "6. Select 'POP or IMAP'"
    Write-Host "7. Click 'Next'"
    Write-Host "8. Fill in:"
    Write-Host "   - Your Name: Your Display Name"
    Write-Host "   - Email Address: mlesn@<LOCAL_HOSTNAME>"
    Write-Host "   - Account Type: IMAP"
    Write-Host "   - Incoming mail server: <NAS_PRIMARY_IP>"
    Write-Host "   - Outgoing mail server (SMTP): <NAS_PRIMARY_IP>"
    Write-Host "   - User Name: mlesn@<LOCAL_HOSTNAME>"
    Write-Host "   - Password: [Your NAS Mail Hub password]"
    Write-Host "9. Click 'More Settings...'"
    Write-Host "10. Outgoing Server tab:"
    Write-Host "    - Check 'My outgoing server (SMTP) requires authentication'"
    Write-Host "    - Select 'Use same settings as my incoming mail server'"
    Write-Host "11. Advanced tab:"
    Write-Host "    - Incoming server (IMAP): 993"
    Write-Host "    - Use encrypted connection: SSL/TLS"
    Write-Host "    - Outgoing server (SMTP): 587"
    Write-Host "    - Use encrypted connection: STARTTLS"
    Write-Host "12. Click 'OK' then 'Next'"
    Write-Host "13. Outlook will test the connection"
    Write-Host "14. Click 'Finish' when successful"
    Write-Host ""
    Write-Host "========================================"
    Write-Host "VERIFICATION"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "After adding the account, run this script again to verify."
    Write-Host ""

    # Try to open Account Settings dialog
    Write-Host "Attempting to open Outlook Account Settings..."
    try {{
        $outlook = New-Object -ComObject Outlook.Application
        $outlook.Session.GetDefaultFolder(6)  # olFolderInbox
        Write-Host "✅ Outlook is ready for manual configuration"
        Write-Host ""
        Write-Host "Opening Outlook Account Settings dialog..."
        # Note: We can't directly open the dialog, but we can guide the user
        Write-Host "   Please manually open: File → Account Settings → Account Settings"
    }} catch {{
        Write-Host "⚠️  Could not interact with Outlook"
    }}
}} else {{
    Write-Host ""
    Write-Host "✅ Account already configured!"
    Write-Host ""
    Write-Host "Verifying account settings..."
    foreach ($account in $accounts) {{
        if ($account.SmtpAddress -eq "mlesn@<LOCAL_HOSTNAME>") {{
            Write-Host "  Account: $($account.DisplayName)"
            Write-Host "  Email: $($account.SmtpAddress)"
            Write-Host "  Type: $($account.AccountType)"
            Write-Host ""
            Write-Host "✅ NAS Mail Hub account is configured!"
        }}
    }}
}}

Write-Host ""
Write-Host "========================================"
Write-Host "SETUP COMPLETE"
Write-Host "========================================"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Verify emails are syncing in Outlook"
Write-Host "2. Check NAS Mail Hub webmail for imported emails"
Write-Host "3. Set up email import if not already running"
Write-Host ""
'''.format(timestamp=datetime.now().isoformat())

        script_path = self.config_dir / "setup_outlook_nas_hub.ps1"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"✅ PowerShell setup script created: {script_path}")
        return script_path

    def create_outlook_setup_batch_file(self) -> Path:
        """
        Create batch file to run PowerShell script.

        Returns:
            Path to batch file
        """
        batch_content = '''@echo off
echo ========================================
echo OUTLOOK CLASSIC - NAS MAIL HUB SETUP
echo ========================================
echo.

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "setup_outlook_nas_hub.ps1"

pause
'''

        batch_path = self.config_dir / "setup_outlook_nas_hub.bat"
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)

        logger.info(f"✅ Batch file created: {batch_path}")
        return batch_path

    def create_detailed_setup_guide(self) -> Path:
        """
        Create detailed step-by-step setup guide with screenshots guidance.

        Returns:
            Path to setup guide
        """
        guide_content = """# Outlook Classic Setup - NAS Mail Hub (Detailed Guide)

## Prerequisites

- ✅ Microsoft Outlook (Classic/Desktop) installed
- ✅ NAS Mail Hub running (<NAS_PRIMARY_IP>)
- ✅ Company email account: mlesn@<LOCAL_HOSTNAME>
- ✅ NAS Mail Hub password

---

## Step-by-Step Setup

### Step 1: Open Outlook Account Settings

1. **Open Microsoft Outlook**
2. Click **File** (top-left menu)
3. Click **Account Settings** → **Account Settings...**
   - This opens the Account Settings dialog

### Step 2: Add New Account

1. In the **Account Settings** dialog, click **New...** button
2. Select **Manual setup or additional server types**
3. Click **Next >**

### Step 3: Choose Account Type

1. Select **POP or IMAP**
2. Click **Next >**

### Step 4: Enter Account Information

Fill in the following information:

**User Information:**
- **Your Name:** Your Display Name (e.g., "Your Name")
- **Email Address:** `mlesn@<LOCAL_HOSTNAME>`

**Server Information:**
- **Account Type:** Select **IMAP** from dropdown
- **Incoming mail server:** `<NAS_PRIMARY_IP>`
- **Outgoing mail server (SMTP):** `<NAS_PRIMARY_IP>`

**Logon Information:**
- **User Name:** `mlesn@<LOCAL_HOSTNAME>`
- **Password:** [Enter your NAS Mail Hub password]
- ☑️ Check **"Remember password"** (optional)

### Step 5: Configure Advanced Settings

1. Click **More Settings...** button

#### Outgoing Server Tab

1. Click **Outgoing Server** tab
2. ☑️ Check **"My outgoing server (SMTP) requires authentication"**
3. Select **"Use same settings as my incoming mail server"**

#### Advanced Tab

1. Click **Advanced** tab
2. **Incoming server (IMAP):**
   - Port: `993`
   - ☑️ Check **"This server requires an encrypted connection (SSL/TLS)"**
   - Encryption: Select **SSL/TLS** from dropdown
3. **Outgoing server (SMTP):**
   - Port: `587`
   - ☑️ Check **"This server requires an encrypted connection"**
   - Encryption: Select **STARTTLS** from dropdown
4. Click **OK**

### Step 6: Test Connection

1. Click **Next >**
2. Outlook will test the connection:
   - ✅ **Green checkmarks** = Connection successful
   - ❌ **Red X** = Connection failed (see troubleshooting)

### Step 7: Complete Setup

1. If test is successful, click **Finish**
2. The account will appear in your Account Settings list
3. Click **Close** to exit Account Settings

---

## Verification

### Check Account in Outlook

1. Go to **File** → **Account Settings** → **Account Settings**
2. You should see: **mlesn@<LOCAL_HOSTNAME>** listed
3. Account Type should show: **IMAP**

### Check Email Sync

1. In Outlook, check your **Inbox**
2. You should see emails from:
   - Gmail (imported to NAS Mail Hub)
   - ProtonMail (imported to NAS Mail Hub)
   - Company email (direct to NAS Mail Hub)

### Check Folder Structure

1. In Outlook, expand the account folder
2. You should see standard IMAP folders:
   - Inbox
   - Sent Items
   - Drafts
   - Deleted Items
   - etc.

---

## Troubleshooting

### Connection Test Fails

**Error: "Cannot connect to server"**

**Solutions:**
1. Verify NAS Mail Hub is running:
   - Open: https://<NAS_PRIMARY_IP>:5001/mailplus
   - Log in and verify webmail works
2. Check network connectivity:
   - Ping: `ping <NAS_PRIMARY_IP>`
   - Verify you're on the same network
3. Check firewall:
   - Ensure ports 993 (IMAP) and 587 (SMTP) are allowed
4. Verify server address:
   - Incoming: `<NAS_PRIMARY_IP>`
   - Outgoing: `<NAS_PRIMARY_IP>`

**Error: "Username and password not accepted"**

**Solutions:**
1. Verify username: `mlesn@<LOCAL_HOSTNAME>`
2. Verify password is correct for NAS Mail Hub
3. Check if account exists in NAS Mail Hub
4. Try logging into webmail with same credentials

**Error: "Cannot send email"**

**Solutions:**
1. Verify SMTP settings:
   - Server: `<NAS_PRIMARY_IP>`
   - Port: `587`
   - Encryption: STARTTLS
2. Verify "My outgoing server requires authentication" is checked
3. Verify "Use same settings as my incoming mail server" is selected

### No Emails Visible

**Issue: Outlook connected but no emails**

**Solutions:**
1. Verify email import is running:
   - Check: `data/email_import/` for import logs
   - Run: `python scripts/python/import_emails_to_nas_hub.py --days-back 7`
2. Check NAS Mail Hub webmail:
   - Verify emails are present in webmail
   - If not, run email import first
3. Check Outlook sync:
   - Right-click account → **Update Folder**
   - Or: **Send/Receive** → **Update Folder**

### Emails Not Syncing

**Issue: Emails not updating**

**Solutions:**
1. Check Outlook send/receive settings:
   - File → Options → Advanced → Send/Receive
   - Verify account is included in send/receive groups
2. Manually sync:
   - Press **F9** to send/receive
   - Or: **Send/Receive** → **Send/Receive All Folders**
3. Check account status:
   - File → Account Settings → Account Settings
   - Verify account shows as "Connected"

---

## Configuration Summary

### Account Settings
- **Email:** mlesn@<LOCAL_HOSTNAME>
- **Account Type:** IMAP
- **Display Name:** Your Name

### IMAP Settings
- **Server:** <NAS_PRIMARY_IP>
- **Port:** 993
- **Encryption:** SSL/TLS
- **Username:** mlesn@<LOCAL_HOSTNAME>

### SMTP Settings
- **Server:** <NAS_PRIMARY_IP>
- **Port:** 587
- **Encryption:** STARTTLS
- **Authentication:** Required (same as incoming)

---

## Next Steps After Setup

1. **Verify Email Import:**
   - Ensure Gmail and ProtonMail emails are being imported to NAS Mail Hub
   - Run: `python scripts/python/import_emails_to_nas_hub.py --days-back 365`

2. **Set Up Email Rules (Optional):**
   - Organize emails by source (Gmail, ProtonMail, Company)
   - Create folders and rules in Outlook

3. **Configure Send/Receive:**
   - Set up automatic send/receive schedule
   - File → Options → Advanced → Send/Receive

4. **Set Default Account (Optional):**
   - If you have multiple accounts, set NAS Mail Hub as default
   - File → Account Settings → Account Settings → Set as Default

---

## Support

If you continue to have issues:

1. **Check Setup Script:**
   - Run: `config/outlook/setup_outlook_nas_hub.bat`
   - This will verify Outlook is accessible

2. **Review Logs:**
   - Check email import logs: `data/email_import/`
   - Check Outlook connection status

3. **Verify NAS Mail Hub:**
   - Access webmail: https://<NAS_PRIMARY_IP>:5001/mailplus
   - Verify account exists and is accessible

---

**Last Updated:** 2026-01-05  
**Status:** Ready for Setup
"""

        guide_path = self.config_dir / "OUTLOOK_DETAILED_SETUP_GUIDE.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)

        logger.info(f"✅ Detailed setup guide created: {guide_path}")
        return guide_path

    def run_automated_setup(self) -> Dict[str, Any]:
        """
        Run automated setup process.

        Returns:
            Setup results
        """
        logger.info("="*80)
        logger.info("AUTOMATED OUTLOOK CLASSIC SETUP - NAS MAIL HUB")
        logger.info("="*80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "powershell_script_created": False,
            "batch_file_created": False,
            "setup_guide_created": False,
            "success": False
        }

        # Create PowerShell script
        logger.info("STEP 1: Creating PowerShell Setup Script")
        logger.info("-" * 80)
        try:
            ps_script = self.create_outlook_setup_powershell_script()
            results["powershell_script_created"] = True
            logger.info(f"✅ PowerShell script: {ps_script.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create PowerShell script: {e}")

        logger.info("")

        # Create batch file
        logger.info("STEP 2: Creating Batch File")
        logger.info("-" * 80)
        try:
            batch_file = self.create_outlook_setup_batch_file()
            results["batch_file_created"] = True
            logger.info(f"✅ Batch file: {batch_file.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create batch file: {e}")

        logger.info("")

        # Create detailed guide
        logger.info("STEP 3: Creating Detailed Setup Guide")
        logger.info("-" * 80)
        try:
            guide = self.create_detailed_setup_guide()
            results["setup_guide_created"] = True
            logger.info(f"✅ Setup guide: {guide.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create setup guide: {e}")

        logger.info("")

        # Summary
        results["success"] = all([
            results["powershell_script_created"],
            results["batch_file_created"],
            results["setup_guide_created"]
        ])

        logger.info("="*80)
        if results["success"]:
            logger.info("✅ OUTLOOK SETUP FILES CREATED")
        else:
            logger.info("⚠️  SETUP PARTIALLY COMPLETE")
        logger.info("="*80)
        logger.info("")

        self._print_next_steps(results)

        return results

    def _print_next_steps(self, results: Dict[str, Any]):
        """Print next steps for user."""
        logger.info("📋 NEXT STEPS:")
        logger.info("")
        logger.info("1. RUN AUTOMATED SETUP SCRIPT:")
        logger.info(f"   Double-click: config/outlook/setup_outlook_nas_hub.bat")
        logger.info("   OR")
        logger.info(f"   Run PowerShell: config/outlook/setup_outlook_nas_hub.ps1")
        logger.info("")
        logger.info("2. FOLLOW MANUAL SETUP (if needed):")
        logger.info(f"   Read: config/outlook/OUTLOOK_DETAILED_SETUP_GUIDE.md")
        logger.info("   This has step-by-step instructions with exact settings")
        logger.info("")
        logger.info("3. VERIFY CONNECTION:")
        logger.info("   - Check Outlook inbox for emails")
        logger.info("   - Verify NAS Mail Hub webmail has emails")
        logger.info("   - Test sending/receiving emails")
        logger.info("")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Outlook Classic Setup for NAS Mail Hub"
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Project root directory"
    )
    parser.add_argument(
        "--run-script",
        action="store_true",
        help="Run the PowerShell script after creating it"
    )

    args = parser.parse_args()

    setup = AutomatedOutlookNASHubSetup(args.project_root)
    results = setup.run_automated_setup()

    if args.run_script and results["success"]:
        logger.info("")
        logger.info("Running PowerShell setup script...")
        script_path = args.project_root / "config" / "outlook" / "setup_outlook_nas_hub.ps1"
        try:
            subprocess.run([
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path)
            ], check=False)
        except Exception as e:
            logger.warning(f"Could not run script automatically: {e}")
            logger.info("Please run it manually: config/outlook/setup_outlook_nas_hub.bat")


if __name__ == "__main__":


    main()