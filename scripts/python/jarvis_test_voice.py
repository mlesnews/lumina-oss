#!/usr/bin/env python3
"""
JARVIS Voice Test

Test JARVIS voice output with ElevenLabs TTS.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

project_root = script_dir.parent.parent

print("="*80)
print("JARVIS VOICE TEST")
print("="*80)
print()

# Test 1: Check ElevenLabs integration
print("1. Checking ElevenLabs Integration...")
try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    print("   ✅ ElevenLabs integration module found")

    tts = JARVISElevenLabsTTS(project_root=project_root)
    print(f"   ✅ TTS object created")

    # Check if API key is available
    if tts.api_key:
        print(f"   ✅ API key found: {tts.api_key[:10]}...")
    else:
        print("   ❌ API key NOT found")
        print("   ⚠️  Set ELEVENLABS_API_KEY environment variable")
        print("   ⚠️  Or add to Azure Key Vault as 'elevenlabs-api-key'")

    # Check if SDK is available
    try:
        from elevenlabs import generate, play, set_api_key
        print("   ✅ ElevenLabs SDK available")
    except ImportError:
        print("   ❌ ElevenLabs SDK NOT installed")
        print("   ⚠️  Install: pip install elevenlabs")

    # Try to speak
    print()
    print("2. Testing Voice Output...")
    print("   Speaking: 'Hello, this is JARVIS. Can you hear me?'")

    try:
        result = tts.speak("Hello, this is JARVIS. Can you hear me?")
        if result:
            print("   ✅ Voice output successful!")
        else:
            print("   ❌ Voice output failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   ⚠️  Check API key and SDK installation")

except ImportError as e:
    print(f"   ❌ Import error: {e}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("="*80)
print("TEST COMPLETE")
print("="*80)
