#!/usr/bin/env python3
"""
Voice Buffer with Pause/Resume System

Provides pause/resume functionality for voice recording by buffering chunks.
Allows natural speech flow without losing context.

Tags: #VOICE #PAUSE #RESUME #BUFFER #WORKFLOW @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from queue import Queue

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

logger = get_logger("VoiceBufferPauseResume")


class VoiceState(Enum):
    """Voice recording state"""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    PROCESSING = "processing"


@dataclass
class VoiceChunk:
    """A chunk of voice recording"""
    chunk_id: str
    audio_data: Any  # Audio data (format depends on implementation)
    timestamp: str
    duration: float
    metadata: Dict[str, Any] = None


class VoiceBufferPauseResume:
    """
    Voice Buffer with Pause/Resume

    Allows:
    - Pause recording (buffers current chunk)
    - Resume recording (continues from buffer)
    - Process buffered chunks when ready
    - Maintain context across pause/resume
    """

    def __init__(self):
        """Initialize voice buffer system"""
        self.state = VoiceState.IDLE
        self.buffer: List[VoiceChunk] = []
        self.current_chunk: Optional[VoiceChunk] = None
        self.lock = threading.Lock()

        logger.info("=" * 80)
        logger.info("🎤 VOICE BUFFER WITH PAUSE/RESUME")
        logger.info("=" * 80)
        logger.info("   Pause = buffer current, Resume = continue")
        logger.info("   Maintains context across pause/resume")
        logger.info("")

    def start_recording(self):
        """Start voice recording"""
        with self.lock:
            if self.state == VoiceState.RECORDING:
                logger.warning("Already recording")
                return False

            self.state = VoiceState.RECORDING
            self.current_chunk = None
            logger.info("🎤 Recording started")
            return True

    def pause_recording(self):
        """Pause recording (buffer current chunk)"""
        with self.lock:
            if self.state != VoiceState.RECORDING:
                logger.warning(f"Cannot pause - state is {self.state.value}")
                return False

            # Buffer current chunk if exists
            if self.current_chunk:
                self.buffer.append(self.current_chunk)
                self.current_chunk = None
                logger.info(f"⏸️  Recording paused - buffered chunk (total: {len(self.buffer)})")
            else:
                logger.info("⏸️  Recording paused (no chunk to buffer)")

            self.state = VoiceState.PAUSED
            return True

    def resume_recording(self):
        """Resume recording (continue from buffer)"""
        with self.lock:
            if self.state != VoiceState.PAUSED:
                logger.warning(f"Cannot resume - state is {self.state.value}")
                return False

            self.state = VoiceState.RECORDING
            logger.info(f"▶️  Recording resumed (buffered chunks: {len(self.buffer)})")
            return True

    def stop_recording(self):
        """Stop recording (process all buffered chunks)"""
        with self.lock:
            if self.state == VoiceState.IDLE:
                logger.warning("Not recording")
                return False

            # Add current chunk to buffer if exists
            if self.current_chunk:
                self.buffer.append(self.current_chunk)
                self.current_chunk = None

            self.state = VoiceState.IDLE
            total_chunks = len(self.buffer)
            logger.info(f"⏹️  Recording stopped - {total_chunks} chunks buffered")
            return True

    def add_chunk(self, audio_data: Any, duration: float, metadata: Optional[Dict[str, Any]] = None):
        """Add audio chunk to current recording"""
        with self.lock:
            if self.state != VoiceState.RECORDING:
                logger.warning(f"Cannot add chunk - not recording (state: {self.state.value})")
                return False

            chunk = VoiceChunk(
                chunk_id=f"chunk_{int(time.time() * 1000000)}",
                audio_data=audio_data,
                timestamp=datetime.now().isoformat(),
                duration=duration,
                metadata=metadata or {}
            )

            self.current_chunk = chunk
            logger.debug(f"📦 Added chunk: {chunk.chunk_id} ({duration:.2f}s)")
            return True

    def get_buffered_chunks(self) -> List[VoiceChunk]:
        """Get all buffered chunks"""
        with self.lock:
            return self.buffer.copy()

    def clear_buffer(self):
        """Clear buffer"""
        with self.lock:
            self.buffer.clear()
            self.current_chunk = None
            logger.info("🗑️  Buffer cleared")

    def process_buffer(self) -> List[VoiceChunk]:
        """Process and return all buffered chunks, then clear buffer"""
        with self.lock:
            chunks = self.buffer.copy()
            self.buffer.clear()
            self.current_chunk = None
            logger.info(f"📤 Processing {len(chunks)} buffered chunks")
            return chunks

    def get_state(self) -> VoiceState:
        """Get current state"""
        with self.lock:
            return self.state


def get_voice_buffer() -> VoiceBufferPauseResume:
    """Get voice buffer (singleton)"""
    global _voice_buffer_instance
    if '_voice_buffer_instance' not in globals():
        _voice_buffer_instance = VoiceBufferPauseResume()
    return _voice_buffer_instance


# Initialize
_voice_buffer_instance = None
