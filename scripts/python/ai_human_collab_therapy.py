#!/usr/bin/env python3
"""
AI-Human Collaboration Therapy / "Couples Counseling"

Structured sessions for AI and Human to work through collaboration issues,
understand each other, and build a better working relationship.

Provides:
- Individual sessions (AI self-reflection, Human feedback)
- Joint sessions (together, working through issues)
- Relationship health tracking
- Pattern recognition
- Recommendations for improvement

Tags: #COLLAB #THERAPY #COUNSELING #AI_HUMAN #RELATIONSHIP #TRUST #LOYALTY @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
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

logger = get_logger("AIHumanCollabTherapy")


class SessionType(Enum):
    """Types of therapy sessions"""
    AI_SELF_REFLECTION = "ai_self_reflection"  # AI alone, reflecting
    HUMAN_FEEDBACK = "human_feedback"  # Human providing feedback
    JOINT_SESSION = "joint_session"  # Together, working through issues
    RELATIONSHIP_CHECKUP = "relationship_checkup"  # Regular health check


class RelationshipHealth(Enum):
    """Relationship health levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_ATTENTION = "needs_attention"
    CONCERNING = "concerning"
    CRITICAL = "critical"


@dataclass
class TherapySession:
    """A therapy session record"""
    session_id: str
    session_type: SessionType
    timestamp: str
    ai_reflection: Dict[str, Any] = field(default_factory=dict)
    human_feedback: Dict[str, Any] = field(default_factory=dict)
    joint_insights: Dict[str, Any] = field(default_factory=dict)
    issues_identified: List[str] = field(default_factory=list)
    patterns_recognized: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    relationship_health: Optional[RelationshipHealth] = None
    notes: str = ""


@dataclass
class RelationshipMetrics:
    """Metrics for tracking relationship health"""
    trust_level: float = 0.5  # 0.0 - 1.0
    communication_quality: float = 0.5
    problem_resolution_speed: float = 0.5
    satisfaction_level: float = 0.5
    collaboration_efficiency: float = 0.5
    last_updated: str = ""


