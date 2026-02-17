#!/usr/bin/env python3
"""
Find Missing TCSinger Models

Searches for SAD and SDLM model files that may have been downloaded to different locations.

Tags: #TCSINGER #FIND #MODELS #REQUIRED @JARVIS @LUMINA
"""

import sys
from pathlib import Path
import os

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FindTCSingerModels")


def find_model_files():
    """Search for missing TCSinger model files"""
    checkpoints_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints"

    # Files we're looking for
    target_files = {
        "SAD": "model_ckpt_steps_80000.ckpt",
        "SDLM": "model_ckpt_steps_120000.ckpt"
    }

    # Search locations
    search_locations = [
        Path.home() / "Downloads",
        Path("D:/Downloads"),
        Path("C:/Downloads"),
        checkpoints_dir,
        project_root / "models" / "singing_synthesis",
    ]

    logger.info("=" * 80)
    logger.info("🔍 SEARCHING FOR MISSING TCSINGER MODELS")
    logger.info("=" * 80)

    found_files = {}

    for location in search_locations:
        if not location.exists():
            continue

        logger.info(f"Searching: {location}")

        try:
            # Search for files matching our target names
            for file_path in location.rglob("*.ckpt"):
                file_name = file_path.name

                # Check if this matches SAD or SDLM
                for model_name, target_name in target_files.items():
                    if target_name in file_name or model_name in file_name:
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        if model_name not in found_files:
                            found_files[model_name] = []
                        found_files[model_name].append({
                            "path": file_path,
                            "size_mb": size_mb
                        })
                        logger.info(f"   ✅ Found {model_name}: {file_path} ({size_mb:.2f} MB)")
        except Exception as e:
            logger.debug(f"   Error searching {location}: {e}")

    logger.info("=" * 80)

    # Report findings
    if found_files:
        logger.info("📋 FOUND FILES:")
        for model_name, files in found_files.items():
            logger.info(f"   {model_name}:")
            for file_info in files:
                logger.info(f"      {file_info['path']} ({file_info['size_mb']:.2f} MB)")

        # Check if they're in the right place
        logger.info("")
        logger.info("📋 VERIFICATION:")
        for model_name, target_name in target_files.items():
            expected_path = checkpoints_dir / model_name / target_name
            if expected_path.exists():
                logger.info(f"   ✅ {model_name} is in correct location")
            else:
                logger.warning(f"   ⚠️  {model_name} needs to be moved to: {expected_path}")
                if model_name in found_files:
                    logger.info(f"      Found at: {found_files[model_name][0]['path']}")
    else:
        logger.warning("❌ No SAD or SDLM files found")
        logger.warning("   They may still be downloading in IDM")
        logger.warning("   Check IDM download queue")

    logger.info("=" * 80)

    return found_files


if __name__ == "__main__":
    find_model_files()
