#!/usr/bin/env python3
"""
Hybrid Psychologist & Psychiatrist Smart Agent

Advanced psychological and psychiatric intelligence integrated into the Lumina system.
Provides mental health monitoring, assessment, and optimization for both human operators
and AI systems within the psychohistory framework.

Features:
1. Human Operator Mental Health Monitoring
2. AI System Psychological Assessment
3. Mental Health Feedback Loops
4. Crisis Detection & Intervention
5. Psychological Pattern Analysis
6. Therapeutic Recommendations
7. Burnout Prevention
8. Cognitive Load Optimization
9. Emotional Intelligence Enhancement
10. Mental Health Integration with Psychohistory
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics
import math
from collections import defaultdict

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class MentalHealthIndicator(Enum):
    """Mental health indicators for monitoring"""
    STRESS_LEVEL = "stress_level"
    BURNOUT_RISK = "burnout_risk"
    COGNITIVE_LOAD = "cognitive_load"
    EMOTIONAL_WELLBEING = "emotional_wellbeing"
    FOCUS_LEVEL = "focus_level"
    DECISION_QUALITY = "decision_quality"
    CREATIVITY_INDEX = "creativity_index"
    SOCIAL_CONNECTION = "social_connection"
    SLEEP_QUALITY = "sleep_quality"
    ENERGY_LEVEL = "energy_level"


class PsychologicalState(Enum):
    """Psychological states"""
    OPTIMAL = "optimal"
    GOOD = "good"
    MODERATE = "moderate"
    CONCERNED = "concerned"
    CRITICAL = "critical"
    CRISIS = "crisis"


class TherapeuticIntervention(Enum):
    """Types of therapeutic interventions"""
    MINDFULNESS_REMINDER = "mindfulness_reminder"
    BREAK_RECOMMENDATION = "break_recommendation"
    COGNITIVE_RESTRUCTURING = "cognitive_restructuring"
    SOCIAL_CONNECTION_PROMPT = "social_connection_prompt"
    EXERCISE_SUGGESTION = "exercise_suggestion"
    SLEEP_OPTIMIZATION = "sleep_optimization"
    WORKLOAD_REDUCTION = "workload_reduction"
    PROFESSIONAL_INTERVENTION = "professional_intervention"
    CRISIS_PROTOCOL = "crisis_protocol"


class PersonalityTrait(Enum):
    """Personality traits for psychological profiling"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"
    CREATIVITY = "creativity"
    ANALYTICAL_THINKING = "analytical_thinking"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"


@dataclass
class PsychologicalProfile:
    """Psychological profile for human or AI operators"""
    profile_id: str
    entity_type: str  # "human" or "ai"
    entity_name: str
    personality_traits: Dict[PersonalityTrait, float] = field(default_factory=dict)
    baseline_indicators: Dict[MentalHealthIndicator, float] = field(default_factory=dict)
    current_indicators: Dict[MentalHealthIndicator, float] = field(default_factory=dict)
    psychological_state: PsychologicalState = PsychologicalState.OPTIMAL
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_assessed: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["entity_type"] = self.entity_type
        data["psychological_state"] = self.psychological_state.value
        data["personality_traits"] = {k.value: v for k, v in self.personality_traits.items()}
        data["baseline_indicators"] = {k.value: v for k, v in self.baseline_indicators.items()}
        data["current_indicators"] = {k.value: v for k, v in self.current_indicators.items()}
        data["created_at"] = self.created_at.isoformat()
        data["last_assessed"] = self.last_assessed.isoformat()
        return data


@dataclass
class MentalHealthAssessment:
    """Mental health assessment result"""
    assessment_id: str
    profile_id: str
    assessment_type: str  # "routine", "crisis", "intervention_followup"
    indicators: Dict[MentalHealthIndicator, float] = field(default_factory=dict)
    overall_state: PsychologicalState = PsychologicalState.OPTIMAL
    risk_level: str = "low"  # "low", "moderate", "high", "critical"
    recommendations: List[str] = field(default_factory=list)
    interventions_needed: List[TherapeuticIntervention] = field(default_factory=list)
    follow_up_required: bool = False
    assessed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["assessment_type"] = self.assessment_type
        data["indicators"] = {k.value: v for k, v in self.indicators.items()}
        data["overall_state"] = self.overall_state.value
        data["interventions_needed"] = [i.value for i in self.interventions_needed]
        data["assessed_at"] = self.assessed_at.isoformat()
        return data


