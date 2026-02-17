#!/usr/bin/env python3
"""
Move Data to NAS for Centralization

Identifies and moves data that should be centralized on the NAS:
- Large data files
- Project archives
- Shared resources
- Logs and cache files
- Backup data
"""

import sys
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
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

logger = get_logger("MoveDataToNAS")


class NASDataMover:
    """
    Identify and move data to NAS for centralization
    """

    def __init__(self, nas_path: str = r"M:\lumina", 
                 local_root: Optional[Path] = None):
        """
        Initialize NAS data mover

        Args:
            nas_path: UNC path or network path to NAS
            local_root: Local root directory to scan (default: project root)
        """
        self.nas_path = Path(nas_path)
        self.local_root = local_root or Path(__file__).parent.parent.parent
        self.logger = logger

        logger.info(f"🗂️  NAS Data Mover initialized")
        logger.info(f"   NAS Path: {self.nas_path}")
        logger.info(f"   Local Root: {self.local_root}")

    def check_nas_connection(self) -> bool:
        """Check if NAS is accessible"""
        try:
            # Try to access NAS path
            if self.nas_path.exists():
                logger.info("✅ NAS path is accessible")
                return True
            else:
                logger.warning(f"⚠️  NAS path not accessible: {self.nas_path}")
                logger.info("   Trying alternative paths...")

                # Try common NAS paths (from config files)
                alternatives = [
                    r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\lumina",
                    r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups",
                    r"\\<NAS_PRIMARY_IP>\backups",
                    r"Z:\lumina",  # Mapped drive
                    r"Y:\lumina",  # Mapped drive
                    r"\\<NAS_PRIMARY_IP>\volume1\lumina",
                    r"\\<NAS_PRIMARY_IP>\volume1\shared\lumina",
                    r"\\<NAS_PRIMARY_IP>\lumina",
                    r"\\<NAS_PRIMARY_IP>\home\lumina",
                ]

                for alt_path in alternatives:
                    alt = Path(alt_path)
                    try:
                        if alt.exists():
                            self.nas_path = alt
                            logger.info(f"✅ Found NAS at: {self.nas_path}")
                            return True
                    except Exception:
                        continue

                logger.warning("⚠️  NAS not directly accessible via network path")
                logger.info("   You may need to:")
                logger.info("   1. Map a network drive (net use Z: \\\\<NAS_PRIMARY_IP>\\backups)")
                logger.info("   2. Authenticate to NAS first")
                logger.info("   3. Use SSH/API to transfer files")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Error checking NAS: {e}")
            logger.info("   Continuing with local analysis - you can move files manually later")
            return False

    def get_directory_size(self, path: Path) -> float:
        """Get directory size in GB"""
        try:
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return round(total / (1024 ** 3), 2)  # Convert to GB
        except Exception as e:
            logger.debug(f"Error calculating size for {path}: {e}")
            return 0.0

    def identify_candidates(self) -> List[Dict[str, any]]:
        try:
            """
            Identify data that should be moved to NAS

            Returns list of candidate directories/files with metadata
            """
            candidates = []

            logger.info("🔍 Identifying data candidates for NAS...")

            # Candidate patterns and reasons
            candidate_patterns = [
                {
                    "paths": ["data/logs", "logs"],
                    "reason": "Log files - can be archived on NAS",
                    "priority": "medium"
                },
                {
                    "paths": ["data/backups", "backups"],
                    "reason": "Backup data - should be on NAS",
                    "priority": "high"
                },
                {
                    "paths": ["data/cache", ".cache", "cache"],
                    "reason": "Cache files - can be regenerated",
                    "priority": "low"
                },
                {
                    "paths": ["data/archives", "archives", "data/session_archives"],
                    "reason": "Archived data - perfect for NAS",
                    "priority": "high"
                },
                {
                    "paths": ["data/holocron/video_production", "data/holocron", "data/videos"],
                    "reason": "Video production files - large, should be on NAS",
                    "priority": "high"
                },
                {
                    "paths": ["data/temp", "temp", "tmp"],
                    "reason": "Temporary files - can be on NAS or cleaned",
                    "priority": "low"
                },
                {
                    "paths": ["data/exports", "exports"],
                    "reason": "Export files - can be archived on NAS",
                    "priority": "medium"
                },
                {
                    "paths": ["data/lumina_data_mining"],
                    "reason": "Data mining results - can be archived",
                    "priority": "medium"
                },
                {
                    "paths": ["data/transcriptions"],
                    "reason": "Transcription files - can be archived",
                    "priority": "medium"
                }
            ]

            # Also check data directory for large subdirectories
            data_dir = self.local_root / "data"
            if data_dir.exists() and data_dir.is_dir():
                logger.info("   Scanning data directory for large subdirectories...")
                for subdir in data_dir.iterdir():
                    if subdir.is_dir():
                        # Skip if already in patterns
                        if any(str(subdir.relative_to(self.local_root)) in pattern["paths"] 
                               for pattern in candidate_patterns):
                            continue

                        size_gb = self.get_directory_size(subdir)
                        if size_gb > 0.1:  # Only include if > 100 MB
                            # Determine priority based on name
                            priority = "medium"
                            if any(keyword in subdir.name.lower() for keyword in ["archive", "backup", "old", "temp", "cache"]):
                                priority = "high" if "archive" in subdir.name.lower() or "backup" in subdir.name.lower() else "low"

                            candidate_patterns.append({
                                "paths": [f"data/{subdir.name}"],
                                "reason": f"Large data directory ({subdir.name}) - candidate for NAS",
                                "priority": priority
                            })

            for pattern in candidate_patterns:
                for rel_path in pattern["paths"]:
                    candidate_path = self.local_root / rel_path

                    if candidate_path.exists() and candidate_path.is_dir():
                        size_gb = self.get_directory_size(candidate_path)

                        if size_gb > 0.1:  # Only include if > 100 MB
                            candidates.append({
                                "path": candidate_path,
                                "relative_path": rel_path,
                                "size_gb": size_gb,
                                "reason": pattern["reason"],
                                "priority": pattern["priority"]
                            })
                            logger.info(f"   📁 {rel_path}: {size_gb} GB ({pattern['priority']} priority)")

            # Sort by priority and size
            priority_order = {"high": 0, "medium": 1, "low": 2}
            candidates.sort(key=lambda x: (priority_order[x["priority"]], -x["size_gb"]))

            return candidates

        except Exception as e:
            self.logger.error(f"Error in identify_candidates: {e}", exc_info=True)
            raise
    def move_to_nas(self, candidate: Dict[str, any], dry_run: bool = True) -> Tuple[bool, str]:
        """
        Move a candidate directory to NAS

        Args:
            candidate: Candidate dictionary from identify_candidates()
            dry_run: If True, only simulate the move

        Returns:
            (success, message)
        """
        local_path = candidate["path"]
        relative_path = candidate["relative_path"]

        # Build NAS destination path correctly
        # If relative_path already starts with "data/", don't duplicate it
        if relative_path.startswith("data/"):
            nas_dest = self.nas_path / relative_path
        else:
            nas_dest = self.nas_path / "data" / relative_path

        try:
            size_gb = candidate["size_gb"]
            logger.info(f"📦 Moving {relative_path} ({size_gb} GB)...")
            logger.info(f"   From: {local_path}")
            logger.info(f"   To:   {nas_dest}")

            if dry_run:
                logger.info("   [DRY RUN] Would move files")
                return True, "Dry run - no files moved"

            # Create destination directory
            nas_dest.parent.mkdir(parents=True, exist_ok=True)

            # If destination exists, ask or rename
            if nas_dest.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nas_dest = nas_dest.parent / f"{nas_dest.name}_{timestamp}"
                logger.info(f"   Destination exists, using: {nas_dest.name}")

            # Move directory
            shutil.move(str(local_path), str(nas_dest))

            # Create symlink back to local (optional - may require admin on Windows)
            try:
                local_path.symlink_to(nas_dest)
                logger.info("   ✅ Created symlink from local to NAS")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not create symlink: {e}")
                logger.info("   💡 You can manually create a shortcut or symlink if needed")

            logger.info(f"   ✅ Successfully moved {size_gb} GB to NAS")
            return True, f"Moved {size_gb} GB to {nas_dest}"

        except Exception as e:
            error_msg = f"Failed to move {relative_path}: {e}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg

    def generate_report(self, candidates: List[Dict[str, any]]) -> str:
        """Generate a report of candidates"""
        total_size = sum(c["size_gb"] for c in candidates)

        report = f"""
{'='*70}
📊 NAS Data Migration Report
{'='*70}

Total Candidates: {len(candidates)}
Total Size: {total_size:.2f} GB

By Priority:
"""

        for priority in ["high", "medium", "low"]:
            priority_candidates = [c for c in candidates if c["priority"] == priority]
            priority_size = sum(c["size_gb"] for c in priority_candidates)

            if priority_candidates:
                report += f"\n{priority.upper()} Priority ({len(priority_candidates)} items, {priority_size:.2f} GB):\n"
                for c in priority_candidates:
                    report += f"  • {c['relative_path']}: {c['size_gb']:.2f} GB - {c['reason']}\n"

        report += f"\n{'='*70}\n"

        return report


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Move data to NAS for centralization")
    parser.add_argument("--nas-path", default=r"M:\lumina",
                       help="NAS path (default: \\\\<NAS_PRIMARY_IP>\\lumina)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run - don't actually move files")
    parser.add_argument("--priority", choices=["high", "medium", "low", "all"],
                       default="high", help="Priority level to move (default: high)")
    parser.add_argument("--auto", action="store_true",
                       help="Automatically move without confirmation")

    args = parser.parse_args()

    print("="*70)
    print("🗂️  Move Data to NAS - Centralization")
    print("="*70)
    print()

    # Initialize mover
    mover = NASDataMover(nas_path=args.nas_path)

    # Check NAS connection (optional - can still analyze without it)
    print("📡 Checking NAS connection...")
    nas_accessible = mover.check_nas_connection()
    if not nas_accessible:
        print("⚠️  NAS not directly accessible - will analyze candidates locally")
        print("   You can move files manually or map a network drive later")
        print()
        if not args.dry_run:
            print("   To map network drive:")
            print("   net use Z: \\\\<NAS_PRIMARY_IP>\\backups /user:admin")
            print()
    print()

    # Identify candidates
    candidates = mover.identify_candidates()

    if not candidates:
        print("✅ No candidates found to move")
        return

    # Filter by priority
    if args.priority != "all":
        candidates = [c for c in candidates if c["priority"] == args.priority]

    # Generate report
    report = mover.generate_report(candidates)
    print(report)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be moved")
        print()

    # Move candidates (only if NAS is accessible)
    if not nas_accessible and not args.dry_run:
        print("⚠️  NAS not accessible - skipping file moves")
        print("   Use the report above to manually move files or:")
        print("   1. Map network drive: net use Z: \\\\<NAS_PRIMARY_IP>\\backups")
        print("   2. Run script again with mapped drive path")
        print()
        return

    if not args.auto and not args.dry_run:
        response = input(f"Move {len(candidates)} candidate(s) to NAS? (y/N): ")
        if response.lower() != 'y':
            print("⏭️  Cancelled")
            return

    print()
    print("📦 Moving data to NAS...")
    print()

    moved = 0
    failed = 0
    total_moved_gb = 0.0

    for candidate in candidates:
        success, message = mover.move_to_nas(candidate, dry_run=args.dry_run)
        if success:
            moved += 1
            if not args.dry_run:
                total_moved_gb += candidate["size_gb"]
        else:
            failed += 1
        print()

    # Summary
    print("="*70)
    print("📊 Summary")
    print("="*70)
    print(f"   Moved: {moved}")
    print(f"   Failed: {failed}")
    if not args.dry_run:
        print(f"   Total moved: {total_moved_gb:.2f} GB")
    print()

    if moved > 0:
        print("✅ Data centralization complete!")
        print()
        print("💡 Next steps:")
        print("   1. Verify data on NAS")
        print("   2. Update any hardcoded paths in code")
        print("   3. Set up cloud sync for NAS data if needed")
        print()


if __name__ == "__main__":


    main()