#!/usr/bin/env python3
"""
Fast Startup - Optimized LUMINA Startup

Optimized startup sequence with:
- Parallel initialization
- Lazy loading
- Timing instrumentation
- Bottleneck identification

Tags: #STARTUP #PERFORMANCE #OPTIMIZATION @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path

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

logger = get_logger("FastStartup")

try:
    from startup_timer import StartupTimer, start_timing, end_timing
    TIMER_AVAILABLE = True
except ImportError:
    TIMER_AVAILABLE = False
    logger.warning("⚠️  Startup timer not available")


def fast_startup():
    """Fast startup with parallel initialization and timing"""
    # Start timing
    if TIMER_AVAILABLE:
        start_timing()
        timer = StartupTimer()
    else:
        timer = None

    overall_start = time.time()

    print("=" * 80)
    print("🚀 FAST STARTUP - LUMINA")
    print("=" * 80)
    print()

    # CRITICAL: Start hybrid listening FIRST (most important)
    print("1. Starting hybrid passive-active listening (CRITICAL)...")
    try:
        service_start = time.time()
        from hybrid_passive_active_listening import HybridPassiveActiveListening
        hybrid_listener = HybridPassiveActiveListening(project_root)
        hybrid_listener.start()
        service_time = time.time() - service_start
        if timer:
            timer.service_times["hybrid_listening"] = service_time
        print(f"✅ Hybrid listening started ({service_time:.2f}s)")
    except Exception as e:
        print(f"❌ Hybrid listening failed: {e}")
        return False

    # OPTIMIZATION: Start other services in parallel (non-critical)
    print()
    print("2. Starting non-critical services in parallel...")

    def start_button_monitors():
        try:
            service_start = time.time()
            from fix_all_clicking_issues import AllButtonMonitor
            monitor = AllButtonMonitor()
            monitor.start_all_monitors()
            service_time = time.time() - service_start
            if timer:
                timer.service_times["button_monitors"] = service_time
            print(f"✅ Button monitors ({service_time:.2f}s)")
        except Exception as e:
            print(f"⚠️  Button monitors failed: {e}")

    def start_kenny():
        try:
            service_start = time.time()
            from kenny_imva_enhanced import KennyIMVAEnhanced
            kenny = KennyIMVAEnhanced(size=120)
            kenny.start()
            service_time = time.time() - service_start
            if timer:
                timer.service_times["kenny"] = service_time
            print(f"✅ Kenny started ({service_time:.2f}s)")
        except Exception as e:
            print(f"⚠️  Kenny failed: {e}")

    # Start in parallel
    t1 = threading.Thread(target=start_button_monitors, daemon=True)
    t2 = threading.Thread(target=start_kenny, daemon=True)

    t1.start()
    t2.start()

    # Wait for parallel services (max 3 seconds)
    t1.join(timeout=3.0)
    t2.join(timeout=3.0)

    total_time = time.time() - overall_start

    print()
    print("=" * 80)
    print("✅ FAST STARTUP COMPLETE")
    print("=" * 80)

    if timer:
        total_timed = end_timing()
        print(f"⏱️  Total startup time: {total_timed:.2f}s")
    else:
        print(f"⏱️  Total startup time: {total_time:.2f}s")

    print()
    print("LUMINA is ready!")
    print("Say 'Hey Jarvis' to activate.")
    print()

    return True


if __name__ == "__main__":
    fast_startup()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
