#!/usr/bin/env python3
"""
Activate HUD Now - Quick Activation

Simple one-command activation to see HUD visually and functionally.

Usage:
    python scripts/python/activate_hud_now.py

Tags: #HUD #ACTIVATE #QUICK @JARVIS @LUMINA
"""

import sys
import time
import webbrowser
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_hud_system import JARVISHUDSystem, AlertPriority, HUDDisplayType
    from jarvis_hud_web_server import JARVISHUDWebServer
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error: {e}")
    print("   Please ensure all dependencies are installed")
    sys.exit(1)

logger = get_logger("ActivateHUDNow")


def main():
    """Activate HUD now"""
    print("=" * 80)
    print("🚀 ACTIVATING JARVIS HUD - IRON MAN STYLE")
    print("=" * 80)
    print()

    # Initialize HUD
    print("Initializing HUD System...")
    hud = JARVISHUDSystem(project_root=project_root)
    print("   ✅ HUD System ready")

    # Create welcome alert
    print("\nCreating welcome alert...")
    alert = hud.create_alert(
        title="JARVIS HUD Activated",
        message="HUD system is now active and monitoring all LUMINA systems",
        priority=AlertPriority.INFO,
        display_type=HUDDisplayType.STATUS
    )
    print(f"   ✅ Alert created: {alert.alert_id}")

    # Start server
    print("\nStarting web server...")
    server = JARVISHUDWebServer(project_root=project_root, port=8080)
    server.start()
    print("   ✅ Web server started")

    # Wait a moment for server to be ready
    time.sleep(1)

    # Open browser
    url = "http://localhost:8080"
    print(f"\n🌐 Opening browser to: {url}")
    try:
        webbrowser.open(url)
        print("   ✅ Browser opened")
    except Exception as e:
        print(f"   ⚠️  Could not open browser automatically: {e}")
        print(f"   Please open manually: {url}")

    print("\n" + "=" * 80)
    print("✅ JARVIS HUD IS NOW ACTIVE!")
    print("=" * 80)
    print()
    print("📺 VISUAL: You should see HUD in your browser")
    print("   - Black background")
    print("   - Green HUD panels")
    print("   - Status information")
    print("   - Progress bars")
    print("   - Alerts")
    print()
    print("🔊 AUDIBLE: Alerts will play sounds")
    print()
    print("📱 MOBILE: Access from mobile at http://<your-ip>:8080")
    print()
    print("Press Ctrl+C to stop...")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server.stop()
        print("✅ HUD stopped")


if __name__ == "__main__":


    main()