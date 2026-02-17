#!/usr/bin/env python3
"""
JARVIS ElevenLabs Voice Integration

JARVIS voice using ElevenLabs text-to-speech.
High-quality, natural voice for JARVIS.

Tags: #JARVIS #ELEVENLABS #TTS #VOICE @JARVIS @LUMINA
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Azure Key Vault integration (CRITICAL: All API keys must come from Azure Vault)
try:
    from azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False
    AzureKeyVaultClient = None

logger = get_logger("JARVISElevenLabs")

# ElevenLabs
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play, save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    try:
        # Try old API
        from elevenlabs import generate, play, set_api_key, voices, save
        ELEVENLABS_AVAILABLE = True
        ELEVENLABS_NEW_API = False
    except ImportError:
        ELEVENLABS_AVAILABLE = False
        ELEVENLABS_NEW_API = None
        logger.warning("elevenlabs not available - install: pip install elevenlabs")


class JARVISElevenLabsVoice:
    """
    JARVIS Voice using ElevenLabs

    High-quality, natural voice for JARVIS.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ElevenLabs voice"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        self.config_file = self.config_dir / "elevenlabs_config.json"
        self.api_key = None
        self.voice_id = None
        # Use standard model that works with all plans (not Ultron which requires higher tier)
        self.model = "eleven_monolingual_v1"  # Default model - works with all plans

        self._load_config()

        # CRITICAL: Retrieve API key from Azure Vault (NEVER from config files)
        self._retrieve_api_key_from_vault()

        # Initialize client if available
        self.client = None
        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                if 'ElevenLabs' in globals():
                    self.client = ElevenLabs(api_key=self.api_key)
                    logger.info("✅ ElevenLabs client initialized (API key from Azure Vault)")
                else:
                    # Old API
                    set_api_key(self.api_key)
                    logger.info("✅ ElevenLabs API key configured (old API, from Azure Vault)")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not initialize client: {e}")

        # Get available voices
        self.available_voices = []
        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                if self.client:
                    voices_list = self.client.voices.get_all()
                    self.available_voices = [v.name for v in voices_list.voices]
                else:
                    # Old API
                    voices_list = voices()
                    self.available_voices = [v.name for v in voices_list]
                logger.info(f"   ✅ Loaded {len(self.available_voices)} ElevenLabs voices")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load voices: {e}")

        # JARVIS voice settings
        self.jarvis_voice_name = "JARVIS"  # Default voice name
        self.jarvis_voice_id = self._find_jarvis_voice()

        logger.info("✅ JARVIS ElevenLabs Voice initialized")
        if self.jarvis_voice_id:
            logger.info(f"   🎤 JARVIS voice: {self.jarvis_voice_name} ({self.jarvis_voice_id})")
        else:
            logger.info("   ⚠️  JARVIS voice not configured - using default")

    def _load_config(self):
        """Load ElevenLabs configuration (voice settings only, NOT API key)"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # DO NOT load API key from config - it must come from Azure Vault
                    # self.api_key = config.get("api_key")  # REMOVED - Azure Vault only
                    self.voice_id = config.get("voice_id")
                    # Check both "model" and "model_id" keys
                    loaded_model = config.get("model") or config.get("model_id") or "eleven_monolingual_v1"

                    # CRITICAL: Reject "Ultron" or other premium models that don't work with standard plans
                    invalid_models = ["ultron", "ultron_v2", "eleven_turbo_v2_5_ultron"]
                    if loaded_model and loaded_model.lower() in invalid_models:
                        logger.warning(f"   ⚠️  Model '{loaded_model}' not available with current plan - using fallback")
                        self.model = "eleven_monolingual_v1"  # Safe fallback
                    else:
                        self.model = loaded_model if loaded_model else "eleven_monolingual_v1"

                    self.jarvis_voice_name = config.get("jarvis_voice_name", "JARVIS")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")
        else:
            # Create default config (without API key)
            self._save_config()

    def _retrieve_api_key_from_vault(self):
        """
        Retrieve ElevenLabs API key from Azure Key Vault

        CRITICAL: All API keys MUST be retrieved from Azure Vault, never from config files.
        This is a 5+ level importance requirement.
        """
        if not AZURE_VAULT_AVAILABLE:
            logger.warning("   ⚠️  Azure Key Vault not available - cannot retrieve API key")
            return

        try:
            vault_client = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
            self.api_key = vault_client.get_secret("elevenlabs-api-key")
            logger.info("   ✅ ElevenLabs API key retrieved from Azure Vault")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not retrieve API key from Azure Vault: {e}")
            logger.warning("   ⚠️  Make sure 'elevenlabs-api-key' secret exists in Azure Key Vault")
            self.api_key = None

    def _save_config(self):
        """Save ElevenLabs configuration (voice settings only, NOT API key)"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    # DO NOT save API key to config - it must be in Azure Vault only
                    # "api_key": self.api_key,  # REMOVED - Azure Vault only
                    "voice_id": self.voice_id,
                    "model": self.model,
                    "jarvis_voice_name": self.jarvis_voice_name,
                    "note": "API key is stored in Azure Key Vault (secret: 'elevenlabs-api-key'), not in this file"
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving config: {e}")

    def _find_jarvis_voice(self) -> Optional[str]:
        """Find JARVIS voice ID from available voices"""
        if not ELEVENLABS_AVAILABLE or not self.api_key:
            return None

        try:
            if self.client:
                voices_list = self.client.voices.get_all()
                voices_data = voices_list.voices
            else:
                # Old API
                voices_list = voices()
                voices_data = voices_list

            # Look for JARVIS voice by name
            for voice in voices_data:
                voice_name = voice.name if hasattr(voice, 'name') else getattr(voice, 'name', '')
                voice_id = voice.voice_id if hasattr(voice, 'voice_id') else getattr(voice, 'voice_id', '')
                if "jarvis" in voice_name.lower():
                    self.jarvis_voice_name = voice_name
                    return voice_id

            # Use voice_id from config if set
            if self.voice_id:
                return self.voice_id

            # Use first available voice as fallback
            if voices_data:
                first_voice = voices_data[0]
                return first_voice.voice_id if hasattr(first_voice, 'voice_id') else getattr(first_voice, 'voice_id', None)

        except Exception as e:
            logger.debug(f"   Could not find JARVIS voice: {e}")

        return None

    def speak(self, text: str, voice_id: Optional[str] = None, model: Optional[str] = None,
              save_audio: bool = False) -> Optional[bytes]:
        """
        Speak text using ElevenLabs

        Args:
            text: Text to speak
            voice_id: Voice ID (default: JARVIS voice)
            model: Model to use (default: configured model)
            save_audio: Save audio to file

        Returns:
            Audio bytes if save_audio=False, None if playing
        """
        if not ELEVENLABS_AVAILABLE:
            logger.warning("   ⚠️  ElevenLabs not available")
            return None

        if not self.api_key:
            logger.warning("   ⚠️  ElevenLabs API key not configured")
            return None

        try:
            # Use JARVIS voice if not specified
            if not voice_id:
                voice_id = self.jarvis_voice_id

            if not voice_id:
                logger.warning("   ⚠️  No voice ID available")
                return None

            # Use configured model if not specified
            if not model:
                model = self.model

            logger.info(f"   🎤 Speaking: {text[:50]}...")
            logger.info(f"      Voice: {voice_id}")
            logger.info(f"      Model: {model}")

            # Ensure we're using a model that works with the current plan
            # Avoid "Ultron" or other premium models that require higher tier plans
            valid_models = [
                "eleven_monolingual_v1",
                "eleven_multilingual_v1",
                "eleven_turbo_v2",
                "eleven_turbo_v2_5"
            ]
            if model not in valid_models:
                logger.warning(f"   ⚠️  Model '{model}' may not be available with current plan, using fallback")
                model = "eleven_monolingual_v1"  # Safe fallback that works with all plans

            # Generate audio
            try:
                if self.client:
                    # New API
                    audio = self.client.generate(
                        text=text,
                        voice=voice_id,
                        model=model
                    )
                else:
                    # Old API
                    audio = generate(
                        text=text,
                        voice=voice_id,
                        model=model
                    )
            except Exception as model_error:
                # If model error, try with default model
                if "model" in str(model_error).lower() or "plan" in str(model_error).lower():
                    logger.warning(f"   ⚠️  Model error: {model_error}")
                    logger.warning(f"   🔄 Retrying with default model: eleven_monolingual_v1")
                    model = "eleven_monolingual_v1"
                    if self.client:
                        audio = self.client.generate(
                            text=text,
                            voice=voice_id,
                            model=model
                        )
                    else:
                        audio = generate(
                            text=text,
                            voice=voice_id,
                            model=model
                        )
                else:
                    raise  # Re-raise if it's not a model error

            # Play or save
            if save_audio:
                # Save to file
                audio_dir = self.project_root / "data" / "elevenlabs_audio"
                audio_dir.mkdir(parents=True, exist_ok=True)
                audio_file = audio_dir / f"jarvis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                save(audio, str(audio_file))
                logger.info(f"   💾 Saved audio: {audio_file}")
                return audio
            else:
                # Play audio - ALWAYS USE SYSTEM PLAYER FOR AUDIBLE OUTPUT
                # ElevenLabs play() may not work reliably, so use system player directly
                try:
                    import tempfile
                    import subprocess
                    import platform
                    import threading

                    # Save to temp file first (required for system player)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                        tmp_path = tmp_file.name
                        save(audio, str(tmp_path))

                    logger.info(f"   💾 Audio saved to temp file for playback")

                    # Play with system audio player (ALWAYS use this for audible output)
                    system = platform.system()
                    if system == "Windows":
                        # Windows: use start command to play audio audibly through speakers
                        # /MIN = minimized window, /B = background
                        process = subprocess.Popen(['start', '/MIN', '/B', tmp_path], shell=True)
                        logger.info(f"   🔊 Audio playing via Windows start command (AUDIBLE THROUGH SPEAKERS)")
                    elif system == "Darwin":  # macOS
                        subprocess.Popen(['afplay', tmp_path])
                        logger.info(f"   🔊 Audio playing via afplay (AUDIBLE THROUGH SPEAKERS)")
                    else:  # Linux
                        subprocess.Popen(['aplay', tmp_path] if 'aplay' in subprocess.run(['which', 'aplay'], capture_output=True).stdout.decode() else ['mpg123', tmp_path])
                        logger.info(f"   🔊 Audio playing via system player (AUDIBLE THROUGH SPEAKERS)")

                    # Clean up temp file after audio finishes playing
                    def cleanup_temp_file():
                        time.sleep(15)  # Wait 15 seconds for audio to finish
                        try:
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
                                logger.debug(f"   🗑️  Cleaned up temp audio file")
                        except Exception as cleanup_error:
                            logger.debug(f"   Cleanup error: {cleanup_error}")
                    threading.Thread(target=cleanup_temp_file, daemon=True).start()

                    logger.info("   ✅ Audio should be AUDIBLE through speakers now")
                    return None

                except Exception as playback_error:
                    logger.error(f"   ❌ System audio playback failed: {playback_error}")
                    # Last resort: try ElevenLabs play() as fallback
                    try:
                        play(audio)
                        logger.info("   ✅ Audio played via ElevenLabs play() (fallback)")
                    except Exception as final_error:
                        logger.error(f"   ❌ All audio playback methods failed: {final_error}")
                        logger.error("   ❌ AUDIO WILL NOT BE AUDIBLE - check audio system and speakers")
                    return None

        except Exception as e:
            logger.error(f"   ❌ ElevenLabs error: {e}")
            return None

    def set_api_key(self, api_key: str):
        """
        Set ElevenLabs API key in Azure Key Vault

        NOTE: This method stores the API key in Azure Vault, not in local config.
        The key should be retrieved from Azure Vault on initialization.
        """
        if not AZURE_VAULT_AVAILABLE:
            logger.error("   ❌ Azure Key Vault not available - cannot store API key")
            return False

        try:
            vault_client = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
            vault_client.set_secret("elevenlabs-api-key", api_key)
            logger.info("   ✅ API key stored in Azure Key Vault")

            # Also set locally for current session
            self.api_key = api_key
            try:
                if 'ElevenLabs' in globals():
                    self.client = ElevenLabs(api_key=api_key)
                else:
                    set_api_key(api_key)
            except:
                pass

            return True
        except Exception as e:
            logger.error(f"   ❌ Failed to store API key in Azure Vault: {e}")
            return False

    def set_voice(self, voice_id: str, voice_name: str = "JARVIS"):
        """Set JARVIS voice"""
        self.voice_id = voice_id
        self.jarvis_voice_id = voice_id
        self.jarvis_voice_name = voice_name
        self._save_config()
        logger.info(f"   ✅ Voice set: {voice_name} ({voice_id})")

    def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices"""
        if not ELEVENLABS_AVAILABLE or not self.api_key:
            return []

        try:
            if self.client:
                voices_list = self.client.voices.get_all()
                voices_data = voices_list.voices
            else:
                voices_list = voices()
                voices_data = voices_list

            return [
                {
                    "name": v.name if hasattr(v, 'name') else getattr(v, 'name', ''),
                    "voice_id": v.voice_id if hasattr(v, 'voice_id') else getattr(v, 'voice_id', ''),
                    "category": getattr(v, 'category', 'unknown')
                }
                for v in voices_data
            ]
        except Exception as e:
            logger.error(f"   ❌ Error listing voices: {e}")
            return []


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS ElevenLabs Voice")
    parser.add_argument("--speak", type=str, help="Text to speak")
    parser.add_argument("--api-key", type=str, help="Set API key")
    parser.add_argument("--voice", nargs=2, metavar=("VOICE_ID", "VOICE_NAME"),
                       help="Set voice")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--save", action="store_true", help="Save audio instead of playing")
    parser.add_argument("--use-manager", action="store_true", help="Use Voice Service Manager (with fallbacks)")

    args = parser.parse_args()

    # Use Voice Service Manager if requested (recommended - has fallbacks)
    if args.use_manager or args.speak:
        try:
            from jarvis_voice_service_manager import VoiceServiceManager
            manager = VoiceServiceManager()

            if args.speak:
                result = manager.speak(args.speak)
                if result.success:
                    print(f"✅ Spoke using {result.provider}")
                else:
                    print(f"❌ Failed: {result.error}")
            else:
                # Fallback to old implementation for other commands
                voice = JARVISElevenLabsVoice()
                if args.api_key:
                    voice.set_api_key(args.api_key)
                    print("✅ API key set")
                elif args.voice:
                    voice_id, voice_name = args.voice
                    voice.set_voice(voice_id, voice_name)
                    print(f"✅ Voice set: {voice_name}")
                elif args.list_voices:
                    voices_list = voice.list_voices()
                    print("\n🎤 Available ElevenLabs Voices:")
                    print("=" * 80)
                    for v in voices_list:
                        print(f"  • {v['name']} ({v['voice_id']})")
                    print("=" * 80)
                else:
                    parser.print_help()
            return
        except ImportError:
            logger.warning("⚠️  Voice Service Manager not available, using direct ElevenLabs")

    # Original implementation (direct ElevenLabs, no fallbacks)
    voice = JARVISElevenLabsVoice()

    if args.api_key:
        voice.set_api_key(args.api_key)
        print("✅ API key set")

    elif args.voice:
        voice_id, voice_name = args.voice
        voice.set_voice(voice_id, voice_name)
        print(f"✅ Voice set: {voice_name}")

    elif args.list_voices:
        voices_list = voice.list_voices()
        print("\n🎤 Available ElevenLabs Voices:")
        print("=" * 80)
        for v in voices_list:
            print(f"  • {v['name']} ({v['voice_id']})")
        print("=" * 80)

    elif args.speak:
        voice.speak(args.speak, save_audio=args.save)

    else:
        parser.print_help()


if __name__ == "__main__":
    from typing import List


    main()