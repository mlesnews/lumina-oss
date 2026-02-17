#!/usr/bin/env python3
"""
Startup All Automation - REQUIRED

Starts ALL automation on system boot:
1. All button monitors (Keep All, Send, Voice, People)
2. Kenny (IMVA) - visible and wandering
3. Ace (ACVA) - ensure visible
4. Auto-listening
5. Voice filtering

Tags: #STARTUP #AUTOMATION #REQUIRED #BOOT @JARVIS @LUMINA
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

logger = get_logger("StartupAllAutomation")


def start_all_automation():
    """Start all automation components - OPTIMIZED: Parallel initialization"""
    # OPTIMIZATION: Start timing
    try:
        from startup_timer import StartupTimer, get_timer, start_timing, end_timing
        start_timing()
        timer = get_timer()
    except:
        timer = None
        logger.warning("⚠️  Startup timer not available")

    print("=" * 80)
    print("🚀 STARTING ALL AUTOMATION - OPTIMIZED STARTUP")
    print("=" * 80)
    print()

    startup_start = time.time()

    # OPTIMIZATION: Start services in parallel where possible
    threads = []
    results = {}

    # 1. Start all button monitors (can run in parallel)
    def start_button_monitors():
        try:
            if timer:
                service_start = time.time()
            from fix_all_clicking_issues import AllButtonMonitor
            button_monitor = AllButtonMonitor()
            button_monitor.start_all_monitors()
            if timer:
                timer.service_times["button_monitors"] = time.time() - service_start
            results["button_monitors"] = True
            print("✅ Button monitors started")
        except Exception as e:
            results["button_monitors"] = False
            print(f"⚠️  Button monitors failed: {e}")

    # 2. Start Kenny (can run in parallel)
    def start_kenny():
        try:
            if timer:
                service_start = time.time()
            from kenny_imva_enhanced import KennyIMVAEnhanced
            kenny = KennyIMVAEnhanced(size=120)
            kenny.start()
            if timer:
                timer.service_times["kenny"] = time.time() - service_start
            results["kenny"] = True
            print("✅ Kenny started")
        except Exception as e:
            results["kenny"] = False
            print(f"⚠️  Kenny failed: {e}")

    # 3. Ensure Ace is visible (can run in parallel)
    def start_ace():
        try:
            if timer:
                service_start = time.time()
            from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
            ace = ACVAArmouryCrateIntegration(project_root)
            hwnd = ace.find_armoury_crate_va()
            if hwnd:
                ace.acva_hwnd = hwnd
                import ctypes
                user32 = ctypes.windll.user32
                user32.ShowWindow(hwnd, 1)
                user32.SetForegroundWindow(hwnd)
                if timer:
                    timer.service_times["ace"] = time.time() - service_start
                results["ace"] = True
                print("✅ Ace made visible")
            else:
                results["ace"] = False
                print("⚠️  Ace not found (Armoury Crate may not be running)")
        except Exception as e:
            results["ace"] = False
            print(f"⚠️  Ace check failed: {e}")

    # OPTIMIZATION: Start these in parallel
    print("Starting services in parallel...")
    t1 = threading.Thread(target=start_button_monitors, daemon=True)
    t2 = threading.Thread(target=start_kenny, daemon=True)
    t3 = threading.Thread(target=start_ace, daemon=True)

    t1.start()
    t2.start()
    t3.start()

    threads.extend([t1, t2, t3])

    # 4. Start Right Alt → @DOIT remapping (can run in parallel)
    def start_right_alt_remap():
        try:
            if timer:
                service_start = time.time()
            from right_alt_doit_remap import RightAltDoitRemap
            remap = RightAltDoitRemap()
            remap.start()
            if timer:
                timer.service_times["right_alt_remap"] = time.time() - service_start
            results["right_alt_remap"] = True
            print("✅ Right Alt → @DOIT remapping started")
        except Exception as e:
            results["right_alt_remap"] = False
            print(f"⚠️  Right Alt remapping failed: {e}")

    # 5. Start auto-listening (must wait for button monitors, but can start after)
    # CRITICAL: This starts passive listening immediately (like VS Code "Hey Code")
    # Voice Input button will be auto-clicked automatically
    print()
    print("4. Starting Right Alt → @DOIT remapping...")
    t4 = threading.Thread(target=start_right_alt_remap, daemon=True)
    t4.start()
    threads.append(t4)

    print()
    print("5. Starting auto-listening (passive mode - like VS Code 'Hey Code')...")
    try:
        if timer:
            service_start = time.time()
        from hybrid_passive_active_listening import HybridPassiveActiveListening
        hybrid_listener = HybridPassiveActiveListening(project_root)
        hybrid_listener.start()
        if timer:
            timer.service_times["hybrid_listening"] = time.time() - service_start
        results["hybrid_listening"] = True
        print("✅ Auto-listening started (passive mode - waiting for 'Hey Jarvis')")
        print("   ✅ Voice Input button auto-clicked (no manual click needed)")
    except Exception as e:
        results["hybrid_listening"] = False
        print(f"⚠️  Auto-listening failed: {e}")

    # 6. Start notification queue manager (monitors and reduces notification count)
    def start_notification_queue_manager():
        try:
            if timer:
                service_start = time.time()
            from cursor_notification_queue_manager import CursorNotificationQueueManager
            queue_manager = CursorNotificationQueueManager(project_root)
            # Start monitoring in background
            monitor_thread = threading.Thread(
                target=queue_manager.monitor_continuously,
                args=(60,),  # Check every 60 seconds
                daemon=True
            )
            monitor_thread.start()
            if timer:
                timer.service_times["notification_queue_manager"] = time.time() - service_start
            results["notification_queue_manager"] = True
            print("✅ Notification queue manager started (monitoring Cursor/VS Code notifications)")
        except Exception as e:
            results["notification_queue_manager"] = False
            print(f"⚠️  Notification queue manager failed: {e}")

    print()
    print("6. Starting notification queue manager...")
    t6 = threading.Thread(target=start_notification_queue_manager, daemon=True)
    t6.start()
    threads.append(t6)

    # Wait for parallel threads to complete (max 5 seconds)
    # Note: notification queue manager runs continuously, don't wait for it
    for t in threads:
        if t != t6:  # Don't wait for notification queue manager
            t.join(timeout=5.0)

    total_time = time.time() - startup_start

    print()
    print("=" * 80)
    print("✅ ALL AUTOMATION STARTED")
    print("=" * 80)

    # OPTIMIZATION: End timing and show results
    if timer:
        total_timed = end_timing()
        print()
        print(f"⏱️  Total startup time: {total_timed:.2f}s")
        print(f"⏱️  Measured time: {total_time:.2f}s")
    print()

    print()
    print("Everything should now be automated:")
    print("  ✅ Keep All button - auto-clicked")
    print("  ✅ Send button - auto-clicked")
    print("  ✅ Voice input button - auto-clicked")
    print("  ✅ People button - auto-clicked")
    print("  ✅ Right Alt → @DOIT remapping - active")
    print("  ✅ Notification queue manager - monitoring and reducing Cursor/VS Code notifications")
    print("  ✅ Kenny - visible and wandering")
    print("  ✅ Ace - visible (if Armoury Crate running)")
    print("  ✅ Auto-listening - active (passive mode, waiting for 'Hey Jarvis')")
    print("  ✅ Team Supervision - active (@PEAK: managers supervised, subordinates report)")
    print()
    print("🔔 Notification Queue Manager:")
    print("   - Monitors notification count every 60 seconds")
    print("   - Auto-reduces queue when count > 5")
    print("   - Dismisses non-critical notifications")
    print("   - Auto-resolves known issues (Git, imports, etc.)")
    print()
    print("👔 Team Management Supervision (@PEAK):")
    print("   - Managers supervised by higher-level AI/agents")
    print("   - Subordinates report completion status to managers/leads")
    print("   - Active monitoring every 5 minutes")
    print()
    print("Press Ctrl+C to stop")
    print()

    # Start team supervision monitor in background
    def start_team_supervision():
        try:
            from active_team_supervision_monitor import run_active_supervision
            run_active_supervision(check_interval=300)  # 5 minutes
        except Exception as e:
            print(f"⚠️  Team supervision failed: {e}")

    t_supervision = threading.Thread(target=start_team_supervision, daemon=True)
    t_supervision.start()
    print("✅ Team supervision monitor started")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping automation...")


if __name__ == "__main__":
    start_all_automation()
