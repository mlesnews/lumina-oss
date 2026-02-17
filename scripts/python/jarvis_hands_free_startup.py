#!/usr/bin/env python3
"""
JARVIS Hands-Free Startup - Complete System

Starts JARVIS hands-free Cursor control with automatic warm recycling.
Single command to activate everything.
"""

import sys
import signal
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_conversation_cursor_bridge import JARVISConversationCursorBridge
from cursor_intelligent_warm_recycle import CursorIntelligentWarmRecycle

def main():
    """Start complete hands-free system"""
    print("="*70)
    print("🎤 JARVIS Hands-Free Cursor Control - Complete System")
    print("="*70)
    print()

    # Initialize bridge
    print("🔧 Initializing systems...")
    bridge = JARVISConversationCursorBridge()

    # Check recycle status
    if bridge.hands_free and bridge.hands_free.recycle_system:
        recycle_system = bridge.hands_free.recycle_system
        decision = recycle_system.should_recycle()

        if decision.should_recycle:
            print(f"⚠️  Cursor needs recycling: {decision.reason.value}")
            print(f"   Memory: {decision.metrics.get('total_memory_mb', 0):.1f}MB")
            print(f"   CPU: {decision.metrics.get('max_cpu_percent', 0):.1f}%")
            print()
            print("🔄 Performing warm recycle...")
            recycle_system.warm_recycle(decision.reason)
            print("✅ Recycle complete")
            print()
            print("Waiting 5 seconds for Cursor to restart...")
            time.sleep(5)

    print("✅ Systems initialized")
    print()
    print("🚀 Starting hands-free mode...")
    print("   - Voice commands → Cursor control")
    print("   - Automatic warm recycling (when needed)")
    print("   - Keyboard shortcuts (primary)")
    print("   - Mouse fallback")
    print()
    print("🎤 Speak your commands or use Ctrl+C to stop")
    print()

    # Start bridge
    bridge.start_conversation_mode()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        bridge.stop_conversation_mode()
        print("✅ Shutdown complete")


if __name__ == "__main__":


    main()