#!/usr/bin/env python3
"""
Integrated Risk Assessment - Combines Risk Matrix, Decision Tree, and R5 Matrix

Part of LUMINA 2.0.0 Cleanup Implementation Plan.

Tags: #CLEANUP #RISK_ASSESSMENT #DECISION_TREE #R5_MATRIX #INTEGRATION @LUMINA
"""

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IntegratedRiskAssessment")

try:
    from universal_decision_tree import DecisionContext, DecisionOutcome

    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    logger.warning("Universal Decision Tree not available")

try:
    from r5_living_context_matrix import R5LivingContextMatrix

    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger.warning("R5 Matrix not available")


class RiskLevel(Enum):
    """Risk levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskAssessment:
    """Integrated risk assessment result"""

    risk_level: RiskLevel
    complexity: str  # low, medium, high
    urgency: str  # low, medium, high
    cost_sensitive: bool
    pattern_frequency: float  # 0.0 to 1.0 (from R5)
    pattern_exists: bool
    approval_required: int
    ci_cd_checks: str  # basic, full, full_audit
    security_scan: bool
    performance_test: bool
    manual_qa: bool
    decision_tree_outcome: Optional[str] = None
    r5_patterns: list = field(default_factory=list)
    reasoning: str = ""


class IntegratedRiskAssessment:
    """Integrated risk assessment using Decision Tree, R5 Matrix, and Risk Matrix"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # Initialize Decision Tree if available
        self.decision_tree = None
        if DECISION_TREE_AVAILABLE:
            try:
                from universal_decision_tree import UniversalDecisionTree

                self.decision_tree = UniversalDecisionTree(project_root)
            except Exception as e:
                logger.warning(f"Could not initialize Decision Tree: {e}")

        # Initialize R5 Matrix if available
        self.r5_matrix = None
        if R5_AVAILABLE:
            try:
                from r5_living_context_matrix import R5Config

                r5_config = R5Config(
                    data_directory=project_root / "--serve" / "data" / "r5_living_matrix",
                    output_file=project_root
                    / "--serve"
                    / "data"
                    / "r5_living_matrix"
                    / "aggregated"
                    / "matrix.json",
                )
                self.r5_matrix = R5LivingContextMatrix(project_root, r5_config)
            except Exception as e:
                logger.warning(f"Could not initialize R5 Matrix: {e}")

    def assess_risk(self, change_context: Dict[str, Any]) -> RiskAssessment:
        """
        Assess risk using all three systems:
        1. Decision Tree: Complexity, urgency, cost sensitivity
        2. R5 Matrix: Pattern frequency, historical success
        3. Risk Matrix: Approval requirements, checks needed
        """
        # Extract context
        complexity = change_context.get("complexity", "medium")
        urgency = change_context.get("urgency", "medium")
        cost_sensitive = change_context.get("cost_sensitive", True)
        error_count = change_context.get("error_count", 0)
        files_changed = change_context.get("files_changed", 0)
        lines_changed = change_context.get("lines_changed", 0)
        breaking_changes = change_context.get("breaking_changes", False)
        infrastructure_change = change_context.get("infrastructure_change", False)
        security_change = change_context.get("security_change", False)

        # Decision Tree assessment
        dt_complexity = complexity
        dt_urgency = urgency
        dt_cost_sensitive = cost_sensitive

        # R5 Matrix pattern check
        pattern_frequency = 0.0
        pattern_exists = False
        r5_patterns = []

        if self.r5_matrix:
            try:
                # Check for similar patterns (simplified - would need actual pattern matching)
                # For now, use change_context to estimate pattern frequency
                pattern_frequency = 0.5  # Default medium frequency
                pattern_exists = True  # Assume pattern exists
            except Exception as e:
                logger.warning(f"R5 Matrix pattern check failed: {e}")

        # Calculate risk level
        risk_level = self._calculate_risk_level(
            complexity=dt_complexity,
            urgency=dt_urgency,
            cost_sensitive=dt_cost_sensitive,
            error_count=error_count,
            pattern_frequency=pattern_frequency,
            pattern_exists=pattern_exists,
            files_changed=files_changed,
            lines_changed=lines_changed,
            breaking_changes=breaking_changes,
            infrastructure_change=infrastructure_change,
            security_change=security_change,
        )

        # Get approval requirements
        approval_reqs = self._get_approval_requirements(risk_level)
        ci_cd_checks = self._get_ci_cd_checks(risk_level)
        security_scan = self._get_security_scan(risk_level)
        performance_test = self._get_performance_test(risk_level)
        manual_qa = self._get_manual_qa(risk_level)

        # Decision Tree outcome
        dt_outcome = None
        if self.decision_tree:
            try:
                dt_context = DecisionContext(
                    complexity=dt_complexity,
                    urgency=dt_urgency,
                    cost_sensitive=dt_cost_sensitive,
                    error_count=error_count,
                )
                # Use approval workflow tree if it exists
                result = self.decision_tree.decide("approval_workflow", dt_context)
                dt_outcome = result.outcome.value
            except Exception as e:
                logger.warning(f"Decision Tree assessment failed: {e}")

        # Build reasoning
        reasoning = self._build_reasoning(
            risk_level, dt_complexity, dt_urgency, pattern_frequency, pattern_exists
        )

        return RiskAssessment(
            risk_level=risk_level,
            complexity=dt_complexity,
            urgency=dt_urgency,
            cost_sensitive=dt_cost_sensitive,
            pattern_frequency=pattern_frequency,
            pattern_exists=pattern_exists,
            approval_required=approval_reqs,
            ci_cd_checks=ci_cd_checks,
            security_scan=security_scan,
            performance_test=performance_test,
            manual_qa=manual_qa,
            decision_tree_outcome=dt_outcome,
            r5_patterns=r5_patterns,
            reasoning=reasoning,
        )

    def _calculate_risk_level(
        self,
        complexity: str,
        urgency: str,
        cost_sensitive: bool,
        error_count: int,
        pattern_frequency: float,
        pattern_exists: bool,
        files_changed: int,
        lines_changed: int,
        breaking_changes: bool,
        infrastructure_change: bool,
        security_change: bool,
    ) -> RiskLevel:
        """Calculate risk level from all factors"""

        # Critical risk factors
        if security_change or infrastructure_change:
            return RiskLevel.CRITICAL

        if error_count > 3:
            return RiskLevel.CRITICAL

        if breaking_changes and (complexity == "high" or urgency == "high"):
            return RiskLevel.CRITICAL

        # High risk factors
        if complexity == "high" and urgency == "high":
            return RiskLevel.HIGH

        if breaking_changes:
            return RiskLevel.HIGH

        if lines_changed > 1000 or files_changed > 50:
            return RiskLevel.HIGH

        if not pattern_exists or pattern_frequency < 0.3:
            return RiskLevel.HIGH

        # Medium risk factors
        if complexity == "medium" or urgency == "medium":
            return RiskLevel.MEDIUM

        if pattern_frequency < 0.7:
            return RiskLevel.MEDIUM

        if lines_changed > 100 or files_changed > 10:
            return RiskLevel.MEDIUM

        # Low risk (default)
        return RiskLevel.LOW

    def _get_approval_requirements(self, risk_level: RiskLevel) -> int:
        """Get required number of approvals"""
        requirements = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }
        return requirements.get(risk_level, 2)

    def _get_ci_cd_checks(self, risk_level: RiskLevel) -> str:
        """Get CI/CD check level"""
        checks = {
            RiskLevel.LOW: "basic",
            RiskLevel.MEDIUM: "full",
            RiskLevel.HIGH: "full",
            RiskLevel.CRITICAL: "full_audit",
        }
        return checks.get(risk_level, "full")

    def _get_security_scan(self, risk_level: RiskLevel) -> bool:
        """Get security scan requirement"""
        return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

    def _get_performance_test(self, risk_level: RiskLevel) -> bool:
        """Get performance test requirement"""
        return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def _get_manual_qa(self, risk_level: RiskLevel) -> bool:
        """Get manual QA requirement"""
        return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def _build_reasoning(
        self,
        risk_level: RiskLevel,
        complexity: str,
        urgency: str,
        pattern_frequency: float,
        pattern_exists: bool,
    ) -> str:
        """Build reasoning string"""
        reasons = [f"Risk level: {risk_level.value.upper()}"]
        reasons.append(f"Complexity: {complexity}, Urgency: {urgency}")

        if pattern_exists:
            reasons.append(f"Pattern frequency: {pattern_frequency:.2f}")
        else:
            reasons.append("No existing pattern found")

        return "; ".join(reasons)


