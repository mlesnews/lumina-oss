#!/usr/bin/env python3
"""
Fix Jarvis Trigger Word - REQUIRED

Ensures "Jarvis" trigger word works and auto-listening starts.
Fixes the issue where saying "Jarvis" does nothing.

Tags: #JARVIS_TRIGGER #AUTO_LISTEN #FIX #REQUIRED @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed
    TRANSCRIPTION_AVAILABLE = True
except ImportError as e:
    TRANSCRIPTION_AVAILABLE = False
    print(f"❌ Transcription service not available: {e}")
    sys.exit(1)

print("=" * 80)
print("🔧 FIXING JARVIS TRIGGER WORD (REQUIRED)")
print("=" * 80)
print()

try:
    project_root = Path(__file__).parent.parent.parent

    # Create transcription service with auto-start
    print("🚀 Creating transcription service with auto-start...")
    transcription = CursorAutoRecordingTranscriptionFixed(
        project_root=project_root,
        auto_start=True  # REQUIRED - auto-start
    )

    # CRITICAL: Add "Jarvis" trigger word
    print("📝 Adding 'Jarvis' trigger word...")

    # Add multiple actions to ensure it works
    transcription.add_trigger_word(
        word="jarvis",
        action="start_recording",  # Explicitly start recording
        case_sensitive=False,
        confidence_threshold=0.5  # Even lower threshold for better detection
    )

    # Also add "activate" action (default action)
    transcription.add_trigger_word("jarvis", "activate", False, 0.5)

    # Add variations
    transcription.add_trigger_word("jarv", "start_recording", False, 0.5)
    transcription.add_trigger_word("jarvis", "start_recording", False, 0.5)

    print("✅ 'Jarvis' trigger word added")
    print()

    # Ensure listening is started
    if not transcription.is_listening:
        print("🔄 Starting listening...")
        transcription.start_listening()
        print("✅ Listening started")
    else:
        print("✅ Already listening")

    print()
    print("=" * 80)
    print("✅ JARVIS TRIGGER WORD FIXED")
    print("=" * 80)
    print()
    print("Now you can:")
    print("  - Say 'Jarvis' to trigger transcription")
    print("  - System will auto-start listening")
    print("  - No manual clicks needed")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)

    # Keep running
    import time
    try:
        while True:
            time.sleep(1)
            if transcription.is_listening:
                print(f"✅ Listening... (say 'Jarvis' to trigger)")
            else:
                print("⚠️  Not listening - restarting...")
                transcription.start_listening()
    except KeyboardInterrupt:
        transcription.stop_listening()
        print("\n👋 Stopped")

except Exception as e:
    print(f"❌ Failed to fix Jarvis trigger: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
