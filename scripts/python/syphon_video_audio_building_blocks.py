#!/usr/bin/env python3
"""
SYPHON Video/Audio Building Blocks - Extract @ask-requested Core Messages

Breaks down video and audio into basic building blocks using SYPHON.
Extracts @ask-requested patterns as core messages.
Uses SYPHON as foundation for video production.
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class VideoBuildingBlock:
    """Video building block extracted by SYPHON"""
    block_id: str
    timestamp_start: float  # seconds
    timestamp_end: float  # seconds
    content_type: str  # "video", "audio", "text", "visual"
    content: str  # Extracted content
    ask_requested_patterns: List[str] = field(default_factory=list)  # @ask-requested patterns
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioBuildingBlock:
    """Audio building block extracted by SYPHON"""
    block_id: str
    timestamp_start: float
    timestamp_end: float
    transcript: str
    ask_requested_patterns: List[str] = field(default_factory=list)
    audio_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoreMessage:
    """Core @ask-requested message extracted from video/audio"""
    message_id: str
    ask_requested_text: str  # The actual @ask-requested content
    confidence: float  # 0.0 - 1.0
    source_blocks: List[str] = field(default_factory=list)  # Block IDs where found
    timestamp_range: Tuple[float, float] = (0.0, 0.0)
    context: Dict[str, Any] = field(default_factory=dict)


class SyphonVideoAudioProcessor:
    """
    SYPHON Video/Audio Processor

    Breaks down video/audio into building blocks.
    Extracts @ask-requested patterns as core messages.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "syphon_video_audio"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.video_blocks: Dict[str, VideoBuildingBlock] = {}
        self.audio_blocks: Dict[str, AudioBuildingBlock] = {}
        self.core_messages: List[CoreMessage] = []

        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("SyphonVideoAudio")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🔬 SYPHON - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def extract_audio_from_video(self, video_path: Path) -> Optional[Path]:
        """Extract audio track from video using FFmpeg"""
        if not video_path.exists():
            return None

        # First check if video has audio stream
        try:
            probe_cmd = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)

            if 'audio' not in probe_result.stdout.lower():
                self.logger.info(f"ℹ️ Video has no audio stream: {video_path.name}")
                return None  # No audio to extract
        except Exception as e:
            self.logger.warning(f"Could not probe video for audio: {e}")

        audio_path = self.data_dir / f"{video_path.stem}_audio.wav"

        try:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # WAV format
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                str(audio_path),
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and audio_path.exists():
                self.logger.info(f"✅ Extracted audio: {audio_path}")
                return audio_path
            else:
                # Check if error is just "no audio stream"
                if 'does not contain any stream' in result.stderr or 'no audio streams' in result.stderr.lower():
                    self.logger.info(f"ℹ️ Video has no audio: {video_path.name}")
                    return None
                self.logger.error(f"❌ Audio extraction failed: {result.stderr[:200]}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Audio extraction error: {e}")
            return None

    def transcribe_audio(self, audio_path: Path) -> List[Dict[str, Any]]:
        """Transcribe audio to text (building block extraction)"""
        # Try whisper or similar
        # For now, return placeholder structure

        blocks = []

        # In real implementation:
        # - Use Whisper API or local model
        # - Segment into time-based blocks
        # - Extract transcript for each block

        return blocks

    def extract_ask_requested_patterns(self, text: str) -> List[str]:
        """Extract @ask-requested patterns from text"""
        ask_patterns = []

        # Pattern 1: @ask followed by request
        pattern1 = r'@ask[:\s]+([^@\n]+?)(?=@|\n|$)'
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            ask_text = match.group(1).strip()
            if ask_text:
                ask_patterns.append(ask_text)

        # Pattern 2: @ASK-REQUESTED in caps
        pattern2 = r'@ASK-REQUESTED[:\s]+([^@\n]+?)(?=@|\n|$)'
        matches = re.finditer(pattern2, text, re.IGNORECASE)
        for match in matches:
            ask_text = match.group(1).strip()
            if ask_text:
                ask_patterns.append(ask_text)

        # Pattern 3: "ask for" or "request" patterns
        pattern3 = r'(?:ask for|request|requested)[:\s]+([^.\n]+)'
        matches = re.finditer(pattern3, text, re.IGNORECASE)
        for match in matches:
            ask_text = match.group(1).strip()
            if ask_text and len(ask_text) > 5:  # Filter short matches
                ask_patterns.append(ask_text)

        return list(set(ask_patterns))  # Remove duplicates

    def break_down_video(self, video_path: Path, block_duration: float = 10.0) -> List[VideoBuildingBlock]:
        try:
            """
            Break down video into building blocks

            Each block is a basic unit that can be reused/reassembled.
            """
            if not video_path.exists():
                self.logger.error(f"❌ Video not found: {video_path}")
                return []

            self.logger.info(f"🔬 Breaking down video into building blocks: {video_path.name}")

            blocks = []

            # Extract audio first
            audio_path = self.extract_audio_from_video(video_path)

            if audio_path:
                # Transcribe audio
                transcript_blocks = self.transcribe_audio(audio_path)

                # Create video blocks from transcript
                for i, transcript_block in enumerate(transcript_blocks):
                    block_id = f"block_{video_path.stem}_{i}"

                    # Extract @ask patterns from transcript
                    transcript_text = transcript_block.get('text', '')
                    ask_patterns = self.extract_ask_requested_patterns(transcript_text)

                    block = VideoBuildingBlock(
                        block_id=block_id,
                        timestamp_start=transcript_block.get('start', i * block_duration),
                        timestamp_end=transcript_block.get('end', (i + 1) * block_duration),
                        content_type="video",
                        content=transcript_text,
                        ask_requested_patterns=ask_patterns,
                        metadata={
                            'video_file': str(video_path),
                            'audio_file': str(audio_path),
                            'block_index': i
                        }
                    )

                    blocks.append(block)
                    self.video_blocks[block_id] = block

            self.logger.info(f"✅ Created {len(blocks)} building blocks from video")
            return blocks

        except Exception as e:
            self.logger.error(f"Error in break_down_video: {e}", exc_info=True)
            raise
    def extract_core_messages(self, blocks: List[VideoBuildingBlock]) -> List[CoreMessage]:
        """
        Extract core @ask-requested messages from building blocks

        Core messages are the @ask-requested patterns.
        These become the central theme of video production.
        """
        core_messages = []
        ask_to_blocks = {}

        # Aggregate @ask patterns from all blocks
        for block in blocks:
            for ask_text in block.ask_requested_patterns:
                if ask_text not in ask_to_blocks:
                    ask_to_blocks[ask_text] = []
                ask_to_blocks[ask_text].append(block.block_id)

        # Create core messages
        for ask_text, block_ids in ask_to_blocks.items():
            # Get timestamp range
            timestamps = [(self.video_blocks[bid].timestamp_start, 
                          self.video_blocks[bid].timestamp_end) 
                         for bid in block_ids if bid in self.video_blocks]

            min_start = min([t[0] for t in timestamps]) if timestamps else 0.0
            max_end = max([t[1] for t in timestamps]) if timestamps else 0.0

            # Calculate confidence (more blocks = higher confidence)
            confidence = min(1.0, len(block_ids) / 5.0)  # Cap at 1.0

            message_id = hashlib.md5(ask_text.encode()).hexdigest()[:16]

            core_message = CoreMessage(
                message_id=message_id,
                ask_requested_text=ask_text,
                confidence=confidence,
                source_blocks=block_ids,
                timestamp_range=(min_start, max_end),
                context={
                    'frequency': len(block_ids),
                    'blocks_count': len(block_ids)
                }
            )

            core_messages.append(core_message)

        # Sort by confidence (highest first)
        core_messages.sort(key=lambda m: m.confidence, reverse=True)

        self.core_messages = core_messages
        self.logger.info(f"✅ Extracted {len(core_messages)} core @ask-requested messages")

        return core_messages

    def create_video_from_core_messages(self, core_messages: List[CoreMessage],
                                       output_path: Path) -> Optional[Path]:
        """
        Create video with @ask-requested messages as core content

        Uses SYPHON building blocks to construct video around core messages.
        """
        if not core_messages:
            self.logger.warning("⚠️ No core messages to build video from")
            return None

        # Primary core message (highest confidence)
        primary_message = core_messages[0]

        self.logger.info(f"🎬 Creating video with core message: {primary_message.ask_requested_text[:100]}")

        # Build video script from core messages
        script_parts = []

        # Introduction
        script_parts.append("Welcome to LUMINA.")
        script_parts.append("Here's what was requested:")

        # Core messages
        for i, msg in enumerate(core_messages[:3], 1):  # Top 3 messages
            script_parts.append(f"{i}. {msg.ask_requested_text}")

        # Closing
        script_parts.append("This is what we're building.")
        script_parts.append("This is LUMINA.")

        script = " ".join(script_parts)

        # Create video using core message
        from lumina_video_production_executor import VideoProductionExecutor
        executor = VideoProductionExecutor()

        video_path = executor.create_text_video(
            script=script,
            title=f"LUMINA - {primary_message.ask_requested_text[:50]}",
            duration=60,  # 1 minute
            output_filename=output_path.name if output_path else None
        )

        if video_path:
            self.logger.info(f"✅ Video created with core @ask-requested message: {video_path}")

        return video_path


