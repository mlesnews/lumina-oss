# scripts/python/kilo_module.py
"""Microphone integration for Cursor’s AI chat (Kilo module).

This file contains a minimal, self‑contained implementation that follows the
conventions used in the rest of the repository:

* pydantic for configuration
* sounddevice for cross‑platform audio capture
* asyncio queues for non‑blocking streaming
* optional VAD/noise filtering via the existing `voice_filter_system` utilities
* integration with the existing `voice_transcript_queue` middleware

The implementation is intentionally lightweight so it can be dropped into the
project without modifying other modules.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class KiloConfig(BaseModel):
    """Microphone configuration for the Kilo module."""

    device_index: Optional[int] = Field(
        None,
        description="Index of the audio input device. None selects the default.",
    )
    sample_rate: int = Field(
        16000,
        description="Sample rate in Hz (must match the LLM's expected rate).",
    )
    channels: int = Field(
        1,
        description="Number of audio channels (mono).",
    )
    chunk_size: int = Field(
        1024,
        description="Number of frames per read. Larger values reduce CPU usage but increase latency.",
    )
    timeout: float = Field(
        5.0,
        description="Timeout in seconds for stream read operations.",
    )

    @classmethod
    def load(cls, path: str | Path | None = None) -> KiloConfig:
        try:
            """Load configuration from a JSON/YAML file or environment variables.

            If *path* is None, the function looks for `kilo_config.json` in the
            repository root. Environment variables override file values.
            """
            data: dict = {}
            if path is None:
                path = Path("kilo_config.json")
            if path.exists():
                if path.suffix in {".json"}:
                    data = json.loads(path.read_text())
                else:
                    # Simple YAML parsing for key: value pairs
                    for line in path.read_text().splitlines():
                        if line.strip() and not line.startswith("#"):
                            key, _, val = line.partition(":")
                            data[key.strip()] = val.strip()
            # Override with environment variables
            for field in cls.model_fields:
                env = os.getenv(field.upper())
                if env is not None:
                    data[field] = env
            return cls(**data)


        except Exception as e:
            print(f"Error loading Kilo config: {e}")
            raise
# ---------------------------------------------------------------------------
# Device discovery & validation
# ---------------------------------------------------------------------------


def list_input_devices() -> list[dict]:
    """Return a list of available input devices."""
    return sd.query_devices(kind="input")


def validate_device(index: Optional[int]) -> int:
    """Return a valid device index; raise ValueError if not found."""
    devices = list_input_devices()
    if index is None:
        # Pick the default input device
        return sd.default.device[0]
    if 0 <= index < len(devices):
        return index
    raise ValueError(f"Device index {index} is out of range. Available: 0-{len(devices) - 1}")


# ---------------------------------------------------------------------------
# Audio capture loop
# ---------------------------------------------------------------------------


async def audio_stream(queue: asyncio.Queue, cfg: KiloConfig):
    """Continuously read from the microphone and push raw frames into the queue."""

    device = validate_device(cfg.device_index)

    def callback(indata, frames, time, status):
        if status:
            # Log or handle stream status (e.g., overflow)
            print(f"[Kilo] Stream status: {status}")
        # Push a copy of the data to avoid mutation
        queue.put_nowait(indata.copy())

    with sd.InputStream(
        device=device,
        samplerate=cfg.sample_rate,
        channels=cfg.channels,
        blocksize=cfg.chunk_size,
        callback=callback,
    ):
        # The stream runs until the context manager exits
        while True:
            await asyncio.sleep(1)  # keep the coroutine alive


# ---------------------------------------------------------------------------
# Pre‑processing (optional VAD / noise filtering)
# ---------------------------------------------------------------------------

try:
    from voice_filter_system import apply_noise_gate
except Exception:  # pragma: no cover

    def apply_noise_gate(frame: np.ndarray) -> np.ndarray:  # type: ignore
        return frame


def preprocess(frame: np.ndarray, cfg: KiloConfig) -> np.ndarray:
    """Apply VAD / noise gate before sending to the LLM."""
    energy = np.linalg.norm(frame)
    if energy < 0.01:  # threshold
        return np.zeros_like(frame)
    return apply_noise_gate(frame)


# ---------------------------------------------------------------------------
# Integration with AI chat (placeholder for existing middleware)
# ---------------------------------------------------------------------------

# The repository already contains `voice_transcript_queue.py` which exposes a
# `TranscriptQueue` class. We import it lazily to avoid circular imports.
try:
    from voice_transcript_queue import TranscriptQueue
except Exception:  # pragma: no cover

    class TranscriptQueue:  # type: ignore
        async def enqueue(self, frame: np.ndarray):
            pass

        async def get_response(self) -> str:
            return "<mock response>"


async def run_kilo_chat():
    cfg = KiloConfig.load()
    audio_q: asyncio.Queue = asyncio.Queue(maxsize=100)
    transcript_q = TranscriptQueue()

    # Start the capture coroutine
    asyncio.create_task(audio_stream(audio_q, cfg))

    while True:
        raw_frame = await audio_q.get()
        processed = preprocess(raw_frame, cfg)
        await transcript_q.enqueue(processed)
        response = await transcript_q.get_response()
        print(f"[AI] {response}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_kilo_chat())
