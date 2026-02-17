#!/usr/bin/env python3
"""
Lumina Unified Logger - Homelab Centralized Logging
====================================================

Unified logging system for entire Lumina homelab with dual-write architecture:
- Local: logs/{category}/{service}/*.log (normal administration, maintenance, rotation)
- NAS Mirror: L:/Logs/{category}/{service}/*.log (long-term aggregate/archive copy)

Architecture:
- Each local host maintains its own logs with normal administration/maintenance
- Logs are mirrored/aggregated to NAS (L: drive) for long-term storage (6 months to 1 year)
- Local logs: Standard rotation and cleanup (e.g., 30 days retention)
- NAS logs: Long-term archival (e.g., 365 days retention)
- Use log_archival_manager.py for maintenance and archival operations

Usage:
    from lumina_unified_logger import LuminaUnifiedLogger

    logger_module = LuminaUnifiedLogger("Application", "Startup")
    logger = logger_module.get_logger()

    logger.info("Service started")
    logger.error("Something went wrong")

Categories:
    - Application: Python scripts, services, VAs
    - System: Windows events, system logs
    - AI: Ollama, Stable Diffusion, model inference
    - Security: Authentication, access logs
    - Network: Traffic, connectivity
    - Performance: GPU, CPU, memory metrics

@LUMINA @LOGGING @HOMELAB @DUAL_WRITE @ARCHIVAL
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import threading


class LuminaUnifiedLogger:
    """
    Unified logging for all Lumina scripts.
    Automatically routes to L: drive (NAS) with local fallback.
    Provides dual-write for redundancy.
    """

    _loggers: dict = {}
    _lock = threading.Lock()

    def __init__(self, category: str, service: str, level: int = logging.INFO):
        """
        Initialize unified logger.

        Args:
            category: Log category (Application, System, AI, Security, Network, Performance)
            service: Service name (Startup, JARVIS, Ollama, etc.)
            level: Logging level (default: INFO)
        """
        self.category = category
        self.service = service
        self.level = level
        self.logger_key = f"{category}.{service}"
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure logger with NAS integration and dual-write"""

        # Check if logger already exists
        with self._lock:
            if self.logger_key in self._loggers:
                return self._loggers[self.logger_key]

        logger = logging.getLogger(f"lumina.{self.logger_key}")
        logger.setLevel(self.level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Prevent propagation to root logger
        logger.propagate = False

        # Format
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Get log paths (NAS primary, local fallback)
        nas_log_path, local_log_path = self._get_log_paths()

        # File handler - NAS (primary)
        if nas_log_path:
            try:
                nas_handler = logging.FileHandler(nas_log_path, encoding='utf-8')
                nas_handler.setFormatter(formatter)
                nas_handler.setLevel(self.level)
                logger.addHandler(nas_handler)
            except (OSError, IOError, PermissionError):
                pass  # NAS unavailable, continue with local only

        # File handler - Local (fallback/redundancy)
        try:
            local_handler = logging.FileHandler(local_log_path, encoding='utf-8')
            local_handler.setFormatter(formatter)
            local_handler.setLevel(self.level)
            logger.addHandler(local_handler)
        except (OSError, IOError, PermissionError):
            pass  # Can't write locally either, continue with console only

        # Console handler (for debugging - only if running interactively)
        if sys.stdout.isatty():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(self.level)
            logger.addHandler(console_handler)

        # Cache logger
        with self._lock:
            self._loggers[self.logger_key] = logger

        return logger

    def _get_log_paths(self) -> Tuple[Optional[Path], Path]:
        """
        Get log paths with dual-write architecture.
        Returns (nas_log_path, local_log_path) tuple.

        Architecture:
        - Local: Primary log location (normal administration/maintenance)
        - NAS: Mirror/aggregate copy for long-term archival
        """
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{self.service}_{date_str}.log"

        # Local log path (primary - normal administration)
        project_root = Path(__file__).parent.parent.parent
        local_log_dir = project_root / "logs" / self.category / self.service
        local_log_dir.mkdir(parents=True, exist_ok=True)
        local_log_path = local_log_dir / filename

        # NAS log path (mirror/aggregate for long-term storage)
        nas_log_path = None
        if Path("L:/").exists():
            try:
                nas_log_dir = Path(f"L:/Logs/{self.category}/{self.service}")
                nas_log_dir.mkdir(parents=True, exist_ok=True)
                nas_log_path = nas_log_dir / filename
            except (OSError, IOError, PermissionError):
                pass  # NAS unavailable, continue with local only

        return nas_log_path, local_log_path

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger

    @property
    def nas_available(self) -> bool:
        try:
            """Check if NAS (L: drive) is available"""
            return Path("L:/").exists()

        except Exception as e:
            self.logger.error(f"Error in nas_available: {e}", exc_info=True)
            raise
    @property
    def log_paths(self) -> dict:
        """Get current log file paths"""
        nas_path, local_path = self._get_log_paths()
        return {
            "nas": str(nas_path) if nas_path else None,
            "local": str(local_path),
            "nas_available": self.nas_available
        }


# Convenience function for quick logger creation
def get_unified_logger(category: str, service: str, level: int = logging.INFO) -> logging.Logger:
    """
    Quick function to get a unified logger.

    Example:
        logger = get_unified_logger("Application", "Startup")
        logger.info("Starting service...")
    """
    logger_module = LuminaUnifiedLogger(category, service, level)
    return logger_module.get_logger()


# Backward compatibility - can replace lumina_logger.get_logger()
def get_logger(name: str) -> logging.Logger:
    """
    Backward-compatible logger function.
    Parses name to extract category and service.

    Format: "category.service" or just "service" (defaults to Application)

    Example:
        logger = get_logger("Application.Startup")
        logger = get_logger("JARVIS")  # defaults to Application.JARVIS
    """
    parts = name.split('.', 1)
    if len(parts) == 2:
        category, service = parts
    else:
        category = "Application"
        service = parts[0]

    return get_unified_logger(category, service)
