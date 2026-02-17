#!/usr/bin/env python3
"""
Intent Preservation System - Immediate Feedback Loop

The center puzzle piece - preserves user intent BEFORE it's lost.
Provides immediate feedback to confirm understanding.

When ANY request comes in (AI, human, alien, whatever), the system:
1. Immediately captures and analyzes intent
2. Provides feedback to confirm understanding
3. Breaks down to basic building blocks
4. Preserves intent throughout the workflow

Tags: #INTENT_PRESERVATION #FEEDBACK_LOOP #BASIC_BUILDING_BLOCKS #LUMINA_CORE
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

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

logger = get_logger("IntentPreservation")


class IntentClarity(Enum):
    """Intent clarity level"""
    CRYSTAL_CLEAR = "crystal_clear"  # No ambiguity
    CLEAR = "clear"  # Mostly clear, minor clarification needed
    UNCLEAR = "unclear"  # Needs clarification
    VERY_UNCLEAR = "very_unclear"  # Major clarification needed


@dataclass
class IntentBlock:
    """A basic building block of intent"""
    action: str  # What to do
    target: str  # What to act on
    context: Dict[str, Any]  # Additional context
    priority: int = 0  # Priority level
    dependencies: List[str] = field(default_factory=list)  # Other blocks this depends on


@dataclass
class IntentAnalysis:
    """Analysis of user intent"""
    original_request: str
    intent_summary: str
    clarity: IntentClarity
    building_blocks: List[IntentBlock]
    confidence: float
    feedback_message: str
    requires_clarification: bool
    suggested_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class IntentPreservationSystem:
    """
    Intent Preservation System - The Center Puzzle Piece

    Preserves user intent BEFORE it's lost by:
    1. Immediate capture and analysis
    2. Immediate feedback to confirm understanding
    3. Breaking down to basic building blocks
    4. Maintaining intent throughout workflow
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize intent preservation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.intent_history: List[IntentAnalysis] = []

    def analyze_intent(
        self,
        request: str,
        source: str = "unknown",  # "human", "ai", "voice", "jarvis", etc.
        context: Optional[Dict[str, Any]] = None
    ) -> IntentAnalysis:
        """
        Analyze intent and provide immediate feedback

        This is the CENTER PUZZLE PIECE - captures intent before it's lost.

        Args:
            request: The request text
            source: Source of request (human, ai, voice, etc.)
            context: Additional context

        Returns:
            IntentAnalysis with immediate feedback
        """
        if not request or len(request.strip()) == 0:
            return IntentAnalysis(
                original_request=request,
                intent_summary="Empty request",
                clarity=IntentClarity.VERY_UNCLEAR,
                building_blocks=[],
                confidence=0.0,
                feedback_message="⚠️ Empty request - please provide more details",
                requires_clarification=True,
                suggested_actions=[]
            )

        # Analyze intent (break down to basic building blocks)
        building_blocks = self._break_down_to_blocks(request, context)

        # Determine clarity
        clarity = self._assess_clarity(request, building_blocks)

        # Generate intent summary
        intent_summary = self._generate_intent_summary(request, building_blocks)

        # Calculate confidence
        confidence = self._calculate_confidence(clarity, building_blocks)

        # Generate immediate feedback
        feedback_message = self._generate_feedback(
            intent_summary, clarity, building_blocks, confidence
        )

        # Determine if clarification needed
        requires_clarification = (
            clarity in [IntentClarity.UNCLEAR, IntentClarity.VERY_UNCLEAR] or
            confidence < 0.7
        )

        # Suggest actions
        suggested_actions = self._suggest_actions(building_blocks, clarity)

        analysis = IntentAnalysis(
            original_request=request,
            intent_summary=intent_summary,
            clarity=clarity,
            building_blocks=building_blocks,
            confidence=confidence,
            feedback_message=feedback_message,
            requires_clarification=requires_clarification,
            suggested_actions=suggested_actions
        )

        # Store in history
        self.intent_history.append(analysis)

        # Keep only last 100 analyses
        if len(self.intent_history) > 100:
            self.intent_history.pop(0)

        logger.info(f"   🎯 Intent analyzed: {intent_summary[:50]}...")
        logger.info(f"      Clarity: {clarity.value}, Confidence: {confidence:.2f}")
        logger.info(f"      Building blocks: {len(building_blocks)}")

        return analysis

    def _break_down_to_blocks(
        self,
        request: str,
        context: Optional[Dict[str, Any]]
    ) -> List[IntentBlock]:
        """
        Break down request to basic building blocks

        This is the core - breaking complex requests into simple, actionable blocks.
        """
        blocks: List[IntentBlock] = []

        # Simple keyword-based breakdown (can be enhanced with LLM)
        request_lower = request.lower()

        # Detect actions
        actions = []
        if any(word in request_lower for word in ["create", "make", "build", "add"]):
            actions.append("create")
        if any(word in request_lower for word in ["fix", "repair", "correct", "update"]):
            actions.append("fix")
        if any(word in request_lower for word in ["delete", "remove", "destroy"]):
            actions.append("delete")
        if any(word in request_lower for word in ["check", "verify", "validate"]):
            actions.append("check")
        if any(word in request_lower for word in ["run", "execute", "start"]):
            actions.append("run")
        if any(word in request_lower for word in ["grammarly", "grammar", "spell"]):
            actions.append("grammar_check")

        # If no actions detected, default to "process"
        if not actions:
            actions = ["process"]

        # Detect targets (what to act on)
        targets = []
        if "grammarly" in request_lower or "grammar" in request_lower:
            targets.append("grammarly")
        if "file" in request_lower:
            targets.append("file")
        if "code" in request_lower or "script" in request_lower:
            targets.append("code")
        if "text" in request_lower or "transcript" in request_lower:
            targets.append("text")

        # If no targets detected, use "request" as default
        if not targets:
            targets = ["request"]

        # Create building blocks
        for action in actions:
            for target in targets:
                block = IntentBlock(
                    action=action,
                    target=target,
                    context=context or {},
                    priority=1 if action in ["create", "fix"] else 0
                )
                blocks.append(block)

        # If still no blocks, create a default "understand" block
        if not blocks:
            blocks.append(IntentBlock(
                action="understand",
                target="request",
                context=context or {},
                priority=0
            ))

        return blocks

    def _assess_clarity(
        self,
        request: str,
        blocks: List[IntentBlock]
    ) -> IntentClarity:
        """Assess how clear the intent is"""
        # Simple heuristics (can be enhanced with LLM)

        # Very unclear: too short or too vague
        if len(request.strip()) < 10:
            return IntentClarity.VERY_UNCLEAR

        # Unclear: no clear action or target
        if len(blocks) == 0 or (len(blocks) == 1 and blocks[0].action == "understand"):
            return IntentClarity.UNCLEAR

        # Clear: has action and target
        if len(blocks) >= 1 and blocks[0].action != "understand":
            # Check if multiple actions might indicate confusion
            unique_actions = set(b.action for b in blocks)
            if len(unique_actions) > 3:
                return IntentClarity.UNCLEAR
            return IntentClarity.CLEAR

        # Crystal clear: specific, actionable, single purpose
        if len(blocks) == 1 and blocks[0].action != "understand":
            return IntentClarity.CRYSTAL_CLEAR

        return IntentClarity.CLEAR

    def _generate_intent_summary(
        self,
        request: str,
        blocks: List[IntentBlock]
    ) -> str:
        """Generate a summary of the intent"""
        if not blocks:
            return f"Understand: {request[:50]}"

        actions = [b.action for b in blocks]
        targets = [b.target for b in blocks]

        action_str = ", ".join(set(actions))
        target_str = ", ".join(set(targets))

        return f"{action_str.title()} {target_str}"

    def _calculate_confidence(
        self,
        clarity: IntentClarity,
        blocks: List[IntentBlock]
    ) -> float:
        """Calculate confidence in understanding"""
        clarity_scores = {
            IntentClarity.CRYSTAL_CLEAR: 0.95,
            IntentClarity.CLEAR: 0.80,
            IntentClarity.UNCLEAR: 0.50,
            IntentClarity.VERY_UNCLEAR: 0.20
        }

        base_confidence = clarity_scores.get(clarity, 0.50)

        # Adjust based on number of blocks (more blocks = potentially less clear)
        if len(blocks) > 5:
            base_confidence *= 0.9
        elif len(blocks) == 0:
            base_confidence *= 0.5

        return min(1.0, max(0.0, base_confidence))

    def _generate_feedback(
        self,
        intent_summary: str,
        clarity: IntentClarity,
        blocks: List[IntentBlock],
        confidence: float
    ) -> str:
        """Generate immediate feedback message"""
        if clarity == IntentClarity.CRYSTAL_CLEAR:
            return f"✅ I understand: {intent_summary}. Proceeding with {len(blocks)} action(s)."

        elif clarity == IntentClarity.CLEAR:
            return f"✅ I understand: {intent_summary}. I'll proceed, but let me know if I need to adjust."

        elif clarity == IntentClarity.UNCLEAR:
            return f"⚠️ I think you want: {intent_summary}, but I'm not 100% sure. Can you clarify?"

        else:  # VERY_UNCLEAR
            return f"❓ I'm not sure what you need. Could you provide more details? I see: {intent_summary}"

    def _suggest_actions(
        self,
        blocks: List[IntentBlock],
        clarity: IntentClarity
    ) -> List[str]:
        """Suggest actions based on building blocks"""
        suggestions = []

        for block in blocks:
            if block.action == "grammar_check":
                suggestions.append("Run Grammarly CLI to check grammar")
            elif block.action == "create":
                suggestions.append(f"Create {block.target}")
            elif block.action == "fix":
                suggestions.append(f"Fix {block.target}")
            elif block.action == "check":
                suggestions.append(f"Check {block.target}")

        return suggestions

    def get_immediate_feedback(self, request: str) -> str:
        """
        Get immediate feedback for a request

        This is the key function - provides instant feedback to preserve intent.
        """
        analysis = self.analyze_intent(request)
        return analysis.feedback_message

    def confirm_intent(self, request: str) -> bool:
        """
        Confirm if intent is clear enough to proceed

        Returns True if intent is clear, False if clarification needed.
        """
        analysis = self.analyze_intent(request)
        return not analysis.requires_clarification


