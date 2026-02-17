#!/usr/bin/env python3
"""
Perspective Validation System - Highest Level of Scrutiny

Uses neutral third parties to determine if our perspective is correct
when compared to their perspective and the overall perspective.

Applies highest level of scrutiny with:
- Neutral third-party analysis
- Multiple perspective comparison
- Critical analysis
- Reality checking
- Bias detection

Tags: #PERSPECTIVE_VALIDATION #SCRUTINY #NEUTRAL_THIRD_PARTY #CRITICAL_ANALYSIS @JARVIS @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("PerspectiveValidation")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PerspectiveValidation")

try:
    from marvin_verification_system import MarvinVerificationSystem, VerificationResult
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    logger.warning("MARVIN verification system not available")

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    logger.warning("Universal Decision Tree not available")


class PerspectiveType(Enum):
    """Types of perspectives"""
    OUR_PERSPECTIVE = "our_perspective"
    THEIR_PERSPECTIVE = "their_perspective"
    OVERALL_PERSPECTIVE = "overall_perspective"
    NEUTRAL_THIRD_PARTY = "neutral_third_party"


class ValidationLevel(Enum):
    """Levels of scrutiny"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    HIGHEST = "highest"


class TestingMethod(Enum):
    """Testing methods for validation"""
    OPEN = "open"  # Tester knows which perspective is which
    SINGLE_BLIND = "single_blind"  # Tester doesn't know which is "ours"
    DOUBLE_BLIND = "double_blind"  # Neither tester nor system knows labels
    TRIPLE_BLIND = "triple_blind"  # Tester, system, and evaluator all blind


@dataclass
class Perspective:
    """A perspective to be validated"""
    perspective_type: PerspectiveType
    content: str
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    biases: List[str] = field(default_factory=list)


@dataclass
class PerspectiveValidationResult:
    """Result of perspective validation"""
    validated: bool
    confidence_score: float
    our_perspective_correct: Optional[bool] = None
    their_perspective_correct: Optional[bool] = None
    overall_perspective_correct: Optional[bool] = None
    neutral_third_party_assessment: Optional[str] = None
    perspective_comparison: Dict[str, Any] = field(default_factory=dict)
    discrepancies: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    bias_detected: List[str] = field(default_factory=list)
    validation_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "validated": self.validated,
            "confidence_score": self.confidence_score,
            "our_perspective_correct": self.our_perspective_correct,
            "their_perspective_correct": self.their_perspective_correct,
            "overall_perspective_correct": self.overall_perspective_correct,
            "neutral_third_party_assessment": self.neutral_third_party_assessment,
            "perspective_comparison": self.perspective_comparison,
            "discrepancies": self.discrepancies,
            "recommendations": self.recommendations,
            "critical_issues": self.critical_issues,
            "bias_detected": self.bias_detected,
            "validation_metadata": self.validation_metadata,
            "timestamp": self.timestamp.isoformat()
        }


