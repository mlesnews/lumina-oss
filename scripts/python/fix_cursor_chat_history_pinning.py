#!/usr/bin/env python3
"""
Fix Cursor IDE Chat History and Pinning Issues

Diagnoses and fixes issues with:
- Chat history not loading
- Pinning not working
- Agent chat sessions not accessible

Tags: #CURSOR_IDE #CHAT_HISTORY #PINNING #FIX @JARVIS @LUMINA
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixCursorChatHistory")


class CursorChatHistoryFixer:
    """Fix Cursor IDE chat history and pinning issues"""

    def __init__(self):
        self.cursor_appdata = Path(os.getenv("APPDATA")) / "Cursor"
        self.cursor_user_data = Path(os.getenv("APPDATA")) / "Cursor" / "User"
        self.workspace_storage = self.cursor_user_data / "workspaceStorage"

        # Common locations for chat history
        self.chat_locations = [
            self.cursor_user_data / "globalStorage",
            self.cursor_user_data / "workspaceStorage",
            self.cursor_user_data / "History",
            Path(os.getenv("LOCALAPPDATA")) / "Cursor" / "User Data"
        ]

    def find_chat_history_files(self) -> List[Path]:
        """Find all chat history files"""
        chat_files = []

        for location in self.chat_locations:
            if location.exists():
                try:
                    # Look for common chat history file patterns
                    patterns = ["*chat*", "*history*", "*agent*", "*session*", "*.json"]
                    for pattern in patterns:
                        found = list(location.rglob(pattern))
                        chat_files.extend(found)
                except Exception as e:
                    logger.debug(f"Error searching {location}: {e}")

        return chat_files

    def check_workspace_storage(self) -> Dict:
        """Check workspace storage for issues"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING CURSOR WORKSPACE STORAGE")
        logger.info("=" * 80)
        logger.info("")

        issues = []
        info = []

        if not self.workspace_storage.exists():
            issues.append(f"Workspace storage not found: {self.workspace_storage}")
            logger.warning(f"❌ Workspace storage not found: {self.workspace_storage}")
        else:
            info.append(f"✅ Workspace storage exists: {self.workspace_storage}")

            # Check for locked files
            try:
                storage_items = list(self.workspace_storage.iterdir())
                info.append(f"   Found {len(storage_items)} workspace storage items")

                # Check for very large files (might be corrupted)
                large_files = []
                for item in storage_items:
                    if item.is_file():
                        size_mb = item.stat().st_size / (1024**2)
                        if size_mb > 100:  # Files larger than 100MB
                            large_files.append((item, size_mb))

                if large_files:
                    issues.append(f"Found {len(large_files)} very large files (possibly corrupted)")
                    for file_path, size_mb in large_files:
                        logger.warning(f"   ⚠️  Large file: {file_path.name} ({size_mb:.2f} MB)")
            except Exception as e:
                issues.append(f"Error reading workspace storage: {e}")

        return {
            "issues": issues,
            "info": info,
            "workspace_storage": str(self.workspace_storage) if self.workspace_storage.exists() else None
        }

    def check_cursor_processes(self) -> Dict:
        """Check for multiple Cursor processes that might cause issues"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING CURSOR PROCESSES")
        logger.info("=" * 80)
        logger.info("")

        try:
            import psutil
            cursor_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'cursor' in proc.info['name'].lower():
                        cursor_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if len(cursor_processes) > 1:
                logger.warning(f"⚠️  Found {len(cursor_processes)} Cursor processes (may cause conflicts)")
                for proc in cursor_processes:
                    logger.info(f"   PID: {proc['pid']}, Memory: {proc['memory_info'].rss / (1024**2):.2f} MB")
                return {
                    "multiple_processes": True,
                    "count": len(cursor_processes),
                    "processes": cursor_processes
                }
            else:
                logger.info(f"✅ Found {len(cursor_processes)} Cursor process")
                return {
                    "multiple_processes": False,
                    "count": len(cursor_processes)
                }
        except ImportError:
            logger.warning("⚠️  psutil not available - cannot check processes")
            return {"error": "psutil not available"}

    def clear_cursor_cache(self, backup: bool = True) -> Dict:
        """Clear Cursor cache (may fix chat history issues)"""
        logger.info("=" * 80)
        logger.info("🧹 CLEARING CURSOR CACHE")
        logger.info("=" * 80)
        logger.info("")

        cache_locations = [
            self.cursor_user_data / "Cache",
            self.cursor_user_data / "Code Cache",
            self.cursor_user_data / "GPUCache",
            Path(os.getenv("LOCALAPPDATA")) / "Cursor" / "Cache"
        ]

        cleared = []
        errors = []

        for cache_dir in cache_locations:
            if cache_dir.exists():
                try:
                    if backup:
                        backup_dir = cache_dir.parent / f"{cache_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copytree(cache_dir, backup_dir)
                        logger.info(f"   ✅ Backed up: {cache_dir.name}")

                    # Clear cache
                    shutil.rmtree(cache_dir)
                    logger.info(f"   ✅ Cleared: {cache_dir}")
                    cleared.append(str(cache_dir))
                except Exception as e:
                    logger.error(f"   ❌ Error clearing {cache_dir}: {e}")
                    errors.append(str(e))

        return {
            "cleared": cleared,
            "errors": errors,
            "backup_created": backup
        }

    def fix_workspace_storage(self) -> Dict:
        """Fix workspace storage issues"""
        logger.info("=" * 80)
        logger.info("🔧 FIXING WORKSPACE STORAGE")
        logger.info("=" * 80)
        logger.info("")

        fixes = []
        errors = []

        if not self.workspace_storage.exists():
            try:
                self.workspace_storage.mkdir(parents=True, exist_ok=True)
                fixes.append("Created workspace storage directory")
                logger.info("✅ Created workspace storage directory")
            except Exception as e:
                errors.append(f"Failed to create workspace storage: {e}")
                logger.error(f"❌ Failed to create workspace storage: {e}")

        # Check for corrupted state files
        if self.workspace_storage.exists():
            try:
                state_files = list(self.workspace_storage.rglob("*.json"))
                for state_file in state_files:
                    try:
                        # Try to read and validate JSON
                        with open(state_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        # Corrupted JSON - backup and recreate
                        backup_file = state_file.with_suffix(f".corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                        shutil.move(state_file, backup_file)
                        logger.warning(f"   ⚠️  Found corrupted state file: {state_file.name} (backed up)")
                        fixes.append(f"Fixed corrupted state file: {state_file.name}")
            except Exception as e:
                errors.append(f"Error checking state files: {e}")

        return {
            "fixes": fixes,
            "errors": errors
        }

    def diagnose_and_fix(self, clear_cache: bool = False) -> Dict:
        """Diagnose and fix chat history/pinning issues"""
        logger.info("=" * 80)
        logger.info("🔍 CURSOR CHAT HISTORY & PINNING DIAGNOSTICS")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "workspace_storage": {},
            "processes": {},
            "fixes": {},
            "recommendations": []
        }

        # Check workspace storage
        results["workspace_storage"] = self.check_workspace_storage()

        # Check processes
        results["processes"] = self.check_cursor_processes()

        # Fix workspace storage
        results["fixes"] = self.fix_workspace_storage()

        # Clear cache if requested
        if clear_cache:
            logger.info("")
            cache_results = self.clear_cursor_cache()
            results["cache_cleared"] = cache_results

        # Generate recommendations
        if results["workspace_storage"].get("issues"):
            results["recommendations"].append("Restart Cursor IDE after fixes")

        if results["processes"].get("multiple_processes"):
            results["recommendations"].append("Close all Cursor windows and restart")

        if results["fixes"].get("fixes"):
            results["recommendations"].append("Workspace storage was fixed - restart Cursor")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 DIAGNOSTICS COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        if results["recommendations"]:
            logger.info("💡 Recommendations:")
            for i, rec in enumerate(results["recommendations"], 1):
                logger.info(f"   {i}. {rec}")
            logger.info("")

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Fix Cursor IDE Chat History and Pinning Issues")
        parser.add_argument("--clear-cache", action="store_true", help="Clear Cursor cache (may help)")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        fixer = CursorChatHistoryFixer()
        results = fixer.diagnose_and_fix(clear_cache=args.clear_cache)

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print("\n" + "=" * 80)
            print("✅ DIAGNOSTICS COMPLETE")
            print("=" * 80)
            print("\nNext steps:")
            print("1. Restart Cursor IDE")
            print("2. Try accessing chat history again")
            print("3. Try pinning items again")
            print("\nIf issues persist:")
            print("- Check Cursor IDE updates")
            print("- Clear cache with --clear-cache flag")
            print("- Check for Cursor IDE extensions that might interfere")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()