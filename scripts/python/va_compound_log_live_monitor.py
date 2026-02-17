#!/usr/bin/env python3
"""
Virtual Assistant Compound Log Live Monitor - ORDER 66: @DOIT

Live monitoring and tailing of virtual assistant compound logs with real-time parsing.
Monitors multiple log sources and provides unified live monitoring interface.

Tags: #LOGS #MONITORING #TAILING #PARSING #COMPOUND #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import logging
import threading
import queue

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VACompoundLogMonitor")


@dataclass
class LogEntry:
    """Parsed log entry"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    raw_line: str
    source_file: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogSource:
    """Log file source"""
    source_id: str
    file_path: Path
    last_position: int = 0
    active: bool = True
    pattern: Optional[str] = None  # Optional regex pattern for filtering


class VACompoundLogMonitor:
    """
    Virtual Assistant Compound Log Live Monitor

    Monitors and tails multiple log files in real-time with parsing and filtering
    """

    # Common log patterns
    LOG_PATTERNS = {
        "standard": re.compile(r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[.,]\d+)?\s*\[?(\w+)\]?\s*(\w+):\s*(.*)'),
        "iso_timestamp": re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.,]\d+)\s*\[(\w+)\]\s*(\w+):\s*(.*)'),
        "simple": re.compile(r'\[(\w+)\]\s*(\w+):\s*(.*)'),
        "json": re.compile(r'\{.*"timestamp".*"level".*"message".*\}'),
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize compound log monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.data_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Log sources
        self.log_sources: Dict[str, LogSource] = {}

        # Monitoring state
        self.monitoring: bool = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Log buffer (circular buffer for recent entries)
        self.log_buffer: deque = deque(maxlen=1000)  # Keep last 1000 entries

        # Filters
        self.level_filter: Set[str] = set()  # Empty = all levels
        self.logger_filter: Set[str] = set()  # Empty = all loggers
        self.message_filter: Optional[str] = None  # Regex pattern

        # Statistics
        self.stats = {
            "total_entries": 0,
            "entries_by_level": {},
            "entries_by_logger": {},
            "start_time": None,
            "last_update": None
        }

        logger.info("✅ VA Compound Log Monitor initialized")

    def discover_log_files(self) -> List[Path]:
        try:
            """Discover all log files in the project"""
            log_files = []

            # Check common log locations
            search_paths = [
                self.logs_dir,
                self.data_dir,
                self.project_root / "logs",
                self.data_dir / "vas" / "logs",
                self.data_dir / "jarvis_intelligence",
            ]

            # Also check for IMVA-specific logs
            imva_logs = [
                self.data_dir / "imva" / "logs",
                self.data_dir / "ironman_va" / "logs",
            ]
            search_paths.extend(imva_logs)

            for search_path in search_paths:
                if search_path.exists():
                    # Find all .log files
                    for log_file in search_path.rglob("*.log"):
                        log_files.append(log_file)

                    # Find all .txt files that might be logs
                    for log_file in search_path.rglob("*.txt"):
                        if "log" in log_file.name.lower():
                            log_files.append(log_file)

            # Also check for lumina_logger output
            for log_file in self.data_dir.rglob("*lumina*.log"):
                log_files.append(log_file)

            logger.info(f"✅ Discovered {len(log_files)} log files")
            return log_files

        except Exception as e:
            self.logger.error(f"Error in discover_log_files: {e}", exc_info=True)
            raise
    def add_log_source(self, source_id: str, file_path: Path, pattern: Optional[str] = None) -> Dict[str, Any]:
        try:
            """Add a log source to monitor"""
            if not file_path.exists():
                return {"error": f"Log file not found: {file_path}"}

            log_source = LogSource(
                source_id=source_id,
                file_path=file_path,
                pattern=pattern
            )

            self.log_sources[source_id] = log_source
            logger.info(f"✅ Added log source: {source_id} ({file_path})")

            return {"success": True, "source_id": source_id}

        except Exception as e:
            self.logger.error(f"Error in add_log_source: {e}", exc_info=True)
            raise
    def auto_discover_and_add(self) -> Dict[str, Any]:
        """Automatically discover and add all log files"""
        log_files = self.discover_log_files()

        added = 0
        for log_file in log_files:
            source_id = f"log_{added}_{log_file.stem}"
            result = self.add_log_source(source_id, log_file)
            if result.get("success"):
                added += 1

        logger.info(f"✅ Auto-discovered and added {added} log sources")
        return {"success": True, "sources_added": added, "total_sources": len(self.log_sources)}

    def parse_log_line(self, line: str, source_file: str) -> Optional[LogEntry]:
        """Parse a log line into structured entry"""
        if not line.strip():
            return None

        # Try different patterns
        for pattern_name, pattern in self.LOG_PATTERNS.items():
            match = pattern.match(line.strip())
            if match:
                groups = match.groups()

                if pattern_name == "iso_timestamp":
                    timestamp, level, logger_name, message = groups
                elif pattern_name == "standard":
                    timestamp = groups[0] if groups[0] else datetime.now().isoformat()
                    level = groups[1] if groups[1] else "INFO"
                    logger_name = groups[2] if len(groups) > 2 else "unknown"
                    message = groups[3] if len(groups) > 3 else line
                elif pattern_name == "simple":
                    level, logger_name, message = groups
                    timestamp = datetime.now().isoformat()
                else:
                    continue

                return LogEntry(
                    timestamp=timestamp or datetime.now().isoformat(),
                    level=level.upper(),
                    logger_name=logger_name,
                    message=message,
                    raw_line=line,
                    source_file=source_file
                )

        # Fallback: create entry from raw line
        return LogEntry(
            timestamp=datetime.now().isoformat(),
            level="UNKNOWN",
            logger_name="unknown",
            message=line.strip(),
            raw_line=line,
            source_file=source_file
        )

    def should_include_entry(self, entry: LogEntry) -> bool:
        """Check if entry should be included based on filters"""
        # Level filter
        if self.level_filter and entry.level not in self.level_filter:
            return False

        # Logger filter
        if self.logger_filter and entry.logger_name not in self.logger_filter:
            return False

        # Message filter (regex)
        if self.message_filter:
            try:
                if not re.search(self.message_filter, entry.message, re.IGNORECASE):
                    return False
            except re.error:
                pass

        return True

    def tail_log_file(self, source: LogSource) -> List[LogEntry]:
        """Tail a log file and return new entries"""
        new_entries = []

        try:
            with open(source.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Seek to last position
                f.seek(source.last_position)

                # Read new lines
                new_lines = f.readlines()

                # Update position
                source.last_position = f.tell()

                # Parse lines
                for line in new_lines:
                    entry = self.parse_log_line(line, str(source.file_path))
                    if entry and self.should_include_entry(entry):
                        new_entries.append(entry)

        except Exception as e:
            logger.warning(f"⚠️  Error tailing {source.source_id}: {e}")

        return new_entries

    def monitor_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        logger.info("🔍 Starting log monitoring loop...")
        self.stats["start_time"] = datetime.now().isoformat()

        while not self.stop_event.is_set():
            all_new_entries = []

            # Tail all active log sources
            for source_id, source in self.log_sources.items():
                if not source.active:
                    continue

                new_entries = self.tail_log_file(source)
                all_new_entries.extend(new_entries)

            # Process new entries
            for entry in all_new_entries:
                self.log_buffer.append(entry)
                self.stats["total_entries"] += 1
                self.stats["entries_by_level"][entry.level] = self.stats["entries_by_level"].get(entry.level, 0) + 1
                self.stats["entries_by_logger"][entry.logger_name] = self.stats["entries_by_logger"].get(entry.logger_name, 0) + 1

                # Print to console (can be customized)
                self._print_entry(entry)

            self.stats["last_update"] = datetime.now().isoformat()

            # Sleep before next check
            time.sleep(0.1)  # 100ms polling interval

        logger.info("✅ Monitoring loop stopped")

    def _print_entry(self, entry: LogEntry):
        """Print log entry to console"""
        # Color coding by level
        level_colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",   # Green
            "WARNING": "\033[33m", # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m" # Magenta
        }
        color = level_colors.get(entry.level, "")
        reset = "\033[0m"

        # Format: [TIMESTAMP] [LEVEL] [LOGGER] MESSAGE
        print(f"{color}[{entry.timestamp}] [{entry.level}] [{entry.logger_name}] {entry.message}{reset}")

    def start_monitoring(self, auto_discover: bool = True) -> Dict[str, Any]:
        """Start live monitoring"""
        if self.monitoring:
            return {"error": "Monitoring already active"}

        # Auto-discover logs if requested
        if auto_discover and not self.log_sources:
            self.auto_discover_and_add()

        if not self.log_sources:
            return {"error": "No log sources to monitor"}

        self.monitoring = True
        self.stop_event.clear()

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info(f"✅ Started monitoring {len(self.log_sources)} log sources")
        return {
            "success": True,
            "sources": len(self.log_sources),
            "message": f"Monitoring {len(self.log_sources)} log sources"
        }

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop live monitoring"""
        if not self.monitoring:
            return {"error": "Monitoring not active"}

        self.monitoring = False
        self.stop_event.set()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        logger.info("✅ Stopped monitoring")
        return {"success": True, "message": "Monitoring stopped"}

    def get_recent_entries(self, count: int = 50) -> List[LogEntry]:
        """Get recent log entries"""
        return list(self.log_buffer)[-count:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            **self.stats,
            "active_sources": len([s for s in self.log_sources.values() if s.active]),
            "total_sources": len(self.log_sources),
            "buffer_size": len(self.log_buffer),
            "monitoring": self.monitoring
        }

    def set_filters(self, levels: Optional[List[str]] = None, 
                   loggers: Optional[List[str]] = None,
                   message_pattern: Optional[str] = None):
        """Set log filters"""
        if levels:
            self.level_filter = set(levels)
        if loggers:
            self.logger_filter = set(loggers)
        if message_pattern:
            self.message_filter = message_pattern

        logger.info(f"✅ Filters updated: levels={self.level_filter}, loggers={self.logger_filter}, message={self.message_filter}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Compound Log Live Monitor - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--stop', action='store_true', help='Stop monitoring')
    parser.add_argument('--auto-discover', action='store_true', default=True, help='Auto-discover log files')
    parser.add_argument('--add-log', type=Path, help='Add specific log file')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--recent', type=int, default=20, help='Show recent entries (default: 20)')
    parser.add_argument('--filter-level', nargs='+', help='Filter by log level (INFO, ERROR, etc.)')
    parser.add_argument('--filter-logger', nargs='+', help='Filter by logger name')
    parser.add_argument('--filter-message', type=str, help='Filter by message pattern (regex)')

    args = parser.parse_args()

    monitor = VACompoundLogMonitor(project_root=args.project_root)

    # Set filters
    if args.filter_level or args.filter_logger or args.filter_message:
        monitor.set_filters(
            levels=args.filter_level,
            loggers=args.filter_logger,
            message_pattern=args.filter_message
        )

    # Add specific log
    if args.add_log:
        result = monitor.add_log_source("custom", args.add_log)
        if not result.get("success"):
            print(f"❌ Error: {result.get('error')}")
            return 1

    # Start monitoring
    if args.start:
        result = monitor.start_monitoring(auto_discover=args.auto_discover)
        if result.get("success"):
            print(f"\n✅ {result['message']}")
            print("   Press Ctrl+C to stop...\n")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
                print("\n✅ Monitoring stopped")
        else:
            print(f"❌ Error: {result.get('error')}")
            return 1
        return 0

    # Stop monitoring
    if args.stop:
        result = monitor.stop_monitoring()
        if result.get("success"):
            print(f"✅ {result['message']}")
        return 0

    # Show statistics
    if args.stats:
        stats = monitor.get_statistics()
        print("\n📊 Log Monitoring Statistics:")
        print("="*80)
        print(f"  Total Entries: {stats['total_entries']}")
        print(f"  Active Sources: {stats['active_sources']}")
        print(f"  Total Sources: {stats['total_sources']}")
        print(f"  Buffer Size: {stats['buffer_size']}")
        print(f"  Monitoring: {stats['monitoring']}")
        if stats.get('start_time'):
            print(f"  Started: {stats['start_time']}")
        if stats.get('last_update'):
            print(f"  Last Update: {stats['last_update']}")
        print(f"\n  Entries by Level:")
        for level, count in sorted(stats['entries_by_level'].items()):
            print(f"    • {level}: {count}")
        return 0

    # Show recent entries
    if args.recent:
        entries = monitor.get_recent_entries(args.recent)
        print(f"\n📋 Recent {len(entries)} Log Entries:")
        print("="*80)
        for entry in entries:
            print(f"[{entry.timestamp}] [{entry.level}] [{entry.logger_name}] {entry.message}")
        return 0

    # Default: auto-discover and show info
    result = monitor.auto_discover_and_add()
    print(f"\n🔍 Discovered {result['sources_added']} log sources")
    print(f"   Total sources: {result['total_sources']}")
    print("\n💡 Use --start to begin live monitoring")
    print("   Use --help for more options")
    return 0


if __name__ == "__main__":


    sys.exit(main())