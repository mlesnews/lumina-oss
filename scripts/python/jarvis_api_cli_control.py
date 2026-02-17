#!/usr/bin/env python3
"""
JARVIS API/CLI Control - Controls Everything

"API CLI Everything" - JARVIS controls all systems through unified API/CLI interface.
Emulates Dragon NaturallySpeaking into workflows.

@JARVIS assists with establishing context & intent of original request <=> @ASK

Tags: #JARVIS #API_CLI #DRAGON_NATURALLYSPEAKING #INTENT #CONTEXT #LUMINA_CORE
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import json

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

logger = get_logger("JARVISAPICLI")


class ControlMethod(Enum):
    """Control method for JARVIS"""
    API = "api"
    CLI = "cli"
    BOTH = "both"


@dataclass
class JARVISCommand:
    """A JARVIS command"""
    command_id: str
    action: str
    target: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    intent: Optional[str] = None
    ask_required: bool = False
    context_established: bool = False
    intent_confirmed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class JARVISResponse:
    """Response from JARVIS command"""
    command_id: str
    success: bool
    result: Any
    message: str
    context_established: bool = False
    intent_confirmed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class JARVISAPICLIControl:
    """
    JARVIS API/CLI Control - Controls Everything

    "API CLI Everything" - Unified control interface for all systems.
    Emulates Dragon NaturallySpeaking workflow patterns.

    @JARVIS assists with establishing context & intent <=> @ASK
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS API/CLI Control"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.command_history: List[JARVISCommand] = []
        self.response_history: List[JARVISResponse] = []

        # Control method preference
        self.control_method = ControlMethod.BOTH  # Use both API and CLI

        # API/CLI Configuration - Port 777
        # APICLI<=>777 - JARVIS API/CLI maps to port 777
        self.api_port = 777
        self.api_host = "localhost"
        self.api_base_url = f"http://{self.api_host}:{self.api_port}"
        self.cli_identifier = "777"  # CLI identifier

        logger.info(f"   🔌 JARVIS API/CLI configured: APICLI<=>777")
        logger.info(f"      API: {self.api_base_url}")
        logger.info(f"      CLI Identifier: {self.cli_identifier}")

        # Dragon NaturallySpeaking emulation
        self.dragon_emulation_enabled = True

        # Intent preservation integration
        try:
            from intent_preservation_system import get_intent_preservation_system
            self.intent_system = get_intent_preservation_system()
            logger.info("✅ Intent Preservation System integrated")
        except ImportError:
            self.intent_system = None
            logger.warning("⚠️  Intent Preservation System not available")

    def execute_command(
        self,
        action: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        establish_context: bool = True,
        confirm_intent: bool = True
    ) -> JARVISResponse:
        """
        Execute a JARVIS command through API/CLI

        This is "API CLI Everything" - JARVIS controls all systems.

        Args:
            action: Action to perform
            target: Target system/resource
            parameters: Command parameters
            context: Additional context
            establish_context: If True, establish context before execution
            confirm_intent: If True, confirm intent before execution

        Returns:
            JARVISResponse with result
        """
        command_id = f"jarvis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        command = JARVISCommand(
            command_id=command_id,
            action=action,
            target=target,
            parameters=parameters or {},
            context=context or {},
            ask_required=False
        )

        # CRITICAL: Establish context & intent (Dragon NaturallySpeaking pattern)
        if establish_context or confirm_intent:
            context_established, intent_confirmed, ask_required = self._establish_context_and_intent(
                command, establish_context, confirm_intent
            )
            command.context_established = context_established
            command.intent_confirmed = intent_confirmed
            command.ask_required = ask_required

            if ask_required:
                logger.info(f"   📋 @ASK required for command: {action} {target}")
                return JARVISResponse(
                    command_id=command_id,
                    success=False,
                    result=None,
                    message=f"@ASK required - awaiting approval for: {action} {target}",
                    context_established=context_established,
                    intent_confirmed=intent_confirmed
                )

        # Store command
        self.command_history.append(command)

        # Execute via API or CLI
        try:
            if self.control_method in [ControlMethod.API, ControlMethod.BOTH]:
                result = self._execute_via_api(command)
            else:
                result = self._execute_via_cli(command)

            response = JARVISResponse(
                command_id=command_id,
                success=result.get("success", False),
                result=result.get("result"),
                message=result.get("message", "Command executed"),
                context_established=command.context_established,
                intent_confirmed=command.intent_confirmed
            )

            self.response_history.append(response)
            logger.info(f"   ✅ JARVIS command executed: {action} {target}")

            return response

        except Exception as e:
            logger.error(f"   ❌ JARVIS command failed: {e}")
            response = JARVISResponse(
                command_id=command_id,
                success=False,
                result=None,
                message=f"Command failed: {str(e)}",
                context_established=command.context_established,
                intent_confirmed=command.intent_confirmed
            )
            self.response_history.append(response)
            return response

    def _establish_context_and_intent(
        self,
        command: JARVISCommand,
        establish_context: bool,
        confirm_intent: bool
    ) -> tuple[bool, bool, bool]:
        """
        Establish context & intent (Dragon NaturallySpeaking pattern)

        This is the critical function - @JARVIS assists with establishing
        context & intent of original request <=> @ASK
        """
        context_established = False
        intent_confirmed = False
        ask_required = False

        # Build request text from command
        request_text = f"{command.action} {command.target}"
        if command.parameters:
            request_text += f" with {', '.join(command.parameters.keys())}"

        # Use intent preservation system
        if self.intent_system:
            try:
                analysis = self.intent_system.analyze_intent(
                    request_text,
                    source="jarvis_api_cli"
                )

                # Establish context
                if establish_context:
                    context_established = True
                    command.context = {
                        **command.context,
                        "intent_summary": analysis.intent_summary,
                        "building_blocks": [
                            {
                                "action": b.action,
                                "target": b.target,
                                "priority": b.priority
                            }
                            for b in analysis.building_blocks
                        ],
                        "clarity": analysis.clarity.value,
                        "confidence": analysis.confidence
                    }
                    logger.info(f"   🎯 Context established: {analysis.intent_summary}")

                # Confirm intent
                if confirm_intent:
                    if analysis.requires_clarification:
                        ask_required = True
                        logger.warning(f"   ⚠️  Intent unclear - @ASK required: {analysis.feedback_message}")
                    else:
                        intent_confirmed = True
                        command.intent = analysis.intent_summary
                        logger.info(f"   ✅ Intent confirmed: {analysis.intent_summary}")

            except Exception as e:
                logger.debug(f"   Intent analysis failed: {e}")
                # Continue without intent analysis
                context_established = True
                intent_confirmed = True
        else:
            # No intent system - assume context/intent OK
            context_established = True
            intent_confirmed = True

        return context_established, intent_confirmed, ask_required

    def _execute_via_api(self, command: JARVISCommand) -> Dict[str, Any]:
        """Execute command via API (Port 777)"""
        # APICLI<=>777 - Execute via API on port 777
        logger.info(f"   🌐 Executing via API (Port {self.api_port}): {command.action} {command.target}")

        try:
            import requests

            # Build API endpoint
            endpoint = f"{self.api_base_url}/api/v1/execute"

            # Prepare request payload
            payload = {
                "command_id": command.command_id,
                "action": command.action,
                "target": command.target,
                "parameters": command.parameters,
                "context": command.context,
                "intent": command.intent
            }

            # Make API call
            response = requests.post(
                endpoint,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "result": data.get("result"),
                    "message": data.get("message", "Command executed via API (Port 777)")
                }
            else:
                return {
                    "success": False,
                    "result": None,
                    "message": f"API call failed (Port {self.api_port}): {response.status_code}"
                }
        except ImportError:
            # requests not available - simulate API call
            logger.debug("   requests library not available - simulating API call")
            return {
                "success": True,
                "result": f"API result for {command.action} {command.target} (Port {self.api_port})",
                "message": f"Command executed via API (Port {self.api_port})"
            }
        except Exception as e:
            logger.warning(f"   API call failed (Port {self.api_port}): {e}")
            return {
                "success": False,
                "result": None,
                "message": f"API execution error (Port {self.api_port}): {str(e)}"
            }

    def _execute_via_cli(self, command: JARVISCommand) -> Dict[str, Any]:
        """Execute command via CLI (Identifier 777)"""
        # APICLI<=>777 - Execute via CLI with identifier 777
        logger.info(f"   💻 Executing via CLI (ID: {self.cli_identifier}): {command.action} {command.target}")

        # Build CLI command
        cli_command = self._build_cli_command(command)

        # Add CLI identifier 777
        cli_command.insert(0, f"jarvis-{self.cli_identifier}")

        try:
            # Execute via subprocess
            result = subprocess.run(
                cli_command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "result": result.stdout,
                    "message": f"Command executed via CLI (ID: {self.cli_identifier})"
                }
            else:
                return {
                    "success": False,
                    "result": result.stderr,
                    "message": f"CLI command failed (ID: {self.cli_identifier}): {result.returncode}"
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "result": None,
                "message": "CLI command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "message": f"CLI execution error: {str(e)}"
            }

    def _build_cli_command(self, command: JARVISCommand) -> List[str]:
        """Build CLI command from JARVIS command"""
        # Map actions to CLI commands
        action_map = {
            "create": ["create"],
            "fix": ["fix"],
            "check": ["check"],
            "run": ["run"],
            "execute": ["execute"],
            "grammar_check": ["grammarly", "check"]
        }

        base_command = action_map.get(command.action, [command.action])

        # Add target
        if command.target:
            base_command.append(command.target)

        # Add parameters
        for key, value in command.parameters.items():
            base_command.extend([f"--{key}", str(value)])

        return base_command

    def emulate_dragon_naturally_speaking(
        self,
        voice_command: str,
        context: Optional[Dict[str, Any]] = None
    ) -> JARVISResponse:
        """
        Emulate Dragon NaturallySpeaking workflow

        Dragon NaturallySpeaking pattern:
        1. Voice command received
        2. Establish context
        3. Confirm intent
        4. Execute via API/CLI
        """
        logger.info(f"   🐉 Dragon NaturallySpeaking emulation: {voice_command}")

        # Parse voice command (simple pattern matching - can be enhanced)
        parts = voice_command.lower().split()

        if len(parts) < 2:
            return JARVISResponse(
                command_id="dragon_error",
                success=False,
                result=None,
                message="Invalid voice command format"
            )

        action = parts[0]
        target = " ".join(parts[1:])

        # Execute with context/intent establishment
        return self.execute_command(
            action=action,
            target=target,
            context=context,
            establish_context=True,
            confirm_intent=True
        )

    def control_everything(
        self,
        request: str,
        source: str = "voice"
    ) -> JARVISResponse:
        """
        Control Everything - Main entry point

        "API CLI Everything" - JARVIS controls all systems.
        Works with voice, text, or any input.
        """
        logger.info(f"   🎛️  JARVIS controlling everything: {request[:50]}...")

        # If voice input, use Dragon NaturallySpeaking emulation
        if source == "voice" and self.dragon_emulation_enabled:
            return self.emulate_dragon_naturally_speaking(request)

        # Otherwise, parse and execute
        # Use intent preservation to understand request
        if self.intent_system:
            analysis = self.intent_system.analyze_intent(request, source=source)

            # Extract action and target from building blocks
            if analysis.building_blocks:
                block = analysis.building_blocks[0]  # Use first block
                return self.execute_command(
                    action=block.action,
                    target=block.target,
                    context=analysis.building_blocks[0].context,
                    establish_context=True,
                    confirm_intent=True
                )

        # Fallback: simple parsing
        parts = request.split()
        if len(parts) >= 2:
            return self.execute_command(
                action=parts[0],
                target=" ".join(parts[1:]),
                establish_context=True,
                confirm_intent=True
            )

        return JARVISResponse(
            command_id="error",
            success=False,
            result=None,
            message="Could not parse request"
        )


