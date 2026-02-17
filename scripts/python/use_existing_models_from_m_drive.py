#!/usr/bin/env python3
"""
Use Existing Models from M Drive
Configure Docker containers to use models already on M drive instead of pulling
"""

import subprocess
import logging
import json
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker" / "homelab-local-ai" / "docker-compose.yml"


def find_models_on_m_drive() -> Optional[Path]:
    try:
        """Find Ollama models on M drive"""
        possible_paths = [
            Path("M:\\ollama"),
            Path("M:\\models"),
            Path("M:\\ollama\\models"),
            Path("M:\\models\\ollama"),
            Path("M:\\ai\\models"),
            Path("M:\\ai\\ollama"),
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"✅ Found models at: {path}")
                return path

        logger.warning("⚠️  Models not found on M drive")
        return None


    except Exception as e:
        logger.error(f"Error in find_models_on_m_drive: {e}", exc_info=True)
        raise
def update_docker_compose_volumes(models_path: Path):
    try:
        """Update docker-compose.yml to mount M drive models"""
        logger.info(f"📝 Updating docker-compose.yml to use models from {models_path}")

        # Read current docker-compose.yml
        with open(DOCKER_COMPOSE_FILE, 'r') as f:
            content = f.read()

        # Convert Windows path to Docker volume mount format
        # M:\ollama -> /mnt/m/ollama (or use Windows path directly)
        windows_path = str(models_path).replace('\\', '/')

        # Update volume definitions
        # Replace named volumes with bind mounts
        updated_content = content.replace(
            "- ollama-models:/root/.ollama",
            f"- {windows_path}:/root/.ollama"
        ).replace(
            "- ollama-data:/root/.ollama/models",
            f"- {windows_path}:/root/.ollama/models"
        ).replace(
            "- iron-legion-models:/root/.ollama",
            f"- {windows_path}:/root/.ollama"
        )

        # Remove volume definitions at bottom (or keep them as fallback)
        # For now, we'll keep them but comment them out

        # Write updated file
        backup_file = DOCKER_COMPOSE_FILE.with_suffix('.yml.backup')
        with open(backup_file, 'w') as f:
            f.write(content)
        logger.info(f"💾 Backup saved to: {backup_file}")

        with open(DOCKER_COMPOSE_FILE, 'w') as f:
            f.write(updated_content)

        logger.info("✅ docker-compose.yml updated")


    except Exception as e:
        logger.error(f"Error in update_docker_compose_volumes: {e}", exc_info=True)
        raise
def verify_models_in_path(models_path: Path) -> bool:
    """Verify models exist in the path"""
    logger.info(f"🔍 Checking for models in {models_path}")

    # Look for model files/directories
    model_indicators = [
        "blobs",  # Ollama stores models in blobs directory
        "manifests",  # Model manifests
        "models",  # Models directory
    ]

    found = False
    for indicator in model_indicators:
        check_path = models_path / indicator
        if check_path.exists():
            logger.info(f"   ✅ Found {indicator}")
            found = True

    if not found:
        logger.warning(f"   ⚠️  No model indicators found in {models_path}")
        logger.info(f"   Checking contents...")
        try:
            items = list(models_path.iterdir())[:10]
            for item in items:
                logger.info(f"      - {item.name}")
        except Exception as e:
            logger.error(f"   ❌ Error reading directory: {e}")

    return found


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Use Existing Models from M Drive")
        parser.add_argument(
            "--path",
            help="Custom path to models (default: auto-detect on M drive)"
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Only verify models exist, don't update docker-compose"
        )

        args = parser.parse_args()

        logger.info("=" * 80)
        logger.info("🔍 FINDING MODELS ON M DRIVE")
        logger.info("=" * 80)

        # Find models path
        if args.path:
            models_path = Path(args.path)
        else:
            models_path = find_models_on_m_drive()

        if not models_path:
            logger.error("❌ Models not found. Please specify path with --path")
            logger.info("\nPossible locations:")
            logger.info("  - M:\\ollama")
            logger.info("  - M:\\models")
            logger.info("  - M:\\ollama\\models")
            return

        # Verify models exist
        if not verify_models_in_path(models_path):
            logger.warning("⚠️  Models may not be in expected format")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return

        if args.verify:
            logger.info("✅ Verification complete")
            return

        # Update docker-compose.yml
        update_docker_compose_volumes(models_path)

        logger.info("\n" + "=" * 80)
        logger.info("✅ CONFIGURATION UPDATED")
        logger.info("=" * 80)
        logger.info("\nNext steps:")
        logger.info("1. Restart containers: docker-compose down && docker-compose up -d")
        logger.info("2. Verify models: docker exec homelab-ollama ollama list")
        logger.info("3. No need to pull models - they're already on M drive!")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()