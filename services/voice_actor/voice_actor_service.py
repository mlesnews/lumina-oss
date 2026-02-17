#!/usr/bin/env python3
"""
Lumina Voice Actor Service

Unified voice synthesis and recognition service that integrates:
- ElevenLabs TTS (primary, high-quality)
- Windows SAPI (fallback)
- NVIDIA Audio2Face (optional, for avatar lip-sync)
- Whisper (local STT)
- Azure Speech (cloud STT/TTS)

Supports multiple voice personas for different AI characters.

@JARVIS @VOICE @ELEVENLABS @NVIDIA @TTS @STT
"""

import base64
import hashlib
import json
import logging
import os
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn

# FastAPI for service
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-actor")

# Project root for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))


class VoiceProvider(Enum):
    ELEVENLABS = "elevenlabs"
    AZURE = "azure"
    SAPI = "sapi"  # Windows SAPI
    NVIDIA = "nvidia"  # Audio2Face


class STTProvider(Enum):
    WHISPER_LOCAL = "whisper_local"
    WHISPER_API = "whisper_api"
    AZURE = "azure"
    WEB_SPEECH = "web_speech"


@dataclass
class VoicePersona:
    """Represents a voice character/persona."""

    id: str
    name: str
    description: str
    provider: VoiceProvider
    voice_id: str  # Provider-specific voice ID
    settings: Dict[str, Any] = field(default_factory=dict)
    avatar_config: Optional[Dict] = None  # For NVIDIA Audio2Face


@dataclass
class VoiceConfig:
    """Voice actor service configuration."""

    default_tts_provider: VoiceProvider = VoiceProvider.ELEVENLABS
    fallback_tts_provider: VoiceProvider = VoiceProvider.SAPI
    default_stt_provider: STTProvider = STTProvider.WHISPER_LOCAL
    cache_enabled: bool = True
    cache_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "voice_cache")
    max_cache_size_mb: int = 500
    personas: Dict[str, VoicePersona] = field(default_factory=dict)


