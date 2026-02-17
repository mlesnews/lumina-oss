#!/usr/bin/env python3
"""
F4 Finger of God - Decision Framework

Roman Style Granular Focus that empowers to Point.

F4 = Fujita Scale F4 Tornado Classification ("Devastating" - 207-260 mph winds)
Like an F4 tornado, F4 decisions cut through ambiguity with devastating clarity,
unstoppable force, and leave no doubt about the direction.

Reference: Movie "Twister" - F4 tornado as central plot device, depicting the raw
fury of wind at full intensity, instilling tremendous respect for Nature's power.

All signs point towards YES or point towards NO - not Magic 8-Ball.
Some questions point to THINK (they exist to make you think).

Tags: #F4 #FINGER_OF_GOD #DECISION_FRAMEWORK #POINTING #ROMAN_STYLE #GRANULAR_FOCUS #TORNADO #TWISTER
@LUMINA @JARVIS @SYPHON
"""

from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("F4FingerOfGod")


class PointDirection(Enum):
    """F4 Pointing Directions"""
    YES = "yes"  # All signs point to YES
    NO = "no"  # All signs point to NO
    THINK = "think"  # Question exists to make you think (no definitive answer)


@dataclass
class Evidence:
    """Evidence gathered for decision"""
    facts: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LogicAnalysis:
    """Logic analysis for decision"""
    reasoning: List[str] = field(default_factory=list)
    principles_applied: List[str] = field(default_factory=list)
    logic_validated: bool = False
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class SignsAssessment:
    """Assessment of all signs"""
    signs_toward_yes: List[str] = field(default_factory=list)
    signs_toward_no: List[str] = field(default_factory=list)
    signs_toward_think: List[str] = field(default_factory=list)
    dominant_direction: Optional[PointDirection] = None
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class F4Decision:
    """F4 Finger of God Decision Result"""
    question: str
    evidence: Evidence
    logic: LogicAnalysis
    signs: SignsAssessment
    point: PointDirection
    authority: str = "F4_Finger_Of_God"
    granular_focus: List[str] = field(default_factory=list)
    roman_style: bool = True  # Decisive, authoritative, clear
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "question": self.question,
            "point": self.point.value,
            "evidence": {
                "facts": self.evidence.facts,
                "data": self.evidence.data,
                "sources": self.evidence.sources,
                "confidence": self.evidence.confidence
            },
            "logic": {
                "reasoning": self.logic.reasoning,
                "principles_applied": self.logic.principles_applied,
                "logic_validated": self.logic.logic_validated,
                "confidence": self.logic.confidence
            },
            "signs": {
                "toward_yes": self.signs.signs_toward_yes,
                "toward_no": self.signs.signs_toward_no,
                "toward_think": self.signs.signs_toward_think,
                "dominant_direction": self.signs.dominant_direction.value if self.signs.dominant_direction else None,
                "confidence": self.signs.confidence
            },
            "granular_focus": self.granular_focus,
            "roman_style": self.roman_style,
            "authority": self.authority,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class F4FingerOfGod:
    """
    F4 Finger of God - Decision Framework

    F4 = Fujita Scale F4 Tornado Classification ("Devastating" - 207-260 mph winds)
    Like an F4 tornado from the movie "Twister", F4 decisions cut through ambiguity
    with devastating clarity, unstoppable force, and leave no doubt about direction.

    Roman Style Granular Focus that empowers to Point.
    All signs point towards YES or point towards NO - not Magic 8-Ball.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize F4 Finger of God decision framework.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "f4_decisions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ F4 Finger of God initialized")

    def gather_evidence(
        self,
        facts: List[str],
        data: Dict[str, Any],
        sources: List[str],
        confidence: float = 0.0
    ) -> Evidence:
        """
        Gather evidence for decision.

        Args:
            facts: List of facts
            data: Data dictionary
            sources: List of sources
            confidence: Confidence level (0.0 to 1.0)

        Returns:
            Evidence object
        """
        evidence = Evidence(
            facts=facts,
            data=data,
            sources=sources,
            confidence=confidence
        )

        logger.debug(f"📊 Evidence gathered: {len(facts)} facts, {len(sources)} sources, confidence: {confidence:.2f}")
        return evidence

    def apply_logic(
        self,
        reasoning: List[str],
        principles: List[str],
        validate: bool = True
    ) -> LogicAnalysis:
        """
        Apply logic to decision.

        Args:
            reasoning: List of reasoning steps
            principles: List of principles applied
            validate: Whether logic is validated

        Returns:
            LogicAnalysis object
        """
        # Calculate confidence based on reasoning and validation
        confidence = 0.5  # Base confidence
        if validate:
            confidence += 0.3
        if len(reasoning) > 0:
            confidence += min(0.2, len(reasoning) * 0.05)

        logic = LogicAnalysis(
            reasoning=reasoning,
            principles_applied=principles,
            logic_validated=validate,
            confidence=min(1.0, confidence)
        )

        logger.debug(f"🧠 Logic applied: {len(reasoning)} steps, {len(principles)} principles, validated: {validate}")
        return logic

    def assess_signs(
        self,
        signs_toward_yes: List[str],
        signs_toward_no: List[str],
        signs_toward_think: Optional[List[str]] = None
    ) -> SignsAssessment:
        """
        Assess all signs to determine direction.

        Args:
            signs_toward_yes: Signs pointing to YES
            signs_toward_no: Signs pointing to NO
            signs_toward_think: Signs pointing to THINK (optional)

        Returns:
            SignsAssessment object
        """
        if signs_toward_think is None:
            signs_toward_think = []

        # Determine dominant direction
        yes_count = len(signs_toward_yes)
        no_count = len(signs_toward_no)
        think_count = len(signs_toward_think)

        # Calculate confidence
        total_signs = yes_count + no_count + think_count
        if total_signs == 0:
            confidence = 0.0
            dominant_direction = None
        else:
            max_count = max(yes_count, no_count, think_count)
            confidence = max_count / total_signs if total_signs > 0 else 0.0

            if think_count > 0 and think_count >= max(yes_count, no_count):
                dominant_direction = PointDirection.THINK
            elif yes_count > no_count:
                dominant_direction = PointDirection.YES
            elif no_count > yes_count:
                dominant_direction = PointDirection.NO
            else:
                # Tie - default to THINK if think signs exist, otherwise THINK
                dominant_direction = PointDirection.THINK

        signs = SignsAssessment(
            signs_toward_yes=signs_toward_yes,
            signs_toward_no=signs_toward_no,
            signs_toward_think=signs_toward_think,
            dominant_direction=dominant_direction,
            confidence=confidence
        )

        logger.debug(f"🔍 Signs assessed: {yes_count} YES, {no_count} NO, {think_count} THINK, dominant: {dominant_direction}")
        return signs

    def point(
        self,
        question: str,
        evidence: Evidence,
        logic: LogicAnalysis,
        signs: SignsAssessment,
        granular_focus: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> F4Decision:
        """
        Point with authority - Roman Style.

        Args:
            question: The question being decided
            evidence: Evidence gathered
            logic: Logic analysis
            signs: Signs assessment
            granular_focus: Granular focus points (optional)
            metadata: Additional metadata (optional)

        Returns:
            F4Decision with definitive point
        """
        # Determine point based on signs
        point = signs.dominant_direction

        # If no dominant direction, default to THINK
        if point is None:
            point = PointDirection.THINK

        # If signs point to THINK, but we have strong evidence/logic, reassess
        if point == PointDirection.THINK:
            # Check if we have enough evidence/logic to make a decision
            if evidence.confidence > 0.7 and logic.confidence > 0.7:
                # Reassess based on evidence and logic
                if len(signs.signs_toward_yes) > len(signs.signs_toward_no):
                    point = PointDirection.YES
                elif len(signs.signs_toward_no) > len(signs.signs_toward_yes):
                    point = PointDirection.NO
                # Otherwise stay at THINK

        if granular_focus is None:
            granular_focus = []

        if metadata is None:
            metadata = {}

        decision = F4Decision(
            question=question,
            evidence=evidence,
            logic=logic,
            signs=signs,
            point=point,
            granular_focus=granular_focus,
            metadata=metadata
        )

        # Save decision
        self._save_decision(decision)

        # Log decision
        point_symbol = "✅" if point == PointDirection.YES else "❌" if point == PointDirection.NO else "💭"
        logger.info(f"{point_symbol} F4 Points to {point.value.upper()}: {question}")

        return decision

    def decide(
        self,
        question: str,
        facts: List[str],
        data: Dict[str, Any],
        sources: List[str],
        reasoning: List[str],
        principles: List[str],
        signs_toward_yes: List[str],
        signs_toward_no: List[str],
        signs_toward_think: Optional[List[str]] = None,
        granular_focus: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> F4Decision:
        """
        Complete F4 decision process.

        Args:
            question: The question being decided
            facts: List of facts
            data: Data dictionary
            sources: List of sources
            reasoning: List of reasoning steps
            principles: List of principles applied
            signs_toward_yes: Signs pointing to YES
            signs_toward_no: Signs pointing to NO
            signs_toward_think: Signs pointing to THINK (optional)
            granular_focus: Granular focus points (optional)
            metadata: Additional metadata (optional)

        Returns:
            F4Decision with definitive point
        """
        # Step 1: Gather Evidence
        evidence = self.gather_evidence(
            facts=facts,
            data=data,
            sources=sources,
            confidence=min(1.0, len(facts) * 0.1 + len(sources) * 0.1)
        )

        # Step 2: Apply Logic
        logic = self.apply_logic(
            reasoning=reasoning,
            principles=principles,
            validate=True
        )

        # Step 3: Assess Signs
        signs = self.assess_signs(
            signs_toward_yes=signs_toward_yes,
            signs_toward_no=signs_toward_no,
            signs_toward_think=signs_toward_think
        )

        # Step 4: Point with Authority
        decision = self.point(
            question=question,
            evidence=evidence,
            logic=logic,
            signs=signs,
            granular_focus=granular_focus,
            metadata=metadata
        )

        return decision

    def _save_decision(self, decision: F4Decision) -> None:
        """Save decision to file"""
        try:
            timestamp_str = decision.timestamp.strftime("%Y%m%d_%H%M%S_%f")
            filename = f"f4_decision_{timestamp_str}.json"
            filepath = self.data_dir / filename

            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(decision.to_dict(), f, indent=2, ensure_ascii=False, default=str)

            logger.debug(f"💾 Decision saved: {filepath}")
        except Exception as e:
            logger.error(f"⚠️  Error saving decision: {e}", exc_info=True)


def main():
    """Example usage"""
    f4 = F4FingerOfGod()

    # Example 1: Technical Decision
    decision1 = f4.decide(
        question="Should we deploy this feature?",
        facts=[
            "All tests pass",
            "Code reviewed",
            "Documentation complete"
        ],
        data={"test_coverage": 0.95, "reviewers": 2},
        sources=["CI/CD", "Code Review", "Documentation"],
        reasoning=[
            "All quality gates passed",
            "No blocking issues found",
            "Deployment follows established process"
        ],
        principles=["Quality First", "Process Compliance"],
        signs_toward_yes=[
            "Tests pass",
            "Code reviewed",
            "Documentation complete",
            "No blocking issues"
        ],
        signs_toward_no=[],
        granular_focus=["Test coverage", "Code review", "Documentation"]
    )

    print(f"\n✅ Decision 1: {decision1.point.value.upper()}")
    print(f"   Question: {decision1.question}")

    # Example 2: Strategic Decision
    decision2 = f4.decide(
        question="Should we pursue this opportunity?",
        facts=[
            "Market analysis shows high risk",
            "Resources are limited",
            "Timeline is tight"
        ],
        data={"risk_score": 0.8, "resource_availability": 0.3},
        sources=["Market Analysis", "Resource Planning"],
        reasoning=[
            "Risk outweighs potential benefit",
            "Resources insufficient for success",
            "Timeline too aggressive"
        ],
        principles=["Risk Management", "Resource Efficiency"],
        signs_toward_yes=[],
        signs_toward_no=[
            "High risk",
            "Limited resources",
            "Tight timeline",
            "Risk > Benefit"
        ],
        granular_focus=["Risk assessment", "Resource availability", "Timeline"]
    )

    print(f"\n❌ Decision 2: {decision2.point.value.upper()}")
    print(f"   Question: {decision2.question}")

    # Example 3: Philosophical Question
    decision3 = f4.decide(
        question="What is the meaning of life?",
        facts=[],
        data={},
        sources=[],
        reasoning=[
            "No definitive answer exists",
            "Question designed for introspection"
        ],
        principles=["Philosophical Inquiry"],
        signs_toward_yes=[],
        signs_toward_no=[],
        signs_toward_think=[
            "No definitive answer",
            "Question exists to make you think",
            "Personal introspection required"
        ],
        granular_focus=["Philosophical inquiry", "Personal journey"]
    )

    print(f"\n💭 Decision 3: {decision3.point.value.upper()}")
    print(f"   Question: {decision3.question}")


if __name__ == "__main__":


    main()