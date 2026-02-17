#!/usr/bin/env python3
"""
LUMINA Video Generation Helper

Automates what we can and prepares everything for video generation.
Since Runway ML/Pika Labs require web interface, this prepares files,
tracks progress, and helps manage the workflow.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import shutil

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaVideoGenerationHelper")

from lumina_pilot_trailer_videos import LuminaPilotTrailerVideos
from lumina_nas_yt_storage import LuminaNASYTStorage, StorageType
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def prepare_trailer_workspace(trailer_id: str = "trailer_002"):
    try:
        """Prepare workspace for trailer generation"""

        print("\n" + "="*80)
        print("🎬 PREPARING TRAILER WORKSPACE")
        print("="*80 + "\n")

        # Get trailer info
        trailers = LuminaPilotTrailerVideos()
        all_trailers = trailers.get_all_trailers()

        trailer = None
        for t in all_trailers:
            if t.trailer_id == trailer_id:
                trailer = t
                break

        if not trailer:
            print(f"❌ Trailer {trailer_id} not found")
            return False

        # Create workspace directory
        workspace = Path("data/lumina_pilot/workspace") / trailer_id
        workspace.mkdir(parents=True, exist_ok=True)

        # Save script file
        script_file = workspace / "script.txt"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(trailer.script)
        print(f"✅ Script saved: {script_file}")

        # Save metadata
        metadata = {
            "trailer_id": trailer.trailer_id,
            "title": trailer.title,
            "description": trailer.description,
            "script": trailer.script,
            "duration_seconds": trailer.duration_seconds,
            "created": datetime.now().isoformat(),
            "status": "ready_for_generation"
        }

        metadata_file = workspace / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved: {metadata_file}")

        # Create prompt file for AI tools
        prompt_file = workspace / "prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"Create a {trailer.duration_seconds}-second video with the following script:\n\n")
            f.write(trailer.script)
            f.write(f"\n\nStyle: Professional, engaging, LUMINA branding\n")
            f.write(f"Aspect Ratio: 16:9\n")
            f.write(f"Duration: {trailer.duration_seconds} seconds\n")
        print(f"✅ Prompt file saved: {prompt_file}")

        # Get NAS storage path
        nas_storage = LuminaNASYTStorage()
        nas_path = nas_storage.get_storage_path(StorageType.TRAILERS)

        # Create instructions file
        instructions_file = workspace / "INSTRUCTIONS.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(f"# Generate Trailer: {trailer.title}\n\n")
            f.write(f"## Script\n\n")
            f.write(f"```\n{trailer.script}\n```\n\n")
            f.write(f"## Steps\n\n")
            f.write(f"1. Open Runway ML: https://runwayml.com\n")
            f.write(f"2. Copy script from `script.txt`\n")
            f.write(f"3. Generate 30-second video\n")
            f.write(f"4. Download video\n")
            f.write(f"5. Save to: `{nas_path}/{trailer_id}.mp4`\n")
            f.write(f"6. Run: `python scripts/python/lumina_video_generation_helper.py --complete {trailer_id}`\n")
        print(f"✅ Instructions saved: {instructions_file}")

        print(f"\n📁 Workspace created: {workspace}")
        print(f"\n📋 Next steps:")
        print(f"   1. Copy script from: {script_file}")
        print(f"   2. Generate video using Runway ML or Pika Labs")
        print(f"   3. Save video to workspace or NAS")
        print(f"   4. Run: python scripts/python/lumina_video_generation_helper.py --complete {trailer_id}")

        return True


    except Exception as e:
        logger.error(f"Error in prepare_trailer_workspace: {e}", exc_info=True)
        raise
def complete_trailer(trailer_id: str, video_path: str):
    try:
        """Mark trailer as complete and organize files"""

        print(f"\n✅ Completing trailer: {trailer_id}")

        # Get NAS storage
        nas_storage = LuminaNASYTStorage()
        nas_trailers_path = nas_storage.get_storage_path(StorageType.TRAILERS)

        # Ensure NAS directory exists
        nas_trailers_path.mkdir(parents=True, exist_ok=True)

        # Copy video to NAS
        video_path_obj = Path(video_path)
        if video_path_obj.exists():
            target_path = nas_trailers_path / f"{trailer_id}.mp4"
            shutil.copy2(video_path_obj, target_path)
            print(f"✅ Video copied to NAS: {target_path}")

            # Also copy to workspace for backup
            workspace = Path("data/lumina_pilot/workspace") / trailer_id
            workspace.mkdir(parents=True, exist_ok=True)
            workspace_video = workspace / f"{trailer_id}.mp4"
            shutil.copy2(video_path_obj, workspace_video)
            print(f"✅ Video saved to workspace: {workspace_video}")

            # Update trailer status
            trailers = LuminaPilotTrailerVideos()
            # Note: Would need to implement status update method

            print(f"\n✅ Trailer {trailer_id} complete!")
            print(f"   Video location: {target_path}")
            print(f"\n📤 Ready to upload to YouTube!")

            return True
        else:
            print(f"❌ Video file not found: {video_path}")
            return False


    except Exception as e:
        logger.error(f"Error in complete_trailer: {e}", exc_info=True)
        raise
def list_ready_trailers():
    try:
        """List all trailers ready for generation"""

        print("\n📋 TRAILERS READY FOR GENERATION\n")

        trailers = LuminaPilotTrailerVideos()
        all_trailers = trailers.get_all_trailers()

        for i, trailer in enumerate(all_trailers, 1):
            workspace = Path("data/lumina_pilot/workspace") / trailer.trailer_id
            status = "✅ Ready" if workspace.exists() else "⏳ Not started"

            print(f"{i}. {trailer.title}")
            print(f"   ID: {trailer.trailer_id}")
            print(f"   Status: {status}")
            print(f"   Script: {trailer.script[:80]}...")
            print()


    except Exception as e:
        logger.error(f"Error in list_ready_trailers: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Video Generation Helper")
    parser.add_argument("--prepare", metavar="TRAILER_ID", help="Prepare workspace for trailer")
    parser.add_argument("--complete", metavar="TRAILER_ID", help="Complete trailer with video path")
    parser.add_argument("--video", metavar="VIDEO_PATH", help="Video file path (with --complete)")
    parser.add_argument("--list", action="store_true", help="List ready trailers")

    args = parser.parse_args()

    if args.prepare:
        prepare_trailer_workspace(args.prepare)
    elif args.complete:
        if args.video:
            complete_trailer(args.complete, args.video)
        else:
            print("❌ --video required with --complete")
    elif args.list:
        list_ready_trailers()
    else:
        # Default: prepare first trailer
        print("🎬 Preparing first trailer workspace...")
        prepare_trailer_workspace("trailer_002")

