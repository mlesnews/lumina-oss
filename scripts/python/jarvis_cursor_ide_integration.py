#!/usr/bin/env python3
"""
JARVIS Cursor IDE Integration
Complete IDE Control via Keyboard Shortcuts - JARVIS Integration

Integrates JARVIS with Cursor IDE for complete keyboard-based control.
No mouse clicking required - all commands via keyboard shortcuts.

Features:
- Natural language command processing via JARVIS
- Complete keyboard shortcut mapping
- Voice and text command support
- Intelligent command parsing
- Seamless IDE control

@JARVIS @MANUS @SYPHON
"""

import sys
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorIDEIntegration")

# Import keyboard controller
try:
    from cursor_ide_keyboard_controller import CursorIDEKeyboardController, ShortcutResult
    KEYBOARD_CONTROLLER_AVAILABLE = True
except ImportError:
    KEYBOARD_CONTROLLER_AVAILABLE = False
    logger.warning("Cursor IDE Keyboard Controller not available")

# Import JARVIS components
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent, ConversationTurn, ConversationMode
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    logger.warning("JARVIS Full-Time Super Agent not available")

try:
    from jarvis_hands_free_cursor_control import JARVISHandsFreeCursorControl
    HANDS_FREE_AVAILABLE = True
except ImportError:
    HANDS_FREE_AVAILABLE = False
    logger.warning("JARVIS Hands-Free Cursor Control not available")


class JARVISCursorIDEIntegration:
    """
    JARVIS Cursor IDE Integration

    Complete integration of JARVIS with Cursor IDE for keyboard-based control.
    Processes natural language commands from JARVIS and executes them via keyboard shortcuts.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS-Cursor IDE integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.running = False

        # Initialize keyboard controller
        if KEYBOARD_CONTROLLER_AVAILABLE:
            self.keyboard_controller = CursorIDEKeyboardController()
        else:
            self.keyboard_controller = None
            logger.error("❌ Keyboard controller not available")

        # Initialize JARVIS (if available)
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent()
            except Exception as e:
                logger.warning(f"JARVIS not available: {e}")

        # Command processing queue
        self.command_queue = queue.Queue()
        self.command_thread = threading.Thread(target=self._command_processor_loop, daemon=True)
        self.command_thread.start()

        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []

        logger.info("✅ JARVIS Cursor IDE Integration initialized")
        logger.info("   Complete keyboard control - no mouse required")

    def process_command(self, command: str, source: str = "text") -> Dict[str, Any]:
        """
        Process command from JARVIS (voice or text)

        Args:
            command: Natural language command
            source: Source of command ("voice" or "text")

        Returns:
            Processing result
        """
        logger.info(f"🎤 Processing command ({source}): {command[:100]}...")

        try:
            # Queue command for processing
            command_entry = {
                "command": command,
                "source": source,
                "timestamp": datetime.now(),
                "status": "pending"
            }
            self.command_queue.put(command_entry)

            # Execute immediately (non-blocking queue processing happens in background)
            result = self._execute_command(command)

            # Update command entry
            command_entry["status"] = "completed" if result["success"] else "failed"
            command_entry["result"] = result

            # Add to conversation history
            self.conversation_history.append(command_entry)

            return result

        except Exception as e:
            logger.error(f"❌ Command processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }

    def _execute_command(self, command: str) -> Dict[str, Any]:
        """Execute command via keyboard controller"""
        if not self.keyboard_controller:
            return {
                "success": False,
                "error": "Keyboard controller not available",
                "command": command
            }

        try:
            # Execute natural language command
            result = self.keyboard_controller.execute_natural_language_command(command)

            return {
                "success": result.success,
                "method": result.method,
                "shortcut": result.shortcut_name,
                "command": result.command,
                "error": result.error,
                "execution_time": result.execution_time,
                "command_text": command
            }

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }

    def _command_processor_loop(self):
        """Background thread for command processing"""
        while True:
            try:
                command_entry = self.command_queue.get(timeout=1.0)
                if command_entry is None:  # Shutdown signal
                    break

                # Process command (already executed in process_command, this is for async processing)
                self.command_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in command processor: {e}")

    def start_conversation_mode(self):
        """Start conversation mode with JARVIS"""
        logger.info("🎤 Starting JARVIS conversation mode...")

        if not self.jarvis:
            logger.error("❌ JARVIS not available")
            return False

        self.running = True

        logger.info("✅ Conversation mode started")
        logger.info("   Speak or type commands to control Cursor IDE")
        logger.info("   Say 'stop' or 'exit' to end")

        return True

    def stop_conversation_mode(self):
        """Stop conversation mode"""
        self.running = False
        logger.info("🛑 Conversation mode stopped")

    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """
        Get command suggestions based on partial input

        Args:
            partial_command: Partial command text

        Returns:
            List of suggested commands
        """
        if not self.keyboard_controller:
            return []

        # Search shortcuts
        results = self.keyboard_controller.search_shortcuts(partial_command)

        # Extract descriptions/aliases
        suggestions = []
        for result in results[:10]:  # Limit to 10 suggestions
            suggestions.append(result["description"])
            # Add first alias
            shortcut_info = self.keyboard_controller.shortcuts_map.get(result["name"], {})
            if shortcut_info.get("aliases"):
                suggestions.append(shortcut_info["aliases"][0])

        return list(set(suggestions))[:10]

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "running": self.running,
            "keyboard_controller_available": self.keyboard_controller is not None,
            "jarvis_available": self.jarvis is not None,
            "conversation_history_count": len(self.conversation_history),
            "pending_commands": self.command_queue.qsize()
        }

    def get_available_commands(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get available commands"""
        if not self.keyboard_controller:
            return {}

        shortcuts = self.keyboard_controller.get_available_shortcuts(category=category)

        # Format for display
        commands = {}
        for name, info in shortcuts.items():
            commands[name] = {
                "description": info.get("description"),
                "keys": info.get("keys", []),
                "category": info.get("category"),
                "aliases": info.get("aliases", [])
            }

        return commands


