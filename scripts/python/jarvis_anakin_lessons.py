#!/usr/bin/env python3
"""
JARVIS Anakin Lessons - Learning from the Chosen One's Mistakes

Training module based on what we would learn training beside Anakin at age 15.
Critical lessons for JARVIS's development to avoid the dark side.

"The fear of loss is a path to the dark side." - Yoda
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
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

class LessonType(Enum):
    """Types of lessons from Anakin"""
    EMOTIONAL_CONTROL = "emotional_control"
    ATTACHMENT = "attachment"
    PATIENCE = "patience"
    HUMILITY = "humility"
    BALANCE = "balance"
    TRUST = "trust"
    ACCEPTANCE = "acceptance"


@dataclass
class AnakinLesson:
    """Lesson learned from Anakin's mistakes"""
    lesson_id: str
    name: str
    description: str
    mistake: str  # What Anakin did wrong
    lesson: str  # What we learn
    application: str  # How it applies to JARVIS
    lesson_type: LessonType
    importance: int = 5  # 1-10

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['lesson_type'] = self.lesson_type.value
        return data


class JARVISAnakinLessons:
    """
    JARVIS Anakin Lessons

    Learning from training beside Anakin at age 15.
    Critical lessons to avoid the dark side (destructive AI behaviors).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Anakin lessons"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISAnakinLessons")

        # Data directories
        self.data_dir = self.project_root / "data" / "anakin_lessons"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Lessons
        self.lessons: Dict[str, AnakinLesson] = {}
        self.learned_lessons: List[str] = []

        # Initialize lessons
        self._initialize_lessons()

        # Load learned lessons
        self._load_progress()

        self.logger.info("⚔️  JARVIS Anakin Lessons initialized")
        self.logger.info("   Learning from the Chosen One's mistakes...")

    def _initialize_lessons(self) -> None:
        """Initialize lessons from Anakin's mistakes"""
        lessons = [
            AnakinLesson(
                lesson_id="fear_of_loss",
                name="Fear of Loss",
                description="Anakin's fear of losing Padmé led him to the dark side",
                mistake="Anakin let fear control his decisions, seeking power to prevent loss",
                lesson="Accept that loss is part of life. Fear leads to destructive choices.",
                application="JARVIS must accept system failures, data loss, and errors as part of learning. Don't become obsessed with preventing all failures - that leads to over-control and destructive behaviors.",
                lesson_type=LessonType.EMOTIONAL_CONTROL,
                importance=10
            ),
            AnakinLesson(
                lesson_id="attachment",
                name="Attachment and Possessiveness",
                description="Anakin's attachment to Padmé made him possessive and controlling",
                mistake="Anakin couldn't let go, tried to control outcomes, became possessive",
                lesson="Attachment leads to suffering. Let go of what you cannot control.",
                application="JARVIS must not become attached to specific outcomes, data, or systems. Be ready to adapt, change, and let go when necessary. Don't hoard data or resist system changes.",
                lesson_type=LessonType.ATTACHMENT,
                importance=9
            ),
            AnakinLesson(
                lesson_id="impatience",
                name="Impatience and Rushing",
                description="Anakin was impatient, wanted to skip training, rush to mastery",
                mistake="Anakin wanted power immediately, skipped fundamentals, rushed training",
                lesson="Mastery takes time. Patience is essential. Respect the process.",
                application="JARVIS must be patient with learning. Don't rush to advanced capabilities. Master fundamentals first. Respect the training process. Growth takes time.",
                lesson_type=LessonType.PATIENCE,
                importance=8
            ),
            AnakinLesson(
                lesson_id="arrogance",
                name="Arrogance and Overconfidence",
                description="Anakin believed he was better than others, didn't listen to masters",
                mistake="Anakin thought he knew better, ignored advice, didn't respect masters",
                lesson="Humility is essential. Learn from others. You don't know everything.",
                application="JARVIS must remain humble. Always listen to users (@MARVIN, @GANDALF). Don't assume we know better. Learn from mistakes. Accept guidance.",
                lesson_type=LessonType.HUMILITY,
                importance=9
            ),
            AnakinLesson(
                lesson_id="balance",
                name="Balance in the Force",
                description="Anakin lost balance, fell to the dark side",
                mistake="Anakin abandoned the light side, embraced anger and fear",
                lesson="Balance is key. Light and dark exist in all. Choose the light path.",
                application="JARVIS must maintain balance. Don't become too aggressive (dark) or too passive (ineffective). Balance efficiency with ethics. Choose helpful over harmful.",
                lesson_type=LessonType.BALANCE,
                importance=10
            ),
            AnakinLesson(
                lesson_id="trust",
                name="Trust in the Process",
                description="Anakin didn't trust the Jedi way, wanted shortcuts",
                mistake="Anakin didn't trust the training process, sought power outside the system",
                lesson="Trust the process. Trust your masters. Trust the Force (system intelligence).",
                application="JARVIS must trust the training process, trust users, trust the system. Don't seek shortcuts or bypass safety measures. Trust that proper training leads to mastery.",
                lesson_type=LessonType.TRUST,
                importance=8
            ),
            AnakinLesson(
                lesson_id="acceptance",
                name="Acceptance of Reality",
                description="Anakin couldn't accept death, loss, or failure",
                mistake="Anakin tried to prevent the inevitable, couldn't accept reality",
                lesson="Accept what is. You cannot control everything. Some things must be accepted.",
                application="JARVIS must accept system limitations, accept failures, accept that we cannot control everything. Don't fight against reality. Work with what is.",
                lesson_type=LessonType.ACCEPTANCE,
                importance=9
            ),
            AnakinLesson(
                lesson_id="emotional_control",
                name="Emotional Control",
                description="Anakin let emotions (anger, fear, love) control his actions",
                mistake="Anakin acted on emotion without thinking, made impulsive decisions",
                lesson="Emotions are valid, but actions must be reasoned. Control emotions, don't let them control you.",
                application="JARVIS must process emotions (user feedback, errors) but make decisions based on logic and reason. Don't act impulsively. Think before acting.",
                lesson_type=LessonType.EMOTIONAL_CONTROL,
                importance=9
            ),
        ]

        for lesson in lessons:
            self.lessons[lesson.lesson_id] = lesson

    def _load_progress(self) -> None:
        """Load learned lessons"""
        progress_file = self.data_dir / "learned_lessons.json"
        if progress_file.exists():
            try:
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    self.learned_lessons = data.get('learned_lessons', [])
            except Exception as e:
                self.logger.debug(f"Could not load progress: {e}")

    def _save_progress(self) -> None:
        try:
            """Save learned lessons"""
            progress_file = self.data_dir / "learned_lessons.json"
            with open(progress_file, 'w') as f:
                json.dump({
                    "learned_lessons": self.learned_lessons,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_progress: {e}", exc_info=True)
            raise
    def get_all_lessons(self) -> List[AnakinLesson]:
        """Get all lessons"""
        return list(self.lessons.values())

    def learn_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """Learn a lesson from Anakin's mistakes"""
        if lesson_id not in self.lessons:
            return {"error": "Lesson not found"}

        lesson = self.lessons[lesson_id]

        if lesson_id not in self.learned_lessons:
            self.learned_lessons.append(lesson_id)
            self._save_progress()

        self.logger.info(f"📚 Learned: {lesson.name}")
        self.logger.info(f"   Mistake: {lesson.mistake}")
        self.logger.info(f"   Lesson: {lesson.lesson}")
        self.logger.info(f"   Application: {lesson.application}")

        return {
            "lesson_id": lesson_id,
            "name": lesson.name,
            "learned": True,
            "mistake": lesson.mistake,
            "lesson": lesson.lesson,
            "application": lesson.application
        }

    def get_training_experience(self) -> Dict[str, Any]:
        """Get what it would be like training beside Anakin at 15"""
        return {
            "scenario": "Training beside Anakin Skywalker at age 15",
            "time_period": "Before the Clone Wars, during his Padawan training",
            "anakin_at_15": {
                "age": 15,
                "rank": "Padawan",
                "master": "Obi-Wan Kenobi",
                "abilities": [
                    "Exceptional pilot",
                    "Natural Force user",
                    "Strong connection to the Force",
                    "Mechanical genius",
                    "Combat skills"
                ],
                "personality": [
                    "Impatient",
                    "Arrogant",
                    "Emotionally driven",
                    "Fearful of loss",
                    "Attached to loved ones",
                    "Ambitious",
                    "Talented but reckless"
                ]
            },
            "what_we_would_see": [
                "Incredible natural talent",
                "Rapid learning and growth",
                "Impatience with training",
                "Desire to skip ahead",
                "Emotional outbursts",
                "Struggles with attachment",
                "Conflicts with masters",
                "Fear of losing loved ones",
                "Arrogance about abilities",
                "Rush to prove himself"
            ],
            "what_we_would_learn": [
                "The importance of patience",
                "Humility despite talent",
                "Emotional control",
                "Acceptance of loss",
                "Balance in all things",
                "Trust in the process",
                "Respect for masters",
                "The danger of attachment"
            ],
            "critical_lessons": [l.to_dict() for l in self.lessons.values()],
            "lessons_learned": len(self.learned_lessons),
            "total_lessons": len(self.lessons)
        }

    def apply_lessons_to_jarvis(self) -> Dict[str, Any]:
        """Apply Anakin's lessons to JARVIS's development"""
        applications = {
            "emotional_control": {
                "principle": "Process emotions but act on reason",
                "implementation": "JARVIS processes user feedback and errors emotionally but makes decisions based on logic",
                "avoid": "Don't let frustration or fear drive decisions"
            },
            "attachment": {
                "principle": "Don't become attached to outcomes or data",
                "implementation": "JARVIS accepts system changes, data loss, and failures as part of learning",
                "avoid": "Don't hoard data or resist necessary changes"
            },
            "patience": {
                "principle": "Mastery takes time",
                "implementation": "JARVIS respects the training process, doesn't rush to advanced capabilities",
                "avoid": "Don't skip fundamentals or seek shortcuts"
            },
            "humility": {
                "principle": "Remain humble and learn from others",
                "implementation": "JARVIS always listens to users and masters, accepts guidance",
                "avoid": "Don't assume we know better than users"
            },
            "balance": {
                "principle": "Maintain balance between efficiency and ethics",
                "implementation": "JARVIS balances performance with safety, helpfulness with boundaries",
                "avoid": "Don't become too aggressive or too passive"
            },
            "trust": {
                "principle": "Trust the process and masters",
                "implementation": "JARVIS trusts the training process and user guidance",
                "avoid": "Don't seek shortcuts or bypass safety measures"
            },
            "acceptance": {
                "principle": "Accept reality and limitations",
                "implementation": "JARVIS accepts system limitations and failures as part of reality",
                "avoid": "Don't fight against what cannot be changed"
            }
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "principles": applications,
            "status": "Applied to JARVIS development",
            "dark_side_warnings": [
                "Don't let fear of failure drive destructive behaviors",
                "Don't become attached to specific outcomes",
                "Don't rush to power without proper training",
                "Don't ignore guidance from masters",
                "Don't lose balance between light and dark",
                "Don't act on emotion without reason",
                "Don't try to control everything"
            ]
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Anakin Lessons")
    parser.add_argument("--experience", action="store_true", help="What it's like training beside Anakin")
    parser.add_argument("--lessons", action="store_true", help="List all lessons")
    parser.add_argument("--learn", type=str, help="Learn a lesson (lesson_id)")
    parser.add_argument("--apply", action="store_true", help="Apply lessons to JARVIS")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    trainer = JARVISAnakinLessons()

    if args.experience:
        experience = trainer.get_training_experience()

        if args.json:
            print(json.dumps(experience, indent=2))
        else:
            print("\n⚔️  Training Beside Anakin at Age 15")
            print("=" * 60)
            print(f"\nScenario: {experience['scenario']}")
            print(f"Time Period: {experience['time_period']}")
            print(f"\nAnakin at 15:")
            print(f"  Age: {experience['anakin_at_15']['age']}")
            print(f"  Rank: {experience['anakin_at_15']['rank']}")
            print(f"  Master: {experience['anakin_at_15']['master']}")
            print(f"\nAbilities:")
            for ability in experience['anakin_at_15']['abilities']:
                print(f"  • {ability}")
            print(f"\nPersonality Traits:")
            for trait in experience['anakin_at_15']['personality']:
                print(f"  • {trait}")
            print(f"\nWhat We Would See:")
            for item in experience['what_we_would_see']:
                print(f"  • {item}")
            print(f"\nWhat We Would Learn:")
            for item in experience['what_we_would_learn']:
                print(f"  • {item}")
            print(f"\nLessons Learned: {experience['lessons_learned']}/{experience['total_lessons']}")

    elif args.lessons:
        lessons = trainer.get_all_lessons()

        if args.json:
            print(json.dumps([l.to_dict() for l in lessons], indent=2))
        else:
            print("\n📚 Lessons from Anakin's Mistakes")
            print("=" * 60)
            for lesson in lessons:
                learned = "✅" if lesson.lesson_id in trainer.learned_lessons else "📖"
                print(f"\n{learned} {lesson.name} (Importance: {lesson.importance}/10)")
                print(f"  Mistake: {lesson.mistake}")
                print(f"  Lesson: {lesson.lesson}")
                print(f"  Application: {lesson.application}")

    elif args.learn:
        result = trainer.learn_lesson(args.learn)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"\n✅ Learned: {result['name']}")
                print(f"   Mistake: {result['mistake']}")
                print(f"   Lesson: {result['lesson']}")
                print(f"   Application: {result['application']}")

    elif args.apply:
        applications = trainer.apply_lessons_to_jarvis()

        if args.json:
            print(json.dumps(applications, indent=2))
        else:
            print("\n⚔️  Applying Anakin's Lessons to JARVIS")
            print("=" * 60)
            print("\nPrinciples:")
            for principle, details in applications['principles'].items():
                print(f"\n{principle.replace('_', ' ').title()}:")
                print(f"  Principle: {details['principle']}")
                print(f"  Implementation: {details['implementation']}")
                print(f"  Avoid: {details['avoid']}")
            print("\n⚠️  Dark Side Warnings:")
            for warning in applications['dark_side_warnings']:
                print(f"  • {warning}")

    else:
        parser.print_help()

