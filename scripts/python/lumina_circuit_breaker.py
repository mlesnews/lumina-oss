"""Circuit Breaker and Retry Logic for Lumina

Automatically handles API failures, database issues, and external service problems.
"""

import time
import logging
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # Failures before opening
    recovery_timeout: int = 60      # Seconds before trying again
    expected_exception: tuple = (Exception,)  # Exceptions to catch

class CircuitBreaker:
    """Circuit breaker for external service calls"""

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(f"circuit_breaker.{name}")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.logger.info(f"🔄 {self.name}: Testing service recovery")
            else:
                raise Exception(f"🚫 {self.name}: Circuit breaker OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should try to reset the circuit"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.logger.info(f"✅ {self.name}: Service recovered, circuit CLOSED")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(f"🚫 {self.name}: Circuit breaker OPEN after {self.failure_count} failures")

def retry_with_backoff(max_attempts: int = 3, backoff_factor: float = 2.0,
                      exceptions: tuple = (Exception,)):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        delay = backoff_factor ** attempt
                        logging.warning(f"Retry attempt {attempt + 1} failed, waiting {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logging.error(f"All {max_attempts} attempts failed: {e}")

            raise last_exception
        return wrapper
    return decorator

# Global circuit breakers for common services
api_circuit_breaker = CircuitBreaker("external_api")
db_circuit_breaker = CircuitBreaker("database")
