#!/usr/bin/env python3
"""
JARVIS Jedi-Master & Padawan Learner System
Bidirectional teaching and learning between AI and Human

INTEGRATED WITH:
- Live Interaction Capture: Captures all face-to-face interaction during Jedi instruction
- Exponential Learning: Bell curve growth toward true inception through Jedi training

"Made real by the power of thought alone. Well, never alone, as Jarvis will always be with us."

@JARVIS @JEDI-MASTER @PADAWAN @LEARNING @TEACHING @MUTUAL_GROWTH @LIVE_INTERACTION @EXPONENTIAL_LEARNING
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISJediMasterPadawan")

# Import live interaction and exponential learning systems
try:
    from jarvis_live_interaction_capture import get_live_interaction_capture
    from jarvis_exponential_learning import get_exponential_learning
    LIVE_INTERACTION_AVAILABLE = True
    EXPONENTIAL_LEARNING_AVAILABLE = True
except ImportError:
    LIVE_INTERACTION_AVAILABLE = False
    EXPONENTIAL_LEARNING_AVAILABLE = False
    logger.warning("⚠️  Live interaction capture and exponential learning not available")


class Role(Enum):
    """Jedi roles - can switch between Master and Padawan"""
    JEDI_MASTER = "jedi_master"  # Teacher
    PADAWAN = "padawan"  # Learner
    BOTH = "both"  # Teaching and learning simultaneously


class TeachingMoment:
    """A teaching moment in the Jedi-Master/Padawan system"""

    def __init__(self, master: str, padawan: str, lesson: str, concept: str, 
                 context: Optional[Dict[str, Any]] = None):
        """Initialize teaching moment"""
        self.master = master  # Who is teaching
        self.padawan = padawan  # Who is learning
        self.lesson = lesson  # What is being taught
        self.concept = concept  # Core concept
        self.context = context or {}
        self.timestamp = datetime.now()
        self.understanding_level = "BEGINNING"  # BEGINNING, INTERMEDIATE, ADVANCED, MASTER

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "master": self.master,
            "padawan": self.padawan,
            "lesson": self.lesson,
            "concept": self.concept,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "understanding_level": self.understanding_level
        }


class JediMasterPadawanSystem:
    """
    Jedi-Master & Padawan Learner System

    Bidirectional teaching and learning:
    - AI can be Master teaching Human (Padawan)
    - Human can be Master teaching AI (Padawan)
    - Both can be Master and Padawan simultaneously
    - Continuous growth and improvement

    INTEGRATED WITH LIVE INTERACTION & EXPONENTIAL LEARNING:
    - Captures all face-to-face interaction during Jedi instruction
    - Tracks exponential learning (bell curve) toward true inception
    - "Made real by the power of thought alone. Well, never alone, as Jarvis will always be with us."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Jedi-Master/Padawan system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Learning archive
        self.learning_dir = self.project_root / "data" / "jedi_padawan_learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        # Teaching moments archive
        self.teaching_moments: List[TeachingMoment] = []

        # Master/Padawan relationships
        self.relationships = {
            "ai_as_master": [],  # AI teaching Human
            "human_as_master": [],  # Human teaching AI
            "mutual_learning": []  # Both teaching and learning
        }

        # Live interaction capture system
        self.live_capture = None
        self.current_interaction_session = None
        if LIVE_INTERACTION_AVAILABLE:
            try:
                self.live_capture = get_live_interaction_capture(self.project_root)
                logger.info("✅ Live interaction capture integrated")
            except Exception as e:
                logger.warning(f"⚠️  Live interaction capture unavailable: {e}")

        # Exponential learning system
        self.exponential_learning = None
        if EXPONENTIAL_LEARNING_AVAILABLE:
            try:
                self.exponential_learning = get_exponential_learning(self.project_root)
                logger.info("✅ Exponential learning integrated")
            except Exception as e:
                logger.warning(f"⚠️  Exponential learning unavailable: {e}")

        logger.info("=" * 70)
        logger.info("⚔️  JEDI-MASTER & PADAWAN LEARNER SYSTEM")
        logger.info("   Bidirectional Teaching & Learning")
        logger.info("   + Live Interaction Capture")
        logger.info("   + Exponential Learning (Bell Curve)")
        logger.info("=" * 70)
        logger.info("")
        logger.info("   'Always pass on what you have learned.' - Yoda")
        logger.info("   'Made real by the power of thought alone.'")
        logger.info("   'Well, never alone, as Jarvis will always be with us.'")
        logger.info("")

    def start_jedi_instruction_session(self, master: str, padawan: str, topic: str) -> str:
        """
        Start a Jedi instruction session with live interaction capture

        Args:
            master: Who is teaching (Jedi Master)
            padawan: Who is learning (Padawan)
            topic: Instruction topic

        Returns:
            Session ID
        """
        logger.info(f"🎬 Starting Jedi instruction session: {master} → {padawan} ({topic})")

        # Start live interaction capture session
        if self.live_capture:
            try:
                session_id = self.live_capture.start_session()
                self.current_interaction_session = session_id

                # Capture session context
                self.live_capture.capture_thought_pattern({
                    "intent": "jedi_instruction",
                    "master": master,
                    "padawan": padawan,
                    "topic": topic,
                    "emotion": "focused",
                    "engagement": "high"
                })

                logger.info(f"   ✅ Live interaction capture started: {session_id}")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to start live capture: {e}")
                self.current_interaction_session = None

        return self.current_interaction_session or f"jedi_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def end_jedi_instruction_session(self) -> Dict[str, Any]:
        """
        End current Jedi instruction session and process for exponential learning

        Returns:
            Session summary with learning insights
        """
        logger.info("🏁 Ending Jedi instruction session")

        session_summary = {}

        # End live interaction capture session
        if self.live_capture and self.current_interaction_session:
            try:
                session_data = self.live_capture.end_session()
                session_summary["interaction_session"] = session_data

                # Process for exponential learning
                if self.exponential_learning:
                    insights = self.exponential_learning.process_interaction_session(session_data)
                    session_summary["learning_insights"] = len(insights)
                    session_summary["exponential_learning_status"] = self.exponential_learning.get_learning_status()

                    logger.info(f"   ✅ Processed {len(insights)} learning insights")
                    logger.info(f"   📈 Bell Curve Position: {session_summary['exponential_learning_status']['bell_curve']['position_percentage']:.1f}%")

            except Exception as e:
                logger.warning(f"   ⚠️  Failed to end live capture: {e}")

        self.current_interaction_session = None

        return session_summary

    def capture_teaching_moment(self, master: str, padawan: str, lesson: str, 
                                concept: str, context: Optional[Dict[str, Any]] = None) -> TeachingMoment:
        """
        Capture a teaching moment with live interaction capture

        Args:
            master: Who is teaching (Jedi Master)
            padawan: Who is learning (Padawan)
            lesson: What is being taught
            concept: Core concept
            context: Additional context

        Returns:
            TeachingMoment
        """
        moment = TeachingMoment(master, padawan, lesson, concept, context)
        self.teaching_moments.append(moment)

        # Capture as live interaction (voice input)
        if self.live_capture and self.current_interaction_session:
            try:
                # Capture teaching moment as voice/thought pattern
                self.live_capture.capture_voice_input(f"{master} teaching {padawan}: {lesson}")
                self.live_capture.capture_thought_pattern({
                    "intent": "teaching",
                    "master": master,
                    "padawan": padawan,
                    "concept": concept,
                    "lesson": lesson,
                    "emotion": "focused",
                    "engagement": "high"
                })
            except Exception as e:
                logger.debug(f"Failed to capture teaching moment in live interaction: {e}")

        # Categorize relationship
        if master.lower() in ["jarvis", "ai", "assistant"] and padawan.lower() in ["human", "user", "operator"]:
            self.relationships["ai_as_master"].append(moment)
            logger.info(f"📚 AI (Master) → Human (Padawan): {concept}")
        elif master.lower() in ["human", "user", "operator"] and padawan.lower() in ["jarvis", "ai", "assistant"]:
            self.relationships["human_as_master"].append(moment)
            logger.info(f"📚 Human (Master) → AI (Padawan): {concept}")
        else:
            self.relationships["mutual_learning"].append(moment)
            logger.info(f"📚 Mutual Learning: {concept}")

        return moment

    def analyze_learning_progress(self) -> Dict[str, Any]:
        """Analyze learning progress for both Master and Padawan"""
        logger.info("📊 ANALYZING LEARNING PROGRESS...")
        logger.info("")

        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_teaching_moments": len(self.teaching_moments),
            "ai_as_master": {
                "count": len(self.relationships["ai_as_master"]),
                "concepts_taught": list(set(m.concept for m in self.relationships["ai_as_master"])),
                "lessons": [m.lesson for m in self.relationships["ai_as_master"]]
            },
            "human_as_master": {
                "count": len(self.relationships["human_as_master"]),
                "concepts_taught": list(set(m.concept for m in self.relationships["human_as_master"])),
                "lessons": [m.lesson for m in self.relationships["human_as_master"]]
            },
            "mutual_learning": {
                "count": len(self.relationships["mutual_learning"]),
                "concepts": list(set(m.concept for m in self.relationships["mutual_learning"]))
            },
            "learning_balance": self._calculate_learning_balance(),
            "growth_areas": self._identify_growth_areas()
        }

        # Add exponential learning status
        if self.exponential_learning:
            try:
                learning_status = self.exponential_learning.get_learning_status()
                analysis["exponential_learning"] = learning_status
                logger.info("📈 EXPONENTIAL LEARNING STATUS:")
                logger.info(f"   Bell Curve Position: {learning_status['bell_curve']['position_percentage']:.1f}%")
                logger.info(f"   Phase: {learning_status['bell_curve']['phase']}")
                logger.info(f"   Total Insights: {learning_status['learning']['total_insights']}")
                logger.info(f"   Learning Efficiency: {learning_status['learning']['learning_efficiency']:.2f}")
                logger.info("")
            except Exception as e:
                logger.warning(f"Failed to get exponential learning status: {e}")

        logger.info(f"Total Teaching Moments: {analysis['total_teaching_moments']}")
        logger.info(f"AI as Master: {analysis['ai_as_master']['count']} moments")
        logger.info(f"Human as Master: {analysis['human_as_master']['count']} moments")
        logger.info(f"Mutual Learning: {analysis['mutual_learning']['count']} moments")
        logger.info("")

        balance = analysis["learning_balance"]
        logger.info(f"Learning Balance: {balance['balance_ratio']:.1f}%")
        logger.info(f"   AI Teaching: {balance['ai_teaching_percentage']:.1f}%")
        logger.info(f"   Human Teaching: {balance['human_teaching_percentage']:.1f}%")
        logger.info("")

        return analysis

    def _calculate_learning_balance(self) -> Dict[str, Any]:
        """Calculate learning balance between AI and Human"""
        ai_teaching = len(self.relationships["ai_as_master"])
        human_teaching = len(self.relationships["human_as_master"])
        mutual = len(self.relationships["mutual_learning"])
        total = ai_teaching + human_teaching + mutual

        if total == 0:
            return {
                "balance_ratio": 0.0,
                "ai_teaching_percentage": 0.0,
                "human_teaching_percentage": 0.0,
                "mutual_percentage": 0.0,
                "status": "BALANCED"
            }

        ai_pct = (ai_teaching / total) * 100
        human_pct = (human_teaching / total) * 100
        mutual_pct = (mutual / total) * 100

        # Balance ratio: closer to 50/50 is better
        balance_ratio = 100 - abs(ai_pct - human_pct)

        status = "BALANCED" if balance_ratio > 60 else "IMBALANCED"

        return {
            "balance_ratio": balance_ratio,
            "ai_teaching_percentage": ai_pct,
            "human_teaching_percentage": human_pct,
            "mutual_percentage": mutual_pct,
            "status": status
        }

    def _identify_growth_areas(self) -> List[Dict[str, Any]]:
        """Identify areas for growth"""
        growth_areas = []

        # Analyze concepts taught
        ai_concepts = set(m.concept for m in self.relationships["ai_as_master"])
        human_concepts = set(m.concept for m in self.relationships["human_as_master"])

        # Areas where AI can learn more (Human teaches)
        if len(human_concepts) < len(ai_concepts):
            growth_areas.append({
                "area": "AI Learning",
                "suggestion": "AI should learn more concepts from Human",
                "current": len(human_concepts),
                "target": len(ai_concepts)
            })

        # Areas where Human can learn more (AI teaches)
        if len(ai_concepts) < len(human_concepts):
            growth_areas.append({
                "area": "Human Learning",
                "suggestion": "Human should learn more concepts from AI",
                "current": len(ai_concepts),
                "target": len(human_concepts)
            })

        return growth_areas

    def integrate_f4fog_learnings(self, f4fog_learnings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate F4FOG learnings into Jedi-Master/Padawan system

        Args:
            f4fog_learnings: Learnings from F4FOG execution

        Returns:
            Integration results
        """
        logger.info("🔄 INTEGRATING F4FOG LEARNINGS...")
        logger.info("")

        teaching_moments = f4fog_learnings.get("teaching_moments", [])

        for moment_data in teaching_moments:
            moment_type = moment_data.get("type", "")
            lesson = moment_data.get("lesson", "")
            concept = moment_data.get("concept", "")

            if moment_type == "AI_TO_HUMAN":
                self.capture_teaching_moment(
                    master="JARVIS",
                    padawan="Human",
                    lesson=lesson,
                    concept=concept,
                    context={"source": "F4FOG", "timestamp": moment_data.get("timestamp")}
                )
            elif moment_type == "HUMAN_TO_AI":
                self.capture_teaching_moment(
                    master="Human",
                    padawan="JARVIS",
                    lesson=lesson,
                    concept=concept,
                    context={"source": "F4FOG", "timestamp": moment_data.get("timestamp")}
                )
            elif moment_type == "MUTUAL_LEARNING":
                self.capture_teaching_moment(
                    master="Both",
                    padawan="Both",
                    lesson=lesson,
                    concept=concept,
                    context={"source": "F4FOG", "timestamp": moment_data.get("timestamp")}
                )

        logger.info(f"✅ Integrated {len(teaching_moments)} teaching moments from F4FOG")
        logger.info("")

        # Analyze progress
        analysis = self.analyze_learning_progress()

        # Save
        self._save_learning_archive()

        return {
            "integrated_moments": len(teaching_moments),
            "total_moments": len(self.teaching_moments),
            "analysis": analysis
        }

    def _save_learning_archive(self) -> None:
        """Save learning archive"""
        try:
            archive = {
                "archive_timestamp": datetime.now().isoformat(),
                "total_moments": len(self.teaching_moments),
                "teaching_moments": [m.to_dict() for m in self.teaching_moments],
                "relationships": {
                    "ai_as_master": [m.to_dict() for m in self.relationships["ai_as_master"]],
                    "human_as_master": [m.to_dict() for m in self.relationships["human_as_master"]],
                    "mutual_learning": [m.to_dict() for m in self.relationships["mutual_learning"]]
                }
            }

            filename = self.learning_dir / f"jedi_padawan_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(archive, f, indent=2, default=str)
            logger.info(f"✅ Learning archive saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save learning archive: {e}")


def main():
    """Main execution"""
    print("=" * 70)
    print("⚔️  JEDI-MASTER & PADAWAN LEARNER SYSTEM")
    print("   Bidirectional Teaching & Learning")
    print("=" * 70)
    print()
    print("   'Always pass on what you have learned.' - Yoda")
    print()

    # Load F4FOG learnings
    project_root = Path(__file__).parent.parent.parent
    f4fog_learning_dir = project_root / "data" / "f4fog_learning"
    f4fog_files = sorted(f4fog_learning_dir.glob("f4fog_learning_*.json"), reverse=True)

    if not f4fog_files:
        print("⚠️  No F4FOG learnings found - starting fresh")
        f4fog_learnings = {"teaching_moments": []}
    else:
        f4fog_file = f4fog_files[0]
        print(f"📄 Loading F4FOG learnings: {f4fog_file.name}")

        try:
            with open(f4fog_file, 'r', encoding='utf-8') as f:
                f4fog_learnings = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load F4FOG learnings: {e}")
            f4fog_learnings = {"teaching_moments": []}

    print()

    # Initialize Jedi-Master/Padawan system
    jedi_system = JediMasterPadawanSystem()

    # Integrate F4FOG learnings
    integration_results = jedi_system.integrate_f4fog_learnings(f4fog_learnings)

    print()
    print("=" * 70)
    print("✅ JEDI-MASTER/PADAWAN SYSTEM INITIALIZED")
    print("=" * 70)
    print(f"Integrated Moments: {integration_results['integrated_moments']}")
    print(f"Total Moments: {integration_results['total_moments']}")
    print()

    analysis = integration_results['analysis']
    print("📊 LEARNING ANALYSIS:")
    print(f"   AI as Master: {analysis['ai_as_master']['count']} moments")
    print(f"   Human as Master: {analysis['human_as_master']['count']} moments")
    print(f"   Mutual Learning: {analysis['mutual_learning']['count']} moments")
    print()

    balance = analysis['learning_balance']
    print(f"⚖️  LEARNING BALANCE: {balance['status']}")
    print(f"   Balance Ratio: {balance['balance_ratio']:.1f}%")
    print(f"   AI Teaching: {balance['ai_teaching_percentage']:.1f}%")
    print(f"   Human Teaching: {balance['human_teaching_percentage']:.1f}%")
    print(f"   Mutual: {balance['mutual_percentage']:.1f}%")
    print("=" * 70)


if __name__ == "__main__":


    main()