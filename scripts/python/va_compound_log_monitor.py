#!/usr/bin/env python3
"""
Virtual Assistant Compound Log Parsing/Tailing LIVE-MONITORING - ORDER 66: @DOIT

Monitors and parses compound logs from all virtual assistants in real-time:
- IMVA (Iron Man Virtual Assistant)
- ACVA (Anakin/Vader Combat Virtual Assistant)
- ULTRON
- JARVIS VA
- All other VAs

Combines multiple log sources into a unified, live-monitored stream with:
- Real-time tailing
- Log parsing and filtering
- Event detection
- Pattern matching
- Alert generation

Tags: #VAS #LOGS #MONITORING #TAILING #PARSING #LIVE #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import os
import time
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging
import threading
from collections import deque, defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# ALWAYS use the standard logging module: lumina_logger
# This is a critical requirement - all scripts must use lumina_logger.get_logger()
from lumina_logger import get_logger

logger = get_logger("VACompoundLogMonitor")


class LogLevel(Enum):
    """Log level"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class VAEventType(Enum):
    """Virtual Assistant event types"""
    STARTED = "started"
    STOPPED = "stopped"
    ERROR = "error"
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    VOICE_COMMAND = "voice_command"
    INTERACTION = "interaction"
    SYSTEM_ALERT = "system_alert"
    POSITION_CHANGED = "position_changed"
    HEALTH_CHANGED = "health_changed"
    STATE_CHANGED = "state_changed"


@dataclass
class LogEntry:
    """Log entry structure"""
    timestamp: str
    va_id: str
    level: LogLevel
    message: str
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['level'] = self.level.value
        return result


@dataclass
class VAEvent:
    """Virtual Assistant event"""
    event_type: VAEventType
    va_id: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)
    log_entry: Optional[LogEntry] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        if self.log_entry:
            result['log_entry'] = self.log_entry.to_dict()
        return result


