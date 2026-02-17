#!/usr/bin/env python3
"""
Data Lifecycle Manager

Archive, delete, retention policies automation.
Part of Phase 3: Medium Priority Enhancements - Data Lifecycle Management
"""

import sys
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DataLifecycleManager")


class RetentionPolicy(Enum):
    """Retention policy types"""
    KEEP_FOREVER = "keep_forever"
    DELETE_AFTER_DAYS = "delete_after_days"
    ARCHIVE_AFTER_DAYS = "archive_after_days"
    DELETE_ON_SIZE = "delete_on_size"


@dataclass
class LifecycleRule:
    """Data lifecycle rule"""
    rule_id: str
    name: str
    pattern: str  # File pattern (glob)
    policy: RetentionPolicy
    policy_value: int  # Days, size in MB, etc.
    archive_path: Optional[Path] = None
    enabled: bool = True


@dataclass
class LifecycleAction:
    """Lifecycle action result"""
    file_path: str
    action: str  # archive, delete, keep
    success: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


class DataLifecycleManager:
    """
    Data Lifecycle Manager

    Automates data archiving, deletion, and retention policies.
    """

    def __init__(self, project_root: Path):
        """Initialize data lifecycle manager"""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.archive_dir = self.project_root / "archive" / "data_lifecycle"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.rules: List[LifecycleRule] = []
        self.action_history: List[LifecycleAction] = []

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("Data Lifecycle Manager initialized")

    def _initialize_default_rules(self) -> None:
        """Initialize default lifecycle rules"""
        # Archive old log files (30 days)
        self.rules.append(LifecycleRule(
            rule_id="archive_old_logs",
            name="Archive old log files",
            pattern="**/*.log",
            policy=RetentionPolicy.ARCHIVE_AFTER_DAYS,
            policy_value=30,
            archive_path=self.archive_dir / "logs"
        ))

        # Delete temporary files (7 days)
        self.rules.append(LifecycleRule(
            rule_id="delete_temp_files",
            name="Delete temporary files",
            pattern="**/tmp/**",
            policy=RetentionPolicy.DELETE_AFTER_DAYS,
            policy_value=7
        ))

        # Archive old data files (90 days)
        self.rules.append(LifecycleRule(
            rule_id="archive_old_data",
            name="Archive old data files",
            pattern="data/**/*.json",
            policy=RetentionPolicy.ARCHIVE_AFTER_DAYS,
            policy_value=90,
            archive_path=self.archive_dir / "data"
        ))

        logger.info(f"Initialized {len(self.rules)} default lifecycle rules")

    def add_rule(self, rule: LifecycleRule) -> None:
        """Add a lifecycle rule"""
        self.rules.append(rule)
        logger.info(f"Added lifecycle rule: {rule.name}")

    def process_files(self, directory: Path, dry_run: bool = False) -> List[LifecycleAction]:
        """Process files according to lifecycle rules"""
        actions = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            # Find matching files
            matching_files = list(directory.glob(rule.pattern))

            for file_path in matching_files:
                if not file_path.is_file():
                    continue

                # Check if rule applies
                action = self._determine_action(file_path, rule)
                if action == "keep":
                    continue

                # Execute action
                if action == "archive":
                    result = self._archive_file(file_path, rule, dry_run)
                elif action == "delete":
                    result = self._delete_file(file_path, rule, dry_run)
                else:
                    continue

                actions.append(result)
                self.action_history.append(result)

        return actions

    def _determine_action(self, file_path: Path, rule: LifecycleRule) -> str:
        """Determine action for a file based on rule"""
        file_stat = file_path.stat()
        file_age = datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)

        if rule.policy == RetentionPolicy.KEEP_FOREVER:
            return "keep"
        elif rule.policy == RetentionPolicy.DELETE_AFTER_DAYS:
            if file_age.days > rule.policy_value:
                return "delete"
        elif rule.policy == RetentionPolicy.ARCHIVE_AFTER_DAYS:
            if file_age.days > rule.policy_value:
                return "archive"
        elif rule.policy == RetentionPolicy.DELETE_ON_SIZE:
            size_mb = file_stat.st_size / (1024 * 1024)
            if size_mb > rule.policy_value:
                return "delete"

        return "keep"

    def _archive_file(self, file_path: Path, rule: LifecycleRule, dry_run: bool) -> LifecycleAction:
        """Archive a file"""
        try:
            if rule.archive_path:
                archive_path = rule.archive_path
            else:
                archive_path = self.archive_dir

            archive_path.mkdir(parents=True, exist_ok=True)

            # Create archive path preserving directory structure
            relative_path = file_path.relative_to(self.project_root)
            target_path = archive_path / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if dry_run:
                return LifecycleAction(
                    file_path=str(file_path),
                    action="archive",
                    success=True,
                    message=f"Would archive to {target_path}"
                )

            shutil.move(str(file_path), str(target_path))

            return LifecycleAction(
                file_path=str(file_path),
                action="archive",
                success=True,
                message=f"Archived to {target_path}"
            )
        except Exception as e:
            logger.error(f"Error archiving {file_path}: {e}")
            return LifecycleAction(
                file_path=str(file_path),
                action="archive",
                success=False,
                message=f"Error: {str(e)}"
            )

    def _delete_file(self, file_path: Path, rule: LifecycleRule, dry_run: bool) -> LifecycleAction:
        """Delete a file"""
        try:
            if dry_run:
                return LifecycleAction(
                    file_path=str(file_path),
                    action="delete",
                    success=True,
                    message=f"Would delete {file_path}"
                )

            file_path.unlink()

            return LifecycleAction(
                file_path=str(file_path),
                action="delete",
                success=True,
                message="Deleted"
            )
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")
            return LifecycleAction(
                file_path=str(file_path),
                action="delete",
                success=False,
                message=f"Error: {str(e)}"
            )

    def get_statistics(self) -> Dict[str, Any]:
        """Get lifecycle management statistics"""
        return {
            "rules_count": len(self.rules),
            "rules_enabled": sum(1 for r in self.rules if r.enabled),
            "actions_taken": len(self.action_history),
            "archived": sum(1 for a in self.action_history if a.action == "archive" and a.success),
            "deleted": sum(1 for a in self.action_history if a.action == "delete" and a.success),
            "failed": sum(1 for a in self.action_history if not a.success)
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Data Lifecycle Manager")
        parser.add_argument("--process", action="store_true", help="Process files")
        parser.add_argument("--dry-run", action="store_true", help="Dry run")
        parser.add_argument("--directory", type=Path, help="Directory to process (default: data)")
        parser.add_argument("--stats", action="store_true", help="Show statistics")

        args = parser.parse_args()

        manager = DataLifecycleManager(project_root)

        if args.stats:
            stats = manager.get_statistics()
            print(json.dumps(stats, indent=2))
            return

        if args.process:
            directory = args.directory or manager.data_dir
            actions = manager.process_files(directory, dry_run=args.dry_run)
            print(json.dumps([
                {
                    "file_path": a.file_path,
                    "action": a.action,
                    "success": a.success,
                    "message": a.message
                }
                for a in actions
            ], indent=2))
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":




    main()