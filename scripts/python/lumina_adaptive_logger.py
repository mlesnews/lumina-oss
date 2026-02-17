#!/usr/bin/env python3
"""
LUMINA Adaptive Logger

Intelligent, context-aware logging that dynamically scales granularity:
- Detailed when issues detected
- Concise when everything working
- Context-aware level adjustment
- Noise reduction through intelligent filtering

Tags: #LOGGING #ADAPTIVE #INTELLIGENT #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
from enum import IntEnum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))


class LogLevel(IntEnum):
    """Log levels with numeric values"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    TRACE = 5  # Ultra-detailed for troubleshooting


class AdaptiveLoggerContext:
    """Context manager for adaptive logging"""

    def __init__(self, logger, context: str, min_level: Optional[int] = None):
        self.logger = logger
        self.context = context
        self.original_level = logger.level
        self.min_level = min_level
        self.issue_detected = False

    def __enter__(self):
        if self.min_level:
            self.logger.setLevel(self.min_level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.min_level:
            self.logger.setLevel(self.original_level)
        if exc_type:
            self.issue_detected = True
        return False


class LuminaAdaptiveLogger:
    """
    Intelligent, adaptive logging system

    Features:
    - Dynamic level adjustment based on system state
    - Context-aware granularity
    - Issue detection triggers detailed logging
    - Noise reduction when everything working
    - Smart filtering of repetitive messages
    """

    def __init__(self, name: str, project_root: Optional[Path] = None):
        """Initialize adaptive logger"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.name = name

        # Check for debug mode
        debug_config_file = self.project_root / "config" / "debug_mode.json"
        debug_mode = False
        if debug_config_file.exists():
            try:
                with open(debug_config_file, 'r', encoding='utf-8') as f:
                    debug_config = json.load(f)
                    debug_mode = debug_config.get("debug_mode", False)
            except Exception:
                pass

        # System state tracking
        self.system_state = "critical" if debug_mode else "normal"  # Force critical in debug mode
        self.issue_count = 999 if debug_mode else 0
        self.last_issue_time = None
        self.recent_errors: Dict[str, int] = defaultdict(int)
        self.recent_warnings: Dict[str, int] = defaultdict(int)

        # Logging configuration
        self.base_level = logging.DEBUG if debug_mode else logging.INFO
        self.adaptive_mode = not debug_mode  # Disable adaptive in debug mode
        self.noise_reduction = not debug_mode  # Disable noise reduction in debug mode

        # Message deduplication
        self.message_history: Dict[str, datetime] = {}
        self.duplicate_threshold = timedelta(seconds=5)

        # Create logger
        self.logger = self._create_logger()

        # Context stack
        self.context_stack: list = []

    def _create_logger(self) -> logging.Logger:
        """Create and configure logger"""
        logger = logging.getLogger(self.name)

        if logger.handlers:
            return logger

        logger.setLevel(self._get_adaptive_level())

        # Console handler with intelligent formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._get_adaptive_level())

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler for persistent logging
        # CRITICAL: Use NAS L: drive for centralized logging
        # If L: is unavailable, we fallback to local data/logs
        # When L: becomes available, nas_logging_watchdog will sync them back
        log_dir = None
        use_nas = False

        try:
            # Check if L: drive is mounted
            l_drive = Path("L:")
            if l_drive.exists():
                # Determine subdirectory based on logger name
                subdirectory = "system"
                name_lower = self.name.lower()

                if "jarvis" in name_lower:
                    subdirectory = "jarvis"
                elif "lumina" in name_lower:
                    subdirectory = "lumina"
                elif "marvin" in name_lower:
                    subdirectory = "system"
                elif "error" in name_lower or "exception" in name_lower:
                    subdirectory = "errors"
                elif "audit" in name_lower or "security" in name_lower:
                    subdirectory = "audit"

                log_dir = l_drive / "logs" / subdirectory
                use_nas = True
                logging.getLogger(self.name).info(f"📁 Centralized Logging: {log_dir}")
        except Exception as e:
            logging.getLogger(self.name).warning(f"⚠️  NAS logging detection failed: {e}")

        # Fallback to local logs if NAS unavailable
        if not use_nas or log_dir is None:
            log_dir = self.project_root / "data" / "logs"
            logging.getLogger(self.name).info(f"🏠 Local Host Logging: {log_dir}")

        log_dir = Path(log_dir)
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Final fallback if even directory creation fails (e.g. invalid drive)
            log_dir = self.project_root / "data" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            logging.getLogger(self.name).warning(f"⚠️  Failed to use requested log dir, falling back to local: {e}")

        file_handler = logging.FileHandler(
            log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        # Check for debug mode - always DEBUG in debug mode
        debug_config_file = self.project_root / "config" / "debug_mode.json"
        file_level = logging.DEBUG
        if debug_config_file.exists():
            try:
                with open(debug_config_file, 'r', encoding='utf-8') as f:
                    debug_config = json.load(f)
                    if debug_config.get("debug_mode", False):
                        file_level = logging.DEBUG
            except Exception:
                pass
        file_handler.setLevel(file_level)  # Always detailed in files, DEBUG in debug mode
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def _get_adaptive_level(self) -> int:
        """Get adaptive log level based on system state"""
        # Check for debug mode
        debug_config_file = self.project_root / "config" / "debug_mode.json"
        if debug_config_file.exists():
            try:
                with open(debug_config_file, 'r', encoding='utf-8') as f:
                    debug_config = json.load(f)
                    if debug_config.get("debug_mode", False):
                        return logging.DEBUG  # Always DEBUG in debug mode
            except Exception:
                pass

        if not self.adaptive_mode:
            return self.base_level

        # Adjust based on system state
        if self.system_state == "critical":
            return logging.DEBUG  # Detailed when critical
        elif self.system_state == "degraded":
            return logging.INFO   # Normal when degraded
        else:
            # Normal state: reduce noise
            if self.issue_count > 0:
                return logging.INFO  # Show info if issues present
            else:
                return logging.WARNING  # Only warnings+ when all good

    def _should_log(self, level: int, message: str) -> bool:
        """Determine if message should be logged - ZERO DARK THIRTY ENFORCED"""
        # ZERO DARK THIRTY: Only log CRITICAL and above
        if level < logging.CRITICAL:
            return False

        # Check for debug mode - always log everything
        debug_config_file = self.project_root / "config" / "debug_mode.json"
        if debug_config_file.exists():
            try:
                with open(debug_config_file, 'r', encoding='utf-8') as f:
                    debug_config = json.load(f)
                    if debug_config.get("debug_mode", False):
                        return True  # Always log in debug mode
            except Exception:
                pass

        if not self.noise_reduction:
            return True

        # Always log errors and critical
        if level >= logging.ERROR:
            return True

        # Check for duplicate messages
        message_key = f"{level}:{message[:100]}"
        now = datetime.now()

        if message_key in self.message_history:
            last_time = self.message_history[message_key]
            if now - last_time < self.duplicate_threshold:
                return False  # Suppress duplicate

        self.message_history[message_key] = now
        return True

    def update_system_state(self, state: str, issue_count: int = 0):
        """Update system state (triggers adaptive level adjustment)"""
        self.system_state = state
        self.issue_count = issue_count

        if issue_count > 0:
            self.last_issue_time = datetime.now()

        # Update logger level
        new_level = self._get_adaptive_level()
        self.logger.setLevel(new_level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(new_level)

    def record_issue(self, level: str, message: str):
        """Record an issue (triggers more detailed logging)"""
        if level == "error":
            self.recent_errors[message[:50]] += 1
            self.issue_count += 1
            self.system_state = "degraded" if self.system_state == "normal" else "critical"
        elif level == "warning":
            self.recent_warnings[message[:50]] += 1
            if self.system_state == "normal":
                self.system_state = "degraded"

        self.update_system_state(self.system_state, self.issue_count)

    def context(self, context_name: str, min_level: Optional[int] = None):
        """Create context for detailed logging"""
        return AdaptiveLoggerContext(self.logger, context_name, min_level)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        if self._should_log(logging.CRITICAL, message):
            self.logger.critical(message, *args, **kwargs)
        self.record_issue("error", message)

    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        if self._should_log(logging.ERROR, message):
            self.logger.error(message, *args, **kwargs)
        self.record_issue("error", message)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        if self._should_log(logging.WARNING, message):
            self.logger.warning(message, *args, **kwargs)
        self.record_issue("warning", message)

    def info(self, message: str, *args, **kwargs):
        """Log info message (adaptive based on state)"""
        if self._should_log(logging.INFO, message):
            self.logger.info(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message (only when detailed logging needed)"""
        if self._should_log(logging.DEBUG, message):
            self.logger.debug(message, *args, **kwargs)

    def trace(self, message: str, *args, **kwargs):
        """Log trace message (ultra-detailed troubleshooting)"""
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"[TRACE] {message}", *args, **kwargs)

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current logging state summary"""
        return {
            "system_state": self.system_state,
            "issue_count": self.issue_count,
            "current_level": logging.getLevelName(self.logger.level),
            "recent_errors": dict(self.recent_errors),
            "recent_warnings": dict(self.recent_warnings),
            "adaptive_mode": self.adaptive_mode,
            "noise_reduction": self.noise_reduction
        }


def get_adaptive_logger(name: str, project_root: Optional[Path] = None) -> LuminaAdaptiveLogger:
    """Get or create adaptive logger instance"""
    logger_key = f"lumina_adaptive_{name}"
    if logger_key not in logging.Logger.manager.loggerDict:
        return LuminaAdaptiveLogger(name, project_root)

    logger = logging.getLogger(logger_key)
    if isinstance(logger, LuminaAdaptiveLogger):
        return logger

    return LuminaAdaptiveLogger(name, project_root)


if __name__ == "__main__":
    # Test adaptive logger
    logger = get_adaptive_logger("test")

    logger.info("System normal - minimal logging")
    logger.update_system_state("normal", 0)

    logger.warning("Issue detected - logging becomes more detailed")
    logger.update_system_state("degraded", 1)

    logger.info("Now showing info messages")
    logger.error("Critical issue - maximum detail")
    logger.update_system_state("critical", 2)

    logger.debug("Debug messages now visible")
    logger.trace("Trace messages for troubleshooting")
