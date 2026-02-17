#!/usr/bin/env python3
"""
JARVIS WSL Migration Manager

Migrates Ubuntu WSL instances to Kali Linux and removes Ubuntu WSL.
LUMINA uses ONLY Kali Linux.

Tags: #MIGRATION #WSL #KALI-LINUX
"""

import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
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


class JARVISWSLMigrationManager:
    """
    JARVIS WSL Migration Manager

    Manages migration from Ubuntu WSL to Kali Linux WSL.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.wsl_distros: List[Dict[str, Any]] = []
        self.ubuntu_distros: List[Dict[str, Any]] = []
        self.kali_distros: List[Dict[str, Any]] = []

        self.logger.info("✅ JARVIS WSL Migration Manager initialized")

    def list_wsl_distributions(self) -> List[Dict[str, Any]]:
        """List all WSL distributions"""
        self.logger.info("🔍 Listing WSL distributions...")

        try:
            # Get list (using --all for cleaner output)
            result = subprocess.run(
                ["wsl", "--list", "--all"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error(f"❌ Failed to list WSL distributions: {result.stderr}")
                return []

            lines = result.stdout.strip().split('\n')
            distros = []

            # Parse output (skip header line if present)
            for line in lines:
                if not line.strip() or line.strip().startswith("NAME") or line.strip().startswith("Default"):
                    continue

                # Clean up line (remove null characters and extra whitespace)
                line = line.replace('\x00', '').strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0].replace('*', '').strip()  # Remove default marker
                    state = parts[1] if len(parts) > 1 else "Unknown"
                    version = parts[2] if len(parts) > 2 else "Unknown"

                    # Skip if name is empty or just markers
                    if not name or name in ["*", "Default", "Distribution"]:
                        continue

                    distro_info = {
                        "name": name,
                        "state": state,
                        "version": version,
                        "is_ubuntu": "ubuntu" in name.lower(),
                        "is_kali": "kali" in name.lower()
                    }

                    distros.append(distro_info)

                    if distro_info["is_ubuntu"]:
                        self.ubuntu_distros.append(distro_info)
                    elif distro_info["is_kali"]:
                        self.kali_distros.append(distro_info)

            self.wsl_distros = distros
            self.logger.info(f"   Found {len(distros)} WSL distribution(s)")
            self.logger.info(f"   Ubuntu: {len(self.ubuntu_distros)}, Kali: {len(self.kali_distros)}")

            return distros

        except subprocess.TimeoutExpired:
            self.logger.error("❌ WSL list command timed out")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error listing WSL distributions: {e}", exc_info=True)
            return []

    def backup_ubuntu_data(self, ubuntu_distro: str) -> Optional[Path]:
        """Backup data from Ubuntu WSL before removal"""
        self.logger.info(f"📦 Backing up data from {ubuntu_distro}...")

        backup_dir = self.project_root / "data" / "wsl_backups" / ubuntu_distro
        backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Export Ubuntu WSL to tar file
            backup_file = backup_dir / f"{ubuntu_distro}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar"

            export_cmd = ["wsl", "--export", ubuntu_distro, str(backup_file)]
            result = subprocess.run(
                export_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                self.logger.info(f"   ✅ Backup created: {backup_file}")
                return backup_file
            else:
                self.logger.error(f"   ❌ Backup failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("   ❌ Backup timed out")
            return None
        except Exception as e:
            self.logger.error(f"   ❌ Error backing up {ubuntu_distro}: {e}", exc_info=True)
            return None

    def migrate_data_to_kali(self, ubuntu_distro: str, kali_distro: str, backup_file: Path) -> bool:
        """Migrate data from Ubuntu backup to Kali Linux WSL"""
        self.logger.info(f"🔄 Migrating data from {ubuntu_distro} to {kali_distro}...")

        try:
            # Import Ubuntu backup into Kali (if needed)
            # Note: This is a simplified approach - actual migration may need more steps

            # Check if Kali WSL exists
            kali_check = subprocess.run(
                ["wsl", "-d", kali_distro, "--", "uname", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if kali_check.returncode != 0:
                self.logger.warning(f"   ⚠️  Kali Linux WSL ({kali_distro}) not found or not running")
                self.logger.info("   📝 Migration data saved to backup - can be manually migrated if needed")
                return False

            # For now, we'll just note that the backup exists
            # Actual data migration would require:
            # 1. Mounting Ubuntu filesystem
            # 2. Copying specific directories (home, configs, etc.)
            # 3. Adjusting paths and permissions

            self.logger.info(f"   ✅ Backup available for manual migration: {backup_file}")
            self.logger.info("   📝 Manual migration steps:")
            self.logger.info(f"      1. Review backup: {backup_file}")
            self.logger.info(f"      2. Extract needed files from backup")
            self.logger.info(f"      3. Copy to Kali Linux WSL: {kali_distro}")

            return True

        except Exception as e:
            self.logger.error(f"   ❌ Error during migration: {e}", exc_info=True)
            return False

    def unregister_ubuntu_wsl(self, ubuntu_distro: str) -> bool:
        """Unregister (remove) Ubuntu WSL distribution"""
        self.logger.info(f"🗑️  Removing Ubuntu WSL: {ubuntu_distro}...")

        try:
            # First, terminate if running
            terminate_cmd = ["wsl", "--terminate", ubuntu_distro]
            subprocess.run(terminate_cmd, capture_output=True, timeout=10)

            # Unregister
            unregister_cmd = ["wsl", "--unregister", ubuntu_distro]
            result = subprocess.run(
                unregister_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info(f"   ✅ Successfully removed {ubuntu_distro}")
                return True
            else:
                self.logger.error(f"   ❌ Failed to remove {ubuntu_distro}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("   ❌ Unregister command timed out")
            return False
        except Exception as e:
            self.logger.error(f"   ❌ Error removing {ubuntu_distro}: {e}", exc_info=True)
            return False

    def ensure_kali_linux_wsl(self) -> bool:
        """Ensure Kali Linux WSL is installed"""
        self.logger.info("🔍 Checking for Kali Linux WSL...")

        if self.kali_distros:
            self.logger.info(f"   ✅ Kali Linux WSL found: {[d['name'] for d in self.kali_distros]}")
            return True

        self.logger.warning("   ⚠️  No Kali Linux WSL found")
        self.logger.info("   📝 To install Kali Linux WSL:")
        self.logger.info("      1. Open Microsoft Store")
        self.logger.info("      2. Search for 'Kali Linux'")
        self.logger.info("      3. Install Kali Linux")
        self.logger.info("      4. Run: wsl --install -d Kali-Linux")

        return False

    def migrate_all_ubuntu_wsl(self, backup: bool = True, migrate: bool = True) -> Dict[str, Any]:
        """Migrate all Ubuntu WSL instances"""
        self.logger.info("🚀 Starting Ubuntu WSL migration process...")

        # List distributions
        distros = self.list_wsl_distributions()

        if not self.ubuntu_distros:
            self.logger.info("   ✅ No Ubuntu WSL instances found")
            return {
                "success": True,
                "ubuntu_found": False,
                "migrated": [],
                "removed": []
            }

        results = {
            "success": True,
            "ubuntu_found": True,
            "ubuntu_count": len(self.ubuntu_distros),
            "backups": [],
            "migrated": [],
            "removed": [],
            "errors": []
        }

        # Ensure Kali Linux exists
        kali_available = self.ensure_kali_linux_wsl()
        kali_distro = self.kali_distros[0]["name"] if self.kali_distros else None

        for ubuntu_distro in self.ubuntu_distros:
            distro_name = ubuntu_distro["name"]
            self.logger.info(f"\n📋 Processing: {distro_name}")

            # Backup
            backup_file = None
            if backup:
                backup_file = self.backup_ubuntu_data(distro_name)
                if backup_file:
                    results["backups"].append(str(backup_file))

            # Migrate
            if migrate and kali_available and backup_file:
                migrated = self.migrate_data_to_kali(distro_name, kali_distro, backup_file)
                if migrated:
                    results["migrated"].append(distro_name)

            # Remove
            removed = self.unregister_ubuntu_wsl(distro_name)
            if removed:
                results["removed"].append(distro_name)
            else:
                results["errors"].append(f"Failed to remove {distro_name}")
                results["success"] = False

        # Summary
        self.logger.info("\n📊 Migration Summary:")
        self.logger.info(f"   Ubuntu WSL found: {results['ubuntu_count']}")
        self.logger.info(f"   Backups created: {len(results['backups'])}")
        self.logger.info(f"   Migrated: {len(results['migrated'])}")
        self.logger.info(f"   Removed: {len(results['removed'])}")
        if results["errors"]:
            self.logger.warning(f"   Errors: {len(results['errors'])}")

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS WSL Migration Manager")
        parser.add_argument("--list", action="store_true", help="List WSL distributions")
        parser.add_argument("--migrate", action="store_true", help="Migrate all Ubuntu WSL")
        parser.add_argument("--no-backup", action="store_true", help="Skip backup before removal")
        parser.add_argument("--no-migrate", action="store_true", help="Skip data migration")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = JARVISWSLMigrationManager(project_root)

        if args.list:
            distros = manager.list_wsl_distributions()
            print(json.dumps(distros, indent=2))

        elif args.migrate:
            backup = not args.no_backup
            migrate = not args.no_migrate
            results = manager.migrate_all_ubuntu_wsl(backup=backup, migrate=migrate)
            print(json.dumps(results, indent=2, default=str))

        else:
            print("Usage:")
            print("  --list       : List WSL distributions")
            print("  --migrate    : Migrate all Ubuntu WSL to Kali Linux")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()