#!/usr/bin/env python3
"""
Outlook IMAP Configuration Helper

Helps configure Outlook with company IMAP email settings.
Generates configuration instructions and validates settings.

Tags: #OUTLOOK #IMAP #EMAIL #CONFIGURATION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
logger = logging.getLogger("outlook_imap_config_helper")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Load email configuration
config_file = project_root / "config" / "outlook" / "hybrid_email_config.json"

def load_email_config() -> Dict[str, Any]:
    """Load email configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration: {e}")
        return {}

def print_imap_settings(config: Dict[str, Any]) -> None:
    """Print IMAP settings in a user-friendly format"""
    nas_config = config.get("nas_mail_hub", {})
    imap = nas_config.get("imap", {})
    smtp = nas_config.get("smtp", {})
    accounts = nas_config.get("accounts", {})

    print("\n" + "=" * 80)
    print("📧 OUTLOOK IMAP CONFIGURATION SETTINGS")
    print("=" * 80)
    print()

    # Get first account (or default)
    account_key = list(accounts.keys())[0] if accounts else "mlesn"
    account = accounts.get(account_key, {})

    print("📥 INCOMING MAIL SERVER (IMAP):")
    print(f"   Server: {imap.get('server', 'N/A')}")
    print(f"   Port: {imap.get('port', 'N/A')}")
    print(f"   Encryption: {imap.get('encryption', 'N/A')}")
    print(f"   Username: {account.get('email', 'N/A')}")
    print(f"   Password: [Your NAS Mail Hub password]")
    print()

    print("📤 OUTGOING MAIL SERVER (SMTP):")
    print(f"   Server: {smtp.get('server', 'N/A')}")
    print(f"   Port: {smtp.get('port', 'N/A')}")
    print(f"   Encryption: {smtp.get('encryption', 'N/A')}")
    print(f"   Username: {account.get('email', 'N/A')}")
    print(f"   Password: [Your NAS Mail Hub password]")
    print()

    print("=" * 80)
    print()

def generate_outlook_config_script() -> str:
    """Generate PowerShell script to configure Outlook via registry (advanced)"""
    config = load_email_config()
    nas_config = config.get("nas_mail_hub", {})
    imap = nas_config.get("imap", {})
    smtp = nas_config.get("smtp", {})
    accounts = nas_config.get("accounts", {})

    account_key = list(accounts.keys())[0] if accounts else "mlesn"
    account = accounts.get(account_key, {})
    email = account.get("email", "")

    script = f"""# Outlook IMAP Configuration Script
# This script helps configure Outlook IMAP settings
# Run this in PowerShell (as Administrator if needed)

Write-Host "📧 Outlook IMAP Configuration Helper" -ForegroundColor Cyan
Write-Host ""

# Configuration values
$imapServer = "{imap.get('server', '')}"
$imapPort = {imap.get('port', 993)}
$smtpServer = "{smtp.get('server', '')}"
$smtpPort = {smtp.get('port', 587)}
$emailAddress = "{email}"

Write-Host "IMAP Server: $imapServer:$imapPort" -ForegroundColor Green
Write-Host "SMTP Server: $smtpServer:$smtpPort" -ForegroundColor Green
Write-Host "Email: $emailAddress" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Note: This script shows configuration values." -ForegroundColor Yellow
Write-Host "   You still need to configure Outlook manually using these settings." -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Steps to configure Outlook:" -ForegroundColor Cyan
Write-Host "   1. Open Outlook" -ForegroundColor White
Write-Host "   2. File → Account Settings → Account Settings" -ForegroundColor White
Write-Host "   3. Click 'New...'" -ForegroundColor White
Write-Host "   4. Select 'Manual setup or additional server types'" -ForegroundColor White
Write-Host "   5. Select 'POP or IMAP'" -ForegroundColor White
Write-Host "   6. Enter the settings shown above" -ForegroundColor White
Write-Host ""
"""
    return script

def validate_network_connectivity(server: str, port: int) -> bool:
    """Test network connectivity to mail server"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"⚠️  Could not test connectivity: {e}")
        return False

def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Outlook IMAP Configuration Helper")
        parser.add_argument("--show-settings", action="store_true", help="Show IMAP/SMTP settings")
        parser.add_argument("--test-connection", action="store_true", help="Test connection to mail server")
        parser.add_argument("--generate-script", action="store_true", help="Generate PowerShell configuration script")

        args = parser.parse_args()

        config = load_email_config()

        if not config:
            print("❌ Could not load email configuration")
            return

        if args.show_settings or not any([args.show_settings, args.test_connection, args.generate_script]):
            print_imap_settings(config)

        if args.test_connection:
            nas_config = config.get("nas_mail_hub", {})
            imap = nas_config.get("imap", {})
            smtp = nas_config.get("smtp", {})

            print("\n🔍 Testing network connectivity...")
            print()

            imap_server = imap.get("server", "")
            imap_port = imap.get("port", 993)
            smtp_server = smtp.get("server", "")
            smtp_port = smtp.get("port", 587)

            imap_ok = validate_network_connectivity(imap_server, imap_port)
            smtp_ok = validate_network_connectivity(smtp_server, smtp_port)

            print(f"IMAP Server ({imap_server}:{imap_port}): {'✅ Reachable' if imap_ok else '❌ Not reachable'}")
            print(f"SMTP Server ({smtp_server}:{smtp_port}): {'✅ Reachable' if smtp_ok else '❌ Not reachable'}")
            print()

            if not imap_ok or not smtp_ok:
                print("⚠️  Connection test failed. Possible issues:")
                print("   - Server is not running")
                print("   - Firewall is blocking ports")
                print("   - You're not on the same network")
                print("   - Server address is incorrect")

        if args.generate_script:
            script = generate_outlook_config_script()
            script_file = project_root / "scripts" / "powershell" / "outlook_imap_config.ps1"
            script_file.parent.mkdir(parents=True, exist_ok=True)

            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)

            print(f"\n✅ PowerShell script generated: {script_file}")
            print("   Run it with: powershell -ExecutionPolicy Bypass -File <script_path>")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()