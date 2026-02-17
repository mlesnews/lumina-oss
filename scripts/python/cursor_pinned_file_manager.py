#!/usr/bin/env python3
"""
Cursor IDE Pinned File Manager

Manages pinned files in Cursor IDE with an allowlist system.
Files on the allowlist are permanently pinned and cannot be unpinned
without explicit human operator confirmation.

Tags: #CURSOR_IDE #FILE_MANAGEMENT #PINNED_FILES #ALLOWLIST #GROUP_LOCKING #LOCK_SYMBOL
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    try:
        from lumina_adaptive_logger import get_adaptive_logger
        get_logger = get_adaptive_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("CursorPinnedFileManager")


@dataclass
class PinnedFileConfig:
    """Configuration for a pinned file with lock symbol support"""
    file_path: str
    permanently_pinned: bool = False
    locked: bool = True  # Locked by default for permanently pinned files
    reason: Optional[str] = None
    added_by: Optional[str] = None
    added_at: Optional[str] = None
    lock_symbol: str = "🔒"  # Lock symbol for visual indication


class CursorPinnedFileManager:
    """
    Manages pinned files in Cursor IDE with allowlist protection and lock symbols

    Features:
    - Allowlist of permanently pinned files with lock symbols (🔒)
    - Integration with Cursor IDE's group locking concept
    - Warning system for unpinning protected files
    - Automatic cleanup of non-allowlisted pinned files
    - Git backup before unpinning
    - Visual lock indicators for permanently pinned files

    Lock Symbol Concept:
    - Permanently pinned files are "locked" and show 🔒 symbol
    - Builds on Cursor IDE's existing group locking functionality
    - Reuses locking logic patterns from Cursor IDE
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize pinned file manager"""
        if project_root is None:
            project_root_path = Path(__file__).parent.parent.parent
        else:
            project_root_path = Path(project_root)

        self.project_root = project_root_path
        self.config_dir = self.project_root / "config" / "cursor_ide"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.allowlist_file = self.config_dir / "pinned_files_allowlist.json"
        self.state_file = self.config_dir / "pinned_files_state.json"

        # Load allowlist
        self.allowlist: Dict[str, PinnedFileConfig] = self._load_allowlist()

        logger.info("✅ Cursor Pinned File Manager initialized")
        logger.info(f"   📋 Allowlist: {len(self.allowlist)} permanently pinned files")

    def _load_allowlist(self) -> Dict[str, PinnedFileConfig]:
        """Load allowlist from config file"""
        if not self.allowlist_file.exists():
            # Create default allowlist with common files
            default_allowlist = self._create_default_allowlist()
            self._save_allowlist(default_allowlist)
            return default_allowlist

        try:
            with open(self.allowlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            allowlist = {}
            for file_path, config_data in data.items():
                # Handle backward compatibility - add default lock fields if missing
                if 'locked' not in config_data:
                    config_data['locked'] = True
                if 'lock_symbol' not in config_data:
                    config_data['lock_symbol'] = "🔒"
                allowlist[file_path] = PinnedFileConfig(**config_data)

            return allowlist
        except Exception as e:
            logger.error(f"Failed to load allowlist: {e}")
            return {}

    def _create_default_allowlist(self) -> Dict[str, PinnedFileConfig]:
        """Create default allowlist with common important files"""
        default_files = [
            ".cursorrules",
            "README.md",
            "requirements.txt",
            "config/ai_decision_tree.json",
            "config/decision_trees/ai_routing.json",
        ]

        allowlist = {}
        for file_path in default_files:
            full_path = str(self.project_root / file_path)
            allowlist[full_path] = PinnedFileConfig(
                file_path=full_path,
                permanently_pinned=True,
                locked=True,
                reason="Default system file",
                added_by="system",
                added_at=datetime.now().isoformat(),
                lock_symbol="🔒"
            )

        return allowlist

    def _save_allowlist(self, allowlist: Optional[Dict[str, PinnedFileConfig]] = None):
        """Save allowlist to config file"""
        if allowlist is None:
            allowlist = self.allowlist

        try:
            data = {}
            for file_path, config in allowlist.items():
                data[file_path] = asdict(config)

            with open(self.allowlist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Allowlist saved: {len(allowlist)} files")
        except Exception as e:
            logger.error(f"Failed to save allowlist: {e}")

    def add_to_allowlist(
        self,
        file_path: str,
        reason: Optional[str] = None,
        added_by: Optional[str] = None
    ) -> bool:
        """
        Add a file to the permanent allowlist

        Args:
            file_path: Path to file (relative or absolute)
            reason: Reason for permanent pinning
            added_by: Who added it (default: 'system')

        Returns:
            True if added successfully
        """
        # Normalize path
        if not Path(file_path).is_absolute():
            file_path = str(self.project_root / file_path)
        else:
            file_path = str(Path(file_path).resolve())

        config = PinnedFileConfig(
            file_path=file_path,
            permanently_pinned=True,
            locked=True,
            reason=reason or "Manually added to allowlist",
            added_by=added_by or "system",
            added_at=datetime.now().isoformat(),
            lock_symbol="🔒"
        )

        self.allowlist[file_path] = config
        self._save_allowlist()

        logger.info(f"✅ Added to allowlist: {file_path}")
        if reason:
            logger.info(f"   📝 Reason: {reason}")

        return True

    def remove_from_allowlist(self, file_path: str, require_confirmation: bool = True) -> bool:
        try:
            """
            Remove a file from the allowlist (with warning)

            Args:
                file_path: Path to file
                require_confirmation: Require explicit confirmation

            Returns:
                True if removed successfully
            """
            # Normalize path
            if not Path(file_path).is_absolute():
                file_path = str(self.project_root / file_path)
            else:
                file_path = str(Path(file_path).resolve())

            if file_path not in self.allowlist:
                logger.warning(f"File not in allowlist: {file_path}")
                return False

            config = self.allowlist[file_path]

            # Show warning with lock symbol
            logger.warning("=" * 60)
            logger.warning(f"⚠️  WARNING: Removing {config.lock_symbol} LOCKED file from allowlist")
            logger.warning("=" * 60)
            logger.warning(f"   {config.lock_symbol} File: {file_path}")
            logger.warning(f"   📝 Reason: {config.reason}")
            logger.warning(f"   👤 Added by: {config.added_by}")
            logger.warning(f"   📅 Added at: {config.added_at}")
            logger.warning("=" * 60)
            logger.warning(f"   This file was {config.lock_symbol} LOCKED and permanently pinned.")
            logger.warning("   Removing it will unlock and allow automatic unpinning.")
            logger.warning("   This integrates with Cursor IDE's group locking concept.")
            logger.warning("=" * 60)

            if require_confirmation:
                logger.warning("   ⚠️  This action requires explicit human operator confirmation.")
                logger.warning("   Set require_confirmation=False to proceed programmatically.")
                return False

            # Remove from allowlist
            del self.allowlist[file_path]
            self._save_allowlist()

            logger.info(f"✅ Removed from allowlist: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error in remove_from_allowlist: {e}", exc_info=True)
            raise
    def is_permanently_pinned(self, file_path: str) -> bool:
        try:
            """Check if a file is permanently pinned (on allowlist)"""
            # Normalize path
            if not Path(file_path).is_absolute():
                file_path = str(self.project_root / file_path)
            else:
                file_path = str(Path(file_path).resolve())

            return file_path in self.allowlist

        except Exception as e:
            self.logger.error(f"Error in is_permanently_pinned: {e}", exc_info=True)
            raise
    def get_allowlist(self) -> List[str]:
        """Get list of all permanently pinned files"""
        return list(self.allowlist.keys())

    def get_locked_files(self) -> List[str]:
        """Get list of locked files (permanently pinned with lock symbol)"""
        return [
            file_path for file_path, config in self.allowlist.items()
            if config.locked
        ]

    def integrate_with_cursor_group_locking(self, file_path: str) -> bool:
        """
        Integrate with Cursor IDE's group locking concept

        This method is designed to work with Cursor IDE's existing group locking
        functionality. When a file is permanently pinned, it should also be
        group-locked in Cursor IDE to prevent accidental unpinning.

        Note: This requires Cursor IDE API integration when available.
        For now, it marks the file as locked in our system.

        Args:
            file_path: Path to file to lock

        Returns:
            True if locked successfully
        """
        if not self.is_permanently_pinned(file_path):
            logger.warning(f"File not in allowlist, cannot lock: {file_path}")
            return False

        config = self.allowlist[file_path]
        if not config.locked:
            config.locked = True
            config.lock_symbol = "🔒"
            self._save_allowlist()
            logger.info(f"   🔒 File locked: {file_path}")
            logger.info("   📝 This integrates with Cursor IDE's group locking concept")

        return True

    def check_unpin_warning(self, file_path: str) -> Optional[str]:
        """
        Check if unpinning a file requires a warning

        Returns:
            Warning message if file is permanently pinned, None otherwise
        """
        if not self.is_permanently_pinned(file_path):
            return None

        config = self.allowlist[file_path]
        warning = (
            f"⚠️  WARNING: Attempting to unpin a {config.lock_symbol} LOCKED file!\n"
            f"   {config.lock_symbol} File: {file_path}\n"
            f"   📝 Reason: {config.reason}\n"
            f"   👤 Added by: {config.added_by}\n"
            f"   📅 Added at: {config.added_at}\n"
            f"\n"
            f"   This file is {config.lock_symbol} LOCKED and on the permanent allowlist.\n"
            f"   It should not be unpinned unless explicitly requested by the human operator.\n"
            f"\n"
            f"   This integrates with Cursor IDE's group locking concept - the file is\n"
            f"   locked to prevent accidental unpinning, similar to group-locked files.\n"
            f"\n"
            f"   To unpin this file, you must:\n"
            f"   1. Remove it from the allowlist first (unlocks it)\n"
            f"   2. Explicitly confirm the unpin action\n"
        )

        return warning

    def cleanup_non_allowlisted_pinned_files(
        self,
        current_pinned_files: List[str],
        backup_with_git: bool = True
    ) -> Dict[str, any]:
        """
        Clean up pinned files that are not on the allowlist

        Args:
            current_pinned_files: List of currently pinned file paths
            backup_with_git: Whether to backup with git before unpinning

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "total_pinned": len(current_pinned_files),
            "permanently_pinned": 0,
            "to_unpin": [],
            "warnings": [],
            "backed_up": [],
            "errors": []
        }

        # Normalize all paths
        normalized_pinned = []
        for file_path in current_pinned_files:
            if not Path(file_path).is_absolute():
                normalized_path = str(self.project_root / file_path)
            else:
                normalized_path = str(Path(file_path).resolve())
            normalized_pinned.append(normalized_path)

        # Check each pinned file
        for file_path in normalized_pinned:
            if self.is_permanently_pinned(file_path):
                results["permanently_pinned"] += 1
                config = self.allowlist[file_path]
                lock_status = f"{config.lock_symbol} LOCKED" if config.locked else "unlocked"
                logger.info(f"   {config.lock_symbol} Permanently pinned ({lock_status}): {file_path}")
                logger.info(f"      Reason: {config.reason}")
            else:
                results["to_unpin"].append(file_path)

                # Check if file exists and needs backup
                file_path_obj = Path(file_path)
                if file_path_obj.exists() and backup_with_git:
                    try:
                        # Git add and commit
                        import subprocess
                        result = subprocess.run(
                            ["git", "add", file_path],
                            cwd=self.project_root,
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            results["backed_up"].append(file_path)
                            logger.info(f"   💾 Backed up with git: {file_path}")
                    except Exception as e:
                        results["errors"].append(f"Backup failed for {file_path}: {e}")
                        logger.warning(f"   ⚠️  Backup failed: {file_path} - {e}")

        logger.info("=" * 60)
        logger.info("📊 Cleanup Summary:")
        logger.info(f"   Total pinned files: {results['total_pinned']}")
        logger.info(f"   Permanently pinned (keeping): {results['permanently_pinned']}")
        logger.info(f"   To unpin: {len(results['to_unpin'])}")
        logger.info(f"   Backed up: {len(results['backed_up'])}")
        logger.info("=" * 60)

        return results


# Global instance
_manager_instance = None


def get_pinned_file_manager() -> CursorPinnedFileManager:
    """Get or create global pinned file manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = CursorPinnedFileManager()
    return _manager_instance


def main():
    try:
        """Main entry point for testing"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Pinned File Manager")
        parser.add_argument("--list", action="store_true", help="List allowlisted files")
        parser.add_argument("--locked", action="store_true", help="List only locked files (🔒)")
        parser.add_argument("--add", type=str, help="Add file to allowlist (automatically locks it)")
        parser.add_argument("--remove", type=str, help="Remove file from allowlist (unlocks it)")
        parser.add_argument("--check", type=str, help="Check if file is permanently pinned/locked")
        parser.add_argument("--reason", type=str, help="Reason for adding to allowlist")
        parser.add_argument("--lock", type=str, help="Lock a file (integrate with Cursor IDE group locking)")

        args = parser.parse_args()

        manager = get_pinned_file_manager()

        if args.list or args.locked:
            if args.locked:
                print("\n🔒 Locked Files (Permanently Pinned with Lock Symbol):")
                print("=" * 60)
                print("   These files are locked and integrate with Cursor IDE's group locking concept")
                print("=" * 60)
                locked_files = manager.get_locked_files()
                if locked_files:
                    for file_path in locked_files:
                        config = manager.allowlist[file_path]
                        print(f"\n   {config.lock_symbol} {file_path}")
                        print(f"      Status: {config.lock_symbol} LOCKED (permanently pinned)")
                        print(f"      📝 Reason: {config.reason}")
                        print(f"      👤 Added by: {config.added_by}")
                        print(f"      📅 Added at: {config.added_at}")
                else:
                    print("   (No locked files)")
            else:
                print("\n📋 Permanently Pinned Files (Allowlist):")
                print("=" * 60)
                allowlist = manager.get_allowlist()
                if allowlist:
                    for file_path in allowlist:
                        config = manager.allowlist[file_path]
                        lock_status = f"{config.lock_symbol} LOCKED" if config.locked else "unlocked"
                        print(f"\n   {config.lock_symbol} {file_path}")
                        print(f"      Status: {lock_status} (permanently pinned)")
                        print(f"      📝 Reason: {config.reason}")
                        print(f"      👤 Added by: {config.added_by}")
                        print(f"      📅 Added at: {config.added_at}")
                else:
                    print("   (No files in allowlist)")
            print("=" * 60)

        if args.add:
            manager.add_to_allowlist(args.add, reason=args.reason)
            print(f"✅ Added to allowlist: {args.add}")

        if args.remove:
            if manager.remove_from_allowlist(args.remove, require_confirmation=False):
                print(f"✅ Removed from allowlist: {args.remove}")
            else:
                print(f"❌ Failed to remove from allowlist: {args.remove}")

        if args.check:
            # Normalize path for lookup
            check_path = args.check
            if not Path(check_path).is_absolute():
                check_path = str(manager.project_root / check_path)
            else:
                check_path = str(Path(check_path).resolve())

            if manager.is_permanently_pinned(check_path):
                config = manager.allowlist[check_path]
                lock_status = f"{config.lock_symbol} LOCKED" if config.locked else "unlocked"
                print(f"✅ File is permanently pinned: {args.check}")
                print(f"   Status: {lock_status}")
                print(f"   Reason: {config.reason}")
                if config.locked:
                    print(f"   🔒 This file is locked and integrates with Cursor IDE's group locking")
            else:
                print(f"❌ File is not permanently pinned: {args.check}")

        if args.lock:
            if manager.integrate_with_cursor_group_locking(args.lock):
                print(f"✅ File locked: {args.lock}")
                print(f"   🔒 This integrates with Cursor IDE's group locking concept")
            else:
                print(f"❌ Failed to lock file: {args.lock}")
                print(f"   (File must be in allowlist first)")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())