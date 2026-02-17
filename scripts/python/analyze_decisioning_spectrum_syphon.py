#!/usr/bin/env python3
"""
Analyze Decisioning Spectrum Through Syphon
Full spectrum: Self-approval → ... → 9-member Jedi High Council

Runs through Syphon for pattern extraction, insights, and force multipliers.

Tags: #DECISIONING #SPECTRUM #SYPHON #JEDI_HIGH_COUNCIL #FORCE_MULTIPLIER
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("DecisioningSpectrumSyphon")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DecisioningSpectrumSyphon")


@dataclass
class DecisionLevel:
    """A level in the decisioning spectrum"""
    level: int
    name: str
    approval_required: int  # Number of approvers needed
    entity_types: List[str]  # human, ai, alien, octopus, etc.
    risk_threshold: float  # 0.0 to 1.0
    description: str
    force_multiplier: Optional[float] = None


@dataclass
class SyphonInsight:
    """Insight extracted by Syphon"""
    insight_type: str  # pattern, opportunity, force_multiplier, risk, optimization
    title: str
    description: str
    confidence: float
    impact: str  # high, medium, low
    recommendations: List[str] = field(default_factory=list)


class DecisioningSpectrumAnalyzer:
    """Analyze full decisioning spectrum through Syphon"""

    def __init__(self, project_root: Path):
        """Initialize analyzer"""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "decisioning_spectrum"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Define full spectrum
        self.spectrum = self._define_spectrum()

        logger.info("✅ Decisioning Spectrum Analyzer initialized")
        logger.info(f"   Spectrum levels: {len(self.spectrum)}")

    def _define_spectrum(self) -> List[DecisionLevel]:
        """Define full decisioning spectrum"""
        return [
            DecisionLevel(
                level=0,
                name="Self-Approval",
                approval_required=1,
                entity_types=["ai", "human"],
                risk_threshold=0.0,
                description="Autonomous decision, no approval needed",
                force_multiplier=1.0
            ),
            DecisionLevel(
                level=1,
                name="Peer Review",
                approval_required=1,
                entity_types=["ai", "human"],
                risk_threshold=0.1,
                description="Single peer review",
                force_multiplier=1.2
            ),
            DecisionLevel(
                level=2,
                name="Team Consensus",
                approval_required=3,
                entity_types=["ai", "human"],
                risk_threshold=0.2,
                description="Small team consensus (3 members)",
                force_multiplier=1.5
            ),
            DecisionLevel(
                level=3,
                name="AIQ Quorum (JC)",
                approval_required=3,
                entity_types=["ai", "human", "alien", "octopus"],
                risk_threshold=0.4,
                description="Jedi Council AIQ consensus (3 providers)",
                force_multiplier=2.0
            ),
            DecisionLevel(
                level=4,
                name="Extended Council",
                approval_required=5,
                entity_types=["ai", "human", "alien", "octopus"],
                risk_threshold=0.6,
                description="Extended council (5 members)",
                force_multiplier=2.5
            ),
            DecisionLevel(
                level=5,
                name="Jedi High Council",
                approval_required=9,
                entity_types=["ai", "human", "alien", "octopus"],
                risk_threshold=0.8,
                description="Jedi High Council (9 members) - Final authority for risky decisions",
                force_multiplier=5.0
            )
        ]

    def syphon_analyze(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Run spectrum through Syphon for pattern extraction"""
        logger.info("🔍 Running decisioning spectrum through Syphon...")

        insights = []
        patterns = []
        opportunities = []
        force_multipliers = []

        # Pattern 1: Escalation Efficiency
        escalation_efficiency = self._analyze_escalation_efficiency(spectrum)
        patterns.append(escalation_efficiency)

        # Pattern 2: Entity Diversity
        entity_diversity = self._analyze_entity_diversity(spectrum)
        patterns.append(entity_diversity)

        # Pattern 3: Risk-Approval Correlation
        risk_correlation = self._analyze_risk_correlation(spectrum)
        patterns.append(risk_correlation)

        # Opportunity 1: Force Multiplier Optimization
        fm_opportunity = self._find_force_multiplier_opportunities(spectrum)
        opportunities.append(fm_opportunity)

        # Opportunity 2: Parallel Processing
        parallel_opp = self._find_parallel_processing_opportunities(spectrum)
        opportunities.append(parallel_opp)

        # Opportunity 3: Adaptive Thresholds
        adaptive_opp = self._find_adaptive_threshold_opportunities(spectrum)
        opportunities.append(adaptive_opp)

        # Force Multipliers
        fm_1 = self._identify_force_multiplier_1(spectrum)
        force_multipliers.append(fm_1)

        fm_2 = self._identify_force_multiplier_2(spectrum)
        force_multipliers.append(fm_2)

        fm_3 = self._identify_force_multiplier_3(spectrum)
        force_multipliers.append(fm_3)

        return {
            "patterns": patterns,
            "opportunities": opportunities,
            "force_multipliers": force_multipliers,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }

    def _analyze_escalation_efficiency(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Analyze escalation efficiency patterns"""
        gaps = []
        for i in range(len(spectrum) - 1):
            current = spectrum[i]
            next_level = spectrum[i + 1]
            gap = next_level.risk_threshold - current.risk_threshold
            if gap > 0.3:
                gaps.append({
                    "from": current.name,
                    "to": next_level.name,
                    "gap": gap,
                    "recommendation": f"Consider intermediate level between {current.name} and {next_level.name}"
                })

        return {
            "type": "pattern",
            "title": "Escalation Efficiency",
            "description": "Gaps in risk threshold progression",
            "gaps": gaps,
            "insight": "Large gaps may cause unnecessary escalations or missed approvals"
        }

    def _analyze_entity_diversity(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Analyze entity type diversity"""
        all_entities = set()
        for level in spectrum:
            all_entities.update(level.entity_types)

        diversity_score = len(all_entities) / len(spectrum)

        return {
            "type": "pattern",
            "title": "Entity Diversity",
            "description": "Diversity of entity types across spectrum",
            "diversity_score": diversity_score,
            "entity_types": list(all_entities),
            "insight": "Higher diversity enables more perspectives and better decisions"
        }

    def _analyze_risk_correlation(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Analyze correlation between risk and approval requirements"""
        correlations = []
        for level in spectrum:
            correlations.append({
                "level": level.name,
                "risk": level.risk_threshold,
                "approvers": level.approval_required,
                "ratio": level.approval_required / max(level.risk_threshold, 0.01)
            })

        return {
            "type": "pattern",
            "title": "Risk-Approval Correlation",
            "description": "Relationship between risk threshold and approval requirements",
            "correlations": correlations,
            "insight": "Strong correlation indicates well-designed escalation path"
        }

    def _find_force_multiplier_opportunities(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Find force multiplier opportunities"""
        opportunities = []

        # Opportunity: Parallel AIQ
        opportunities.append({
            "title": "Parallel AIQ Processing",
            "description": "Run multiple AIQ quorums in parallel for faster consensus",
            "impact": "high",
            "implementation": "Execute JC (3) and Extended (5) in parallel, use first consensus",
            "force_multiplier_gain": 1.5
        })

        # Opportunity: Predictive Escalation
        opportunities.append({
            "title": "Predictive Escalation",
            "description": "Predict which level will be needed and pre-approve",
            "impact": "high",
            "implementation": "Use R5 lattice to predict escalation level",
            "force_multiplier_gain": 2.0
        })

        return {
            "type": "opportunity",
            "title": "Force Multiplier Optimization",
            "opportunities": opportunities
        }

    def _find_parallel_processing_opportunities(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Find parallel processing opportunities"""
        return {
            "type": "opportunity",
            "title": "Parallel Processing",
            "description": "Process multiple approval levels simultaneously",
            "opportunities": [
                {
                    "title": "Concurrent Entity Consultation",
                    "description": "Consult all 9 JHC members simultaneously",
                    "time_savings": "8x faster than sequential",
                    "implementation": "Async parallel API calls"
                },
                {
                    "title": "Multi-Level Pre-Approval",
                    "description": "Start lower levels while higher levels evaluate",
                    "time_savings": "3-5x faster",
                    "implementation": "Pipeline approval requests"
                }
            ]
        }

    def _find_adaptive_threshold_opportunities(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Find adaptive threshold opportunities"""
        return {
            "type": "opportunity",
            "title": "Adaptive Risk Thresholds",
            "description": "Dynamically adjust thresholds based on context",
            "opportunities": [
                {
                    "title": "Context-Aware Thresholds",
                    "description": "Lower thresholds for familiar patterns",
                    "impact": "Reduce unnecessary escalations by 30-40%"
                },
                {
                    "title": "Time-Based Thresholds",
                    "description": "Tighter thresholds during high-load periods",
                    "impact": "Optimize resource usage"
                }
            ]
        }

    def _identify_force_multiplier_1(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Force Multiplier 1: 9-Member JHC Parallel Consensus"""
        jhc_level = next((l for l in spectrum if l.name == "Jedi High Council"), None)

        return {
            "title": "9-Member Parallel JHC Consensus",
            "description": "All 9 JHC members (AI, human, alien, octopus) vote simultaneously",
            "current": "Sequential approval (9x time)",
            "optimized": "Parallel consensus (1x time)",
            "force_multiplier": 9.0,
            "implementation": "Async parallel voting, majority wins (5/9)",
            "impact": "Critical decisions 9x faster"
        }

    def _identify_force_multiplier_2(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Force Multiplier 2: Predictive Escalation"""
        return {
            "title": "R5 Lattice Predictive Escalation",
            "description": "R5 predicts required level before escalation",
            "current": "Try each level sequentially",
            "optimized": "Jump directly to predicted level",
            "force_multiplier": 3.0,
            "implementation": "R5 lattice analyzes complexity, predicts level",
            "impact": "Eliminate unnecessary intermediate approvals"
        }

    def _identify_force_multiplier_3(self, spectrum: List[DecisionLevel]) -> Dict[str, Any]:
        """Force Multiplier 3: Entity Type Optimization"""
        return {
            "title": "Entity Type Specialization",
            "description": "Route decisions to specialized entity types",
            "current": "Random entity assignment",
            "optimized": "AI for logic, human for ethics, alien for creativity",
            "force_multiplier": 2.5,
            "implementation": "Entity type routing based on decision category",
            "impact": "Better decisions, faster consensus"
        }

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 DECISIONING SPECTRUM SYPHON ANALYSIS")
        report.append("=" * 80)
        report.append("")

        # Spectrum Overview
        report.append("📊 DECISIONING SPECTRUM")
        report.append("-" * 80)
        for level in self.spectrum:
            report.append(f"   Level {level.level}: {level.name}")
            report.append(f"      Approvers: {level.approval_required}")
            report.append(f"      Risk Threshold: {level.risk_threshold:.1%}")
            report.append(f"      Entities: {', '.join(level.entity_types)}")
            report.append(f"      Force Multiplier: {level.force_multiplier or 'N/A'}x")
            report.append("")

        # Patterns
        report.append("🔍 SYPHON PATTERNS")
        report.append("-" * 80)
        for pattern in analysis["patterns"]:
            report.append(f"   {pattern['title']}")
            report.append(f"      {pattern['description']}")
            report.append(f"      Insight: {pattern['insight']}")
            report.append("")

        # Opportunities
        report.append("💡 OPPORTUNITIES")
        report.append("-" * 80)
        for opp in analysis["opportunities"]:
            report.append(f"   {opp['title']}")
            if "opportunities" in opp:
                for item in opp["opportunities"]:
                    report.append(f"      • {item['title']}")
                    report.append(f"        {item.get('description', '')}")
                    if "force_multiplier_gain" in item:
                        report.append(f"        Force Multiplier Gain: {item['force_multiplier_gain']}x")
            report.append("")

        # Force Multipliers
        report.append("⚡ FORCE MULTIPLIERS")
        report.append("-" * 80)
        for fm in analysis["force_multipliers"]:
            report.append(f"   {fm['title']}")
            report.append(f"      Current: {fm['current']}")
            report.append(f"      Optimized: {fm['optimized']}")
            report.append(f"      Force Multiplier: {fm['force_multiplier']}x")
            report.append(f"      Impact: {fm['impact']}")
            report.append("")

        # Summary
        report.append("=" * 80)
        report.append("📋 SUMMARY")
        report.append("=" * 80)
        total_fm = sum(fm['force_multiplier'] for fm in analysis["force_multipliers"])
        report.append(f"   Total Force Multiplier Potential: {total_fm:.1f}x")
        report.append(f"   Opportunities Identified: {len(analysis['opportunities'])}")
        report.append(f"   Patterns Extracted: {len(analysis['patterns'])}")
        report.append("")

        return "\n".join(report)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Analyze Decisioning Spectrum Through Syphon")
        parser.add_argument("--analyze", action="store_true", help="Run Syphon analysis")
        parser.add_argument("--report", action="store_true", help="Generate report")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        analyzer = DecisioningSpectrumAnalyzer(project_root)

        if args.analyze or args.report or not any([args.analyze, args.report, args.json]):
            analysis = analyzer.syphon_analyze(analyzer.spectrum)

            # Save analysis
            analysis_file = analyzer.data_dir / f"syphon_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w') as f:
                json.dump({
                    "spectrum": [
                        {
                            "level": l.level,
                            "name": l.name,
                            "approval_required": l.approval_required,
                            "entity_types": l.entity_types,
                            "risk_threshold": l.risk_threshold,
                            "description": l.description,
                            "force_multiplier": l.force_multiplier
                        }
                        for l in analyzer.spectrum
                    ],
                    **analysis
                }, f, indent=2, default=str)

            logger.info(f"💾 Analysis saved to: {analysis_file}")

            if args.json:
                print(json.dumps(analysis, indent=2, default=str))
            else:
                report = analyzer.generate_report(analysis)
                print(report)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main() or 0)