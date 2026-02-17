#!/usr/bin/env python3
"""
LUMINA Real Elevator Pitch - An ACTUAL Pitch, Not Word Salad

Creates a compelling 60-90 second elevator pitch that:
- Tells a STORY (problem → solution → vision)
- Has conversational flow
- Uses AI-generated imagery for visual interest
- Sounds like you're actually talking to someone
- Has a narrative arc that hooks and delivers

NOT just short phrases flashing on screen!
"""

import subprocess
import asyncio
import json
import os
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ElevatorPitch")


# =============================================================================
# THE ACTUAL ELEVATOR PITCH SCRIPT
# =============================================================================
# This is written as if you're ACTUALLY talking to someone in an elevator

ELEVATOR_PITCH_SCRIPT = """
You know what I realized the other day?

Every single one of us has opinions. Perspectives. Ideas worth sharing.

But here's the thing - in this age of AI and algorithms, individual human voices are getting drowned out.

That's why I built LUMINA.

Think of it as... a platform that amplifies human perspectives. Not replaces them. Amplifies them.

See, most AI systems try to give you THE answer. One answer. The "optimal" response.

But that's not how the real world works, is it?

In the real world, your perspective matters. My perspective matters. Every individual's unique take on things - that's what makes us human.

LUMINA captures that. It illuminates individual perspectives and shares them with the world.

Because here's what I believe: for whatever your opinion is worth - which is everything - it deserves to be heard.

We're not leaving anyone behind.

So that's LUMINA. Illuminating the world, one perspective at a time.

Want to join us?
"""

# Break into natural speech segments with scene descriptions
PITCH_SCENES = [
    {
        "text": "You know what I realized the other day?",
        "visual": "Person in contemplative moment, city skyline, golden hour",
        "mood": "reflective",
        "duration": 3.5
    },
    {
        "text": "Every single one of us has opinions. Perspectives. Ideas worth sharing.",
        "visual": "Diverse crowd of people, each with unique expressions, connected by light threads",
        "mood": "hopeful",
        "duration": 4.5
    },
    {
        "text": "But here's the thing - in this age of AI and algorithms, individual human voices are getting drowned out.",
        "visual": "Person's face being fragmented/pixelated by digital noise, overwhelmed",
        "mood": "concern",
        "duration": 5.0
    },
    {
        "text": "That's why I built LUMINA.",
        "visual": "LUMINA logo emerging from darkness with soft glow",
        "mood": "reveal",
        "duration": 3.0
    },
    {
        "text": "Think of it as a platform that amplifies human perspectives. Not replaces them. Amplifies them.",
        "visual": "Sound waves transforming into light beams, megaphone becoming lighthouse",
        "mood": "explanation",
        "duration": 5.5
    },
    {
        "text": "See, most AI systems try to give you THE answer. One answer. The optimal response.",
        "visual": "Robot giving single robotic answer, cold blue light, sterile",
        "mood": "contrast",
        "duration": 4.5
    },
    {
        "text": "But that's not how the real world works, is it?",
        "visual": "Question mark dissolving into multiple colorful perspectives",
        "mood": "challenge",
        "duration": 3.0
    },
    {
        "text": "In the real world, your perspective matters. My perspective matters. Every individual's unique take on things - that's what makes us human.",
        "visual": "Kaleidoscope of human faces, each with different colors/lights emanating",
        "mood": "warmth",
        "duration": 6.0
    },
    {
        "text": "LUMINA captures that. It illuminates individual perspectives and shares them with the world.",
        "visual": "Lighthouse beam scanning across globe, lighting up individual points",
        "mood": "inspiration",
        "duration": 5.0
    },
    {
        "text": "Because here's what I believe: for whatever your opinion is worth - which is everything - it deserves to be heard.",
        "visual": "Single candle becoming bonfire of diverse flames",
        "mood": "conviction",
        "duration": 5.5
    },
    {
        "text": "We're not leaving anyone behind.",
        "visual": "Hands reaching out, connecting across divides",
        "mood": "inclusive",
        "duration": 3.0
    },
    {
        "text": "So that's LUMINA. Illuminating the world, one perspective at a time.",
        "visual": "LUMINA logo with tagline, warm golden glow",
        "mood": "conclusion",
        "duration": 4.0
    },
    {
        "text": "Want to join us?",
        "visual": "Open door with light streaming through, invitation",
        "mood": "call_to_action",
        "duration": 3.5
    }
]