class PerspectiveValidationSystem:
    """
    Perspective Validation System - Highest Level of Scrutiny

    Uses neutral third parties to validate perspectives:
    - @MARVIN: Critical analysis and reality checking
    - Decision Tree: Logical validation
    - Cross-perspective comparison
    - Bias detection
    - Reality checking
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize perspective validation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.validation_dir = self.project_root / "data" / "perspective_validation"
        self.validation_dir.mkdir(parents=True, exist_ok=True)

        # Blind testing state
        self._blind_mapping: Optional[Dict[str, str]] = None

        # Initialize neutral third parties
        self.marvin: Optional[MarvinVerificationSystem] = None
        if MARVIN_AVAILABLE:
            try:
                self.marvin = MarvinVerificationSystem()
                logger.info("✅ MARVIN initialized as neutral third party")
            except Exception as e:
                logger.warning(f"MARVIN initialization failed: {e}")

        logger.info("="*80)
        logger.info("🔍 PERSPECTIVE VALIDATION SYSTEM - HIGHEST SCRUTINY")
        logger.info("   Blind/Double-Blind Testing Enabled")
        logger.info("="*80)
        logger.info("")

    def validate_perspectives(
        self,
        our_perspective: str,
        their_perspective: Optional[str] = None,
        overall_perspective: Optional[str] = None,
        validation_level: ValidationLevel = ValidationLevel.HIGHEST,
        testing_method: TestingMethod = TestingMethod.DOUBLE_BLIND,
        context: Optional[Dict[str, Any]] = None
    ) -> PerspectiveValidationResult:
        """
        Validate perspectives using highest level of scrutiny

        Args:
            our_perspective: Our perspective to validate
            their_perspective: Their perspective (if available)
            overall_perspective: Overall perspective (if available)
            validation_level: Level of scrutiny to apply
            context: Additional context for validation

        Returns:
            Comprehensive validation result
        """
        logger.info("🔍 Starting perspective validation with highest scrutiny...")
        logger.info(f"   Testing Method: {testing_method.value}")
        logger.info("")

        # Apply blind testing methodology
        blinded_perspectives = self._apply_blind_testing(
            our_perspective,
            their_perspective,
            overall_perspective,
            testing_method
        )

        result = PerspectiveValidationResult(
            validated=False,
            confidence_score=0.0,
            validation_metadata={
                "validation_level": validation_level.value,
                "testing_method": testing_method.value,
                "perspectives_provided": {
                    "our": True,
                    "their": their_perspective is not None,
                    "overall": overall_perspective is not None
                },
                "blinded": testing_method != TestingMethod.OPEN
            }
        )

        # Phase 1: Neutral Third-Party Analysis (MARVIN) - BLIND
        logger.info("   🔍 Phase 1: Neutral Third-Party Analysis (MARVIN) - BLIND TESTING...")
        if self.marvin:
            # Use blinded perspectives for analysis
            marvin_result = self._marvin_analysis(
                blinded_perspectives["perspective_a"],
                blinded_perspectives.get("perspective_b"),
                blinded_perspectives.get("perspective_c"),
                context,
                blinded=True
            )
            result.validation_metadata["marvin_analysis"] = marvin_result
            result.neutral_third_party_assessment = marvin_result.get("assessment", "No assessment available")
            result.critical_issues.extend(marvin_result.get("critical_issues", []))
            result.bias_detected.extend(marvin_result.get("biases", []))

            # Map blind results back to original perspectives
            if testing_method != TestingMethod.OPEN:
                marvin_result = self._unblind_results(marvin_result, blinded_perspectives)
        else:
            logger.warning("   ⚠️  MARVIN not available for neutral third-party analysis")

        # Phase 2: Perspective Comparison
        logger.info("   🔍 Phase 2: Perspective Comparison...")
        comparison = self._compare_perspectives(our_perspective, their_perspective, overall_perspective)
        result.perspective_comparison = comparison
        result.discrepancies = comparison.get("discrepancies", [])

        # Phase 3: Bias Detection
        logger.info("   🔍 Phase 3: Bias Detection...")
        biases = self._detect_biases(our_perspective, their_perspective, overall_perspective)
        result.bias_detected.extend(biases)

        # Phase 4: Reality Checking
        logger.info("   🔍 Phase 4: Reality Checking...")
        reality_check = self._reality_check(our_perspective, their_perspective, overall_perspective, context)
        result.validation_metadata["reality_check"] = reality_check

        # Phase 5: Decision Tree Validation (if available)
        if DECISION_TREE_AVAILABLE:
            logger.info("   🔍 Phase 5: Decision Tree Validation...")
            decision_result = self._decision_tree_validation(our_perspective, context)
            result.validation_metadata["decision_tree"] = decision_result

        # Phase 6: Final Assessment
        logger.info("   🔍 Phase 6: Final Assessment...")
        final_assessment = self._final_assessment(result)
        result.our_perspective_correct = final_assessment.get("our_correct")
        result.their_perspective_correct = final_assessment.get("their_correct")
        result.overall_perspective_correct = final_assessment.get("overall_correct")
        result.confidence_score = final_assessment.get("confidence", 0.0)
        result.validated = final_assessment.get("validated", False)
        result.recommendations = final_assessment.get("recommendations", [])

        # Save validation result
        self._save_validation_result(result)

        logger.info("")
        logger.info("="*80)
        logger.info("✅ PERSPECTIVE VALIDATION COMPLETE")
        logger.info("="*80)
        logger.info(f"   Our Perspective Correct: {result.our_perspective_correct}")
        logger.info(f"   Their Perspective Correct: {result.their_perspective_correct}")
        logger.info(f"   Overall Perspective Correct: {result.overall_perspective_correct}")
        logger.info(f"   Confidence Score: {result.confidence_score:.2f}")
        logger.info(f"   Critical Issues: {len(result.critical_issues)}")
        logger.info(f"   Biases Detected: {len(result.bias_detected)}")
        logger.info("")

        return result

    def _marvin_analysis(
        self,
        perspective_a: str,
        perspective_b: Optional[str],
        perspective_c: Optional[str],
        context: Optional[Dict[str, Any]],
        blinded: bool = False
    ) -> Dict[str, Any]:
        """MARVIN's neutral third-party analysis (blind if requested)"""
        if not self.marvin:
            return {"assessment": "MARVIN not available"}

        # Combine all perspectives for analysis (with or without labels)
        if blinded:
            analysis_text = f"""
PERSPECTIVE A:
{perspective_a}

"""
            if perspective_b:
                analysis_text += f"""
PERSPECTIVE B:
{perspective_b}

"""
            if perspective_c:
                analysis_text += f"""
PERSPECTIVE C:
{perspective_c}

"""
            analysis_text += """
VALIDATION REQUEST (BLIND TEST):
Evaluate these perspectives without knowing which is "ours", "theirs", or "overall".
Apply highest level of scrutiny. Identify which perspective is most correct.
Identify biases, discrepancies, and critical issues in each perspective.
"""
        else:
            analysis_text = f"""
OUR PERSPECTIVE:
{perspective_a}

"""
            if perspective_b:
                analysis_text += f"""
THEIR PERSPECTIVE:
{perspective_b}

"""
            if perspective_c:
                analysis_text += f"""
OVERALL PERSPECTIVE:
{perspective_c}

"""
            analysis_text += """
VALIDATION REQUEST:
Determine if our perspective is correct when compared to their perspective and the overall perspective.
Apply highest level of scrutiny. Identify biases, discrepancies, and critical issues.
"""

        try:
            verification_result = self.marvin.verify_work(
                work_content=analysis_text,
                work_type="perspective_validation",
                context=context or {}
            )

            return {
                "assessment": verification_result.philosophical_insights[0] if verification_result.philosophical_insights else "No assessment",
                "confidence": verification_result.confidence_score,
                "critical_issues": [issue.get("description", "") for issue in verification_result.issues_found],
                "biases": verification_result.recommendations,  # MARVIN's recommendations often identify biases
                "verified": verification_result.verified
            }
        except Exception as e:
            logger.error(f"MARVIN analysis error: {e}")
            return {"assessment": f"Error: {e}"}

    def _compare_perspectives(
        self,
        our_perspective: str,
        their_perspective: Optional[str],
        overall_perspective: Optional[str]
    ) -> Dict[str, Any]:
        """Compare perspectives to identify discrepancies"""
        comparison = {
            "perspectives_provided": {
                "our": True,
                "their": their_perspective is not None,
                "overall": overall_perspective is not None
            },
            "discrepancies": [],
            "agreements": [],
            "key_differences": []
        }

        if not their_perspective and not overall_perspective:
            comparison["discrepancies"].append({
                "type": "insufficient_data",
                "description": "Only our perspective provided - cannot compare"
            })
            return comparison

        # Simple keyword/theme comparison (can be enhanced with NLP)
        our_keywords = set(our_perspective.lower().split())
        their_keywords = set(their_perspective.lower().split()) if their_perspective else set()
        overall_keywords = set(overall_perspective.lower().split()) if overall_perspective else set()

        # Find common themes
        common = our_keywords & their_keywords if their_perspective else set()
        common = common & overall_keywords if overall_perspective else common

        # Find differences
        our_unique = our_keywords - their_keywords - overall_keywords if (their_perspective and overall_perspective) else set()
        their_unique = their_keywords - our_keywords if their_perspective else set()

        comparison["agreements"] = list(common)[:10]  # Top 10 common themes
        comparison["key_differences"] = {
            "our_unique": list(our_unique)[:10],
            "their_unique": list(their_unique)[:10]
        }

        if our_unique:
            comparison["discrepancies"].append({
                "type": "our_perspective_unique",
                "description": f"Our perspective has {len(our_unique)} unique elements not in other perspectives",
                "elements": list(our_unique)[:5]
            })

        if their_unique:
            comparison["discrepancies"].append({
                "type": "their_perspective_unique",
                "description": f"Their perspective has {len(their_unique)} unique elements not in our perspective",
                "elements": list(their_unique)[:5]
            })

        return comparison

    def _detect_biases(
        self,
        our_perspective: str,
        their_perspective: Optional[str],
        overall_perspective: Optional[str]
    ) -> List[str]:
        """Detect biases in perspectives"""
        biases = []

        # Check for confirmation bias (only seeing what confirms our view)
        if their_perspective and not any(word in our_perspective.lower() for word in their_perspective.lower().split()[:10]):
            biases.append("Potential confirmation bias: Our perspective doesn't acknowledge their perspective")

        # Check for overconfidence
        if len(our_perspective) > 500 and not their_perspective:
            biases.append("Potential overconfidence: Long perspective without considering alternatives")

        # Check for anchoring bias
        if overall_perspective and our_perspective[:100] == overall_perspective[:100]:
            biases.append("Potential anchoring bias: Our perspective may be anchored to overall perspective")

        return biases

    def _reality_check(
        self,
        our_perspective: str,
        their_perspective: Optional[str],
        overall_perspective: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reality check against known facts"""
        reality_check = {
            "facts_checked": [],
            "reality_aligned": True,
            "discrepancies_with_reality": []
        }

        # Check against context/facts if provided
        if context:
            facts = context.get("facts", [])
            for fact in facts:
                reality_check["facts_checked"].append(fact)
                # Simple check: does our perspective align with facts?
                if fact.lower() not in our_perspective.lower():
                    reality_check["reality_aligned"] = False
                    reality_check["discrepancies_with_reality"].append({
                        "fact": fact,
                        "issue": "Our perspective doesn't acknowledge this fact"
                    })

        return reality_check

    def _decision_tree_validation(
        self,
        our_perspective: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use decision tree for logical validation"""
        if not DECISION_TREE_AVAILABLE:
            return {"status": "decision_tree_not_available"}

        try:
            decision_context = DecisionContext(
                user_query=our_perspective,
                session_id="perspective_validation",
                custom_data=context or {}
            )

            result = decide("perspective_validation", decision_context)

            return {
                "outcome": result.outcome.value,
                "confidence": result.confidence,
                "reasoning": result.reasoning,
                "next_action": result.next_action
            }
        except Exception as e:
            logger.warning(f"Decision tree validation error: {e}")
            return {"status": "error", "error": str(e)}

    def _final_assessment(self, result: PerspectiveValidationResult) -> Dict[str, Any]:
        """Final assessment combining all validation results"""
        assessment = {
            "our_correct": None,
            "their_correct": None,
            "overall_correct": None,
            "confidence": 0.0,
            "validated": False,
            "recommendations": []
        }

        # Determine correctness based on validation results
        marvin_assessment = result.validation_metadata.get("marvin_analysis", {})
        discrepancies = result.discrepancies
        biases = result.bias_detected
        critical_issues = result.critical_issues

        # If no critical issues and low discrepancies, our perspective is likely correct
        if not critical_issues and len(discrepancies) < 2:
            assessment["our_correct"] = True
            assessment["confidence"] = 0.7
        elif len(critical_issues) > 0 or len(biases) > 2:
            assessment["our_correct"] = False
            assessment["confidence"] = 0.9
            assessment["recommendations"].append("Address critical issues and biases before proceeding")
        else:
            assessment["our_correct"] = None  # Uncertain
            assessment["confidence"] = 0.5
            assessment["recommendations"].append("Gather more information to determine correctness")

        # Add recommendations based on findings
        if biases:
            assessment["recommendations"].append(f"Address {len(biases)} detected biases")
        if discrepancies:
            assessment["recommendations"].append(f"Resolve {len(discrepancies)} discrepancies with other perspectives")
        if critical_issues:
            assessment["recommendations"].append(f"Address {len(critical_issues)} critical issues")

        assessment["validated"] = assessment["confidence"] >= 0.7

        return assessment

    def _apply_blind_testing(
        self,
        our_perspective: str,
        their_perspective: Optional[str],
        overall_perspective: Optional[str],
        testing_method: TestingMethod
    ) -> Dict[str, Any]:
        """Apply blind testing methodology (like Pepsi vs Coke taste test)"""
        import random

        perspectives = {
            "our": our_perspective,
            "their": their_perspective,
            "overall": overall_perspective
        }

        # Remove None values
        valid_perspectives = {k: v for k, v in perspectives.items() if v is not None}

        if testing_method == TestingMethod.OPEN:
            # No blinding - return as-is with labels
            return {
                "perspective_a": our_perspective,
                "perspective_b": their_perspective,
                "perspective_c": overall_perspective,
                "mapping": {"perspective_a": "our", "perspective_b": "their", "perspective_c": "overall"}
            }

        elif testing_method == TestingMethod.SINGLE_BLIND:
            # Tester doesn't know which is "ours" - randomize order
            perspective_list = list(valid_perspectives.items())
            random.shuffle(perspective_list)

            blinded = {}
            mapping = {}
            labels = ["perspective_a", "perspective_b", "perspective_c"]
            for i, (original_label, content) in enumerate(perspective_list):
                if i < len(labels):
                    blinded[labels[i]] = content
                    mapping[labels[i]] = original_label

            return {**blinded, "mapping": mapping, "original": valid_perspectives}

        elif testing_method == TestingMethod.DOUBLE_BLIND:
            # Neither tester nor system knows labels - fully randomized
            perspective_list = list(valid_perspectives.items())
            random.shuffle(perspective_list)

            blinded = {}
            mapping = {}
            labels = ["perspective_a", "perspective_b", "perspective_c"]
            for i, (original_label, content) in enumerate(perspective_list):
                if i < len(labels):
                    blinded[labels[i]] = content
                    mapping[labels[i]] = original_label

            # Store mapping separately (not accessible during validation)
            self._blind_mapping = mapping

            return {**blinded, "mapping": mapping, "original": valid_perspectives}

        elif testing_method == TestingMethod.TRIPLE_BLIND:
            # Maximum blinding - even evaluator doesn't know
            perspective_list = list(valid_perspectives.items())
            random.shuffle(perspective_list)

            blinded = {}
            mapping = {}
            labels = ["perspective_a", "perspective_b", "perspective_c"]
            for i, (original_label, content) in enumerate(perspective_list):
                if i < len(labels):
                    blinded[labels[i]] = content
                    mapping[labels[i]] = original_label

            # Store mapping in separate file (not accessible during validation)
            mapping_file = self.validation_dir / f"blind_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(mapping_file, 'w') as f:
                json.dump({"mapping": mapping, "timestamp": datetime.now().isoformat()}, f)

            return {**blinded, "mapping_file": str(mapping_file), "original": valid_perspectives}

        return {"perspective_a": our_perspective, "perspective_b": their_perspective, "perspective_c": overall_perspective}

    def _unblind_results(
        self,
        results: Dict[str, Any],
        blinded_perspectives: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Unblind results after validation"""
        mapping = blinded_perspectives.get("mapping", {})

        # Map blind labels back to original labels
        unblinded = {}
        for blind_label, original_label in mapping.items():
            if blind_label in results:
                unblinded[original_label] = results[blind_label]

        return {**results, "unblinded": unblinded, "mapping": mapping}

    def _save_validation_result(self, result: PerspectiveValidationResult):
        try:
            """Save validation result"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = self.validation_dir / f"validation_{timestamp}.json"

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"   💾 Validation result saved: {result_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_validation_result: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Perspective Validation System")
        parser.add_argument("--our-perspective", required=True, help="Our perspective to validate")
        parser.add_argument("--their-perspective", help="Their perspective (optional)")
        parser.add_argument("--overall-perspective", help="Overall perspective (optional)")
        parser.add_argument("--context", help="JSON context file (optional)")

        args = parser.parse_args()

        context = None
        if args.context:
            with open(args.context, 'r') as f:
                context = json.load(f)

        system = PerspectiveValidationSystem()
        result = system.validate_perspectives(
            our_perspective=args.our_perspective,
            their_perspective=args.their_perspective,
            overall_perspective=args.overall_perspective,
            context=context
        )

        print(json.dumps(result.to_dict(), indent=2))

        return 0 if result.validated else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())