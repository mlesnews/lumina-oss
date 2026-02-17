#!/usr/bin/env python3
"""
@ASK Intent vs Implementation Comparison System

Compares original @ASK intent with actual implementation results,
feeds findings into the global master feedback "GOD LOOP" for continuous improvement.

This system enables real-world testing by:
1. Capturing original @ASK intent
2. Comparing with actual implementation
3. Identifying gaps, over-implementations, and misalignments
4. Feeding learnings into the global master feedback loop
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

class IntentAlignmentLevel(Enum):
    """Levels of alignment between intent and implementation"""
    PERFECT = "perfect"  # Implementation matches intent exactly
    GOOD = "good"  # Minor differences, intent fulfilled
    PARTIAL = "partial"  # Some intent fulfilled, gaps present
    MISALIGNED = "misaligned"  # Implementation doesn't match intent
    OPPOSITE = "opposite"  # Implementation contradicts intent

class LearningCategory(Enum):
    """Categories of learnings from comparison"""
    INTENT_CLARITY = "intent_clarity"  # Intent was unclear, led to misalignment
    IMPLEMENTATION_GAP = "implementation_gap"  # Missing features/functionality
    OVER_IMPLEMENTATION = "over_implementation"  # Added features not requested
    TECHNICAL_MISALIGNMENT = "technical_misalignment"  # Wrong technical approach
    SCOPE_DRIFT = "scope_drift"  # Scope expanded beyond intent
    QUALITY_ISSUE = "quality_issue"  # Implementation quality problems

@dataclass
class IntentCapture:
    """Captured intent from original @ASK"""
    ask_id: str
    original_ask: str
    extracted_intent: Dict[str, Any]
    intent_entities: List[str]
    intent_goals: List[str]
    intent_constraints: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImplementationResult:
    """Actual implementation results"""
    ask_id: str
    implemented_features: List[str]
    implementation_details: Dict[str, Any]
    files_created: List[str]
    files_modified: List[str]
    code_changes: Dict[str, Any]
    deliverables: List[str]
    completion_status: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class IntentImplementationComparison:
    """Comparison between intent and implementation"""
    ask_id: str
    intent: IntentCapture
    implementation: ImplementationResult
    alignment_level: IntentAlignmentLevel
    alignment_score: float  # 0.0 to 1.0
    gaps: List[str]  # Intent goals not implemented
    over_implementations: List[str]  # Features added beyond intent
    misalignments: List[str]  # Contradictions or wrong approaches
    learnings: List[Dict[str, Any]]  # Learnings from comparison
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FeedbackLoopEntry:
    """Entry for the global master feedback loop"""
    entry_id: str
    source: str  # "ask_intent_comparison"
    category: LearningCategory
    learning: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    priority: str  # "high", "medium", "low"
    timestamp: datetime = field(default_factory=datetime.now)
    impact_areas: List[str] = field(default_factory=list)

class ASKIntentComparisonSystem:
    """
    System for comparing @ASK intent with actual implementation
    and feeding learnings into the global master feedback loop
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the comparison system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ask_intent_comparison"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.intent_captures: Dict[str, IntentCapture] = {}
        self.implementation_results: Dict[str, ImplementationResult] = {}
        self.comparisons: Dict[str, IntentImplementationComparison] = {}
        self.feedback_entries: List[FeedbackLoopEntry] = []

    def capture_intent(self, ask_id: str, original_ask: str, context: Optional[Dict[str, Any]] = None) -> IntentCapture:
        """
        Capture the intent from an original @ASK

        Args:
            ask_id: Unique identifier for the @ASK
            original_ask: The original @ASK text
            context: Additional context (user info, session info, etc.)

        Returns:
            IntentCapture object
        """
        # Extract intent from @ASK
        extracted_intent = self._extract_intent(original_ask)
        intent_entities = self._extract_entities(original_ask)
        intent_goals = self._extract_goals(original_ask)
        intent_constraints = self._extract_constraints(original_ask)

        intent = IntentCapture(
            ask_id=ask_id,
            original_ask=original_ask,
            extracted_intent=extracted_intent,
            intent_entities=intent_entities,
            intent_goals=intent_goals,
            intent_constraints=intent_constraints,
            context=context or {}
        )

        self.intent_captures[ask_id] = intent
        self._save_intent_capture(intent)

        return intent

    def record_implementation(self, ask_id: str, implementation_data: Dict[str, Any]) -> ImplementationResult:
        """
        Record the actual implementation results

        Args:
            ask_id: The @ASK ID this implementation corresponds to
            implementation_data: Dictionary with implementation details

        Returns:
            ImplementationResult object
        """
        implementation = ImplementationResult(
            ask_id=ask_id,
            implemented_features=implementation_data.get("features", []),
            implementation_details=implementation_data.get("details", {}),
            files_created=implementation_data.get("files_created", []),
            files_modified=implementation_data.get("files_modified", []),
            code_changes=implementation_data.get("code_changes", {}),
            deliverables=implementation_data.get("deliverables", []),
            completion_status=implementation_data.get("completion_status", "unknown")
        )

        self.implementation_results[ask_id] = implementation
        self._save_implementation_result(implementation)

        return implementation

    def compare_intent_vs_implementation(self, ask_id: str) -> IntentImplementationComparison:
        """
        Compare the original intent with actual implementation

        Args:
            ask_id: The @ASK ID to compare

        Returns:
            IntentImplementationComparison object
        """
        if ask_id not in self.intent_captures:
            raise ValueError(f"Intent not captured for ask_id: {ask_id}")

        if ask_id not in self.implementation_results:
            raise ValueError(f"Implementation not recorded for ask_id: {ask_id}")

        intent = self.intent_captures[ask_id]
        implementation = self.implementation_results[ask_id]

        # Perform comparison
        alignment_score = self._calculate_alignment_score(intent, implementation)
        alignment_level = self._determine_alignment_level(alignment_score)

        gaps = self._identify_gaps(intent, implementation)
        over_implementations = self._identify_over_implementations(intent, implementation)
        misalignments = self._identify_misalignments(intent, implementation)

        # Generate learnings
        learnings = self._generate_learnings(intent, implementation, gaps, over_implementations, misalignments)

        comparison = IntentImplementationComparison(
            ask_id=ask_id,
            intent=intent,
            implementation=implementation,
            alignment_level=alignment_level,
            alignment_score=alignment_score,
            gaps=gaps,
            over_implementations=over_implementations,
            misalignments=misalignments,
            learnings=learnings
        )

        self.comparisons[ask_id] = comparison
        self._save_comparison(comparison)

        # Feed learnings into feedback loop
        self._feed_to_feedback_loop(comparison)

        return comparison

    def _extract_intent(self, ask_text: str) -> Dict[str, Any]:
        """Extract structured intent from @ASK text"""
        intent = {
            "action": self._extract_action(ask_text),
            "target": self._extract_target(ask_text),
            "requirements": self._extract_requirements(ask_text),
            "scope": self._extract_scope(ask_text)
        }
        return intent

    def _extract_action(self, text: str) -> str:
        """Extract the main action verb"""
        action_keywords = ["create", "implement", "build", "fix", "add", "update", "modify", "remove", "delete", "analyze", "generate"]
        text_lower = text.lower()
        for keyword in action_keywords:
            if keyword in text_lower:
                return keyword
        return "unknown"

    def _extract_target(self, text: str) -> str:
        """Extract the target of the action"""
        # Simple extraction - can be enhanced with NLP
        words = text.split()
        if len(words) > 1:
            # Take words after action verb
            action_idx = next((i for i, w in enumerate(words) if w.lower() in ["create", "implement", "build", "fix"]), 0)
            if action_idx < len(words) - 1:
                return " ".join(words[action_idx+1:action_idx+4])  # Next few words
        return "unknown"

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements/constraints"""
        requirements = []
        requirement_keywords = ["must", "should", "require", "need", "with", "including"]
        sentences = text.split(".")
        for sentence in sentences:
            for keyword in requirement_keywords:
                if keyword in sentence.lower():
                    requirements.append(sentence.strip())
        return requirements

    def _extract_scope(self, text: str) -> str:
        """Extract scope information"""
        scope_keywords = ["all", "every", "entire", "complete", "full", "system", "module"]
        text_lower = text.lower()
        for keyword in scope_keywords:
            if keyword in text_lower:
                return keyword
        return "specific"

    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities (nouns, proper nouns)"""
        # Simple extraction - can be enhanced
        words = text.split()
        # Capitalized words are likely entities
        entities = [w for w in words if w[0].isupper() and len(w) > 1]
        return entities

    def _extract_goals(self, text: str) -> List[str]:
        """Extract goals/objectives"""
        goals = []
        goal_patterns = [
            "to ", "so that", "in order to", "enable", "allow", "support"
        ]
        text_lower = text.lower()
        for pattern in goal_patterns:
            if pattern in text_lower:
                idx = text_lower.find(pattern)
                goal_text = text[idx:idx+100].split(".")[0]
                goals.append(goal_text.strip())
        return goals if goals else ["Complete the requested task"]

    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints/limitations"""
        constraints = []
        constraint_keywords = ["without", "avoid", "don't", "not", "except", "excluding"]
        sentences = text.split(".")
        for sentence in sentences:
            for keyword in constraint_keywords:
                if keyword in sentence.lower():
                    constraints.append(sentence.strip())
        return constraints

    def _calculate_alignment_score(self, intent: IntentCapture, implementation: ImplementationResult) -> float:
        """Calculate alignment score between intent and implementation (0.0 to 1.0)"""
        score = 0.0

        # Goal fulfillment (40%)
        goal_count = len(intent.intent_goals)
        if goal_count > 0:
            fulfilled_goals = sum(1 for goal in intent.intent_goals 
                                 if any(goal.lower() in feature.lower() or goal.lower() in deliverable.lower() 
                                       for feature in implementation.implemented_features 
                                       for deliverable in implementation.deliverables))
            goal_score = fulfilled_goals / goal_count
            score += goal_score * 0.4

        # Entity coverage (20%)
        entity_count = len(intent.intent_entities)
        if entity_count > 0:
            covered_entities = sum(1 for entity in intent.intent_entities 
                                 if any(entity.lower() in str(feature).lower() or entity.lower() in str(detail).lower()
                                       for feature in implementation.implemented_features
                                       for detail in implementation.implementation_details.values()))
            entity_score = covered_entities / entity_count
            score += entity_score * 0.2

        # Constraint adherence (20%)
        constraint_count = len(intent.intent_constraints)
        if constraint_count > 0:
            adhered_constraints = sum(1 for constraint in intent.intent_constraints
                                    if not any(constraint.lower() in str(feature).lower()
                                              for feature in implementation.implemented_features))
            constraint_score = adhered_constraints / constraint_count if constraint_count > 0 else 1.0
            score += constraint_score * 0.2

        # Completion status (20%)
        if implementation.completion_status in ["complete", "completed", "success"]:
            score += 0.2
        elif implementation.completion_status in ["partial", "in_progress"]:
            score += 0.1

        return min(1.0, max(0.0, score))

    def _determine_alignment_level(self, score: float) -> IntentAlignmentLevel:
        """Determine alignment level from score"""
        if score >= 0.95:
            return IntentAlignmentLevel.PERFECT
        elif score >= 0.75:
            return IntentAlignmentLevel.GOOD
        elif score >= 0.5:
            return IntentAlignmentLevel.PARTIAL
        elif score >= 0.25:
            return IntentAlignmentLevel.MISALIGNED
        else:
            return IntentAlignmentLevel.OPPOSITE

    def _identify_gaps(self, intent: IntentCapture, implementation: ImplementationResult) -> List[str]:
        """Identify gaps - intent goals not implemented"""
        gaps = []
        for goal in intent.intent_goals:
            goal_implemented = any(goal.lower() in feature.lower() or goal.lower() in deliverable.lower()
                                  for feature in implementation.implemented_features
                                  for deliverable in implementation.deliverables)
            if not goal_implemented:
                gaps.append(f"Goal not implemented: {goal}")

        # Check entities
        for entity in intent.intent_entities:
            entity_covered = any(entity.lower() in str(feature).lower() or entity.lower() in str(detail).lower()
                               for feature in implementation.implemented_features
                               for detail in implementation.implementation_details.values())
            if not entity_covered:
                gaps.append(f"Entity not covered: {entity}")

        return gaps

    def _identify_over_implementations(self, intent: IntentCapture, implementation: ImplementationResult) -> List[str]:
        """Identify over-implementations - features added beyond intent"""
        over_implementations = []

        # Compare features with intent goals
        intent_keywords = set()
        for goal in intent.intent_goals:
            intent_keywords.update(goal.lower().split())
        for entity in intent.intent_entities:
            intent_keywords.add(entity.lower())

        for feature in implementation.implemented_features:
            feature_keywords = set(feature.lower().split())
            overlap = feature_keywords & intent_keywords
            if len(overlap) == 0:  # No overlap with intent
                over_implementations.append(f"Feature beyond intent: {feature}")

        return over_implementations

    def _identify_misalignments(self, intent: IntentCapture, implementation: ImplementationResult) -> List[str]:
        """Identify misalignments - contradictions or wrong approaches"""
        misalignments = []

        # Check constraint violations
        for constraint in intent.intent_constraints:
            constraint_violated = any(constraint.lower() in str(feature).lower()
                                    for feature in implementation.implemented_features)
            if constraint_violated:
                misalignments.append(f"Constraint violated: {constraint}")

        return misalignments

    def _generate_learnings(self, intent: IntentCapture, implementation: ImplementationResult,
                          gaps: List[str], over_implementations: List[str], misalignments: List[str]) -> List[Dict[str, Any]]:
        """Generate learnings from the comparison"""
        learnings = []

        # Learning from gaps
        if gaps:
            learnings.append({
                "category": LearningCategory.IMPLEMENTATION_GAP.value,
                "learning": f"Intent goals not fully implemented: {len(gaps)} gaps identified",
                "evidence": {"gaps": gaps},
                "recommendation": "Improve intent extraction and implementation tracking"
            })

        # Learning from over-implementations
        if over_implementations:
            learnings.append({
                "category": LearningCategory.OVER_IMPLEMENTATION.value,
                "learning": f"Features added beyond intent: {len(over_implementations)} over-implementations",
                "evidence": {"over_implementations": over_implementations},
                "recommendation": "Clarify scope boundaries and stick to intent"
            })

        # Learning from misalignments
        if misalignments:
            learnings.append({
                "category": LearningCategory.SCOPE_DRIFT.value,
                "learning": f"Implementation contradicted intent: {len(misalignments)} misalignments",
                "evidence": {"misalignments": misalignments},
                "recommendation": "Improve constraint extraction and validation"
            })

        return learnings

    def _feed_to_feedback_loop(self, comparison: IntentImplementationComparison):
        """Feed learnings into the global master feedback loop"""
        for learning in comparison.learnings:
            entry_id = f"ask_intent_{comparison.ask_id}_{datetime.now().timestamp()}"

            # Determine priority
            priority = "high" if comparison.alignment_score < 0.5 else "medium" if comparison.alignment_score < 0.75 else "low"

            feedback_entry = FeedbackLoopEntry(
                entry_id=entry_id,
                source="ask_intent_comparison",
                category=LearningCategory(learning["category"]),
                learning=learning["learning"],
                evidence=learning["evidence"],
                recommendations=learning.get("recommendations", []),
                priority=priority,
                impact_areas=["intent_extraction", "implementation_tracking", "alignment_validation"]
            )

            self.feedback_entries.append(feedback_entry)
            self._save_feedback_entry(feedback_entry)

    def _save_intent_capture(self, intent: IntentCapture):
        try:
            """Save intent capture to file"""
            file_path = self.data_dir / f"intent_{intent.ask_id}.json"
            with open(file_path, 'w') as f:
                json.dump({
                    "ask_id": intent.ask_id,
                    "original_ask": intent.original_ask,
                    "extracted_intent": intent.extracted_intent,
                    "intent_entities": intent.intent_entities,
                    "intent_goals": intent.intent_goals,
                    "intent_constraints": intent.intent_constraints,
                    "timestamp": intent.timestamp.isoformat(),
                    "context": intent.context
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_intent_capture: {e}", exc_info=True)
            raise
    def _save_implementation_result(self, implementation: ImplementationResult):
        try:
            """Save implementation result to file"""
            file_path = self.data_dir / f"implementation_{implementation.ask_id}.json"
            with open(file_path, 'w') as f:
                json.dump({
                    "ask_id": implementation.ask_id,
                    "implemented_features": implementation.implemented_features,
                    "implementation_details": implementation.implementation_details,
                    "files_created": implementation.files_created,
                    "files_modified": implementation.files_modified,
                    "code_changes": implementation.code_changes,
                    "deliverables": implementation.deliverables,
                    "completion_status": implementation.completion_status,
                    "timestamp": implementation.timestamp.isoformat()
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_implementation_result: {e}", exc_info=True)
            raise
    def _save_comparison(self, comparison: IntentImplementationComparison):
        try:
            """Save comparison to file"""
            file_path = self.data_dir / f"comparison_{comparison.ask_id}.json"
            with open(file_path, 'w') as f:
                json.dump({
                    "ask_id": comparison.ask_id,
                    "alignment_level": comparison.alignment_level.value,
                    "alignment_score": comparison.alignment_score,
                    "gaps": comparison.gaps,
                    "over_implementations": comparison.over_implementations,
                    "misalignments": comparison.misalignments,
                    "learnings": comparison.learnings,
                    "timestamp": comparison.timestamp.isoformat()
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_comparison: {e}", exc_info=True)
            raise
    def _save_feedback_entry(self, entry: FeedbackLoopEntry):
        try:
            """Save feedback entry to global master feedback loop"""
            feedback_dir = self.project_root / "data" / "master_feedback_loop"
            feedback_dir.mkdir(parents=True, exist_ok=True)

            file_path = feedback_dir / f"feedback_{entry.entry_id}.json"
            with open(file_path, 'w') as f:
                json.dump({
                    "entry_id": entry.entry_id,
                    "source": entry.source,
                    "category": entry.category.value,
                    "learning": entry.learning,
                    "evidence": entry.evidence,
                    "recommendations": entry.recommendations,
                    "priority": entry.priority,
                    "timestamp": entry.timestamp.isoformat(),
                    "impact_areas": entry.impact_areas
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_feedback_entry: {e}", exc_info=True)
            raise
# Example usage
if __name__ == "__main__":
    print("🎯 @ASK Intent vs Implementation Comparison System")
    print("="*70)

    system = ASKIntentComparisonSystem()

    # Example: Capture intent from an @ASK
    ask_id = "example_001"
    original_ask = "Create a script to analyze workflow patterns and generate a report"

    print(f"\n1. Capturing intent from @ASK: {original_ask}")
    intent = system.capture_intent(ask_id, original_ask)
    print(f"   Intent goals: {intent.intent_goals}")
    print(f"   Intent entities: {intent.intent_entities}")

    # Example: Record implementation
    print(f"\n2. Recording implementation results...")
    implementation_data = {
        "features": ["pattern_analysis", "report_generation"],
        "files_created": ["analyze_patterns.py", "generate_report.py"],
        "deliverables": ["pattern_report.json"],
        "completion_status": "complete"
    }
    implementation = system.record_implementation(ask_id, implementation_data)
    print(f"   Implemented features: {implementation.implemented_features}")

    # Compare
    print(f"\n3. Comparing intent vs implementation...")
    comparison = system.compare_intent_vs_implementation(ask_id)
    print(f"   Alignment Score: {comparison.alignment_score:.2f}")
    print(f"   Alignment Level: {comparison.alignment_level.value}")
    print(f"   Gaps: {len(comparison.gaps)}")
    print(f"   Over-implementations: {len(comparison.over_implementations)}")
    print(f"   Learnings: {len(comparison.learnings)}")

    print(f"\n✅ Comparison complete. Feedbacks fed to global master feedback loop.")
    print("="*70)