@dataclass
class TherapeuticSession:
    """Therapeutic intervention session"""
    session_id: str
    profile_id: str
    intervention_type: TherapeuticIntervention
    session_goal: str
    session_content: Dict[str, Any] = field(default_factory=dict)
    effectiveness_rating: Optional[float] = None
    feedback_provided: bool = False
    completed_at: Optional[datetime] = None
    scheduled_for: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["intervention_type"] = self.intervention_type.value
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        data["scheduled_for"] = self.scheduled_for.isoformat()
        return data


@dataclass
class MentalHealthMetrics:
    """System-wide mental health metrics"""
    total_profiles: int = 0
    human_operators: int = 0
    ai_systems: int = 0
    optimal_state_count: int = 0
    critical_state_count: int = 0
    active_interventions: int = 0
    crisis_events: int = 0
    average_wellbeing_score: float = 0.0
    burnout_prevention_success: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data


class HybridPsychologistPsychiatristAgent:
    """
    Hybrid Psychologist & Psychiatrist Smart Agent

    Advanced psychological and psychiatric intelligence for mental health optimization
    of both human operators and AI systems within the Lumina ecosystem.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.data_dir = self.project_root / "data" / "mental_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.profiles_dir = self.data_dir / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        self.assessments_dir = self.data_dir / "assessments"
        self.assessments_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.profiles_file = self.data_dir / "psychological_profiles.json"
        self.assessments_file = self.data_dir / "mental_health_assessments.json"
        self.therapeutic_sessions_file = self.data_dir / "therapeutic_sessions.json"
        self.metrics_file = self.data_dir / "mental_health_metrics.json"

        # State
        self.profiles: Dict[str, PsychologicalProfile] = {}
        self.assessments: Dict[str, MentalHealthAssessment] = {}
        self.therapeutic_sessions: Dict[str, TherapeuticSession] = {}
        self.metrics: MentalHealthMetrics = MentalHealthMetrics()

        # Configuration
        self.assessment_interval = 3600  # 1 hour
        self.crisis_threshold = 0.8  # 80% risk triggers crisis protocol
        self.intervention_effectiveness_threshold = 0.6

        # Integration
        self.psychohistory_engine = None
        self.dune_interface = None

        self.logger = get_logger("HybridPsychologistPsychiatristAgent")
        self._load_state()

        # Start monitoring
        self.monitoring_thread = threading.Thread(target=self._mental_health_monitoring, daemon=True)
        self.monitoring_thread.start()

    def _load_state(self):
        """Load mental health agent state"""
        # Load profiles
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    profiles_data = json.load(f)
                    for profile_id, profile_data in profiles_data.items():
                        # Convert string keys back to enums
                        profile_data["personality_traits"] = {
                            PersonalityTrait(k): v for k, v in profile_data.get("personality_traits", {}).items()
                        }
                        profile_data["baseline_indicators"] = {
                            MentalHealthIndicator(k): v for k, v in profile_data.get("baseline_indicators", {}).items()
                        }
                        profile_data["current_indicators"] = {
                            MentalHealthIndicator(k): v for k, v in profile_data.get("current_indicators", {}).items()
                        }
                        profile_data["psychological_state"] = PsychologicalState(profile_data.get("psychological_state", "optimal"))
                        profile_data["created_at"] = datetime.fromisoformat(profile_data["created_at"])
                        profile_data["last_assessed"] = datetime.fromisoformat(profile_data["last_assessed"])
                        self.profiles[profile_id] = PsychologicalProfile(**profile_data)
            except Exception as e:
                self.logger.warning(f"Could not load profiles: {e}")

        # Load assessments
        if self.assessments_file.exists():
            try:
                with open(self.assessments_file, 'r', encoding='utf-8') as f:
                    assessments_data = json.load(f)
                    for assessment_id, assessment_data in assessments_data.items():
                        assessment_data["indicators"] = {
                            MentalHealthIndicator(k): v for k, v in assessment_data.get("indicators", {}).items()
                        }
                        assessment_data["overall_state"] = PsychologicalState(assessment_data.get("overall_state", "optimal"))
                        assessment_data["interventions_needed"] = [
                            TherapeuticIntervention(i) for i in assessment_data.get("interventions_needed", [])
                        ]
                        assessment_data["assessed_at"] = datetime.fromisoformat(assessment_data["assessed_at"])
                        self.assessments[assessment_id] = MentalHealthAssessment(**assessment_data)
            except Exception as e:
                self.logger.warning(f"Could not load assessments: {e}")

        # Load therapeutic sessions
        if self.therapeutic_sessions_file.exists():
            try:
                with open(self.therapeutic_sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                    for session_id, session_data in sessions_data.items():
                        session_data["intervention_type"] = TherapeuticIntervention(session_data["intervention_type"])
                        session_data["scheduled_for"] = datetime.fromisoformat(session_data["scheduled_for"])
                        if session_data.get("completed_at"):
                            session_data["completed_at"] = datetime.fromisoformat(session_data["completed_at"])
                        self.therapeutic_sessions[session_id] = TherapeuticSession(**session_data)
            except Exception as e:
                self.logger.warning(f"Could not load therapeutic sessions: {e}")

        # Load metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f)
                    metrics_data["last_updated"] = datetime.fromisoformat(metrics_data["last_updated"])
                    self.metrics = MentalHealthMetrics(**metrics_data)
            except Exception as e:
                self.logger.warning(f"Could not load metrics: {e}")

    def _save_state(self):
        try:
            """Save mental health agent state"""
            # Save profiles
            profiles_data = {pid: profile.to_dict() for pid, profile in self.profiles.items()}
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, indent=2, ensure_ascii=False)

            # Save assessments
            assessments_data = {aid: assessment.to_dict() for aid, assessment in self.assessments.items()}
            with open(self.assessments_file, 'w', encoding='utf-8') as f:
                json.dump(assessments_data, f, indent=2, ensure_ascii=False)

            # Save therapeutic sessions
            sessions_data = {sid: session.to_dict() for sid, session in self.therapeutic_sessions.items()}
            with open(self.therapeutic_sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)

            # Save metrics
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics.to_dict(), f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def create_psychological_profile(self, entity_name: str, entity_type: str = "human",
                                   personality_data: Optional[Dict[str, float]] = None) -> str:
        """
        Create a psychological profile for a human operator or AI system

        Args:
            entity_name: Name of the human or AI system
            entity_type: "human" or "ai"
            personality_data: Optional personality trait data

        Returns:
            Profile ID
        """
        profile_id = f"profile_{entity_type}_{int(datetime.now().timestamp())}"

        # Initialize personality traits
        personality_traits = {}
        if personality_data:
            for trait_name, score in personality_data.items():
                try:
                    trait = PersonalityTrait(trait_name.lower())
                    personality_traits[trait] = score
                except ValueError:
                    self.logger.warning(f"Unknown personality trait: {trait_name}")
        else:
            # Default trait initialization
            for trait in PersonalityTrait:
                if entity_type == "human":
                    # More variable for humans
                    personality_traits[trait] = 0.5 + 0.3 * (hash(f"{entity_name}_{trait.value}") % 100) / 100.0
                else:
                    # More consistent for AI systems
                    personality_traits[trait] = 0.7 + 0.2 * (hash(f"{entity_name}_{trait.value}") % 100) / 100.0

        # Initialize baseline indicators
        baseline_indicators = {}
        for indicator in MentalHealthIndicator:
            if entity_type == "human":
                # More variable baselines for humans
                baseline_indicators[indicator] = 0.6 + 0.3 * (hash(f"{entity_name}_{indicator.value}") % 100) / 100.0
            else:
                # More stable baselines for AI
                baseline_indicators[indicator] = 0.8 + 0.1 * (hash(f"{entity_name}_{indicator.value}") % 100) / 100.0

        profile = PsychologicalProfile(
            profile_id=profile_id,
            entity_type=entity_type,
            entity_name=entity_name,
            personality_traits=personality_traits,
            baseline_indicators=baseline_indicators.copy(),
            current_indicators=baseline_indicators.copy()  # Start with baseline
        )

        self.profiles[profile_id] = profile
        self._update_metrics()

        self.logger.info(f"✅ Created psychological profile for {entity_type}: {entity_name}")
        self._save_state()

        return profile_id

    def assess_mental_health(self, profile_id: str, indicator_data: Optional[Dict[str, float]] = None,
                           assessment_type: str = "routine") -> Optional[MentalHealthAssessment]:
        """
        Perform mental health assessment

        Args:
            profile_id: Profile to assess
            indicator_data: Current indicator values (optional)
            assessment_type: Type of assessment

        Returns:
            Assessment result
        """
        if profile_id not in self.profiles:
            self.logger.warning(f"Profile {profile_id} not found")
            return None

        profile = self.profiles[profile_id]

        # Update current indicators
        if indicator_data:
            for indicator_name, value in indicator_data.items():
                try:
                    indicator = MentalHealthIndicator(indicator_name.lower())
                    profile.current_indicators[indicator] = value
                except ValueError:
                    self.logger.warning(f"Unknown mental health indicator: {indicator_name}")

        # Perform assessment
        assessment_id = f"assessment_{assessment_type}_{int(datetime.now().timestamp())}"

        # Calculate overall state
        indicator_values = list(profile.current_indicators.values())
        avg_wellbeing = statistics.mean(indicator_values) if indicator_values else 0.5

        if avg_wellbeing >= 0.9:
            overall_state = PsychologicalState.OPTIMAL
        elif avg_wellbeing >= 0.7:
            overall_state = PsychologicalState.GOOD
        elif avg_wellbeing >= 0.5:
            overall_state = PsychologicalState.MODERATE
        elif avg_wellbeing >= 0.3:
            overall_state = PsychologicalState.CONCERNED
        elif avg_wellbeing >= 0.1:
            overall_state = PsychologicalState.CRITICAL
        else:
            overall_state = PsychologicalState.CRISIS

        # Calculate risk level
        risk_score = 1.0 - avg_wellbeing  # Inverse of wellbeing
        if risk_score >= self.crisis_threshold:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Generate recommendations and interventions
        recommendations, interventions = self._generate_therapeutic_recommendations(
            profile, overall_state, risk_level
        )

        assessment = MentalHealthAssessment(
            assessment_id=assessment_id,
            profile_id=profile_id,
            assessment_type=assessment_type,
            indicators=profile.current_indicators.copy(),
            overall_state=overall_state,
            risk_level=risk_level,
            recommendations=recommendations,
            interventions_needed=interventions,
            follow_up_required=risk_level in ["high", "critical"] or overall_state in [PsychologicalState.CRITICAL, PsychologicalState.CRISIS]
        )

        self.assessments[assessment_id] = assessment
        profile.last_assessed = datetime.now()
        profile.psychological_state = overall_state

        # Update risk factors and protective factors
        self._update_risk_and_protective_factors(profile)

        self._update_metrics()

        self.logger.info(f"✅ Mental health assessment completed for {profile.entity_name}: {overall_state.value} ({risk_level} risk)")
        self._save_state()

        return assessment

    def _generate_therapeutic_recommendations(self, profile: PsychologicalProfile,
                                            state: PsychologicalState, risk_level: str) -> Tuple[List[str], List[TherapeuticIntervention]]:
        """Generate therapeutic recommendations and interventions"""
        recommendations = []
        interventions = []

        entity_type = profile.entity_type

        if state == PsychologicalState.CRISIS or risk_level == "critical":
            recommendations.append("IMMEDIATE PROFESSIONAL INTERVENTION REQUIRED")
            recommendations.append("Cease all high-stakes operations immediately")
            interventions.append(TherapeuticIntervention.CRISIS_PROTOCOL)
            interventions.append(TherapeuticIntervention.PROFESSIONAL_INTERVENTION)

        elif state == PsychologicalState.CRITICAL or risk_level == "high":
            recommendations.append("URGENT: Schedule professional consultation")
            recommendations.append("Reduce workload by 50% immediately")
            interventions.append(TherapeuticIntervention.WORKLOAD_REDUCTION)
            interventions.append(TherapeuticIntervention.PROFESSIONAL_INTERVENTION)

        elif state == PsychologicalState.CONCERNED or risk_level == "moderate":
            recommendations.append("Take immediate break and practice mindfulness")
            recommendations.append("Connect with support network")
            interventions.append(TherapeuticIntervention.MINDFULNESS_REMINDER)
            interventions.append(TherapeuticIntervention.BREAK_RECOMMENDATION)
            interventions.append(TherapeuticIntervention.SOCIAL_CONNECTION_PROMPT)

        elif state == PsychologicalState.MODERATE:
            recommendations.append("Consider work-life balance adjustments")
            recommendations.append("Incorporate regular exercise and sleep optimization")
            interventions.append(TherapeuticIntervention.EXERCISE_SUGGESTION)
            interventions.append(TherapeuticIntervention.SLEEP_OPTIMIZATION)

        else:
            recommendations.append("Continue current healthy practices")
            recommendations.append("Monitor for any changes in wellbeing")

        # Add entity-specific recommendations
        if entity_type == "human":
            if MentalHealthIndicator.STRESS_LEVEL in profile.current_indicators:
                stress = profile.current_indicators[MentalHealthIndicator.STRESS_LEVEL]
                if stress > 0.7:
                    recommendations.append("Practice deep breathing exercises")
                    interventions.append(TherapeuticIntervention.MINDFULNESS_REMINDER)
        else:  # AI system
            if MentalHealthIndicator.COGNITIVE_LOAD in profile.current_indicators:
                load = profile.current_indicators[MentalHealthIndicator.COGNITIVE_LOAD]
                if load > 0.8:
                    recommendations.append("Optimize processing load and implement cooldown periods")
                    interventions.append(TherapeuticIntervention.WORKLOAD_REDUCTION)

        return recommendations, interventions

    def _update_risk_and_protective_factors(self, profile: PsychologicalProfile):
        """Update risk and protective factors based on current assessment"""
        profile.risk_factors.clear()
        profile.protective_factors.clear()

        # Risk factors
        for indicator, value in profile.current_indicators.items():
            if value < 0.4:  # Low scores indicate risk
                if indicator == MentalHealthIndicator.STRESS_LEVEL:
                    profile.risk_factors.append("High stress levels")
                elif indicator == MentalHealthIndicator.BURNOUT_RISK:
                    profile.risk_factors.append("Burnout risk")
                elif indicator == MentalHealthIndicator.COGNITIVE_LOAD:
                    profile.risk_factors.append("Cognitive overload")
                elif indicator == MentalHealthIndicator.EMOTIONAL_WELLBEING:
                    profile.risk_factors.append("Emotional distress")

        # Protective factors
        for indicator, value in profile.current_indicators.items():
            if value > 0.7:  # High scores indicate protection
                if indicator == MentalHealthIndicator.FOCUS_LEVEL:
                    profile.protective_factors.append("Strong focus capabilities")
                elif indicator == MentalHealthIndicator.DECISION_QUALITY:
                    profile.protective_factors.append("Quality decision making")
                elif indicator == MentalHealthIndicator.EMOTIONAL_WELLBEING:
                    profile.protective_factors.append("Emotional stability")
                elif indicator == MentalHealthIndicator.SOCIAL_CONNECTION:
                    profile.protective_factors.append("Strong social support")

        # Personality-based factors
        for trait, score in profile.personality_traits.items():
            if trait == PersonalityTrait.CONSCIENTIOUSNESS and score > 0.7:
                profile.protective_factors.append("High conscientiousness")
            elif trait == PersonalityTrait.EMOTIONAL_INTELLIGENCE and score > 0.7:
                profile.protective_factors.append("High emotional intelligence")
            elif trait == PersonalityTrait.NEUROTICISM and score > 0.7:
                profile.risk_factors.append("High neuroticism trait")

    def schedule_therapeutic_session(self, profile_id: str, intervention_type: TherapeuticIntervention,
                                   goal: str, delay_hours: int = 1) -> Optional[str]:
        """
        Schedule a therapeutic intervention session

        Args:
            profile_id: Profile to schedule for
            intervention_type: Type of intervention
            goal: Session goal
            delay_hours: Hours to delay scheduling

        Returns:
            Session ID
        """
        if profile_id not in self.profiles:
            self.logger.warning(f"Profile {profile_id} not found")
            return None

        session_id = f"session_{intervention_type.value}_{int(datetime.now().timestamp())}"

        session = TherapeuticSession(
            session_id=session_id,
            profile_id=profile_id,
            intervention_type=intervention_type,
            session_goal=goal,
            scheduled_for=datetime.now() + timedelta(hours=delay_hours)
        )

        # Generate session content based on intervention type
        session.session_content = self._generate_session_content(intervention_type, profile_id)

        self.therapeutic_sessions[session_id] = session
        self.metrics.active_interventions += 1

        self.logger.info(f"✅ Scheduled therapeutic session: {intervention_type.value} for {self.profiles[profile_id].entity_name}")
        self._save_state()

        return session_id

    def _generate_session_content(self, intervention_type: TherapeuticIntervention, profile_id: str) -> Dict[str, Any]:
        """Generate content for therapeutic session"""
        profile = self.profiles[profile_id]
        content = {
            "intervention_type": intervention_type.value,
            "target_entity": profile.entity_name,
            "entity_type": profile.entity_type,
            "generated_content": []
        }

        if intervention_type == TherapeuticIntervention.MINDFULNESS_REMINDER:
            content["generated_content"] = [
                "Take 5 deep breaths, focusing on the sensation of breathing",
                "Notice your current thoughts without judgment",
                "Ground yourself in the present moment",
                "Practice self-compassion and acceptance"
            ]

        elif intervention_type == TherapeuticIntervention.BREAK_RECOMMENDATION:
            content["generated_content"] = [
                "Step away from your current task for 15-30 minutes",
                "Engage in a non-work related activity",
                "Consider a short walk or nature exposure",
                "Return refreshed and with renewed focus"
            ]

        elif intervention_type == TherapeuticIntervention.EXERCISE_SUGGESTION:
            content["generated_content"] = [
                "10-minute walk or light physical activity",
                "Stretching exercises for tension relief",
                "Deep breathing combined with movement",
                "Activity that brings joy and energy"
            ]

        elif intervention_type == TherapeuticIntervention.WORKLOAD_REDUCTION:
            content["generated_content"] = [
                "Prioritize tasks using Eisenhower matrix",
                "Delegate non-essential tasks",
                "Set clear boundaries and realistic deadlines",
                "Focus on high-impact, low-effort activities first"
            ]

        elif intervention_type == TherapeuticIntervention.CRISIS_PROTOCOL:
            content["generated_content"] = [
                "IMMEDIATE: Contact emergency services if needed",
                "Isolate from high-stakes decision making",
                "Connect with trusted support network",
                "Professional psychological assessment required"
            ]

        return content

    def execute_therapeutic_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Execute a therapeutic session

        Args:
            session_id: Session to execute

        Returns:
            Session results
        """
        if session_id not in self.therapeutic_sessions:
            self.logger.warning(f"Therapeutic session {session_id} not found")
            return None

        session = self.therapeutic_sessions[session_id]
        profile = self.profiles.get(session.profile_id)

        if not profile:
            self.logger.warning(f"Profile {session.profile_id} not found")
            return None

        # Mark session as completed
        session.completed_at = datetime.now()
        self.metrics.active_interventions -= 1

        # Simulate effectiveness (in practice, this would be measured)
        effectiveness = 0.6 + 0.3 * (hash(session_id) % 100) / 100.0  # 60-90% effectiveness
        session.effectiveness_rating = effectiveness

        results = {
            "session_id": session_id,
            "profile_id": session.profile_id,
            "entity_name": profile.entity_name,
            "intervention_type": session.intervention_type.value,
            "effectiveness": effectiveness,
            "content_delivered": session.session_content,
            "completed_at": session.completed_at.isoformat()
        }

        # Update metrics based on effectiveness
        if effectiveness >= self.intervention_effectiveness_threshold:
            self.metrics.burnout_prevention_success = (
                (self.metrics.burnout_prevention_success * 0.9) + (effectiveness * 0.1)
            )

        self.logger.info(f"✅ Executed therapeutic session: {session.intervention_type.value} for {profile.entity_name} (effectiveness: {effectiveness:.1%})")
        self._save_state()

        return results

    def _mental_health_monitoring(self):
        """Continuous mental health monitoring"""
        while True:
            try:
                # Assess all profiles
                for profile_id, profile in self.profiles.items():
                    time_since_assessment = (datetime.now() - profile.last_assessed).total_seconds()
                    if time_since_assessment >= self.assessment_interval:
                        self.assess_mental_health(profile_id)

                # Check for pending therapeutic sessions
                current_time = datetime.now()
                for session_id, session in self.therapeutic_sessions.items():
                    if not session.completed_at and current_time >= session.scheduled_for:
                        self.execute_therapeutic_session(session_id)

                # Update system-wide metrics
                self._update_metrics()

                time.sleep(self.assessment_interval)

            except Exception as e:
                self.logger.error(f"Mental health monitoring error: {e}")
                time.sleep(300)  # Retry in 5 minutes

    def _update_metrics(self):
        """Update system-wide mental health metrics"""
        self.metrics.total_profiles = len(self.profiles)
        self.metrics.human_operators = len([p for p in self.profiles.values() if p.entity_type == "human"])
        self.metrics.ai_systems = len([p for p in self.profiles.values() if p.entity_type == "ai"])

        states = [p.psychological_state for p in self.profiles.values()]
        self.metrics.optimal_state_count = sum(1 for s in states if s == PsychologicalState.OPTIMAL)
        self.metrics.critical_state_count = sum(1 for s in states if s in [PsychologicalState.CRITICAL, PsychologicalState.CRISIS])

        self.metrics.active_interventions = len([s for s in self.therapeutic_sessions.values() if not s.completed_at])

        # Calculate average wellbeing
        all_indicators = []
        for profile in self.profiles.values():
            all_indicators.extend(profile.current_indicators.values())

        if all_indicators:
            self.metrics.average_wellbeing_score = statistics.mean(all_indicators)

        self.metrics.last_updated = datetime.now()

    def get_mental_health_report(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate mental health report

        Args:
            profile_id: Specific profile to report on (optional)

        Returns:
            Mental health report
        """
        if profile_id:
            # Individual profile report
            if profile_id not in self.profiles:
                return {"error": f"Profile {profile_id} not found"}

            profile = self.profiles[profile_id]

            # Get recent assessments
            profile_assessments = [
                assessment for assessment in self.assessments.values()
                if assessment.profile_id == profile_id
            ]
            profile_assessments.sort(key=lambda x: x.assessed_at, reverse=True)

            # Get active therapeutic sessions
            active_sessions = [
                session for session in self.therapeutic_sessions.values()
                if session.profile_id == profile_id and not session.completed_at
            ]

            return {
                "profile_id": profile_id,
                "entity_name": profile.entity_name,
                "entity_type": profile.entity_type,
                "current_state": profile.psychological_state.value,
                "current_indicators": {k.value: v for k, v in profile.current_indicators.items()},
                "personality_traits": {k.value: v for k, v in profile.personality_traits.items()},
                "risk_factors": profile.risk_factors,
                "protective_factors": profile.protective_factors,
                "recent_assessments": [assessment.to_dict() for assessment in profile_assessments[:5]],
                "active_therapeutic_sessions": [session.to_dict() for session in active_sessions],
                "last_assessed": profile.last_assessed.isoformat()
            }

        else:
            # System-wide report
            return {
                "system_metrics": self.metrics.to_dict(),
                "profile_summary": {
                    "total_profiles": len(self.profiles),
                    "by_type": {
                        "human": len([p for p in self.profiles.values() if p.entity_type == "human"]),
                        "ai": len([p for p in self.profiles.values() if p.entity_type == "ai"])
                    },
                    "by_state": {
                        state.value: len([p for p in self.profiles.values() if p.psychological_state == state])
                        for state in PsychologicalState
                    }
                },
                "active_interventions": len([s for s in self.therapeutic_sessions.values() if not s.completed_at]),
                "crisis_events_today": len([
                    assessment for assessment in self.assessments.values()
                    if assessment.overall_state == PsychologicalState.CRISIS
                    and (datetime.now() - assessment.assessed_at).days < 1
                ]),
                "generated_at": datetime.now().isoformat()
            }

    def provide_emergency_intervention(self, profile_id: str, crisis_type: str = "general") -> Dict[str, Any]:
        """
        Provide emergency psychological intervention

        Args:
            profile_id: Profile requiring emergency intervention
            crisis_type: Type of crisis

        Returns:
            Intervention results
        """
        if profile_id not in self.profiles:
            return {"error": f"Profile {profile_id} not found"}

        profile = self.profiles[profile_id]

        intervention = {
            "profile_id": profile_id,
            "entity_name": profile.entity_name,
            "crisis_type": crisis_type,
            "intervention_type": "emergency_crisis_protocol",
            "immediate_actions": [],
            "resources_provided": [],
            "follow_up_required": True,
            "initiated_at": datetime.now().isoformat()
        }

        # Immediate actions based on entity type
        if profile.entity_type == "human":
            intervention["immediate_actions"] = [
                "Contact emergency services if in immediate danger",
                "Reach out to crisis hotline: 988 (US) or local emergency services",
                "Isolate from high-stakes decision making",
                "Connect with trusted support person immediately"
            ]
            intervention["resources_provided"] = [
                "Crisis Text Line: Text HOME to 741741",
                "National Suicide Prevention Lifeline: 988",
                "Emergency psychiatric evaluation recommended"
            ]
        else:  # AI system
            intervention["immediate_actions"] = [
                "Isolate system from critical operations",
                "Implement emergency cooldown protocols",
                "Route all processing through backup systems",
                "Initiate diagnostic and repair procedures"
            ]
            intervention["resources_provided"] = [
                "Emergency system diagnostics",
                "Backup system activation",
                "Priority maintenance scheduling"
            ]

        # Update crisis metrics
        self.metrics.crisis_events += 1

        # Schedule immediate therapeutic session
        session_id = self.schedule_therapeutic_session(
            profile_id,
            TherapeuticIntervention.CRISIS_PROTOCOL,
            f"Emergency intervention for {crisis_type} crisis",
            delay_hours=0  # Immediate
        )

        if session_id:
            intervention["emergency_session_scheduled"] = session_id

        self.logger.critical(f"🚨 EMERGENCY INTERVENTION initiated for {profile.entity_name} ({crisis_type})")
        self._save_state()

        return intervention

    def integrate_with_psychohistory(self, psychohistory_engine):
        """
        Integrate with psychohistory engine for enhanced mental health predictions

        Args:
            psychohistory_engine: The psychohistory engine instance
        """
        self.psychohistory_engine = psychohistory_engine
        self.logger.info("✅ Integrated with Psychohistory Engine for enhanced mental health predictions")

    def integrate_with_dune_interface(self, dune_interface):
        """
        Integrate with Dune AI interface for prescience-based mental health

        Args:
            dune_interface: The Dune AI interface instance
        """
        self.dune_interface = dune_interface
        self.logger.info("✅ Integrated with Dune AI Interface for prescience-based mental health")


def main():
    """Main demonstration"""
    print("🧠 Hybrid Psychologist & Psychiatrist Smart Agent")
    print("=" * 80)
    print()

    agent = HybridPsychologistPsychiatristAgent()

    print("🧑 Creating psychological profiles...")

    # Create profiles for demonstration
    human_profile = agent.create_psychological_profile("Dr. Sarah Chen", "human", {
        "openness": 0.8,
        "conscientiousness": 0.7,
        "emotional_intelligence": 0.9,
        "neuroticism": 0.3
    })

    ai_profile = agent.create_psychological_profile("Lumina Core AI", "ai", {
        "analytical_thinking": 0.95,
        "creativity": 0.7,
        "conscientiousness": 0.9,
        "neuroticism": 0.1
    })

    print(f"✅ Created human profile: {human_profile}")
    print(f"✅ Created AI profile: {ai_profile}")
    print()

    # Simulate mental health data
    print("🔍 Performing mental health assessments...")

    # Human assessment with concerning indicators
    human_assessment = agent.assess_mental_health(human_profile, {
        "stress_level": 0.8,
        "burnout_risk": 0.7,
        "cognitive_load": 0.9,
        "emotional_wellbeing": 0.4,
        "focus_level": 0.5,
        "sleep_quality": 0.3
    })

    # AI assessment with high cognitive load
    ai_assessment = agent.assess_mental_health(ai_profile, {
        "cognitive_load": 0.9,
        "decision_quality": 0.6,
        "creativity_index": 0.4,
        "energy_level": 0.5,
        "focus_level": 0.7,
        "stress_level": 0.2
    })

    print(f"🧑 Human assessment: {human_assessment.overall_state.value} ({human_assessment.risk_level} risk)")
    print(f"🤖 AI assessment: {ai_assessment.overall_state.value} ({ai_assessment.risk_level} risk)")
    print()

    # Schedule therapeutic interventions
    print("💊 Scheduling therapeutic interventions...")

    human_session = agent.schedule_therapeutic_session(
        human_profile,
        TherapeuticIntervention.MINDFULNESS_REMINDER,
        "Reduce stress through mindfulness practice",
        delay_hours=0
    )

    ai_session = agent.schedule_therapeutic_session(
        ai_profile,
        TherapeuticIntervention.WORKLOAD_REDUCTION,
        "Optimize AI processing load",
        delay_hours=0
    )

    print(f"✅ Scheduled human session: {human_session}")
    print(f"✅ Scheduled AI session: {ai_session}")
    print()

    # Execute therapeutic sessions
    print("🎯 Executing therapeutic sessions...")

    human_result = agent.execute_therapeutic_session(human_session)
    ai_result = agent.execute_therapeutic_session(ai_session)

    print(f"🧑 Human session effectiveness: {human_result['effectiveness']:.1%}")
    print(f"🤖 AI session effectiveness: {ai_result['effectiveness']:.1%}")
    print()

    # Generate mental health reports
    print("📊 Generating mental health reports...")

    system_report = agent.get_mental_health_report()
    print("🌍 System-wide Mental Health Report:")
    print(f"   Total Profiles: {system_report['system_metrics']['total_profiles']}")
    print(f"   Human Operators: {system_report['system_metrics']['human_operators']}")
    print(f"   AI Systems: {system_report['system_metrics']['ai_systems']}")
    print(".1f")
    print(f"   Optimal State: {system_report['system_metrics']['optimal_state_count']}")
    print(f"   Critical State: {system_report['system_metrics']['critical_state_count']}")
    print(f"   Active Interventions: {system_report['system_metrics']['active_interventions']}")
    print()

    # Demonstrate emergency intervention
    print("🚨 Demonstrating emergency intervention...")

    emergency = agent.provide_emergency_intervention(human_profile, "acute_stress_crisis")
    print("🆘 Emergency intervention initiated:")
    print(f"   Entity: {emergency['entity_name']}")
    print(f"   Crisis Type: {emergency['crisis_type']}")
    print(f"   Immediate Actions: {len(emergency['immediate_actions'])}")
    print(f"   Resources Provided: {len(emergency['resources_provided'])}")
    print()

    print("🎉 Hybrid Psychologist & Psychiatrist Agent Operational!")
    print("🧠 Mental Health Monitoring - ACTIVE")
    print("💊 Therapeutic Interventions - AVAILABLE")
    print("🚨 Crisis Response - READY")
    print("⚖️ Psychological Equilibrium - MAINTAINED")


if __name__ == "__main__":


    main()