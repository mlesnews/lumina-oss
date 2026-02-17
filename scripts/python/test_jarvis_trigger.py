#!/usr/bin/env python3
"""Quick test of Jarvis trigger word"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed

print("=" * 80)
print("🧪 TESTING JARVIS TRIGGER WORD")
print("=" * 80)
print()

t = CursorAutoRecordingTranscriptionFixed(auto_start=True)
print(f"✅ Service started")
print(f"✅ Listening: {t.is_listening}")
print(f"✅ Trigger words: {[tw.word + ' -> ' + tw.action for tw in t.trigger_words]}")
print()
print("Say 'Jarvis' to trigger recording")
print("Press Ctrl+C to stop")
print("=" * 80)

import time
try:
    while True:
        time.sleep(1)
        if t.is_recording:
            print(f"🎤 RECORDING! (Session: {t.current_session.session_id if t.current_session else 'N/A'})")
except KeyboardInterrupt:
    t.stop_listening()
    print("\n👋 Stopped")
