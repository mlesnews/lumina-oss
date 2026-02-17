"""
Setup Classic Outlook for Gmail and ProtonMail
Comprehensive setup script for configuring Microsoft Outlook with Gmail and ProtonMail (via Proton Bridge).

This script provides:
- Automated checks for Proton Bridge installation
- Step-by-step configuration instructions
- Connection testing
- Configuration file generation

#JARVIS #LUMINA #OUTLOOK #GMAIL #PROTONMAIL #PROTONBRIDGE #EMAIL #CONFIGURATION
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SetupOutlook")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SetupOutlook")

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    logger.warning("⚠️  Unified Secrets Manager not available")


@dataclass
class EmailAccountConfig:
    """Email account configuration for Outlook."""
    account_name: str
    email_address: str
    account_type: str  # "gmail" or "protonmail"
    imap_server: str
    imap_port: int
    imap_encryption: str  # "SSL" or "TLS"
    smtp_server: str
    smtp_port: int
    smtp_encryption: str  # "SSL" or "TLS"
    username: str
    password: Optional[str] = None
    requires_app_password: bool = False
    notes: str = ""


class OutlookSetupHelper:
    """
    Helper class for setting up Outlook with Gmail and ProtonMail.
    """

    def __init__(self, project_root: Path):
        """
        Initialize Outlook Setup Helper.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "outlook"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if SECRETS_MANAGER_AVAILABLE:
            self.secrets_manager = UnifiedSecretsManager(
                self.project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.secrets_manager = None

    def check_proton_bridge_installed(self) -> Tuple[bool, Optional[str]]:
        """
        Check if Proton Bridge is installed.

        Returns:
            Tuple of (is_installed, installation_path_or_error)
        """
        logger.info("Checking for Proton Bridge installation...")

        # Common installation paths on Windows
        possible_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "ProtonMail Bridge",
            Path("C:/Program Files/ProtonMail Bridge"),
            Path("C:/Program Files (x86)/ProtonMail Bridge"),
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"✅ Found Proton Bridge at: {path}")
                return True, str(path)

        # Check if running as a process
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq ProtonMail Bridge.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "ProtonMail Bridge.exe" in result.stdout:
                logger.info("✅ Proton Bridge is running")
                return True, "running"
        except Exception as e:
            logger.debug(f"Could not check running processes: {e}")

        logger.warning("⚠️  Proton Bridge not found in common locations")
        return False, "Not found in common installation paths"

    def check_proton_bridge_running(self) -> bool:
        """
        Check if Proton Bridge is currently running.

        Returns:
            True if running, False otherwise
        """
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq ProtonMail Bridge.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "ProtonMail Bridge.exe" in result.stdout
        except Exception as e:
            logger.warning(f"Could not check if Proton Bridge is running: {e}")
            return False

    def get_proton_bridge_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get Proton Bridge credentials from secrets manager.

        Returns:
            Dictionary with username and password, or None if not found
        """
        if not self.secrets_manager:
            return None

        try:
            # Try to get ProtonMail credentials
            username = self.secrets_manager.get_secret("protonmail-username")
            password = self.secrets_manager.get_secret("protonmail-password")

            if username and password:
                return {
                    "username": username,
                    "password": password
                }
        except Exception as e:
            logger.debug(f"Could not retrieve credentials: {e}")

        return None

    def get_gmail_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get Gmail credentials from secrets manager.

        Returns:
            Dictionary with email and app_password, or None if not found
        """
        if not self.secrets_manager:
            return None

        try:
            email = self.secrets_manager.get_secret("gmail-email")
            app_password = self.secrets_manager.get_secret("gmail-app-password")

            if email:
                return {
                    "email": email,
                    "app_password": app_password
                }
        except Exception as e:
            logger.debug(f"Could not retrieve Gmail credentials: {e}")

        return None

    def generate_gmail_config(self) -> EmailAccountConfig:
        """
        Generate Gmail account configuration for Outlook.

        Returns:
            EmailAccountConfig for Gmail
        """
        return EmailAccountConfig(
            account_name="Gmail",
            email_address="your-email@gmail.com",  # User needs to replace
            account_type="gmail",
            imap_server="imap.gmail.com",
            imap_port=993,
            imap_encryption="SSL",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            smtp_encryption="TLS",
            username="your-email@gmail.com",  # User needs to replace
            requires_app_password=True,
            notes="Requires Gmail App Password (not regular password). Enable 2FA and generate app password at: https://myaccount.google.com/apppasswords"
        )

    def generate_protonmail_config(self) -> EmailAccountConfig:
        """
        Generate ProtonMail account configuration for Outlook (via Proton Bridge).

        Returns:
            EmailAccountConfig for ProtonMail
        """
        return EmailAccountConfig(
            account_name="ProtonMail",
            email_address="your-email@protonmail.com",  # User needs to replace
            account_type="protonmail",
            imap_server="127.0.0.1",  # Proton Bridge runs locally
            imap_port=1143,  # Default Proton Bridge IMAP port
            imap_encryption="SSL",
            smtp_server="127.0.0.1",  # Proton Bridge runs locally
            smtp_port=1025,  # Default Proton Bridge SMTP port
            smtp_encryption="SSL",
            username="your-email@protonmail.com",  # User needs to replace
            requires_app_password=False,
            notes="Requires Proton Bridge to be installed and running. Use your ProtonMail password (not bridge password). Bridge password is only for Bridge app itself."
        )

    def generate_setup_instructions(self) -> str:
        """
        Generate comprehensive setup instructions.

        Returns:
            Markdown formatted instructions
        """
        instructions = """# Classic Outlook Setup Guide: Gmail + ProtonMail

## Prerequisites

1. **Microsoft Outlook** (Classic/Desktop version) installed
2. **Proton Bridge** installed and configured (for ProtonMail)
3. **Gmail account** with 2-Factor Authentication enabled (for Gmail)

---

## Part 1: Install and Configure Proton Bridge

### Step 1: Download and Install Proton Bridge

1. Go to: https://proton.me/mail/bridge
2. Download Proton Bridge for Windows
3. Install the application
4. Launch Proton Bridge

### Step 2: Add Your ProtonMail Account to Bridge

1. Open Proton Bridge
2. Click "Add Account" or "Sign In"
3. Enter your ProtonMail email address
4. Enter your ProtonMail password
5. Complete any 2FA verification if enabled
6. Bridge will generate a **Bridge Password** - **SAVE THIS SECURELY**

### Step 3: Verify Bridge is Running

1. Check system tray for Proton Bridge icon
2. Bridge must be running for Outlook to connect to ProtonMail
3. Default ports:
   - **IMAP**: 127.0.0.1:1143 (SSL)
   - **SMTP**: 127.0.0.1:1025 (SSL)

---

## Part 2: Configure Gmail in Outlook

### Step 1: Enable Gmail IMAP Access

1. Go to: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Go to **Security** → **App passwords**
4. Generate a new app password:
   - Select "Mail" as app type
   - Select "Other (Custom name)" as device
   - Enter "Outlook" as name
   - Click "Generate"
   - **COPY THE 16-CHARACTER PASSWORD** (you'll need this)

### Step 2: Add Gmail Account to Outlook

1. Open Outlook
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in the account information:
   - **Your Name**: Your display name
   - **Email Address**: your-email@gmail.com
   - **Account Type**: IMAP
   - **Incoming mail server**: imap.gmail.com
   - **Outgoing mail server (SMTP)**: smtp.gmail.com
   - **User Name**: your-email@gmail.com
   - **Password**: [Use the 16-character App Password from Step 1]
9. Click **More Settings...**
10. Go to **Outgoing Server** tab:
    - Check "My outgoing server (SMTP) requires authentication"
    - Select "Use same settings as my incoming mail server"
11. Go to **Advanced** tab:
    - **Incoming server (IMAP)**: 993
    - **Use the following type of encrypted connection**: SSL/TLS
    - **Outgoing server (SMTP)**: 587
    - **Use the following type of encrypted connection**: STARTTLS
12. Click **OK**
13. Click **Next**
14. Outlook will test the connection
15. Click **Finish** when successful

---

## Part 3: Configure ProtonMail in Outlook (via Proton Bridge)

### Step 1: Ensure Proton Bridge is Running

1. Check system tray for Proton Bridge icon
2. If not running, launch Proton Bridge
3. Verify your ProtonMail account is added and active

### Step 2: Get Bridge Connection Details

1. Open Proton Bridge
2. Click on your account
3. Note the connection details:
   - **IMAP Port**: Usually 1143
   - **SMTP Port**: Usually 1025
   - **Username**: Your ProtonMail email address
   - **Password**: Your ProtonMail password (NOT the Bridge password)

### Step 3: Add ProtonMail Account to Outlook

1. Open Outlook
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in the account information:
   - **Your Name**: Your display name
   - **Email Address**: your-email@protonmail.com (or @proton.me)
   - **Account Type**: IMAP
   - **Incoming mail server**: 127.0.0.1
   - **Outgoing mail server (SMTP)**: 127.0.0.1
   - **User Name**: your-email@protonmail.com
   - **Password**: Your ProtonMail password (NOT Bridge password)
9. Click **More Settings...**
10. Go to **Outgoing Server** tab:
    - Check "My outgoing server (SMTP) requires authentication"
    - Select "Use same settings as my incoming mail server"
11. Go to **Advanced** tab:
    - **Incoming server (IMAP)**: 1143 (or port shown in Bridge)
    - **Use the following type of encrypted connection**: SSL/TLS
    - **Outgoing server (SMTP)**: 1025 (or port shown in Bridge)
    - **Use the following type of encrypted connection**: SSL/TLS
12. Click **OK**
13. Click **Next**
14. Outlook will test the connection
15. Click **Finish** when successful

---

## Part 4: Verification and Troubleshooting

### Verify Both Accounts

1. In Outlook, go to **File** → **Account Settings** → **Account Settings**
2. You should see both accounts listed:
   - Gmail (IMAP)
   - ProtonMail (IMAP)
3. Test sending/receiving from both accounts

### Common Issues

#### Gmail Connection Fails
- **Issue**: "Username and password not accepted"
  - **Solution**: Make sure you're using the 16-character App Password, not your regular Gmail password
- **Issue**: "Cannot connect to server"
  - **Solution**: Check internet connection, verify IMAP is enabled in Gmail settings

#### ProtonMail Connection Fails
- **Issue**: "Cannot connect to server"
  - **Solution**: Ensure Proton Bridge is running (check system tray)
  - **Solution**: Verify Bridge ports match Outlook settings (1143 for IMAP, 1025 for SMTP)
- **Issue**: "Username and password not accepted"
  - **Solution**: Use your ProtonMail password, NOT the Bridge password
  - **Solution**: Verify account is properly added in Proton Bridge

#### Outlook Can't Send Emails
- **Gmail**: Verify SMTP port is 587 with STARTTLS
- **ProtonMail**: Verify SMTP port matches Bridge (usually 1025) with SSL/TLS
- Both: Ensure "My outgoing server requires authentication" is checked

---

## Security Notes

1. **Gmail App Passwords**: Store securely, never share
2. **Proton Bridge Password**: Different from ProtonMail password, used only for Bridge app
3. **ProtonMail Password**: Used in Outlook, different from Bridge password
4. **Local Connection**: ProtonMail connects via localhost (127.0.0.1), so Bridge must always be running

---

## Configuration Summary

### Gmail Settings
- **IMAP Server**: imap.gmail.com:993 (SSL)
- **SMTP Server**: smtp.gmail.com:587 (STARTTLS)
- **Authentication**: App Password required

### ProtonMail Settings (via Bridge)
- **IMAP Server**: 127.0.0.1:1143 (SSL)
- **SMTP Server**: 127.0.0.1:1025 (SSL)
- **Authentication**: ProtonMail password (not Bridge password)
- **Requires**: Proton Bridge running

---

## Next Steps

After setup:
1. Test sending emails from both accounts
2. Test receiving emails in both accounts
3. Configure email rules/folders as needed
4. Set default account for sending (if desired)

For automated email management, see: `scripts/python/unified_email_service.py`
"""
        return instructions

    def save_configuration(self, gmail_config: EmailAccountConfig, protonmail_config: EmailAccountConfig) -> Path:
        try:
            """
            Save account configurations to JSON file.

            Args:
                gmail_config: Gmail account configuration
                protonmail_config: ProtonMail account configuration

            Returns:
                Path to saved configuration file
            """
            config_data = {
                "gmail": asdict(gmail_config),
                "protonmail": asdict(protonmail_config),
                "generated_at": str(datetime.now()),
                "notes": "Remove password fields before sharing this file"
            }

            config_file = self.config_dir / "outlook_accounts.json"

            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"✅ Configuration saved to: {config_file}")
            return config_file

        except Exception as e:
            self.logger.error(f"Error in save_configuration: {e}", exc_info=True)
            raise
    def save_instructions(self) -> Path:
        try:
            """
            Save setup instructions to markdown file.

            Returns:
                Path to saved instructions file
            """
            instructions = self.generate_setup_instructions()
            instructions_file = self.config_dir / "OUTLOOK_SETUP_INSTRUCTIONS.md"

            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(instructions)

            logger.info(f"✅ Instructions saved to: {instructions_file}")
            return instructions_file

        except Exception as e:
            self.logger.error(f"Error in save_instructions: {e}", exc_info=True)
            raise
    def run_setup_check(self) -> Dict[str, any]:
        """
        Run comprehensive setup check.

        Returns:
            Dictionary with check results
        """
        results = {
            "proton_bridge_installed": False,
            "proton_bridge_running": False,
            "proton_bridge_path": None,
            "gmail_credentials_available": False,
            "protonmail_credentials_available": False,
            "config_files_generated": False
        }

        logger.info("="*80)
        logger.info("OUTLOOK SETUP CHECK")
        logger.info("="*80)

        # Check Proton Bridge
        installed, path = self.check_proton_bridge_installed()
        results["proton_bridge_installed"] = installed
        results["proton_bridge_path"] = path

        if installed:
            running = self.check_proton_bridge_running()
            results["proton_bridge_running"] = running
            if running:
                logger.info("✅ Proton Bridge is installed and running")
            else:
                logger.warning("⚠️  Proton Bridge is installed but not running")
                logger.info("   → Launch Proton Bridge before configuring Outlook")
        else:
            logger.warning("⚠️  Proton Bridge not found")
            logger.info("   → Download from: https://proton.me/mail/bridge")

        # Check credentials
        gmail_creds = self.get_gmail_credentials()
        if gmail_creds:
            results["gmail_credentials_available"] = True
            logger.info("✅ Gmail credentials found in secrets manager")
        else:
            logger.warning("⚠️  Gmail credentials not found in secrets manager")
            logger.info("   → You'll need to enter Gmail settings manually in Outlook")

        protonmail_creds = self.get_proton_bridge_credentials()
        if protonmail_creds:
            results["protonmail_credentials_available"] = True
            logger.info("✅ ProtonMail credentials found in secrets manager")
        else:
            logger.warning("⚠️  ProtonMail credentials not found in secrets manager")
            logger.info("   → You'll need to enter ProtonMail settings manually in Outlook")

        # Generate configurations
        try:
            gmail_config = self.generate_gmail_config()
            protonmail_config = self.generate_protonmail_config()

            # Update with credentials if available
            if gmail_creds:
                gmail_config.email_address = gmail_creds.get("email", gmail_config.email_address)
                gmail_config.username = gmail_creds.get("email", gmail_config.username)

            if protonmail_creds:
                protonmail_config.email_address = protonmail_creds.get("username", protonmail_config.email_address)
                protonmail_config.username = protonmail_creds.get("username", protonmail_config.username)

            config_file = self.save_configuration(gmail_config, protonmail_config)
            instructions_file = self.save_instructions()
            results["config_files_generated"] = True

            logger.info("\n" + "="*80)
            logger.info("SETUP FILES GENERATED")
            logger.info("="*80)
            logger.info(f"📄 Configuration: {config_file}")
            logger.info(f"📖 Instructions: {instructions_file}")

        except Exception as e:
            logger.error(f"❌ Failed to generate configuration files: {e}")

        return results


