#!/usr/bin/env python3
"""
JARVIS ElevenLabs Manual Setup Helper

Helps manually configure ElevenLabs API key when Neo browser automation isn't available.
Provides step-by-step instructions and clipboard support.
"""

import sys
import os
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

project_root = script_dir.parent.parent

print("="*80)
print("JARVIS ELEVENLABS API KEY SETUP")
print("="*80)
print()
print("Since you have the ElevenLabs page open in Neo browser:")
print()
print("📋 INSTRUCTIONS:")
print()
print("1. On the ElevenLabs page, find your API key")
print("   - It's usually in Settings > API Keys")
print("   - Or on the API Keys page")
print()
print("2. Copy the API key (Ctrl+C)")
print()
print("3. Choose how to configure it:")
print()
print("   Option A: Set environment variable (this session only)")
print("   Option B: Store in Azure Key Vault (permanent)")
print()

choice = input("Choose option (A/B) or press Enter to use clipboard: ").strip().upper()

api_key = None

# Try clipboard first
try:
    import pyperclip
    clipboard = pyperclip.paste()
    if clipboard and len(clipboard) > 20:
        print(f"\n📋 Found in clipboard: {clipboard[:20]}...")
        use_clipboard = input("Use this? (y/n): ").strip().lower()
        if use_clipboard == 'y':
            api_key = clipboard
except:
    pass

# If not from clipboard, ask for input
if not api_key:
    print("\n🔑 Please paste your ElevenLabs API key:")
    api_key = input("API Key: ").strip()

if not api_key or len(api_key) < 20:
    print("\n❌ Invalid API key")
    sys.exit(1)

print(f"\n✅ API key received: {api_key[:20]}...")
print()

# Configure based on choice
if choice == 'A' or not choice:
    # Environment variable
    os.environ['ELEVENLABS_API_KEY'] = api_key
    print("✅ API key set in environment variable (this session)")
    print("   ⚠️  This is temporary - will be lost when terminal closes")
    print()
    print("   For permanent setup, use Option B (Azure Key Vault)")

if choice == 'B' or not choice:
    # Azure Key Vault
    try:
        from azure_service_bus_integration import AzureKeyVaultClient

        print("🔐 Storing in Azure Key Vault...")
        vault_client = AzureKeyVaultClient()
        success = vault_client.set_secret("elevenlabs-api-key", api_key)

        if success:
            print("✅ API key stored in Azure Key Vault (permanent)")
        else:
            print("❌ Failed to store in Key Vault")
    except Exception as e:
        print(f"⚠️  Key Vault error: {e}")
        print("   Environment variable is set as fallback")

# Test voice
print()
print("🧪 Testing voice output...")
try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

    tts = JARVISElevenLabsTTS(project_root=project_root)
    if tts.api_key:
        print("✅ TTS initialized with API key")
        print("🗣️  Speaking test message...")

        result = tts.speak("Hello, this is JARVIS. Can you hear me now?")

        if result:
            print("✅ Voice output successful!")
            print("🎉 JARVIS voice is now working!")
        else:
            print("❌ Voice output failed - check API key and SDK")
    else:
        print("❌ API key not configured in TTS")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("="*80)
print("SETUP COMPLETE")
print("="*80)
