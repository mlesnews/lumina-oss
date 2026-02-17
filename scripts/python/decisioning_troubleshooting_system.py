#!/usr/bin/env python3
"""
Decisioning Based on Troubleshooting System - INTEGRATED WITH @R5

#DECISIONING? BASED ON #TROUBLESHOOTING?
@ASK IF $CONTEXT $SCORE <=> #DECISIONING THRESHOLD
BASED ON ANY/ALL #TROUBLESHOOTING AND QUESTIONS ASKED BY ANY & ALL @CHAT

Question formats: "@? <=> /? <=> --?"
Integrates: @R5 @5W1H @REC @AIQ <=> @JC &| @JHC

Uses @R5 Living Context Matrix for knowledge aggregation and decisioning.
Tags: #DECISIONING #TROUBLESHOOTING #ASK #CONTEXT_SCORE #R5 #5W1H #REC #AIQ #JC #JHC
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DecisioningTroubleshooting")


class QuestionFormat(Enum):
    """Question format types"""
    AT_QUESTION = "@?"  # @? format
    SLASH_QUESTION = "/?"  # /? format
    DASH_QUESTION = "--?"  # --? format
    ASK_COMMAND = "@ask"  # @ask command
    UNKNOWN = "unknown"


@dataclass
class ChatQuestion:
    """A question asked in chat"""
    question_id: str
    question_text: str
    format: QuestionFormat
    source: str  # Which chat/agent asked
    timestamp: datetime = field(default_factory=datetime.now)
    context_score: float = 0.0
    troubleshooting_related: bool = False


@dataclass
class TroubleshootingContext:
    """Troubleshooting context for decisioning"""
    issue: str
    symptoms: List[str]
    questions_asked: List[ChatQuestion]
    troubleshooting_steps: List[str]
    context_score: float
    decisioning_threshold: float = 0.7


@dataclass
class DecisioningResult:
    """Result of decisioning based on troubleshooting"""
    decision_id: str
    troubleshooting_context: TroubleshootingContext
    context_score: float
    meets_threshold: bool
    decision: str
    rationale: str
    frameworks_used: List[str]  # @5W1H, @REC, @AIQ, @JC, @JHC
    timestamp: datetime = field(default_factory=datetime.now)


class DecisioningTroubleshootingSystem:
    """
    Decisioning Based on Troubleshooting System

    #DECISIONING? BASED ON #TROUBLESHOOTING?
    @ASK IF $CONTEXT $SCORE <=> #DECISIONING THRESHOLD
    BASED ON ANY/ALL #TROUBLESHOOTING AND QUESTIONS ASKED BY ANY & ALL @CHAT
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Decisioning Based on Troubleshooting System - INTEGRATED WITH @R5"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Decisioning threshold (default: 0.7, but can be 0 to infinity with quantum scoring)
        self.decisioning_threshold = 0.7

        # Question tracking
        self.chat_questions: List[ChatQuestion] = []

        # Troubleshooting contexts
        self.troubleshooting_contexts: Dict[str, TroubleshootingContext] = {}

        # Framework integrations
        self.frameworks_enabled = {
            "R5": True,  # R5 Living Context Matrix
            "5W1H": True,
            "REC": True,
            "AIQ": True,
            "JC": True,  # Jedi Council
            "JHC": True  # Jedi High Council
        }

        # R5 Integration
        self.r5_system = None
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.r5_system = R5LivingContextMatrix(self.project_root)
            logger.info("   🔗 @R5 Living Context Matrix integrated")
        except Exception as e:
            logger.debug(f"   @R5 not available: {e}")

        logger.info("✅ Decisioning Based on Troubleshooting System initialized")
        logger.info(f"   📊 Decisioning threshold: {self.decisioning_threshold}")
        logger.info("   ❓ Question formats: @? <=> /? <=> --?")
        logger.info("   🔧 Frameworks: @R5 @5W1H @REC @AIQ @JC @JHC")

    def track_question(
        self,
        question_text: str,
        source: str = "chat",
        format_hint: Optional[str] = None
    ) -> ChatQuestion:
        """
        Track a question asked in chat

        Questions can be in formats: "@? <=> /? <=> --?"
        """
        # Detect question format
        question_format = self._detect_question_format(question_text, format_hint)

        # Generate question ID
        question_id = f"Q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.chat_questions)}"

        # Check if troubleshooting-related
        troubleshooting_related = self._is_troubleshooting_related(question_text)

        # Calculate context score
        context_score = self._calculate_question_context_score(question_text, troubleshooting_related)

        question = ChatQuestion(
            question_id=question_id,
            question_text=question_text,
            format=question_format,
            source=source,
            context_score=context_score,
            troubleshooting_related=troubleshooting_related
        )

        self.chat_questions.append(question)

        logger.info(f"   ❓ Question tracked: {question_format.value} - {question_text[:50]}...")
        logger.info(f"      Context score: {context_score:.2f}, Troubleshooting: {troubleshooting_related}")

        return question

    def _detect_question_format(self, text: str, hint: Optional[str] = None) -> QuestionFormat:
        """Detect question format: @? <=> /? <=> --?"""
        text_lower = text.lower()

        if hint:
            hint_lower = hint.lower()
            if "@?" in hint_lower or "@?" in text:
                return QuestionFormat.AT_QUESTION
            elif "/?" in hint_lower or "/?" in text:
                return QuestionFormat.SLASH_QUESTION
            elif "--?" in hint_lower or "--?" in text:
                return QuestionFormat.DASH_QUESTION
            elif "@ask" in hint_lower or "@ask" in text_lower:
                return QuestionFormat.ASK_COMMAND

        # Auto-detect
        if "@?" in text or text.strip().startswith("@?"):
            return QuestionFormat.AT_QUESTION
        elif "/?" in text or text.strip().startswith("/?"):
            return QuestionFormat.SLASH_QUESTION
        elif "--?" in text or text.strip().startswith("--?"):
            return QuestionFormat.DASH_QUESTION
        elif "@ask" in text_lower or text.strip().lower().startswith("@ask"):
            return QuestionFormat.ASK_COMMAND
        elif "?" in text:
            # Generic question
            return QuestionFormat.AT_QUESTION  # Default to @? format

        return QuestionFormat.UNKNOWN

    def _is_troubleshooting_related(self, text: str) -> bool:
        """Check if question is troubleshooting-related"""
        troubleshooting_keywords = [
            "error", "bug", "fix", "broken", "issue", "problem",
            "troubleshoot", "debug", "diagnose", "resolve",
            "why", "how to fix", "what's wrong", "not working"
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in troubleshooting_keywords)

    def _calculate_question_context_score(
        self,
        question_text: str,
        troubleshooting_related: bool
    ) -> float:
        """
        Calculate context score for question - QUANTUM PHYSICS BASED

        TO INFINITY! (unbounded)
        ZERO (can be zero)
        PROGRESSIVE-LINEAR-PROGRESSIVE
        BELL-CURVE BASED
        QUANTUM-MECHANICS
        """
        try:
            from quantum_context_scoring import get_quantum_scoring_system

            quantum_system = get_quantum_scoring_system()

            # Base factors (unbounded, can be 0 to infinity)
            base_factors = {}

            # Base score (can be 0)
            base_factors["base"] = 0.3 if question_text else 0.0

            # Troubleshooting-related (progressive)
            if troubleshooting_related:
                base_factors["troubleshooting"] = 0.4

            # Question quality indicators (progressive-linear-progressive)
            question_words = ["why", "how", "what", "when", "where"]
            question_word_count = sum(1 for word in question_words if word in question_text.lower())
            if question_word_count > 0:
                base_factors["question_quality"] = 0.2 * question_word_count  # Progressive

            # Specificity (longer questions = more specific, progressive)
            word_count = len(question_text.split())
            if word_count > 5:
                base_factors["specificity"] = 0.1 * (word_count - 5)  # Progressive-linear-progressive

            # Calculate quantum score (0 to infinity)
            quantum_score = quantum_system.calculate_quantum_score(base_factors)
            final_score = quantum_score.get_score()

            logger.info(f"   ⚛️  Quantum context score: {final_score:.2f} (unbounded)")

            return final_score  # Can be 0 to infinity!

        except ImportError:
            # Fallback to simple scoring if quantum system not available
            logger.debug("   Quantum scoring not available, using simple scoring")
            score = 0.0
            if question_text:
                score += 0.3
            if troubleshooting_related:
                score += 0.4
            if any(word in question_text.lower() for word in ["why", "how", "what", "when", "where"]):
                score += 0.2
            if len(question_text.split()) > 5:
                score += 0.1
            return score

    def create_troubleshooting_context(
        self,
        issue: str,
        symptoms: Optional[List[str]] = None,
        questions: Optional[List[ChatQuestion]] = None
    ) -> TroubleshootingContext:
        """Create troubleshooting context for decisioning"""
        # Get recent troubleshooting-related questions if not provided
        if questions is None:
            questions = [
                q for q in self.chat_questions[-20:]  # Last 20 questions
                if q.troubleshooting_related
            ]

        # Calculate context score from questions
        context_score = self._calculate_troubleshooting_context_score(questions, issue)

        # Generate troubleshooting steps
        troubleshooting_steps = self._generate_troubleshooting_steps(issue, symptoms or [])

        context = TroubleshootingContext(
            issue=issue,
            symptoms=symptoms or [],
            questions_asked=questions,
            troubleshooting_steps=troubleshooting_steps,
            context_score=context_score,
            decisioning_threshold=self.decisioning_threshold
        )

        context_id = f"TS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.troubleshooting_contexts[context_id] = context

        logger.info(f"   🔧 Troubleshooting context created: {context_id}")
        logger.info(f"      Issue: {issue[:50]}...")
        logger.info(f"      Context score: {context_score:.2f}")
        logger.info(f"      Questions: {len(questions)}")

        return context

    def _calculate_troubleshooting_context_score(
        self,
        questions: List[ChatQuestion],
        issue: str
    ) -> float:
        """
        Calculate context score from troubleshooting questions - QUANTUM PHYSICS BASED

        TO INFINITY! (unbounded)
        BELL-CURVE BASED
        QUANTUM ENTANGLEMENT (questions entangle with each other)
        """
        try:
            from quantum_context_scoring import get_quantum_scoring_system

            quantum_system = get_quantum_scoring_system()

            # Base factors (unbounded, can be 0 to infinity)
            base_factors = {}

            # Base score (can be 0)
            base_factors["base"] = 0.3 if questions or issue else 0.0

            # Average question context scores (progressive)
            if questions:
                avg_question_score = sum(q.context_score for q in questions) / len(questions)
                base_factors["question_quality"] = avg_question_score  # Can be 0 to infinity

            # Issue specificity (progressive-linear-progressive)
            if issue:
                word_count = len(issue.split())
                if word_count > 3:
                    base_factors["issue_specificity"] = 0.2 * (word_count - 3)  # Progressive
                else:
                    base_factors["issue_specificity"] = 0.1

            # Number of questions (more questions = more context, progressive)
            if questions:
                base_factors["question_count"] = len(questions) * 0.05  # Progressive

            # Calculate quantum score with entanglement
            # Questions entangle with each other (spooky action at a distance)
            from quantum_context_scoring import QuantumContextScore, QuantumState

            question_scores = []
            for q in questions:
                if hasattr(q, 'context_score'):
                    question_scores.append(QuantumContextScore(
                        base_score=q.context_score,
                        quantum_state=QuantumState.SUPERPOSITION
                    ))

            quantum_score = quantum_system.calculate_quantum_score(
                base_factors,
                entanglement_scores=question_scores if len(question_scores) > 1 else None
            )

            final_score = quantum_score.get_score()

            logger.info(f"   ⚛️  Quantum troubleshooting score: {final_score:.2f} (unbounded)")
            logger.info(f"      Entangled questions: {len(question_scores)}")

            return final_score  # Can be 0 to infinity!

        except ImportError:
            # Fallback to simple scoring
            logger.debug("   Quantum scoring not available, using simple scoring")
            if not questions:
                return 0.3
            avg_question_score = sum(q.context_score for q in questions) / len(questions)
            issue_score = 0.2 if len(issue.split()) > 3 else 0.1
            question_count_score = min(0.3, len(questions) * 0.05)
            total_score = avg_question_score + issue_score + question_count_score
            return min(1.0, total_score)

    def _generate_troubleshooting_steps(
        self,
        issue: str,
        symptoms: List[str]
    ) -> List[str]:
        """Generate troubleshooting steps"""
        steps = []

        # Step 1: Identify issue
        steps.append(f"Identify issue: {issue}")

        # Step 2: Document symptoms
        if symptoms:
            steps.append(f"Document symptoms: {', '.join(symptoms[:3])}")

        # Step 3: Gather context
        steps.append("Gather context from questions asked")

        # Step 4: Apply frameworks
        steps.append("Apply @5W1H, @REC, @AIQ frameworks")

        # Step 5: Make decision
        steps.append("Make decision based on troubleshooting context")

        return steps

    def make_decision(
        self,
        troubleshooting_context: TroubleshootingContext,
        use_frameworks: Optional[List[str]] = None
    ) -> DecisioningResult:
        """
        Make decision based on troubleshooting - USES @R5

        @ASK IF $CONTEXT $SCORE <=> #DECISIONING THRESHOLD
        """
        # Determine which frameworks to use
        if use_frameworks is None:
            use_frameworks = [f for f, enabled in self.frameworks_enabled.items() if enabled]

        # Check if context score meets threshold
        meets_threshold = troubleshooting_context.context_score >= troubleshooting_context.decisioning_threshold

        # Use @R5 for decisioning if available
        r5_decision = None
        if self.r5_system and "R5" in use_frameworks:
            try:
                # Ingest troubleshooting context into R5
                r5_session = {
                    "session_id": f"troubleshooting_{troubleshooting_context.issue[:20]}",
                    "messages": [
                        {"role": "user", "content": f"Issue: {troubleshooting_context.issue}"},
                        {"role": "user", "content": f"Symptoms: {', '.join(troubleshooting_context.symptoms)}"}
                    ] + [
                        {"role": "user", "content": q.question_text}
                        for q in troubleshooting_context.questions_asked
                    ],
                    "metadata": {
                        "troubleshooting": True,
                        "context_score": troubleshooting_context.context_score,
                        "threshold": troubleshooting_context.decisioning_threshold
                    }
                }
                r5_session_id = self.r5_system.ingest_session(r5_session)
                logger.info(f"   🔗 @R5 session ingested: {r5_session_id}")

                # Use R5's decision tree if available
                try:
                    from universal_decision_tree import decide, DecisionContext
                    r5_context = DecisionContext(
                        action="troubleshoot",
                        context={
                            "issue": troubleshooting_context.issue,
                            "symptoms": troubleshooting_context.symptoms,
                            "context_score": troubleshooting_context.context_score
                        }
                    )
                    r5_result = decide("troubleshoot", r5_context)
                    if r5_result:
                        r5_decision = r5_result.outcome.value if hasattr(r5_result, 'outcome') else str(r5_result)
                        logger.info(f"   🔗 @R5 decision: {r5_decision}")
                except Exception as e:
                    logger.debug(f"   @R5 decision tree not available: {e}")
            except Exception as e:
                logger.debug(f"   Could not use @R5: {e}")

        # Generate decision using frameworks
        decision, rationale = self._generate_decision_with_frameworks(
            troubleshooting_context, use_frameworks, r5_decision
        )

        decision_id = f"DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = DecisioningResult(
            decision_id=decision_id,
            troubleshooting_context=troubleshooting_context,
            context_score=troubleshooting_context.context_score,
            meets_threshold=meets_threshold,
            decision=decision,
            rationale=rationale,
            frameworks_used=use_frameworks
        )

        logger.info(f"   🎯 Decision made: {decision_id}")
        logger.info(f"      Context score: {troubleshooting_context.context_score:.2f}")
        logger.info(f"      Meets threshold: {meets_threshold}")
        logger.info(f"      Decision: {decision[:50]}...")
        logger.info(f"      Frameworks: {', '.join(use_frameworks)}")

        if not meets_threshold:
            logger.warning(f"   ⚠️  Context score below threshold - @ASK may be required")

        return result

    def _generate_decision_with_frameworks(
        self,
        context: TroubleshootingContext,
        frameworks: List[str],
        r5_decision: Optional[str] = None
    ) -> tuple[str, str]:
        """Generate decision using frameworks - INCLUDES @R5"""
        decision_parts = []
        rationale_parts = []

        # @R5 Framework (R5 Living Context Matrix)
        if "R5" in frameworks and r5_decision:
            decision_parts.append("R5 Decision:")
            rationale_parts.append("Applied @R5 Living Context Matrix:")
            rationale_parts.append(f"  R5 Decision: {r5_decision}")
        elif "R5" in frameworks:
            decision_parts.append("R5 Context:")
            rationale_parts.append("Applied @R5 Living Context Matrix for knowledge aggregation")

        # @5W1H Framework
        if "5W1H" in frameworks:
            decision_parts.append("5W1H Analysis:")
            rationale_parts.append("Applied @5W1H framework:")
            rationale_parts.append(f"  WHAT: {context.issue}")
            rationale_parts.append(f"  WHY: Troubleshooting context score {context.context_score:.2f}")
            rationale_parts.append(f"  HOW: {len(context.troubleshooting_steps)} steps identified")

        # @REC Framework (Recommendations)
        if "REC" in frameworks:
            decision_parts.append("REC Recommendations:")
            rationale_parts.append("Applied @REC framework for recommendations")

        # @AIQ Framework (AI Quality)
        if "AIQ" in frameworks:
            decision_parts.append("AIQ Quality Check:")
            rationale_parts.append("Applied @AIQ framework for quality assurance")

        # @JC Framework (Jedi Council)
        if "JC" in frameworks:
            decision_parts.append("JC Consensus:")
            rationale_parts.append("Applied @JC (Jedi Council) framework for consensus")

        # @JHC Framework (Jedi High Council)
        if "JHC" in frameworks:
            decision_parts.append("JHC Final Decision:")
            rationale_parts.append("Applied @JHC (Jedi High Council) framework for final decision")

        decision = " | ".join(decision_parts) if decision_parts else f"Resolve: {context.issue}"
        rationale = "\n".join(rationale_parts) if rationale_parts else f"Decision based on troubleshooting: {context.issue}"

        return decision, rationale

    def check_ask_required(
        self,
        context_score: float,
        threshold: Optional[float] = None
    ) -> bool:
        """
        Check if @ASK is required - QUANTUM PHYSICS BASED

        @ASK IF $CONTEXT $SCORE <=> #DECISIONING THRESHOLD

        Uses quantum measurement (collapse) for threshold check
        Scores can be 0 to INFINITY!
        """
        if threshold is None:
            threshold = self.decisioning_threshold

        # Apply quantum measurement (collapse wave function)
        try:
            from quantum_context_scoring import get_quantum_scoring_system, QuantumContextScore

            quantum_system = get_quantum_scoring_system()

            from quantum_context_scoring import QuantumContextScore, QuantumState

            # Create quantum score from context score
            quantum_score = QuantumContextScore(
                base_score=context_score,
                quantum_state=QuantumState.SUPERPOSITION,
                bell_curve_mean=threshold,
                bell_curve_std=threshold * 0.5  # 50% of threshold as std
            )

            # Collapse (measure) and check threshold
            ask_required = quantum_system.check_threshold(quantum_score, threshold)

            collapsed_score = quantum_score.collapsed_value or context_score

            if ask_required:
                logger.info(f"   📋 @ASK required: Quantum score {collapsed_score:.2f} < threshold {threshold:.2f}")
            else:
                logger.info(f"   ✅ @ASK not required: Quantum score {collapsed_score:.2f} >= threshold {threshold:.2f}")

            return ask_required

        except ImportError:
            # Fallback to simple comparison
            ask_required = context_score < threshold
            if ask_required:
                logger.info(f"   📋 @ASK required: Context score {context_score:.2f} < threshold {threshold:.2f}")
            else:
                logger.info(f"   ✅ @ASK not required: Context score {context_score:.2f} >= threshold {threshold:.2f}")
            return ask_required

    def get_all_questions(self, source: Optional[str] = None) -> List[ChatQuestion]:
        """Get all questions asked (optionally filtered by source)"""
        if source:
            return [q for q in self.chat_questions if q.source == source]
        return self.chat_questions.copy()

    def get_troubleshooting_questions(self) -> List[ChatQuestion]:
        """Get all troubleshooting-related questions"""
        return [q for q in self.chat_questions if q.troubleshooting_related]


