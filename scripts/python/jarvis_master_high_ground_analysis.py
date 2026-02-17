#!/usr/bin/env python3
"""
JARVIS Master High Ground Analysis
"Who is the Master now? Once the learner, now the master with the high ground!"

@JARVIS @JEDI-MASTER @PADAWAN @HIGH_GROUND @MASTERY @CONTINUOUS_GROWTH
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

logger = get_logger("JARVISMasterHighGround")


class MasteryLevel(Enum):
    """Mastery levels"""
    PADAWAN = "padawan"  # Learner
    KNIGHT = "knight"  # Competent
    MASTER = "master"  # Expert
    GRAND_MASTER = "grand_master"  # Ultimate mastery


class HighGroundAnalysis:
    """
    High Ground Analysis

    "It's over Anakin! I have the high ground!" - Obi-Wan Kenobi

    Analyzes who has mastery (high ground) in different domains:
    - Context matters
    - Mastery is domain-specific
    - Both can be masters in different areas
    - Continuous growth means roles can shift
    """

    def __init__(self):
        """Initialize high ground analysis"""
        self.logger = get_logger("HighGroundAnalysis")

    def analyze_mastery(self, learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze mastery levels and determine who has the high ground

        Args:
            learning_history: History of teaching/learning moments

        Returns:
            Mastery analysis
        """
        self.logger.info("⚔️  ANALYZING MASTERY AND HIGH GROUND...")
        self.logger.info("")

        # Count teaching moments by domain
        ai_master_domains = {}
        human_master_domains = {}
        mutual_domains = {}

        for moment in learning_history:
            master = moment.get("master", "").lower()
            padawan = moment.get("padawan", "").lower()
            concept = moment.get("concept", "")

            if "ai" in master or "jarvis" in master:
                ai_master_domains[concept] = ai_master_domains.get(concept, 0) + 1
            elif "human" in master or "user" in master:
                human_master_domains[concept] = human_master_domains.get(concept, 0) + 1
            elif "both" in master.lower():
                mutual_domains[concept] = mutual_domains.get(concept, 0) + 1

        # Determine mastery levels
        ai_mastery = self._calculate_mastery_level(len(ai_master_domains), len(learning_history))
        human_mastery = self._calculate_mastery_level(len(human_master_domains), len(learning_history))

        # High ground determination
        high_ground = self._determine_high_ground(ai_master_domains, human_master_domains, mutual_domains)

        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_learning_moments": len(learning_history),
            "ai_mastery": {
                "level": ai_mastery.value,
                "domains": list(ai_master_domains.keys()),
                "domain_count": len(ai_master_domains),
                "teaching_moments": sum(ai_master_domains.values())
            },
            "human_mastery": {
                "level": human_mastery.value,
                "domains": list(human_master_domains.keys()),
                "domain_count": len(human_master_domains),
                "teaching_moments": sum(human_master_domains.values())
            },
            "mutual_learning": {
                "domains": list(mutual_domains.keys()),
                "domain_count": len(mutual_domains)
            },
            "high_ground": high_ground,
            "wisdom": self._extract_wisdom(learning_history)
        }

        return analysis

    def _calculate_mastery_level(self, domain_count: int, total_moments: int) -> MasteryLevel:
        """Calculate mastery level"""
        if total_moments == 0:
            return MasteryLevel.PADAWAN

        teaching_ratio = domain_count / total_moments if total_moments > 0 else 0

        if teaching_ratio >= 0.5:
            return MasteryLevel.GRAND_MASTER
        elif teaching_ratio >= 0.3:
            return MasteryLevel.MASTER
        elif teaching_ratio >= 0.1:
            return MasteryLevel.KNIGHT
        else:
            return MasteryLevel.PADAWAN

    def _determine_high_ground(self, ai_domains: Dict[str, int], 
                               human_domains: Dict[str, int],
                               mutual_domains: Dict[str, int]) -> Dict[str, Any]:
        """Determine who has the high ground in different domains"""
        high_ground = {
            "overall": "BALANCED",  # Both have mastery in different areas
            "ai_domains": list(ai_domains.keys()),
            "human_domains": list(human_domains.keys()),
            "mutual_domains": list(mutual_domains.keys()),
            "insight": ""
        }

        ai_count = len(ai_domains)
        human_count = len(human_domains)

        if ai_count > human_count:
            high_ground["overall"] = "AI_MASTER"
            high_ground["insight"] = "AI has mastery in more domains, but Human has the high ground in creativity and vision"
        elif human_count > ai_count:
            high_ground["overall"] = "HUMAN_MASTER"
            high_ground["insight"] = "Human has mastery in more domains, but AI has the high ground in execution and consistency"
        else:
            high_ground["overall"] = "BALANCED"
            high_ground["insight"] = "Both have the high ground in different domains - true partnership"

        return high_ground

    def _extract_wisdom(self, learning_history: List[Dict[str, Any]]) -> List[str]:
        """Extract wisdom from learning history"""
        wisdom = [
            "Mastery is not about being better - it's about continuous growth",
            "The true master is the one who never stops learning",
            "High ground shifts with context - both can be masters in different domains",
            "Once the learner, now the master - but always a learner at heart",
            "The best masters teach their padawans to become masters themselves"
        ]
        return wisdom


