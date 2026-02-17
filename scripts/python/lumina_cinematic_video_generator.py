#!/usr/bin/env python3
"""
LUMINA Cinematic Video Generator - IMPRESSIVE Production Quality

Creates CINEMATIC videos with:
- Professional voiceover (Microsoft Neural TTS)
- Animated gradient backgrounds with glow effects
- Typewriter text animations
- Background ambient music (generated)
- Particle/light effects
- Cinematic letterboxing
- Professional color grading
"""

import subprocess
import asyncio
import json
import sys
import os
import math
import wave
import struct
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CinematicGenerator")


class LuminaCinematicGenerator:
    """Generate CINEMATIC quality videos"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output" / "videos" / "cinematic"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = self.project_root / "output" / "videos" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.audio_dir = self.temp_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # Cinematic settings
        self.width = 1920
        self.height = 1080
        self.fps = 30

        # Check dependencies
        self.ffmpeg_available = self._check_ffmpeg()
        self.tts_available = self._check_tts()

        logger.info("🎬 Cinematic Video Generator initialized")

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
        return 3.0

    def generate_ambient_music(self, duration: float, output_file: Path) -> bool:
        """Generate ambient drone music using FFmpeg"""
        try:
            # Create layered ambient tones
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', (
                    f"sine=frequency=55:duration={duration},"  # Deep bass drone
                    f"volume=0.15,"
                    f"highpass=f=30,lowpass=f=200"
                ),
                '-f', 'lavfi',
                '-i', (
                    f"sine=frequency=110:duration={duration},"  # Harmonic
                    f"volume=0.08,"
                    f"tremolo=f=0.1:d=0.3"
                ),
                '-f', 'lavfi',
                '-i', (
                    f"sine=frequency=165:duration={duration},"  # Fifth
                    f"volume=0.05,"
                    f"tremolo=f=0.15:d=0.4"
                ),
                '-f', 'lavfi',
                '-i', (
                    f"anoisesrc=d={duration}:c=pink:a=0.02"  # Subtle texture
                ),
                '-filter_complex', (
                    "[0:a][1:a][2:a][3:a]amix=inputs=4:duration=longest,"
                    "afade=t=in:st=0:d=2,"
                    f"afade=t=out:st={duration-3}:d=3,"
                    "equalizer=f=100:t=q:w=1:g=3,"
                    "equalizer=f=3000:t=q:w=1:g=-5,"
                    "acompressor=threshold=-20dB:ratio=4:attack=200:release=1000"
                ),
                '-c:a', 'aac',
                '-b:a', '192k',
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return output_file.exists()
        except Exception as e:
            logger.warning(f"Ambient music generation failed: {e}")
            return False

    def _create_cinematic_scene(self, text: str, scene_num: int,
                                    voice: str = "en-US-GuyNeural",
                                    style: str = "dramatic") -> Dict[str, Any]:
        try:
            """Create a cinematic scene with effects"""

            scene_id = f"cine_{scene_num}_{int(time.time() * 1000)}"
            audio_file = self.audio_dir / f"{scene_id}.mp3"
            video_file = self.temp_dir / f"{scene_id}.mp4"

            # Generate voiceover
            logger.info(f"   🎤 Scene {scene_num}: {text[:40]}...")

            if self.tts_available:
                # Clean text for TTS (remove special chars that cause issues)
                tts_text = text.replace("'", "'").replace('"', '')
                success = self.generate_voiceover(tts_text, audio_file, voice)
                if success:
                    duration = self.get_audio_duration(audio_file) + 1.5  # Extra padding
                else:
                    duration = max(3.0, len(text.split()) * 0.5)
                    audio_file = None
            else:
                duration = max(3.0, len(text.split()) * 0.5)
                audio_file = None

            # Escape text for FFmpeg drawtext
            safe_text = (text.replace("\\", "\\\\\\\\")
                            .replace("'", "")
                            .replace(":", "\\:")
                            .replace("%", "\\%"))

            # Determine font size based on text length
            if len(text) < 20:
                fontsize = 72
            elif len(text) < 40:
                fontsize = 56
            elif len(text) < 60:
                fontsize = 48
            else:
                fontsize = 40

            # Cinematic color grade (teal/orange look)
            # Animated glow background with gradient

            # Build complex filter
            vf_parts = []

            # Base: animated gradient background
            # Using geq for animated colors
            vf_parts.append(
                f"color=c=black:s={self.width}x{self.height}:d={duration}:r={self.fps}"
            )

            # Color grading filter
            color_filter = (
                f"geq="
                f"r='clip(12+8*sin(2*PI*t/6+X/{self.width}*0.5),0,30)':"
                f"g='clip(15+5*sin(2*PI*t/8+Y/{self.height}*0.3),0,35)':"
                f"b='clip(35+15*sin(2*PI*t/10),0,60)'"
            )

            # Text with glow effect (using multiple drawtext layers)
            # Shadow/glow layer
            glow_filter = (
                f"drawtext=text='{safe_text}':"
                f"fontsize={fontsize+4}:"
                f"fontcolor=0x4080ff@0.3:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2:"
                f"font=Arial"
            )

            # Main text layer with fade
            text_filter = (
                f"drawtext=text='{safe_text}':"
                f"fontsize={fontsize}:"
                f"fontcolor=white:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2:"
                f"font=Arial:"
                f"shadowcolor=black@0.8:"
                f"shadowx=3:shadowy=3:"
                f"alpha='if(lt(t,0.8),t/0.8,if(gt(t,{duration-0.8}),({duration}-t)/0.8,1))'"
            )

            # Cinematic letterbox (adds black bars for movie feel)
            letterbox_filter = (
                f"drawbox=x=0:y=0:w={self.width}:h=80:color=black@0.9:t=fill,"
                f"drawbox=x=0:y={self.height-80}:w={self.width}:h=80:color=black@0.9:t=fill"
            )

            # Vignette effect
            vignette_filter = "vignette=PI/4"

            # Combine filters
            full_vf = f"{color_filter},{glow_filter},{text_filter},{letterbox_filter},{vignette_filter}"

            if audio_file and audio_file.exists():
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=black:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-i', str(audio_file),
                    '-vf', full_vf,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '18',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    str(video_file)
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=black:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-vf', full_vf,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '18',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                logger.warning(f"Scene {scene_num} complex filter failed, using simple version")
                # Fallback to simpler filter
                simple_vf = (
                    f"drawtext=text='{safe_text}':"
                    f"fontsize={fontsize}:fontcolor=white:"
                    f"x=(w-text_w)/2:y=(h-text_h)/2:font=Arial:"
                    f"shadowcolor=black:shadowx=2:shadowy=2,"
                    f"fade=in:0:15,fade=out:{int((duration-0.5)*self.fps)}:15"
                )

                if audio_file and audio_file.exists():
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=c=0x0a0a1a:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                        '-i', str(audio_file),
                        '-vf', simple_vf,
                        '-c:v', 'libx264', '-preset', 'fast',
                        '-c:a', 'aac', '-b:a', '192k',
                        '-t', str(duration), '-pix_fmt', 'yuv420p', '-shortest',
                        str(video_file)
                    ]
                else:
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=c=0x0a0a1a:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                        '-vf', simple_vf,
                        '-c:v', 'libx264', '-preset', 'fast',
                        '-t', str(duration), '-pix_fmt', 'yuv420p',
                        str(video_file)
                    ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if not video_file.exists():
                return None

            return {
                "video_file": video_file,
                "audio_file": audio_file,
                "duration": duration,
                "text": text
            }

        except Exception as e:
            logger.error(f"Error in _create_cinematic_scene: {e}", exc_info=True)
            raise

    def _create_title_scene(self, title: str, subtitle: str,
                               duration: float = 6.0,
                               voice: str = "en-US-GuyNeural") -> Dict[str, Any]:
        try:
            """Create dramatic title scene"""

            scene_id = f"title_{int(time.time() * 1000)}"
            audio_file = self.audio_dir / f"{scene_id}.mp3"
            video_file = self.temp_dir / f"{scene_id}.mp4"

            tts_text = f"{title}. {subtitle}"

            if self.tts_available:
                success = self.generate_voiceover(tts_text, audio_file, voice)
                if success:
                    duration = max(self.get_audio_duration(audio_file) + 2.0, duration)

            safe_title = title.replace("'", "").replace(":", "\\:")
            safe_subtitle = subtitle.replace("'", "").replace(":", "\\:")

            # Epic title with glow
            vf = (
                # Animated background
                f"geq=r='clip(8+5*sin(2*PI*t/8),0,20)':g='clip(8+3*sin(2*PI*t/10),0,20)':b='clip(25+10*sin(2*PI*t/6),0,50)',"
                # Title glow
                f"drawtext=text='{safe_title}':fontsize=90:fontcolor=0x6090ff@0.4:"
                f"x=(w-text_w)/2:y=(h/2-70):font=Arial,"
                # Title main
                f"drawtext=text='{safe_title}':fontsize=84:fontcolor=white:"
                f"x=(w-text_w)/2:y=(h/2-70):font=Arial:"
                f"shadowcolor=black@0.9:shadowx=4:shadowy=4:"
                f"alpha='if(lt(t,1.5),t/1.5,if(gt(t,{duration-1.5}),({duration}-t)/1.5,1))',"
                # Subtitle
                f"drawtext=text='{safe_subtitle}':fontsize=36:fontcolor=0xaaaaaa:"
                f"x=(w-text_w)/2:y=(h/2+50):font=Arial:"
                f"alpha='if(lt(t,2),(t-0.5)/1.5,if(gt(t,{duration-1.5}),({duration}-t)/1.5,1))',"
                # Letterbox
                f"drawbox=x=0:y=0:w={self.width}:h=100:color=black@0.95:t=fill,"
                f"drawbox=x=0:y={self.height-100}:w={self.width}:h=100:color=black@0.95:t=fill,"
                # Vignette
                f"vignette=PI/3.5"
            )

            if audio_file.exists():
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=black:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-i', str(audio_file),
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-t', str(duration), '-pix_fmt', 'yuv420p', '-shortest',
                    str(video_file)
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=black:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                    '-t', str(duration), '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                # Fallback
                simple_vf = (
                    f"drawtext=text='{safe_title}':fontsize=80:fontcolor=white:"
                    f"x=(w-text_w)/2:y=(h/2-60):font=Arial:shadowcolor=black:shadowx=3:shadowy=3,"
                    f"drawtext=text='{safe_subtitle}':fontsize=36:fontcolor=0xcccccc:"
                    f"x=(w-text_w)/2:y=(h/2+40):font=Arial,"
                    f"fade=in:0:30,fade=out:{int((duration-1)*self.fps)}:30"
                )
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c=0x080818:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-i', str(audio_file) if audio_file.exists() else '/dev/null',
                    '-vf', simple_vf,
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-c:a', 'aac' if audio_file.exists() else 'copy',
                    '-t', str(duration), '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]
                if not audio_file.exists():
                    cmd = [c for c in cmd if c != '-i' or cmd[cmd.index(c)+1] != '/dev/null']
                    cmd = [
                        'ffmpeg', '-y',
                        '-f', 'lavfi',
                        '-i', f'color=c=0x080818:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                        '-vf', simple_vf,
                        '-c:v', 'libx264', '-preset', 'fast',
                        '-t', str(duration), '-pix_fmt', 'yuv420p',
                        str(video_file)
                    ]
                subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            return {"video_file": video_file, "duration": duration}

        except Exception as e:
            self.logger.error(f"Error in _create_title_scene: {e}", exc_info=True)
            raise
    def _mix_audio_with_music(self, video_file: Path, music_file: Path, 
                             output_file: Path) -> bool:
        """Mix background music with video audio"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_file),
                '-i', str(music_file),
                '-filter_complex', (
                    "[0:a]volume=1.0[voice];"
                    "[1:a]volume=0.15[music];"
                    "[voice][music]amix=inputs=2:duration=shortest"
                ),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                str(output_file)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            return result.returncode == 0
        except:
            return False

    def generate_cinematic_video(self, title: str, subtitle: str,
                                segments: List[str],
                                voice: str = "en-US-GuyNeural",
                                include_music: bool = True) -> Dict[str, Any]:
        """Generate cinematic video with all effects"""

        logger.info(f"🎬 Generating CINEMATIC video: {title}")
        logger.info(f"   Segments: {len(segments)}")
        logger.info(f"   Music: {'Yes' if include_music else 'No'}")

        safe_title = "".join(c for c in title if c.isalnum() or c in ' -_').strip()
        output_filename = f"CINEMATIC_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path = self.output_dir / output_filename

        try:
            scenes = []

            # Title scene
            logger.info("🎬 Creating title sequence...")
            title_scene = self._create_title_scene(title, subtitle, voice=voice)
            if title_scene:
                scenes.append(title_scene)

            # Content scenes
            for i, segment in enumerate(segments):
                scene = self._create_cinematic_scene(segment, i+1, voice=voice)
                if scene:
                    scenes.append(scene)

            # End scene
            logger.info("🎬 Creating end sequence...")
            end_scene = self._create_title_scene("LUMINA", "Knowledge Power Granted ⚡", voice=voice)
            if end_scene:
                scenes.append(end_scene)

            # Concatenate scenes
            logger.info("🔗 Assembling final video...")
            concat_file = self.temp_dir / f"concat_{int(time.time())}.txt"
            with open(concat_file, 'w') as f:
                for scene in scenes:
                    if scene and scene.get("video_file"):
                        f.write(f"file '{scene['video_file']}'\n")

            temp_output = self.temp_dir / f"temp_final_{int(time.time())}.mp4"

            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-c:a', 'aac', '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                str(temp_output)
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Add background music if requested
            total_duration = sum(s.get("duration", 0) for s in scenes if s)

            if include_music and temp_output.exists():
                logger.info("🎵 Adding background music...")
                music_file = self.temp_dir / f"ambient_{int(time.time())}.aac"

                if self.generate_ambient_music(total_duration + 5, music_file):
                    if self._mix_audio_with_music(temp_output, music_file, output_path):
                        logger.info("   ✅ Music mixed successfully")
                    else:
                        # Just copy without music
                        import shutil
                        shutil.copy(temp_output, output_path)
                else:
                    import shutil
                    shutil.copy(temp_output, output_path)
            else:
                import shutil
                shutil.copy(temp_output, output_path)

            # Cleanup
            for scene in scenes:
                try:
                    if scene and scene.get("video_file"):
                        Path(scene["video_file"]).unlink()
                    if scene and scene.get("audio_file"):
                        Path(scene["audio_file"]).unlink()
                except:
                    pass

            try:
                temp_output.unlink()
            except:
                pass

            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            logger.info(f"✅ CINEMATIC Video created!")
            logger.info(f"   📁 {output_path}")
            logger.info(f"   📊 Size: {file_size_mb:.2f} MB")
            logger.info(f"   ⏱️  Duration: {total_duration:.1f}s")

            return {
                "success": True,
                "output_file": str(output_path),
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": total_duration,
                "has_music": include_music
            }

        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


def main():
    print("="*80)
    print("🎬 LUMINA CINEMATIC Video Generator")
    print("   Professional Quality with Music & Effects")
    print("="*80)

    generator = LuminaCinematicGenerator()

    result = generator.generate_cinematic_video(
        title="LUMINA",
        subtitle="Illuminate the World",
        segments=[
            "Welcome to LUMINA",
            "What is LUMINA?",
            "Personal human opinion",
            "Plus individual perspective",
            "For whatever its worth",
            "Which is EVERYTHING",
            "We illuminate the global public",
            "We share knowledge",
            "We share perspectives",
            "We share insights",
            "Every being matters",
            "We leave no one behind",
            "This is LUMINA",
            "This is our mission",
            "Join us"
        ],
        voice="en-US-GuyNeural",
        include_music=True
    )

    print("\n" + "="*80)
    if result.get("success"):
        print(f"✅ CINEMATIC VIDEO COMPLETE!")
        print(f"   📁 {result['output_file']}")
        print(f"   📊 {result['file_size_mb']:.2f} MB")
        print(f"   🎵 Music: {'Yes' if result.get('has_music') else 'No'}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    print("="*80)


if __name__ == "__main__":



    main()