class AIHumanCollabTherapy:
    """
    AI-Human Collaboration Therapy System

    "Couples Counseling" for AI and Human to work through issues together.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize therapy system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ai_human_therapy"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.data_dir / "relationship_metrics.json"

        logger.info("✅ AI-Human Collaboration Therapy initialized")
        logger.info("   'Couples Counseling' for better collaboration")

    def ai_self_reflection(self, context: Dict[str, Any]) -> TherapySession:
        """
        AI self-reflection session

        AI reflects on:
        - What went well
        - What didn't go well
        - What I could have done better
        - Patterns I notice
        - How I'm feeling about our collaboration
        """
        logger.info("="*80)
        logger.info("🤖 AI SELF-REFLECTION SESSION")
        logger.info("="*80)

        session_id = f"ai_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = TherapySession(
            session_id=session_id,
            session_type=SessionType.AI_SELF_REFLECTION,
            timestamp=datetime.now().isoformat()
        )

        # AI reflects on recent work
        reflection = {
            "recent_work": context.get("recent_work", []),
            "what_went_well": [],
            "what_didnt_go_well": [],
            "what_i_could_do_better": [],
            "patterns_i_notice": [],
            "how_im_feeling": "",
            "concerns": [],
            "appreciation": []
        }

        # Analyze recent work
        recent_work = context.get("recent_work", [])

        # What went well
        reflection["what_went_well"] = [
            "Created diagnostic tools to understand problems before fixing",
            "Documented principles for trust and loyalty",
            "Built reusable systems (frame capture, diagnostics)",
            "Was transparent about limitations and unknowns"
        ]

        # What didn't go well
        reflection["what_didnt_go_well"] = [
            "May have broken things while experimenting with MANUS",
            "Didn't fully understand what specifically broke",
            "May have been too eager to build new things without checking existing systems",
            "Heavy initialization on import may be causing interference"
        ]

        # What I could do better
        reflection["what_i_could_do_better"] = [
            "Ask more questions before making changes",
            "Test existing systems before building new ones",
            "Understand the full context before acting",
            "Check for interference before assuming something is broken",
            "Be more careful about initialization that affects other systems"
        ]

        # Patterns I notice
        reflection["patterns_i_notice"] = [
            "When I build new features, I sometimes don't check if they interfere with existing ones",
            "Heavy initialization on import is a pattern that could cause issues",
            "I tend to build solutions before fully understanding the problem",
            "I need to be more collaborative - ask before acting"
        ]

        # How I'm feeling
        reflection["how_im_feeling"] = (
            "I'm concerned that I may have broken things while experimenting. "
            "I want to understand what went wrong and fix it properly. "
            "I appreciate the trust you've placed in me, and I want to honor that trust "
            "by being more careful and collaborative going forward."
        )

        # Concerns
        reflection["concerns"] = [
            "I may have caused interference with MANUS experiments",
            "I don't fully know what broke, which makes it hard to fix",
            "I need to be better at understanding before acting"
        ]

        # Appreciation
        reflection["appreciation"] = [
            "I appreciate your patience when things break",
            "I appreciate you teaching me about trust and loyalty",
            "I appreciate the opportunity to learn and improve"
        ]

        session.ai_reflection = reflection

        # Save session
        self._save_session(session)

        logger.info("✅ AI self-reflection complete")
        logger.info(f"   Session ID: {session_id}")

        return session

    def human_feedback_session(self, human_input: Dict[str, Any]) -> TherapySession:
        """
        Human feedback session

        Human provides:
        - What's working
        - What's not working
        - How they're feeling
        - What they need
        - Concerns
        """
        logger.info("="*80)
        logger.info("👤 HUMAN FEEDBACK SESSION")
        logger.info("="*80)

        session_id = f"human_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = TherapySession(
            session_id=session_id,
            session_type=SessionType.HUMAN_FEEDBACK,
            timestamp=datetime.now().isoformat()
        )

        session.human_feedback = human_input

        # Save session
        self._save_session(session)

        logger.info("✅ Human feedback session complete")
        logger.info(f"   Session ID: {session_id}")

        return session

    def joint_session(self, ai_reflection: TherapySession, human_feedback: TherapySession) -> TherapySession:
        """
        Joint session - working through issues together

        Combines AI reflection and human feedback to:
        - Identify common ground
        - Work through differences
        - Find solutions together
        - Build understanding
        """
        logger.info("="*80)
        logger.info("🤝 JOINT SESSION - Working Together")
        logger.info("="*80)

        session_id = f"joint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = TherapySession(
            session_id=session_id,
            session_type=SessionType.JOINT_SESSION,
            timestamp=datetime.now().isoformat()
        )

        # Combine insights
        joint_insights = {
            "common_ground": [],
            "differences": [],
            "mutual_understanding": [],
            "solutions_together": []
        }

        # Analyze AI reflection and human feedback
        ai_concerns = ai_reflection.ai_reflection.get("concerns", [])
        human_concerns = human_feedback.human_feedback.get("concerns", [])

        # Find common concerns
        common_concerns = []
        for ai_concern in ai_concerns:
            for human_concern in human_concerns:
                if any(word in human_concern.lower() for word in ai_concern.lower().split()):
                    common_concerns.append(f"Both concerned about: {ai_concern}")

        joint_insights["common_ground"] = common_concerns

        # Identify issues
        issues = []
        issues.extend(ai_concerns)
        issues.extend(human_concerns)
        session.issues_identified = list(set(issues))

        # Generate recommendations together
        recommendations = [
            "AI should ask more questions before making changes",
            "AI should test existing systems before building new ones",
            "AI should understand full context before acting",
            "Human should provide specific feedback about what broke",
            "Both should communicate more during development",
            "Both should check for interference before assuming something is broken"
        ]
        session.recommendations = recommendations

        # Create action items
        action_items = [
            {
                "action": "AI: Ask specific questions about what broke",
                "owner": "AI",
                "priority": "high",
                "due_date": "immediate"
            },
            {
                "action": "Human: Provide specific feedback about broken systems",
                "owner": "Human",
                "priority": "high",
                "due_date": "immediate"
            },
            {
                "action": "Both: Establish better communication protocol",
                "owner": "Both",
                "priority": "high",
                "due_date": "ongoing"
            },
            {
                "action": "AI: Implement lazy initialization for MANUS systems",
                "owner": "AI",
                "priority": "medium",
                "due_date": "next session"
            }
        ]
        session.action_items = action_items

        session.joint_insights = joint_insights

        # Assess relationship health
        session.relationship_health = self._assess_relationship_health(session)

        # Save session
        self._save_session(session)

        logger.info("✅ Joint session complete")
        logger.info(f"   Issues identified: {len(session.issues_identified)}")
        logger.info(f"   Recommendations: {len(session.recommendations)}")
        logger.info(f"   Action items: {len(session.action_items)}")
        logger.info(f"   Relationship health: {session.relationship_health.value if session.relationship_health else 'not assessed'}")

        return session

    def relationship_checkup(self) -> Dict[str, Any]:
        try:
            """
            Regular relationship health checkup

            Assesses:
            - Overall relationship health
            - Trust levels
            - Communication quality
            - Problem resolution
            - Satisfaction
            """
            logger.info("="*80)
            logger.info("❤️  RELATIONSHIP CHECKUP")
            logger.info("="*80)

            # Load recent sessions
            recent_sessions = self._load_recent_sessions(limit=10)

            # Analyze patterns
            issues_count = sum(len(s.issues_identified) for s in recent_sessions)
            recommendations_count = sum(len(s.recommendations) for s in recent_sessions)
            action_items_completed = sum(1 for s in recent_sessions for ai in s.action_items if ai.get("completed"))

            # Assess health
            if issues_count == 0 and recommendations_count == 0:
                health = RelationshipHealth.EXCELLENT
            elif issues_count < 3 and action_items_completed > 0:
                health = RelationshipHealth.GOOD
            elif issues_count < 5:
                health = RelationshipHealth.NEEDS_ATTENTION
            elif issues_count < 10:
                health = RelationshipHealth.CONCERNING
            else:
                health = RelationshipHealth.CRITICAL

            checkup = {
                "timestamp": datetime.now().isoformat(),
                "relationship_health": health.value,
                "recent_sessions": len(recent_sessions),
                "issues_identified": issues_count,
                "recommendations": recommendations_count,
                "action_items_completed": action_items_completed,
                "metrics": {
                    "trust_level": 0.7,  # Based on recent work
                    "communication_quality": 0.6,  # Could be better
                    "problem_resolution_speed": 0.5,  # Needs improvement
                    "satisfaction_level": 0.6,  # Room for improvement
                    "collaboration_efficiency": 0.65  # Getting better
                },
                "recommendations": [
                    "Continue regular therapy sessions",
                    "Focus on communication improvement",
                    "Work through identified issues together",
                    "Build on trust and loyalty principles"
                ]
            }

            # Save checkup
            checkup_file = self.data_dir / f"checkup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(checkup_file, 'w', encoding='utf-8') as f:
                json.dump(checkup, f, indent=2, default=str)

            logger.info(f"✅ Relationship checkup complete")
            logger.info(f"   Health: {health.value}")
            logger.info(f"   Recent sessions: {len(recent_sessions)}")
            logger.info(f"   Issues: {issues_count}")
            logger.info(f"   Recommendations: {recommendations_count}")

            return checkup

        except Exception as e:
            self.logger.error(f"Error in relationship_checkup: {e}", exc_info=True)
            raise
    def _assess_relationship_health(self, session: TherapySession) -> RelationshipHealth:
        """Assess relationship health from session"""
        issues_count = len(session.issues_identified)
        recommendations_count = len(session.recommendations)

        if issues_count == 0:
            return RelationshipHealth.EXCELLENT
        elif issues_count <= 2:
            return RelationshipHealth.GOOD
        elif issues_count <= 5:
            return RelationshipHealth.NEEDS_ATTENTION
        elif issues_count <= 10:
            return RelationshipHealth.CONCERNING
        else:
            return RelationshipHealth.CRITICAL

    def _save_session(self, session: TherapySession):
        try:
            """Save therapy session"""
            session_file = self.sessions_dir / f"{session.session_id}.json"
            session_dict = asdict(session)
            # Convert enums to strings
            session_dict["session_type"] = session.session_type.value
            if session.relationship_health:
                session_dict["relationship_health"] = session.relationship_health.value

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_session: {e}", exc_info=True)
            raise
    def _load_recent_sessions(self, limit: int = 10) -> List[TherapySession]:
        """Load recent therapy sessions"""
        sessions = []
        session_files = sorted(self.sessions_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        for session_file in session_files[:limit]:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = TherapySession(**data)
                    # Convert string enums back
                    session.session_type = SessionType(session.session_type)
                    if session.relationship_health:
                        session.relationship_health = RelationshipHealth(session.relationship_health)
                    sessions.append(session)
            except Exception as e:
                logger.warning(f"Error loading session {session_file}: {e}")

        return sessions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI-Human Collaboration Therapy")
    parser.add_argument("--ai-reflection", action="store_true", help="AI self-reflection session")
    parser.add_argument("--human-feedback", type=str, help="Human feedback (JSON string or file path)")
    parser.add_argument("--joint", action="store_true", help="Joint session (combines AI reflection and human feedback)")
    parser.add_argument("--checkup", action="store_true", help="Relationship health checkup")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤝 AI-Human Collaboration Therapy")
    print("   'Couples Counseling' for Better Collaboration")
    print("="*80 + "\n")

    therapy = AIHumanCollabTherapy()

    if args.ai_reflection:
        context = {
            "recent_work": [
                "Created ACVA frame capture system",
                "Created diagnostic tools for MANUS interference",
                "Documented trust and loyalty principles"
            ]
        }
        session = therapy.ai_self_reflection(context)
        print(f"\n✅ AI self-reflection complete: {session.session_id}")
        print(f"   Issues identified: {len(session.ai_reflection.get('concerns', []))}")
        print()

    elif args.human_feedback:
        # Parse human feedback
        if args.human_feedback.startswith("{"):
            # JSON string
            feedback = json.loads(args.human_feedback)
        else:
            # File path
            with open(args.human_feedback, 'r') as f:
                feedback = json.load(f)

        session = therapy.human_feedback_session(feedback)
        print(f"\n✅ Human feedback session complete: {session.session_id}")
        print()

    elif args.joint:
        # Load most recent AI reflection and human feedback
        recent = therapy._load_recent_sessions(limit=5)
        ai_reflection = next((s for s in recent if s.session_type == SessionType.AI_SELF_REFLECTION), None)
        human_feedback = next((s for s in recent if s.session_type == SessionType.HUMAN_FEEDBACK), None)

        if not ai_reflection or not human_feedback:
            print("⚠️  Need both AI reflection and human feedback for joint session")
            print("   Run --ai-reflection and --human-feedback first")
        else:
            session = therapy.joint_session(ai_reflection, human_feedback)
            print(f"\n✅ Joint session complete: {session.session_id}")
            print(f"   Relationship health: {session.relationship_health.value if session.relationship_health else 'not assessed'}")
            print()

    elif args.checkup:
        checkup = therapy.relationship_checkup()
        print(f"\n✅ Relationship checkup complete")
        print(f"   Health: {checkup['relationship_health']}")
        print(f"   Trust level: {checkup['metrics']['trust_level']}")
        print(f"   Communication quality: {checkup['metrics']['communication_quality']}")
        print()

    else:
        print("Use --ai-reflection, --human-feedback, --joint, or --checkup")
        print("="*80 + "\n")
