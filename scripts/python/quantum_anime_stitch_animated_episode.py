#!/usr/bin/env python3
"""
Stitch Animated Episode with Commercials

Takes the REAL animated episode and stitches it with commercials
to create the full 40-minute Cartoon Network style episode.

Tags: #PEAK #F4 #EPISODE #STITCH #40MIN #ANIMATED @LUMINA @JARVIS
"""

import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

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

from quantum_anime_commercial_generator import QuantumAnimeCommercialGenerator
from quantum_anime_40min_episode_stitcher import QuantumAnime40MinStitcher

logger = get_logger("QuantumAnimeStitchAnimatedEpisode")


def main():
    """Stitch animated episode with commercials"""
    print("="*80)
    print("QUANTUM ANIME - STITCH ANIMATED EPISODE WITH COMMERCIALS")
    print("="*80)

    # Paths
    animated_episode = project_root / "data" / "quantum_anime" / "videos_animated" / "S01E01_ANIMATED_COMPLETE.mp4"

    if not animated_episode.exists():
        print(f"\n❌ Animated episode not found: {animated_episode}")
        return

    # Get duration
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(animated_episode)],
            capture_output=True, text=True, timeout=10
        )
        content_duration = float(result.stdout.strip())
        print(f"\n✅ Animated episode found: {content_duration/60:.1f} minutes")
    except Exception as e:
        print(f"\n❌ Error getting duration: {e}")
        return

    # Use the existing stitcher
    stitcher = QuantumAnime40MinStitcher(project_root)

    # Create full 40-minute episode
    output_path = project_root / "data" / "quantum_anime" / "videos" / "S01E01_40MIN_ANIMATED_FINAL.mp4"

    print(f"\n🎬 Stitching animated episode with commercials...")
    print(f"   Content: {content_duration/60:.1f} minutes (REAL animated visuals)")
    print(f"   Target: 40 minutes total (20 min content + 20 min commercials)")

    # Stitch using the animated episode as content
    success = stitcher.create_40min_episode(
        content_video=animated_episode,
        episode_id="S01E01",
        output_path=output_path
    )

    if success and output_path.exists():
        size_mb = output_path.stat().st_size / 1024 / 1024

        # Get final duration
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(output_path)],
                capture_output=True, text=True, timeout=10
            )
            final_duration = float(result.stdout.strip())
        except:
            final_duration = 0

        print(f"\n✅ 40-MINUTE ANIMATED EPISODE CREATED!")
        print(f"   📁 Location: {output_path}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        print(f"   ⏱️  Duration: {final_duration/60:.1f} minutes")
        print(f"   🎬 Content: REAL animated visuals (not text!)")
        print(f"   📺 Commercials: Cartoon Network style")
    else:
        print(f"\n❌ Stitching failed")

    print("="*80)


if __name__ == "__main__":


    main()