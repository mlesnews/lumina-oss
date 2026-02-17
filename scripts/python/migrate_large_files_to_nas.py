#!/usr/bin/env python3
"""
Migrate Large Files to NAS
Executes migration of identified large files and directories to NAS.

Tags: #NAS #MIGRATION #STORAGE #DOIT
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    NASAzureVaultIntegration = None

logger = get_logger("MigrateLargeFilesToNAS")


class LargeFileMigrator:
    """Migrate large files to NAS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nas_base = r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups"
        self.nas_integration = None

        if NASAzureVaultIntegration:
            try:
                self.nas_integration = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
            except Exception as e:
                logger.warning(f"NAS integration not available: {e}")

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
                    proc.communicate(input=password, timeout=10)
                    logger.info("NAS authenticated")
            except Exception as e:
                logger.warning(f"NAS authentication warning: {e}")

    def migrate_directory(self, source: Path, target: str, priority: str = "MEDIUM") -> Dict[str, Any]:
        """Migrate a directory to NAS"""
        logger.info(f"📦 Migrating: {source.name} ({priority} priority)")
        logger.info(f"   Source: {source}")
        logger.info(f"   Target: {target}")

        result = {
            "source": str(source),
            "target": target,
            "status": "PENDING",
            "size_gb": 0.0,
            "error": None
        }

        if not source.exists():
            result["status"] = "SKIPPED"
            result["error"] = "Source does not exist"
            return result

        try:
            # Ensure target directory exists
            target_path = Path(target)
            target_path.mkdir(parents=True, exist_ok=True)

            # Use robocopy for reliable migration
            robocopy_cmd = [
                "robocopy",
                str(source),
                str(target_path),
                "/E",  # Copy subdirectories
                "/R:3",  # Retry 3 times
                "/W:5",  # Wait 5 seconds
                "/MT:8",  # Multi-threaded
                "/NP",  # No progress (cleaner output)
                "/NFL",  # No file list
                "/NDL",  # No directory list
            ]

            logger.info(f"   Executing robocopy...")
            process = subprocess.run(
                robocopy_cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            # Robocopy returns 0-7 for success, 8+ for errors
            if process.returncode < 8:
                result["status"] = "SUCCESS"
                logger.info(f"   ✅ Migration successful")
            else:
                result["status"] = "PARTIAL"
                result["error"] = f"Robocopy exit code: {process.returncode}"
                logger.warning(f"   ⚠️  Partial migration (exit code: {process.returncode})")

        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["error"] = "Migration timed out"
            logger.error(f"   ❌ Migration timed out")
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            logger.error(f"   ❌ Migration error: {e}", exc_info=True)

        return result

    def migrate_file(self, source: Path, target: str) -> Dict[str, Any]:
        """Migrate a single file to NAS"""
        logger.info(f"📄 Migrating file: {source.name}")
        logger.info(f"   Source: {source}")
        logger.info(f"   Target: {target}")

        result = {
            "source": str(source),
            "target": target,
            "status": "PENDING",
            "error": None
        }

        if not source.exists():
            result["status"] = "SKIPPED"
            result["error"] = "Source does not exist"
            return result

        try:
            target_path = Path(target)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Use robocopy for single file
            robocopy_cmd = [
                "robocopy",
                str(source.parent),
                str(target_path.parent),
                source.name,
                "/R:3",
                "/W:5",
            ]

            process = subprocess.run(
                robocopy_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for files
            )

            if process.returncode < 8:
                result["status"] = "SUCCESS"
                logger.info(f"   ✅ File migration successful")
            else:
                result["status"] = "ERROR"
                result["error"] = f"Robocopy exit code: {process.returncode}"
                logger.error(f"   ❌ File migration failed")

        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            logger.error(f"   ❌ File migration error: {e}", exc_info=True)

        return result

    def migrate_from_report(self, report_path: Path, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate files based on migration candidates report"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 MIGRATING LARGE FILES TO NAS")
            logger.info("=" * 80)

            if not report_path.exists():
                logger.error(f"❌ Report file not found: {report_path}")
                return {"error": "Report file not found"}

            # Load report
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)

            logger.info(f"📊 Loaded report: {report['summary']['total_candidates']} candidates")
            logger.info(f"   Total size: {report['summary']['total_size_gb']:.2f} GB")

            if dry_run:
                logger.info("🔍 DRY RUN MODE - No files will be migrated")

            # Authenticate to NAS
            if not dry_run:
                self.authenticate_nas()

            migration_results = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "directories": [],
                "files": [],
                "project_data": [],
                "summary": {
                    "total_migrated": 0,
                    "total_success": 0,
                    "total_failed": 0,
                    "total_size_gb": 0.0
                }
            }

            # Migrate HIGH priority directories first
            high_priority_dirs = [d for d in report.get("directories", []) if d.get("priority") == "HIGH"]
            medium_priority_dirs = [d for d in report.get("directories", []) if d.get("priority") == "MEDIUM"]

            # Migrate project data (HIGH priority)
            high_priority_data = [d for d in report.get("project_data", []) if d.get("priority") == "HIGH"]
            medium_priority_data = [d for d in report.get("project_data", []) if d.get("priority") == "MEDIUM"]

            logger.info(f"\n📦 Migrating {len(high_priority_dirs + high_priority_data)} HIGH priority items...")

            # Migrate HIGH priority items
            for item in high_priority_dirs + high_priority_data:
                if dry_run:
                    logger.info(f"   [DRY RUN] Would migrate: {item['path']}")
                    migration_results["directories"].append({
                        "source": item["path"],
                        "target": item["target"],
                        "status": "DRY_RUN"
                    })
                else:
                    result = self.migrate_directory(
                        Path(item["path"]),
                        item["target"],
                        item.get("priority", "MEDIUM")
                    )
                    migration_results["directories"].append(result)
                    if result["status"] == "SUCCESS":
                        migration_results["summary"]["total_success"] += 1
                    else:
                        migration_results["summary"]["total_failed"] += 1

            # Migrate large files
            logger.info(f"\n📄 Migrating {len(report.get('files', []))} large files...")
            for item in report.get("files", [])[:10]:  # Top 10 files
                if dry_run:
                    logger.info(f"   [DRY RUN] Would migrate: {item['path']}")
                    migration_results["files"].append({
                        "source": item["path"],
                        "target": item["target"],
                        "status": "DRY_RUN"
                    })
                else:
                    result = self.migrate_file(Path(item["path"]), item["target"])
                    migration_results["files"].append(result)
                    if result["status"] == "SUCCESS":
                        migration_results["summary"]["total_success"] += 1
                    else:
                        migration_results["summary"]["total_failed"] += 1

            migration_results["summary"]["total_migrated"] = len(migration_results["directories"]) + len(migration_results["files"])

            logger.info("\n" + "=" * 80)
            logger.info("📊 MIGRATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total migrated: {migration_results['summary']['total_migrated']}")
            logger.info(f"Successful: {migration_results['summary']['total_success']}")
            logger.info(f"Failed: {migration_results['summary']['total_failed']}")
            logger.info("=" * 80)

            return migration_results


        except Exception as e:
            logger.error(f"Error in migrate_from_report: {e}", exc_info=True)
            raise

def main():
    """Main function"""
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Migrate large files to NAS")
        parser.add_argument("--report", type=str, help="Path to migration candidates report JSON")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")

        args = parser.parse_args()

        # Find latest report if not specified
        if args.report:
            report_path = Path(args.report)
        else:
            system_dir = project_root / "data" / "system"
            reports = sorted(system_dir.glob("nas_migration_candidates_*.json"), reverse=True)
            if reports:
                report_path = reports[0]
                logger.info(f"Using latest report: {report_path}")
            else:
                logger.error("No migration report found. Run find_large_files_for_nas.py first.")
                return

        migrator = LargeFileMigrator(project_root)
        results = migrator.migrate_from_report(report_path, dry_run=args.dry_run)

        # Save results
        results_file = project_root / "data" / "system" / f"nas_migration_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Results saved to: {results_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()