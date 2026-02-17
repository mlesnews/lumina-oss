#!/usr/bin/env python3
"""
LUMINA SYPHON Video Production - Core Message Extraction

Breaks down videos with SYPHON.
Extracts @ask-requested as core messages.
Creates videos with @ask-requested as core content.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import SYPHON video processor
from syphon_video_audio_building_blocks import (
    SyphonVideoAudioProcessor,
    SyphonVideoProductionPipeline
)

# Import video executor
from lumina_video_production_executor import VideoProductionExecutor
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class LuminaSyphonVideoProduction:
    """
    LUMINA SYPHON Video Production

    Complete pipeline:
    1. Break down videos with SYPHON (building blocks)
    2. Extract @ask-requested core messages
    3. Create videos with @ask-requested as core content
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.syphon_processor = SyphonVideoAudioProcessor()
        self.video_executor = VideoProductionExecutor()
        self.pipeline = SyphonVideoProductionPipeline()

        self.logger = logging.getLogger("LuminaSyphonVideo")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🎬🔬 %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)

    def process_existing_videos_for_core_messages(self):
        """Process all existing videos to extract and create core message videos"""
        video_dir = self.project_root / "output" / "videos"

        if not video_dir.exists():
            self.logger.warning(f"⚠️ Video directory not found: {video_dir}")
            return []

        videos = list(video_dir.glob("*.mp4"))
        self.logger.info(f"🔬 Processing {len(videos)} videos with SYPHON...")

        results = []

        for video in videos:
            try:
                self.logger.info(f"🔬 Processing: {video.name}")

                # Process video for core @ask-requested message
                result = self.pipeline.process_video_for_core_message(video)

                if result.get('success'):
                    results.append(result)
                    self.logger.info(f"   ✅ Core message: {result.get('primary_message', 'Unknown')[:80]}")
                    self.logger.info(f"   ✅ Blocks: {result.get('blocks_extracted', 0)}")
                    self.logger.info(f"   ✅ Messages: {result.get('core_messages', 0)}")
                else:
                    self.logger.warning(f"   ⚠️ {result.get('error', 'Unknown error')}")

            except Exception as e:
                self.logger.error(f"   ❌ Error processing {video.name}: {e}")

        return results

    def create_video_from_ask_requested(self, ask_requested_text: str,
                                       output_filename: Optional[str] = None) -> Optional[Path]:
        """
        Create video with @ask-requested as core message

        The @ask-requested text becomes the central theme of the video.
        """
        self.logger.info(f"🎬 Creating video with @ask-requested core message")
        self.logger.info(f"   Core message: {ask_requested_text[:100]}")

        # Build script around @ask-requested
        script = (
            f"Welcome to LUMINA. "
            f"This is what was requested: {ask_requested_text}. "
            f"This is what we're building. "
            f"This is LUMINA. "
            f"Personal human opinion. Individual perspective. "
            f"For whatever it's worth - which is everything."
        )

        # Create video
        safe_title = "".join(c for c in ask_requested_text[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        title = f"LUMINA - {safe_title}"

        video_path = self.video_executor.create_text_video(
            script=script,
            title=title,
            duration=45,  # 45 seconds
            output_filename=output_filename
        )

        if video_path:
            self.logger.info(f"✅ Video created with @ask-requested core message: {video_path}")

        return video_path


async def main():
    """Main execution"""
    producer = LuminaSyphonVideoProduction()

    print("🎬🔬 LUMINA SYPHON VIDEO PRODUCTION")
    print("=" * 80)
    print("Breaking down videos with SYPHON building blocks.")
    print("Extracting @ask-requested core messages.")
    print("Creating videos with @ask-requested as core content.")
    print()

    # Process existing videos
    print("🔬 Step 1: Processing existing videos for core @ask-requested messages...")
    results = producer.process_existing_videos_for_core_messages()

    print()
    print("📊 RESULTS:")
    print(f"   Videos Processed: {len(results)}")
    for i, result in enumerate(results[:5], 1):
        if result.get('success'):
            print(f"   {i}. Core Message: {result.get('primary_message', 'Unknown')[:60]}")
            print(f"      Blocks: {result.get('blocks_extracted', 0)}")
            print(f"      Messages: {result.get('core_messages', 0)}")

    print()
    print("✅ SYPHON video processing complete!")


if __name__ == "__main__":



    asyncio.run(main())