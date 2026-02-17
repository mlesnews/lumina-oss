#!/usr/bin/env python3
"""
Speech Pathologist Feedback Loop

Continuous learning system that improves voice recognition accuracy by:
- Learning how people speak
- Learning how they pronounce words
- Improving transcription accuracy
- Adapting to individual speech patterns

Tags: #VOICE_RECOGNITION #LEARNING #FEEDBACK_LOOP #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("SpeechPathologistFeedback")


class SpeechPattern:
    """Speech pattern for a speaker"""
    def __init__(self, speaker_id: str):
        self.speaker_id = speaker_id
        self.pronunciations: Dict[str, List[str]] = defaultdict(list)  # word -> [pronunciations]
        self.speech_rate: float = 0.0  # Words per minute
        self.pause_patterns: List[float] = []  # Pause durations
        self.accent_features: Dict[str, Any] = {}
        self.sample_count = 0
        self.last_updated = datetime.now()

    def add_pronunciation(self, word: str, pronunciation: str):
        """Add pronunciation variant"""
        if pronunciation not in self.pronunciations[word]:
            self.pronunciations[word].append(pronunciation)
        self.sample_count += 1
        self.last_updated = datetime.now()

    def get_common_pronunciation(self, word: str) -> Optional[str]:
        """Get most common pronunciation for word"""
        if word in self.pronunciations and self.pronunciations[word]:
            # Return most frequent
            return self.pronunciations[word][0]
        return None


class SpeechPathologistFeedbackLoop:
    """
    Speech Pathologist Feedback Loop

    Continuously learns from voice interactions to improve accuracy:
    - How people speak
    - How they pronounce words
    - Individual speech patterns
    - Accent and dialect features
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize feedback loop"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "speech_pathologist"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.data_dir / "speech_patterns.json"
        self.feedback_file = self.data_dir / "feedback_history.jsonl"

        # Load existing patterns
        self.speech_patterns: Dict[str, SpeechPattern] = {}
        self._load_patterns()

    def _load_patterns(self):
        """Load speech patterns from disk"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for speaker_id, pattern_data in data.items():
                        pattern = SpeechPattern(speaker_id)
                        pattern.pronunciations = pattern_data.get("pronunciations", {})
                        pattern.speech_rate = pattern_data.get("speech_rate", 0.0)
                        pattern.pause_patterns = pattern_data.get("pause_patterns", [])
                        pattern.accent_features = pattern_data.get("accent_features", {})
                        pattern.sample_count = pattern_data.get("sample_count", 0)
                        self.speech_patterns[speaker_id] = pattern
                logger.debug(f"   📚 Loaded {len(self.speech_patterns)} speech patterns")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to load patterns: {e}")

    def _save_patterns(self):
        """Save speech patterns to disk"""
        try:
            data = {}
            for speaker_id, pattern in self.speech_patterns.items():
                data[speaker_id] = {
                    "pronunciations": dict(pattern.pronunciations),
                    "speech_rate": pattern.speech_rate,
                    "pause_patterns": pattern.pause_patterns,
                    "accent_features": pattern.accent_features,
                    "sample_count": pattern.sample_count,
                    "last_updated": pattern.last_updated.isoformat()
                }

            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"   💾 Saved {len(self.speech_patterns)} speech patterns")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save patterns: {e}")

    def learn_from_interaction(
        self,
        speaker_id: str,
        transcription: str,
        audio_features: Optional[Dict[str, Any]] = None,
        corrections: Optional[List[Dict[str, str]]] = None
    ):
        """
        Learn from voice interaction

        Args:
            speaker_id: ID of speaker
            transcription: Transcribed text
            audio_features: Audio features (pitch, tone, etc.)
            corrections: List of corrections {original: "...", corrected: "..."}
        """
        logger.debug(f"   📚 Learning from interaction: {speaker_id}")

        # Get or create pattern
        if speaker_id not in self.speech_patterns:
            self.speech_patterns[speaker_id] = SpeechPattern(speaker_id)

        pattern = self.speech_patterns[speaker_id]

        # Learn pronunciations from corrections
        if corrections:
            for correction in corrections:
                original = correction.get("original", "")
                corrected = correction.get("corrected", "")

                # Extract words
                words = corrected.split()
                for word in words:
                    # Learn how this word was pronounced (based on what was transcribed)
                    pattern.add_pronunciation(word, original)

        # Learn speech rate
        if audio_features:
            words_per_minute = audio_features.get("words_per_minute", 0)
            if words_per_minute > 0:
                # Update running average
                if pattern.speech_rate == 0:
                    pattern.speech_rate = words_per_minute
                else:
                    pattern.speech_rate = (pattern.speech_rate + words_per_minute) / 2

        # Learn pause patterns
        if audio_features and "pause_durations" in audio_features:
            pattern.pause_patterns.extend(audio_features["pause_durations"])
            # Keep only recent pauses (last 100)
            pattern.pause_patterns = pattern.pause_patterns[-100:]

        # Learn accent features
        if audio_features:
            accent_features = audio_features.get("accent_features", {})
            pattern.accent_features.update(accent_features)

        # Save feedback
        self._save_feedback(speaker_id, transcription, corrections)

        # Save patterns
        self._save_patterns()

    def _save_feedback(self, speaker_id: str, transcription: str, corrections: Optional[List[Dict[str, str]]]):
        """Save feedback to history"""
        try:
            feedback = {
                "timestamp": datetime.now().isoformat(),
                "speaker_id": speaker_id,
                "transcription": transcription,
                "corrections": corrections or []
            }

            with open(self.feedback_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback) + '\n')
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save feedback: {e}")

    def get_speaker_pattern(self, speaker_id: str) -> Optional[SpeechPattern]:
        """Get speech pattern for speaker"""
        return self.speech_patterns.get(speaker_id)

    def improve_transcription(
        self,
        speaker_id: str,
        raw_transcription: str
    ) -> str:
        """
        Improve transcription using learned patterns

        Uses learned pronunciations and speech patterns to correct transcription
        """
        if speaker_id not in self.speech_patterns:
            return raw_transcription

        pattern = self.speech_patterns[speaker_id]
        improved = raw_transcription

        # Apply learned pronunciations
        words = raw_transcription.split()
        corrected_words = []

        for word in words:
            # Check if we have a learned pronunciation for this word
            common_pronunciation = pattern.get_common_pronunciation(word)
            if common_pronunciation and common_pronunciation != word:
                # Use learned pronunciation
                corrected_words.append(common_pronunciation)
            else:
                corrected_words.append(word)

        improved = " ".join(corrected_words)

        if improved != raw_transcription:
            logger.debug(f"   ✨ Improved transcription using learned patterns")

        return improved

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        total_samples = sum(p.sample_count for p in self.speech_patterns.values())
        total_words = sum(len(p.pronunciations) for p in self.speech_patterns.values())

        return {
            "speakers_learned": len(self.speech_patterns),
            "total_samples": total_samples,
            "total_words_learned": total_words,
            "average_samples_per_speaker": total_samples / len(self.speech_patterns) if self.speech_patterns else 0,
            "speakers": {
                speaker_id: {
                    "samples": pattern.sample_count,
                    "words_learned": len(pattern.pronunciations),
                    "speech_rate": pattern.speech_rate
                }
                for speaker_id, pattern in self.speech_patterns.items()
            }
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Speech Pathologist Feedback Loop")
        parser.add_argument("--learn", action="store_true", help="Learn from interaction")
        parser.add_argument("--stats", action="store_true", help="Show statistics")
        parser.add_argument("--improve", help="Improve transcription for speaker")

        args = parser.parse_args()

        feedback_loop = SpeechPathologistFeedbackLoop()

        if args.learn:
            # Example learning
            feedback_loop.learn_from_interaction(
                speaker_id="user",
                transcription="Hello world",
                corrections=[
                    {"original": "helo", "corrected": "hello"},
                    {"original": "wurld", "corrected": "world"}
                ]
            )
            logger.info("   ✅ Learned from interaction")
        elif args.stats:
            stats = feedback_loop.get_statistics()
            print(json.dumps(stats, indent=2))
        elif args.improve:
            improved = feedback_loop.improve_transcription("user", args.improve)
            print(f"Original: {args.improve}")
            print(f"Improved: {improved}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())