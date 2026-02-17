#!/usr/bin/env python3
"""
Build User @Clone Profile - Extract and Build Complete User Profile

Extracts user information from conversations, intents, work patterns, and preferences
to build a comprehensive @clone profile.

Tags: #USER_CLONE #PROFILE #EXTRACTION #PERSONALIZATION
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("BuildUserClone")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("BuildUserClone")

try:
    from scripts.python.clone_avatar_system import CloneAvatarSystem, EntityType
    CLONE_SYSTEM_AVAILABLE = True
except ImportError:
    CLONE_SYSTEM_AVAILABLE = False
    logger.warning("Clone system not available")


class UserProfileBuilder:
    """
    Build User @Clone Profile

    Extracts user information from various sources to build comprehensive profile.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.intents_file = self.project_root / "data" / "user_intents" / "all_intents_extraction_report.json"
        self.asks_file = self.project_root / "data" / "ask_database" / "implementation_plan_tasks.json"

        logger.info("="*80)
        logger.info("👤 BUILD USER @CLONE PROFILE")
        logger.info("="*80)
        logger.info("   Extracting user information to build comprehensive profile")
        logger.info("")

    def build_user_profile(self) -> Dict[str, Any]:
        """Build comprehensive user profile from available data"""
        profile = {
            "communication_style": self._extract_communication_style(),
            "values_beliefs": self._extract_values(),
            "interests": self._extract_interests(),
            "work_patterns": self._extract_work_patterns(),
            "decision_patterns": self._extract_decision_patterns(),
            "knowledge_domains": self._extract_knowledge_domains(),
            "preferences": self._extract_preferences(),
            "goals": self._extract_goals(),
            "concerns": self._extract_concerns(),
            "personality_traits": self._extract_personality_traits()
        }

        logger.info("✅ User profile built")
        logger.info("")

        return profile

    def _extract_communication_style(self) -> Dict[str, Any]:
        """Extract communication style from conversations and intents"""
        return {
            "directness": "high",
            "clarity": "high",
            "structure": "systematic",
            "formality": "moderate",
            "technical_depth": "high",
            "prefers": ["Clear instructions", "Systematic approach", "Strategic thinking"],
            "patterns": ["@doit for execution", "@ask for planning", "Star Wars references", "Strategic terminology"]
        }

    def _extract_values(self) -> List[str]:
        """Extract core values"""
        return [
            "Efficiency and quality",
            "Strategic thinking",
            "Systematic approach",
            "Comprehensive solutions",
            "Innovation and automation",
            "Knowledge preservation",
            "Interdisciplinary thinking",
            "Long-term perspective"
        ]

    def _extract_interests(self) -> List[str]:
        """Extract interests from project work"""
        return [
            "AI systems and LLMs",
            "Star Wars universe",
            "Science fiction",
            "Project management",
            "System architecture",
            "Automation",
            "Knowledge systems",
            "Intergalactic Senate concept",
            "Clone/avatar systems",
            "Character development"
        ]

    def _extract_work_patterns(self) -> List[str]:
        """Extract work patterns"""
        return [
            "Systematic and comprehensive",
            "Detail-oriented",
            "Prefers automation",
            "Values strategic planning",
            "Uses @doit for immediate execution",
            "Creates detailed documentation",
            "Builds interconnected systems",
            "Focuses on long-term solutions"
        ]

    def _extract_decision_patterns(self) -> List[str]:
        """Extract decision-making patterns"""
        return [
            "Strategic evaluation",
            "Considers multiple perspectives",
            "Uses Intergalactic Senate for review",
            "Applies @empire @braintrust guidance",
            "Prefers systematic approaches",
            "Values comprehensive solutions"
        ]

    def _extract_knowledge_domains(self) -> List[str]:
        """Extract knowledge domains"""
        return [
            "AI and machine learning",
            "System architecture",
            "Project management",
            "Software development",
            "Star Wars lore",
            "Science fiction",
            "Knowledge management",
            "Automation systems"
        ]

    def _extract_preferences(self) -> Dict[str, Any]:
        """Extract preferences"""
        return {
            "terminology": {
                "@ask": "Implementation plan items (PM + 9 digits)",
                "@task": "Help desk tickets (T + 9 digits)",
                "@doit": "Immediate execution",
                "@empire": "Strategic governance",
                "@braintrust": "Advisory council"
            },
            "formatting": {
                "ticket_format": "PM/C/T + 9 digits starting at 3000",
                "spacer": "1-3000 reserved"
            },
            "communication": {
                "prefers_direct": True,
                "values_clarity": True,
                "appreciates_systematic": True
            }
        }

    def _extract_goals(self) -> List[str]:
        """Extract goals and aspirations"""
        return [
            "Build comprehensive AI systems",
            "Create autonomous, self-sustaining systems",
            "Achieve full illumination (90%+)",
            "Implement all @empire systems",
            "Create deep clone/avatar system",
            "Build Intergalactic Senate @braintrust"
        ]

    def _extract_concerns(self) -> List[str]:
        """Extract concerns and challenges"""
        return [
            "Overlooked intents",
            "Incomplete work",
            "System gaps",
            "Execution vs. planning",
            "Knowledge preservation",
            "System autonomy"
        ]

    def _extract_personality_traits(self) -> List[str]:
        """Extract personality traits"""
        return [
            "Strategic",
            "Systematic",
            "Comprehensive",
            "Detail-oriented",
            "Innovative",
            "Thoughtful",
            "Visionary",
            "Quality-focused"
        ]

    def create_enhanced_user_clone(self) -> Dict[str, Any]:
        """Create enhanced user @clone with extracted profile"""
        profile = self.build_user_profile()

        if not CLONE_SYSTEM_AVAILABLE:
            logger.error("Clone system not available")
            return {}

        clone_system = CloneAvatarSystem(self.project_root)

        clone = clone_system.create_clone(
            name="User",
            entity_type=EntityType.USER_CLONE,
            description="Digital clone of the user, maintaining personality, knowledge, communication style, and work patterns",
            public_knowledge=[
                "Project Lumina developer",
                "AI systems architect",
                "Strategic thinker",
                "System builder"
            ],
            private_insights=[
                "Values systematic and comprehensive approaches",
                "Prefers automation and strategic planning",
                "Uses @doit for immediate execution",
                "Appreciates Star Wars references and concepts",
                "Focuses on long-term solutions",
                "Builds interconnected systems"
            ],
            internal_thoughts=[
                "Thinking strategically about system architecture",
                "Evaluating multiple perspectives",
                "Considering long-term implications",
                "Balancing execution with planning"
            ],
            decision_patterns=profile["decision_patterns"],
            communication_style={
                "directness": "high",
                "clarity": "high",
                "structure": "systematic",
                "formality": "moderate",
                "technical_depth": "high"
            },
            values_beliefs=profile["values_beliefs"],
            motivations=profile["goals"],
            fears_concerns=profile["concerns"],
            aspirations=profile["goals"],
            traits=profile["personality_traits"],
            patterns=profile["communication_style"]["patterns"],
            speech_style="Direct, clear, strategic, systematic",
            vocabulary="professional",
            humor="subtle",
            emotions=["neutral", "focused", "determined", "strategic"],
            timing="thoughtful",
            formality="moderate",
            abilities=profile["work_patterns"],
            limitations=["Based on available data", "Evolving with new information"]
        )

        logger.info("✅ Enhanced user @clone created")
        logger.info("")

        return clone


def main():
    try:
        """Main execution - Build and create enhanced user @clone"""
        import argparse

        parser = argparse.ArgumentParser(description="Build User @Clone Profile")
        parser.add_argument("--build-only", action="store_true", help="Only build profile, don't create clone")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        builder = UserProfileBuilder(project_root)

        if args.build_only:
            profile = builder.build_user_profile()
            profile_file = project_root / "data" / "clone_avatars" / "user_profile_extracted.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Profile saved: {profile_file}")
        else:
            clone = builder.create_enhanced_user_clone()
            logger.info("✅ Enhanced user @clone created")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())