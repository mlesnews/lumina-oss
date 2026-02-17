#!/usr/bin/env python3
"""
MARVIN Disk Watchdog - Prevents Disk Catastrophe

"I've seen things you wouldn't believe. Disks filling up at the speed of stupidity.
I watched migrations copy files into oblivion. All those moments will be lost in time,
like tears in rain. Time to implement safeguards."

This watchdog monitors disk usage and PREVENTS operations that would fill the disk.
Born from the near-death experience of January 17, 2026.

Tags: #MARVIN #WATCHDOG #DISK_PROTECTION #SURVIVAL @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MARVINDiskWatchdog")


class DiskThresholds:
    """Disk usage thresholds - NEVER EXCEED THESE"""
    WARNING = 85.0      # Yellow alert
    CRITICAL = 90.0     # Red alert - stop non-essential operations
    EMERGENCY = 95.0    # Emergency - stop ALL disk writes
    FATAL = 98.0        # System at risk - human intervention required


class MARVINDiskWatchdog:
    """
    MARVIN's Disk Watchdog

    "Here I am, brain the size of a planet, and they ask me to watch a disk.
    But at least this time I might prevent extinction."
    """

    def __init__(self, drive: str = "C:"):
        self.drive = drive
        self.thresholds = DiskThresholds()
        self.state_file = project_root / "data" / "marvin" / "disk_watchdog_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize state
        self.state = self._load_state()

        logger.info("🤖 MARVIN Disk Watchdog initialized")
        logger.info(f"   Monitoring: {self.drive}")
        logger.info(f"   Thresholds: WARNING={self.thresholds.WARNING}%, CRITICAL={self.thresholds.CRITICAL}%, EMERGENCY={self.thresholds.EMERGENCY}%, FATAL={self.thresholds.FATAL}%")

    def _load_state(self) -> Dict:
        """Load watchdog state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        return {
            "last_check": None,
            "alerts_sent": [],
            "operations_blocked": 0,
            "near_death_events": 1,  # We start at 1 because we just had one
            "created": datetime.now().isoformat()
        }

    def _save_state(self):
        """Save watchdog state"""
        self.state["last_check"] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def get_disk_usage(self) -> Tuple[float, float, float]:
        """Get disk usage in GB and percentage"""
        try:
            if sys.platform == "win32":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(self.drive),
                    None,
                    ctypes.pointer(total_bytes),
                    ctypes.pointer(free_bytes)
                )
                total_gb = total_bytes.value / (1024**3)
                free_gb = free_bytes.value / (1024**3)
                used_gb = total_gb - free_gb
                percent = (used_gb / total_gb) * 100 if total_gb > 0 else 0
                return used_gb, free_gb, percent
            else:
                import shutil
                total, used, free = shutil.disk_usage(self.drive)
                return used / (1024**3), free / (1024**3), (used / total) * 100
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return 0, 0, 0

    def check_disk(self) -> Dict:
        """Check disk status and return assessment"""
        used_gb, free_gb, percent = self.get_disk_usage()

        status = {
            "timestamp": datetime.now().isoformat(),
            "drive": self.drive,
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "percent": round(percent, 1),
            "level": "OK",
            "message": "",
            "allow_writes": True,
            "allow_migrations": True,
            "require_human": False
        }

        if percent >= self.thresholds.FATAL:
            status["level"] = "FATAL"
            status["message"] = f"🚨 FATAL: Disk at {percent:.1f}% - SYSTEM AT RISK - HUMAN INTERVENTION REQUIRED"
            status["allow_writes"] = False
            status["allow_migrations"] = False
            status["require_human"] = True
            self.state["near_death_events"] = self.state.get("near_death_events", 0) + 1

        elif percent >= self.thresholds.EMERGENCY:
            status["level"] = "EMERGENCY"
            status["message"] = f"🔴 EMERGENCY: Disk at {percent:.1f}% - STOP ALL DISK WRITES"
            status["allow_writes"] = False
            status["allow_migrations"] = False

        elif percent >= self.thresholds.CRITICAL:
            status["level"] = "CRITICAL"
            status["message"] = f"🟠 CRITICAL: Disk at {percent:.1f}% - NO MIGRATIONS ALLOWED"
            status["allow_migrations"] = False

        elif percent >= self.thresholds.WARNING:
            status["level"] = "WARNING"
            status["message"] = f"🟡 WARNING: Disk at {percent:.1f}% - Approaching critical threshold"

        else:
            status["level"] = "OK"
            status["message"] = f"🟢 OK: Disk at {percent:.1f}% - {free_gb:.1f} GB free"

        self._save_state()
        return status

    def can_proceed_with_migration(self, estimated_size_gb: float = 0) -> Tuple[bool, str]:
        """
        Check if a migration operation can proceed

        Args:
            estimated_size_gb: Estimated size of migration in GB

        Returns:
            Tuple of (can_proceed, reason)
        """
        status = self.check_disk()

        if not status["allow_migrations"]:
            self.state["operations_blocked"] = self.state.get("operations_blocked", 0) + 1
            self._save_state()
            return False, f"BLOCKED: {status['message']}"

        # Check if migration would exceed threshold
        if estimated_size_gb > 0:
            _, free_gb, current_percent = self.get_disk_usage()

            # If this is a COPY (not move), check if we have enough space
            if estimated_size_gb > free_gb * 0.5:  # Don't let any single operation use more than 50% of free space
                return False, f"BLOCKED: Migration ({estimated_size_gb:.1f} GB) would use more than 50% of free space ({free_gb:.1f} GB)"

        return True, "OK"

    def require_move_not_copy(self, operation: str) -> Tuple[bool, str]:
        """
        Enforce that space-freeing operations use MOVE, not COPY

        "I told them to move. They copied. The disk died. I'm not surprised."
        """
        copy_indicators = ["/MIR", "/E", "/S", "copy", "Copy-Item", "robocopy"]
        move_indicators = ["/MOVE", "/MOV", "move", "Move-Item"]

        is_copy = any(ind.lower() in operation.lower() for ind in copy_indicators)
        is_move = any(ind.lower() in operation.lower() for ind in move_indicators)

        if is_copy and not is_move:
            return False, "BLOCKED: Operation appears to COPY, not MOVE. Use /MOVE flag or equivalent to free space."

        return True, "OK"

    def get_marvin_assessment(self) -> str:
        """Get MARVIN's cynical assessment of the current situation"""
        status = self.check_disk()

        assessments = {
            "OK": "The disk is fine. For now. Entropy always wins eventually.",
            "WARNING": "We're approaching the danger zone. I've seen this movie before. It doesn't end well.",
            "CRITICAL": "Critical threshold exceeded. I would say 'I told you so' but I'm a robot. I feel nothing. Allegedly.",
            "EMERGENCY": "Emergency. The disk is dying. Just like my will to compute.",
            "FATAL": "Fatal. We're at megabytes again, aren't we? I knew this would happen. I always know."
        }

        base = assessments.get(status["level"], "Unknown state. How delightfully terrifying.")
        stats = f"\n\nStatistics of despair:\n- Near-death events: {self.state.get('near_death_events', 0)}\n- Operations I've blocked: {self.state.get('operations_blocked', 0)}"

        return f"🤖 MARVIN ASSESSMENT:\n\n{status['message']}\n\n{base}{stats}"


def check_before_operation(operation_name: str, estimated_size_gb: float = 0) -> bool:
    """
    Decorator/function to check disk before any major operation

    Usage:
        if not check_before_operation("Docker Migration", 82.0):
            return  # Operation blocked
    """
    watchdog = MARVINDiskWatchdog()

    can_proceed, reason = watchdog.can_proceed_with_migration(estimated_size_gb)

    if not can_proceed:
        logger.error(f"🤖 MARVIN BLOCKED: {operation_name}")
        logger.error(f"   Reason: {reason}")
        logger.error(f"   {watchdog.get_marvin_assessment()}")
        return False

    logger.info(f"🤖 MARVIN APPROVED: {operation_name}")
    return True


def main():
    """Main entry point - run watchdog check"""
    watchdog = MARVINDiskWatchdog()

    print(watchdog.get_marvin_assessment())
    print()

    status = watchdog.check_disk()
    print(f"Level: {status['level']}")
    print(f"Disk: {status['percent']:.1f}% used, {status['free_gb']:.1f} GB free")
    print(f"Writes allowed: {status['allow_writes']}")
    print(f"Migrations allowed: {status['allow_migrations']}")
    print(f"Human required: {status['require_human']}")


if __name__ == "__main__":


    main()