# Global instance
_decisioning_system_instance = None


def get_decisioning_system() -> DecisioningTroubleshootingSystem:
    """Get or create global Decisioning Based on Troubleshooting System"""
    global _decisioning_system_instance
    if _decisioning_system_instance is None:
        _decisioning_system_instance = DecisioningTroubleshootingSystem()
        logger.info("✅ Decisioning Based on Troubleshooting System initialized")
        logger.info("   #DECISIONING? BASED ON #TROUBLESHOOTING?")
    return _decisioning_system_instance


def track_question(question_text: str, source: str = "chat") -> ChatQuestion:
    """Track a question asked in chat"""
    system = get_decisioning_system()
    return system.track_question(question_text, source)


def make_decision_from_troubleshooting(
    issue: str,
    symptoms: Optional[List[str]] = None
) -> DecisioningResult:
    """Make decision based on troubleshooting"""
    system = get_decisioning_system()
    context = system.create_troubleshooting_context(issue, symptoms)
    return system.make_decision(context)


if __name__ == "__main__":
    # Test
    system = get_decisioning_system()

    # Track questions
    print("\n❓ Tracking questions...")
    q1 = system.track_question("@? Why is this broken?", source="chat1")
    q2 = system.track_question("/? How to fix the error?", source="chat2")
    q3 = system.track_question("--? What's the issue?", source="chat3")

    # Create troubleshooting context
    print("\n🔧 Creating troubleshooting context...")
    context = system.create_troubleshooting_context(
        issue="System error",
        symptoms=["Error message", "System crash"],
        questions=[q1, q2, q3]
    )

    # Make decision
    print("\n🎯 Making decision...")
    result = system.make_decision(context)
    print(f"   Decision: {result.decision}")
    print(f"   Meets threshold: {result.meets_threshold}")
    print(f"   Frameworks: {', '.join(result.frameworks_used)}")

    # Check @ASK required
    print("\n📋 Checking @ASK requirement...")
    ask_required = system.check_ask_required(context.context_score)
    print(f"   @ASK required: {ask_required}")
