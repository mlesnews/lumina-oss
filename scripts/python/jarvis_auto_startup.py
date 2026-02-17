#!/usr/bin/env python3
"""
JARVIS Auto-Startup - AI-Managed Automatic Startup

JARVIS automatically starts and manages all LUMINA services:
- Self-times startup/shutdown
- Learns and optimizes automatically
- No manual scripts needed
- Fully AI-managed

Tags: #AI_MANAGED #AUTOMATIC #JARVIS #SELF_OPTIMIZING @JARVIS @LUMINA
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
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoStartup")

try:
    from ai_managed_startup import ai_managed_startup, get_ai_startup
    AI_STARTUP_AVAILABLE = True
except ImportError:
    AI_STARTUP_AVAILABLE = False
    logger.warning("⚠️  AI-managed startup not available")


def main():
    """Main entry point - JARVIS automatically manages everything"""
    print("=" * 80)
    print("🤖 JARVIS AUTO-STARTUP - AI-MANAGED")
    print("=" * 80)
    print()
    print("JARVIS is automatically managing startup:")
    print("  ✅ Self-timing startup/shutdown")
    print("  ✅ Learning from historical data")
    print("  ✅ Auto-optimizing startup sequence")
    print("  ✅ Self-adjusting based on performance")
    print("  ✅ No manual intervention needed")
    print()
    print("=" * 80)
    print()

    if AI_STARTUP_AVAILABLE:
        # AI-managed startup
        success = ai_managed_startup()

        if success:
            print()
            print("=" * 80)
            print("✅ JARVIS AUTO-STARTUP COMPLETE")
            print("=" * 80)
            print()
            print("JARVIS is now ready!")
            print("Say 'Hey Jarvis' to activate.")
            print()
            print("🤖 JARVIS will continue to learn and optimize automatically.")
            print()
        else:
            print("❌ Startup failed")
            return False
    else:
        # Fallback to basic startup
        logger.warning("⚠️  AI-managed startup not available - using fallback")
        try:
            from hybrid_passive_active_listening import HybridPassiveActiveListening
            hybrid_listener = HybridPassiveActiveListening(project_root)
            hybrid_listener.start()
            print("✅ Basic startup complete")
            print("   ✅ Passive listening active (waiting for 'Hey Jarvis')")
            print("   ✅ Voice Input button auto-clicked (no manual click needed)")
        except Exception as e:
            logger.error(f"❌ Fallback startup failed: {e}")
            return False

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🤖 JARVIS: Shutting down...")
        if AI_STARTUP_AVAILABLE:
            startup = get_ai_startup()
            startup.shutdown()
        print("👋 Goodbye!")

    return True


if __name__ == "__main__":


    main()