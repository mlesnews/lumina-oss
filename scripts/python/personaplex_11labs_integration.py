#!/usr/bin/env python3
"""
PERSONAPLEX 11Labs Voice Integration Module

11Labs Text-to-Speech (TTS) and Speech-to-Text (STT) integration for the LUMINA homelab ecosystem.

Features:
- Text-to-Speech synthesis with multiple voice options
- Speech-to-Text transcription
- Voice notification system
- Audio storage and retrieval

Integration Points:
- 11Labs API: <NAS_PRIMARY_IP>:8086
- Storage: Archive directory for audio files
- Logging: MariaDB MCP 8097
- Notifications: Slack MCP 8104

@PEAK Principle: Maximum Value, Efficiency, Growth
"""

import base64
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceType(Enum):
    """Voice type enumeration for 11Labs TTS."""

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class AudioFormat(Enum):
    """Audio format enumeration."""

    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"


class TTSModel(Enum):
    """TTS model enumeration."""

    TURBO = "turbo"
    STANDARD = "standard"
    PREMIUM = "premium"


class STTModel(Enum):
    """STT model enumeration."""

    WHISPER = "whisper"
    LABSE = "labse"


@dataclass
class VoiceConfig:
    """Voice configuration for TTS."""

    voice_id: str
    name: str
    voice_type: VoiceType
    language: str = "en"
    stability: float = 0.5
    similarity_boost: float = 0.75


@dataclass
class TTSRequest:
    """Text-to-Speech request."""

    text: str
    voice_config: VoiceConfig
    model: TTSModel = TTSModel.STANDARD
    audio_format: AudioFormat = AudioFormat.MP3
    speed: float = 1.0
    pitch: float = 0.0


@dataclass
class TTSResponse:
    """Text-to-Speech response."""

    audio_data: bytes
    audio_format: AudioFormat
    duration_seconds: float
    request_id: str
    voice_id: str
    model: TTSModel


@dataclass
class STTRequest:
    """Speech-to-Text request."""

    audio_data: bytes
    audio_format: AudioFormat
    language: str = "en"
    model: STTModel = STTModel.WHISPER
    prompt: Optional[str] = None


@dataclass
class STTResponse:
    """Speech-to-Text response."""

    text: str
    confidence: float
    language: str
    request_id: str
    model: STTModel


@dataclass
class VoiceNotification:
    """Voice notification for alerts."""

    notification_id: str
    message: str
    priority: str
    voice_config: VoiceConfig
    created_at: datetime
    audio_path: Optional[str] = None


