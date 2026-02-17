#!/usr/bin/env python3
"""
Fix IDM SAD File Location

Moves the SAD model file from IDM temp folder to correct location.

Tags: #TCSINGER #IDM #FIX #REQUIRED @JARVIS @LUMINA
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

logger = get_logger("FixIDMSADFile")


def fix_sad_file():
    """Move SAD file from IDM temp to correct location"""
    source = Path(r"C:\Users\mlesn\AppData\Roaming\IDM\DwnlData\mlesn\model_ckpt_steps_800_20\model_ckpt_steps_800.ckpt")
    dest_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints" / "SAD"
    dest_file = dest_dir / "model_ckpt_steps_80000.ckpt"

    logger.info("=" * 80)
    logger.info("🔧 FIXING IDM SAD FILE LOCATION")
    logger.info("=" * 80)

    if not source.exists():
        logger.error(f"❌ Source file not found: {source}")
        return False

    # Create destination directory (handle if it exists as file)
    if dest_dir.exists() and not dest_dir.is_dir():
        logger.warning(f"⚠️  {dest_dir} exists as file, removing...")
        dest_dir.unlink()
    dest_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Destination directory: {dest_dir}")

    # Copy file
    try:
        logger.info(f"📦 Copying from: {source}")
        logger.info(f"   To: {dest_file}")
        shutil.copy2(str(source), str(dest_file))

        if dest_file.exists():
            size_mb = dest_file.stat().st_size / (1024 * 1024)
            logger.info(f"✅ SAD model file copied successfully!")
            logger.info(f"   Size: {size_mb:.2f} MB")
            logger.info(f"   Location: {dest_file}")
            logger.info("=" * 80)
            return True
        else:
            logger.error("❌ File copy failed - destination file not found")
            return False
    except Exception as e:
        logger.error(f"❌ Error copying file: {e}")
        return False


if __name__ == "__main__":
    success = fix_sad_file()
    sys.exit(0 if success else 1)
