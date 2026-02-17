#!/usr/bin/env python3
"""
Setup GitHub Personal Access Token from Azure Key Vault
Loads the token from Azure Key Vault and sets it as an environment variable

Tags: #SECURITY #GITHUB #KEYVAULT @JARVIS @LUMINA
"""
import sys
import os
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from lumina_logger import get_logger
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

logger = get_logger("SetupGitHubToken")


def setup_github_token():
    """Load GitHub token from Azure Key Vault and set as environment variable"""
    logger.info("=" * 70)
    logger.info("🔐 SETTING UP GITHUB PERSONAL ACCESS TOKEN")
    logger.info("=" * 70)
    logger.info("")

    manager = UnifiedSecretsManager(project_root)

    # Try to get token from Azure Key Vault
    secret_name = "github-personal-access-token"
    logger.info(f"🔍 Retrieving '{secret_name}' from Azure Key Vault...")

    token = manager.get_secret(secret_name)

    if not token:
        logger.warning(f"⚠️  Secret '{secret_name}' not found in Azure Key Vault")
        logger.info("")
        logger.info("💡 To store the token in Azure Key Vault:")
        logger.info(f"   python scripts/python/add_secret_to_vault.py {secret_name}")
        logger.info("")
        logger.info("⚠️  IMPORTANT: If you have an exposed GitHub token, it should be:")
        logger.info("   1. Revoked immediately on GitHub (Settings > Developer > Tokens)")
        logger.info("   2. Replaced with a new fine-grained token")
        logger.info("   3. Stored securely: az keyvault secret set --vault-name jarvis-lumina --name github-token --value <NEW>")
        return False

    # Set as environment variable
    os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = token
    logger.info(f"✅ GitHub token loaded and set as environment variable")
    logger.info(f"   Token length: {len(token)} characters")
    logger.info(f"   Token prefix: {token[:7]}...")
    logger.info("")
    logger.info("✅ Environment variable GITHUB_PERSONAL_ACCESS_TOKEN is now set")
    logger.info("   This will be available for the MCP GitHub server")
    logger.info("")

    return True


def main():
    success = setup_github_token()
    return 0 if success else 1


if __name__ == "__main__":

    sys.exit(main())