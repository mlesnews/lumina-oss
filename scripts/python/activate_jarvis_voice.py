#!/usr/bin/env python3
"""
Activate JARVIS Voice - Quick Activation Script

Simple script to activate JARVIS with full voice capabilities.
JARVIS will speak out loud and listen for voice commands.

Usage:
    python scripts/python/activate_jarvis_voice.py

@JARVIS @VOICE @ACTIVATION
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_voice_activation import JARVISVoiceActivation


def main():
    """Activate JARVIS Voice"""
    print("\n" + "="*80)
    print("🎯 Activating JARVIS Voice Interface")
    print("="*80)
    print()
    print("JARVIS will:")
    print("  🗣️  Speak responses out loud")
    print("  👂 Listen to your voice commands")
    print("  🧠 Determine intent from your requests")
    print()
    print("Say 'exit', 'quit', or 'goodbye' to end the conversation")
    print("="*80)
    print()

    activation = JARVISVoiceActivation()
    activation.run_continuous()


if __name__ == "__main__":


    main()