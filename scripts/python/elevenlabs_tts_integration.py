#!/usr/bin/env python3
"""
ElevenLabs TTS Integration for LUMINA

Best-in-class text-to-speech with:
- Natural pronunciation (no SSML needed)
- No word smooshing
- Professional quality voices
- Voice cloning capability

API Key stored in Azure Key Vault: elevenlabs-api-key

Official Docs: https://elevenlabs.io/docs/overview/intro
Official Python SDK: pip install elevenlabs
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ElevenLabsTTS")

# Try to use official SDK (preferred)
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
    ELEVENLABS_SDK_AVAILABLE = True
except ImportError:
    ELEVENLABS_SDK_AVAILABLE = False
    logger.debug("Official ElevenLabs SDK not installed. Using requests-based approach.")
    logger.debug("   Install with: pip install elevenlabs")

# ElevenLabs API
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Default voices (can be customized)
ELEVENLABS_VOICES = {
    "adam": "pNInz6obpgDQGcFmaJgB",      # Deep male
    "antoni": "ErXwobaYiN019PkySvjV",    # Warm male
    "arnold": "VR6AewLTigWG4xSOukaG",    # Strong male
    "bella": "EXAVITQu4vr4xnSDxMaL",     # Soft female
    "domi": "AZnzlk1XvdvUeBnXmlld",      # Strong female
    "elli": "MF3mGyEYCl7XYWbV9V6O",      # Young female
    "josh": "TxGEqnHWrfWFTfGW9XjX",      # Young male
    "rachel": "21m00Tcm4TlvDq8ikWAM",    # Calm female
    "sam": "yoZ06aMxZJJ28mfd3POQ",       # Raspy male
}

# Recommended voice for LUMINA (professional, clear, engaging)
DEFAULT_VOICE = "josh"  # Young, clear, engaging male voice


class ElevenLabsTTS:
    """
    ElevenLabs TTS Integration

    Best quality TTS with natural pronunciation - no SSML hacking needed.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_api_key_from_vault()
        self.available = bool(self.api_key)

        if self.available:
            logger.info("✅ ElevenLabs TTS initialized")
            self._load_voices()
        else:
            logger.warning("⚠️  ElevenLabs API key not found")

    def _get_api_key_from_vault(self) -> Optional[str]:
        """Get API key from Azure Key Vault"""
        try:
            from azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            # Try different secret names
            for secret_name in ["elevenlabs-api-key", "eleven-labs-api-key", "elevenlabs-key"]:
                try:
                    key = vault_client.get_secret(secret_name)
                    if key:
                        logger.info(f"✅ ElevenLabs API key retrieved from Key Vault ({secret_name})")
                        return key
                except:
                    continue

            return None
        except Exception as e:
            logger.debug(f"Key Vault retrieval failed: {e}")
            return None

    def _load_voices(self):
        """Load available voices from ElevenLabs"""
        try:
            response = requests.get(
                f"{ELEVENLABS_API_URL}/voices",
                headers={"xi-api-key": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                voices = response.json().get("voices", [])
                self.custom_voices = {v["name"]: v["voice_id"] for v in voices}
                logger.info(f"   Loaded {len(voices)} voices")
            else:
                self.custom_voices = {}
        except Exception as e:
            logger.debug(f"Failed to load voices: {e}")
            self.custom_voices = {}

    def get_voice_id(self, voice_name: str) -> str:
        """Get voice ID by name"""
        # Check custom voices first
        if voice_name in self.custom_voices:
            return self.custom_voices[voice_name]

        # Check default voices
        if voice_name.lower() in ELEVENLABS_VOICES:
            return ELEVENLABS_VOICES[voice_name.lower()]

        # Default
        return ELEVENLABS_VOICES[DEFAULT_VOICE]

    def list_voices(self) -> List[Dict[str, Any]]:
        """List all available voices"""
        if not self.available:
            return []

        try:
            response = requests.get(
                f"{ELEVENLABS_API_URL}/voices",
                headers={"xi-api-key": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get("voices", [])
            return []
        except:
            return []

    def synthesize(self, text: str, output_file: Path, 
                   voice: str = DEFAULT_VOICE,
                   model: str = "eleven_multilingual_v2",
                   stability: float = 0.5,
                   similarity_boost: float = 0.75) -> Dict[str, Any]:
        """
        Synthesize speech using ElevenLabs

        Args:
            text: Text to synthesize
            output_file: Output audio file path
            voice: Voice name or ID
            model: TTS model (eleven_multilingual_v2, eleven_monolingual_v1, eleven_turbo_v2_5, eleven_flash_v2_5)
            stability: Voice stability (0-1, lower = more expressive)
            similarity_boost: Voice similarity (0-1, higher = more consistent)

        Returns:
            Dict with success status and metadata
        """
        if not self.available:
            return {"success": False, "error": "ElevenLabs API key not available"}

        voice_id = self.get_voice_id(voice)

        # Preprocess text for natural speech
        processed_text = self._preprocess_text(text)

        # Use official SDK if available (recommended)
        if ELEVENLABS_SDK_AVAILABLE:
            return self._synthesize_with_sdk(processed_text, output_file, voice_id, model, stability, similarity_boost)
        else:
            return self._synthesize_with_requests(processed_text, output_file, voice_id, model, stability, similarity_boost)

    def _synthesize_with_sdk(self, text: str, output_file: Path, voice_id: str,
                            model: str, stability: float, similarity_boost: float) -> Dict[str, Any]:
        """Synthesize using official ElevenLabs Python SDK"""
        try:
            client = ElevenLabs(api_key=self.api_key)

            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=model,
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost
                )
            )

            # Save audio
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)

            file_size = output_file.stat().st_size

            logger.info(f"   ✅ ElevenLabs (SDK): {text[:40]}...")

            return {
                "success": True,
                "output_file": str(output_file),
                "file_size": file_size,
                "voice": voice_id,
                "model": model,
                "characters": len(text),
                "method": "official_sdk"
            }
        except Exception as e:
            logger.error(f"   ❌ ElevenLabs SDK error: {e}")
            return {"success": False, "error": str(e), "method": "official_sdk"}

    def _synthesize_with_requests(self, text: str, output_file: Path, voice_id: str,
                                 model: str, stability: float, similarity_boost: float) -> Dict[str, Any]:
        """Synthesize using requests (fallback if SDK not available)"""
        try:
            response = requests.post(
                f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": model,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                # Save audio
                output_file = Path(output_file)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                file_size = output_file.stat().st_size

                logger.info(f"   ✅ ElevenLabs (requests): {text[:40]}...")

                return {
                    "success": True,
                    "output_file": str(output_file),
                    "file_size": file_size,
                    "voice": voice_id,
                    "model": model,
                    "characters": len(text),
                    "method": "requests"
                }
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error = error_data.get("detail", {}).get("message", response.text) if error_data else response.text
                logger.error(f"   ❌ ElevenLabs error: {error}")
                return {"success": False, "error": error, "method": "requests"}

        except requests.Timeout:
            return {"success": False, "error": "Request timeout", "method": "requests"}
        except Exception as e:
            return {"success": False, "error": str(e), "method": "requests"}

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for ElevenLabs

        Unlike Azure, ElevenLabs handles most pronunciation naturally.
        We just need minimal cleanup.
        """
        processed = text

        # Clean stage directions
        processed = processed.replace("[", "").replace("]", "")

        # LUMINA pronunciation hint (ElevenLabs usually gets it right, but help it)
        # "LUMINA" -> "Loomina" for clearer pronunciation
        for variant in ["LUMINA", "Lumina"]:
            processed = processed.replace(variant, "Loomina")

        # lumina.io -> "Loomina dot I O"
        processed = processed.replace("lumina.io", "Loomina dot I O")

        # AI -> "A.I." for clearer pronunciation
        processed = processed.replace(" AI ", " A.I. ")
        processed = processed.replace(" AI.", " A.I.")
        processed = processed.replace(" AI,", " A.I.,")

        # Clean up
        while "  " in processed:
            processed = processed.replace("  ", " ")

        return processed.strip()

    def get_usage(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        if not self.available:
            return {"error": "Not available"}

        try:
            response = requests.get(
                f"{ELEVENLABS_API_URL}/user/subscription",
                headers={"xi-api-key": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "character_count": data.get("character_count", 0),
                    "character_limit": data.get("character_limit", 0),
                    "tier": data.get("tier", "unknown"),
                    "remaining": data.get("character_limit", 0) - data.get("character_count", 0)
                }
            return {"error": "Failed to get usage"}
        except Exception as e:
            return {"error": str(e)}


def provision_elevenlabs_key():
    """
    MANUS: Add ElevenLabs API key to Azure Key Vault

    Official instructions: https://elevenlabs.io/docs/overview/intro
    """
    import subprocess

    print("\n" + "="*70)
    print("🎤 MANUS: ElevenLabs API Key Provisioning")
    print("="*70)
    print()
    print("📋 Official Setup Steps (from ElevenLabs docs):")
    print()
    print("1. Go to: https://elevenlabs.io")
    print("2. Sign up (FREE tier: 10,000 chars/month)")
    print("3. After login, click your profile icon (bottom left)")
    print("4. Select 'API Keys' from the dropdown")
    print("5. Click 'Create API Key' button")
    print("6. Name it (e.g., 'LUMINA-TTS')")
    print("7. Enable 'Text to Speech' permission")
    print("8. Click 'Create Key'")
    print("9. COPY THE KEY (it's only shown once!)")
    print()
    print("📚 Docs: https://elevenlabs.io/docs/overview/intro")
    print()

    api_key = input("Paste your ElevenLabs API key (or press Enter to skip): ").strip()

    if not api_key:
        print("⏭️  Skipped - no API key provided")
        print()
        print("💡 You can also run:")
        print("   python scripts/python/manus_neo_elevenlabs_simple.py")
        print("   (Launches NEO browser and monitors clipboard)")
        return False

    # Store in Key Vault
    print("\n🔧 Storing in Azure Key Vault...")

    try:
        result = subprocess.run([
            "az", "keyvault", "secret", "set",
            "--vault-name", "jarvis-lumina",
            "--name", "elevenlabs-api-key",
            "--value", api_key
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ ElevenLabs API key stored in Key Vault!")
            print("   Secret name: elevenlabs-api-key")
            print()
            print("🚀 Next steps:")
            print("   - Install official SDK (optional): pip install elevenlabs")
            print("   - Test: python scripts/python/elevenlabs_tts_integration.py --test")
            return True
        else:
            print(f"❌ Failed to store key: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_elevenlabs():
    try:
        """Test ElevenLabs TTS"""
        print("\n🎤 Testing ElevenLabs TTS...")

        tts = ElevenLabsTTS()

        if not tts.available:
            print("❌ ElevenLabs not available")
            print("\nTo set up ElevenLabs, run:")
            print("   python scripts/python/elevenlabs_tts_integration.py --setup")
            return

        # Check usage
        usage = tts.get_usage()
        print(f"\n📊 Usage: {usage.get('character_count', 0):,} / {usage.get('character_limit', 0):,} characters")
        print(f"   Remaining: {usage.get('remaining', 0):,} characters")

        # Test synthesis
        test_text = "Welcome to LUMINA. Where every perspective matters."
        output_file = Path("output/test_elevenlabs.mp3")

        print(f"\n🎙️  Testing: \"{test_text}\"")
        result = tts.synthesize(test_text, output_file)

        if result.get("success"):
            print(f"✅ Success! Audio saved to: {result['output_file']}")
            print(f"   Size: {result['file_size'] / 1024:.1f} KB")
            print(f"   Characters: {result['characters']}")

            # Play it
            import subprocess
            subprocess.run(["start", str(output_file)], shell=True)
        else:
            print(f"❌ Failed: {result.get('error')}")


    except Exception as e:
        logger.error(f"Error in test_elevenlabs: {e}", exc_info=True)
        raise
def main():
    import argparse

    parser = argparse.ArgumentParser(description="ElevenLabs TTS Integration")
    parser.add_argument("--setup", action="store_true", help="Set up ElevenLabs API key")
    parser.add_argument("--test", action="store_true", help="Test ElevenLabs TTS")
    parser.add_argument("--voices", action="store_true", help="List available voices")
    parser.add_argument("--usage", action="store_true", help="Show API usage")

    args = parser.parse_args()

    if args.setup:
        provision_elevenlabs_key()
    elif args.test:
        test_elevenlabs()
    elif args.voices:
        tts = ElevenLabsTTS()
        if tts.available:
            voices = tts.list_voices()
            print(f"\n🎙️  Available Voices ({len(voices)}):\n")
            for v in voices:
                print(f"   {v['name']}: {v['voice_id']}")
        else:
            print("❌ ElevenLabs not available")
    elif args.usage:
        tts = ElevenLabsTTS()
        if tts.available:
            usage = tts.get_usage()
            print(f"\n📊 ElevenLabs Usage:")
            print(f"   Characters used: {usage.get('character_count', 0):,}")
            print(f"   Character limit: {usage.get('character_limit', 0):,}")
            print(f"   Remaining: {usage.get('remaining', 0):,}")
            print(f"   Tier: {usage.get('tier', 'unknown')}")
        else:
            print("❌ ElevenLabs not available")
    else:
        parser.print_help()


if __name__ == "__main__":



    main()