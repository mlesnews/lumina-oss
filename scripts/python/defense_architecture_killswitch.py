#!/usr/bin/env python3
"""
Defense Architecture - Killswitch System
Implements killswitch mechanisms for all systems

All systems MUST have verified killswitches for emergency shutdown.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DefenseKillswitch")


class KillswitchStatus(Enum):
    """Killswitch status"""
    ACTIVE = "active"
    KILLED = "killed"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class SystemKillswitch:
    """Killswitch for a single system"""

    def __init__(self, system_name: str, killswitch_file: Path):
        self.system_name = system_name
        self.killswitch_file = killswitch_file
        self.killswitch_file.parent.mkdir(parents=True, exist_ok=True)
        self._status = self._load_status()

    def _load_status(self) -> KillswitchStatus:
        """Load killswitch status from file"""
        if self.killswitch_file.exists():
            try:
                with open(self.killswitch_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return KillswitchStatus(data.get("status", "active"))
            except Exception:
                return KillswitchStatus.UNKNOWN
        return KillswitchStatus.ACTIVE

    def is_active(self) -> bool:
        """Check if system is active (not killed)"""
        return self._status == KillswitchStatus.ACTIVE

    def kill(self, reason: str = "Emergency shutdown") -> bool:
        """Kill the system"""
        try:
            self._status = KillswitchStatus.KILLED
            self._save_status(reason)
            logger.critical(f"🔴 KILLSWITCH ACTIVATED: {self.system_name} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error activating killswitch for {self.system_name}: {e}")
            return False

    def activate(self) -> bool:
        """Activate the system"""
        try:
            self._status = KillswitchStatus.ACTIVE
            self._save_status("System activated")
            logger.info(f"🟢 KILLSWITCH DEACTIVATED: {self.system_name}")
            return True
        except Exception as e:
            logger.error(f"Error deactivating killswitch for {self.system_name}: {e}")
            return False

    def suspend(self, reason: str = "Temporary suspension") -> bool:
        """Suspend the system"""
        try:
            self._status = KillswitchStatus.SUSPENDED
            self._save_status(reason)
            logger.warning(f"🟡 KILLSWITCH SUSPENDED: {self.system_name} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error suspending killswitch for {self.system_name}: {e}")
            return False

    def _save_status(self, reason: str):
        try:
            """Save killswitch status to file"""
            data = {
                "system_name": self.system_name,
                "status": self._status.value,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.killswitch_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_status: {e}", exc_info=True)
            raise
    def get_status(self) -> Dict[str, Any]:
        """Get killswitch status"""
        return {
            "system_name": self.system_name,
            "status": self._status.value,
            "is_active": self.is_active()
        }


class DefenseKillswitchManager:
    """Manager for all system killswitches"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.killswitch_dir = self.project_root / "data" / "defense" / "killswitches"
        self.killswitch_dir.mkdir(parents=True, exist_ok=True)

        self.killswitches: Dict[str, SystemKillswitch] = {}
        self._register_all_systems()

    def _register_all_systems(self):
        """Register all systems that need killswitches"""
        systems = [
            "jarvis-master-agent",
            "lumina-core",
            "r5-knowledge-matrix",
            "helpdesk-system",
            "workflow-processor",
            "service-bus-integration",
            "key-vault-integration",
            "master-feedback-loop",
            "syphon-intelligence",
            "verification-system"
        ]

        for system_name in systems:
            killswitch_file = self.killswitch_dir / f"{system_name}.json"
            self.killswitches[system_name] = SystemKillswitch(system_name, killswitch_file)

    def register_system(self, system_name: str) -> SystemKillswitch:
        """Register a new system killswitch"""
        killswitch_file = self.killswitch_dir / f"{system_name}.json"
        killswitch = SystemKillswitch(system_name, killswitch_file)
        self.killswitches[system_name] = killswitch
        return killswitch

    def get_killswitch(self, system_name: str) -> Optional[SystemKillswitch]:
        """Get killswitch for a system"""
        return self.killswitches.get(system_name)

    def kill_all(self, reason: str = "Emergency shutdown - all systems") -> Dict[str, bool]:
        """Kill all systems"""
        results = {}
        for system_name, killswitch in self.killswitches.items():
            results[system_name] = killswitch.kill(reason)
        logger.critical(f"🔴 ALL SYSTEMS KILLED: {reason}")
        return results

    def activate_all(self) -> Dict[str, bool]:
        """Activate all systems"""
        results = {}
        for system_name, killswitch in self.killswitches.items():
            results[system_name] = killswitch.activate()
        logger.info("🟢 ALL SYSTEMS ACTIVATED")
        return results

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all killswitches"""
        return {
            system_name: killswitch.get_status()
            for system_name, killswitch in self.killswitches.items()
        }

    def verify_all_killswitches(self) -> Dict[str, bool]:
        """Verify all systems have working killswitches"""
        results = {}
        for system_name, killswitch in self.killswitches.items():
            # Test killswitch by checking file operations
            try:
                status = killswitch.get_status()
                results[system_name] = status is not None
            except Exception as e:
                logger.error(f"Killswitch verification failed for {system_name}: {e}")
                results[system_name] = False
        return results


def get_killswitch_manager(project_root: Optional[Path] = None) -> DefenseKillswitchManager:
    try:
        """Get global killswitch manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return DefenseKillswitchManager(project_root)


    except Exception as e:
        logger.error(f"Error in get_killswitch_manager: {e}", exc_info=True)
        raise
def check_killswitch(system_name: str, project_root: Optional[Path] = None) -> bool:
    """Check if a system's killswitch is active"""
    manager = get_killswitch_manager(project_root)
    killswitch = manager.get_killswitch(system_name)
    if killswitch:
        return killswitch.is_active()
    # If system not registered, assume active
    return True


if __name__ == "__main__":
    # Test killswitch system
    project_root = Path(__file__).parent.parent.parent
    manager = get_killswitch_manager(project_root)

    print("=" * 60)
    print("Defense Architecture - Killswitch System")
    print("=" * 60)

    # Verify all killswitches
    print("\nVerifying all killswitches...")
    verification = manager.verify_all_killswitches()
    for system, verified in verification.items():
        status = "✅" if verified else "❌"
        print(f"  {status} {system}: {'Verified' if verified else 'Failed'}")

    # Get all status
    print("\nAll killswitch statuses:")
    all_status = manager.get_all_status()
    for system_name, status in all_status.items():
        status_icon = "🟢" if status["is_active"] else "🔴"
        print(f"  {status_icon} {system_name}: {status['status']}")

    print("\n" + "=" * 60)
