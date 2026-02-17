#!/usr/bin/env python3
"""
JARVIS Communication Bridge
<COMPANY_NAME> LLC

Solves the communication disconnect between AI and IDE operator.
JARVIS acts as the central supervisor and translator.

Problem: AI and IDE operator speak different "languages"
Solution: JARVIS translates and supervises all communication

@JARVIS @MARVIN @TONY @MACE @GANDALF
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from measurement_gatekeeper import get_measurement_gatekeeper, MeasurementLevel
    GATEKEEPER_AVAILABLE = True
except ImportError:
    GATEKEEPER_AVAILABLE = False

logger = get_logger("JARVISCommunicationBridge")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CommunicationParty(Enum):
    """Communication parties"""
    AI = "ai"  # AI agent/system
    IDE_OPERATOR = "ide_operator"  # Human IDE operator
    JARVIS = "jarvis"  # JARVIS supervisor


class MessageType(Enum):
    """Message types"""
    HELLO = "hello"  # Handshake/acknowledgment
    DIRECTIVE = "directive"  # Clear instruction from operator
    DIRECTION = "direction"  # Guidance/context
    RESPONSE = "response"  # Response to directive
    STATUS = "status"  # Status update
    CONFIRMATION = "confirmation"  # Acknowledgment of understanding
    ERROR = "error"  # Error/issue
    QUESTION = "question"  # Question/clarification


class CommunicationState(Enum):
    """Communication state"""
    IDLE = "idle"  # No active communication
    HELLO_SENT = "hello_sent"  # Hello signal sent, waiting for acknowledgment
    HELLO_RECEIVED = "hello_received"  # Hello received, communication established
    DIRECTIVE_PENDING = "directive_pending"  # Directive received, processing
    DIRECTIVE_CONFIRMED = "directive_confirmed"  # Directive understood and confirmed
    EXECUTING = "executing"  # Executing directive
    COMPLETED = "completed"  # Directive completed
    ERROR = "error"  # Communication error


@dataclass
class HelloSignal:
    """Hello signal for handshake"""
    signal_id: str
    timestamp: datetime
    from_party: CommunicationParty
    to_party: CommunicationParty
    message: str = "Hello - Communication established"
    capabilities: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledgment_timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['from_party'] = self.from_party.value
        data['to_party'] = self.to_party.value
        if self.acknowledgment_timestamp:
            data['acknowledgment_timestamp'] = self.acknowledgment_timestamp.isoformat()
        return data


@dataclass
class Directive:
    """Clear directive from IDE operator"""
    directive_id: str
    timestamp: datetime
    from_party: CommunicationParty
    to_party: CommunicationParty

    # Directive content
    directive: str  # Clear, loud directive
    priority: str = "normal"  # low, normal, high, urgent
    context: Dict[str, Any] = field(default_factory=dict)

    # Understanding
    understood: bool = False
    confirmation: Optional[str] = None

    # Execution
    delegated_to: Optional[str] = None  # Which AI agent
    execution_state: CommunicationState = CommunicationState.IDLE
    execution_result: Optional[Any] = None
    execution_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['from_party'] = self.from_party.value
        data['to_party'] = self.to_party.value
        data['execution_state'] = self.execution_state.value
        return data


@dataclass
class CommunicationMessage:
    """Communication message"""
    message_id: str
    timestamp: datetime
    message_type: MessageType
    from_party: CommunicationParty
    to_party: CommunicationParty

    # Message content
    content: str
    data: Dict[str, Any] = field(default_factory=dict)

    # Translation
    original_language: str = "native"  # Language of origin
    translated: bool = False
    translation: Optional[str] = None

    # Understanding
    understood: bool = False
    requires_confirmation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['message_type'] = self.message_type.value
        data['from_party'] = self.from_party.value
        data['to_party'] = self.to_party.value
        return data


class JARVISCommunicationBridge:
    """
    JARVIS Communication Bridge

    Solves communication disconnect between AI and IDE operator.
    JARVIS supervises and translates all communication.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Communication Bridge"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISCommunicationBridge")

        # Data directories
        self.data_dir = self.project_root / "data" / "jarvis_communication"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Communication state
        self.communication_state: Dict[str, CommunicationState] = {}
        self.hello_signals: Dict[str, HelloSignal] = {}
        self.directives: Dict[str, Directive] = {}
        self.messages: List[CommunicationMessage] = []

        # Translation dictionaries
        self.ai_to_human_translations: Dict[str, str] = {}
        self.human_to_ai_translations: Dict[str, str] = {}
        self._load_translation_dictionaries()

        # Handshake status
        self.handshake_established: Dict[str, bool] = {}

        # Measurement integration
        self.gatekeeper = None
        if GATEKEEPER_AVAILABLE:
            try:
                self.gatekeeper = get_measurement_gatekeeper()
            except Exception:
                pass

        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.HELLO: self._handle_hello,
            MessageType.DIRECTIVE: self._handle_directive,
            MessageType.DIRECTION: self._handle_direction,
            MessageType.RESPONSE: self._handle_response,
            MessageType.CONFIRMATION: self._handle_confirmation
        }

        self.logger.info("✅ JARVIS Communication Bridge initialized")
        self.logger.info("   Solving AI ↔ IDE Operator communication disconnect")
        self.logger.info("   JARVIS: Central supervisor and translator")

    def _load_translation_dictionaries(self) -> None:
        """Load translation dictionaries"""
        # AI to Human translations
        self.ai_to_human_translations = {
            "processing": "Working on it",
            "completed": "Done",
            "error": "Something went wrong",
            "success": "Successfully completed",
            "pending": "Waiting",
            "executing": "Currently running",
            "measurement": "Tracking progress",
            "state": "Current status"
        }

        # Human to AI translations
        self.human_to_ai_translations = {
            "do this": "execute_operation",
            "fix that": "resolve_issue",
            "check status": "get_status",
            "what's happening": "get_current_state",
            "make it work": "ensure_operational",
            "show me": "display_information"
        }

    def send_hello(self, from_party: CommunicationParty, 
                   to_party: CommunicationParty,
                   capabilities: Optional[List[str]] = None,
                   context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send hello signal (handshake)

        This is the "hello" signal - loud and clear
        """
        signal_id = f"hello_{from_party.value}_{to_party.value}_{int(time.time() * 1000)}"

        hello = HelloSignal(
            signal_id=signal_id,
            timestamp=datetime.now(),
            from_party=from_party,
            to_party=to_party,
            capabilities=capabilities or [],
            context=context or {}
        )

        self.hello_signals[signal_id] = hello

        # Log hello
        self.logger.info(f"👋 HELLO: {from_party.value} → {to_party.value}")
        self.logger.info(f"   Signal ID: {signal_id}")
        self.logger.info(f"   Message: {hello.message}")

        # Measure communication
        if self.gatekeeper:
            try:
                self.gatekeeper.measure(
                    operation="send_hello",
                    component="JARVISCommunicationBridge",
                    level=MeasurementLevel.HIGH,
                    context={'from': from_party.value, 'to': to_party.value}
                )
            except Exception:
                pass

        # Save hello signal
        self._save_hello_signal(hello)

        return signal_id

    def acknowledge_hello(self, signal_id: str, 
                         acknowledgment_message: Optional[str] = None) -> bool:
        """Acknowledge hello signal"""
        if signal_id not in self.hello_signals:
            self.logger.warning(f"Hello signal not found: {signal_id}")
            return False

        hello = self.hello_signals[signal_id]
        hello.acknowledged = True
        hello.acknowledgment_timestamp = datetime.now()

        if acknowledgment_message:
            hello.message = acknowledgment_message

        # Establish handshake
        handshake_key = f"{hello.from_party.value}_{hello.to_party.value}"
        self.handshake_established[handshake_key] = True

        # Log acknowledgment
        self.logger.info(f"✅ ACKNOWLEDGED: {hello.to_party.value} → {hello.from_party.value}")
        self.logger.info(f"   Signal ID: {signal_id}")
        self.logger.info(f"   Communication established")

        # Update communication state
        self.communication_state[handshake_key] = CommunicationState.HELLO_RECEIVED

        # Save acknowledgment
        self._save_hello_signal(hello)

        return True

    def send_directive(self, directive: str,
                     from_party: CommunicationParty = CommunicationParty.IDE_OPERATOR,
                     to_party: CommunicationParty = CommunicationParty.AI,
                     priority: str = "normal",
                     context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send clear directive from IDE operator to AI

        This is the "loud and clear directive" system
        """
        # Check handshake
        handshake_key = f"{from_party.value}_{to_party.value}"
        if not self.handshake_established.get(handshake_key, False):
            self.logger.warning(f"⚠️  No handshake established - sending hello first")
            self.send_hello(from_party, to_party)
            time.sleep(0.1)  # Brief pause
            self.acknowledge_hello(list(self.hello_signals.keys())[-1])

        directive_id = f"directive_{int(time.time() * 1000)}"

        # Translate directive if needed
        translated_directive = self._translate_to_ai(directive)

        directive_obj = Directive(
            directive_id=directive_id,
            timestamp=datetime.now(),
            from_party=from_party,
            to_party=to_party,
            directive=directive,
            priority=priority,
            context=context or {}
        )

        self.directives[directive_id] = directive_obj

        # Log directive
        self.logger.info(f"📢 DIRECTIVE: {from_party.value} → {to_party.value}")
        self.logger.info(f"   ID: {directive_id}")
        self.logger.info(f"   Priority: {priority}")
        self.logger.info(f"   Directive: {directive}")
        if translated_directive != directive:
            self.logger.info(f"   Translated: {translated_directive}")

        # Measure communication
        if self.gatekeeper:
            try:
                self.gatekeeper.measure(
                    operation="send_directive",
                    component="JARVISCommunicationBridge",
                    level=MeasurementLevel.HIGH,
                    context={'directive': directive, 'priority': priority}
                )
            except Exception:
                pass

        # Update state
        self.communication_state[directive_id] = CommunicationState.DIRECTIVE_PENDING

        # Save directive
        self._save_directive(directive_obj)

        return directive_id

    def confirm_directive(self, directive_id: str, 
                         confirmation_message: str,
                         delegated_to: Optional[str] = None) -> bool:
        """Confirm understanding of directive"""
        if directive_id not in self.directives:
            self.logger.warning(f"Directive not found: {directive_id}")
            return False

        directive = self.directives[directive_id]
        directive.understood = True
        directive.confirmation = confirmation_message
        directive.delegated_to = delegated_to
        directive.execution_state = CommunicationState.DIRECTIVE_CONFIRMED

        # Log confirmation
        self.logger.info(f"✅ CONFIRMED: Directive {directive_id}")
        self.logger.info(f"   Confirmation: {confirmation_message}")
        if delegated_to:
            self.logger.info(f"   Delegated to: {delegated_to}")

        # Update state
        self.communication_state[directive_id] = CommunicationState.DIRECTIVE_CONFIRMED

        # Save directive
        self._save_directive(directive)

        return True

    def complete_directive(self, directive_id: str,
                          result: Any = None,
                          error: Optional[str] = None) -> bool:
        """Complete directive execution"""
        if directive_id not in self.directives:
            self.logger.warning(f"Directive not found: {directive_id}")
            return False

        directive = self.directives[directive_id]

        if error:
            directive.execution_state = CommunicationState.ERROR
            directive.execution_error = error
            self.logger.error(f"❌ ERROR: Directive {directive_id} - {error}")
        else:
            directive.execution_state = CommunicationState.COMPLETED
            directive.execution_result = result
            self.logger.info(f"✅ COMPLETED: Directive {directive_id}")

        # Update state
        self.communication_state[directive_id] = directive.execution_state

        # Save directive
        self._save_directive(directive)

        return True

    def send_message(self, message_type: MessageType,
                    content: str,
                    from_party: CommunicationParty,
                    to_party: CommunicationParty,
                    data: Optional[Dict[str, Any]] = None) -> str:
        """Send communication message"""
        message_id = f"msg_{message_type.value}_{int(time.time() * 1000)}"

        # Translate message if needed
        if from_party == CommunicationParty.AI and to_party == CommunicationParty.IDE_OPERATOR:
            translated_content = self._translate_to_human(content)
        elif from_party == CommunicationParty.IDE_OPERATOR and to_party == CommunicationParty.AI:
            translated_content = self._translate_to_ai(content)
        else:
            translated_content = content

        message = CommunicationMessage(
            message_id=message_id,
            timestamp=datetime.now(),
            message_type=message_type,
            from_party=from_party,
            to_party=to_party,
            content=content,
            data=data or {},
            translation=translated_content if translated_content != content else None,
            translated=translated_content != content
        )

        self.messages.append(message)

        # Keep only last 10000 messages
        if len(self.messages) > 10000:
            self.messages = self.messages[-10000:]

        # Handle message
        if message_type in self.message_handlers:
            try:
                self.message_handlers[message_type](message)
            except Exception as e:
                self.logger.error(f"Message handler error: {e}")

        # Log message
        self.logger.debug(f"📨 MESSAGE: {from_party.value} → {to_party.value}")
        self.logger.debug(f"   Type: {message_type.value}")
        self.logger.debug(f"   Content: {content}")
        if translated_content != content:
            self.logger.debug(f"   Translated: {translated_content}")

        # Save message
        self._save_message(message)

        return message_id

    def _translate_to_human(self, ai_message: str) -> str:
        """Translate AI message to human language"""
        translated = ai_message
        for ai_term, human_term in self.ai_to_human_translations.items():
            translated = translated.replace(ai_term, human_term)
        return translated

    def _translate_to_ai(self, human_message: str) -> str:
        """Translate human message to AI language"""
        translated = human_message.lower()
        for human_term, ai_term in self.human_to_ai_translations.items():
            if human_term in translated:
                translated = translated.replace(human_term, ai_term)
        return translated

    def _handle_hello(self, message: CommunicationMessage) -> None:
        """Handle hello message"""
        # Auto-acknowledge hello from AI to operator
        if message.from_party == CommunicationParty.AI:
            # Find corresponding hello signal
            for signal_id, hello in self.hello_signals.items():
                if not hello.acknowledged:
                    self.acknowledge_hello(signal_id, "Hello acknowledged - Ready to communicate")
                    break

    def _handle_directive(self, message: CommunicationMessage) -> None:
        """Handle directive message"""
        # This is handled by send_directive
        pass

    def _handle_direction(self, message: CommunicationMessage) -> None:
        """Handle direction/guidance message"""
        self.logger.info(f"🧭 DIRECTION: {message.content}")

    def _handle_response(self, message: CommunicationMessage) -> None:
        """Handle response message"""
        self.logger.info(f"💬 RESPONSE: {message.content}")

    def _handle_confirmation(self, message: CommunicationMessage) -> None:
        """Handle confirmation message"""
        message.understood = True
        self.logger.info(f"✅ CONFIRMED: {message.content}")

    def _save_hello_signal(self, hello: HelloSignal) -> None:
        """Save hello signal"""
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            hello_file = self.data_dir / f"hello_signals_{date_str}.jsonl"
            with open(hello_file, 'a', encoding='utf-8') as f:
                json.dump(hello.to_dict(), f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to save hello signal: {e}")

    def _save_directive(self, directive: Directive) -> None:
        """Save directive"""
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            directive_file = self.data_dir / f"directives_{date_str}.jsonl"
            with open(directive_file, 'a', encoding='utf-8') as f:
                json.dump(directive.to_dict(), f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to save directive: {e}")

    def _save_message(self, message: CommunicationMessage) -> None:
        """Save message"""
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            message_file = self.data_dir / f"messages_{date_str}.jsonl"
            with open(message_file, 'a', encoding='utf-8') as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to save message: {e}")

    def get_communication_status(self) -> Dict[str, Any]:
        """Get communication status"""
        return {
            'handshakes_established': len(self.handshake_established),
            'active_directives': sum(1 for d in self.directives.values() 
                                   if d.execution_state in [CommunicationState.DIRECTIVE_PENDING, 
                                                           CommunicationState.DIRECTIVE_CONFIRMED,
                                                           CommunicationState.EXECUTING]),
            'completed_directives': sum(1 for d in self.directives.values() 
                                      if d.execution_state == CommunicationState.COMPLETED),
            'total_messages': len(self.messages),
            'communication_state': {k: v.value for k, v in self.communication_state.items()}
        }


# Singleton instance
_bridge_instance: Optional[JARVISCommunicationBridge] = None


def get_jarvis_bridge() -> JARVISCommunicationBridge:
    """Get singleton JARVIS bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = JARVISCommunicationBridge()
    return _bridge_instance


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Communication Bridge")
    parser.add_argument("--hello", action="store_true", help="Send hello signal")
    parser.add_argument("--directive", type=str, help="Send directive")
    parser.add_argument("--status", action="store_true", help="Get communication status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    bridge = get_jarvis_bridge()

    if args.hello:
        signal_id = bridge.send_hello(
            CommunicationParty.IDE_OPERATOR,
            CommunicationParty.AI,
            capabilities=["directives", "status", "execution"]
        )
        bridge.acknowledge_hello(signal_id, "Hello acknowledged - Ready")
        print(f"✅ Hello signal sent and acknowledged: {signal_id}")

    elif args.directive:
        directive_id = bridge.send_directive(
            args.directive,
            from_party=CommunicationParty.IDE_OPERATOR,
            to_party=CommunicationParty.AI,
            priority="normal"
        )
        bridge.confirm_directive(directive_id, f"Understood: {args.directive}")
        print(f"✅ Directive sent and confirmed: {directive_id}")

    elif args.status:
        status = bridge.get_communication_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n📡 JARVIS Communication Bridge Status")
            print("=" * 60)
            print(f"Handshakes: {status['handshakes_established']}")
            print(f"Active Directives: {status['active_directives']}")
            print(f"Completed Directives: {status['completed_directives']}")
            print(f"Total Messages: {status['total_messages']}")

    else:
        parser.print_help()
        print("\n📡 JARVIS Communication Bridge")
        print("   Solving AI ↔ IDE Operator communication disconnect")

