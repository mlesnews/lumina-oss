#!/usr/bin/env python3
"""
Execute Cloud Storage Migration to NAS
Migrates Dropbox and OneDrive directly to NAS unified cloud storage.

Uses robocopy with UNC paths - no DSM API required.
Implements automatic sync prevention and dynamic scaling.

Tags: #CLOUD_STORAGE #MIGRATION #NAS #DOIT
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
    from stop_cloud_storage_clients import CloudStorageClientStopper, DynamicScalingModule
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"⚠️  Import error: {e}")

logger = get_logger("ExecuteCloudStorageMigration")


class CloudStorageMigrator:
    """Execute cloud storage migration to NAS"""

    def __init__(self):
        self.project_root = project_root
        self.nas_ip = "<NAS_PRIMARY_IP>"
        # Use the actual NAS share path (backups, not cloud_storage)
        self.nas_base = f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\cloud_storage"
        self.scaling = DynamicScalingModule(base_wait=5.0)

        # Cloud storage paths
        self.cloud_paths = {
            "Dropbox": Path("C:/Users/mlesn/Dropbox"),
            "OneDrive": Path("C:/Users/mlesn/OneDrive"),
        }

        # NAS integration for authentication
        try:
            self.nas_integration = NASAzureVaultIntegration(nas_ip=self.nas_ip)
        except Exception as e:
            logger.warning(f"NAS integration not available: {e}")
            self.nas_integration = None

    def authenticate_nas(self):
        """Authenticate to NAS if needed"""
        if self.nas_integration:
            try:
                creds = self.nas_integration.get_nas_credentials()
                if creds:
                    username = creds.get("username")
                    password = creds.get("password")
                    # COMPUSEC: pipe password via stdin to avoid process-list exposure
                    proc = subprocess.Popen(
                        ["net", "use", str(self.nas_base), f"/user:{username}", "/persistent:no"],
                        stdin=subprocess.PIPE, capture_output=True, text=True
                    )
                    stdout, stderr = proc.communicate(input=password, timeout=10)
                    result = type('Result', (), {'returncode': proc.returncode})()
                    if result.returncode == 0:
                        logger.info("✅ NAS authenticated")
                    else:
                        logger.warning("⚠️  NAS authentication may have failed, but continuing...")
            except Exception as e:
                logger.warning(f"NAS authentication warning: {e}")

    def migrate_cloud_storage(self, provider: str, source_path: Path, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate cloud storage to NAS"""
        logger.info("=" * 80)
        logger.info(f"🚀 MIGRATING {provider.upper()} TO NAS UNIFIED CLOUD STORAGE")
        logger.info("=" * 80)
        logger.info(f"Source: {source_path}")

        if not source_path.exists():
            logger.error(f"❌ Source path does not exist: {source_path}")
            return {"success": False, "error": "Source path does not exist"}

        # Calculate NAS target
        nas_target = f"{self.nas_base}\\{provider}"
        logger.info(f"Target: {nas_target}")
        logger.info("")

        if dry_run:
            logger.info("🔍 DRY RUN MODE - No files will be migrated")
            return {
                "success": True,
                "dry_run": True,
                "source": str(source_path),
                "target": nas_target
            }

        # Authenticate to NAS
        logger.info("🔐 Authenticating to NAS...")
        self.authenticate_nas()
        logger.info("")

        # Create target directory
        try:
            target_path = Path(nas_target)
            target_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Target directory ready: {nas_target}")
        except Exception as e:
            logger.warning(f"⚠️  Could not create target directory (may already exist): {e}")

        logger.info("")
        logger.info("📦 Starting migration with robocopy...")
        logger.info("   This may take a while for large directories...")
        logger.info("")

        # Robocopy command
        robocopy_args = [
            str(source_path),
            nas_target,
            "/E",      # Copy subdirectories
            "/MT:16",  # Multi-threaded (16 threads)
            "/R:3",    # Retry 3 times
            "/W:5",    # Wait 5 seconds between retries
            "/Z",      # Restartable mode
            "/J",      # Unbuffered I/O
            "/COPYALL", # Copy all file info
            "/MIR",    # Mirror (copy all files)
            "/NP",     # No progress (cleaner output)
            "/NFL",    # No file list
            "/NDL",    # No directory list
        ]

        try:
            # Start robocopy
            process = subprocess.Popen(
                ["robocopy"] + robocopy_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logger.info(f"   🔄 Migration in progress (PID: {process.pid})")
            logger.info("   💡 You can monitor progress in Task Manager")
            logger.info("   💡 Migration will continue in background")
            logger.info("")

            # Wait a bit to see if it starts successfully
            import time
            time.sleep(2)

            if process.poll() is None:
                logger.info("   ✅ Migration started successfully")
                logger.info("   ⏳ Migration will continue running...")
                return {
                    "success": True,
                    "source": str(source_path),
                    "target": nas_target,
                    "pid": process.pid,
                    "status": "running"
                }
            else:
                # Process finished quickly (might be error or nothing to copy)
                stdout, stderr = process.communicate()
                return_code = process.returncode

                # Robocopy returns 0-7 for success
                if return_code <= 7:
                    logger.info("   ✅ Migration completed")
                    return {
                        "success": True,
                        "source": str(source_path),
                        "target": nas_target,
                        "exit_code": return_code
                    }
                else:
                    logger.error(f"   ❌ Migration failed (exit code: {return_code})")
                    return {
                        "success": False,
                        "source": str(source_path),
                        "target": nas_target,
                        "exit_code": return_code,
                        "error": f"Robocopy exit code: {return_code}"
                    }

        except Exception as e:
            logger.error(f"   ❌ Migration error: {e}", exc_info=True)
            return {
                "success": False,
                "source": str(source_path),
                "target": nas_target,
                "error": str(e)
            }

    def execute_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            """Execute complete cloud storage migration"""
            logger.info("=" * 80)
            logger.info("🚀 EXECUTE CLOUD STORAGE MIGRATION TO NAS")
            logger.info("=" * 80)
            logger.info("   Migrating to: NAS Unified Cloud Storage")
            logger.info("   Target: \\\\<NAS_PRIMARY_IP>\\cloud_storage\\")
            logger.info("")

            # Verify clients are stopped
            logger.info("🔍 Verifying cloud storage clients are stopped...")
            stopper = CloudStorageClientStopper()
            running = stopper.check_running_processes()

            if running:
                logger.warning(f"⚠️  Warning: {len(running)} cloud storage client(s) still running")
                logger.warning("   Migration will proceed, but clients may interfere")
                logger.info("")
            else:
                logger.info("   ✅ No cloud storage clients running")
                logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "migrations": [],
                "total_providers": 0,
                "successful": 0,
                "failed": 0
            }

            # Migrate OneDrive first (smaller, faster)
            if self.cloud_paths["OneDrive"].exists():
                logger.info("📦 Migrating OneDrive...")
                result = self.migrate_cloud_storage("OneDrive", self.cloud_paths["OneDrive"], dry_run=dry_run)
                results["migrations"].append({
                    "provider": "OneDrive",
                    "result": result
                })
                results["total_providers"] += 1
                if result.get("success"):
                    results["successful"] += 1
                else:
                    results["failed"] += 1

                # Dynamic wait between migrations
                if not dry_run and results["total_providers"] > 0:
                    logger.info("   ⏳ Waiting before next migration...")
                    self.scaling.wait({"migrations": results["total_providers"]})
                logger.info("")

            # Migrate Dropbox (larger, may take longer)
            if self.cloud_paths["Dropbox"].exists():
                logger.info("📦 Migrating Dropbox...")
                result = self.migrate_cloud_storage("Dropbox", self.cloud_paths["Dropbox"], dry_run=dry_run)
                results["migrations"].append({
                    "provider": "Dropbox",
                    "result": result
                })
                results["total_providers"] += 1
                if result.get("success"):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                logger.info("")

            # Summary
            logger.info("=" * 80)
            logger.info("📊 MIGRATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total Providers: {results['total_providers']}")
            logger.info(f"Successful: {results['successful']}")
            logger.info(f"Failed: {results['failed']}")
            logger.info("=" * 80)
            logger.info("")
            logger.info("✅ Cloud storage migration initiated")
            logger.info("   All files will be available at: \\\\<NAS_PRIMARY_IP>\\cloud_storage\\")
            logger.info("")

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_migration: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Execute Cloud Storage Migration to NAS")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")

        args = parser.parse_args()

        migrator = CloudStorageMigrator()
        results = migrator.execute_migration(dry_run=args.dry_run)

        # Save results
        results_file = project_root / "data" / "system" / f"cloud_storage_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Results saved to: {results_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()