#!/usr/bin/env python3
"""
Exponential Backoff Retry Enhancement for Auto-Accept

Implements exponential backoff retry logic for failed auto-accept detections.
Prevents infinite loops while ensuring reliable acceptance.

Tags: #AUTO_ACCEPT #RETRY #EXPONENTIAL_BACKOFF #IMPROVEMENT @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
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
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AutoAcceptRetry")


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"
    FIXED = "fixed"


@dataclass
class RetryResult:
    """Result of retry operation"""
    success: bool
    attempts: int
    total_time: float
    final_error: Optional[str] = None


class ExponentialBackoffRetry:
    """
    Exponential Backoff Retry for Auto-Accept

    Retries failed auto-accept operations with exponential backoff
    to prevent infinite loops while ensuring reliability.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        max_attempts: int = 5,
        initial_delay: float = 0.1,
        max_delay: float = 2.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        backoff_multiplier: float = 2.0
    ):
        """Initialize retry system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.backoff_multiplier = backoff_multiplier

        # Statistics
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0

        logger.info("✅ Exponential Backoff Retry initialized")
        logger.info(f"   Max attempts: {max_attempts}")
        logger.info(f"   Strategy: {strategy.value}")
        logger.info(f"   Initial delay: {initial_delay}s")
        logger.info(f"   Max delay: {max_delay}s")

    def retry_with_backoff(
        self,
        operation: Callable[[], bool],
        operation_name: str = "operation"
    ) -> RetryResult:
        """
        Retry operation with exponential backoff

        Args:
            operation: Function that returns True on success, False on failure
            operation_name: Name of operation for logging

        Returns:
            RetryResult with success status and attempt count
        """
        start_time = time.time()
        attempts = 0
        delay = self.initial_delay
        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            attempts = attempt
            self.total_retries += 1

            try:
                # Attempt operation
                success = operation()

                if success:
                    self.successful_retries += 1
                    total_time = time.time() - start_time

                    if attempts > 1:
                        logger.info(
                            f"   ✅ {operation_name} succeeded on attempt {attempts} "
                            f"(after {total_time:.2f}s)"
                        )

                    return RetryResult(
                        success=True,
                        attempts=attempts,
                        total_time=total_time
                    )

                # Operation failed
                last_error = f"{operation_name} returned False"

                # If not last attempt, wait before retrying
                if attempt < self.max_attempts:
                    logger.debug(
                        f"   ⏳ {operation_name} failed (attempt {attempt}/{self.max_attempts}), "
                        f"retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

                    # Calculate next delay based on strategy
                    delay = self._calculate_next_delay(delay, attempt)
                else:
                    logger.warning(
                        f"   ⚠️  {operation_name} failed after {attempts} attempts"
                    )

            except Exception as e:
                last_error = str(e)
                logger.debug(f"   ⚠️  {operation_name} error on attempt {attempt}: {e}")

                # If not last attempt, wait before retrying
                if attempt < self.max_attempts:
                    time.sleep(delay)
                    delay = self._calculate_next_delay(delay, attempt)

        # All attempts failed
        self.failed_retries += 1
        total_time = time.time() - start_time

        logger.warning(
            f"   ❌ {operation_name} failed after {attempts} attempts "
            f"(total time: {total_time:.2f}s)"
        )

        return RetryResult(
            success=False,
            attempts=attempts,
            total_time=total_time,
            final_error=last_error
        )

    def _calculate_next_delay(self, current_delay: float, attempt: int) -> float:
        """Calculate next delay based on strategy"""

        if self.strategy == RetryStrategy.EXPONENTIAL:
            # Exponential: delay = initial * (multiplier ^ attempt)
            next_delay = self.initial_delay * (self.backoff_multiplier ** attempt)

        elif self.strategy == RetryStrategy.LINEAR:
            # Linear: delay = initial * attempt
            next_delay = self.initial_delay * attempt

        elif self.strategy == RetryStrategy.FIBONACCI:
            # Fibonacci: delay = initial * fibonacci(attempt)
            fib_n = self._fibonacci(attempt)
            next_delay = self.initial_delay * fib_n

        else:  # FIXED
            # Fixed: delay stays the same
            next_delay = current_delay

        # Apply max delay cap
        return min(next_delay, self.max_delay)

    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def get_statistics(self) -> Dict[str, Any]:
        """Get retry statistics"""
        success_rate = (
            (self.successful_retries / self.total_retries * 100)
            if self.total_retries > 0
            else 0.0
        )

        return {
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "success_rate": success_rate,
            "max_attempts": self.max_attempts,
            "strategy": self.strategy.value
        }


def main():
    """Test retry system"""
    retry = ExponentialBackoffRetry(
        max_attempts=5,
        initial_delay=0.1,
        max_delay=2.0,
        strategy=RetryStrategy.EXPONENTIAL
    )

    print("\n🧪 Testing Exponential Backoff Retry")
    print("=" * 80)

    # Test 1: Success on first attempt
    print("\n✅ Test 1: Success on first attempt")
    attempt_count = [0]
    def success_immediately():
        attempt_count[0] += 1
        return True

    result = retry.retry_with_backoff(success_immediately, "test_operation_1")
    print(f"   Result: {result.success}, Attempts: {result.attempts}, Time: {result.total_time:.2f}s")

    # Test 2: Success on third attempt
    print("\n✅ Test 2: Success on third attempt")
    attempt_count = [0]
    def success_on_third():
        attempt_count[0] += 1
        return attempt_count[0] >= 3

    result = retry.retry_with_backoff(success_on_third, "test_operation_2")
    print(f"   Result: {result.success}, Attempts: {result.attempts}, Time: {result.total_time:.2f}s")

    # Test 3: All attempts fail
    print("\n❌ Test 3: All attempts fail")
    def always_fail():
        return False

    result = retry.retry_with_backoff(always_fail, "test_operation_3")
    print(f"   Result: {result.success}, Attempts: {result.attempts}, Time: {result.total_time:.2f}s")
    print(f"   Error: {result.final_error}")

    print("\n" + "=" * 80)
    stats = retry.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total Retries: {stats['total_retries']}")
    print(f"   Successful: {stats['successful_retries']}")
    print(f"   Failed: {stats['failed_retries']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")


if __name__ == "__main__":


    main()