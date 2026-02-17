#!/usr/bin/env python3
"""
JARVIS Methodical WOPR Execution
Careful, methodical execution using A+B matrix and WOPR reasoning

@JARVIS @DOIT @WOPR @A+B @MATRIX @METHODICAL @CAREFUL
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

logger = get_logger("JARVISMethodicalWOPR")


class DecisionLevel(Enum):
    """Decision levels for A+B matrix"""
    AUTOMATIC = "automatic"  # Can proceed automatically
    REVIEW = "review"  # Needs review before execution
    ESCALATE = "escalate"  # Needs escalation/approval
    BLOCK = "block"  # Should not proceed


class WOPRReasoning:
    """
    WOPR (War Operation Plan Response) Reasoning System

    Provides careful, methodical decision-making using:
    - Threat assessment
    - Risk analysis
    - Pattern matching
    - Strategic evaluation
    """

    def __init__(self):
        """Initialize WOPR reasoning"""
        self.logger = get_logger("WOPRReasoning")

    def assess_risk(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk of an action using WOPR reasoning

        Args:
            action: Action to assess

        Returns:
            Risk assessment with level and reasoning
        """
        risk_factors = []
        risk_score = 0

        # Factor 1: Impact on core systems
        if action.get("affects_core_systems", False):
            risk_factors.append("Affects core systems")
            risk_score += 3

        # Factor 2: Data modification
        if action.get("modifies_data", False):
            risk_factors.append("Modifies data")
            risk_score += 2

        # Factor 3: Irreversible changes
        if action.get("irreversible", False):
            risk_factors.append("Irreversible changes")
            risk_score += 4

        # Factor 4: System-wide impact
        if action.get("system_wide", False):
            risk_factors.append("System-wide impact")
            risk_score += 3

        # Factor 5: Validation status
        if action.get("validation_status") == "FAIL":
            risk_factors.append("Validation failed")
            risk_score += 5

        # Determine risk level
        if risk_score >= 10:
            risk_level = "CRITICAL"
        elif risk_score >= 7:
            risk_level = "HIGH"
        elif risk_score >= 4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": self._get_risk_recommendation(risk_level)
        }

    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "CRITICAL": "BLOCK - Do not proceed without explicit approval",
            "HIGH": "ESCALATE - Requires review and approval",
            "MEDIUM": "REVIEW - Review before execution",
            "LOW": "PROCEED - Can proceed with caution"
        }
        return recommendations.get(risk_level, "UNKNOWN")

    def pattern_match(self, action: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Pattern match action against known patterns

        Args:
            action: Action to match
            patterns: Known patterns to match against

        Returns:
            Pattern match results
        """
        matches = []

        for pattern in patterns:
            match_score = 0

            # Match action type
            if action.get("type") == pattern.get("type"):
                match_score += 3

            # Match target systems
            action_targets = set(action.get("targets", []))
            pattern_targets = set(pattern.get("targets", []))
            if action_targets.intersection(pattern_targets):
                match_score += 2

            # Match complexity
            if action.get("complexity") == pattern.get("complexity"):
                match_score += 1

            if match_score > 0:
                matches.append({
                    "pattern": pattern.get("name"),
                    "match_score": match_score,
                    "recommendation": pattern.get("recommendation")
                })

        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "matches": matches,
            "best_match": matches[0] if matches else None
        }


class ABMatrix:
    """
    A+B Matrix Decision-Making System

    Provides lattice-based decision framework:
    - A: Automatic/Approved actions
    - B: Blocked/Requires approval actions
    - Matrix evaluation for escalation decisions
    """

    def __init__(self):
        """Initialize A+B matrix"""
        self.logger = get_logger("ABMatrix")

    def evaluate(self, action: Dict[str, Any], wopr_assessment: Dict[str, Any]) -> Tuple[DecisionLevel, Dict[str, Any]]:
        """
        Evaluate action using A+B matrix

        Args:
            action: Action to evaluate
            wopr_assessment: WOPR risk assessment

        Returns:
            Tuple of (decision_level, reasoning)
        """
        # A+B Matrix Logic
        # A = Automatic approval criteria
        # B = Block/Requires approval criteria

        # A Criteria (Automatic approval)
        a_criteria = [
            action.get("validation_status") == "PASS",
            wopr_assessment.get("risk_level") == "LOW",
            action.get("reversible", True),
            not action.get("affects_core_systems", False),
            action.get("has_backup", False)
        ]

        # B Criteria (Block/Requires approval)
        b_criteria = [
            action.get("validation_status") == "FAIL",
            wopr_assessment.get("risk_level") == "CRITICAL",
            action.get("irreversible", False),
            action.get("affects_core_systems", False),
            not action.get("has_backup", True)
        ]

        a_score = sum(1 for c in a_criteria if c)
        b_score = sum(1 for c in b_criteria if c)

        # Decision logic
        if b_score >= 3:
            decision = DecisionLevel.BLOCK
            reasoning = "Multiple B criteria met - BLOCK required"
        elif b_score >= 2:
            decision = DecisionLevel.ESCALATE
            reasoning = "Multiple B criteria met - ESCALATE for approval"
        elif a_score >= 4 and b_score == 0:
            decision = DecisionLevel.AUTOMATIC
            reasoning = "All A criteria met - AUTOMATIC approval"
        elif a_score >= 3:
            decision = DecisionLevel.REVIEW
            reasoning = "Most A criteria met - REVIEW recommended"
        else:
            decision = DecisionLevel.REVIEW
            reasoning = "Mixed criteria - REVIEW required"

        return decision, {
            "a_score": a_score,
            "b_score": b_score,
            "a_criteria": a_criteria,
            "b_criteria": b_criteria,
            "reasoning": reasoning,
            "decision": decision.value
        }


class JARVISMethodicalWOPRExecution:
    """
    Methodical WOPR Execution System

    Executes actions carefully and methodically using:
    - WOPR reasoning for risk assessment
    - A+B matrix for decision-making
    - Pattern matching for known solutions
    - Careful validation before execution
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize methodical execution system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Initialize subsystems
        self.wopr = WOPRReasoning()
        self.ab_matrix = ABMatrix()

        # Execution results
        self.execution_dir = self.project_root / "data" / "wopr_execution"
        self.execution_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("🎯 JARVIS METHODICAL WOPR EXECUTION")
        logger.info("   Careful, Methodical Execution with A+B Matrix")
        logger.info("=" * 70)
        logger.info("")

    def execute_methodically(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute actions methodically using WOPR reasoning and A+B matrix

        Args:
            actions: List of actions to execute

        Returns:
            Execution results
        """
        logger.info("🎯 METHODICAL EXECUTION STARTING...")
        logger.info("")

        results = {
            "execution_id": f"wopr_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "actions": [],
            "summary": {}
        }

        # Step 1: WOPR Assessment
        logger.info("STEP 1: WOPR RISK ASSESSMENT")
        logger.info("-" * 70)

        for i, action in enumerate(actions, 1):
            logger.info(f"\nAction {i}: {action.get('name', 'Unknown')}")

            # WOPR risk assessment
            wopr_assessment = self.wopr.assess_risk(action)
            logger.info(f"  Risk Level: {wopr_assessment['risk_level']}")
            logger.info(f"  Risk Score: {wopr_assessment['risk_score']}")
            logger.info(f"  Recommendation: {wopr_assessment['recommendation']}")

            # A+B Matrix evaluation
            decision, matrix_reasoning = self.ab_matrix.evaluate(action, wopr_assessment)
            logger.info(f"  A+B Decision: {decision.value.upper()}")
            logger.info(f"  A Score: {matrix_reasoning['a_score']}/5")
            logger.info(f"  B Score: {matrix_reasoning['b_score']}/5")
            logger.info(f"  Reasoning: {matrix_reasoning['reasoning']}")

            # Execute based on decision
            if decision == DecisionLevel.BLOCK:
                logger.warning(f"  ⛔ BLOCKED: {action.get('name')} - Cannot proceed")
                action_result = {
                    "action": action.get("name"),
                    "status": "BLOCKED",
                    "reason": "A+B matrix decision: BLOCK",
                    "wopr_assessment": wopr_assessment,
                    "matrix_reasoning": matrix_reasoning
                }
            elif decision == DecisionLevel.ESCALATE:
                logger.warning(f"  ⚠️  ESCALATED: {action.get('name')} - Requires approval")
                action_result = {
                    "action": action.get("name"),
                    "status": "ESCALATED",
                    "reason": "A+B matrix decision: ESCALATE",
                    "wopr_assessment": wopr_assessment,
                    "matrix_reasoning": matrix_reasoning
                }
            elif decision == DecisionLevel.REVIEW:
                logger.info(f"  📋 REVIEW: {action.get('name')} - Review before execution")
                action_result = {
                    "action": action.get("name"),
                    "status": "REVIEW",
                    "reason": "A+B matrix decision: REVIEW",
                    "wopr_assessment": wopr_assessment,
                    "matrix_reasoning": matrix_reasoning
                }
            else:  # AUTOMATIC
                logger.info(f"  ✅ APPROVED: {action.get('name')} - Can proceed")
                action_result = {
                    "action": action.get("name"),
                    "status": "APPROVED",
                    "reason": "A+B matrix decision: AUTOMATIC",
                    "wopr_assessment": wopr_assessment,
                    "matrix_reasoning": matrix_reasoning
                }

            results["actions"].append(action_result)

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 EXECUTION SUMMARY")
        logger.info("=" * 70)

        total = len(results["actions"])
        approved = sum(1 for a in results["actions"] if a["status"] == "APPROVED")
        review = sum(1 for a in results["actions"] if a["status"] == "REVIEW")
        escalated = sum(1 for a in results["actions"] if a["status"] == "ESCALATED")
        blocked = sum(1 for a in results["actions"] if a["status"] == "BLOCKED")

        results["summary"] = {
            "total_actions": total,
            "approved": approved,
            "review": review,
            "escalated": escalated,
            "blocked": blocked
        }

        logger.info(f"Total Actions: {total}")
        logger.info(f"Approved: {approved}")
        logger.info(f"Review: {review}")
        logger.info(f"Escalated: {escalated}")
        logger.info(f"Blocked: {blocked}")
        logger.info("")

        results["completed_at"] = datetime.now().isoformat()

        # Save results
        self._save_results(results)

        logger.info("=" * 70)
        logger.info("✅ METHODICAL EXECUTION COMPLETE")
        logger.info("=" * 70)

        return results

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save execution results"""
        try:
            filename = self.execution_dir / f"{results['execution_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Results saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """Main execution"""
    print("=" * 70)
    print("🎯 JARVIS METHODICAL WOPR EXECUTION")
    print("   Careful, Methodical Execution with A+B Matrix")
    print("=" * 70)
    print()

    # Load actionable items from SYPHON results
    project_root = Path(__file__).parent.parent.parent
    syphon_dir = project_root / "data" / "syphon_validation"
    syphon_files = sorted(syphon_dir.glob("validation_syphon_*.json"), reverse=True)

    if not syphon_files:
        print("❌ No SYPHON results found")
        return

    syphon_file = syphon_files[0]
    print(f"📄 Loading SYPHON results: {syphon_file.name}")

    try:
        with open(syphon_file, 'r', encoding='utf-8') as f:
            syphon_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load SYPHON results: {e}")
        return

    # Convert actionable items to actions
    actionable_items = syphon_data.get("actionable_items", [])
    actions = []

    for item in actionable_items:
        actions.append({
            "name": item.get("item", "Unknown"),
            "type": "VALIDATION_IMPROVEMENT",
            "priority": item.get("priority", "MEDIUM"),
            "validation_status": "PARTIAL",  # Current status
            "affects_core_systems": False,
            "modifies_data": False,
            "irreversible": False,
            "system_wide": False,
            "reversible": True,
            "has_backup": True,
            "targets": ["validation_system"],
            "complexity": "LOW"
        })

    if not actions:
        print("⚠️  No actionable items found")
        return

    print(f"📋 Found {len(actions)} actionable items")
    print()

    # Execute methodically
    executor = JARVISMethodicalWOPRExecution()
    results = executor.execute_methodically(actions)

    print()
    print("=" * 70)
    print("✅ METHODICAL EXECUTION COMPLETE")
    print("=" * 70)
    print(f"Total Actions: {results['summary']['total_actions']}")
    print(f"Approved: {results['summary']['approved']}")
    print(f"Review: {results['summary']['review']}")
    print(f"Escalated: {results['summary']['escalated']}")
    print(f"Blocked: {results['summary']['blocked']}")
    print("=" * 70)


if __name__ == "__main__":


    main()