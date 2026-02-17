#!/usr/bin/env python3
"""
Start Token Usage Monitoring System
====================================

Starts all token monitoring components:
1. Cursor token integration (monitors logs)
2. Auto-send monitor (tracks asks)
3. HUD display updates

Run this to start the full monitoring system.
"""

import sys
import time
import threading
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from cursor_token_integration import CursorTokenIntegration
    from cursor_auto_send_monitor import get_auto_send_monitor
    from token_usage_monitor import TokenUsageMonitor
    HAS_COMPONENTS = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    HAS_COMPONENTS = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TokenMonitoringSystem")


def start_monitoring():
    """Start all monitoring components."""
    if not HAS_COMPONENTS:
        print("❌ Required components not available")
        return

    print("\n" + "=" * 80)
    print("🚀 STARTING TOKEN USAGE MONITORING SYSTEM")
    print("=" * 80)
    print()

    # 1. Start auto-send monitor (already tracks asks)
    print("1️⃣ Starting Auto-Send Monitor...")
    try:
        auto_send = get_auto_send_monitor()
        print("   ✅ Auto-Send Monitor active (tracks asks)")
    except Exception as e:
        print(f"   ⚠️  Auto-Send Monitor error: {e}")

    print()

    # 2. Start Cursor token integration (monitors logs for actual tokens)
    print("2️⃣ Starting Cursor Token Integration...")
    try:
        cursor_integration = CursorTokenIntegration()

        # Start in background thread
        def monitor_cursor():
            cursor_integration.monitor_loop(interval=5.0)

        cursor_thread = threading.Thread(target=monitor_cursor, daemon=True, name="CursorTokenMonitor")
        cursor_thread.start()
        print("   ✅ Cursor token monitoring active (background thread)")
    except Exception as e:
        print(f"   ⚠️  Cursor integration error: {e}")

    print()

    # 3. Start token usage monitor gauge updates
    print("3️⃣ Starting Token Usage Gauge Updates...")
    try:
        token_monitor = TokenUsageMonitor()

        def update_gauges():
            while True:
                try:
                    token_monitor._update_gauges()
                    time.sleep(1.0)  # Update every second
                except Exception as e:
                    logger.error(f"Gauge update error: {e}")
                    time.sleep(5.0)

        gauge_thread = threading.Thread(target=update_gauges, daemon=True, name="GaugeUpdater")
        gauge_thread.start()
        print("   ✅ Gauge updates active (1s interval)")
    except Exception as e:
        print(f"   ⚠️  Gauge updates error: {e}")

    print()
    print("=" * 80)
    print("✅ TOKEN MONITORING SYSTEM ACTIVE")
    print("=" * 80)
    print()
    print("Components running:")
    print("  • Auto-Send Monitor: Tracks asks when messages are sent")
    print("  • Cursor Integration: Monitors logs for token counts")
    print("  • Gauge Updates: Updates HUD display every second")
    print()
    print("View HUD:")
    print("  python scripts/python/token_hud_display.py")
    print()
    print("View Header:")
    print("  python scripts/python/display_active_model_with_tokens.py --header")
    print()
    print("Press Ctrl+C to stop all monitoring")
    print("=" * 80)
    print()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring system...")
        print("✅ Monitoring stopped")


if __name__ == "__main__":
    start_monitoring()
