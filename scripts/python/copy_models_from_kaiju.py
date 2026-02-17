#!/usr/bin/env python3
"""
Copy Models from Kaiju D Drive
Copy existing models from Kaiju (<NAS_IP>) D drive to localhost
"""

import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KAIJU_IP = "<NAS_IP>"
KAIJU_USER = "mlesn"
KAIJU_MODELS_PATH = "D:\\ollama"  # Or D:\models
LOCAL_MODELS_PATH = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker\\wsl\\data\\ext4.vhdx")  # Docker volume location


def check_kaiju_ssh() -> bool:
    """Check if we can SSH to Kaiju"""
    try:
        result = subprocess.run(
            ["ssh", f"{KAIJU_USER}@{KAIJU_IP}", "echo test"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"SSH check failed: {e}")
        return False


def find_models_on_kaiju() -> Optional[str]:
    """Find models directory on Kaiju D drive"""
    possible_paths = [
        "D:\\ollama",
        "D:\\models",
        "D:\\ollama\\models",
        "D:\\models\\ollama",
    ]

    for path in possible_paths:
        try:
            result = subprocess.run(
                ["ssh", f"{KAIJU_USER}@{KAIJU_IP}", f"Test-Path '{path}'"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "True" in result.stdout:
                logger.info(f"✅ Found models at: {path}")
                return path
        except Exception as e:
            logger.debug(f"Checked {path}: {e}")

    return None


def list_models_on_kaiju(models_path: str) -> list:
    """List models available on Kaiju"""
    logger.info(f"📋 Listing models in {models_path}...")
    try:
        result = subprocess.run(
            ["ssh", f"{KAIJU_USER}@{KAIJU_IP}", f"Get-ChildItem '{models_path}' -Recurse -Filter '*.gguf' | Select-Object -First 20 Name"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            models = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            logger.info(f"   Found {len(models)} model files")
            return models
        else:
            # Try listing directories instead
            result = subprocess.run(
                ["ssh", f"{KAIJU_USER}@{KAIJU_IP}", f"Get-ChildItem '{models_path}' | Select-Object Name"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                items = [line.strip() for line in result.stdout.split('\n') if line.strip() and 'Name' not in line]
                logger.info(f"   Found {len(items)} items")
                return items
    except Exception as e:
        logger.error(f"Error listing models: {e}")

    return []


def copy_models_via_ssh(kaiju_path: str, local_path: Path):
    """Copy models from Kaiju to local using rsync or robocopy"""
    logger.info(f"📥 Copying models from Kaiju {kaiju_path} to {local_path}...")

    # Ensure local path exists
    local_path.mkdir(parents=True, exist_ok=True)

    # Use robocopy for Windows
    try:
        # Map Kaiju path to UNC
        unc_path = f"\\\\{KAIJU_IP}\\D$\\ollama"

        result = subprocess.run(
            ["robocopy", unc_path, str(local_path), "/E", "/COPYALL", "/R:3", "/W:5"],
            capture_output=True,
            text=True,
            timeout=3600
        )

        # Robocopy returns non-zero for success (when files copied)
        if result.returncode < 8:  # 0-7 are success codes
            logger.info("✅ Models copied successfully")
            return True
        else:
            logger.error(f"❌ Robocopy failed: {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"❌ Error copying models: {e}")
        return False


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Copy Models from Kaiju D Drive")
        parser.add_argument(
            "--list",
            action="store_true",
            help="Only list models, don't copy"
        )
        parser.add_argument(
            "--path",
            help="Custom path on Kaiju (default: auto-detect)"
        )

        args = parser.parse_args()

        logger.info("=" * 80)
        logger.info("🔍 FINDING MODELS ON KAIJU D DRIVE")
        logger.info("=" * 80)

        # Check SSH access
        if not check_kaiju_ssh():
            logger.error("❌ Cannot SSH to Kaiju. Check credentials/network.")
            return

        # Find models path
        if args.path:
            models_path = args.path
        else:
            models_path = find_models_on_kaiju()

        if not models_path:
            logger.error("❌ Models not found on Kaiju D drive")
            logger.info("\nTried paths:")
            logger.info("  - D:\\ollama")
            logger.info("  - D:\\models")
            logger.info("  - D:\\ollama\\models")
            return

        # List models
        models = list_models_on_kaiju(models_path)
        if models:
            logger.info("\n📋 Available models:")
            for model in models[:10]:
                logger.info(f"   - {model}")
            if len(models) > 10:
                logger.info(f"   ... and {len(models) - 10} more")

        if args.list:
            return

        # Copy models
        local_path = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker\\wsl\\data")
        if copy_models_via_ssh(models_path, local_path):
            logger.info("\n✅ Models copied successfully!")
            logger.info("Next: Restart Docker containers to use copied models")
        else:
            logger.error("\n❌ Model copy failed")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()