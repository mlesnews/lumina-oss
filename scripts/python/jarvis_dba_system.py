#!/usr/bin/env python3
"""
JARVIS Database Administrator (@DBA) System

@DBA - Database Administrator
Responsible for:
- Database administration
- User management
- Security and access control
- Backup and recovery
- Performance monitoring
- Capacity planning
- Disaster recovery

Tags: #DATABASE[@DB] @TEAM @DBA
"""

import sys
import json
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
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

logger = get_logger("JARVISDBA")


class JARVISDatabaseAdministrator:
    """
    Database Administrator (@DBA) System

    Handles database administration, backup, recovery, and monitoring.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # DBA configuration
        self.config = self._load_config()

        # Backup directory
        self.backup_dir = project_root / "data" / "database_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # NAS backup directory (if accessible)
        self.nas_backup_dir = None
        if self.config.get("nas_integration", True):
            try:
                nas_path = Path(f"\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\database_backups")
                # Don't check exists() as it may fail - just set path
                self.nas_backup_dir = nas_path
            except Exception:
                pass

        self.logger.info("✅ Database Administrator (@DBA) System initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load DBA configuration"""
        config_file = self.project_root / "config" / "dba_config.json"

        default_config = {
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "backup_retention_days": 30,
            "nas_integration": True,
            "monitoring_enabled": True,
            "health_checks_enabled": True
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}")
        else:
            try:
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to save config: {e}")

        return default_config

    def backup_database(self, db_path: Path, backup_to_nas: bool = True) -> Dict[str, Any]:
        """Backup database to local and optionally NAS"""
        self.logger.info(f"💾 Backing up database: {db_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_path.stem}_{timestamp}.db"

        # Local backup
        local_backup_path = self.backup_dir / backup_name

        try:
            # Copy database file
            shutil.copy2(db_path, local_backup_path)

            result = {
                "success": True,
                "database_path": str(db_path),
                "local_backup": str(local_backup_path),
                "backup_size_mb": local_backup_path.stat().st_size / (1024 * 1024),
                "timestamp": timestamp
            }

            # NAS backup (if enabled and accessible)
            if backup_to_nas and self.nas_backup_dir:
                try:
                    nas_backup_path = self.nas_backup_dir / backup_name
                    # Try to create NAS backup (may fail if not accessible)
                    try:
                        self.nas_backup_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(db_path, nas_backup_path)
                        result["nas_backup"] = str(nas_backup_path)
                        result["nas_backup_success"] = True
                    except (OSError, PermissionError) as e:
                        result["nas_backup_success"] = False
                        result["nas_backup_error"] = str(e)
                        self.logger.warning(f"⚠️  NAS backup failed: {e}")
                except Exception as e:
                    result["nas_backup_success"] = False
                    result["nas_backup_error"] = str(e)

            self.logger.info(f"✅ Backup created: {local_backup_path}")
            return result

        except Exception as e:
            return {
                "success": False,
                "database_path": str(db_path),
                "error": str(e)
            }

    def restore_database(self, backup_path: Path, target_path: Path) -> Dict[str, Any]:
        """Restore database from backup"""
        self.logger.info(f"🔄 Restoring database from: {backup_path}")

        try:
            shutil.copy2(backup_path, target_path)

            return {
                "success": True,
                "backup_path": str(backup_path),
                "target_path": str(target_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def monitor_database_health(self, db_path: Path) -> Dict[str, Any]:
        """Monitor database health"""
        self.logger.info(f"🏥 Monitoring database health: {db_path}")

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]

            # Get database size
            db_size = db_path.stat().st_size if db_path.exists() else 0

            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]

            conn.close()

            health_status = {
                "database_path": str(db_path),
                "integrity": integrity,
                "size_mb": db_size / (1024 * 1024),
                "table_count": table_count,
                "healthy": integrity == "ok",
                "timestamp": datetime.now().isoformat()
            }

            return health_status

        except Exception as e:
            return {
                "database_path": str(db_path),
                "healthy": False,
                "error": str(e)
            }

    def list_backups(self, database_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []

        # Local backups
        for backup_file in self.backup_dir.glob("*.db"):
            if database_name and database_name not in backup_file.name:
                continue

            backups.append({
                "path": str(backup_file),
                "location": "local",
                "size_mb": backup_file.stat().st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            })

        # NAS backups (if accessible)
        if self.nas_backup_dir:
            try:
                if self.nas_backup_dir.exists():
                    for backup_file in self.nas_backup_dir.glob("*.db"):
                        if database_name and database_name not in backup_file.name:
                            continue

                        backups.append({
                            "path": str(backup_file),
                            "location": "nas",
                            "size_mb": backup_file.stat().st_size / (1024 * 1024),
                            "modified": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                        })
            except Exception:
                pass

        return sorted(backups, key=lambda x: x["modified"], reverse=True)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Database Administrator (@DBA) System")
        parser.add_argument("--backup", type=str, help="Backup a database")
        parser.add_argument("--restore", type=str, nargs=2, metavar=("BACKUP", "TARGET"), help="Restore database")
        parser.add_argument("--health", type=str, help="Check database health")
        parser.add_argument("--list-backups", type=str, nargs="?", help="List backups (optional: database name)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        dba = JARVISDatabaseAdministrator(project_root)

        if args.backup:
            result = dba.backup_database(Path(args.backup))
            import json
            print(json.dumps(result, indent=2, default=str))

        elif args.restore:
            result = dba.restore_database(Path(args.restore[0]), Path(args.restore[1]))
            import json
            print(json.dumps(result, indent=2))

        elif args.health:
            result = dba.monitor_database_health(Path(args.health))
            import json
            print(json.dumps(result, indent=2, default=str))

        elif args.list_backups is not None:
            backups = dba.list_backups(args.list_backups)
            import json
            print(json.dumps(backups, indent=2, default=str))

        else:
            print("Usage:")
            print("  --backup <db_path>           : Backup database")
            print("  --restore <backup> <target>  : Restore database")
            print("  --health <db_path>           : Check database health")
            print("  --list-backups [db_name]     : List backups")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()