#!/usr/bin/env python3
"""
LUMINA Generate First Trailer - LEROY JENKINS MODE

Let's do this! Generate the first trailer video NOW.

Quick start: Generate one trailer to get something watchable immediately.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaGenerateFirstTrailer")

from lumina_pilot_trailer_videos import LuminaPilotTrailerVideos
from lumina_nas_yt_storage import LuminaNASYTStorage, StorageType
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def generate_trailer_instructions(trailer_id: str = "trailer_002"):
    try:
        """
        Generate instructions for creating the first trailer
        Trailer 002 is the Elevator Pitch - perfect for quick start
        """

        print("\n" + "="*80)
        print("🎬 LUMINA - GENERATE FIRST TRAILER (LEEROY JENKINS MODE!)")
        print("="*80 + "\n")

        trailers = LuminaPilotTrailerVideos()
        all_trailers = trailers.get_all_trailers()

        # Find the requested trailer
        trailer = None
        for t in all_trailers:
            if t.trailer_id == trailer_id:
                trailer = t
                break

        if not trailer:
            print(f"❌ Trailer {trailer_id} not found")
            print("\nAvailable trailers:")
            for t in all_trailers:
                print(f"  {t.trailer_id}: {t.title}")
            return

        nas_storage = LuminaNASYTStorage()
        storage_path = nas_storage.get_storage_path(StorageType.TRAILERS)

        print(f"🎯 TARGET: {trailer.title}\n")
        print(f"📝 SCRIPT ({trailer.duration_seconds} seconds):")
        print(f"{'='*80}")
        print(trailer.script)
        print(f"{'='*80}\n")

        print("🚀 STEP-BY-STEP GENERATION:\n")

        print("METHOD 1: Runway ML (Recommended - Best Quality)")
        print("-" * 80)
        print("1. Go to: https://runwayml.com")
        print("2. Sign up/Log in")
        print("3. Click 'Gen-3' or 'Text to Video'")
        print("4. Enter prompt:")
        print(f"   '{trailer.script}'")
        print("5. Set duration: 30 seconds")
        print("6. Set aspect ratio: 16:9 (YouTube)")
        print("7. Click 'Generate'")
        print("8. Wait for generation (2-5 minutes)")
        print("9. Download video")
        print(f"10. Save as: {storage_path}/trailer_{trailer_id}.mp4")
        print("\n")

        print("METHOD 2: Pika Labs (Fast Generation)")
        print("-" * 80)
        print("1. Go to: https://pika.art")
        print("2. Sign up/Log in")
        print("3. Click 'Create' → 'Text to Video'")
        print("4. Enter prompt:")
        print(f"   '{trailer.script}'")
        print("5. Set duration: 30 seconds")
        print("6. Click 'Generate'")
        print("7. Wait for generation (1-3 minutes)")
        print("8. Download video")
        print(f"9. Save as: {storage_path}/trailer_{trailer_id}.mp4")
        print("\n")

        print("METHOD 3: OpenAI Sora (If Available)")
        print("-" * 80)
        print("1. Check OpenAI Sora availability")
        print("2. Use API or interface")
        print(f"3. Generate with script: '{trailer.script[:100]}...'")
        print(f"4. Save as: {storage_path}/trailer_{trailer_id}.mp4")
        print("\n")

        print("="*80)
        print("📤 AFTER GENERATION - UPLOAD TO YOUTUBE")
        print("="*80 + "\n")

        print("1. Go to: https://studio.youtube.com")
        print("2. Click 'Create' → 'Upload video'")
        print(f"3. Select: {storage_path}/trailer_{trailer_id}.mp4")
        print(f"4. Title: '{trailer.title}'")
        print("5. Description:")
        print("   Welcome to LUMINA!")
        print("   Personal human opinion. Individual perspective.")
        print("   For whatever it's worth - which is everything.")
        print("   ")
        print("   Illuminate the @GLOBAL @PUBLIC")
        print("   ")
        print("   Like, Comment, Subscribe!")
        print("6. Tags: LUMINA, AI, Education, Learning, Philosophy")
        print("7. Thumbnail: Create or upload")
        print("8. Visibility: Public (or Unlisted for review)")
        print("9. Click 'Publish'")
        print("10. ✅ WATCH, COMMENT, LIKE, SUBSCRIBE!")
        print("\n")

        print("="*80)
        print("🎯 QUICK COMMAND REFERENCE")
        print("="*80 + "\n")

        print(f"# Mark trailer as produced after generation:")
        print(f"python scripts/python/lumina_pilot_trailer_videos.py --produce {trailer_id}")
        print("\n")
        print(f"# Check all trailers:")
        print("python scripts/python/lumina_pilot_trailer_videos.py --list")
        print("\n")
        print(f"# Get storage location:")
        print("python scripts/python/lumina_nas_yt_storage.py --summary")
        print("\n")

        print("="*80)
        print("🐔 LEEEEEROY JENKINS! LET'S DO THIS!")
        print("="*80 + "\n")

        print("Next steps:")
        print("1. ✅ Script ready (above)")
        print("2. ⏳ Open Runway ML or Pika Labs")
        print("3. ⏳ Generate video")
        print("4. ⏳ Upload to YouTube")
        print("5. ⏳ Watch, Comment, Like, Subscribe!")
        print("\n")

        # Save script to file for easy copy-paste
        script_file = Path("data/lumina_pilot/trailer_script.txt")
        script_file.parent.mkdir(parents=True, exist_ok=True)
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(f"LUMINA TRAILER SCRIPT - {trailer.title}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Duration: {trailer.duration_seconds} seconds\n\n")
            f.write("SCRIPT:\n")
            f.write("-"*80 + "\n")
            f.write(trailer.script)
            f.write("\n" + "-"*80 + "\n\n")
            f.write("Copy this script into your AI video tool!\n")

        print(f"✅ Script saved to: {script_file}")
        print("   Copy this file content into your AI video tool!\n")


    except Exception as e:
        logger.error(f"Error in generate_trailer_instructions: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate First LUMINA Trailer")
    parser.add_argument("--trailer", default="trailer_002", help="Trailer ID to generate")

    args = parser.parse_args()

    generate_trailer_instructions(args.trailer)

