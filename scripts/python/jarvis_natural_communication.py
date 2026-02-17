#!/usr/bin/env python3
"""
JARVIS Natural Communication

Context-aware responses, emotional intelligence.
Part of Phase 3 (Child → Adolescent).

Tags: #JARVIS #COMMUNICATION #PHASE3 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
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

logger = get_logger("JARVISNaturalCommunication")


class CommunicationStyle(Enum):
    """Communication styles"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    EMPATHETIC = "empathetic"


@dataclass
class CommunicationContext:
    """Context for communication"""
    operator_mood: Optional[str] = None
    urgency: str = "normal"  # low, normal, high, critical
    topic: Optional[str] = None
    previous_interactions: List[str] = field(default_factory=list)


class JARVISNaturalCommunication:
    """
    Natural communication system

    Capabilities:
    - Context-aware responses
    - Emotional intelligence
    - Adaptive communication style
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize natural communication"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_communication"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Integrate with context analyzer
        try:
            from jarvis_context_analyzer import get_jarvis_context_analyzer
            self.context_analyzer = get_jarvis_context_analyzer(self.project_root)
        except ImportError:
            self.context_analyzer = None

        logger.info("=" * 80)
        logger.info("💬 JARVIS NATURAL COMMUNICATION")
        logger.info("=" * 80)
        logger.info("   Context-aware responses, emotional intelligence")
        logger.info("")

    def generate_response(self, input_text: str, context: Optional[CommunicationContext] = None) -> str:
        """Generate natural, context-aware response"""
        context = context or CommunicationContext()

        # Analyze context
        style = self._select_communication_style(context)

        # Generate response
        response = self._generate_contextual_response(input_text, style, context)

        logger.debug(f"💬 Generated {style.value} response")
        return response

    def _select_communication_style(self, context: CommunicationContext) -> CommunicationStyle:
        """Select appropriate communication style"""
        if context.urgency == "critical":
            return CommunicationStyle.FORMAL
        elif context.operator_mood == "frustrated":
            return CommunicationStyle.EMPATHETIC
        elif context.topic and "technical" in context.topic.lower():
            return CommunicationStyle.TECHNICAL
        else:
            return CommunicationStyle.FRIENDLY

    def _generate_contextual_response(self, input_text: str, style: CommunicationStyle, context: CommunicationContext) -> str:
        """Generate contextual response"""
        # Simple template-based generation
        if style == CommunicationStyle.EMPATHETIC:
            return f"I understand. Let me help with: {input_text}"
        elif style == CommunicationStyle.TECHNICAL:
            return f"Technical analysis: {input_text}"
        else:
            return f"Response to: {input_text}"


# Singleton
_communication_instance: Optional[JARVISNaturalCommunication] = None

def get_jarvis_natural_communication(project_root: Optional[Path] = None) -> JARVISNaturalCommunication:
    global _communication_instance
    if _communication_instance is None:
        _communication_instance = JARVISNaturalCommunication(project_root)
    return _communication_instance
