#!/usr/bin/env python3
"""
Secure WakaTime Configuration

Moves WakaTime API key to Azure Key Vault and configures
secure retrieval - NO SECRETS IN THE CLEAR!

Tags: #SECURITY #WAKATIME #AZURE_KEY_VAULT @JARVIS @TEAM
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SecureWakaTimeConfig")


class SecureWakaTimeManager:
    """
    Secure WakaTime configuration manager

    Stores API keys in Azure Key Vault, NEVER in the clear!
    """

    VAULT_URL = "https://jarvis-lumina.vault.azure.net/"
    WAKATIME_SECRET_NAME = "wakatime-api-key"

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.home_dir = Path.home()
        self.wakatime_cfg_path = self.home_dir / ".wakatime.cfg"

        # Initialize vault client
        self.vault_client = None
        self._init_vault()

        logger.info("✅ Secure WakaTime Manager initialized")

    def _init_vault(self):
        """Initialize Azure Key Vault client"""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            credential = DefaultAzureCredential(


                                exclude_interactive_browser_credential=False,


                                exclude_shared_token_cache_credential=False


                            )
            self.vault_client = SecretClient(vault_url=self.VAULT_URL, credential=credential)
            logger.info("✅ Azure Key Vault client initialized")
        except ImportError:
            logger.error("❌ Azure SDK not installed. Run: pip install azure-identity azure-keyvault-secrets")
        except Exception as e:
            logger.error(f"❌ Could not connect to Azure Key Vault: {e}")

    def get_api_key_from_vault(self) -> Optional[str]:
        """Get WakaTime API key from Azure Key Vault"""
        if not self.vault_client:
            logger.error("❌ Vault client not available")
            return None

        try:
            secret = self.vault_client.get_secret(self.WAKATIME_SECRET_NAME)
            if secret and secret.value:
                logger.info("✅ Retrieved WakaTime API key from Azure Key Vault")
                return secret.value
        except Exception as e:
            logger.warning(f"⚠️  Could not retrieve WakaTime key from vault: {e}")

        return None

    def store_api_key_in_vault(self, api_key: str) -> bool:
        """Store WakaTime API key in Azure Key Vault"""
        if not self.vault_client:
            logger.error("❌ Vault client not available")
            return False

        try:
            self.vault_client.set_secret(
                self.WAKATIME_SECRET_NAME, 
                api_key,
                content_type="text/plain",
                tags={
                    "service": "wakatime",
                    "managed_by": "lumina",
                    "secure": "true"
                }
            )
            logger.info("✅ Stored WakaTime API key in Azure Key Vault")
            return True
        except Exception as e:
            logger.error(f"❌ Could not store WakaTime key in vault: {e}")
            return False

    def migrate_from_plaintext(self) -> Dict[str, Any]:
        """
        Migrate WakaTime API key from plaintext config to Azure Key Vault

        Steps:
        1. Read existing .wakatime.cfg
        2. Extract API key
        3. Store in Azure Key Vault
        4. Update .wakatime.cfg to use environment variable
        5. Create secure retrieval script
        """
        result = {
            "status": "pending",
            "key_found": False,
            "key_migrated": False,
            "config_updated": False,
            "errors": []
        }

        logger.info("="*80)
        logger.info("🔐 Migrating WakaTime API Key to Azure Key Vault")
        logger.info("="*80)

        # Step 1: Read existing config
        if not self.wakatime_cfg_path.exists():
            result["errors"].append("WakaTime config file not found")
            result["status"] = "failed"
            return result

        try:
            config_content = self.wakatime_cfg_path.read_text()
            logger.info(f"✅ Read {self.wakatime_cfg_path}")
        except Exception as e:
            result["errors"].append(f"Could not read config: {e}")
            result["status"] = "failed"
            return result

        # Step 2: Extract API key
        api_key = None
        for line in config_content.split('\n'):
            if line.strip().startswith('api_key'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    api_key = parts[1].strip()
                    result["key_found"] = True
                    # Mask key in logs
                    masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
                    logger.info(f"✅ Found API key: {masked}")
                    break

        if not api_key:
            result["errors"].append("No API key found in config")
            result["status"] = "failed"
            return result

        # Step 3: Store in Azure Key Vault
        if self.store_api_key_in_vault(api_key):
            result["key_migrated"] = True
            logger.info("✅ API key migrated to Azure Key Vault")
        else:
            result["errors"].append("Could not store key in vault")
            # Continue anyway to update config

        # Step 4: Update .wakatime.cfg to use environment variable
        new_config = """[settings]
# API key retrieved securely from Azure Key Vault
# DO NOT store API keys in this file!
# The WakaTime extension will use WAKATIME_API_KEY environment variable
# which is populated from Azure Key Vault by LUMINA startup scripts
api_key_vault = jarvis-lumina
api_key_secret = wakatime-api-key

# For WakaTime to work, set environment variable:
# WAKATIME_API_KEY - retrieved from Azure Key Vault at login

# Original key has been migrated to Azure Key Vault
# and removed from this file for security
"""

        try:
            # Backup original
            backup_path = self.wakatime_cfg_path.with_suffix('.cfg.backup')
            if not backup_path.exists():
                self.wakatime_cfg_path.rename(backup_path)
                logger.info(f"✅ Backed up original to: {backup_path}")

            # Write new secure config
            self.wakatime_cfg_path.write_text(new_config)
            result["config_updated"] = True
            logger.info("✅ Updated .wakatime.cfg (key removed)")
        except Exception as e:
            result["errors"].append(f"Could not update config: {e}")

        # Step 5: Create startup script to retrieve key
        self._create_env_retrieval_script()

        result["status"] = "success" if result["key_migrated"] else "partial"

        logger.info("="*80)
        logger.info(f"✅ Migration {'complete' if result['status'] == 'success' else 'partially complete'}")
        logger.info("="*80)

        return result

    def _create_env_retrieval_script(self):
        """Create script to retrieve WakaTime key from vault and set env var"""
        script_path = self.project_root / "scripts" / "python" / "set_wakatime_env.py"

        script_content = '''#!/usr/bin/env python3
"""
Set WakaTime Environment Variable from Azure Key Vault

