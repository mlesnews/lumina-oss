#!/usr/bin/env python3
"""
LUMINA Lesson Generator

Automatically generates lessons for Illumination curricula,
creating age-appropriate, plain-language content.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from lumina_illumination_curriculum_system import (
        LUMINAIlluminationCurriculumSystem,
        AgeGroup,
        Subject,
        Lesson,
        Module
    )
    CURRICULUM_SYSTEM_AVAILABLE = True
except ImportError:
    CURRICULUM_SYSTEM_AVAILABLE = False
    LUMINAIlluminationCurriculumSystem = None

logger = get_logger("LUMINALessonGenerator")


class LUMINALessonGenerator:
    """
    Generates lessons automatically for Illumination curricula

    Creates age-appropriate, plain-language lessons based on
    curriculum requirements and learning objectives.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        if CURRICULUM_SYSTEM_AVAILABLE:
            self.curriculum_system = LUMINAIlluminationCurriculumSystem(project_root)
        else:
            self.curriculum_system = None

        self.lessons_dir = project_root / "data" / "illumination" / "lessons"
        self.lessons_dir.mkdir(parents=True, exist_ok=True)

        # Lesson templates by age group
        self.lesson_templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize lesson templates for each age group"""
        return {
            'children': {
                'language_style': 'simple',
                'sentence_length': 'short',
                'examples': 'concrete',
                'activities': 'hands_on',
                'duration': 30
            },
            'teens': {
                'language_style': 'engaging',
                'sentence_length': 'medium',
                'examples': 'relatable',
                'activities': 'interactive',
                'duration': 45
            },
            'adults': {
                'language_style': 'professional',
                'sentence_length': 'varied',
                'examples': 'practical',
                'activities': 'application',
                'duration': 60
            },
            'seniors': {
                'language_style': 'respectful',
                'sentence_length': 'clear',
                'examples': 'life_experience',
                'activities': 'reflective',
                'duration': 60
            }
        }

    def generate_lesson(self, age_group: AgeGroup, subject: Subject,
                       lesson_title: str, learning_objectives: List[str],
                       topic: str) -> Lesson:
        """
        Generate a lesson automatically

        Args:
            age_group: Target age group
            subject: Subject area
            lesson_title: Title of the lesson
            learning_objectives: List of learning objectives
            topic: Main topic/content area

        Returns:
            Generated Lesson object
        """
        self.logger.info(f"Generating lesson: {lesson_title} for {age_group.value}")

        template = self.lesson_templates.get(age_group.value, self.lesson_templates['adults'])

        # Generate plain language content
        content = self._generate_content(age_group, subject, topic, template)

        # Generate activities
        activities = self._generate_activities(age_group, subject, topic, template)

        # Generate learning objectives
        objectives = self._generate_learning_objectives(age_group, subject, learning_objectives)

        # Create lesson
        lesson_id = f"{age_group.value}_{subject.value}_{lesson_title.lower().replace(' ', '_')}"

        lesson = Lesson(
            lesson_id=lesson_id,
            title=lesson_title,
            description=f"Learn about {topic} - designed for {age_group.value}",
            age_group=age_group,
            subject=subject,
            duration_minutes=template['duration'],
            learning_objectives=objectives,
            content=content,
            activities=activities
        )

        return lesson

    def _generate_content(self, age_group: AgeGroup, subject: Subject,
                         topic: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plain language content for a lesson"""

        # Age-appropriate language patterns
        if age_group == AgeGroup.CHILDREN:
            plain_language = f"Let's learn about {topic}! It's fun and easy. You can do it!"
            explanation = f"{topic} is something you can learn. Everyone can learn it. You can too!"

        elif age_group == AgeGroup.TEENS:
            plain_language = f"Today we're exploring {topic}. This is about finding your own way and expressing yourself."
            explanation = f"{topic} is about discovering what makes you unique. Your perspective matters. Your ideas matter."

        elif age_group == AgeGroup.ADULTS:
            plain_language = f"We'll explore {topic} and how it applies to your work and life. Practical, actionable insights."
            explanation = f"{topic} is a valuable skill that can enhance your professional and personal development."

        else:  # SENIORS
            plain_language = f"Let's explore {topic} together. Your experience and wisdom are valuable. Let's share them."
            explanation = f"{topic} is about preserving and sharing your knowledge. Your stories matter. Your wisdom matters."

        return {
            'plain_language': plain_language,
            'explanation': explanation,
            'examples': self._generate_examples(age_group, subject, topic),
            'key_points': self._generate_key_points(subject, topic)
        }

    def _generate_examples(self, age_group: AgeGroup, subject: Subject, topic: str) -> List[str]:
        """Generate age-appropriate examples"""
        examples = []

        if subject == Subject.STORYTELLING:
            if age_group == AgeGroup.CHILDREN:
                examples = ["Your favorite day", "A funny thing that happened", "A story you make up"]
            elif age_group == AgeGroup.TEENS:
                examples = ["Your personal journey", "A challenge you overcame", "Your dreams and goals"]
            elif age_group == AgeGroup.ADULTS:
                examples = ["Professional success story", "Life lesson learned", "Vision for the future"]
            else:
                examples = ["Life story", "Wisdom to share", "Legacy to preserve"]

        elif subject == Subject.INNOVATION:
            if age_group == AgeGroup.CHILDREN:
                examples = ["New way to play", "Creative solution", "Fun idea"]
            else:
                examples = ["Problem-solving approach", "Creative thinking", "Innovative solution"]

        elif subject == Subject.SELF_EXPRESSION:
            examples = ["Express your thoughts", "Share your feelings", "Show who you are"]

        else:  # DIGITAL_STORYTELLING
            examples = ["Video story", "Blog post", "Social media content", "Digital art"]

        return examples

    def _generate_key_points(self, subject: Subject, topic: str) -> List[str]:
        """Generate key learning points"""
        key_points = [
            f"Understanding {topic}",
            f"Applying {topic} in practice",
            f"Creating with {topic}"
        ]
        return key_points

    def _generate_activities(self, age_group: AgeGroup, subject: Subject,
                           topic: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate age-appropriate activities"""
        activities = []

        activity_type = template.get('activities', 'application')

        if activity_type == 'hands_on':
            activities = [
                {
                    'type': 'create',
                    'description': f"Create something about {topic}",
                    'instructions': f"Use your imagination to create something related to {topic}"
                },
                {
                    'type': 'share',
                    'description': f"Share your {topic} creation",
                    'instructions': f"Show or tell someone about what you created"
                }
            ]
        elif activity_type == 'interactive':
            activities = [
                {
                    'type': 'explore',
                    'description': f"Explore {topic}",
                    'instructions': f"Think about {topic} and how it relates to you"
                },
                {
                    'type': 'create',
                    'description': f"Create your own {topic}",
                    'instructions': f"Make something that represents your unique take on {topic}"
                }
            ]
        elif activity_type == 'application':
            activities = [
                {
                    'type': 'analyze',
                    'description': f"Analyze {topic}",
                    'instructions': f"Think about how {topic} applies to your work or life"
                },
                {
                    'type': 'apply',
                    'description': f"Apply {topic}",
                    'instructions': f"Use {topic} in a practical way"
                }
            ]
        else:  # reflective
            activities = [
                {
                    'type': 'reflect',
                    'description': f"Reflect on {topic}",
                    'instructions': f"Think about your experiences with {topic}"
                },
                {
                    'type': 'share',
                    'description': f"Share your {topic} wisdom",
                    'instructions': f"Share what you've learned about {topic} with others"
                }
            ]

        return activities

    def _generate_learning_objectives(self, age_group: AgeGroup, subject: Subject,
                                     objectives: List[str]) -> List[Dict[str, Any]]:
        """Generate learning objectives"""
        learning_objectives = []

        for i, obj in enumerate(objectives, 1):
            learning_objectives.append({
                'objective_id': f"obj_{i}",
                'title': obj,
                'description': f"Learn to {obj.lower()}",
                'assessment': f"Can demonstrate understanding of {obj}"
            })

        return learning_objectives

    def generate_lessons_for_curriculum(self, age_group: AgeGroup, subject: Subject,
                                       topics: List[str]) -> List[Lesson]:
        """Generate multiple lessons for a curriculum"""
        lessons = []

        for i, topic in enumerate(topics, 1):
            lesson_title = f"{topic.title()} - Part {i}"
            learning_objectives = [
                f"Understand {topic}",
                f"Apply {topic}",
                f"Create with {topic}"
            ]

            lesson = self.generate_lesson(
                age_group=age_group,
                subject=subject,
                lesson_title=lesson_title,
                learning_objectives=learning_objectives,
                topic=topic
            )

            lessons.append(lesson)

        return lessons

    def save_lesson(self, lesson: Lesson):
        """Save a generated lesson"""
        lesson_file = self.lessons_dir / f"{lesson.lesson_id}.json"

        try:
            lesson_dict = {
                'lesson_id': lesson.lesson_id,
                'title': lesson.title,
                'description': lesson.description,
                'age_group': lesson.age_group.value,
                'subject': lesson.subject.value,
                'duration_minutes': lesson.duration_minutes,
                'learning_objectives': lesson.learning_objectives,
                'content': lesson.content,
                'activities': lesson.activities,
                'prerequisites': lesson.prerequisites,
                'created_at': datetime.now().isoformat()
            }

            with open(lesson_file, 'w') as f:
                json.dump(lesson_dict, f, indent=2)

            self.logger.info(f"✅ Saved lesson: {lesson.lesson_id}")

        except Exception as e:
            self.logger.error(f"Failed to save lesson {lesson.lesson_id}: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Lesson Generator")
        parser.add_argument("--generate", action="store_true", help="Generate a lesson")
        parser.add_argument("--age-group", type=str, choices=['children', 'teens', 'adults', 'seniors'],
                           help="Age group")
        parser.add_argument("--subject", type=str, choices=['storytelling', 'innovation', 'self_expression', 'digital_storytelling'],
                           help="Subject")
        parser.add_argument("--topic", type=str, help="Topic for the lesson")
        parser.add_argument("--title", type=str, help="Lesson title")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        generator = LUMINALessonGenerator(project_root)

        if args.generate:
            if not all([args.age_group, args.subject, args.topic]):
                print("❌ Please provide --age-group, --subject, and --topic")
                return

            age_group = AgeGroup(args.age_group)
            subject = Subject(args.subject)

            lesson = generator.generate_lesson(
                age_group=age_group,
                subject=subject,
                lesson_title=args.title or f"Introduction to {args.topic}",
                learning_objectives=[f"Understand {args.topic}", f"Apply {args.topic}"],
                topic=args.topic
            )

            generator.save_lesson(lesson)

            print(f"\n✅ Generated lesson: {lesson.title}")
            print(f"   Age Group: {age_group.value}")
            print(f"   Subject: {subject.value}")
            print(f"   Duration: {lesson.duration_minutes} minutes")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()