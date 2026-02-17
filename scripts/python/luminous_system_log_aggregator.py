#!/usr/bin/env python3
"""
Luminous System Log Aggregator

"One ring to find them, and the rest to bind them."

Aggregates ALL system logs into a single Luminous system log for unified monitoring.
All processes log to this single aggregated log, which can be tailed for real-time monitoring.

Tags: #LOG_AGGREGATION #LUMINOUS_LOG #SYSTEM_LOG #ONE_RING #HEADLESS @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import queue

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("LuminousSystemLog")


@dataclass
class LogEntry:
    """Single log entry in Luminous system log"""
    timestamp: datetime
    source: str  # Process/service name
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class LuminousSystemLogAggregator:
    """
    Luminous System Log Aggregator

    "One ring to find them, and the rest to bind them."

    Aggregates all system logs into a single unified log:
    - All processes log to Luminous system log
    - Real-time aggregation from multiple sources
    - Single log file for monitoring
    - Can be tailed for real-time updates
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Luminous system log aggregator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Get NAS logs path (L: drive)
        try:
            from nas_logging_watchdog import get_nas_logs_path
            self.log_dir = get_nas_logs_path("system")
        except ImportError:
            # Fallback to local
            self.log_dir = self.project_root / "data" / "logs" / "system"
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Luminous system log file
        self.luminous_log_file = self.log_dir / f"luminous_system_{datetime.now().strftime('%Y%m%d')}.log"

        # Log queue for aggregation
        self.log_queue = queue.Queue()

        # Active log sources
        self.log_sources: Dict[str, bool] = {}

        # Aggregation thread
        self._aggregation_thread: Optional[threading.Thread] = None
        self._running = False

        # Recent log entries (for tailing)
        self.recent_logs = deque(maxlen=1000)

        self.logger = logger
        self.logger.info("✅ Luminous System Log Aggregator initialized")
        self.logger.info(f"   📁 Luminous log: {self.luminous_log_file}")
        self.logger.info("   💍 'One ring to find them, and the rest to bind them.'")

    def start_aggregation(self):
        """Start log aggregation"""
        if self._running:
            return

        self._running = True
        self._aggregation_thread = threading.Thread(
            target=self._aggregation_loop,
            name="LuminousLogAggregator",
            daemon=True
        )
        self._aggregation_thread.start()

        self.logger.info("🔄 Luminous log aggregation started")

    def stop_aggregation(self):
        """Stop log aggregation"""
        self._running = False
        if self._aggregation_thread:
            self._aggregation_thread.join(timeout=5.0)
        self.logger.info("🛑 Luminous log aggregation stopped")

    def _aggregation_loop(self):
        """Main aggregation loop"""
        while self._running:
            try:
                # Get log entry from queue (with timeout)
                try:
                    entry = self.log_queue.get(timeout=1.0)
                    self._write_log_entry(entry)
                    self.log_queue.task_done()
                except queue.Empty:
                    continue
            except Exception as e:
                self.logger.error(f"Error in aggregation loop: {e}")
                time.sleep(1.0)

    def _write_log_entry(self, entry: LogEntry):
        """Write log entry to Luminous system log"""
        try:
            # Format log entry
            log_line = (
                f"{entry.timestamp.isoformat()} "
                f"[{entry.level}] "
                f"[{entry.source}] "
                f"{entry.message}"
            )

            # Add metadata if present
            if entry.metadata:
                metadata_str = json.dumps(entry.metadata, default=str)
                log_line += f" | {metadata_str}"

            log_line += "\n"

            # Write to file
            with open(self.luminous_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)

            # Add to recent logs
            self.recent_logs.append(entry)

        except Exception as e:
            self.logger.error(f"Failed to write log entry: {e}")

    def log(self, source: str, level: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add log entry to Luminous system log

        Args:
            source: Source process/service name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            metadata: Optional metadata
        """
        entry = LogEntry(
            timestamp=datetime.now(),
            source=source,
            level=level.upper(),
            message=message,
            metadata=metadata or {}
        )

        # Add to queue
        self.log_queue.put(entry)

        # Register source
        self.log_sources[source] = True

    def get_recent_logs(self, count: int = 100) -> List[LogEntry]:
        """Get recent log entries"""
        return list(self.recent_logs)[-count:]

    def tail_log(self, callback: callable, follow: bool = True):
        """
        Tail Luminous system log

        Args:
            callback: Function to call with each new log entry
            follow: If True, continue tailing (like tail -f)
        """
        if not self.luminous_log_file.exists():
            return

        # Read existing logs
        with open(self.luminous_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                entry = self._parse_log_line(line)
                if entry:
                    callback(entry)

        # Follow new logs
        if follow:
            # Monitor queue for new entries
            while True:
                try:
                    entry = self.log_queue.get(timeout=1.0)
                    callback(entry)
                    self.log_queue.task_done()
                except queue.Empty:
                    continue

    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """Parse log line into LogEntry"""
        try:
            # Format: TIMESTAMP [LEVEL] [SOURCE] MESSAGE | METADATA
            parts = line.strip().split(' | ', 1)
            main_part = parts[0]
            metadata_str = parts[1] if len(parts) > 1 else None

            # Parse main part
            # Format: TIMESTAMP [LEVEL] [SOURCE] MESSAGE
            import re
            match = re.match(r'^(.+?) \[(.+?)\] \[(.+?)\] (.+)$', main_part)
            if not match:
                return None

            timestamp_str, level, source, message = match.groups()
            timestamp = datetime.fromisoformat(timestamp_str)

            # Parse metadata
            metadata = {}
            if metadata_str:
                try:
                    metadata = json.loads(metadata_str)
                except:
                    pass

            return LogEntry(
                timestamp=timestamp,
                source=source,
                level=level,
                message=message,
                metadata=metadata
            )
        except Exception as e:
            self.logger.debug(f"Failed to parse log line: {e}")
            return None

    def get_log_statistics(self) -> Dict[str, Any]:
        try:
            """Get log statistics"""
            return {
                "total_entries": len(self.recent_logs),
                "active_sources": len(self.log_sources),
                "sources": list(self.log_sources.keys()),
                "log_file": str(self.luminous_log_file),
                "log_file_size": self.luminous_log_file.stat().st_size if self.luminous_log_file.exists() else 0
            }


        except Exception as e:
            self.logger.error(f"Error in get_log_statistics: {e}", exc_info=True)
            raise
# Global instance
_global_aggregator: Optional[LuminousSystemLogAggregator] = None


def get_luminous_log(project_root: Optional[Path] = None) -> LuminousSystemLogAggregator:
    try:
        """Get or create global Luminous system log aggregator"""
        global _global_aggregator

        if _global_aggregator is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_aggregator = LuminousSystemLogAggregator(project_root)
            _global_aggregator.start_aggregation()

        return _global_aggregator


    except Exception as e:
        logger.error(f"Error in get_luminous_log: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test Luminous system log
    print("=" * 80)
    print("Luminous System Log Aggregator")
    print("=" * 80)
    print()
    print("'One ring to find them, and the rest to bind them.'")
    print()

    aggregator = get_luminous_log()

    # Test logging
    aggregator.log("JARVIS", "INFO", "JARVIS starting up")
    aggregator.log("LUMINA", "INFO", "LUMINA system initialized")
    aggregator.log("JARVIS", "WARNING", "Low memory detected")
    aggregator.log("LUMINA", "ERROR", "Connection failed", {"retry_count": 3})

    time.sleep(2)  # Wait for aggregation

    # Get statistics
    stats = aggregator.get_log_statistics()
    print("Log Statistics:")
    print(json.dumps(stats, indent=2, default=str))

    print()
    print(f"✅ Luminous system log: {aggregator.luminous_log_file}")