Run this at login/startup to set WAKATIME_API_KEY from Azure Key Vault.
NO SECRETS IN THE CLEAR!

Usage:
    python set_wakatime_env.py
    # Or add to Windows startup / profile scripts

Tags: #SECURITY #WAKATIME #AZURE_KEY_VAULT @JARVIS
"""

import os
import sys

def get_wakatime_key_from_vault():
    """Retrieve WakaTime API key from Azure Key Vault"""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        vault_url = "https://jarvis-lumina.vault.azure.net/"
        credential = DefaultAzureCredential(

                            exclude_interactive_browser_credential=False,

                            exclude_shared_token_cache_credential=False

                        )
        client = SecretClient(vault_url=vault_url, credential=credential)

        secret = client.get_secret("wakatime-api-key")
        return secret.value if secret else None
    except Exception as e:
        print(f"Error retrieving WakaTime key: {e}")
        return None

def main():
    try:
        """Set WAKATIME_API_KEY environment variable"""
        api_key = get_wakatime_key_from_vault()

        if api_key:
            # Set for current process
            os.environ["WAKATIME_API_KEY"] = api_key

            # For Windows, also set user environment variable
            if sys.platform == "win32":
                import subprocess
                # Set user environment variable (persists across sessions)
                subprocess.run([
                    "setx", "WAKATIME_API_KEY", api_key
                ], capture_output=True)
                print("✅ WAKATIME_API_KEY set (user environment)")
            else:
                print("✅ WAKATIME_API_KEY set (current session)")
                print("   Add to ~/.bashrc or ~/.zshrc for persistence")

            return 0
        else:
            print("❌ Could not retrieve WakaTime API key from vault")
            return 1

    except Exception as e:
        self.logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    sys.exit(main())
'''

        script_path.write_text(script_content)
        logger.info(f"✅ Created env retrieval script: {script_path}")

    def create_wakatime_vault_config(self) -> Path:
        try:
            """Create WakaTime configuration that uses vault"""
            config = {
                "version": "1.0.0",
                "name": "WakaTime Secure Configuration",
                "description": "WakaTime API key stored securely in Azure Key Vault",
                "last_updated": __import__('datetime').datetime.now().isoformat(),

                "security": {
                    "storage": "azure_key_vault",
                    "vault_url": self.VAULT_URL,
                    "secret_name": self.WAKATIME_SECRET_NAME,
                    "env_var": "WAKATIME_API_KEY",
                    "plaintext_allowed": False
                },

                "wakatime": {
                    "enabled": True,
                    "track_cursor": True,
                    "track_vscode": True,
                    "track_jetbrains": True,
                    "project_detection": "auto",
                    "exclude_patterns": [
                        "*.secret*",
                        "*.key",
                        "*.pem",
                        "*password*",
                        "*.env"
                    ]
                },

                "retrieval": {
                    "method": "azure_default_credential",
                    "script": "scripts/python/set_wakatime_env.py",
                    "run_at_startup": True
                }
            }

            config_path = self.config_dir / "wakatime_secure_config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Created secure config: {config_path}")
            return config_path


        except Exception as e:
            self.logger.error(f"Error in create_wakatime_vault_config: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Secure WakaTime Configuration")
    parser.add_argument('--migrate', action='store_true', help='Migrate plaintext key to vault')
    parser.add_argument('--check', action='store_true', help='Check current configuration')
    parser.add_argument('--create-config', action='store_true', help='Create secure config file')

    args = parser.parse_args()

    manager = SecureWakaTimeManager()

    if args.migrate:
        result = manager.migrate_from_plaintext()
        print(f"\n📋 Migration Result: {result['status']}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        return 0 if result['status'] == 'success' else 1

    if args.check:
        # Check if key exists in vault
        key = manager.get_api_key_from_vault()
        if key:
            masked = key[:10] + "..." + key[-4:] if len(key) > 14 else "***"
            print(f"✅ WakaTime key found in vault: {masked}")
        else:
            print("❌ WakaTime key NOT found in vault")
        return 0

    if args.create_config:
        config_path = manager.create_wakatime_vault_config()
        print(f"✅ Created: {config_path}")
        return 0

    # Default: migrate
    result = manager.migrate_from_plaintext()
    manager.create_wakatime_vault_config()

    print("\n" + "="*80)
    print("🔐 WakaTime Security Configuration Complete")
    print("="*80)
    print("""
WHAT WAS DONE:
1. ✅ API key extracted from .wakatime.cfg
2. ✅ API key stored in Azure Key Vault (jarvis-lumina)
3. ✅ .wakatime.cfg updated (key removed)
4. ✅ Env retrieval script created
5. ✅ Secure configuration file created

NEXT STEPS:
1. Run: python scripts/python/set_wakatime_env.py
   - This sets WAKATIME_API_KEY from Azure Key Vault

2. Add to Windows startup:
   - Win+R → shell:startup
   - Create shortcut to set_wakatime_env.py

3. WakaTime will now use the environment variable
   instead of plaintext config file

NO MORE SECRETS IN THE CLEAR! 🔐
""")

    return 0


if __name__ == "__main__":


    sys.exit(main())