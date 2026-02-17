# scripts/python/jarvis_agent.py
"""Jarvis Personal Assistant.

This module implements a high‑level personal assistant that can:

* Manage tasks and reminders.
* Interact with the user via voice (ElevenLabs TTS/STT) or text.
* Integrate with external services (calendar, email, etc.) – placeholders for now.
* Maintain context across turns and provide natural‑language responses.

The implementation follows the pattern used by the `elevenlabs_agent.py` and the
`@ace` assistant from the armoury crate (not present in this repo but used as a
reference).  The code is intentionally modular so that each feature can be
extended independently.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Optional imports for voice
try:
    from elevenlabs import generate, play, set_api_key
except Exception:  # pragma: no cover
    generate = None
    play = None
    set_api_key = None

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

# Optional STT fallback
try:
    import vosk
except Exception:  # pragma: no cover
    vosk = None

# Logging setup
logger = logging.getLogger("jarvis_agent")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class JarvisConfig:
    api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    timeout: float = 5.0

    @classmethod
    def load(cls) -> JarvisConfig:
        return cls()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


async def _record_audio(cfg: JarvisConfig) -> bytes:
    """Record a single chunk of audio and return raw bytes."""
    import sounddevice as sd

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
    return audio.tobytes()


# ---------------------------------------------------------------------------
# Jarvis Agent
# ---------------------------------------------------------------------------


class JarvisAgent:
    """Personal assistant that can handle tasks, reminders, and general queries."""

    def __init__(self, cfg: Optional[JarvisConfig] = None):
        self.cfg = cfg or JarvisConfig.load()
        if self.cfg.api_key:
            set_api_key(self.cfg.api_key)
        self._running = False
        self._paused = False
        self._context: List[str] = []
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=100)
        self._stt_task: Optional[asyncio.Task] = None
        self._tts_task: Optional[asyncio.Task] = None
        self._tasks: List[str] = []  # simple task list

    # ---------------------------------------------------------------------
    # Public control methods
    # ---------------------------------------------------------------------

    def start(self) -> None:
        if self._running:
            logger.info("Jarvis already running.")
            return
        self._running = True
        self._stt_task = asyncio.create_task(self._listen_loop())
        self._tts_task = asyncio.create_task(self._speak_loop())
        logger.info("Jarvis started.")

    def pause(self) -> None:
        if not self._running:
            logger.info("Jarvis not running.")
            return
        self._paused = True
        logger.info("Jarvis paused.")

    def resume(self) -> None:
        if not self._running:
            logger.info("Jarvis not running.")
            return
        self._paused = False
        logger.info("Jarvis resumed.")

    def terminate(self) -> None:
        if not self._running:
            logger.info("Jarvis not running.")
            return
        self._running = False
        if self._stt_task:
            self._stt_task.cancel()
        if self._tts_task:
            self._tts_task.cancel()
        logger.info("Jarvis terminated.")

    # ---------------------------------------------------------------------
    # Internal loops
    # ---------------------------------------------------------------------

    async def _listen_loop(self) -> None:
        while self._running:
            if self._paused:
                await asyncio.sleep(0.1)
                continue
            try:
                raw = await _record_audio(self.cfg)
                transcript = await self._stt(raw)
                if transcript:
                    logger.info(f"User: {transcript}")
                    self._context.append(f"User: {transcript}")
                    await self._audio_queue.put(transcript)
            except Exception as exc:
                logger.error(f"STT error: {exc}")
                await asyncio.sleep(1)

    async def _speak_loop(self) -> None:
        while self._running:
            if self._paused:
                await asyncio.sleep(0.1)
                continue
            try:
                user_input = await self._audio_queue.get()
                response = await self._process(user_input)
                logger.info(f"Jarvis: {response}")
                self._context.append(f"Jarvis: {response}")
                await self._tts(response)
            except Exception as exc:
                logger.error(f"TTS error: {exc}")
                await asyncio.sleep(1)

    # ---------------------------------------------------------------------
    # Core functionality
    # ---------------------------------------------------------------------

    async def _stt(self, raw: bytes) -> str:
        if generate is not None and self.cfg.api_key:
            # Placeholder: real STT would use ElevenLabs API
            return "[ElevenLabs STT placeholder]"
        if vosk is not None:
            model = vosk.Model("model")
            rec = vosk.KaldiRecognizer(model, self.cfg.sample_rate)
            rec.AcceptWaveform(raw)
            res = rec.Result()
            data = json.loads(res)
            return data.get("text", "")
        raise RuntimeError("No STT engine available.")

    async def _tts(self, text: str) -> None:
        if generate is not None and self.cfg.api_key:
            try:
                audio = await asyncio.to_thread(generate, text, voice=self.cfg.voice_id)
                await asyncio.to_thread(play, audio)
                return
            except Exception as exc:
                logger.warning(f"ElevenLabs TTS failed: {exc}")
        if pyttsx3 is not None:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return
        raise RuntimeError("No TTS engine available.")

    async def _process(self, user_input: str) -> str:
        """Process user input and generate a response.

        This is a placeholder that demonstrates task handling.  In a real
        implementation, this method would call an LLM or rule‑based engine.
        """
        # Simple task management logic
        if user_input.lower().startswith("add task"):
            task = user_input[8:].strip()
            self._tasks.append(task)
            return f"Task added: {task}"
        if user_input.lower().startswith("list tasks"):
            if not self._tasks:
                return "No tasks scheduled."
            return "\n".join(f"{i + 1}. {t}" for i, t in enumerate(self._tasks))
        # Default echo
        return f"You said: {user_input}."


# ---------------------------------------------------------------------------
# IMVA Agent – a lightweight version of Jarvis focused on quick interactions.
# ---------------------------------------------------------------------------


class IMVAAgent(JarvisAgent):
    """Imva is a minimal assistant that only handles quick queries.

    It inherits from JarvisAgent but overrides the _process method to provide
    concise answers.
    """

    async def _process(self, user_input: str) -> str:
        # Very simple Q&A logic
        if "weather" in user_input.lower():
            return "The weather is sunny with a high of 75°F."
        if "time" in user_input.lower():
            from datetime import datetime

            return f"Current time is {datetime.now().strftime('%H:%M:%S')}"
        return f"I didn't understand: {user_input}"


# ---------------------------------------------------------------------------
# Example usage (uncomment to run as a script)
# ---------------------------------------------------------------------------
# if __name__ == "__main__":
#     agent = JarvisAgent()
#     agent.start()
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
