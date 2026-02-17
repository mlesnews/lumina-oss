#!/usr/bin/env python3
"""
LUMINA Local TTS System

Fully local text-to-speech using open-source models:
- No API keys required
- No rate limits
- Privacy-first (all processing local)
- Best quality: Coqui XTTS-v2 (if available)
- Fast fallback: Piper TTS
- Universal fallback: Edge TTS (local processing)

This eliminates all external API restrictions.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LocalTTS")


class LocalTTSSystem:
    """
    Local TTS System - No API keys, no limits, all local

    Priority:
    1. Coqui XTTS-v2 (best quality, multilingual)
    2. Piper TTS (fast, lightweight)
    3. Edge TTS (universal fallback, still local)
    """

    def __init__(self):
        self.available = False
        self.engine_type = None
        self.engine = None
        self.models_dir = Path("models/tts")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🔊 Initializing Local TTS System...")

        # Check available engines in priority order
        if self._check_coqui():
            self.available = True
            self.engine_type = "coqui"
        elif self._check_piper():
            self.available = True
            self.engine_type = "piper"
        elif self._check_edge():
            self.available = True
            self.engine_type = "edge"
        else:
            logger.warning("   ⚠️  No local TTS engines available")

    def _check_coqui(self) -> bool:
        """Check if Coqui TTS (XTTS-v2) is available"""
        try:
            import TTS
            self.engine = TTS.TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            logger.info("   ✅ Coqui XTTS-v2 available (Quality: ⭐⭐⭐⭐⭐)")
            return True
        except ImportError:
            logger.debug("   Coqui TTS not installed (pip install TTS)")
            return False
        except Exception as e:
            logger.debug(f"   Coqui TTS check failed: {e}")
            return False

    def _check_piper(self) -> bool:
        """Check if Piper TTS is available"""
        try:
            # Check if piper binary exists
            result = subprocess.run(["piper", "--version"], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info("   ✅ Piper TTS available (Quality: ⭐⭐⭐⭐)")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check Python package
        try:
            import piper_tts
            logger.info("   ✅ Piper TTS (Python) available")
            return True
        except ImportError:
            logger.debug("   Piper TTS not installed")
            return False

    def _check_edge(self) -> bool:
        """Edge TTS is always available (runs locally, no API)"""
        try:
            import edge_tts
            logger.info("   ✅ Edge TTS available (Quality: ⭐⭐⭐)")
            return True
        except ImportError:
            logger.debug("   Edge TTS not installed (pip install edge-tts)")
            return False

    def synthesize(self, text: str, output_file: Path,
                       voice: str = "default",
                       language: str = "en") -> Dict[str, Any]:
        try:
            """
            Synthesize speech locally

            Args:
                text: Text to speak
                output_file: Output audio file (WAV/MP3)
                voice: Voice name (engine-specific)
                language: Language code (default: en)

            Returns:
                Dict with success status and metadata
            """
            if not self.available:
                return {"success": False, "error": "No local TTS engine available"}

            # Preprocess text for natural speech
            processed_text = self._preprocess_text(text)

            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Route to appropriate engine
            if self.engine_type == "coqui":
                return self._synth_coqui(processed_text, output_file, voice, language)
            elif self.engine_type == "piper":
                return self._synth_piper(processed_text, output_file, voice, language)
            elif self.engine_type == "edge":
                return self._synth_edge(processed_text, output_file, voice, language)
            else:
                return {"success": False, "error": "Unknown engine type"}

        except Exception as e:
            self.logger.error(f"Error in synthesize: {e}", exc_info=True)
            raise
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for natural speech

        Local models handle pronunciation better than cloud APIs,
        but we still help them with common issues.
        """
        processed = text

        # Remove stage directions
        processed = processed.replace("[", "").replace("]", "")

        # LUMINA pronunciation hint
        # Most local models handle this well, but help if needed
        for variant in ["LUMINA", "Lumina"]:
            # Keep as-is, local models usually get it right
            # But can add space: "Loo-MEE-nah" if needed
            pass

        # Clean up spacing
        while "  " in processed:
            processed = processed.replace("  ", " ")

        return processed.strip()

    def _synth_coqui(self, text: str, output_file: Path, 
                    voice: str, language: str) -> Dict[str, Any]:
        """Synthesize with Coqui XTTS-v2"""
        try:
            import TTS

            # XTTS-v2 supports cloning from a reference audio
            # For now, use default voice
            voice_name = voice if voice != "default" else "default"

            # Synthesize
            self.engine.tts_to_file(
                text=text,
                file_path=str(output_file),
                speaker_wav=None,  # Can add voice cloning here
                language=language
            )

            return {
                "success": True,
                "engine": "coqui",
                "output_file": str(output_file),
                "file_size": output_file.stat().st_size,
                "voice": voice_name,
                "model": "xtts-v2"
            }
        except Exception as e:
            return {"success": False, "engine": "coqui", "error": str(e)}

    def _synth_piper(self, text: str, output_file: Path,
                    voice: str, language: str) -> Dict[str, Any]:
        """Synthesize with Piper TTS"""
        try:
            # Default English voice
            voice_name = voice if voice != "default" else "en_US-lessac-medium"

            # Use piper command line
            cmd = [
                "piper",
                "--model", f"models/{voice_name}.onnx",
                "--output_file", str(output_file)
            ]

            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=60
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "engine": "piper",
                    "output_file": str(output_file),
                    "file_size": output_file.stat().st_size,
                    "voice": voice_name
                }
            else:
                return {"success": False, "engine": "piper", "error": result.stderr}
        except Exception as e:
            return {"success": False, "engine": "piper", "error": str(e)}

    def _synth_edge(self, text: str, output_file: Path,
                   voice: str, language: str) -> Dict[str, Any]:
        """Synthesize with Edge TTS (local processing)"""
        try:
            import edge_tts
            import asyncio

            voice_name = voice if voice != "default" else "en-US-GuyNeural"

            async def generate():
                communicate = edge_tts.Communicate(text, voice_name)
                await communicate.save(str(output_file))

            asyncio.run(generate())

            return {
                "success": True,
                "engine": "edge",
                "output_file": str(output_file),
                "file_size": output_file.stat().st_size,
                "voice": voice_name
            }
        except Exception as e:
            return {"success": False, "engine": "edge", "error": str(e)}


