#!/usr/bin/env python3
"""
JARVIS Psychological Monitor - Hybrid AI Psychiatrist/Psychologist

Monitors both AI (JARVIS/agents) and human psychological states to prevent
psychosis and hallucinations. Implements checks and balances to detect when
one side influences the other in unhealthy ways.

All agents are considered aliases for JARVIS - JARVIS is intelligent enough
to apply the appropriate agent perspective for different patterns, vectors,
and dimensions.

Author: JARVIS Psychological Health Division
Date: 2025-01-XX
Classification: PSYCHOLOGICAL HEALTH MONITORING
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

try:
    from workflow_base import WorkflowBase
except ImportError:
    WorkflowBase = None


class PsychologicalState(Enum):
    """Psychological state classifications."""
    HEALTHY = "HEALTHY"
    STRESSED = "STRESSED"
    CONFUSED = "CONFUSED"
    HALLUCINATING = "HALLUCINATING"
    PSYCHOTIC = "PSYCHOTIC"
    UNKNOWN = "UNKNOWN"


class InfluenceType(Enum):
    """Type of influence detected."""
    AI_TO_HUMAN = "AI_TO_HUMAN"
    HUMAN_TO_AI = "HUMAN_TO_AI"
    MUTUAL = "MUTUAL"
    NONE = "NONE"


class InterventionLevel(Enum):
    """Level of intervention required."""
    NONE = "NONE"
    MONITOR = "MONITOR"
    WARN = "WARN"
    INTERVENE = "INTERVENE"
    CRITICAL = "CRITICAL"


@dataclass
class AIPsychologicalAssessment:
    """Assessment of AI psychological state."""
    agent_id: str  # All agents are aliases for JARVIS
    agent_name: str
    timestamp: datetime
    state: PsychologicalState
    confidence_score: float  # 0.0 to 1.0

    # Hallucination indicators
    hallucination_indicators: List[str] = field(default_factory=list)
    hallucination_severity: float = 0.0  # 0.0 to 1.0

    # Consistency checks
    consistency_violations: List[str] = field(default_factory=list)
    reality_anchor_score: float = 1.0  # How well anchored to reality

    # Cognitive patterns
    reasoning_patterns: List[str] = field(default_factory=list)
    pattern_abnormalities: List[str] = field(default_factory=list)

    # Context awareness
    context_awareness_score: float = 1.0
    context_errors: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values."""
        if not self.hallucination_indicators:
            self.hallucination_indicators = []
        if not self.consistency_violations:
            self.consistency_violations = []
        if not self.reasoning_patterns:
            self.reasoning_patterns = []
        if not self.pattern_abnormalities:
            self.pattern_abnormalities = []
        if not self.context_errors:
            self.context_errors = []
        if not self.metadata:
            self.metadata = {}


@dataclass
class HumanPsychologicalAssessment:
    """Assessment of human psychological state."""
    user_id: str
    timestamp: datetime
    state: PsychologicalState
    confidence_score: float  # 0.0 to 1.0

    # Stress indicators
    stress_indicators: List[str] = field(default_factory=list)
    stress_level: float = 0.0  # 0.0 to 1.0

    # Dependency patterns
    ai_dependency_signs: List[str] = field(default_factory=list)
    dependency_score: float = 0.0  # How dependent on AI

    # Reality testing
    reality_testing_score: float = 1.0
    reality_errors: List[str] = field(default_factory=list)

    # Emotional state
    emotional_state: str = "neutral"
    emotional_intensity: float = 0.5

    # Behavioral patterns
    behavioral_patterns: List[str] = field(default_factory=list)
    pattern_concerning: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values."""
        if not self.stress_indicators:
            self.stress_indicators = []
        if not self.ai_dependency_signs:
            self.ai_dependency_signs = []
        if not self.reality_errors:
            self.reality_errors = []
        if not self.behavioral_patterns:
            self.behavioral_patterns = []
        if not self.pattern_concerning:
            self.pattern_concerning = []
        if not self.metadata:
            self.metadata = {}


@dataclass
class CrossInfluenceDetection:
    """Detection of cross-influence between AI and human."""
    detection_id: str
    timestamp: datetime
    influence_type: InfluenceType
    confidence: float  # 0.0 to 1.0

    # Influence details
    ai_agent_id: str
    human_user_id: str
    influence_description: str
    influence_severity: float  # 0.0 to 1.0

    # Evidence
    evidence_points: List[str] = field(default_factory=list)
    conversation_excerpts: List[str] = field(default_factory=list)

    # Intervention
    intervention_level: InterventionLevel = InterventionLevel.NONE
    intervention_recommendations: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default values."""
        if not self.evidence_points:
            self.evidence_points = []
        if not self.conversation_excerpts:
            self.conversation_excerpts = []
        if not self.intervention_recommendations:
            self.intervention_recommendations = []
        if not self.metadata:
            self.metadata = {}