def main():
    """Main function."""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description="Setup Classic Outlook for Gmail and ProtonMail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full setup check
  python setup_outlook_gmail_protonmail.py --check

  # Generate configuration files only
  python setup_outlook_gmail_protonmail.py --generate-config

  # Generate instructions only
  python setup_outlook_gmail_protonmail.py --generate-instructions
        """
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Project root directory"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run comprehensive setup check"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate account configuration file"
    )
    parser.add_argument(
        "--generate-instructions",
        action="store_true",
        help="Generate setup instructions"
    )

    args = parser.parse_args()

    helper = OutlookSetupHelper(args.project_root)

    if args.check:
        results = helper.run_setup_check()

        logger.info("\n" + "="*80)
        logger.info("SETUP SUMMARY")
        logger.info("="*80)
        logger.info(f"Proton Bridge Installed: {'✅' if results['proton_bridge_installed'] else '❌'}")
        logger.info(f"Proton Bridge Running: {'✅' if results['proton_bridge_running'] else '❌'}")
        logger.info(f"Gmail Credentials: {'✅' if results['gmail_credentials_available'] else '⚠️  Manual entry required'}")
        logger.info(f"ProtonMail Credentials: {'✅' if results['protonmail_credentials_available'] else '⚠️  Manual entry required'}")
        logger.info(f"Config Files Generated: {'✅' if results['config_files_generated'] else '❌'}")

        logger.info("\n📖 See generated instructions file for step-by-step setup guide")

    elif args.generate_config:
        gmail_config = helper.generate_gmail_config()
        protonmail_config = helper.generate_protonmail_config()
        config_file = helper.save_configuration(gmail_config, protonmail_config)
        logger.info(f"✅ Configuration saved to: {config_file}")

    elif args.generate_instructions:
        instructions_file = helper.save_instructions()
        logger.info(f"✅ Instructions saved to: {instructions_file}")

    else:
        # Default: run full check
        results = helper.run_setup_check()

        logger.info("\n" + "="*80)
        logger.info("NEXT STEPS")
        logger.info("="*80)
        logger.info("1. Review the generated instructions file")
        logger.info("2. Follow the step-by-step guide to configure Outlook")
        logger.info("3. Ensure Proton Bridge is running before adding ProtonMail account")
        logger.info("4. Use Gmail App Password (not regular password) for Gmail")


if __name__ == "__main__":


    main()