class RealElevatorPitchGenerator:
    """Generate an actual elevator pitch video"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output" / "videos" / "pitch"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = self.project_root / "output" / "videos" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.audio_dir = self.temp_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.images_dir = self.project_root / "output" / "videos" / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Video settings
        self.width = 1920
        self.height = 1080
        self.fps = 30

        # Check capabilities
        self.ffmpeg_available = self._check_ffmpeg()
        self.tts_available = self._check_tts()
        self.openai_available = self._check_openai()

        logger.info("🎬 Real Elevator Pitch Generator")
        logger.info(f"   FFmpeg: {'✅' if self.ffmpeg_available else '❌'}")
        logger.info(f"   TTS: {'✅' if self.tts_available else '❌'}")
        logger.info(f"   OpenAI (images): {'✅' if self.openai_available else '❌'}")

    def _check_ffmpeg(self) -> bool:
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _check_tts(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def _check_openai(self) -> bool:
        """Check if OpenAI API is available for image generation"""
        api_key = os.environ.get("OPENAI_API_KEY")
        return api_key is not None and len(api_key) > 20

    async def _generate_voiceover_async(self, text: str, output_file: Path,
                                        voice: str = "en-US-GuyNeural") -> bool:
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_file))
            return output_file.exists()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False

    def generate_voiceover(self, text: str, output_file: Path,
                          voice: str = "en-US-GuyNeural") -> bool:
        return asyncio.run(self._generate_voiceover_async(text, output_file, voice))

    def get_audio_duration(self, audio_file: Path) -> float:
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 4.0

    def generate_image_dalle(self, prompt: str, output_file: Path) -> bool:
        """Generate image using DALL-E 3"""
        if not self.openai_available:
            return False

        try:
            import openai

            client = openai.OpenAI()

            # Enhance prompt for cinematic quality
            enhanced_prompt = (
                f"Cinematic, high quality, 16:9 aspect ratio, professional lighting, "
                f"moody atmospheric scene: {prompt}. "
                f"Style: modern, minimalist, warm tones, subtle glow effects."
            )

            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download image
            urllib.request.urlretrieve(image_url, str(output_file))

            logger.info(f"   🖼️ Generated image: {output_file.name}")
            return True

        except Exception as e:
            logger.warning(f"   ⚠️ DALL-E generation failed: {e}")
            return False

    def create_placeholder_image(self, mood: str, output_file: Path) -> bool:
        try:
            """Create a placeholder gradient image based on mood"""

            mood_colors = {
                "reflective": ("0x1a1a3a", "0x2a2a4a"),
                "hopeful": ("0x1a2a3a", "0x2a4a5a"),
                "concern": ("0x2a1a1a", "0x3a2a2a"),
                "reveal": ("0x0a0a2a", "0x1a1a4a"),
                "explanation": ("0x1a2a2a", "0x2a4a4a"),
                "contrast": ("0x1a1a2a", "0x2a2a3a"),
                "challenge": ("0x2a2a1a", "0x4a4a2a"),
                "warmth": ("0x2a1a0a", "0x4a3a2a"),
                "inspiration": ("0x1a1a2a", "0x3a3a5a"),
                "conviction": ("0x2a1a1a", "0x4a2a2a"),
                "inclusive": ("0x1a2a1a", "0x2a4a2a"),
                "conclusion": ("0x1a1a1a", "0x3a3a4a"),
                "call_to_action": ("0x2a2a3a", "0x4a4a5a")
            }

            colors = mood_colors.get(mood, ("0x1a1a2a", "0x2a2a3a"))

            # Create gradient using FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c={colors[0]}:s={self.width}x{self.height}:d=1',
                '-vf', (
                    f"geq=r='clip(p(X,Y,0)+{int(colors[1][2:4], 16)-int(colors[0][2:4], 16)}*Y/{self.height},0,255)':"
                    f"g='clip(p(X,Y,1)+{int(colors[1][4:6], 16)-int(colors[0][4:6], 16)}*Y/{self.height},0,255)':"
                    f"b='clip(p(X,Y,2)+{int(colors[1][6:8], 16)-int(colors[0][6:8], 16)}*Y/{self.height},0,255)'"
                ),
                '-frames:v', '1',
                str(output_file)
            ]

            # Simpler fallback
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c={colors[0]}:s={self.width}x{self.height}:d=1',
                '-frames:v', '1',
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return output_file.exists()

        except Exception as e:
            logger.error(f"Error in create_placeholder_image: {e}", exc_info=True)
            raise

    def create_scene(self, scene: Dict, scene_num: int,
                        voice: str = "en-US-GuyNeural",
                        use_ai_images: bool = True) -> Optional[Dict]:
        try:
            """Create a single scene with voiceover and visuals"""

            scene_id = f"pitch_{scene_num}_{int(time.time() * 1000)}"
            audio_file = self.audio_dir / f"{scene_id}.mp3"
            image_file = self.images_dir / f"{scene_id}.png"
            video_file = self.temp_dir / f"{scene_id}.mp4"

            text = scene["text"]
            visual = scene["visual"]
            mood = scene["mood"]

            logger.info(f"📝 Scene {scene_num}: \"{text[:50]}...\"")

            # Generate voiceover
            if self.tts_available:
                success = self.generate_voiceover(text, audio_file, voice)
                if success:
                    duration = self.get_audio_duration(audio_file) + 0.8  # Pause after speech
                else:
                    duration = scene.get("duration", 4.0)
                    audio_file = None
            else:
                duration = scene.get("duration", 4.0)
                audio_file = None

            # Generate or create image
            if use_ai_images and self.openai_available:
                if not self.generate_image_dalle(visual, image_file):
                    self.create_placeholder_image(mood, image_file)
            else:
                self.create_placeholder_image(mood, image_file)

            # Create video from image + audio with Ken Burns effect
            safe_text = (text.replace("\\", "\\\\\\\\")
                            .replace("'", "")
                            .replace(":", "\\:")
                            .replace("%", "\\%")
                            .replace('"', ""))

            # Ken Burns effect (subtle zoom) + text overlay
            if image_file.exists():
                # Use image as background with zoom
                vf = (
                    f"scale=2048:-1,"  # Scale up for zoom headroom
                    f"zoompan=z='1.05+0.03*in/{duration}/{self.fps}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                    f"d={int(duration*self.fps)}:s={self.width}x{self.height}:fps={self.fps},"
                    # Subtle vignette
                    f"vignette=PI/4,"
                    # Text overlay at bottom with box
                    f"drawbox=x=0:y={self.height-180}:w={self.width}:h=180:color=black@0.6:t=fill,"
                    # Subtitle text
                    f"drawtext=text='{safe_text}':"
                    f"fontsize=36:fontcolor=white:"
                    f"x=(w-text_w)/2:y={self.height-120}:"
                    f"font=Arial:"
                    f"shadowcolor=black@0.8:shadowx=2:shadowy=2"
                )
            else:
                # Fallback: color background
                vf = (
                    f"drawtext=text='{safe_text}':"
                    f"fontsize=42:fontcolor=white:"
                    f"x=(w-text_w)/2:y=(h-text_h)/2:"
                    f"font=Arial:"
                    f"shadowcolor=black:shadowx=2:shadowy=2,"
                    f"fade=in:0:15,fade=out:{int((duration-0.5)*self.fps)}:15"
                )

            if audio_file and audio_file.exists() and image_file.exists():
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', str(image_file),
                    '-i', str(audio_file),
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    str(video_file)
                ]
            elif image_file.exists():
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', str(image_file),
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]
            else:
                # Pure color background
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=0x1a1a2a:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-i', str(audio_file) if audio_file and audio_file.exists() else '',
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]
                if not (audio_file and audio_file.exists()):
                    cmd = [c for c in cmd if c]  # Remove empty strings

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                logger.warning(f"   ⚠️ Scene creation had issues, trying simpler approach")
                # Simpler fallback
                simple_vf = (
                    f"drawtext=text='{safe_text}':"
                    f"fontsize=40:fontcolor=white:"
                    f"x=(w-text_w)/2:y=(h-text_h)/2:"
                    f"font=Arial:shadowcolor=black:shadowx=2:shadowy=2"
                )
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=0x1a1a2a:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-vf', simple_vf,
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]
                if audio_file and audio_file.exists():
                    cmd.insert(4, '-i')
                    cmd.insert(5, str(audio_file))
                    cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-shortest'])

                subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if not video_file.exists():
                return None

            return {
                "video_file": video_file,
                "audio_file": audio_file,
                "duration": duration,
                "text": text
            }

        except Exception as e:
            self.logger.error(f"Error in create_scene: {e}", exc_info=True)
            raise
    def generate_pitch_video(self, 
                            voice: str = "en-US-GuyNeural",
                            use_ai_images: bool = False) -> Dict[str, Any]:
        """Generate the complete elevator pitch video"""

        logger.info("🎬 Generating REAL Elevator Pitch Video")
        logger.info(f"   Voice: {voice}")
        logger.info(f"   AI Images: {'Yes' if use_ai_images and self.openai_available else 'No'}")
        logger.info(f"   Scenes: {len(PITCH_SCENES)}")

        output_filename = f"LUMINA_Elevator_Pitch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path = self.output_dir / output_filename

        try:
            scenes = []

            # Create each scene
            for i, scene in enumerate(PITCH_SCENES):
                result = self.create_scene(scene, i+1, voice, use_ai_images)
                if result:
                    scenes.append(result)

            if not scenes:
                return {"error": "No scenes created"}

            # Concatenate all scenes
            logger.info("🔗 Assembling final video...")

            concat_file = self.temp_dir / f"concat_{int(time.time())}.txt"
            with open(concat_file, 'w') as f:
                for scene in scenes:
                    f.write(f"file '{scene['video_file']}'\n")

            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-c:a', 'aac', '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Cleanup temp files
            for scene in scenes:
                try:
                    if scene.get("video_file"):
                        Path(scene["video_file"]).unlink()
                except:
                    pass

            if not output_path.exists():
                return {"error": "Final video not created"}

            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            total_duration = sum(s.get("duration", 0) for s in scenes)

            logger.info(f"✅ Elevator Pitch Video Created!")
            logger.info(f"   📁 {output_path}")
            logger.info(f"   📊 Size: {file_size_mb:.2f} MB")
            logger.info(f"   ⏱️  Duration: {total_duration:.1f}s")

            return {
                "success": True,
                "output_file": str(output_path),
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": total_duration,
                "scenes": len(scenes),
                "has_ai_images": use_ai_images and self.openai_available
            }

        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


def main():
    print("="*70)
    print("🎬 LUMINA REAL ELEVATOR PITCH")
    print("   An actual pitch, not word salad!")
    print("="*70)
    print()
    print("📜 THE PITCH:")
    print("-"*70)
    for scene in PITCH_SCENES:
        print(f"  💬 \"{scene['text']}\"")
        print(f"     🖼️  Visual: {scene['visual'][:50]}...")
        print()
    print("-"*70)
    print()

    generator = RealElevatorPitchGenerator()

    # Check for OpenAI API key
    use_ai_images = generator.openai_available
    if use_ai_images:
        print("✅ DALL-E available - will generate AI images!")
    else:
        print("⚠️ No OPENAI_API_KEY - using placeholder backgrounds")
        print("   Set OPENAI_API_KEY env var for AI-generated visuals")

    print()
    print("🎬 Generating video...")

    result = generator.generate_pitch_video(
        voice="en-US-GuyNeural",  # Professional male voice
        use_ai_images=use_ai_images
    )

    print()
    print("="*70)
    if result.get("success"):
        print("✅ ELEVATOR PITCH COMPLETE!")
        print(f"   📁 {result['output_file']}")
        print(f"   📊 {result['file_size_mb']:.2f} MB")
        print(f"   ⏱️  {result['duration_seconds']:.1f} seconds")
        print(f"   🖼️  AI Images: {'Yes' if result.get('has_ai_images') else 'No'}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    print("="*70)


if __name__ == "__main__":



    main()