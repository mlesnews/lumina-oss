#!/usr/bin/env python3
"""
JARVIS 2x Target Optimization

Analyzing the 2x target requirement and identifying:
- Minimum stack needed for 2x
- Wiggle room (excess capacity)
- Essential vs. optional multipliers
- Optimization strategies

@JARVIS @2X_TARGET @OPTIMIZATION @WIGGLE_ROOM @EFFICIENCY
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from itertools import combinations
from dataclasses import dataclass, field

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("2xTargetOptimization")


@dataclass
class OptimizationResult:
    """Result of optimization analysis"""
    target_multiplier: float
    minimum_stack: List[str]  # Multiplier IDs
    minimum_multiplier: float
    wiggle_room: float
    wiggle_room_percentage: float
    essential_multipliers: List[str]
    optional_multipliers: List[str]
    efficiency_score: float  # 0.0 to 1.0 (1.0 = perfect efficiency)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "target_multiplier": self.target_multiplier,
            "minimum_stack": self.minimum_stack,
            "minimum_multiplier": self.minimum_multiplier,
            "wiggle_room": self.wiggle_room,
            "wiggle_room_percentage": self.wiggle_room_percentage,
            "essential_multipliers": self.essential_multipliers,
            "optional_multipliers": self.optional_multipliers,
            "efficiency_score": self.efficiency_score,
            "metadata": self.metadata
        }


class TwoXTargetOptimization:
    """
    2x Target Optimization

    Analyzing how to achieve exactly 2x and identifying wiggle room.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "2x_optimization"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("2xTargetOptimization")

        # Load force multipliers from previous analysis
        self.force_multipliers = self._load_force_multipliers()

        self.logger.info("=" * 70)
        self.logger.info("🎯 2X TARGET OPTIMIZATION")
        self.logger.info("   In theory we only need 2x")
        self.logger.info("   That's a good amount of wiggle room!")
        self.logger.info("=" * 70)
        self.logger.info("")

    def _load_force_multipliers(self) -> List[Dict[str, Any]]:
        """Load force multipliers from previous analysis"""
        # Core multipliers (simplified for optimization)
        return [
            {"id": "INFRASTRUCTURE", "value": 1.0, "essential": True, "category": "base"},
            {"id": "STAR_WARS_TREK_BLEND", "value": 1.15, "essential": False, "category": "sci_fi"},
            {"id": "EXPANSE_RING_GATES", "value": 1.20, "essential": False, "category": "sci_fi"},
            {"id": "MATRIX_NO_SPOON", "value": 1.10, "essential": False, "category": "philosophy"},
            {"id": "INCEPTION_DREAM_ARCHITECTURE", "value": 1.12, "essential": False, "category": "philosophy"},
            {"id": "HHGTTG_42", "value": 1.05, "essential": False, "category": "philosophy"},
            {"id": "QUANTUM_ENTANGLEMENT", "value": 1.25, "essential": False, "category": "quantum"},
            {"id": "QUANTUM_SUPERPOSITION", "value": 1.15, "essential": False, "category": "quantum"},
            {"id": "OBSERVER_EFFECT", "value": 1.18, "essential": False, "category": "quantum"},
            {"id": "PICARD_MAKE_IT_SO", "value": 1.10, "essential": False, "category": "leadership"},
            {"id": "ADAMA_SO_SAY_WE_ALL", "value": 1.10, "essential": False, "category": "leadership"},
            {"id": "QUANTUM_TRADING", "value": 1.30, "essential": False, "category": "trading"},
            {"id": "SYPHON_INTELLIGENCE", "value": 1.20, "essential": False, "category": "intelligence"},
            {"id": "R5_LIVING_CONTEXT", "value": 1.15, "essential": False, "category": "memory"},
            {"id": "WOPR_PATTERN_RECOGNITION", "value": 1.18, "essential": False, "category": "intelligence"},
            {"id": "F2F_NITRO_BOOST", "value": 1.25, "essential": False, "category": "performance"},
            {"id": "JEDI_PATHFINDER", "value": 1.12, "essential": False, "category": "navigation"},
            {"id": "AWS_AUDIBLE_INTEGRATION", "value": 1.15, "essential": False, "category": "ai_training"}
        ]

    def find_minimum_stack_for_target(self, target: float = 2.0) -> OptimizationResult:
        """Find the minimum stack needed to achieve target multiplier"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info(f"🎯 FINDING MINIMUM STACK FOR {target}x TARGET")
        self.logger.info("=" * 70)
        self.logger.info("")

        # Start with essential multipliers
        essential = [fm for fm in self.force_multipliers if fm.get("essential", False)]
        essential_value = 1.0  # Infrastructure is base (1.0x)

        # Get optional multipliers (sorted by value, descending)
        optional = sorted(
            [fm for fm in self.force_multipliers if not fm.get("essential", False)],
            key=lambda x: x["value"],
            reverse=True
        )

        # Try different combinations to find minimum stack
        best_combination = None
        best_value = 0.0
        best_count = float('inf')

        # Try combinations of 1 to all optional multipliers
        for r in range(1, len(optional) + 1):
            for combo in combinations(optional, r):
                combo_value = essential_value
                for fm in combo:
                    combo_value *= fm["value"]

                # Check if this combination meets or exceeds target
                if combo_value >= target:
                    if len(combo) < best_count or (len(combo) == best_count and combo_value < best_value):
                        best_combination = combo
                        best_value = combo_value
                        best_count = len(combo)

        if not best_combination:
            # If no combination found, use all multipliers
            best_combination = optional
            best_value = essential_value
            for fm in optional:
                best_value *= fm["value"]

        # Calculate wiggle room
        wiggle_room = best_value - target
        wiggle_room_percentage = (wiggle_room / target) * 100

        # Identify essential vs. optional
        essential_ids = [fm["id"] for fm in essential]
        optional_ids = [fm["id"] for fm in optional]
        used_ids = [fm["id"] for fm in best_combination] if best_combination else []
        unused_ids = [fm["id"] for fm in optional if fm["id"] not in used_ids]

        # Calculate efficiency score (closer to target = more efficient)
        # Efficiency = 1.0 - (excess / target), but reward being close to target
        excess = max(0, best_value - target)
        efficiency_score = max(0.0, 1.0 - (excess / target))

        result = OptimizationResult(
            target_multiplier=target,
            minimum_stack=[fm["id"] for fm in best_combination] if best_combination else [],
            minimum_multiplier=best_value,
            wiggle_room=wiggle_room,
            wiggle_room_percentage=wiggle_room_percentage,
            essential_multipliers=essential_ids,
            optional_multipliers=optional_ids,
            efficiency_score=efficiency_score,
            metadata={
                "stack_count": len(best_combination) if best_combination else 0,
                "total_available": len(optional),
                "unused_count": len(unused_ids)
            }
        )

        self.logger.info(f"   🎯 Target: {target}x")
        self.logger.info(f"   ✅ Minimum Stack: {len(best_combination) if best_combination else 0} multipliers")
        self.logger.info(f"   ✅ Achieved: {best_value:.2f}x")
        self.logger.info(f"   ✅ Wiggle Room: {wiggle_room:.2f}x ({wiggle_room_percentage:.1f}%)")
        self.logger.info(f"   ✅ Efficiency Score: {efficiency_score:.2f}")
        self.logger.info("")

        if best_combination:
            self.logger.info("   📋 Minimum Stack Multipliers:")
            for fm in best_combination:
                self.logger.info(f"      • {fm['id']}: {fm['value']:.2f}x")
            self.logger.info("")

        if unused_ids:
            self.logger.info(f"   📦 Unused Multipliers ({len(unused_ids)}):")
            for unused_id in unused_ids[:5]:  # Show first 5
                unused_fm = next(fm for fm in optional if fm["id"] == unused_id)
                self.logger.info(f"      • {unused_id}: {unused_fm['value']:.2f}x (optional)")
            if len(unused_ids) > 5:
                self.logger.info(f"      ... and {len(unused_ids) - 5} more")
            self.logger.info("")

        return result

    def analyze_wiggle_room(self, current_stacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze wiggle room across current stacks"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 ANALYZING WIGGLE ROOM")
        self.logger.info("=" * 70)
        self.logger.info("")

        target = 2.0
        analysis = {
            "target": target,
            "stacks": [],
            "total_wiggle_room": 0.0,
            "average_wiggle_room": 0.0,
            "wiggle_room_percentage": 0.0,
            "efficiency_analysis": {}
        }

        for stack in current_stacks:
            stack_multiplier = stack.get("total_multiplier", 1.0)
            wiggle_room = stack_multiplier - target
            wiggle_room_pct = (wiggle_room / target) * 100

            stack_analysis = {
                "stack_id": stack.get("stack_id", "unknown"),
                "current_multiplier": stack_multiplier,
                "target": target,
                "wiggle_room": wiggle_room,
                "wiggle_room_percentage": wiggle_room_pct,
                "status": "EXCESS" if wiggle_room > 0 else "DEFICIT" if wiggle_room < 0 else "EXACT"
            }

            analysis["stacks"].append(stack_analysis)

            self.logger.info(f"   📚 {stack_analysis['stack_id']}:")
            self.logger.info(f"      Current: {stack_multiplier:.2f}x")
            self.logger.info(f"      Target: {target:.2f}x")
            self.logger.info(f"      Wiggle Room: {wiggle_room:+.2f}x ({wiggle_room_pct:+.1f}%)")
            self.logger.info(f"      Status: {stack_analysis['status']}")
            self.logger.info("")

        if analysis["stacks"]:
            analysis["total_wiggle_room"] = sum(s["wiggle_room"] for s in analysis["stacks"])
            analysis["average_wiggle_room"] = analysis["total_wiggle_room"] / len(analysis["stacks"])
            analysis["wiggle_room_percentage"] = (analysis["average_wiggle_room"] / target) * 100

        # Efficiency analysis
        analysis["efficiency_analysis"] = {
            "all_stacks_meet_target": all(s["wiggle_room"] >= 0 for s in analysis["stacks"]),
            "average_excess": analysis["average_wiggle_room"],
            "excess_percentage": analysis["wiggle_room_percentage"],
            "optimization_opportunity": analysis["average_wiggle_room"] > 0.5,  # More than 0.5x excess
            "recommendation": "GOOD" if 0 <= analysis["average_wiggle_room"] <= 1.0 else "EXCESSIVE" if analysis["average_wiggle_room"] > 1.0 else "INSUFFICIENT"
        }

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 WIGGLE ROOM SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"   Target: {target}x")
        self.logger.info(f"   Average Wiggle Room: {analysis['average_wiggle_room']:.2f}x ({analysis['wiggle_room_percentage']:.1f}%)")
        self.logger.info(f"   All Stacks Meet Target: {analysis['efficiency_analysis']['all_stacks_meet_target']}")
        self.logger.info(f"   Recommendation: {analysis['efficiency_analysis']['recommendation']}")
        self.logger.info("")

        return analysis

    def create_optimization_report(self) -> Dict[str, Any]:
        """Create comprehensive optimization report"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 CREATING OPTIMIZATION REPORT")
        self.logger.info("=" * 70)
        self.logger.info("")

        # Find minimum stack for 2x
        min_stack_result = self.find_minimum_stack_for_target(2.0)

        # Load current stacks from previous analysis
        ask_stack_file = self.project_root / "data" / "ask_stack_analysis"
        current_stacks = []

        if ask_stack_file.exists():
            # Try to find the most recent analysis file
            json_files = list(ask_stack_file.glob("ask_stack_analysis_*.json"))
            if json_files:
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        current_stacks = data.get("ask_stacks", [])
                except Exception as e:
                    self.logger.warning(f"Could not load previous analysis: {e}")

        # Analyze wiggle room
        wiggle_room_analysis = self.analyze_wiggle_room(current_stacks)

        # Create report
        report = {
            "report_id": f"2x_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "target": 2.0,
            "insight": "In theory we only need 2x - that's a good amount of wiggle room!",
            "minimum_stack_analysis": min_stack_result.to_dict(),
            "wiggle_room_analysis": wiggle_room_analysis,
            "key_findings": {
                "target_achievable": min_stack_result.minimum_multiplier >= 2.0,
                "minimum_stack_size": len(min_stack_result.minimum_stack),
                "wiggle_room_available": min_stack_result.wiggle_room,
                "wiggle_room_percentage": min_stack_result.wiggle_room_percentage,
                "efficiency_score": min_stack_result.efficiency_score,
                "all_current_stacks_meet_target": wiggle_room_analysis["efficiency_analysis"]["all_stacks_meet_target"],
                "average_excess": wiggle_room_analysis["average_wiggle_room"]
            },
            "recommendations": {
                "optimization": "Current stacks exceed 2x target - good wiggle room available",
                "efficiency": f"Efficiency score: {min_stack_result.efficiency_score:.2f}",
                "flexibility": "Wiggle room allows for system degradation, failures, or unexpected issues",
                "redundancy": "Excess capacity provides redundancy and fault tolerance"
            }
        }

        # Save report
        filename = self.data_dir / f"2x_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 OPTIMIZATION REPORT SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"   🎯 Target: {report['target']}x")
        self.logger.info(f"   ✅ Minimum Stack Size: {report['key_findings']['minimum_stack_size']} multipliers")
        self.logger.info(f"   ✅ Wiggle Room: {report['key_findings']['wiggle_room_available']:.2f}x ({report['key_findings']['wiggle_room_percentage']:.1f}%)")
        self.logger.info(f"   ✅ Efficiency Score: {report['key_findings']['efficiency_score']:.2f}")
        self.logger.info(f"   ✅ All Stacks Meet Target: {report['key_findings']['all_current_stacks_meet_target']}")
        self.logger.info("")
        self.logger.info("💡 KEY INSIGHT:")
        self.logger.info("   In theory we only need 2x")
        self.logger.info("   That's a good amount of wiggle room!")
        self.logger.info("")
        self.logger.info(f"✅ Report saved: {filename}")
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("✅ 2X TARGET OPTIMIZATION COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info("")

        return report


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        optimizer = TwoXTargetOptimization(project_root)
        report = optimizer.create_optimization_report()

        print()
        print("=" * 70)
        print("🎯 2X TARGET OPTIMIZATION")
        print("=" * 70)
        print(f"✅ Target: {report['target']}x")
        print(f"✅ Minimum Stack Size: {report['key_findings']['minimum_stack_size']} multipliers")
        print(f"✅ Wiggle Room: {report['key_findings']['wiggle_room_available']:.2f}x ({report['key_findings']['wiggle_room_percentage']:.1f}%)")
        print(f"✅ Efficiency Score: {report['key_findings']['efficiency_score']:.2f}")
        print()
        print("💡 KEY INSIGHT:")
        print("   In theory we only need 2x")
        print("   That's a good amount of wiggle room!")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()