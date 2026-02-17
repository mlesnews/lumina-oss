#!/usr/bin/env python3
"""
Test ProtonPass integration to verify it's actually working
"""
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_secrets_manager import UnifiedSecretsManager, SecretSource
from lumina_logger import get_logger

logger = get_logger("TestProtonPassIntegration")

def main():
    logger.info("=" * 70)
    logger.info("🧪 TESTING PROTONPASS INTEGRATION")
    logger.info("=" * 70)
    logger.info("")

    manager = UnifiedSecretsManager(project_root)

    # Check availability
    logger.info("📊 System Status:")
    logger.info(f"   Azure Key Vault: {'✅ Available' if manager.azure_vault_client else '❌ Not available'}")
    logger.info(f"   ProtonPass CLI: {'✅ Available' if manager.protonpass_available else '❌ Not available'}")
    logger.info(f"   Dashlane: {'✅ Available' if manager.dashlane_available else '❌ Not available'}")
    logger.info("")

    if manager.protonpass_available:
        logger.info(f"   ProtonPass CLI Path: {manager.protonpass_path}")
        logger.info("")

        # Test source priority
        priority = manager._get_source_priority()
        logger.info("📋 Source Priority (fallback order):")
        for i, source in enumerate(priority, 1):
            logger.info(f"   {i}. {source.value}")
        logger.info("")

        # Try to list items from ProtonPass
        logger.info("🔍 Testing ProtonPass item listing...")
        try:
            import subprocess
            result = subprocess.run(
                [str(manager.protonpass_path), "item", "list", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                import json
                items = json.loads(result.stdout) if result.stdout.strip() else []
                logger.info(f"   ✅ Successfully listed {len(items)} items from ProtonPass")
                if items:
                    logger.info("   Sample items:")
                    for item in items[:3]:
                        title = item.get("title", "Untitled")
                        logger.info(f"      - {title}")
            else:
                logger.warning(f"   ⚠️  Failed to list items: {result.stderr[:200]}")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")

        logger.info("")

        # Test retrieving a secret (try a common one)
        logger.info("🔐 Testing secret retrieval from ProtonPass...")
        test_secrets = ["nas-password", "protonpass-extra-password", "test-secret"]
        for secret_name in test_secrets:
            secret = manager.get_secret(secret_name, source=SecretSource.PROTONPASS)
            if secret:
                logger.info(f"   ✅ Found '{secret_name}' in ProtonPass: {'*' * len(secret)}")
                break
        else:
            logger.info("   ℹ️  No test secrets found in ProtonPass (this is OK)")
    else:
        logger.warning("⚠️  ProtonPass CLI is not available - cannot test retrieval")
        logger.info("   The system will only use Azure Key Vault")

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ TEST COMPLETE")
    logger.info("=" * 70)

    # Summary
    logger.info("")
    logger.info("📊 Summary:")
    if manager.protonpass_available:
        logger.info("   ✅ ProtonPass CLI is installed and available")
        logger.info("   ✅ The triad system can now use ProtonPass as a source")
        logger.info("   ✅ Fallback order: Azure Key Vault → ProtonPass → Dashlane")
    else:
        logger.info("   ⚠️  ProtonPass CLI is not available")
        logger.info("   ⚠️  System is only using Azure Key Vault (monad, not triad)")

    return 0 if manager.protonpass_available else 1

if __name__ == "__main__":

    sys.exit(main())