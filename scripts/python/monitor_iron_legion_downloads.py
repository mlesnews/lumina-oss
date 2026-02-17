#!/usr/bin/env python3
"""
Monitor Iron Legion Model Downloads
                    -LUM THE MODERN

Monitors IDM downloads and verifies completion of model files on NAS.

Tags: #IRON_LEGION #IDM #MONITOR #DOWNLOAD @JARVIS @LUMINA @DOIT
"""

import sys
import time
from pathlib import Path
from typing import Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("IronLegionDownloadMonitor")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IronLegionDownloadMonitor")

# NAS path
NAS_MODELS_PATH = Path(r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\models\ollama")

# Expected files
EXPECTED_FILES = {
    "llama3.2:11b": {
        "filename": "llama-3.2-11b-vision-instruct.Q4_K_M.gguf",
        "expected_size_mb": 6500,  # ~6.5 GB
        "node": "Mark II",
        "port": 3002
    },
    "mixtral:8x7b": {
        "filename": "mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "expected_size_mb": 28000,  # ~28 GB
        "node": "Mark VI",
        "port": 3006
    }
}

def check_file_status(model_key: str, file_info: Dict) -> Dict:
    try:
        """Check status of a model file"""
        file_path = NAS_MODELS_PATH / file_info["filename"]

        if not file_path.exists():
            return {
                "exists": False,
                "size_mb": 0,
                "complete": False,
                "progress": 0
            }

        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        expected_mb = file_info["expected_size_mb"]
        progress = min(100, (size_mb / expected_mb) * 100) if expected_mb > 0 else 0
        complete = size_mb >= (expected_mb * 0.95)  # 95% threshold

        return {
            "exists": True,
            "size_mb": size_mb,
            "expected_mb": expected_mb,
            "complete": complete,
            "progress": progress,
            "path": str(file_path)
        }

    except Exception as e:
        logger.error(f"Error in check_file_status: {e}", exc_info=True)
        raise
def monitor_downloads(check_interval: int = 30, max_checks: Optional[int] = None) -> bool:
    """
    Monitor downloads until completion

    Args:
        check_interval: Seconds between checks
        max_checks: Maximum number of checks (None = unlimited)

    Returns:
        True if all downloads complete
    """
    logger.info("=" * 80)
    logger.info("🔍 MONITORING IRON LEGION MODEL DOWNLOADS")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)
    logger.info(f"   NAS Path: {NAS_MODELS_PATH}")
    logger.info(f"   Check Interval: {check_interval}s")
    logger.info("=" * 80)

    check_count = 0
    all_complete = False

    while not all_complete:
        check_count += 1
        if max_checks and check_count > max_checks:
            logger.warning("⚠️  Maximum checks reached")
            break

        logger.info(f"\n📊 Check #{check_count} - {time.strftime('%H:%M:%S')}")
        all_complete = True

        for model_key, file_info in EXPECTED_FILES.items():
            status = check_file_status(model_key, file_info)

            if status["exists"]:
                size_str = f"{status['size_mb']:.1f} MB"
                progress_str = f"({status['progress']:.1f}%)" if status['progress'] < 100 else ""
                complete_str = " ✅ COMPLETE" if status["complete"] else ""

                logger.info(f"   {file_info['node']} ({model_key}): {size_str} {progress_str}{complete_str}")

                if not status["complete"]:
                    all_complete = False
            else:
                logger.info(f"   {file_info['node']} ({model_key}): ⏳ Not started")
                all_complete = False

        if all_complete:
            logger.info("\n" + "=" * 80)
            logger.info("✅ ALL DOWNLOADS COMPLETE")
            logger.info("=" * 80)

            # Verify all files
            logger.info("\n📋 File Verification:")
            for model_key, file_info in EXPECTED_FILES.items():
                status = check_file_status(model_key, file_info)
                if status["complete"]:
                    logger.info(f"   ✅ {file_info['node']}: {status['size_mb']:.1f} MB - Ready")
                else:
                    logger.warning(f"   ⚠️  {file_info['node']}: {status['size_mb']:.1f} MB - Incomplete")

            return True

        if not all_complete:
            logger.info(f"\n⏳ Waiting {check_interval}s before next check...")
            time.sleep(check_interval)

    return all_complete

def get_download_summary() -> Dict:
    """Get summary of download status"""
    summary = {
        "total": len(EXPECTED_FILES),
        "complete": 0,
        "in_progress": 0,
        "not_started": 0,
        "files": {}
    }

    for model_key, file_info in EXPECTED_FILES.items():
        status = check_file_status(model_key, file_info)
        summary["files"][model_key] = status

        if status["complete"]:
            summary["complete"] += 1
        elif status["exists"]:
            summary["in_progress"] += 1
        else:
            summary["not_started"] += 1

    return summary

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Iron Legion model downloads")
    parser.add_argument("--check", action="store_true", help="Single check and exit")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--max-checks", type=int, help="Maximum number of checks")
    args = parser.parse_args()

    if args.check:
        # Single check
        logger.info("=" * 80)
        logger.info("📊 DOWNLOAD STATUS CHECK")
        logger.info("=" * 80)

        summary = get_download_summary()

        for model_key, file_info in EXPECTED_FILES.items():
            status = summary["files"][model_key]
            node = file_info["node"]

            if status["complete"]:
                logger.info(f"   ✅ {node}: {status['size_mb']:.1f} MB - Complete")
            elif status["exists"]:
                logger.info(f"   ⏳ {node}: {status['size_mb']:.1f} MB ({status['progress']:.1f}%) - In Progress")
            else:
                logger.info(f"   ⏸️  {node}: Not started")

        logger.info("")
        logger.info(f"   Complete: {summary['complete']}/{summary['total']}")
        logger.info(f"   In Progress: {summary['in_progress']}")
        logger.info(f"   Not Started: {summary['not_started']}")
        logger.info("=" * 80)

        return 0 if summary["complete"] == summary["total"] else 1
    else:
        # Continuous monitoring
        success = monitor_downloads(args.interval, args.max_checks)
        return 0 if success else 1

if __name__ == "__main__":


    sys.exit(main())