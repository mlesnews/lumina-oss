#!/usr/bin/env python3
"""
Actively Find and Move TCSinger Models

Searches for SAD and SDLM files and moves them to the correct location.
Runs continuously until files are found and moved.

Tags: #TCSINGER #FIND #MOVE #ACTIVE #REQUIRED @JARVIS @LUMINA
"""

import sys
import shutil
import time
from pathlib import Path

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

logger = get_logger("FindMoveTCSinger")


def find_and_move_models():
    """Actively search for and move missing models"""
    checkpoints_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints"

    target_files = {
        "SAD": {
            "filename": "model_ckpt_steps_80000.ckpt",
            "expected_size_mb": 700,
            "dest": checkpoints_dir / "SAD" / "model_ckpt_steps_80000.ckpt"
        },
        "SDLM": {
            "filename": "model_ckpt_steps_120000.ckpt",
            "expected_size_mb": 2500,
            "dest": checkpoints_dir / "SDLM" / "model_ckpt_steps_120000.ckpt"
        }
    }

    logger.info("=" * 80)
    logger.info("🔍 ACTIVELY SEARCHING FOR TCSINGER MODELS")
    logger.info("=" * 80)

    # Search locations (prioritize common download locations)
    search_locations = [
        Path.home() / "Downloads",
        Path("D:/Downloads"),
        Path("C:/Downloads"),
        checkpoints_dir,
        project_root / "models" / "singing_synthesis",
        Path("C:/Users/mlesn/Dropbox"),
    ]

    found_count = 0

    for model_name, info in target_files.items():
        if info["dest"].exists():
            size_mb = info["dest"].stat().st_size / (1024 * 1024)
            logger.info(f"✅ {model_name} already in place: {size_mb:.2f} MB")
            found_count += 1
            continue

        logger.info(f"🔍 Searching for {model_name}...")

        # Search for files matching the pattern
        for location in search_locations:
            if not location.exists():
                continue

            try:
                # Search for files with matching name or size
                for file_path in location.rglob("*.ckpt"):
                    file_name = file_path.name
                    size_mb = file_path.stat().st_size / (1024 * 1024)

                    # Check if this matches our target
                    if (info["filename"] in file_name or 
                        model_name in file_name or
                        ("80000" in file_name and model_name == "SAD") or
                        ("120000" in file_name and model_name == "SDLM")):

                        # Check if size is reasonable (within 50% of expected)
                        if abs(size_mb - info["expected_size_mb"]) < info["expected_size_mb"] * 0.5:
                            logger.info(f"   ✅ Found {model_name} at: {file_path}")
                            logger.info(f"      Size: {size_mb:.2f} MB")

                            # Move to correct location
                            dest_dir = info["dest"].parent
                            dest_dir.mkdir(parents=True, exist_ok=True)

                            logger.info(f"   📦 Moving to: {info['dest']}")
                            shutil.move(str(file_path), str(info["dest"]))

                            logger.info(f"   ✅ {model_name} moved successfully!")
                            found_count += 1
                            break
            except Exception as e:
                logger.debug(f"   Error searching {location}: {e}")

    logger.info("=" * 80)
    if found_count == len(target_files):
        logger.info("✅ ALL MODELS FOUND AND MOVED!")
        return True
    else:
        logger.warning(f"⚠️  Found {found_count}/{len(target_files)} models")
        return False


if __name__ == "__main__":
    success = find_and_move_models()
    sys.exit(0 if success else 1)
