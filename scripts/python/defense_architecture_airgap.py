#!/usr/bin/env python3
"""
Defense Architecture - Air Gap Capabilities
Implements air gap isolation for critical systems

Air gap capabilities allow systems to operate in isolation when needed.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
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

logger = get_logger("DefenseAirGap")


class AirGapMode(Enum):
    """Air gap operation modes"""
    NORMAL = "normal"  # Normal operation with all connections
    ISOLATED = "isolated"  # Isolated mode - no external connections
    EMERGENCY = "emergency"  # Emergency mode - minimal operations only


class AirGapManager:
    """Manages air gap capabilities for systems"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.airgap_config_file = self.project_root / "config" / "defense" / "airgap_config.json"
        self.airgap_config_file.parent.mkdir(parents=True, exist_ok=True)

        self.current_mode = self._load_mode()
        self.isolated_systems: List[str] = []
        self.blocked_connections: List[str] = []

    def _load_mode(self) -> AirGapMode:
        """Load current air gap mode"""
        if self.airgap_config_file.exists():
            try:
                with open(self.airgap_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AirGapMode(data.get("mode", "normal"))
            except Exception:
                return AirGapMode.NORMAL
        return AirGapMode.NORMAL

    def _save_mode(self):
        try:
            """Save current air gap mode"""
            data = {
                "mode": self.current_mode.value,
                "isolated_systems": self.isolated_systems,
                "blocked_connections": self.blocked_connections,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.airgap_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_mode: {e}", exc_info=True)
            raise
    def set_mode(self, mode: AirGapMode, reason: str = "Manual mode change"):
        """Set air gap mode"""
        self.current_mode = mode
        self._save_mode()
        logger.info(f"🛡️ Air gap mode changed to {mode.value}: {reason}")

    def enable_isolation(self, system_name: str):
        """Enable isolation for a specific system"""
        if system_name not in self.isolated_systems:
            self.isolated_systems.append(system_name)
            self._save_mode()
            logger.info(f"🛡️ System isolated: {system_name}")

    def disable_isolation(self, system_name: str):
        """Disable isolation for a specific system"""
        if system_name in self.isolated_systems:
            self.isolated_systems.remove(system_name)
            self._save_mode()
            logger.info(f"🛡️ System isolation disabled: {system_name}")

    def is_system_isolated(self, system_name: str) -> bool:
        """Check if a system is isolated"""
        if self.current_mode == AirGapMode.EMERGENCY:
            return True  # All systems isolated in emergency mode
        if self.current_mode == AirGapMode.ISOLATED:
            return True  # All systems isolated in isolated mode
        return system_name in self.isolated_systems

    def can_connect(self, connection_type: str) -> bool:
        """Check if a connection type is allowed"""
        if self.current_mode == AirGapMode.EMERGENCY:
            return False  # No external connections in emergency mode
        if self.current_mode == AirGapMode.ISOLATED:
            return False  # No external connections in isolated mode
        return connection_type not in self.blocked_connections

    def block_connection(self, connection_type: str):
        """Block a connection type"""
        if connection_type not in self.blocked_connections:
            self.blocked_connections.append(connection_type)
            self._save_mode()
            logger.warning(f"🛡️ Connection blocked: {connection_type}")

    def allow_connection(self, connection_type: str):
        """Allow a connection type"""
        if connection_type in self.blocked_connections:
            self.blocked_connections.remove(connection_type)
            self._save_mode()
            logger.info(f"🛡️ Connection allowed: {connection_type}")

    def get_status(self) -> Dict[str, Any]:
        """Get air gap status"""
        return {
            "mode": self.current_mode.value,
            "isolated_systems": self.isolated_systems,
            "blocked_connections": self.blocked_connections,
            "timestamp": datetime.now().isoformat()
        }


def get_airgap_manager(project_root: Optional[Path] = None) -> AirGapManager:
    try:
        """Get global air gap manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return AirGapManager(project_root)


    except Exception as e:
        logger.error(f"Error in get_airgap_manager: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test air gap system
    project_root = Path(__file__).parent.parent.parent
    manager = get_airgap_manager(project_root)

    print("=" * 60)
    print("Defense Architecture - Air Gap Capabilities")
    print("=" * 60)

    status = manager.get_status()
    print(f"\nCurrent Mode: {status['mode']}")
    print(f"Isolated Systems: {len(status['isolated_systems'])}")
    print(f"Blocked Connections: {len(status['blocked_connections'])}")

    print("\n" + "=" * 60)