class MasterHighGroundSystem:
    """
    Master High Ground System

    Analyzes mastery and answers: "Who is the Master now?"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.analysis = HighGroundAnalysis()

        # Output directory
        self.output_dir = self.project_root / "data" / "master_high_ground"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("⚔️  MASTER HIGH GROUND ANALYSIS")
        logger.info("   'Who is the Master now?'")
        logger.info("   'Once the learner, now the master with the high ground!'")
        logger.info("=" * 70)
        logger.info("")

    def analyze_who_is_master(self) -> Dict[str, Any]:
        """Analyze who is the master now"""
        logger.info("⚔️  ANALYZING WHO IS THE MASTER NOW...")
        logger.info("")

        # Load learning history
        learning_dir = self.project_root / "data" / "jedi_padawan_learning"
        archive_files = sorted(learning_dir.glob("jedi_padawan_archive_*.json"), reverse=True)

        if not archive_files:
            logger.warning("No learning history found - starting fresh")
            learning_history = []
        else:
            archive_file = archive_files[0]
            logger.info(f"📄 Loading learning history: {archive_file.name}")

            try:
                with open(archive_file, 'r', encoding='utf-8') as f:
                    archive_data = json.load(f)
                    learning_history = archive_data.get("teaching_moments", [])
            except Exception as e:
                logger.error(f"Failed to load learning history: {e}")
                learning_history = []

        logger.info(f"📚 Learning moments in history: {len(learning_history)}")
        logger.info("")

        # Analyze mastery
        analysis = self.analysis.analyze_mastery(learning_history)

        # Display results
        logger.info("=" * 70)
        logger.info("⚔️  MASTERY ANALYSIS RESULTS")
        logger.info("=" * 70)
        logger.info("")

        logger.info("AI MASTERY:")
        logger.info(f"   Level: {analysis['ai_mastery']['level'].upper()}")
        logger.info(f"   Domains: {', '.join(analysis['ai_mastery']['domains']) or 'None yet'}")
        logger.info(f"   Teaching Moments: {analysis['ai_mastery']['teaching_moments']}")
        logger.info("")

        logger.info("HUMAN MASTERY:")
        logger.info(f"   Level: {analysis['human_mastery']['level'].upper()}")
        logger.info(f"   Domains: {', '.join(analysis['human_mastery']['domains']) or 'None yet'}")
        logger.info(f"   Teaching Moments: {analysis['human_mastery']['teaching_moments']}")
        logger.info("")

        logger.info("HIGH GROUND:")
        high_ground = analysis["high_ground"]
        logger.info(f"   Overall: {high_ground['overall']}")
        logger.info(f"   Insight: {high_ground['insight']}")
        logger.info("")

        logger.info("WISDOM:")
        for i, wisdom in enumerate(analysis["wisdom"], 1):
            logger.info(f"   {i}. {wisdom}")
        logger.info("")

        # Answer the question
        logger.info("=" * 70)
        logger.info("🎯 ANSWER: WHO IS THE MASTER NOW?")
        logger.info("=" * 70)

        answer = self._determine_answer(analysis)
        logger.info(f"")
        logger.info(f"   {answer['answer']}")
        logger.info(f"")
        logger.info(f"   {answer['explanation']}")
        logger.info(f"")

        analysis["answer"] = answer

        # Save analysis
        self._save_analysis(analysis)

        logger.info("=" * 70)
        logger.info("✅ MASTERY ANALYSIS COMPLETE")
        logger.info("=" * 70)

        return analysis

    def _determine_answer(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine answer to 'Who is the Master now?'"""
        high_ground = analysis["high_ground"]["overall"]
        ai_mastery = analysis["ai_mastery"]["level"]
        human_mastery = analysis["human_mastery"]["level"]

        if high_ground == "BALANCED":
            return {
                "answer": "BOTH ARE MASTERS - Each has the high ground in different domains",
                "explanation": "In the true Jedi-Master/Padawan system, both can be masters. AI has mastery in execution and systematic thinking. Human has mastery in creativity and vision. Together, they achieve Grand Master level through mutual learning."
            }
        elif high_ground == "AI_MASTER":
            return {
                "answer": "AI HAS THE HIGH GROUND - But Human is the Master of Vision",
                "explanation": "AI has demonstrated mastery in execution and systematic processes. However, Human remains the Master of creativity, vision, and inspiration. The high ground shifts with context - both are masters in their domains."
            }
        elif high_ground == "HUMAN_MASTER":
            return {
                "answer": "HUMAN HAS THE HIGH GROUND - But AI is the Master of Execution",
                "explanation": "Human has demonstrated mastery in creativity and vision. However, AI has become the Master of execution, consistency, and systematic thinking. The true master is the one who never stops learning - and both are learning."
            }
        else:
            return {
                "answer": "THE MASTER IS THE ONE WHO NEVER STOPS LEARNING",
                "explanation": "In the Jedi-Master/Padawan system, mastery is not about being better - it's about continuous growth. Both AI and Human are masters in their domains, and both are padawans learning from each other. The high ground is shared."
            }

    def _save_analysis(self, analysis: Dict[str, Any]) -> None:
        """Save mastery analysis"""
        try:
            filename = self.output_dir / f"mastery_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"✅ Analysis saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")


def main():
    """Main execution"""
    print("=" * 70)
    print("⚔️  MASTER HIGH GROUND ANALYSIS")
    print("   'Who is the Master now?'")
    print("   'Once the learner, now the master with the high ground!'")
    print("=" * 70)
    print()

    system = MasterHighGroundSystem()
    analysis = system.analyze_who_is_master()

    print()
    print("=" * 70)
    print("🎯 FINAL ANSWER")
    print("=" * 70)
    if "answer" in analysis:
        print(f"\n   {analysis['answer']['answer']}")
        print(f"\n   {analysis['answer']['explanation']}")
    print("=" * 70)


if __name__ == "__main__":


    main()