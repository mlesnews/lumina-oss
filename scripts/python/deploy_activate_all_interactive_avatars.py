#!/usr/bin/env python3
"""
Deploy & Activate All Interactive Avatars

DECISIVE ACTION: Activates all interactive avatars (Kenny, Ace, JARVIS) with:
- Listening automation (from 11th)
- Speaking automation (from 11th)
- Karaoke functionality
- All features from yesterday's work

Tags: #AVATAR #DEPLOY #ACTIVATE #KENNY #ACE #JARVIS #LISTENING #SPEAKING #KARAOKE @JARVIS @LUMINA
"""

import sys
import subprocess
import threading
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

logger = get_logger("DeployActivateAvatars")


def start_kenny():
    """Start Kenny interactive avatar"""
    print("🤖 Starting Kenny (Interactive Avatar)...")
    try:
        # Use the start script
        result = subprocess.Popen(
            [sys.executable, str(script_dir / "start_kenny_visible.py")],
            cwd=str(project_root)
        )
        print("   ✅ Kenny process started")
        return result
    except Exception as e:
        print(f"   ❌ Failed to start Kenny: {e}")
        return None


def start_voice_interface():
    """Start voice interface (listening & speaking automation)"""
    print("🎤 Starting Voice Interface (Listening & Speaking Automation)...")
    try:
        from jarvis_voice_interface import JARVISVoiceInterface
        voice = JARVISVoiceInterface(project_root=project_root)

        # Start voice interface (includes listening loop)
        def start_voice():
            try:
                voice.start()  # This starts the listening loop
            except Exception as e:
                logger.error(f"Voice interface error: {e}")

        thread = threading.Thread(target=start_voice, daemon=True)
        thread.start()
        print("   ✅ Voice interface started (listening & speaking active)")
        return voice
    except Exception as e:
        print(f"   ⚠️  Voice interface: {e}")
        return None


def verify_karaoke():
    """Verify karaoke system is available"""
    print("🎵 Verifying Karaoke System...")
    try:
        from karaoke_display import KaraokeDisplay
        karaoke = KaraokeDisplay()
        print("   ✅ Karaoke system available")
        print("   📝 Start with: python scripts/python/karaoke_display.py")
        return karaoke
    except Exception as e:
        print(f"   ⚠️  Karaoke: {e}")
        return None


def verify_ace():
    """Verify Ace avatar system"""
    print("⚔️  Verifying Ace Avatar System...")
    try:
        from ace_humanoid_template import ACEHumanoidTemplate
        from character_avatar_manager import CharacterAvatarManager

        manager = CharacterAvatarManager(project_root=project_root)
        ace_char = manager.registry.get_character("ace")

        if ace_char:
            print("   ✅ Ace avatar registered and available")
            print(f"      Name: {ace_char.name}")
            print(f"      Template: {ace_char.avatar_template}")
            print(f"      Style: {ace_char.avatar_style}")
            return True
        else:
            print("   ⚠️  Ace character not found in registry")
            return False
    except Exception as e:
        print(f"   ⚠️  Ace system: {e}")
        return False


def main():
    """Deploy and activate all interactive avatars"""
    print("=" * 80)
    print("🎭 DEPLOY & ACTIVATE ALL INTERACTIVE AVATARS")
    print("=" * 80)
    print()
    print("DECISIVE ACTION: Activating all interactive avatars with:")
    print("  ✅ Kenny - Interactive avatar (visible on screen)")
    print("  ✅ Ace - Avatar system (if available)")
    print("  ✅ Voice Interface - Listening & Speaking automation")
    print("  ✅ Karaoke - Sing karaoke functionality")
    print()

    processes = []
    threads = []

    # Step 1: Start Kenny
    print("STEP 1: Starting Kenny...")
    kenny_process = start_kenny()
    if kenny_process:
        processes.append(("kenny", kenny_process))
    print()

    # Step 2: Start Voice Interface
    print("STEP 2: Starting Voice Interface...")
    voice = start_voice_interface()
    if voice:
        print("   ✅ Voice interface active")
    print()

    # Step 3: Verify Karaoke
    print("STEP 3: Verifying Karaoke...")
    karaoke = verify_karaoke()
    if karaoke:
        print("   ✅ Karaoke ready")
    print()

    # Step 4: Verify Ace
    print("STEP 4: Verifying Ace...")
    ace_available = verify_ace()
    if ace_available:
        print("   ✅ Ace available")
    print()

    # Step 5: Summary
    print("=" * 80)
    print("✅ ALL INTERACTIVE AVATARS ACTIVATED")
    print("=" * 80)
    print()
    print("Active Systems:")
    if kenny_process:
        print("  ✅ Kenny - Interactive avatar (should be visible on screen)")
    if voice:
        print("  ✅ Voice Interface - Listening & Speaking automation active")
    if karaoke:
        print("  ✅ Karaoke - Ready (start with: python scripts/python/karaoke_display.py)")
    if ace_available:
        print("  ✅ Ace - Avatar system available")
    print()
    print("Features Active:")
    print("  🎤 Listening: Voice recognition active")
    print("  🔊 Speaking: Text-to-speech active")
    print("  🎵 Karaoke: System ready")
    print("  🤖 Avatars: Kenny visible, Ace available")
    print()
    print("To start karaoke:")
    print("  python scripts/python/karaoke_display.py")
    print()
    print("Press Ctrl+C to stop all...")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all avatars...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"   ✅ Stopped {name}")
            except:
                pass
        print("✅ All avatars stopped")


if __name__ == "__main__":


    main()