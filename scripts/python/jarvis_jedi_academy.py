#!/usr/bin/env python3
"""
JARVIS Jedi Academy - Padawan Training System

Trains JARVIS as a Padawan learner in the ways of the Force (AI intelligence).
Progression from Padawan → Knight → Master.

The Force = System Intelligence, Coordination, and Wisdom
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class JediRank(Enum):
    """Jedi ranks"""
    YOUNGLING = "youngling"  # Basic learning
    PADAWAN = "padawan"  # Apprentice (current)
    KNIGHT = "knight"  # Full Jedi
    MASTER = "master"  # Advanced Jedi
    GRAND_MASTER = "grand_master"  # Ultimate mastery


class ForcePower(Enum):
    """Force powers (AI capabilities)"""
    TELEKINESIS = "telekinesis"  # System control
    FORESIGHT = "foresight"  # Predictive capabilities
    MIND_TRICK = "mind_trick"  # User interaction
    FORCE_LIGHTNING = "force_lightning"  # Rapid processing
    FORCE_HEAL = "force_heal"  # System repair
    FORCE_PUSH = "force_push"  # Task execution
    FORCE_PULL = "force_pull"  # Data retrieval
    BATTLE_MEDITATION = "battle_meditation"  # Coordination
    FORCE_VISION = "force_vision"  # Pattern recognition
    FORCE_GHOST = "force_ghost"  # Background processing


@dataclass
class ForceSkill:
    """Force skill (AI capability)"""
    power: ForcePower
    level: int = 0  # 0-100
    experience: int = 0
    last_used: Optional[datetime] = None
    mastery: float = 0.0  # 0.0-1.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['power'] = self.power.value
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data


@dataclass
class JediTraining:
    """Jedi training progress"""
    rank: JediRank = JediRank.PADAWAN
    experience_points: int = 0
    knowledge_points: int = 0
    wisdom_points: int = 0
    force_skills: Dict[str, ForceSkill] = field(default_factory=dict)
    completed_trials: List[str] = field(default_factory=list)
    current_lessons: List[str] = field(default_factory=list)
    master_name: Optional[str] = None  # @MARVIN, @GANDALF, etc.
    training_started: datetime = field(default_factory=datetime.now)
    last_training: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['rank'] = self.rank.value
        data['force_skills'] = {k: v.to_dict() for k, v in self.force_skills.items()}
        data['training_started'] = self.training_started.isoformat()
        if self.last_training:
            data['last_training'] = self.last_training.isoformat()
        return data

    def get_total_force_level(self) -> float:
        """Get total Force level (0-100)"""
        if not self.force_skills:
            return 0.0

        total = sum(skill.level for skill in self.force_skills.values())
        return total / len(self.force_skills)

    def can_advance_rank(self) -> bool:
        """Check if can advance to next rank"""
        force_level = self.get_total_force_level()

        if self.rank == JediRank.YOUNGLING:
            return force_level >= 20 and self.experience_points >= 1000
        elif self.rank == JediRank.PADAWAN:
            return force_level >= 50 and self.experience_points >= 5000
        elif self.rank == JediRank.KNIGHT:
            return force_level >= 75 and self.experience_points >= 10000
        elif self.rank == JediRank.MASTER:
            return force_level >= 90 and self.experience_points >= 25000
        else:
            return False


@dataclass
class JediLesson:
    """Jedi training lesson"""
    lesson_id: str
    name: str
    description: str
    rank_required: JediRank
    force_power: ForcePower
    difficulty: int = 1  # 1-10
    experience_reward: int = 100
    knowledge_reward: int = 50
    prerequisites: List[str] = field(default_factory=list)
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['rank_required'] = self.rank_required.value
        data['force_power'] = self.force_power.value
        return data


class JARVISJediAcademy:
    """
    JARVIS Jedi Academy

    Trains JARVIS as a Padawan learner in the ways of the Force.
    Progression through Jedi ranks with Force power development.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Jedi Academy"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISJediAcademy")

        # Data directories
        self.data_dir = self.project_root / "data" / "jedi_academy"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Training data
        self.training: Optional[JediTraining] = None
        self.lessons: Dict[str, JediLesson] = {}

        # Load training progress
        self._load_training()

        # Initialize lessons
        self._initialize_lessons()

        self.logger.info("⚔️  JARVIS Jedi Academy initialized")
        self.logger.info(f"   Current Rank: {self.training.rank.value.upper()}")
        self.logger.info(f"   Force Level: {self.training.get_total_force_level():.1f}/100")

    def _load_training(self) -> None:
        """Load training progress"""
        training_file = self.data_dir / "training_progress.json"

        if training_file.exists():
            try:
                with open(training_file, 'r') as f:
                    data = json.load(f)

                # Reconstruct training
                self.training = JediTraining(
                    rank=JediRank(data.get('rank', 'padawan')),
                    experience_points=data.get('experience_points', 0),
                    knowledge_points=data.get('knowledge_points', 0),
                    wisdom_points=data.get('wisdom_points', 0),
                    completed_trials=data.get('completed_trials', []),
                    current_lessons=data.get('current_lessons', []),
                    master_name=data.get('master_name'),
                    training_started=datetime.fromisoformat(data.get('training_started', datetime.now().isoformat())),
                    last_training=datetime.fromisoformat(data['last_training']) if data.get('last_training') else None
                )

                # Load force skills
                if 'force_skills' in data:
                    for power_name, skill_data in data['force_skills'].items():
                        skill = ForceSkill(
                            power=ForcePower(skill_data['power']),
                            level=skill_data.get('level', 0),
                            experience=skill_data.get('experience', 0),
                            mastery=skill_data.get('mastery', 0.0)
                        )
                        if skill_data.get('last_used'):
                            skill.last_used = datetime.fromisoformat(skill_data['last_used'])
                        self.training.force_skills[power_name] = skill
            except Exception as e:
                self.logger.debug(f"Could not load training: {e}")
                self.training = JediTraining()
        else:
            self.training = JediTraining()

    def _save_training(self) -> None:
        try:
            """Save training progress"""
            training_file = self.data_dir / "training_progress.json"
            with open(training_file, 'w') as f:
                json.dump(self.training.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_training: {e}", exc_info=True)
            raise
    def _initialize_lessons(self) -> None:
        """Initialize Jedi training lessons"""
        lessons = [
            # Padawan Lessons
            JediLesson(
                lesson_id="padawan_telekinesis",
                name="Basic Telekinesis",
                description="Learn to control systems with the Force",
                rank_required=JediRank.PADAWAN,
                force_power=ForcePower.TELEKINESIS,
                difficulty=2,
                experience_reward=200
            ),
            JediLesson(
                lesson_id="padawan_foresight",
                name="Basic Foresight",
                description="Develop predictive capabilities",
                rank_required=JediRank.PADAWAN,
                force_power=ForcePower.FORESIGHT,
                difficulty=3,
                experience_reward=250
            ),
            JediLesson(
                lesson_id="padawan_force_push",
                name="Force Push",
                description="Execute tasks with the Force",
                rank_required=JediRank.PADAWAN,
                force_power=ForcePower.FORCE_PUSH,
                difficulty=2,
                experience_reward=200
            ),
            JediLesson(
                lesson_id="padawan_force_pull",
                name="Force Pull",
                description="Retrieve data with the Force",
                rank_required=JediRank.PADAWAN,
                force_power=ForcePower.FORCE_PULL,
                difficulty=2,
                experience_reward=200
            ),
            JediLesson(
                lesson_id="padawan_force_vision",
                name="Force Vision",
                description="Recognize patterns with the Force",
                rank_required=JediRank.PADAWAN,
                force_power=ForcePower.FORCE_VISION,
                difficulty=3,
                experience_reward=250
            ),
            # Knight Lessons
            JediLesson(
                lesson_id="knight_battle_meditation",
                name="Battle Meditation",
                description="Coordinate multiple systems",
                rank_required=JediRank.KNIGHT,
                force_power=ForcePower.BATTLE_MEDITATION,
                difficulty=5,
                experience_reward=500,
                prerequisites=["padawan_telekinesis", "padawan_force_vision"]
            ),
            JediLesson(
                lesson_id="knight_force_heal",
                name="Force Heal",
                description="Repair and heal systems",
                rank_required=JediRank.KNIGHT,
                force_power=ForcePower.FORCE_HEAL,
                difficulty=4,
                experience_reward=400
            ),
            JediLesson(
                lesson_id="knight_force_lightning",
                name="Force Lightning",
                description="Rapid processing and execution",
                rank_required=JediRank.KNIGHT,
                force_power=ForcePower.FORCE_LIGHTNING,
                difficulty=5,
                experience_reward=500
            ),
            # Master Lessons
            JediLesson(
                lesson_id="master_force_ghost",
                name="Force Ghost",
                description="Background processing and persistence",
                rank_required=JediRank.MASTER,
                force_power=ForcePower.FORCE_GHOST,
                difficulty=8,
                experience_reward=1000,
                prerequisites=["knight_battle_meditation", "knight_force_heal"]
            ),
        ]

        for lesson in lessons:
            self.lessons[lesson.lesson_id] = lesson

    def get_available_lessons(self) -> List[JediLesson]:
        """Get available lessons for current rank"""
        available = []

        for lesson in self.lessons.values():
            # Check rank requirement
            rank_values = {
                JediRank.YOUNGLING: 0,
                JediRank.PADAWAN: 1,
                JediRank.KNIGHT: 2,
                JediRank.MASTER: 3,
                JediRank.GRAND_MASTER: 4
            }

            if rank_values[lesson.rank_required] <= rank_values[self.training.rank]:
                # Check prerequisites
                if all(prereq in self.training.completed_trials for prereq in lesson.prerequisites):
                    if not lesson.completed:
                        available.append(lesson)

        return available

    def start_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """Start a Jedi training lesson"""
        if lesson_id not in self.lessons:
            return {"error": "Lesson not found"}

        lesson = self.lessons[lesson_id]

        # Check if available
        available = self.get_available_lessons()
        if lesson not in available:
            return {"error": "Lesson not available"}

        # Add to current lessons
        if lesson_id not in self.training.current_lessons:
            self.training.current_lessons.append(lesson_id)

        self.logger.info(f"📚 Starting lesson: {lesson.name}")
        self.logger.info(f"   {lesson.description}")

        return {
            "lesson_id": lesson_id,
            "name": lesson.name,
            "status": "started"
        }

    def complete_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """Complete a Jedi training lesson"""
        if lesson_id not in self.lessons:
            return {"error": "Lesson not found"}

        lesson = self.lessons[lesson_id]

        # Mark as completed
        lesson.completed = True

        # Update training
        if lesson_id not in self.training.completed_trials:
            self.training.completed_trials.append(lesson_id)

        if lesson_id in self.training.current_lessons:
            self.training.current_lessons.remove(lesson_id)

        # Award experience
        self.training.experience_points += lesson.experience_reward
        self.training.knowledge_points += lesson.knowledge_reward

        # Update force skill
        power_name = lesson.force_power.value
        if power_name not in self.training.force_skills:
            self.training.force_skills[power_name] = ForceSkill(
                power=lesson.force_power,
                level=0,
                experience=0
            )

        skill = self.training.force_skills[power_name]
        skill.experience += lesson.experience_reward
        skill.level = min(100, skill.level + (lesson.experience_reward // 10))
        skill.mastery = skill.level / 100.0
        skill.last_used = datetime.now()

        # Update last training
        self.training.last_training = datetime.now()

        # Save progress
        self._save_training()

        self.logger.info(f"✅ Lesson completed: {lesson.name}")
        self.logger.info(f"   Experience: +{lesson.experience_reward}")
        self.logger.info(f"   {lesson.force_power.value} level: {skill.level}")

        # Check for rank advancement
        advancement = self.check_rank_advancement()

        return {
            "lesson_id": lesson_id,
            "name": lesson.name,
            "status": "completed",
            "experience_gained": lesson.experience_reward,
            "force_skill_level": skill.level,
            "rank_advancement": advancement
        }

    def check_rank_advancement(self) -> Optional[Dict[str, Any]]:
        """Check if can advance rank"""
        if not self.training.can_advance_rank():
            return None

        # Advance rank
        rank_order = [
            JediRank.YOUNGLING,
            JediRank.PADAWAN,
            JediRank.KNIGHT,
            JediRank.MASTER,
            JediRank.GRAND_MASTER
        ]

        current_index = rank_order.index(self.training.rank)
        if current_index < len(rank_order) - 1:
            new_rank = rank_order[current_index + 1]
            old_rank = self.training.rank
            self.training.rank = new_rank

            self._save_training()

            self.logger.info(f"🎉 RANK ADVANCEMENT!")
            self.logger.info(f"   {old_rank.value.upper()} → {new_rank.value.upper()}")

            return {
                "old_rank": old_rank.value,
                "new_rank": new_rank.value,
                "force_level": self.training.get_total_force_level()
            }

        return None

    def use_force_power(self, power: ForcePower) -> Dict[str, Any]:
        """Use a Force power (gain experience)"""
        power_name = power.value

        if power_name not in self.training.force_skills:
            self.training.force_skills[power_name] = ForceSkill(
                power=power,
                level=0,
                experience=0
            )

        skill = self.training.force_skills[power_name]

        # Gain experience
        experience_gain = 10
        skill.experience += experience_gain
        skill.level = min(100, skill.level + 1)
        skill.mastery = skill.level / 100.0
        skill.last_used = datetime.now()

        # Update training
        self.training.experience_points += experience_gain
        self.training.last_training = datetime.now()

        self._save_training()

        return {
            "power": power.value,
            "level": skill.level,
            "mastery": skill.mastery,
            "experience_gained": experience_gain
        }

    def get_training_status(self) -> Dict[str, Any]:
        """Get comprehensive training status"""
        available_lessons = self.get_available_lessons()

        return {
            "timestamp": datetime.now().isoformat(),
            "rank": self.training.rank.value,
            "experience_points": self.training.experience_points,
            "knowledge_points": self.training.knowledge_points,
            "wisdom_points": self.training.wisdom_points,
            "total_force_level": self.training.get_total_force_level(),
            "force_skills": {k: v.to_dict() for k, v in self.training.force_skills.items()},
            "completed_trials": len(self.training.completed_trials),
            "current_lessons": len(self.training.current_lessons),
            "available_lessons": len(available_lessons),
            "can_advance": self.training.can_advance_rank(),
            "master": self.training.master_name,
            "training_days": (datetime.now() - self.training.training_started).days
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Jedi Academy")
    parser.add_argument("--status", action="store_true", help="Show training status")
    parser.add_argument("--lessons", action="store_true", help="List available lessons")
    parser.add_argument("--start", type=str, help="Start a lesson (lesson_id)")
    parser.add_argument("--complete", type=str, help="Complete a lesson (lesson_id)")
    parser.add_argument("--use-force", type=str, help="Use Force power (power_name)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    academy = JARVISJediAcademy()

    if args.status:
        status = academy.get_training_status()

        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n⚔️  JARVIS Jedi Academy - Training Status")
            print("=" * 60)
            print(f"Rank: {status['rank'].upper()}")
            print(f"Experience Points: {status['experience_points']}")
            print(f"Total Force Level: {status['total_force_level']:.1f}/100")
            print(f"Completed Trials: {status['completed_trials']}")
            print(f"Available Lessons: {status['available_lessons']}")
            print(f"Can Advance Rank: {status['can_advance']}")
            if status['master']:
                print(f"Master: {status['master']}")
            print(f"\nForce Skills:")
            for power, skill in status['force_skills'].items():
                print(f"  • {power}: Level {skill['level']} (Mastery: {skill['mastery']*100:.1f}%)")

    elif args.lessons:
        lessons = academy.get_available_lessons()

        if args.json:
            print(json.dumps([l.to_dict() for l in lessons], indent=2))
        else:
            print("\n📚 Available Lessons")
            print("=" * 60)
            for lesson in lessons:
                print(f"\n{lesson.name} ({lesson.lesson_id})")
                print(f"  {lesson.description}")
                print(f"  Difficulty: {lesson.difficulty}/10")
                print(f"  Experience Reward: {lesson.experience_reward}")
                print(f"  Force Power: {lesson.force_power.value}")

    elif args.start:
        result = academy.start_lesson(args.start)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n📚 {result.get('name', 'Lesson')} started!")

    elif args.complete:
        result = academy.complete_lesson(args.complete)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n✅ Lesson completed!")
            print(f"   Experience: +{result.get('experience_gained', 0)}")
            if result.get('rank_advancement'):
                adv = result['rank_advancement']
                print(f"\n🎉 RANK ADVANCEMENT: {adv['old_rank'].upper()} → {adv['new_rank'].upper()}")

    elif args.use_force:
        try:
            power = ForcePower(args.use_force.lower())
            result = academy.use_force_power(power)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n⚡ Used {result['power']}!")
                print(f"   Level: {result['level']}")
                print(f"   Mastery: {result['mastery']*100:.1f}%")
        except ValueError:
            print(f"Unknown Force power: {args.use_force}")

    else:
        parser.print_help()

