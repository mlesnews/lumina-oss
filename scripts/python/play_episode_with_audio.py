#!/usr/bin/env python3
"""Play episode with audio"""
from pathlib import Path
import os
import subprocess

project_root = Path(__file__).parent.parent.parent
video = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIMATED_WITH_AUDIO.mp4"

if video.exists():
    print("="*80)
    print("🎬 PLAYING EPISODE WITH AUDIO - FULL SCREEN")
    print("="*80)
    print(f"✅ Episode: {video.name}")
    print(f"🎵 Audio: Background music + narration")
    print(f"🎬 Video: Real animated content")
    print("="*80)
    print("\n🚀 Launching player...")

    # Try VLC first (best for full screen)
    try:
        subprocess.Popen(
            ["vlc", "--fullscreen", "--no-video-title-show", str(video)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Playing in VLC (full screen)")
    except FileNotFoundError:
        # Fallback to system default
        os.startfile(str(video))
        print("✅ Playing with system default player")
        print("   (Press F11 for full screen)")

    print("\n🎬 Episode is now playing with SOUND!")
    print("   - Background ambient music")
    print("   - Narration track")
    print("   - Real animated visuals")
    print("   Press ESC or close the player to exit.")
else:
    print(f"❌ Episode not found: {video}")
