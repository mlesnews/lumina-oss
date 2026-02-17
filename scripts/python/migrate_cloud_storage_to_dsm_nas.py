#!/usr/bin/env python3
"""
Migrate Cloud Storage Providers to DSM-Compounded Local Cloud Package

Migrates cloud storage provider files (Dropbox, OneDrive, etc.) from C drive to NAS
to free up C drive space. Targets the DSM-compounded local cloud package setup.

THE REAL @ASK: C drive at 90% utilization - migration is URGENT

@DOIT #SPACE-UTILIZATION #C-DRIVE #MIGRATION-URGENT #CLOUD-STORAGE #DSM #NAS
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json
import re
import threading
import time

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from cloud_nas_migration_tracker import CloudNASMigrationTracker
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"⚠️  Import error: {e}")

logger = get_logger("MigrateCloudToDSM")


class CloudStorageToDSMMigrator:
    """
    Migrate Cloud Storage Providers to DSM-Compounded Local Cloud Package

    Migrates files from cloud storage providers on C drive to NAS
    to free up critical C drive space.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize migrator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # Cloud storage paths on C drive
        self.cloud_paths = {
            "Dropbox": Path("C:/Users/mlesn/Dropbox"),
            "OneDrive": Path("C:/Users/mlesn/OneDrive"),
            "GoogleDrive": Path("C:/Users/mlesn/Google Drive"),
        }

        # NAS configuration (DSM-compounded local cloud package)
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_port = 5001  # DSM default
        self.nas_base_path = "/volume1/cloud_storage"  # DSM-compounded local cloud package

        # Progress tracking
        self.progress_file = self.project_root / "data" / "migration_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.migration_tracker = CloudNASMigrationTracker(project_root=self.project_root)

        # NAS integration (optional - for API-based operations)
        try:
            self.nas_integration = NASAzureVaultIntegration(
                nas_ip=self.nas_ip,
                nas_port=self.nas_port
            )
            logger.info("✅ NAS integration initialized")
        except Exception as e:
            logger.warning(f"⚠️  NAS integration not available: {e}")
            logger.info("   Will use robocopy with UNC paths instead")
            self.nas_integration = None

        logger.info("✅ Cloud Storage to DSM Migrator initialized")
        logger.info(f"   NAS: {self.nas_ip}:{self.nas_port}")
        logger.info(f"   Target: {self.nas_base_path}")

    def check_c_drive_space(self) -> Dict[str, Any]:
        """Check C drive space utilization - THE REAL @ASK"""
        try:
            import psutil
            c_drive = psutil.disk_usage("C:")
            used_gb = c_drive.used / (1024**3)
            free_gb = c_drive.free / (1024**3)
            total_gb = c_drive.total / (1024**3)
            used_percent = (c_drive.used / c_drive.total) * 100

            status = "CRITICAL" if used_percent >= 90 else "WARNING" if used_percent >= 80 else "OK"

            return {
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
                "status": status,
                "migration_urgent": used_percent >= 90
            }
        except Exception as e:
            logger.error(f"❌ Error checking C drive space: {e}")
            return {"error": str(e)}

    def detect_cloud_storage_on_c_drive(self) -> List[Dict[str, Any]]:
        """Detect cloud storage providers on C drive"""
        logger.info("🔍 Detecting cloud storage providers on C drive...")

        detected = []
        for name, path in self.cloud_paths.items():
            if path.exists():
                try:
                    # Get directory size
                    ps_command = f"""
                    $path = '{path}'
                    $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                    $sizeGB = [math]::Round($size / 1GB, 2)
                    $fileCount = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue).Count

                    @{{
                        size_gb = $sizeGB
                        file_count = $fileCount
                    }} | ConvertTo-Json
                    """

                    result = subprocess.run(
                        ["powershell", "-Command", ps_command],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        size_data = json.loads(result.stdout)
                        detected.append({
                            "name": name,
                            "path": str(path),
                            "size_gb": size_data.get("size_gb", 0),
                            "file_count": size_data.get("file_count", 0),
                            "exists": True
                        })
                        logger.info(f"   ✅ {name}: {size_data.get('size_gb', 0)} GB ({size_data.get('file_count', 0):,} files)")
                    else:
                        detected.append({
                            "name": name,
                            "path": str(path),
                            "exists": True,
                            "size_unknown": True
                        })
                        logger.info(f"   ⚠️  {name}: Size calculation failed")
                except Exception as e:
                    logger.warning(f"   ⚠️  Error checking {name}: {e}")
                    detected.append({
                        "name": name,
                        "path": str(path),
                        "exists": True,
                        "error": str(e)
                    })
            else:
                logger.info(f"   ℹ️  {name}: Not found on C drive")

        return detected

    def calculate_nas_target_path(self, cloud_provider: str, source_path: Path) -> str:
        """Calculate NAS target path for cloud storage"""
        # Extract relative path from cloud provider root
        if cloud_provider == "Dropbox":
            # Dropbox structure: C:/Users/mlesn/Dropbox/my_projects -> /volume1/cloud_storage/Dropbox/my_projects
            relative = source_path.relative_to(self.cloud_paths["Dropbox"])
            return f"{self.nas_base_path}/Dropbox/{relative}"
        elif cloud_provider == "OneDrive":
            relative = source_path.relative_to(self.cloud_paths["OneDrive"])
            return f"{self.nas_base_path}/OneDrive/{relative}"
        elif cloud_provider == "GoogleDrive":
            relative = source_path.relative_to(self.cloud_paths["GoogleDrive"])
            return f"{self.nas_base_path}/GoogleDrive/{relative}"
        else:
            # Default: use provider name
            return f"{self.nas_base_path}/{cloud_provider}/{source_path.name}"

    def count_files_in_directory(self, directory: Path) -> int:
        """Count total files in directory recursively"""
        try:
            count = 0
            for item in directory.rglob("*"):
                if item.is_file():
                    count += 1
            return count
        except Exception as e:
            logger.warning(f"   ⚠️  Error counting files: {e}")
            return 0

    def write_progress(self, progress_data: Dict[str, Any]):
        """Write progress to JSON file for real-time monitoring"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.debug(f"Error writing progress: {e}")

    def parse_robocopy_log(self, log_content: str) -> Dict[str, Any]:
        """Parse robocopy log output for progress information"""
        stats = {
            "total_files": 0,
            "copied_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "total_dirs": 0,
            "copied_dirs": 0,
            "bytes_copied": 0
        }

        # Parse file statistics: "Files :    12345    12340        5        0"
        file_match = re.search(r"Files\s+:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", log_content)
        if file_match:
            stats["total_files"] = int(file_match.group(1))
            stats["copied_files"] = int(file_match.group(2))
            stats["skipped_files"] = int(file_match.group(3))
            stats["failed_files"] = int(file_match.group(4))

        # Parse directory statistics
        dir_match = re.search(r"Dirs\s+:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", log_content)
        if dir_match:
            stats["total_dirs"] = int(dir_match.group(1))
            stats["copied_dirs"] = int(dir_match.group(2))

        # Parse bytes: "Bytes : 1234567890 1234567890 0 0"
        bytes_match = re.search(r"Bytes\s+:\s+([\d.]+)\s+([\d.]+)", log_content)
        if bytes_match:
            stats["bytes_copied"] = int(float(bytes_match.group(2)))

        return stats

    def migrate_cloud_storage_to_nas(
        self,
        source_path: Path,
        cloud_provider: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Migrate cloud storage to NAS using robocopy with full progress tracking

        Uses robocopy for maximum speed and resume capability
        Provides real-time progress: total files, current file, percentage, ETA
        """
        logger.info(f"🚀 Migrating {cloud_provider} to NAS...")
        logger.info(f"   Source: {source_path}")

        # Calculate NAS target
        nas_target = self.calculate_nas_target_path(cloud_provider, source_path)
        logger.info(f"   Target: {nas_target}")

        if dry_run:
            logger.info("   🔍 DRY RUN - No files will be migrated")
            return {
                "success": True,
                "dry_run": True,
                "source": str(source_path),
                "target": nas_target
            }

        # COUNT TOTAL FILES BEFORE MIGRATION
        logger.info("   📊 Counting total files to migrate...")
        total_files = self.count_files_in_directory(source_path)
        logger.info(f"   📁 Total files to migrate: {total_files:,}")

        # Use robocopy for migration
        # Map NAS path to Windows network drive if needed
        # For now, use UNC path: \\<NAS_PRIMARY_IP>\cloud_storage\...
        nas_unc = f"\\\\{self.nas_ip}\\cloud_storage"

        # Extract relative path for UNC
        if cloud_provider == "Dropbox":
            relative = source_path.relative_to(self.cloud_paths["Dropbox"])
            unc_target = f"{nas_unc}\\Dropbox\\{relative}"
        else:
            unc_target = f"{nas_unc}\\{cloud_provider}\\{source_path.name}"

        logger.info(f"   UNC Target: {unc_target}")

        # Create target directory structure
        try:
            target_dir = Path(unc_target).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"   ✅ Target directory created/verified")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not create target directory: {e}")
            # Continue anyway - robocopy will create it

        # Create robocopy log file for progress parsing
        log_file = self.project_root / "data" / f"robocopy_{cloud_provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Robocopy parameters for migration WITH PROGRESS TRACKING
        robocopy_args = [
            str(source_path),
            str(unc_target),
            "/MT:16",  # Multi-threaded (16 threads)
            "/R:3",    # Retry 3 times
            "/W:5",    # Wait 5 seconds between retries
            "/Z",      # Copy in restartable mode (resume capability)
            "/J",      # Copy using unbuffered I/O
            "/DCOPY:T", # Copy directory timestamps
            "/COPYALL", # Copy all file info
            "/MIR",    # Mirror (copy all files)
            "/LOG+:" + str(log_file),  # Log to file (append mode)
            "/TEE",    # Output to console AND log
        ]

        logger.info("   🔄 Starting robocopy migration...")
        logger.info(f"   📝 Progress log: {log_file}")
        logger.info(f"   📊 Total files: {total_files:,}")
        logger.info("")

        # Initialize progress tracking
        start_time = datetime.now()
        progress_data = {
            "status": "running",
            "cloud_provider": cloud_provider,
            "source": str(source_path),
            "target": unc_target,
            "total_files": total_files,
            "current_file": 0,
            "copied_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "percentage": 0.0,
            "eta_seconds": 0,
            "eta_formatted": "Calculating...",
            "start_time": start_time.isoformat(),
            "elapsed_seconds": 0,
            "speed_files_per_second": 0.0,
            "bytes_copied": 0,
            "bytes_total": 0
        }
        self.write_progress(progress_data)

        # Start robocopy process
        try:
            process = subprocess.Popen(
                ["robocopy"] + robocopy_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Monitor progress by parsing log file
            last_log_size = 0
            last_update_time = time.time()

            while process.poll() is None:
                # Read log file for progress
                try:
                    if log_file.exists():
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()

                        # Parse log for current progress
                        stats = self.parse_robocopy_log(log_content)

                        # Update progress
                        copied = stats.get("copied_files", 0)
                        skipped = stats.get("skipped_files", 0)
                        current_file = copied + skipped
                        progress_data["copied_files"] = copied
                        progress_data["skipped_files"] = skipped
                        progress_data["current_file"] = current_file

                        # Calculate percentage
                        if total_files > 0:
                            progress_data["percentage"] = round((current_file / total_files) * 100, 2)
                        else:
                            progress_data["percentage"] = 0.0

                        # Calculate ETA
                        elapsed = (datetime.now() - start_time).total_seconds()
                        progress_data["elapsed_seconds"] = round(elapsed, 1)

                        if current_file > 0 and elapsed > 0:
                            speed = current_file / elapsed
                            progress_data["speed_files_per_second"] = round(speed, 2)

                            remaining_files = total_files - current_file
                            if speed > 0:
                                eta_seconds = remaining_files / speed
                                progress_data["eta_seconds"] = round(eta_seconds, 0)
                                eta_timedelta = timedelta(seconds=int(eta_seconds))
                                hours = eta_timedelta.seconds // 3600
                                minutes = (eta_timedelta.seconds % 3600) // 60
                                seconds = eta_timedelta.seconds % 60
                                if hours > 0:
                                    progress_data["eta_formatted"] = f"{hours}h {minutes}m {seconds}s"
                                elif minutes > 0:
                                    progress_data["eta_formatted"] = f"{minutes}m {seconds}s"
                                else:
                                    progress_data["eta_formatted"] = f"{seconds}s"
                            else:
                                progress_data["eta_formatted"] = "Calculating..."
                        else:
                            progress_data["eta_formatted"] = "Calculating..."

                        # Update bytes
                        progress_data["bytes_copied"] = stats.get("bytes_copied", 0)

                        # Write progress every second
                        if time.time() - last_update_time >= 1.0:
                            self.write_progress(progress_data)
                            last_update_time = time.time()

                            # Log progress
                            logger.info(
                                f"   📊 Progress: {progress_data['current_file']:,}/{progress_data['total_files']:,} "
                                f"files ({progress_data['percentage']:.1f}%) | "
                                f"ETA: {progress_data['eta_formatted']} | "
                                f"Speed: {progress_data['speed_files_per_second']:.1f} files/sec"
                            )
                except Exception as e:
                    logger.debug(f"Error reading progress: {e}")

                time.sleep(0.5)  # Check every 500ms

            # Get final result
            return_code = process.returncode

            # Read final log
            final_stats = {}
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                final_stats = self.parse_robocopy_log(log_content)

            # Final progress update
            elapsed = (datetime.now() - start_time).total_seconds()
            progress_data.update({
                "status": "completed" if return_code <= 7 else "failed",
                "copied_files": final_stats.get("copied_files", 0),
                "skipped_files": final_stats.get("skipped_files", 0),
                "current_file": final_stats.get("copied_files", 0) + final_stats.get("skipped_files", 0),
                "percentage": 100.0 if return_code <= 7 else progress_data.get("percentage", 0),
                "elapsed_seconds": round(elapsed, 1),
                "eta_formatted": "Complete" if return_code <= 7 else "Failed",
                "exit_code": return_code
            })
            self.write_progress(progress_data)

            # Robocopy exit codes: 0-7 are success, 8+ are errors
            if return_code <= 7:
                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
                logger.info("=" * 80)
                logger.info(f"   Total files: {total_files:,}")
                logger.info(f"   Copied: {final_stats.get('copied_files', 0):,}")
                logger.info(f"   Skipped: {final_stats.get('skipped_files', 0):,}")
                logger.info(f"   Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
                logger.info(f"   Average speed: {progress_data.get('speed_files_per_second', 0):.1f} files/sec")
                logger.info("=" * 80)
                return {
                    "success": True,
                    "source": str(source_path),
                    "target": unc_target,
                    "exit_code": return_code,
                    "total_files": total_files,
                    "copied_files": final_stats.get("copied_files", 0),
                    "skipped_files": final_stats.get("skipped_files", 0),
                    "elapsed_seconds": elapsed
                }
            else:
                logger.error("")
                logger.error("=" * 80)
                logger.error("❌ MIGRATION FAILED")
                logger.error("=" * 80)
                logger.error(f"   Exit code: {return_code}")
                logger.error(f"   Check log file: {log_file}")
                logger.error("=" * 80)
                return {
                    "success": False,
                    "source": str(source_path),
                    "target": unc_target,
                    "exit_code": return_code,
                    "error": f"Robocopy exit code: {return_code}",
                    "log_file": str(log_file)
                }
        except Exception as e:
            logger.error(f"   ❌ Migration error: {e}", exc_info=True)
            progress_data["status"] = "error"
            progress_data["error"] = str(e)
            self.write_progress(progress_data)
            return {
                "success": False,
                "source": str(source_path),
                "target": unc_target,
                "error": str(e)
            }

    def cleanup_dropbox_before_migration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Cleanup Dropbox nested inception and duplicates before migration"""
        logger.info("🧹 Cleaning up Dropbox before migration...")
        logger.info("   Handling nested Dropbox inception and duplicates")

        try:
            from cleanup_dropbox_before_migration import DropboxCleanup

            dropbox_path = Path("C:/Users/mlesn/Dropbox")
            if not dropbox_path.exists():
                logger.warning("⚠️  Dropbox path not found")
                return {"success": False, "error": "Dropbox path not found"}

            cleanup = DropboxCleanup(dropbox_path=dropbox_path, dry_run=dry_run)
            results = cleanup.cleanup_dropbox()

            logger.info(f"   ✅ Cleanup complete - freed {results.get('total_space_freed_gb', 0):.2f} GB")
            return results

        except ImportError:
            logger.warning("⚠️  Dropbox cleanup module not available")
            return {"success": False, "error": "Cleanup module not available"}
        except Exception as e:
            logger.error(f"❌ Dropbox cleanup error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def migrate_all_cloud_storage(self, dry_run: bool = False, cleanup_dropbox: bool = True) -> Dict[str, Any]:
        try:
            """
            Migrate all cloud storage providers to NAS

            Prioritizes based on C drive space utilization
            """
            logger.info("=" * 80)
            logger.info("🚀 MIGRATE CLOUD STORAGE TO DSM-COMPOUNDED LOCAL CLOUD PACKAGE")
            logger.info("=" * 80)
            logger.info("   THE REAL @ASK: C drive at 90% utilization - migration is URGENT")
            logger.info("")

            # Check C drive space
            space_info = self.check_c_drive_space()
            logger.info("📊 C DRIVE SPACE STATUS")
            logger.info(f"   Used: {space_info.get('used_gb', 0)} GB ({space_info.get('used_percent', 0)}%)")
            logger.info(f"   Free: {space_info.get('free_gb', 0)} GB")
            logger.info(f"   Status: {space_info.get('status', 'UNKNOWN')}")
            logger.info("")

            if space_info.get("migration_urgent"):
                logger.error("🚨 CRITICAL: C drive at 90%+ utilization - MIGRATION IS URGENT")
                logger.error("   Files must be migrated to NAS immediately")
                logger.info("")

            # Detect cloud storage
            cloud_storage = self.detect_cloud_storage_on_c_drive()

            if not cloud_storage:
                logger.warning("⚠️  No cloud storage providers detected on C drive")
                return {
                    "success": False,
                    "error": "No cloud storage providers detected"
                }

            logger.info(f"📁 Detected {len(cloud_storage)} cloud storage provider(s)")
            logger.info("")

            # Cleanup Dropbox before migration (if requested and Dropbox detected)
            if cleanup_dropbox:
                dropbox_provider = next((p for p in cloud_storage if p["name"] == "Dropbox"), None)
                if dropbox_provider and dropbox_provider.get("exists"):
                    logger.info("🧹 Step 1: Cleaning up Dropbox (nested inception & duplicates)...")
                    cleanup_result = self.cleanup_dropbox_before_migration(dry_run=dry_run)
                    if cleanup_result.get("success"):
                        logger.info("   ✅ Dropbox cleanup complete")
                    else:
                        logger.warning(f"   ⚠️  Dropbox cleanup had issues: {cleanup_result.get('error')}")
                    logger.info("")

            # Sort by size (largest first) to maximize space freed
            cloud_storage.sort(key=lambda x: x.get("size_gb", 0), reverse=True)

            results = {
                "timestamp": datetime.now().isoformat(),
                "c_drive_space": space_info,
                "cloud_storage_detected": cloud_storage,
                "migrations": [],
                "total_space_freed_gb": 0,
                "success": True
            }

            # Migrate each cloud storage provider
            for provider in cloud_storage:
                if not provider.get("exists"):
                    continue

                provider_name = provider["name"]
                provider_path = Path(provider["path"])
                size_gb = provider.get("size_gb", 0)

                # Special handling for Dropbox: cleanup first
                if provider_name == "Dropbox" and cleanup_dropbox:
                    logger.info(f"🧹 Cleaning up {provider_name} before migration...")
                    cleanup_result = self.cleanup_dropbox_before_migration(
                        dropbox_path=provider_path,
                        dry_run=dry_run
                    )
                    logger.info("")

                logger.info(f"🔄 Migrating {provider_name} ({size_gb} GB)...")

                # Migrate
                migration_result = self.migrate_cloud_storage_to_nas(
                    source_path=provider_path,
                    cloud_provider=provider_name,
                    dry_run=dry_run
                )

                results["migrations"].append({
                    "provider": provider_name,
                    "source": str(provider_path),
                    "size_gb": size_gb,
                    "result": migration_result
                })

                if migration_result.get("success"):
                    results["total_space_freed_gb"] += size_gb
                    logger.info(f"   ✅ {provider_name} migration completed")
                else:
                    results["success"] = False
                    logger.error(f"   ❌ {provider_name} migration failed")

                logger.info("")

            # Summary
            logger.info("=" * 80)
            logger.info("📊 MIGRATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"   Cloud Storage Providers: {len(cloud_storage)}")
            logger.info(f"   Successful Migrations: {sum(1 for m in results['migrations'] if m['result'].get('success'))}")
            logger.info(f"   Total Space to Free: {results['total_space_freed_gb']:.2f} GB")
            logger.info("=" * 80)

            return results


        except Exception as e:
            self.logger.error(f"Error in migrate_all_cloud_storage: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate Cloud Storage to DSM-Compounded Local Cloud Package"
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")
    parser.add_argument("--check-space", action="store_true", help="Only check C drive space")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip Dropbox cleanup (not recommended)")
    parser.add_argument("--skip-dropbox-cleanup", action="store_true", help="Skip Dropbox cleanup before migration")

    args = parser.parse_args()

    migrator = CloudStorageToDSMMigrator()

    if args.check_space:
        space_info = migrator.check_c_drive_space()
        print("\n" + "=" * 80)
        print("📊 C DRIVE SPACE STATUS")
        print("=" * 80)
        print(f"Used: {space_info.get('used_gb', 0)} GB ({space_info.get('used_percent', 0)}%)")
        print(f"Free: {space_info.get('free_gb', 0)} GB")
        print(f"Total: {space_info.get('total_gb', 0)} GB")
        print(f"Status: {space_info.get('status', 'UNKNOWN')}")
        if space_info.get("migration_urgent"):
            print("\n🚨 CRITICAL: Migration is URGENT - C drive at 90%+ utilization")
        print("=" * 80)
    else:
        results = migrator.migrate_all_cloud_storage(
            dry_run=args.dry_run,
            cleanup_dropbox=not args.skip_dropbox_cleanup
        )

        if not results.get("success"):
            sys.exit(1)

    return 0


if __name__ == "__main__":


    sys.exit(main())