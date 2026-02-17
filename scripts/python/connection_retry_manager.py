#!/usr/bin/env python3
"""
Connection Retry Manager

Implements robust connection error handling with exponential backoff, circuit breaker,
and request ID correlation. Core responsibility of #AIMLSEA for network resilience.

Tags: #AIMLSEA #CONNECTION_ERROR #RETRY_MANAGER #CIRCUIT_BREAKER #NETWORK_RESILIENCE @JARVIS @LUMINA
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, TypeVar, Union
from dataclasses import dataclass, field
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
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConnectionRetryManager")

T = TypeVar('T')


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"
    FIXED = "fixed"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryResult:
    """Result of retry operation"""
    success: bool
    attempts: int
    total_time: float
    final_error: Optional[str] = None
    request_id: Optional[str] = None
    circuit_breaker_state: Optional[str] = None


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Open circuit after N failures
    success_threshold: int = 2  # Close circuit after N successes
    timeout: float = 60.0  # Time to wait before half-open (seconds)
    half_open_max_requests: int = 3  # Max requests in half-open state


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 5
    initial_delay: float = 0.1
    max_delay: float = 30.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0
    jitter: bool = True  # Add randomness to delays
    retryable_errors: list = field(default_factory=lambda: [
        "ECONNRESET", "ECONNREFUSED", "ETIMEDOUT", "ENOTFOUND",
        "ENETDOWN", "ENETUNREACH", "EHOSTDOWN", "EHOSTUNREACH",
        "EPIPE", "ConnectionError", "TimeoutError"
    ])


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation

    Prevents cascading failures by opening circuit when service is failing
    and allowing recovery attempts when service may have recovered.
    """

    def __init__(self, config: CircuitBreakerConfig):
        """Initialize circuit breaker"""
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_requests = 0

        logger.info("✅ Circuit Breaker initialized")
        logger.info(f"   Failure threshold: {config.failure_threshold}")
        logger.info(f"   Timeout: {config.timeout}s")

    def call(self, func: Callable[[], T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Arguments for function

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        # Check circuit state
        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.config.timeout:
                    logger.info("   🔄 Circuit breaker: OPEN → HALF_OPEN")
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_requests = 0
                else:
                    raise Exception(
                        f"Circuit breaker is OPEN. "
                        f"Retry after {self.config.timeout - elapsed:.1f}s"
                    )
            else:
                raise Exception("Circuit breaker is OPEN")

        # Execute function
        try:
            result = func(*args, **kwargs)

            # Success - update state
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                self.half_open_requests += 1

                if self.success_count >= self.config.success_threshold:
                    logger.info("   ✅ Circuit breaker: HALF_OPEN → CLOSED")
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.half_open_requests = 0
                elif self.half_open_requests >= self.config.half_open_max_requests:
                    # Too many requests in half-open, go back to open
                    logger.warning("   ⚠️  Circuit breaker: HALF_OPEN → OPEN (too many requests)")
                    self.state = CircuitBreakerState.OPEN
                    self.last_failure_time = datetime.now()
                    self.half_open_requests = 0
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

            return result

        except Exception as e:
            # Failure - update state
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitBreakerState.HALF_OPEN:
                logger.warning("   ⚠️  Circuit breaker: HALF_OPEN → OPEN (failure)")
                self.state = CircuitBreakerState.OPEN
                self.success_count = 0
                self.half_open_requests = 0
            elif self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    logger.warning("   ⚠️  Circuit breaker: CLOSED → OPEN (threshold reached)")
                    self.state = CircuitBreakerState.OPEN

            raise


class ConnectionRetryManager:
    """
    Connection Retry Manager with Exponential Backoff and Circuit Breaker

    Implements robust connection error handling with:
    - Exponential backoff retry
    - Circuit breaker pattern
    - Request ID correlation
    - Error classification
    - Observability
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        enable_request_id_tracking: bool = True
    ):
        """Initialize connection retry manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
        self.enable_request_id_tracking = enable_request_id_tracking

        # Request ID tracking integration
        self.request_id_tracker = None
        if self.enable_request_id_tracking:
            try:
                from track_request_id import RequestIDTracker
                self.request_id_tracker = RequestIDTracker(project_root=self.project_root)
                logger.info("   Request ID tracking: ✅ Enabled")
            except ImportError:
                logger.warning("   Request ID tracking: ⚠️  Not available (track_request_id module not found)")

        # Statistics
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0
        self.circuit_breaker_trips = 0

        logger.info("✅ Connection Retry Manager initialized")
        logger.info(f"   Max attempts: {self.retry_config.max_attempts}")
        logger.info(f"   Strategy: {self.retry_config.strategy.value}")
        logger.info(f"   Initial delay: {self.retry_config.initial_delay}s")
        logger.info(f"   Max delay: {self.retry_config.max_delay}s")

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if self.retry_config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.retry_config.initial_delay * (
                self.retry_config.backoff_multiplier ** (attempt - 1)
            )
        elif self.retry_config.strategy == RetryStrategy.LINEAR:
            delay = self.retry_config.initial_delay * attempt
        elif self.retry_config.strategy == RetryStrategy.FIBONACCI:
            # Fibonacci sequence
            fib = [1, 1]
            for _ in range(attempt - 1):
                fib.append(fib[-1] + fib[-2])
            delay = self.retry_config.initial_delay * fib[min(attempt, len(fib) - 1)]
        else:  # FIXED
            delay = self.retry_config.initial_delay

        # Apply max delay limit
        delay = min(delay, self.retry_config.max_delay)

        # Add jitter if enabled
        if self.retry_config.jitter:
            import random
            jitter = delay * 0.1 * random.random()  # 10% jitter
            delay = delay + jitter

        return delay

    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if error is retryable"""
        error_str = str(error).upper()
        error_type = type(error).__name__.upper()

        for retryable in self.retry_config.retryable_errors:
            if retryable.upper() in error_str or retryable.upper() in error_type:
                return True

        return False

    def _extract_error_type(self, error: Exception) -> Optional[str]:
        """Extract error type from exception"""
        error_str = str(error).upper()
        error_type = type(error).__name__.upper()

        # Check for specific error types
        if "ECONNRESET" in error_str or "ECONNRESET" in error_type:
            return "ECONNRESET"
        elif "ECONNREFUSED" in error_str or "ECONNREFUSED" in error_type:
            return "ECONNREFUSED"
        elif "ETIMEDOUT" in error_str or "TIMEOUT" in error_str or "TIMEOUT" in error_type:
            return "ETIMEDOUT"
        elif "CONNECTIONERROR" in error_str or "CONNECTIONERROR" in error_type:
            return "CONNECTION_ERROR"
        else:
            return None

    def retry_with_backoff(
        self,
        operation: Callable[[], T],
        operation_name: str = "operation",
        request_id: Optional[str] = None
    ) -> RetryResult:
        """
        Retry operation with exponential backoff and circuit breaker

        Args:
            operation: Function to execute
            operation_name: Name of operation for logging
            request_id: Optional Request ID for correlation

        Returns:
            RetryResult with success status and attempt count
        """
        start_time = time.time()
        attempts = 0
        last_error = None

        for attempt in range(1, self.retry_config.max_attempts + 1):
            attempts = attempt
            self.total_retries += 1

            try:
                # Execute with circuit breaker protection
                result = self.circuit_breaker.call(operation)

                # Success
                self.successful_retries += 1
                total_time = time.time() - start_time

                if attempts > 1:
                    logger.info(
                        f"   ✅ {operation_name} succeeded on attempt {attempts} "
                        f"(after {total_time:.2f}s)"
                    )
                    if request_id:
                        logger.info(f"   Request ID: {request_id}")

                return RetryResult(
                    success=True,
                    attempts=attempts,
                    total_time=total_time,
                    request_id=request_id,
                    circuit_breaker_state=self.circuit_breaker.state.value
                )

            except Exception as e:
                last_error = str(e)

                # Track Request ID with error context if tracking enabled
                if request_id and self.request_id_tracker:
                    try:
                        error_type = self._extract_error_type(e)
                        self.request_id_tracker.track_request_id(
                            request_id=request_id,
                            source="retry_manager",
                            error_type=error_type,
                            context={
                                "operation": operation_name,
                                "attempt": attempt,
                                "max_attempts": self.retry_config.max_attempts,
                                "error": str(e),
                                "error_class": type(e).__name__,
                                "circuit_breaker_state": self.circuit_breaker.state.value
                            }
                        )
                    except Exception as track_error:
                        logger.debug(f"   Failed to track Request ID: {track_error}")

                # Check if error is retryable
                if not self._is_retryable_error(e):
                    logger.warning(
                        f"   ⚠️  {operation_name} failed with non-retryable error: {e}"
                    )
                    self.failed_retries += 1
                    break

                # Check if circuit breaker is open
                if "Circuit breaker is OPEN" in last_error:
                    logger.warning(f"   ⚠️  Circuit breaker is OPEN for {operation_name}")
                    self.circuit_breaker_trips += 1
                    self.failed_retries += 1
                    break

                # If not last attempt, wait before retrying
                if attempt < self.retry_config.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"   ⏳ {operation_name} failed (attempt {attempt}/{self.retry_config.max_attempts}), "
                        f"retrying in {delay:.2f}s... Error: {e}"
                    )
                    if request_id:
                        logger.info(f"   Request ID: {request_id}")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"   ❌ {operation_name} failed after {attempts} attempts: {e}"
                    )
                    if request_id:
                        logger.error(f"   Request ID: {request_id}")

        # All attempts failed
        total_time = time.time() - start_time
        self.failed_retries += 1

        return RetryResult(
            success=False,
            attempts=attempts,
            total_time=total_time,
            final_error=last_error,
            request_id=request_id,
            circuit_breaker_state=self.circuit_breaker.state.value
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get retry statistics"""
        return {
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "success_rate": (
                self.successful_retries / self.total_retries * 100
                if self.total_retries > 0 else 0
            ),
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "circuit_breaker_state": self.circuit_breaker.state.value
        }


def main():
    """Main entry point for testing"""
    import random

    def flaky_operation() -> bool:
        """Simulate flaky operation"""
        if random.random() < 0.3:  # 30% success rate
            return True
        raise ConnectionError("ECONNRESET: Connection reset by peer")

    manager = ConnectionRetryManager(
        retry_config=RetryConfig(
            max_attempts=5,
            initial_delay=0.1,
            max_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL
        )
    )

    result = manager.retry_with_backoff(
        flaky_operation,
        operation_name="test_operation",
        request_id="test-request-id"
    )

    print(f"\n✅ Retry Result:")
    print(f"   Success: {result.success}")
    print(f"   Attempts: {result.attempts}")
    print(f"   Total time: {result.total_time:.2f}s")
    print(f"   Circuit breaker state: {result.circuit_breaker_state}")

    stats = manager.get_statistics()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":


    main()