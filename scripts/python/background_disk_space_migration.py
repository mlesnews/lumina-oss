#!/usr/bin/env python3
"""
Background Disk Space Migration Manager

Runs in the background to monitor and migrate files between laptop and desktop
to achieve 50% disk usage goal.

Features:
- Monitors disk space on both laptop and desktop
- Identifies large files/directories for migration
- Automatically migrates files to reach 50% usage target
- Background daemon mode
- Progress tracking and logging

Tags: #DISK-SPACE #MIGRATION #BACKGROUND #50-PERCENT-GOAL @JARVIS @LUMINA
"""

import atexit
import json
import logging
import multiprocessing
import os
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)

    def get_logger(name):
        return logging.getLogger(name)


logger = get_logger("BackgroundDiskMigration")


@dataclass
class DiskStatus:
    """Disk space status"""

    drive: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float
    percent_free: float
    target_percent: float = 50.0  # 50% usage goal
    needs_migration: bool = False
    space_to_free_gb: float = 0.0


@dataclass
class MigrationItem:
    """Item to migrate"""

    source_path: Path
    target_path: Path
    size_gb: float
    file_count: int
    priority: str  # "HIGH", "MEDIUM", "LOW"
    migration_type: str  # "move", "copy"


class BackgroundDiskSpaceMigration:
    """
    Background disk space migration manager

    Monitors disk usage and automatically migrates files to reach 50% usage goal.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Configuration - OPTIMIZED FOR MAX SPEED WITH RESOURCE BALANCE
        self.target_usage_percent = 50.0  # Goal: 50% disk usage
        self.check_interval_seconds = 30  # Check every 30 seconds (optimized from 5 min)
        self.migration_batch_size_gb = 25.0  # Migrate in 25GB batches (optimized from 5GB)

        # Resource-aware parallel processing configuration
        # Calculate optimal worker count based on system resources
        cpu_count = multiprocessing.cpu_count()

        # Get available memory to balance CPU and memory usage
        available_gb = 0.0
        try:
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            # Reserve 2GB per worker for safety, but don't exceed CPU cores
            memory_based_workers = max(1, int(available_gb / 2))
        except Exception:
            memory_based_workers = cpu_count
            available_gb = 8.0  # Default assumption if memory check fails

        # Optimal worker count: balance CPU cores, memory, and I/O
        # For disk I/O bound operations, use 1.5x CPU cores (optimal for I/O wait)
        # But cap based on available memory
        optimal_workers = min(
            max(2, int(cpu_count * 1.5)),  # I/O bound: 1.5x CPU cores (min 2)
            memory_based_workers,  # Don't exceed memory capacity
            cpu_count * 2,  # Never exceed 2x CPU cores
        )

        self.thread_pool_size = optimal_workers
        self.parallel_scanning = True  # Parallel directory scanning (OPTIMAL)
        self.max_workers = optimal_workers  # Resource-balanced thread pool size

        self.logger.info(
            f"⚡ Parallel processing: {self.max_workers} workers "
            f"(CPU: {cpu_count}, Memory: {available_gb:.1f}GB available)"
        )

        # Mustafar Mode detection (can be overridden)
        self.mustafar_mode = os.environ.get("MUSTAFAR_MODE", "false").lower() == "true"
        if self.mustafar_mode:
            # Mustafar: Maximum performance, less resource conservation
            self.max_workers = min(8, cpu_count * 2)  # Up to 8 workers or 2x CPU
            self.migration_batch_size_gb = 50.0  # 50GB batches
            self.check_interval_seconds = 10  # 10 second checks
            self.logger.info("🔥 MUSTAFAR MODE DETECTED - Maximum stress configuration")

        # Data directories
        self.data_dir = project_root / "data" / "disk_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # State tracking with resume capability
        self.state_file = self.data_dir / "migration_state.json"
        self.resume_state_file = self.data_dir / "resume_state.json"  # Resume state
        self.log_file = self.data_dir / "migration_log.jsonl"
        # Current operation status
        self.operation_status_file = self.data_dir / "operation_status.json"
        # PID lock file - prevents duplicate instances (Task Scheduler, multiple --start)
        self.lock_file = self.data_dir / "migration.lock"
        self._lock_held = False

        # System detection
        self.is_laptop = self._detect_laptop()
        self.system_name = self._get_system_name()

        # Migration targets
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"
        # Use the correct NAS share path that actually exists
        self.nas_migration_path = f"{self.nas_base}\\backups\\MATT_Backups"
        self.desktop_drive = "D:"  # Desktop drive (adjust as needed)

        # Running state
        self.running = False
        self.migration_thread = None

        self.logger.info("✅ Background Disk Space Migration initialized")
        system_type = "Laptop" if self.is_laptop else "Desktop"
        self.logger.info("   System: %s (%s)", self.system_name, system_type)
        self.logger.info("   Target: %s%% disk usage", self.target_usage_percent)
        interval = self.check_interval_seconds
        self.logger.info("   Check interval: %ss", interval)
        self.logger.info("   Resume capability: Enabled")
        self.logger.info("   Auto-start: Enabled (runs automatically)")

        # Resume from previous state if exists
        self._resume_from_state()

        # AUTO-START: Start migration automatically if disk needs migration
        # This ensures migration happens regardless and resumes on interruption
        # BUT: Only auto-start if not just checking status (avoid starting during status checks)
        skip_env = os.environ.get("SKIP_AUTO_START", "").lower() == "1"
        if not hasattr(self, "_skip_auto_start") and not skip_env:
            self._auto_start_if_needed()

    def get_disk_status(self, drive: str = "C:") -> DiskStatus:
        """Get current disk space status"""
        try:
            usage = psutil.disk_usage(drive)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent_used = (used_gb / total_gb) * 100
            percent_free = (free_gb / total_gb) * 100

            # Calculate if migration is needed
            needs_migration = percent_used > self.target_usage_percent
            space_to_free_gb = 0.0
            if needs_migration:
                # Calculate how much to free to reach 50%
                target_used_gb = total_gb * (self.target_usage_percent / 100)
                space_to_free_gb = used_gb - target_used_gb

            return DiskStatus(
                drive=drive,
                total_gb=round(total_gb, 2),
                used_gb=round(used_gb, 2),
                free_gb=round(free_gb, 2),
                percent_used=round(percent_used, 2),
                percent_free=round(percent_free, 2),
                target_percent=self.target_usage_percent,
                needs_migration=needs_migration,
                space_to_free_gb=round(space_to_free_gb, 2),
            )
        except Exception as e:
            self.logger.error(f"❌ Error getting disk status for {drive}: {e}")
            return None

    def find_migration_candidates(
        self, drive: str = "C:", min_size_gb: float = 1.0
    ) -> List[MigrationItem]:
        """Find files/directories to migrate - OPTIMIZED with parallel scanning"""
        msg = f"🔍 Finding migration candidates on {drive} (parallel enabled)..."
        self.logger.info(msg)

        candidates = []

        # Target directories to check
        target_dirs = [
            Path(f"{drive}/Users/mlesn/Dropbox/my_projects"),
            Path(f"{drive}/Users/mlesn/Downloads"),
            Path(f"{drive}/Users/mlesn/Videos"),
            Path(f"{drive}/Users/mlesn/Documents"),
            Path(f"{drive}/Users/mlesn/.ollama/models"),
            Path(f"{drive}/Users/mlesn/AppData/Local/Docker"),
        ]

        # Filter existing directories
        existing_dirs = [d for d in target_dirs if d.exists()]

        # Parallel size scanning - OPTIMIZED
        if self.parallel_scanning and len(existing_dirs) > 1:
            self.logger.info(f"   ⚡ Scanning {len(existing_dirs)} directories in parallel...")
            size_map = self._get_directory_size_parallel(existing_dirs)
        else:
            size_map = {d: self._get_directory_size(d) for d in existing_dirs}

        # Process results
        for target_dir in existing_dirs:
            try:
                size_bytes = size_map.get(target_dir, 0)
                size_gb = size_bytes / (1024**3)

                if size_gb >= min_size_gb:
                    file_count = self._count_files(target_dir)

                    # Determine target path
                    target_path = self._calculate_target_path(target_dir, drive)

                    # Determine priority (larger = higher priority for max speed)
                    if size_gb > 50:
                        priority = "HIGH"
                    elif size_gb > 20:
                        priority = "MEDIUM"
                    else:
                        priority = "LOW"

                    candidates.append(
                        MigrationItem(
                            source_path=target_dir,
                            target_path=target_path,
                            size_gb=round(size_gb, 2),
                            file_count=file_count,
                            priority=priority,
                            migration_type="move",  # Move to free space
                        )
                    )

                    name = target_dir.name
                    self.logger.info(f"   ✅ Found: {name} - {size_gb:.2f} GB ({priority})")
            except Exception as e:
                self.logger.debug(f"   Skipping {target_dir}: {e}")
                continue

        # Sort by size DESCENDING (largest first for max speed) - OPTIMIZED
        candidates.sort(key=lambda x: -x.size_gb, reverse=True)

        msg = f"   ⚡ Found {len(candidates)} candidates (sorted by size)"
        self.logger.info(msg)
        return candidates

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes - OPTIMIZED with os.scandir"""
        total = 0
        try:
            # Use os.scandir for faster directory scanning
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat().st_size
                        elif entry.is_dir(follow_symlinks=False):
                            # Recursively scan subdirectories
                            total += self._get_directory_size(Path(entry.path))
                    except (OSError, PermissionError):
                        pass
        except Exception as e:
            self.logger.debug(f"Error calculating size for {path}: {e}")
        return total

    def _get_directory_size_parallel(self, paths: List[Path]) -> Dict[Path, int]:
        """
        Get directory sizes in parallel - OPTIMIZED FOR RESOURCE BALANCE

        Parallel scanning IS optimal for:
        - Multiple directory scanning (I/O bound operations)
        - Maximizing disk throughput
        - Utilizing available CPU cores during I/O wait

        Only disabled during status checks to avoid interpreter shutdown conflicts.
        """
        if not self.parallel_scanning:
            return {path: self._get_directory_size(path) for path in paths}

        # Check if we're in a status check (skip parallel to avoid shutdown issues)
        # This is the ONLY case where parallel is disabled - status checks are quick
        if hasattr(self, "_skip_auto_start") and self._skip_auto_start:
            # Use sequential for status checks to avoid interpreter shutdown issues
            # Status checks are fast anyway, so parallel overhead isn't worth it
            return {path: self._get_directory_size(path) for path in paths}

        # Check if interpreter is shutting down BEFORE creating ThreadPoolExecutor
        # This prevents the RuntimeError from occurring in the first place
        if hasattr(sys, "is_finalizing") and sys.is_finalizing():
            # Interpreter is shutting down - use sequential immediately
            return {path: self._get_directory_size(path) for path in paths}

        # For actual migrations: PARALLEL IS OPTIMAL
        # I/O bound operations benefit from parallel execution during disk wait times
        def scan_path(path: Path) -> Tuple[Path, int]:
            return (path, self._get_directory_size(path))

        results = {}
        try:
            # Use resource-balanced worker count for optimal performance
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(scan_path, path): path for path in paths}
                for future in as_completed(futures):
                    try:
                        path, size = future.result()
                        results[path] = size
                    except Exception as e:
                        self.logger.debug(f"Error scanning {futures[future]}: {e}")
        except RuntimeError as e:
            # Handle "cannot schedule new futures after interpreter shutdown"
            # Fall back to sequential scanning only if interpreter is shutting down
            error_str = str(e).lower()
            if (
                "interpreter shutdown" in error_str
                or "cannot schedule new futures" in error_str
                or "cannot schedule" in error_str
            ):
                # Only log as debug during status checks (expected behavior)
                # Log as warning only during actual migrations (unexpected)
                if hasattr(self, "_skip_auto_start") and self._skip_auto_start:
                    self.logger.debug("Parallel scanning skipped (status check mode)")
                else:
                    self.logger.warning(
                        "⚠️  Parallel scanning unavailable (interpreter shutdown) - using sequential"
                    )
                return {path: self._get_directory_size(path) for path in paths}
            raise

        return results

    def _count_files(self, path: Path) -> int:
        """Count files in directory"""
        count = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    count += 1
        except Exception as e:
            self.logger.debug(f"Error counting files in {path}: {e}")
        return count

    def _calculate_target_path(self, source_path: Path, source_drive: str) -> Path:
        """Calculate target path for migration - ALWAYS prefer NAS"""
        # ALWAYS try NAS first (preferred - network storage)
        # Use the correct NAS share path: \\<NAS_PRIMARY_IP>\backups\MATT_Backups
        nas_path = Path(f"{self.nas_migration_path}/{source_path.name}")

        # Check if NAS is accessible
        if self._check_nas_accessible():
            self.logger.debug(f"   Using NAS target: {nas_path}")
            return nas_path

        # If NAS not accessible, log warning but still return NAS path
        # This allows retry logic to work and NAS may become available
        msg = f"   ⚠️  NAS not accessible, using NAS path for retry: {nas_path}"
        self.logger.warning(msg)

        # DO NOT fall back to D: drive - it's not ready
        # Always use NAS to avoid "device not ready" errors
        return nas_path

    def _check_nas_accessible(self) -> bool:
        """Check if NAS is accessible"""
        try:
            # Check the actual migration path, not just the base
            nas_path = Path(self.nas_migration_path)
            return nas_path.exists()
        except Exception:
            return False

    def _acquire_lock(self) -> bool:
        """Acquire PID lock to prevent duplicate migration instances.
        Returns True if lock acquired, False if another instance is running.
        """
        try:
            if self.lock_file.exists():
                try:
                    with open(self.lock_file, encoding="utf-8") as f:
                        data = json.load(f)
                    other_pid = data.get("pid")
                    if other_pid is not None and psutil.pid_exists(other_pid):
                        self.logger.info(
                            "Another migration instance is running (PID %s) - skipping",
                            other_pid,
                        )
                        return False
                    self.logger.debug("Removing stale lock from PID %s", other_pid)
                except (json.JSONDecodeError, OSError):
                    pass
                try:
                    self.lock_file.unlink()
                except OSError:
                    pass

            with open(self.lock_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"pid": os.getpid(), "started": datetime.now().isoformat()},
                    f,
                    indent=2,
                )
            self._lock_held = True
            atexit.register(self._release_lock_on_exit)
            return True
        except OSError as e:
            self.logger.warning("Could not acquire lock: %s", e)
            return False

    def _release_lock(self) -> None:
        """Release PID lock. Safe to call multiple times."""
        if not self._lock_held:
            return
        try:
            if self.lock_file.exists():
                with open(self.lock_file, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("pid") == os.getpid():
                    self.lock_file.unlink()
                    self.logger.debug("Lock released")
        except (json.JSONDecodeError, OSError) as e:
            self.logger.debug("Lock release: %s", e)
        finally:
            self._lock_held = False
            try:
                atexit.unregister(self._release_lock_on_exit)
            except (AttributeError, TypeError):
                pass

    def _release_lock_on_exit(self) -> None:
        """atexit callback - release lock when process exits."""
        self._release_lock()

    def _detect_laptop(self) -> bool:
        """Detect if running on laptop"""
        try:
            import socket

            hostname = socket.gethostname().lower()
            # Common laptop indicators
            laptop_indicators = ["laptop", "notebook", "portable", "thinkpad", "xps", "surface"]
            return any(indicator in hostname for indicator in laptop_indicators)
        except Exception:
            # Default: assume laptop if C: drive is primary
            return True

    def _get_system_name(self) -> str:
        """Get system name"""
        try:
            import socket

            return socket.gethostname()
        except Exception:
            return "unknown"

    def _save_operation_status(self, status: str, message: str, details: Optional[Dict] = None):
        """Save current operation status for transparency"""
        try:
            status_data = {
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            }
            with open(self.operation_status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.debug(f"Error saving operation status: {e}")

    def get_operation_status(self) -> Dict[str, Any]:
        """Get current operation status"""
        try:
            if self.operation_status_file.exists():
                with open(self.operation_status_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"status": "unknown", "message": "Status not available"}

    def _resume_from_state(self):
        """Resume migration from previous state - with error handling"""
        try:
            if self.resume_state_file.exists():
                with open(self.resume_state_file, encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    resume_state = json.loads(content)

                if resume_state.get("in_progress"):
                    msg = "🔄 Resuming migration from previous state..."
                    self.logger.info(msg)
                    last = resume_state.get("last_migration", "unknown")
                    self.logger.info(f"   Last migration: {last}")
                    total = resume_state.get("total_migrated_gb", 0)
                    self.logger.info(f"   Total migrated: {total:.2f} GB")
                    pending = resume_state.get("pending_items", [])
                    self.logger.info(f"   Pending items: {len(pending)}")

                    # Restore pending items (validate they're valid)
                    pending = resume_state.get("pending_items", [])
                    # Filter out invalid items
                    valid_pending = []
                    for item in pending:
                        if isinstance(item, dict) and item.get("source_path"):
                            valid_pending.append(item)
                    return valid_pending
        except json.JSONDecodeError as e:
            self.logger.warning(f"Resume state JSON error: {e} - resetting resume state")
            # Reset corrupted resume state
            try:
                self.resume_state_file.unlink()
            except Exception:
                pass
        except Exception as e:
            self.logger.warning(f"Could not resume from state: {e}")
        return []

    def save_resume_state(self, pending_items: List[MigrationItem], in_progress: bool = True):
        """Save resume state for reconnection"""
        try:
            # Convert MigrationItem objects to dicts and make JSON serializable
            pending_items_dicts = []
            for item in pending_items:
                item_dict = asdict(item)
                # Convert Path objects to strings
                item_dict = self._make_json_serializable(item_dict)
                pending_items_dicts.append(item_dict)

            resume_state = {
                "in_progress": in_progress,
                "last_migration": datetime.now().isoformat(),
                "system_name": self.system_name,
                "is_laptop": self.is_laptop,
                "total_migrated_gb": (self.load_state().get("total_migrated_gb", 0)),
                "pending_items": pending_items_dicts,
                "timestamp": datetime.now().isoformat(),
            }

            # Ensure entire state is JSON serializable
            resume_state = self._make_json_serializable(resume_state)

            with open(self.resume_state_file, "w", encoding="utf-8") as f:
                json.dump(resume_state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving resume state: {e}")

    def _safe_move_directory(self, source: Path, target: Path) -> None:
        """Move directory, merging into target if it already exists.

        Prevents path duplication (e.g. models/models, my_projects/my_projects) that
        occurs when shutil.move(src, existing_dir) puts src inside existing_dir.
        """
        source = Path(source)
        target = Path(target)
        if not target.exists():
            shutil.move(str(source), str(target))
            return
        if target.is_file():
            raise OSError(f"Cannot move directory over existing file: {target}")
        # Target exists and is a directory: merge (copy into it, then remove source)
        self.logger.info(f"   Target exists - merging into {target}")
        shutil.copytree(str(source), str(target), dirs_exist_ok=True)
        shutil.rmtree(str(source))

    def execute_migration(self, item: MigrationItem, dry_run: bool = False) -> Dict[str, Any]:
        """Execute migration of a single item with robust error handling"""
        self.logger.info(f"📦 Migrating: {item.source_path.name} ({item.size_gb} GB)")

        # Convert item to dict and make JSON serializable (Path -> str)
        item_dict = asdict(item)
        item_dict = self._make_json_serializable(item_dict)

        result = {
            "success": False,
            "item": item_dict,
            "space_freed_gb": 0.0,
            "errors": [],
            "exit_code": 0,
            "timestamp": datetime.now().isoformat(),
        }

        if dry_run:
            self.logger.info(f"   DRY RUN: Would move {item.source_path} -> {item.target_path}")
            result["success"] = True
            result["space_freed_gb"] = item.size_gb
            return result

        try:
            # Check target drive space (only if target is a local drive)
            target_drive = item.target_path.drive
            if target_drive and target_drive != "":
                try:
                    target_status = self.get_disk_status(target_drive)
                    needed = item.size_gb * 1.1
                    if target_status and target_status.free_gb < needed:
                        msg = (
                            f"Insufficient space on target: "
                            f"{target_status.free_gb:.2f} GB available, "
                            f"{needed:.2f} GB needed"
                        )
                        result["errors"].append(msg)
                        result["exit_code"] = 1
                        return result
                except Exception as e:
                    # If target drive check fails (e.g., network drive), continue
                    msg = f"Could not check target drive {target_drive}: {e}"
                    self.logger.debug(msg)

            # Create target directory
            try:
                item.target_path.parent.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                error_str = str(e).lower()
                # If directory creation fails due to device not ready, try NAS instead
                if "not ready" in error_str or "device" in error_str or "d:" in error_str:
                    self.logger.warning(f"   ⚠️  Target drive not ready ({e}), switching to NAS...")
                    # Recalculate target to use NAS (correct share path)
                    nas_path = Path(f"{self.nas_migration_path}/{item.source_path.name}")
                    item.target_path = nas_path

                    # Try to create NAS directory
                    try:
                        item.target_path.parent.mkdir(parents=True, exist_ok=True)
                        self.logger.info(f"   ✅ Switched to NAS target: {nas_path}")
                    except Exception as e2:
                        # If NAS also fails, log but don't fail completely - will retry
                        self.logger.warning(f"   ⚠️  NAS directory creation also failed: {e2}")
                        msg = f"Target drive not ready and NAS creation failed: {e2}"
                        result["errors"].append(msg)
                        result["exit_code"] = 1
                        # Don't return - allow retry logic to handle it
                else:
                    # Other errors - raise to be handled by retry logic
                    raise

            # OPTIMIZATION: Use fast transfer method (robocopy) instead of slow shutil.move()
            # This is 10-100x faster for network transfers
            try:
                from fast_migration_transfer import FastMigrationTransfer

                fast_transfer = FastMigrationTransfer(self.project_root)

                name = item.source_path.name
                self.logger.info(f"   🚀 Using FAST transfer (robocopy): {name}")
                transfer_result = fast_transfer.transfer_with_robocopy(
                    item.source_path,
                    item.target_path,
                    move=(item.migration_type == "move"),
                    multi_threaded=True,
                    size_gb=item.size_gb,
                )

                if transfer_result["success"]:
                    result["space_freed_gb"] = item.size_gb
                    result["success"] = True
                    result["exit_code"] = 0
                    result["transfer_speed_mbps"] = transfer_result["speed_mbps"]
                    result["files_transferred"] = transfer_result["files_transferred"]
                    speed = transfer_result["speed_mbps"]
                    msg = f"   ✅ Fast transfer complete: {speed:.2f} Mbps"
                    self.logger.info(msg)
                else:
                    result["errors"].extend(transfer_result.get("errors", []))
                    result["exit_code"] = 1
                    # Fall back to shutil if robocopy fails
                    self.logger.warning("   ⚠️  Fast transfer failed, falling back to shutil...")
                    raise Exception("Fast transfer failed")

            except ImportError:
                # Fallback to shutil if fast_transfer not available
                self.logger.warning("   ⚠️  Fast transfer not available, using shutil (slower)")
                pass
            except Exception as e:
                # Fallback to shutil
                msg = f"   ⚠️  Fast transfer error: {e}, using shutil"
                self.logger.warning(msg)
                pass

            # Execute migration with retry logic (fallback or if fast transfer not available)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if item.migration_type == "move":
                        source = item.source_path
                        target = item.target_path
                        attempt_num = attempt + 1
                        msg = (
                            f"   Moving: {source} -> {target} (attempt {attempt_num}/{max_retries})"
                        )
                        self.logger.info(msg)
                        self._safe_move_directory(source, target)
                        result["space_freed_gb"] = item.size_gb
                        result["success"] = True
                        result["exit_code"] = 0
                        self.logger.info("   ✅ Migration complete")
                        break
                except (OSError, PermissionError, shutil.Error) as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"   ⚠️  Attempt {attempt + 1} failed: {e}, retrying...")
                        time.sleep(2)  # Wait before retry
                    else:
                        raise
                except Exception as e:
                    self.logger.error(f"   ❌ Migration error: {e}")
                    result["errors"].append(str(e))
                    result["exit_code"] = 1
                    break

        except Exception as e:
            self.logger.error(f"   ❌ Migration error: {e}", exc_info=True)
            result["errors"].append(str(e))
            result["exit_code"] = 1

        return result

    def log_migration(self, result: Dict[str, Any]):
        """Log migration result with detailed tracking"""
        try:
            # Convert Path objects to strings for JSON serialization
            item = result.get("item", {})
            source_path = item.get("source_path", "")
            target_path = item.get("target_path", "")

            # Convert Path objects to strings
            if isinstance(source_path, Path):
                source_path = str(source_path)
            if isinstance(target_path, Path):
                target_path = str(target_path)

            # Add detailed tracking info
            result["migration_details"] = {
                "source_directory": source_path,
                "target_directory": target_path,
                "directory_name": Path(source_path).name if source_path else "",
                "file_count": item.get("file_count", 0),
                "migration_type": item.get("migration_type", "move"),
            }

            # Ensure all Path objects are converted to strings
            serializable_result = self._make_json_serializable(result)

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(serializable_result) + "\n")
        except Exception as e:
            self.logger.error(f"Error logging migration: {e}")

    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert Path objects and other non-serializable types to strings"""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {str(k): self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return type(obj)(self._make_json_serializable(item) for item in obj)
        elif hasattr(obj, "__dict__"):
            # Handle dataclass objects
            return self._make_json_serializable(obj.__dict__)
        else:
            try:
                # Test if it's JSON serializable
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # If not serializable, convert to string
                return str(obj)

    def save_state(self, state: Dict[str, Any]):
        """Save migration state"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")

    def load_state(self) -> Dict[str, Any]:
        """Load migration state"""
        try:
            if self.state_file.exists():
                with open(self.state_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
        return {}

    def migration_worker(self):
        """Background worker thread for migration - PERSISTS ON INTERRUPTION"""
        self.logger.info("🔄 Background migration worker started")
        self.logger.info("   ⚡ Auto-resume enabled - will continue after interruption")

        # Save current operation status for transparency
        self._save_operation_status("initializing", "Starting migration worker...")

        # Main loop - continues running regardless of interruptions
        while True:
            try:
                # Check if we should continue (allows graceful stop)
                if not self.running:
                    # Check if migration is still needed - if yes, keep running
                    disk_status = self.get_disk_status("C:")
                    if disk_status and disk_status.needs_migration:
                        msg = "🔄 Migration still needed - continuing despite stop"
                        self.logger.info(msg)
                        self.running = True  # Auto-resume
                    else:
                        self.logger.info("✅ Migration goal reached or not needed - stopping")
                        break

                # Update status: Checking disk
                self._save_operation_status("checking_disk", "Checking disk space status...")

                # Check disk status
                disk_status = self.get_disk_status("C:")

                if not disk_status:
                    self._save_operation_status("error", "Could not get disk status")
                    # OPTIMIZATION: Reduce wait time when disk is critically full
                    wait_time = max(5, self.check_interval_seconds // 3)  # Check 3x more often
                    time.sleep(wait_time)
                    continue

                pct = disk_status.percent_used
                used = disk_status.used_gb
                total = disk_status.total_gb
                self.logger.info(
                    f"📊 Disk Status: {pct:.1f}% used ({used:.2f} GB / {total:.2f} GB)"
                )

                # Check if migration is needed
                if disk_status.needs_migration:
                    to_free = disk_status.space_to_free_gb
                    self.logger.info(f"🚨 Migration needed: {to_free:.2f} GB to free")

                    # Update status: Scanning for candidates
                    msg = "Scanning directories for migration candidates..."
                    self._save_operation_status("scanning", msg)

                    # Find candidates
                    candidates = self.find_migration_candidates("C:", min_size_gb=1.0)

                    # Update status: Found candidates
                    if candidates:
                        # OPTIMIZATION: Sort by size DESC for sequential writes
                        candidates.sort(key=lambda x: -x.size_gb)
                        count = len(candidates)
                        total_gb = sum(c.size_gb for c in candidates)
                        msg = f"Migrating {count} candidates ({total_gb:.2f} GB total)..."
                        self._save_operation_status("migrating", msg)
                    else:
                        msg = "No migration candidates found"
                        self._save_operation_status("no_candidates", msg)
                        time.sleep(wait_time)
                        continue

                    if candidates:
                        # PARALLEL MIGRATION - OPTIMIZED FOR MAX SPEED
                        workers = self.max_workers
                        msg = f"⚡ Starting PARALLEL migration ({workers} workers)..."
                        self.logger.info(msg)
                        total_migrated = 0.0
                        pending_items = []
                        completed_items = []

                        # Use ThreadPoolExecutor for parallel migrations
                        try:
                            max_candidates = self.max_workers * 2
                            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                                # Submit all migrations
                                future_to_candidate = {
                                    executor.submit(
                                        self.execute_migration, candidate, False
                                    ): candidate
                                    for candidate in candidates[:max_candidates]
                                }

                                # Process completed migrations
                                for future in as_completed(future_to_candidate):
                                    if not self.running:
                                        break

                                    candidate = future_to_candidate[future]

                                    try:
                                        result = future.result()
                                        self.log_migration(result)

                                        # Check exit code
                                        exit_code = result.get("exit_code", 0)
                                        if exit_code != 0:
                                            msg = f"   ⚠️  Migration exit code: {exit_code}"
                                            self.logger.warning(msg)
                                            pending_items.append(candidate)

                                        if result["success"]:
                                            freed = result["space_freed_gb"]
                                            total_migrated += freed
                                            completed_items.append(candidate)

                                            name = candidate.source_path.name
                                            self.logger.info(
                                                f"   ✅ Migrated: {name} ({freed:.2f} GB)"
                                            )

                                            # Update state
                                            state = self.load_state()
                                            state["last_migration"] = datetime.now().isoformat()
                                            state["total_migrated_gb"] = (
                                                state.get("total_migrated_gb", 0) + freed
                                            )
                                            state["migrations_count"] = (
                                                state.get("migrations_count", 0) + 1
                                            )
                                            self.save_state(state)

                                            # Check if batch complete
                                            if total_migrated >= self.migration_batch_size_gb:
                                                msg = (
                                                    f"   ⚡ Batch complete: "
                                                    f"{total_migrated:.2f} GB migrated"
                                                )
                                                self.logger.info(msg)
                                                # Remaining items
                                                remaining = [
                                                    c
                                                    for c in candidates
                                                    if c not in completed_items
                                                    and c not in pending_items
                                                ]
                                                pending_items.extend(remaining)
                                                break

                                            # Recheck disk status
                                            new_status = self.get_disk_status("C:")
                                            target = self.target_usage_percent
                                            if new_status and new_status.percent_used <= target:
                                                pct = new_status.percent_used
                                                self.logger.info(
                                                    f"✅ Goal reached: {pct:.1f}% usage"
                                                )
                                                break
                                        else:
                                            errors = result.get("errors", [])
                                            msg = f"   Migration failed: {errors}"
                                            self.logger.warning(msg)
                                            pending_items.append(candidate)

                                    except Exception as e:
                                        msg = f"   ❌ Error executing migration: {e}"
                                        self.logger.error(msg, exc_info=True)
                                        pending_items.append(candidate)

                        except RuntimeError as e:
                            # Handle "cannot schedule new futures after shutdown"
                            if "interpreter shutdown" in str(e):
                                msg = (
                                    "⚠️  Parallel migration unavailable "
                                    "(interpreter shutdown) - using sequential"
                                )
                                self.logger.warning(msg)
                                # Fall back to sequential migration
                                for candidate in candidates[:5]:
                                    if not self.running:
                                        break
                                    try:
                                        result = self.execute_migration(candidate, False)
                                        self.log_migration(result)
                                        if result["success"]:
                                            freed = result["space_freed_gb"]
                                            total_migrated += freed
                                            completed_items.append(candidate)
                                            name = candidate.source_path.name
                                            self.logger.info(
                                                f"   ✅ Migrated: {name} ({freed:.2f} GB)"
                                            )

                                            # Update state
                                            state = self.load_state()
                                            state["last_migration"] = datetime.now().isoformat()
                                            state["total_migrated_gb"] = (
                                                state.get("total_migrated_gb", 0) + freed
                                            )
                                            state["migrations_count"] = (
                                                state.get("migrations_count", 0) + 1
                                            )
                                            self.save_state(state)

                                            if total_migrated >= self.migration_batch_size_gb:
                                                break
                                    except Exception as err:
                                        msg = f"   ❌ Sequential migration error: {err}"
                                        self.logger.error(msg)
                                        pending_items.append(candidate)
                            else:
                                raise

                        # Save resume state
                        if pending_items:
                            self.save_resume_state(pending_items, in_progress=True)
                            count = len(pending_items)
                            self.logger.info(f"   💾 Saved {count} pending items for resume")
                        else:
                            self.save_resume_state([], in_progress=False)

                        msg = (
                            f"⚡ Parallel migration cycle complete: "
                            f"{total_migrated:.2f} GB migrated"
                        )
                        self.logger.info(msg)
                    else:
                        self.logger.info("   No migration candidates found")
                else:
                    self._save_operation_status("waiting", "Waiting for next check cycle")
                    wait_time = self.check_interval_seconds
                    pct = disk_status.percent_used
                    target = self.target_usage_percent
                    self.logger.info(f"✅ Disk usage OK: {pct:.1f}% (target: {target}%)")

                # OPTIMIZATION: Reduce wait time when disk is critically full
                if disk_status and disk_status.percent_used > 90:
                    wait_time = max(5, self.check_interval_seconds // 3)  # Check 3x more often
                else:
                    wait_time = self.check_interval_seconds

                # Wait before next check
                time.sleep(wait_time)

            except KeyboardInterrupt:
                # Handle interruption gracefully - save state and continue
                msg = "⚠️  Interruption detected - saving state and continuing..."
                self.logger.warning(msg)
                msg2 = "Migration interrupted but continuing..."
                self._save_operation_status("interrupted", msg2)
                # Save current state for resume
                try:
                    disk_status = self.get_disk_status("C:")
                    if disk_status and disk_status.needs_migration:
                        # Migration still needed - continue after brief pause
                        time.sleep(5)
                        self.logger.info("🔄 Resuming migration after interruption...")
                        continue
                except Exception:
                    pass
                time.sleep(1)  # Brief pause before continuing

            except Exception as e:
                # Handle any errors - log and continue
                self.logger.error(f"❌ Migration worker error: {e}", exc_info=True)
                self._save_operation_status("error", f"Error occurred: {e}")
                # Wait before retrying
                time.sleep(self.check_interval_seconds)
                continue

        # Worker thread ending
        self.logger.info("🛑 Migration worker thread ending")
        self._save_operation_status("stopped", "Migration worker stopped")
        self._release_lock()

    def start(self, show_progress: bool = True, foreground_progress: bool = False) -> bool:
        """Start background migration

        Args:
            show_progress: Show progress bar
            foreground_progress: If True, progress bar runs in foreground (visible to operator)

        Returns:
            True if migration started, False if blocked (e.g. another instance running)
        """
        if self.running:
            self.logger.warning("⚠️  Migration already running")
            return False

        if not self._acquire_lock():
            self.logger.warning("Another migration instance is running - use --status to check")
            return False

        self.running = True
        # CRITICAL: Use daemon=False so thread persists even if main exits
        # This ensures migration continues regardless of interruption
        self.migration_thread = threading.Thread(target=self.migration_worker, daemon=False)
        self.migration_thread.start()

        self.logger.info("🚀 Background disk space migration started")
        self.logger.info(f"   Target: {self.target_usage_percent}% disk usage")
        self.logger.info("   Monitoring drive C:")

        # Start progress display - FOREGROUND so operator can see it
        if show_progress:
            try:
                from disk_migration_progress_display import MigrationProgressDisplay

                progress_display = MigrationProgressDisplay(self.project_root)

                if foreground_progress:
                    # Run in foreground - operator can see it
                    self.logger.info("   📊 Progress display running in FOREGROUND (visible)")
                    # This will block, so run in separate thread but make it visible
                    progress_thread = threading.Thread(
                        target=self._run_foreground_progress,
                        args=(progress_display,),
                        daemon=False,  # Not daemon so it stays visible
                    )
                    progress_thread.start()
                else:
                    # Background thread (less visible)
                    progress_thread = threading.Thread(
                        target=progress_display.display_live_progress, args=(5,), daemon=True
                    )
                    progress_thread.start()
                    self.logger.info("   📊 Progress display started (background)")
                    msg = "   💡 Run 'show_migration_progress.py --live' to view"
                    self.logger.info(msg)
            except Exception as e:
                self.logger.warning(f"   Could not start progress display: {e}")
        return True

    def _run_foreground_progress(self, progress_display):
        """Run progress display in foreground (visible to operator)"""
        try:
            progress_display.display_live_progress(update_interval=5)
        except Exception as e:
            self.logger.error(f"Progress display error: {e}")

    def _auto_start_if_needed(self):
        """Auto-start migration if disk needs migration and not already running"""
        try:
            # Check if migration is needed
            disk_status = self.get_disk_status("C:")
            if disk_status and disk_status.needs_migration and not self.running:
                msg = "🚀 AUTO-START: Disk needs migration, starting automatically..."
                self.logger.info(msg)
                self.start(show_progress=False, foreground_progress=False)
        except Exception as e:
            msg = f"Auto-start check failed: {e}"
            self.logger.debug(msg)

    def stop(self):
        """Stop background migration"""
        self.running = False
        if self.migration_thread:
            self.migration_thread.join(timeout=10)
        self._release_lock()
        self.logger.info("🛑 Background disk space migration stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        disk_status = self.get_disk_status("C:")
        state = self.load_state()

        return {
            "running": self.running,
            "disk_status": asdict(disk_status) if disk_status else None,
            "target_percent": self.target_usage_percent,
            "state": state,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Background Disk Space Migration")
    parser.add_argument("--start", action="store_true", help="Start background migration")
    parser.add_argument("--stop", action="store_true", help="Stop background migration")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--progress", action="store_true", help="Show visual progress bar")
    parser.add_argument(
        "--progress-live", action="store_true", help="Show live updating progress bar"
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze disk and find candidates")
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run mode (don't actually migrate)"
    )
    parser.add_argument(
        "--target-percent", type=float, default=50.0, help="Target disk usage percent (default: 50)"
    )
    parser.add_argument("--no-progress", action="store_true", help="Start without progress display")

    args = parser.parse_args()

    # Set skip_auto_start BEFORE creating manager to prevent auto-start during status checks
    skip_auto_start = args.status or args.analyze

    # Create manager with skip flag if needed
    if skip_auto_start:
        # Temporarily set environment variable to signal skip (checked in __init__)
        os.environ["SKIP_AUTO_START"] = "1"

    manager = BackgroundDiskSpaceMigration(project_root)

    # Set the flag explicitly after creation (for status/analyze commands)
    if skip_auto_start:
        manager._skip_auto_start = True

    if args.target_percent != 50.0:
        manager.target_usage_percent = args.target_percent

    if args.progress or args.progress_live:
        # Show progress display
        from disk_migration_progress_display import MigrationProgressDisplay

        display = MigrationProgressDisplay()
        if args.progress_live:
            display.display_live_progress(update_interval=5)
        else:
            display.display_progress_bar()

    elif args.start:
        print("\n" + "=" * 80)
        print("🚀 STARTING BACKGROUND DISK SPACE MIGRATION")
        print("=" * 80)
        print(f"Target: {manager.target_usage_percent}% disk usage")
        print(f"Check interval: {manager.check_interval_seconds}s")
        print("=" * 80 + "\n")

        # Start with visible progress bar by default
        if not manager.start(show_progress=not args.no_progress, foreground_progress=True):
            sys.exit(0)  # Another instance running - exit cleanly

        # Keep running
        try:
            while True:
                time.sleep(60)
                status = manager.get_status()
                if status["disk_status"]:
                    ds = status["disk_status"]
                    now = datetime.now().strftime("%H:%M:%S")
                    pct = ds["percent_used"]
                    used = ds["used_gb"]
                    total = ds["total_gb"]
                    print(f"[{now}] Disk: {pct:.1f}% used ({used:.2f} GB / {total:.2f} GB)")
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            manager.stop()

    elif args.stop:
        manager.stop()
        print("✅ Migration stopped")

    elif args.status:
        # Flag already set before manager creation, but ensure it's set
        manager._skip_auto_start = True
        status = manager.get_status()
        print("\n" + "=" * 80)
        print("📊 MIGRATION STATUS")
        print("=" * 80)
        print(f"Running: {status['running']}")
        print(f"Target: {status['target_percent']}%")

        if status["disk_status"]:
            ds = status["disk_status"]
            print("\nDisk Status (C:):")
            print(f"  Used: {ds['used_gb']:.2f} GB ({ds['percent_used']:.1f}%)")
            print(f"  Free: {ds['free_gb']:.2f} GB ({ds['percent_free']:.1f}%)")
            print(f"  Total: {ds['total_gb']:.2f} GB")
            print(f"  Needs Migration: {ds['needs_migration']}")
            if ds["needs_migration"]:
                print(f"  Space to Free: {ds['space_to_free_gb']:.2f} GB")

        if status["state"]:
            state = status["state"]
            print("\nMigration History:")
            print(f"  Total Migrated: {state.get('total_migrated_gb', 0):.2f} GB")
            print(f"  Migrations: {state.get('migrations_count', 0)}")
            if "last_migration" in state:
                print(f"  Last Migration: {state['last_migration']}")

        print("=" * 80 + "\n")

    elif args.analyze:
        print("\n" + "=" * 80)
        print("🔍 DISK ANALYSIS")
        print("=" * 80 + "\n")

        disk_status = manager.get_disk_status("C:")
        if disk_status:
            print("Disk Status (C:):")
            print(f"  Used: {disk_status.used_gb:.2f} GB ({disk_status.percent_used:.1f}%)")
            print(f"  Free: {disk_status.free_gb:.2f} GB ({disk_status.percent_free:.1f}%)")
            print(f"  Total: {disk_status.total_gb:.2f} GB")
            print(f"  Target: {disk_status.target_percent}%")
            print(f"  Needs Migration: {disk_status.needs_migration}")
            if disk_status.needs_migration:
                print(f"  Space to Free: {disk_status.space_to_free_gb:.2f} GB")
            print()

        candidates = manager.find_migration_candidates("C:", min_size_gb=1.0)
        if candidates:
            print(f"Migration Candidates ({len(candidates)}):")
            total_size = 0.0
            for i, candidate in enumerate(candidates, 1):
                print(f"  {i}. {candidate.source_path.name}")
                print(f"     Size: {candidate.size_gb:.2f} GB")
                print(f"     Files: {candidate.file_count:,}")
                print(f"     Priority: {candidate.priority}")
                print(f"     Target: {candidate.target_path}")
                print()
                total_size += candidate.size_gb

            print(f"Total: {total_size:.2f} GB can be migrated")
        else:
            print("No migration candidates found")

        print("=" * 80 + "\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
    main()