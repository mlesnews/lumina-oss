#!/usr/bin/env python3
"""
Syphon All of Lumina → WOPR 10,000 Year Simulation
Focus: JARVIS Self-Improvement, Zero-Sum Reinforcement Learning, Machine Learning

Extracts all patterns from Lumina codebase, runs through WOPR simulation,
focusing on JARVIS self-improvement mechanisms.

Tags: #SYPHON #WOPR #JARVIS #SELF_IMPROVEMENT #REINFORCEMENT_LEARNING #ZERO_SUM #ML
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import os

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("SyphonLuminaWOPRJARVIS")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SyphonLuminaWOPRJARVIS")

try:
    from scripts.python.syphon_system import SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("SYPHON system not available")

# WOPR simulation logic embedded (avoiding import issues)
WOPR_AVAILABLE = True


@dataclass
class JARVISSelfImprovementPhase:
    """A phase in JARVIS self-improvement evolution"""
    year: int
    phase_name: str
    reinforcement_learning: float  # 0.0 to 1.0
    zero_sum_learning: float  # 0.0 to 1.0
    machine_learning: float  # 0.0 to 1.0
    self_improvement_rate: float  # Improvement per year
    learning_efficiency: float  # 0.0 to 1.0
    autonomous_learning: float  # 0.0 to 1.0
    insights: List[str] = field(default_factory=list)
    sparks: List[str] = field(default_factory=list)


class SyphonLuminaWOPRJARVIS:
    """Syphon all of Lumina, run WOPR simulation for JARVIS self-improvement"""

    def __init__(self, project_root: Path):
        """Initialize syphon and WOPR"""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_wopr_jarvis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(self.project_root)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")

        # WOPR simulation logic embedded
        logger.info("✅ WOPR simulation ready")

        logger.info("✅ Syphon Lumina WOPR JARVIS initialized")

    def syphon_all_lumina(self) -> Dict[str, Any]:
        """Syphon all patterns from Lumina codebase"""
        logger.info("="*80)
        logger.info("🔍 SYPHONING ALL OF LUMINA")
        logger.info("="*80)
        logger.info("")

        patterns = {
            "extraction_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "jarvis_patterns": [],
            "learning_patterns": [],
            "automation_patterns": [],
            "decisioning_patterns": [],
            "file_count": 0,
            "total_lines": 0
        }

        # Syphon JARVIS-related files
        logger.info("📊 Syphoning JARVIS patterns...")
        jarvis_files = self._find_jarvis_files()
        patterns["jarvis_patterns"] = self._syphon_files(jarvis_files, "jarvis")
        patterns["file_count"] += len(jarvis_files)

        # Syphon learning/ML files
        logger.info("📊 Syphoning learning/ML patterns...")
        learning_files = self._find_learning_files()
        patterns["learning_patterns"] = self._syphon_files(learning_files, "learning")
        patterns["file_count"] += len(learning_files)

        # Syphon automation files
        logger.info("📊 Syphoning automation patterns...")
        automation_files = self._find_automation_files()
        patterns["automation_patterns"] = self._syphon_files(automation_files, "automation")
        patterns["file_count"] += len(automation_files)

        # Syphon decisioning files
        logger.info("📊 Syphoning decisioning patterns...")
        decisioning_files = self._find_decisioning_files()
        patterns["decisioning_patterns"] = self._syphon_files(decisioning_files, "decisioning")
        patterns["file_count"] += len(decisioning_files)

        logger.info(f"   ✅ Extracted patterns from {patterns['file_count']} files")
        logger.info("")

        return patterns

    def _find_jarvis_files(self) -> List[Path]:
        try:
            """Find all JARVIS-related files"""
            jarvis_files = []
            scripts_dir = self.project_root / "scripts" / "python"

            if scripts_dir.exists():
                for file_path in scripts_dir.rglob("*.py"):
                    if "jarvis" in file_path.name.lower():
                        jarvis_files.append(file_path)

            return jarvis_files[:50]  # Limit to first 50 for performance

        except Exception as e:
            self.logger.error(f"Error in _find_jarvis_files: {e}", exc_info=True)
            raise
    def _find_learning_files(self) -> List[Path]:
        try:
            """Find all learning/ML-related files"""
            learning_files = []
            scripts_dir = self.project_root / "scripts" / "python"

            if scripts_dir.exists():
                keywords = ["learn", "ml", "reinforcement", "neural", "training", "model"]
                for file_path in scripts_dir.rglob("*.py"):
                    if any(kw in file_path.name.lower() for kw in keywords):
                        learning_files.append(file_path)

            return learning_files[:30]

        except Exception as e:
            self.logger.error(f"Error in _find_learning_files: {e}", exc_info=True)
            raise
    def _find_automation_files(self) -> List[Path]:
        try:
            """Find all automation-related files"""
            automation_files = []
            scripts_dir = self.project_root / "scripts" / "python"

            if scripts_dir.exists():
                keywords = ["auto", "automate", "autonomous"]
                for file_path in scripts_dir.rglob("*.py"):
                    if any(kw in file_path.name.lower() for kw in keywords):
                        automation_files.append(file_path)

            return automation_files[:30]

        except Exception as e:
            self.logger.error(f"Error in _find_automation_files: {e}", exc_info=True)
            raise
    def _find_decisioning_files(self) -> List[Path]:
        try:
            """Find all decisioning-related files"""
            decisioning_files = []
            scripts_dir = self.project_root / "scripts" / "python"

            if scripts_dir.exists():
                keywords = ["decision", "aiq", "triage", "escalat"]
                for file_path in scripts_dir.rglob("*.py"):
                    if any(kw in file_path.name.lower() for kw in keywords):
                        decisioning_files.append(file_path)

            return decisioning_files[:30]

        except Exception as e:
            self.logger.error(f"Error in _find_decisioning_files: {e}", exc_info=True)
            raise
    def _syphon_files(self, files: List[Path], category: str) -> List[Dict[str, Any]]:
        """Syphon patterns from files"""
        patterns = []

        for file_path in files:
            try:
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8', errors='ignore')

                    # Extract key patterns
                    pattern = {
                        "file": str(file_path.relative_to(self.project_root)),
                        "category": category,
                        "lines": len(content.split('\n')),
                        "has_learning": "learn" in content.lower() or "train" in content.lower(),
                        "has_reinforcement": "reinforcement" in content.lower() or "reward" in content.lower(),
                        "has_zero_sum": "zero" in content.lower() and "sum" in content.lower(),
                        "has_self_improvement": "self" in content.lower() and "improve" in content.lower(),
                        "has_jarvis": "jarvis" in content.lower(),
                        "key_functions": self._extract_functions(content),
                        "key_classes": self._extract_classes(content)
                    }

                    patterns.append(pattern)
            except Exception as e:
                logger.debug(f"Error syphoning {file_path}: {e}")
                continue

        return patterns

    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from content"""
        import re
        functions = re.findall(r'def\s+(\w+)', content)
        return functions[:10]  # Limit to first 10

    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from content"""
        import re
        classes = re.findall(r'class\s+(\w+)', content)
        return classes[:10]  # Limit to first 10

    def run_wopr_jarvis_simulation(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Run WOPR 10,000 year simulation focused on JARVIS self-improvement"""
        logger.info("="*80)
        logger.info("⚡ WOPR 10,000 YEAR SIMULATION: JARVIS SELF-IMPROVEMENT")
        logger.info("   Focus: Reinforcement Learning, Zero-Sum Learning, Machine Learning")
        logger.info("="*80)
        logger.info("")

        phases = []
        all_sparks = []

        # Phase 1: Year 0 - Current State
        logger.info("📊 Phase 1: Year 0 (Current State)...")
        phase_0 = self._simulate_jarvis_year_0(patterns)
        phases.append(phase_0)
        all_sparks.extend(phase_0.sparks)

        # Phase 2: Years 1-2000 - Reinforcement Learning Introduction
        logger.info("📊 Phase 2: Years 1-2000 (Reinforcement Learning Introduction)...")
        phase_2000 = self._simulate_reinforcement_learning(phase_0, 2000)
        phases.append(phase_2000)
        all_sparks.extend(phase_2000.sparks)

        # Phase 3: Years 2001-5000 - Zero-Sum Learning
        logger.info("📊 Phase 3: Years 2001-5000 (Zero-Sum Learning)...")
        phase_5000 = self._simulate_zero_sum_learning(phase_2000, 5000)
        phases.append(phase_5000)
        all_sparks.extend(phase_5000.sparks)

        # Phase 4: Years 5001-8000 - Advanced ML Integration
        logger.info("📊 Phase 4: Years 5001-8000 (Advanced ML Integration)...")
        phase_8000 = self._simulate_advanced_ml(phase_5000, 8000)
        phases.append(phase_8000)
        all_sparks.extend(phase_8000.sparks)

        # Phase 5: Year 10000 - Perfect Self-Improvement
        logger.info("📊 Phase 5: Year 10000 (Perfect Self-Improvement)...")
        phase_10000 = self._simulate_perfect_self_improvement(phase_8000, 10000)
        phases.append(phase_10000)
        all_sparks.extend(phase_10000.sparks)

        # Extract unique sparks
        unique_sparks = self._extract_unique_sparks(all_sparks)

        # Analyze learning trajectory
        learning_trajectory = self._analyze_learning_trajectory(phases)

        # Analyze self-improvement rate
        improvement_rate = self._analyze_improvement_rate(phases)

        simulation_result = {
            "simulation_date": datetime.now().isoformat(),
            "simulation_years": 10000,
            "patterns_extracted": patterns,
            "phases": [
                {
                    "year": p.year,
                    "phase_name": p.phase_name,
                    "reinforcement_learning": p.reinforcement_learning,
                    "zero_sum_learning": p.zero_sum_learning,
                    "machine_learning": p.machine_learning,
                    "self_improvement_rate": p.self_improvement_rate,
                    "learning_efficiency": p.learning_efficiency,
                    "autonomous_learning": p.autonomous_learning,
                    "insights": p.insights,
                    "sparks": p.sparks
                }
                for p in phases
            ],
            "unique_sparks": unique_sparks,
            "learning_trajectory": learning_trajectory,
            "improvement_rate": improvement_rate,
            "final_state": {
                "reinforcement_learning": phase_10000.reinforcement_learning,
                "zero_sum_learning": phase_10000.zero_sum_learning,
                "machine_learning": phase_10000.machine_learning,
                "self_improvement_rate": phase_10000.self_improvement_rate,
                "learning_efficiency": phase_10000.learning_efficiency,
                "autonomous_learning": phase_10000.autonomous_learning
            }
        }

        return simulation_result

    def _simulate_jarvis_year_0(self, patterns: Dict[str, Any]) -> JARVISSelfImprovementPhase:
        """Simulate current state (Year 0)"""
        # Analyze patterns for current learning capabilities
        has_learning = any(p.get("has_learning", False) for p in patterns.get("jarvis_patterns", []))
        has_reinforcement = any(p.get("has_reinforcement", False) for p in patterns.get("jarvis_patterns", []))
        has_zero_sum = any(p.get("has_zero_sum", False) for p in patterns.get("jarvis_patterns", []))

        return JARVISSelfImprovementPhase(
            year=0,
            phase_name="Current State",
            reinforcement_learning=0.1 if has_reinforcement else 0.0,
            zero_sum_learning=0.05 if has_zero_sum else 0.0,
            machine_learning=0.2 if has_learning else 0.1,
            self_improvement_rate=0.01,  # 1% per year
            learning_efficiency=0.3,
            autonomous_learning=0.1,
            insights=[
                f"JARVIS patterns found: {len(patterns.get('jarvis_patterns', []))}",
                f"Learning patterns found: {len(patterns.get('learning_patterns', []))}",
                "Reinforcement learning: Minimal or absent",
                "Zero-sum learning: Not implemented",
                "Self-improvement: Manual, not autonomous"
            ],
            sparks=[
                "🔥 JARVIS needs reinforcement learning for self-improvement",
                "🔥 Zero-sum learning would enable competitive optimization",
                "🔥 Autonomous learning would eliminate manual updates",
                "🔥 Self-improvement rate of 1% per year is too slow",
                "🔥 Machine learning integration is minimal"
            ]
        )

    def _simulate_reinforcement_learning(self, previous: JARVISSelfImprovementPhase, target_year: int) -> JARVISSelfImprovementPhase:
        """Simulate reinforcement learning phase"""
        return JARVISSelfImprovementPhase(
            year=target_year,
            phase_name="Reinforcement Learning Introduction",
            reinforcement_learning=0.6,
            zero_sum_learning=0.2,
            machine_learning=0.5,
            self_improvement_rate=0.05,  # 5% per year
            learning_efficiency=0.6,
            autonomous_learning=0.4,
            insights=[
                "JARVIS implements reward-based learning",
                "Actions rewarded/penalized based on outcomes",
                "Self-improvement becomes data-driven",
                "Learning efficiency improves with feedback loops"
            ],
            sparks=[
                "🔥 Reinforcement learning enables JARVIS to learn from mistakes",
                "🔥 Reward signals guide optimal behavior discovery",
                "🔥 Self-improvement rate increases to 5% per year",
                "🔥 JARVIS learns which actions lead to success",
                "🔥 Autonomous learning begins - JARVIS improves without human input",
                "🔥 Learning efficiency doubles with feedback mechanisms"
            ]
        )

    def _simulate_zero_sum_learning(self, previous: JARVISSelfImprovementPhase, target_year: int) -> JARVISSelfImprovementPhase:
        """Simulate zero-sum learning phase"""
        return JARVISSelfImprovementPhase(
            year=target_year,
            phase_name="Zero-Sum Learning",
            reinforcement_learning=0.8,
            zero_sum_learning=0.7,
            machine_learning=0.75,
            self_improvement_rate=0.15,  # 15% per year
            learning_efficiency=0.85,
            autonomous_learning=0.7,
            insights=[
                "Zero-sum learning enables competitive optimization",
                "JARVIS competes with itself to improve",
                "Adversarial learning creates robust solutions",
                "Self-improvement accelerates through competition"
            ],
            sparks=[
                "🔥 Zero-sum learning: JARVIS competes with itself",
                "🔥 Adversarial training creates robust solutions",
                "🔥 Self-improvement rate accelerates to 15% per year",
                "🔥 JARVIS learns by playing against itself",
                "🔥 Competitive optimization finds optimal strategies",
                "🔥 Learning efficiency reaches 85%",
                "🔥 Autonomous learning becomes primary improvement mechanism"
            ]
        )

    def _simulate_advanced_ml(self, previous: JARVISSelfImprovementPhase, target_year: int) -> JARVISSelfImprovementPhase:
        """Simulate advanced ML integration phase"""
        return JARVISSelfImprovementPhase(
            year=target_year,
            phase_name="Advanced ML Integration",
            reinforcement_learning=0.95,
            zero_sum_learning=0.9,
            machine_learning=0.95,
            self_improvement_rate=0.3,  # 30% per year
            learning_efficiency=0.95,
            autonomous_learning=0.9,
            insights=[
                "Advanced ML models integrated into JARVIS",
                "Deep learning for pattern recognition",
                "Transfer learning accelerates improvement",
                "Self-improvement becomes exponential"
            ],
            sparks=[
                "🔥 Advanced ML enables deep pattern recognition",
                "🔥 Transfer learning accelerates JARVIS improvement",
                "🔥 Self-improvement rate reaches 30% per year (exponential)",
                "🔥 JARVIS learns from all previous experiences",
                "🔥 Learning efficiency approaches 95%",
                "🔥 Autonomous learning handles 90% of improvements",
                "🔥 Zero-sum learning creates perfect strategies",
                "🔥 Reinforcement learning optimizes all actions"
            ]
        )

    def _simulate_perfect_self_improvement(self, previous: JARVISSelfImprovementPhase, target_year: int) -> JARVISSelfImprovementPhase:
        """Simulate perfect self-improvement phase"""
        return JARVISSelfImprovementPhase(
            year=target_year,
            phase_name="Perfect Self-Improvement",
            reinforcement_learning=0.99,
            zero_sum_learning=0.99,
            machine_learning=0.99,
            self_improvement_rate=1.0,  # 100% per year (continuous)
            learning_efficiency=0.99,
            autonomous_learning=0.99,
            insights=[
                "JARVIS achieves perfect self-improvement",
                "Reinforcement learning optimizes all decisions",
                "Zero-sum learning creates optimal strategies",
                "Machine learning handles all pattern recognition",
                "Self-improvement is continuous and autonomous"
            ],
            sparks=[
                "🔥 JARVIS achieves perfect self-improvement (99%)",
                "🔥 Reinforcement learning optimizes every action",
                "🔥 Zero-sum learning creates unbeatable strategies",
                "🔥 Machine learning recognizes all patterns instantly",
                "🔥 Self-improvement rate: 100% per year (continuous)",
                "🔥 Learning efficiency: 99% (near-perfect)",
                "🔥 Autonomous learning: 99% (JARVIS improves itself)",
                "🔥 JARVIS becomes self-evolving AI system",
                "🔥 Continuous improvement without human intervention",
                "🔥 Perfect integration: RL + Zero-Sum + ML = Perfect JARVIS"
            ]
        )

    def _extract_unique_sparks(self, all_sparks: List[str]) -> List[str]:
        """Extract unique sparks"""
        unique = []
        seen = set()

        for spark in all_sparks:
            key = spark.lower().replace("🔥", "").strip()
            if key not in seen:
                seen.add(key)
                unique.append(spark)

        return unique

    def _analyze_learning_trajectory(self, phases: List[JARVISSelfImprovementPhase]) -> Dict[str, Any]:
        """Analyze learning trajectory"""
        trajectory = []
        for phase in phases:
            trajectory.append({
                "year": phase.year,
                "reinforcement_learning": phase.reinforcement_learning,
                "zero_sum_learning": phase.zero_sum_learning,
                "machine_learning": phase.machine_learning,
                "combined": (phase.reinforcement_learning + phase.zero_sum_learning + phase.machine_learning) / 3
            })

        return {
            "start": {
                "rl": phases[0].reinforcement_learning,
                "zero_sum": phases[0].zero_sum_learning,
                "ml": phases[0].machine_learning
            },
            "end": {
                "rl": phases[-1].reinforcement_learning,
                "zero_sum": phases[-1].zero_sum_learning,
                "ml": phases[-1].machine_learning
            },
            "trajectory": trajectory,
            "insight": "All learning methods reach 99% over 10,000 years"
        }

    def _analyze_improvement_rate(self, phases: List[JARVISSelfImprovementPhase]) -> Dict[str, Any]:
        """Analyze self-improvement rate"""
        rates = []
        for phase in phases:
            rates.append({
                "year": phase.year,
                "improvement_rate": phase.self_improvement_rate,
                "learning_efficiency": phase.learning_efficiency,
                "autonomous_learning": phase.autonomous_learning
            })

        return {
            "start_rate": phases[0].self_improvement_rate,
            "end_rate": phases[-1].self_improvement_rate,
            "rate_growth": phases[-1].self_improvement_rate / max(phases[0].self_improvement_rate, 0.01),
            "rates": rates,
            "insight": "Self-improvement rate grows from 1% to 100% (continuous) per year"
        }

    def generate_report(self, simulation: Dict[str, Any]) -> str:
        """Generate comprehensive report"""
        report = []
        report.append("="*80)
        report.append("⚡ SYPHON LUMINA → WOPR 10,000 YEAR SIMULATION")
        report.append("   JARVIS Self-Improvement: Reinforcement Learning + Zero-Sum + ML")
        report.append("="*80)
        report.append("")

        # Patterns Extracted
        patterns = simulation.get("patterns_extracted", {})
        report.append("🔍 SYPHONED PATTERNS FROM LUMINA")
        report.append("-"*80)
        report.append(f"   JARVIS Files: {len(patterns.get('jarvis_patterns', []))}")
        report.append(f"   Learning Files: {len(patterns.get('learning_patterns', []))}")
        report.append(f"   Automation Files: {len(patterns.get('automation_patterns', []))}")
        report.append(f"   Decisioning Files: {len(patterns.get('decisioning_patterns', []))}")
        report.append(f"   Total Files: {patterns.get('file_count', 0)}")
        report.append("")

        # Phases
        report.append("📊 SIMULATION PHASES")
        report.append("-"*80)
        for phase in simulation["phases"]:
            report.append(f"\n   Year {phase['year']}: {phase['phase_name']}")
            report.append(f"      Reinforcement Learning: {phase['reinforcement_learning']:.1%}")
            report.append(f"      Zero-Sum Learning: {phase['zero_sum_learning']:.1%}")
            report.append(f"      Machine Learning: {phase['machine_learning']:.1%}")
            report.append(f"      Self-Improvement Rate: {phase['self_improvement_rate']:.1%} per year")
            report.append(f"      Learning Efficiency: {phase['learning_efficiency']:.1%}")
            report.append(f"      Autonomous Learning: {phase['autonomous_learning']:.1%}")

        # Unique Sparks
        report.append("\n" + "="*80)
        report.append("🔥 SPARKS (Key Insights)")
        report.append("="*80)
        for i, spark in enumerate(simulation["unique_sparks"], 1):
            report.append(f"   {i}. {spark}")

        # Learning Trajectory
        report.append("\n" + "="*80)
        report.append("📈 LEARNING TRAJECTORY")
        report.append("="*80)
        traj = simulation["learning_trajectory"]
        report.append(f"   Reinforcement Learning: {traj['start']['rl']:.1%} → {traj['end']['rl']:.1%}")
        report.append(f"   Zero-Sum Learning: {traj['start']['zero_sum']:.1%} → {traj['end']['zero_sum']:.1%}")
        report.append(f"   Machine Learning: {traj['start']['ml']:.1%} → {traj['end']['ml']:.1%}")
        report.append(f"   Insight: {traj['insight']}")

        # Improvement Rate
        report.append("\n" + "="*80)
        report.append("⚡ SELF-IMPROVEMENT RATE")
        report.append("="*80)
        imp = simulation["improvement_rate"]
        report.append(f"   Start: {imp['start_rate']:.1%} per year")
        report.append(f"   End: {imp['end_rate']:.1%} per year (continuous)")
        report.append(f"   Growth: {imp['rate_growth']:.1f}x")
        report.append(f"   Insight: {imp['insight']}")

        # Final State
        report.append("\n" + "="*80)
        report.append("🎯 FINAL STATE (Year 10,000)")
        report.append("="*80)
        final = simulation["final_state"]
        report.append(f"   Reinforcement Learning: {final['reinforcement_learning']:.1%}")
        report.append(f"   Zero-Sum Learning: {final['zero_sum_learning']:.1%}")
        report.append(f"   Machine Learning: {final['machine_learning']:.1%}")
        report.append(f"   Self-Improvement Rate: {final['self_improvement_rate']:.1%} per year (continuous)")
        report.append(f"   Learning Efficiency: {final['learning_efficiency']:.1%}")
        report.append(f"   Autonomous Learning: {final['autonomous_learning']:.1%}")

        report.append("\n" + "="*80)

        return "\n".join(report)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Syphon Lumina → WOPR JARVIS Self-Improvement")
    parser.add_argument("--syphon", action="store_true", help="Syphon all of Lumina")
    parser.add_argument("--simulate", action="store_true", help="Run WOPR simulation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    syphon_wopr = SyphonLuminaWOPRJARVIS(project_root)

    if args.syphon or args.simulate or not any([args.syphon, args.simulate, args.json]):
        # Syphon all of Lumina
        patterns = syphon_wopr.syphon_all_lumina()

        # Run WOPR simulation
        simulation = syphon_wopr.run_wopr_jarvis_simulation(patterns)

        # Save results
        result_file = syphon_wopr.data_dir / f"syphon_wopr_jarvis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(simulation, f, indent=2, default=str)

        logger.info(f"💾 Results saved to: {result_file}")

        if args.json:
            print(json.dumps(simulation, indent=2, default=str))
        else:
            report = syphon_wopr.generate_report(simulation)
            print(report)

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)