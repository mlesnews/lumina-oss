#!/usr/bin/env python3
"""
LUMINA Error Recovery System

Automatic recovery from failures with retry logic and fallback mechanisms.
Ensures system remains functional even when errors occur.

Tags: #ERROR_RECOVERY #RESILIENCE #AUTOMATION #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Any
from datetime import datetime
from functools import wraps

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("ErrorRecovery")


class RetryConfig:
    """Retry configuration"""
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff


def retry_on_failure(config: Optional[RetryConfig] = None):
    """
    Decorator for automatic retry on failure

    Args:
        config: Retry configuration (default: 3 attempts, 1s delay, 2x backoff)
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.delay

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < config.max_attempts:
                        logger.warning(f"   ⚠️  {func.__name__} failed (attempt {attempt}/{config.max_attempts}): {e}")
                        logger.info(f"   🔄 Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        delay *= config.backoff
                    else:
                        logger.error(f"   ❌ {func.__name__} failed after {config.max_attempts} attempts: {e}")

            # All attempts failed
            raise last_exception

        return wrapper
    return decorator


class LuminaErrorRecovery:
    """
    LUMINA Error Recovery System

    Provides automatic recovery from failures with:
    - Retry logic
    - Fallback mechanisms
    - Error context logging
    - Graceful degradation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize error recovery system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_history: List[Dict[str, Any]] = []

    def execute_with_recovery(
        self,
        operation: Callable,
        operation_name: str,
        fallback: Optional[Callable] = None,
        retry_config: Optional[RetryConfig] = None
    ) -> Any:
        """
        Execute operation with automatic recovery

        Args:
            operation: Function to execute
            operation_name: Name of operation (for logging)
            fallback: Fallback function if operation fails
            retry_config: Retry configuration

        Returns: Result of operation or fallback
        """
        if retry_config is None:
            retry_config = RetryConfig()

        last_exception = None
        delay = retry_config.delay

        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                result = operation()
                if attempt > 1:
                    logger.info(f"   ✅ {operation_name} succeeded on attempt {attempt}")
                    self._record_recovery(operation_name, attempt)
                return result
            except Exception as e:
                last_exception = e
                self._record_error(operation_name, e, attempt)

                if attempt < retry_config.max_attempts:
                    logger.warning(f"   ⚠️  {operation_name} failed (attempt {attempt}/{retry_config.max_attempts}): {e}")
                    logger.info(f"   🔄 Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= retry_config.backoff
                else:
                    logger.error(f"   ❌ {operation_name} failed after {retry_config.max_attempts} attempts: {e}")

        # All attempts failed - try fallback
        if fallback:
            try:
                logger.info(f"   🔄 Attempting fallback for {operation_name}...")
                result = fallback()
                logger.info(f"   ✅ Fallback succeeded for {operation_name}")
                self._record_recovery(operation_name, "fallback")
                return result
            except Exception as e:
                logger.error(f"   ❌ Fallback also failed for {operation_name}: {e}")
                raise e

        # No fallback - raise last exception
        raise last_exception

    def _record_error(self, operation_name: str, error: Exception, attempt: int):
        """Record error in history"""
        self.error_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation_name,
            "error": str(error),
            "error_type": type(error).__name__,
            "attempt": attempt
        })

    def _record_recovery(self, operation_name: str, recovery_method: Any):
        """Record successful recovery"""
        self.recovery_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation_name,
            "recovery_method": str(recovery_method)
        })

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        return {
            "total_errors": len(self.error_history),
            "total_recoveries": len(self.recovery_history),
            "recent_errors": self.error_history[-10:] if self.error_history else [],
            "recent_recoveries": self.recovery_history[-10:] if self.recovery_history else []
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Error Recovery System")
        parser.add_argument("--summary", action="store_true", help="Show error summary")

        args = parser.parse_args()

        recovery = LuminaErrorRecovery()

        if args.summary:
            summary = recovery.get_error_summary()
            import json
            print(json.dumps(summary, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())