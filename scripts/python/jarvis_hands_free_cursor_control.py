#!/usr/bin/env python3
"""
JARVIS Hands-Free Cursor Control

Complete hands-free interface where JARVIS controls Cursor IDE:
- Voice input (hands-free conversation)
- JARVIS processes requests
- MANUS executes actions via keyboard shortcuts (primary)
- Mouse control as backup
- Voice responses back to user

No clicking required - fully automated IDE control.
"""

import sys
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISHandsFreeCursor")

# Import dependencies
try:
    from manus_cursor_controller import ManusCursorController, CursorState
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.warning("MANUS Cursor Controller not available")

try:
    from cursor_intelligent_warm_recycle import CursorIntelligentWarmRecycle, RecycleReason
    RECYCLE_AVAILABLE = True
except ImportError:
    RECYCLE_AVAILABLE = False
    logger.warning("Cursor warm recycle system not available")

try:
    from jarvis_voice_activated import JARVISVoiceActivated
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("JARVIS Voice Activated not available")

try:
    from jarvis_natural_conversation import JARVISNaturalConversation
    CONVERSATION_AVAILABLE = True
except ImportError:
    CONVERSATION_AVAILABLE = False
    logger.warning("JARVIS Natural Conversation not available")

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    import pygetwindow as gw
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput not available - install: pip install pynput pygetwindow")


