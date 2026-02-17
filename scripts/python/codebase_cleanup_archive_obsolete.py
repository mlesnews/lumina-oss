#!/usr/bin/env python3
"""
Codebase Cleanup - Archive Obsolete Code

Audits and archives obsolete code (demos, tests, examples) as identified in
MANUS gap analysis. Part of Phase 2: Codebase Cleanup.

Moves files to archive directory instead of deleting them.
"""

import sys
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CodebaseCleanupArchive")


@dataclass
class ArchiveEntry:
    """Entry for archived file"""
    original_path: str
    archived_path: str
    category: str
    reason: str
    archived_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodebaseCleanupArchive:
    """
    Archive obsolete code (demos, tests, examples)

    Moves files to archive directory instead of deleting them.
    """

    def __init__(self, project_root: Path, archive_dir: Optional[Path] = None):
        """Initialize cleanup archive system"""
        self.project_root = Path(project_root)
        self.archive_dir = archive_dir or (self.project_root / "archive" / "obsolete_code" / datetime.now().strftime("%Y%m%d"))
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive manifest
        self.archive_manifest_file = self.archive_dir / "archive_manifest.json"
        self.archived_files: List[ArchiveEntry] = []
        self._load_manifest()

        logger.info(f"Codebase Cleanup Archive initialized: {self.archive_dir}")

    def _load_manifest(self) -> None:
        """Load archive manifest"""
        if self.archive_manifest_file.exists():
            try:
                with open(self.archive_manifest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.archived_files = [ArchiveEntry(**entry) for entry in data.get("entries", [])]
                logger.info(f"Loaded {len(self.archived_files)} archived entries")
            except Exception as e:
                logger.warning(f"Error loading manifest: {e}")
                self.archived_files = []

    def _save_manifest(self) -> None:
        """Save archive manifest"""
        try:
            data = {
                "created_at": datetime.now().isoformat(),
                "total_entries": len(self.archived_files),
                "entries": [asdict(entry) for entry in self.archived_files]
            }
            with open(self.archive_manifest_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")

    def identify_obsolete_files(self, scripts_dir: Path) -> Dict[str, List[Path]]:
        """
        Identify obsolete files by category

        Returns:
            Dictionary mapping categories to lists of file paths
        """
        obsolete = {
            "demo": [],
            "test": [],
            "example": [],
            "todo_fixme": []
        }

        scripts_path = Path(scripts_dir)
        if not scripts_path.exists():
            logger.warning(f"Scripts directory not found: {scripts_path}")
            return obsolete

        # Find demo files
        for pattern in ["*demo*.py", "*_demo.py"]:
            obsolete["demo"].extend(scripts_path.glob(pattern))

        # Find test files (but not actual test infrastructure)
        for pattern in ["test_*.py", "*_test.py"]:
            for path in scripts_path.glob(pattern):
                # Exclude actual test infrastructure
                if "test" not in path.stem.lower() or path.stem.startswith("test_"):
                    obsolete["test"].append(path)

        # Find example files
        for pattern in ["example_*.py", "*_example.py"]:
            obsolete["example"].extend(scripts_path.glob(pattern))

        # Find files with TODO/FIXME markers (simple check - first 50 lines)
        for py_file in scripts_path.glob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    first_lines = ''.join(f.readlines()[:50])
                    if any(marker in first_lines for marker in ["# TODO", "# FIXME", "# DEPRECATED", "# OBSOLETE"]):  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                        obsolete["todo_fixme"].append(py_file)
            except Exception:
                continue

        # Remove duplicates
        for category in obsolete:
            obsolete[category] = list(set(obsolete[category]))

        logger.info(f"Identified obsolete files: {sum(len(files) for files in obsolete.values())} total")
        return obsolete

    def archive_file(self, file_path: Path, category: str, reason: str, dry_run: bool = False) -> bool:
        """
        Archive a single file

        Args:
            file_path: Path to file to archive
            category: Category (demo, test, example, todo_fixme)
            reason: Reason for archiving
            dry_run: If True, don't actually move file

        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        # Create category directory in archive
        category_dir = self.archive_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Archive path
        archived_path = category_dir / file_path.name

        # Handle conflicts (add number suffix)
        counter = 1
        while archived_path.exists():
            archived_path = category_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1

        if dry_run:
            logger.info(f"[DRY RUN] Would archive: {file_path} -> {archived_path}")
            return True

        try:
            # Move file
            shutil.move(str(file_path), str(archived_path))

            # Create archive entry
            entry = ArchiveEntry(
                original_path=str(file_path.relative_to(self.project_root)),
                archived_path=str(archived_path.relative_to(self.project_root)),
                category=category,
                reason=reason,
                archived_at=datetime.now().isoformat(),
                metadata={
                    "file_size": file_path.stat().st_size if file_path.exists() else 0,
                    "parent_dir": str(file_path.parent.relative_to(self.project_root))
                }
            )

            self.archived_files.append(entry)
            self._save_manifest()

            logger.info(f"Archived: {file_path.name} -> {archived_path}")
            return True

        except Exception as e:
            logger.error(f"Error archiving {file_path}: {e}")
            return False

    def archive_category(self, category: str, files: List[Path], reason: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Archive all files in a category

        Returns:
            Dictionary with success/failure counts
        """
        results = {
            "category": category,
            "total": len(files),
            "success": 0,
            "failed": 0,
            "files": []
        }

        for file_path in files:
            success = self.archive_file(file_path, category, reason, dry_run=dry_run)
            if success:
                results["success"] += 1
                results["files"].append({"file": str(file_path.name), "status": "archived"})
            else:
                results["failed"] += 1
                results["files"].append({"file": str(file_path.name), "status": "failed"})

        return results

    def archive_all_obsolete(self, scripts_dir: Path, dry_run: bool = False) -> Dict[str, Any]:
        """
        Archive all identified obsolete files

        Returns:
            Summary of archiving operation
        """
        obsolete = self.identify_obsolete_files(scripts_dir)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "archive_dir": str(self.archive_dir.relative_to(self.project_root)),
            "categories": {},
            "total_files": 0,
            "total_archived": 0,
            "total_failed": 0
        }

        # Archive by category
        category_reasons = {
            "demo": "Demo script - moved to archive",
            "test": "Test script - moved to archive",
            "example": "Example script - moved to archive",
            "todo_fixme": "Contains TODO/FIXME markers - review needed"
        }

        for category, files in obsolete.items():
            if files:
                reason = category_reasons.get(category, "Obsolete code")
                results = self.archive_category(category, files, reason, dry_run=dry_run)
                summary["categories"][category] = results
                summary["total_files"] += results["total"]
                summary["total_archived"] += results["success"]
                summary["total_failed"] += results["failed"]

        logger.info(f"Archive operation complete: {summary['total_archived']} archived, {summary['total_failed']} failed")
        return summary


def main():
    try:
        """CLI interface for codebase cleanup archive"""
        import argparse

        parser = argparse.ArgumentParser(description="Archive Obsolete Code")
        parser.add_argument("--scripts-dir", type=Path, default=script_dir, help="Scripts directory to scan")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually archive)")
        parser.add_argument("--list", action="store_true", help="List obsolete files without archiving")
        parser.add_argument("--archive", action="store_true", help="Archive obsolete files")
        parser.add_argument("--manifest", action="store_true", help="Show archive manifest")

        args = parser.parse_args()

        cleanup = CodebaseCleanupArchive(project_root)

        if args.manifest:
            print(json.dumps({
                "archive_dir": str(cleanup.archive_dir.relative_to(project_root)),
                "total_archived": len(cleanup.archived_files),
                "entries": [asdict(entry) for entry in cleanup.archived_files[-20:]]  # Last 20
            }, indent=2))
            return

        if args.list:
            obsolete = cleanup.identify_obsolete_files(args.scripts_dir)
            print(json.dumps({
                "categories": {
                    cat: [str(f.relative_to(project_root)) for f in files]
                    for cat, files in obsolete.items()
                },
                "totals": {cat: len(files) for cat, files in obsolete.items()},
                "grand_total": sum(len(files) for files in obsolete.values())
            }, indent=2))
            return

        if args.archive:
            summary = cleanup.archive_all_obsolete(args.scripts_dir, dry_run=args.dry_run)
            print(json.dumps(summary, indent=2))
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()