#!/usr/bin/env python3
"""
Voice Coding A/B Testing

Compare effectiveness of:
- A: Traditional coding (text input)
- B: Voice coding (voice input, transcribed to text)

Hypothesis: If everything is transcribed, then text = text, so it should be the same thing.

Tags: #VOICE_CODING #AB_TESTING #EXPERIMENT #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("VoiceCodingABTest")


class InputMethod(Enum):
    """Input methods"""
    TEXT = "text"  # Traditional coding
    VOICE = "voice"  # Voice coding (transcribed)


class ABTestResult:
    """A/B test result"""
    def __init__(self, method: InputMethod, task: str, time_taken: float, accuracy: float, user_satisfaction: float):
        self.method = method
        self.task = task
        self.time_taken = time_taken
        self.accuracy = accuracy
        self.user_satisfaction = user_satisfaction
        self.timestamp = datetime.now()


class VoiceCodingABTest:
    """
    A/B Testing for Voice Coding

    Compare:
    - A: Text coding (keyboard input)
    - B: Voice coding (voice input, transcribed)

    Hypothesis: If transcribed, text = text, so should be same.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize A/B test"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.results_dir = self.project_root / "data" / "voice_coding_ab_test"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.results: List[ABTestResult] = []

    def run_test(
        self,
        task: str,
        text_input: str,
        voice_transcription: str,
        time_text: float,
        time_voice: float,
        accuracy_text: float = 1.0,
        accuracy_voice: float = 1.0,
        satisfaction_text: float = 0.0,
        satisfaction_voice: float = 0.0
    ) -> Dict[str, Any]:
        """
        Run A/B test comparing text vs. voice coding

        Args:
            task: Description of coding task
            text_input: Code written via text
            voice_transcription: Code transcribed from voice
            time_text: Time taken for text input
            time_voice: Time taken for voice input
            accuracy_text: Accuracy of text input (0-1)
            accuracy_voice: Accuracy of voice transcription (0-1)
            satisfaction_text: User satisfaction with text (0-1)
            satisfaction_voice: User satisfaction with voice (0-1)
        """
        logger.info(f"   🧪 Running A/B test: {task}")

        # Create test results
        result_text = ABTestResult(
            method=InputMethod.TEXT,
            task=task,
            time_taken=time_text,
            accuracy=accuracy_text,
            user_satisfaction=satisfaction_text
        )

        result_voice = ABTestResult(
            method=InputMethod.VOICE,
            task=task,
            time_taken=time_voice,
            accuracy=accuracy_voice,
            user_satisfaction=satisfaction_voice
        )

        self.results.append(result_text)
        self.results.append(result_voice)

        # Compare results
        comparison = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "text": {
                "time": time_text,
                "accuracy": accuracy_text,
                "satisfaction": satisfaction_text,
                "input": text_input[:100] + "..." if len(text_input) > 100 else text_input
            },
            "voice": {
                "time": time_voice,
                "accuracy": accuracy_voice,
                "satisfaction": satisfaction_voice,
                "transcription": voice_transcription[:100] + "..." if len(voice_transcription) > 100 else voice_transcription
            },
            "comparison": {
                "time_difference": time_voice - time_text,
                "time_winner": "voice" if time_voice < time_text else "text",
                "accuracy_difference": accuracy_voice - accuracy_text,
                "accuracy_winner": "voice" if accuracy_voice > accuracy_text else "text",
                "satisfaction_difference": satisfaction_voice - satisfaction_text,
                "satisfaction_winner": "voice" if satisfaction_voice > satisfaction_text else "text"
            },
            "hypothesis_test": {
                "text_equals_text": text_input.strip() == voice_transcription.strip(),
                "if_transcribed_then_same": "If transcribed correctly, text = text, so should be same"
            }
        }

        # Save results
        self._save_result(comparison)

        logger.info(f"   ✅ Test complete: {task}")
        logger.info(f"      Time: {comparison['comparison']['time_winner']} wins")
        logger.info(f"      Accuracy: {comparison['comparison']['accuracy_winner']} wins")
        logger.info(f"      Satisfaction: {comparison['comparison']['satisfaction_winner']} wins")

        return comparison

    def _save_result(self, result: Dict[str, Any]):
        """Save test result"""
        result_file = self.results_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            logger.debug(f"   💾 Result saved: {result_file.name}")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save result: {e}")

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze all test results"""
        if not self.results:
            return {"error": "No results to analyze"}

        text_results = [r for r in self.results if r.method == InputMethod.TEXT]
        voice_results = [r for r in self.results if r.method == InputMethod.VOICE]

        analysis = {
            "total_tests": len(self.results) // 2,
            "text_average": {
                "time": sum(r.time_taken for r in text_results) / len(text_results) if text_results else 0,
                "accuracy": sum(r.accuracy for r in text_results) / len(text_results) if text_results else 0,
                "satisfaction": sum(r.user_satisfaction for r in text_results) / len(text_results) if text_results else 0
            },
            "voice_average": {
                "time": sum(r.time_taken for r in voice_results) / len(voice_results) if voice_results else 0,
                "accuracy": sum(r.accuracy for r in voice_results) / len(voice_results) if voice_results else 0,
                "satisfaction": sum(r.user_satisfaction for r in voice_results) / len(voice_results) if voice_results else 0
            },
            "conclusion": "Analysis complete"
        }

        return analysis


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Voice Coding A/B Test")
        parser.add_argument("--test", action="store_true", help="Run test")
        parser.add_argument("--analyze", action="store_true", help="Analyze results")

        args = parser.parse_args()

        ab_test = VoiceCodingABTest()

        if args.test:
            # Example test
            result = ab_test.run_test(
                task="Write a simple Python function",
                text_input="def hello(): print('Hello')",
                voice_transcription="def hello(): print('Hello')",
                time_text=10.5,
                time_voice=8.2,
                accuracy_text=1.0,
                accuracy_voice=0.95,
                satisfaction_text=0.7,
                satisfaction_voice=0.9
            )
            print(json.dumps(result, indent=2))
        elif args.analyze:
            analysis = ab_test.analyze_results()
            print(json.dumps(analysis, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())