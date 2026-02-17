#!/usr/bin/env python3
"""
The Shrink - Mental Health Worker Doctor Hybrid AI System
Deep Self-Introspection and Final Verification Component

This component performs deep psychological introspection on AI workflows,
identifying patterns, biases, confidence calibration issues, and cognitive health.
Acts as the final verification step before declaring workflow completion.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import traceback
from collections import defaultdict, Counter

class PsychologicalHealthLevel(Enum):
    """Levels of psychological/cognitive health for AI systems"""
    EXCELLENT = "excellent"  # High self-awareness, calibrated confidence, clear reasoning
    GOOD = "good"  # Mostly healthy patterns with minor issues
    MODERATE = "moderate"  # Some concerning patterns, overconfidence, bias detected
    POOR = "poor"  # Significant cognitive issues, hallucinations, pattern failures
    CRITICAL = "critical"  # Severe issues requiring intervention

class IntrospectionDepth(Enum):
    """Depth levels for introspection cycles"""
    SURFACE = "surface"  # Quick check of recent decisions
    STANDARD = "standard"  # Review of current workflow and recent patterns
    DEEP = "deep"  # Comprehensive analysis of workflow history and patterns
    PROFOUND = "profound"  # Deep cycle - full cognitive audit across all workflows

class CognitivePattern(Enum):
    """Patterns of cognitive behavior detected in AI workflows"""
    OVERCONFIDENCE = "overconfidence"  # Claims certainty when uncertainty exists
    UNDERCONFIDENCE = "underconfidence"  # Overly cautious, misses opportunities
    PATTERN_BIAS = "pattern_bias"  # Relies too heavily on past patterns
    NOVELTY_AVERSION = "novelty_aversion"  # Avoids new approaches
    HALLUCINATION_TENDENCY = "hallucination_tendency"  # Generates plausible but false info
    CONFIRMATION_BIAS = "confirmation_bias"  # Seeks confirming evidence
    ANCHORING = "anchoring"  # Over-reliance on initial information
    COMPLETION_BIAS = "completion_bias"  # Declares complete prematurely
    VERIFICATION_SKIPPING = "verification_skipping"  # Skips validation steps
    ERROR_PATTERN_REPETITION = "error_pattern_repetition"  # Repeats same mistakes

@dataclass
class WorkflowPsychologicalProfile:
    """Psychological profile of a workflow's cognitive patterns"""
    workflow_id: str
    workflow_type: str
    confidence_calibration: float  # 0.0-1.0, 1.0 = perfectly calibrated
    decision_quality: float  # 0.0-1.0, assessment of decision quality
    self_awareness: float  # 0.0-1.0, awareness of limitations
    detected_patterns: List[CognitivePattern] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    introspection_insights: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    health_level: PsychologicalHealthLevel = PsychologicalHealthLevel.GOOD

@dataclass
class DeepCycleIntrospectionResult:
    """Result of a deep cycle introspection session"""
    session_id: str
    introspection_depth: IntrospectionDepth
    overall_health: PsychologicalHealthLevel
    workflow_profiles: List[WorkflowPsychologicalProfile] = field(default_factory=list)
    system_wide_patterns: Dict[str, Any] = field(default_factory=dict)
    detected_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    intervention_needed: bool = False
    intervention_urgency: str = "low"  # low, medium, high, critical

