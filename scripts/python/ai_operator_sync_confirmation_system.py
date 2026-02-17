#!/usr/bin/env python3
"""
AI-Operator Sync Confirmation System

PEAK Standard: Root cause fix for workflow drift.
Ensures AI and operator are synchronized before execution.

Workflow:
1. Receive input (voice/text)
2. Analyze intent
3. Reformulate in AI Speak + Grammarly CLI format
4. Present back for confirmation
5. Execute only after operator confirms
6. Prevent drift by maintaining stable frequency

Tags: #PEAK #SYNC #CONFIRMATION #WORKFLOW #ROOT_CAUSE @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIOperatorSync")


class SyncStatus(Enum):
    """Sync status between AI and operator"""
    UNSYNCED = "unsynced"  # Not confirmed, don't proceed
    PENDING_CONFIRMATION = "pending_confirmation"  # Waiting for operator
    CONFIRMED = "confirmed"  # Operator confirmed, proceed
    EXECUTING = "executing"  # Currently executing
    COMPLETE = "complete"  # Execution complete


@dataclass
class ReformulatedRequest:
    """Reformulated request in AI Speak format"""
    original_input: str
    intent_summary: str
    reformulated_text: str  # AI Speak + Grammarly formatted
    clarity_score: float  # 0-1
    confidence_score: float  # 0-1
    requires_confirmation: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConfirmationRequest:
    """Confirmation request presented to operator"""
    request_id: str
    reformulated: ReformulatedRequest
    status: SyncStatus
    operator_response: Optional[str] = None
    confirmed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class AIOperatorSyncConfirmationSystem:
    """
    AI-Operator Sync Confirmation System

    PEAK Standard implementation:
    - Diagnoses: Why sync fails (no confirmation loop)
    - Fixes: Adds confirmation before execution
    - Prevents: Workflow drift by requiring sync
    - Creates: Reusable pattern for all AI-operator interactions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize sync confirmation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.data_dir = project_root / "data" / "ai_operator_sync"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Pending confirmations
        self.pending_confirmations: Dict[str, ConfirmationRequest] = {}

        # Sync state
        self.current_sync_status = SyncStatus.UNSYNCED
        self.sync_frequency_stable = True

        # Integration with intent classifier
        try:
            from jarvis_intent_classifier import get_jarvis_intent_classifier
            self.intent_classifier = get_jarvis_intent_classifier(self.project_root)
        except ImportError:
            self.intent_classifier = None
            logger.debug("Intent classifier not available")

        logger.info("=" * 80)
        logger.info("🔄 AI-OPERATOR SYNC CONFIRMATION SYSTEM")
        logger.info("=" * 80)
        logger.info("   PEAK Standard: Root cause fix for workflow drift")
        logger.info("   Ensures AI and operator are synchronized before execution")
        logger.info("=" * 80)

    def process_request(self, input_text: str, source: str = "text") -> ConfirmationRequest:
        """
        Process request through confirmation workflow

        Steps:
        1. Analyze intent
        2. Reformulate in AI Speak + Grammarly CLI
        3. Create confirmation request
        4. Present to operator
        5. Wait for confirmation
        """
        logger.info("=" * 80)
        logger.info("🔄 PROCESSING REQUEST - SYNC CONFIRMATION WORKFLOW")
        logger.info("=" * 80)
        logger.info(f"   Source: {source}")
        logger.info(f"   Input: {input_text[:100]}...")

        # Step 1: Analyze intent
        intent_analysis = self._analyze_intent(input_text, source)

        # Step 2: Reformulate in AI Speak + Grammarly CLI format
        reformulated = self._reformulate_request(input_text, intent_analysis)

        # Step 3: Create confirmation request
        request_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        confirmation = ConfirmationRequest(
            request_id=request_id,
            reformulated=reformulated,
            status=SyncStatus.PENDING_CONFIRMATION
        )

        # Step 4: Present to operator
        self._present_confirmation(confirmation)

        # PREDICTIVE ACTIONS: Suggest likely next actions based on this request
        try:
            from predictive_actions_framework import (
                get_predictive_actions_framework
            )

            framework = get_predictive_actions_framework()

            # Get context from intent analysis
            current_context = {
                "intent": intent_analysis.get("intent_summary", ""),
                "source": source,
                "system_state": "awaiting_confirmation"
            }

            # Get predictive suggestions
            suggestions = framework.suggest_actions(
                current_context, max_suggestions=2
            )

            if suggestions:
                logger.info("")
                logger.info(
                    "   🔮 PREDICTIVE ACTIONS - Likely next actions after this:"
                )
                for suggestion in suggestions:
                    pred = suggestion.predicted_action
                    logger.info(
                        f"      • {pred.action_type.value} -> {pred.target} "
                        f"({pred.confidence.value})"
                    )

        except ImportError:
            pass  # Predictive actions optional
        except Exception as e:
            logger.debug(f"Predictive actions suggestion error: {e}")

        # Store pending confirmation
        self.pending_confirmations[request_id] = confirmation
        self.current_sync_status = SyncStatus.PENDING_CONFIRMATION

        logger.info("=" * 80)
        logger.info("✅ CONFIRMATION REQUEST CREATED")
        logger.info("=" * 80)
        logger.info(f"   Request ID: {request_id}")
        logger.info("   Status: Waiting for operator confirmation")
        logger.info("=" * 80)

        return confirmation

    def _analyze_intent(self, input_text: str, source: str) -> Dict[str, Any]:
        """Analyze operator intent from input"""
        # ENHANCED: Use intent classifier if available
        if self.intent_classifier:
            try:
                intent = self.intent_classifier.classify_intent(input_text)
                return {
                    "intent_summary": f"Intent: {intent.intent_type.value} -> {intent.action or 'unknown action'}",
                    "clarity": "high" if intent.confidence > 0.7 else "medium" if intent.confidence > 0.5 else "low",
                    "confidence": intent.confidence,
                    "building_blocks": [],
                    "requires_clarification": intent.confidence < 0.5,
                    "intent_classifier_result": {
                        "intent_type": intent.intent_type.value,
                        "action": intent.action,
                        "entities": intent.entities
                    }
                }
            except Exception as e:
                logger.debug(f"Intent classifier error: {e}")

        # Fallback to existing intent preservation system
        try:
            # Use existing intent preservation system if available
            try:
                from intent_preservation_system import analyze_intent
                intent_result = analyze_intent(input_text, source=source)

                return {
                    "intent_summary": intent_result.intent_summary,
                    "clarity": intent_result.clarity.value if hasattr(intent_result, 'clarity') else "medium",
                    "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.5,
                    "building_blocks": intent_result.building_blocks if hasattr(intent_result, 'building_blocks') else [],
                    "requires_clarification": intent_result.requires_clarification if hasattr(intent_result, 'requires_clarification') else False
                }
            except ImportError:
                # Fallback: Basic intent analysis
                return self._basic_intent_analysis(input_text)
        except Exception as e:
            logger.warning(f"Intent analysis error: {e}")
            return self._basic_intent_analysis(input_text)

    def _basic_intent_analysis(self, input_text: str) -> Dict[str, Any]:
        """Basic intent analysis fallback"""
        # Simple keyword-based analysis
        text_lower = input_text.lower()

        intent_keywords = {
            "create": ["create", "make", "build", "add", "new"],
            "modify": ["change", "update", "modify", "edit", "fix"],
            "delete": ["delete", "remove", "destroy", "kill"],
            "query": ["what", "show", "list", "get", "find"],
            "execute": ["run", "execute", "start", "launch", "do"]
        }

        detected_intent = "unknown"
        for intent, keywords in intent_keywords.items():
            if any(kw in text_lower for kw in keywords):
                detected_intent = intent
                break

        return {
            "intent_summary": f"Operator wants to {detected_intent}",
            "clarity": "medium",
            "confidence": 0.6,
            "building_blocks": [],
            "requires_clarification": detected_intent == "unknown"
        }

    def _reformulate_request(self, input_text: str, intent_analysis: Dict[str, Any]) -> ReformulatedRequest:
        """Reformulate request in AI Speak + Grammarly CLI format"""
        try:
            # Step 1: Process through Grammarly CLI for clarity
            reformulated_text = self._process_through_grammarly(input_text)

            # Step 2: Format in "AI Speak" (structured, clear, actionable)
            ai_speak_format = self._format_ai_speak(reformulated_text, intent_analysis)

            return ReformulatedRequest(
                original_input=input_text,
                intent_summary=intent_analysis.get("intent_summary", "Unknown intent"),
                reformulated_text=ai_speak_format,
                clarity_score=self._calculate_clarity_score(intent_analysis),
                confidence_score=intent_analysis.get("confidence", 0.5),
                requires_confirmation=True
            )
        except Exception as e:
            logger.warning(f"Reformulation error: {e}")
            # Fallback: Use original with basic formatting
            return ReformulatedRequest(
                original_input=input_text,
                intent_summary=intent_analysis.get("intent_summary", "Unknown intent"),
                reformulated_text=input_text,  # Use original if reformulation fails
                clarity_score=0.5,
                confidence_score=0.5,
                requires_confirmation=True
            )

    def _process_through_grammarly(self, text: str) -> str:
        """Process text through Grammarly CLI for clarity and correctness"""
        try:
            from grammarly_ai_driven_cli import process_transcript

            logger.info("   🔍 Processing through Grammarly CLI...")
            corrected_text = process_transcript(text)

            if corrected_text and corrected_text != text:
                logger.info("   ✅ Grammarly corrections applied")
                return corrected_text
            else:
                logger.info("   ✅ No Grammarly corrections needed")
                return text
        except ImportError:
            logger.debug("   Grammarly CLI not available - using original text")
            return text
        except Exception as e:
            logger.debug(f"   Grammarly processing error: {e}")
            return text

    def _format_ai_speak(self, text: str, intent_analysis: Dict[str, Any]) -> str:
        """Format text in AI Speak (structured, clear, actionable)"""
        # AI Speak format: Clear, structured, actionable
        intent = intent_analysis.get("intent_summary", "Unknown intent")

        # Structure the reformulated request
        formatted = f"""## REFORMULATED REQUEST (AI Speak Format)

**Intent Analysis:**
{intent}

**Original Input:**
{text}

**Reformulated (AI Speak):**
{text}

**Clarity:** {intent_analysis.get('clarity', 'medium')}
**Confidence:** {intent_analysis.get('confidence', 0.5):.2%}

**Action Required:**
Please confirm if this accurately represents your intent.
"""
        return formatted

    def _calculate_clarity_score(self, intent_analysis: Dict[str, Any]) -> float:
        """Calculate clarity score from intent analysis"""
        clarity_map = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3
        }
        clarity = intent_analysis.get("clarity", "medium")
        return clarity_map.get(clarity, 0.5)

    def _present_confirmation(self, confirmation: ConfirmationRequest):
        """Present confirmation request to operator"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("❓ CONFIRMATION REQUIRED - AI-OPERATOR SYNC")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 REFORMULATED REQUEST (AI Speak + Grammarly CLI):")
        logger.info("")
        logger.info(confirmation.reformulated.reformulated_text)
        logger.info("")
        logger.info("=" * 80)
        logger.info("❓ IS THIS WHAT YOU MEANT?")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Please confirm:")
        logger.info("  ✅ YES - This is correct, proceed")
        logger.info("  ❌ NO - This is not what I meant, wait for clarification")
        logger.info("")
        logger.info(f"Request ID: {confirmation.request_id}")
        logger.info("=" * 80)
        logger.info("")
        logger.info("⏸️  WAITING FOR OPERATOR CONFIRMATION...")
        logger.info("   (Execution paused until confirmation received)")
        logger.info("")

    def confirm_request(self, request_id: str, operator_response: str = "yes") -> bool:
        """Operator confirms request - proceed with execution"""
        if request_id not in self.pending_confirmations:
            logger.warning(f"⚠️  Request ID not found: {request_id}")
            return False

        confirmation = self.pending_confirmations[request_id]

        if operator_response.lower() in ["yes", "y", "confirm", "proceed", "ok"]:
            confirmation.confirmed = True
            confirmation.operator_response = operator_response
            confirmation.status = SyncStatus.CONFIRMED
            self.current_sync_status = SyncStatus.CONFIRMED

            logger.info("=" * 80)
            logger.info("✅ OPERATOR CONFIRMED - PROCEEDING")
            logger.info("=" * 80)
            logger.info(f"   Request ID: {request_id}")
            logger.info("   Status: CONFIRMED - AI and operator are synced")
            logger.info("   Proceeding with execution...")
            logger.info("=" * 80)

            return True
        else:
            confirmation.confirmed = False
            confirmation.operator_response = operator_response
            confirmation.status = SyncStatus.UNSYNCED
            self.current_sync_status = SyncStatus.UNSYNCED

            logger.info("=" * 80)
            logger.info("❌ OPERATOR REJECTED - NOT PROCEEDING")
            logger.info("=" * 80)
            logger.info(f"   Request ID: {request_id}")
            logger.info("   Status: UNSYNCED - Waiting for clarification")
            logger.info("=" * 80)

            return False

    def is_synced(self) -> bool:
        """Check if AI and operator are currently synced"""
        return self.current_sync_status == SyncStatus.CONFIRMED

    def get_pending_confirmation(self) -> Optional[ConfirmationRequest]:
        """Get current pending confirmation"""
        for conf in self.pending_confirmations.values():
            if conf.status == SyncStatus.PENDING_CONFIRMATION:
                return conf
        return None


def get_sync_system() -> AIOperatorSyncConfirmationSystem:
    """Get singleton sync confirmation system"""
    global _sync_system
    if '_sync_system' not in globals():
        _sync_system = AIOperatorSyncConfirmationSystem()
    return _sync_system


# Global singleton
_sync_system = None
