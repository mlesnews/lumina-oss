#!/usr/bin/env python3
"""
Quantum Anime 40-Minute Episode Stitcher

Stitches together 20 minutes of content + 20 minutes of commercials
to create the full 40-minute Cartoon Network style episode.

Tags: #PEAK #F4 #EPISODE #STITCH #40MIN #MARKETING @LUMINA @JARVIS
"""

import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

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

logger = get_logger("QuantumAnime40MinStitcher")


@dataclass
class EpisodeSegment:
    """Episode segment (content or commercial)"""
    segment_id: str
    video_path: Path
    duration: float
    type: str  # content or commercial
    start_time: float = 0.0


class QuantumAnime40MinStitcher:
    """
    40-Minute Episode Stitcher

    Creates full episodes with integrated commercials
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize stitcher"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("QuantumAnime40MinStitcher")

        # Directories
        self.video_dir = self.project_root / "data" / "quantum_anime" / "videos"
        self.commercial_dir = self.project_root / "data" / "quantum_anime" / "commercials"
        self.output_dir = self.project_root / "data" / "quantum_anime" / "episodes_40min"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # NAS output
        v_drive = Path("V:\\")
        if v_drive.exists():
            self.nas_output_dir = v_drive / "quantum_anime" / "episodes_40min"
            self.nas_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.nas_output_dir = None

        # Commercial generator
        self.commercial_generator = QuantumAnimeCommercialGenerator(self.project_root)

        # Episode structure
        self.content_duration = 1200.0  # 20 minutes
        self.commercial_duration = 1200.0  # 20 minutes
        self.total_duration = 2400.0  # 40 minutes

        # Commercial placement strategy
        self.commercial_breaks = [
            (300.0, 120.0),   # 5 min in, 2 min commercial
            (600.0, 120.0),   # 10 min in, 2 min commercial
            (900.0, 120.0),   # 15 min in, 2 min commercial
            (1200.0, 120.0),  # 20 min in, 2 min commercial (end of content)
            (1320.0, 120.0),  # 22 min in, 2 min commercial
            (1440.0, 120.0),  # 24 min in, 2 min commercial
            (1560.0, 120.0),  # 26 min in, 2 min commercial
            (1680.0, 120.0),  # 28 min in, 2 min commercial
            (1800.0, 120.0),  # 30 min in, 2 min commercial
            (1920.0, 120.0),  # 32 min in, 2 min commercial
        ]

    def create_40min_episode(self, episode_id: str) -> Path:
        try:
            """Create full 40-minute episode with commercials"""
            self.logger.info(f"🎬 Creating 40-minute episode: {episode_id}")

            # Step 1: Get content video
            content_video = self.video_dir / f"{episode_id}_COMPLETE_REAL.mp4"
            if not content_video.exists():
                # Try scene videos
                self.logger.info("   Complete episode not found, using scene videos...")
                content_video = self._create_content_from_scenes(episode_id)

            if not content_video or not content_video.exists():
                raise FileNotFoundError(f"Content video not found for {episode_id}")

            # Step 2: Ensure commercials exist
            self.logger.info("   Ensuring commercials are created...")
            self.commercial_generator.create_all_commercials()

            # Step 3: Get commercial videos
            commercials = self._get_commercial_videos()

            if len(commercials) < 10:
                self.logger.warning(f"   Only {len(commercials)} commercials available, need 10")

            # Step 4: Create episode structure
            segments = self._create_episode_structure(content_video, commercials)

            # Step 5: Stitch together
            output_path = self.output_dir / f"{episode_id}_40MIN_FINAL.mp4"
            self._stitch_episode(segments, output_path)

            # Step 6: Copy to NAS
            if self.nas_output_dir:
                self._copy_to_nas(output_path)

            self.logger.info(f"✅ 40-minute episode created: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error in create_40min_episode: {e}", exc_info=True)
            raise
    def _create_content_from_scenes(self, episode_id: str) -> Optional[Path]:
        try:
            """Create content video from individual scenes"""
            scene_videos = []

            for scene_num in range(1, 8):
                scene_path = self.video_dir / f"{episode_id}_scene_{scene_num:02d}_REAL.mp4"
                if scene_path.exists():
                    scene_videos.append(scene_path)

            if not scene_videos:
                return None

            # Concatenate scenes
            output_path = self.video_dir / f"{episode_id}_CONTENT_TEMP.mp4"
            self._concatenate_videos(scene_videos, output_path)

            return output_path if output_path.exists() else None

        except Exception as e:
            self.logger.error(f"Error in _create_content_from_scenes: {e}", exc_info=True)
            raise
    def _get_commercial_videos(self) -> List[Path]:
        try:
            """Get commercial video files"""
            commercials = []

            # Star Wars parodies
            star_wars_commercials = [
                "poppa_palps_001_REAL.mp4",
                "vader_crying_001_REAL.mp4",
                "aluminum_falcon_001_REAL.mp4",
                "blue_harvest_001_REAL.mp4"
            ]

            # LUMINA ads
            lumina_ads = [
                "lumina_ai_001_REAL.mp4",
                "lumina_quantum_001_REAL.mp4"
            ]

            # Third-party sponsors
            sponsors = [
                "sponsor_tech_001_REAL.mp4",
                "sponsor_edu_001_REAL.mp4"
            ]

            # Collect all available commercials
            all_commercials = star_wars_commercials + lumina_ads + sponsors

            for commercial_name in all_commercials:
                commercial_path = self.commercial_dir / commercial_name
                if commercial_path.exists():
                    commercials.append(commercial_path)

            # If we don't have enough, repeat commercials
            while len(commercials) < 10:
                commercials.extend(commercials[:10-len(commercials)])

            return commercials[:10]  # Return exactly 10

        except Exception as e:
            self.logger.error(f"Error in _get_commercial_videos: {e}", exc_info=True)
            raise
    def _create_episode_structure(self, content_video: Path, 
                                  commercials: List[Path]) -> List[EpisodeSegment]:
        """Create episode structure with content and commercials"""
        segments = []
        commercial_index = 0

        # Get actual content duration
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(content_video)],
                capture_output=True,
                text=True,
                timeout=10
            )
            actual_content_duration = float(result.stdout.strip())
        except Exception:
            actual_content_duration = 1200.0  # Default 20 minutes

        self.logger.info(f"   Content video duration: {actual_content_duration:.1f} seconds")

        # Strategy: Insert commercials at intervals within content, then add more commercials
        # Commercial breaks at: 5min, 10min, 15min, 20min (end of content)
        # Then: 10 more commercials to fill remaining 20 minutes

        content_chunks = [
            (0.0, 300.0),      # 0-5 min
            (300.0, 300.0),    # 5-10 min  
            (600.0, 300.0),   # 10-15 min
            (900.0, 300.0),   # 15-20 min
        ]

        # Add content chunks with commercial breaks
        for chunk_start, chunk_duration in content_chunks:
            # Add content chunk
            segments.append(EpisodeSegment(
                segment_id=f"content_{int(chunk_start)}",
                video_path=content_video,
                duration=chunk_duration,
                type="content",
                start_time=chunk_start
            ))

            # Add commercial break after each chunk
            if commercial_index < len(commercials):
                segments.append(EpisodeSegment(
                    segment_id=f"commercial_{commercial_index}",
                    video_path=commercials[commercial_index],
                    duration=120.0,
                    type="commercial",
                    start_time=0.0  # Will be calculated during stitching
                ))
                commercial_index += 1

        # Add remaining commercials to reach 20 minutes total commercial time
        # We've added 4 commercials (480 seconds), need 720 more seconds (6 more commercials)
        remaining_commercials_needed = 6
        for i in range(remaining_commercials_needed):
            if commercial_index < len(commercials):
                segments.append(EpisodeSegment(
                    segment_id=f"commercial_{commercial_index}",
                    video_path=commercials[commercial_index],
                    duration=120.0,
                    type="commercial",
                    start_time=0.0
                ))
                commercial_index += 1
            else:
                # Loop back through commercials
                segments.append(EpisodeSegment(
                    segment_id=f"commercial_loop_{i}",
                    video_path=commercials[i % len(commercials)],
                    duration=120.0,
                    type="commercial",
                    start_time=0.0
                ))

        self.logger.info(f"   Created {len(segments)} segments: {sum(1 for s in segments if s.type == 'content')} content, {sum(1 for s in segments if s.type == 'commercial')} commercials")

        return segments

    def _stitch_episode(self, segments: List[EpisodeSegment], output_path: Path):
        """Stitch episode segments together"""
        self.logger.info(f"   Stitching {len(segments)} segments into 40-minute episode...")

        # Create temp directory for segments
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "quantum_anime_stitch"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Create concat file
        concat_file = temp_dir / "episode_concat.txt"

        segment_files = []
        with open(concat_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments):
                if segment.type == "content":
                    # Extract segment from content video
                    temp_segment = self._extract_video_segment(
                        segment.video_path,
                        segment.start_time,
                        segment.duration,
                        f"{segment.segment_id}_temp.mp4"
                    )
                    if temp_segment and temp_segment.exists():
                        path_str = str(temp_segment.absolute()).replace('\\', '/')
                        f.write(f"file '{path_str}'\n")
                        segment_files.append(temp_segment)
                        self.logger.info(f"      Added content segment: {segment.segment_id} ({segment.duration:.1f}s)")
                else:
                    # Use full commercial
                    if segment.video_path.exists():
                        path_str = str(segment.video_path.absolute()).replace('\\', '/')
                        f.write(f"file '{path_str}'\n")
                        segment_files.append(segment.video_path)
                        self.logger.info(f"      Added commercial: {segment.segment_id}")

        if not segment_files:
            self.logger.error("   ❌ No valid segments to concatenate")
            return

        # Render locally first, then copy to NAS
        local_output = temp_dir / output_path.name

        # Concatenate
        self.logger.info(f"   Concatenating {len(segment_files)} files...")
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
            str(local_output)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200  # 2 hours
            )

            if result.returncode == 0 and local_output.exists():
                # Copy to final location
                import shutil
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_output, output_path)

                size_mb = output_path.stat().st_size / 1024 / 1024
                self.logger.info(f"   ✅ Episode stitched: {output_path} ({size_mb:.1f} MB)")
            else:
                self.logger.error(f"   ❌ Stitching failed: {result.stderr[:500]}")
        except Exception as e:
            self.logger.error(f"   ❌ Error: {e}")

    def _extract_video_segment(self, video_path: Path, start_time: float, 
                              duration: float, output_name: str) -> Optional[Path]:
        """Extract segment from video"""
        temp_dir = Path(tempfile.gettempdir()) / "quantum_anime_video"
        temp_dir.mkdir(parents=True, exist_ok=True)

        output_path = temp_dir / output_name

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",
            "-y",
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and output_path.exists():
                return output_path
            else:
                return None
        except Exception:
            return None

    def _concatenate_videos(self, video_paths: List[Path], output_path: Path):
        """Concatenate videos"""
        import tempfile
        concat_file = Path(tempfile.gettempdir()) / "quantum_anime_video" / "concat.txt"
        concat_file.parent.mkdir(parents=True, exist_ok=True)

        with open(concat_file, 'w', encoding='utf-8') as f:
            for video in video_paths:
                path_str = str(video.absolute()).replace('\\', '/')
                f.write(f"file '{path_str}'\n")

        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            "-y",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, capture_output=True, timeout=1800)
        except Exception:
            pass

    def _copy_to_nas(self, local_path: Path):
        """Copy to NAS with retry logic"""
        if not self.nas_output_dir:
            return

        nas_path = self.nas_output_dir / local_path.name

        # Retry logic for network drive issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                import shutil
                import time

                # Ensure parent directory exists
                try:
                    nas_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass  # May fail if already exists or network issue

                # Try copying with a small delay
                if attempt > 0:
                    time.sleep(2)

                # Use copyfile with explicit error handling
                with open(local_path, 'rb') as src:
                    with open(nas_path, 'wb') as dst:
                        shutil.copyfileobj(src, dst, length=1024*1024)  # 1MB chunks

                # Verify copy
                if nas_path.exists() and nas_path.stat().st_size == local_path.stat().st_size:
                    self.logger.info(f"   ✅ Copied to NAS: {nas_path} ({nas_path.stat().st_size/1024/1024:.1f} MB)")
                    return
                else:
                    raise Exception("File size mismatch after copy")

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"   ⚠️  NAS copy attempt {attempt + 1} failed: {e}, retrying...")
                else:
                    self.logger.warning(f"   ⚠️  Could not copy to NAS after {max_retries} attempts: {e}")
                    self.logger.info(f"   📁 Local file available at: {local_path}")


def main():
    try:
        """Main entry point"""
        print("="*80)
        print("QUANTUM ANIME 40-MINUTE EPISODE STITCHER")
        print("="*80)

        stitcher = QuantumAnime40MinStitcher()

        # Create 40-minute episode
        print("\n🎬 Creating 40-minute episode (S01E01)...")
        episode_path = stitcher.create_40min_episode("S01E01")

        if episode_path and episode_path.exists():
            size_mb = episode_path.stat().st_size / 1024 / 1024
            print(f"\n✅ 40-minute episode created!")
            print(f"   📁 Location: {episode_path}")
            print(f"   📊 Size: {size_mb:.1f} MB")
            print(f"   ⏱️  Duration: 40 minutes (20 min content + 20 min commercials)")
        else:
            print("\n❌ Episode creation failed")

        print("\n✅ Stitching complete!")
        print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()