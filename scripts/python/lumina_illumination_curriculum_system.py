#!/usr/bin/env python3
"""
LUMINA Illumination Curriculum System

Creates teaching curricula for Illumination - teaching the masses
in storytelling and innovation, recognizing that every human,
any age, is capable of truly unique and innovative ideas.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
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

logger = get_logger("IlluminationCurriculum")


class AgeGroup(Enum):
    """Age groups for adaptive teaching"""
    CHILDREN = "children"  # 5-12
    TEENS = "teens"  # 13-17
    ADULTS = "adults"  # 18-64
    SENIORS = "seniors"  # 65+


class Subject(Enum):
    """Core subjects in Illumination"""
    STORYTELLING = "storytelling"
    INNOVATION = "innovation"
    SELF_EXPRESSION = "self_expression"
    DIGITAL_STORYTELLING = "digital_storytelling"


@dataclass
class LearningObjective:
    """A learning objective for a lesson"""
    objective_id: str
    title: str
    description: str
    age_groups: List[AgeGroup]
    subject: Subject
    skills: List[str] = field(default_factory=list)
    assessment_criteria: List[str] = field(default_factory=list)


@dataclass
class Lesson:
    """A single lesson in the curriculum"""
    lesson_id: str
    title: str
    description: str
    age_group: AgeGroup
    subject: Subject
    duration_minutes: int
    learning_objectives: List[LearningObjective]
    content: Dict[str, Any]  # Plain language content
    activities: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    assessment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Module:
    """A module containing multiple lessons"""
    module_id: str
    title: str
    description: str
    age_group: AgeGroup
    subject: Subject
    lessons: List[Lesson]
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration_hours: float = 0.0


@dataclass
class Curriculum:
    """A complete curriculum for Illumination"""
    curriculum_id: str
    title: str
    description: str
    age_group: AgeGroup
    subject: Subject
    modules: List[Module]
    total_duration_hours: float = 0.0
    learning_path: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class LUMINAIlluminationCurriculumSystem:
    """
    System for creating and managing Illumination curricula

    Core Belief: Every human, any age, is capable of truly unique
    and innovative ideas and storytelling.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Directories
        self.curriculum_dir = project_root / "data" / "illumination" / "curricula"
        self.lessons_dir = project_root / "data" / "illumination" / "lessons"
        self.curriculum_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_dir.mkdir(parents=True, exist_ok=True)

        # Core belief
        self.core_belief = "Every human, any age, is capable of truly unique and innovative ideas and storytelling"

        # Initialize default curricula
        self._initialize_default_curricula()

    def _initialize_default_curricula(self):
        """Initialize default curricula for all age groups and subjects"""
        self.logger.info("Initializing default Illumination curricula...")

        # Create curricula for each age group and subject combination
        for age_group in AgeGroup:
            for subject in Subject:
                curriculum = self._create_default_curriculum(age_group, subject)
                if curriculum:
                    self._save_curriculum(curriculum)

    def _create_default_curriculum(self, age_group: AgeGroup, subject: Subject) -> Optional[Curriculum]:
        """Create a default curriculum for an age group and subject"""
        curriculum_id = f"{age_group.value}_{subject.value}_curriculum"

        # Generate curriculum based on age and subject
        if subject == Subject.STORYTELLING:
            return self._create_storytelling_curriculum(age_group, curriculum_id)
        elif subject == Subject.INNOVATION:
            return self._create_innovation_curriculum(age_group, curriculum_id)
        elif subject == Subject.SELF_EXPRESSION:
            return self._create_self_expression_curriculum(age_group, curriculum_id)
        elif subject == Subject.DIGITAL_STORYTELLING:
            return self._create_digital_storytelling_curriculum(age_group, curriculum_id)

        return None

    def _create_storytelling_curriculum(self, age_group: AgeGroup, curriculum_id: str) -> Curriculum:
        """Create storytelling curriculum"""
        modules = []

        if age_group == AgeGroup.CHILDREN:
            modules = [
                self._create_module(
                    module_id="storytelling_basics_kids",
                    title="Telling Your Story",
                    description="Learn how to tell your own unique story",
                    age_group=age_group,
                    subject=Subject.STORYTELLING,
                    lessons=[
                        self._create_lesson(
                            lesson_id="what_is_a_story",
                            title="What is a Story?",
                            description="Learn what makes a story special",
                            age_group=age_group,
                            subject=Subject.STORYTELLING,
                            duration_minutes=30,
                            content={
                                "plain_language": "A story is when you share something that happened to you or something you imagine. Every story is special because it's yours!",
                                "examples": ["Your favorite day", "A funny thing that happened", "A story you make up"]
                            }
                        ),
                        self._create_lesson(
                            lesson_id="your_unique_story",
                            title="Your Unique Story",
                            description="Discover what makes your story special",
                            age_group=age_group,
                            subject=Subject.STORYTELLING,
                            duration_minutes=30,
                            content={
                                "plain_language": "Your story is special because it's yours! No one else has the same story. What makes you special? What makes your story unique?",
                                "activities": ["Draw your story", "Tell your story to a friend", "Write or record your story"]
                            }
                        )
                    ]
                )
            ]
        elif age_group == AgeGroup.TEENS:
            modules = [
                self._create_module(
                    module_id="finding_your_voice",
                    title="Finding Your Voice",
                    description="Discover and express your unique storytelling voice",
                    age_group=age_group,
                    subject=Subject.STORYTELLING,
                    lessons=[
                        self._create_lesson(
                            lesson_id="what_is_your_voice",
                            title="What is Your Voice?",
                            description="Understand what makes your storytelling style unique",
                            age_group=age_group,
                            subject=Subject.STORYTELLING,
                            duration_minutes=45,
                            content={
                                "plain_language": "Your voice is how you tell stories. It's your style, your way of seeing things, your unique perspective. Everyone has a different voice!",
                                "activities": ["Write about something you care about", "Compare your writing style to others", "Experiment with different storytelling styles"]
                            }
                        )
                    ]
                )
            ]
        elif age_group == AgeGroup.ADULTS:
            modules = [
                self._create_module(
                    module_id="professional_storytelling",
                    title="Professional Storytelling",
                    description="Learn to tell compelling stories for work and life",
                    age_group=age_group,
                    subject=Subject.STORYTELLING,
                    lessons=[
                        self._create_lesson(
                            lesson_id="story_structure",
                            title="Story Structure",
                            description="Learn the building blocks of great stories",
                            age_group=age_group,
                            subject=Subject.STORYTELLING,
                            duration_minutes=60,
                            content={
                                "plain_language": "Great stories have a beginning, middle, and end. They have characters, a setting, and something that happens. But most importantly, they have meaning - why does this story matter?",
                                "activities": ["Analyze a story you love", "Write a story with clear structure", "Share your story and get feedback"]
                            }
                        )
                    ]
                )
            ]
        else:  # SENIORS
            modules = [
                self._create_module(
                    module_id="preserving_wisdom",
                    title="Preserving Your Wisdom",
                    description="Share your life stories and wisdom",
                    age_group=age_group,
                    subject=Subject.STORYTELLING,
                    lessons=[
                        self._create_lesson(
                            lesson_id="life_stories",
                            title="Your Life Stories",
                            description="Capture and share the stories of your life",
                            age_group=age_group,
                            subject=Subject.STORYTELLING,
                            duration_minutes=60,
                            content={
                                "plain_language": "You have lived a full life with many stories. These stories are valuable. They contain wisdom, lessons, and experiences that others can learn from. Let's help you share them.",
                                "activities": ["Write about a memorable moment", "Record your story", "Share with family or community"]
                            }
                        )
                    ]
                )
            ]

        return Curriculum(
            curriculum_id=curriculum_id,
            title=f"Storytelling for {age_group.value.title()}",
            description=f"Learn to tell your unique story - designed for {age_group.value}",
            age_group=age_group,
            subject=Subject.STORYTELLING,
            modules=modules,
            total_duration_hours=sum(m.estimated_duration_hours for m in modules)
        )

    def _create_innovation_curriculum(self, age_group: AgeGroup, curriculum_id: str) -> Curriculum:
        """Create innovation curriculum"""
        modules = []

        if age_group == AgeGroup.CHILDREN:
            modules = [
                self._create_module(
                    module_id="creative_thinking_kids",
                    title="Creative Thinking",
                    description="Learn to think in new and creative ways",
                    age_group=age_group,
                    subject=Subject.INNOVATION,
                    lessons=[
                        self._create_lesson(
                            lesson_id="what_is_innovation",
                            title="What is Innovation?",
                            description="Learn what it means to create something new",
                            age_group=age_group,
                            subject=Subject.INNOVATION,
                            duration_minutes=30,
                            content={
                                "plain_language": "Innovation means thinking of new ideas or doing things in a new way. You can innovate! Everyone can have new ideas.",
                                "activities": ["Think of a new way to do something", "Draw your idea", "Share your innovation"]
                            }
                        )
                    ]
                )
            ]
        else:
            # Similar structure for other age groups
            modules = [
                self._create_module(
                    module_id=f"innovation_{age_group.value}",
                    title=f"Innovation for {age_group.value.title()}",
                    description=f"Learn innovation techniques for {age_group.value}",
                    age_group=age_group,
                    subject=Subject.INNOVATION,
                    lessons=[
                        self._create_lesson(
                            lesson_id="innovation_basics",
                            title="Innovation Basics",
                            description="Learn the fundamentals of innovation",
                            age_group=age_group,
                            subject=Subject.INNOVATION,
                            duration_minutes=60,
                            content={
                                "plain_language": "Innovation is about solving problems in new ways, creating new solutions, and thinking creatively. Everyone can innovate - you just need the right tools and mindset.",
                                "activities": ["Identify a problem to solve", "Brainstorm solutions", "Prototype your idea"]
                            }
                        )
                    ]
                )
            ]

        return Curriculum(
            curriculum_id=curriculum_id,
            title=f"Innovation for {age_group.value.title()}",
            description=f"Learn innovation and creative thinking - designed for {age_group.value}",
            age_group=age_group,
            subject=Subject.INNOVATION,
            modules=modules,
            total_duration_hours=sum(m.estimated_duration_hours for m in modules)
        )

    def _create_self_expression_curriculum(self, age_group: AgeGroup, curriculum_id: str) -> Curriculum:
        """Create self-expression curriculum"""
        modules = [
            self._create_module(
                module_id=f"self_expression_{age_group.value}",
                title=f"Self-Expression for {age_group.value.title()}",
                description=f"Learn to express yourself authentically",
                age_group=age_group,
                subject=Subject.SELF_EXPRESSION,
                lessons=[
                    self._create_lesson(
                        lesson_id="finding_your_voice_expression",
                        title="Finding Your Voice",
                        description="Discover how to express your unique self",
                        age_group=age_group,
                        subject=Subject.SELF_EXPRESSION,
                        duration_minutes=45,
                        content={
                            "plain_language": "Self-expression is about sharing who you are, what you think, and what you feel. Your voice matters. Your perspective is unique. Let's help you express it.",
                            "activities": ["Write about yourself", "Create something that represents you", "Share your creation"]
                        }
                    )
                ]
            )
        ]

        return Curriculum(
            curriculum_id=curriculum_id,
            title=f"Self-Expression for {age_group.value.title()}",
            description=f"Learn to express yourself authentically - designed for {age_group.value}",
            age_group=age_group,
            subject=Subject.SELF_EXPRESSION,
            modules=modules,
            total_duration_hours=sum(m.estimated_duration_hours for m in modules)
        )

    def _create_digital_storytelling_curriculum(self, age_group: AgeGroup, curriculum_id: str) -> Curriculum:
        """Create digital storytelling curriculum"""
        modules = [
            self._create_module(
                module_id=f"digital_storytelling_{age_group.value}",
                title=f"Digital Storytelling for {age_group.value.title()}",
                description=f"Learn to tell stories using technology",
                age_group=age_group,
                subject=Subject.DIGITAL_STORYTELLING,
                lessons=[
                    self._create_lesson(
                        lesson_id="digital_tools",
                        title="Digital Storytelling Tools",
                        description="Learn to use technology to tell your story",
                        age_group=age_group,
                        subject=Subject.DIGITAL_STORYTELLING,
                        duration_minutes=60,
                        content={
                            "plain_language": "Digital storytelling means using computers, phones, or other technology to tell your story. You can make videos, write blogs, create art, or use any tool that helps you share your story.",
                            "activities": ["Choose a digital tool", "Create your first digital story", "Share it online"]
                        }
                    )
                ]
            )
        ]

        return Curriculum(
            curriculum_id=curriculum_id,
            title=f"Digital Storytelling for {age_group.value.title()}",
            description=f"Learn to tell stories using technology - designed for {age_group.value}",
            age_group=age_group,
            subject=Subject.DIGITAL_STORYTELLING,
            modules=modules,
            total_duration_hours=sum(m.estimated_duration_hours for m in modules)
        )

    def _create_module(self, module_id: str, title: str, description: str,
                      age_group: AgeGroup, subject: Subject,
                      lessons: List[Lesson]) -> Module:
        """Create a module"""
        total_hours = sum(l.duration_minutes for l in lessons) / 60.0

        return Module(
            module_id=module_id,
            title=title,
            description=description,
            age_group=age_group,
            subject=subject,
            lessons=lessons,
            estimated_duration_hours=total_hours
        )

    def _create_lesson(self, lesson_id: str, title: str, description: str,
                      age_group: AgeGroup, subject: Subject,
                      duration_minutes: int, content: Dict[str, Any],
                      activities: Optional[List[Dict[str, Any]]] = None,
                      prerequisites: Optional[List[str]] = None) -> Lesson:
        """Create a lesson"""
        learning_objectives = [
            LearningObjective(
                objective_id=f"{lesson_id}_obj1",
                title=f"Understand {title}",
                description=f"Learn the fundamentals of {title}",
                age_groups=[age_group],
                subject=subject,
                skills=[f"{subject.value}_basics"],
                assessment_criteria=["Can explain the concept", "Can apply the concept"]
            )
        ]

        return Lesson(
            lesson_id=lesson_id,
            title=title,
            description=description,
            age_group=age_group,
            subject=subject,
            duration_minutes=duration_minutes,
            learning_objectives=learning_objectives,
            content=content,
            activities=activities or [],
            prerequisites=prerequisites or []
        )

    def _save_curriculum(self, curriculum: Curriculum):
        """Save a curriculum to disk"""
        curriculum_file = self.curriculum_dir / f"{curriculum.curriculum_id}.json"

        try:
            # Convert to dict
            curriculum_dict = {
                'curriculum_id': curriculum.curriculum_id,
                'title': curriculum.title,
                'description': curriculum.description,
                'age_group': curriculum.age_group.value,
                'subject': curriculum.subject.value,
                'modules': [
                    {
                        'module_id': m.module_id,
                        'title': m.title,
                        'description': m.description,
                        'age_group': m.age_group.value,
                        'subject': m.subject.value,
                        'lessons': [
                            {
                                'lesson_id': l.lesson_id,
                                'title': l.title,
                                'description': l.description,
                                'age_group': l.age_group.value,
                                'subject': l.subject.value,
                                'duration_minutes': l.duration_minutes,
                                'content': l.content,
                                'activities': l.activities,
                                'prerequisites': l.prerequisites
                            }
                            for l in m.lessons
                        ],
                        'estimated_duration_hours': m.estimated_duration_hours
                    }
                    for m in curriculum.modules
                ],
                'total_duration_hours': curriculum.total_duration_hours,
                'created_at': curriculum.created_at
            }

            with open(curriculum_file, 'w') as f:
                json.dump(curriculum_dict, f, indent=2)

            self.logger.info(f"✅ Saved curriculum: {curriculum.curriculum_id}")

        except Exception as e:
            self.logger.error(f"Failed to save curriculum {curriculum.curriculum_id}: {e}")

    def get_curriculum(self, age_group: AgeGroup, subject: Subject) -> Optional[Dict[str, Any]]:
        """Get a curriculum for an age group and subject"""
        curriculum_id = f"{age_group.value}_{subject.value}_curriculum"
        curriculum_file = self.curriculum_dir / f"{curriculum_id}.json"

        if curriculum_file.exists():
            try:
                with open(curriculum_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load curriculum: {e}")

        return None

    def list_all_curricula(self) -> List[Dict[str, Any]]:
        """List all available curricula"""
        curricula = []

        for curriculum_file in self.curriculum_dir.glob("*.json"):
            try:
                with open(curriculum_file, 'r') as f:
                    curricula.append(json.load(f))
            except Exception as e:
                self.logger.error(f"Failed to load {curriculum_file}: {e}")

        return curricula


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Illumination Curriculum System")
        parser.add_argument("--init", action="store_true", help="Initialize default curricula")
        parser.add_argument("--list", action="store_true", help="List all curricula")
        parser.add_argument("--age-group", type=str, choices=['children', 'teens', 'adults', 'seniors'],
                           help="Filter by age group")
        parser.add_argument("--subject", type=str, choices=['storytelling', 'innovation', 'self_expression', 'digital_storytelling'],
                           help="Filter by subject")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = LUMINAIlluminationCurriculumSystem(project_root)

        if args.init:
            print("✅ Initialized default curricula")

        if args.list:
            curricula = system.list_all_curricula()

            if args.age_group:
                age_group_enum = AgeGroup(args.age_group)
                curricula = [c for c in curricula if c['age_group'] == age_group_enum.value]

            if args.subject:
                subject_enum = Subject(args.subject)
                curricula = [c for c in curricula if c['subject'] == subject_enum.value]

            print(f"\n📚 Available Curricula: {len(curricula)}")
            for curriculum in curricula:
                print(f"\n  {curriculum['title']}")
                print(f"    Age Group: {curriculum['age_group']}")
                print(f"    Subject: {curriculum['subject']}")
                print(f"    Modules: {len(curriculum['modules'])}")
                print(f"    Duration: {curriculum['total_duration_hours']:.1f} hours")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()