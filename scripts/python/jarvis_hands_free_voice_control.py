#!/usr/bin/env python3
"""
JARVIS Hands-Free Voice Control - Full IDE Control via MANUS

Complete hands-free operation:
- No clicking
- No pasting
- No copying
- Full voice control of everything
- MANUS integration for desktop/IDE control

Tags: #JARVIS #VOICE #HANDS-FREE #MANUS #IDE_CONTROL #NO_CLICKING @JARVIS @LUMINA
"""

import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
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

logger = get_logger("JARVISHandsFreeVoice")


class VoiceCommandType(Enum):
    """Voice command types"""
    IDE_CONTROL = "ide_control"
    FILE_OPERATION = "file_operation"
    TEXT_OPERATION = "text_operation"
    NAVIGATION = "navigation"
    SEARCH = "search"
    GIT = "git"
    TERMINAL = "terminal"
    CHARACTER = "character"
    TODO = "todo"
    NOTIFICATION = "notification"
    GENERAL = "general"


@dataclass
class VoiceCommand:
    """Voice command"""
    command_id: str
    raw_text: str
    command_type: VoiceCommandType
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_type"] = self.command_type.value
        return data


class JARVISHandsFreeVoiceControl:
    """
    JARVIS Hands-Free Voice Control

    Complete hands-free operation using MANUS for full IDE control.
    No clicking, pasting, or copying required.
    """

    def __init__(self, project_root: Optional[Path] = None, silent_mode: bool = False):
        """Initialize hands-free voice control"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.silent_mode = silent_mode

        # MANUS integration
        try:
            from manus_unified_control import MANUSUnifiedControl, ControlArea
            self.manus = MANUSUnifiedControl(self.project_root)
            self.manus_available = True
            logger.info("✅ MANUS Unified Control initialized")
        except Exception as e:
            logger.warning(f"   ⚠️  MANUS not available: {e}")
            self.manus = None
            self.manus_available = False

        # Voice interface
        try:
            from jarvis_voice_interface import JARVISVoiceInterface
            self.voice_interface = JARVISVoiceInterface(self.project_root)
            self.voice_available = True
        except Exception as e:
            logger.warning(f"   ⚠️  Voice interface not available: {e}")
            self.voice_interface = None
            self.voice_available = False

        # Character system
        try:
            from jarvis_character_actor_system import JARVISCharacterActorSystem
            self.character_system = JARVISCharacterActorSystem(
                self.project_root,
                silent_mode=silent_mode
            )
        except Exception as e:
            logger.warning(f"   ⚠️  Character system not available: {e}")
            self.character_system = None

        # To-do display
        try:
            from chat_session_todo_display import ChatSessionTodoDisplay
            self.todo_display = ChatSessionTodoDisplay(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  To-do display not available: {e}")
            self.todo_display = None

        # Command history
        self.command_history: List[VoiceCommand] = []
        self.data_dir = self.project_root / "data" / "hands_free_voice"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Command patterns
        self._initialize_command_patterns()

        logger.info("✅ JARVIS Hands-Free Voice Control initialized")
        logger.info("   🎙️  Full hands-free operation enabled")
        logger.info("   🖱️  No clicking required")
        logger.info("   📋 No pasting required")
        logger.info("   📄 No copying required")

    def _initialize_command_patterns(self):
        """Initialize voice command patterns"""
        self.command_patterns = {
            # IDE Control
            VoiceCommandType.IDE_CONTROL: [
                (r"open file (.+)", "open_file", {"file": 1}),
                (r"create file (.+)", "create_file", {"file": 1}),
                (r"save file", "save_file", {}),
                (r"close file", "close_file", {}),
                (r"new file", "new_file", {}),
                (r"go to line (\d+)", "go_to_line", {"line": 1}),
                (r"find (.+)", "find_text", {"text": 1}),
                (r"replace (.+) with (.+)", "replace_text", {"find": 1, "replace": 2}),
                (r"undo", "undo", {}),
                (r"redo", "redo", {}),
                (r"format code", "format_code", {}),
                (r"run code", "run_code", {}),
                (r"debug", "start_debug", {}),
                (r"stop debug", "stop_debug", {}),
            ],

            # File Operations
            VoiceCommandType.FILE_OPERATION: [
                (r"copy file (.+) to (.+)", "copy_file", {"source": 1, "dest": 2}),
                (r"move file (.+) to (.+)", "move_file", {"source": 1, "dest": 2}),
                (r"delete file (.+)", "delete_file", {"file": 1}),
                (r"rename file (.+) to (.+)", "rename_file", {"old": 1, "new": 2}),
            ],

            # Text Operations (no manual copy/paste)
            VoiceCommandType.TEXT_OPERATION: [
                (r"select all", "select_all", {}),
                (r"select line", "select_line", {}),
                (r"select word", "select_word", {}),
                (r"copy selection", "copy_selection", {}),
                (r"cut selection", "cut_selection", {}),
                (r"paste", "paste", {}),
                (r"type (.+)", "type_text", {"text": 1}),
                (r"insert (.+)", "insert_text", {"text": 1}),
                (r"delete selection", "delete_selection", {}),
            ],

            # Navigation
            VoiceCommandType.NAVIGATION: [
                (r"go to definition", "go_to_definition", {}),
                (r"go back", "go_back", {}),
                (r"go forward", "go_forward", {}),
                (r"show files", "show_files", {}),
                (r"show terminal", "show_terminal", {}),
                (r"focus editor", "focus_editor", {}),
                (r"focus terminal", "focus_terminal", {}),
            ],

            # Search
            VoiceCommandType.SEARCH: [
                (r"search in files (.+)", "search_in_files", {"query": 1}),
                (r"search symbol (.+)", "search_symbol", {"symbol": 1}),
                (r"find references", "find_references", {}),
            ],

            # Git
            VoiceCommandType.GIT: [
                (r"git commit (.+)", "git_commit", {"message": 1}),
                (r"git push", "git_push", {}),
                (r"git pull", "git_pull", {}),
                (r"git status", "git_status", {}),
                (r"git diff", "git_diff", {}),
            ],

            # Terminal
            VoiceCommandType.TERMINAL: [
                (r"run command (.+)", "run_terminal_command", {"command": 1}),
                (r"execute (.+)", "execute_command", {"command": 1}),
                (r"clear terminal", "clear_terminal", {}),
            ],

            # Character commands
            VoiceCommandType.CHARACTER: [
                (r"pop in (.+)", "pop_in_character", {"character": 1}),
                (r"pop out (.+)", "pop_out_character", {"character": 1}),
                (r"mace windu", "handle_mace_windu", {}),
                (r"iron man", "handle_iron_man", {}),
            ],

            # To-do
            VoiceCommandType.TODO: [
                (r"show todos", "show_todos", {}),
                (r"add todo (.+)", "add_todo", {"title": 1}),
                (r"complete todo (.+)", "complete_todo", {"todo": 1}),
                (r"show master list", "show_master_list", {}),
            ],

            # Notification
            VoiceCommandType.NOTIFICATION: [
                (r"show notifications", "show_notifications", {}),
                (r"track notification (.+)", "track_notification", {"text": 1}),
            ],
        }

    def parse_voice_command(self, text: str) -> Optional[VoiceCommand]:
        """
        Parse voice command from text

        Args:
            text: Voice command text

        Returns:
            VoiceCommand object or None
        """
        text_lower = text.lower().strip()

        # Try each command type
        for cmd_type, patterns in self.command_patterns.items():
            for pattern, action, param_map in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    # Extract parameters
                    parameters = {}
                    for param_name, group_index in param_map.items():
                        if group_index <= len(match.groups()):
                            parameters[param_name] = match.group(group_index)

                    import hashlib
                    command_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

                    command = VoiceCommand(
                        command_id=command_id,
                        raw_text=text,
                        command_type=cmd_type,
                        action=action,
                        parameters=parameters
                    )

                    logger.info(f"   ✅ Parsed command: {action} ({cmd_type.value})")
                    return command

        # No match found
        logger.warning(f"   ⚠️  Could not parse command: {text}")
        return None

    def execute_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """
        Execute voice command using MANUS

        Args:
            command: Voice command to execute

        Returns:
            Execution result
        """
        if not self.manus_available:
            return {"success": False, "error": "MANUS not available"}

        try:
            # Route to appropriate handler
            handler = getattr(self, f"_handle_{command.action}", None)
            if handler:
                result = handler(command)
            else:
                # Try MANUS direct control
                result = self._execute_via_manus(command)

            # Record command
            self.command_history.append(command)
            self._save_command_history()

            return result
        except Exception as e:
            logger.error(f"   ❌ Error executing command: {e}")
            return {"success": False, "error": str(e)}

    def _execute_via_manus(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute command via MANUS"""
        try:
            from manus_unified_control import ControlArea

            # Map command type to control area
            area_map = {
                VoiceCommandType.IDE_CONTROL: ControlArea.IDE_CONTROL,
                VoiceCommandType.FILE_OPERATION: ControlArea.IDE_CONTROL,
                VoiceCommandType.TEXT_OPERATION: ControlArea.IDE_CONTROL,
                VoiceCommandType.NAVIGATION: ControlArea.IDE_CONTROL,
                VoiceCommandType.SEARCH: ControlArea.IDE_CONTROL,
                VoiceCommandType.GIT: ControlArea.PROJECT_LUMINA_MANAGEMENT,
                VoiceCommandType.TERMINAL: ControlArea.IDE_CONTROL,
            }

            area = area_map.get(command.command_type)
            if not area:
                return {"success": False, "error": "Unknown command area"}

            # Execute via MANUS
            if hasattr(self.manus, 'execute_operation'):
                result = self.manus.execute_operation(
                    area=area,
                    action=command.action,
                    parameters=command.parameters
                )
            else:
                # Try alternative MANUS interface
                result = self._execute_via_manus_alternative(area, command)

            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_via_manus_alternative(self, area, command: VoiceCommand) -> Dict[str, Any]:
        """Alternative MANUS execution method"""
        try:
            # Try to get IDE controller from MANUS
            if hasattr(self.manus, 'controllers') and area in self.manus.controllers:
                controller = self.manus.controllers[area]
                if controller:
                    # Try to call action on controller
                    if hasattr(controller, command.action):
                        method = getattr(controller, command.action)
                        result = method(**command.parameters)
                        return {"success": True, "result": result}

            return {"success": False, "error": "MANUS controller not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Command handlers
    def _handle_open_file(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle open file command"""
        file_path = command.parameters.get("file", "")
        if self.manus and self.manus_available:
            from manus_unified_control import ControlArea
            # Use MANUS to open file (no clicking)
            result = self._execute_via_manus(command)
            return {"success": True, "message": f"Opening file: {file_path}"}
        return {"success": False, "error": "MANUS not available"}

    def _handle_type_text(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle type text command (no pasting)"""
        text = command.parameters.get("text", "")
        if self.manus and self.manus_available:
            # Use MANUS to type text directly
            result = self.manus.execute_operation(
                area=ControlArea.IDE_CONTROL,
                action="type_text",
                parameters={"text": text}
            )
            return {"success": True, "message": f"Typed: {text}"}
        return {"success": False, "error": "MANUS not available"}

    def _handle_copy_selection(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle copy selection (no manual copying)"""
        if self.manus and self.manus_available:
            result = self.manus.execute_operation(
                area=ControlArea.IDE_CONTROL,
                action="copy_selection",
                parameters={}
            )
            return {"success": True, "message": "Selection copied"}
        return {"success": False, "error": "MANUS not available"}

    def _handle_paste(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle paste (no manual pasting)"""
        if self.manus and self.manus_available:
            result = self.manus.execute_operation(
                area=ControlArea.IDE_CONTROL,
                action="paste",
                parameters={}
            )
            return {"success": True, "message": "Pasted"}
        return {"success": False, "error": "MANUS not available"}

    def _handle_pop_in_character(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle pop in character"""
        character = command.parameters.get("character", "").replace(" ", "_").lower()
        if self.character_system:
            success = self.character_system.pop_in_character(character, "Voice command")
            return {"success": success, "message": f"Popped in {character}"}
        return {"success": False, "error": "Character system not available"}

    def _handle_show_todos(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle show todos"""
        if self.todo_display:
            display = self.todo_display.get_dual_display()
            # Speak or display
            if not self.silent_mode and self.voice_interface:
                self.voice_interface.speak("Showing to-do lists")
            return {"success": True, "display": display}
        return {"success": False, "error": "To-do display not available"}

    def _handle_add_todo(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle add todo"""
        title = command.parameters.get("title", "")
        if self.todo_display:
            self.todo_display.add_session_todo(title)
            if not self.silent_mode and self.voice_interface:
                self.voice_interface.speak(f"Added todo: {title}")
            return {"success": True, "message": f"Added todo: {title}"}
        return {"success": False, "error": "To-do display not available"}

    def process_voice_input(self, text: str) -> Dict[str, Any]:
        """
        Process voice input and execute command

        Args:
            text: Voice input text

        Returns:
            Execution result
        """
        logger.info(f"   🎙️  Voice input: {text}")

        # Parse command
        command = self.parse_voice_command(text)
        if not command:
            return {"success": False, "error": "Could not parse command"}

        # Execute command
        result = self.execute_command(command)

        # Provide feedback
        if result.get("success") and not self.silent_mode:
            message = result.get("message", "Command executed")
            if self.voice_interface:
                self.voice_interface.speak(message)

        return result

    def start_continuous_listening(self):
        """Start continuous voice listening"""
        if not self.voice_available:
            logger.error("   ❌ Voice interface not available")
            return

        logger.info("=" * 80)
        logger.info("🎙️  JARVIS HANDS-FREE VOICE CONTROL")
        logger.info("=" * 80)
        logger.info("   🖱️  No clicking required")
        logger.info("   📋 No pasting required")
        logger.info("   📄 No copying required")
        logger.info("   🎙️  Just speak naturally")
        logger.info("=" * 80)
        logger.info("")

        if self.voice_interface:
            # Start listening loop
            if hasattr(self.voice_interface, 'voice_loop'):
                # Use existing voice loop
                self.voice_interface.is_listening = True
                # Override process_voice_command to use our handler
                original_process = self.voice_interface.process_voice_command
                def enhanced_process(command: str) -> str:
                    result = self.process_voice_input(command)
                    if result.get("success"):
                        return result.get("message", "Command executed")
                    else:
                        return result.get("error", "Command failed")
                self.voice_interface.process_voice_command = enhanced_process
                self.voice_interface.voice_loop()
            elif hasattr(self.voice_interface, 'listen'):
                # Manual loop
                self._manual_listening_loop()
            else:
                logger.warning("   ⚠️  Voice interface does not support continuous listening")

    def _manual_listening_loop(self):
        """Manual listening loop"""
        logger.info("   🎤 Starting manual listening loop...")
        if not self.silent_mode and self.voice_interface:
            self.voice_interface.speak("JARVIS hands-free mode activated. I'm listening.")

        while True:
            try:
                text = self.voice_interface.listen(timeout=5)
                if text:
                    result = self.process_voice_input(text)
                    if not self.silent_mode and self.voice_interface:
                        message = result.get("message", "Command executed" if result.get("success") else "Command failed")
                        self.voice_interface.speak(message)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"   ❌ Listening error: {e}")
                time.sleep(1)

    def _save_command_history(self):
        """Save command history"""
        try:
            history_file = self.data_dir / "command_history.json"
            data = {
                "last_updated": datetime.now().isoformat(),
                "commands": [cmd.to_dict() for cmd in self.command_history[-100:]]  # Last 100
            }
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"   Could not save command history: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Hands-Free Voice Control")
        parser.add_argument("--command", type=str, help="Execute voice command")
        parser.add_argument("--start", action="store_true", help="Start continuous listening")
        parser.add_argument("--silent", action="store_true", help="Enable silent mode")
        parser.add_argument("--test", type=str, help="Test command parsing")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        control = JARVISHandsFreeVoiceControl(silent_mode=args.silent)

        if args.test:
            command = control.parse_voice_command(args.test)
            if args.json:
                print(json.dumps(command.to_dict() if command else {"error": "No match"}, indent=2))
            else:
                if command:
                    print(f"✅ Parsed: {command.action} ({command.command_type.value})")
                    print(f"   Parameters: {command.parameters}")
                else:
                    print(f"❌ Could not parse: {args.test}")

        elif args.command:
            result = control.process_voice_input(args.command)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result.get("success"):
                    print(f"✅ {result.get('message', 'Command executed')}")
                else:
                    print(f"❌ {result.get('error', 'Command failed')}")

        elif args.start:
            control.start_continuous_listening()

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()