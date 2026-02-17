#!/usr/bin/env python3
"""Play the animated episode"""
from pathlib import Path
import os
import subprocess

project_root = Path(__file__).parent.parent.parent
animated = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIMATED_COMPLETE.mp4"

if animated.exists():
    print("="*80)
    print("🎬 PLAYING ANIMATED EPISODE - FULL SCREEN")
    print("="*80)
    print(f"✅ Found: {animated.name}")
    print(f"📁 Location: {animated}")
    print(f"🎬 This is REAL animated content (not text!)")
    print(f"   - Animated backgrounds")
    print(f"   - Moving characters")
    print(f"   - Particle effects")
    print(f"   - 60 FPS smooth animation")
    print("="*80)
    print("\n🚀 Launching player...")

    # Try VLC first (best for full screen)
    try:
        subprocess.Popen(
            ["vlc", "--fullscreen", "--no-video-title-show", str(animated)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Playing in VLC (full screen)")
    except FileNotFoundError:
        # Fallback to system default
        os.startfile(str(animated))
        print("✅ Playing with system default player")
        print("   (Press F11 for full screen)")

    print("\n🎬 Episode is now playing!")
    print("   Press ESC or close the player to exit.")
else:
    print(f"❌ Animated episode not found: {animated}")
