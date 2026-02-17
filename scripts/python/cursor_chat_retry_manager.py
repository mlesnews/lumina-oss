#!/usr/bin/env python3
"""
Cursor IDE Chat Retry Manager

Handles retries for Cursor IDE chat operations when they fail due to:
- Timeouts
- Disconnects
- Network breakdowns
- API failures

Tags: #CURSOR #CHAT #RETRY #RESILIENCE @JARVIS @LUMINA
"""

import sys
import time
import logging
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from functools import wraps
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorChatRetryManager")


class RetryStrategy(Enum):
    """Retry strategies"""
    LINEAR = "linear"  # Fixed delay between retries
    EXPONENTIAL = "exponential"  # Exponential backoff
    FIBONACCI = "fibonacci"  # Fibonacci backoff


class CursorChatRetryManager:
    """
    Retry manager for Cursor IDE chat operations.

    Handles:
    - Timeout errors
    - Connection errors
    - Network failures
    - API failures
    - Graceful degradation
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    ):
        """
        Initialize retry manager.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            strategy: Retry strategy (linear, exponential, fibonacci)
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.strategy = strategy

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        if self.strategy == RetryStrategy.LINEAR:
            delay = self.initial_delay * (attempt + 1)
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay * (2 ** attempt)
        elif self.strategy == RetryStrategy.FIBONACCI:
            # Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, ...
            fib = [1, 1]
            for i in range(2, attempt + 2):
                fib.append(fib[i-1] + fib[i-2])
            delay = self.initial_delay * fib[attempt]
        else:
            delay = self.initial_delay

        # Cap at max_delay
        return min(delay, self.max_delay)

    def is_retryable_error(self, error: Exception) -> bool:
        """
        Check if error is retryable.

        Args:
            error: Exception to check

        Returns:
            True if error is retryable, False otherwise
        """
        # LOGICAL FIX: Make ALL errors retryable by default (conservative approach)
        # Keyboard automation errors (pynput, pyautogui) don't raise ConnectionError
        # but failures should still be retried

        retryable_errors = (
            TimeoutError,
            ConnectionError,
            OSError,  # Network errors
            RuntimeError,  # Some runtime errors are retryable
            Exception,  # ALL exceptions are retryable (default to retry)
        )

        error_str = str(error).lower()
        retryable_keywords = [
            'timeout',
            'disconnect',
            'connection',
            'network',
            'broken',
            'unavailable',
            'temporarily',
            'failed',
            'error',
            'connecterror',
            'serialize binary',
            'invalid int',
            '4294967295',
            'econnreset',
            'aborted',
        ]

        # Check exception type - ALL exceptions are retryable
        if isinstance(error, Exception):
            return True

        # Check error message (backup check)
        if any(keyword in error_str for keyword in retryable_keywords):
            return True

        # Default to retry (conservative - retry everything)
        return True

    def retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                result = func(*args, **kwargs)

                # Success - log if retried (use global logging)
                if attempt > 0:
                    try:
                        from lumina_logger import log
                        log(
                            f"✅ Retry successful after {attempt} attempt(s) - message sent to Cursor",
                            level="info",
                            name="CursorChatRetryManager"
                        )
                    except ImportError:
                        logger.info(f"✅ Retry successful after {attempt} attempt(s)")

                return result

            except Exception as e:
                last_error = e

                # LOGICAL FIX: Always retry (is_retryable_error now returns True for all exceptions)
                # Check if we've exhausted retries
                if attempt >= self.max_retries:
                    try:
                        from lumina_logger import log
                        log(
                            f"❌ Max retries ({self.max_retries}) exceeded. Last error: {type(e).__name__}: {e}",
                            level="error",
                            name="CursorChatRetryManager"
                        )
                    except ImportError:
                        logger.error(f"❌ Max retries ({self.max_retries}) exceeded. Last error: {e}")
                    raise

                # Calculate delay
                delay = self.calculate_delay(attempt)

                # Log retry attempt with global logging pattern
                try:
                    from lumina_logger import log
                    log(
                        f"⚠️  Retry attempt {attempt + 1}/{self.max_retries} after {delay:.1f}s delay. "
                        f"Error: {type(e).__name__}: {e}",
                        level="warning",
                        name="CursorChatRetryManager"
                    )
                except ImportError:
                    logger.warning(
                        f"⚠️  Retry attempt {attempt + 1}/{self.max_retries} after {delay:.1f}s delay. "
                        f"Error: {type(e).__name__}: {e}"
                    )

                # Wait before retry
                time.sleep(delay)

        # Should never reach here, but just in case
        if last_error:
            raise last_error
        raise RuntimeError("Retry logic failed unexpectedly")

    def retry_decorator(self, func: Optional[Callable] = None, **decorator_kwargs):
        """
        Decorator for automatic retry.

        Usage:
            @retry_manager.retry_decorator(max_retries=5)
            def send_chat_message(message):
                ...
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Merge decorator kwargs with instance defaults
                manager = CursorChatRetryManager(
                    max_retries=decorator_kwargs.get('max_retries', self.max_retries),
                    initial_delay=decorator_kwargs.get('initial_delay', self.initial_delay),
                    max_delay=decorator_kwargs.get('max_delay', self.max_delay),
                    strategy=decorator_kwargs.get('strategy', self.strategy)
                )
                return manager.retry(f, *args, **kwargs)
            return wrapper

        if func is None:
            return decorator
        else:
            return decorator(func)


# Global retry manager instance
_default_retry_manager = CursorChatRetryManager(
    max_retries=3,
    initial_delay=1.0,
    max_delay=10.0,
    strategy=RetryStrategy.EXPONENTIAL
)


def retry_chat_operation(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
) -> Any:
    """
    Convenience function for retrying chat operations.

    Usage:
        result = retry_chat_operation(send_message, message="Hello")
    """
    manager = CursorChatRetryManager(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        strategy=strategy
    )
    return manager.retry(func)


def retry_decorator(max_retries: int = 3, **kwargs):
    """
    Decorator for automatic retry.

    Usage:
        @retry_decorator(max_retries=5)
        def send_chat_message(message):
            ...
    """
    return _default_retry_manager.retry_decorator(**{**kwargs, 'max_retries': max_retries})


if __name__ == "__main__":
    # Test retry manager
    def test_function(succeed_on_attempt: int = 2):
        """Test function that fails then succeeds"""
        test_function.attempt = getattr(test_function, 'attempt', 0) + 1
        if test_function.attempt < succeed_on_attempt:
            raise TimeoutError(f"Simulated timeout (attempt {test_function.attempt})")
        return f"Success on attempt {test_function.attempt}"

    manager = CursorChatRetryManager(max_retries=3)
    result = manager.retry(test_function, succeed_on_attempt=3)
    print(f"✅ Test result: {result}")
