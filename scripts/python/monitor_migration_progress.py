#!/usr/bin/env python3
"""
Monitor Migration Progress

Real-time monitoring of cleanup and migration progress with full transparency:
- Maximum number of files
- Current file number
- Percentage complete
- Projected ETA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
data_dir = project_root / "data"

cleanup_progress_file = data_dir / "cleanup_progress.json"
migration_progress_file = data_dir / "migration_progress.json"


def format_time(seconds):
    """Format seconds into human-readable time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


def display_progress(file_path: Path, title: str):
    """Display progress from JSON file"""
    if not file_path.exists():
        return False

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        status = data.get("status", "unknown")
        phase = data.get("phase", "unknown")

        print(f"\n{'=' * 80}")
        print(f"{title}")
        print(f"{'=' * 80}")

        if status == "running":
            total_files = data.get("total_files", 0)
            current_file = data.get("current_file", 0)
            percentage = data.get("percentage", 0.0)
            eta = data.get("eta_formatted", "Calculating...")
            speed = data.get("speed_files_per_second", 0.0)
            elapsed = data.get("elapsed_seconds", 0)

            print(f"Status: {status.upper()} - Phase: {phase}")
            print(f"")
            print(f"📊 MAXIMUM FILES: {total_files:,}")
            print(f"📁 CURRENT FILE: {current_file:,}")
            print(f"📈 PERCENTAGE: {percentage:.2f}%")
            print(f"⏱️  ETA: {eta}")
            print(f"⚡ SPEED: {speed:.1f} files/second")
            print(f"⏳ ELAPSED: {format_time(elapsed)}")

            if "space_freed_gb" in data:
                print(f"💾 SPACE FREED: {data['space_freed_gb']:.2f} GB")

            if "bytes_copied" in data:
                bytes_copied = data.get("bytes_copied", 0)
                bytes_gb = bytes_copied / (1024 ** 3)
                print(f"📦 BYTES COPIED: {bytes_gb:.2f} GB")

        elif status == "completed":
            print(f"Status: ✅ COMPLETED")
            total_files = data.get("total_files", 0)
            current_file = data.get("current_file", total_files)
            elapsed = data.get("elapsed_seconds", 0)

            print(f"")
            print(f"📊 TOTAL FILES: {total_files:,}")
            print(f"📁 FILES PROCESSED: {current_file:,}")
            print(f"⏳ TOTAL TIME: {format_time(elapsed)}")

            if "space_freed_gb" in data:
                print(f"💾 SPACE FREED: {data['space_freed_gb']:.2f} GB")

        elif status == "failed" or status == "error":
            print(f"Status: ❌ {status.upper()}")
            if "error" in data:
                print(f"Error: {data['error']}")

        print(f"{'=' * 80}")

        return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def main():
    """Monitor progress in real-time"""
    print("🔍 Monitoring Migration Progress...")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Clear screen (works on Windows and Unix)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Check cleanup progress
            cleanup_running = display_progress(cleanup_progress_file, "🧹 CLEANUP PROGRESS")

            # Check migration progress
            migration_running = display_progress(migration_progress_file, "🚀 MIGRATION PROGRESS")

            if not cleanup_running and not migration_running:
                print("\n⏳ Waiting for processes to start...")

            time.sleep(1)  # Update every second

    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")


if __name__ == "__main__":


    main()