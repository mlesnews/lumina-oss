#!/usr/bin/env python3
"""
@DOIT Aggressive Disk Space Recovery
                    -LUM THE MODERN

GOAL: Get laptop hard drive utilization UNDER 50%
Current: 92.6% (CRITICAL)
Target: <50% (1.5TB+ to free)

@DOIT @SCOTTY @PEAK @LUMINA @DT -LUM_THE_MODERN
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DOITDiskRecovery")

NAS_IP = "<NAS_PRIMARY_IP>"
NAS_BACKUPS = Path(f"\\\\{NAS_IP}\\backups")


@dataclass
class LargeItem:
    """Represents a large file or directory"""
    path: Path
    size_gb: float
    item_type: str  # "file" or "directory"
    category: str  # "cache", "downloads", "games", "media", "projects", "other"
    can_migrate: bool = True
    can_delete: bool = False
    priority: int = 5  # 1-10, lower = higher priority


class DOITAggressiveDiskRecovery:
    """
    @DOIT Aggressive Disk Space Recovery System

    Uses @SCOTTY's @PEAK engineering to aggressively free disk space.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.nas_backups = NAS_BACKUPS
        self.large_items: List[LargeItem] = []
        self.total_freed_gb = 0.0

        logger.info("=" * 80)
        logger.info("🚀 @DOIT AGGRESSIVE DISK SPACE RECOVERY")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info("   Goal: <50% disk utilization")
        logger.info("   Method: @SCOTTY's @PEAK Engineering")
        logger.info("=" * 80)

    def get_disk_usage(self) -> Tuple[float, float, float, float]:
        """Get current disk usage"""
        total, used, free = shutil.disk_usage('C:')
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        usage_pct = (used / total) * 100
        return total_gb, used_gb, free_gb, usage_pct

    def find_large_directories(self, root: Path, min_size_gb: float = 1.0) -> List[LargeItem]:
        """Find large directories using PowerShell Get-ChildItem"""
        logger.info("🔍 Scanning for large directories...")
        large_items = []

        # Key directories to check
        check_paths = [
            Path(os.path.expanduser("~")) / "Downloads",
            Path(os.path.expanduser("~")) / "Documents",
            Path(os.path.expanduser("~")) / "Desktop",
            Path(os.path.expanduser("~")) / "Dropbox",
            Path(os.path.expanduser("~")) / "OneDrive",
            Path("C:\\Program Files"),
            Path("C:\\Program Files (x86)"),
            Path("C:\\ProgramData"),
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / "AppData" / "Local",
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / "AppData" / "LocalLow",
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / "AppData" / "Roaming",
            Path("C:\\Windows") / "Temp",
            Path("C:\\Temp"),
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / ".cache",
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / ".ollama",
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / "AppData" / "Local" / "pip",
            Path("C:\\Users") / os.getenv("USERNAME", "mlesn") / "AppData" / "Local" / "npm-cache",
        ]

        # Use PowerShell to get directory sizes
        ps_script = """
        $results = @()
        $paths = @(
            "$env:USERPROFILE\\Downloads",
            "$env:USERPROFILE\\Documents",
            "$env:USERPROFILE\\Desktop",
            "$env:USERPROFILE\\Dropbox",
            "$env:USERPROFILE\\OneDrive",
            "$env:LOCALAPPDATA",
            "$env:LOCALAPPDATA\\..\\LocalLow",
            "$env:APPDATA",
            "$env:TEMP",
            "$env:USERPROFILE\\.cache",
            "$env:USERPROFILE\\.ollama",
            "$env:LOCALAPPDATA\\pip",
            "$env:LOCALAPPDATA\\npm-cache"
        )
        foreach ($path in $paths) {
            if (Test-Path $path) {
                $size = (Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | 
                         Measure-Object -Property Length -Sum).Sum
                $sizeGB = [math]::Round($size / 1GB, 2)
                if ($sizeGB -ge 0.5) {
                    $results += [PSCustomObject]@{
                        Path = $path
                        SizeGB = $sizeGB
                    }
                }
            }
        }
        $results | ConvertTo-Json
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                import json
                items = json.loads(result.stdout)
                for item in items:
                    path = Path(item['Path'])
                    size_gb = float(item['SizeGB'])
                    if size_gb >= min_size_gb:
                        category = self._categorize_path(path)
                        can_delete = category in ["cache", "temp"]
                        large_items.append(LargeItem(
                            path=path,
                            size_gb=size_gb,
                            item_type="directory",
                            category=category,
                            can_migrate=True,
                            can_delete=can_delete,
                            priority=self._get_priority(category, size_gb)
                        ))
        except Exception as e:
            logger.warning("   PowerShell scan failed: %s", e)
            # Fallback: manual check of known large directories
            for check_path in check_paths:
                if check_path.exists():
                    try:
                        size = self._get_directory_size(check_path)
                        size_gb = size / (1024**3)
                        if size_gb >= min_size_gb:
                            category = self._categorize_path(check_path)
                            can_delete = category in ["cache", "temp"]
                            large_items.append(LargeItem(
                                path=check_path,
                                size_gb=size_gb,
                                item_type="directory",
                                category=category,
                                can_migrate=True,
                                can_delete=can_delete,
                                priority=self._get_priority(category, size_gb)
                            ))
                    except Exception as e:
                        logger.debug("   Could not check %s: %s", check_path, e)

        # Sort by priority (lower = higher priority) then by size (larger first)
        large_items.sort(key=lambda x: (x.priority, -x.size_gb))

        logger.info("   ✅ Found %d large directories (>=%.1f GB)", len(large_items), min_size_gb)
        return large_items

    def _get_directory_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total

    def _categorize_path(self, path: Path) -> str:
        """Categorize a path"""
        path_str = str(path).lower()
        if "download" in path_str:
            return "downloads"
        elif "cache" in path_str or "temp" in path_str or "tmp" in path_str:
            return "cache"
        elif "dropbox" in path_str or "onedrive" in path_str:
            return "cloud_storage"
        elif "ollama" in path_str or "models" in path_str:
            return "ai_models"
        elif "pip" in path_str or "npm" in path_str:
            return "cache"
        elif "program files" in path_str:
            return "programs"
        elif "appdata" in path_str:
            return "appdata"
        elif "documents" in path_str or "desktop" in path_str:
            return "user_data"
        else:
            return "other"

    def _get_priority(self, category: str, size_gb: float) -> int:
        """Get priority for migration/deletion (lower = higher priority)"""
        # High priority: large caches, temp files, downloads
        if category == "cache" and size_gb > 5:
            return 1
        elif category == "downloads" and size_gb > 10:
            return 2
        elif category == "ai_models" and size_gb > 20:
            return 2
        elif category == "cloud_storage" and size_gb > 50:
            return 3
        elif category == "temp" and size_gb > 1:
            return 1
        elif size_gb > 100:
            return 3
        elif size_gb > 50:
            return 4
        elif size_gb > 20:
            return 5
        else:
            return 6

    def clean_temp_files(self) -> float:
        """Aggressively clean temp files"""
        logger.info("🧹 Cleaning temp files...")
        freed_gb = 0.0

        temp_paths = [
            Path(os.getenv("TEMP", "C:\\Temp")),
            Path(os.getenv("TMP", "C:\\Temp")),
            Path("C:\\Windows\\Temp"),
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "Temp",
        ]

        for temp_path in temp_paths:
            if temp_path.exists():
                try:
                    size_before = self._get_directory_size(temp_path)
                    # Clean old temp files (older than 7 days)
                    cutoff_time = datetime.now().timestamp() - (7 * 24 * 60 * 60)
                    cleaned = 0
                    for item in temp_path.rglob('*'):
                        if item.is_file():
                            try:
                                if item.stat().st_mtime < cutoff_time:
                                    size = item.stat().st_size
                                    item.unlink()
                                    cleaned += size
                            except (OSError, PermissionError):
                                pass
                    size_after = self._get_directory_size(temp_path)
                    freed = (size_before - size_after) / (1024**3)
                    freed_gb += freed
                    if freed > 0.1:
                        logger.info("   ✅ Cleaned %s: %.2f GB freed", temp_path.name, freed)
                except Exception as e:
                    logger.debug("   Could not clean %s: %s", temp_path, e)

        return freed_gb

    def clean_caches(self) -> float:
        """Clean various caches"""
        logger.info("🧹 Cleaning caches...")
        freed_gb = 0.0

        cache_paths = [
            Path(os.path.expanduser("~")) / ".cache",
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "pip" / "cache",
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "npm-cache",
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
        ]

        for cache_path in cache_paths:
            if cache_path.exists():
                try:
                    size_before = self._get_directory_size(cache_path)
                    # Delete all cache files
                    for item in cache_path.rglob('*'):
                        if item.is_file():
                            try:
                                item.unlink()
                            except (OSError, PermissionError):
                                pass
                    size_after = self._get_directory_size(cache_path)
                    freed = (size_before - size_after) / (1024**3)
                    freed_gb += freed
                    if freed > 0.1:
                        logger.info("   ✅ Cleaned %s: %.2f GB freed", cache_path.name, freed)
                except Exception as e:
                    logger.debug("   Could not clean %s: %s", cache_path, e)

        return freed_gb

    def migrate_to_nas(self, item: LargeItem) -> bool:
        """Migrate item to NAS"""
        try:
            # Determine NAS destination
            if item.category == "downloads":
                nas_dest = self.nas_backups / "Downloads"
            elif item.category == "ai_models":
                nas_dest = self.nas_backups / "ollama_models"
            elif item.category == "cloud_storage":
                nas_dest = self.nas_backups / "LOCAL-CLOUD-STORAGE"
            elif item.category == "user_data":
                nas_dest = self.nas_backups / "UserData"
            else:
                nas_dest = self.nas_backups / "MigratedData"

            nas_dest.mkdir(parents=True, exist_ok=True)

            # Use robocopy to MOVE (not copy) files
            target_path = nas_dest / item.path.name

            logger.info("   📦 Migrating %s (%.2f GB) to NAS...", item.path.name, item.size_gb)

            # Robocopy with /MOVE to actually move files
            robocopy_cmd = [
                "robocopy",
                str(item.path),
                str(target_path),
                "/MOVE",  # MOVE, not copy!
                "/E",  # Include subdirectories
                "/MT:32",  # Multi-threaded
                "/R:3",  # Retry 3 times
                "/W:5",  # Wait 5 seconds
                "/NP",  # No progress
                "/NDL",  # No directory list
                "/NFL",  # No file list
            ]

            result = subprocess.run(
                robocopy_cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )

            # Robocopy returns 0-7 for success, 8+ for errors
            if result.returncode < 8:
                logger.info("   ✅ Migrated: %.2f GB freed", item.size_gb)
                return True
            else:
                logger.warning("   ⚠️  Migration warning (code %d)", result.returncode)
                return False

        except Exception as e:
            logger.error("   ❌ Migration failed: %s", e)
            return False

    def aggressive_recovery(self) -> Dict[str, Any]:
        """
        Execute aggressive disk space recovery

        Strategy:
        1. Clean temp files (safe to delete)
        2. Clean caches (safe to delete)
        3. Migrate large directories to NAS (priority order)
        4. Verify space freed
        """
        logger.info("=" * 80)
        logger.info("🚀 AGGRESSIVE DISK SPACE RECOVERY - @DOIT MODE")
        logger.info("=" * 80)

        # Get initial state
        total_gb, used_gb, free_gb, usage_pct = self.get_disk_usage()
        logger.info("")
        logger.info("📊 INITIAL STATE:")
        logger.info("   Total: %.2f GB", total_gb)
        logger.info("   Used: %.2f GB (%.1f%%)", used_gb, usage_pct)
        logger.info("   Free: %.2f GB", free_gb)
        logger.info("")

        target_usage = 50.0
        target_free_gb = (total_gb * target_usage / 100)
        needed_gb = target_free_gb - free_gb

        logger.info("🎯 TARGET:")
        logger.info("   Usage: <%.1f%%", target_usage)
        logger.info("   Free: >%.2f GB", target_free_gb)
        logger.info("   Need to free: %.2f GB", needed_gb)
        logger.info("")

        results = {
            "initial_usage_pct": usage_pct,
            "initial_free_gb": free_gb,
            "target_usage_pct": target_usage,
            "target_free_gb": target_free_gb,
            "needed_gb": needed_gb,
            "freed_gb": 0.0,
            "temp_cleaned_gb": 0.0,
            "cache_cleaned_gb": 0.0,
            "migrated_gb": 0.0,
            "items_migrated": 0,
            "items_failed": 0
        }

        # Step 1: Clean temp files
        logger.info("=" * 80)
        logger.info("STEP 1: Cleaning Temp Files")
        logger.info("=" * 80)
        temp_freed = self.clean_temp_files()
        results["temp_cleaned_gb"] = temp_freed
        results["freed_gb"] += temp_freed
        logger.info("   ✅ Temp files cleaned: %.2f GB", temp_freed)
        logger.info("")

        # Step 2: Clean caches
        logger.info("=" * 80)
        logger.info("STEP 2: Cleaning Caches")
        logger.info("=" * 80)
        cache_freed = self.clean_caches()
        results["cache_cleaned_gb"] = cache_freed
        results["freed_gb"] += cache_freed
        logger.info("   ✅ Caches cleaned: %.2f GB", cache_freed)
        logger.info("")

        # Step 3: Find large items
        logger.info("=" * 80)
        logger.info("STEP 3: Finding Large Directories")
        logger.info("=" * 80)
        large_items = self.find_large_directories(Path("C:"), min_size_gb=1.0)

        # Display found items
        logger.info("")
        logger.info("📦 LARGE ITEMS FOUND:")
        for i, item in enumerate(large_items[:20], 1):  # Top 20
            logger.info(
                "   %2d. %s (%.2f GB) [%s] %s",
                i,
                item.path.name,
                item.size_gb,
                item.category,
                "🗑️ DELETE" if item.can_delete else "📦 MIGRATE"
            )
        logger.info("")

        # Step 4: Migrate/Delete large items
        logger.info("=" * 80)
        logger.info("STEP 4: Migrating/Deleting Large Items")
        logger.info("=" * 80)

        migrated_gb = 0.0
        for item in large_items:
            # Check if we've freed enough space
            total_gb, used_gb, free_gb, usage_pct = self.get_disk_usage()
            if usage_pct < target_usage:
                logger.info("")
                logger.info("✅ TARGET REACHED! Usage: %.1f%%", usage_pct)
                break

            if item.can_delete:
                # Delete cache/temp items
                try:
                    logger.info("   🗑️  Deleting %s (%.2f GB)...", item.path.name, item.size_gb)
                    if item.path.is_file():
                        item.path.unlink()
                    else:
                        shutil.rmtree(item.path)
                    migrated_gb += item.size_gb
                    results["items_migrated"] += 1
                    logger.info("   ✅ Deleted: %.2f GB freed", item.size_gb)
                except Exception as e:
                    logger.warning("   ⚠️  Could not delete %s: %s", item.path.name, e)
                    results["items_failed"] += 1
            elif item.can_migrate:
                # Migrate to NAS
                if self.migrate_to_nas(item):
                    migrated_gb += item.size_gb
                    results["items_migrated"] += 1
                else:
                    results["items_failed"] += 1

        results["migrated_gb"] = migrated_gb
        results["freed_gb"] += migrated_gb

        # Final state
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 FINAL STATE:")
        logger.info("=" * 80)
        total_gb, used_gb, free_gb, usage_pct = self.get_disk_usage()
        logger.info("   Total: %.2f GB", total_gb)
        logger.info("   Used: %.2f GB (%.1f%%)", used_gb, usage_pct)
        logger.info("   Free: %.2f GB", free_gb)
        logger.info("")
        logger.info("📈 RECOVERY SUMMARY:")
        logger.info("   Temp files cleaned: %.2f GB", results["temp_cleaned_gb"])
        logger.info("   Caches cleaned: %.2f GB", results["cache_cleaned_gb"])
        logger.info("   Items migrated: %.2f GB (%d items)", results["migrated_gb"], results["items_migrated"])
        logger.info("   Total freed: %.2f GB", results["freed_gb"])
        logger.info("   Failed items: %d", results["items_failed"])
        logger.info("")

        if usage_pct < target_usage:
            logger.info("✅ SUCCESS! Disk usage is now %.1f%% (<50% target)", usage_pct)
        else:
            logger.info("⚠️  Progress: Disk usage is %.1f%% (target: <50%%)", usage_pct)
            logger.info("   Still need to free: %.2f GB", needed_gb - results["freed_gb"])

        logger.info("=" * 80)

        results["final_usage_pct"] = usage_pct
        results["final_free_gb"] = free_gb
        results["success"] = usage_pct < target_usage

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="@DOIT Aggressive Disk Space Recovery")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")

        args = parser.parse_args()

        recovery = DOITAggressiveDiskRecovery(project_root)

        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
            large_items = recovery.find_large_directories(Path("C:"), min_size_gb=1.0)
            logger.info("")
            logger.info("📦 Would process %d large items", len(large_items))
            for item in large_items[:10]:
                action = "DELETE" if item.can_delete else "MIGRATE"
                logger.info("   %s: %s (%.2f GB)", action, item.path.name, item.size_gb)
        else:
            results = recovery.aggressive_recovery()

            print(f"\n🎯 RESULTS:")
            print(f"   Initial Usage: {results['initial_usage_pct']:.1f}%")
            print(f"   Final Usage: {results['final_usage_pct']:.1f}%")
            print(f"   Total Freed: {results['freed_gb']:.2f} GB")
            print(f"   Success: {'✅ YES' if results['success'] else '⚠️  PARTIAL'}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()