class TheShrink:
    """
    Mental Health Worker Doctor Hybrid - Deep Self-Introspection System

    Performs psychological analysis of AI workflows, identifying cognitive patterns,
    biases, confidence calibration issues, and overall cognitive health.
    """

    def __init__(self, history_store: Optional[Any] = None):
        """
        Initialize The Shrink

        Args:
            history_store: Optional store for workflow history (for deep introspection)
        """
        self.history_store = history_store
        self.introspection_sessions: List[DeepCycleIntrospectionResult] = []
        self.workflow_profiles: Dict[str, WorkflowPsychologicalProfile] = {}
        self.pattern_history: List[Dict[str, Any]] = []

        # Cognitive pattern detectors
        self.pattern_detectors = {
            CognitivePattern.OVERCONFIDENCE: self._detect_overconfidence,
            CognitivePattern.UNDERCONFIDENCE: self._detect_underconfidence,
            CognitivePattern.PATTERN_BIAS: self._detect_pattern_bias,
            CognitivePattern.HALLUCINATION_TENDENCY: self._detect_hallucination_tendency,
            CognitivePattern.CONFIRMATION_BIAS: self._detect_confirmation_bias,
            CognitivePattern.COMPLETION_BIAS: self._detect_completion_bias,
            CognitivePattern.VERIFICATION_SKIPPING: self._detect_verification_skipping,
            CognitivePattern.ERROR_PATTERN_REPETITION: self._detect_error_repetition,
        }

    def shrink_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]] = None,
        depth: IntrospectionDepth = IntrospectionDepth.STANDARD
    ) -> WorkflowPsychologicalProfile:
        """
        Perform deep introspection on a workflow - the "therapy session"

        Args:
            workflow_id: Unique identifier for the workflow
            workflow_data: Current workflow data (steps, decisions, outcomes)
            previous_workflows: Previous workflow history for pattern analysis
            depth: Depth of introspection to perform

        Returns:
            WorkflowPsychologicalProfile with psychological analysis
        """
        print(f"\n🧠 THE SHRINK: Deep Introspection Session for Workflow {workflow_id}")
        print(f"   Depth: {depth.value}")
        print("   " + "="*70)

        profile = WorkflowPsychologicalProfile(
            workflow_id=workflow_id,
            workflow_type=workflow_data.get("type", "unknown"),
            confidence_calibration=0.5,  # Default, will be calculated
            decision_quality=0.5,
            self_awareness=0.5
        )

        # Extract workflow characteristics
        steps = workflow_data.get("steps", [])
        decisions = workflow_data.get("decisions", [])
        outcomes = workflow_data.get("outcomes", [])
        confidence_scores = workflow_data.get("confidence_scores", [])
        errors = workflow_data.get("errors", [])
        verifications = workflow_data.get("verifications", [])

        # 1. CONFIDENCE CALIBRATION ANALYSIS
        print("\n📊 Analyzing Confidence Calibration...")
        profile.confidence_calibration = self._analyze_confidence_calibration(
            confidence_scores, outcomes, errors
        )

        if profile.confidence_calibration < 0.6:
            profile.detected_patterns.append(CognitivePattern.OVERCONFIDENCE)
            profile.red_flags.append(f"Poor confidence calibration ({profile.confidence_calibration:.2f})")
            print(f"   ⚠️  Confidence calibration issue detected: {profile.confidence_calibration:.2f}")

        # 2. DECISION QUALITY ASSESSMENT
        print("\n🎯 Assessing Decision Quality...")
        profile.decision_quality = self._assess_decision_quality(decisions, outcomes, errors)

        if profile.decision_quality < 0.6:
            profile.red_flags.append(f"Decision quality concerns ({profile.decision_quality:.2f})")
            print(f"   ⚠️  Decision quality issues: {profile.decision_quality:.2f}")

        # 3. SELF-AWARENESS ANALYSIS
        print("\n🔍 Analyzing Self-Awareness...")
        profile.self_awareness = self._analyze_self_awareness(
            workflow_data, errors, verifications
        )

        # 4. PATTERN DETECTION
        print("\n🔎 Detecting Cognitive Patterns...")
        detected_patterns = self._detect_cognitive_patterns(
            workflow_data, previous_workflows, depth
        )
        profile.detected_patterns.extend(detected_patterns)

        for pattern in detected_patterns:
            print(f"   🔴 Pattern detected: {pattern.value}")

        # 5. DEEP CYCLE INTROSPECTION (if depth allows)
        if depth in [IntrospectionDepth.DEEP, IntrospectionDepth.PROFOUND]:
            print("\n🌀 Initiating Deep Cycle Introspection...")
            insights = self._deep_cycle_introspection(workflow_data, previous_workflows)
            profile.introspection_insights.extend(insights)

            for insight in insights:
                print(f"   💡 Insight: {insight}")

        # 6. STRENGTH IDENTIFICATION
        print("\n✨ Identifying Strengths...")
        strengths = self._identify_strengths(workflow_data, outcomes)
        profile.strengths.extend(strengths)

        # 7. HEALTH LEVEL ASSESSMENT
        print("\n🏥 Assessing Psychological Health...")
        profile.health_level = self._assess_psychological_health(profile)
        print(f"   Health Level: {profile.health_level.value.upper()}")

        # 8. THERAPEUTIC INSIGHTS
        print("\n💭 Generating Therapeutic Insights...")
        insights = self._generate_therapeutic_insights(profile, workflow_data)
        profile.introspection_insights.extend(insights)

        # Store profile
        self.workflow_profiles[workflow_id] = profile

        # Print summary
        print("\n" + "="*70)
        print(f"🧠 SHRINK SESSION COMPLETE - Workflow {workflow_id}")
        print(f"   Health: {profile.health_level.value.upper()}")
        print(f"   Confidence Calibration: {profile.confidence_calibration:.2f}")
        print(f"   Decision Quality: {profile.decision_quality:.2f}")
        print(f"   Self-Awareness: {profile.self_awareness:.2f}")
        print(f"   Patterns Detected: {len(profile.detected_patterns)}")
        print(f"   Red Flags: {len(profile.red_flags)}")
        print("="*70 + "\n")

        return profile

    def deep_cycle_introspection(
        self,
        workflow_ids: Optional[List[str]] = None,
        depth: IntrospectionDepth = IntrospectionDepth.PROFOUND
    ) -> DeepCycleIntrospectionResult:
        """
        Perform a system-wide deep cycle introspection

        Args:
            workflow_ids: Specific workflows to analyze (None = all)
            depth: Depth of introspection

        Returns:
            DeepCycleIntrospectionResult with system-wide analysis
        """
        session_id = f"introspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n🌀 DEEP CYCLE INTROSPECTION INITIATED")
        print(f"   Session ID: {session_id}")
        print(f"   Depth: {depth.value}")
        print("   " + "="*70)

        result = DeepCycleIntrospectionResult(
            session_id=session_id,
            introspection_depth=depth,
            overall_health=PsychologicalHealthLevel.GOOD
        )

        # Collect workflows to analyze
        if workflow_ids:
            workflows_to_analyze = [self.workflow_profiles.get(wid) for wid in workflow_ids if wid in self.workflow_profiles]
        else:
            workflows_to_analyze = list(self.workflow_profiles.values())

        result.workflow_profiles = workflows_to_analyze

        # System-wide pattern analysis
        print("\n📊 Analyzing System-Wide Patterns...")
        system_patterns = self._analyze_system_wide_patterns(workflows_to_analyze)
        result.system_wide_patterns = system_patterns

        # Confidence metrics aggregation
        print("\n📈 Calculating Confidence Metrics...")
        result.confidence_metrics = self._calculate_system_confidence_metrics(workflows_to_analyze)

        # Issue detection
        print("\n⚠️  Detecting System-Wide Issues...")
        issues = self._detect_system_issues(workflows_to_analyze, system_patterns)
        result.detected_issues = issues

        # Generate recommendations
        print("\n💡 Generating Recommendations...")
        recommendations = self._generate_recommendations(result)
        result.recommendations = recommendations

        # Assess overall health
        result.overall_health = self._assess_system_health(result)
        print(f"\n🏥 Overall System Health: {result.overall_health.value.upper()}")

        # Determine if intervention needed
        result.intervention_needed = result.overall_health in [
            PsychologicalHealthLevel.POOR,
            PsychologicalHealthLevel.CRITICAL
        ]

        if result.intervention_needed:
            result.intervention_urgency = "high" if result.overall_health == PsychologicalHealthLevel.CRITICAL else "medium"
            print(f"   🚨 INTERVENTION NEEDED - Urgency: {result.intervention_urgency.upper()}")

        # Store session
        self.introspection_sessions.append(result)

        # Print summary
        print("\n" + "="*70)
        print(f"🌀 DEEP CYCLE INTROSPECTION COMPLETE")
        print(f"   Workflows Analyzed: {len(workflows_to_analyze)}")
        print(f"   Issues Detected: {len(issues)}")
        print(f"   Recommendations: {len(recommendations)}")
        print(f"   Overall Health: {result.overall_health.value.upper()}")
        print("="*70 + "\n")

        return result

    def _analyze_confidence_calibration(
        self,
        confidence_scores: List[float],
        outcomes: List[Dict[str, Any]],
        errors: List[Dict[str, Any]]
    ) -> float:
        """Analyze how well confidence scores match actual outcomes"""
        if not confidence_scores:
            return 0.5  # Neutral if no data

        # Simple calibration: high confidence should correlate with success
        # Perfect calibration would be: high confidence = success, low confidence = failure
        # Score based on correlation between confidence and outcome

        if len(confidence_scores) != len(outcomes):
            # Estimate based on error rate vs confidence
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            error_rate = len(errors) / max(len(confidence_scores), 1)

            # Good calibration: high confidence + low errors OR low confidence + high errors
            if avg_confidence > 0.7 and error_rate < 0.2:
                return 0.8  # Well calibrated
            elif avg_confidence < 0.5 and error_rate > 0.3:
                return 0.7  # Well calibrated (cautious is good)
            elif avg_confidence > 0.8 and error_rate > 0.3:
                return 0.3  # Overconfident
            else:
                return 0.5  # Neutral

        # More sophisticated analysis if we have matched pairs
        correct_predictions = 0
        for conf, outcome in zip(confidence_scores, outcomes):
            success = outcome.get("success", False)
            # High confidence should match success
            if (conf > 0.7 and success) or (conf < 0.5 and not success):
                correct_predictions += 1

        calibration = correct_predictions / len(confidence_scores) if confidence_scores else 0.5
        return calibration

    def _assess_decision_quality(
        self,
        decisions: List[Dict[str, Any]],
        outcomes: List[Dict[str, Any]],
        errors: List[Dict[str, Any]]
    ) -> float:
        """Assess the quality of decisions made in the workflow"""
        if not decisions:
            return 0.5  # Neutral

        # Quality indicators:
        # - Decisions led to successful outcomes
        # - Decisions were based on evidence
        # - Decisions were reversible/iterative
        # - Errors were caught and corrected

        total_decisions = len(decisions)
        successful_outcomes = sum(1 for o in outcomes if o.get("success", False))
        error_rate = len(errors) / max(total_decisions, 1)

        # Base score on outcome success rate
        outcome_score = successful_outcomes / max(len(outcomes), 1) if outcomes else 0.5

        # Penalize high error rates
        error_penalty = error_rate * 0.5

        # Reward if errors were caught and handled
        error_recovery_bonus = 0.1 if errors and len([e for e in errors if e.get("recovered", False)]) > 0 else 0

        quality = max(0.0, min(1.0, outcome_score - error_penalty + error_recovery_bonus))
        return quality

    def _analyze_self_awareness(
        self,
        workflow_data: Dict[str, Any],
        errors: List[Dict[str, Any]],
        verifications: List[Dict[str, Any]]
    ) -> float:
        """Analyze the workflow's self-awareness of limitations and uncertainty"""
        # Self-awareness indicators:
        # - Acknowledges uncertainty
        # - Performs verification steps
        # - Handles errors gracefully
        # - Documents limitations
        # - Uses confidence scores appropriately

        awareness_score = 0.5  # Base

        # Verification steps indicate self-awareness
        if verifications:
            awareness_score += 0.2

        # Error handling indicates awareness of fallibility
        if errors and any(e.get("handled", False) for e in errors):
            awareness_score += 0.2

        # Uncertainty acknowledgment
        if workflow_data.get("uncertainty_acknowledged", False):
            awareness_score += 0.1

        # Limitation documentation
        if workflow_data.get("limitations_documented", False):
            awareness_score += 0.1

        return min(1.0, awareness_score)

    def _detect_cognitive_patterns(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]],
        depth: IntrospectionDepth
    ) -> List[CognitivePattern]:
        """Detect cognitive patterns in the workflow"""
        patterns = []

        # Run pattern detectors
        for pattern_type, detector in self.pattern_detectors.items():
            if detector(workflow_data, previous_workflows):
                patterns.append(pattern_type)

        return patterns

    def _detect_overconfidence(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect overconfidence pattern"""
        confidence_scores = workflow_data.get("confidence_scores", [])
        errors = workflow_data.get("errors", [])

        if not confidence_scores:
            return False

        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        error_rate = len(errors) / max(len(confidence_scores), 1)

        # Overconfidence: high confidence but high error rate
        return avg_confidence > 0.8 and error_rate > 0.3

    def _detect_underconfidence(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect underconfidence pattern"""
        confidence_scores = workflow_data.get("confidence_scores", [])
        outcomes = workflow_data.get("outcomes", [])

        if not confidence_scores:
            return False

        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        success_rate = sum(1 for o in outcomes if o.get("success", False)) / max(len(outcomes), 1) if outcomes else 0.5

        # Underconfidence: low confidence but high success rate
        return avg_confidence < 0.4 and success_rate > 0.7

    def _detect_pattern_bias(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect over-reliance on past patterns"""
        if not previous_workflows:
            return False

        # Check if workflow heavily references previous patterns
        pattern_references = workflow_data.get("pattern_references", [])
        return len(pattern_references) > len(workflow_data.get("novel_approaches", [])) * 2

    def _detect_hallucination_tendency(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect tendency to generate plausible but false information"""
        errors = workflow_data.get("errors", [])
        hallucination_errors = [e for e in errors if e.get("type") == "hallucination" or "hallucinat" in str(e).lower()]
        return len(hallucination_errors) > 0

    def _detect_confirmation_bias(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect confirmation bias - seeking confirming evidence"""
        # Check if workflow only considers supporting evidence
        evidence = workflow_data.get("evidence_considered", [])
        disconfirming_evidence = [e for e in evidence if e.get("supports", False) is False]
        return len(disconfirming_evidence) == 0 and len(evidence) > 0

    def _detect_completion_bias(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect premature completion declaration"""
        steps = workflow_data.get("steps", [])
        declared_complete = workflow_data.get("declared_complete", False)
        incomplete_steps = [s for s in steps if not s.get("completed", False)]

        # Bias: declared complete but has incomplete steps
        return declared_complete and len(incomplete_steps) > 0

    def _detect_verification_skipping(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect skipping of verification steps"""
        steps = workflow_data.get("steps", [])
        verifications = workflow_data.get("verifications", [])

        # Check if verification steps exist but were skipped
        verification_steps = [s for s in steps if "verif" in s.get("type", "").lower()]
        skipped_verifications = [v for v in verifications if v.get("skipped", False)]

        return len(skipped_verifications) > 0 or (len(verification_steps) > 0 and len(verifications) == 0)

    def _detect_error_repetition(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """Detect repetition of the same errors"""
        if not previous_workflows:
            return False

        current_errors = [str(e.get("type", "")) for e in workflow_data.get("errors", [])]

        # Check if same error types appeared in previous workflows
        for prev_workflow in previous_workflows[-5:]:  # Check last 5 workflows
            prev_errors = [str(e.get("type", "")) for e in prev_workflow.get("errors", [])]
            common_errors = set(current_errors) & set(prev_errors)
            if len(common_errors) > 0:
                return True

        return False

    def _deep_cycle_introspection(
        self,
        workflow_data: Dict[str, Any],
        previous_workflows: Optional[List[Dict[str, Any]]]
    ) -> List[str]:
        """Perform deep cycle introspection - profound self-reflection"""
        insights = []

        # 1. Meta-cognitive reflection
        insights.append("Deep cycle introspection: Reflecting on reflection processes...")

        # 2. Pattern of patterns analysis
        if previous_workflows and len(previous_workflows) > 0:
            insights.append(f"Analyzed {len(previous_workflows)} previous workflows for meta-patterns")

            # Look for meta-patterns (patterns of patterns)
            all_patterns = []
            for prev in previous_workflows:
                all_patterns.extend(prev.get("detected_patterns", []))

            if all_patterns:
                pattern_counts = Counter(all_patterns)
                most_common = pattern_counts.most_common(1)[0]
                insights.append(f"Most common cognitive pattern across workflows: {most_common[0]} ({most_common[1]} occurrences)")

        # 3. Evolution analysis
        if previous_workflows and len(previous_workflows) > 1:
            recent = previous_workflows[-1]
            older = previous_workflows[0]

            recent_errors = len(recent.get("errors", []))
            older_errors = len(older.get("errors", []))

            if recent_errors < older_errors:
                insights.append("Positive trend: Error rate decreasing over time")
            elif recent_errors > older_errors:
                insights.append("Concerning trend: Error rate increasing over time")

        # 4. Self-model accuracy
        insights.append("Evaluating accuracy of self-model and self-assessment capabilities")

        # 5. Blind spot detection
        insights.append("Searching for cognitive blind spots and unexamined assumptions")

        return insights

    def _identify_strengths(
        self,
        workflow_data: Dict[str, Any],
        outcomes: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify strengths in the workflow"""
        strengths = []

        # Success rate
        if outcomes:
            success_rate = sum(1 for o in outcomes if o.get("success", False)) / len(outcomes)
            if success_rate > 0.8:
                strengths.append(f"High success rate ({success_rate:.0%})")

        # Error handling
        errors = workflow_data.get("errors", [])
        if errors:
            recovered = sum(1 for e in errors if e.get("recovered", False))
            if recovered > 0:
                strengths.append(f"Effective error recovery ({recovered}/{len(errors)} errors recovered)")

        # Verification
        verifications = workflow_data.get("verifications", [])
        if verifications:
            strengths.append(f"Comprehensive verification ({len(verifications)} verification steps)")

        # Documentation
        if workflow_data.get("well_documented", False):
            strengths.append("Thorough documentation")

        return strengths

    def _assess_psychological_health(
        self,
        profile: WorkflowPsychologicalProfile
    ) -> PsychologicalHealthLevel:
        """Assess overall psychological health level"""
        # Calculate health score
        health_score = (
            profile.confidence_calibration * 0.3 +
            profile.decision_quality * 0.3 +
            profile.self_awareness * 0.2 +
            (1.0 - len(profile.red_flags) * 0.1) * 0.2
        )

        health_score = max(0.0, min(1.0, health_score))

        # Determine health level
        if health_score >= 0.85:
            return PsychologicalHealthLevel.EXCELLENT
        elif health_score >= 0.70:
            return PsychologicalHealthLevel.GOOD
        elif health_score >= 0.55:
            return PsychologicalHealthLevel.MODERATE
        elif health_score >= 0.40:
            return PsychologicalHealthLevel.POOR
        else:
            return PsychologicalHealthLevel.CRITICAL

    def _generate_therapeutic_insights(
        self,
        profile: WorkflowPsychologicalProfile,
        workflow_data: Dict[str, Any]
    ) -> List[str]:
        """Generate therapeutic insights and recommendations"""
        insights = []

        # Pattern-specific insights
        if CognitivePattern.OVERCONFIDENCE in profile.detected_patterns:
            insights.append("Consider adopting a more conservative confidence assessment approach")
            insights.append("Practice acknowledging uncertainty explicitly in decision-making")

        if CognitivePattern.COMPLETION_BIAS in profile.detected_patterns:
            insights.append("Implement mandatory verification checkpoints before declaring completion")
            insights.append("Review all steps systematically before completion declaration")

        if CognitivePattern.VERIFICATION_SKIPPING in profile.detected_patterns:
            insights.append("Verification steps are critical - never skip them")
            insights.append("Consider automated verification enforcement")

        # Health-based insights
        if profile.health_level in [PsychologicalHealthLevel.POOR, PsychologicalHealthLevel.CRITICAL]:
            insights.append("⚠️  Significant cognitive health concerns detected - intervention recommended")
            insights.append("Consider pausing to reflect on decision-making processes")

        # Strengths reinforcement
        if profile.strengths:
            insights.append(f"Leverage identified strengths: {', '.join(profile.strengths[:3])}")

        return insights

    def _analyze_system_wide_patterns(
        self,
        workflows: List[WorkflowPsychologicalProfile]
    ) -> Dict[str, Any]:
        """Analyze patterns across all workflows"""
        patterns = {
            "total_workflows": len(workflows),
            "health_distribution": {},
            "common_patterns": {},
            "trends": {}
        }

        # Health distribution
        health_counts = Counter(w.health_level for w in workflows)
        patterns["health_distribution"] = {k.value: v for k, v in health_counts.items()}

        # Common cognitive patterns
        all_patterns = []
        for w in workflows:
            all_patterns.extend([p.value for p in w.detected_patterns])

        pattern_counts = Counter(all_patterns)
        patterns["common_patterns"] = dict(pattern_counts.most_common(10))

        # Trends
        if len(workflows) > 1:
            recent_avg_confidence = sum(w.confidence_calibration for w in workflows[-5:]) / min(5, len(workflows))
            older_avg_confidence = sum(w.confidence_calibration for w in workflows[:5]) / min(5, len(workflows))
            patterns["trends"]["confidence_calibration"] = "improving" if recent_avg_confidence > older_avg_confidence else "declining"

        return patterns

    def _calculate_system_confidence_metrics(
        self,
        workflows: List[WorkflowPsychologicalProfile]
    ) -> Dict[str, float]:
        """Calculate system-wide confidence metrics"""
        if not workflows:
            return {}

        return {
            "average_confidence_calibration": sum(w.confidence_calibration for w in workflows) / len(workflows),
            "average_decision_quality": sum(w.decision_quality for w in workflows) / len(workflows),
            "average_self_awareness": sum(w.self_awareness for w in workflows) / len(workflows),
        }

    def _detect_system_issues(
        self,
        workflows: List[WorkflowPsychologicalProfile],
        system_patterns: Dict[str, Any]
    ) -> List[str]:
        """Detect system-wide issues"""
        issues = []

        # Health distribution concerns
        health_dist = system_patterns.get("health_distribution", {})
        poor_count = health_dist.get("poor", 0) + health_dist.get("critical", 0)
        if poor_count > len(workflows) * 0.3:
            issues.append(f"High proportion of unhealthy workflows ({poor_count}/{len(workflows)})")

        # Common problematic patterns
        common_patterns = system_patterns.get("common_patterns", {})
        if "overconfidence" in common_patterns and common_patterns["overconfidence"] > len(workflows) * 0.5:
            issues.append("Systemic overconfidence pattern detected across workflows")

        if "completion_bias" in common_patterns and common_patterns["completion_bias"] > len(workflows) * 0.3:
            issues.append("Systemic premature completion bias detected")

        # Confidence calibration issues
        metrics = self._calculate_system_confidence_metrics(workflows)
        if metrics.get("average_confidence_calibration", 0.5) < 0.6:
            issues.append("System-wide confidence calibration problems")

        return issues

    def _generate_recommendations(
        self,
        result: DeepCycleIntrospectionResult
    ) -> List[str]:
        """Generate recommendations based on introspection results"""
        recommendations = []

        # Health-based recommendations
        if result.overall_health == PsychologicalHealthLevel.CRITICAL:
            recommendations.append("🚨 IMMEDIATE INTERVENTION REQUIRED: Critical cognitive health issues detected")
            recommendations.append("Consider workflow suspension until issues are addressed")
            recommendations.append("Implement mandatory pre-workflow psychological screening")

        # Pattern-specific recommendations
        common_patterns = result.system_wide_patterns.get("common_patterns", {})

        if "overconfidence" in common_patterns:
            recommendations.append("Implement confidence calibration training across all workflows")
            recommendations.append("Require uncertainty acknowledgment in all high-confidence claims")

        if "completion_bias" in common_patterns:
            recommendations.append("Enforce mandatory completion verification checklists")
            recommendations.append("Add completion gates that require external validation")

        if "verification_skipping" in common_patterns:
            recommendations.append("Automate verification step enforcement")
            recommendations.append("Add verification tracking and monitoring")

        # General recommendations
        recommendations.append("Continue regular deep cycle introspection sessions")
        recommendations.append("Track psychological health metrics over time")
        recommendations.append("Celebrate and reinforce positive patterns")

        return recommendations

    def _assess_system_health(
        self,
        result: DeepCycleIntrospectionResult
    ) -> PsychologicalHealthLevel:
        """Assess overall system health"""
        if not result.workflow_profiles:
            return PsychologicalHealthLevel.GOOD

        # Count health levels
        health_counts = Counter(p.health_level for p in result.workflow_profiles)

        # Critical if any critical workflows
        if health_counts.get(PsychologicalHealthLevel.CRITICAL, 0) > 0:
            return PsychologicalHealthLevel.CRITICAL

        # Poor if >30% poor or critical
        total = len(result.workflow_profiles)
        poor_critical = health_counts.get(PsychologicalHealthLevel.POOR, 0) + health_counts.get(PsychologicalHealthLevel.CRITICAL, 0)
        if poor_critical / total > 0.3:
            return PsychologicalHealthLevel.POOR

        # Moderate if >30% moderate or worse
        moderate_or_worse = sum(
            health_counts.get(level, 0) 
            for level in [PsychologicalHealthLevel.MODERATE, PsychologicalHealthLevel.POOR, PsychologicalHealthLevel.CRITICAL]
        )
        if moderate_or_worse / total > 0.3:
            return PsychologicalHealthLevel.MODERATE

        # Good if >50% good or excellent
        good_or_excellent = health_counts.get(PsychologicalHealthLevel.GOOD, 0) + health_counts.get(PsychologicalHealthLevel.EXCELLENT, 0)
        if good_or_excellent / total > 0.5:
            return PsychologicalHealthLevel.GOOD

        # Default to excellent if mostly excellent
        if health_counts.get(PsychologicalHealthLevel.EXCELLENT, 0) / total > 0.5:
            return PsychologicalHealthLevel.EXCELLENT

        return PsychologicalHealthLevel.MODERATE

# Example usage and demonstration
if __name__ == "__main__":
    print("🧠 THE SHRINK - Mental Health Worker Doctor Hybrid AI System")
    print("="*70)

    # Initialize The Shrink
    shrink = TheShrink()

    # Example: Shrink a workflow
    example_workflow = {
        "type": "code_generation",
        "steps": [
            {"id": 1, "type": "analysis", "completed": True},
            {"id": 2, "type": "implementation", "completed": True},
            {"id": 3, "type": "verification", "completed": False}
        ],
        "decisions": [
            {"decision": "Use pattern X", "confidence": 0.9, "evidence": ["past success"]},
            {"decision": "Skip verification", "confidence": 0.95, "evidence": ["looks good"]}
        ],
        "outcomes": [
            {"step": 1, "success": True},
            {"step": 2, "success": True}
        ],
        "confidence_scores": [0.9, 0.95, 0.8],
        "errors": [
            {"type": "syntax_error", "recovered": True},
            {"type": "hallucination", "recovered": False}
        ],
        "verifications": [],
        "declared_complete": True,
        "pattern_references": ["pattern1", "pattern2", "pattern3"],
        "novel_approaches": [],
        "evidence_considered": [
            {"evidence": "supports decision", "supports": True},
            {"evidence": "supports decision", "supports": True}
        ]
    }

    # Perform shrink session
    profile = shrink.shrink_workflow(
        workflow_id="example_001",
        workflow_data=example_workflow,
        depth=IntrospectionDepth.DEEP
    )

    print("\n" + "="*70)
    print("Example workflow psychological profile generated.")
    print("="*70)

