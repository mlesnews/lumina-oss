#!/usr/bin/env python3
"""
JARVIS Voice Service Manager

Manages voice services with ElevenLabs as primary and automatic fallback chain.
Implements the voice services framework: ElevenLabs Primary + Fallbacks.

Tags: #JARVIS #VOICE_SERVICES #ELEVENLABS #FRAMEWORK #FALLBACK @JARVIS @LUMINA #PEAK
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

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

# Azure Key Vault integration
try:
    from azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False
    AzureKeyVaultClient = None

logger = get_logger("JARVISVoiceServiceManager")


@dataclass
class VoiceServiceResult:
    """Result from voice service operation"""
    success: bool
    provider: str
    latency_ms: float
    error: Optional[str] = None
    audio_data: Optional[bytes] = None


class VoiceService(ABC):
    """Base voice service interface"""

    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority
        self.enabled = True
        self.logger = get_logger(f"VoiceService.{name}")

    @abstractmethod
    def is_available(self) -> bool:
        """Check if service is available"""
        pass

    @abstractmethod
    def speak(self, text: str) -> VoiceServiceResult:
        """Speak text - returns result"""
        pass

    def get_quality(self) -> float:
        """Get service quality score (0.0-1.0)"""
        # Default quality based on priority (higher priority = better quality)
        return max(0.0, 1.0 - (self.priority - 1) * 0.15)


class ElevenLabsVoiceService(VoiceService):
    """ElevenLabs voice service (Primary)"""

    def __init__(self):
        super().__init__("ElevenLabs", priority=1)
        self.api_key = None
        self.client = None
        self.voice_id = None
        self.model = "eleven_multilingual_v2"
        self._initialize()

    def _initialize(self):
        """Initialize ElevenLabs client"""
        # Try to import ElevenLabs
        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs import play, save
            self.ELEVENLABS_AVAILABLE = True
            self.ElevenLabs = ElevenLabs
            self.play = play
            self.save = save
        except ImportError:
            try:
                from elevenlabs import generate, play, set_api_key, voices, save
                self.ELEVENLABS_AVAILABLE = True
                self.ELEVENLABS_NEW_API = False
                self.generate = generate
                self.play = play
                self.set_api_key = set_api_key
                self.voices = voices
                self.save = save
            except ImportError:
                self.ELEVENLABS_AVAILABLE = False
                self.logger.warning("elevenlabs not available - install: pip install elevenlabs")
                return

        # Retrieve API key from Azure Vault
        if AZURE_VAULT_AVAILABLE:
            try:
                vault_client = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
                self.api_key = vault_client.get_secret("elevenlabs-api-key")
                self.logger.info("✅ ElevenLabs API key retrieved from Azure Vault")
            except Exception as e:
                self.logger.warning(f"⚠️  Could not retrieve API key from Azure Vault: {e}")
                self.api_key = None

        # Initialize client
        if self.ELEVENLABS_AVAILABLE and self.api_key:
            try:
                if hasattr(self, 'ElevenLabs'):
                    self.client = self.ElevenLabs(api_key=self.api_key)
                    self.logger.info("✅ ElevenLabs client initialized")
                else:
                    self.set_api_key(self.api_key)
                    self.logger.info("✅ ElevenLabs API key configured (old API)")
            except Exception as e:
                self.logger.warning(f"⚠️  Could not initialize client: {e}")

        # Load config for voice settings
        config_file = project_root / "config" / "elevenlabs_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.voice_id = config.get("voice_id")
                    self.model = config.get("model_id", "eleven_multilingual_v2")
            except Exception as e:
                self.logger.debug(f"Could not load config: {e}")

    def is_available(self) -> bool:
        """Check if ElevenLabs is available"""
        return (self.ELEVENLABS_AVAILABLE and
                self.api_key is not None and
                self.enabled)

    def speak(self, text: str) -> VoiceServiceResult:
        """Speak text using ElevenLabs"""
        start_time = time.time()

        if not self.is_available():
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=0,
                error="ElevenLabs not available"
            )

        try:
            # Use configured voice or find JARVIS voice
            voice_id = self.voice_id
            if not voice_id:
                # Try to find JARVIS voice
                try:
                    if self.client:
                        voices_list = self.client.voices.get_all()
                        for voice in voices_list.voices:
                            if "jarvis" in voice.name.lower():
                                voice_id = voice.voice_id
                                break
                    else:
                        voices_list = self.voices()
                        for voice in voices_list:
                            if "jarvis" in voice.name.lower():
                                voice_id = voice.voice_id
                                break
                except:
                    pass

            if not voice_id:
                return VoiceServiceResult(
                    success=False,
                    provider=self.name,
                    latency_ms=(time.time() - start_time) * 1000,
                    error="No voice ID available"
                )

            # Generate audio
            if self.client:
                # New API
                audio = self.client.generate(
                    text=text,
                    voice=voice_id,
                    model=self.model
                )
            else:
                # Old API
                audio = self.generate(
                    text=text,
                    voice=voice_id,
                    model=self.model
                )

            # Play audio
            self.play(audio)

            latency_ms = (time.time() - start_time) * 1000
            self.logger.info(f"✅ Spoke using {self.name} (latency: {latency_ms:.0f}ms)")

            return VoiceServiceResult(
                success=True,
                provider=self.name,
                latency_ms=latency_ms,
                audio_data=audio if hasattr(audio, '__bytes__') else None
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.warning(f"⚠️  {self.name} failed: {e}")
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=latency_ms,
                error=str(e)
            )


class WindowsTTSVoiceService(VoiceService):
    """Windows Speech API TTS (Fallback 1)"""

    def __init__(self):
        super().__init__("Windows TTS", priority=2)
        self.engine = None
        self._initialize()

    def _initialize(self):
        """Initialize Windows TTS"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.logger.info("✅ Windows TTS initialized")
        except ImportError:
            self.logger.warning("⚠️  pyttsx3 not available - install: pip install pyttsx3")
        except Exception as e:
            self.logger.warning(f"⚠️  Could not initialize Windows TTS: {e}")

    def is_available(self) -> bool:
        """Check if Windows TTS is available"""
        return self.engine is not None and self.enabled

    def speak(self, text: str) -> VoiceServiceResult:
        """Speak text using Windows TTS"""
        start_time = time.time()

        if not self.is_available():
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=0,
                error="Windows TTS not available"
            )

        try:
            self.engine.say(text)
            self.engine.runAndWait()

            latency_ms = (time.time() - start_time) * 1000
            self.logger.info(f"✅ Spoke using {self.name} (latency: {latency_ms:.0f}ms)")

            return VoiceServiceResult(
                success=True,
                provider=self.name,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.warning(f"⚠️  {self.name} failed: {e}")
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=latency_ms,
                error=str(e)
            )


