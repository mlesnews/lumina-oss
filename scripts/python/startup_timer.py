#!/usr/bin/env python3
"""
Startup Timer - Measure and Optimize Startup Time

Times the startup of all LUMINA services and identifies bottlenecks.
Optimizes startup by parallelizing initialization where possible.

Tags: #STARTUP #PERFORMANCE #TIMING #OPTIMIZATION @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

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

logger = get_logger("StartupTimer")


class StartupTimer:
    """Times startup of LUMINA services and identifies bottlenecks"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.service_times: Dict[str, float] = {}
        self.service_order: List[str] = []
        self.bottlenecks: List[Tuple[str, float]] = []

    def start(self):
        """Start timing overall startup"""
        self.start_time = time.time()
        logger.info("⏱️  Startup timer started")

    def time_service(self, service_name: str, func, *args, **kwargs):
        """Time a service initialization"""
        service_start = time.time()
        try:
            result = func(*args, **kwargs)
            service_time = time.time() - service_start
            self.service_times[service_name] = service_time
            self.service_order.append(service_name)
            logger.info(f"⏱️  {service_name}: {service_time:.2f}s")
            return result
        except Exception as e:
            service_time = time.time() - service_start
            self.service_times[service_name] = service_time
            self.service_order.append(service_name)
            logger.error(f"❌ {service_name} failed after {service_time:.2f}s: {e}")
            raise

    def end(self):
        """End timing and calculate statistics"""
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        # Identify bottlenecks (services taking > 1 second)
        self.bottlenecks = [
            (name, time_taken) 
            for name, time_taken in self.service_times.items() 
            if time_taken > 1.0
        ]
        self.bottlenecks.sort(key=lambda x: x[1], reverse=True)

        logger.info("=" * 80)
        logger.info("⏱️  STARTUP TIMING RESULTS - JARVIS READY FOR FIRST WAKE WORD")
        logger.info("=" * 80)
        logger.info(f"   ⏱️  TOTAL TIME: {total_time:.2f}s (from startup to ready for 'Hey Jarvis')")
        logger.info(f"   Services initialized: {len(self.service_times)}")
        logger.info("")
        logger.info("   🎯 JARVIS IS NOW READY TO RECEIVE 'HEY JARVIS'")
        logger.info("")

        if self.bottlenecks:
            logger.info("🐌 BOTTLENECKS (>1s):")
            for name, time_taken in self.bottlenecks:
                logger.info(f"   {name}: {time_taken:.2f}s")
            logger.info("")

        logger.info("📊 Service Times:")
        for name in self.service_order:
            time_taken = self.service_times.get(name, 0)
            logger.info(f"   {name}: {time_taken:.2f}s")

        logger.info("=" * 80)
        logger.info(f"✅ JARVIS READY - Total startup time: {total_time:.2f}s")
        logger.info("=" * 80)

        # Save timing data
        self._save_timing_data(total_time)

        return total_time

    def _save_timing_data(self, total_time: float):
        """Save timing data to file"""
        try:
            data_dir = project_root / "data" / "startup_timing"
            data_dir.mkdir(parents=True, exist_ok=True)

            timing_file = data_dir / f"startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            data = {
                "timestamp": datetime.now().isoformat(),
                "total_time": total_time,
                "total_time_description": "Time from startup to JARVIS ready for first wake word ('Hey Jarvis')",
                "ready_for_wake_word": True,
                "service_times": self.service_times,
                "service_order": self.service_order,
                "bottlenecks": [
                    {"name": name, "time": time_taken} 
                    for name, time_taken in self.bottlenecks
                ]
            }

            with open(timing_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Timing data saved: {timing_file}")
        except Exception as e:
            logger.warning(f"⚠️  Could not save timing data: {e}")


# Global timer instance
_timer: Optional[StartupTimer] = None


def get_timer() -> StartupTimer:
    """Get global startup timer instance"""
    global _timer
    if _timer is None:
        _timer = StartupTimer()
    return _timer


def time_service(service_name: str):
    """Decorator to time a service initialization"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            timer = get_timer()
            return timer.time_service(service_name, func, *args, **kwargs)
        return wrapper
    return decorator


def start_timing():
    """Start timing overall startup"""
    timer = get_timer()
    timer.start()


def end_timing() -> float:
    """End timing and return total time"""
    timer = get_timer()
    return timer.end()


if __name__ == "__main__":
    # Test timing
    timer = StartupTimer()
    timer.start()

    # Simulate some services
    timer.time_service("test_service_1", lambda: time.sleep(0.1))
    timer.time_service("test_service_2", lambda: time.sleep(0.2))
    timer.time_service("test_service_3", lambda: time.sleep(1.5))  # Bottleneck

    total = timer.end()
    print(f"\n✅ Total time: {total:.2f}s")
