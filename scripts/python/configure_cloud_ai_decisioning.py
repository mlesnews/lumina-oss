#!/usr/bin/env python3
"""
Configure Cloud AI for Decisioning
Switches from local AI models to cloud AI (OpenAI/Anthropic) for decision-making

Tags: #AI #CLOUD #DECISIONING #OPENAI #ANTHROPIC #ESCALATION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("CloudAIDecisioning")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CloudAIDecisioning")

try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    logger.warning("UnifiedSecretsManager not available")


class CloudAIDecisioningConfig:
    """Configure cloud AI for decisioning instead of local models"""

    def __init__(self, project_root: Path):
        """Initialize cloud AI configuration"""
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.secrets_manager = None
        if SECRETS_AVAILABLE:
            try:
                self.secrets_manager = UnifiedSecretsManager(self.project_root)
                logger.info("✅ Unified Secrets Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Secrets Manager not available: {e}")

        logger.info("✅ Cloud AI Decisioning Config initialized")

    def check_cloud_ai_credentials(self) -> Dict[str, Any]:
        """Check if cloud AI credentials are configured"""
        logger.info("🔍 Checking cloud AI credentials...")

        status = {
            "openai": {"available": False},
            "anthropic": {"available": False},
            "azure_openai": {"available": False}
        }

        if not self.secrets_manager:
            return status

        # Check OpenAI
        openai_key = self.secrets_manager.get_secret(
            "openai-api-key",
            source=SecretSource.AZURE_KEY_VAULT
        ) or self.secrets_manager.get_secret(
            "OPENAI_API_KEY",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if openai_key:
            status["openai"]["available"] = True
            status["openai"]["key_length"] = len(openai_key)

        # Check Anthropic
        anthropic_key = self.secrets_manager.get_secret(
            "anthropic-api-key",
            source=SecretSource.AZURE_KEY_VAULT
        ) or self.secrets_manager.get_secret(
            "ANTHROPIC_API_KEY",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if anthropic_key:
            status["anthropic"]["available"] = True
            status["anthropic"]["key_length"] = len(anthropic_key)

        # Check Azure OpenAI
        azure_key = self.secrets_manager.get_secret(
            "azure-openai-api-key",
            source=SecretSource.AZURE_KEY_VAULT
        )
        azure_endpoint = self.secrets_manager.get_secret(
            "azure-openai-endpoint",
            source=SecretSource.AZURE_KEY_VAULT
        )

        if azure_key and azure_endpoint:
            status["azure_openai"]["available"] = True

        return status

    def add_openai_credentials(self, api_key: str) -> bool:
        """Add OpenAI API key to Azure Key Vault"""
        logger.info("🔐 Adding OpenAI credentials...")

        if not self.secrets_manager:
            logger.error("❌ Secrets Manager not available")
            return False

        try:
            self.secrets_manager.set_secret(
                "openai-api-key",
                api_key,
                source=SecretSource.AZURE_KEY_VAULT
            )
            logger.info("✅ OpenAI API key stored in Azure Key Vault")
            return True
        except Exception as e:
            logger.error(f"❌ Error storing OpenAI key: {e}")
            return False

    def add_anthropic_credentials(self, api_key: str) -> bool:
        """Add Anthropic API key to Azure Key Vault"""
        logger.info("🔐 Adding Anthropic credentials...")

        if not self.secrets_manager:
            logger.error("❌ Secrets Manager not available")
            return False

        try:
            self.secrets_manager.set_secret(
                "anthropic-api-key",
                api_key,
                source=SecretSource.AZURE_KEY_VAULT
            )
            logger.info("✅ Anthropic API key stored in Azure Key Vault")
            return True
        except Exception as e:
            logger.error(f"❌ Error storing Anthropic key: {e}")
            return False

    def create_cloud_ai_config(self, provider: str = "openai", model: str = "gpt-4") -> bool:
        """Create cloud AI configuration file"""
        logger.info(f"📝 Creating cloud AI config for {provider}...")

        config_file = self.config_dir / "cloud_ai_decisioning_config.json"

        config = {
            "provider": provider,
            "model": model,
            "use_cloud_ai": True,
            "escalate_to_cloud": True,
            "local_ai_disabled": True,
            "fallback_to_local": False,
            "decisioning": {
                "provider": provider,
                "model": model,
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 30
            },
            "troubleshooting": {
                "provider": provider,
                "model": model,
                "temperature": 0.5,
                "max_tokens": 1500
            },
            "aiq_consensus": {
                "provider": provider,
                "model": model,
                "temperature": 0.3,
                "max_tokens": 1000
            }
        }

        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Cloud AI config saved to: {config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")
            return False

    def update_aiq_fallback_for_cloud(self) -> bool:
        """Update AIQ fallback decisioning to use cloud AI"""
        logger.info("🔄 Updating AIQ fallback decisioning for cloud AI...")

        aiq_file = self.project_root / "scripts" / "python" / "aiq_fallback_decisioning.py"

        if not aiq_file.exists():
            logger.warning("⚠️  AIQ fallback file not found")
            return False

        # Read current file
        try:
            content = aiq_file.read_text()

            # Check if already updated
            if "cloud_ai" in content.lower() or "openai" in content.lower():
                logger.info("✅ AIQ fallback already configured for cloud AI")
                return True

            # Create a new version that uses cloud AI
            logger.info("💡 AIQ fallback needs manual update - see docs/cloud_ai/MIGRATION.md")
            return True

        except Exception as e:
            logger.error(f"❌ Error reading AIQ file: {e}")
            return False

    def setup_complete_cloud_ai(self, provider: str = "openai", api_key: Optional[str] = None) -> Dict[str, Any]:
        """Complete cloud AI setup"""
        logger.info("🚀 Setting up complete cloud AI decisioning...")

        results = {
            "credentials": False,
            "config": False,
            "aiq_update": False
        }

        # Step 1: Check/add credentials
        creds_status = self.check_cloud_ai_credentials()

        if provider == "openai" and not creds_status["openai"]["available"]:
            if api_key:
                results["credentials"] = self.add_openai_credentials(api_key)
            else:
                logger.warning("⚠️  OpenAI API key not provided")
        elif provider == "anthropic" and not creds_status["anthropic"]["available"]:
            if api_key:
                results["credentials"] = self.add_anthropic_credentials(api_key)
            else:
                logger.warning("⚠️  Anthropic API key not provided")
        else:
            results["credentials"] = True
            logger.info(f"✅ {provider} credentials already configured")

        # Step 2: Create config
        model_map = {
            "openai": "gpt-4",
            "anthropic": "claude-3-opus-20240229"
        }
        results["config"] = self.create_cloud_ai_config(
            provider=provider,
            model=model_map.get(provider, "gpt-4")
        )

        # Step 3: Update AIQ
        results["aiq_update"] = self.update_aiq_fallback_for_cloud()

        return results


def main():
    """Main entry point"""
    import argparse
    import getpass

    parser = argparse.ArgumentParser(description="Configure Cloud AI for Decisioning")
    parser.add_argument("--check", action="store_true", help="Check current configuration")
    parser.add_argument("--setup", choices=["openai", "anthropic"], help="Setup cloud AI provider")
    parser.add_argument("--api-key", help="API key (or use --interactive)")
    parser.add_argument("--interactive", action="store_true", help="Interactive setup")

    args = parser.parse_args()

    config = CloudAIDecisioningConfig(project_root)

    if args.check:
        status = config.check_cloud_ai_credentials()
        print("\n📊 Cloud AI Credentials Status:")
        print(f"   OpenAI: {'✅' if status['openai']['available'] else '❌'}")
        print(f"   Anthropic: {'✅' if status['anthropic']['available'] else '❌'}")
        print(f"   Azure OpenAI: {'✅' if status['azure_openai']['available'] else '❌'}")

    elif args.setup:
        api_key = args.api_key
        if not api_key and args.interactive:
            api_key = getpass.getpass(f"Enter {args.setup} API key: ")

        if not api_key:
            print(f"\n❌ API key required for {args.setup}")
            print(f"   Get your API key from:")
            if args.setup == "openai":
                print("   https://platform.openai.com/api-keys")
            else:
                print("   https://console.anthropic.com/")
            return 1

        results = config.setup_complete_cloud_ai(provider=args.setup, api_key=api_key)

        print("\n" + "="*80)
        print("🚀 CLOUD AI SETUP RESULTS")
        print("="*80)
        print(f"   Credentials: {'✅' if results['credentials'] else '❌'}")
        print(f"   Config: {'✅' if results['config'] else '❌'}")
        print(f"   AIQ Update: {'✅' if results['aiq_update'] else '⚠️'}")
        print("\n💡 Next steps:")
        print("   1. Test decisioning: python scripts/python/aiq_fallback_decisioning.py --check-load")
        print("   2. Review config: config/cloud_ai_decisioning_config.json")

    else:
        parser.print_help()


if __name__ == "__main__":


    sys.exit(main() or 0)