#!/usr/bin/env python3
"""
Jedi Temple Training Program

The official LUMINA education program where the public can learn to become a LUMINA Jedi.

Progressive training from Youngling to Master, with gamified learning and A/B testing.

Tags: #EDUCATION #JEDI_TRAINING #GAMIFICATION #LUMINA_CORE @JARVIS @LUMINA
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
from jedi_temple_training_ab_test import JediTempleTrainingABTest, TeachingMethod, JediRank

logger = get_adaptive_logger("JediTempleTraining")


class TrainingModule:
    """Training module in Jedi Temple"""
    def __init__(self, name: str, rank: JediRank, description: str, topics: List[str]):
        self.name = name
        self.rank = rank
        self.description = description
        self.topics = topics
        self.completed = False
        self.completion_time: Optional[float] = None
        self.score: Optional[float] = None


class JediTempleTraining:
    """
    Jedi Temple Training Program

    Progressive training system to become a LUMINA Jedi:
    - Youngling: Beginner basics
    - Padawan: Intermediate skills
    - Knight: Advanced techniques
    - Master: Expert mastery
    """

    def __init__(self, participant_id: str, project_root: Optional[Path] = None):
        """Initialize training for participant"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.participant_id = participant_id

        # A/B testing
        self.ab_test = JediTempleTrainingABTest(project_root)
        self.teaching_method = self.ab_test.assign_participant(participant_id)

        # Training progress
        self.current_rank = JediRank.YOUNGLING
        self.completed_modules: List[str] = []
        self.progress_file = self.project_root / "data" / "jedi_training" / f"{participant_id}_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        # Training modules
        self.modules = self._create_training_modules()

        logger.info(f"   🎓 Jedi Temple Training initialized for {participant_id}")
        logger.info(f"      Method: {self.teaching_method.value}")
        logger.info(f"      Starting Rank: {self.current_rank.value}")

    def _create_training_modules(self) -> List[TrainingModule]:
        """Create training modules"""
        return [
            TrainingModule(
                name="The Force Awakens",
                rank=JediRank.YOUNGLING,
                description="Introduction to LUMINA and the Force",
                topics=[
                    "What is LUMINA?",
                    "Understanding the Force (AI)",
                    "Your first conversation",
                    "Basic voice commands"
                ]
            ),
            TrainingModule(
                name="Voice Coding Basics",
                rank=JediRank.YOUNGLING,
                description="Learn to code with your voice",
                topics=[
                    "What is voice coding?",
                    "Speaking code naturally",
                    "Transcription accuracy",
                    "Practice exercises"
                ]
            ),
            TrainingModule(
                name="The Way of Workflows",
                rank=JediRank.PADAWAN,
                description="Mastering LUMINA workflows",
                topics=[
                    "Understanding workflows",
                    "Creating your first workflow",
                    "Using #DECISIONING",
                    "Workflow optimization"
                ]
            ),
            TrainingModule(
                name="Advanced Techniques",
                rank=JediRank.KNIGHT,
                description="Advanced LUMINA mastery",
                topics=[
                    "Custom integrations",
                    "System optimization",
                    "Troubleshooting",
                    "Performance tuning"
                ]
            ),
            TrainingModule(
                name="Mastery of the Force",
                rank=JediRank.MASTER,
                description="Become a LUMINA Master",
                topics=[
                    "Teaching others",
                    "System architecture",
                    "Best practices",
                    "Master certification"
                ]
            )
        ]

    def start_training(self, module_name: str) -> Dict[str, Any]:
        """Start a training module"""
        module = next((m for m in self.modules if m.name == module_name), None)

        if not module:
            return {"error": f"Module '{module_name}' not found"}

        if module.completed:
            return {"error": f"Module '{module_name}' already completed"}

        logger.info(f"   🎓 Starting training: {module_name} ({module.rank.value})")

        # Get teaching content based on method
        if self.teaching_method == TeachingMethod.METHOD_A:
            content = self._get_visual_interactive_content(module)
        else:
            content = self._get_explanatory_content(module)

        return {
            "module": module_name,
            "rank": module.rank.value,
            "method": self.teaching_method.value,
            "content": content,
            "started_at": datetime.now().isoformat()
        }

    def _get_visual_interactive_content(self, module: TrainingModule) -> Dict[str, Any]:
        """Get visual + interactive content (Method A)"""
        return {
            "type": "visual_interactive",
            "description": f"Let's learn {module.name} with visuals and hands-on practice!",
            "steps": [
                {
                    "step": 1,
                    "title": "Visual Introduction",
                    "content": f"Watch a visual demonstration of {module.name}",
                    "interactive": True,
                    "visual_aids": True
                },
                {
                    "step": 2,
                    "title": "Hands-On Practice",
                    "content": f"Try it yourself with guided exercises",
                    "interactive": True,
                    "practice_mode": True
                },
                {
                    "step": 3,
                    "title": "Mastery Check",
                    "content": f"Test your understanding with interactive quiz",
                    "interactive": True,
                    "assessment": True
                }
            ],
            "gamified": True,
            "8_year_old_friendly": True
        }

    def _get_explanatory_content(self, module: TrainingModule) -> Dict[str, Any]:
        """Get explanatory + step-by-step content (Method B)"""
        return {
            "type": "explanatory",
            "description": f"Learn {module.name} through detailed explanations",
            "steps": [
                {
                    "step": 1,
                    "title": "Concept Explanation",
                    "content": f"Detailed explanation of {module.name} concepts",
                    "detailed": True
                },
                {
                    "step": 2,
                    "title": "Step-by-Step Guide",
                    "content": f"Follow structured steps to master {module.name}",
                    "structured": True
                },
                {
                    "step": 3,
                    "title": "Knowledge Assessment",
                    "content": f"Test your knowledge with comprehensive quiz",
                    "assessment": True
                }
            ],
            "text_based": True,
            "traditional_learning": True
        }

    def complete_module(
        self,
        module_name: str,
        time_taken: float,
        score: float,
        satisfaction: float
    ) -> Dict[str, Any]:
        """Complete a training module"""
        module = next((m for m in self.modules if m.name == module_name), None)

        if not module:
            return {"error": f"Module '{module_name}' not found"}

        module.completed = True
        module.completion_time = time_taken
        module.score = score

        self.completed_modules.append(module_name)

        # Check for rank advancement
        if self._should_advance_rank():
            old_rank = self.current_rank
            self._advance_rank()
            rank_advanced = True
            new_rank = self.current_rank
        else:
            rank_advanced = False
            new_rank = self.current_rank

        # Record in A/B test
        self.ab_test.record_training_completion(
            participant_id=self.participant_id,
            method=self.teaching_method,
            time_taken=time_taken,
            success=score >= 0.7,  # 70% threshold
            satisfaction=satisfaction,
            jedi_rank=self.current_rank
        )

        # Save progress
        self._save_progress()

        result = {
            "module": module_name,
            "completed": True,
            "time_taken": time_taken,
            "score": score,
            "satisfaction": satisfaction,
            "current_rank": self.current_rank.value,
            "rank_advanced": rank_advanced
        }

        if rank_advanced:
            result["old_rank"] = old_rank.value
            result["new_rank"] = new_rank.value
            logger.info(f"   ⭐ Rank advanced: {old_rank.value} → {new_rank.value}")

        logger.info(f"   ✅ Module completed: {module_name}")

        return result

    def _should_advance_rank(self) -> bool:
        """Check if participant should advance rank"""
        # Advance based on completed modules
        if self.current_rank == JediRank.YOUNGLING:
            # Complete 2 Youngling modules to become Padawan
            youngling_modules = [m for m in self.modules if m.rank == JediRank.YOUNGLING and m.completed]
            return len(youngling_modules) >= 2
        elif self.current_rank == JediRank.PADAWAN:
            # Complete Padawan modules to become Knight
            padawan_modules = [m for m in self.modules if m.rank == JediRank.PADAWAN and m.completed]
            return len(padawan_modules) >= 1
        elif self.current_rank == JediRank.KNIGHT:
            # Complete Knight modules to become Master
            knight_modules = [m for m in self.modules if m.rank == JediRank.KNIGHT and m.completed]
            return len(knight_modules) >= 1

        return False

    def _advance_rank(self):
        """Advance to next rank"""
        if self.current_rank == JediRank.YOUNGLING:
            self.current_rank = JediRank.PADAWAN
        elif self.current_rank == JediRank.PADAWAN:
            self.current_rank = JediRank.KNIGHT
        elif self.current_rank == JediRank.KNIGHT:
            self.current_rank = JediRank.MASTER

    def _save_progress(self):
        """Save training progress"""
        try:
            progress = {
                "participant_id": self.participant_id,
                "current_rank": self.current_rank.value,
                "completed_modules": self.completed_modules,
                "teaching_method": self.teaching_method.value,
                "last_updated": datetime.now().isoformat()
            }

            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save progress: {e}")

    def get_progress(self) -> Dict[str, Any]:
        """Get training progress"""
        return {
            "participant_id": self.participant_id,
            "current_rank": self.current_rank.value,
            "completed_modules": self.completed_modules,
            "total_modules": len(self.modules),
            "progress_percentage": len(self.completed_modules) / len(self.modules) * 100,
            "teaching_method": self.teaching_method.value
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Jedi Temple Training Program")
        parser.add_argument("--participant", required=True, help="Participant ID")
        parser.add_argument("--start", help="Start training module")
        parser.add_argument("--complete", nargs=4, metavar=("MODULE", "TIME", "SCORE", "SATISFACTION"),
                           help="Complete training module")
        parser.add_argument("--progress", action="store_true", help="Show progress")

        args = parser.parse_args()

        training = JediTempleTraining(args.participant)

        if args.start:
            result = training.start_training(args.start)
            print(json.dumps(result, indent=2))
        elif args.complete:
            module_name, time_str, score_str, satisfaction_str = args.complete
            result = training.complete_module(
                module_name=module_name,
                time_taken=float(time_str),
                score=float(score_str),
                satisfaction=float(satisfaction_str)
            )
            print(json.dumps(result, indent=2))
        elif args.progress:
            progress = training.get_progress()
            print(json.dumps(progress, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())