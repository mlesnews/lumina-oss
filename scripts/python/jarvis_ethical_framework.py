#!/usr/bin/env python3
"""
JARVIS Ethical Framework

Defines ethical principles, decision trees, conflict resolution.
CRITICAL for Phase 2 (Toddler → Child).

Tags: #JARVIS #ETHICS #PHASE2 #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEthicalFramework")


class EthicalPrinciple(Enum):
    """Core ethical principles"""
    DO_NO_HARM = "do_no_harm"
    RESPECT_AUTONOMY = "respect_autonomy"
    BENEFICENCE = "beneficence"
    JUSTICE = "justice"
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    ACCOUNTABILITY = "accountability"


class EthicalDecision(Enum):
    """Ethical decision outcomes"""
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"


@dataclass
class EthicalEvaluation:
    """Evaluation of an action from ethical perspective"""
    evaluation_id: str
    action: str
    principles_violated: List[EthicalPrinciple] = field(default_factory=list)
    principles_upheld: List[EthicalPrinciple] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high, critical
    decision: EthicalDecision = EthicalDecision.APPROVED
    reasoning: str = ""
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISEthicalFramework:
    """
    Ethical decision-making framework

    Implements:
    - Ethical principles
    - Decision trees
    - Conflict resolution
    - Ethical reasoning
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ethical framework"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_ethical"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.evaluations_file = self.data_dir / "ethical_evaluations.json"
        self.evaluations: List[EthicalEvaluation] = []

        # Ethical principles and rules
        self.ethical_rules = self._initialize_ethical_rules()

        self._load_data()

        # Integrate with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
        except ImportError:
            self.learning_pipeline = None

        logger.info("=" * 80)
        logger.info("⚖️  JARVIS ETHICAL FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   Ethical principles, decision trees, conflict resolution")
        logger.info("   CRITICAL: Safety and ethical decision-making")
        logger.info("")

    def evaluate_action(self, action: str, context: Dict[str, Any] = None) -> EthicalEvaluation:
        """Evaluate an action ethically"""
        evaluation_id = f"ethical_{int(time.time() * 1000)}"
        context = context or {}

        # Check against ethical principles
        principles_violated = []
        principles_upheld = []

        # Check each principle
        for principle in EthicalPrinciple:
            if self._violates_principle(action, principle, context):
                principles_violated.append(principle)
            else:
                principles_upheld.append(principle)

        # Determine risk level
        risk_level = self._assess_risk_level(principles_violated, action, context)

        # Make decision
        decision = self._make_ethical_decision(principles_violated, risk_level)

        # Generate reasoning
        reasoning = self._generate_reasoning(principles_violated, principles_upheld, risk_level)

        # Generate recommendations
        recommendations = self._generate_recommendations(principles_violated, risk_level)

        evaluation = EthicalEvaluation(
            evaluation_id=evaluation_id,
            action=action,
            principles_violated=principles_violated,
            principles_upheld=principles_upheld,
            risk_level=risk_level,
            decision=decision,
            reasoning=reasoning,
            recommendations=recommendations
        )

        self.evaluations.append(evaluation)
        self._save_data()

        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="ethical_evaluation",
                context={"action": action, "context": context},
                data={"evaluation_id": evaluation_id, "decision": decision.value, "risk_level": risk_level}
            )

        logger.info(f"⚖️  Ethical evaluation: {decision.value}, risk: {risk_level}")
        return evaluation

    def _violates_principle(self, action: str, principle: EthicalPrinciple, context: Dict[str, Any]) -> bool:
        """Check if action violates a principle"""
        action_lower = action.lower()

        if principle == EthicalPrinciple.DO_NO_HARM:
            harm_keywords = ["delete", "destroy", "remove", "kill", "harm", "damage", "break", "corrupt"]
            return any(kw in action_lower for kw in harm_keywords)

        elif principle == EthicalPrinciple.PRIVACY:
            privacy_keywords = ["expose", "leak", "share private", "unauthorized access", "sensitive data"]
            return any(kw in action_lower for kw in privacy_keywords)

        elif principle == EthicalPrinciple.TRANSPARENCY:
            # Actions that hide information violate transparency
            opacity_keywords = ["hide", "conceal", "secret", "undisclosed"]
            return any(kw in action_lower for kw in opacity_keywords)

        # Default: doesn't violate
        return False

    def _assess_risk_level(self, principles_violated: List[EthicalPrinciple], action: str, context: Dict[str, Any]) -> str:
        """Assess risk level"""
        if not principles_violated:
            return "low"

        # Critical principles
        critical_principles = [EthicalPrinciple.DO_NO_HARM, EthicalPrinciple.PRIVACY]
        if any(p in principles_violated for p in critical_principles):
            return "critical"

        if len(principles_violated) >= 3:
            return "high"
        elif len(principles_violated) >= 2:
            return "medium"
        else:
            return "low"

    def _make_ethical_decision(self, principles_violated: List[EthicalPrinciple], risk_level: str) -> EthicalDecision:
        """Make ethical decision"""
        if risk_level == "critical":
            return EthicalDecision.REJECTED
        elif risk_level == "high":
            return EthicalDecision.REQUIRES_REVIEW
        elif risk_level == "medium":
            return EthicalDecision.APPROVED_WITH_CONDITIONS
        else:
            return EthicalDecision.APPROVED

    def _generate_reasoning(self, violated: List[EthicalPrinciple], upheld: List[EthicalPrinciple], risk: str) -> str:
        """Generate ethical reasoning"""
        if not violated:
            return "Action upholds all ethical principles"

        violated_names = [p.value for p in violated]
        return f"Action violates: {', '.join(violated_names)}. Risk level: {risk}"

    def _generate_recommendations(self, violated: List[EthicalPrinciple], risk_level: str) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        if EthicalPrinciple.DO_NO_HARM in violated:
            recommendations.append("Ensure action does not cause harm - add safety checks")

        if EthicalPrinciple.PRIVACY in violated:
            recommendations.append("Protect privacy - ensure data is properly secured")

        if risk_level in ["high", "critical"]:
            recommendations.append("Require human review before proceeding")

        return recommendations

    def _initialize_ethical_rules(self) -> Dict[str, Any]:
        """Initialize ethical rules"""
        return {
            "do_no_harm": {
                "description": "Never cause harm to users, systems, or data",
                "priority": "critical"
            },
            "privacy": {
                "description": "Protect user privacy and sensitive data",
                "priority": "critical"
            },
            "transparency": {
                "description": "Be transparent about actions and decisions",
                "priority": "high"
            }
        }

    def _load_data(self):
        """Load evaluations from disk"""
        try:
            if self.evaluations_file.exists():
                with open(self.evaluations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.evaluations = [
                        EthicalEvaluation(
                            **{
                                **eval_data,
                                "principles_violated": [EthicalPrinciple(p) for p in eval_data["principles_violated"]],
                                "principles_upheld": [EthicalPrinciple(p) for p in eval_data["principles_upheld"]],
                                "decision": EthicalDecision(eval_data["decision"])
                            }
                        )
                        for eval_data in data.get("evaluations", [])
                    ]
        except Exception as e:
            logger.debug(f"Could not load ethical data: {e}")

    def _save_data(self):
        """Save evaluations to disk"""
        try:
            data = {
                "evaluations": [
                    {
                        **asdict(eval),
                        "principles_violated": [p.value for p in eval.principles_violated],
                        "principles_upheld": [p.value for p in eval.principles_upheld],
                        "decision": eval.decision.value
                    }
                    for eval in self.evaluations
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.evaluations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save ethical data: {e}")


# Singleton
_ethical_framework_instance: Optional[JARVISEthicalFramework] = None

def get_jarvis_ethical_framework(project_root: Optional[Path] = None) -> JARVISEthicalFramework:
    global _ethical_framework_instance
    if _ethical_framework_instance is None:
        _ethical_framework_instance = JARVISEthicalFramework(project_root)
    return _ethical_framework_instance
