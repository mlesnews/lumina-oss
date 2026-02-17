#!/usr/bin/env python3
"""
Resume Interrupted Migration

Resumes interrupted migrations from where they left off.
Handles: initial start, partial completion, interrupted by change/tasks.

Tags: #MIGRATION #RESUME #INTERRUPTED #AUTOMATION @JARVIS @TEAM
"""

import sys
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from cloud_nas_migration_tracker import CloudNASMigrationTracker
    from comprehensive_storage_migration_manager import ComprehensiveStorageMigrationManager
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ResumeMigration")


def resume_migration(source_path: str, dry_run: bool = False, nas_target_path: Optional[str] = None):
    """Resume interrupted migration - ACTUAL IMPLEMENTATION"""
    source = Path(source_path)

    if not source.exists():
        print(f"❌ Source path does not exist: {source}")
        return False

    print("\n" + "="*80)
    print("🔄 RESUMING INTERRUPTED MIGRATION")
    print("="*80 + "\n")

    # Check migration status (if target not provided)
    tracker = CloudNASMigrationTracker()

    if nas_target_path:
        # Use provided target path (from logs, etc.)
        nas_target = Path(nas_target_path)
        print(f"📋 Using provided target: {nas_target}")
        print(f"   Source: {source}")
        print()

        # Try to get status, but don't fail if we can't access
        try:
            status = tracker.check_migration_status(source, nas_target=nas_target)
            if status.migration_status == "complete":
                print("✅ Migration already complete")
                return True
        except Exception as e:
            logger.warning(f"⚠️  Cannot check status (may need authentication): {e}")
            status = None
    else:
        # Check migration status normally
        status = tracker.check_migration_status(source)

        if status.migration_status != "interrupted" and status.migration_status != "partial":
            print(f"⚠️  Migration status is '{status.migration_status}' - attempting resume anyway")
            print(f"   (Migration may be interrupted but status not detected)")

        if not status.can_resume and status.migration_status not in ["interrupted", "partial"]:
            print(f"⚠️  Cannot determine if migration can resume")
            print(f"   Proceeding with file comparison...")

        if status:
            print(f"📋 MIGRATION STATUS:")
            print(f"   Source: {status.source_path}")
            print(f"   Status: {status.migration_status.upper()}")
            if status.migration_started:
                print(f"   Started: {status.migration_started}")
            if status.migration_interrupted:
                print(f"   Interrupted: {status.migration_interrupted}")
            if status.interrupted_reason:
                print(f"   Reason: {status.interrupted_reason}")
            if hasattr(status, 'size_migrated_gb'):
                print(f"   Progress: {status.size_migrated_gb:.2f} GB / {status.size_total_gb:.2f} GB")
            if hasattr(status, 'files_migrated'):
                print(f"   Files: {status.files_migrated} / {status.files_total}")
            print()

        if not status or not status.nas_target:
            if not nas_target_path:
                print("❌ No NAS target specified - cannot resume")
                return False

        nas_target = Path(status.nas_target) if status and status.nas_target else None
        if not nas_target and not nas_target_path:
            print("❌ No NAS target available - cannot resume")
            return False

    print(f"🎯 RESUME PLAN:")
    print(f"   Source: {source}")
    print(f"   Target: {nas_target}")
    print(f"   Remaining: {status.size_total_gb - status.size_migrated_gb:.2f} GB")
    print(f"   Files remaining: {status.files_total - status.files_migrated}")
    print()

    # ACTUAL RESUME IMPLEMENTATION - Compare files and migrate only missing
    print("🔍 Comparing source and target to find missing files...")

    missing_files = []
    existing_files = []
    target_accessible = False

    # Check if target is accessible (may require authentication)
    try:
        target_accessible = nas_target.exists()
    except Exception as e:
        logger.warning(f"⚠️  Cannot access target (authentication may be required): {e}")
        logger.info("   Proceeding with migration - will attempt to create target if needed")
        target_accessible = False

    # Compare source vs target to find missing files
    if target_accessible:
        # Get all files in source
        source_files = {}
        for file_path in source.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(source)
                source_files[rel_path] = file_path

        # Get all files in target
        target_files = {}
        for file_path in nas_target.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(nas_target)
                target_files[rel_path] = file_path

        # Find missing files (in source but not in target, or different)
        import hashlib

        for rel_path, source_file in source_files.items():
            target_file = nas_target / rel_path

            if rel_path not in target_files:
                # File doesn't exist in target
                missing_files.append((source_file, target_file, rel_path))
            else:
                # File exists - check if same (size + hash)
                try:
                    source_size = source_file.stat().st_size
                    target_size = target_file.stat().st_size

                    if source_size != target_size:
                        # Different size - needs migration
                        missing_files.append((source_file, target_file, rel_path))
                    else:
                        # Same size - check hash for verification
                        with open(source_file, 'rb') as f:
                            source_hash = hashlib.md5(f.read()).hexdigest()
                        with open(target_file, 'rb') as f:
                            target_hash = hashlib.md5(f.read()).hexdigest()

                        if source_hash != target_hash:
                            # Different content - needs migration
                            missing_files.append((source_file, target_file, rel_path))
                        else:
                            # Same file - already migrated
                            existing_files.append(rel_path)
                except Exception as e:
                    # Error checking - assume needs migration
                    missing_files.append((source_file, target_file, rel_path))
    else:
        # Target doesn't exist or not accessible - all files need migration
        logger.info("   Target not accessible or doesn't exist - all files will be migrated")
        for file_path in source.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(source)
                target_file = nas_target / rel_path
                missing_files.append((file_path, target_file, rel_path))

    print(f"📊 COMPARISON RESULTS:")
    print(f"   Files already migrated: {len(existing_files)}")
    print(f"   Files to migrate: {len(missing_files)}")
    print()

    if not missing_files:
        print("✅ All files already migrated - nothing to resume")
        return True

    # Calculate size of files to migrate
    total_size = sum(source_file.stat().st_size for source_file, _, _ in missing_files)
    total_size_gb = total_size / (1024 ** 3)

    print(f"📦 MIGRATION NEEDED:")
    print(f"   Files to migrate: {len(missing_files)}")
    print(f"   Size to migrate: {total_size_gb:.2f} GB")
    print()

    if dry_run:
        print("🔍 DRY RUN - Would migrate:")
        for source_file, target_file, rel_path in missing_files[:10]:  # Show first 10
            print(f"   {rel_path}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more files")
        print()
        return True

    # ACTUAL MIGRATION - Migrate only missing files
    print("🚀 Starting migration of missing files...")

    migrated_count = 0
    failed_count = 0

    for source_file, target_file, rel_path in missing_files:
        try:
            # Create target directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_file, target_file)

            migrated_count += 1
            if migrated_count % 100 == 0:
                print(f"   Migrated {migrated_count}/{len(missing_files)} files...")
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ Failed to migrate {rel_path}: {e}")

    print()
    print(f"✅ MIGRATION COMPLETE:")
    print(f"   Migrated: {migrated_count} files")
    if failed_count > 0:
        print(f"   Failed: {failed_count} files")
    print()

    # Update migration status (refresh after migration)
    status = tracker.check_migration_status(source)
    tracker._save_migration_status()

    return True


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Resume Interrupted Migration")
    parser.add_argument("path", type=str, help="Source path to resume migration for")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")

    args = parser.parse_args()

    resume_migration(args.path, dry_run=args.dry_run)


if __name__ == "__main__":


    main()