#!/usr/bin/env python3
"""
Create Anime Episode with Real Audio and Subtitles

Creates a full anime-style episode with:
- Japanese anime art style (Ghibli-inspired)
- Real TTS narration (actual words)
- On-screen subtitles
- Background music

Tags: #PEAK #ANIME #JAPANESE #TTS #SUBTITLES @LUMINA @JARVIS
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple

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

from quantum_anime_anime_style_generator import QuantumAnimeAnimeStyleGenerator
from quantum_anime_real_tts_narration import QuantumAnimeRealTTSNarration
from quantum_anime_audio_generator import QuantumAnimeAudioGenerator, AudioTrack
import subprocess

logger = get_logger("CreateAnimeEpisodeWithAudio")


def main():
    """Create full anime episode with audio and subtitles"""
    print("="*80)
    print("CREATING ANIME EPISODE WITH REAL AUDIO & SUBTITLES")
    print("="*80)
    print("🎨 Japanese anime style (Ghibli-inspired)")
    print("🎤 Real TTS narration (actual words)")
    print("📝 On-screen subtitles")
    print("🎵 Background music")
    print("="*80)

    # Episode script with narration and subtitles
    episode_script = [
        {
            "start_time": 0.0,
            "duration": 30.0,
            "title": "Quantum Dimensions",
            "subtitle": "Welcome to Quantum Dimensions",
            "narration": "Welcome to Quantum Dimensions. Today we explore the universe and discover amazing things about space and time."
        },
        {
            "start_time": 30.0,
            "duration": 30.0,
            "title": "The Tiny Dot",
            "subtitle": "Everything starts with a single point",
            "narration": "Everything in the universe starts with a single point. A tiny dot that contains infinite possibilities."
        },
        {
            "start_time": 60.0,
            "duration": 30.0,
            "title": "Understanding Dimensions",
            "subtitle": "We live in three dimensions of space",
            "narration": "We live in three dimensions of space. Length, width, and height define our physical world."
        },
        {
            "start_time": 90.0,
            "duration": 30.0,
            "title": "Time as Dimension",
            "subtitle": "Time is the fourth dimension",
            "narration": "Time is the fourth dimension. It flows forward, connecting past, present, and future."
        },
        {
            "start_time": 120.0,
            "duration": 30.0,
            "title": "Quantum Realm",
            "subtitle": "Beyond the visible dimensions",
            "narration": "Beyond the visible dimensions lies the quantum realm. A place where particles behave in mysterious ways."
        },
        {
            "start_time": 150.0,
            "duration": 30.0,
            "title": "String Theory",
            "subtitle": "Eleven dimensions in string theory",
            "narration": "String theory suggests there are eleven dimensions. Most are curled up so small we cannot see them."
        },
        {
            "start_time": 180.0,
            "duration": 30.0,
            "title": "The Journey Continues",
            "subtitle": "Our exploration never ends",
            "narration": "Our exploration of dimensions never ends. There is always more to discover and understand."
        }
    ]

    total_duration = sum(seg["duration"] for seg in episode_script)
    print(f"\n📝 Episode script: {len(episode_script)} segments, {total_duration/60:.1f} minutes")

    # Initialize generators
    print("\n🎨 Initializing generators...")
    anime_gen = QuantumAnimeAnimeStyleGenerator(project_root)
    tts_gen = QuantumAnimeRealTTSNarration(project_root)
    audio_gen = QuantumAnimeAudioGenerator(project_root)

    # Generate scenes with anime style and subtitles
    print("\n🎬 Generating anime-style scenes...")
    scene_videos = []
    narration_files = []

    for i, segment in enumerate(episode_script):
        scene_id = f"S01E01_anime_segment_{i+1:02d}"

        # Create subtitles list
        subtitles = [
            (0.0, segment["subtitle"])
        ]

        # Generate anime-style scene
        print(f"   🎨 Scene {i+1}/{len(episode_script)}: {segment['title']}")
        scene_path = anime_gen.create_anime_scene(
            scene_id=scene_id,
            duration=segment["duration"],
            fps=60,
            resolution=(1920, 1080),
            title=segment["title"],
            subtitles=subtitles,
            style="ghibli"
        )

        if scene_path.exists():
            scene_videos.append(scene_path)
            print(f"      ✅ Created: {scene_path.name}")

        # Generate narration
        print(f"   🎤 Narration {i+1}/{len(episode_script)}...")
        narration_path = audio_gen.audio_dir / f"{scene_id}_narration.wav"

        if tts_gen.generate_narration(segment["narration"], narration_path):
            narration_files.append((segment["start_time"], narration_path))
            print(f"      ✅ Generated: {narration_path.name}")
        else:
            print(f"      ⚠️  TTS failed, using fallback")

    if not scene_videos:
        print("\n❌ No scenes generated")
        return

    # Concatenate scenes
    print(f"\n🎬 Concatenating {len(scene_videos)} scenes...")
    import tempfile
    concat_file = Path(tempfile.gettempdir()) / "quantum_anime_anime" / "concat.txt"
    concat_file.parent.mkdir(parents=True, exist_ok=True)

    with open(concat_file, 'w', encoding='utf-8') as f:
        for scene_path in scene_videos:
            path_str = str(scene_path.absolute()).replace('\\', '/')
            f.write(f"file '{path_str}'\n")

    video_without_audio = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIME_STYLE_NO_AUDIO.mp4"

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-y",
        str(video_without_audio)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0 and video_without_audio.exists():
            print(f"   ✅ Video concatenated: {video_without_audio.name}")
        else:
            print(f"   ❌ Concatenation failed")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Generate background music
    print(f"\n🎵 Generating background music...")
    music_path = audio_gen.audio_dir / "S01E01_anime_background_music.wav"
    audio_gen.generate_background_music(total_duration, music_path, "ambient")

    # Mix narration files
    print(f"\n🎚️  Mixing audio tracks...")
    if narration_files:
        # Create mixed narration
        mixed_narration_path = audio_gen.audio_dir / "S01E01_anime_mixed_narration.wav"

        tracks = [
            AudioTrack("music", music_path, total_duration, "music", volume=0.25, start_time=0.0)
        ]

        # Add narration tracks at their start times
        for start_time, narration_path in narration_files:
            if narration_path.exists():
                # Get duration
                try:
                    result = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", str(narration_path)],
                        capture_output=True, text=True, timeout=10
                    )
                    duration = float(result.stdout.strip())
                except:
                    duration = 30.0

                tracks.append(AudioTrack(
                    f"narration_{start_time}",
                    narration_path,
                    duration,
                    "narration",
                    volume=0.8,
                    start_time=start_time
                ))

        audio_gen.mix_audio_tracks(tracks, mixed_narration_path)

        # Add audio to video
        print(f"\n🎬 Adding audio to video...")
        final_output = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIME_STYLE_WITH_AUDIO.mp4"

        if audio_gen.add_audio_to_video(video_without_audio, mixed_narration_path, final_output):
            size_mb = final_output.stat().st_size / 1024 / 1024
            print(f"\n✅ ANIME EPISODE WITH AUDIO CREATED!")
            print(f"   📁 Location: {final_output}")
            print(f"   📊 Size: {size_mb:.1f} MB")
            print(f"   🎨 Style: Japanese anime (Ghibli-inspired)")
            print(f"   🎤 Narration: Real TTS (actual words)")
            print(f"   📝 Subtitles: On-screen")
            print(f"   🎵 Music: Background ambient")
            print(f"\n🚀 Ready to play!")
        else:
            print(f"\n❌ Failed to add audio")
    else:
        print(f"\n⚠️  No narration files to mix")

    print("="*80)


if __name__ == "__main__":


    main()