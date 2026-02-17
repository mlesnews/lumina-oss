#!/usr/bin/env python3
"""
JARVIS Master Command Interface

The single entry point for all JARVIS interactions. Integrates all JARVIS
capabilities into one unified command interface.

MCU JARVIS Capability: Unified command and control interface

@JARVIS @MASTER_COMMAND @MCU_FEATURE
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMasterCommand")

# Import JARVIS modules
try:
    from jarvis_unified_interface import JARVISUnifiedInterface
    UNIFIED_INTERFACE_AVAILABLE = True
except ImportError:
    UNIFIED_INTERFACE_AVAILABLE = False
    logger.warning("JARVIS Unified Interface not available")

try:
    from jarvis_core_intelligence import JARVISCoreIntelligence
    CORE_INTELLIGENCE_AVAILABLE = True
except ImportError:
    CORE_INTELLIGENCE_AVAILABLE = False
    logger.warning("JARVIS Core Intelligence not available")

try:
    from jarvis_realtime_diagnostics import JARVISRealtimeDiagnostics
    REALTIME_DIAGNOSTICS_AVAILABLE = True
except ImportError:
    REALTIME_DIAGNOSTICS_AVAILABLE = False
    logger.warning("JARVIS Real-Time Diagnostics not available")

try:
    from jarvis_azure_voice_interface import JARVISAzureVoiceInterface
    VOICE_INTERFACE_AVAILABLE = True
except ImportError:
    VOICE_INTERFACE_AVAILABLE = False
    logger.warning("JARVIS Voice Interface not available")


class JARVISMasterCommand:
    """
    JARVIS Master Command Interface

    Single entry point for all JARVIS interactions. Integrates all capabilities.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Master Command"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISMasterCommand")

        # Initialize core components
        self.unified_interface = None
        self.core_intelligence = None
        self.realtime_diagnostics = None
        self.voice_interface = None
        self.natural_conversation = None

        self._initialize_components()

        self.logger.info("🎯 JARVIS Master Command initialized")
        self.logger.info("   Ready for commands")

    def _initialize_components(self):
        """Initialize all JARVIS components"""
        # Unified Interface
        if UNIFIED_INTERFACE_AVAILABLE:
            try:
                self.unified_interface = JARVISUnifiedInterface(self.project_root)
                self.logger.info("   ✅ Unified Interface loaded")
            except Exception as e:
                self.logger.error(f"   ❌ Failed to load Unified Interface: {e}")

        # Core Intelligence
        if CORE_INTELLIGENCE_AVAILABLE:
            try:
                self.core_intelligence = JARVISCoreIntelligence(self.project_root)
                self.logger.info("   ✅ Core Intelligence loaded")
            except Exception as e:
                self.logger.error(f"   ❌ Failed to load Core Intelligence: {e}")

        # Real-Time Diagnostics
        if REALTIME_DIAGNOSTICS_AVAILABLE:
            try:
                self.realtime_diagnostics = JARVISRealtimeDiagnostics(self.project_root)
                # Auto-start monitoring
                self.realtime_diagnostics.start_monitoring()
                self.logger.info("   ✅ Real-Time Diagnostics loaded (monitoring active)")
            except Exception as e:
                self.logger.error(f"   ❌ Failed to load Real-Time Diagnostics: {e}")

        # Voice Interface (available for activation)
        if VOICE_INTERFACE_AVAILABLE:
            self.logger.info("   ℹ️  Voice Interface available (activate with jarvis_voice_activation.py)")
        else:
            self.logger.warning("   ⚠️  Voice Interface not available (Azure Speech SDK required)")

        # Natural Conversation System
        try:
            from jarvis_natural_conversation import JARVISNaturalConversation, ConversationStyle
            self.natural_conversation = JARVISNaturalConversation(self.project_root, style=ConversationStyle.MIXED)
            self.logger.info("   ✅ Natural Conversation enabled (human-like responses)")
        except Exception as e:
            self.natural_conversation = None
            self.logger.debug(f"   Natural Conversation not available: {e}")

    def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a command through JARVIS

        This is the main entry point for all JARVIS interactions.
        """
        self.logger.info(f"📋 Processing command: {command[:100]}")

        # Use Core Intelligence to understand intent
        intent = None
        if self.core_intelligence:
            intent = self.core_intelligence.understand_intent(command)
            self.logger.info(f"   Intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")

        # Route to appropriate handler
        if intent:
            if intent.intent_type.value == "question":
                return self._handle_question(command, intent, context)
            elif intent.intent_type.value == "command":
                return self._handle_command(command, intent, context)
            elif intent.intent_type.value == "request":
                return self._handle_request(command, intent, context)
            elif intent.intent_type.value == "information":
                return self._handle_information(command, intent, context)
            else:
                return self._handle_general(command, intent, context)
        else:
            return self._handle_general(command, None, context)

    def _handle_question(self, command: str, intent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle question intent"""
        # Get relevant context and memories
        relevant_contexts = []
        relevant_memories = []
        if self.core_intelligence:
            relevant_contexts = self.core_intelligence.get_relevant_context(intent)
            relevant_memories = self.core_intelligence.get_relevant_memories(intent)

        # Generate response context
        response_context = ""
        if self.core_intelligence:
            response_context = self.core_intelligence.generate_response_context(
                intent, relevant_contexts, relevant_memories
            )

        # For now, delegate to unified interface
        if self.unified_interface:
            result = self.unified_interface.delegate(command, context)
            base_response = result.get('result', {}).get('message', 'Got it.')
        else:
            base_response = "I'm not sure about that right now."

        # Use natural conversation system to humanize response
        response = self._humanize_response(base_response, command, "question")

        # Store conversation turn
        if self.core_intelligence:
            self.core_intelligence.process_conversation(command, response)

        return {
            "success": True,
            "type": "question",
            "response": response,
            "context": response_context,
            "intent": intent.to_dict() if intent else None
        }

    def _handle_command(self, command: str, intent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle command intent"""
        # Delegate to unified interface
        if self.unified_interface:
            result = self.unified_interface.delegate(command, context)
            base_response = f"Done. {result.get('result', {}).get('message', '')}" if result.get('result', {}).get('message') else "Done."
        else:
            base_response = "Can't do that right now."

        # Use natural conversation system to humanize response
        response = self._humanize_response(base_response, command, "command")

        # Store conversation turn
        if self.core_intelligence:
            self.core_intelligence.process_conversation(command, response)

        return {
            "success": True,
            "type": "command",
            "response": response,
            "result": result if self.unified_interface else None,
            "intent": intent.to_dict() if intent else None
        }

    def _handle_request(self, command: str, intent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle request intent"""
        # Similar to command, but more polite
        return self._handle_command(command, intent, context)

    def _handle_information(self, command: str, intent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle information request"""
        # Check if it's a system status request
        if any(word in command.lower() for word in ['status', 'health', 'diagnostics', 'system']):
            if self.realtime_diagnostics:
                status = self.realtime_diagnostics.get_quick_status()
                report = self.realtime_diagnostics.get_status_report()
                return {
                    "success": True,
                    "type": "information",
                    "response": status,
                    "details": report,
                    "intent": intent.to_dict() if intent else None
                }

        # Delegate to unified interface
        if self.unified_interface:
            result = self.unified_interface.delegate(command, context)
            base_response = result.get('result', {}).get('message', 'Here you go.')
        else:
            base_response = "Don't have that info right now."

        # Use natural conversation system to humanize response
        response = self._humanize_response(base_response, command, "information")

        # Store conversation turn
        if self.core_intelligence:
            self.core_intelligence.process_conversation(command, response)

        return {
            "success": True,
            "type": "information",
            "response": response,
            "result": result if self.unified_interface else None,
            "intent": intent.to_dict() if intent else None
        }

    def _handle_general(self, command: str, intent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle general/unrecognized intent"""
        # Try unified interface
        if self.unified_interface:
            result = self.unified_interface.delegate(command, context)
            base_response = result.get('result', {}).get('message', 'Sure, what do you need?')
        else:
            base_response = "What's up?"

        # Use natural conversation system to humanize response
        response = self._humanize_response(base_response, command, "general")

        # Store conversation turn
        if self.core_intelligence:
            self.core_intelligence.process_conversation(command, response)

        return {
            "success": True,
            "type": "general",
            "response": response,
            "result": result if self.unified_interface else None,
            "intent": intent.to_dict() if intent else None
        }

    def _humanize_response(self, base_response: str, user_input: str, response_type: str) -> str:
        """
        Humanize a response to make it natural and conversational

        If natural conversation system is available, use it. Otherwise,
        apply basic humanization rules.
        """
        if self.natural_conversation:
            # Use natural conversation system to humanize the base response
            # We'll use the _humanize_response method directly
            response = self.natural_conversation._humanize_response(base_response, user_input, None)
            return response

        # Basic humanization fallback
        response = base_response

        # Remove obvious AI patterns
        ai_patterns = [
            ("I understand your question", "Got it"),
            ("Command executed", "Done"),
            ("Here is the information", "Here's"),
            ("I cannot", "Can't"),
            ("I will", "I'll"),
        ]

        for pattern, replacement in ai_patterns:
            if pattern.lower() in response.lower():
                response = response.replace(pattern, replacement, 1)
                break

        # Use contractions
        response = response.replace(" cannot ", " can't ")
        response = response.replace(" I will ", " I'll ")
        response = response.replace(" that is ", " that's ")

        return response

    def get_status(self) -> Dict[str, Any]:
        """Get JARVIS master status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "unified_interface": self.unified_interface is not None,
                "core_intelligence": self.core_intelligence is not None,
                "realtime_diagnostics": self.realtime_diagnostics is not None,
                "voice_interface": VOICE_INTERFACE_AVAILABLE,
            },
            "system_status": None,
            "intelligence_status": None,
        }

        # Add system status
        if self.realtime_diagnostics:
            status["system_status"] = self.realtime_diagnostics.get_quick_status()

        # Add intelligence status
        if self.core_intelligence:
            status["intelligence_status"] = self.core_intelligence.get_status_report()

        return status


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Master Command Interface")
    parser.add_argument("--status", action="store_true", help="Get JARVIS status")
    parser.add_argument("--command", type=str, help="Execute a command")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")

    args = parser.parse_args()

    jarvis = JARVISMasterCommand()

    if args.status:
        status = jarvis.get_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.command:
        result = jarvis.process_command(args.command)

        # Use formatter for clear speaker labels
        try:
            from jarvis_conversation_formatter import ConversationFormatter, Speaker
            formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)

            # Print human input
            human_msg = formatter.format_message(Speaker.HUMAN, args.command, None)
            print(human_msg.formatted)

            # Print JARVIS response
            if result.get('response'):
                jarvis_msg = formatter.format_message(Speaker.JARVIS, result['response'], None)
                print(jarvis_msg.formatted)
            else:
                jarvis_msg = formatter.format_message(Speaker.JARVIS, "Command processed.", None)
                print(jarvis_msg.formatted)

            # Optionally print full JSON for debugging
            if args.json:
                print("\n" + "="*80)
                print("Full Response (JSON):")
                print("="*80)
                print(json.dumps(result, indent=2, default=str))
        except ImportError:
            # Fallback without formatter
            print(json.dumps(result, indent=2, default=str))
            if result.get('response'):
                print(f"\n🤖 JARVIS: {result['response']}")

    elif args.interactive:
        # Import conversation formatter for clear speaker labels
        try:
            from jarvis_conversation_formatter import ConversationFormatter, Speaker
            formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)
        except ImportError:
            formatter = None

        print("🎯 JARVIS Master Command Interface")
        print("   Type 'exit' or 'quit' to end")
        print("   Type 'status' for system status")
        print("   Ready for commands...\n")

        try:
            while True:
                try:
                    # Clear speaker label for human input
                    if formatter:
                        human_prompt = formatter.format_message(Speaker.HUMAN, "", None).formatted.replace("  ", " ").strip()
                        if human_prompt.endswith(":"):
                            human_prompt = human_prompt[:-1]
                        command = input(f"\n{human_prompt} ").strip()
                    else:
                        command = input("\n👤 HUMAN: ").strip()

                    if not command:
                        continue

                    if command.lower() in ['exit', 'quit', 'q']:
                        if formatter:
                            goodbye = formatter.format_message(Speaker.JARVIS, "Goodbye.", None)
                            print(goodbye.formatted)
                        else:
                            print("🤖 JARVIS: Goodbye.")
                        break

                    if command.lower() == 'status':
                        status = jarvis.get_status()
                        status_msg = status.get('system_status', 'Status unavailable')
                        if formatter:
                            response = formatter.format_message(Speaker.JARVIS, status_msg, None)
                            print(response.formatted)
                        else:
                            print(f"🤖 JARVIS: {status_msg}")
                        continue

                    result = jarvis.process_command(command)
                    if result.get('response'):
                        if formatter:
                            response = formatter.format_message(Speaker.JARVIS, result['response'], None)
                            print(response.formatted)
                        else:
                            print(f"🤖 JARVIS: {result['response']}")
                    else:
                        if formatter:
                            response = formatter.format_message(Speaker.JARVIS, "Command processed.", None)
                            print(response.formatted)
                        else:
                            print("🤖 JARVIS: Command processed.")

                except KeyboardInterrupt:
                    if formatter:
                        goodbye = formatter.format_message(Speaker.JARVIS, "Goodbye.", None)
                        print(f"\n{goodbye.formatted}")
                    else:
                        print("\n🤖 JARVIS: Goodbye.")
                    break
                except Exception as e:
                    if formatter:
                        error_msg = formatter.format_message(Speaker.SYSTEM, f"Error: {e}", None)
                        print(error_msg.formatted)
                    else:
                        print(f"⚙️  SYSTEM: Error: {e}")
        except EOFError:
            if formatter:
                goodbye = formatter.format_message(Speaker.JARVIS, "Goodbye.", None)
                print(f"\n{goodbye.formatted}")
            else:
                print("\n🤖 JARVIS: Goodbye.")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()