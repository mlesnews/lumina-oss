#!/usr/bin/env python3
"""
Live monitoring script for NAS migration progress.
Shows real-time robocopy output and status updates.
"""

import os
import sys
import time
import json
import glob
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("watch_nas_migration_live")


def get_latest_log_file():
    try:
        """Get the latest robocopy log file."""
        log_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp' / 'nas_migration_logs'
        if not log_dir.exists():
            return None

        log_files = list(log_dir.glob('robocopy_*.log'))
        if not log_files:
            return None

        return max(log_files, key=lambda p: p.stat().st_mtime)

    except Exception as e:
        logger.error(f"Error in get_latest_log_file: {e}", exc_info=True)
        raise
def get_status():
    """Get current migration status from JSON file."""
    status_file = Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp' / 'nas_migration_logs' / 'migration_status.json'
    if not status_file.exists():
        return None

    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def format_bytes(bytes_val):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def watch_live():
    """Watch migration progress in real-time."""
    print("\n" + "="*70)
    print("NAS MIGRATION LIVE MONITOR")
    print("="*70)
    print("Press Ctrl+C to stop monitoring\n")

    log_file = get_latest_log_file()
    if not log_file:
        print("Waiting for robocopy log file to be created...")
        for _ in range(10):
            time.sleep(2)
            log_file = get_latest_log_file()
            if log_file:
                break
        if not log_file:
            print("ERROR: No robocopy log file found")
            return

    print(f"Monitoring: {log_file.name}")
    print(f"Full path: {log_file}\n")
    print("-"*70)

    last_size = 0
    last_lines = []

    try:
        while True:
            # Read status
            status = get_status()
            if status:
                mig = status.get('migration', {})
                stats = status.get('statistics', {})

                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] ", end='')
                print(f"Status: {status.get('status', 'unknown'):<10} | ", end='')
                print(f"Attempt: {mig.get('current_attempt', 0)}/{mig.get('max_attempts', 10)} | ", end='')
                print(f"Files: {stats.get('files_copied', 0):<8} | ", end='')
                print(f"Bytes: {format_bytes(stats.get('bytes_copied', 0)):<12}", end='', flush=True)

            # Read log file
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        current_size = log_file.stat().st_size

                        # Show new lines
                        if len(lines) > len(last_lines):
                            new_lines = lines[len(last_lines):]
                            for line in new_lines:
                                line = line.strip()
                                if line:
                                    # Highlight important lines
                                    if 'ERROR' in line.upper():
                                        print(f"\n{'!'*70}")
                                        print(f"ERROR: {line}")
                                        print('!'*70)
                                    elif any(keyword in line.upper() for keyword in ['FILES', 'DIRS', 'BYTES', 'TIMES', 'ENDED', 'STARTED']):
                                        print(f"\n{line}")
                                    elif line.startswith('2026/'):  # Robocopy timestamp lines
                                        print(f"\n{line}")

                            last_lines = lines
                            last_size = current_size
                        elif current_size != last_size:
                            # File was rewritten or truncated
                            last_lines = []
                            last_size = current_size
                            print("\n[Log file was updated - refreshing...]")
                except Exception as e:
                    pass  # File might be locked by robocopy

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("Monitoring stopped.")
        print("="*70)

if __name__ == '__main__':
    try:
        watch_live()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