class VACompoundLogMonitor:
    """
    Virtual Assistant Compound Log Monitor

    Monitors and parses logs from all VAs in real-time, combining them into
    a unified stream with event detection and pattern matching.
    """

    # VA log patterns
    VA_LOG_PATTERNS = {
        'imva': [
            r'ironman.*virtual.*assistant',
            r'IMVA',
            r'IRON.*MAN.*VA'
        ],
        'acva': [
            r'acva',
            r'anakin.*combat.*va',
            r'AC.*VA'
        ],
        'ultron': [
            r'ultron',
            r'ULTRON'
        ],
        'jarvis_va': [
            r'jarvis.*va',
            r'JARVIS.*VA'
        ]
    }

    # Event detection patterns
    EVENT_PATTERNS = {
        VAEventType.STARTED: [
            r'started',
            r'initialized',
            r'online',
            r'ready'
        ],
        VAEventType.STOPPED: [
            r'stopped',
            r'closed',
            r'exited',
            r'shutdown'
        ],
        VAEventType.ERROR: [
            r'error',
            r'exception',
            r'failed',
            r'critical'
        ],
        VAEventType.COMBAT_STARTED: [
            r'combat.*started',
            r'fight.*started',
            r'lightsaber.*activated'
        ],
        VAEventType.COMBAT_ENDED: [
            r'combat.*ended',
            r'fight.*ended',
            r'combat.*complete'
        ],
        VAEventType.VOICE_COMMAND: [
            r'voice.*command',
            r'heard.*command',
            r'processing.*command'
        ],
        VAEventType.INTERACTION: [
            r'clicked',
            r'interaction',
            r'user.*action'
        ],
        VAEventType.SYSTEM_ALERT: [
            r'alert',
            r'warning',
            r'notification'
        ],
        VAEventType.POSITION_CHANGED: [
            r'position.*changed',
            r'moved.*to',
            r'new.*position'
        ],
        VAEventType.HEALTH_CHANGED: [
            r'health.*changed',
            r'damage.*taken',
            r'health.*updated'
        ],
        VAEventType.STATE_CHANGED: [
            r'state.*changed',
            r'mode.*changed',
            r'status.*changed'
        ]
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize compound log monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.data_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Log files to monitor
        self.log_files: Dict[str, Path] = {}
        self._discover_log_files()

        # Monitoring state
        self.monitoring: bool = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.file_handles: Dict[str, Any] = {}
        self.file_positions: Dict[str, int] = {}

        # Event handlers
        self.event_handlers: Dict[VAEventType, List[Callable]] = defaultdict(list)

        # Log buffer (circular buffer for recent logs)
        self.log_buffer: deque = deque(maxlen=1000)

        # Event history
        self.event_history: deque = deque(maxlen=500)

        # Statistics
        self.stats = {
            "total_entries": 0,
            "entries_by_va": defaultdict(int),
            "entries_by_level": defaultdict(int),
            "events_detected": defaultdict(int),
            "start_time": None
        }

        logger.info("✅ VA Compound Log Monitor initialized")
        logger.info(f"   Monitoring {len(self.log_files)} log files")

    def _discover_log_files(self):
        try:
            """Discover log files for all VAs"""
            # Standard log locations
            log_locations = [
                self.logs_dir,
                self.data_dir / "vas",
                self.project_root / "logs"
            ]

            # Explicitly add SSH connections log (with timestamps)
            ssh_log = self.logs_dir / "ssh_connections.log"
            if ssh_log.exists() or self.logs_dir.exists():
                self.log_files["ssh_connections"] = ssh_log
                logger.info(f"   Found log: ssh_connections -> {ssh_log}")

            # Look for log files
            for location in log_locations:
                if not location.exists():
                    continue

                for log_file in location.glob("*.log"):
                    # Skip if already added
                    if log_file in self.log_files.values():
                        continue

                    # Try to identify VA from filename
                    va_id = self._identify_va_from_filename(log_file.name)
                    if va_id:
                        self.log_files[va_id] = log_file
                        logger.info(f"   Found log: {va_id} -> {log_file}")

            # Also check for lumina logger files
            for log_file in self.logs_dir.glob("*.log"):
                if log_file not in self.log_files.values():
                    # Try to identify from content or use generic name
                    va_id = f"va_{len(self.log_files)}"
                    self.log_files[va_id] = log_file
                    logger.info(f"   Found log: {va_id} -> {log_file}")

        except Exception as e:
            self.logger.error(f"Error in _discover_log_files: {e}", exc_info=True)
            raise
    def _identify_va_from_filename(self, filename: str) -> Optional[str]:
        """Identify VA from log filename"""
        filename_lower = filename.lower()

        if 'imva' in filename_lower or 'ironman' in filename_lower or 'iron_man' in filename_lower:
            return 'imva'
        elif 'acva' in filename_lower or 'anakin' in filename_lower:
            return 'acva'
        elif 'ultron' in filename_lower:
            return 'ultron'
        elif 'jarvis' in filename_lower and 'va' in filename_lower:
            return 'jarvis_va'
        elif 'va' in filename_lower:
            # Generic VA
            return filename_lower.replace('.log', '').replace('_', '')

        return None

    def parse_log_line(self, line: str, va_id: str, source_file: Path) -> Optional[LogEntry]:
        """Parse a log line into a LogEntry"""
        if not line.strip():
            return None

        # Try to parse standard log format: TIMESTAMP LEVEL MESSAGE
        # Common formats:
        # - ISO format: 2025-01-24T18:00:00 [LEVEL] message
        # - Standard: 2025-01-24 18:00:00,123 [LEVEL] message
        # - Simple: LEVEL: message

        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)'
        level_pattern = r'\[?(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]?'

        timestamp = datetime.now().isoformat()
        level = LogLevel.INFO
        message = line.strip()

        # Try to extract timestamp
        ts_match = re.search(timestamp_pattern, line)
        if ts_match:
            timestamp = ts_match.group(1)
            message = line[ts_match.end():].strip()

        # Try to extract level
        level_match = re.search(level_pattern, message, re.IGNORECASE)
        if level_match:
            try:
                level = LogLevel[level_match.group(1).upper()]
            except KeyError:
                pass
            message = message[level_match.end():].strip()

        # Clean up message
        message = re.sub(r'^\W+', '', message)  # Remove leading non-word chars

        return LogEntry(
            timestamp=timestamp,
            va_id=va_id,
            level=level,
            message=message,
            source_file=str(source_file.name),
            metadata={}
        )

    def detect_events(self, log_entry: LogEntry) -> List[VAEvent]:
        """Detect events from log entry"""
        events = []
        message_lower = log_entry.message.lower()

        for event_type, patterns in self.EVENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    event = VAEvent(
                        event_type=event_type,
                        va_id=log_entry.va_id,
                        timestamp=log_entry.timestamp,
                        details={"pattern": pattern, "message": log_entry.message},
                        log_entry=log_entry
                    )
                    events.append(event)
                    self.stats["events_detected"][event_type.value] += 1
                    break  # Only detect one event type per entry

        return events

    def start_monitoring(self, callback: Optional[Callable[[LogEntry], None]] = None):
        """Start live monitoring of all log files"""
        if self.monitoring:
            logger.warning("⚠️  Monitoring already started")
            return

        self.monitoring = True
        self.stats["start_time"] = datetime.now().isoformat()

        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(callback,),
            daemon=True
        )
        self.monitor_thread.start()

        logger.info("✅ Started compound log monitoring")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False

        # Close file handles
        for handle in self.file_handles.values():
            try:
                handle.close()
            except Exception:
                pass

        self.file_handles.clear()
        self.file_positions.clear()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        logger.info("✅ Stopped compound log monitoring")

    def _monitor_loop(self, callback: Optional[Callable[[LogEntry], None]] = None):
        """Main monitoring loop"""
        # Initialize file positions
        for va_id, log_file in self.log_files.items():
            if log_file.exists():
                try:
                    # Start from end of file (tail)
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(0, 2)  # Seek to end
                        self.file_positions[va_id] = f.tell()
                except Exception as e:
                    logger.warning(f"⚠️  Could not initialize position for {va_id}: {e}")
                    self.file_positions[va_id] = 0

        # Monitoring loop
        while self.monitoring:
            try:
                for va_id, log_file in self.log_files.items():
                    if not log_file.exists():
                        continue

                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            # Seek to last known position
                            last_pos = self.file_positions.get(va_id, 0)
                            f.seek(last_pos)

                            # Read new lines
                            new_lines = f.readlines()
                            self.file_positions[va_id] = f.tell()

                            # Process new lines
                            for line in new_lines:
                                log_entry = self.parse_log_line(line, va_id, log_file)
                                if log_entry:
                                    self.log_buffer.append(log_entry)
                                    self.stats["total_entries"] += 1
                                    self.stats["entries_by_va"][va_id] += 1
                                    self.stats["entries_by_level"][log_entry.level.value] += 1

                                    # Detect events
                                    events = self.detect_events(log_entry)
                                    for event in events:
                                        self.event_history.append(event)
                                        # Call event handlers
                                        for handler in self.event_handlers.get(event.event_type, []):
                                            try:
                                                handler(event)
                                            except Exception as e:
                                                logger.error(f"❌ Event handler error: {e}")

                                    # Call callback if provided
                                    if callback:
                                        try:
                                            callback(log_entry)
                                        except Exception as e:
                                            logger.error(f"❌ Callback error: {e}")

                    except Exception as e:
                        logger.debug(f"⚠️  Error reading {va_id} log: {e}")

                # Sleep before next check
                time.sleep(0.1)  # 100ms polling interval

            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(1.0)

    def add_event_handler(self, event_type: VAEventType, handler: Callable[[VAEvent], None]):
        """Add event handler"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"✅ Added event handler for {event_type.value}")

    def get_recent_logs(self, count: int = 100, va_id: Optional[str] = None) -> List[LogEntry]:
        """Get recent log entries"""
        logs = list(self.log_buffer)

        if va_id:
            logs = [log for log in logs if log.va_id == va_id]

        return logs[-count:]

    def get_recent_events(self, count: int = 100, event_type: Optional[VAEventType] = None) -> List[VAEvent]:
        """Get recent events"""
        events = list(self.event_history)

        if event_type:
            events = [event for event in events if event.event_type == event_type]

        return events[-count:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            "monitoring": self.monitoring,
            "log_files_monitored": len(self.log_files),
            "stats": dict(self.stats),
            "recent_logs_count": len(self.log_buffer),
            "recent_events_count": len(self.event_history)
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Compound Log Monitor - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--tail', action='store_true', help='Tail logs in real-time')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--recent', type=int, default=50, help='Show recent logs (default: 50)')
    parser.add_argument('--va-id', type=str, help='Filter by VA ID')
    parser.add_argument('--events', action='store_true', help='Show recent events')

    args = parser.parse_args()

    monitor = VACompoundLogMonitor(project_root=args.project_root)

    if args.stats:
        stats = monitor.get_statistics()
        print("\n📊 VA Compound Log Monitor Statistics:")
        print("="*80)
        print(f"  Monitoring: {stats['monitoring']}")
        print(f"  Log Files: {stats['log_files_monitored']}")
        print(f"  Total Entries: {stats['stats']['total_entries']}")
        print(f"\n  Entries by VA:")
        for va_id, count in stats['stats']['entries_by_va'].items():
            print(f"    • {va_id}: {count}")
        print(f"\n  Entries by Level:")
        for level, count in stats['stats']['entries_by_level'].items():
            print(f"    • {level}: {count}")
        print(f"\n  Events Detected:")
        for event_type, count in stats['stats']['events_detected'].items():
            print(f"    • {event_type}: {count}")
        return 0

    if args.events:
        events = monitor.get_recent_events(count=args.recent)
        print("\n📋 Recent Events:")
        print("="*80)
        for event in events:
            print(f"\n  [{event.timestamp}] {event.event_type.value.upper()} - {event.va_id}")
            if event.details:
                print(f"    {event.details.get('message', '')}")
        return 0

    if args.tail:
        print("\n📡 Tail Mode: Monitoring logs in real-time...")
        print("="*80)
        print("Press Ctrl+C to stop\n")

        def print_log(log_entry: LogEntry):
            print(f"[{log_entry.timestamp}] [{log_entry.level.value}] [{log_entry.va_id}] {log_entry.message}")

        try:
            monitor.start_monitoring(callback=print_log)
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n✅ Stopping monitor...")
            monitor.stop_monitoring()
            return 0

    # Default: show recent logs
    logs = monitor.get_recent_logs(count=args.recent, va_id=args.va_id)
    print(f"\n📋 Recent Logs ({len(logs)} entries):")
    print("="*80)
    for log in logs:
        print(f"[{log.timestamp}] [{log.level.value}] [{log.va_id}] {log.message}")

    return 0


if __name__ == "__main__":


    sys.exit(main())