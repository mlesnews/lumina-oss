#!/usr/bin/env python3
"""
SYPHON Configuration Helper

Interactive script to help configure SYPHON systems:
- Email accounts (IMAP, POP3, OAuth2)
- SMS sources (ElevenLabs, backups, N8N)
- Messenger platforms (Telegram, Signal, WhatsApp, Discord, Slack)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class SyphonConfigHelper:
    """Helper for configuring SYPHON systems"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SyphonConfigHelper")

        # Config files
        self.email_config = self.project_root / "config" / "email_accounts.json"
        self.sms_config = self.project_root / "config" / "sms_sources.json"
        self.messenger_config = self.project_root / "config" / "messenger_sources.json"

    def load_config(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration file"""
        if not config_file.exists():
            self.logger.error(f"Config file not found: {config_file}")
            return {}

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}

    def save_config(self, config_file: Path, config: Dict[str, Any]):
        """Save configuration file"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Saved: {config_file}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def print_email_instructions(self):
        """Print email configuration instructions"""
        print("\n" + "=" * 80)
        print("📧 EMAIL SYPHON CONFIGURATION")
        print("=" * 80)
        print("\nConfiguration file: config/email_accounts.json")
        print("\nAccount Types:")
        print("  1. OAuth2 Gmail - Recommended for Gmail accounts")
        print("     - Get OAuth2 credentials from Google Cloud Console")
        print("     - Enable Gmail API")
        print("     - Create OAuth2 client ID and secret")
        print("\n  2. IMAP - For Outlook, Exchange, and other IMAP servers")
        print("     - Use app password for 2FA accounts")
        print("     - Server: outlook.office365.com (Outlook)")
        print("     - Port: 993 (SSL) or 143 (TLS)")
        print("\n  3. POP3 - For legacy email accounts")
        print("     - Less secure, use with caution")
        print("     - Port: 995 (SSL)")
        print("\nSteps:")
        print("  1. Open config/email_accounts.json")
        print("  2. Set 'enabled': true for accounts to SYPHON")
        print("  3. Fill in email address, server, port (for IMAP/POP3)")
        print("  4. Set credentials to null (use environment variables)")
        print("  5. Store credentials securely (not in config file)")
        print("\n⚠️  SECURITY: Never commit credentials to version control!")
        print("=" * 80)

    def print_sms_instructions(self):
        """Print SMS configuration instructions"""
        print("\n" + "=" * 80)
        print("📱 SMS SYPHON CONFIGURATION")
        print("=" * 80)
        print("\nConfiguration file: config/sms_sources.json")
        print("\nSource Types:")
        print("  1. ElevenLabs - Cloud SMS/Voice service")
        print("     - Get API key from ElevenLabs dashboard")
        print("     - URL: https://elevenlabs.io")
        print("\n  2. Android Backup - SMS backup file")
        print("     - Export using SMS Backup & Restore app")
        print("     - Save as XML or JSON")
        print("     - Provide full path to backup file")
        print("\n  3. iOS Backup - SMS database")
        print("     - Extract from iOS backup")
        print("     - Location: Library/SMS/sms.db")
        print("     - Provide full path to database file")
        print("\n  4. N8N Webhook - Via N8N workflow")
        print("     - Configure N8N workflow with SMS webhook")
        print("     - Webhook URL: http://<NAS_PRIMARY_IP>:5678/webhook/syphon/sms")
        print("\nSteps:")
        print("  1. Open config/sms_sources.json")
        print("  2. Set 'enabled': true for sources to SYPHON")
        print("  3. Fill in phone number, credentials, or file paths")
        print("  4. Set API keys to null (use environment variables)")
        print("  5. Store credentials securely")
        print("\n⚠️  SECURITY: Never commit credentials to version control!")
        print("=" * 80)

    def print_messenger_instructions(self):
        """Print messenger configuration instructions"""
        print("\n" + "=" * 80)
        print("💬 MESSENGER SYPHON CONFIGURATION")
        print("=" * 80)
        print("\nConfiguration file: config/messenger_sources.json")
        print("\nPlatforms:")
        print("  1. Telegram")
        print("     - API: Get credentials from https://my.telegram.org/apps")
        print("     - Export: Settings > Advanced > Export Telegram data")
        print("\n  2. Signal")
        print("     - Database location varies by platform")
        print("     - Android: /data/data/org.thoughtcrime.securesms/databases/signal.db")
        print("     - iOS: Requires backup extraction")
        print("\n  3. WhatsApp")
        print("     - Export: Settings > Chats > Chat history > Export chat")
        print("     - Save as .txt file")
        print("\n  4. Discord")
        print("     - Bot: Create bot in Discord Developer Portal")
        print("     - Get bot token and store securely")
        print("     - Export: Use Discord export tools")
        print("\n  5. Slack")
        print("     - API: Create Slack app at https://api.slack.com/apps")
        print("     - Install app to workspace and get bot token")
        print("     - Export: Settings > Import/Export Data > Export")
        print("\nSteps:")
        print("  1. Open config/messenger_sources.json")
        print("  2. Set 'enabled': true for sources to SYPHON")
        print("  3. Fill in API keys, tokens, or export file paths")
        print("  4. Set API keys/tokens to null (use environment variables)")
        print("  5. Store credentials securely")
        print("\n⚠️  SECURITY: Never commit credentials to version control!")
        print("=" * 80)

    def show_config_status(self):
        """Show current configuration status"""
        print("\n" + "=" * 80)
        print("📊 SYPHON CONFIGURATION STATUS")
        print("=" * 80)

        # Email status
        email_config = self.load_config(self.email_config)
        email_accounts = email_config.get("email_accounts", {}).get("accounts", [])
        enabled_emails = [a for a in email_accounts if a.get("enabled", False)]
        print(f"\n📧 Email Accounts: {len(enabled_emails)}/{len(email_accounts)} enabled")

        # SMS status
        sms_config = self.load_config(self.sms_config)
        sms_sources = sms_config.get("sms_sources", {}).get("sources", [])
        enabled_sms = [s for s in sms_sources if s.get("enabled", False)]
        print(f"📱 SMS Sources: {len(enabled_sms)}/{len(sms_sources)} enabled")

        # Messenger status
        messenger_config = self.load_config(self.messenger_config)
        messenger_sources = messenger_config.get("messenger_sources", {}).get("sources", [])
        enabled_messengers = [m for m in messenger_sources if m.get("enabled", False)]
        print(f"💬 Messenger Sources: {len(enabled_messengers)}/{len(messenger_sources)} enabled")

        print("\n" + "=" * 80)

    def interactive_menu(self):
        """Interactive configuration menu"""
        while True:
            print("\n" + "=" * 80)
            print("🔧 SYPHON CONFIGURATION HELPER")
            print("=" * 80)
            print("\n1. Show configuration status")
            print("2. Email configuration instructions")
            print("3. SMS configuration instructions")
            print("4. Messenger configuration instructions")
            print("5. Exit")

            choice = input("\nSelect option (1-5): ").strip()

            if choice == "1":
                self.show_config_status()
            elif choice == "2":
                self.print_email_instructions()
            elif choice == "3":
                self.print_sms_instructions()
            elif choice == "4":
                self.print_messenger_instructions()
            elif choice == "5":
                print("\n✅ Exiting configuration helper")
                break
            else:
                print("\n❌ Invalid option. Please select 1-5.")


def main():
    """Main execution"""
    helper = SyphonConfigHelper()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "status":
            helper.show_config_status()
        elif command == "email":
            helper.print_email_instructions()
        elif command == "sms":
            helper.print_sms_instructions()
        elif command == "messenger":
            helper.print_messenger_instructions()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python configure_syphon_systems.py [status|email|sms|messenger]")
    else:
        helper.interactive_menu()


if __name__ == "__main__":



    main()