#!/usr/bin/env python3
"""
Diagnose Voice Systems - Check if dynamic listening and auto-accept are working

Tags: #troubleshooting #decisioning #VOICE_SYSTEM #DIAGNOSTIC
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    logger = get_adaptive_logger("VoiceSystemDiagnostic")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VoiceSystemDiagnostic")

def check_auto_send_monitor():
    """Check if auto-send monitor is running and configured correctly"""
    print("\n" + "="*80)
    print("🔍 CHECKING AUTO-SEND MONITOR (Dynamic Listening Scaling)")
    print("="*80)

    try:
        from cursor_auto_send_monitor import get_auto_send_monitor
        monitor = get_auto_send_monitor()

        if not monitor:
            print("❌ Monitor instance is None")
            return False

        print(f"✅ Monitor instance exists")
        print(f"   Running: {monitor.running}")
        print(f"   Enabled: {monitor.enabled}")
        print(f"   Min pause threshold: {monitor.min_pause_threshold}s")
        print(f"   Max pause threshold: {monitor.max_pause_threshold}s")
        print(f"   Current pause threshold: {monitor.pause_threshold}s")
        print(f"   Has pending message: {monitor.has_pending_message}")
        print(f"   Last activity time: {monitor.last_activity_time}")
        print(f"   Last speech end time: {monitor.last_speech_end_time}")
        print(f"   Stats: {monitor.stats}")

        if not monitor.running:
            print("⚠️  WARNING: Monitor is not running!")
            print("   Fix: Monitor should be started by full_time_monitoring_service")
            return False

        if monitor.min_pause_threshold != 1.5:
            print(f"⚠️  WARNING: Min pause threshold is {monitor.min_pause_threshold}s, expected 1.5s")
            return False

        print("✅ Auto-Send Monitor appears to be configured correctly")
        return True

    except Exception as e:
        print(f"❌ Error checking auto-send monitor: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_auto_accept_service():
    """Check if auto-accept service is running"""
    print("\n" + "="*80)
    print("🔍 CHECKING AUTO-ACCEPT SERVICE (Keep All / Accept All)")
    print("="*80)

    try:
        from cursor_ide_auto_accept import CursorIDEAutoAccept
        auto_accept = CursorIDEAutoAccept()

        print(f"✅ Auto-accept instance created")
        print(f"   UI available: {auto_accept.ui_available}")
        print(f"   MANUS available: {auto_accept.manus_available}")
        print(f"   Cursor running: {auto_accept._is_cursor_running()}")

        # Check if service is actually monitoring
        from full_time_monitoring_service import get_full_time_monitoring_service
        service = get_full_time_monitoring_service()

        if hasattr(service, 'auto_accept_instance'):
            print(f"✅ Auto-accept instance in monitoring service: {service.auto_accept_instance is not None}")
            if hasattr(service, 'auto_accept_thread'):
                print(f"   Thread alive: {service.auto_accept_thread.is_alive() if service.auto_accept_thread else 'No thread'}")
            else:
                print("   ⚠️  No auto_accept_thread attribute found")
        else:
            print("⚠️  WARNING: Monitoring service doesn't have auto_accept_instance")

        # Test dialog detection
        print("\n   Testing dialog detection...")
        signal_detected = auto_accept._monitor_dialog_signal()
        print(f"   Dialog signal detected: {signal_detected}")

        if not auto_accept._is_cursor_running():
            print("⚠️  WARNING: Cursor IDE not detected - auto-accept won't work")
            return False

        print("✅ Auto-Accept Service appears to be configured correctly")
        return True

    except Exception as e:
        print(f"❌ Error checking auto-accept service: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_full_time_monitoring():
    """Check if full-time monitoring service is running"""
    print("\n" + "="*80)
    print("🔍 CHECKING FULL-TIME MONITORING SERVICE")
    print("="*80)

    try:
        from full_time_monitoring_service import get_full_time_monitoring_service
        service = get_full_time_monitoring_service()

        print(f"✅ Monitoring service instance exists")
        print(f"   Running: {service.running}")
        print(f"   Stats: {service.stats}")

        if not service.running:
            print("⚠️  WARNING: Full-time monitoring service is not running!")
            print("   Fix: Start the service or ensure it auto-starts")
            return False

        print("✅ Full-Time Monitoring Service is running")
        return True

    except Exception as e:
        print(f"❌ Error checking monitoring service: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostics"""
    print("\n" + "="*80)
    print("🔧 VOICE SYSTEM DIAGNOSTIC")
    print("="*80)
    print("\nChecking all voice-related systems...")

    results = {
        "auto_send_monitor": check_auto_send_monitor(),
        "auto_accept_service": check_auto_accept_service(),
        "full_time_monitoring": check_full_time_monitoring()
    }

    print("\n" + "="*80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*80)

    for system, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {system}: {'PASS' if status else 'FAIL'}")

    all_passing = all(results.values())

    if all_passing:
        print("\n✅ All systems appear to be working correctly")
    else:
        print("\n⚠️  Some systems have issues - see details above")
        print("\n💡 Recommendations:")
        if not results["auto_send_monitor"]:
            print("   - Ensure auto-send monitor is started by full_time_monitoring_service")
            print("   - Check that min_pause_threshold is set to 1.5 seconds")
        if not results["auto_accept_service"]:
            print("   - Ensure auto-accept service is started in background thread")
            print("   - Check that Cursor IDE is running")
            print("   - Verify UI automation libraries are installed (pyautogui, pywinauto)")
        if not results["full_time_monitoring"]:
            print("   - Start full_time_monitoring_service")
            print("   - Check logs for startup errors")

    return 0 if all_passing else 1

if __name__ == "__main__":


    sys.exit(main())