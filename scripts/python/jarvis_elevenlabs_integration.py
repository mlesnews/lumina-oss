#!/usr/bin/env python3
"""
JARVIS ElevenLabs Integration

Integrates ElevenLabs Text-to-Speech with JARVIS voice interface.
Provides high-quality voice synthesis using ElevenLabs API.

Can be used alongside or instead of Azure Speech SDK TTS.

@JARVIS @ELEVENLABS @TTS @VOICE
"""

import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from elevenlabs_audio_cache import ElevenLabsAudioCache

    ELEVENLABS_CACHE_AVAILABLE = True
except ImportError:
    ElevenLabsAudioCache = None
    ELEVENLABS_CACHE_AVAILABLE = False

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISElevenLabs")

# Try to import ElevenLabs SDK (v2.27.0+ uses client-based API)
try:
    from elevenlabs import play
    from elevenlabs.client import ElevenLabs

    ELEVENLABS_SDK_AVAILABLE = True
    # Try legacy imports for backward compatibility
    try:
        from elevenlabs import generate, set_api_key, voices

        LEGACY_API_AVAILABLE = True
    except ImportError:
        LEGACY_API_AVAILABLE = False
        generate = None
        set_api_key = None
        voices = None
except ImportError:
    ELEVENLABS_SDK_AVAILABLE = False
    LEGACY_API_AVAILABLE = False
    # Only log once to reduce noise (module-level import happens once)
    if not hasattr(logger, "_elevenlabs_warning_logged"):
        logger.warning("ElevenLabs SDK not available - install: pip install elevenlabs")
        logger._elevenlabs_warning_logged = True
    ElevenLabs = None
    play = None
    generate = None
    set_api_key = None
    voices = None


