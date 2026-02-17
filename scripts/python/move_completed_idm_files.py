#!/usr/bin/env python3
"""
Move Completed IDM Files to Correct Location

Finds files that IDM completed but are in wrong location and moves them.

Tags: #TCSINGER #IDM #MOVE #REQUIRED @JARVIS @LUMINA
"""

import sys
import shutil
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

logger = get_logger("MoveIDMFiles")


def find_and_move_completed_files():
    """Find and move completed IDM files"""
    checkpoints_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints"

    target_files = {
        "SAD": {
            "pattern": "80000",
            "filename": "model_ckpt_steps_80000.ckpt",
            "dest": checkpoints_dir / "SAD" / "model_ckpt_steps_80000.ckpt",
            "min_size_mb": 600
        },
        "SDLM": {
            "pattern": "120000",
            "filename": "model_ckpt_steps_120000.ckpt",
            "dest": checkpoints_dir / "SDLM" / "model_ckpt_steps_120000.ckpt",
            "min_size_mb": 2000
        }
    }

    # Search locations
    search_locations = [
        Path.home() / "Downloads",
        Path.home() / "Downloads" / "IDM",
        Path("D:/Downloads"),
        Path("C:/Downloads"),
        Path("D:/IDM Downloads"),
        Path("C:/IDM Downloads"),
        checkpoints_dir,
    ]

    logger.info("=" * 80)
    logger.info("🔍 FINDING COMPLETED IDM FILES")
    logger.info("=" * 80)

    moved_count = 0

    for model_name, info in target_files.items():
        if info["dest"].exists():
            size_mb = info["dest"].stat().st_size / (1024 * 1024)
            logger.info(f"✅ {model_name} already in place: {size_mb:.2f} MB")
            continue

        logger.info(f"🔍 Searching for {model_name}...")
        found = False

        for location in search_locations:
            if not location.exists():
                continue

            try:
                for file_path in location.rglob("*.ckpt"):
                    if info["pattern"] in file_path.name:
                        size_mb = file_path.stat().st_size / (1024 * 1024)

                        if size_mb >= info["min_size_mb"]:
                            logger.info(f"   ✅ Found: {file_path}")
                            logger.info(f"      Size: {size_mb:.2f} MB")

                            # Move to correct location
                            dest_dir = info["dest"].parent
                            dest_dir.mkdir(parents=True, exist_ok=True)

                            logger.info(f"   📦 Moving to: {info['dest']}")
                            shutil.move(str(file_path), str(info["dest"]))

                            logger.info(f"   ✅ {model_name} moved successfully!")
                            moved_count += 1
                            found = True
                            break

                if found:
                    break
            except Exception as e:
                logger.debug(f"   Error searching {location}: {e}")

        if not found:
            logger.warning(f"   ⚠️  {model_name} not found in search locations")

    logger.info("=" * 80)
    if moved_count == len(target_files):
        logger.info("✅ ALL FILES MOVED SUCCESSFULLY!")
        return True
    else:
        logger.warning(f"⚠️  Moved {moved_count}/{len(target_files)} files")
        return False


if __name__ == "__main__":
    success = find_and_move_completed_files()
    sys.exit(0 if success else 1)
