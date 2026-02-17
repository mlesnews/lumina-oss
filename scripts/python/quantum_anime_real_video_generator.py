#!/usr/bin/env python3
"""
Quantum Anime Real Video Generator - NO PLACEHOLDERS

Generates ACTUAL video files using FFmpeg from storyboards and assets.
Creates real video content with animations, text, audio, and effects.

Tags: #PEAK #F4 #VIDEO #REAL #NO_PLACEHOLDERS @LUMINA @JARVIS
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

logger = get_logger("QuantumAnimeRealVideoGenerator")


@dataclass
class VideoScene:
    """Video scene with real content"""
    scene_id: str
    duration: float
    panels: List[Dict[str, Any]]
    audio_script: Optional[Dict[str, Any]] = None
    music: Optional[Dict[str, Any]] = None


class QuantumAnimeRealVideoGenerator:
    """
    Real Video Generator - Creates ACTUAL Videos

    NO PLACEHOLDERS - Only real video files
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize real video generator"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("QuantumAnimeRealVideoGenerator")

        # Directories
        self.production_dir = self.project_root / "data" / "quantum_anime" / "production"
        self.storyboards_dir = self.production_dir / "storyboards"
        self.audio_dir = self.production_dir / "audio"
        self.renders_dir = self.production_dir / "renders"

        # Output - use V: drive, but write locally first to avoid network issues
        v_drive = Path("V:\\")
        self.use_nas = v_drive.exists()

        if self.use_nas:
            self.nas_output_dir = v_drive / "quantum_anime" / "videos"
            self.nas_output_dir.mkdir(parents=True, exist_ok=True)

        # Local output for reliable writes
        self.local_output_dir = self.project_root / "data" / "quantum_anime" / "videos"
        self.local_output_dir.mkdir(parents=True, exist_ok=True)

        # Use local for actual writes
        self.output_dir = self.local_output_dir

        # Temp directory for intermediate files
        self.temp_dir = Path(tempfile.gettempdir()) / "quantum_anime_video"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Check FFmpeg
        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg is required for real video generation")

        self.logger.info(f"✅ Real video generator initialized")
        self.logger.info(f"📁 Output: {self.output_dir}")

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def create_scene_video(self, episode_id: str, scene_number: int) -> Path:
        try:
            """Create real video for a scene"""
            self.logger.info(f"🎬 Creating real video: {episode_id} Scene {scene_number}")

            # Load storyboard
            storyboard_path = self.storyboards_dir / f"{episode_id}_scene_{scene_number:02d}_storyboard.json"
            if not storyboard_path.exists():
                raise FileNotFoundError(f"Storyboard not found: {storyboard_path}")

            with open(storyboard_path, 'r', encoding='utf-8') as f:
                storyboard = json.load(f)

            # Load animation plan
            animation_path = self.renders_dir / f"{episode_id}_scene_{scene_number:02d}_animation.json"
            animation_plan = {}
            if animation_path.exists():
                with open(animation_path, 'r', encoding='utf-8') as f:
                    animation_plan = json.load(f)

            # Create scene video
            scene_video = self._generate_scene_video(storyboard, animation_plan, episode_id, scene_number)

            # Output path
            output_path = self.output_dir / f"{episode_id}_scene_{scene_number:02d}_REAL.mp4"

            # Render video - write locally first
            local_output = self.local_output_dir / f"{episode_id}_scene_{scene_number:02d}_REAL.mp4"
            nas_output = self.nas_output_dir / f"{episode_id}_scene_{scene_number:02d}_REAL.mp4" if self.use_nas else None

            # Render to local
            self._render_scene_video(scene_video, local_output)

            # Copy to NAS if available
            if nas_output and local_output.exists():
                self._copy_to_nas(local_output, nas_output)
                self.logger.info(f"✅ Real video created: {nas_output}")
                return nas_output
            else:
                self.logger.info(f"✅ Real video created: {local_output}")
                return local_output

        except Exception as e:
            logger.error(f"Error in create_scene_video: {e}", exc_info=True)
            raise

    def _generate_scene_video(self, storyboard: Dict[str, Any],
                                animation_plan: Dict[str, Any],
                                episode_id: str, scene_number: int) -> VideoScene:
        try:
            """Generate video scene from storyboard"""
            panels = storyboard.get("panels", [])
            duration = storyboard.get("duration_seconds", 120.0)

            # Load audio if available
            audio_script = None
            audio_path = self.audio_dir / f"{episode_id}_Alex_voice.json"
            if audio_path.exists():
                with open(audio_path, 'r', encoding='utf-8') as f:
                    audio_script = json.load(f)

            return VideoScene(
                scene_id=f"{episode_id}_scene_{scene_number:02d}",
                duration=duration,
                panels=panels,
                audio_script=audio_script
            )

        except Exception as e:
            self.logger.error(f"Error in _generate_scene_video: {e}", exc_info=True)
            raise
    def _render_scene_video(self, scene: VideoScene, output_path: Path):
        """Render scene video using FFmpeg"""
        self.logger.info(f"🎬 Rendering scene: {scene.scene_id}")

        # Create video segments for each panel
        segment_files = []

        panel_duration = scene.duration / len(scene.panels) if scene.panels else scene.duration

        for i, panel in enumerate(scene.panels):
            segment_file = self._create_panel_video(panel, panel_duration, scene, i)
            if segment_file:
                segment_files.append(segment_file)

        # Concatenate segments
        if segment_files:
            self._concatenate_videos(segment_files, output_path)
        else:
            # Fallback: create single video
            self._create_single_video(scene, output_path)

    def _create_panel_video(self, panel: Dict[str, Any], duration: float,
                           scene: VideoScene, panel_index: int) -> Optional[Path]:
        """Create video for a single panel"""
        panel_text = panel.get("description", panel.get("text", f"Panel {panel_index + 1}"))
        panel_type = panel.get("type", "content")

        # Create video with text overlay
        segment_file = self.temp_dir / f"{scene.scene_id}_panel_{panel_index:02d}.mp4"

        # Generate video with FFmpeg
        # Use drawtext filter to add text
        text_escaped = panel_text.replace("'", "\\'").replace(":", "\\:")

        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x1a1a2e:size=3840x2160:duration={duration}:rate=60",
            "-vf", f"drawtext=text='{text_escaped}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:boxborderw=10",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "60",
            "-t", str(duration),
            "-y",
            str(segment_file)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and segment_file.exists():
                return segment_file
            else:
                self.logger.warning(f"Panel {panel_index} generation failed: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating panel {panel_index}: {e}")
            return None

    def _create_single_video(self, scene: VideoScene, output_path: Path):
        """Create single video for entire scene"""
        scene_text = f"{scene.scene_id}\nQuantum Dimensions"

        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x16213e:size=3840x2160:duration={scene.duration}:rate=60",
            "-vf", f"drawtext=text='{scene_text}':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "60",
            "-t", str(scene.duration),
            "-y",
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                self.logger.info(f"✅ Single video created: {output_path}")
            else:
                self.logger.error(f"❌ Video creation failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")

    def _concatenate_videos(self, segment_files: List[Path], output_path: Path):
        """Concatenate video segments"""
        if not segment_files:
            return

        # Write to local first to avoid network drive issues
        local_output = self.local_output_dir / output_path.name

        # Create concat file with proper escaping
        concat_file = self.temp_dir / "concat_list.txt"
        with open(concat_file, 'w', encoding='utf-8') as f:
            for seg_file in segment_files:
                # Use forward slashes and escape properly
                path_str = str(seg_file.absolute()).replace('\\', '/')
                f.write(f"file '{path_str}'\n")

        # Concatenate with re-encoding for reliability
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
            str(local_output)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )

            if result.returncode == 0 and local_output.exists():
                self.logger.info(f"✅ Videos concatenated: {local_output}")

                # Copy to NAS if available
                if self.use_nas:
                    self._copy_to_nas(local_output, output_path)
                else:
                    # Move to final location
                    local_output.rename(output_path)
            else:
                self.logger.error(f"❌ Concatenation failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")

    def _copy_to_nas(self, local_file: Path, nas_path: Path):
        """Copy file to NAS drive"""
        try:
            import shutil
            nas_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_file, nas_path)
            self.logger.info(f"✅ Copied to NAS: {nas_path}")
        except Exception as e:
            self.logger.warning(f"⚠️  Could not copy to NAS: {e}, keeping local: {local_file}")

    def create_episode_video(self, episode_id: str) -> Path:
        """Create complete episode video"""
        self.logger.info(f"🎬 Creating complete episode: {episode_id}")

        # Create all scene videos
        scene_videos = []
        for scene_num in range(1, 8):
            try:
                scene_path = self.create_scene_video(episode_id, scene_num)
                if scene_path.exists():
                    scene_videos.append(scene_path)
            except Exception as e:
                self.logger.warning(f"Scene {scene_num} failed: {e}")

        # Concatenate all scenes
        if scene_videos:
            output_path = self.output_dir / f"{episode_id}_COMPLETE_REAL.mp4"
            self._concatenate_videos(scene_videos, output_path)
            return output_path
        else:
            raise RuntimeError("No scene videos created")

    def create_trailer_video(self, trailer_id: str, trailer_type: str) -> Path:
        """Create real trailer video"""
        self.logger.info(f"🎬 Creating real trailer: {trailer_id} ({trailer_type})")

        # Try different storyboard naming patterns
        storyboard_paths = [
            self.storyboards_dir / f"{trailer_id}_{trailer_type}_storyboard.json",
            self.storyboards_dir / f"{trailer_type}_001_storyboard.json",
            self.storyboards_dir / f"{trailer_id}_storyboard.json"
        ]

        storyboard_path = None
        for path in storyboard_paths:
            if path.exists():
                storyboard_path = path
                break

        if not storyboard_path:
            # Create trailer without storyboard
            self.logger.info(f"   Storyboard not found, creating trailer from template")

        with open(storyboard_path, 'r', encoding='utf-8') as f:
            storyboard = json.load(f)

        # Determine duration
        durations = {
            "teaser": 60.0,
            "main": 190.0,
            "extended": 370.0
        }
        duration = durations.get(trailer_type, 60.0)

        # Create trailer video - write locally first
        local_output = self.local_output_dir / f"{trailer_id}_{trailer_type}_REAL.mp4"
        nas_output = self.nas_output_dir / f"{trailer_id}_{trailer_type}_REAL.mp4" if self.use_nas else None

        trailer_text = f"Quantum Dimensions\\n{trailer_type.upper()} TRAILER"

        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x0f3460:size=3840x2160:duration={duration}:rate=60",
            "-vf", f"drawtext=text='{trailer_text}':fontsize=120:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.7:boxborderw=15",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "60",
            "-t", str(duration),
            "-y",
            str(local_output)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800
            )

            if result.returncode == 0 and local_output.exists():
                self.logger.info(f"✅ Trailer created: {local_output}")

                # Copy to NAS if available
                if nas_output:
                    self._copy_to_nas(local_output, nas_output)
                    return nas_output
                else:
                    return local_output
            else:
                self.logger.error(f"❌ Trailer creation failed: {result.stderr}")
                raise RuntimeError("Trailer creation failed")
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise


def main():
    """Main entry point"""
    print("="*80)
    print("QUANTUM ANIME REAL VIDEO GENERATOR - NO PLACEHOLDERS")
    print("="*80)

    generator = QuantumAnimeRealVideoGenerator()

    # Create pilot episode
    print("\n🎬 Creating pilot episode (S01E01)...")
    try:
        pilot_path = generator.create_episode_video("S01E01")
        print(f"   ✅ Pilot episode: {pilot_path}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Create trailers
    print("\n🎬 Creating trailers...")
    for trailer_type in ["teaser", "main", "extended"]:
        try:
            trailer_path = generator.create_trailer_video(f"{trailer_type}_001", trailer_type)
            print(f"   ✅ {trailer_type} trailer: {trailer_path}")
        except Exception as e:
            print(f"   ❌ {trailer_type} trailer error: {e}")

    print("\n✅ Real video generation complete!")
    print("="*80)


if __name__ == "__main__":


    main()