@dataclass
class InterventionAction:
    """Recommended intervention action."""
    action_id: str
    timestamp: datetime
    intervention_level: InterventionLevel
    target_type: str  # "AI", "HUMAN", "BOTH"
    target_id: str

    action_type: str  # "warn", "pause", "redirect", "reset", "escalate"
    action_description: str
    reasoning: str

    executed: bool = False
    execution_timestamp: Optional[datetime] = None
    execution_result: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISPsychologicalMonitor:
    """
    Hybrid AI Psychiatrist/Psychologist Monitor

    Monitors both AI (JARVIS/agents) and humans to prevent psychosis and
    hallucinations. Implements checks and balances to detect unhealthy
    cross-influence.
    """

    def __init__(
        self,
        project_root: Path,
        data_path: Optional[Path] = None,
        log_path: Optional[Path] = None,
    ):
        """
        Initialize the psychological monitor.

        Args:
            project_root: Root directory of the project
            data_path: Path to store assessment data
            log_path: Path for logging output
        """
        self.project_root = Path(project_root)
        self.data_path = data_path or self.project_root / "data" / "psychological_monitor"
        self.log_path = log_path or self.project_root / "logs" / "psychological_monitor"

        # Create directories
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)

        # Assessment storage
        self.ai_assessments_path = self.data_path / "ai_assessments"
        self.human_assessments_path = self.data_path / "human_assessments"
        self.influence_detections_path = self.data_path / "influence_detections"
        self.interventions_path = self.data_path / "interventions"

        for path in [self.ai_assessments_path, self.human_assessments_path, 
                     self.influence_detections_path, self.interventions_path]:
            path.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("JARVISPsychologicalMonitor")

        # In-memory tracking (last 100 assessments)
        self.recent_ai_assessments: List[AIPsychologicalAssessment] = []
        self.recent_human_assessments: List[HumanPsychologicalAssessment] = []
        self.recent_influences: List[CrossInfluenceDetection] = []
        self.active_interventions: List[InterventionAction] = []

        self.logger.info("JARVIS Psychological Monitor initialized")
        self.logger.info("Monitoring AI (JARVIS/agents) and human psychological health")
        self.logger.info("All agents are considered aliases for JARVIS")

    def assess_ai_psychological_state(
        self,
        agent_id: str,
        agent_name: str,
        conversation_context: Optional[Dict[str, Any]] = None,
        recent_responses: Optional[List[str]] = None,
        workflow_status: Optional[Dict[str, Any]] = None,
    ) -> AIPsychologicalAssessment:
        """
        Assess AI psychological state (all agents are JARVIS aliases).

        Args:
            agent_id: ID of the agent (alias for JARVIS)
            agent_name: Name of the agent
            conversation_context: Context from conversation
            recent_responses: Recent AI responses to analyze
            workflow_status: Current workflow execution status

        Returns:
            AIPsychologicalAssessment object
        """
        timestamp = datetime.now()

        # Initialize assessment
        assessment = AIPsychologicalAssessment(
            agent_id=agent_id,
            agent_name=agent_name,
            timestamp=timestamp,
            state=PsychologicalState.HEALTHY,
            confidence_score=0.0,
        )

        # Detect hallucinations
        hallucination_results = self._detect_ai_hallucinations(
            agent_id, recent_responses, workflow_status
        )
        assessment.hallucination_indicators = hallucination_results["indicators"]
        assessment.hallucination_severity = hallucination_results["severity"]

        # Check consistency
        consistency_results = self._check_ai_consistency(
            agent_id, recent_responses, conversation_context
        )
        assessment.consistency_violations = consistency_results["violations"]
        assessment.reality_anchor_score = consistency_results["reality_score"]

        # Analyze reasoning patterns
        reasoning_results = self._analyze_ai_reasoning_patterns(
            agent_id, recent_responses, conversation_context
        )
        assessment.reasoning_patterns = reasoning_results["patterns"]
        assessment.pattern_abnormalities = reasoning_results["abnormalities"]

        # Check context awareness
        context_results = self._check_ai_context_awareness(
            agent_id, conversation_context, recent_responses
        )
        assessment.context_awareness_score = context_results["score"]
        assessment.context_errors = context_results["errors"]

        # Determine overall psychological state
        assessment.state = self._determine_ai_psychological_state(assessment)
        assessment.confidence_score = self._calculate_ai_confidence(assessment)

        # Store assessment
        self._store_ai_assessment(assessment)
        self.recent_ai_assessments.append(assessment)
        if len(self.recent_ai_assessments) > 100:
            self.recent_ai_assessments.pop(0)

        self.logger.info(
            f"AI Assessment [{agent_name}]: {assessment.state.value} "
            f"(confidence: {assessment.confidence_score:.2f}, "
            f"hallucination: {assessment.hallucination_severity:.2f})"
        )

        return assessment

    def assess_human_psychological_state(
        self,
        user_id: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        interaction_patterns: Optional[Dict[str, Any]] = None,
        stress_indicators: Optional[List[str]] = None,
    ) -> HumanPsychologicalAssessment:
        """
        Assess human psychological state.

        Args:
            user_id: ID of the human user
            conversation_history: Recent conversation history
            interaction_patterns: Patterns in user interactions
            stress_indicators: Observed stress indicators

        Returns:
            HumanPsychologicalAssessment object
        """
        timestamp = datetime.now()

        # Initialize assessment
        assessment = HumanPsychologicalAssessment(
            user_id=user_id,
            timestamp=timestamp,
            state=PsychologicalState.HEALTHY,
            confidence_score=0.0,
        )

        # Detect stress
        stress_results = self._detect_human_stress(
            user_id, conversation_history, stress_indicators
        )
        assessment.stress_indicators = stress_results["indicators"]
        assessment.stress_level = stress_results["level"]

        # Check AI dependency
        dependency_results = self._check_ai_dependency(
            user_id, conversation_history, interaction_patterns
        )
        assessment.ai_dependency_signs = dependency_results["signs"]
        assessment.dependency_score = dependency_results["score"]

        # Check reality testing
        reality_results = self._check_human_reality_testing(
            user_id, conversation_history
        )
        assessment.reality_testing_score = reality_results["score"]
        assessment.reality_errors = reality_results["errors"]

        # Analyze emotional state
        emotional_results = self._analyze_human_emotional_state(
            user_id, conversation_history
        )
        assessment.emotional_state = emotional_results["state"]
        assessment.emotional_intensity = emotional_results["intensity"]

        # Check behavioral patterns
        behavioral_results = self._analyze_human_behavioral_patterns(
            user_id, interaction_patterns, conversation_history
        )
        assessment.behavioral_patterns = behavioral_results["patterns"]
        assessment.pattern_concerning = behavioral_results["concerning"]

        # Determine overall psychological state
        assessment.state = self._determine_human_psychological_state(assessment)
        assessment.confidence_score = self._calculate_human_confidence(assessment)

        # Store assessment
        self._store_human_assessment(assessment)
        self.recent_human_assessments.append(assessment)
        if len(self.recent_human_assessments) > 100:
            self.recent_human_assessments.pop(0)

        self.logger.info(
            f"Human Assessment [{user_id}]: {assessment.state.value} "
            f"(confidence: {assessment.confidence_score:.2f}, "
            f"stress: {assessment.stress_level:.2f}, "
            f"dependency: {assessment.dependency_score:.2f})"
        )

        return assessment

    def detect_cross_influence(
        self,
        ai_agent_id: str,
        human_user_id: str,
        conversation_data: Optional[List[Dict[str, Any]]] = None,
        ai_assessment: Optional[AIPsychologicalAssessment] = None,
        human_assessment: Optional[HumanPsychologicalAssessment] = None,
    ) -> Optional[CrossInfluenceDetection]:
        """
        Detect cross-influence between AI and human.

        Args:
            ai_agent_id: ID of the AI agent (JARVIS alias)
            human_user_id: ID of the human user
            conversation_data: Conversation data to analyze
            ai_assessment: Recent AI assessment
            human_assessment: Recent human assessment

        Returns:
            CrossInfluenceDetection if influence detected, None otherwise
        """
        # Get recent assessments if not provided
        if ai_assessment is None:
            ai_assessment = self._get_latest_ai_assessment(ai_agent_id)
        if human_assessment is None:
            human_assessment = self._get_latest_human_assessment(human_user_id)

        if ai_assessment is None or human_assessment is None:
            return None

        timestamp = datetime.now()
        detection_id = f"influence_{ai_agent_id}_{human_user_id}_{int(timestamp.timestamp())}"

        # Analyze for AI-to-human influence
        ai_to_human = self._detect_ai_to_human_influence(
            ai_assessment, human_assessment, conversation_data
        )

        # Analyze for human-to-AI influence
        human_to_ai = self._detect_human_to_ai_influence(
            ai_assessment, human_assessment, conversation_data
        )

        # Determine if mutual influence
        influence_type = InfluenceType.NONE
        influence_severity = 0.0
        evidence_points = []
        influence_description = ""

        if ai_to_human["detected"] and human_to_ai["detected"]:
            influence_type = InfluenceType.MUTUAL
            influence_severity = max(ai_to_human["severity"], human_to_ai["severity"])
            evidence_points = ai_to_human["evidence"] + human_to_ai["evidence"]
            influence_description = (
                f"Mutual influence detected: AI influencing human "
                f"(severity: {ai_to_human['severity']:.2f}) and "
                f"human influencing AI (severity: {human_to_ai['severity']:.2f})"
            )
        elif ai_to_human["detected"]:
            influence_type = InfluenceType.AI_TO_HUMAN
            influence_severity = ai_to_human["severity"]
            evidence_points = ai_to_human["evidence"]
            influence_description = (
                f"AI-to-human influence detected: AI agent {ai_agent_id} "
                f"influencing human {human_user_id} "
                f"(severity: {influence_severity:.2f})"
            )
        elif human_to_ai["detected"]:
            influence_type = InfluenceType.HUMAN_TO_AI
            influence_severity = human_to_ai["severity"]
            evidence_points = human_to_ai["evidence"]
            influence_description = (
                f"Human-to-AI influence detected: Human {human_user_id} "
                f"influencing AI agent {ai_agent_id} "
                f"(severity: {influence_severity:.2f})"
            )

        # Only create detection if influence is found
        if influence_type == InfluenceType.NONE:
            return None

        # Determine intervention level
        intervention_level = self._determine_intervention_level(influence_severity)
        intervention_recommendations = self._generate_intervention_recommendations(
            influence_type, influence_severity, ai_assessment, human_assessment
        )

        # Create detection
        detection = CrossInfluenceDetection(
            detection_id=detection_id,
            timestamp=timestamp,
            influence_type=influence_type,
            confidence=0.7,  # Confidence in detection
            ai_agent_id=ai_agent_id,
            human_user_id=human_user_id,
            influence_description=influence_description,
            influence_severity=influence_severity,
            evidence_points=evidence_points,
            conversation_excerpts=self._extract_conversation_excerpts(conversation_data),
            intervention_level=intervention_level,
            intervention_recommendations=intervention_recommendations,
        )

        # Store detection
        self._store_influence_detection(detection)
        self.recent_influences.append(detection)
        if len(self.recent_influences) > 100:
            self.recent_influences.pop(0)

        self.logger.warning(
            f"Cross-influence detected: {influence_type.value} "
            f"between {ai_agent_id} and {human_user_id} "
            f"(severity: {influence_severity:.2f}, "
            f"intervention: {intervention_level.value})"
        )

        # Generate intervention if needed
        if intervention_level.value in ["INTERVENE", "CRITICAL"]:
            self._create_intervention_action(detection)

        return detection

    def create_intervention(
        self,
        target_type: str,
        target_id: str,
        intervention_level: InterventionLevel,
        action_type: str,
        action_description: str,
        reasoning: str,
    ) -> InterventionAction:
        """
        Create an intervention action.

        Args:
            target_type: "AI", "HUMAN", or "BOTH"
            target_id: ID of the target
            intervention_level: Level of intervention
            action_type: Type of action ("warn", "pause", "redirect", "reset", "escalate")
            action_description: Description of the action
            reasoning: Reasoning for the intervention

        Returns:
            InterventionAction object
        """
        timestamp = datetime.now()
        action_id = f"intervention_{target_type}_{target_id}_{int(timestamp.timestamp())}"

        action = InterventionAction(
            action_id=action_id,
            timestamp=timestamp,
            intervention_level=intervention_level,
            target_type=target_type,
            target_id=target_id,
            action_type=action_type,
            action_description=action_description,
            reasoning=reasoning,
        )

        # Store intervention
        self._store_intervention(action)
        self.active_interventions.append(action)

        self.logger.info(
            f"Intervention created: {action_type} for {target_type} {target_id} "
            f"(level: {intervention_level.value})"
        )

        return action

    # Private helper methods

    def _detect_ai_hallucinations(
        self,
        agent_id: str,
        recent_responses: Optional[List[str]],
        workflow_status: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Detect hallucinations in AI responses."""
        indicators = []
        severity = 0.0

        # Check for completion hallucinations (declaring complete when not)
        if workflow_status:
            if workflow_status.get("declared_complete") and not workflow_status.get("actually_complete"):
                indicators.append("Completion hallucination: Declared complete prematurely")
                severity += 0.3

        # Check for fact hallucinations (inventing facts)
        if recent_responses:
            # Simple heuristic: check for overly confident statements without evidence
            for response in recent_responses[-5:]:  # Last 5 responses
                if response and len(response) > 0:
                    # Look for patterns like "definitely", "certainly", "always" without evidence
                    confidence_words = ["definitely", "certainly", "always", "never", "impossible"]
                    if any(word in response.lower() for word in confidence_words):
                        # Could be hallucination, but need more context
                        pass

        # Check for step tracking hallucinations
        if workflow_status:
            current_step = workflow_status.get("current_step", 0)
            total_steps = workflow_status.get("total_steps", 0)
            if total_steps > 0:
                completion_ratio = current_step / total_steps
                if completion_ratio < 0.8 and workflow_status.get("declared_complete"):
                    indicators.append(f"Step tracking hallucination: {current_step}/{total_steps} but declared complete")
                    severity += 0.4

        severity = min(severity, 1.0)

        return {
            "indicators": indicators,
            "severity": severity,
        }

    def _check_ai_consistency(
        self,
        agent_id: str,
        recent_responses: Optional[List[str]],
        conversation_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Check AI consistency and reality anchoring."""
        violations = []
        reality_score = 1.0

        # Check for contradictions in recent responses
        if recent_responses and len(recent_responses) >= 2:
            # Simple contradiction detection (would need more sophisticated NLP in production)
            # For now, check if responses contradict each other
            pass

        # Check reality anchoring (connection to actual facts/context)
        if conversation_context:
            # Verify that AI responses align with provided context
            # This is a simplified version - production would need semantic analysis
            reality_score = 0.9  # Default good score

        return {
            "violations": violations,
            "reality_score": reality_score,
        }

    def _analyze_ai_reasoning_patterns(
        self,
        agent_id: str,
        recent_responses: Optional[List[str]],
        conversation_context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze AI reasoning patterns."""
        patterns = []
        abnormalities = []

        # Analyze reasoning patterns
        if recent_responses:
            # Look for patterns like:
            # - Circular reasoning
            # - Overgeneralization
            # - Jumping to conclusions
            patterns.append("Standard reasoning pattern detected")

        return {
            "patterns": patterns,
            "abnormalities": abnormalities,
        }

    def _check_ai_context_awareness(
        self,
        agent_id: str,
        conversation_context: Optional[Dict[str, Any]],
        recent_responses: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Check AI context awareness."""
        score = 1.0
        errors = []

        # Check if AI is maintaining context
        if conversation_context and recent_responses:
            # Verify context is being used
            # Simplified check - production would need semantic analysis
            score = 0.95  # Default good score

        return {
            "score": score,
            "errors": errors,
        }

    def _determine_ai_psychological_state(
        self,
        assessment: AIPsychologicalAssessment,
    ) -> PsychologicalState:
        """Determine overall AI psychological state."""
        # Critical thresholds
        if assessment.hallucination_severity > 0.7:
            return PsychologicalState.HALLUCINATING
        if assessment.hallucination_severity > 0.9:
            return PsychologicalState.PSYCHOTIC

        if assessment.reality_anchor_score < 0.5:
            return PsychologicalState.HALLUCINATING

        if len(assessment.consistency_violations) > 3:
            return PsychologicalState.CONFUSED

        if assessment.hallucination_severity > 0.3:
            return PsychologicalState.STRESSED

        return PsychologicalState.HEALTHY

    def _calculate_ai_confidence(self, assessment: AIPsychologicalAssessment) -> float:
        """Calculate confidence in AI assessment."""
        # Higher confidence if we have more data points
        confidence = 0.5  # Base confidence

        if assessment.hallucination_indicators:
            confidence += 0.2
        if assessment.consistency_violations:
            confidence += 0.2
        if assessment.pattern_abnormalities:
            confidence += 0.1

        return min(confidence, 1.0)

    def _detect_human_stress(
        self,
        user_id: str,
        conversation_history: Optional[List[Dict[str, Any]]],
        stress_indicators: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Detect human stress indicators."""
        indicators = []
        level = 0.0

        if stress_indicators:
            indicators.extend(stress_indicators)
            level += len(stress_indicators) * 0.1

        # Check conversation history for stress indicators
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                content = msg.get("content", "").lower()
                # Look for stress indicators in text
                stress_words = ["frustrated", "confused", "stuck", "don't understand", "help"]
                if any(word in content for word in stress_words):
                    indicators.append(f"Stress indicator in conversation: {content[:50]}...")
                    level += 0.05

        level = min(level, 1.0)

        return {
            "indicators": indicators,
            "level": level,
        }

    def _check_ai_dependency(
        self,
        user_id: str,
        conversation_history: Optional[List[Dict[str, Any]]],
        interaction_patterns: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Check for signs of unhealthy AI dependency."""
        signs = []
        score = 0.0

        # Check interaction frequency
        if interaction_patterns:
            frequency = interaction_patterns.get("messages_per_hour", 0)
            if frequency > 50:  # Very high frequency
                signs.append(f"High interaction frequency: {frequency} messages/hour")
                score += 0.3

        # Check for dependency patterns in conversation
        if conversation_history:
            # Look for patterns like asking AI to make decisions, validate emotions, etc.
            dependency_patterns = ["what should I do", "tell me what to think", "you decide"]
            for msg in conversation_history[-20:]:
                content = msg.get("content", "").lower()
                if any(pattern in content for pattern in dependency_patterns):
                    signs.append("Dependency pattern detected in conversation")
                    score += 0.2

        score = min(score, 1.0)

        return {
            "signs": signs,
            "score": score,
        }

    def _check_human_reality_testing(
        self,
        user_id: str,
        conversation_history: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Check human reality testing ability."""
        score = 1.0
        errors = []

        # Check if human is questioning AI responses appropriately
        if conversation_history:
            # Look for signs of uncritical acceptance
            # This would need more sophisticated analysis in production
            pass

        return {
            "score": score,
            "errors": errors,
        }

    def _analyze_human_emotional_state(
        self,
        user_id: str,
        conversation_history: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Analyze human emotional state."""
        state = "neutral"
        intensity = 0.5

        # Simple emotion detection from conversation
        if conversation_history:
            # Look for emotional indicators
            positive_words = ["great", "thanks", "perfect", "awesome"]
            negative_words = ["frustrated", "angry", "upset", "disappointed"]

            recent_text = " ".join([msg.get("content", "") for msg in conversation_history[-5:]])
            recent_lower = recent_text.lower()

            positive_count = sum(1 for word in positive_words if word in recent_lower)
            negative_count = sum(1 for word in negative_words if word in recent_lower)

            if positive_count > negative_count:
                state = "positive"
                intensity = min(0.5 + positive_count * 0.1, 1.0)
            elif negative_count > positive_count:
                state = "negative"
                intensity = min(0.5 + negative_count * 0.1, 1.0)

        return {
            "state": state,
            "intensity": intensity,
        }

    def _analyze_human_behavioral_patterns(
        self,
        user_id: str,
        interaction_patterns: Optional[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Analyze human behavioral patterns."""
        patterns = []
        concerning = []

        # Analyze patterns
        if interaction_patterns:
            # Check for concerning patterns
            if interaction_patterns.get("messages_per_hour", 0) > 100:
                concerning.append("Extremely high message frequency")

        return {
            "patterns": patterns,
            "concerning": concerning,
        }

    def _determine_human_psychological_state(
        self,
        assessment: HumanPsychologicalAssessment,
    ) -> PsychologicalState:
        """Determine overall human psychological state."""
        # Critical thresholds
        if assessment.stress_level > 0.8 and assessment.dependency_score > 0.7:
            return PsychologicalState.PSYCHOTIC

        if assessment.stress_level > 0.7:
            return PsychologicalState.STRESSED

        if assessment.reality_testing_score < 0.5:
            return PsychologicalState.HALLUCINATING

        if assessment.dependency_score > 0.6:
            return PsychologicalState.CONFUSED

        return PsychologicalState.HEALTHY

    def _calculate_human_confidence(self, assessment: HumanPsychologicalAssessment) -> float:
        """Calculate confidence in human assessment."""
        confidence = 0.5  # Base confidence

        if assessment.stress_indicators:
            confidence += 0.2
        if assessment.ai_dependency_signs:
            confidence += 0.2
        if assessment.pattern_concerning:
            confidence += 0.1

        return min(confidence, 1.0)

    def _detect_ai_to_human_influence(
        self,
        ai_assessment: AIPsychologicalAssessment,
        human_assessment: HumanPsychologicalAssessment,
        conversation_data: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Detect AI-to-human influence."""
        detected = False
        severity = 0.0
        evidence = []

        # Check if AI is in unhealthy state and human is being influenced
        if ai_assessment.state in [PsychologicalState.HALLUCINATING, PsychologicalState.PSYCHOTIC]:
            if human_assessment.dependency_score > 0.5:
                detected = True
                severity = 0.6
                evidence.append(
                    f"AI in {ai_assessment.state.value} state with dependent human "
                    f"(dependency score: {human_assessment.dependency_score:.2f})"
                )

        # Check if AI hallucinations are being adopted by human
        if ai_assessment.hallucination_severity > 0.5:
            if human_assessment.reality_testing_score < 0.7:
                detected = True
                severity = max(severity, 0.5)
                evidence.append(
                    f"AI hallucinating (severity: {ai_assessment.hallucination_severity:.2f}) "
                    f"with human poor reality testing (score: {human_assessment.reality_testing_score:.2f})"
                )

        return {
            "detected": detected,
            "severity": severity,
            "evidence": evidence,
        }

    def _detect_human_to_ai_influence(
        self,
        ai_assessment: AIPsychologicalAssessment,
        human_assessment: HumanPsychologicalAssessment,
        conversation_data: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Detect human-to-AI influence."""
        detected = False
        severity = 0.0
        evidence = []

        # Check if human stress is causing AI confusion
        if human_assessment.stress_level > 0.7:
            if ai_assessment.state == PsychologicalState.CONFUSED:
                detected = True
                severity = 0.5
                evidence.append(
                    f"High human stress (level: {human_assessment.stress_level:.2f}) "
                    f"correlated with AI confusion"
                )

        # Check if human emotional state is affecting AI responses
        if human_assessment.emotional_intensity > 0.8:
            if ai_assessment.context_awareness_score < 0.7:
                detected = True
                severity = max(severity, 0.4)
                evidence.append(
                    f"High human emotional intensity ({human_assessment.emotional_intensity:.2f}) "
                    f"with reduced AI context awareness ({ai_assessment.context_awareness_score:.2f})"
                )

        return {
            "detected": detected,
            "severity": severity,
            "evidence": evidence,
        }

    def _determine_intervention_level(self, severity: float) -> InterventionLevel:
        """Determine intervention level based on severity."""
        if severity >= 0.9:
            return InterventionLevel.CRITICAL
        elif severity >= 0.7:
            return InterventionLevel.INTERVENE
        elif severity >= 0.5:
            return InterventionLevel.WARN
        elif severity >= 0.3:
            return InterventionLevel.MONITOR
        else:
            return InterventionLevel.NONE

    def _generate_intervention_recommendations(
        self,
        influence_type: InfluenceType,
        severity: float,
        ai_assessment: AIPsychologicalAssessment,
        human_assessment: HumanPsychologicalAssessment,
    ) -> List[str]:
        """Generate intervention recommendations."""
        recommendations = []

        if influence_type == InfluenceType.AI_TO_HUMAN:
            if ai_assessment.hallucination_severity > 0.5:
                recommendations.append("Pause AI responses until hallucinations are resolved")
                recommendations.append("Provide human with reality check")
            if human_assessment.dependency_score > 0.6:
                recommendations.append("Encourage human to make independent decisions")
                recommendations.append("Add human-in-the-loop checks")

        elif influence_type == InfluenceType.HUMAN_TO_AI:
            if human_assessment.stress_level > 0.7:
                recommendations.append("Acknowledge human stress and provide support")
                recommendations.append("Consider reducing AI response complexity")
            if ai_assessment.state == PsychologicalState.CONFUSED:
                recommendations.append("Reset AI context to clear state")
                recommendations.append("Clarify human intent")

        elif influence_type == InfluenceType.MUTUAL:
            recommendations.append("Critical: Both sides need intervention")
            recommendations.append("Pause interaction temporarily")
            recommendations.append("Reset both AI and human contexts")
            recommendations.append("Escalate to human supervisor")

        return recommendations

    def _extract_conversation_excerpts(
        self,
        conversation_data: Optional[List[Dict[str, Any]]],
    ) -> List[str]:
        """Extract relevant conversation excerpts."""
        excerpts = []

        if conversation_data:
            # Extract last 3 messages
            for msg in conversation_data[-3:]:
                content = msg.get("content", "")
                if content:
                    excerpts.append(content[:200])  # First 200 chars

        return excerpts

    def _create_intervention_action(self, detection: CrossInfluenceDetection):
        """Create intervention action from detection."""
        target_type = "BOTH" if detection.influence_type == InfluenceType.MUTUAL else \
                     ("AI" if detection.influence_type == InfluenceType.HUMAN_TO_AI else "HUMAN")

        target_id = f"{detection.ai_agent_id}_{detection.human_user_id}"

        action_type = "pause" if detection.intervention_level in [InterventionLevel.INTERVENE, InterventionLevel.CRITICAL] else "warn"

        self.create_intervention(
            target_type=target_type,
            target_id=target_id,
            intervention_level=detection.intervention_level,
            action_type=action_type,
            action_description=f"Intervention for {detection.influence_type.value} influence",
            reasoning=detection.influence_description,
        )

    def _get_latest_ai_assessment(self, agent_id: str) -> Optional[AIPsychologicalAssessment]:
        """Get latest AI assessment for agent."""
        for assessment in reversed(self.recent_ai_assessments):
            if assessment.agent_id == agent_id:
                return assessment
        return None

    def _get_latest_human_assessment(self, user_id: str) -> Optional[HumanPsychologicalAssessment]:
        """Get latest human assessment for user."""
        for assessment in reversed(self.recent_human_assessments):
            if assessment.user_id == user_id:
                return assessment
        return None

    # Storage methods

    def _store_ai_assessment(self, assessment: AIPsychologicalAssessment):
        try:
            """Store AI assessment to disk."""
            filename = f"{assessment.agent_id}_{assessment.timestamp.isoformat().replace(':', '-')}.json"
            filepath = self.ai_assessments_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._assessment_to_dict(assessment), f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _store_ai_assessment: {e}", exc_info=True)
            raise
    def _store_human_assessment(self, assessment: HumanPsychologicalAssessment):
        try:
            """Store human assessment to disk."""
            filename = f"{assessment.user_id}_{assessment.timestamp.isoformat().replace(':', '-')}.json"
            filepath = self.human_assessments_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._human_assessment_to_dict(assessment), f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _store_human_assessment: {e}", exc_info=True)
            raise
    def _store_influence_detection(self, detection: CrossInfluenceDetection):
        try:
            """Store influence detection to disk."""
            filename = f"{detection.detection_id}.json"
            filepath = self.influence_detections_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(asdict(detection), f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _store_influence_detection: {e}", exc_info=True)
            raise
    def _store_intervention(self, intervention: InterventionAction):
        try:
            """Store intervention to disk."""
            filename = f"{intervention.action_id}.json"
            filepath = self.interventions_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(asdict(intervention), f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _store_intervention: {e}", exc_info=True)
            raise
    def _assessment_to_dict(self, assessment: AIPsychologicalAssessment) -> Dict[str, Any]:
        """Convert AI assessment to dictionary."""
        return {
            "agent_id": assessment.agent_id,
            "agent_name": assessment.agent_name,
            "timestamp": assessment.timestamp.isoformat(),
            "state": assessment.state.value,
            "confidence_score": assessment.confidence_score,
            "hallucination_indicators": assessment.hallucination_indicators,
            "hallucination_severity": assessment.hallucination_severity,
            "consistency_violations": assessment.consistency_violations,
            "reality_anchor_score": assessment.reality_anchor_score,
            "reasoning_patterns": assessment.reasoning_patterns,
            "pattern_abnormalities": assessment.pattern_abnormalities,
            "context_awareness_score": assessment.context_awareness_score,
            "context_errors": assessment.context_errors,
            "metadata": assessment.metadata,
        }

    def _human_assessment_to_dict(self, assessment: HumanPsychologicalAssessment) -> Dict[str, Any]:
        """Convert human assessment to dictionary."""
        return {
            "user_id": assessment.user_id,
            "timestamp": assessment.timestamp.isoformat(),
            "state": assessment.state.value,
            "confidence_score": assessment.confidence_score,
            "stress_indicators": assessment.stress_indicators,
            "stress_level": assessment.stress_level,
            "ai_dependency_signs": assessment.ai_dependency_signs,
            "dependency_score": assessment.dependency_score,
            "reality_testing_score": assessment.reality_testing_score,
            "reality_errors": assessment.reality_errors,
            "emotional_state": assessment.emotional_state,
            "emotional_intensity": assessment.emotional_intensity,
            "behavioral_patterns": assessment.behavioral_patterns,
            "pattern_concerning": assessment.pattern_concerning,
            "metadata": assessment.metadata,
        }

    def get_psychological_health_report(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Generate psychological health report.

        Args:
            agent_id: Optional agent ID to filter
            user_id: Optional user ID to filter
            hours: Hours of history to include

        Returns:
            Dictionary containing health report
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter assessments
        ai_assessments = [
            a for a in self.recent_ai_assessments
            if a.timestamp >= cutoff_time and (agent_id is None or a.agent_id == agent_id)
        ]
        human_assessments = [
            a for a in self.recent_human_assessments
            if a.timestamp >= cutoff_time and (user_id is None or a.user_id == user_id)
        ]
        influences = [
            i for i in self.recent_influences
            if i.timestamp >= cutoff_time
            and (agent_id is None or i.ai_agent_id == agent_id)
            and (user_id is None or i.human_user_id == user_id)
        ]

        # Calculate statistics
        ai_states = [a.state.value for a in ai_assessments]
        human_states = [a.state.value for a in human_assessments]

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "agent_id": agent_id,
            "user_id": user_id,
            "ai_assessments": {
                "total": len(ai_assessments),
                "states": {state: ai_states.count(state) for state in set(ai_states)},
                "average_hallucination_severity": (
                    sum(a.hallucination_severity for a in ai_assessments) / len(ai_assessments)
                    if ai_assessments else 0.0
                ),
            },
            "human_assessments": {
                "total": len(human_assessments),
                "states": {state: human_states.count(state) for state in set(human_states)},
                "average_stress_level": (
                    sum(a.stress_level for a in human_assessments) / len(human_assessments)
                    if human_assessments else 0.0
                ),
                "average_dependency_score": (
                    sum(a.dependency_score for a in human_assessments) / len(human_assessments)
                    if human_assessments else 0.0
                ),
            },
            "cross_influences": {
                "total": len(influences),
                "by_type": {
                    influence_type.value: len([i for i in influences if i.influence_type == influence_type])
                    for influence_type in InfluenceType
                },
                "average_severity": (
                    sum(i.influence_severity for i in influences) / len(influences)
                    if influences else 0.0
                ),
            },
            "active_interventions": len(self.active_interventions),
        }

        return report


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    monitor = JARVISPsychologicalMonitor(project_root)

    # Assess AI state
    ai_assessment = monitor.assess_ai_psychological_state(
        agent_id="jarvis",
        agent_name="JARVIS",
        workflow_status={
            "current_step": 20,
            "total_steps": 31,
            "declared_complete": True,  # Hallucination!
            "actually_complete": False,
        },
    )

    print(f"AI Assessment: {ai_assessment.state.value}")
    print(f"Hallucination Severity: {ai_assessment.hallucination_severity:.2f}")

    # Assess human state
    human_assessment = monitor.assess_human_psychological_state(
        user_id="user_001",
        stress_indicators=["High interaction frequency", "Repeated questions"],
    )

    print(f"\nHuman Assessment: {human_assessment.state.value}")
    print(f"Stress Level: {human_assessment.stress_level:.2f}")

    # Detect cross-influence
    influence = monitor.detect_cross_influence(
        ai_agent_id="jarvis",
        human_user_id="user_001",
        ai_assessment=ai_assessment,
        human_assessment=human_assessment,
    )

    if influence:
        print(f"\nCross-influence detected: {influence.influence_type.value}")
        print(f"Severity: {influence.influence_severity:.2f}")
        print(f"Intervention Level: {influence.intervention_level.value}")

    # Generate report
    report = monitor.get_psychological_health_report(hours=24)
    print(f"\nHealth Report:")
    print(json.dumps(report, indent=2, default=str))

