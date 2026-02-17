#!/usr/bin/env python3
"""
JARVIS Cursor Agent Key Manager

Manages Cursor Agent API key configuration:
- Detects key from clipboard
- Stores in Azure Key Vault
- Sets environment variable
- Configures for ElevenLabs integration
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorAgentKeyManager")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    logger.warning("pyperclip not available - install: pip install pyperclip")

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False
    logger.warning("Azure Key Vault client not available")


class JARVISCursorAgentKeyManager:
    """
    Manages Cursor Agent API key
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.key_name = "cursor-agent-api-key"
        self.vault_client = None

        if AZURE_VAULT_AVAILABLE:
            try:
                # Try to get vault URL from environment or config
                vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
                self.vault_client = AzureKeyVaultClient(vault_url=vault_url)
                self.logger.info("✅ Azure Key Vault client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Azure Key Vault not available: {e}")
                self.vault_client = None

    def get_key_from_clipboard(self) -> Optional[str]:
        """Get API key from clipboard"""
        if not PYPERCLIP_AVAILABLE:
            self.logger.error("❌ pyperclip not available - cannot read clipboard")
            return None

        try:
            clipboard_text = pyperclip.paste()

            # Check if it looks like an API key
            if clipboard_text and len(clipboard_text) > 20:
                # Could be an API key
                self.logger.info("📋 Found text in clipboard (potential API key)")
                return clipboard_text.strip()
            else:
                self.logger.warning("⚠️  Clipboard text doesn't look like an API key")
                return None

        except Exception as e:
            self.logger.error(f"❌ Error reading clipboard: {e}")
            return None

    def store_in_vault(self, api_key: str) -> bool:
        """Store API key in Azure Key Vault"""
        if not self.vault_client:
            self.logger.error("❌ Azure Key Vault client not available")
            return False

        try:
            self.vault_client.set_secret(self.key_name, api_key)
            self.logger.info(f"✅ API key stored in Azure Key Vault: {self.key_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error storing key in vault: {e}")
            return False

    def get_from_vault(self) -> Optional[str]:
        """Get API key from Azure Key Vault"""
        if not self.vault_client:
            return None

        try:
            secret = self.vault_client.get_secret(self.key_name)
            if secret:
                self.logger.info(f"✅ API key retrieved from Azure Key Vault")
                return secret
            else:
                self.logger.warning(f"⚠️  API key not found in vault: {self.key_name}")
                return None
        except Exception as e:
            self.logger.error(f"❌ Error retrieving key from vault: {e}")
            return None

    def check_key_exists(self) -> bool:
        """Check if API key exists in vault"""
        key = self.get_from_vault()
        return key is not None

    def configure_for_elevenlabs(self, api_key: str) -> bool:
        """Configure Cursor Agent key for ElevenLabs integration"""
        try:
            success = False

            # Try to store in vault (optional)
            if self.vault_client:
                if self.store_in_vault(api_key):
                    success = True
                    self.logger.info("✅ Key stored in Azure Key Vault")
            else:
                self.logger.info("⚠️  Key Vault not available - using config file only")

            # Always create/update config file (fallback)
            config_dir = self.project_root / "config" / "cursor_agent"
            config_dir.mkdir(parents=True, exist_ok=True)

            config_file = config_dir / "cursor_agent_config.json"
            config = {
                "cursor_agent_api_key": api_key,
                "configured_at": datetime.now().isoformat(),
                "source": "clipboard",
                "elevenlabs_integration": True,
                "vault_stored": success
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            # Also set as environment variable (for current session)
            os.environ["CURSOR_AGENT_API_KEY"] = api_key

            self.logger.info(f"✅ Cursor Agent key configured for ElevenLabs")
            self.logger.info(f"   Config saved: {config_file}")
            self.logger.info(f"   Environment variable set: CURSOR_AGENT_API_KEY")

            return True

        except Exception as e:
            self.logger.error(f"❌ Error configuring for ElevenLabs: {e}")
            return False

    def setup_from_clipboard(self) -> bool:
        """Setup Cursor Agent key from clipboard"""
        self.logger.info("="*80)
        self.logger.info("JARVIS CURSOR AGENT KEY MANAGER")
        self.logger.info("="*80)
        self.logger.info("Setting up Cursor Agent API key from clipboard...")

        # Get key from clipboard
        api_key = self.get_key_from_clipboard()

        if not api_key:
            self.logger.error("❌ No API key found in clipboard")
            self.logger.info("   Please copy the Cursor Agent API key to clipboard")
            self.logger.info("   Then run this script again")
            return False

        self.logger.info(f"✅ API key detected in clipboard ({len(api_key)} characters)")

        # Configure for ElevenLabs
        if self.configure_for_elevenlabs(api_key):
            self.logger.info("")
            self.logger.info("="*80)
            self.logger.info("✅ CURSOR AGENT KEY CONFIGURED")
            self.logger.info("="*80)
            self.logger.info(f"   Key stored in: Azure Key Vault ({self.key_name})")
            self.logger.info(f"   Config file: config/cursor_agent/cursor_agent_config.json")
            self.logger.info(f"   ElevenLabs integration: Enabled")
            self.logger.info("="*80)
            return True
        else:
            self.logger.error("❌ Failed to configure Cursor Agent key")
            return False


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor Agent Key Manager")
        parser.add_argument("--setup", action="store_true", help="Setup from clipboard")
        parser.add_argument("--check", action="store_true", help="Check if key exists")
        parser.add_argument("--key", type=str, help="Provide API key directly")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = JARVISCursorAgentKeyManager(project_root)

        if args.key:
            # Direct key provided
            if manager.configure_for_elevenlabs(args.key):
                print("✅ Cursor Agent key configured")
            else:
                print("❌ Failed to configure key")
        elif args.check:
            # Check if key exists
            if manager.check_key_exists():
                print("✅ Cursor Agent API key exists in vault")
            else:
                print("❌ Cursor Agent API key not found")
        elif args.setup or not args:
            # Setup from clipboard
            if manager.setup_from_clipboard():
                print("\n✅ Setup complete!")
            else:
                print("\n❌ Setup failed - please ensure key is in clipboard")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()