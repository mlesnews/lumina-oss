#!/usr/bin/env python3
"""
LUMINA Holocron Video Generator - Creates REAL Videos

Generates proper Holocron videos with:
- Multiple scenes with transitions
- Background visuals
- Text overlays with animations
- Audio (TTS voiceover or music)

Uses FFmpeg for video generation.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import time
import tempfile
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HolocronVideoGenerator")


class HolocronVideoGenerator:
    """
    Generate proper Holocron videos with content, not just title cards
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output" / "videos" / "holocron"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = self.project_root / "output" / "videos" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Video settings
        self.width = 1920
        self.height = 1080
        self.fps = 30

        # Check FFmpeg
        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            logger.error("❌ FFmpeg not available!")

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _create_scene_clip(self, text: str, duration: float, 
                          bg_color: str = "0x1a1a2e",
                          text_color: str = "white",
                          fontsize: int = 48,
                          output_file: Path = None) -> Path:
        """
        Create a single scene clip with text overlay
        """
        try:
            if output_file is None:
                output_file = self.temp_dir / f"scene_{int(time.time() * 1000)}.mp4"

            # Escape special characters in text for FFmpeg
            safe_text = text.replace("'", "'\\''").replace(":", "\\:")

            cmd = [
                'ffmpeg',
                '-y',  # Overwrite
                '-f', 'lavfi',
                '-i', f'color=c={bg_color}:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                '-vf', (
                    f"drawtext=text='{safe_text}':"
                    f"fontsize={fontsize}:"
                    f"fontcolor={text_color}:"
                    f"x=(w-text_w)/2:"
                    f"y=(h-text_h)/2:"
                    f"font=Arial:"
                    f"shadowcolor=black:"
                    f"shadowx=2:"
                    f"shadowy=2,"
                    f"fade=t=in:st=0:d=0.5,"
                    f"fade=t=out:st={duration-0.5}:d=0.5"
                ),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-pix_fmt', 'yuv420p',
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr[:500]}")
                raise Exception(f"Failed to create scene: {result.stderr[:200]}")

            return output_file

        except Exception as e:
            logger.error(f"Error in _create_scene_clip: {e}", exc_info=True)
            raise

    def _create_title_scene(self, title: str, subtitle: str = "", 
                            duration: float = 5.0) -> Path:
        """Create title scene with large text"""
        try:
            output_file = self.temp_dir / f"title_{int(time.time() * 1000)}.mp4"

            safe_title = title.replace("'", "'\\''").replace(":", "\\:")
            safe_subtitle = subtitle.replace("'", "'\\''").replace(":", "\\:")

            # Create title with gradient background effect
            vf_filter = (
                f"drawtext=text='{safe_title}':"
                f"fontsize=72:"
                f"fontcolor=white:"
                f"x=(w-text_w)/2:"
                f"y=(h/2-50):"
                f"font=Arial:"
                f"shadowcolor=black:"
                f"shadowx=3:"
                f"shadowy=3"
            )

            if subtitle:
                vf_filter += (
                    f",drawtext=text='{safe_subtitle}':"
                    f"fontsize=36:"
                    f"fontcolor=0xcccccc:"
                    f"x=(w-text_w)/2:"
                    f"y=(h/2+50):"
                    f"font=Arial"
                )

            vf_filter += f",fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1"

            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'lavfi',
                '-i', f'color=c=0x0f0f23:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                '-vf', vf_filter,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-pix_fmt', 'yuv420p',
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                raise Exception(f"Failed to create title: {result.stderr[:200]}")

            return output_file

        except Exception as e:
            logger.error(f"Error in _create_title_scene: {e}", exc_info=True)
            raise

    def _concatenate_clips(self, clips: List[Path], output_file: Path) -> Path:
        """Concatenate multiple clips into final video"""
        try:
            # Create concat file
            concat_file = self.temp_dir / f"concat_{int(time.time())}.txt"
            with open(concat_file, 'w') as f:
                for clip in clips:
                    f.write(f"file '{clip}'\n")

            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                raise Exception(f"Failed to concatenate: {result.stderr[:200]}")

            return output_file

        except Exception as e:
            logger.error(f"Error in _concatenate_clips: {e}", exc_info=True)
            raise
    def generate_holocron_video(self, 
                                title: str,
                                script_segments: List[str],
                                subtitle: str = "LUMINA Holocron Archive",
                                duration_per_segment: float = 4.0,
                                output_filename: str = None) -> Dict[str, Any]:
        """
        Generate a proper Holocron video with multiple scenes

        Args:
            title: Video title
            script_segments: List of text segments to display
            subtitle: Subtitle for title screen
            duration_per_segment: Seconds per text segment
            output_filename: Output filename

        Returns:
            Video metadata dict
        """
        logger.info(f"🎬 Generating Holocron Video: {title}")

        if not self.ffmpeg_available:
            return {"error": "FFmpeg not available"}

        if output_filename is None:
            safe_title = "".join(c for c in title if c.isalnum() or c in ' -_').strip()
            output_filename = f"HOLOCRON_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        output_path = self.output_dir / output_filename

        try:
            clips = []

            # Create title scene
            logger.info("   📝 Creating title scene...")
            title_clip = self._create_title_scene(title, subtitle, duration=5.0)
            clips.append(title_clip)

            # Create content scenes with alternating colors
            colors = ["0x1a1a2e", "0x16213e", "0x1a1a2e", "0x0f3460"]

            for i, segment in enumerate(script_segments):
                logger.info(f"   📝 Creating scene {i+1}/{len(script_segments)}...")
                bg_color = colors[i % len(colors)]

                scene_clip = self._create_scene_clip(
                    text=segment,
                    duration=duration_per_segment,
                    bg_color=bg_color,
                    fontsize=42
                )
                clips.append(scene_clip)

            # Create end scene
            logger.info("   📝 Creating end scene...")
            end_clip = self._create_title_scene(
                "LUMINA", 
                "Knowledge Power Granted ⚡",
                duration=3.0
            )
            clips.append(end_clip)

            # Concatenate all clips
            logger.info("   🔗 Concatenating clips...")
            self._concatenate_clips(clips, output_path)

            # Get file size
            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            # Cleanup temp files
            for clip in clips:
                try:
                    clip.unlink()
                except:
                    pass

            # Calculate total duration
            total_duration = 5.0 + (len(script_segments) * duration_per_segment) + 3.0

            logger.info(f"✅ Video created: {output_path}")
            logger.info(f"   📊 Size: {file_size_mb:.2f} MB")
            logger.info(f"   ⏱️  Duration: {total_duration:.1f} seconds")

            return {
                "success": True,
                "output_file": str(output_path),
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": total_duration,
                "segments": len(script_segments),
                "title": title,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            return {"error": str(e)}

    def generate_lumina_trailers(self) -> List[Dict[str, Any]]:
        """Generate all LUMINA trailer videos properly"""
        logger.info("🎬 Generating LUMINA Holocron Trailers...")

        trailers = [
            {
                "title": "LUMINA - Main Trailer",
                "subtitle": "Illuminate the World",
                "segments": [
                    "Welcome to LUMINA",
                    "What is LUMINA?",
                    "Personal human opinion",
                    "plus individual perspective",
                    "For whatever it's worth",
                    "which is EVERYTHING",
                    "We illuminate the global public",
                    "We share knowledge",
                    "We share perspectives", 
                    "We share insights",
                    "Every being matters",
                    "We leave no one behind",
                    "This is LUMINA",
                    "This is our mission",
                    "Join us"
                ]
            },
            {
                "title": "LUMINA - Elevator Pitch",
                "subtitle": "30 Second Overview",
                "segments": [
                    "What is LUMINA?",
                    "Personal human opinion",
                    "Individual perspective",
                    "For whatever it's worth",
                    "Which is EVERYTHING",
                    "We illuminate",
                    "We share",
                    "We matter",
                    "That is LUMINA"
                ]
            },
            {
                "title": "LUMINA - Mission Trailer",
                "subtitle": "Our Purpose",
                "segments": [
                    "Our Mission",
                    "Illuminate the global public",
                    "Share knowledge",
                    "Share perspectives",
                    "Share insights",
                    "Every being matters",
                    "No one left behind",
                    "That is our mission",
                    "That is LUMINA"
                ]
            },
            {
                "title": "LUMINA - Personal Journey",
                "subtitle": "How I Embraced AI in My Fifties",
                "segments": [
                    "How I decided in my fifties",
                    "to chill and embrace AI",
                    "Life's too short to fight change",
                    "Too short to resist what's coming",
                    "So I embraced it",
                    "I learned",
                    "I adapted",
                    "I decided to work WITH AI",
                    "not against it",
                    "Personal human opinion",
                    "Individual perspective",
                    "For whatever it's worth",
                    "Which is EVERYTHING",
                    "That is LUMINA"
                ]
            }
        ]

        results = []

        for trailer in trailers:
            result = self.generate_holocron_video(
                title=trailer["title"],
                script_segments=trailer["segments"],
                subtitle=trailer["subtitle"],
                duration_per_segment=2.5
            )
            results.append(result)

            if result.get("success"):
                logger.info(f"✅ {trailer['title']} - {result.get('file_size_mb', 0):.2f} MB")
            else:
                logger.error(f"❌ {trailer['title']} - {result.get('error', 'Unknown error')}")

        return results


def main():
    """Generate Holocron videos"""
    print("="*80)
    print("🎬 LUMINA Holocron Video Generator")
    print("="*80)

    generator = HolocronVideoGenerator()

    if not generator.ffmpeg_available:
        print("❌ FFmpeg not available. Cannot generate videos.")
        return

    print("\n🎬 Generating LUMINA Holocron Trailers...\n")

    results = generator.generate_lumina_trailers()

    print("\n" + "="*80)
    print("📊 GENERATION COMPLETE")
    print("="*80)

    total_size = 0
    for result in results:
        if result.get("success"):
            print(f"✅ {result.get('title')}")
            print(f"   📁 {result.get('output_file')}")
            print(f"   📊 {result.get('file_size_mb', 0):.2f} MB | {result.get('duration_seconds', 0):.1f}s")
            total_size += result.get('file_size_bytes', 0)
        else:
            print(f"❌ Failed: {result.get('error')}")

    print(f"\n📊 Total size: {total_size / (1024*1024):.2f} MB")
    print("="*80)


if __name__ == "__main__":



    main()