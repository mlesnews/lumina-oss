#!/usr/bin/env python3
"""
Tail All Homelab Logs

Unix-style log tailing utility for all logs generated in @homelab.
Tails logs from NAS centralized storage (L:/Logs/) with fallback to local logs.

Features:
- Tail all logs or specific category/service
- Follow mode (like tail -f)
- Color-coded output by log level
- Filter by level, category, service, or search term
- Real-time updates

Usage:
    # Tail all logs
    python tail_homelab_logs.py

    # Tail specific category
    python tail_homab_logs.py --category Application

    # Tail specific service
    python tail_homelab_logs.py --service Startup

    # Follow mode (default)
    python tail_homelab_logs.py --follow

    # Search for specific term
    python tail_homelab_logs.py --grep "ERROR"

    # Filter by log level
    python tail_homelab_logs.py --level ERROR

Tags: #LOGGING #HOMELAB #TAIL #MONITORING
"""

import sys
import argparse
import time
from pathlib import Path
from typing import List, Optional
import re
import logging
logger = logging.getLogger("tail_homelab_logs")


# ANSI color codes for terminal output
COLORS = {
    'RESET': '\033[0m',
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'WARN': '\033[33m',       # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[35m',   # Magenta
    'TIMESTAMP': '\033[90m',  # Gray
    'SERVICE': '\033[94m',    # Blue
}


class LogTailer:
    """Tail logs from NAS centralized storage"""

    def __init__(self, nas_path: Path = None, local_path: Path = None):
        self.nas_path = nas_path or Path("L:/Logs")
        self.local_path = local_path or Path(__file__).parent.parent.parent / "logs"
        self.file_handles = {}
        self.file_positions = {}

    def find_log_files(
        self,
        category: Optional[str] = None,
        service: Optional[str] = None
    ) -> List[Path]:
        """Find all log files matching criteria"""
        log_files = []

        # Try NAS first
        if self.nas_path.exists():
            search_path = self.nas_path
            if category:
                search_path = search_path / category
                if service:
                    search_path = search_path / service
            log_files.extend(search_path.rglob("*.log"))

        # Add local logs
        search_path = self.local_path
        if category:
            search_path = search_path / category
            if service:
                search_path = search_path / service
        if search_path.exists():
            log_files.extend(search_path.rglob("*.log"))

        # Remove duplicates and sort
        log_files = sorted(set(log_files), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)

        return log_files

    def parse_log_line(self, line: str) -> Optional[dict]:
        """Parse a log line into components"""
        # Format: [YYYY-MM-DD HH:MM:SS] [LEVEL] [NAME] MESSAGE
        pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] \[([^\]]+)\] (.+)'
        match = re.match(pattern, line.strip())

        if match:
            return {
                'timestamp': match.group(1),
                'level': match.group(2),
                'name': match.group(3),
                'message': match.group(4),
                'raw': line.strip()
            }
        return None

    def colorize_line(self, parsed: dict, use_color: bool = True) -> str:
        """Colorize log line for terminal output"""
        if not use_color:
            return parsed['raw']

        level_color = COLORS.get(parsed['level'], COLORS['RESET'])
        timestamp_color = COLORS['TIMESTAMP']
        service_color = COLORS['SERVICE']
        reset = COLORS['RESET']

        return (
            f"{timestamp_color}[{parsed['timestamp']}]{reset} "
            f"{level_color}[{parsed['level']}]{reset} "
            f"{service_color}[{parsed['name']}]{reset} "
            f"{parsed['message']}"
        )

    def tail_files(
        self,
        files: List[Path],
        follow: bool = True,
        level_filter: Optional[str] = None,
        grep_pattern: Optional[str] = None,
        use_color: bool = True
    ):
        """Tail log files with filtering"""
        # Open all files
        for file_path in files:
            try:
                if file_path.exists():
                    handle = open(file_path, 'r', encoding='utf-8', errors='ignore')
                    # Seek to end for new logs
                    handle.seek(0, 2)  # Seek to end
                    self.file_handles[file_path] = handle
                    self.file_positions[file_path] = handle.tell()
            except Exception as e:
                print(f"Warning: Could not open {file_path}: {e}", file=sys.stderr)

        if not self.file_handles:
            print("No log files found to tail.", file=sys.stderr)
            return

        print(f"Tailing {len(self.file_handles)} log file(s). Press Ctrl+C to stop.")
        print("=" * 80)

        try:
            while True:
                any_new = False

                for file_path, handle in self.file_handles.items():
                    # Check for new content
                    current_pos = handle.tell()
                    handle.seek(self.file_positions[file_path])

                    new_lines = handle.readlines()
                    if new_lines:
                        any_new = True
                        self.file_positions[file_path] = current_pos

                        for line in new_lines:
                            parsed = self.parse_log_line(line)
                            if not parsed:
                                # Unparsed line, print as-is
                                print(line.rstrip())
                                continue

                            # Apply filters
                            if level_filter and parsed['level'] != level_filter.upper():
                                continue

                            if grep_pattern and grep_pattern.lower() not in parsed['message'].lower():
                                continue

                            # Print colorized line
                            print(self.colorize_line(parsed, use_color))

                if not follow:
                    break

                if not any_new:
                    time.sleep(0.5)  # Small delay when no new content
                else:
                    time.sleep(0.1)  # Shorter delay when there's new content

        except KeyboardInterrupt:
            print("\nStopping log tail...")
        finally:
            # Close all file handles
            for handle in self.file_handles.values():
                handle.close()


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="Tail all homelab logs")
        parser.add_argument("--category", help="Filter by category (Application, System, AI, etc.)")
        parser.add_argument("--service", help="Filter by service name")
        parser.add_argument("--follow", "-f", action="store_true", default=True, help="Follow log files (default: True)")
        parser.add_argument("--no-follow", action="store_false", dest="follow", help="Don't follow, just show recent logs")
        parser.add_argument("--level", help="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
        parser.add_argument("--grep", help="Search for pattern in log messages")
        parser.add_argument("--no-color", action="store_true", help="Disable color output")
        parser.add_argument("--nas-path", help="NAS log path (default: L:/Logs)")
        parser.add_argument("--local-path", help="Local log path (default: project_root/logs)")

        args = parser.parse_args()

        nas_path = Path(args.nas_path) if args.nas_path else None
        local_path = Path(args.local_path) if args.local_path else None

        tailer = LogTailer(nas_path=nas_path, local_path=local_path)

        # Find log files
        log_files = tailer.find_log_files(category=args.category, service=args.service)

        if not log_files:
            print(f"No log files found for category={args.category}, service={args.service}", file=sys.stderr)
            return 1

        # Tail files
        tailer.tail_files(
            log_files,
            follow=args.follow,
            level_filter=args.level,
            grep_pattern=args.grep,
            use_color=not args.no_color
        )

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())