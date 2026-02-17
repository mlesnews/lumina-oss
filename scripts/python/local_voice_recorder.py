#!/usr/bin/env python3
"""
Local Voice Recorder with Pause/Resume

Our own voice recording system that works independently of Cursor.
Records locally, transcribes locally, submits text to Cursor.

Tags: #VOICE #LOCAL #PAUSE #RESUME #OUR_SOLUTION @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

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

logger = get_logger("LocalVoiceRecorder")

# Try to import audio libraries
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("pyaudio not available - install with: pip install pyaudio")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("whisper not available - install with: pip install openai-whisper")


class RecordingState(Enum):
    """Recording state"""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    PROCESSING = "processing"


@dataclass
class AudioChunk:
    """Audio chunk data"""
    chunk_id: str
    audio_data: bytes
    timestamp: str
    sample_rate: int
    channels: int
    chunk_size: int


class LocalVoiceRecorder:
    """
    Local Voice Recorder with Pause/Resume

    Our own voice recording system:
    - Records locally (independent of Cursor)
    - Pause/resume functionality
    - Local transcription (Whisper)
    - Submit text to Cursor (bypass voice UI)
    """

    def __init__(self):
        """Initialize local voice recorder"""
        self.state = RecordingState.IDLE
        self.audio_chunks: List[AudioChunk] = []
        self.lock = threading.Lock()

        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = None  # Will be set based on pyaudio

        # Recording thread
        self.recording_thread: Optional[threading.Thread] = None
        self.recording_active = False

        # Integration with voice buffer
        try:
            from voice_buffer_pause_resume import get_voice_buffer
            self.voice_buffer = get_voice_buffer()
        except ImportError:
            self.voice_buffer = None
            logger.warning("Voice buffer not available")

        logger.info("=" * 80)
        logger.info("🎤 LOCAL VOICE RECORDER")
        logger.info("=" * 80)
        logger.info("   Our own voice recording system")
        logger.info("   Independent of Cursor's voice UI")
        logger.info("   Pause/resume functionality built-in")
        logger.info("")

    def start_recording(self):
        """Start recording"""
        with self.lock:
            if self.state == RecordingState.RECORDING:
                logger.warning("Already recording")
                return False

            if not PYAUDIO_AVAILABLE:
                logger.error("pyaudio not available - cannot record")
                return False

            self.state = RecordingState.RECORDING
            self.audio_chunks.clear()
            self.recording_active = True

            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                daemon=True
            )
            self.recording_thread.start()

            # Integrate with voice buffer
            if self.voice_buffer:
                self.voice_buffer.start_recording()

            logger.info("🎤 Recording started (local)")
            return True

    def pause_recording(self):
        """Pause recording"""
        with self.lock:
            if self.state != RecordingState.RECORDING:
                logger.warning(f"Cannot pause - state is {self.state.value}")
                return False

            self.state = RecordingState.PAUSED

            # Integrate with voice buffer
            if self.voice_buffer:
                self.voice_buffer.pause_recording()

            logger.info(f"⏸️  Recording paused (buffered {len(self.audio_chunks)} chunks)")
            return True

    def resume_recording(self):
        """Resume recording"""
        with self.lock:
            if self.state != RecordingState.PAUSED:
                logger.warning(f"Cannot resume - state is {self.state.value}")
                return False

            self.state = RecordingState.RECORDING

            # Integrate with voice buffer
            if self.voice_buffer:
                self.voice_buffer.resume_recording()

            logger.info("▶️  Recording resumed")
            return True

    def stop_recording(self) -> str:
        """Stop recording and return transcription"""
        with self.lock:
            if self.state == RecordingState.IDLE:
                logger.warning("Not recording")
                return ""

            self.recording_active = False
            self.state = RecordingState.PROCESSING

            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)

            # Integrate with voice buffer
            if self.voice_buffer:
                self.voice_buffer.stop_recording()

            # Transcribe audio
            transcript = self._transcribe_audio()

            self.state = RecordingState.IDLE
            self.audio_chunks.clear()

            logger.info(f"⏹️  Recording stopped - transcript: {transcript[:50]}...")
            return transcript

    def _record_audio(self):
        """Record audio in background thread"""
        if not PYAUDIO_AVAILABLE:
            return

        try:
            import pyaudio

            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            chunk_count = 0
            while self.recording_active:
                if self.state == RecordingState.RECORDING:
                    try:
                        data = stream.read(self.chunk_size, exception_on_overflow=False)
                        chunk = AudioChunk(
                            chunk_id=f"chunk_{chunk_count}",
                            audio_data=data,
                            timestamp=datetime.now().isoformat(),
                            sample_rate=self.sample_rate,
                            channels=self.channels,
                            chunk_size=len(data)
                        )
                        self.audio_chunks.append(chunk)
                        chunk_count += 1
                    except Exception as e:
                        logger.debug(f"Audio read error: {e}")
                elif self.state == RecordingState.PAUSED:
                    # Paused - don't record, but keep thread alive
                    time.sleep(0.1)
                else:
                    break

            stream.stop_stream()
            stream.close()
            audio.terminate()

        except Exception as e:
            logger.error(f"Recording error: {e}")
            self.recording_active = False

    def _transcribe_audio(self) -> str:
        """Transcribe audio using local Whisper"""
        if not self.audio_chunks:
            return ""

        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available - cannot transcribe")
            return ""

        try:
            import whisper
            import numpy as np

            # Load Whisper model
            model = whisper.load_model("base")  # Can use "tiny", "base", "small", "medium", "large"

            # Combine audio chunks
            audio_data = b''.join([chunk.audio_data for chunk in self.audio_chunks])

            # Convert to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe
            result = model.transcribe(audio_np)
            transcript = result["text"].strip()

            logger.info(f"📝 Transcribed: {transcript}")
            return transcript

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    def submit_to_cursor(self, transcript: str):
        """Submit transcript to Cursor (as text, bypassing voice UI)"""
        if not transcript:
            return

        try:
            from voice_transcript_queue import VoiceTranscriptQueue, RequestType
            queue = VoiceTranscriptQueue()
            request_id = queue.queue_request(
                content=transcript,
                request_type=RequestType.TEXT,  # Submit as TEXT, not VOICE_TRANSCRIPT
                priority=0
            )
            logger.info(f"✅ Submitted to Cursor queue: {request_id}")
            return request_id
        except Exception as e:
            logger.error(f"Failed to submit to Cursor: {e}")
            return None

    def get_state(self) -> RecordingState:
        """Get current recording state"""
        with self.lock:
            return self.state


def get_local_voice_recorder() -> LocalVoiceRecorder:
    """Get local voice recorder (singleton)"""
    global _recorder_instance
    if '_recorder_instance' not in globals():
        _recorder_instance = LocalVoiceRecorder()
    return _recorder_instance


# Initialize
_recorder_instance = None
