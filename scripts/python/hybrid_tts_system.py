#!/usr/bin/env python3
"""
LUMINA Hybrid TTS System

Intelligent Text-to-Speech with automatic quality fallback:
1. ElevenLabs (best quality, most natural)
2. OpenAI TTS (excellent quality, simple API)
3. Azure Neural TTS (good quality, enterprise)
4. Edge TTS (free fallback)

Each engine handles pronunciation differently - the hybrid system
abstracts away complexity and always gives the best available result.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridTTS")


class HybridTTSSystem:
    """
    Hybrid TTS System - Automatically uses best available engine

    Priority:
    1. ElevenLabs - Best natural speech, no SSML needed
    2. OpenAI TTS - Great quality, simple
    3. Azure Speech - Good quality with SSML
    4. Edge TTS - Free fallback
    """

    def __init__(self, preferred_engine: str = "auto"):
        """
        Initialize Hybrid TTS

        Args:
            preferred_engine: "auto", "local", "elevenlabs", "openai", "azure", "edge"
        """
        self.preferred_engine = preferred_engine
        self.available_engines: Dict[str, Any] = {}

        logger.info("🎙️  Initializing Hybrid TTS System...")

        # Check each engine (local first - highest priority)
        self._check_local()
        self._check_elevenlabs()
        self._check_openai()
        self._check_azure()
        self._check_edge()

        # Determine best engine
        self.best_engine = self._determine_best_engine()

        logger.info(f"   ✅ Best available engine: {self.best_engine}")
        if self.available_engines:
            logger.info(f"   📊 Available: {list(self.available_engines.keys())}")

    def _check_elevenlabs(self):
        """Check if ElevenLabs is available"""
        try:
            key = self._get_secret("elevenlabs-api-key")
            if key:
                from elevenlabs_tts_integration import ElevenLabsTTS
                self.available_engines["elevenlabs"] = {
                    "instance": ElevenLabsTTS(api_key=key),
                    "quality": 5,
                    "name": "ElevenLabs"
                }
                logger.info("   ✅ ElevenLabs available (Quality: ⭐⭐⭐⭐⭐)")
        except ImportError:
            logger.debug("ElevenLabs module not available")
        except Exception as e:
            logger.debug(f"ElevenLabs check failed: {e}")

    def _check_openai(self):
        """Check if OpenAI TTS is available"""
        try:
            key = os.getenv("OPENAI_API_KEY") or self._get_secret("openai-api-key")
            if key:
                import openai
                self.available_engines["openai"] = {
                    "client": openai.OpenAI(api_key=key),
                    "quality": 4,
                    "name": "OpenAI TTS"
                }
                logger.info("   ✅ OpenAI TTS available (Quality: ⭐⭐⭐⭐)")
        except ImportError:
            logger.debug("OpenAI not installed")
        except Exception as e:
            logger.debug(f"OpenAI check failed: {e}")

    def _check_azure(self):
        """Check if Azure Speech is available"""
        try:
            key = self._get_secret("azure-speech-key")
            region = self._get_secret("azure-speech-region")

            if key and region:
                import azure.cognitiveservices.speech as speechsdk
                self.available_engines["azure"] = {
                    "key": key,
                    "region": region,
                    "quality": 3.5,
                    "name": "Azure Neural TTS"
                }
                logger.info("   ✅ Azure Speech available (Quality: ⭐⭐⭐⭐)")
        except ImportError:
            logger.debug("Azure Speech SDK not installed")
        except Exception as e:
            logger.debug(f"Azure check failed: {e}")

    def _check_local(self):
        """Check if Local TTS (Coqui XTTS-v2) is available"""
        try:
            from local_tts_system import LocalTTSSystem
            local_tts = LocalTTSSystem()
            if local_tts.available:
                self.available_engines["local"] = {
                    "instance": local_tts,
                    "quality": 5,  # Best quality (near ElevenLabs)
                    "name": "Local TTS (XTTS-v2)"
                }
                logger.info("   ✅ Local TTS available (Quality: ⭐⭐⭐⭐⭐)")
        except ImportError:
            logger.debug("Local TTS module not available")
        except Exception as e:
            logger.debug(f"Local TTS check failed: {e}")

    def _check_edge(self):
        """Edge TTS is always available (free)"""
        try:
            import edge_tts
            self.available_engines["edge"] = {
                "quality": 3,
                "name": "Microsoft Edge TTS"
            }
            logger.info("   ✅ Edge TTS available (Quality: ⭐⭐⭐)")
        except ImportError:
            logger.debug("Edge TTS not installed")

    def _get_secret(self, name: str) -> Optional[str]:
        """Get secret from Azure Key Vault"""
        try:
            cmd = f'az keyvault secret show --vault-name jarvis-lumina --name {name} --query value -o tsv'
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Secret retrieval failed for {name}: {e}")
        return None

    def _determine_best_engine(self) -> str:
        """Determine best engine based on quality (local preferred)"""
        if self.preferred_engine != "auto" and self.preferred_engine in self.available_engines:
            return self.preferred_engine

        if not self.available_engines:
            return "none"

        # Prefer local if available (no API limits, privacy)
        if "local" in self.available_engines:
            return "local"

        # Otherwise sort by quality, return best
        return max(self.available_engines.keys(), 
                   key=lambda x: self.available_engines[x]["quality"])

    def synthesize(self, text: str, output_file: Path,
                   voice: str = "default", engine: str = "auto") -> Dict[str, Any]:
        """
        Synthesize speech using best available engine

        Args:
            text: Text to speak
            output_file: Output audio file
            voice: Voice name (engine-specific)
            engine: Force specific engine or "auto"

        Returns:
            Dict with success, engine used, and metadata
        """
        target_engine = engine if engine != "auto" else self.best_engine

        if target_engine == "none" or target_engine not in self.available_engines:
            return {"success": False, "error": "No TTS engine available"}

        # Preprocess text for natural speech
        processed_text = self._universal_preprocess(text)

        # Route to appropriate engine
        if target_engine == "local":
            return self._synth_local(processed_text, output_file, voice)
        elif target_engine == "elevenlabs":
            return self._synth_elevenlabs(processed_text, output_file, voice)
        elif target_engine == "openai":
            return self._synth_openai(processed_text, output_file, voice)
        elif target_engine == "azure":
            return self._synth_azure(processed_text, output_file, voice)
        elif target_engine == "edge":
            return self._synth_edge(processed_text, output_file, voice)
        else:
            return {"success": False, "error": f"Unknown engine: {target_engine}"}

    def _universal_preprocess(self, text: str) -> str:
        """
        Universal text preprocessing for all engines

        Handles common pronunciation issues across all TTS systems.
        """
        processed = text

        # Remove stage directions
        processed = processed.replace("[", "").replace("]", "")

        # LUMINA - Help all engines pronounce it correctly
        # "Loo-MEE-nah" not "Loo-MAH-nah"
        for variant in ["LUMINA", "Lumina"]:
            processed = processed.replace(variant, "Loomina")

        # lumina.io pronunciation
        processed = processed.replace("lumina.io", "Loomina dot I O")

        # AI -> spell it out for clarity
        processed = processed.replace(" AI ", " A.I. ")
        processed = processed.replace(" AI.", " A.I.")
        processed = processed.replace(" AI,", " A.I.,")
        processed = processed.replace("AI-", "A.I. ")

        # Common tech terms
        processed = processed.replace("Gen Z", "Gen Zee")
        processed = processed.replace("GPT", "G.P.T.")
        processed = processed.replace("LLM", "L.L.M.")

        # Name corrections
        processed = processed.replace("Andre Karpathy", "Andrej Karpathy")
        processed = processed.replace("Andrej", "Andray")  # Help pronunciation

        # Clean double spaces
        while "  " in processed:
            processed = processed.replace("  ", " ")

        return processed.strip()

    def _synth_elevenlabs(self, text: str, output_file: Path, voice: str) -> Dict[str, Any]:
        """Synthesize with ElevenLabs"""
        engine_data = self.available_engines["elevenlabs"]
        tts = engine_data["instance"]

        voice_name = voice if voice != "default" else "josh"
        result = tts.synthesize(text, output_file, voice=voice_name)
        result["engine"] = "elevenlabs"
        return result

    def _synth_openai(self, text: str, output_file: Path, voice: str) -> Dict[str, Any]:
        """Synthesize with OpenAI TTS"""
        try:
            engine_data = self.available_engines["openai"]
            client = engine_data["client"]

            # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
            voice_name = voice if voice != "default" else "onyx"

            response = client.audio.speech.create(
                model="tts-1-hd",  # Higher quality
                voice=voice_name,
                input=text
            )

            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            response.stream_to_file(str(output_file))

            return {
                "success": True,
                "engine": "openai",
                "output_file": str(output_file),
                "file_size": output_file.stat().st_size,
                "voice": voice_name,
                "model": "tts-1-hd"
            }
        except Exception as e:
            return {"success": False, "engine": "openai", "error": str(e)}

    def _synth_azure(self, text: str, output_file: Path, voice: str) -> Dict[str, Any]:
        """Synthesize with Azure Speech"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            engine_data = self.available_engines["azure"]

            speech_config = speechsdk.SpeechConfig(
                subscription=engine_data["key"],
                region=engine_data["region"]
            )

            # Azure neural voices
            voice_name = voice if voice != "default" else "en-US-GuyNeural"
            speech_config.speech_synthesis_voice_name = voice_name

            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_file))
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )

            # Generate SSML for better control
            ssml = self._generate_azure_ssml(text, voice_name)
            result = synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return {
                    "success": True,
                    "engine": "azure",
                    "output_file": str(output_file),
                    "file_size": output_file.stat().st_size,
                    "voice": voice_name
                }
            else:
                return {"success": False, "engine": "azure", "error": str(result.reason)}

        except Exception as e:
            return {"success": False, "engine": "azure", "error": str(e)}

    def _generate_azure_ssml(self, text: str, voice: str) -> str:
        """Generate SSML for Azure with improved pronunciation"""
        # Use sub tags for pronunciation hints
        ssml_text = text

        # These are already preprocessed, but add SSML specifics
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                         xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice}">
                <prosody rate="0%" pitch="+0%">
                    {ssml_text}
                </prosody>
            </voice>
        </speak>'''
        return ssml

    def _synth_local(self, text: str, output_file: Path, voice: str) -> Dict[str, Any]:
        """Synthesize with Local TTS (Coqui/Piper/Edge)"""
        try:
            engine_data = self.available_engines["local"]
            local_tts = engine_data["instance"]

            result = local_tts.synthesize(text, output_file, voice=voice)
            result["engine"] = "local"
            return result
        except Exception as e:
            return {"success": False, "engine": "local", "error": str(e)}

    def _synth_edge(self, text: str, output_file: Path, voice: str) -> Dict[str, Any]:
        """Synthesize with Edge TTS (free)"""
        try:
            import edge_tts

            voice_name = voice if voice != "default" else "en-US-GuyNeural"

            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Edge TTS is async
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

    def get_status(self) -> Dict[str, Any]:
        """Get system status and available engines"""
        return {
            "best_engine": self.best_engine,
            "preferred_engine": self.preferred_engine,
            "available_engines": {
                name: {
                    "name": data["name"],
                    "quality": data["quality"]
                }
                for name, data in self.available_engines.items()
            }
        }


def provision_elevenlabs_key():
    try:
        """Interactive setup for ElevenLabs"""
        print("\n" + "="*70)
        print("🎙️  ElevenLabs API Key Setup")
        print("="*70)
        print()
        print("ElevenLabs offers the BEST text-to-speech quality.")
        print()
        print("📋 Setup Steps:")
        print("   1. Go to: https://elevenlabs.io")
        print("   2. Sign up (free tier: 10,000 chars/month)")
        print("   3. Click your profile → 'Profile + API Key'")
        print("   4. Copy your API key")
        print()

        api_key = input("Paste your ElevenLabs API key (or Enter to skip): ").strip()

        if not api_key:
            print("⏭️  Skipped")
            return False

        # Store in vault
        result = subprocess.run([
            "az", "keyvault", "secret", "set",
            "--vault-name", "jarvis-lumina",
            "--name", "elevenlabs-api-key",
            "--value", api_key
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ ElevenLabs API key stored in Azure Key Vault!")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False


    except Exception as e:
        logger.error(f"Error in provision_elevenlabs_key: {e}", exc_info=True)
        raise
def provision_openai_key():
    try:
        """Interactive setup for OpenAI"""
        print("\n" + "="*70)
        print("🤖 OpenAI API Key Setup")
        print("="*70)
        print()
        print("OpenAI TTS offers excellent quality speech synthesis.")
        print()
        print("📋 Setup Steps:")
        print("   1. Go to: https://platform.openai.com/api-keys")
        print("   2. Create a new API key")
        print("   3. Copy the key")
        print()

        api_key = input("Paste your OpenAI API key (or Enter to skip): ").strip()

        if not api_key:
            print("⏭️  Skipped")
            return False

        # Store in vault
        result = subprocess.run([
            "az", "keyvault", "secret", "set",
            "--vault-name", "jarvis-lumina",
            "--name", "openai-api-key",
            "--value", api_key
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ OpenAI API key stored in Azure Key Vault!")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False


    except Exception as e:
        logger.error(f"Error in provision_openai_key: {e}", exc_info=True)
        raise
def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Hybrid TTS System")
        parser.add_argument("--setup", action="store_true", help="Setup TTS API keys")
        parser.add_argument("--status", action="store_true", help="Show system status")
        parser.add_argument("--test", type=str, help="Test with sample text")
        parser.add_argument("--engine", type=str, default="auto", 
                           help="Force specific engine (local, elevenlabs, openai, azure, edge)")

        args = parser.parse_args()

        if args.setup:
            print("\n🎙️  LUMINA Hybrid TTS Setup")
            print("="*70)
            provision_elevenlabs_key()
            provision_openai_key()
            print("\n✅ Setup complete! Run --status to see available engines.")

        elif args.status:
            tts = HybridTTSSystem()
            status = tts.get_status()

            print("\n📊 Hybrid TTS System Status")
            print("="*50)
            print(f"   Best Engine: {status['best_engine']}")
            print(f"\n   Available Engines:")
            for name, info in status["available_engines"].items():
                stars = "⭐" * int(info["quality"])
                print(f"      • {info['name']}: {stars}")

        elif args.test:
            tts = HybridTTSSystem(preferred_engine=args.engine)
            output = Path("output/test_hybrid_tts.mp3")

            print(f"\n🎙️  Testing: \"{args.test}\"")
            print(f"   Engine: {args.engine if args.engine != 'auto' else tts.best_engine}")

            result = tts.synthesize(args.test, output, engine=args.engine)

            if result.get("success"):
                print(f"✅ Success! Engine: {result['engine']}")
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