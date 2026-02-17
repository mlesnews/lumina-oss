#!/usr/bin/env python3
"""
Centralized Log Parser and Aggregator
Parses startup logs (IDE and services) and aggregates patterns over time for debugging

Features:
- Parses IDE startup logs
- Parses service startup logs
- Aggregates logs by patterns
- Tracks patterns over time
- Enables debugging and analysis
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Pattern
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger

logger = get_logger("CentralizedLogParser")


class LogSource(Enum):
    """Log source types"""
    IDE_STARTUP = "ide_startup"
    SERVICE_STARTUP = "service_startup"
    SERVICE_RUNTIME = "service_runtime"
    APPLICATION = "application"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    source: LogSource
    component: str
    message: str
    raw_line: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "source": self.source.value,
            "component": self.component,
            "message": self.message,
            "raw_line": self.raw_line,
            "metadata": self.metadata
        }


@dataclass
class LogPattern:
    """Pattern detected in logs"""
    pattern_id: str
    pattern_name: str
    regex: str
    description: str
    category: str
    severity: str
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    examples: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "regex": self.regex,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "occurrences": self.occurrences,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "examples": self.examples[:5]  # Limit examples
        }


class CentralizedLogParser:
    """Parse and aggregate centralized logs"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize log parser"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logs_dir = project_root / "logs"
        self.nas_logs_path = Path(r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\logs")

        # Aggregation storage
        self.aggregated_data_dir = project_root / "data" / "log_aggregation"
        self.aggregated_data_dir.mkdir(parents=True, exist_ok=True)

        # Pattern registry
        self.patterns_file = self.aggregated_data_dir / "patterns.json"
        self.patterns: Dict[str, LogPattern] = {}

        # Load existing patterns
        self._load_patterns()

        # Initialize common patterns
        self._initialize_common_patterns()

        logger.info(f"Centralized Log Parser initialized")
        logger.info(f"  Logs directory: {self.logs_dir}")
        logger.info(f"  NAS logs path: {self.nas_logs_path}")
        logger.info(f"  Aggregation data: {self.aggregated_data_dir}")

    def _load_patterns(self):
        """Load existing patterns from file"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    for pattern_id, pattern_data in patterns_data.items():
                        pattern = LogPattern(
                            pattern_id=pattern_data['pattern_id'],
                            pattern_name=pattern_data['pattern_name'],
                            regex=pattern_data['regex'],
                            description=pattern_data['description'],
                            category=pattern_data['category'],
                            severity=pattern_data['severity'],
                            occurrences=pattern_data.get('occurrences', 0),
                            first_seen=datetime.fromisoformat(pattern_data['first_seen']),
                            last_seen=datetime.fromisoformat(pattern_data['last_seen']),
                            examples=pattern_data.get('examples', [])
                        )
                        self.patterns[pattern_id] = pattern
                logger.info(f"Loaded {len(self.patterns)} existing patterns")
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")

    def _save_patterns(self):
        """Save patterns to file"""
        try:
            patterns_dict = {
                pattern_id: pattern.to_dict()
                for pattern_id, pattern in self.patterns.items()
            }
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_dict, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.patterns)} patterns")
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def _initialize_common_patterns(self):
        """Initialize common log patterns"""
        common_patterns = [
            {
                "pattern_id": "ide_startup",
                "pattern_name": "IDE Startup",
                "regex": r"(?i)(ide|editor|cursor|vscode|startup|initializing|starting)",
                "description": "IDE startup events",
                "category": "startup",
                "severity": "info"
            },
            {
                "pattern_id": "service_startup",
                "pattern_name": "Service Startup",
                "regex": r"(?i)(service|daemon|started|starting|initialized|startup)",
                "description": "Service startup events",
                "category": "startup",
                "severity": "info"
            },
            {
                "pattern_id": "error_exit_code",
                "pattern_name": "Error Exit Code",
                "regex": r"exit\s+code[:\s]+(\d+)",
                "description": "Process exit codes (especially non-zero)",
                "category": "error",
                "severity": "warning"
            },
            {
                "pattern_id": "connection_failed",
                "pattern_name": "Connection Failed",
                "regex": r"(?i)(connection|connect|failed|timeout|refused|error)",
                "description": "Connection failures",
                "category": "error",
                "severity": "error"
            },
            {
                "pattern_id": "service_crash",
                "pattern_name": "Service Crash",
                "regex": r"(?i)(crash|exception|fatal|terminated|aborted)",
                "description": "Service crashes or fatal errors",
                "category": "error",
                "severity": "critical"
            },
            {
                "pattern_id": "resource_exhaustion",
                "pattern_name": "Resource Exhaustion",
                "regex": r"(?i)(memory|out of|exhausted|limit|quota|full)",
                "description": "Resource exhaustion warnings",
                "category": "warning",
                "severity": "warning"
            },
            {
                "pattern_id": "performance_issue",
                "pattern_name": "Performance Issue",
                "regex": r"(?i)(slow|timeout|latency|performance|bottleneck)",
                "description": "Performance issues",
                "category": "performance",
                "severity": "warning"
            }
        ]

        for pattern_data in common_patterns:
            if pattern_data['pattern_id'] not in self.patterns:
                pattern = LogPattern(
                    pattern_id=pattern_data['pattern_id'],
                    pattern_name=pattern_data['pattern_name'],
                    regex=pattern_data['regex'],
                    description=pattern_data['description'],
                    category=pattern_data['category'],
                    severity=pattern_data['severity'],
                    occurrences=0,
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    examples=[]
                )
                self.patterns[pattern_data['pattern_id']] = pattern

        self._save_patterns()

    def _detect_log_source(self, line: str) -> LogSource:
        """Detect log source from line content"""
        line_lower = line.lower()

        if any(keyword in line_lower for keyword in ['ide', 'cursor', 'vscode', 'editor', 'workspace']):
            return LogSource.IDE_STARTUP
        elif any(keyword in line_lower for keyword in ['service', 'daemon', 'systemd', 'windows service']):
            return LogSource.SERVICE_STARTUP
        elif any(keyword in line_lower for keyword in ['application', 'app', 'program']):
            return LogSource.APPLICATION
        elif any(keyword in line_lower for keyword in ['system', 'kernel', 'os']):
            return LogSource.SYSTEM
        else:
            return LogSource.UNKNOWN

    def _detect_log_level(self, line: str) -> LogLevel:
        """Detect log level from line content"""
        line_upper = line.upper()

        if 'CRITICAL' in line_upper or 'FATAL' in line_upper:
            return LogLevel.CRITICAL
        elif 'ERROR' in line_upper or 'ERR' in line_upper:
            return LogLevel.ERROR
        elif 'WARNING' in line_upper or 'WARN' in line_upper:
            return LogLevel.WARNING
        elif 'DEBUG' in line_upper:
            return LogLevel.DEBUG
        else:
            return LogLevel.INFO

    def _parse_timestamp(self, line: str) -> Optional[datetime]:
        """Parse timestamp from log line"""
        # Common timestamp patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
            r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]',
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # Try different formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                        try:
                            return datetime.strptime(timestamp_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue

        # Default to now if no timestamp found
        return datetime.now()

    def parse_log_file(self, log_file: Path) -> List[LogEntry]:
        """Parse a single log file"""
        entries = []

        if not log_file.exists():
            logger.warning(f"Log file not found: {log_file}")
            return entries

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    # Parse log entry
                    timestamp = self._parse_timestamp(line)
                    level = self._detect_log_level(line)
                    source = self._detect_log_source(line)

                    # Extract component name (if present)
                    component_match = re.search(r'\[([^\]]+)\]', line)
                    component = component_match.group(1) if component_match else "unknown"

                    # Extract message (remove timestamp and level markers)
                    message = re.sub(r'^\d{4}-\d{2}-\d{2}.*?\[.*?\]\s*', '', line)
                    message = re.sub(r'^\[.*?\]\s*', '', message)
                    message = message.strip()

                    entry = LogEntry(
                        timestamp=timestamp,
                        level=level,
                        source=source,
                        component=component,
                        message=message,
                        raw_line=line,
                        metadata={
                            "file": str(log_file),
                            "line_number": line_num
                        }
                    )
                    entries.append(entry)

        except Exception as e:
            logger.error(f"Error parsing log file {log_file}: {e}")

        return entries

    def discover_log_files(self) -> List[Path]:
        """Discover all log files"""
        log_files = []

        # Check local logs directory
        if self.logs_dir.exists():
            for log_file in self.logs_dir.rglob("*.log"):
                if log_file.is_file():
                    log_files.append(log_file)

        # Check NAS logs (if accessible)
        try:
            if self.nas_logs_path.exists():
                for log_file in self.nas_logs_path.rglob("*.log"):
                    if log_file.is_file():
                        log_files.append(log_file)
        except Exception:
            logger.debug("NAS logs path not accessible")

        logger.info(f"Discovered {len(log_files)} log files")
        return log_files

    def aggregate_by_patterns(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """Aggregate log entries by patterns"""
        pattern_matches = defaultdict(list)

        for entry in entries:
            # Check each pattern
            for pattern_id, pattern in self.patterns.items():
                try:
                    regex = re.compile(pattern.regex)
                    if regex.search(entry.message) or regex.search(entry.raw_line):
                        pattern_matches[pattern_id].append(entry)

                        # Update pattern statistics
                        pattern.occurrences += 1
                        if entry.timestamp < pattern.first_seen:
                            pattern.first_seen = entry.timestamp
                        if entry.timestamp > pattern.last_seen:
                            pattern.last_seen = entry.timestamp

                        # Add example (limit to 5)
                        if len(pattern.examples) < 5:
                            pattern.examples.append(entry.message[:200])
                except Exception as e:
                    logger.debug(f"Error matching pattern {pattern_id}: {e}")

        # Save updated patterns
        self._save_patterns()

        # Build aggregation result
        aggregation = {
            "timestamp": datetime.now().isoformat(),
            "total_entries": len(entries),
            "patterns_matched": len(pattern_matches),
            "pattern_details": {}
        }

        for pattern_id, matches in pattern_matches.items():
            pattern = self.patterns[pattern_id]
            aggregation["pattern_details"][pattern_id] = {
                "pattern_name": pattern.pattern_name,
                "occurrences": len(matches),
                "severity": pattern.severity,
                "category": pattern.category,
                "first_seen": pattern.first_seen.isoformat(),
                "last_seen": pattern.last_seen.isoformat(),
                "recent_examples": [e.message[:200] for e in matches[-5:]]
            }

        return aggregation

    def aggregate_by_time(self, entries: List[LogEntry], time_window: str = "hour") -> Dict[str, Any]:
        """Aggregate logs by time window"""
        time_aggregation = defaultdict(lambda: {
            "total": 0,
            "by_level": defaultdict(int),
            "by_source": defaultdict(int),
            "by_component": defaultdict(int)
        })

        for entry in entries:
            # Determine time window
            if time_window == "hour":
                time_key = entry.timestamp.strftime("%Y-%m-%d %H:00")
            elif time_window == "day":
                time_key = entry.timestamp.strftime("%Y-%m-%d")
            elif time_window == "week":
                time_key = entry.timestamp.strftime("%Y-W%W")
            else:
                time_key = entry.timestamp.strftime("%Y-%m-%d %H:00")

            time_aggregation[time_key]["total"] += 1
            time_aggregation[time_key]["by_level"][entry.level.value] += 1
            time_aggregation[time_key]["by_source"][entry.source.value] += 1
            time_aggregation[time_key]["by_component"][entry.component] += 1

        return {
            "time_window": time_window,
            "aggregation": dict(time_aggregation)
        }

    def parse_all_logs(self) -> Dict[str, Any]:
        try:
            """Parse all discovered log files"""
            logger.info("Starting log parsing and aggregation...")

            # Discover log files
            log_files = self.discover_log_files()

            # Parse all files
            all_entries = []
            for log_file in log_files:
                entries = self.parse_log_file(log_file)
                all_entries.extend(entries)
                logger.debug(f"Parsed {len(entries)} entries from {log_file.name}")

            logger.info(f"Total entries parsed: {len(all_entries)}")

            # Aggregate by patterns
            pattern_aggregation = self.aggregate_by_patterns(all_entries)

            # Aggregate by time
            time_aggregation = self.aggregate_by_time(all_entries, time_window="hour")

            # Build result
            result = {
                "timestamp": datetime.now().isoformat(),
                "total_log_files": len(log_files),
                "total_entries": len(all_entries),
                "pattern_aggregation": pattern_aggregation,
                "time_aggregation": time_aggregation,
                "summary": {
                    "by_level": {
                        level.value: sum(1 for e in all_entries if e.level == level)
                        for level in LogLevel
                    },
                    "by_source": {
                        source.value: sum(1 for e in all_entries if e.source == source)
                        for source in LogSource
                    }
                }
            }

            # Save aggregation result
            aggregation_file = self.aggregated_data_dir / f"aggregation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(aggregation_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Aggregation saved to {aggregation_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in parse_all_logs: {e}", exc_info=True)
            raise
    def get_startup_logs(self, source: Optional[LogSource] = None) -> List[LogEntry]:
        """Get startup logs (IDE or services)"""
        log_files = self.discover_log_files()
        all_entries = []

        for log_file in log_files:
            entries = self.parse_log_file(log_file)
            all_entries.extend(entries)

        # Filter by source
        if source:
            startup_entries = [
                e for e in all_entries
                if e.source == source
            ]
        else:
            # Get both IDE and service startup
            startup_entries = [
                e for e in all_entries
                if e.source in [LogSource.IDE_STARTUP, LogSource.SERVICE_STARTUP]
            ]

        # Sort by timestamp
        startup_entries.sort(key=lambda e: e.timestamp)

        return startup_entries

    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of all patterns"""
        return {
            "total_patterns": len(self.patterns),
            "patterns": {
                pattern_id: pattern.to_dict()
                for pattern_id, pattern in self.patterns.items()
            }
        }


if __name__ == "__main__":
    parser = CentralizedLogParser()

    # Parse all logs
    result = parser.parse_all_logs()

    # Print summary
    print("\n" + "="*60)
    print("CENTRALIZED LOG PARSING SUMMARY")
    print("="*60)
    print(f"Total log files: {result['total_log_files']}")
    print(f"Total entries: {result['total_entries']}")
    print(f"\nBy Level:")
    for level, count in result['summary']['by_level'].items():
        print(f"  {level}: {count}")
    print(f"\nBy Source:")
    for source, count in result['summary']['by_source'].items():
        print(f"  {source}: {count}")
    print(f"\nPatterns Matched: {result['pattern_aggregation']['patterns_matched']}")
    for pattern_id, details in result['pattern_aggregation']['pattern_details'].items():
        print(f"  {details['pattern_name']}: {details['occurrences']} occurrences ({details['severity']})")

    # Get startup logs
    print("\n" + "="*60)
    print("STARTUP LOGS")
    print("="*60)
    startup_logs = parser.get_startup_logs()
    print(f"Found {len(startup_logs)} startup log entries")
    for entry in startup_logs[:10]:  # Show first 10
        print(f"  [{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{entry.source.value}] {entry.message[:100]}")

