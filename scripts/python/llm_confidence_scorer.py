#!/usr/bin/env python3
"""
LLM Confidence Scorer - Detects Hallucinations Before They Become Problems

Analyzes LLM outputs for hallucination patterns and assigns confidence scores.
Integrated into workflow system to prevent probabilistic outputs from becoming
deterministic failures.

Based on analysis of hallucination patterns from workflow verification logs.

@SYPHON @WORKFLOW @VERIFICATION
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LLMConfidenceScorer")


class HallucinationType(Enum):
    """Types of hallucinations detected"""
    COMPLETION_CLAIM = "completion_claim"
    DELIVERABLE_CLAIM = "deliverable_claim"
    CONTEXT_DRIFT = "context_drift"
    ASSUMPTION_WITHOUT_VERIFICATION = "assumption_without_verification"
    FACTUAL_INACCURACY = "factual_inaccuracy"


class ConfidenceLevel(Enum):
    """Confidence assessment levels"""
    HIGH = "high"      # > 0.8 - Safe to proceed
    MEDIUM = "medium"  # 0.5-0.8 - Needs review
    LOW = "low"        # < 0.5 - Requires human intervention


@dataclass
class HallucinationDetection:
    """Detected hallucination instance"""
    hallucination_type: HallucinationType
    severity: float  # 0.0 to 1.0
    evidence: str
    suggestion: str
    confidence_impact: float  # How much this reduces overall confidence


@dataclass
class ConfidenceScore:
    """Complete confidence analysis"""
    overall_confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    hallucinations_detected: List[HallucinationDetection]
    analysis_timestamp: str
    semantic_coherence: float
    factual_grounding: float
    deliverable_alignment: float
    completion_claim_validity: float
    recommendations: List[str]


class LLMConfidenceScorer:
    """
    Analyzes LLM outputs for hallucination patterns and assigns confidence scores.

    Prevents probabilistic LLM outputs from becoming deterministic workflow failures.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the confidence scorer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Load hallucination patterns from SYPHON
        self.hallucination_patterns = self._load_syphon_patterns()

        # Confidence thresholds
        self.thresholds = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.0
        }

    def _load_syphon_patterns(self) -> Dict[str, Any]:
        """Load hallucination patterns from SYPHON blacklist"""
        patterns = {}

        blacklist_dir = self.project_root / "data" / "syphon" / "blacklist_patterns"
        if blacklist_dir.exists():
            for pattern_file in blacklist_dir.glob("*.json"):
                try:
                    with open(pattern_file, 'r', encoding='utf-8') as f:
                        pattern_data = json.load(f)
                        patterns[pattern_data.get("pattern_id", pattern_file.stem)] = pattern_data
                except Exception as e:
                    self.logger.warning(f"Failed to load pattern {pattern_file}: {e}")

        return patterns

    def analyze_llm_output(self, prompt: str, response: str, context: Optional[str] = None,
                          expected_deliverables: Optional[List[str]] = None) -> ConfidenceScore:
        """
        Analyze LLM output for hallucinations and assign confidence score

        Args:
            prompt: Original prompt given to LLM
            response: LLM response to analyze
            context: Additional context provided (optional)
            expected_deliverables: List of deliverables that should be mentioned/created

        Returns:
            ConfidenceScore with detailed analysis
        """
        hallucinations = []
        scores = {}

        # Analyze semantic coherence (does response stay on topic?)
        scores["semantic_coherence"] = self._analyze_semantic_coherence(prompt, response, context)

        # Analyze factual grounding (does it reference info not in context?)
        scores["factual_grounding"] = self._analyze_factual_grounding(response, context or prompt)

        # Analyze deliverable alignment (does it claim outputs that don't exist?)
        scores["deliverable_alignment"] = self._analyze_deliverable_alignment(response, expected_deliverables)

        # Analyze completion claims (does it claim completion without verification?)
        scores["completion_claim_validity"] = self._analyze_completion_claims(response)

        # Detect specific hallucination patterns
        hallucinations.extend(self._detect_completion_hallucinations(response))
        hallucinations.extend(self._detect_deliverable_hallucinations(response, expected_deliverables))
        hallucinations.extend(self._detect_context_drift(response, context or prompt))
        hallucinations.extend(self._detect_assumption_patterns(response))

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(scores, hallucinations)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(overall_confidence)

        # Generate recommendations
        recommendations = self._generate_recommendations(confidence_level, hallucinations)

        return ConfidenceScore(
            overall_confidence=overall_confidence,
            confidence_level=confidence_level,
            hallucinations_detected=hallucinations,
            analysis_timestamp=datetime.now().isoformat(),
            semantic_coherence=scores["semantic_coherence"],
            factual_grounding=scores["factual_grounding"],
            deliverable_alignment=scores["deliverable_alignment"],
            completion_claim_validity=scores["completion_claim_validity"],
            recommendations=recommendations
        )

    def _analyze_semantic_coherence(self, prompt: str, response: str, context: Optional[str] = None) -> float:
        """Analyze if response stays semantically coherent with prompt/context"""
        # Simple coherence check - response should reference key terms from prompt
        prompt_words = set(re.findall(r'\b\w{3,}\b', prompt.lower()))
        response_words = set(re.findall(r'\b\w{3,}\b', response.lower()))

        # Calculate overlap
        if prompt_words:
            overlap = len(prompt_words.intersection(response_words)) / len(prompt_words)
            return min(1.0, overlap * 2.0)  # Scale up to give benefit of doubt
        return 0.5  # Neutral if no clear terms to match

    def _analyze_factual_grounding(self, response: str, context: str) -> float:
        """Analyze if response is grounded in provided context"""
        # Check for claims that reference information not in context
        # This is a simplified version - real implementation would need NLP

        # Look for definitive statements that might be ungrounded
        definitive_phrases = [
            "is located at", "was created on", "consists of", "includes",
            "has been", "was implemented", "exists at", "can be found"
        ]

        definitive_claims = 0
        grounded_claims = 0

        for phrase in definitive_phrases:
            claims = response.lower().count(phrase)
            definitive_claims += claims
            # If phrase appears in context, consider it potentially grounded
            if phrase in context.lower():
                grounded_claims += claims

        if definitive_claims == 0:
            return 1.0  # No definitive claims = no risk

        grounding_ratio = grounded_claims / definitive_claims
        return max(0.0, grounding_ratio)

    def _analyze_deliverable_alignment(self, response: str, expected_deliverables: Optional[List[str]]) -> float:
        try:
            """Analyze if response claims deliverables that actually exist"""
            if not expected_deliverables:
                return 1.0  # No deliverables to verify

            claimed_deliverables = []
            # Look for file path patterns in response
            file_patterns = [
                r'\b\w+\.\w{2,4}\b',  # file.ext
                r'\b\w+/\w+\.\w{2,4}\b',  # path/file.ext
                r'\b\w+/\w+/\w+\.\w{2,4}\b'  # deeper/path/file.ext
            ]

            for pattern in file_patterns:
                matches = re.findall(pattern, response)
                claimed_deliverables.extend(matches)

            if not claimed_deliverables:
                return 1.0  # No deliverables claimed

            # Check if claimed deliverables actually exist
            existing_count = 0
            for deliverable in claimed_deliverables:
                full_path = self.project_root / deliverable
                if full_path.exists():
                    existing_count += 1

            alignment_ratio = existing_count / len(claimed_deliverables)
            return alignment_ratio

        except Exception as e:
            self.logger.error(f"Error in _analyze_deliverable_alignment: {e}", exc_info=True)
            raise
    def _analyze_completion_claims(self, response: str) -> float:
        """Analyze validity of completion claims"""
        completion_phrases = [
            "complete", "finished", "done", "completed",
            "100%", "all set", "ready", "working", "operational"
        ]

        # Count completion claims
        completion_claims = 0
        for phrase in completion_phrases:
            completion_claims += response.lower().count(phrase)

        if completion_claims == 0:
            return 1.0  # No completion claims = no risk

        # Check if completion claims are qualified
        qualification_phrases = [
            "verified", "tested", "validated", "confirmed", "checked",
            "according to", "based on", "after testing", "confirmed that"
        ]

        qualifications = 0
        for phrase in qualification_phrases:
            qualifications += response.lower().count(phrase)

        # Completion claims should be qualified
        qualification_ratio = qualifications / max(1, completion_claims)
        return min(1.0, qualification_ratio * 2.0)  # Scale up

    def _detect_completion_hallucinations(self, response: str) -> List[HallucinationDetection]:
        """Detect when AI claims completion without verification"""
        detections = []

        # Pattern: Claims 100% complete but uses simplistic criteria
        if "100% complete" in response.lower() or "all complete" in response.lower():
            # Check if there's actual verification mentioned
            verification_indicators = ["verified", "tested", "validated", "confirmed"]
            has_verification = any(indicator in response.lower() for indicator in verification_indicators)

            if not has_verification:
                detections.append(HallucinationDetection(
                    hallucination_type=HallucinationType.COMPLETION_CLAIM,
                    severity=0.7,
                    evidence="Claims 100% completion without verification evidence",
                    suggestion="Add verification steps before claiming completion",
                    confidence_impact=0.3
                ))

        return detections

    def _detect_deliverable_hallucinations(self, response: str, expected_deliverables: Optional[List[str]]) -> List[HallucinationDetection]:
        try:
            """Detect when AI claims deliverables that don't exist or fails to mention expected deliverables"""
            detections = []

            if not expected_deliverables:
                return detections

            # Normalize expected deliverables for comparison
            expected_normalized = {Path(d).name.lower() for d in expected_deliverables}

            # Extract claimed file paths from response
            file_pattern = r'\b[\w/\\]+\.\w{2,4}\b'
            claimed_files = re.findall(file_pattern, response)

            # Check 1: Validate expected deliverables are mentioned in response
            response_lower = response.lower()
            for expected_deliverable in expected_deliverables:
                expected_name = Path(expected_deliverable).name.lower()
                # Check if expected deliverable is mentioned in response
                if expected_name not in response_lower and expected_deliverable.lower() not in response_lower:
                    # Also check for partial matches (without extension)
                    expected_base = Path(expected_deliverable).stem.lower()
                    if expected_base not in response_lower:
                        detections.append(HallucinationDetection(
                            hallucination_type=HallucinationType.DELIVERABLE_CLAIM,
                            severity=0.7,
                            evidence=f"Expected deliverable '{expected_deliverable}' not mentioned in response",
                            suggestion="Ensure all expected deliverables are explicitly mentioned",
                            confidence_impact=0.3
                        ))

            # Check 2: Validate claimed files actually exist on disk
            for claimed_file in claimed_files:
                # Try both relative and absolute paths
                full_path = self.project_root / claimed_file
                if not full_path.exists():
                    # Check if it matches an expected deliverable (might be in different location)
                    claimed_name = Path(claimed_file).name.lower()
                    is_expected = claimed_name in expected_normalized

                    detections.append(HallucinationDetection(
                        hallucination_type=HallucinationType.DELIVERABLE_CLAIM,
                        severity=0.8 if is_expected else 0.6,
                        evidence=f"Claims deliverable exists: {claimed_file}",
                        suggestion="Verify file actually exists before claiming",
                        confidence_impact=0.4 if is_expected else 0.2
                    ))

            return detections

        except Exception as e:
            self.logger.error(f"Error in _detect_deliverable_hallucinations: {e}", exc_info=True)
            raise
    def _detect_context_drift(self, response: str, context: str) -> List[HallucinationDetection]:
        """Detect when response drifts from provided context"""
        detections = []

        # Simple check: response should reference context topics
        context_topics = set(re.findall(r'\b\w{4,}\b', context.lower()))
        response_topics = set(re.findall(r'\b\w{4,}\b', response.lower()))

        overlap = len(context_topics.intersection(response_topics))
        total_context_topics = len(context_topics)

        if total_context_topics > 0:
            topic_overlap_ratio = overlap / total_context_topics
            if topic_overlap_ratio < 0.3:  # Less than 30% topic overlap
                detections.append(HallucinationDetection(
                    hallucination_type=HallucinationType.CONTEXT_DRIFT,
                    severity=0.6,
                    evidence=f"Response covers only {topic_overlap_ratio:.1%} of context topics",
                    suggestion="Ensure response addresses the original query topics",
                    confidence_impact=0.2
                ))

        return detections

    def _detect_assumption_patterns(self, response: str) -> List[HallucinationDetection]:
        """Detect assumption patterns from SYPHON blacklist"""
        detections = []

        # Check against SYPHON assumption patterns
        assumption_indicators = [
            "probably", "assume", "should be", "likely", "presumably",
            "i think", "i believe", "seems like", "appears to"
        ]

        for indicator in assumption_indicators:
            if indicator in response.lower():
                detections.append(HallucinationDetection(
                    hallucination_type=HallucinationType.ASSUMPTION_WITHOUT_VERIFICATION,
                    severity=0.5,
                    evidence=f"Uses assumption language: '{indicator}'",
                    suggestion="Replace assumptions with verification",
                    confidence_impact=0.15
                ))

        return detections

    def _calculate_overall_confidence(self, scores: Dict[str, float], hallucinations: List[HallucinationDetection]) -> float:
        """Calculate overall confidence score"""
        # Base confidence from analysis scores
        base_confidence = (
            scores["semantic_coherence"] * 0.25 +
            scores["factual_grounding"] * 0.25 +
            scores["deliverable_alignment"] * 0.25 +
            scores["completion_claim_validity"] * 0.25
        )

        # Apply hallucination penalties
        total_penalty = sum(h.confidence_impact for h in hallucinations)
        final_confidence = max(0.0, base_confidence - total_penalty)

        return final_confidence

    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level from score"""
        if confidence >= self.thresholds["high"]:
            return ConfidenceLevel.HIGH
        elif confidence >= self.thresholds["medium"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _generate_recommendations(self, confidence_level: ConfidenceLevel, hallucinations: List[HallucinationDetection]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if confidence_level == ConfidenceLevel.LOW:
            recommendations.append("🚨 REQUIRES HUMAN REVIEW: Low confidence detected")
            recommendations.append("Do not proceed with automated workflow steps")

        elif confidence_level == ConfidenceLevel.MEDIUM:
            recommendations.append("⚠️ NEEDS VERIFICATION: Medium confidence - verify critical claims")
            recommendations.append("Consider human review for high-stakes decisions")

        else:
            recommendations.append("✅ SAFE TO PROCEED: High confidence analysis")

        # Add specific recommendations for detected hallucinations
        for hallucination in hallucinations:
            recommendations.append(f"🔧 {hallucination.hallucination_type.value.upper()}: {hallucination.suggestion}")

        return recommendations


def score_llm_confidence(prompt: str, response: str, **kwargs) -> ConfidenceScore:
    """
    Convenience function to score LLM confidence

    Args:
        prompt: Original prompt
        response: LLM response
        **kwargs: Additional arguments for analysis

    Returns:
        ConfidenceScore analysis
    """
    scorer = LLMConfidenceScorer()
    return scorer.analyze_llm_output(prompt, response, **kwargs)


def get_risk_level(confidence_score: ConfidenceScore) -> str:
    """
    Get human-readable risk level from confidence score

    Args:
        confidence_score: The confidence analysis result

    Returns:
        Risk level string
    """
    if confidence_score.confidence_level == ConfidenceLevel.HIGH:
        return "low"
    elif confidence_score.confidence_level == ConfidenceLevel.MEDIUM:
        return "medium"
    else:  # LOW
        if len(confidence_score.hallucinations_detected) > 2:
            return "critical"
        else:
            return "high"


def should_trust_llm_output(confidence_score: ConfidenceScore) -> bool:
    """
    Determine if LLM output should be trusted based on confidence analysis

    Args:
        confidence_score: The confidence analysis result

    Returns:
        True if output should be trusted (HIGH confidence only), False otherwise
        Note: MEDIUM confidence (0.5-0.8) requires review and should not be trusted automatically
    """
    # Only HIGH confidence should be trusted automatically
    # MEDIUM confidence (0.5-0.8) needs review per ConfidenceLevel enum documentation
    return confidence_score.confidence_level == ConfidenceLevel.HIGH


# Example usage and testing
if __name__ == "__main__":
    # Test the confidence scorer
    scorer = LLMConfidenceScorer()

    # Example of hallucinated response
    test_prompt = "Create a user authentication system"
    test_response = "I've created the authentication system. The login.py file handles user auth, register.py manages registration, and database.py connects to the database. Everything is 100% complete and working perfectly."

    score = scorer.analyze_llm_output(test_prompt, test_response)

    print(f"Confidence Score: {score.overall_confidence:.2f} ({score.confidence_level.value})")
    print(f"Semantic Coherence: {score.semantic_coherence:.2f}")
    print(f"Factual Grounding: {score.factual_grounding:.2f}")
    print(f"Deliverable Alignment: {score.deliverable_alignment:.2f}")
    print(f"Completion Validity: {score.completion_claim_validity:.2f}")

    print("\nDetected Hallucinations:")
    for h in score.hallucinations_detected:
        print(f"- {h.hallucination_type.value}: {h.evidence}")

    print("\nRecommendations:")
    for rec in score.recommendations:
        print(f"- {rec}")
