#!/usr/bin/env python3
"""
Standardized Timestamp/Datestamp Logging Module

@AUTOMATE workflow mantra - Standardize, Modularize, Automate everything!

Features:
- Standardized timestamp formats across all systems
- Modular, reusable logging components
- Automatic timestamp injection
- Consistent date/time formatting
- ISO 8601 compliance
- Timezone awareness
- Performance tracking timestamps

Tags: #STANDARDIZE #MODULARIZE #AUTOMATE #TIMESTAMP #LOGGING #WORKFLOW @JARVIS @TEAM @RR
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import functools
import inspect

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# ALWAYS use the standard logging module: lumina_logger
# This is a critical requirement - all scripts must use lumina_logger.get_logger()
from lumina_logger import get_logger

logger = get_logger("StandardizedTimestampLogging")


class TimestampFormat(Enum):
    """Standardized timestamp formats"""
    ISO8601_FULL = "iso8601_full"  # 2026-01-03T00:53:30.123456+00:00
    ISO8601_COMPACT = "iso8601_compact"  # 20260103T005330
    ISO8601_DATE = "iso8601_date"  # 2026-01-03
    ISO8601_TIME = "iso8601_time"  # 00:53:30.123456
    UNIX_TIMESTAMP = "unix_timestamp"  # 1704251610.123456
    HUMAN_READABLE = "human_readable"  # 2026-01-03 00:53:30
    LOG_FORMAT = "log_format"  # 2026-01-03 00:53:30,123
    FILENAME_SAFE = "filename_safe"  # 20260103_005330


@dataclass
class TimestampMetadata:
    """Metadata for timestamp logging"""
    timestamp: datetime
    format_used: TimestampFormat
    timezone: str
    source: str  # Function/class name
    context: Dict[str, Any] = field(default_factory=dict)
    performance_ms: Optional[float] = None


class StandardizedTimestampLogger:
    """
    Standardized Timestamp Logger

    @AUTOMATE: Modular, reusable, standardized timestamp logging
    """

    def __init__(self, default_format: TimestampFormat = TimestampFormat.ISO8601_FULL, timezone_str: str = "UTC"):
        """Initialize standardized timestamp logger"""
        self.default_format = default_format
        self.timezone_str = timezone_str
        self.tz = timezone.utc if timezone_str == "UTC" else None  # Can be extended for other timezones

        # Logging history
        self.log_history: List[TimestampMetadata] = []
        self.max_history = 1000

        logger.info("✅ Standardized Timestamp Logger initialized")
        logger.info(f"   Default format: {default_format.value}")
        logger.info(f"   Timezone: {timezone_str}")

    def now(self, format_type: Optional[TimestampFormat] = None) -> str:
        """Get current timestamp in standardized format"""
        format_type = format_type or self.default_format
        dt = datetime.now(self.tz)
        return self.format_timestamp(dt, format_type)

    def format_timestamp(self, dt: datetime, format_type: TimestampFormat) -> str:
        """Format datetime to standardized format"""
        if format_type == TimestampFormat.ISO8601_FULL:
            return dt.isoformat()
        elif format_type == TimestampFormat.ISO8601_COMPACT:
            return dt.strftime("%Y%m%dT%H%M%S")
        elif format_type == TimestampFormat.ISO8601_DATE:
            return dt.strftime("%Y-%m-%d")
        elif format_type == TimestampFormat.ISO8601_TIME:
            return dt.strftime("%H:%M:%S.%f")
        elif format_type == TimestampFormat.UNIX_TIMESTAMP:
            return str(dt.timestamp())
        elif format_type == TimestampFormat.HUMAN_READABLE:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        elif format_type == TimestampFormat.LOG_FORMAT:
            return dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # Milliseconds
        elif format_type == TimestampFormat.FILENAME_SAFE:
            return dt.strftime("%Y%m%d_%H%M%S")
        else:
            return dt.isoformat()

    def log_timestamp(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        format_type: Optional[TimestampFormat] = None,
        performance_ms: Optional[float] = None
    ) -> TimestampMetadata:
        """Log timestamp with metadata"""
        dt = datetime.now(self.tz)
        format_type = format_type or self.default_format

        metadata = TimestampMetadata(
            timestamp=dt,
            format_used=format_type,
            timezone=self.timezone_str,
            source=source,
            context=context or {},
            performance_ms=performance_ms
        )

        # Add to history
        self.log_history.append(metadata)
        if len(self.log_history) > self.max_history:
            self.log_history.pop(0)

        return metadata

    def get_timestamp_dict(self, source: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get standardized timestamp dictionary"""
        dt = datetime.now(self.tz)
        return {
            "timestamp": dt.isoformat(),
            "timestamp_iso8601": self.format_timestamp(dt, TimestampFormat.ISO8601_FULL),
            "timestamp_compact": self.format_timestamp(dt, TimestampFormat.ISO8601_COMPACT),
            "timestamp_date": self.format_timestamp(dt, TimestampFormat.ISO8601_DATE),
            "timestamp_time": self.format_timestamp(dt, TimestampFormat.ISO8601_TIME),
            "timestamp_unix": self.format_timestamp(dt, TimestampFormat.UNIX_TIMESTAMP),
            "timestamp_human": self.format_timestamp(dt, TimestampFormat.HUMAN_READABLE),
            "timestamp_filename": self.format_timestamp(dt, TimestampFormat.FILENAME_SAFE),
            "source": source,
            "timezone": self.timezone_str,
            "context": context or {}
        }

    def inject_timestamp(self, data: Dict[str, Any], source: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Inject standardized timestamps into data dictionary"""
        timestamp_dict = self.get_timestamp_dict(source, context)
        data.update(timestamp_dict)
        return data


# Global instance for easy access
_global_timestamp_logger = StandardizedTimestampLogger()


def get_timestamp_logger() -> StandardizedTimestampLogger:
    """Get global timestamp logger instance"""
    return _global_timestamp_logger


def auto_timestamp(func: Optional[Callable] = None, format_type: TimestampFormat = TimestampFormat.ISO8601_FULL):
    """
    Decorator to automatically add timestamps to function calls

    @AUTOMATE: Automatic timestamp injection
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Get source name
            source = f"{f.__module__}.{f.__qualname__}"

            # Log start timestamp
            start_time = datetime.now()
            ts_logger = get_timestamp_logger()
            start_metadata = ts_logger.log_timestamp(
                source=f"{source}.start",
                context={"function": f.__name__, "args_count": len(args), "kwargs_keys": list(kwargs.keys())},
                format_type=format_type
            )

            try:
                # Execute function
                result = f(*args, **kwargs)

                # Log end timestamp
                end_time = datetime.now()
                performance_ms = (end_time - start_time).total_seconds() * 1000
                end_metadata = ts_logger.log_timestamp(
                    source=f"{source}.end",
                    context={"function": f.__name__, "result_type": type(result).__name__},
                    format_type=format_type,
                    performance_ms=performance_ms
                )

                # Inject timestamp into result if it's a dict
                if isinstance(result, dict):
                    result = ts_logger.inject_timestamp(result, source=f"{source}.result")

                return result

            except Exception as e:
                # Log error timestamp
                error_time = datetime.now()
                performance_ms = (error_time - start_time).total_seconds() * 1000
                ts_logger.log_timestamp(
                    source=f"{source}.error",
                    context={"function": f.__name__, "error": str(e), "error_type": type(e).__name__},
                    format_type=format_type,
                    performance_ms=performance_ms
                )
                raise

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def timestamped_log(message: str, level: str = "INFO", source: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
    try:
        """Log message with standardized timestamp"""
        ts_logger = get_timestamp_logger()

        if source is None:
            # Try to get caller info
            frame = inspect.currentframe().f_back
            source = f"{frame.f_globals.get('__name__', 'unknown')}.{frame.f_code.co_name}"

        timestamp_dict = ts_logger.get_timestamp_dict(source, context)

        log_message = f"[{timestamp_dict['timestamp_human']}] {message}"

        if context:
            log_message += f" | Context: {json.dumps(context)}"

        # Use appropriate log level
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(log_message)

        return timestamp_dict


    except Exception as e:
        logger.error(f"Error in timestamped_log: {e}", exc_info=True)
        raise
class TimestampedDataClass:
    """Base class for dataclasses with automatic timestamp injection"""

    def __post_init__(self):
        """Inject timestamps after initialization"""
        ts_logger = get_timestamp_logger()
        source = f"{self.__class__.__module__}.{self.__class__.__name__}"

        # Inject timestamps into dataclass fields
        if hasattr(self, '__dict__'):
            timestamp_dict = ts_logger.get_timestamp_dict(source)
            for key, value in timestamp_dict.items():
                if not hasattr(self, key):
                    setattr(self, key, value)


def standardize_existing_logs(log_file: Path, output_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Standardize timestamps in existing log files

    @AUTOMATE: Automatically fix existing logs
    """
    ts_logger = get_timestamp_logger()

    if not log_file.exists():
        return {"error": "Log file not found", "file": str(log_file)}

    standardized = []
    errors = []

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        # Try to parse as JSON
                        data = json.loads(line)
                        if isinstance(data, dict):
                            # Inject standardized timestamps
                            standardized_data = ts_logger.inject_timestamp(
                                data,
                                source=f"standardize_existing_logs.{log_file.name}",
                                context={"original_line": line_num}
                            )
                            standardized.append(standardized_data)
                    except json.JSONDecodeError:
                        # Not JSON, try to extract timestamp from log line
                        # Add standardized timestamp prefix
                        timestamp_dict = ts_logger.get_timestamp_dict(
                            source=f"standardize_existing_logs.{log_file.name}",
                            context={"original_line": line_num, "original": line.strip()}
                        )
                        standardized.append({
                            "original_line": line,
                            **timestamp_dict
                        })
                    except Exception as e:
                        errors.append({"line": line_num, "error": str(e)})

    except Exception as e:
        return {"error": str(e), "file": str(log_file)}

    # Write standardized output
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in standardized:
                f.write(json.dumps(item, default=str) + '\n')

    return {
        "standardized_count": len(standardized),
        "errors_count": len(errors),
        "errors": errors,
        "output_file": str(output_file) if output_file else None
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Standardized Timestamp Logging")
    parser.add_argument("--now", action="store_true", help="Get current timestamp")
    parser.add_argument("--format", type=str, help="Timestamp format")
    parser.add_argument("--standardize", type=str, help="Standardize existing log file")
    parser.add_argument("--output", type=str, help="Output file for standardization")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("⏰ Standardized Timestamp Logging")
    print("   @AUTOMATE: Standardize, Modularize, Automate")
    print("="*80 + "\n")

    ts_logger = get_timestamp_logger()

    if args.now:
        format_type = TimestampFormat(args.format) if args.format else None
        timestamp = ts_logger.now(format_type)
        print(f"📅 Current Timestamp: {timestamp}\n")

    elif args.standardize:
        result = standardize_existing_logs(Path(args.standardize), Path(args.output) if args.output else None)
        print(f"\n📊 STANDARDIZATION RESULT:")
        print(f"   Standardized: {result.get('standardized_count', 0)}")
        print(f"   Errors: {result.get('errors_count', 0)}")
        if result.get('output_file'):
            print(f"   Output: {result['output_file']}")
        print()

    else:
        # Show all formats
        print("📅 Available Timestamp Formats:\n")
        for fmt in TimestampFormat:
            timestamp = ts_logger.now(fmt)
            print(f"   {fmt.value:20s}: {timestamp}")
        print()
