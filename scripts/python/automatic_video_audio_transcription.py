#!/usr/bin/env python3
"""
Automatic Video/Audio Transcription System

Automatically transcribes YouTube videos, audio files, and other video content
for intelligence extraction and SYPHON integration.

Supports:
- YouTube videos (via yt-dlp + Whisper)
- Audio files (MP3, WAV, etc.)
- Video files (MP4, etc.)
- Real-time transcription capabilities
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class VideoAudioTranscriber:
    """
    Automatic transcription system for videos and audio
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize transcriber"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.transcriptions_dir = self.project_root / "data" / "transcriptions"
        self.transcriptions_dir.mkdir(parents=True, exist_ok=True)

        self.intelligence_dir = self.project_root / "data" / "intelligence"
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        dependencies = {
            "yt-dlp": False,
            "whisper": False,
            "ffmpeg": False
        }

        # Check yt-dlp
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            dependencies["yt-dlp"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Check whisper (openai-whisper)
        try:
            import whisper
            dependencies["whisper"] = True
        except ImportError:
            pass

        # Check ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            dependencies["ffmpeg"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return dependencies

    def transcribe_youtube_video(self, video_url: str, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Transcribe a YouTube video

        Args:
            video_url: YouTube video URL
            output_dir: Optional output directory

        Returns:
            Transcription metadata and results
        """
        if output_dir is None:
            output_dir = self.transcriptions_dir

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        video_id = self._extract_video_id(video_url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_prefix = output_dir / f"youtube_{video_id}_{timestamp}"

        print(f"📹 Transcribing YouTube video: {video_url}")
        print(f"   Video ID: {video_id}")

        # Step 1: Download audio using yt-dlp with size validation
        audio_file = output_prefix.with_suffix(".wav")
        print(f"\n1️⃣ Downloading audio...")

        # First, get expected original video file size from YouTube metadata
        original_video_size = None
        size_metadata = {}  # Initialize size metadata dict early
        try:
            print(f"   📊 Getting original video metadata...")
            info_result = subprocess.run([
                "yt-dlp",
                "--print", "%(filesize)s",  # Original video file size in bytes
                "--skip-download",
                video_url
            ], capture_output=True, text=True, check=True, timeout=60)

            if info_result.returncode == 0:
                output_lines = info_result.stdout.strip().split('\n')
                for line in output_lines:
                    line = line.strip()
                    # Look for numeric value (file size in bytes)
                    if line and line.isdigit():
                        original_video_size = int(line)
                        print(f"   📊 Original video size: {original_video_size / (1024*1024):.2f} MB")
                        break
        except Exception as e:
            print(f"   ⚠️  Could not get original video size (non-critical): {e}")

        # Download audio
        try:
            download_result = subprocess.run([
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "wav",
                "--audio-quality", "0",  # Best quality
                "-o", str(audio_file),
                video_url
            ], check=True, capture_output=True, text=True, timeout=600)
            print(f"   ✅ Audio downloaded: {audio_file}")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"   ❌ Error downloading audio: {error_msg[:200]}")
            return {"error": f"Failed to download audio: {e}"}
        except subprocess.TimeoutExpired:
            print(f"   ❌ Download timeout (exceeded 10 minutes)")
            return {"error": "Download timeout - file may be very large or connection slow"}

        # Validate downloaded file exists and get size
        if not audio_file.exists():
            print(f"   ❌ ERROR: Downloaded file does not exist: {audio_file}")
            return {"error": "Downloaded file not found"}

        downloaded_audio_size = audio_file.stat().st_size
        print(f"   📊 Downloaded audio size: {downloaded_audio_size / (1024*1024):.2f} MB")

        # Compare sizes to detect corruption
        if original_video_size:
            size_diff = abs(downloaded_audio_size - original_video_size)
            size_ratio = downloaded_audio_size / original_video_size if original_video_size > 0 else 0

            # Audio should be smaller than video (typically 5-20% of original video size)
            # If audio is LARGER than video, that's impossible and indicates corruption
            if downloaded_audio_size > original_video_size:
                print(f"   ❌ CORRUPTION DETECTED: Downloaded audio ({downloaded_audio_size / (1024*1024):.2f} MB) is LARGER than original video ({original_video_size / (1024*1024):.2f} MB)!")
                print(f"      This is impossible - file is likely corrupt or incorrect.")
                audio_file.unlink()  # Delete corrupt file
                return {
                    "error": f"File size corruption detected: audio ({downloaded_audio_size / (1024*1024):.2f} MB) > video ({original_video_size / (1024*1024):.2f} MB)",
                    "corruption_detected": True,
                    "original_size": original_video_size,
                    "downloaded_size": downloaded_audio_size
                }
            # If audio is suspiciously small (<0.1% of video), likely corrupt or incomplete
            elif size_ratio < 0.001 and downloaded_audio_size < 1024 * 100:  # Less than 0.1% and under 100KB
                print(f"   ❌ CORRUPTION DETECTED: Downloaded audio ({downloaded_audio_size / (1024*1024):.2f} MB) is suspiciously small compared to original video ({original_video_size / (1024*1024):.2f} MB)!")
                print(f"      Ratio: {size_ratio * 100:.3f}% - file is likely corrupt or incomplete.")
                audio_file.unlink()  # Delete corrupt file
                return {
                    "error": f"File size corruption detected: audio ({downloaded_audio_size / (1024*1024):.2f} MB) is too small vs video ({original_video_size / (1024*1024):.2f} MB) - ratio: {size_ratio * 100:.3f}%",
                    "corruption_detected": True,
                    "original_size": original_video_size,
                    "downloaded_size": downloaded_audio_size,
                    "size_ratio": size_ratio
                }
            else:
                print(f"   ✅ Size validation passed: Audio is {size_ratio * 100:.1f}% of original video (expected: 5-20%)")

        # Absolute minimum size check (any file under 1KB is definitely corrupt)
        if downloaded_audio_size < 1024:
            print(f"   ❌ ERROR: Downloaded file is too small ({downloaded_audio_size} bytes < 1KB) - definitely corrupt")
            audio_file.unlink()  # Delete corrupt file
            return {
                "error": f"Downloaded file is too small ({downloaded_audio_size} bytes) - likely corrupt",
                "corruption_detected": True,
                "downloaded_size": downloaded_audio_size
            }

        # Store size metadata for later comparison
        size_metadata.update({
            "original_video_size_bytes": original_video_size,
            "downloaded_audio_size_bytes": downloaded_audio_size,
            "size_ratio": (downloaded_audio_size / original_video_size) if original_video_size else None,
            "size_validation_passed": True
        })

        # Step 2: Transcribe using Whisper
        print(f"\n2️⃣ Transcribing audio with Whisper...")
        transcript_text = self._transcribe_audio_whisper(audio_file)

        if not transcript_text:
            return {"error": "Failed to transcribe audio"}

        # Step 3: Save transcription
        transcript_file = output_prefix.with_suffix(".txt")
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        print(f"   ✅ Transcript saved: {transcript_file}")

        # Step 4: Save metadata (include size validation data)
        metadata = {
            "source": "youtube",
            "video_url": video_url,
            "video_id": video_id,
            "transcription_timestamp": datetime.now().isoformat(),
            "transcript_file": str(transcript_file.relative_to(self.project_root)),
            "audio_file": str(audio_file.relative_to(self.project_root)),
            "transcript_length": len(transcript_text),
            "word_count": len(transcript_text.split()),
            "size_validation": size_metadata
        }

        metadata_file = output_prefix.with_suffix(".json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"   ✅ Metadata saved: {metadata_file}")

        # Step 5: Feed to SYPHON
        print(f"\n3️⃣ Feeding to SYPHON intelligence system...")
        self._feed_to_syphon(video_url, transcript_text, metadata)

        return {
            "success": True,
            "transcript": transcript_text,
            "metadata": metadata,
            "transcript_file": str(transcript_file),
            "metadata_file": str(metadata_file)
        }

    def transcribe_audio_file(self, audio_path: Path, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        try:
            """
            Transcribe an audio file

            Args:
                audio_path: Path to audio file
                output_dir: Optional output directory

            Returns:
                Transcription results
            """
            audio_path = Path(audio_path)
            if not audio_path.exists():
                return {"error": f"Audio file not found: {audio_path}"}

            if output_dir is None:
                output_dir = self.transcriptions_dir

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_prefix = output_dir / f"audio_{audio_path.stem}_{timestamp}"

            print(f"🎵 Transcribing audio file: {audio_path}")

            # Transcribe using Whisper
            transcript_text = self._transcribe_audio_whisper(audio_path)

            if not transcript_text:
                return {"error": "Failed to transcribe audio"}

            # Save transcription
            transcript_file = output_prefix.with_suffix(".txt")
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            # Save metadata
            metadata = {
                "source": "audio_file",
                "audio_file": str(audio_path),
                "transcription_timestamp": datetime.now().isoformat(),
                "transcript_file": str(transcript_file.relative_to(self.project_root)),
                "transcript_length": len(transcript_text),
                "word_count": len(transcript_text.split())
            }

            metadata_file = output_prefix.with_suffix(".json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            # Feed to SYPHON
            self._feed_to_syphon(str(audio_path), transcript_text, metadata)

            return {
                "success": True,
                "transcript": transcript_text,
                "metadata": metadata
            }

        except Exception as e:
            self.logger.error(f"Error in transcribe_audio_file: {e}", exc_info=True)
            raise
    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from YouTube URL"""
        import re

        # Match various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)

        # Fallback: use hash of URL
        return video_url.replace("https://", "").replace("http://", "").replace("/", "_")[:20]

    def _transcribe_audio_whisper(self, audio_file: Path) -> Optional[str]:
        """Transcribe audio file using Whisper"""
        try:
            import whisper

            print(f"   Loading Whisper model...")
            model = whisper.load_model("base")  # base, small, medium, large

            print(f"   Transcribing audio...")
            result = model.transcribe(str(audio_file))

            transcript_text = result["text"]
            print(f"   ✅ Transcription complete ({len(transcript_text)} characters)")

            return transcript_text

        except ImportError:
            print(f"   ⚠️  Whisper not available. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"   ❌ Error transcribing: {e}")
            return None

    def _feed_to_syphon(self, source: str, transcript: str, metadata: Dict[str, Any]):
        """Feed transcription to SYPHON intelligence system"""
        # Create intelligence report
        intelligence_file = self.intelligence_dir / f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Video/Audio Transcription Intelligence

**Source:** {source}
**Transcription Date:** {metadata.get('transcription_timestamp', datetime.now().isoformat())}
**Word Count:** {metadata.get('word_count', 'unknown')}
**Classification:** Transcribed Intelligence

---

## Full Transcript

{transcript}

---

## Metadata

```json
{json.dumps(metadata, indent=2)}
```

---

**Status:** Automatic transcription complete. Ready for SYPHON processing.
"""

        with open(intelligence_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"   ✅ Intelligence report saved: {intelligence_file}")

        # Also save JSON for programmatic access
        json_file = intelligence_file.with_suffix(".json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "source": source,
                "transcript": transcript,
                "metadata": metadata,
                "intelligence_file": str(intelligence_file.relative_to(self.project_root))
            }, f, indent=2, ensure_ascii=False)

        print(f"   ✅ JSON data saved: {json_file}")

def main():
    """Test transcription system"""
    print("="*80)
    print("🎤 Automatic Video/Audio Transcription System")
    print("="*80)

    transcriber = VideoAudioTranscriber()

    # Check dependencies
    print("\n🔍 Checking dependencies...")
    deps = transcriber.check_dependencies()
    for dep, available in deps.items():
        status = "✅" if available else "❌"
        print(f"   {status} {dep}: {'Available' if available else 'Not available'}")

    if not all(deps.values()):
        print("\n⚠️  Some dependencies are missing.")
        print("Install with:")
        print("  pip install yt-dlp openai-whisper")
        print("  # ffmpeg: https://ffmpeg.org/download.html")
        return

    # Example: Transcribe YouTube video
    # video_url = "https://youtu.be/X_EJi6yCuTM?si=2BzxQTKNm50iif2k"
    # result = transcriber.transcribe_youtube_video(video_url)
    # print(f"\n✅ Transcription complete: {result.get('transcript_file')}")

    print("\n" + "="*80)
    print("✅ Transcription system ready")
    print("="*80)

if __name__ == "__main__":



    main()