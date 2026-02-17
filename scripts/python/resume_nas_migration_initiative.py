#!/usr/bin/env python3
"""
Resume NAS Migration Initiative

Resumes the interrupted NAS migration and all associated tasks.
Handles the complete migration workflow from detection to completion.

Tags: #MIGRATION #NAS #RESUME #INITIATIVE #AUTOMATION @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from cloud_nas_migration_tracker import CloudNASMigrationTracker
    from resume_interrupted_migration import resume_migration
    from comprehensive_storage_migration_manager import ComprehensiveStorageMigrationManager
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ResumeNASMigrationInitiative")
ts_logger = get_timestamp_logger()


class NASMigrationInitiative:
    """
    Resume NAS Migration Initiative

    Handles:
    1. Detection of interrupted migrations
    2. Finding actual migration targets from logs
    3. Resuming interrupted migrations
    4. Completing all associated tasks
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize NAS migration initiative"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.tracker = CloudNASMigrationTracker(project_root=project_root)
        self.migration_mgr = ComprehensiveStorageMigrationManager(project_root=project_root)

        # Known migration target from logs
        self.known_targets = [
            Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\my_projects\\.lumina"),
            Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\my_projects"),
        ]

        logger.info("🚀 NAS Migration Initiative initialized")

    def find_migration_target_from_logs(self, source_path: Path) -> Optional[Path]:
        """Find actual migration target from migration logs"""
        log_dir = self.project_root
        source_str = str(source_path).lower()

        # Search for migration log files
        for log_file in log_dir.glob("migration_log*.txt"):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Look for target paths
                    if "<NAS_PRIMARY_IP>" in content or "MATT_Backups" in content:
                        # Extract target path
                        import re
                        patterns = [
                            r'\\\\10\.17\.17\.32[^\s\n]+',
                            r'Target[:\s]+(\\\\[^\s\n]+)',
                            r'Destination[:\s]+(\\\\[^\s\n]+)',
                        ]

                        for pattern in patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                target_str = matches[0] if isinstance(matches[0], str) else matches[0]
                                if "<NAS_PRIMARY_IP>" in target_str:
                                    # Build full target path
                                    # Target base is: \\<NAS_PRIMARY_IP>\backups\MATT_Backups\my_projects\
                                    # Source is: C:\Users\mlesn\Dropbox\my_projects\.lumina
                                    # So target should be: \\<NAS_PRIMARY_IP>\backups\MATT_Backups\my_projects\.lumina
                                    if "my_projects" in source_str:
                                        parts = source_path.parts
                                        if "my_projects" in parts:
                                            idx = parts.index("my_projects")
                                            # Get parts after my_projects (e.g., [".lumina"])
                                            relative_parts = parts[idx + 1:]
                                            target = Path(target_str)
                                            # target_str already includes my_projects, so just add relative parts
                                            for part in relative_parts:
                                                target = target / part
                                            return target
            except Exception as e:
                logger.debug(f"Error reading log {log_file}: {e}")

        return None

    def check_migration_status(self, source_path: Path) -> Dict[str, Any]:
        """Check migration status with actual target detection"""
        logger.info(f"🔍 Checking migration status: {source_path}")

        # First, try to find target from logs
        target_from_logs = self.find_migration_target_from_logs(source_path)

        if target_from_logs:
            logger.info(f"✅ Found target from logs: {target_from_logs}")
            # Check if target exists (may require authentication)
            try:
                if target_from_logs.exists():
                    logger.info(f"✅ Target exists - checking migration status")
                    status = self.tracker.check_migration_status(source_path, nas_target=target_from_logs)
                    return {
                        "status": status,
                        "target": target_from_logs,
                        "target_found": True,
                    }
                else:
                    logger.warning(f"⚠️  Target from logs doesn't exist or not accessible: {target_from_logs}")
                    logger.info(f"   (May require NAS authentication)")
            except Exception as e:
                logger.warning(f"⚠️  Cannot access target (may need authentication): {e}")
                # Still return the target even if we can't access it - user may need to authenticate
                return {
                    "status": None,
                    "target": target_from_logs,
                    "target_found": True,
                    "access_error": str(e),
                }

        # Fallback: use tracker's detection
        status = self.tracker.check_migration_status(source_path)
        return {
            "status": status,
            "target": Path(status.nas_target) if status.nas_target else None,
            "target_found": bool(status.nas_target),
        }

    def resume_migration_initiative(self, source_path: Path, dry_run: bool = False) -> bool:
        try:
            """Resume the complete NAS migration initiative"""
            logger.info("="*80)
            logger.info("🚀 RESUMING NAS MIGRATION INITIATIVE")
            logger.info("="*80)

            # Step 1: Check migration status
            migration_info = self.check_migration_status(source_path)
            status = migration_info.get("status")
            target = migration_info.get("target")
            access_error = migration_info.get("access_error")

            if status is None:
                logger.warning("⚠️  Cannot determine migration status - NAS may require authentication")
                if access_error:
                    logger.warning(f"   Error: {access_error}")
                logger.info("   Proceeding with target from logs...")
            else:
                logger.info(f"📋 Migration Status: {status.migration_status}")
                logger.info(f"   Source: {source_path}")
                logger.info(f"   Target: {target}")
                logger.info(f"   Progress: {status.size_migrated_gb:.2f} GB / {status.size_total_gb:.2f} GB")

            # Step 2: Determine if we can resume
            if status and status.migration_status == "complete":
                logger.info("✅ Migration already complete")
                return True

            # If status is None, we'll proceed anyway (user may need to authenticate)
            if status is None:
                logger.warning("⚠️  Migration status unknown - will attempt to resume anyway")
                logger.info("   Note: NAS authentication may be required")

            if not target:
                logger.error("❌ No migration target found - cannot resume")
                logger.info("   Attempting to find target from logs...")

                # Try known targets
                for known_target in self.known_targets:
                    if known_target.exists():
                        logger.info(f"✅ Found existing target: {known_target}")
                        target = known_target
                        break

                if not target:
                    logger.error("❌ Cannot find migration target")
                    return False

            # Step 3: Resume migration
            logger.info(f"🔄 Resuming migration to: {target}")

            if dry_run:
                logger.info("🔍 DRY RUN MODE - No files will be migrated")

            # Use resume function with target path
            success = resume_migration(str(source_path), dry_run=dry_run, nas_target_path=str(target) if target else None)

            if success:
                logger.info("✅ Migration resume completed")
            else:
                logger.error("❌ Migration resume failed")

            return success

        except Exception as e:
            self.logger.error(f"Error in resume_migration_initiative: {e}", exc_info=True)
            raise
    def resume_all_tasks(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            """Resume all associated migration tasks"""
            results = {
                "tasks_completed": [],
                "tasks_failed": [],
                "tasks_skipped": [],
            }

            # Task 1: Resume .lumina migration
            lumina_path = Path("C:/Users/mlesn/Dropbox/my_projects/.lumina")
            if lumina_path.exists():
                logger.info("📦 Task 1: Resuming .lumina migration")
                success = self.resume_migration_initiative(lumina_path, dry_run=dry_run)
                if success:
                    results["tasks_completed"].append(".lumina migration")
                else:
                    results["tasks_failed"].append(".lumina migration")
            else:
                results["tasks_skipped"].append(".lumina migration (path not found)")

            # Task 2: Resume my_projects migration (if needed)
            my_projects_path = Path("C:/Users/mlesn/Dropbox/my_projects")
            if my_projects_path.exists():
                logger.info("📦 Task 2: Checking my_projects migration")
                migration_info = self.check_migration_status(my_projects_path)
                if migration_info["status"].migration_status in ["interrupted", "partial"]:
                    success = self.resume_migration_initiative(my_projects_path, dry_run=dry_run)
                    if success:
                        results["tasks_completed"].append("my_projects migration")
                    else:
                        results["tasks_failed"].append("my_projects migration")
                else:
                    results["tasks_skipped"].append("my_projects migration (not interrupted)")

            return results


        except Exception as e:
            self.logger.error(f"Error in resume_all_tasks: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Resume NAS Migration Initiative")
        parser.add_argument("--path", type=str, help="Specific path to resume (default: .lumina)")
        parser.add_argument("--all", action="store_true", help="Resume all migration tasks")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")

        args = parser.parse_args()

        print("="*80)
        print("🚀 RESUME NAS MIGRATION INITIATIVE")
        print("="*80)
        print()

        initiative = NASMigrationInitiative()

        if args.all:
            print("🔄 Resuming all migration tasks...")
            results = initiative.resume_all_tasks(dry_run=args.dry_run)

            print()
            print("📊 RESULTS:")
            print(f"   Completed: {len(results['tasks_completed'])}")
            print(f"   Failed: {len(results['tasks_failed'])}")
            print(f"   Skipped: {len(results['tasks_skipped'])}")

            if results["tasks_completed"]:
                print("\n✅ Completed tasks:")
                for task in results["tasks_completed"]:
                    print(f"   - {task}")

            if results["tasks_failed"]:
                print("\n❌ Failed tasks:")
                for task in results["tasks_failed"]:
                    print(f"   - {task}")
        else:
            # Resume specific path
            if args.path:
                path = Path(args.path)
            else:
                path = Path("C:/Users/mlesn/Dropbox/my_projects/.lumina")

            print(f"🔄 Resuming migration for: {path}")
            success = initiative.resume_migration_initiative(path, dry_run=args.dry_run)

            if success:
                print("\n✅ Migration initiative resumed successfully")
            else:
                print("\n❌ Migration initiative resume failed")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()