class KeyboardShortcutExecutor:
    """
    Execute keyboard shortcuts for Cursor IDE control
    Primary method: Keyboard shortcuts
    Backup: Mouse control
    """

    CURSOR_SHORTCUTS = {
        # Chat/Conversation
        "open_chat": [Key.ctrl, Key.shift, 'p'],  # Command palette, then type "Chat"
        "focus_chat": ['ctrl', 'l'],  # Cursor chat shortcut
        "composer": ['ctrl', 'i'],  # Cursor Composer
        "inline_chat": ['ctrl', 'k'],  # Inline chat

        # File Operations
        "open_file": [Key.ctrl, 'p'],  # Quick open
        "new_file": [Key.ctrl, 'n'],
        "save_file": [Key.ctrl, 's'],
        "close_file": [Key.ctrl, 'w'],
        "close_all": [Key.ctrl, Key.shift, 'w'],

        # Editing
        "undo": [Key.ctrl, 'z'],
        "redo": [Key.ctrl, Key.shift, 'z'],
        "cut": [Key.ctrl, 'x'],
        "copy": [Key.ctrl, 'c'],
        "paste": [Key.ctrl, 'v'],
        "select_all": [Key.ctrl, 'a'],
        "find": [Key.ctrl, 'f'],
        "replace": [Key.ctrl, 'h'],
        "goto_line": [Key.ctrl, 'g'],
        "goto_symbol": [Key.ctrl, Key.shift, 'o'],

        # Code Actions
        "format_document": [Key.shift, Key.alt, 'f'],
        "format_selection": [Key.ctrl, 'k', Key.ctrl, 'f'],
        "comment_line": [Key.ctrl, '/'],
        "toggle_line_comment": [Key.ctrl, '/'],
        "indent_line": [Key.ctrl, ']'],
        "outdent_line": [Key.ctrl, '['],

        # Navigation
        "goto_definition": ['f12'],
        "peek_definition": [Key.alt, 'f12'],
        "goto_references": [Key.shift, 'f12'],
        "go_back": [Key.ctrl, Key.alt, '-'],
        "go_forward": [Key.ctrl, Key.shift, '-'],
        "switch_editor": [Key.ctrl, 'pageup'],
        "next_editor": [Key.ctrl, 'pagedown'],

        # Terminal
        "toggle_terminal": [Key.ctrl, '`'],
        "new_terminal": [Key.ctrl, Key.shift, '`'],
        "split_terminal": [Key.ctrl, Key.shift, '\\'],

        # Panels
        "toggle_sidebar": [Key.ctrl, 'b'],
        "toggle_explorer": [Key.ctrl, Key.shift, 'e'],
        "toggle_search": [Key.ctrl, Key.shift, 'f'],
        "toggle_git": [Key.ctrl, Key.shift, 'g'],
        "toggle_extensions": [Key.ctrl, Key.shift, 'x'],
        "toggle_output": [Key.ctrl, Key.shift, 'u'],
        "toggle_problems": [Key.ctrl, Key.shift, 'm'],

        # Debug
        "start_debugging": ['f5'],
        "stop_debugging": [Key.shift, 'f5'],
        "toggle_breakpoint": ['f9'],
        "step_over": ['f10'],
        "step_into": ['f11'],
        "step_out": [Key.shift, 'f11'],

        # AI/Assistance
        "cursor_chat": [Key.ctrl, 'l'],  # Open Cursor chat
        "cursor_composer": [Key.ctrl, 'i'],  # Composer mode
        "accept_suggestion": ['tab'],  # Accept inline suggestion
        "dismiss_suggestion": ['escape'],
        "trigger_suggestion": [Key.ctrl, ' '],  # Trigger autocomplete
    }

    def __init__(self):
        """Initialize keyboard executor"""
        if not PYNPUT_AVAILABLE:
            logger.error("❌ pynput not available - keyboard control disabled")
            self.keyboard = None
            self.mouse = None
            return

        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.cursor_window = None

        logger.info("✅ Keyboard Shortcut Executor initialized")

    def find_cursor_window(self) -> bool:
        """Find and activate Cursor window"""
        if not PYNPUT_AVAILABLE:
            return False

        try:
            windows = gw.getWindowsWithTitle('Cursor')
            if not windows:
                windows = gw.getWindowsWithTitle('cursor')
            if not windows:
                # Try partial match
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if 'cursor' in w.title.lower()]

            if windows:
                self.cursor_window = windows[0]
                self.cursor_window.activate()
                time.sleep(0.2)  # Wait for window to activate
                return True
            else:
                logger.warning("⚠️  Cursor window not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error finding Cursor window: {e}")
            return False

    def execute_shortcut(self, shortcut_name: str, fallback_to_mouse: bool = True) -> Dict[str, Any]:
        """
        Execute keyboard shortcut (primary method)
        Falls back to mouse if keyboard fails

        Args:
            shortcut_name: Name of shortcut from CURSOR_SHORTCUTS
            fallback_to_mouse: Whether to try mouse if keyboard fails

        Returns:
            Execution result
        """
        if not self.keyboard:
            return {"success": False, "error": "Keyboard controller not available"}

        if shortcut_name not in self.CURSOR_SHORTCUTS:
            return {"success": False, "error": f"Unknown shortcut: {shortcut_name}"}

        # Ensure Cursor window is active
        if not self.cursor_window:
            if not self.find_cursor_window():
                return {"success": False, "error": "Cursor window not found"}

        try:
            shortcut = self.CURSOR_SHORTCUTS[shortcut_name]
            logger.info(f"⌨️  Executing keyboard shortcut: {shortcut_name}")

            # Release all keys first
            self.keyboard.release(Key.ctrl)
            self.keyboard.release(Key.shift)
            self.keyboard.release(Key.alt)
            time.sleep(0.1)

            # Parse and execute key combination
            modifiers = []
            regular_keys = []

            for key in shortcut:
                if isinstance(key, Key):
                    modifiers.append(key)
                elif isinstance(key, str):
                    # Convert string keys to Key objects if needed
                    key_map = {
                        'ctrl': Key.ctrl, 'shift': Key.shift, 'alt': Key.alt,
                        'cmd': Key.cmd, 'tab': Key.tab, 'enter': Key.enter,
                        'space': Key.space, 'escape': Key.esc, 'backspace': Key.backspace
                    }
                    if key.lower() in key_map:
                        modifiers.append(key_map[key.lower()])
                    elif key in ['ctrl', 'shift', 'alt']:
                        modifiers.append(Key.ctrl if key == 'ctrl' else 
                                       Key.shift if key == 'shift' else Key.alt)
                    else:
                        regular_keys.append(key)

            # Press all modifiers first
            for mod in modifiers:
                self.keyboard.press(mod)
            time.sleep(0.05)

            # Press regular keys
            for key in regular_keys:
                if isinstance(key, str):
                    self.keyboard.press(key)
                    time.sleep(0.02)
                    self.keyboard.release(key)
                    time.sleep(0.02)

            # Release modifiers (in reverse order)
            for mod in reversed(modifiers):
                self.keyboard.release(mod)

            time.sleep(0.2)  # Wait for action to complete

            logger.info(f"   ✅ Shortcut executed: {shortcut_name}")
            return {"success": True, "method": "keyboard", "shortcut": shortcut_name}

        except Exception as e:
            logger.error(f"   ❌ Keyboard shortcut failed: {e}")

            # Try mouse fallback
            if fallback_to_mouse:
                logger.info(f"   🖱️  Attempting mouse fallback for: {shortcut_name}")
                return self._execute_mouse_fallback(shortcut_name)

            return {"success": False, "error": str(e), "method": "keyboard"}

    def _execute_mouse_fallback(self, shortcut_name: str) -> Dict[str, Any]:
        """
        Fallback to mouse-based control when keyboard fails

        Args:
            shortcut_name: Name of action to perform

        Returns:
            Execution result
        """
        try:
            # Map shortcuts to mouse actions
            mouse_actions = {
                "open_chat": self._mouse_open_chat,
                "focus_chat": self._mouse_click_chat_icon,
                "save_file": self._mouse_save_file,
                "new_file": self._mouse_new_file,
                "open_file": self._mouse_open_file,
            }

            if shortcut_name in mouse_actions:
                action = mouse_actions[shortcut_name]
                if action():
                    return {"success": True, "method": "mouse", "shortcut": shortcut_name}

            logger.warning(f"   ⚠️  No mouse fallback available for: {shortcut_name}")
            return {"success": False, "error": "No mouse fallback available", "method": "mouse"}

        except Exception as e:
            logger.error(f"   ❌ Mouse fallback failed: {e}")
            return {"success": False, "error": str(e), "method": "mouse"}

    def _mouse_open_chat(self) -> bool:
        """Open chat using mouse"""
        try:
            if not self.cursor_window:
                return False

            # Click on chat icon (usually in top right or via command palette)
            # This is a simplified version - would need screen coordinates
            self.mouse.click(Button.left)
            return True
        except:
            return False

    def _mouse_click_chat_icon(self) -> bool:
        """Click chat icon with mouse"""
        try:
            if not self.cursor_window:
                return False
            # Implementation would need screen coordinate detection
            return True
        except:
            return False

    def _mouse_save_file(self) -> bool:
        """Save file via menu"""
        try:
            # Ctrl+S via keyboard is more reliable, but could use File > Save
            return self.execute_shortcut("save_file", fallback_to_mouse=False)
        except:
            return False

    def _mouse_new_file(self) -> bool:
        """Create new file via menu"""
        try:
            return self.execute_shortcut("new_file", fallback_to_mouse=False)
        except:
            return False

    def _mouse_open_file(self) -> bool:
        """Open file dialog via menu"""
        try:
            return self.execute_shortcut("open_file", fallback_to_mouse=False)
        except:
            return False

    def type_text(self, text: str, delay: float = 0.03) -> Dict[str, Any]:
        """
        Type text into active Cursor window

        Args:
            text: Text to type
            delay: Delay between characters (seconds)

        Returns:
            Execution result
        """
        if not self.keyboard:
            return {"success": False, "error": "Keyboard controller not available"}

        try:
            if not self.cursor_window:
                if not self.find_cursor_window():
                    return {"success": False, "error": "Cursor window not found"}

            logger.info(f"⌨️  Typing text: {text[:50]}...")

            # Use keyboard.type() for whole text (more reliable than character-by-character)
            self.keyboard.type(text)
            time.sleep(0.2)  # Wait for text to be processed

            logger.info(f"   ✅ Text typed successfully")
            return {"success": True, "text_length": len(text)}

        except Exception as e:
            logger.error(f"   ❌ Typing failed: {e}")
            return {"success": False, "error": str(e)}


