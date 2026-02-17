#!/usr/bin/env python3
"""
Monitor TCSinger Downloads and Proceed Automatically

Monitors IDM downloads, verifies completion, and automatically proceeds with testing
when all models are ready.

Tags: #TCSINGER #MONITOR #AUTOMATION #REQUIRED @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("MonitorTCSinger")

from verify_tcsinger_models import verify_tcsinger_models
from idm_download_monitor import IDMDownloadMonitor


def monitor_and_proceed(check_interval=10, max_wait_minutes=120):
    try:
        """
        Monitor downloads and proceed when complete - ACTIVE MONITORING

        Args:
            check_interval: Seconds between checks
            max_wait_minutes: Maximum minutes to wait
        """
        checkpoints_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints"

        logger.info("=" * 80)
        logger.info("🔍 ACTIVE MONITORING: TCSINGER DOWNLOADS")
        logger.info("=" * 80)
        logger.info("   Continuously checking for completion...")
        logger.info(f"   Check interval: {check_interval}s")
        logger.info(f"   Max wait: {max_wait_minutes} minutes")
        logger.info("=" * 80)

        # Expected file sizes (approximate)
        required_files = {
            "SAD/model_ckpt_steps_80000.ckpt": 700 * 1024 * 1024,  # ~700 MB
            "SDLM/model_ckpt_steps_120000.ckpt": 2500 * 1024 * 1024,  # ~2.5 GB
        }

        max_checks = (max_wait_minutes * 60) // check_interval
        check_count = 0

        while check_count < max_checks:
            check_count += 1
            logger.info(f"📊 Check {check_count}/{max_checks}...")

            all_complete = True
            for relative_path, expected_size in required_files.items():
                file_path = checkpoints_dir / relative_path

                if file_path.exists():
                    current_size = file_path.stat().st_size
                    size_mb = current_size / (1024 * 1024)

                    # Check if file is complete (within 1MB of expected, or stable size)
                    if abs(current_size - expected_size) < 1024 * 1024 or current_size > expected_size * 0.9:
                        logger.info(f"   ✅ {Path(relative_path).parent.name}: {size_mb:.2f} MB - COMPLETE")
                    else:
                        progress = (current_size / expected_size * 100) if expected_size else 0
                        logger.info(f"   📥 {Path(relative_path).parent.name}: {size_mb:.2f} MB ({progress:.1f}%) - DOWNLOADING")
                        all_complete = False
                else:
                    logger.info(f"   ⏳ {Path(relative_path).parent.name}: Waiting for download...")
                    all_complete = False

            if all_complete:
                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ ALL DOWNLOADS COMPLETE - VERIFYING MODELS")
                logger.info("=" * 80)

                # Verify all models
                if verify_tcsinger_models():
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info("🎉 READY TO TEST AI SINGING SYNTHESIS")
                    logger.info("=" * 80)
                    logger.info("   All TCSinger models are present and verified")
                    logger.info("   System will now use AI singing instead of formant synthesis")
                    logger.info("=" * 80)
                    logger.info("")
                    logger.info("🚀 PROCEEDING TO TEST DANNY BOY DUET WITH AI SINGING...")
                    logger.info("=" * 80)

                    # Proceed with testing
                    return proceed_with_testing()
                else:
                    logger.warning("⚠️  Verification failed - some models may be incomplete")
                    time.sleep(check_interval)
                    continue

            # Wait before next check
            time.sleep(check_interval)

        logger.warning("⚠️  Monitoring timeout - check IDM manually")
        return False


    except Exception as e:
        logger.error(f"Error in monitor_and_proceed: {e}", exc_info=True)
        raise
def proceed_with_testing():
    """Proceed with testing AI singing synthesis"""
    import subprocess

    logger.info("🎵 Starting Danny Boy duet test with AI singing synthesis...")
    logger.info("")

    try:
        # Run the duet test
        script_path = script_dir / "jarvis_danny_boy_duet.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            logger.info("✅ Duet test completed successfully")
            return True
        else:
            logger.warning(f"⚠️  Duet test exited with code {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"❌ Error running duet test: {e}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Monitor TCSinger downloads and proceed")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")
    parser.add_argument("--max-wait", type=int, default=120, help="Max wait time in minutes (default: 120)")
    parser.add_argument("--continuous", action="store_true", help="Run continuously until complete")
    args = parser.parse_args()

    if args.continuous:
        # Run until complete, no timeout
        logger.info("🔄 Running in continuous mode (no timeout)")
        while True:
            if monitor_and_proceed(check_interval=args.interval, max_wait_minutes=999999):
                break
            logger.info("   Waiting 30s before retry...")
            time.sleep(30)
    else:
        success = monitor_and_proceed(check_interval=args.interval, max_wait_minutes=args.max_wait)
        sys.exit(0 if success else 1)
