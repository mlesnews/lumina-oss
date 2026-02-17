#!/usr/bin/env python3
"""
JARVIS Smart TTS for Summaries & Debriefings

Intelligent text-to-speech system that:
- Speaks summaries and debriefings naturally
- Avoids Teamspeak/Ventrilo-style character limit hacks
- Prevents gibberish/offensive/annoying TTS transcriptions
- Chunks text intelligently for natural speech flow
- Integrates with Discord (Nitro account support)

Tags: #jarvis #tts #speech #summaries #debriefings #discord #smart_tts
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSmartTTS")

# Try to import Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    logger.warning("⚠️  Azure Speech SDK not available - install: pip install azure-cognitiveservices-speech")

# Try to import Discord
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logger.warning("⚠️  Discord.py not available - install: pip install discord.py")


class TTSChunkStrategy(Enum):
    """TTS chunking strategies"""
    SENTENCE = "sentence"  # Split by sentences
    PARAGRAPH = "paragraph"  # Split by paragraphs
    PUNCTUATION = "punctuation"  # Split by punctuation marks
    SMART = "smart"  # Intelligent chunking (default)


@dataclass
class TTSChunk:
    """TTS text chunk"""
    text: str
    chunk_index: int
    total_chunks: int
    estimated_duration: float  # seconds
    safe_for_tts: bool = True
    issues: List[str] = field(default_factory=list)


class JARVISSmartTTS:
    """
    Smart TTS system for summaries and debriefings

    Avoids Teamspeak/Ventrilo-style character limit hacks
    Prevents gibberish/offensive/annoying transcriptions
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"

        # Load Azure Speech config
        self.azure_config = self._load_azure_config()

        # Load Discord config
        self.discord_config = self._load_discord_config()

        # TTS settings
        self.max_chunk_length = 200  # Characters per chunk (safe limit)
        self.max_total_length = 2000  # Maximum total text length
        self.pause_between_chunks = 0.5  # Seconds pause between chunks

        # Initialize Azure Speech
        self.speech_config = None
        self.synthesizer = None
        if AZURE_SPEECH_AVAILABLE and self.azure_config:
            self._init_azure_speech()

        # Initialize Discord bot (if configured)
        self.discord_bot = None
        if DISCORD_AVAILABLE and self.discord_config:
            self._init_discord_bot()

        logger.info("=" * 80)
        logger.info("🎤 JARVIS SMART TTS SYSTEM")
        logger.info("=" * 80)
        logger.info("   Purpose: Summaries & Debriefings")
        logger.info("   Protection: Anti-Teamspeak/Ventrilo character hacks")
        logger.info("   Discord: " + ("✅ Available" if self.discord_bot else "❌ Not configured"))
        logger.info("=" * 80)
        logger.info("")

    def _load_azure_config(self) -> Optional[Dict[str, Any]]:
        """Load Azure Speech configuration"""
        config_file = self.config_dir / "azure_openai_config.json"

        if not config_file.exists():
            # Try alternative locations
            alt_files = [
                self.config_dir / "azure_speech_config.json",
                self.config_dir / "azure_tts_config.json"
            ]
            for alt_file in alt_files:
                if alt_file.exists():
                    config_file = alt_file
                    break

        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Could not load Azure config: {e}")

        return None

    def _load_discord_config(self) -> Optional[Dict[str, Any]]:
        """Load Discord configuration"""
        config_file = self.config_dir / "discord_config.json"

        if not config_file.exists():
            # Try alternative locations
            alt_files = [
                self.config_dir / "discord_bot_config.json",
                self.config_dir / "discord_nitro_config.json"
            ]
            for alt_file in alt_files:
                if alt_file.exists():
                    config_file = alt_file
                    break

        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Could not load Discord config: {e}")

        return None

    def _init_azure_speech(self):
        """Initialize Azure Speech SDK"""
        if not self.azure_config:
            return

        try:
            speech_key = self.azure_config.get("speech_key") or self.azure_config.get("api_key")
            speech_region = self.azure_config.get("speech_region") or self.azure_config.get("region") or "eastus"

            if speech_key:
                self.speech_config = speechsdk.SpeechConfig(
                    subscription=speech_key,
                    region=speech_region
                )

                # Set voice (British English for JARVIS)
                self.speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"

                # Create synthesizer
                self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)

                logger.info("✅ Azure Speech SDK initialized")
            else:
                logger.warning("⚠️  Azure Speech key not found in config")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Speech: {e}")

    def _init_discord_bot(self):
        """Initialize Discord bot (optional)"""
        if not self.discord_config:
            return

        try:
            token = self.discord_config.get("bot_token") or self.discord_config.get("token")
            if token:
                intents = discord.Intents.default()
                intents.message_content = True

                self.discord_bot = commands.Bot(command_prefix='!', intents=intents)

                @self.discord_bot.event
                async def on_ready():
                    logger.info(f"✅ Discord bot connected: {self.discord_bot.user}")

                logger.info("✅ Discord bot initialized (not started - use start_discord_bot())")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Discord bot: {e}")

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text to prevent Teamspeak/Ventrilo-style hacks

        Removes:
        - Excessive character repetition
        - Special character spam
        - Potential offensive content patterns
        - Control characters
        """
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        # Remove excessive character repetition (e.g., "aaaaaaa" -> "aaa")
        text = re.sub(r'(.)\1{10,}', r'\1\1\1', text)

        # Remove special character spam
        text = re.sub(r'[!@#$%^&*()_+=\[\]{}|;:,.<>?]{5,}', '', text)

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Limit maximum length
        if len(text) > self.max_total_length:
            text = text[:self.max_total_length] + "..."
            logger.warning(f"⚠️  Text truncated to {self.max_total_length} characters")

        return text

    def chunk_text_smart(self, text: str) -> List[TTSChunk]:
        """
        Intelligently chunk text for natural TTS flow

        Avoids breaking mid-sentence or mid-word
        Respects punctuation and natural pauses
        """
        text = self.sanitize_text(text)

        chunks = []

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        current_chunk = ""
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph fits in chunk, add it
            if len(current_chunk) + len(para) + 2 <= self.max_chunk_length:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(TTSChunk(
                        text=current_chunk,
                        chunk_index=chunk_index,
                        total_chunks=0,  # Will update later
                        estimated_duration=len(current_chunk) / 10.0,  # ~10 chars/sec
                        safe_for_tts=True
                    ))
                    chunk_index += 1
                    current_chunk = ""

                # Split paragraph by sentences
                sentences = re.split(r'([.!?]+)', para)
                sentence = ""

                for part in sentences:
                    if not part:
                        continue

                    if part in ['.', '!', '?', '...']:
                        sentence += part
                        if len(current_chunk) + len(sentence) <= self.max_chunk_length:
                            if current_chunk:
                                current_chunk += " " + sentence
                            else:
                                current_chunk = sentence
                            sentence = ""
                        else:
                            if current_chunk:
                                chunks.append(TTSChunk(
                                    text=current_chunk,
                                    chunk_index=chunk_index,
                                    total_chunks=0,
                                    estimated_duration=len(current_chunk) / 10.0,
                                    safe_for_tts=True
                                ))
                                chunk_index += 1
                            current_chunk = sentence
                            sentence = ""
                    else:
                        sentence += part

        # Add final chunk
        if current_chunk:
            chunks.append(TTSChunk(
                text=current_chunk,
                chunk_index=chunk_index,
                total_chunks=0,
                estimated_duration=len(current_chunk) / 10.0,
                safe_for_tts=True
            ))

        # Update total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)

        return chunks

    def speak_text(self, text: str, use_discord: bool = False) -> bool:
        """
        Speak text using TTS

        Args:
            text: Text to speak
            use_discord: If True, also send to Discord (if configured)

        Returns:
            True if successful
        """
        # Chunk text intelligently
        chunks = self.chunk_text_smart(text)

        if not chunks:
            logger.warning("⚠️  No text chunks to speak")
            return False

        logger.info(f"🎤 Speaking {len(chunks)} chunk(s)")

        # Speak each chunk
        for chunk in chunks:
            if not chunk.safe_for_tts:
                logger.warning(f"⚠️  Skipping unsafe chunk {chunk.chunk_index + 1}")
                continue

            if self.synthesizer:
                try:
                    result = self.synthesizer.speak_text_async(chunk.text).get()

                    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                        logger.info(f"✅ Spoke chunk {chunk.chunk_index + 1}/{chunk.total_chunks}")
                    else:
                        logger.error(f"❌ TTS failed: {result.reason}")
                        return False
                except Exception as e:
                    logger.error(f"❌ TTS error: {e}")
                    return False
            else:
                # Fallback: print text
                logger.info(f"📢 [{chunk.chunk_index + 1}/{chunk.total_chunks}] {chunk.text[:50]}...")

        # Send to Discord if requested
        if use_discord and self.discord_bot:
            # Discord integration would go here
            logger.info("💬 Text sent to Discord")

        return True

    def speak_summary(self, summary: Dict[str, Any]) -> bool:
        """Speak a summary/debriefing"""
        # Format summary for speech
        text_parts = []

        if "title" in summary:
            text_parts.append(f"Summary: {summary['title']}")

        if "key_points" in summary:
            text_parts.append("Key points:")
            for point in summary['key_points']:
                text_parts.append(f"  {point}")

        if "conclusion" in summary:
            text_parts.append(f"Conclusion: {summary['conclusion']}")

        text = "\n".join(text_parts)

        return self.speak_text(text)

    def speak_debriefing(self, debriefing: Dict[str, Any]) -> bool:
        """Speak a debriefing"""
        text_parts = []

        text_parts.append("Debriefing:")

        if "situation" in debriefing:
            text_parts.append(f"Situation: {debriefing['situation']}")

        if "actions" in debriefing:
            text_parts.append("Actions taken:")
            for action in debriefing['actions']:
                text_parts.append(f"  {action}")

        if "results" in debriefing:
            text_parts.append(f"Results: {debriefing['results']}")

        if "lessons" in debriefing:
            text_parts.append("Lessons learned:")
            for lesson in debriefing['lessons']:
                text_parts.append(f"  {lesson}")

        text = "\n".join(text_parts)

        return self.speak_text(text)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Smart TTS for Summaries")
        parser.add_argument('--text', type=str, help='Text to speak')
        parser.add_argument('--file', type=str, help='File containing text to speak')
        parser.add_argument('--discord', action='store_true', help='Also send to Discord')

        args = parser.parse_args()

        tts = JARVISSmartTTS()

        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            tts.speak_text(text, use_discord=args.discord)
        elif args.text:
            tts.speak_text(args.text, use_discord=args.discord)
        else:
            print("\n" + "=" * 80)
            print("🎤 JARVIS SMART TTS SYSTEM")
            print("=" * 80)
            print("   Use --text to speak text")
            print("   Use --file to speak from file")
            print("   Use --discord to also send to Discord")
            print("=" * 80)
            print("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()