# Global instance
_intent_system_instance = None


def get_intent_preservation_system() -> IntentPreservationSystem:
    """Get or create global intent preservation system"""
    global _intent_system_instance
    if _intent_system_instance is None:
        _intent_system_instance = IntentPreservationSystem()
        logger.info("✅ Intent Preservation System initialized - CENTER PUZZLE PIECE ACTIVE")
    return _intent_system_instance


def analyze_intent(request: str, source: str = "unknown") -> IntentAnalysis:
    """Analyze intent and get immediate feedback"""
    system = get_intent_preservation_system()
    return system.analyze_intent(request, source)


def get_immediate_feedback(request: str) -> str:
    """Get immediate feedback for a request"""
    system = get_intent_preservation_system()
    return system.get_immediate_feedback(request)


if __name__ == "__main__":
    # Test
    system = get_intent_preservation_system()

    test_requests = [
        "Fix the grammar in my text",
        "Create a file",
        "What?",
        "Use Grammarly CLI to check and auto-accept all corrections"
    ]

    for request in test_requests:
        print(f"\n📝 Request: {request}")
        analysis = system.analyze_intent(request)
        print(f"   {analysis.feedback_message}")
        print(f"   Blocks: {len(analysis.building_blocks)}")
        print(f"   Confidence: {analysis.confidence:.2f}")
