#!/usr/bin/env python3
"""
IDM Download Monitor

Monitors Internet Download Manager (IDM) downloads and detects when files are complete.
Automatically verifies file integrity and notifies when downloads finish.

Tags: #IDM #DOWNLOAD #MONITOR #AUTOMATION #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
import json

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

logger = get_logger("IDMDownloadMonitor")


class IDMDownloadMonitor:
    """
    Monitor IDM downloads and detect completion
    """

    def __init__(self):
        """Initialize download monitor"""
        self.monitored_files: Dict[str, Dict] = {}
        self.completed_files: Set[str] = set()

    def add_file_to_monitor(self, file_path: Path, expected_size: Optional[int] = None, description: str = ""):
        """
        Add a file to monitor for download completion

        Args:
            file_path: Path to the file being downloaded
            expected_size: Expected file size in bytes (optional)
            description: Description of the file
        """
        file_str = str(file_path)
        self.monitored_files[file_str] = {
            "path": file_path,
            "expected_size": expected_size,
            "description": description,
            "last_size": 0,
            "stable_count": 0,
            "completed": False
        }
        logger.info(f"📋 Monitoring: {description or file_path.name}")
        logger.info(f"   Path: {file_path}")
        if expected_size:
            logger.info(f"   Expected size: {expected_size / (1024*1024):.2f} MB")

    def check_download_status(self, file_path: Path) -> Dict[str, any]:
        try:
            """
            Check the status of a download

            Returns:
                Dict with status information
            """
            file_str = str(file_path)
            if file_str not in self.monitored_files:
                return {"monitored": False}

            info = self.monitored_files[file_str]
            path = info["path"]

            if not path.exists():
                return {
                    "monitored": True,
                    "exists": False,
                    "completed": False,
                    "size": 0
                }

            current_size = path.stat().st_size
            expected_size = info["expected_size"]

            # Check if file size is stable (not changing)
            if current_size == info["last_size"]:
                info["stable_count"] += 1
            else:
                info["stable_count"] = 0
                info["last_size"] = current_size

            # Consider complete if:
            # 1. File exists
            # 2. Size is stable for 3+ checks (30+ seconds)
            # 3. If expected size provided, matches expected size
            is_complete = (
                path.exists() and
                info["stable_count"] >= 3 and
                (expected_size is None or abs(current_size - expected_size) < 1024)  # Within 1KB tolerance
            )

            if is_complete and not info["completed"]:
                info["completed"] = True
                self.completed_files.add(file_str)
                logger.info("=" * 80)
                logger.info(f"✅ DOWNLOAD COMPLETE: {info['description'] or path.name}")
                logger.info(f"   Path: {path}")
                logger.info(f"   Size: {current_size / (1024*1024):.2f} MB")
                logger.info("=" * 80)

            return {
                "monitored": True,
                "exists": True,
                "completed": is_complete,
                "size": current_size,
                "expected_size": expected_size,
                "progress": (current_size / expected_size * 100) if expected_size else None,
                "stable": info["stable_count"] >= 3
            }

        except Exception as e:
            self.logger.error(f"Error in check_download_status: {e}", exc_info=True)
            raise
    def monitor_all(self, check_interval: float = 10.0, max_checks: Optional[int] = None) -> bool:
        try:
            """
            Monitor all files until completion

            Args:
                check_interval: Seconds between checks
                max_checks: Maximum number of checks (None = unlimited)

            Returns:
                True if all files completed, False if timeout
            """
            logger.info("=" * 80)
            logger.info("🔍 STARTING IDM DOWNLOAD MONITOR")
            logger.info("=" * 80)
            logger.info(f"   Monitoring {len(self.monitored_files)} file(s)")
            logger.info(f"   Check interval: {check_interval}s")
            logger.info("=" * 80)

            check_count = 0
            while True:
                check_count += 1
                if max_checks and check_count > max_checks:
                    logger.warning("⚠️  Maximum checks reached")
                    return False

                all_complete = True
                for file_str, info in self.monitored_files.items():
                    if info["completed"]:
                        continue

                    status = self.check_download_status(info["path"])
                    all_complete = False

                    if status["exists"]:
                        progress_str = ""
                        if status["progress"] is not None:
                            progress_str = f" ({status['progress']:.1f}%)"
                        stable_str = " [STABLE]" if status["stable"] else ""
                        logger.info(f"📊 {info['description'] or Path(file_str).name}: {status['size']/(1024*1024):.2f} MB{progress_str}{stable_str}")

                if all_complete:
                    logger.info("=" * 80)
                    logger.info("✅ ALL DOWNLOADS COMPLETE")
                    logger.info("=" * 80)
                    return True

                time.sleep(check_interval)

        except Exception as e:
            self.logger.error(f"Error in monitor_all: {e}", exc_info=True)
            raise
    def get_completion_summary(self) -> Dict:
        """Get summary of completed downloads"""
        return {
            "total": len(self.monitored_files),
            "completed": len(self.completed_files),
            "pending": len(self.monitored_files) - len(self.completed_files),
            "files": {
                file_str: {
                    "description": info["description"],
                    "path": str(info["path"]),
                    "completed": info["completed"]
                }
                for file_str, info in self.monitored_files.items()
            }
        }


def monitor_tcsinger_downloads():
    try:
        """Monitor TCSinger model downloads"""
        monitor = IDMDownloadMonitor()

        checkpoints_dir = project_root / "models" / "singing_synthesis" / "TCSinger" / "checkpoints"

        # Expected file sizes (approximate, in bytes)
        expected_sizes = {
            "TCSinger/model_ckpt_steps_200000.ckpt": 500 * 1024 * 1024,  # ~500 MB
            "SAD/model_ckpt_steps_80000.ckpt": 700 * 1024 * 1024,  # ~700 MB
            "SDLM/model_ckpt_steps_120000.ckpt": 2500 * 1024 * 1024,  # ~2.5 GB
            "hifigan/model_ckpt_steps_1000000.ckpt": 100 * 1024 * 1024,  # ~100 MB
        }

        # Add files to monitor
        for relative_path, expected_size in expected_sizes.items():
            file_path = checkpoints_dir / relative_path
            description = f"TCSinger: {Path(relative_path).parent.name} Model"
            monitor.add_file_to_monitor(file_path, expected_size, description)

        # Monitor until complete
        success = monitor.monitor_all(check_interval=10.0)

        if success:
            logger.info("🎉 All TCSinger models downloaded successfully!")
            logger.info("   System is ready to use AI singing synthesis!")
            return True
        else:
            logger.warning("⚠️  Some downloads may still be in progress")
            logger.warning("   Check IDM manually or run monitor again")
            return False


    except Exception as e:
        logger.error(f"Error in monitor_tcsinger_downloads: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Monitor IDM downloads")
    parser.add_argument("--tcsinger", action="store_true", help="Monitor TCSinger downloads")
    args = parser.parse_args()

    if args.tcsinger:
        monitor_tcsinger_downloads()
    else:
        logger.info("Use --tcsinger to monitor TCSinger model downloads")