class AzureSpeechVoiceService(VoiceService):
    """Azure Cognitive Services Speech (Fallback 2)"""

    def __init__(self):
        super().__init__("Azure Speech", priority=3)
        self.speech_config = None
        self.synthesizer = None
        self._initialize()

    def _initialize(self):
        """Initialize Azure Speech"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            self.speechsdk = speechsdk

            # Retrieve API key from Azure Vault
            if AZURE_VAULT_AVAILABLE:
                try:
                    vault_client = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
                    api_key = vault_client.get_secret("azure-speech-api-key")
                    region = "eastus"  # Default region

                    self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
                    self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
                    self.logger.info("✅ Azure Speech initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️  Could not initialize Azure Speech: {e}")
        except ImportError:
            self.logger.warning("⚠️  azure-cognitiveservices-speech not available")
        except Exception as e:
            self.logger.warning(f"⚠️  Could not initialize Azure Speech: {e}")

    def is_available(self) -> bool:
        """Check if Azure Speech is available"""
        return self.synthesizer is not None and self.enabled

    def speak(self, text: str) -> VoiceServiceResult:
        """Speak text using Azure Speech"""
        start_time = time.time()

        if not self.is_available():
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=0,
                error="Azure Speech not available"
            )

        try:
            result = self.synthesizer.speak_text_async(text).get()

            if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
                latency_ms = (time.time() - start_time) * 1000
                self.logger.info(f"✅ Spoke using {self.name} (latency: {latency_ms:.0f}ms)")

                return VoiceServiceResult(
                    success=True,
                    provider=self.name,
                    latency_ms=latency_ms,
                    audio_data=result.audio_data
                )
            else:
                error_msg = f"Synthesis failed: {result.reason}"
                latency_ms = (time.time() - start_time) * 1000
                return VoiceServiceResult(
                    success=False,
                    provider=self.name,
                    latency_ms=latency_ms,
                    error=error_msg
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.warning(f"⚠️  {self.name} failed: {e}")
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=latency_ms,
                error=str(e)
            )


class SystemTTSVoiceService(VoiceService):
    """System Default TTS (Last Resort)"""

    def __init__(self):
        super().__init__("System TTS", priority=5)
        self.enabled = True  # Always enabled as last resort

    def is_available(self) -> bool:
        """System TTS is always available"""
        return self.enabled

    def speak(self, text: str) -> VoiceServiceResult:
        """Speak text using system TTS"""
        start_time = time.time()

        try:
            import platform
            system = platform.system()

            if system == "Windows":
                import subprocess
                # Use Windows SAPI via PowerShell
                subprocess.run([
                    "powershell", "-Command",
                    f"Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak('{text}')"
                ], check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["say", text], check=True)
            elif system == "Linux":
                subprocess.run(["espeak", text], check=True)
            else:
                return VoiceServiceResult(
                    success=False,
                    provider=self.name,
                    latency_ms=(time.time() - start_time) * 1000,
                    error=f"Unsupported system: {system}"
                )

            latency_ms = (time.time() - start_time) * 1000
            self.logger.info(f"✅ Spoke using {self.name} (latency: {latency_ms:.0f}ms)")

            return VoiceServiceResult(
                success=True,
                provider=self.name,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.warning(f"⚠️  {self.name} failed: {e}")
            return VoiceServiceResult(
                success=False,
                provider=self.name,
                latency_ms=latency_ms,
                error=str(e)
            )


class VoiceServiceManager:
    """
    Manages voice services with ElevenLabs primary and automatic fallback chain.

    Framework: ElevenLabs Primary + Fallbacks
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Voice Service Manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" / "voice_services"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("VoiceServiceManager")

        # Initialize services in priority order
        self.services: List[VoiceService] = [
            ElevenLabsVoiceService(),      # Primary (Priority 1)
            WindowsTTSVoiceService(),      # Fallback 1 (Priority 2)
            AzureSpeechVoiceService(),     # Fallback 2 (Priority 3)
            SystemTTSVoiceService()        # Last Resort (Priority 5)
        ]

        # Load configuration
        self.config_file = self.config_dir / "voice_services_config.json"
        self._load_config()

        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "provider_usage": {},
            "fallback_count": 0
        }

        self.logger.info("✅ Voice Service Manager initialized")
        self.logger.info(f"   Primary: ElevenLabs")
        self.logger.info(f"   Fallbacks: {len(self.services) - 1} providers")

    def _load_config(self):
        """Load voice services configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    # Enable/disable services based on config
                    for service in self.services:
                        service.enabled = config.get("fallbacks", {}).get(service.name.lower().replace(" ", "_"), {}).get("enabled", True)
            except Exception as e:
                self.logger.warning(f"⚠️  Could not load config: {e}")
        else:
            # Create default config
            self._save_config()

    def _save_config(self):
        """Save voice services configuration"""
        try:
            config = {
                "version": "1.0.0",
                "primary": "elevenlabs",
                "fallbacks": {
                    service.name.lower().replace(" ", "_"): {
                        "priority": service.priority,
                        "enabled": service.enabled
                    }
                    for service in self.services[1:]  # Skip primary
                }
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Error saving config: {e}")

    def speak(self, text: str, preferred_provider: Optional[str] = None) -> VoiceServiceResult:
        """
        Speak text with automatic fallback chain.

        Args:
            text: Text to speak
            preferred_provider: Preferred provider name (optional)

        Returns:
            VoiceServiceResult with success status and provider used
        """
        self.stats["total_requests"] += 1

        # Sort services by priority (or preferred provider first)
        services_to_try = self.services.copy()

        if preferred_provider:
            # Move preferred provider to front
            preferred = [s for s in services_to_try if s.name.lower() == preferred_provider.lower()]
            others = [s for s in services_to_try if s.name.lower() != preferred_provider.lower()]
            services_to_try = preferred + others

        # Try each service in order
        for i, service in enumerate(services_to_try):
            if not service.is_available():
                self.logger.debug(f"⏭️  Skipping {service.name} (not available)")
                continue

            try:
                result = service.speak(text)

                if result.success:
                    # Track statistics
                    self.stats["successful"] += 1
                    provider_name = result.provider
                    if provider_name not in self.stats["provider_usage"]:
                        self.stats["provider_usage"][provider_name] = 0
                    self.stats["provider_usage"][provider_name] += 1

                    # Log fallback if not primary
                    if i > 0:
                        self.stats["fallback_count"] += 1
                        self.logger.info(f"🔄 Used fallback: {provider_name}")

                    # Log decision
                    self._log_decision(text, result, i > 0)

                    return result
                else:
                    self.logger.debug(f"⚠️  {service.name} failed: {result.error}")
                    continue

            except Exception as e:
                self.logger.warning(f"⚠️  {service.name} exception: {e}")
                continue

        # All services failed
        self.stats["failed"] += 1
        self.logger.error("❌ All voice services failed")

        return VoiceServiceResult(
            success=False,
            provider="None",
            latency_ms=0,
            error="All voice services failed"
        )

    def _log_decision(self, text: str, result: VoiceServiceResult, was_fallback: bool):
        """Log voice service decision for transparency"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "text_preview": text[:50] + "..." if len(text) > 50 else text,
            "provider": result.provider,
            "success": result.success,
            "latency_ms": result.latency_ms,
            "was_fallback": was_fallback,
            "error": result.error
        }

        log_file = self.data_dir / "voice_service_logs.jsonl"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.debug(f"Could not log decision: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get voice service statistics"""
        return {
            **self.stats,
            "success_rate": (self.stats["successful"] / self.stats["total_requests"] * 100)
                           if self.stats["total_requests"] > 0 else 0,
            "fallback_rate": (self.stats["fallback_count"] / self.stats["total_requests"] * 100)
                            if self.stats["total_requests"] > 0 else 0
        }

    def list_available_services(self) -> List[Dict[str, Any]]:
        """List available voice services"""
        return [
            {
                "name": service.name,
                "priority": service.priority,
                "available": service.is_available(),
                "enabled": service.enabled,
                "quality": service.get_quality()
            }
            for service in self.services
        ]


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Voice Service Manager")
    parser.add_argument("--speak", type=str, help="Text to speak")
    parser.add_argument("--provider", type=str, help="Preferred provider")
    parser.add_argument("--list", action="store_true", help="List available services")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    manager = VoiceServiceManager()

    if args.list:
        services = manager.list_available_services()
        print("\n🎤 Available Voice Services:")
        print("=" * 80)
        for service in services:
            status = "✅" if service["available"] else "❌"
            print(f"  {status} {service['name']} (Priority: {service['priority']}, Quality: {service['quality']:.2f})")
        print("=" * 80)

    elif args.stats:
        stats = manager.get_stats()
        print("\n📊 Voice Service Statistics:")
        print("=" * 80)
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Fallback Rate: {stats['fallback_rate']:.1f}%")
        print(f"\n  Provider Usage:")
        for provider, count in stats['provider_usage'].items():
            print(f"    • {provider}: {count}")
        print("=" * 80)

    elif args.speak:
        result = manager.speak(args.speak, preferred_provider=args.provider)
        if result.success:
            print(f"✅ Spoke using {result.provider} (latency: {result.latency_ms:.0f}ms)")
        else:
            print(f"❌ Failed: {result.error}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()