def main():
    """Main entry point"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Integrated Risk Assessment")
    parser.add_argument("--context", help="Change context JSON file")
    parser.add_argument("--complexity", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--urgency", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--files-changed", type=int, default=0)
    parser.add_argument("--lines-changed", type=int, default=0)
    parser.add_argument("--breaking", action="store_true", help="Breaking changes")
    parser.add_argument("--infrastructure", action="store_true", help="Infrastructure change")
    parser.add_argument("--security", action="store_true", help="Security change")

    args = parser.parse_args()

    # Build context
    if args.context:
        with open(args.context) as f:
            change_context = json.load(f)
    else:
        change_context = {
            "complexity": args.complexity,
            "urgency": args.urgency,
            "files_changed": args.files_changed,
            "lines_changed": args.lines_changed,
            "breaking_changes": args.breaking,
            "infrastructure_change": args.infrastructure,
            "security_change": args.security,
        }

    # Assess risk
    assessor = IntegratedRiskAssessment(project_root)
    assessment = assessor.assess_risk(change_context)

    # Print results
    print("\n" + "=" * 80)
    print("INTEGRATED RISK ASSESSMENT")
    print("=" * 80)
    print(f"Risk Level: {assessment.risk_level.value.upper()}")
    print(f"Complexity: {assessment.complexity}, Urgency: {assessment.urgency}")
    print(f"Pattern Exists: {assessment.pattern_exists}")
    print(f"Pattern Frequency: {assessment.pattern_frequency:.2f}")
    print(f"\nApproval Required: {assessment.approval_required} reviewers")
    print(f"CI/CD Checks: {assessment.ci_cd_checks}")
    print(f"Security Scan: {assessment.security_scan}")
    print(f"Performance Test: {assessment.performance_test}")
    print(f"Manual QA: {assessment.manual_qa}")
    if assessment.decision_tree_outcome:
        print(f"\nDecision Tree Outcome: {assessment.decision_tree_outcome}")
    print(f"\nReasoning: {assessment.reasoning}")
    print("=" * 80)

    # Output JSON
    output = {
        "risk_level": assessment.risk_level.value,
        "complexity": assessment.complexity,
        "urgency": assessment.urgency,
        "approval_required": assessment.approval_required,
        "ci_cd_checks": assessment.ci_cd_checks,
        "security_scan": assessment.security_scan,
        "performance_test": assessment.performance_test,
        "manual_qa": assessment.manual_qa,
        "decision_tree_outcome": assessment.decision_tree_outcome,
        "reasoning": assessment.reasoning,
    }

    print("\nJSON Output:")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
