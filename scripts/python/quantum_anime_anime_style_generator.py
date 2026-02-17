#!/usr/bin/env python3
"""
Quantum Anime - Japanese Anime Style Generator

Creates anime-style visuals inspired by popular anime:
- Studio Ghibli (soft colors, detailed backgrounds)
- Attack on Titan (dynamic action, dramatic angles)
- Demon Slayer (vibrant colors, fluid motion)
- My Hero Academia (bold, energetic style)

Tags: #PEAK #ANIME #JAPANESE #STYLE @LUMINA @JARVIS
"""

import sys
import subprocess
import tempfile
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

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

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = get_logger("QuantumAnimeAnimeStyleGenerator")


@dataclass
class AnimeStyle:
    """Anime style definition"""
    name: str
    color_palette: List[Tuple[int, int, int]]
    line_style: str  # bold, soft, detailed
    background_style: str  # detailed, simple, gradient
    character_style: str  # realistic, stylized, chibi


class QuantumAnimeAnimeStyleGenerator:
    """
    Japanese Anime Style Generator

    Creates anime-style visuals inspired by popular anime series
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize anime style generator"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("QuantumAnimeAnimeStyleGenerator")

        # Check tools
        self.opencv_available = OPENCV_AVAILABLE
        self.pil_available = PIL_AVAILABLE

        if not self.opencv_available and not self.pil_available:
            raise RuntimeError("No image libraries available")

        # Anime styles inspired by popular series
        self.styles = {
            "ghibli": AnimeStyle(
                name="Studio Ghibli",
                color_palette=[
                    (135, 206, 250),  # Sky blue
                    (255, 228, 196),  # Bisque (warm)
                    (144, 238, 144),  # Light green
                    (255, 218, 185),  # Peach
                    (176, 224, 230),  # Powder blue
                ],
                line_style="soft",
                background_style="detailed",
                character_style="stylized"
            ),
            "demon_slayer": AnimeStyle(
                name="Demon Slayer",
                color_palette=[
                    (255, 20, 147),   # Deep pink
                    (0, 191, 255),    # Deep sky blue
                    (255, 140, 0),    # Dark orange
                    (138, 43, 226),   # Blue violet
                    (255, 215, 0),    # Gold
                ],
                line_style="bold",
                background_style="vibrant",
                character_style="realistic"
            ),
            "my_hero": AnimeStyle(
                name="My Hero Academia",
                color_palette=[
                    (30, 144, 255),   # Dodger blue
                    (255, 69, 0),     # Red orange
                    (50, 205, 50),    # Lime green
                    (255, 20, 147),   # Deep pink
                    (255, 215, 0),    # Gold
                ],
                line_style="bold",
                background_style="energetic",
                character_style="stylized"
            )
        }

        # Default style
        self.current_style = self.styles["ghibli"]

        # Output directory
        self.output_dir = self.project_root / "data" / "quantum_anime" / "animations_anime_style"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Temp directory
        self.temp_dir = Path(tempfile.gettempdir()) / "quantum_anime_anime_frames"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Check FFmpeg
        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg is required")

        self.logger.info(f"✅ Anime style generator initialized ({self.current_style.name} style)")

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

    def create_anime_frame(self, frame_num: int, timestamp: float, 
                           width: int, height: int, 
                           title: str = "", subtitle: str = "",
                           style_name: str = "ghibli") -> Any:
        """Create a single anime-style frame"""
        self.current_style = self.styles.get(style_name, self.styles["ghibli"])

        if self.opencv_available:
            return self._create_anime_frame_opencv(frame_num, timestamp, width, height, title, subtitle)
        else:
            return self._create_anime_frame_pil(frame_num, timestamp, width, height, title, subtitle)

    def _create_anime_frame_opencv(self, frame_num: int, timestamp: float,
                                   width: int, height: int,
                                   title: str, subtitle: str) -> np.ndarray:
        """Create anime frame using OpenCV"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Anime-style background (Ghibli-inspired sky gradient)
        for y in range(height):
            # Sky gradient - soft blue to warm colors
            sky_ratio = y / height
            if sky_ratio < 0.6:  # Sky
                r = int(135 + 20 * math.sin(timestamp * 0.3 + sky_ratio * 2))
                g = int(206 + 30 * math.sin(timestamp * 0.2 + sky_ratio * 1.5))
                b = int(250 + 10 * math.sin(timestamp * 0.4))
            else:  # Ground/horizon
                r = int(144 + 50 * math.sin(timestamp * 0.2))
                g = int(238 + 20 * math.sin(timestamp * 0.3))
                b = int(144 + 30 * math.sin(timestamp * 0.25))

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            frame[y, :] = [b, g, r]  # BGR for OpenCV

        # Anime-style clouds (soft, fluffy)
        for i in range(5):
            cloud_x = int((i * 200 + timestamp * 30) % width)
            cloud_y = int(height * 0.2 + 50 * math.sin(timestamp * 0.5 + i))
            cloud_size = int(80 + 20 * math.sin(timestamp * 0.3 + i))

            # Draw soft cloud (multiple circles)
            for offset_x in range(-cloud_size, cloud_size, 20):
                for offset_y in range(-cloud_size//2, cloud_size//2, 20):
                    x = cloud_x + offset_x
                    y = cloud_y + offset_y
                    if 0 <= x < width and 0 <= y < height:
                        dist = math.sqrt(offset_x**2 + offset_y**2)
                        if dist < cloud_size:
                            intensity = int(255 - (dist / cloud_size) * 100)
                            cv2.circle(frame, (x, y), 15, (intensity, intensity, intensity), -1)

        # Anime-style character (simplified but stylized)
        char_x = int(width * 0.3 + 30 * math.sin(timestamp * 1.2))
        char_y = int(height * 0.7)
        char_size = 100

        # Character body (anime style - simple shapes)
        # Head
        cv2.circle(frame, (char_x, char_y - char_size), char_size//2, (255, 220, 177), -1)
        cv2.circle(frame, (char_x, char_y - char_size), char_size//2, (0, 0, 0), 3)

        # Eyes (anime-style large eyes)
        eye_size = 15
        cv2.circle(frame, (char_x - 20, char_y - char_size - 10), eye_size, (255, 255, 255), -1)
        cv2.circle(frame, (char_x + 20, char_y - char_size - 10), eye_size, (255, 255, 255), -1)
        cv2.circle(frame, (char_x - 20, char_y - char_size - 10), eye_size//2, (0, 0, 0), -1)
        cv2.circle(frame, (char_x + 20, char_y - char_size - 10), eye_size//2, (0, 0, 0), -1)

        # Body
        cv2.ellipse(frame, (char_x, char_y), (char_size//3, char_size), 0, 0, 360, (100, 150, 255), -1)
        cv2.ellipse(frame, (char_x, char_y), (char_size//3, char_size), 0, 0, 360, (0, 0, 0), 2)

        # Anime-style particles/effects
        for i in range(20):
            particle_x = int(char_x + 150 * math.cos(timestamp * 2 + i))
            particle_y = int(char_y - 50 + 100 * math.sin(timestamp * 2 + i))
            particle_color = self.current_style.color_palette[i % len(self.current_style.color_palette)]
            cv2.circle(frame, (particle_x, particle_y), 5, particle_color, -1)

        # Anime-style title text (with outline for readability)
        if title:
            font_scale = 2.5
            thickness = 4
            text_x = int(width / 2)
            text_y = int(height * 0.15)

            # Text outline (black)
            for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]:
                cv2.putText(frame, title, (text_x + dx, text_y + dy),
                          cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

            # Text (white)
            cv2.putText(frame, title, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        # Subtitle (bottom of screen, anime-style)
        if subtitle:
            font_scale = 1.2
            thickness = 2
            text_x = int(width / 2)
            text_y = int(height * 0.9)

            # Subtitle background box (semi-transparent)
            text_size = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            box_x1 = text_x - text_size[0]//2 - 20
            box_x2 = text_x + text_size[0]//2 + 20
            box_y1 = text_y - text_size[1] - 10
            box_y2 = text_y + 10

            overlay = frame.copy()
            cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            # Subtitle text (white with outline)
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                cv2.putText(frame, subtitle, (text_x + dx, text_y + dy),
                          cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
            cv2.putText(frame, subtitle, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        return frame

    def _create_anime_frame_pil(self, frame_num: int, timestamp: float,
                                width: int, height: int,
                                title: str, subtitle: str) -> Image.Image:
        """Create anime frame using PIL"""
        img = Image.new('RGB', (width, height), color=(135, 206, 250))
        draw = ImageDraw.Draw(img)

        # Similar logic but using PIL
        # (Simplified version - full implementation would mirror OpenCV version)

        return img

    def create_anime_scene(self, scene_id: str, duration: float, fps: int = 60,
                           resolution: Tuple[int, int] = (1920, 1080),
                           title: str = "", subtitles: List[Tuple[float, str]] = None,
                           style: str = "ghibli") -> Path:
        """Create full anime-style scene"""
        self.logger.info(f"🎨 Creating anime-style scene: {scene_id} ({style} style)")

        total_frames = int(duration * fps)
        width, height = resolution

        # Generate frames
        frames = []
        for frame_num in range(total_frames):
            timestamp = frame_num / fps

            # Find current subtitle
            current_subtitle = ""
            if subtitles:
                for sub_time, sub_text in subtitles:
                    if sub_time <= timestamp < sub_time + 3.0:  # Show subtitle for 3 seconds
                        current_subtitle = sub_text
                        break

            frame = self.create_anime_frame(frame_num, timestamp, width, height,
                                          title, current_subtitle, style)
            frames.append(frame)

            if (frame_num + 1) % 60 == 0:
                self.logger.info(f"   Generated {frame_num + 1}/{total_frames} frames...")

        # Render to video
        output_path = self.output_dir / f"{scene_id}_ANIME_STYLE.mp4"
        self._render_frames_to_video(frames, output_path, fps, resolution)

        self.logger.info(f"✅ Anime-style scene created: {output_path}")
        return output_path

    def _render_frames_to_video(self, frames: List[Any], output_path: Path,
                                fps: int, resolution: Tuple[int, int]):
        """Render frames to video"""
        self.logger.info(f"   Rendering {len(frames)} frames to video...")

        # Save frames
        frame_dir = self.temp_dir / f"frames_{frames[0].frame_number if hasattr(frames[0], 'frame_number') else 0}"
        frame_dir.mkdir(parents=True, exist_ok=True)

        for i, frame in enumerate(frames):
            frame_path = frame_dir / f"frame_{i:06d}.png"

            if isinstance(frame, np.ndarray):
                cv2.imwrite(str(frame_path), frame)
            elif isinstance(frame, Image.Image):
                frame.save(frame_path)

        # Render with FFmpeg
        width, height = resolution
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", str(frame_dir / "frame_%06d.png"),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )

            if result.returncode == 0 and output_path.exists():
                self.logger.info(f"   ✅ Video rendered: {output_path}")
            else:
                self.logger.error(f"   ❌ Rendering failed: {result.stderr[:500]}")
        except Exception as e:
            self.logger.error(f"   ❌ Error: {e}")


def main():
    try:
        """Test anime style generator"""
        print("="*80)
        print("QUANTUM ANIME - JAPANESE ANIME STYLE GENERATOR")
        print("="*80)

        generator = QuantumAnimeAnimeStyleGenerator()

        # Test scene with subtitles
        subtitles = [
            (0.0, "Welcome to Quantum Dimensions"),
            (3.0, "Let's explore the universe together"),
            (6.0, "Every dimension tells a story"),
        ]

        scene = generator.create_anime_scene(
            scene_id="test_anime_001",
            duration=10.0,
            fps=60,
            resolution=(1920, 1080),
            title="Quantum Dimensions",
            subtitles=subtitles,
            style="ghibli"
        )

        if scene.exists():
            size_mb = scene.stat().st_size / 1024 / 1024
            print(f"\n✅ Anime-style scene created!")
            print(f"   📁 Location: {scene}")
            print(f"   📊 Size: {size_mb:.1f} MB")
            print(f"   🎨 Style: Studio Ghibli inspired")
        else:
            print("\n❌ Scene creation failed")

        print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()