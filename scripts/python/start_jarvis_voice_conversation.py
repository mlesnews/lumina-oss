#!/usr/bin/env python3
"""
Start JARVIS Hands-Free Voice Conversation
Quick launcher for always-listening voice conversation

Usage:
    python start_jarvis_voice_conversation.py
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from jarvis_async_voice_conversation import get_async_voice_conversation

if __name__ == "__main__":
    print("="*70)
    print("🎤 JARVIS Hands-Free Voice Conversation")
    print("="*70)
    print()
    print("Starting always-listening voice conversation...")
    print()

    conversation = get_async_voice_conversation()
    conversation.start()

    print("✅ JARVIS is now listening")
    print("   Just speak naturally - no trigger words needed")
    print("   Press Ctrl+C to stop")
    print()

    try:
        import time
        while conversation.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n")
        conversation.stop()
        print("👋 Conversation ended")
