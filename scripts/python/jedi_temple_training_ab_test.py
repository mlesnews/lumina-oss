#!/usr/bin/env python3
"""
Jedi Temple Training - A/B Testing

A/B testing framework for LUMINA education system.
Comparing different teaching methods to find the optimal way to teach
the public how to become a LUMINA Jedi.

Tags: #EDUCATION #AB_TESTING #JEDI_TRAINING #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
import random
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("JediTempleABTest")


class TeachingMethod(Enum):
    """Teaching methods for A/B testing"""
    METHOD_A = "method_a"  # Visual + Interactive (8-year-old friendly)
    METHOD_B = "method_b"  # Explanatory + Step-by-step (traditional)


class JediRank(Enum):
    """Jedi ranks (progression system)"""
    YOUNGLING = "youngling"  # Beginner
    PADAWAN = "padawan"  # Intermediate
    KNIGHT = "knight"  # Advanced
    MASTER = "master"  # Expert


class TestGroup:
    """A/B test group"""
    def __init__(self, group_id: str, method: TeachingMethod):
        self.group_id = group_id
        self.method = method
        self.participants: List[str] = []
        self.completion_times: List[float] = []
        self.success_rates: List[float] = []
        self.satisfaction_scores: List[float] = []
        self.created_at = datetime.now()

    def add_participant(self, participant_id: str):
        """Add participant to group"""
        if participant_id not in self.participants:
            self.participants.append(participant_id)

    def record_completion(self, participant_id: str, time_taken: float, success: bool, satisfaction: float):
        """Record participant completion"""
        if participant_id in self.participants:
            self.completion_times.append(time_taken)
            self.success_rates.append(1.0 if success else 0.0)
            self.satisfaction_scores.append(satisfaction)

    def get_statistics(self) -> Dict[str, Any]:
        """Get group statistics"""
        return {
            "group_id": self.group_id,
            "method": self.method.value,
            "participant_count": len(self.participants),
            "average_completion_time": sum(self.completion_times) / len(self.completion_times) if self.completion_times else 0,
            "success_rate": sum(self.success_rates) / len(self.success_rates) if self.success_rates else 0,
            "average_satisfaction": sum(self.satisfaction_scores) / len(self.satisfaction_scores) if self.satisfaction_scores else 0
        }


class JediTempleTrainingABTest:
    """
    A/B Testing for Jedi Temple Training Program

    Compares:
    - Method A: Visual + Interactive (8-year-old friendly)
    - Method B: Explanatory + Step-by-step (traditional)

    Goal: Find optimal way to teach public how to become LUMINA Jedi
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize A/B test"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jedi_temple_ab_test"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Test groups
        self.group_a = TestGroup("group_a", TeachingMethod.METHOD_A)
        self.group_b = TestGroup("group_b", TeachingMethod.METHOD_B)

        # Test configuration
        self.config_file = self.data_dir / "test_config.json"
        self.results_file = self.data_dir / "test_results.jsonl"

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")

        return {
            "version": "1.0.0",
            "test_name": "Jedi Temple Training A/B Test",
            "method_a": {
                "name": "Visual + Interactive",
                "description": "8-year-old friendly, visual demonstrations, hands-on practice",
                "features": [
                    "Visual demonstrations",
                    "Interactive exercises",
                    "Step-by-step with visuals",
                    "Gamified learning"
                ]
            },
            "method_b": {
                "name": "Explanatory + Step-by-step",
                "description": "Traditional teaching, detailed explanations, structured learning",
                "features": [
                    "Detailed explanations",
                    "Step-by-step instructions",
                    "Text-based tutorials",
                    "Structured progression"
                ]
            },
            "metrics": [
                "completion_time",
                "success_rate",
                "satisfaction_score",
                "knowledge_retention",
                "jedi_rank_achieved"
            ],
            "description": "A/B testing for LUMINA Jedi Temple Training Program",
            "tags": ["#EDUCATION", "#AB_TESTING", "#JEDI_TRAINING", "@JARVIS", "@LUMINA"]
        }

    def assign_participant(self, participant_id: str) -> TeachingMethod:
        """
        Assign participant to test group (random assignment)

        Returns: TeachingMethod assigned
        """
        # Random assignment (50/50 split)
        if random.random() < 0.5:
            method = TeachingMethod.METHOD_A
            self.group_a.add_participant(participant_id)
            logger.debug(f"   🎯 Assigned {participant_id} to Method A (Visual + Interactive)")
        else:
            method = TeachingMethod.METHOD_B
            self.group_b.add_participant(participant_id)
            logger.debug(f"   🎯 Assigned {participant_id} to Method B (Explanatory + Step-by-step)")

        return method

    def record_training_completion(
        self,
        participant_id: str,
        method: TeachingMethod,
        time_taken: float,
        success: bool,
        satisfaction: float,
        jedi_rank: Optional[JediRank] = None,
        knowledge_retention: Optional[float] = None
    ):
        """
        Record training completion

        Args:
            participant_id: ID of participant
            method: Teaching method used
            time_taken: Time to complete training (minutes)
            success: Whether training was completed successfully
            satisfaction: Satisfaction score (0-1)
            jedi_rank: Jedi rank achieved
            knowledge_retention: Knowledge retention score (0-1)
        """
        logger.info(f"   📊 Recording completion: {participant_id} ({method.value})")

        # Record in appropriate group
        if method == TeachingMethod.METHOD_A:
            self.group_a.record_completion(participant_id, time_taken, success, satisfaction)
        else:
            self.group_b.record_completion(participant_id, time_taken, success, satisfaction)

        # Save result
        result = {
            "timestamp": datetime.now().isoformat(),
            "participant_id": participant_id,
            "method": method.value,
            "time_taken": time_taken,
            "success": success,
            "satisfaction": satisfaction,
            "jedi_rank": jedi_rank.value if jedi_rank else None,
            "knowledge_retention": knowledge_retention
        }

        self._save_result(result)

    def _save_result(self, result: Dict[str, Any]):
        """Save test result"""
        try:
            with open(self.results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result) + '\n')
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save result: {e}")

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze A/B test results"""
        logger.info("   📊 Analyzing A/B test results...")

        stats_a = self.group_a.get_statistics()
        stats_b = self.group_b.get_statistics()

        # Calculate differences
        time_diff = stats_b["average_completion_time"] - stats_a["average_completion_time"]
        success_diff = stats_a["success_rate"] - stats_b["success_rate"]
        satisfaction_diff = stats_a["average_satisfaction"] - stats_b["average_satisfaction"]

        # Determine winner
        winner = "A" if (success_diff > 0 or (success_diff == 0 and satisfaction_diff > 0)) else "B"

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "method_a": {
                "name": self.config["method_a"]["name"],
                "statistics": stats_a
            },
            "method_b": {
                "name": self.config["method_b"]["name"],
                "statistics": stats_b
            },
            "comparison": {
                "time_difference": time_diff,
                "time_winner": "A" if time_diff < 0 else "B",
                "success_difference": success_diff,
                "success_winner": "A" if success_diff > 0 else "B",
                "satisfaction_difference": satisfaction_diff,
                "satisfaction_winner": "A" if satisfaction_diff > 0 else "B"
            },
            "overall_winner": winner,
            "recommendation": f"Method {winner} appears to be more effective based on current data"
        }

        return analysis

    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        return {
            "test_name": self.config["test_name"],
            "method_a": self.config["method_a"],
            "method_b": self.config["method_b"],
            "group_a_participants": len(self.group_a.participants),
            "group_b_participants": len(self.group_b.participants),
            "total_participants": len(self.group_a.participants) + len(self.group_b.participants)
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Jedi Temple Training A/B Test")
        parser.add_argument("--assign", help="Assign participant ID to test group")
        parser.add_argument("--complete", nargs=6, metavar=("PARTICIPANT", "METHOD", "TIME", "SUCCESS", "SATISFACTION", "RANK"),
                           help="Record training completion")
        parser.add_argument("--analyze", action="store_true", help="Analyze results")
        parser.add_argument("--summary", action="store_true", help="Show test summary")

        args = parser.parse_args()

        ab_test = JediTempleTrainingABTest()

        if args.assign:
            method = ab_test.assign_participant(args.assign)
            print(f"Assigned to: {method.value}")
        elif args.complete:
            participant_id, method_str, time_str, success_str, satisfaction_str, rank_str = args.complete
            method = TeachingMethod(method_str)
            time_taken = float(time_str)
            success = success_str.lower() == "true"
            satisfaction = float(satisfaction_str)
            jedi_rank = JediRank(rank_str) if rank_str != "None" else None

            ab_test.record_training_completion(
                participant_id=participant_id,
                method=method,
                time_taken=time_taken,
                success=success,
                satisfaction=satisfaction,
                jedi_rank=jedi_rank
            )
            print("✅ Completion recorded")
        elif args.analyze:
            analysis = ab_test.analyze_results()
            print(json.dumps(analysis, indent=2))
        elif args.summary:
            summary = ab_test.get_test_summary()
            print(json.dumps(summary, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())