#!/usr/bin/env python3
"""
Decision Panel System - #5-#7-#9 JUDGES + CLOUD-AI Matching

Decision-making panels consist of 5, 7, or 9 JUDGES plus CLOUD-AI matching,
depending on decision complexity. Panels evaluate decisions based on multiple
dimensions and match appropriate AI models to actorial digital personage models.

Tags: @JEDI-COUNCIL #DECISIONING #JUDGES #CLOUD-AI #PANELS
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

logger = get_logger("DecisionPanelSystem")


class PanelSize(Enum):
    """Decision Panel Sizes"""
    FIVE = 5
    SEVEN = 7
    NINE = 9


class DecisionComplexity(Enum):
    """Decision Complexity Levels"""
    STANDARD = "standard"
    COMPLEX = "complex"
    CRITICAL = "critical"


@dataclass
class JudgeEvaluation:
    """Judge evaluation result"""
    judge_type: str
    score: float  # 0-1.0
    reasoning: str
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CloudAIMatch:
    """CLOUD-AI model matching result"""
    matched_model: str
    matching_rationale: str
    personality_alignment: str  # high, medium, low
    boons_banes_considered: bool
    complexity_match: bool
    trait_matching: Dict[str, float] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PanelDecision:
    """Decision from a panel"""
    panel_size: PanelSize
    complexity: DecisionComplexity
    question: str
    category: str
    judges: List[JudgeEvaluation]
    cloud_ai_match: CloudAIMatch
    consensus_score: float
    recommendation: str
    action_items: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["panel_size"] = self.panel_size.value
        data["complexity"] = self.complexity.value
        data["judges"] = [j.to_dict() for j in self.judges]
        data["cloud_ai_match"] = self.cloud_ai_match.to_dict()
        return data


class DecisionPanelSystem:
    """
    Decision Panel System - #5-#7-#9 JUDGES + CLOUD-AI Matching

    Creates decision-making panels with JUDGES evaluations and CLOUD-AI
    model matching based on decision complexity and actorial digital
    personage model requirements.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Decision Panel System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("DecisionPanelSystem")

        # Load configuration
        self.config_dir = self.project_root / "config" / "jedi_council"
        self.config = self._load_config()

        # Judge types
        self.judge_types = [
            "technical_feasibility",
            "strategic_alignment",
            "risk_assessment",
            "ethical_considerations",
            "resource_requirements",
            "timeline_constraints",
            "stakeholder_impact",
            "long_term_viability",
            "innovation_potential"
        ]

        # CLOUD-AI models
        self.cloud_ai_models = [
            "gpt-4",
            "gpt-4-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "gemini-pro",
            "local_advanced_models"
        ]

        self.logger.info("⚖️ Decision Panel System initialized")
        self.logger.info(f"   Judge Types: {len(self.judge_types)}")
        self.logger.info(f"   CLOUD-AI Models: {len(self.cloud_ai_models)}")

    def _load_config(self) -> Dict[str, Any]:
        try:
            """Load panel configuration"""
            config_file = self.config_dir / "level_zero_council.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("decision_panels", {})
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def create_panel(self, question: str, category: str,
                     complexity: DecisionComplexity,
                     context: Optional[Dict[str, Any]] = None) -> PanelDecision:
        """
        Create decision panel based on complexity

        - Standard: #5 Panel (5 JUDGES + 1 CLOUD-AI)
        - Complex: #7 Panel (7 JUDGES + 1 CLOUD-AI)
        - Critical: #9 Panel (9 JUDGES + 1 CLOUD-AI)
        """
        self.logger.info(f"⚖️ Creating Decision Panel")
        self.logger.info(f"   Question: {question[:100]}...")
        self.logger.info(f"   Complexity: {complexity.value}")

        # Determine panel size
        panel_size_map = {
            DecisionComplexity.STANDARD: PanelSize.FIVE,
            DecisionComplexity.COMPLEX: PanelSize.SEVEN,
            DecisionComplexity.CRITICAL: PanelSize.NINE
        }
        panel_size = panel_size_map.get(complexity, PanelSize.FIVE)

        self.logger.info(f"   Panel Size: #{panel_size.value}")

        # Create judges
        judges = self._create_judges(question, category, panel_size.value, context)

        # Match CLOUD-AI
        cloud_ai_match = self._match_cloud_ai(question, category, complexity, context)

        # Calculate consensus
        consensus_score = self._calculate_consensus(judges)

        # Generate recommendation
        recommendation = self._generate_recommendation(judges, consensus_score)

        # Extract action items
        action_items = self._extract_action_items(judges)

        panel_decision = PanelDecision(
            panel_size=panel_size,
            complexity=complexity,
            question=question,
            category=category,
            judges=judges,
            cloud_ai_match=cloud_ai_match,
            consensus_score=consensus_score,
            recommendation=recommendation,
            action_items=action_items
        )

        self.logger.info(f"✅ Panel Decision Complete")
        self.logger.info(f"   Consensus Score: {consensus_score:.2f}")
        self.logger.info(f"   Recommendation: {recommendation}")

        return panel_decision

    def _create_judges(self, question: str, category: str,
                      panel_size: int, context: Optional[Dict[str, Any]]) -> List[JudgeEvaluation]:
        """Create JUDGES evaluations"""
        # Select judge types based on panel size
        selected_judges = self.judge_types[:panel_size]

        judges = []
        for judge_type in selected_judges:
            evaluation = self._evaluate_judge(judge_type, question, category, context)
            judges.append(evaluation)

        return judges

    def _evaluate_judge(self, judge_type: str, question: str,
                        category: str, context: Optional[Dict[str, Any]]) -> JudgeEvaluation:
        """Evaluate using a specific judge type"""
        # Judge-specific evaluation logic
        if judge_type == "technical_feasibility":
            score = self._evaluate_technical_feasibility(question, category, context)
            reasoning = "Technical feasibility assessment based on current capabilities and constraints"
            concerns = []
            recommendations = []

        elif judge_type == "strategic_alignment":
            score = self._evaluate_strategic_alignment(question, category, context)
            reasoning = "Strategic alignment with long-term goals and vision"
            concerns = []
            recommendations = []

        elif judge_type == "risk_assessment":
            score = self._evaluate_risk(question, category, context)
            reasoning = "Risk assessment considering potential negative outcomes"
            concerns = []
            recommendations = []

        elif judge_type == "ethical_considerations":
            score = self._evaluate_ethics(question, category, context)
            reasoning = "Ethical considerations and moral implications"
            concerns = []
            recommendations = []

        elif judge_type == "resource_requirements":
            score = self._evaluate_resources(question, category, context)
            reasoning = "Resource requirements assessment (time, cost, personnel)"
            concerns = []
            recommendations = []

        elif judge_type == "timeline_constraints":
            score = self._evaluate_timeline(question, category, context)
            reasoning = "Timeline constraints and feasibility assessment"
            concerns = []
            recommendations = []

        else:
            # Generic evaluation
            score = 0.75
            reasoning = f"{judge_type} evaluation: General assessment"
            concerns = []
            recommendations = []

        return JudgeEvaluation(
            judge_type=judge_type,
            score=score,
            reasoning=reasoning,
            concerns=concerns,
            recommendations=recommendations
        )

    def _evaluate_technical_feasibility(self, question: str, category: str,
                                       context: Optional[Dict[str, Any]]) -> float:
        """Evaluate technical feasibility"""
        # Placeholder - would use actual technical assessment
        return 0.85

    def _evaluate_strategic_alignment(self, question: str, category: str,
                                      context: Optional[Dict[str, Any]]) -> float:
        """Evaluate strategic alignment"""
        # Placeholder - would use actual strategic assessment
        return 0.80

    def _evaluate_risk(self, question: str, category: str,
                      context: Optional[Dict[str, Any]]) -> float:
        """Evaluate risk"""
        # Placeholder - would use actual risk assessment
        return 0.75

    def _evaluate_ethics(self, question: str, category: str,
                        context: Optional[Dict[str, Any]]) -> float:
        """Evaluate ethical considerations"""
        # Placeholder - would use actual ethical assessment
        return 0.90

    def _evaluate_resources(self, question: str, category: str,
                           context: Optional[Dict[str, Any]]) -> float:
        """Evaluate resource requirements"""
        # Placeholder - would use actual resource assessment
        return 0.70

    def _evaluate_timeline(self, question: str, category: str,
                          context: Optional[Dict[str, Any]]) -> float:
        """Evaluate timeline constraints"""
        # Placeholder - would use actual timeline assessment
        return 0.75

    def _match_cloud_ai(self, question: str, category: str,
                       complexity: DecisionComplexity,
                       context: Optional[Dict[str, Any]]) -> CloudAIMatch:
        """
        Match CLOUD-AI model to actorial digital personage model

        Matching based on:
        - Personality traits (BOONS/BANES)
        - Decision complexity
        - Required expertise
        - Model capabilities
        - Performance requirements
        """
        # Load avatar personality traits if available
        personality_traits = context.get("personality_traits", {}) if context else {}
        boons_banes = context.get("boons_banes", {}) if context else {}

        # Match model based on complexity and requirements
        if complexity == DecisionComplexity.CRITICAL:
            matched_model = "gpt-4"  # Highest capability
            personality_alignment = "high"
        elif complexity == DecisionComplexity.COMPLEX:
            matched_model = "claude-3-opus"  # High capability
            personality_alignment = "high"
        else:
            matched_model = "gpt-4-turbo"  # Standard capability
            personality_alignment = "medium"

        # Generate matching rationale
        rationale = f"Matched {matched_model} based on complexity ({complexity.value})"
        if personality_traits:
            rationale += f" and personality traits alignment"
        if boons_banes:
            rationale += f" with BOONS/BANES consideration"

        # Calculate trait matching scores
        trait_matching = {}
        if personality_traits:
            for trait, value in personality_traits.items():
                # Match trait to model capability
                trait_matching[trait] = min(value / 100.0, 1.0)

        return CloudAIMatch(
            matched_model=matched_model,
            matching_rationale=rationale,
            personality_alignment=personality_alignment,
            boons_banes_considered=bool(boons_banes),
            complexity_match=True,
            trait_matching=trait_matching
        )

    def _calculate_consensus(self, judges: List[JudgeEvaluation]) -> float:
        """Calculate consensus score from judges"""
        if not judges:
            return 0.0

        scores = [j.score for j in judges]
        return sum(scores) / len(scores)

    def _generate_recommendation(self, judges: List[JudgeEvaluation],
                                 consensus_score: float) -> str:
        """Generate panel recommendation"""
        if consensus_score >= 0.9:
            return "Strong consensus - Proceed with confidence"
        elif consensus_score >= 0.8:
            return "High consensus - Proceed with monitoring"
        elif consensus_score >= 0.7:
            return "Moderate consensus - Proceed with caution"
        elif consensus_score >= 0.6:
            return "Low consensus - Proceed with significant caution"
        else:
            return "Very low consensus - Require additional deliberation or escalation"

    def _extract_action_items(self, judges: List[JudgeEvaluation]) -> List[str]:
        """Extract action items from judges"""
        action_items = []
        for judge in judges:
            action_items.extend(judge.recommendations)
        return list(set(action_items))  # Remove duplicates


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Decision Panel System")
    parser.add_argument("--question", type=str, required=True, help="Decision question")
    parser.add_argument("--category", type=str, default="reasoning",
                       choices=["reasoning", "decisioning", "troubleshooting", "problem-solving"],
                       help="Category of question")
    parser.add_argument("--complexity", type=str, default="standard",
                       choices=["standard", "complex", "critical"],
                       help="Decision complexity")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    complexity_map = {
        "standard": DecisionComplexity.STANDARD,
        "complex": DecisionComplexity.COMPLEX,
        "critical": DecisionComplexity.CRITICAL
    }

    system = DecisionPanelSystem()
    panel_decision = system.create_panel(
        args.question,
        args.category,
        complexity_map[args.complexity]
    )

    if args.json:
        print(json.dumps(panel_decision.to_dict(), indent=2))
    else:
        print(f"\n⚖️ Decision Panel Result")
        print(f"   Panel Size: #{panel_decision.panel_size.value}")
        print(f"   Complexity: {panel_decision.complexity.value}")
        print(f"   Consensus Score: {panel_decision.consensus_score:.2f}")
        print(f"   Recommendation: {panel_decision.recommendation}")
        print(f"\n   Judges ({len(panel_decision.judges)}):")
        for judge in panel_decision.judges:
            print(f"     • {judge.judge_type}: {judge.score:.2f}")
            print(f"       {judge.reasoning[:80]}...")
        print(f"\n   CLOUD-AI Match:")
        print(f"     Model: {panel_decision.cloud_ai_match.matched_model}")
        print(f"     Alignment: {panel_decision.cloud_ai_match.personality_alignment}")
        print(f"     Rationale: {panel_decision.cloud_ai_match.matching_rationale}")
