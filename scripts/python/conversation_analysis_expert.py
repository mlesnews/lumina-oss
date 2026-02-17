#!/usr/bin/env python3
"""
Conversation Analysis Expert - Dual Role Specialist

Specialized dual-role expert:
- Speech Pathologist
- Behavioral Psychologist/Psychiatrist

Analyzes where conversations are falling down and defines:
- Active speaking vs Passive speaking
- Conversation breakdown patterns
- Speech behavior analysis
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

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

logger = get_logger("ConversationAnalysisExpert")


@dataclass
class SpeakingMode:
    """Definition of speaking mode"""
    mode_type: str  # "active" or "passive"
    characteristics: List[str]
    indicators: List[str]
    context_dependencies: List[str]
    confidence_threshold: Optional[float] = None


@dataclass
class ConversationBreakdown:
    """Analysis of where conversation broke down"""
    breakdown_point: str
    cause: str
    speaking_mode_at_breakdown: str
    confidence_level: float
    recommendations: List[str]
    context: Dict[str, Any]


class ConversationAnalysisExpert:
    """
    Dual-Role Specialist:
    - Speech Pathologist: Analyzes speech patterns, articulation, fluency
    - Behavioral Psychologist/Psychiatrist: Analyzes behavior, communication patterns, breakdowns
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize conversation analysis expert"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.analysis_history = []

        logger.info("✅ Conversation Analysis Expert initialized")
        logger.info("   Role: Speech Pathologist + Behavioral Psychologist/Psychiatrist")

    def define_active_vs_passive_speaking(self) -> Dict[str, SpeakingMode]:
        """
        Define the difference between active speaking and passive speaking

        Returns: Dictionary with definitions of both modes
        """
        active_speaking = SpeakingMode(
            mode_type="active",
            characteristics=[
                "Explicit activation required (e.g., voice input button click)",
                "User-initiated communication",
                "Intentional speech production",
                "Conscious engagement in conversation",
                "Clear intent to communicate"
            ],
            indicators=[
                "Voice input button pressed/clicked",
                "Explicit activation signal",
                "User-initiated interaction",
                "Intentional pause before speaking",
                "Clear speech onset"
            ],
            context_dependencies=[
                "User intent to communicate",
                "Explicit activation context",
                "Confidence in user's intent",
                "Contextual appropriateness"
            ],
            confidence_threshold=0.8  # High confidence required for active mode
        )

        passive_speaking = SpeakingMode(
            mode_type="passive",
            characteristics=[
                "Background/ambient listening",
                "No explicit activation required",
                "Continuous monitoring",
                "Unintentional or background speech capture",
                "Ambient noise/voice detection"
            ],
            indicators=[
                "No explicit activation",
                "Background monitoring active",
                "Ambient sound detection",
                "Continuous listening mode",
                "No user-initiated signal"
            ],
            context_dependencies=[
                "Background monitoring context",
                "Ambient environment",
                "No explicit user intent",
                "Lower confidence in intent"
            ],
            confidence_threshold=0.5  # Lower threshold for passive mode
        )

        definitions = {
            "active": active_speaking,
            "passive": passive_speaking
        }

        logger.info("📋 Defined Active vs Passive Speaking Modes")
        logger.info(f"   Active: {len(active_speaking.characteristics)} characteristics")
        logger.info(f"   Passive: {len(passive_speaking.characteristics)} characteristics")

        return definitions

    def analyze_conversation_breakdown(
        self,
        conversation_data: Dict[str, Any],
        speaking_mode: str,
        confidence_level: float
    ) -> ConversationBreakdown:
        """
        Analyze where conversation broke down

        Args:
            conversation_data: Conversation context and data
            speaking_mode: "active" or "passive"
            confidence_level: Confidence in the interaction

        Returns: Analysis of breakdown
        """
        # Speech Pathologist Analysis
        speech_issues = []
        if confidence_level < 0.7:
            speech_issues.append("Low confidence in speech recognition")
        if speaking_mode == "passive" and confidence_level > 0.6:
            speech_issues.append("Passive mode with high confidence - may indicate misclassification")

        # Behavioral Psychologist Analysis
        behavioral_issues = []
        if "interruption" in conversation_data.get("issues", []):
            behavioral_issues.append("Interruption detected - system responding too quickly")
        if "infinite_loop" in conversation_data.get("issues", []):
            behavioral_issues.append("Infinite loop - lack of feedback/state tracking")
        if "context_mismatch" in conversation_data.get("issues", []):
            behavioral_issues.append("Context mismatch - wrong mode activated")

        # Determine breakdown point
        breakdown_point = conversation_data.get("breakdown_point", "unknown")
        if not breakdown_point or breakdown_point == "unknown":
            if speech_issues:
                breakdown_point = "Speech recognition/classification"
            elif behavioral_issues:
                breakdown_point = "Behavioral pattern/feedback loop"
            else:
                breakdown_point = "Context-dependent decision making"

        # Generate recommendations
        recommendations = []

        # Speech Pathologist Recommendations
        if speech_issues:
            recommendations.append("Improve speech recognition confidence thresholds")
            recommendations.append("Clarify active vs passive mode classification")
            recommendations.append("Add context-dependent confidence adjustment")

        # Behavioral Psychologist Recommendations
        if behavioral_issues:
            recommendations.append("Implement feedback loops to prevent infinite loops")
            recommendations.append("Add state tracking for conversation flow")
            recommendations.append("Increase wait times to prevent interruption")
            recommendations.append("Context-dependent listening mode selection")

        # General recommendations
        recommendations.append("Use context + confidence level to determine listening mode")
        recommendations.append("Wait longer before responding (20+ seconds)")
        recommendations.append("Only activate on explicit user intent (active mode)")

        breakdown = ConversationBreakdown(
            breakdown_point=breakdown_point,
            cause=" | ".join(speech_issues + behavioral_issues) if (speech_issues or behavioral_issues) else "Context/confidence mismatch",
            speaking_mode_at_breakdown=speaking_mode,
            confidence_level=confidence_level,
            recommendations=recommendations,
            context=conversation_data
        )

        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "breakdown": breakdown,
            "speaking_mode": speaking_mode,
            "confidence": confidence_level
        })

        logger.info(f"🔍 Analyzed conversation breakdown: {breakdown_point}")
        logger.info(f"   Cause: {breakdown.cause}")
        logger.info(f"   Recommendations: {len(recommendations)}")

        return breakdown

    def get_listening_mode_recommendation(
        self,
        context: Dict[str, Any],
        confidence_level: float,
        explicit_activation: bool = False,
        wake_word_detected: bool = False
    ) -> str:
        """
        Recommend listening mode based on context and confidence

        Args:
            context: Current conversation context
            confidence_level: Confidence in user intent
            explicit_activation: Whether user explicitly activated (e.g., clicked voice button)
            wake_word_detected: Whether wake word was detected (e.g., "Hey JARVIS", "Hey LUMINA")

        Returns: "active" or "passive"
        """
        # Explicit activation = always active
        if explicit_activation:
            return "active"

        # Wake word detected = active listening mode
        if wake_word_detected:
            return "active"

        # High confidence + clear context = active
        if confidence_level >= 0.8 and context.get("clear_intent", False):
            return "active"

        # Low confidence or ambiguous = passive (or wait for explicit activation)
        if confidence_level < 0.6:
            return "passive"

        # Context-dependent: Use context + confidence
        context_weight = context.get("context_strength", 0.5)
        combined_score = (confidence_level * 0.6) + (context_weight * 0.4)

        if combined_score >= 0.7:
            return "active"
        else:
            return "passive"

    def get_dynamic_scaling_parameters(
        self,
        listening_mode: str,
        confidence_level: float,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Get dynamic scaling parameters for listening sensitivity

        ACT OF LISTENING: Dynamic scaling adjusts sensitivity based on:
        - Listening mode (active vs passive)
        - Confidence level
        - Context strength
        - Timing factors

        Returns: Dictionary with scaling parameters
        """
        base_sensitivity = 0.5  # Base listening sensitivity

        # Active mode: Higher sensitivity (more responsive)
        if listening_mode == "active":
            sensitivity_multiplier = 1.5
            response_time_multiplier = 0.8  # Faster response
        else:
            # Passive mode: Lower sensitivity (less responsive, wait for clear signal)
            sensitivity_multiplier = 0.7
            response_time_multiplier = 1.5  # Slower response, more cautious

        # Confidence-based scaling
        confidence_scaling = confidence_level * 0.3  # 0-0.3 range

        # Context-based scaling
        context_strength = context.get("context_strength", 0.5)
        context_scaling = context_strength * 0.2  # 0-0.2 range

        # Calculate final sensitivity
        final_sensitivity = base_sensitivity * sensitivity_multiplier + confidence_scaling + context_scaling
        final_sensitivity = max(0.1, min(1.0, final_sensitivity))  # Clamp 0.1-1.0

        # Timing parameters
        base_wait_time = 20.0  # Base wait time (already doubled)
        wait_time = base_wait_time * response_time_multiplier

        # Dynamic scaling for wake word detection
        wake_word_sensitivity = 0.8 if listening_mode == "passive" else 0.95  # Higher in passive mode

        return {
            "listening_sensitivity": final_sensitivity,
            "response_wait_time": wait_time,
            "wake_word_sensitivity": wake_word_sensitivity,
            "confidence_threshold": confidence_level,
            "scaling_factor": sensitivity_multiplier
        }

    def get_timing_parameters(
        self,
        listening_mode: str,
        context: Dict[str, Any],
        confidence_level: float
    ) -> Dict[str, float]:
        """
        Get timing parameters for listening and response

        ACT OF LISTENING: Timing is critical:
        - When to start listening
        - How long to wait before responding
        - When to stop listening
        - Dynamic timing based on context

        Returns: Dictionary with timing parameters
        """
        # Base timing (already doubled to 20 seconds)
        base_response_wait = 20.0

        # Active mode: Faster response (but still respectful)
        if listening_mode == "active":
            response_wait = base_response_wait * 0.8  # 16 seconds
            listening_duration = 60.0  # Listen for up to 60 seconds
            pause_detection = 2.0  # Detect pauses after 2 seconds
        else:
            # Passive mode: Longer wait, more cautious
            response_wait = base_response_wait * 1.5  # 30 seconds
            listening_duration = 120.0  # Listen for up to 2 minutes
            pause_detection = 5.0  # Detect pauses after 5 seconds

        # Confidence-based timing adjustment
        if confidence_level < 0.6:
            response_wait *= 1.3  # Wait longer if low confidence
        elif confidence_level > 0.8:
            response_wait *= 0.9  # Slightly faster if high confidence

        # Context-based timing
        if context.get("urgent", False):
            response_wait *= 0.7  # Faster for urgent
        if context.get("complex", False):
            response_wait *= 1.2  # Longer for complex

        return {
            "response_wait_time": response_wait,
            "listening_duration": listening_duration,
            "pause_detection_threshold": pause_detection,
            "wake_word_timeout": 3.0,  # Timeout for wake word detection
            "silence_threshold": 1.0,  # Silence threshold before considering pause
            "max_listening_time": listening_duration
        }

    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        definitions = self.define_active_vs_passive_speaking()

        report = {
            "timestamp": datetime.now().isoformat(),
            "expert_role": "Speech Pathologist + Behavioral Psychologist/Psychiatrist",
            "definitions": {
                "active": {
                    "type": definitions["active"].mode_type,
                    "characteristics": definitions["active"].characteristics,
                    "indicators": definitions["active"].indicators,
                    "context_dependencies": definitions["active"].context_dependencies,
                    "confidence_threshold": definitions["active"].confidence_threshold
                },
                "passive": {
                    "type": definitions["passive"].mode_type,
                    "characteristics": definitions["passive"].characteristics,
                    "indicators": definitions["passive"].indicators,
                    "context_dependencies": definitions["passive"].context_dependencies,
                    "confidence_threshold": definitions["passive"].confidence_threshold
                }
            },
            "breakdown_analyses": [
                {
                    "breakdown_point": b["breakdown"].breakdown_point,
                    "cause": b["breakdown"].cause,
                    "recommendations": b["breakdown"].recommendations
                }
                for b in self.analysis_history
            ],
            "key_insights": [
                "Active speaking requires explicit activation (voice button click)",
                "Passive speaking is background/ambient listening",
                "Context + confidence level determines listening mode",
                "Wait times must be longer to prevent interruption",
                "Feedback loops prevent infinite loops"
            ]
        }

        return report


def main():
    """Main entry point"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Conversation Analysis Expert")
    parser.add_argument("--define-modes", action="store_true", help="Define active vs passive speaking")
    parser.add_argument("--analyze", type=str, help="Analyze conversation breakdown (JSON file)")
    parser.add_argument("--report", action="store_true", help="Generate analysis report")

    args = parser.parse_args()

    expert = ConversationAnalysisExpert()

    if args.define_modes:
        definitions = expert.define_active_vs_passive_speaking()
        print("\n📋 Active vs Passive Speaking Definitions:")
        print("=" * 70)
        for mode_type, mode in definitions.items():
            print(f"\n{mode_type.upper()} SPEAKING:")
            print(f"  Characteristics: {', '.join(mode.characteristics[:3])}...")
            print(f"  Indicators: {', '.join(mode.indicators[:3])}...")
            print(f"  Confidence Threshold: {mode.confidence_threshold}")

    if args.analyze:
        try:
            with open(args.analyze, 'r') as f:
                conversation_data = json.load(f)
            breakdown = expert.analyze_conversation_breakdown(
                conversation_data,
                conversation_data.get("speaking_mode", "unknown"),
                conversation_data.get("confidence", 0.5)
            )
            print(f"\n🔍 Breakdown Analysis:")
            print(f"  Point: {breakdown.breakdown_point}")
            print(f"  Cause: {breakdown.cause}")
            print(f"  Recommendations: {len(breakdown.recommendations)}")
        except Exception as e:
            logger.error(f"Failed to analyze: {e}")

    if args.report:
        report = expert.generate_analysis_report()
        print("\n📊 Analysis Report:")
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":


    sys.exit(main())