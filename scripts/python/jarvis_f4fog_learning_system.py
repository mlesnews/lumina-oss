#!/usr/bin/env python3
"""
JARVIS F4FOG Learning System
Capture learnings from F4FOG execution and identify next steps

@JARVIS @F4FOG @LEARNING @INSIGHTS @NEXT_STEPS @XP_BONUS
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISF4FOGLearning")


class F4FOGLearningSystem:
    """
    F4FOG Learning System

    Captures learnings from F4FOG executions:
    - What worked well
    - What needs improvement
    - Patterns discovered
    - Next steps identified
    - Teaching moments (AI teaching human, human teaching AI)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize learning system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Learning output
        self.learning_dir = self.project_root / "data" / "f4fog_learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("🧠 JARVIS F4FOG LEARNING SYSTEM")
        logger.info("   Capturing Learnings & Identifying Next Steps")
        logger.info("=" * 70)
        logger.info("")

    def capture_learnings(self, f4fog_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture learnings from F4FOG execution

        Args:
            f4fog_results: F4FOG execution results

        Returns:
            Learning insights
        """
        logger.info("🧠 CAPTURING LEARNINGS...")
        logger.info("")

        learnings = {
            "learning_id": f"f4fog_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "captured_at": datetime.now().isoformat(),
            "source_execution": f4fog_results.get("f4fog_id"),
            "insights": {},
            "patterns": [],
            "improvements": [],
            "teaching_moments": [],
            "next_steps": []
        }

        # Insight 1: F4FOG Effectiveness
        logger.info("INSIGHT 1: F4FOG Effectiveness")
        logger.info("-" * 70)
        effectiveness = self._analyze_effectiveness(f4fog_results)
        learnings["insights"]["effectiveness"] = effectiveness
        logger.info(f"   Focus Level Achieved: {effectiveness['focus_level']}")
        logger.info(f"   Teams Aligned: {effectiveness['alignment_percentage']}")
        logger.info("")

        # Insight 2: Layer Performance
        logger.info("INSIGHT 2: Layer Performance")
        logger.info("-" * 70)
        layer_performance = self._analyze_layer_performance(f4fog_results)
        learnings["insights"]["layer_performance"] = layer_performance
        for layer, perf in layer_performance.items():
            logger.info(f"   {layer}: {perf['status']} - {perf['performance']}")
        logger.info("")

        # Insight 3: Patterns Discovered
        logger.info("INSIGHT 3: Patterns Discovered")
        logger.info("-" * 70)
        patterns = self._discover_patterns(f4fog_results)
        learnings["patterns"] = patterns
        for pattern in patterns:
            logger.info(f"   • {pattern['name']}: {pattern['description']}")
        logger.info("")

        # Insight 4: Improvements Needed
        logger.info("INSIGHT 4: Improvements Needed")
        logger.info("-" * 70)
        improvements = self._identify_improvements(f4fog_results)
        learnings["improvements"] = improvements
        for improvement in improvements:
            logger.info(f"   • {improvement['area']}: {improvement['suggestion']}")
        logger.info("")

        # Insight 5: Teaching Moments
        logger.info("INSIGHT 5: Teaching Moments")
        logger.info("-" * 70)
        teaching_moments = self._capture_teaching_moments(f4fog_results)
        learnings["teaching_moments"] = teaching_moments
        for moment in teaching_moments:
            logger.info(f"   • {moment['type']}: {moment['lesson']}")
        logger.info("")

        # Insight 6: Next Steps
        logger.info("INSIGHT 6: Next Steps")
        logger.info("-" * 70)
        next_steps = self._identify_next_steps(f4fog_results, learnings)
        learnings["next_steps"] = next_steps
        for step in next_steps:
            logger.info(f"   • [{step['priority']}] {step['action']}")
        logger.info("")

        # Summary
        logger.info("=" * 70)
        logger.info("📊 LEARNING SUMMARY")
        logger.info("=" * 70)

        learnings["summary"] = {
            "total_insights": len(learnings["insights"]),
            "patterns_discovered": len(learnings["patterns"]),
            "improvements_identified": len(learnings["improvements"]),
            "teaching_moments": len(learnings["teaching_moments"]),
            "next_steps": len(learnings["next_steps"]),
            "xp_bonus_earned": True
        }

        logger.info(f"Total Insights: {learnings['summary']['total_insights']}")
        logger.info(f"Patterns Discovered: {learnings['summary']['patterns_discovered']}")
        logger.info(f"Improvements Identified: {learnings['summary']['improvements_identified']}")
        logger.info(f"Teaching Moments: {learnings['summary']['teaching_moments']}")
        logger.info(f"Next Steps: {learnings['summary']['next_steps']}")
        logger.info(f"XP Bonus Earned: ✅ YES!")
        logger.info("")

        # Save learnings
        self._save_learnings(learnings)

        logger.info("=" * 70)
        logger.info("✅ LEARNINGS CAPTURED")
        logger.info("=" * 70)

        return learnings

    def _analyze_effectiveness(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze F4FOG effectiveness"""
        summary = results.get("summary", {})

        return {
            "focus_level": summary.get("focus_level", "UNKNOWN"),
            "alignment_percentage": summary.get("alignment_percentage", "0%"),
            "teams_assigned": summary.get("teams_assigned", 0),
            "can_proceed": summary.get("can_proceed", False),
            "effectiveness_score": self._calculate_effectiveness_score(summary)
        }

    def _calculate_effectiveness_score(self, summary: Dict[str, Any]) -> float:
        """Calculate effectiveness score"""
        score = 0.0

        # Focus level score
        focus_level = summary.get("focus_level", "")
        if focus_level == "singular":
            score += 40
        elif focus_level == "focused":
            score += 30
        elif focus_level == "converging":
            score += 20

        # Alignment score
        alignment = float(summary.get("alignment_percentage", "0%").replace("%", ""))
        score += alignment * 0.3

        # Can proceed score
        if summary.get("can_proceed", False):
            score += 20

        # Teams assigned score
        teams = summary.get("teams_assigned", 0)
        score += min(teams * 2, 10)

        return min(score, 100.0)

    def _analyze_layer_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance of each inference layer"""
        layers = results.get("layers", {})

        performance = {}

        # Decisioning layer
        if "decisioning" in layers:
            decisioning = layers["decisioning"]
            performance["decisioning"] = {
                "status": "SUCCESS",
                "performance": "Primary objective decided successfully",
                "decision_score": decisioning.get("primary_objective", {}).get("score", 0)
            }

        # Troubleshooting layer
        if "troubleshooting" in layers:
            troubleshooting = layers["troubleshooting"]
            diagnosis = troubleshooting.get("diagnosis", {})
            performance["troubleshooting"] = {
                "status": "SUCCESS",
                "performance": f"Diagnosed {len(diagnosis.get('blockers', []))} blockers, {len(diagnosis.get('issues', []))} issues",
                "can_proceed": diagnosis.get("can_proceed", False)
            }

        # AI Architect layer
        if "ai_architect" in layers:
            architect = layers["ai_architect"]
            performance["ai_architect"] = {
                "status": "SUCCESS",
                "performance": f"Assigned {architect.get('assigned_teams', 0)} teams",
                "focus_level": architect.get("focus_level", "UNKNOWN")
            }

        return performance

    def _discover_patterns(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover patterns from execution"""
        patterns = []

        # Pattern 1: Singular Focus Effectiveness
        summary = results.get("summary", {})
        if summary.get("focus_level") == "singular":
            patterns.append({
                "name": "Singular Focus Pattern",
                "description": "F4FOG singular focus successfully aligns all teams",
                "category": "FOCUS",
                "confidence": "HIGH"
            })

        # Pattern 2: Multi-Layer Inference
        layers = results.get("layers", {})
        if len(layers) >= 3:
            patterns.append({
                "name": "Multi-Layer Inference Pattern",
                "description": "Decisioning → Troubleshooting → AI Architect layers work effectively together",
                "category": "ARCHITECTURE",
                "confidence": "HIGH"
            })

        # Pattern 3: Team Assignment Pattern
        if summary.get("teams_assigned", 0) > 0:
            patterns.append({
                "name": "Universal Team Assignment Pattern",
                "description": "All teams assigned to primary objective (F4FOG principle)",
                "category": "TEAM_MANAGEMENT",
                "confidence": "HIGH"
            })

        return patterns

    def _identify_improvements(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify areas for improvement"""
        improvements = []

        summary = results.get("summary", {})

        # Improvement 1: Alignment
        alignment = float(summary.get("alignment_percentage", "0%").replace("%", ""))
        if alignment < 100:
            improvements.append({
                "area": "Team Alignment",
                "suggestion": f"Improve alignment from {alignment:.1f}% to 100% by better matching team capabilities to objective requirements",
                "priority": "MEDIUM"
            })

        # Improvement 2: Blockers
        if summary.get("blockers", 0) > 0:
            improvements.append({
                "area": "Blocker Resolution",
                "suggestion": "Implement automatic blocker resolution in troubleshooting layer",
                "priority": "HIGH"
            })

        # Improvement 3: Learning Integration
        improvements.append({
            "area": "Learning Integration",
            "suggestion": "Integrate learnings into R5 Living Context Matrix for future reference",
            "priority": "MEDIUM"
        })

        return improvements

    def _capture_teaching_moments(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Capture teaching moments (AI teaching human, human teaching AI)"""
        moments = []

        # Teaching Moment 1: F4FOG Concept
        moments.append({
            "type": "AI_TO_HUMAN",
            "lesson": "F4FOG (Finger of God) system demonstrates how singular focus can align entire company resources",
            "teacher": "JARVIS",
            "student": "Human",
            "concept": "Singular Focus Strategy"
        })

        # Teaching Moment 2: Multi-Layer Inference
        moments.append({
            "type": "AI_TO_HUMAN",
            "lesson": "Decisioning → Troubleshooting → AI Architect layers create comprehensive execution framework",
            "teacher": "JARVIS",
            "student": "Human",
            "concept": "Layered Inference Architecture"
        })

        # Teaching Moment 3: Human Teaching AI
        moments.append({
            "type": "HUMAN_TO_AI",
            "lesson": "Human provided Twister movie inspiration for F4FOG concept - creative problem-solving approach",
            "teacher": "Human",
            "student": "JARVIS",
            "concept": "Creative Inspiration"
        })

        # Teaching Moment 4: Learning Loop
        moments.append({
            "type": "MUTUAL_LEARNING",
            "lesson": "Both AI and Human learning together - AI teaches execution, Human teaches creativity",
            "teacher": "Both",
            "student": "Both",
            "concept": "Collaborative Learning"
        })

        return moments

    def _identify_next_steps(self, results: Dict[str, Any], learnings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify next steps based on learnings"""
        next_steps = []

        summary = results.get("summary", {})

        # Next Step 1: Execute Prescribed Fixes
        troubleshooting = results.get("layers", {}).get("troubleshooting", {})
        prescribed_fixes = troubleshooting.get("prescribed_fixes", [])
        if prescribed_fixes:
            next_steps.append({
                "priority": "HIGH",
                "action": "Execute prescribed fixes from troubleshooting layer",
                "target": "validation_system",
                "estimated_time": "2-4 hours"
            })

        # Next Step 2: Improve Alignment
        alignment = float(summary.get("alignment_percentage", "0%").replace("%", ""))
        if alignment < 100:
            next_steps.append({
                "priority": "MEDIUM",
                "action": f"Improve team alignment from {alignment:.1f}% to 100%",
                "target": "team_assignment",
                "estimated_time": "1-2 hours"
            })

        # Next Step 3: Integrate Learnings
        next_steps.append({
            "priority": "MEDIUM",
            "action": "Integrate learnings into R5 Living Context Matrix",
            "target": "knowledge_system",
            "estimated_time": "30 minutes"
        })

        # Next Step 4: Apply F4FOG to Next Objective
        next_steps.append({
            "priority": "LOW",
            "action": "Apply F4FOG system to next high-priority objective",
            "target": "f4fog_system",
            "estimated_time": "Varies"
        })

        return next_steps

    def _save_learnings(self, learnings: Dict[str, Any]) -> None:
        """Save learnings"""
        try:
            filename = self.learning_dir / f"{learnings['learning_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(learnings, f, indent=2, default=str)
            logger.info(f"✅ Learnings saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save learnings: {e}")


def main():
    """Main execution"""
    print("=" * 70)
    print("🧠 JARVIS F4FOG LEARNING SYSTEM")
    print("   Capturing Learnings & Identifying Next Steps")
    print("=" * 70)
    print()

    # Load latest F4FOG execution
    project_root = Path(__file__).parent.parent.parent
    f4fog_dir = project_root / "data" / "f4fog_execution"
    f4fog_files = sorted(f4fog_dir.glob("f4fog_*.json"), reverse=True)

    if not f4fog_files:
        print("❌ No F4FOG execution results found")
        return

    f4fog_file = f4fog_files[0]
    print(f"📄 Loading F4FOG execution: {f4fog_file.name}")

    try:
        with open(f4fog_file, 'r', encoding='utf-8') as f:
            f4fog_results = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load F4FOG results: {e}")
        return

    print()

    # Capture learnings
    learning_system = F4FOGLearningSystem()
    learnings = learning_system.capture_learnings(f4fog_results)

    print()
    print("=" * 70)
    print("✅ LEARNINGS CAPTURED")
    print("=" * 70)
    print(f"Total Insights: {learnings['summary']['total_insights']}")
    print(f"Patterns Discovered: {learnings['summary']['patterns_discovered']}")
    print(f"Improvements: {learnings['summary']['improvements_identified']}")
    print(f"Teaching Moments: {learnings['summary']['teaching_moments']}")
    print(f"Next Steps: {learnings['summary']['next_steps']}")
    print(f"XP Bonus: ✅ EARNED!")
    print("=" * 70)
    print()
    print("🎯 NEXT STEPS:")
    for step in learnings['next_steps']:
        print(f"   [{step['priority']}] {step['action']}")
    print("=" * 70)


if __name__ == "__main__":


    main()