class SyphonVideoProductionPipeline:
    """
    SYPHON Video Production Pipeline

    Complete pipeline:
    1. Break down source videos into SYPHON building blocks
    2. Extract @ask-requested core messages
    3. Create new videos with @ask-requested as core content
    """

    def __init__(self):
        self.processor = SyphonVideoAudioProcessor()
        self.project_root = Path(__file__).parent.parent.parent

        self.logger = logging.getLogger("SyphonVideoPipeline")
        self.logger.setLevel(logging.INFO)

    def process_video_for_core_message(self, video_path: Path) -> Dict[str, Any]:
        """
        Process video to extract core @ask-requested message

        Returns video built around the core message.
        """
        self.logger.info(f"🔬 Processing video for core @ask-requested message: {video_path.name}")

        # Step 1: Break down into building blocks
        blocks = self.processor.break_down_video(video_path)

        # Step 2: Extract core messages
        core_messages = self.processor.extract_core_messages(blocks)

        if not core_messages:
            return {
                'success': False,
                'error': 'No @ask-requested patterns found in video'
            }

        # Step 3: Create video from core messages
        output_path = self.project_root / "output" / "videos" / f"core_message_{video_path.stem}.mp4"
        video_path_output = self.processor.create_video_from_core_messages(
            core_messages,
            output_path
        )

        return {
            'success': True,
            'blocks_extracted': len(blocks),
            'core_messages': len(core_messages),
            'primary_message': core_messages[0].ask_requested_text if core_messages else None,
            'output_video': str(video_path_output) if video_path_output else None
        }


def main():
    try:
        """Main execution"""
        processor = SyphonVideoAudioProcessor()

        print("🔬 SYPHON Video/Audio Building Blocks")
        print("=" * 80)
        print("Breaking down videos into building blocks.")
        print("Extracting @ask-requested core messages.")
        print()

        # Example: Process existing videos
        video_dir = Path("output/videos")
        if video_dir.exists():
            videos = list(video_dir.glob("*.mp4"))
            if videos:
                print(f"Found {len(videos)} videos to process")
                for video in videos[:3]:  # Process first 3
                    print(f"\n🔬 Processing: {video.name}")
                    blocks = processor.break_down_video(video)
                    if blocks:
                        core_messages = processor.extract_core_messages(blocks)
                        if core_messages:
                            print(f"   ✅ Found {len(core_messages)} core @ask-requested messages:")
                            for msg in core_messages[:3]:
                                print(f"      - {msg.ask_requested_text[:80]}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()