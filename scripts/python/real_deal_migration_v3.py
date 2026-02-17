#!/usr/bin/env python3
"""
LUMINA Real Deal Migration Script - V3 (SMB Optimized)
Moves Ollama models to NAS using SMB-friendly flags and provides
live visual progress by polling destination file sizes.

Tags: #MIGRATION #OLLAMA #NAS #SMB #LUMINA
"""

import contextlib
import logging
import os
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Generator, Optional

# Configure logging at module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("RealDealMigrationV3")


@contextlib.contextmanager
def safe_operation(operation_name: str) -> Generator[None, None, None]:
    """Context manager for safe operations with cleanup and logging"""
    try:
        logger.info(f"Starting: {operation_name}")
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info(f"Completed: {operation_name}")


def validate_file_path(path: Path, must_exist: bool = False) -> bool:
    try:
        """Validate file path before use with proper error messages"""
        if not isinstance(path, Path):
            path = Path(path)
        if must_exist and not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not must_exist and path.exists():
            raise FileExistsError(f"File already exists: {path}")
        return True


    except Exception as e:
        logger.error(f"Error in validate_file_path: {e}", exc_info=True)
        raise
def validate_input(value: Any, expected_type: type, param_name: str) -> bool:
    """Validate input parameters with proper type checking"""
    if not isinstance(value, expected_type):
        raise TypeError(f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}")
    return True

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from jarvis_progress_tracker import get_progress_tracker
except ImportError:
    print("Error: Could not import JARVISProgressTracker.")
    sys.exit(1)

def update_meter(process: str, total_bytes: int, current_bytes: int, message: str = "", complete: bool = False) -> None:
    """Update progress meter with validation"""
    validate_input(process, str, "process")
    validate_input(total_bytes, int, "total_bytes")
    validate_input(current_bytes, int, "current_bytes")

    total_mb = int(total_bytes / (1024 * 1024))
    current_mb = int(current_bytes / (1024 * 1024))

    try:
        tracker = get_progress_tracker(project_root)
        process_id = "ollama_nas_move_v3"

        if process_id not in tracker.processes:
            tracker.register_process(process_id, process, "Migration-V3", total_mb)

        tracker.update_progress(process_id, current_mb, total_mb)

        if complete:
            tracker.complete_process(process_id)
    except (ImportError, OSError, PermissionError) as e:
        logger.warning(f"Could not update progress tracker: {e}")

    percent = (current_bytes / total_bytes * 100) if total_bytes > 0 else 0
    bar_len = 40
    filled_len = int(bar_len * current_bytes // total_bytes) if total_bytes > 0 else 0
    bar = '█' * filled_len + '-' * (bar_len - filled_len)

    # Force print to terminal
    progress_msg = (
        f"\r🚀 {process} |{bar}| {percent:.1f}% "
        f"({current_mb}/{total_mb} MB) {message}"
    )
    sys.stdout.write(progress_msg)
    sys.stdout.flush()
    if complete:
        print()

def monitor_progress(dest_root: Path, total_bytes: int, process_name: str, stop_event: threading.Event) -> None:
    """Polls the destination directory to track real-time progress."""
    with safe_operation("monitor_progress"):
        while not stop_event.is_set():
            current_bytes = 0
            try:
                for root, _, files in os.walk(dest_root):
                    for f in files:
                        try:
                            current_bytes += (Path(root) / f).stat().st_size
                        except (OSError, PermissionError):
                            pass
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not walk destination directory: {e}")

            try:
                update_meter(process_name, total_bytes, current_bytes)
            except Exception as e:
                logger.warning(f"Could not update meter: {e}")

            time.sleep(2)

def migrate_smb_optimized():
    source_root = Path.home() / ".ollama"
    dest_root = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels")
    process_name = "Ollama NAS Move"

    print(f"🚀 Starting SMB-Optimized Migration: {source_root} -> {dest_root}")

    # Initialize progress tracker and start status updater for Cursor IDE
    tracker = get_progress_tracker(project_root, auto_start=True)
    print("✅ Visual progress tracking activated (Terminal + Cursor IDE status bar)")

    # 1. Stop Ollama
    print("🛑 Ensuring Ollama is stopped...")
    cmd_stop = "Stop-Process -Name ollama* -Force -ErrorAction SilentlyContinue"
    os.system(f"powershell -Command \"{cmd_stop}\"")
    time.sleep(2)

    # 2. Total size calculation
    total_bytes = 0
    for root, _, files in os.walk(source_root):
        for f in files:
            total_bytes += (Path(root) / f).stat().st_size

    total_mb = int(total_bytes / (1024 * 1024))
    print(f"📊 Total Migration Size: {total_bytes / (1024**3):.2f} GB ({total_mb} MB)")

    # Register process with tracker for visual progress
    process_id = "ollama_nas_move_v3"
    tracker.register_process(process_id, process_name, "Migration-V3", total_mb)
    print(f"📈 Progress tracking: {process_name} ({total_mb} MB total)")

    # 3. Start background monitor
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_progress,
        args=(dest_root, total_bytes, process_name, stop_event)
    )
    monitor_thread.daemon = True
    monitor_thread.start()

    # 4. Execute Robocopy with SMB-safe flags
    # /Z - Restartable mode (crucial for network)
    # /J - Unbuffered I/O (better for large files)
    # /COPY:D - DATA ONLY (prevents Error 5 Access Denied on timestamps/perms)
    # /MT:4 - Multithreaded (modest for network stability)
    cmd = [
        "robocopy", str(source_root), str(dest_root),
        "/MOVE", "/E", "/Z", "/J", "/COPY:D", "/MT:4", "/R:3", "/W:5", "/V", "/TS", "/FP"
    ]

    print(f"🛠️  Executing: {' '.join(cmd)}")
    try:
        # We run this synchronously so the script waits for completion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
            check=False
        )

        # Stop monitor
        stop_event.set()
        monitor_thread.join(timeout=5)

        # Get tracker for final update
        tracker = get_progress_tracker(project_root)
        process_id = "ollama_nas_move_v3"

        if result.returncode < 8:
            print("\n✅ Migration successful!")
            update_meter(process_name, total_bytes, total_bytes, "Complete", complete=True)
            tracker.complete_process(process_id)
            print("✅ Visual progress tracking complete")
        else:
            print(f"\n❌ Robocopy failed (Code {result.returncode})")
            print("--- Robocopy Errors ---")
            # Print only lines containing ERROR
            for line in result.stdout.splitlines():
                if "ERROR" in line:
                    print(line)
            tracker.fail_process(process_id, f"Robocopy return code: {result.returncode}")
    except (subprocess.TimeoutExpired, OSError, ValueError) as e:
        print(f"\n❌ Script error: {e}")
        stop_event.set()
        tracker = get_progress_tracker(project_root)
        tracker.fail_process("ollama_nas_move_v3", str(e))

if __name__ == "__main__":
    """Main entry point with proper error handling"""
    try:
        success = migrate_smb_optimized()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        sys.exit(1)