class JARVISElevenLabsTTS:
    """
    ElevenLabs Text-to-Speech integration for JARVIS

    Provides high-quality voice synthesis using ElevenLabs API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize ElevenLabs TTS

        Args:
            api_key: ElevenLabs API key (retrieved from Key Vault if None)
            voice_id: Voice ID to use (default: "21m00Tcm4TlvDq8ikWAM" - Rachel)
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger

        # Get API key from Key Vault if not provided
        # CRITICAL: Azure Key Vault is the PRIMARY source for all secrets, API keys, credentials
        if api_key is None:
            # PRIMARY: Try Azure Key Vault first (as per user requirement)
            self.logger.info("🔐 Retrieving ElevenLabs API key from Azure Key Vault...")
            api_key = self._get_api_key_from_vault()

            # Fallback: Try environment variable only if Key Vault fails
            if not api_key:
                self.logger.debug(
                    "Azure Key Vault retrieval failed, trying environment variable..."
                )
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if api_key:
                    self.logger.warning(
                        "⚠️  Using environment variable - Azure Key Vault should be primary source"
                    )

        self.api_key = api_key

        if not self.api_key:
            self.logger.error("❌ ElevenLabs API key not found - TTS will be disabled")
            self.logger.error("   🔐 CRITICAL: API key should be in Azure Key Vault")
            self.logger.error(
                "   Please add 'elevenlabs-api-key' or 'ElevenLabs-API-Key' to Azure Key Vault"
            )
            self.logger.error(
                "   Azure Key Vault is the PRIMARY source for all secrets, API keys, and credentials"
            )
            # Don't raise error - allow graceful degradation

        # Initialize ElevenLabs client (v2.27.0+ uses client-based API)
        self.client = None
        if self.api_key and ELEVENLABS_SDK_AVAILABLE and ElevenLabs:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                self.logger.info("✅ ElevenLabs client initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize ElevenLabs client: {e}")
                self.api_key = None  # Disable TTS if key is invalid

        # Also try legacy set_api_key for backward compatibility
        if self.api_key and LEGACY_API_AVAILABLE and set_api_key:
            try:
                set_api_key(self.api_key)
                self.logger.info("✅ ElevenLabs API key set (legacy)")
            except Exception as e:
                self.logger.debug(f"Legacy API key set failed: {e}")

        # Default voice (Rachel - clear, professional)
        self.default_voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Rachel
        self.current_voice_id = self.default_voice_id

        # Load available voices
        self.available_voices = {}
        self._load_voices()

        # Optional cache to reduce API usage (50–80% for repeated phrases)
        self._cache = None
        if ELEVENLABS_CACHE_AVAILABLE and ElevenLabsAudioCache and self.api_key:
            try:
                self._cache = ElevenLabsAudioCache(project_root=self.project_root)
            except Exception as e:
                self.logger.debug(f"ElevenLabs cache not used: {e}")

        # Rate limit to avoid burst calls and quota exhaustion
        self._last_speak_time = 0.0
        self._min_speak_interval = 1.0  # seconds between TTS calls

        self.logger.info("🎤 JARVIS ElevenLabs TTS initialized")
        self.logger.info(f"   Voice: {self.current_voice_id}")

    def _get_api_key_from_vault(self) -> Optional[str]:
        """
        Retrieve ElevenLabs API key from triple account management system:
        Azure Key Vault → ProtonPass CLI → Dashlane API CLI

        ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
        """
        try:
            # Try Unified Secrets Manager first (triple account management)
            try:
                from unified_secrets_manager import SecretSource, UnifiedSecretsManager

                secret_manager = UnifiedSecretsManager(project_root=self.project_root)

                # Try multiple secret name variations in order
                # CRITICAL: Azure Key Vault is PRIMARY source - try most common names first
                # MUST be valid Key Vault names: alphanumeric and hyphens only (no underscores or spaces)
                secret_names = [
                    "elevenlabs-api-key",  # Most common name (confirmed working)
                    "ElevenLabs-API-Key",  # Capitalized version (hyphens are ok)
                    "elevenlabs-key",  # Short version
                    "elevenlabs-api-key-jarvis",  # JARVIS-specific
                    "elevenlabs-tts-api-key",  # TTS-specific
                    "cursor-api-key",  # Cursor version
                    "cursor-elevenlabs-api-key",  # Combined
                ]

                for secret_name in secret_names:
                    try:
                        # CRITICAL: Azure Key Vault is PRIMARY source
                        secret = secret_manager.get_secret(
                            secret_name,
                        )
                        if secret:
                            self.logger.info(
                                f"✅ Retrieved ElevenLabs API key from Azure Key Vault (name: {secret_name})"
                            )
                            self.logger.info("   🔐 Source: Azure Key Vault (PRIMARY)")
                            return secret
                    except Exception as e:
                        self.logger.debug(
                            f"Could not retrieve '{secret_name}' from Azure Key Vault: {e}"
                        )
                        continue

                self.logger.warning(
                    "⚠️  ElevenLabs API key not found in Azure Key Vault with any name variation"
                )
                self.logger.warning("   Tried names: " + ", ".join(secret_names[:5]) + "...")

            except ImportError:
                self.logger.debug(
                    "Unified Secrets Manager not available, trying direct Azure Key Vault access"
                )

            # Fallback: Direct Azure Key Vault access (for backward compatibility)
            try:
                try:
                    from azure_service_bus_integration import AzureKeyVaultClient
                except ImportError:
                    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient

                vault_url = os.getenv(
                    "AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/"
                )

                # Set timeout to avoid hanging
                import signal

                timeout_seconds = 5

                try:
                    vault_client = AzureKeyVaultClient(vault_url=vault_url)

                    # Try secret names with timeout protection
                    # CRITICAL: Azure Key Vault is PRIMARY - try most common names first
                    # MUST be valid Key Vault names: alphanumeric and hyphens only
                    secret_names_to_try = [
                        "elevenlabs-api-key",  # Most common (confirmed working)
                        "ElevenLabs-API-Key",  # Capitalized version
                        "elevenlabs-key",
                        "elevenlabs-tts-api-key",
                        "cursor-api-key",
                        "cursor-cursor-api-key",
                        "elevenlabs-api-key-jarvis",
                    ]

                    for secret_name in secret_names_to_try:
                        try:
                            # Use threading timeout to prevent hanging
                            import threading

                            result_container = {"secret": None, "error": None}

                            def get_secret_with_timeout():
                                try:
                                    result_container["secret"] = vault_client.get_secret(
                                        secret_name
                                    )
                                except Exception as e:
                                    result_container["error"] = e

                            thread = threading.Thread(target=get_secret_with_timeout)
                            thread.daemon = True
                            thread.start()
                            thread.join(timeout=timeout_seconds)

                            if thread.is_alive():
                                self.logger.debug(
                                    f"Azure Key Vault request for '{secret_name}' timed out after {timeout_seconds}s"
                                )
                                continue  # Try next secret name

                            if result_container["secret"]:
                                self.logger.info(
                                    f"✅ Retrieved ElevenLabs API key from Azure Key Vault: {secret_name}"
                                )
                                self.logger.info("   🔐 Source: Azure Key Vault (PRIMARY)")
                                return result_container["secret"]
                            elif result_container["error"]:
                                error_msg = str(result_container["error"])
                                # Log more details about the error
                                if "NotFound" in error_msg or "404" in error_msg:
                                    self.logger.debug(
                                        f"Secret '{secret_name}' not found in Azure Key Vault"
                                    )
                                else:
                                    self.logger.debug(
                                        f"Error retrieving '{secret_name}': {error_msg}"
                                    )
                        except Exception as e:
                            self.logger.debug(f"Error trying '{secret_name}': {e}")
                            continue

                    return None
                except Exception as e:
                    self.logger.debug(f"Key Vault client error: {e}")
                    return None
            except ImportError as e:
                self.logger.debug(f"Azure Key Vault client not available: {e}")
                return None
            except Exception as e:
                self.logger.debug(f"Key Vault retrieval error: {e}")
                return None

        except Exception as e:
            self.logger.debug(f"Secret retrieval error: {e}")
            return None

    def _load_voices(self):
        """Load available ElevenLabs voices"""
        if not ELEVENLABS_SDK_AVAILABLE or not voices:
            # Debug level - SDK is optional, system works without it
            self.logger.debug("ElevenLabs SDK not available - cannot load voices")
            return

        try:
            voices_list = voices()
            for voice in voices_list:
                self.available_voices[voice.voice_id] = {
                    "name": voice.name,
                    "category": getattr(voice, "category", "premade"),
                    "description": getattr(voice, "description", ""),
                }
            self.logger.info(f"✅ Loaded {len(self.available_voices)} available voices")
        except Exception as e:
            self.logger.error(f"Error loading voices: {e}")

    def speak(
        self, text: str, voice_id: Optional[str] = None, model: str = "eleven_multilingual_v2"
    ) -> bool:
        """
        Speak text using ElevenLabs TTS

        Args:
            text: Text to speak
            voice_id: Voice ID to use (uses current voice if None)
            model: Model to use (default: eleven_multilingual_v2)

        Returns:
            True if successful
        """
        if not ELEVENLABS_SDK_AVAILABLE:
            self.logger.debug("ElevenLabs SDK not available")
            return False

        if not self.api_key:
            self.logger.debug("ElevenLabs API key not configured - TTS disabled")
            return False

        if not text or not text.strip():
            return False

        voice_to_use = voice_id or self.current_voice_id

        # Rate limit to avoid burst calls and quota exhaustion
        now = time.monotonic()
        elapsed = now - self._last_speak_time
        if elapsed < self._min_speak_interval:
            time.sleep(self._min_speak_interval - elapsed)
        self._last_speak_time = time.monotonic()

        try:
            # Cache: play from cache if available to reduce API usage
            if self._cache:
                cached_path = self._cache.get_cached_audio(text, voice_to_use)
                if cached_path and cached_path.exists():
                    with open(cached_path, "rb") as f:
                        audio_bytes = f.read()
                    if play:
                        try:
                            play(audio_bytes)
                            self.logger.debug("✅ Played from cache")
                            return True
                        except Exception as e:
                            self.logger.debug(f"Cache play failed, falling back to API: {e}")
                    # If play failed, fall through to API

            self.logger.info(f"🗣️  Speaking with ElevenLabs (voice: {voice_to_use})...")

            # Use new client-based API (v2.27.0+)
            # CRITICAL: Use text_to_speech.convert() not client.generate()
            if self.client:
                # Generate audio using text_to_speech.convert()
                audio = self.client.text_to_speech.convert(
                    text=text, voice_id=voice_to_use, model_id=model, output_format="mp3_44100_128"
                )
                # Audio is already bytes/generator - convert to bytes if needed
                if hasattr(audio, "__iter__") and not isinstance(audio, (bytes, str)):
                    audio = b"".join(audio)
            elif LEGACY_API_AVAILABLE and generate:
                # Fallback to legacy API
                audio = generate(text=text, voice=voice_to_use, model=model)
            else:
                self.logger.error("❌ Neither new nor legacy ElevenLabs API available")
                return False

            # Cache the result for future use
            tmp_path = None
            if self._cache and isinstance(audio, bytes):
                try:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        tmp.write(audio)
                        tmp_path = Path(tmp.name)
                    self._cache.cache_audio(text, voice_to_use, tmp_path)
                except Exception as e:
                    self.logger.debug(f"Could not cache audio: {e}")
                finally:
                    if tmp_path and tmp_path.exists():
                        try:
                            tmp_path.unlink()
                        except OSError:
                            pass

            # Play audio using ElevenLabs play() function (handles MP3 properly)
            if play:
                try:
                    play(audio)
                    self.logger.info("✅ Played audio using ElevenLabs play()")
                except Exception as e:
                    self.logger.error(f"❌ ElevenLabs play() failed: {e}")
                    # Fallback: Try pydub
                    try:
                        from io import BytesIO

                        from pydub import AudioSegment
                        from pydub.playback import play as pydub_play

                        # Ensure audio is bytes
                        if hasattr(audio, "__iter__") and not isinstance(audio, (bytes, str)):
                            audio = b"".join(audio)

                        audio_segment = AudioSegment.from_mp3(BytesIO(audio))
                        pydub_play(audio_segment)
                        self.logger.info("✅ Played audio using pydub (fallback)")
                    except Exception as e2:
                        self.logger.error(f"❌ pydub fallback also failed: {e2}")
            else:
                self.logger.warning("⚠️  play() not available - audio generated but not played")
                self.logger.warning("   Install: pip install elevenlabs")

            self.logger.info(f"✅ Spoke: {text[:50]}...")
            return True

        except Exception as e:
            err_str = str(e).lower()
            if "429" in str(e) or "quota" in err_str or "rate" in err_str or "limit" in err_str:
                self.logger.warning("⚠️  ElevenLabs quota/rate limit - fallback to SAPI recommended")
                return False
            self.logger.error(f"❌ ElevenLabs TTS error: {e}", exc_info=True)
            return False

    def speak_to_file(
        self,
        text: str,
        output_file: Path,
        voice_id: Optional[str] = None,
        model: str = "eleven_multilingual_v2",
    ) -> bool:
        """
        Generate speech audio and save to file

        Args:
            text: Text to speak
            output_file: Path to save audio file
            voice_id: Voice ID to use
            model: Model to use

        Returns:
            True if successful
        """
        if not ELEVENLABS_SDK_AVAILABLE:
            self.logger.error("❌ ElevenLabs SDK not available")
            return False

        voice_to_use = voice_id or self.current_voice_id

        try:
            self.logger.info("🗣️  Generating audio file with ElevenLabs...")

            # Generate audio using new client API or legacy API
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if self.client:
                # Use new client-based API (v2.27.0+)
                # CRITICAL: Use text_to_speech.convert() not client.generate()
                audio = self.client.text_to_speech.convert(
                    text=text, voice_id=voice_to_use, model_id=model, output_format="mp3_44100_128"
                )
                # Save to file
                with open(output_file, "wb") as f:
                    # Audio may be bytes or generator
                    if isinstance(audio, bytes):
                        f.write(audio)
                    else:
                        for chunk in audio:
                            f.write(chunk)
            elif LEGACY_API_AVAILABLE and generate:
                # Fallback to legacy API
                audio = generate(text=text, voice=voice_to_use, model=model)
                # Save to file
                with open(output_file, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)
            else:
                self.logger.error("❌ Neither new nor legacy ElevenLabs API available")
                return False

            self.logger.info(f"✅ Saved audio to: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"❌ ElevenLabs TTS file generation error: {e}", exc_info=True)
            return False

    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use for TTS

        Args:
            voice_id: ElevenLabs voice ID

        Returns:
            True if voice is valid and set
        """
        if voice_id in self.available_voices:
            self.current_voice_id = voice_id
            self.logger.info(
                f"✅ Voice set to: {self.available_voices[voice_id]['name']} ({voice_id})"
            )
            return True
        else:
            self.logger.warning(f"⚠️  Voice ID not found: {voice_id}")
            # Still set it in case it's a valid ID we haven't loaded
            self.current_voice_id = voice_id
            return False

    def list_voices(self) -> Dict[str, Dict[str, str]]:
        """List all available voices"""
        return self.available_voices

    def get_current_voice_info(self) -> Dict[str, Any]:
        """Get information about the current voice"""
        if self.current_voice_id in self.available_voices:
            info = self.available_voices[self.current_voice_id].copy()
            info["voice_id"] = self.current_voice_id
            return info
        else:
            return {"voice_id": self.current_voice_id, "name": "Unknown", "category": "Unknown"}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS ElevenLabs TTS Integration")
    parser.add_argument("--text", type=str, help="Text to speak")
    parser.add_argument("--voice", type=str, help="Voice ID to use")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--api-key", type=str, help="ElevenLabs API key")

    args = parser.parse_args()

    try:
        tts = JARVISElevenLabsTTS(api_key=args.api_key, voice_id=args.voice)

        if args.list_voices:
            voices = tts.list_voices()
            print("\nAvailable ElevenLabs Voices:")
            print("=" * 80)
            for voice_id, info in voices.items():
                print(f"  {voice_id}: {info['name']} ({info.get('category', 'unknown')})")
                if info.get("description"):
                    print(f"    {info['description']}")

        elif args.text:
            success = tts.speak(args.text, voice_id=args.voice)
            if success:
                print("✅ Spoke successfully")
            else:
                print("❌ Failed to speak")

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
