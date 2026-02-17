#!/usr/bin/env python3
"""
Configure Azure AI Foundry Project Endpoint
                    -LUM THE MODERN

Configures Azure AI Foundry project endpoint in Key Vault or config file.
Supports both interactive and automated configuration.

Tags: #CONFIGURATION #AZURE #AI_FOUNDRY #ENDPOINT @LUMINA
"""

import sys
from pathlib import Path
from typing import Optional
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("ConfigureEndpoint")


class AzureFoundryEndpointConfigurator:
    """Configure Azure AI Foundry project endpoint"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.config_file = self.config_dir / "azure_ai_foundry_config.json"

        logger.info("=" * 80)
        logger.info("🔧 AZURE AI FOUNDRY ENDPOINT CONFIGURATION")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

    def validate_endpoint_format(self, endpoint: str) -> bool:
        """Validate endpoint format"""
        if not endpoint.startswith("https://"):
            logger.error("❌ Endpoint must start with https://")
            return False

        if "/api/projects/" not in endpoint:
            logger.error("❌ Endpoint must contain /api/projects/")
            return False

        if not endpoint.endswith("/") and not endpoint.split("/")[-1]:
            logger.warning("⚠️  Endpoint should end with / or project name")

        return True

    def configure_in_key_vault(self, endpoint: str) -> bool:
        """Configure endpoint in Azure Key Vault"""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential

            key_vault_url = "https://jarvis-lumina.vault.azure.net/"
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            key_vault_client = SecretClient(vault_url=key_vault_url, credential=credential)

            # Set secret
            key_vault_client.set_secret("azure-ai-foundry-project-endpoint", endpoint)

            logger.info(f"✅ Endpoint configured in Key Vault: {key_vault_url}")
            logger.info(f"   Secret name: azure-ai-foundry-project-endpoint")
            return True

        except Exception as e:
            logger.error(f"❌ Key Vault configuration failed: {e}")
            return False

    def configure_in_config_file(self, endpoint: str) -> bool:
        """Configure endpoint in config file"""
        try:
            # Load existing config
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
            else:
                config = {}

            # Update config
            if "azure_ai_foundry" not in config:
                config["azure_ai_foundry"] = {}

            config["azure_ai_foundry"]["project_endpoint"] = endpoint

            # Save config
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Endpoint configured in config file: {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Config file update failed: {e}")
            return False

    def configure(self, endpoint: str, use_key_vault: bool = True, use_config: bool = True) -> bool:
        """Configure endpoint in Key Vault and/or config file"""
        # Validate format
        if not self.validate_endpoint_format(endpoint):
            return False

        success = True

        # Configure in Key Vault
        if use_key_vault:
            if not self.configure_in_key_vault(endpoint):
                success = False

        # Configure in config file
        if use_config:
            if not self.configure_in_config_file(endpoint):
                success = False

        if success:
            logger.info("\n✅ Endpoint configuration complete!")
            logger.info(f"   Endpoint: {endpoint}")
            logger.info("   Ready for production deployment")

        return success

    def get_endpoint_from_user(self) -> Optional[str]:
        """Get endpoint from user input"""
        print("\n" + "=" * 80)
        print("Azure AI Foundry Project Endpoint Configuration")
        print("=" * 80)
        print("\nEnter your Azure AI Foundry project endpoint.")
        print("Format: https://<account>.services.ai.azure.com/api/projects/<project-name>")
        print("\nYou can find this in:")
        print("  - Azure Portal → AI Foundry → Your Project → Overview")
        print("  - Or in the project settings")
        print("\n" + "-" * 80)

        endpoint = input("\nProject Endpoint: ").strip()

        if not endpoint:
            logger.warning("⚠️  No endpoint provided")
            return None

        return endpoint


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure Azure AI Foundry Project Endpoint")
    parser.add_argument("--endpoint", type=str, help="Project endpoint URL")
    parser.add_argument("--key-vault-only", action="store_true", help="Configure only in Key Vault")
    parser.add_argument("--config-only", action="store_true", help="Configure only in config file")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    configurator = AzureFoundryEndpointConfigurator()

    # Get endpoint
    if args.endpoint:
        endpoint = args.endpoint
    elif args.interactive:
        endpoint = configurator.get_endpoint_from_user()
        if not endpoint:
            return 1
    else:
        logger.error("❌ No endpoint provided. Use --endpoint or --interactive")
        return 1

    # Configure
    use_key_vault = not args.config_only
    use_config = not args.key_vault_only

    success = configurator.configure(endpoint, use_key_vault, use_config)

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())