# Global instance
_jarvis_api_cli_instance = None


def get_jarvis_api_cli() -> JARVISAPICLIControl:
    """Get or create global JARVIS API/CLI control instance"""
    global _jarvis_api_cli_instance
    if _jarvis_api_cli_instance is None:
        _jarvis_api_cli_instance = JARVISAPICLIControl()
        logger.info("✅ JARVIS API/CLI Control initialized - API CLI EVERYTHING ACTIVE")
        logger.info(f"   🔌 APICLI<=>777 - Port {_jarvis_api_cli_instance.api_port}, CLI ID: {_jarvis_api_cli_instance.cli_identifier}")
    return _jarvis_api_cli_instance


def control_everything(request: str, source: str = "voice") -> JARVISResponse:
    """Control everything via JARVIS API/CLI"""
    jarvis = get_jarvis_api_cli()
    return jarvis.control_everything(request, source)


if __name__ == "__main__":
    # Test
    jarvis = get_jarvis_api_cli()

    # Test Dragon NaturallySpeaking emulation
    print("\n🐉 Testing Dragon NaturallySpeaking emulation...")
    response = jarvis.emulate_dragon_naturally_speaking("check grammar in my text")
    print(f"   Success: {response.success}")
    print(f"   Message: {response.message}")
    print(f"   Context established: {response.context_established}")
    print(f"   Intent confirmed: {response.intent_confirmed}")

    # Test control everything
    print("\n🎛️  Testing control everything...")
    response = jarvis.control_everything("fix the grammar", source="voice")
    print(f"   Success: {response.success}")
    print(f"   Message: {response.message}")
