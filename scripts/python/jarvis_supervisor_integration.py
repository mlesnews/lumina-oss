#!/usr/bin/env python3
"""
JARVIS Supervisor Integration
<COMPANY_NAME> LLC

Integrates JARVIS Communication Bridge with all systems.
Ensures all AI-IDE operator communication goes through JARVIS.

@JARVIS
"""

import sys
from pathlib import Path
from typing import Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_communication_bridge import (
        get_jarvis_bridge,
        CommunicationParty,
        MessageType
    )
    from universal_logging_wrapper import get_logger
    JARVIS_BRIDGE_AVAILABLE = True
except ImportError:
    JARVIS_BRIDGE_AVAILABLE = False
    get_logger = lambda name: __import__('logging').getLogger(name)

logger = get_logger("JARVISSupervisorIntegration")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class JARVISSupervisor:
    """
    JARVIS Supervisor

    Central entity that delegates and supervises all communication
    between AI and IDE operator.
    """

    def __init__(self):
        """Initialize JARVIS Supervisor"""
        self.bridge = None
        if JARVIS_BRIDGE_AVAILABLE:
            try:
                self.bridge = get_jarvis_bridge()
                logger.info("✅ JARVIS Supervisor initialized")
                logger.info("   All communication supervised by JARVIS")
            except Exception as e:
                logger.error(f"Failed to initialize JARVIS bridge: {e}")

    def establish_communication(self) -> bool:
        """Establish communication between AI and IDE operator"""
        if not self.bridge:
            logger.warning("JARVIS bridge not available")
            return False

        # Send hello from IDE operator to AI
        signal_id = self.bridge.send_hello(
            CommunicationParty.IDE_OPERATOR,
            CommunicationParty.AI,
            capabilities=["directives", "status", "execution", "measurement"],
            context={"supervisor": "JARVIS"}
        )

        # Acknowledge hello
        success = self.bridge.acknowledge_hello(
            signal_id,
            "Hello acknowledged - JARVIS supervising communication"
        )

        if success:
            logger.info("✅ Communication established - JARVIS supervising")

        return success

    def receive_directive(self, directive: str, priority: str = "normal") -> str:
        """
        Receive directive from IDE operator

        JARVIS supervises and delegates to appropriate AI agent
        """
        if not self.bridge:
            logger.warning("JARVIS bridge not available")
            return None

        # Send directive through bridge
        directive_id = self.bridge.send_directive(
            directive,
            from_party=CommunicationParty.IDE_OPERATOR,
            to_party=CommunicationParty.AI,
            priority=priority
        )

        # JARVIS confirms understanding
        confirmation = f"JARVIS: Understood directive - '{directive}'. Delegating to appropriate agent."
        self.bridge.confirm_directive(
            directive_id,
            confirmation,
            delegated_to="JARVIS"
        )

        logger.info(f"📢 JARVIS received directive: {directive}")
        logger.info(f"   Directive ID: {directive_id}")
        logger.info(f"   Status: Confirmed and delegated")

        return directive_id

    def send_status(self, status_message: str, data: Optional[dict] = None) -> str:
        """Send status update from AI to IDE operator"""
        if not self.bridge:
            logger.warning("JARVIS bridge not available")
            return None

        message_id = self.bridge.send_message(
            MessageType.STATUS,
            status_message,
            from_party=CommunicationParty.AI,
            to_party=CommunicationParty.IDE_OPERATOR,
            data=data or {}
        )

        return message_id

    def send_response(self, response: str, data: Optional[dict] = None) -> str:
        """Send response from AI to IDE operator"""
        if not self.bridge:
            logger.warning("JARVIS bridge not available")
            return None

        message_id = self.bridge.send_message(
            MessageType.RESPONSE,
            response,
            from_party=CommunicationParty.AI,
            to_party=CommunicationParty.IDE_OPERATOR,
            data=data or {}
        )

        return message_id


# Singleton instance
_jarvis_supervisor_instance: Optional[JARVISSupervisor] = None


def get_jarvis_supervisor() -> JARVISSupervisor:
    """Get singleton JARVIS supervisor instance"""
    global _jarvis_supervisor_instance
    if _jarvis_supervisor_instance is None:
        _jarvis_supervisor_instance = JARVISSupervisor()
    return _jarvis_supervisor_instance


# Auto-establish communication on import
if JARVIS_BRIDGE_AVAILABLE:
    try:
        supervisor = get_jarvis_supervisor()
        supervisor.establish_communication()
    except Exception:
        pass

