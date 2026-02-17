#!/usr/bin/env python3
"""
Universal Logging Wrapper
<COMPANY_NAME> LLC

Ensures EVERYTHING is logged. No operation happens without logging.
Integrates with Measurement Gatekeeper for comprehensive measurement.

"If we're not logging, we're not measuring."
"""

import sys
import logging
import functools
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from measurement_gatekeeper import (
        get_measurement_gatekeeper,
        MeasurementLevel,
        measure_operation
    )
    GATEKEEPER_AVAILABLE = True
except ImportError:
    GATEKEEPER_AVAILABLE = False

# Setup universal logger

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

# Save original getLogger BEFORE monkey-patching
_original_getLogger = logging.getLogger

def setup_universal_logger(name: str, project_root: Optional[Path] = None) -> logging.Logger:
    try:
        """
        Setup universal logger that ALWAYS logs

        This ensures no operation happens without logging.
        Uses _original_getLogger to avoid recursion.
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        # Use original getLogger to avoid recursion
        logger = _original_getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Logs directory
        logs_dir = project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # File handler - ALL logs
        log_file = logs_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler - INFO and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Ensure logger doesn't propagate to root (avoid duplicate logs)
        logger.propagate = False

        return logger

    except Exception as e:
        logger.error(f"Error in setup_universal_logger: {e}", exc_info=True)
        raise
def get_logger(name: str) -> logging.Logger:
    """
    Get logger - ensures logging is ALWAYS enabled

    This is the replacement for standard logging.getLogger()
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, setup universal logging
    if not logger.handlers:
        logger = setup_universal_logger(name)

    return logger


def log_all_operations(component: str, level: MeasurementLevel = MeasurementLevel.MEDIUM):
    """
    Decorator that ensures operation is logged AND measured

    Usage:
        @log_all_operations("MyComponent", MeasurementLevel.HIGH)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Get logger for this function
        logger = get_logger(f"{component}.{func.__name__}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log operation start
            logger.info(f"▶️  START: {func.__name__}")
            logger.debug(f"   Args: {args}")
            logger.debug(f"   Kwargs: {kwargs}")

            # Measure operation if gatekeeper available
            measurement_id = None
            if GATEKEEPER_AVAILABLE:
                try:
                    gatekeeper = get_measurement_gatekeeper()
                    measurement_id = gatekeeper.measure(
                        operation=func.__name__,
                        component=component,
                        level=level,
                        context={
                            'args': str(args)[:200],
                            'kwargs': str(kwargs)[:200]
                        }
                    )
                except Exception as e:
                    logger.warning(f"Measurement gatekeeper error: {e}")

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Log success
                logger.info(f"✅ SUCCESS: {func.__name__}")
                logger.debug(f"   Result: {result}")

                # Complete measurement
                if measurement_id and GATEKEEPER_AVAILABLE:
                    try:
                        gatekeeper = get_measurement_gatekeeper()
                        gatekeeper.complete_measurement(
                            measurement_id,
                            result=result,
                            metrics={'success': True}
                        )
                    except Exception as e:
                        logger.warning(f"Measurement completion error: {e}")

                return result
            except Exception as e:
                # Log error
                logger.error(f"❌ ERROR: {func.__name__} - {e}")
                logger.exception("Exception details:")

                # Complete measurement with error
                if measurement_id and GATEKEEPER_AVAILABLE:
                    try:
                        gatekeeper = get_measurement_gatekeeper()
                        gatekeeper.complete_measurement(
                            measurement_id,
                            error=str(e),
                            metrics={'success': False}
                        )
                    except Exception:
                        pass

                raise

        return wrapper
    return decorator


# Monkey-patch logging.getLogger to use our universal logger
def patched_getLogger(name: str = None) -> logging.Logger:
    """Patched getLogger that ensures logging is always enabled"""
    if name is None:
        name = "root"

    # Use original getLogger to get the logger instance
    logger = _original_getLogger(name)

    # If logger has no handlers, setup universal logging
    if not logger.handlers and name != "root":
        logger = setup_universal_logger(name)

    return logger

# Apply monkey patch AFTER defining setup_universal_logger
logging.getLogger = patched_getLogger


if __name__ == "__main__":
    # Test universal logging
    logger = get_logger("UniversalLoggingTest")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test decorator
    @log_all_operations("TestComponent", MeasurementLevel.MEDIUM)
    def test_function(x: int, y: int) -> int:
        return x + y

    result = test_function(5, 3)
    print(f"Result: {result}")

    print("✅ Universal logging test completed")

