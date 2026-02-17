#!/usr/bin/env python3
"""
LUMINA Visual Progressive Meter
CLI utility for visual progress tracking with ETA and total count.
Integrates with JARVIS Progress Tracker and Cursor IDE status bar.

Usage:
  python lumina_visual_meter.py --process "My Task" --total 100 --current 50 --source "CLI"
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from jarvis_progress_tracker import get_progress_tracker
except ImportError:
    print("Error: Could not import JARVISProgressTracker.")
    sys.exit(1)

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()

def main():
    parser = argparse.ArgumentParser(description="LUMINA Visual Progressive Meter")
    parser.add_argument("--process", type=str, required=True, help="Name of the process")
    parser.add_argument("--id", type=str, default=None, help="Process ID (defaults to name)")
    parser.add_argument("--source", type=str, default="LUMINA-CLI", help="Source of the process")
    parser.add_argument("--total", type=int, required=True, help="Total items")
    parser.add_argument("--current", type=int, required=True, help="Current items completed")
    parser.add_argument("--complete", action="store_true", help="Mark as complete")
    parser.add_argument("--fail", type=str, default=None, help="Mark as failed with error message")
    parser.add_argument("--show-bar", action="store_true", help="Show terminal progress bar")

    args = parser.parse_args()

    process_id = args.id or args.process.lower().replace(" ", "_")
    tracker = get_progress_tracker(project_root)

    # Register if new
    if process_id not in tracker.processes:
        tracker.register_process(process_id, args.process, args.source, args.total)

    # Update
    tracker.update_progress(process_id, args.current, args.total)

    # Get current status for display
    process = tracker.processes[process_id]
    eta = process.eta_string

    if args.show_bar:
        print_progress_bar(
            args.current,
            args.total,
            prefix=f"🚀 {args.process}",
            suffix=f"({args.current}/{args.total}) ETA: {eta}",
            length=40
        )

    if args.complete:
        tracker.complete_process(process_id)
        if args.show_bar:
            print(f"✅ {args.process} COMPLETE")

    if args.fail:
        tracker.fail_process(process_id, args.fail)
        if args.show_bar:
            print(f"❌ {args.process} FAILED: {args.fail}")

    # Ensure status is flushed before exit
    tracker._update_cursor_status()

if __name__ == "__main__":


    main()