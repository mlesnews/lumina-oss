# scripts/python/elevenlabs_agent.py
"""ElevenLabs Master‑Super‑Agent for high‑fidelity voice synthesis and recognition.

This module implements a conversational agent that:

* Uses ElevenLabs text‑to‑speech (TTS) for natural‑sounding responses.
* Uses ElevenLabs speech‑to‑text (STT) for real‑time transcription.
* Provides a simple interface to start, pause, resume, and terminate conversations.
* Maintains context and turn‑taking for multi‑turn dialogues.
* Falls back to local TTS/STT (pyttsx3 / vosk) if ElevenLabs is unavailable.
* Logs all interactions and errors for debugging.

The agent is designed to be imported and used by other parts of the project, e.g. the
`kilo_module.py` or a higher‑level orchestration script.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import sounddevice as sd

# Optional imports for fallback engines
try:
    import pyttsx3  # local TTS fallback
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import vosk  # local STT fallback
except Exception:  # pragma: no cover
    vosk = None

# ElevenLabs SDK – optional import
try:
    from elevenlabs import generate, play, set_api_key
except Exception:  # pragma: no cover
    generate = None
    play = None
    set_api_key = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class ElevenLabsConfig:
    api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # default ElevenLabs voice
    # Audio capture settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    timeout: float = 5.0

    @classmethod
    def load(cls) -> ElevenLabsConfig:
        return cls()


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logger = logging.getLogger("elevenlabs_agent")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


async def _record_audio(cfg: ElevenLabsConfig) -> np.ndarray:
    """Record a single chunk of audio from the default microphone."""
    device = sd.default.device[0]
    if device is None:
        raise RuntimeError("No default input device configured.")
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(
        None,
        lambda: sd.rec(
            int(cfg.chunk_size),
            samplerate=cfg.sample_rate,
            channels=cfg.channels,
            dtype="float32",
        ),
    )
    await asyncio.sleep(cfg.timeout)
    audio = await future
    return audio


# ---------------------------------------------------------------------------
# ElevenLabs Agent
# ---------------------------------------------------------------------------


class ElevenLabsAgent:
    """Master‑Super‑Agent that manages a multi‑turn conversation.

    Public API:
        start_conversation() -> None
        pause() -> None
        resume() -> None
        terminate() -> None
    """

    def __init__(self, cfg: Optional[ElevenLabsConfig] = None):
        self.cfg = cfg or ElevenLabsConfig.load()
        if not self.cfg.api_key:
            logger.warning("ELEVENLABS_API_KEY not set; falling back to local engines.")
        else:
            set_api_key(self.cfg.api_key)
        self._running = False
        self._paused = False
        self._context: List[str] = []  # conversation history
        self._audio_queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=100)
        self._stt_task: Optional[asyncio.Task] = None
        self._tts_task: Optional[asyncio.Task] = None

    # ---------------------------------------------------------------------
    # Public control methods
    # ---------------------------------------------------------------------

    def start_conversation(self) -> None:
        if self._running:
            logger.info("Conversation already running.")
            return
        self._running = True
        self._stt_task = asyncio.create_task(self._listen_loop())
        self._tts_task = asyncio.create_task(self._speak_loop())
        logger.info("Conversation started.")

    def pause(self) -> None:
        if not self._running:
            logger.info("No active conversation to pause.")
            return
        self._paused = True
        logger.info("Conversation paused.")

    def resume(self) -> None:
        if not self._running:
            logger.info("No active conversation to resume.")
            return
        self._paused = False
        logger.info("Conversation resumed.")

    def terminate(self) -> None:
        if not self._running:
            logger.info("No active conversation to terminate.")
            return
        self._running = False
        if self._stt_task:
            self._stt_task.cancel()
        if self._tts_task:
            self._tts_task.cancel()
        logger.info("Conversation terminated.")

    # ---------------------------------------------------------------------
    # Internal loops
    # ---------------------------------------------------------------------

    async def _listen_loop(self) -> None:
        """Continuously record audio and push transcriptions to the queue."""
        while self._running:
            if self._paused:
                await asyncio.sleep(0.1)
                continue
            try:
                audio = await _record_audio(self.cfg)
                transcript = await self._stt(audio)
                if transcript:
                    logger.info(f"User: {transcript}")
                    self._context.append(f"User: {transcript}")
                    await self._audio_queue.put(transcript)
            except Exception as exc:
                logger.error(f"STT error: {exc}")
                await asyncio.sleep(1)

    async def _speak_loop(self) -> None:
        """Consume transcriptions and generate agent responses."""
        while self._running:
            if self._paused:
                await asyncio.sleep(0.1)
                continue
            try:
                user_input = await self._audio_queue.get()
                response = await self._generate_response(user_input)
                logger.info(f"Agent: {response}")
                self._context.append(f"Agent: {response}")
                await self._tts(response)
            except Exception as exc:
                logger.error(f"TTS error: {exc}")
                await asyncio.sleep(1)

    # ---------------------------------------------------------------------
    # Core functionality
    # ---------------------------------------------------------------------

    async def _stt(self, audio: np.ndarray) -> str:
        """Transcribe audio using ElevenLabs or fallback."""
        if generate is not None and self.cfg.api_key:
            try:
                # ElevenLabs STT endpoint (placeholder – actual API may differ)
                # For demonstration, we assume a function `elevenlabs_stt` exists.
                # Replace with real SDK call.
                return await asyncio.to_thread(self._elevenlabs_stt, audio)
            except Exception as exc:
                logger.warning(f"ElevenLabs STT failed: {exc}")
        # Fallback to Vosk
        if vosk is not None:
            return await asyncio.to_thread(self._vosk_stt, audio)
        raise RuntimeError("No STT engine available.")

    def _elevenlabs_stt(self, audio: np.ndarray) -> str:  # pragma: no cover
        # Placeholder implementation – replace with actual ElevenLabs STT call
        return "[ElevenLabs STT placeholder]"

    def _vosk_stt(self, audio: np.ndarray) -> str:  # pragma: no cover
        try:
            model = vosk.Model("model")  # path to Vosk model
            rec = vosk.KaldiRecognizer(model, self.cfg.sample_rate)
            rec.AcceptWaveform(audio.tobytes())
            res = rec.Result()
            data = json.loads(res)
            return data.get("text", "")

        except Exception as e:
            self.logger.error(f"Error in _vosk_stt: {e}", exc_info=True)
            raise
    async def _generate_response(self, user_input: str) -> str:
        """Generate a response using an LLM (placeholder)."""
        # In a real system, this would call an LLM API (e.g., Anthropic, OpenAI).
        # For now, echo the input with a simple transformation.
        return f"You said: {user_input}. I propose we plan further steps."

    async def _tts(self, text: str) -> None:
        if generate is not None and self.cfg.api_key:
            try:
                audio = await asyncio.to_thread(generate, text, voice=self.cfg.voice_id)
                await asyncio.to_thread(play, audio)
                return
            except Exception as exc:
                logger.warning(f"ElevenLabs TTS failed: {exc}")
        # Fallback to pyttsx3
        if pyttsx3 is not None:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return
        raise RuntimeError("No TTS engine available.")


# ---------------------------------------------------------------------------
# Example usage (uncomment to run as a script)
# ---------------------------------------------------------------------------
# if __name__ == "__main__":
#     agent = ElevenLabsAgent()
#     agent.start_conversation()
#     try:
#         while True:
#             cmd = input("Command (pause/resume/terminate): ")
#             if cmd == "pause":
#                 agent.pause()
#             elif cmd == "resume":
#                 agent.resume()
#             elif cmd == "terminate":
#                 agent.terminate()
#                 break
#     except KeyboardInterrupt:
#         agent.terminate()
#         print("\nInterrupted.")
""
