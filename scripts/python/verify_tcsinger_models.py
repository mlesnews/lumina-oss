#!/usr/bin/env python3
"""
Verify TCSinger Models

Verifies that all TCSinger model files are present and ready for use.
Can be run automatically after downloads complete.

Tags: #TCSINGER #VERIFY #MODELS #REQUIRED @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("VerifyTCSinger")


def verify_tcsinger_models() -> bool:
    try:
        """
        Verify all TCSinger models are present

        Returns:
            True if all models are present and ready
        """
        checkpoints_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints"

        required_files = {
            "TCSinger/model_ckpt_steps_200000.ckpt": "TCSinger Acoustic Model",
            "SAD/model_ckpt_steps_80000.ckpt": "Style Adaptive Decoder",
            "SDLM/model_ckpt_steps_120000.ckpt": "Style and Duration Language Model",
            "hifigan/model_ckpt_steps_1000000.ckpt": "HIFI-GAN Neural Vocoder",
        }

        logger.info("=" * 80)
        logger.info("🔍 VERIFYING TCSINGER MODELS")
        logger.info("=" * 80)

        all_present = True
        total_size = 0

        for relative_path, description in required_files.items():
            file_path = checkpoints_dir / relative_path

            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                total_size += file_path.stat().st_size
                logger.info(f"✅ {description}")
                logger.info(f"   {relative_path} - {size_mb:.2f} MB")
            else:
                logger.error(f"❌ {description} - MISSING")
                logger.error(f"   Expected: {file_path}")
                all_present = False

        logger.info("=" * 80)
        if all_present:
            total_size_mb = total_size / (1024 * 1024)
            logger.info(f"✅ ALL MODELS PRESENT")
            logger.info(f"   Total size: {total_size_mb:.2f} MB")
            logger.info("=" * 80)
            logger.info("🎉 TCSINGER READY FOR AI SINGING SYNTHESIS!")
            logger.info("   System will automatically use AI models instead of formant synthesis")
            logger.info("=" * 80)
            return True
        else:
            logger.warning("⚠️  SOME MODELS MISSING")
            logger.warning("   Check IDM for download status")
            logger.info("=" * 80)
            return False


    except Exception as e:
        logger.error(f"Error in verify_tcsinger_models: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    success = verify_tcsinger_models()
    sys.exit(0 if success else 1)
