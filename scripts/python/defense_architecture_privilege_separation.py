#!/usr/bin/env python3
"""
Defense Architecture - Privilege Separation
Implements privilege separation and access control

All systems MUST enforce privilege separation.
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

logger = get_logger("DefensePrivilege")


class PrivilegeLevel(Enum):
    """Privilege levels"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SYSTEM = "system"
    ROOT = "root"


class PrivilegeManager:
    """Manages privilege separation"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.privilege_config_file = self.project_root / "config" / "defense" / "privilege_config.json"
        self.privilege_config_file.parent.mkdir(parents=True, exist_ok=True)

        self.system_privileges: Dict[str, PrivilegeLevel] = {}
        self.resource_permissions: Dict[str, List[str]] = {}
        self._load_privileges()

    def _load_privileges(self):
        """Load privilege configuration"""
        if self.privilege_config_file.exists():
            try:
                with open(self.privilege_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for system, level in data.get("system_privileges", {}).items():
                        self.system_privileges[system] = PrivilegeLevel(level)
                    self.resource_permissions = data.get("resource_permissions", {})
            except Exception as e:
                logger.error(f"Error loading privileges: {e}")

        # Set default privileges if not configured
        if not self.system_privileges:
            self._set_default_privileges()

    def _set_default_privileges(self):
        """Set default privilege levels"""
        defaults = {
            "jarvis-master-agent": PrivilegeLevel.SYSTEM,
            "lumina-core": PrivilegeLevel.ADMIN,
            "r5-knowledge-matrix": PrivilegeLevel.READ_WRITE,
            "helpdesk-system": PrivilegeLevel.READ_WRITE,
            "workflow-processor": PrivilegeLevel.READ_WRITE,
            "service-bus-integration": PrivilegeLevel.READ_WRITE,
            "key-vault-integration": PrivilegeLevel.SYSTEM,
            "master-feedback-loop": PrivilegeLevel.READ_WRITE,
            "syphon-intelligence": PrivilegeLevel.READ_WRITE,
            "verification-system": PrivilegeLevel.READ_WRITE
        }
        self.system_privileges.update(defaults)
        self._save_privileges()

    def _save_privileges(self):
        try:
            """Save privilege configuration"""
            data = {
                "system_privileges": {
                    system: level.value
                    for system, level in self.system_privileges.items()
                },
                "resource_permissions": self.resource_permissions,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.privilege_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_privileges: {e}", exc_info=True)
            raise
    def set_system_privilege(self, system_name: str, level: PrivilegeLevel):
        """Set privilege level for a system"""
        self.system_privileges[system_name] = level
        self._save_privileges()
        logger.info(f"🔐 Privilege set for {system_name}: {level.value}")

    def get_system_privilege(self, system_name: str) -> PrivilegeLevel:
        """Get privilege level for a system"""
        return self.system_privileges.get(system_name, PrivilegeLevel.READ_ONLY)

    def has_permission(self, system_name: str, resource: str, action: str) -> bool:
        """Check if system has permission for resource action"""
        privilege = self.get_system_privilege(system_name)

        # Root and System can do anything
        if privilege in [PrivilegeLevel.ROOT, PrivilegeLevel.SYSTEM]:
            return True

        # Admin can do most things
        if privilege == PrivilegeLevel.ADMIN:
            return action in ["read", "write", "delete", "execute"]

        # Read-Write can read and write
        if privilege == PrivilegeLevel.READ_WRITE:
            return action in ["read", "write"]

        # Read-Only can only read
        if privilege == PrivilegeLevel.READ_ONLY:
            return action == "read"

        return False

    def enforce_privilege(self, system_name: str, resource: str, action: str) -> bool:
        """Enforce privilege check - raises exception if not allowed"""
        if not self.has_permission(system_name, resource, action):
            raise PermissionError(
                f"System {system_name} with privilege {self.get_system_privilege(system_name).value} "
                f"does not have permission to {action} {resource}"
            )
        return True


def get_privilege_manager(project_root: Optional[Path] = None) -> PrivilegeManager:
    try:
        """Get global privilege manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return PrivilegeManager(project_root)


    except Exception as e:
        logger.error(f"Error in get_privilege_manager: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test privilege system
    project_root = Path(__file__).parent.parent.parent
    manager = get_privilege_manager(project_root)

    print("=" * 60)
    print("Defense Architecture - Privilege Separation")
    print("=" * 60)

    print("\nSystem Privileges:")
    for system, privilege in manager.system_privileges.items():
        print(f"  {system}: {privilege.value}")

    print("\n" + "=" * 60)