# Default personas
DEFAULT_PERSONAS = {
    "jarvis": VoicePersona(
        id="jarvis",
        name="JARVIS",
        description="Just A Rather Very Intelligent System - Primary AI assistant",
        provider=VoiceProvider.ELEVENLABS,
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel (closest to JARVIS tone)
        settings={
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    ),
    "friday": VoicePersona(
        id="friday",
        name="F.R.I.D.A.Y.",
        description="Female Replacement Intelligent Digital Assistant Youth",
        provider=VoiceProvider.ELEVENLABS,
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Bella
        settings={"stability": 0.6, "similarity_boost": 0.8, "style": 0.2},
    ),
    "ultron": VoicePersona(
        id="ultron",
        name="ULTRON",
        description="Local AI supermodel voice",
        provider=VoiceProvider.ELEVENLABS,
        voice_id="VR6AewLTigWG4xSOukaG",  # Arnold
        settings={"stability": 0.4, "similarity_boost": 0.7, "style": 0.3},
    ),
    "system": VoicePersona(
        id="system",
        name="System",
        description="Neutral system announcements",
        provider=VoiceProvider.SAPI,
        voice_id="Microsoft David Desktop",
        settings={},
    ),
}


class VoiceActorService:
    """Main voice actor service."""

    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.config.personas = DEFAULT_PERSONAS.copy()
        self._elevenlabs_client = None
        self._cache: Dict[str, Path] = {}
        self._load_cache_index()

    def _load_cache_index(self):
        """Load cache index from disk."""
        index_path = self.config.cache_dir / "index.json"
        if index_path.exists():
            with open(index_path) as f:
                self._cache = {k: Path(v) for k, v in json.load(f).items()}

    def _save_cache_index(self):
        """Save cache index to disk."""
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)
        index_path = self.config.cache_dir / "index.json"
        with open(index_path, "w") as f:
            json.dump({k: str(v) for k, v in self._cache.items()}, f)

    def _get_cache_key(self, text: str, persona_id: str) -> str:
        """Generate cache key for text + persona."""
        content = f"{persona_id}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_elevenlabs_client(self):
        """Get or create ElevenLabs client."""
        if self._elevenlabs_client is None:
            try:
                from elevenlabs.client import ElevenLabs

                api_key = os.environ.get("ELEVENLABS_API_KEY")
                if not api_key:
                    # Try to get from Azure Key Vault
                    try:
                        from jarvis_keyvault_utils import get_secret_from_vault

                        api_key = get_secret_from_vault("elevenlabs-api-key")
                    except:
                        pass
                if api_key:
                    self._elevenlabs_client = ElevenLabs(api_key=api_key)
                else:
                    logger.warning("ElevenLabs API key not available")
            except ImportError:
                logger.warning("ElevenLabs SDK not installed")
        return self._elevenlabs_client

    async def synthesize(
        self, text: str, persona_id: str = "jarvis", use_cache: bool = True, stream: bool = False
    ) -> Optional[bytes]:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            persona_id: Voice persona to use
            use_cache: Whether to use/store in cache
            stream: Return streaming audio

        Returns:
            Audio bytes (MP3 format)
        """
        persona = self.config.personas.get(persona_id)
        if not persona:
            persona = self.config.personas["jarvis"]

        # Check cache
        if use_cache and self.config.cache_enabled:
            cache_key = self._get_cache_key(text, persona_id)
            if cache_key in self._cache:
                cache_path = self._cache[cache_key]
                if cache_path.exists():
                    logger.info(f"Cache hit for {persona_id}: {text[:30]}...")
                    return cache_path.read_bytes()

        # Synthesize based on provider
        audio_data = None

        if persona.provider == VoiceProvider.ELEVENLABS:
            audio_data = await self._synthesize_elevenlabs(text, persona)
        elif persona.provider == VoiceProvider.AZURE:
            audio_data = await self._synthesize_azure(text, persona)
        elif persona.provider == VoiceProvider.SAPI:
            audio_data = await self._synthesize_sapi(text, persona)

        # Fallback if primary fails
        if audio_data is None and self.config.fallback_tts_provider != persona.provider:
            logger.warning("Primary TTS failed, using fallback")
            fallback_persona = VoicePersona(
                id="fallback",
                name="Fallback",
                description="Fallback voice",
                provider=self.config.fallback_tts_provider,
                voice_id="Microsoft David Desktop",
                settings={},
            )
            audio_data = await self._synthesize_sapi(text, fallback_persona)

        # Cache result
        if audio_data and use_cache and self.config.cache_enabled:
            cache_key = self._get_cache_key(text, persona_id)
            cache_path = self.config.cache_dir / f"{cache_key}.mp3"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(audio_data)
            self._cache[cache_key] = cache_path
            self._save_cache_index()

        return audio_data

    async def _synthesize_elevenlabs(self, text: str, persona: VoicePersona) -> Optional[bytes]:
        """Synthesize using ElevenLabs."""
        client = self._get_elevenlabs_client()
        if not client:
            return None

        try:
            audio = client.generate(
                text=text,
                voice=persona.voice_id,
                model="eleven_multilingual_v2",
                voice_settings={
                    "stability": persona.settings.get("stability", 0.5),
                    "similarity_boost": persona.settings.get("similarity_boost", 0.75),
                    "style": persona.settings.get("style", 0.0),
                    "use_speaker_boost": persona.settings.get("use_speaker_boost", True),
                },
            )
            # Collect generator output
            if hasattr(audio, "__iter__"):
                return b"".join(chunk for chunk in audio)
            return audio
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            return None

    async def _synthesize_azure(self, text: str, persona: VoicePersona) -> Optional[bytes]:
        """Synthesize using Azure Speech."""
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_key = os.environ.get("AZURE_SPEECH_KEY")
            speech_region = os.environ.get("AZURE_SPEECH_REGION", "eastus")

            if not speech_key:
                return None

            config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
            config.speech_synthesis_voice_name = persona.voice_id or "en-US-GuyNeural"

            synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
        except Exception as e:
            logger.error(f"Azure synthesis failed: {e}")
        return None

    async def _synthesize_sapi(self, text: str, persona: VoicePersona) -> Optional[bytes]:
        """Synthesize using Windows SAPI."""
        try:
            import pyttsx3

            engine = pyttsx3.init()

            # Set voice if specified
            if persona.voice_id:
                voices = engine.getProperty("voices")
                for voice in voices:
                    if persona.voice_id in voice.name:
                        engine.setProperty("voice", voice.id)
                        break

            # Save to temp file (pyttsx3 doesn't support direct bytes output)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            engine.save_to_file(text, temp_path)
            engine.runAndWait()

            # Read and return
            audio_data = Path(temp_path).read_bytes()
            Path(temp_path).unlink()
            return audio_data
        except Exception as e:
            logger.error(f"SAPI synthesis failed: {e}")
        return None

    async def transcribe(
        self, audio_data: bytes, provider: Optional[STTProvider] = None
    ) -> Optional[str]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes (WAV format preferred)
            provider: STT provider to use

        Returns:
            Transcribed text
        """
        provider = provider or self.config.default_stt_provider

        if provider == STTProvider.WHISPER_LOCAL:
            return await self._transcribe_whisper_local(audio_data)
        elif provider == STTProvider.WHISPER_API:
            return await self._transcribe_whisper_api(audio_data)
        elif provider == STTProvider.AZURE:
            return await self._transcribe_azure(audio_data)

        return None

    async def _transcribe_whisper_local(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using local Whisper model."""
        try:
            import whisper

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            model = whisper.load_model("base")
            result = model.transcribe(temp_path)

            Path(temp_path).unlink()
            return result.get("text", "")
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
        return None

    async def _transcribe_whisper_api(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using OpenAI Whisper API."""
        try:
            import openai

            client = openai.OpenAI()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            with open(temp_path, "rb") as audio_file:
                result = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

            Path(temp_path).unlink()
            return result.text
        except Exception as e:
            logger.error(f"Whisper API transcription failed: {e}")
        return None

    async def _transcribe_azure(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Azure Speech."""
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_key = os.environ.get("AZURE_SPEECH_KEY")
            speech_region = os.environ.get("AZURE_SPEECH_REGION", "eastus")

            if not speech_key:
                return None

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
            audio_config = speechsdk.AudioConfig(filename=temp_path)

            recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio_config)
            result = recognizer.recognize_once()

            Path(temp_path).unlink()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
        except Exception as e:
            logger.error(f"Azure transcription failed: {e}")
        return None

    def list_personas(self) -> List[Dict]:
        """List available voice personas."""
        return [
            {"id": p.id, "name": p.name, "description": p.description, "provider": p.provider.value}
            for p in self.config.personas.values()
        ]

    def get_quota_status(self) -> Dict:
        """Get ElevenLabs quota status."""
        client = self._get_elevenlabs_client()
        if not client:
            return {"available": False, "reason": "ElevenLabs not configured"}

        try:
            user = client.user.get()
            subscription = user.subscription
            return {
                "available": True,
                "character_count": subscription.character_count,
                "character_limit": subscription.character_limit,
                "remaining": subscription.character_limit - subscription.character_count,
                "tier": subscription.tier,
            }
        except Exception as e:
            return {"available": False, "reason": str(e)}


# FastAPI Application
app = FastAPI(
    title="Lumina Voice Actor Service",
    description="Unified voice synthesis and recognition",
    version="1.0.0",
)

service = VoiceActorService()


class SynthesizeRequest(BaseModel):
    text: str
    persona: str = "jarvis"
    use_cache: bool = True


class TranscribeRequest(BaseModel):
    audio_base64: str
    provider: Optional[str] = None


@app.get("/")
async def root():
    return {"service": "Lumina Voice Actor", "status": "running"}


@app.get("/personas")
async def list_personas():
    return {"personas": service.list_personas()}


@app.get("/quota")
async def get_quota():
    return service.get_quota_status()


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    audio = await service.synthesize(
        text=request.text, persona_id=request.persona, use_cache=request.use_cache
    )

    if audio is None:
        raise HTTPException(500, "Synthesis failed")

    return {"audio_base64": base64.b64encode(audio).decode()}


@app.post("/synthesize/stream")
async def synthesize_stream(request: SynthesizeRequest):
    audio = await service.synthesize(
        text=request.text, persona_id=request.persona, use_cache=request.use_cache
    )

    if audio is None:
        raise HTTPException(500, "Synthesis failed")

    return StreamingResponse(iter([audio]), media_type="audio/mpeg")


@app.post("/transcribe")
async def transcribe(request: TranscribeRequest):
    audio_data = base64.b64decode(request.audio_base64)
    provider = STTProvider(request.provider) if request.provider else None

    text = await service.transcribe(audio_data, provider)

    if text is None:
        raise HTTPException(500, "Transcription failed")

    return {"text": text}


@app.get("/health")
async def health():
    quota = service.get_quota_status()
    return {
        "status": "healthy",
        "elevenlabs": quota.get("available", False),
        "personas": len(service.list_personas()),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "voice_actor_service:app", host="127.0.0.1", port=11436, reload=True, log_level="info"
    )
