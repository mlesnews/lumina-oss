#!/usr/bin/env python3
"""
Copy Kaiju Models to Local Docker Volume
Copy models from Kaiju D drive to local Docker volume for faster access
"""

import subprocess
import logging
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KAIJU_MODELS = "\\\\<NAS_IP>\\D$\\ollama\\models"
LOCAL_DOCKER_VOLUME = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker\\wsl\\data")
LOCAL_MODELS = LOCAL_DOCKER_VOLUME / "ollama" / "models"


def copy_models_robocopy() -> bool:
    """Copy models using robocopy"""
    logger.info(f"📥 Copying models from {KAIJU_MODELS} to {LOCAL_MODELS}...")

    LOCAL_MODELS.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                "robocopy",
                KAIJU_MODELS,
                str(LOCAL_MODELS),
                "/E",  # Copy subdirectories
                "/COPYALL",  # Copy all file info
                "/R:3",  # Retry 3 times
                "/W:5",  # Wait 5 seconds between retries
                "/NP",  # No progress
                "/NFL",  # No file list
                "/NDL",  # No directory list
            ],
            capture_output=True,
            text=True,
            timeout=7200  # 2 hours max
        )

        # Robocopy returns 0-7 for success
        if result.returncode < 8:
            logger.info("✅ Models copied successfully")
            return True
        else:
            logger.error(f"❌ Robocopy failed: {result.returncode}")
            logger.error(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        logger.warning("⏱️  Copy timeout (may still be running)")
        return False
    except Exception as e:
        logger.error(f"❌ Error copying models: {e}")
        return False


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("📥 COPYING MODELS FROM KAIJU TO LOCAL")
    logger.info("=" * 80)

    if copy_models_robocopy():
        logger.info("\n✅ Models copied! Next:")
        logger.info("1. Restart containers: docker-compose up -d")
        logger.info("2. Verify: docker exec homelab-ollama ollama list")
    else:
        logger.error("\n❌ Copy failed. Check network/credentials.")


if __name__ == "__main__":


    main()