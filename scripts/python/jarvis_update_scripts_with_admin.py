#!/usr/bin/env python3
"""
JARVIS Update Scripts with Admin Elevation

Updates existing scripts to use the new admin elevation module.
Provides migration guide and integration examples.

@JARVIS @ADMIN @ELEVATION @MIGRATION @INTEGRATION
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UpdateScriptsWithAdmin")


class AdminElevationMigration:
    """
    Admin Elevation Migration Guide

    Shows how to migrate existing scripts to use the admin elevation module.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = get_logger("AdminElevationMigration")

        self.logger.info("=" * 70)
        self.logger.info("🔧 ADMIN ELEVATION MIGRATION GUIDE")
        self.logger.info("=" * 70)
        self.logger.info("")

    def get_migration_examples(self) -> Dict[str, Any]:
        """Get migration examples for common patterns"""
        return {
            "check_admin": {
                "old": """
import ctypes
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False
""",
                "new": """
from scripts.python.jarvis_admin_elevation import is_admin
# or
from scripts.python.jarvis_admin_elevation import AdminElevation
if AdminElevation.is_admin():
    ...
"""
            },
            "request_elevation": {
                "old": """
import ctypes
import sys
def run_as_admin():
    if is_admin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, str(script_path), None, 1
        )
        return False
""",
                "new": """
from scripts.python.jarvis_admin_elevation import ensure_admin_or_exit
from pathlib import Path

ensure_admin_or_exit(Path(__file__).resolve())
# If we get here, we have admin privileges
"""
            },
            "run_powershell": {
                "old": """
def run_powershell_as_admin(command: str):
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result
    except Exception as e:
        self.logger.error(f"Error in run_powershell_as_admin: {e}", exc_info=True)
        raise
""",
                "new": """
from scripts.python.jarvis_admin_elevation import AdminElevation

result = AdminElevation.run_powershell_as_admin(command)
# Returns: {"success": bool, "stdout": str, "stderr": str, "returncode": int, "admin": bool}
"""
            },
            "service_management": {
                "old": """
subprocess.run(
    ["powershell", "-Command", "Set-Service -Name 'ServiceName' -StartupType Manual"],
    capture_output=True
)
""",
                "new": """
from scripts.python.jarvis_admin_elevation import AdminElevation

result = AdminElevation.set_service_startup_type("ServiceName", "Manual")
if result["success"]:
    AdminElevation.start_service("ServiceName")
"""
            }
        }

    def get_scripts_needing_migration(self) -> List[Dict[str, Any]]:
        """Get list of scripts that could benefit from admin elevation"""
        scripts = [
            {
                "file": "jarvis_automated_external_lighting_fix.py",
                "reason": "Uses custom run_powershell_as_admin - should use AdminElevation",
                "priority": "high"
            },
            {
                "file": "jarvis_smart_lighting_day_night_sync.py",
                "reason": "Service management needs admin - should use AdminElevation",
                "priority": "high"
            },
            {
                "file": "jarvis_power_killswitch_external_lights.py",
                "reason": "Has admin check code - should use AdminElevation",
                "priority": "medium"
            },
            {
                "file": "jarvis_elevated_lighting_fix.py",
                "reason": "Has custom admin elevation - should use AdminElevation",
                "priority": "medium"
            }
        ]
        return scripts

    def create_migration_report(self) -> Dict[str, Any]:
        """Create migration report"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 MIGRATION REPORT")
        self.logger.info("=" * 70)
        self.logger.info("")

        examples = self.get_migration_examples()
        scripts = self.get_scripts_needing_migration()

        self.logger.info("   📝 Migration Examples:")
        for pattern, code in examples.items():
            self.logger.info(f"      - {pattern}")

        self.logger.info("")
        self.logger.info("   📋 Scripts Needing Migration:")
        for script in scripts:
            priority_icon = "🔴" if script["priority"] == "high" else "🟡" if script["priority"] == "medium" else "🟢"
            self.logger.info(f"      {priority_icon} {script['file']}")
            self.logger.info(f"         Reason: {script['reason']}")

        return {
            "examples": examples,
            "scripts": scripts
        }


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        migration = AdminElevationMigration(project_root)
        report = migration.create_migration_report()

        print()
        print("=" * 70)
        print("🔧 ADMIN ELEVATION MIGRATION GUIDE")
        print("=" * 70)
        print()
        print("   ✅ Admin elevation module is ready to use")
        print("   📝 Migration examples available")
        print(f"   📋 {len(report['scripts'])} scripts identified for migration")
        print()
        print("   💡 Use: from scripts.python.jarvis_admin_elevation import AdminElevation")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()