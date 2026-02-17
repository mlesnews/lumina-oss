#!/usr/bin/env python3
"""
JARVIS Dynamic Scaling Helper

Integrates dynamic scaling timers into JARVIS scripts to prevent fixed delays
and improve responsiveness based on system state.

This addresses the issue: "30 second pause waiting for JARVIS - background 
monitoring workflow of dynamic scaling timers not working"

Tags: @JARVIS #DYNAMIC_SCALING #TIMERS #PERFORMANCE
"""

import sys
import time
from pathlib import Path
from typing import Optional

# Add project root to path
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.autohotkey_dynamic_scaling import calculate_dynamic_wait
    DYNAMIC_SCALING_AVAILABLE = True
except ImportError:
    DYNAMIC_SCALING_AVAILABLE = False
    calculate_dynamic_wait = None

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDynamicScaling")


class JARVISDynamicWait:
    """
    JARVIS Dynamic Wait Helper

    Replaces fixed time.sleep() calls with dynamic scaling based on:
    - System load (CPU, memory)
    - Operation context
    - Number of operations
    """

    def __init__(self):
        """Initialize dynamic wait helper"""
        self.operation_count = 0
        self.dynamic_scaling_enabled = DYNAMIC_SCALING_AVAILABLE

        if self.dynamic_scaling_enabled:
            logger.info("✅ JARVIS Dynamic Scaling enabled")
            logger.info("   Background monitoring workflow active")
        else:
            logger.warning("⚠️  Dynamic scaling not available, using fixed delays")

    def wait(
        self,
        base_wait: float = 1.0,
        operation_type: str = "default",
        context: Optional[str] = None
    ) -> None:
        """
        Wait with dynamic scaling.

        Args:
            base_wait: Base wait time in seconds
            operation_type: Type of operation (focus, send_text, enter, etc.)
            context: Optional context description
        """
        if self.dynamic_scaling_enabled:
            try:
                # Calculate dynamic wait time
                wait_time = calculate_dynamic_wait(
                    base_wait=base_wait,
                    operation_count=self.operation_count,
                    operation_type=operation_type
                )

                if context:
                    logger.debug(f"   Dynamic wait: {wait_time:.2f}s ({context})")
                else:
                    logger.debug(f"   Dynamic wait: {wait_time:.2f}s")

                time.sleep(wait_time)
                self.operation_count += 1
            except Exception as e:
                logger.warning(f"   Dynamic scaling error, using base wait: {e}")
                time.sleep(base_wait)
        else:
            # Fallback to fixed wait
            time.sleep(base_wait)
            self.operation_count += 1

    def reset_operation_count(self) -> None:
        """Reset operation counter"""
        self.operation_count = 0

    def get_wait_time(
        self,
        base_wait: float = 1.0,
        operation_type: str = "default"
    ) -> float:
        """
        Get calculated wait time without actually waiting.

        Useful for logging or planning.
        """
        if self.dynamic_scaling_enabled:
            try:
                return calculate_dynamic_wait(
                    base_wait=base_wait,
                    operation_count=self.operation_count,
                    operation_type=operation_type
                )
            except Exception:
                return base_wait
        else:
            return base_wait


# Global instance for easy import
_jarvis_wait = None

def get_jarvis_wait() -> JARVISDynamicWait:
    """Get or create global JARVIS wait instance"""
    global _jarvis_wait
    if _jarvis_wait is None:
        _jarvis_wait = JARVISDynamicWait()
    return _jarvis_wait


# Convenience function for easy replacement of time.sleep()
def jarvis_wait(
    seconds: float = 1.0,
    operation_type: str = "default",
    context: Optional[str] = None
) -> None:
    """
    JARVIS dynamic wait - replacement for time.sleep()

    Usage:
        # Instead of: time.sleep(2.0)
        # Use: jarvis_wait(2.0, operation_type="enter", context="Waiting for Cursor")
    """
    wait_helper = get_jarvis_wait()
    wait_helper.wait(
        base_wait=seconds,
        operation_type=operation_type,
        context=context
    )


if __name__ == "__main__":
    """Test dynamic scaling"""
    print("=" * 80)
    print("JARVIS Dynamic Scaling Helper Test")
    print("=" * 80)
    print()

    wait_helper = JARVISDynamicWait()

    print("Testing dynamic wait times:")
    print("-" * 80)

    # Test different operation types
    for op_type in ["focus", "send_text", "enter", "layout_switch", "default"]:
        wait_time = wait_helper.get_wait_time(base_wait=1.0, operation_type=op_type)
        print(f"  {op_type:15s}: {wait_time:.2f}s")

    print()
    print("Testing actual wait (1 second base, enter operation):")
    print("-" * 80)
    print("  Waiting...", end="", flush=True)
    wait_helper.wait(base_wait=1.0, operation_type="enter", context="Test wait")
    print(" Done!")
    print()
    print("=" * 80)
    print("✅ Dynamic scaling test complete")
    print("=" * 80)