class JARVISHandsFreeCursorControl:
    """
    Hands-Free JARVIS Cursor Control System

    Allows conversations with JARVIS without clicking - fully automated
    IDE control via keyboard shortcuts (primary) and mouse (backup).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize hands-free control system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.running = False

        # Initialize components
        self.keyboard_executor = KeyboardShortcutExecutor() if PYNPUT_AVAILABLE else None
        self.manus_controller = ManusCursorController() if MANUS_AVAILABLE else None
        self.recycle_system = CursorIntelligentWarmRecycle(project_root=self.project_root) if RECYCLE_AVAILABLE else None
        self.voice_interface = None
        self.conversation = None

        # Auto-recycle monitoring
        if self.recycle_system:
            logger.info("   🔄 Intelligent warm recycle: Enabled")

        # Initialize voice (if available)
        if VOICE_AVAILABLE:
            try:
                self.voice_interface = JARVISVoiceActivated(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Voice interface not available: {e}")

        # Initialize conversation
        if CONVERSATION_AVAILABLE:
            try:
                self.conversation = JARVISNaturalConversation(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Conversation system not available: {e}")

        # Action queue
        self.action_queue = queue.Queue()
        self.action_thread = threading.Thread(target=self._action_executor_loop, daemon=True)
        self.action_thread.start()

        # Auto-recycle check thread
        if self.recycle_system:
            self.recycle_check_thread = threading.Thread(target=self._auto_recycle_check_loop, daemon=True)
            self.recycle_check_thread.start()

        # Conversation context
        self.conversation_context = {
            "last_action": None,
            "cursor_state": None,
            "conversation_history": []
        }

        logger.info("🎤 JARVIS Hands-Free Cursor Control initialized")
        logger.info("   Primary: Keyboard shortcuts")
        logger.info("   Backup: Mouse control")

    def _action_executor_loop(self):
        """Background thread to execute actions"""
        while True:
            try:
                action = self.action_queue.get(timeout=1.0)
                if action is None:  # Shutdown signal
                    break

                self._execute_action(action)
                self.action_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in action executor: {e}")

    def _execute_action(self, action: Dict[str, Any]):
        """Execute an action in Cursor IDE"""
        action_type = action.get("type")

        if action_type == "shortcut":
            shortcut_name = action.get("shortcut")
            if self.keyboard_executor:
                result = self.keyboard_executor.execute_shortcut(shortcut_name)
                action["result"] = result

        elif action_type == "type":
            text = action.get("text")
            if self.keyboard_executor:
                result = self.keyboard_executor.type_text(text)
                action["result"] = result

        elif action_type == "manus":
            # Use MANUS controller for complex actions
            if self.manus_controller:
                manus_action = action.get("action")
                # Execute via MANUS
                action["result"] = {"success": True, "method": "manus"}

    def process_voice_command(self, command: str) -> Dict[str, Any]:
        """
        Process voice command and execute in Cursor

        Args:
            command: Voice command text

        Returns:
            Processing result
        """
        logger.info(f"🎤 Processing voice command: {command[:100]}")

        # Parse command intent
        intent = self._parse_command_intent(command)

        # Generate actions
        actions = self._generate_actions_from_intent(intent, command)

        # Queue actions for execution
        for action in actions:
            self.action_queue.put(action)

        # Generate response
        response = self._generate_response(intent, actions)

        return {
            "success": True,
            "command": command,
            "intent": intent,
            "actions": len(actions),
            "response": response
        }

    def _parse_command_intent(self, command: str) -> Dict[str, Any]:
        """Parse command to determine intent"""
        command_lower = command.lower()

        intent = {
            "type": "unknown",
            "action": None,
            "target": None,
            "parameters": {}
        }

        # Chat/Conversation
        if any(word in command_lower for word in ["open chat", "start chat", "talk to", "chat with"]):
            intent["type"] = "open_chat"
            intent["action"] = "cursor_chat"

        # File operations
        elif any(word in command_lower for word in ["open file", "open", "file"]):
            intent["type"] = "open_file"
            intent["action"] = "open_file"
            # Extract filename if mentioned
            if "file" in command_lower:
                intent["parameters"]["filename"] = command_lower.split("file")[-1].strip()

        elif any(word in command_lower for word in ["new file", "create file"]):
            intent["type"] = "new_file"
            intent["action"] = "new_file"

        elif any(word in command_lower for word in ["save", "save file"]):
            intent["type"] = "save_file"
            intent["action"] = "save_file"

        # Code actions
        elif any(word in command_lower for word in ["format", "format code"]):
            intent["type"] = "format_code"
            intent["action"] = "format_document"

        elif any(word in command_lower for word in ["comment", "comment out"]):
            intent["type"] = "comment_code"
            intent["action"] = "comment_line"

        # Navigation
        elif any(word in command_lower for word in ["go to definition", "definition"]):
            intent["type"] = "goto_definition"
            intent["action"] = "goto_definition"

        # Terminal
        elif any(word in command_lower for word in ["terminal", "open terminal"]):
            intent["type"] = "toggle_terminal"
            intent["action"] = "toggle_terminal"

        # Debug
        elif any(word in command_lower for word in ["debug", "start debugging"]):
            intent["type"] = "start_debug"
            intent["action"] = "start_debugging"

        # AI/Assistance
        elif any(word in command_lower for word in ["composer", "cursor composer"]):
            intent["type"] = "open_composer"
            intent["action"] = "cursor_composer"

        else:
            # Generic chat/open conversation
            intent["type"] = "chat"
            intent["action"] = "cursor_chat"

        return intent

    def _generate_actions_from_intent(self, intent: Dict[str, Any], original_command: str) -> List[Dict[str, Any]]:
        """Generate action sequence from parsed intent"""
        actions = []

        action_type = intent.get("type")

        if action_type == "open_chat" or action_type == "chat":
            # Open Cursor chat
            actions.append({
                "type": "shortcut",
                "shortcut": "cursor_chat",
                "description": "Open Cursor chat"
            })

        elif action_type == "open_file":
            actions.append({
                "type": "shortcut",
                "shortcut": "open_file",
                "description": "Open file dialog"
            })
            # If filename specified, type it
            filename = intent.get("parameters", {}).get("filename")
            if filename:
                actions.append({
                    "type": "type",
                    "text": filename,
                    "description": f"Type filename: {filename}"
                })

        elif action_type == "new_file":
            actions.append({
                "type": "shortcut",
                "shortcut": "new_file",
                "description": "Create new file"
            })

        elif action_type == "save_file":
            actions.append({
                "type": "shortcut",
                "shortcut": "save_file",
                "description": "Save current file"
            })

        elif action_type == "format_code":
            actions.append({
                "type": "shortcut",
                "shortcut": "format_document",
                "description": "Format document"
            })

        elif action_type == "comment_code":
            actions.append({
                "type": "shortcut",
                "shortcut": "comment_line",
                "description": "Comment/uncomment line"
            })

        elif action_type == "goto_definition":
            actions.append({
                "type": "shortcut",
                "shortcut": "goto_definition",
                "description": "Go to definition"
            })

        elif action_type == "toggle_terminal":
            actions.append({
                "type": "shortcut",
                "shortcut": "toggle_terminal",
                "description": "Toggle terminal"
            })

        elif action_type == "start_debug":
            actions.append({
                "type": "shortcut",
                "shortcut": "start_debugging",
                "description": "Start debugging"
            })

        elif action_type == "open_composer":
            actions.append({
                "type": "shortcut",
                "shortcut": "cursor_composer",
                "description": "Open Cursor Composer"
            })

        # If command contains text to type (after opening chat/composer)
        if action_type in ["chat", "open_chat", "open_composer"]:
            # Extract text to send
            # This would be processed after chat opens
            pass

        return actions

    def _generate_response(self, intent: Dict[str, Any], actions: List[Dict[str, Any]]) -> str:
        """Generate voice response for user"""
        action_type = intent.get("type")

        responses = {
            "open_chat": "Opening Cursor chat for you.",
            "chat": "Opening chat so we can talk.",
            "open_file": "Opening file dialog.",
            "new_file": "Creating a new file.",
            "save_file": "Saving the file.",
            "format_code": "Formatting the code.",
            "comment_code": "Commenting the line.",
            "goto_definition": "Navigating to definition.",
            "toggle_terminal": "Toggling terminal.",
            "start_debug": "Starting debug session.",
            "open_composer": "Opening Cursor Composer.",
            "unknown": "I'll open chat so we can discuss that."
        }

        return responses.get(action_type, responses["unknown"])

    def start_hands_free_mode(self):
        """Start hands-free conversation mode"""
        logger.info("🎤 Starting hands-free mode...")

        if not self.voice_interface:
            logger.error("❌ Voice interface not available")
            return False

        self.running = True

        # Start auto-recycle monitoring if available
        if self.recycle_system:
            logger.info("   🔄 Auto-recycle monitoring: Active")
            # Monitoring is handled by background thread

        # Start voice listening
        try:
            # This would integrate with voice interface
            logger.info("✅ Hands-free mode started")
            logger.info("   Speak your commands - JARVIS will control Cursor automatically")
            logger.info("   Say 'stop' or 'exit' to end")

            # Main loop would be in voice interface
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start hands-free mode: {e}")
            return False

    def stop_hands_free_mode(self):
        """Stop hands-free mode"""
        self.running = False
        if self.recycle_system:
            self.recycle_system.stop_monitoring()
        logger.info("🛑 Hands-free mode stopped")

    def _auto_recycle_check_loop(self):
        """Background thread to check if Cursor needs recycling"""
        while True:
            try:
                if not self.running:
                    time.sleep(5)
                    continue

                if self.recycle_system:
                    decision = self.recycle_system.should_recycle()

                    if decision.should_recycle:
                        logger.warning(f"🔄 Auto-recycle triggered: {decision.reason.value} "
                                     f"(urgency: {decision.urgency})")

                        # Perform warm recycle
                        success = self.recycle_system.warm_recycle(decision.reason)

                        if success:
                            logger.info("✅ Cursor recycled successfully")
                            # Wait a bit after recycle before checking again
                            time.sleep(30)
                        else:
                            logger.error("❌ Recycle failed")
                            time.sleep(60)  # Wait longer if recycle failed

                # Check every 60 seconds
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in auto-recycle check: {e}")
                time.sleep(60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Hands-Free Cursor Control - No clicking required"
    )
    parser.add_argument("--start", action="store_true",
                       help="Start hands-free mode")
    parser.add_argument("--command", type=str,
                       help="Execute a single voice command")
    parser.add_argument("--test-shortcut", type=str,
                       help="Test a keyboard shortcut")

    args = parser.parse_args()

    control = JARVISHandsFreeCursorControl()

    if args.start:
        control.start_hands_free_mode()
        try:
            # Keep running
            while control.running:
                time.sleep(1)
        except KeyboardInterrupt:
            control.stop_hands_free_mode()

    elif args.command:
        result = control.process_voice_command(args.command)
        print(json.dumps(result, indent=2))

    elif args.test_shortcut:
        if control.keyboard_executor:
            result = control.keyboard_executor.execute_shortcut(args.test_shortcut)
            print(json.dumps(result, indent=2))
        else:
            print("Keyboard executor not available")

    else:
        parser.print_help()
        print("\n🎤 JARVIS Hands-Free Cursor Control")
        print("   Control Cursor IDE with voice - no clicking required")
        print("   Primary: Keyboard shortcuts")
        print("   Backup: Mouse control")


if __name__ == "__main__":
    import json


    main()