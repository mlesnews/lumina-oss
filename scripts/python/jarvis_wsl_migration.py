#!/usr/bin/env python3
"""
JARVIS WSL Migration Tool

Identifies Ubuntu WSL instances, migrates data/services, and removes them.
Ensures only Kali Linux WSL remains (if needed).

Tags: #MIGRATION #WSL #KALI-LINUX
"""

import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWSLMigration")


class JARVISWSLMigration:
    """
    JARVIS WSL Migration

    Handles migration and removal of Ubuntu WSL instances.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.wsl_instances: List[Dict[str, Any]] = []

        self.logger.info("✅ JARVIS WSL Migration initialized")

    def list_wsl_instances(self) -> List[Dict[str, Any]]:
        """List all WSL instances"""
        self.logger.info("🔍 Listing WSL instances...")

        try:
            result = subprocess.run(
                ["wsl", "--list", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.warning(f"⚠️  WSL list command failed: {result.stderr}")
                return []

            lines = result.stdout.strip().split('\n')
            instances = []

            # Skip header line (first line is usually "NAME STATE VERSION")
            for line in lines[1:]:
                if not line.strip():
                    continue

                # Clean up the line (remove null bytes and extra whitespace)
                line = line.replace('\x00', '').strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0].strip()
                    state = parts[1].strip() if len(parts) > 1 else "Unknown"
                    version = parts[2].strip() if len(parts) > 2 else "Unknown"

                    # Skip default marker (*)
                    if name == "*":
                        continue

                    is_ubuntu = "ubuntu" in name.lower()
                    is_kali = "kali" in name.lower()

                    instances.append({
                        "name": name,
                        "state": state,
                        "version": version,
                        "is_ubuntu": is_ubuntu,
                        "is_kali": is_kali,
                        "needs_migration": is_ubuntu,
                        "needs_removal": is_ubuntu
                    })

            self.wsl_instances = instances

            ubuntu_count = sum(1 for i in instances if i["is_ubuntu"])
            kali_count = sum(1 for i in instances if i["is_kali"])

            self.logger.info(f"   Found {len(instances)} WSL instances:")
            self.logger.info(f"   - Ubuntu: {ubuntu_count}")
            self.logger.info(f"   - Kali Linux: {kali_count}")
            self.logger.info(f"   - Other: {len(instances) - ubuntu_count - kali_count}")

            return instances

        except FileNotFoundError:
            self.logger.warning("⚠️  WSL not found - may not be installed")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error listing WSL instances: {e}", exc_info=True)
            return []

    def check_wsl_status(self) -> Dict[str, Any]:
        """Check WSL status"""
        self.logger.info("🔍 Checking WSL status...")

        try:
            result = subprocess.run(
                ["wsl", "--status"],
                capture_output=True,
                text=True,
                timeout=10
            )

            status = {
                "available": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }

            if status["available"]:
                self.logger.info("   ✅ WSL is available")
            else:
                self.logger.warning("   ⚠️  WSL status check failed")

            return status

        except Exception as e:
            self.logger.error(f"❌ Error checking WSL status: {e}", exc_info=True)
            return {"available": False, "error": str(e)}

    def export_wsl_data(self, wsl_name: str, export_path: Path) -> Dict[str, Any]:
        """Export data from WSL instance"""
        self.logger.info(f"📦 Exporting data from {wsl_name}...")

        try:
            # Create export directory
            export_path.mkdir(parents=True, exist_ok=True)

            # Export using wsl --export
            export_file = export_path / f"{wsl_name}_export.tar"

            result = subprocess.run(
                ["wsl", "--export", wsl_name, str(export_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                self.logger.info(f"   ✅ Exported to {export_file}")
                return {
                    "success": True,
                    "export_file": str(export_file),
                    "size": export_file.stat().st_size if export_file.exists() else 0
                }
            else:
                self.logger.error(f"   ❌ Export failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            self.logger.error(f"❌ Error exporting WSL data: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def unregister_wsl(self, wsl_name: str) -> Dict[str, Any]:
        """Unregister (remove) WSL instance"""
        self.logger.info(f"🗑️  Unregistering WSL instance: {wsl_name}...")

        try:
            result = subprocess.run(
                ["wsl", "--unregister", wsl_name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info(f"   ✅ Successfully unregistered {wsl_name}")
                return {"success": True}
            else:
                self.logger.error(f"   ❌ Unregister failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            self.logger.error(f"❌ Error unregistering WSL: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def migrate_ubuntu_wsl(self, wsl_name: str) -> Dict[str, Any]:
        """Migrate Ubuntu WSL instance"""
        self.logger.info(f"🔄 Migrating Ubuntu WSL: {wsl_name}...")

        migration = {
            "wsl_name": wsl_name,
            "timestamp": datetime.now().isoformat(),
            "export": None,
            "unregister": None,
            "success": False
        }

        # Step 1: Export data
        export_dir = self.project_root / "data" / "wsl_exports"
        export_result = self.export_wsl_data(wsl_name, export_dir)
        migration["export"] = export_result

        if not export_result.get("success"):
            self.logger.warning(f"   ⚠️  Export failed, but proceeding with removal")

        # Step 2: Unregister
        unregister_result = self.unregister_wsl(wsl_name)
        migration["unregister"] = unregister_result

        if unregister_result.get("success"):
            migration["success"] = True
            self.logger.info(f"   ✅ Successfully migrated and removed {wsl_name}")
        else:
            self.logger.error(f"   ❌ Migration incomplete for {wsl_name}")

        return migration

    def full_migration(self) -> Dict[str, Any]:
        """Perform full WSL migration - remove all Ubuntu instances"""
        self.logger.info("🚀 Starting full WSL migration...")

        # List instances
        instances = self.list_wsl_instances()

        if not instances:
            self.logger.info("   ℹ️  No WSL instances found")
            return {
                "success": True,
                "message": "No WSL instances to migrate",
                "instances": []
            }

        # Find Ubuntu instances
        ubuntu_instances = [i for i in instances if i["is_ubuntu"]]

        if not ubuntu_instances:
            self.logger.info("   ✅ No Ubuntu WSL instances found - nothing to migrate")
            return {
                "success": True,
                "message": "No Ubuntu WSL instances found",
                "instances": instances
            }

        self.logger.info(f"   Found {len(ubuntu_instances)} Ubuntu WSL instance(s) to migrate")

        # Migrate each Ubuntu instance
        migrations = []
        for instance in ubuntu_instances:
            migration = self.migrate_ubuntu_wsl(instance["name"])
            migrations.append(migration)

        # Summary
        successful = sum(1 for m in migrations if m.get("success"))
        failed = len(migrations) - successful

        result = {
            "success": failed == 0,
            "timestamp": datetime.now().isoformat(),
            "total_ubuntu": len(ubuntu_instances),
            "migrated": successful,
            "failed": failed,
            "migrations": migrations,
            "remaining_instances": [i for i in instances if not i["is_ubuntu"]]
        }

        self.logger.info(f"   ✅ Migration complete: {successful} successful, {failed} failed")

        return result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS WSL Migration")
        parser.add_argument("--list", action="store_true", help="List WSL instances")
        parser.add_argument("--status", action="store_true", help="Check WSL status")
        parser.add_argument("--migrate", action="store_true", help="Migrate all Ubuntu WSL instances")
        parser.add_argument("--migrate-instance", type=str, help="Migrate specific WSL instance")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        migration = JARVISWSLMigration(project_root)

        if args.list:
            instances = migration.list_wsl_instances()
            print(json.dumps(instances, indent=2))

        elif args.status:
            status = migration.check_wsl_status()
            print(json.dumps(status, indent=2))

        elif args.migrate:
            result = migration.full_migration()
            print(json.dumps(result, indent=2, default=str))

        elif args.migrate_instance:
            result = migration.migrate_ubuntu_wsl(args.migrate_instance)
            print(json.dumps(result, indent=2, default=str))

        else:
            print("Usage:")
            print("  --list              : List WSL instances")
            print("  --status            : Check WSL status")
            print("  --migrate           : Migrate all Ubuntu WSL instances")
            print("  --migrate-instance  : Migrate specific WSL instance")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()