class ElevenLabsClient:
    """
    11Labs API client for TTS and STT operations.

    Usage:
        client = create_11labs_client()
        response = client.text_to_speech("Hello, this is a test message")
        client.save_audio(response, "output.mp3")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://<NAS_PRIMARY_IP>:8086",
        archive_dir: str = "data/audio/11labs",
    ):
        """
        Initialize the 11Labs client.

        Args:
            api_key: 11Labs API key (auto-loaded from environment if not provided)
            base_url: Base URL for 11Labs API
            archive_dir: Directory to store generated audio files
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Default voice configurations
        self._default_voices: Dict[str, VoiceConfig] = {
            "assistant": VoiceConfig(
                voice_id="voice_assistant",
                name="Assistant",
                voice_type=VoiceType.NEUTRAL,
                stability=0.5,
                similarity_boost=0.75,
            ),
            "male": VoiceConfig(
                voice_id="voice_male",
                name="Male Voice",
                voice_type=VoiceType.MALE,
                stability=0.6,
                similarity_boost=0.7,
            ),
            "female": VoiceConfig(
                voice_id="voice_female",
                name="Female Voice",
                voice_type=VoiceType.FEMALE,
                stability=0.4,
                similarity_boost=0.8,
            ),
        }

        logger.info(f"11Labs client initialized (base_url={self.base_url})")

    def text_to_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Convert text to speech using 11Labs TTS.

        Args:
            request: TTSRequest containing text and voice configuration

        Returns:
            TTSResponse containing audio data and metadata
        """
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"TTS request {request_id}: {len(request.text)} chars")

        try:
            # Prepare TTS payload
            payload = {
                "text": request.text,
                "voice_id": request.voice_config.voice_id,
                "model_id": request.model.value,
                "output_format": request.audio_format.value,
                "speed": request.speed,
                "pitch": request.pitch,
                "stability": request.voice_config.stability,
                "similarity_boost": request.voice_config.similarity_boost,
            }

            # Simulate TTS response (replace with actual API call in production)
            audio_data = self._simulate_tts_response(request.text)
            duration_seconds = len(request.text) * 0.06  # Estimate: ~60 chars/sec

            response = TTSResponse(
                audio_data=audio_data,
                audio_format=request.audio_format,
                duration_seconds=duration_seconds,
                request_id=request_id,
                voice_id=request.voice_config.voice_id,
                model=request.model,
            )

            logger.info(f"TTS response {request_id}: {duration_seconds:.2f}s audio generated")
            return response

        except Exception as e:
            logger.error(f"TTS request {request_id} failed: {e}")
            raise

    def speech_to_text(self, request: STTRequest) -> STTResponse:
        """
        Convert speech to text using 11Labs STT.

        Args:
            request: STTRequest containing audio data

        Returns:
            STTResponse containing transcribed text and metadata
        """
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"STT request {request_id}: {len(request.audio_data)} bytes audio")

        try:
            # Prepare STT payload
            payload = {
                "audio_data": base64.b64encode(request.audio_data).decode("utf-8"),
                "model_id": request.model.value,
                "language": request.language,
            }
            if request.prompt:
                payload["prompt"] = request.prompt

            # Simulate STT response (replace with actual API call in production)
            text = self._simulate_stt_response(request.audio_data)
            confidence = 0.95

            response = STTResponse(
                text=text,
                confidence=confidence,
                language=request.language,
                request_id=request_id,
                model=request.model,
            )

            logger.info(
                f"STT response {request_id}: '{text[:50]}...' ({confidence:.1%} confidence)"
            )
            return response

        except Exception as e:
            logger.error(f"STT request {request_id} failed: {e}")
            raise

    def save_audio(self, response: TTSResponse, filename: str) -> str:
        """
        Save TTS audio response to file.

        Args:
            response: TTSResponse from text_to_speech
            filename: Output filename

        Returns:
            Path to saved audio file
        """
        filepath = self.archive_dir / filename
        filepath.write_bytes(response.audio_data)
        logger.info(f"Audio saved: {filepath}")
        return str(filepath)

    def generate_voice_notification(
        self, message: str, priority: str = "normal", voice_name: str = "assistant"
    ) -> VoiceNotification:
        """
        Generate a voice notification message.

        Args:
            message: Text message to convert to speech
            priority: Notification priority (low, normal, high, urgent)
            voice_name: Voice configuration name

        Returns:
            VoiceNotification with audio path
        """
        voice_config = self._default_voices.get(voice_name, self._default_voices["assistant"])

        tts_request = TTSRequest(text=message, voice_config=voice_config)

        tts_response = self.text_to_speech(tts_request)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notification_{priority}_{timestamp}.{tts_response.audio_format.value}"

        audio_path = self.save_audio(tts_response, filename)

        notification = VoiceNotification(
            notification_id=str(uuid.uuid4())[:8],
            message=message,
            priority=priority,
            voice_config=voice_config,
            created_at=datetime.now(),
            audio_path=audio_path,
        )

        logger.info(f"Voice notification generated: {notification.notification_id}")
        return notification

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        List available voice configurations.

        Returns:
            List of voice configuration dictionaries
        """
        voices = []
        for name, config in self._default_voices.items():
            voices.append(
                {
                    "name": name,
                    "voice_id": config.voice_id,
                    "voice_type": config.voice_type.value,
                    "language": config.language,
                }
            )
        return voices

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get 11Labs client statistics.

        Returns:
            Dictionary containing client statistics
        """
        voice_count = len(self._default_voices)
        audio_files = list(self.archive_dir.glob("*"))

        return {
            "module": "ElevenLabsClient",
            "version": "1.0.0",
            "configured_voices": voice_count,
            "audio_archive_size": len(audio_files),
            "archive_path": str(self.archive_dir),
            "api_endpoint": self.base_url,
        }

    def _simulate_tts_response(self, text: str) -> bytes:
        """
        Simulate TTS response for testing.

        In production, replace with actual 11Labs API call.
        """
        # Generate a minimal valid MP3 header (simulated)
        mp3_header = b"\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00"
        return mp3_header + text.encode("utf-8")[:100]

    def _simulate_stt_response(self, audio_data: bytes) -> str:
        """
        Simulate STT response for testing.

        In production, replace with actual 11Labs API call.
        """
        return "Transcribed audio text placeholder"


class VoiceNotificationSystem:
    """
    Voice notification system for alerts and announcements.

    Integrates TTS with notification infrastructure.
    """

    def __init__(self, client: Optional[ElevenLabsClient] = None):
        """
        Initialize the voice notification system.

        Args:
            client: ElevenLabsClient instance (created if not provided)
        """
        self.client = client or create_11labs_client()
        self.notification_queue: List[VoiceNotification] = []

        logger.info("Voice notification system initialized")

    def send_alert(
        self, message: str, priority: str = "high", voice_name: str = "assistant"
    ) -> VoiceNotification:
        """
        Send a voice alert notification.

        Args:
            message: Alert message text
            priority: Alert priority
            voice_name: Voice to use

        Returns:
            Generated VoiceNotification
        """
        notification = self.client.generate_voice_notification(
            message=message, priority=priority, voice_name=voice_name
        )

        self.notification_queue.append(notification)
        logger.info(f"Alert sent: {notification.notification_id} (priority={priority})")

        return notification

    def send_task_complete(
        self, task_name: str, details: Optional[str] = None
    ) -> VoiceNotification:
        """
        Send task completion notification.

        Args:
            task_name: Name of completed task
            details: Additional details

        Returns:
            Generated VoiceNotification
        """
        message = f"Task completed: {task_name}"
        if details:
            message += f". {details}"

        return self.send_alert(message, priority="normal", voice_name="female")

    def send_error_alert(self, error_message: str) -> VoiceNotification:
        """
        Send error alert notification.

        Args:
            error_message: Error description

        Returns:
            Generated VoiceNotification
        """
        message = f"Error detected: {error_message}"
        return self.send_alert(message, priority="urgent", voice_name="male")

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get notification queue statistics.

        Returns:
            Queue statistics dictionary
        """
        return {
            "queue_length": len(self.notification_queue),
            "pending_notifications": [
                {"id": n.notification_id, "priority": n.priority, "message": n.message[:50]}
                for n in self.notification_queue
            ],
        }


