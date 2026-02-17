#!/usr/bin/env python3
"""
Cursor IDE Connection Resilience

Handles connection errors from Cursor IDE, specifically:
- ECONNRESET (Connection reset)
- ConnectError (Connection errors)
- Aborted connections
- Timeout errors

Tags: #CURSOR_IDE #CONNECTION_RESILIENCE #ECONNRESET #ERROR_HANDLING @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from functools import wraps
import traceback
import errno

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorConnectionResilience")


class CursorConnectionResilience:
    """
    Cursor IDE Connection Resilience Handler

    Specifically handles connection errors from Cursor IDE AI connections.
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0, project_root: Optional[Path] = None):
        """
        Initialize connection resilience handler

        Args:
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            project_root: Project root path for health monitoring
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Initialize health monitor
        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor
            self.health_monitor = CursorConnectionHealthMonitor(self.project_root)
        except Exception:
            self.health_monitor = None

        logger.info("✅ Cursor Connection Resilience initialized")
        logger.info(f"   Max retries: {max_retries}")
        logger.info(f"   Retry delay: {retry_delay}s")
        if self.health_monitor:
            logger.info("   📊 Health monitoring: Active")

    def is_connection_error(self, error: Exception) -> bool:
        """
        Check if error is a connection error that should be retried

        Args:
            error: The exception to check

        Returns:
            True if it's a connection error
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        error_repr = repr(error).lower()

        # Check for Python standard library connection exception types
        # ConnectionResetError is a subclass of ConnectionError
        if isinstance(error, ConnectionResetError):
            return True

        # ConnectionError (base class for connection-related errors)
        if isinstance(error, ConnectionError):
            return True

        # OSError with ECONNRESET errno (Windows/Linux)
        if isinstance(error, OSError):
            if hasattr(error, 'errno') and error.errno in (
                errno.ECONNRESET,  # Connection reset by peer
                errno.ECONNREFUSED,  # Connection refused
                errno.ECONNABORTED,  # Connection aborted
                errno.ETIMEDOUT,  # Connection timed out
                errno.EPIPE,  # Broken pipe
            ):
                return True

        # ECONNRESET - Connection reset by peer (string check)
        if "econnreset" in error_str or "econnreset" in error_repr:
            return True

        # ConnectError (including serialize binary errors)
        if "connecterror" in error_str or error_type == "ConnectError":
            return True

        # Serialize binary errors (internal Cursor IDE errors)
        if "serialize binary" in error_str or "invalid int" in error_str:
            return True

        # Invalid int32 errors (4294967295 = 0xFFFFFFFF)
        if "4294967295" in error_str or "invalid int 32" in error_str:
            return True

        # Aborted
        if "aborted" in error_str or "[aborted]" in error_str:
            return True

        # Connection reset
        if "connection reset" in error_str:
            return True

        # Network errors
        if "network" in error_str and "error" in error_str:
            return True

        # Timeout errors
        if "timeout" in error_str or "timed out" in error_str:
            return True

        return False

    def handle_connection_error(self, error: Exception, attempt: int, ai_service: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle a connection error

        Args:
            error: The connection error
            attempt: Current attempt number
            ai_service: AI service name (optional)

        Returns:
            Dict with handling information
        """
        error_str = str(error)
        error_type = type(error).__name__

        logger.warning("=" * 80)
        logger.warning("⚠️  CURSOR IDE CONNECTION ERROR DETECTED")
        logger.warning("=" * 80)
        logger.warning(f"   Error Type: {error_type}")
        logger.warning(f"   Error: {error_str}")
        logger.warning(f"   Attempt: {attempt}/{self.max_retries}")
        if ai_service:
            logger.warning(f"   AI Service: {ai_service}")
        logger.warning("")

        # Determine error category
        if "serialize binary" in error_str.lower() or "invalid int 32" in error_str.lower() or "4294967295" in error_str:
            category = "SerializeBinaryError"
            description = "Internal Cursor IDE serialization error (invalid int32)"
            action = "Retrying with connection reset"
        elif "econnreset" in error_str.lower():
            category = "ECONNRESET"
            description = "Connection reset by peer"
            action = "Retrying with exponential backoff"
        elif "connecterror" in error_str.lower() or error_type == "ConnectError":
            category = "ConnectError"
            description = "Connection error"
            action = "Retrying connection"
        elif "aborted" in error_str.lower():
            category = "Aborted"
            description = "Connection aborted"
            action = "Retrying operation"
        elif "timeout" in error_str.lower():
            category = "Timeout"
            description = "Connection timeout"
            action = "Retrying with longer timeout"
        else:
            category = "Unknown"
            description = "Connection error"
            action = "Retrying"

        logger.warning(f"   Category: {category}")
        logger.warning(f"   Description: {description}")
        logger.warning(f"   Action: {action}")
        logger.warning("")

        # Record to health monitor
        if self.health_monitor:
            self.health_monitor.record_connection_attempt(
                success=False,
                error=error,
                retry_attempt=attempt,
                ai_service=ai_service
            )

        # Calculate retry delay (exponential backoff)
        delay = self.retry_delay * (2 ** (attempt - 1))
        delay = min(delay, 30.0)  # Cap at 30 seconds

        logger.info(f"   ⏳ Waiting {delay:.1f}s before retry...")
        time.sleep(delay)

        return {
            "category": category,
            "description": description,
            "action": action,
            "retry_delay": delay,
            "should_retry": attempt < self.max_retries
        }

    def retry_on_connection_error(self, func: Callable) -> Callable:
        """
        Decorator to retry function on connection errors

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with retry logic
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            start_time = time.time()
            ai_service = kwargs.get("ai_service") or args[0] if args else None

            for attempt in range(1, self.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    response_time = time.time() - start_time

                    # Record success to health monitor
                    if self.health_monitor:
                        self.health_monitor.record_connection_attempt(
                            success=True,
                            retry_attempt=attempt - 1,
                            response_time=response_time,
                            ai_service=ai_service
                        )

                    return result
                except Exception as e:
                    last_error = e

                    # Check if it's a connection error
                    if self.is_connection_error(e):
                        if attempt < self.max_retries:
                            self.handle_connection_error(e, attempt, ai_service)
                            continue
                        else:
                            logger.error("   ❌ Max retries reached. Connection failed.")

                            # Record final failure
                            if self.health_monitor:
                                self.health_monitor.record_connection_attempt(
                                    success=False,
                                    error=e,
                                    retry_attempt=attempt,
                                    ai_service=ai_service
                                )

                            raise
                    else:
                        # Not a connection error, don't retry
                        if self.health_monitor:
                            self.health_monitor.record_connection_attempt(
                                success=False,
                                error=e,
                                retry_attempt=0,
                                ai_service=ai_service
                            )
                        raise

            # If we get here, all retries failed
            if last_error:
                raise last_error

        return wrapper


def handle_cursor_connection_error(error: Exception) -> Dict[str, Any]:
    """
    Handle Cursor IDE connection error (standalone function)

    Args:
        error: The connection error

    Returns:
        Dict with error handling information
    """
    resilience = CursorConnectionResilience()

    if resilience.is_connection_error(error):
        return resilience.handle_connection_error(error, 1)
    else:
        return {
            "category": "NotConnectionError",
            "description": "Not a connection error",
            "action": "Do not retry",
            "should_retry": False
        }


if __name__ == "__main__":
    """Test connection resilience"""
    resilience = CursorConnectionResilience()

    # Test error detection
    test_errors = [
        Exception("ConnectError: [aborted] read ECONNRESET"),
        Exception("Connection reset by peer"),
        Exception("Timeout error"),
        Exception("Network error"),
        Exception("Some other error")
    ]

    print("Testing connection error detection:")
    print("=" * 80)
    for error in test_errors:
        is_conn_error = resilience.is_connection_error(error)
        print(f"Error: {error}")
        print(f"Is connection error: {is_conn_error}")
        print()
