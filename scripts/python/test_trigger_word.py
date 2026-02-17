#!/usr/bin/env python3
"""
Quick test for trigger word detection
Tests microphone and speech recognition
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("TRIGGER WORD TEST")
print("=" * 60)
print()

# Test 1: Check dependencies
print("[1] Checking dependencies...")
try:
    import speech_recognition as sr
    print("   ✅ speech_recognition installed")
except ImportError:
    print("   ❌ speech_recognition NOT installed")
    print("   Install: pip install SpeechRecognition")
    sys.exit(1)

try:
    import pyaudio
    print("   ✅ pyaudio installed")
except ImportError:
    print("   ⚠️  pyaudio not installed (may still work)")
    print("   Install: pip install pyaudio")

print()

# Test 2: Test microphone
print("[2] Testing microphone...")
try:
    r = sr.Recognizer()
    # Use improved settings (same as passive_active_voice_system.py)
    r.energy_threshold = 3000  # Lower = more sensitive
    r.pause_threshold = 1.0  # Longer pause for clearer phrases
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("   🎤 Adjusting for ambient noise (2 seconds)...")
        r.adjust_for_ambient_noise(source, duration=2.0)
        print(f"   ✅ Energy threshold: {r.energy_threshold:.0f}")
        print("   ✅ Microphone working")
except Exception as e:
    print(f"   ❌ Microphone error: {e}")
    sys.exit(1)

print()

# Test 3: Test speech recognition
print("[3] Testing speech recognition...")
print("   🎤 Listening for 5 seconds...")
print("   👉 Say 'Hey Jarvis' or 'Jarvis'")
print()

try:
    r = sr.Recognizer()
    # Use improved settings
    r.energy_threshold = 3000
    r.pause_threshold = 1.0
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2.0)
        # Longer timeout for trigger word
        audio = r.listen(source, timeout=5, phrase_time_limit=15)

    print("   ✅ Audio captured, recognizing...")
    text = r.recognize_google(audio)
    print(f"   📝 Heard: '{text}'")

    # Check for trigger words
    text_lower = text.lower()
    triggers = ["hey jarvis", "jarvis", "hey cursor"]
    found = False

    for trigger in triggers:
        if trigger in text_lower:
            print(f"   ✅ TRIGGER WORD DETECTED: '{trigger}'")
            found = True
            break

    if not found:
        print("   ⚠️  No trigger word detected")
        print(f"   Heard: '{text}'")
        print(f"   Looking for: {triggers}")

except sr.WaitTimeoutError:
    print("   ⚠️  No audio detected (timeout)")
    print("   Check microphone is working")
except sr.UnknownValueError:
    print("   ⚠️  Could not understand audio")
    print("   Try speaking more clearly")
except sr.RequestError as e:
    print(f"   ❌ Speech recognition error: {e}")
    print("   Check internet connection (uses Google Speech API)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
