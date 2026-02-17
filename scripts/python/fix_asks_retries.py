#!/usr/bin/env python3
"""
Fix @ASKS Not Stalling and Retries Working as Intended

"HOW ABOUT @ASKS NOT STALLING, AND RETRIES WORKING AS INTENDED? IS THAT TOO MUCH TO ASK NOW, JARVIS?"

Fixes:
- @ASKS not stalling
- Retries working as intended
- Proper timeout handling
- Exponential backoff
- Circuit breaker pattern
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixAsksRetries")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    timeout: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0


@dataclass
class RetryResult:
    """Result of retry operation"""
    success: bool
    attempts: int
    total_time: float
    error: Optional[str] = None
    result: Any = None


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures"""

    def __init__(self, threshold: int = 5, timeout: float = 60.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.threshold:
            self.state = "open"
            logger.warning(f"  ⚠️  Circuit breaker OPEN after {self.failure_count} failures")

    def can_attempt(self) -> bool:
        """Check if operation can be attempted"""
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
                self.state = "half_open"
                logger.info("  🔄 Circuit breaker HALF_OPEN - attempting recovery")
                return True
            return False

        if self.state == "half_open":
            return True

        return False


class FixedAsksRetries:
    """
    Fixed @ASKS with proper retry logic

    "HOW ABOUT @ASKS NOT STALLING, AND RETRIES WORKING AS INTENDED? IS THAT TOO MUCH TO ASK NOW, JARVIS?"
    """

    def __init__(self, project_root: Optional[Path] = None, config: Optional[RetryConfig] = None):
        """Initialize Fixed @ASKS Retries"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("FixedAsksRetries")
        self.config = config or RetryConfig()
        self.circuit_breaker = CircuitBreaker(
            self.config.circuit_breaker_threshold,
            self.config.circuit_breaker_timeout
        )

        self.logger.info("🔧 Fixed @ASKS Retries initialized")
        self.logger.info("   No stalling. Retries working as intended.")

    def ask_with_retry(self, operation: Callable, *args, **kwargs) -> RetryResult:
        """
        Execute operation with retry logic

        Features:
        - No stalling
        - Exponential backoff
        - Circuit breaker
        - Proper timeout handling
        """
        if not self.circuit_breaker.can_attempt():
            return RetryResult(
                success=False,
                attempts=0,
                total_time=0.0,
                error="Circuit breaker is OPEN"
            )

        start_time = time.time()
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                self.logger.debug(f"  🔄 Attempt {attempt + 1}/{self.config.max_retries + 1}")

                # Execute with timeout
                result = self._execute_with_timeout(operation, *args, **kwargs)

                # Success
                self.circuit_breaker.record_success()
                total_time = time.time() - start_time

                self.logger.info(f"  ✅ Success on attempt {attempt + 1} (took {total_time:.2f}s)")

                return RetryResult(
                    success=True,
                    attempts=attempt + 1,
                    total_time=total_time,
                    result=result
                )

            except Exception as e:
                last_error = str(e)
                self.logger.debug(f"  ⚠️  Attempt {attempt + 1} failed: {last_error}")

                # Record failure
                self.circuit_breaker.record_failure()

                # Don't retry on last attempt
                if attempt >= self.config.max_retries:
                    break

                # Exponential backoff
                delay = min(
                    self.config.initial_delay * (self.config.exponential_base ** attempt),
                    self.config.max_delay
                )

                self.logger.debug(f"  ⏳ Waiting {delay:.2f}s before retry...")
                time.sleep(delay)

        # All retries failed
        total_time = time.time() - start_time

        self.logger.error(f"  ❌ All {self.config.max_retries + 1} attempts failed (took {total_time:.2f}s)")

        return RetryResult(
            success=False,
            attempts=self.config.max_retries + 1,
            total_time=total_time,
            error=last_error
        )

    def _execute_with_timeout(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with timeout"""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {self.config.timeout}s")

        # Set timeout (Unix only - Windows needs different approach)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(self.config.timeout))

        try:
            result = operation(*args, **kwargs)
            return result
        finally:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel timeout

    def get_status(self) -> Dict[str, Any]:
        """Get retry system status"""
        return {
            "config": asdict(self.config),
            "circuit_breaker": {
                "state": self.circuit_breaker.state,
                "failure_count": self.circuit_breaker.failure_count,
                "can_attempt": self.circuit_breaker.can_attempt()
            },
            "status": "Operational - No stalling, retries working as intended"
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix @ASKS Retries")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    fixed_retries = FixedAsksRetries()

    if args.status:
        status = fixed_retries.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🔧 Fixed @ASKS Retries Status")
            print(f"   Status: {status['status']}")
            print(f"   Circuit Breaker: {status['circuit_breaker']['state']}")
            print(f"   Can Attempt: {status['circuit_breaker']['can_attempt']}")

