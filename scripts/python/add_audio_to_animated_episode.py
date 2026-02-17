#!/usr/bin/env python3
"""
Add Audio to Animated Episode

Generates and adds audio (narration, music) to the animated episode.

Tags: #PEAK #AUDIO #EPISODE @LUMINA @JARVIS
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from quantum_anime_audio_generator import QuantumAnimeAudioGenerator, AudioTrack
import subprocess

logger = get_logger("AddAudioToAnimatedEpisode")


def main():
    """Add audio to animated episode"""
    print("="*80)
    print("ADDING AUDIO TO ANIMATED EPISODE")
    print("="*80)

    # Paths
    animated_video = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIMATED_COMPLETE.mp4"

    if not animated_video.exists():
        print(f"\n❌ Animated episode not found: {animated_video}")
        return

    # Get video duration
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(animated_video)],
            capture_output=True, text=True, timeout=10
        )
        video_duration = float(result.stdout.strip())
        print(f"\n✅ Found animated episode: {video_duration/60:.1f} minutes")
    except Exception as e:
        print(f"\n❌ Error getting duration: {e}")
        return

    # Initialize audio generator
    audio_gen = QuantumAnimeAudioGenerator(project_root)

    print(f"\n🎵 Generating audio tracks...")

    # Generate background music for entire duration
    music_path = audio_gen.audio_dir / "S01E01_background_music.wav"
    print(f"   🎵 Background music...")
    audio_gen.generate_background_music(video_duration, music_path, "ambient")

    # Generate narration (simplified - in production would use actual TTS)
    narration_path = audio_gen.audio_dir / "S01E01_narration.wav"
    print(f"   🎤 Narration...")
    audio_gen.generate_narration("Quantum Dimensions - Episode 1", video_duration, narration_path)

    # Mix audio tracks
    print(f"\n🎚️  Mixing audio tracks...")
    mixed_audio_path = audio_gen.audio_dir / "S01E01_mixed_audio.wav"

    tracks = [
        AudioTrack("music", music_path, video_duration, "music", volume=0.3, start_time=0.0),
        AudioTrack("narration", narration_path, video_duration, "narration", volume=0.7, start_time=0.0)
    ]

    audio_gen.mix_audio_tracks(tracks, mixed_audio_path)

    # Add audio to video
    print(f"\n🎬 Adding audio to video...")
    output_path = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIMATED_WITH_AUDIO.mp4"

    success = audio_gen.add_audio_to_video(animated_video, mixed_audio_path, output_path)

    if success and output_path.exists():
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"\n✅ EPISODE WITH AUDIO CREATED!")
        print(f"   📁 Location: {output_path}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        print(f"   🎵 Audio: Background music + narration")
        print(f"   🎬 Video: Real animated content")
        print(f"\n🚀 Ready to play!")
    else:
        print(f"\n❌ Failed to add audio")

    print("="*80)


if __name__ == "__main__":


    main()