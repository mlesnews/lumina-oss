#!/usr/bin/env python3
"""
Quantum Anime Video Retry System - Automatic Retry for All Videos

Automatically retries failed video generation, verifies integrity,
and completes missing videos.

Tags: #PEAK #F4 #VIDEO #RETRY #AUTOMATIC @LUMINA @JARVIS
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
import time

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

from quantum_anime_real_video_generator import QuantumAnimeRealVideoGenerator

logger = get_logger("QuantumAnimeVideoRetry")


class QuantumAnimeVideoRetry:
    """
    Automatic Retry System for Video Generation

    Retries all failed videos and verifies integrity
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize retry system"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("QuantumAnimeVideoRetry")

        self.generator = QuantumAnimeRealVideoGenerator(self.project_root)

        # Directories
        self.local_output_dir = self.project_root / "data" / "quantum_anime" / "videos"
        v_drive = Path("V:\\")
        if v_drive.exists():
            self.nas_output_dir = v_drive / "quantum_anime" / "videos"
        else:
            self.nas_output_dir = None

        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def verify_video_file(self, video_path: Path) -> bool:
        """Verify video file is valid and complete"""
        if not video_path.exists():
            return False

        # Check file size (should be > 0)
        if video_path.stat().st_size == 0:
            return False

        # Use FFprobe to verify video integrity
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                 "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration > 0
            else:
                return False
        except Exception as e:
            self.logger.warning(f"Could not verify {video_path}: {e}")
            # Fallback: check if file exists and has size
            return video_path.stat().st_size > 1000  # At least 1KB

    def retry_scene_video(self, episode_id: str, scene_number: int) -> Optional[Path]:
        """Retry creating a scene video"""
        self.logger.info(f"🔄 Retrying: {episode_id} Scene {scene_number}")

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"   Attempt {attempt}/{self.max_retries}")
                video_path = self.generator.create_scene_video(episode_id, scene_number)

                # Verify the video
                if video_path and self.verify_video_file(video_path):
                    self.logger.info(f"   ✅ Scene {scene_number} verified: {video_path}")
                    return video_path
                else:
                    self.logger.warning(f"   ⚠️  Scene {scene_number} verification failed")
                    if video_path and video_path.exists():
                        video_path.unlink()  # Delete corrupted file

                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)

            except Exception as e:
                self.logger.error(f"   ❌ Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

        return None

    def retry_trailer_video(self, trailer_id: str, trailer_type: str) -> Optional[Path]:
        """Retry creating a trailer video"""
        self.logger.info(f"🔄 Retrying: {trailer_id} ({trailer_type})")

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"   Attempt {attempt}/{self.max_retries}")
                video_path = self.generator.create_trailer_video(trailer_id, trailer_type)

                # Verify the video
                if video_path and self.verify_video_file(video_path):
                    self.logger.info(f"   ✅ Trailer verified: {video_path}")
                    return video_path
                else:
                    self.logger.warning(f"   ⚠️  Trailer verification failed")
                    if video_path and video_path.exists():
                        video_path.unlink()

                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)

            except Exception as e:
                self.logger.error(f"   ❌ Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

        return None

    def find_missing_scenes(self, episode_id: str) -> List[int]:
        try:
            """Find missing or corrupted scene videos"""
            missing = []

            for scene_num in range(1, 8):
                # Check local
                local_path = self.local_output_dir / f"{episode_id}_scene_{scene_num:02d}_REAL.mp4"
                # Check NAS
                nas_path = None
                if self.nas_output_dir:
                    nas_path = self.nas_output_dir / f"{episode_id}_scene_{scene_num:02d}_REAL.mp4"

                # Check if exists and is valid
                found_valid = False
                if local_path.exists() and self.verify_video_file(local_path):
                    found_valid = True
                elif nas_path and nas_path.exists() and self.verify_video_file(nas_path):
                    found_valid = True

                if not found_valid:
                    missing.append(scene_num)
                    self.logger.info(f"   ⚠️  Scene {scene_num} missing or corrupted")

            return missing

        except Exception as e:
            self.logger.error(f"Error in find_missing_scenes: {e}", exc_info=True)
            raise
    def find_missing_trailers(self) -> List[tuple]:
        try:
            """Find missing or corrupted trailers"""
            missing = []

            trailers = [
                ("teaser_001", "teaser"),
                ("main_001", "main"),
                ("extended_001", "extended")
            ]

            for trailer_id, trailer_type in trailers:
                # Check local
                local_path = self.local_output_dir / f"{trailer_id}_{trailer_type}_REAL.mp4"
                # Check NAS
                nas_path = None
                if self.nas_output_dir:
                    nas_path = self.nas_output_dir / f"{trailer_id}_{trailer_type}_REAL.mp4"

                # Check if exists and is valid
                found_valid = False
                if local_path.exists() and self.verify_video_file(local_path):
                    found_valid = True
                elif nas_path and nas_path.exists() and self.verify_video_file(nas_path):
                    found_valid = True

                if not found_valid:
                    missing.append((trailer_id, trailer_type))
                    self.logger.info(f"   ⚠️  Trailer {trailer_id} ({trailer_type}) missing or corrupted")

            return missing

        except Exception as e:
            self.logger.error(f"Error in find_missing_trailers: {e}", exc_info=True)
            raise
    def copy_to_nas_retry(self, local_path: Path, nas_path: Path, max_attempts: int = 3) -> bool:
        """Retry copying file to NAS"""
        import shutil

        for attempt in range(1, max_attempts + 1):
            try:
                nas_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_path, nas_path)

                # Verify copy
                if nas_path.exists() and nas_path.stat().st_size == local_path.stat().st_size:
                    self.logger.info(f"   ✅ Copied to NAS (attempt {attempt}): {nas_path}")
                    return True
                else:
                    self.logger.warning(f"   ⚠️  Copy verification failed (attempt {attempt})")
                    if nas_path.exists():
                        nas_path.unlink()

                    if attempt < max_attempts:
                        time.sleep(2)

            except Exception as e:
                self.logger.warning(f"   ⚠️  Copy attempt {attempt} failed: {e}")
                if attempt < max_attempts:
                    time.sleep(2)

        return False

    def sync_to_nas(self):
        try:
            """Sync all local videos to NAS"""
            self.logger.info("🔄 Syncing videos to NAS...")

            if not self.nas_output_dir:
                self.logger.warning("   ⚠️  NAS drive not available")
                return

            # Find all local videos
            local_videos = list(self.local_output_dir.glob("*_REAL.mp4"))

            for local_video in local_videos:
                nas_video = self.nas_output_dir / local_video.name

                # Check if NAS copy exists and is valid
                if nas_video.exists() and self.verify_video_file(nas_video):
                    # Check if sizes match
                    if nas_video.stat().st_size == local_video.stat().st_size:
                        continue  # Already synced

                # Copy to NAS
                self.logger.info(f"   📤 Copying: {local_video.name}")
                self.copy_to_nas_retry(local_video, nas_video)

        except Exception as e:
            self.logger.error(f"Error in sync_to_nas: {e}", exc_info=True)
            raise
    def create_complete_episode(self, episode_id: str) -> Optional[Path]:
        """Create complete episode from all scene videos"""
        self.logger.info(f"🎬 Creating complete episode: {episode_id}")

        # Find all valid scene videos
        scene_videos = []

        for scene_num in range(1, 8):
            # Try local first
            local_path = self.local_output_dir / f"{episode_id}_scene_{scene_num:02d}_REAL.mp4"
            nas_path = None
            if self.nas_output_dir:
                nas_path = self.nas_output_dir / f"{episode_id}_scene_{scene_num:02d}_REAL.mp4"

            # Use whichever exists and is valid
            video_path = None
            if local_path.exists() and self.verify_video_file(local_path):
                video_path = local_path
            elif nas_path and nas_path.exists() and self.verify_video_file(nas_path):
                video_path = nas_path

            if video_path:
                scene_videos.append(video_path)
            else:
                self.logger.warning(f"   ⚠️  Scene {scene_num} not available for concatenation")

        if not scene_videos:
            self.logger.error("   ❌ No valid scene videos found")
            return None

        # Concatenate
        output_path = self.local_output_dir / f"{episode_id}_COMPLETE_REAL.mp4"

        # Create concat file
        import tempfile
        concat_file = Path(tempfile.gettempdir()) / "quantum_anime_video" / "concat_list.txt"
        concat_file.parent.mkdir(parents=True, exist_ok=True)

        with open(concat_file, 'w', encoding='utf-8') as f:
            for video in scene_videos:
                # Use forward slashes for FFmpeg
                path_str = str(video.absolute()).replace('\\', '/')
                f.write(f"file '{path_str}'\n")

        # Concatenate with re-encoding
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "copy",
            "-y",
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour
            )

            if result.returncode == 0 and output_path.exists() and self.verify_video_file(output_path):
                self.logger.info(f"   ✅ Complete episode created: {output_path}")

                # Copy to NAS
                if self.nas_output_dir:
                    nas_output = self.nas_output_dir / output_path.name
                    self.copy_to_nas_retry(output_path, nas_output)

                return output_path
            else:
                self.logger.error(f"   ❌ Episode creation failed: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"   ❌ Error: {e}")
            return None

    def retry_all(self, episode_id: str = "S01E01"):
        """Retry all failed videos"""
        self.logger.info("="*80)
        self.logger.info("QUANTUM ANIME VIDEO RETRY - AUTOMATIC RETRY ALL")
        self.logger.info("="*80)

        # Step 1: Find missing scenes
        self.logger.info("\n📊 Step 1: Checking scene videos...")
        missing_scenes = self.find_missing_scenes(episode_id)

        if missing_scenes:
            self.logger.info(f"   Found {len(missing_scenes)} missing/corrupted scenes: {missing_scenes}")

            # Retry missing scenes
            for scene_num in missing_scenes:
                self.retry_scene_video(episode_id, scene_num)
        else:
            self.logger.info("   ✅ All scenes are valid")

        # Step 2: Find missing trailers
        self.logger.info("\n📊 Step 2: Checking trailers...")
        missing_trailers = self.find_missing_trailers()

        if missing_trailers:
            self.logger.info(f"   Found {len(missing_trailers)} missing/corrupted trailers")

            # Retry missing trailers
            for trailer_id, trailer_type in missing_trailers:
                self.retry_trailer_video(trailer_id, trailer_type)
        else:
            self.logger.info("   ✅ All trailers are valid")

        # Step 3: Sync to NAS
        self.logger.info("\n📊 Step 3: Syncing to NAS...")
        self.sync_to_nas()

        # Step 4: Create complete episode
        self.logger.info("\n📊 Step 4: Creating complete episode...")
        complete_episode = self.create_complete_episode(episode_id)

        if complete_episode:
            self.logger.info(f"   ✅ Complete episode: {complete_episode}")
        else:
            self.logger.warning("   ⚠️  Complete episode creation failed")

        self.logger.info("\n✅ Retry complete!")
        self.logger.info("="*80)


def main():
    """Main entry point"""
    retry = QuantumAnimeVideoRetry()
    retry.retry_all("S01E01")


if __name__ == "__main__":


    main()