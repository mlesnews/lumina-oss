#!/usr/bin/env python3
"""
LUMINA Storytelling Coach

Coaches users in storytelling, helping them discover and express
their unique stories. Every human, any age, is capable of truly
unique and innovative storytelling.
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

logger = get_logger("LUMINAStorytellingCoach")


class LUMINAStorytellingCoach:
    """
    Coaches users in storytelling

    Core Belief: Every human, any age, is capable of truly unique
    and innovative storytelling.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.core_belief = "Every human, any age, is capable of truly unique and innovative storytelling"

        self.coaching_sessions_dir = project_root / "data" / "illumination" / "coaching_sessions"
        self.coaching_sessions_dir.mkdir(parents=True, exist_ok=True)

    def coach_user(self, user_id: str, age: int, story_topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Coach a user in storytelling

        Args:
            user_id: User identifier
            age: User's age
            story_topic: Optional story topic they want to tell

        Returns:
            Coaching session with guidance
        """
        self.logger.info(f"Coaching user {user_id} in storytelling")

        # Determine age group
        if age < 13:
            age_group = "children"
        elif age < 18:
            age_group = "teens"
        elif age < 65:
            age_group = "adults"
        else:
            age_group = "seniors"

        # Generate coaching guidance
        guidance = self._generate_guidance(age_group, story_topic)

        # Create coaching session
        session = {
            'session_id': f"storytelling_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'user_id': user_id,
            'age': age,
            'age_group': age_group,
            'story_topic': story_topic,
            'guidance': guidance,
            'core_belief': self.core_belief,
            'created_at': datetime.now().isoformat()
        }

        # Save session
        self._save_session(session)

        return session

    def _generate_guidance(self, age_group: str, story_topic: Optional[str]) -> Dict[str, Any]:
        """Generate storytelling guidance"""

        if age_group == "children":
            guidance = {
                'message': f"Hi! I'm here to help you tell your story. {self.core_belief}",
                'steps': [
                    "Think about something that happened to you",
                    "What made it special?",
                    "Tell me about it in your own words",
                    "We'll make it into a great story together!"
                ],
                'encouragement': "Your story is special because it's yours! No one else has the same story."
            }

        elif age_group == "teens":
            guidance = {
                'message': f"Let's discover your unique storytelling voice. {self.core_belief}",
                'steps': [
                    "What story do you want to tell?",
                    "What makes it important to you?",
                    "How can you express it in your own way?",
                    "Let's craft it together"
                ],
                'encouragement': "Your perspective is unique. Your voice matters. Your story matters."
            }

        elif age_group == "adults":
            guidance = {
                'message': f"Let's craft your story for maximum impact. {self.core_belief}",
                'steps': [
                    "Identify your core message",
                    "Structure your narrative",
                    "Develop your unique voice",
                    "Refine and polish"
                ],
                'encouragement': "Your experience and insights are valuable. Let's share them effectively."
            }

        else:  # seniors
            guidance = {
                'message': f"Let's preserve and share your wisdom through storytelling. {self.core_belief}",
                'steps': [
                    "Reflect on your life experiences",
                    "Identify stories worth sharing",
                    "Capture your wisdom",
                    "Share with others"
                ],
                'encouragement': "Your stories contain wisdom. Your experiences matter. Let's preserve them."
            }

        if story_topic:
            guidance['story_topic'] = story_topic
            guidance['message'] += f" Let's work on your story about: {story_topic}"

        return guidance

    def provide_feedback(self, session_id: str, story_content: str) -> Dict[str, Any]:
        """Provide feedback on a user's story"""
        feedback = {
            'session_id': session_id,
            'feedback': {
                'strengths': self._identify_strengths(story_content),
                'suggestions': self._generate_suggestions(story_content),
                'encouragement': "Keep going! Your story is developing well."
            },
            'created_at': datetime.now().isoformat()
        }

        return feedback

    def _identify_strengths(self, story_content: str) -> List[str]:
        """Identify strengths in the story"""
        strengths = []

        if len(story_content) > 100:
            strengths.append("Good detail and depth")

        if 'I' in story_content or 'my' in story_content.lower():
            strengths.append("Personal voice and perspective")

        if any(word in story_content.lower() for word in ['because', 'when', 'then']):
            strengths.append("Clear narrative structure")

        return strengths or ["You've started your story - that's the first step!"]

    def _generate_suggestions(self, story_content: str) -> List[str]:
        """Generate suggestions for improvement"""
        suggestions = []

        if len(story_content) < 50:
            suggestions.append("Add more details - what happened? How did you feel?")

        if 'because' not in story_content.lower():
            suggestions.append("Consider explaining why this story matters to you")

        suggestions.append("Keep writing - every story gets better with practice")

        return suggestions

    def _save_session(self, session: Dict[str, Any]):
        """Save a coaching session"""
        session_file = self.coaching_sessions_dir / f"{session['session_id']}.json"

        try:
            with open(session_file, 'w') as f:
                json.dump(session, f, indent=2)
            self.logger.info(f"✅ Saved coaching session: {session['session_id']}")
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Storytelling Coach")
        parser.add_argument("--coach", action="store_true", help="Start coaching session")
        parser.add_argument("--user-id", type=str, help="User ID")
        parser.add_argument("--age", type=int, help="User age")
        parser.add_argument("--topic", type=str, help="Story topic")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        coach = LUMINAStorytellingCoach(project_root)

        if args.coach:
            if not args.user_id or not args.age:
                print("❌ Please provide --user-id and --age")
                return

            session = coach.coach_user(args.user_id, args.age, args.topic)

            print("\n" + "="*80)
            print("STORYTELLING COACHING SESSION")
            print("="*80)
            print(f"\n{session['guidance']['message']}")
            print(f"\nSteps:")
            for i, step in enumerate(session['guidance']['steps'], 1):
                print(f"  {i}. {step}")
            print(f"\n{session['guidance']['encouragement']}")
            print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()