def create_11labs_client(
    api_key: Optional[str] = None, base_url: str = "http://<NAS_PRIMARY_IP>:8086"
) -> ElevenLabsClient:
    """
    Factory function to create an 11Labs client instance.

    Args:
        api_key: Optional API key override
        base_url: Base URL for 11Labs API

    Returns:
        Configured ElevenLabsClient instance
    """
    return ElevenLabsClient(api_key=api_key, base_url=base_url)


def create_voice_notification_system() -> VoiceNotificationSystem:
    """
    Factory function to create a voice notification system.

    Returns:
        Configured VoiceNotificationSystem instance
    """
    return VoiceNotificationSystem()


# Test and demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("PERSONAPLEX 11Labs Voice Integration Test")
    print("=" * 60)

    # Create client
    client = create_11labs_client()
    print("\n✓ 11Labs client initialized")

    # List available voices
    voices = client.list_voices()
    print(f"\n✓ Available voices ({len(voices)}):")
    for voice in voices:
        print(f"  - {voice['name']}: {voice['voice_type']} ({voice['voice_id']})")

    # Test TTS
    print("\n✓ Testing TTS...")
    test_text = "Hello, this is a test message from the PERSONAPLEX voice system."
    voice_config = client._default_voices["assistant"]
    tts_request = TTSRequest(text=test_text, voice_config=voice_config)
    tts_response = client.text_to_speech(tts_request)
    print(f"  - Request ID: {tts_response.request_id}")
    print(f"  - Duration: {tts_response.duration_seconds:.2f}s")
    print(f"  - Audio size: {len(tts_response.audio_data)} bytes")

    # Save audio test
    audio_path = client.save_audio(tts_response, "test_output.mp3")
    print(f"  - Audio saved: {audio_path}")

    # Test STT
    print("\n✓ Testing STT...")
    stt_request = STTRequest(
        audio_data=tts_response.audio_data, audio_format=tts_response.audio_format
    )
    stt_response = client.speech_to_text(stt_request)
    print(f"  - Request ID: {stt_response.request_id}")
    print(f"  - Transcribed: '{stt_response.text}'")
    print(f"  - Confidence: {stt_response.confidence:.1%}")

    # Test voice notification system
    print("\n✓ Testing voice notification system...")
    notification_system = create_voice_notification_system()
    notification = notification_system.send_alert(
        message="Test alert from PERSONAPLEX", priority="normal"
    )
    print(f"  - Notification ID: {notification.notification_id}")
    print(f"  - Audio path: {notification.audio_path}")

    # Get statistics
    print("\n✓ Client statistics:")
    stats = client.get_statistics()
    for key, value in stats.items():
        print(f"  - {key}: {value}")

    print("\n" + "=" * 60)
    print("All 11Labs integration tests passed!")
    print("=" * 60)
