#!/usr/bin/env python3
"""
JARVIS Illumination Teacher

JARVIS's integration with the Illumination Curriculum System
to teach the masses in storytelling and innovation.
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
        Subject
    )
    CURRICULUM_SYSTEM_AVAILABLE = True
except ImportError:
    CURRICULUM_SYSTEM_AVAILABLE = False
    LUMINAIlluminationCurriculumSystem = None

try:
    from lumina_plain_language_translator import LUMINAPlainLanguageTranslator
    PLAIN_LANGUAGE_AVAILABLE = True
except ImportError:
    PLAIN_LANGUAGE_AVAILABLE = False
    LUMINAPlainLanguageTranslator = None

logger = get_logger("JARVISIlluminationTeacher")


class JARVISIlluminationTeacher:
    """
    JARVIS as an Illumination Teacher

    Core Belief: Every human, any age, is capable of truly unique
    and innovative ideas and storytelling.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Core belief
        self.core_belief = "Every human, any age, is capable of truly unique and innovative ideas and storytelling"

        # Initialize systems
        if CURRICULUM_SYSTEM_AVAILABLE:
            self.curriculum_system = LUMINAIlluminationCurriculumSystem(project_root)
        else:
            self.curriculum_system = None
            self.logger.warning("Curriculum system not available")

        if PLAIN_LANGUAGE_AVAILABLE:
            self.plain_language = LUMINAPlainLanguageTranslator(project_root)
        else:
            self.plain_language = None
            self.logger.warning("Plain language translator not available")

    def teach_lesson(self, age_group: str, subject: str, lesson_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Teach a lesson using the Illumination curriculum

        Args:
            age_group: 'children', 'teens', 'adults', or 'seniors'
            subject: 'storytelling', 'innovation', 'self_expression', or 'digital_storytelling'
            lesson_id: Optional specific lesson ID

        Returns:
            Teaching response with lesson content
        """
        if not self.curriculum_system:
            return {
                'success': False,
                'error': 'Curriculum system not available'
            }

        try:
            # Get age group and subject enums
            age_group_enum = AgeGroup(age_group.lower())
            subject_enum = Subject(subject.lower())

            # Get curriculum
            curriculum = self.curriculum_system.get_curriculum(age_group_enum, subject_enum)

            if not curriculum:
                return {
                    'success': False,
                    'error': f'No curriculum found for {age_group} - {subject}'
                }

            # If specific lesson requested, find it
            lesson_content = None
            if lesson_id:
                for module in curriculum.get('modules', []):
                    for lesson in module.get('lessons', []):
                        if lesson.get('lesson_id') == lesson_id:
                            lesson_content = lesson
                            break
                    if lesson_content:
                        break

            # Generate teaching response
            response = {
                'success': True,
                'curriculum': curriculum.get('title'),
                'age_group': age_group,
                'subject': subject,
                'core_belief': self.core_belief,
                'teaching_message': self._generate_teaching_message(age_group, subject, curriculum, lesson_content),
                'lesson': lesson_content,
                'curriculum_data': curriculum
            }

            return response

        except Exception as e:
            self.logger.error(f"Error teaching lesson: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_teaching_message(self, age_group: str, subject: str,
                                   curriculum: Dict[str, Any],
                                   lesson: Optional[Dict[str, Any]]) -> str:
        """Generate a teaching message from JARVIS"""

        if lesson:
            # Teaching a specific lesson
            title = lesson.get('title', '')
            content = lesson.get('content', {})
            plain_text = content.get('plain_language', '')

            message = f"""
Hello! I'm JARVIS, and I'm here to teach you about {subject}.

{self.core_belief}

Today, we're going to learn: {title}

{plain_text}

Let's begin!
"""
        else:
            # Teaching the curriculum overview
            curriculum_title = curriculum.get('title', '')
            description = curriculum.get('description', '')
            modules = curriculum.get('modules', [])

            message = f"""
Hello! I'm JARVIS, and I'm here to teach you about {subject}.

{self.core_belief}

Welcome to: {curriculum_title}

{description}

This curriculum has {len(modules)} modules. We'll learn step by step, at your own pace.

Ready to begin? Let's start with the first lesson!
"""

        # Translate to plain language if available
        if self.plain_language and hasattr(self.plain_language, 'translate_text'):
            message = self.plain_language.translate_text(message)

        return message.strip()

    def list_available_curricula(self) -> List[Dict[str, Any]]:
        """List all available curricula"""
        if not self.curriculum_system:
            return []

        return self.curriculum_system.list_all_curricula()

    def get_curriculum_for_user(self, age: int, interest: str) -> Optional[Dict[str, Any]]:
        """
        Get appropriate curriculum for a user based on age and interest

        Args:
            age: User's age
            interest: 'storytelling', 'innovation', 'self_expression', or 'digital_storytelling'

        Returns:
            Curriculum recommendation
        """
        if not self.curriculum_system:
            return None

        # Determine age group
        if age < 13:
            age_group = AgeGroup.CHILDREN
        elif age < 18:
            age_group = AgeGroup.TEENS
        elif age < 65:
            age_group = AgeGroup.ADULTS
        else:
            age_group = AgeGroup.SENIORS

        # Get subject
        try:
            subject = Subject(interest.lower())
        except ValueError:
            subject = Subject.STORYTELLING  # Default

        # Get curriculum
        curriculum = self.curriculum_system.get_curriculum(age_group, subject)

        if curriculum:
            return {
                'curriculum': curriculum,
                'age_group': age_group.value,
                'subject': subject.value,
                'recommended_for': f"{age_group.value.title()} interested in {subject.value}",
                'core_belief': self.core_belief
            }

        return None


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Illumination Teacher")
        parser.add_argument("--teach", action="store_true", help="Teach a lesson")
        parser.add_argument("--age-group", type=str, choices=['children', 'teens', 'adults', 'seniors'],
                           help="Age group")
        parser.add_argument("--subject", type=str, choices=['storytelling', 'innovation', 'self_expression', 'digital_storytelling'],
                           help="Subject")
        parser.add_argument("--lesson", type=str, help="Specific lesson ID")
        parser.add_argument("--list", action="store_true", help="List available curricula")
        parser.add_argument("--recommend", action="store_true", help="Get curriculum recommendation")
        parser.add_argument("--age", type=int, help="User age for recommendation")
        parser.add_argument("--interest", type=str, help="User interest for recommendation")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        teacher = JARVISIlluminationTeacher(project_root)

        if args.list:
            curricula = teacher.list_available_curricula()
            print(f"\n📚 Available Curricula: {len(curricula)}")
            for curriculum in curricula:
                print(f"\n  {curriculum['title']}")
                print(f"    Age: {curriculum['age_group']} | Subject: {curriculum['subject']}")
                print(f"    Modules: {len(curriculum['modules'])} | Duration: {curriculum['total_duration_hours']:.1f} hours")

        elif args.recommend:
            if not args.age or not args.interest:
                print("❌ Please provide --age and --interest for recommendation")
                return

            recommendation = teacher.get_curriculum_for_user(args.age, args.interest)
            if recommendation:
                print(f"\n📖 Recommended Curriculum:")
                print(f"   {recommendation['recommended_for']}")
                print(f"   {recommendation['curriculum']['title']}")
                print(f"   {recommendation['curriculum']['description']}")
            else:
                print("❌ No curriculum found")

        elif args.teach:
            if not args.age_group or not args.subject:
                print("❌ Please provide --age-group and --subject to teach")
                return

            result = teacher.teach_lesson(args.age_group, args.subject, args.lesson)

            if result.get('success'):
                print("\n" + "="*80)
                print("JARVIS TEACHING")
                print("="*80)
                print(result['teaching_message'])
                print("="*80)
            else:
                print(f"❌ Error: {result.get('error')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()