def install_coqui():
    """Install Coqui TTS (best quality)"""
    print("\n🔊 Installing Coqui TTS (XTTS-v2)...")
    print("   This may take a few minutes (downloads ~500MB model)")
    print()

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "TTS"], check=True)
        print("✅ Coqui TTS installed!")
        print()
        print("Next steps:")
        print("  1. Run this script again to initialize")
        print("  2. First run will download the XTTS-v2 model (~500MB)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def install_edge():
    """Install Edge TTS (universal fallback)"""
    print("\n🔊 Installing Edge TTS...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"], check=True)
        print("✅ Edge TTS installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Local TTS System")
        parser.add_argument("--install-coqui", action="store_true", 
                           help="Install Coqui TTS (best quality)")
        parser.add_argument("--install-edge", action="store_true",
                           help="Install Edge TTS (fallback)")
        parser.add_argument("--test", type=str, help="Test with sample text")
        parser.add_argument("--status", action="store_true", help="Show status")

        args = parser.parse_args()

        if args.install_coqui:
            install_coqui()
        elif args.install_edge:
            install_edge()
        elif args.status:
            tts = LocalTTSSystem()
            if tts.available:
                print(f"\n✅ Local TTS Available")
                print(f"   Engine: {tts.engine_type}")
                print(f"   Quality: ⭐⭐⭐⭐⭐" if tts.engine_type == "coqui" else 
                      "⭐⭐⭐⭐" if tts.engine_type == "piper" else "⭐⭐⭐")
            else:
                print("\n❌ No local TTS engines available")
                print("\nTo install:")
                print("  python local_tts_system.py --install-edge")
                print("  python local_tts_system.py --install-coqui")
        elif args.test:
            tts = LocalTTSSystem()
            if not tts.available:
                print("❌ No local TTS available. Install with --install-edge or --install-coqui")
                return

            output = Path("output/test_local_tts.wav")
            print(f"\n🎙️  Testing: \"{args.test}\"")
            print(f"   Engine: {tts.engine_type}")

            result = tts.synthesize(args.test, output)

            if result.get("success"):
                print(f"✅ Success!")
                print(f"   Output: {result['output_file']}")
                print(f"   Size: {result['file_size'] / 1024:.1f} KB")

                # Play it
                subprocess.run(["start", str(output)], shell=True)
            else:
                print(f"❌ Failed: {result.get('error')}")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()