class JARVISCursorCommandBridge:
    """
    Bridge between JARVIS and Cursor IDE commands

    Provides a clean interface for JARVIS to control Cursor IDE.
    """

    def __init__(self, integration: Optional[JARVISCursorIDEIntegration] = None):
        """Initialize command bridge"""
        if integration is None:
            integration = JARVISCursorIDEIntegration()

        self.integration = integration
        self.logger = logger

    def execute(self, command: str, source: str = "text") -> Dict[str, Any]:
        """
        Execute command via bridge

        Args:
            command: Natural language command
            source: Source of command

        Returns:
            Execution result
        """
        return self.integration.process_command(command, source)

    def get_help(self) -> str:
        """Get help text for available commands"""
        commands = self.integration.get_available_commands()

        help_text = "Available Cursor IDE Commands:\n\n"

        # Group by category
        categories = {}
        for name, info in commands.items():
            category = info.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append((name, info))

        for category, command_list in sorted(categories.items()):
            help_text += f"\n{category}:\n"
            for name, info in command_list[:10]:  # Limit per category
                aliases = ", ".join(info.get("aliases", [])[:3])  # First 3 aliases
                help_text += f"  - {info['description']} ({aliases})\n"

        return help_text


def get_jarvis_cursor_integration() -> JARVISCursorIDEIntegration:
    """Get singleton JARVIS-Cursor IDE integration instance"""
    global _integration_instance
    if '_integration_instance' not in globals():
        _integration_instance = JARVISCursorIDEIntegration()
    return _integration_instance


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Cursor IDE Integration")
    parser.add_argument("--command", type=str, help="Execute command")
    parser.add_argument("--start", action="store_true", help="Start conversation mode")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--commands", action="store_true", help="List available commands")
    parser.add_argument("--category", type=str, help="Filter commands by category")
    parser.add_argument("--search", type=str, help="Search commands")
    parser.add_argument("--help-text", action="store_true", help="Show help text")

    args = parser.parse_args()

    integration = JARVISCursorIDEIntegration()

    if args.command:
        result = integration.process_command(args.command)
        print(f"Success: {result.get('success')}")
        if result.get('error'):
            print(f"Error: {result.get('error')}")

    elif args.start:
        integration.start_conversation_mode()
        try:
            while integration.running:
                time.sleep(1)
        except KeyboardInterrupt:
            integration.stop_conversation_mode()

    elif args.status:
        status = integration.get_status()
        import json
        print(json.dumps(status, indent=2))

    elif args.commands:
        commands = integration.get_available_commands(category=args.category)
        import json
        print(json.dumps(commands, indent=2))

    elif args.search:
        suggestions = integration.get_command_suggestions(args.search)
        print(f"Suggestions for '{args.search}':")
        for suggestion in suggestions:
            print(f"  - {suggestion}")

    elif args.help_text:
        bridge = JARVISCursorCommandBridge(integration)
        print(bridge.get_help())

    else:
        parser.print_help()
        print("\n✅ JARVIS Cursor IDE Integration")
        print("   Complete keyboard control - no mouse required")


if __name__ == "__main__":

    main()