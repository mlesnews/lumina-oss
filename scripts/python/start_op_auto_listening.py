#!/usr/bin/env python3
"""
Start Primary Operator Auto-Listening - REQUIRED

Starts automatic listening for primary operator's voice.
No manual clicks needed - system automatically recognizes OP and starts listening.

Tags: #PRIMARY_OPERATOR #AUTO_LISTEN #REQUIRED @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from primary_operator_voice_recognition import PrimaryOperatorVoiceRecognition
    OP_RECOGNITION_AVAILABLE = True
except ImportError as e:
    OP_RECOGNITION_AVAILABLE = False
    print(f"❌ Primary operator recognition not available: {e}")
    sys.exit(1)

print("=" * 80)
print("🎤 STARTING PRIMARY OPERATOR AUTO-LISTENING (REQUIRED)")
print("=" * 80)
print()
print("This will:")
print("  - Automatically recognize your voice (OP)")
print("  - Start listening without manual clicks")
print("  - Filter out TV/background/wife/other voices")
print("  - Train your voice profile automatically")
print()

try:
    recognition = PrimaryOperatorVoiceRecognition()
    recognition.start_auto_listening()

    print("✅ Auto-listening started")
    print("   System is now listening for your voice")
    print("   No manual clicks needed!")
    print()
    print("To stop: Press Ctrl+C or close this window")
    print("=" * 80)

    # Keep running
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recognition.stop_auto_listening()
        print("\n👋 Auto-listening stopped")

except Exception as e:
    print(f"❌ Failed to start auto-listening: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
