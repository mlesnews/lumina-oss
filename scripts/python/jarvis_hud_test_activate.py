#!/usr/bin/env python3
"""
JARVIS HUD Test & Activate

Quick test and activation script to verify HUD is working visually and functionally.

Tags: #JARVIS #HUD #TEST #ACTIVATE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_hud_system import JARVISHUDSystem, AlertPriority, HUDDisplayType
    from jarvis_hud_web_server import JARVISHUDWebServer
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("JARVISHUDTest")
    logger.error(f"Required imports not available: {e}")
    sys.exit(1)

logger = get_logger("JARVISHUDTest")


def main():
    """Test and activate HUD"""
    print("=" * 80)
    print("🚀 JARVIS HUD TEST & ACTIVATE")
    print("=" * 80)
    print()

    # Initialize HUD system
    print("1. Initializing HUD System...")
    try:
        hud_system = JARVISHUDSystem(project_root=project_root)
        print("   ✅ HUD System initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize HUD System: {e}")
        return

    # Create test alerts
    print("\n2. Creating test alerts...")
    try:
        # Info alert
        alert1 = hud_system.create_alert(
            title="HUD System Active",
            message="JARVIS HUD is now operational",
            priority=AlertPriority.INFO,
            display_type=HUDDisplayType.STATUS
        )
        print(f"   ✅ Created INFO alert: {alert1.alert_id}")

        # Warning alert
        alert2 = hud_system.create_alert(
            title="System Monitoring",
            message="All systems being monitored",
            priority=AlertPriority.WARNING,
            display_type=HUDDisplayType.STATUS
        )
        print(f"   ✅ Created WARNING alert: {alert2.alert_id}")

        # Test alert
        alert3 = hud_system.create_alert(
            title="Test Alert",
            message="This is a test alert to verify HUD display",
            priority=AlertPriority.ALERT,
            display_type=HUDDisplayType.ALERTS
        )
        print(f"   ✅ Created ALERT: {alert3.alert_id}")
    except Exception as e:
        print(f"   ⚠️  Could not create test alerts: {e}")

    # Start web server
    print("\n3. Starting HUD Web Server...")
    try:
        server = JARVISHUDWebServer(project_root=project_root, port=8080)
        server.start()
        print("   ✅ Web Server started")
        print(f"   🌐 Access HUD at: http://localhost:8080")
        print(f"   📱 Mobile: http://<your-ip>:8080")
    except Exception as e:
        print(f"   ❌ Failed to start web server: {e}")
        return

    # Verify HUD data
    print("\n4. Verifying HUD data...")
    try:
        hud_data = hud_system.generate_hud_data()
        print(f"   ✅ HUD data generated")
        print(f"      Alerts: {len(hud_data.get('alerts', []))}")
        print(f"      Displays: {len(hud_data.get('displays', []))}")
        print(f"      System Status: {hud_data.get('system_status', {}).get('status', 'unknown')}")
    except Exception as e:
        print(f"   ⚠️  Could not verify HUD data: {e}")

    print("\n" + "=" * 80)
    print("✅ JARVIS HUD IS NOW ACTIVE!")
    print("=" * 80)
    print()
    print("📺 VISUAL: Open browser to http://localhost:8080")
    print("🔊 AUDIBLE: Alerts will play sounds when triggered")
    print("📱 MOBILE: Access from mobile device on same network")
    print()
    print("Press Ctrl+C to stop...")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down HUD...")
        server.stop()
        print("✅ HUD stopped")


if __name__ == "__main__":


    main()