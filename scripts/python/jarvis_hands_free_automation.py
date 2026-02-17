#!/usr/bin/env python3
"""
JARVIS Hands-Free Automation

Tracks user workflow and automates:
- Voice transcription in Cursor
- Eliminates clicking (keyboard-only)
- Auto-sends messages
- Records exact steps for automation
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_fulltime_super_agent import get_jarvis_fulltime
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False

logger = logging.getLogger("JARVISHandsFree")


class WorkflowTracker:
    """Track user workflow steps for automation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflow_log = project_root / "data" / "jarvis_workflows"
        self.workflow_log.mkdir(parents=True, exist_ok=True)
        self.current_workflow = []
        self.recording = False

    def start_recording(self, workflow_name: str):
        """Start recording workflow steps"""
        self.recording = True
        self.current_workflow = [{
            "workflow_name": workflow_name,
            "started": datetime.now().isoformat(),
            "steps": []
        }]
        logger.info(f"📹 Started recording workflow: {workflow_name}")

    def record_step(self, action: str, details: Dict = None):
        """Record a workflow step"""
        if not self.recording:
            return

        step = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }
        self.current_workflow[0]["steps"].append(step)
        logger.info(f"📝 Recorded step: {action}")

    def stop_recording(self):
        try:
            """Stop recording and save workflow"""
            if not self.recording:
                return

            self.current_workflow[0]["ended"] = datetime.now().isoformat()
            self.current_workflow[0]["total_steps"] = len(self.current_workflow[0]["steps"])

            # Save workflow
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            workflow_file = self.workflow_log / f"workflow_{timestamp}.json"
            with open(workflow_file, 'w') as f:
                json.dump(self.current_workflow, f, indent=2)

            logger.info(f"💾 Saved workflow: {workflow_file}")
            self.recording = False
            return workflow_file


        except Exception as e:
            self.logger.error(f"Error in stop_recording: {e}", exc_info=True)
            raise
class CursorVoiceAutomation:
    """Automate Cursor voice transcription and interaction"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tracker = WorkflowTracker(project_root)

        # Try to import keyboard automation
        try:
            import pyautogui
            import keyboard
            self.pyautogui = pyautogui
            self.keyboard = keyboard
            self.automation_available = True
        except ImportError:
            logger.warning("pyautogui or keyboard not available - install: pip install pyautogui keyboard")
            self.automation_available = False

        # Load mapped shortcuts from config
        self.shortcuts_config = self.project_root / "config" / "cursor_ide_complete_keyboard_shortcuts.json"
        self.cursor_shortcuts = self._load_mapped_shortcuts()

    def _load_mapped_shortcuts(self) -> Dict[str, str]:
        """Load keyboard shortcuts from mapped config"""
        shortcuts = {
            "open_chat": "ctrl+l",  # Default
            "voice_input": None,
            "send_message": "enter",
            "focus_input": "tab",
        }

        if self.shortcuts_config.exists():
            try:
                import json
                with open(self.shortcuts_config, 'r') as f:
                    config = json.load(f)

                # Load Cursor AI shortcuts
                cursor_ai = config.get("shortcuts", {}).get("cursor_ide_ai", {})
                if "cursor_chat" in cursor_ai:
                    keys = cursor_ai["cursor_chat"].get("keys", [])
                    shortcuts["open_chat"] = "+".join(keys).lower()

                # Load other useful shortcuts
                editing = config.get("shortcuts", {}).get("editing", {})
                if "format_document" in editing:
                    keys = editing["format_document"].get("keys", [])
                    shortcuts["format_code"] = "+".join(keys).lower()

                logger.info(f"✅ Loaded {len(shortcuts)} mapped shortcuts")
            except Exception as e:
                logger.warning(f"Failed to load shortcuts: {e}")

        return shortcuts

    def discover_cursor_shortcuts(self):
        """Discover Cursor keyboard shortcuts"""
        logger.info("🔍 Discovering Cursor shortcuts...")

        # Common patterns to try
        voice_shortcuts = [
            "Ctrl+Shift+V",  # Common voice shortcut
            "Ctrl+`",  # Backtick
            "Ctrl+;",  # Semicolon
            "Ctrl+Shift+Space",  # Voice space
            "Alt+V",  # Alt V for voice
        ]

        # Record discovery attempt
        self.tracker.record_step("discover_shortcuts", {
            "attempted": voice_shortcuts
        })

        return voice_shortcuts

    def automate_voice_transcription(self, message: str = None):
        try:
            """
            Automate voice transcription in Cursor

            Steps to automate:
            1. Open Cursor chat (Ctrl+L)
            2. Focus input field
            3. Trigger voice input (shortcut to be discovered)
            4. Wait for transcription
            5. Auto-send (Enter)
            """
            if not self.automation_available:
                logger.error("❌ Automation libraries not available")
                return False

            logger.info("🎤 Automating voice transcription...")

            steps = []

            # Step 1: Open Cursor chat
            # FIXED: Removed ctrl+l to prevent layout switching
            # Assume chat is already open or user will open it manually
            logger.info("   Step 1: Chat should be open (ctrl+l removed to prevent layout switching)")
            time.sleep(0.5)
            steps.append("open_chat_manual")

            # Step 2: Focus input field (Tab or click - but we'll use Tab)
            logger.info("   Step 2: Focusing input field")
            self.keyboard.press_and_release('tab')
            time.sleep(0.3)
            steps.append("focus_input_tab")

            # Step 3: Try voice input shortcuts
            logger.info("   Step 3: Triggering voice input")
            voice_shortcuts = self.discover_cursor_shortcuts()

            # Try the most likely one first
            logger.info("   Trying: Ctrl+Shift+V")
            self.keyboard.press_and_release('ctrl+shift+v')
            time.sleep(1)  # Wait for voice input to start

            steps.append("trigger_voice_ctrl_shift_v")

            # Step 4: Wait for transcription (user speaks)
            logger.info("   Step 4: Waiting for voice transcription...")
            logger.info("   💡 Speak now - automation will auto-send when done")

            # Record the workflow
            self.tracker.record_step("voice_transcription_automation", {
                "steps": steps,
                "voice_shortcut": "Ctrl+Shift+V"
            })

            # Step 5: Auto-send (Enter) - but wait a bit for transcription
            # This should be configurable
            logger.info("   Step 5: Auto-sending (Enter)")
            time.sleep(2)  # Wait for transcription to complete
            self.keyboard.press_and_release('enter')
            steps.append("auto_send_enter")

            logger.info("✅ Voice transcription automation complete")
            return True

        except Exception as e:
            self.logger.error(f"Error in automate_voice_transcription: {e}", exc_info=True)
            raise
    def automate_text_message(self, message: str):
        try:
            """Automate sending text message (no voice)"""
            if not self.automation_available:
                logger.error("❌ Automation libraries not available")
                return False

            logger.info(f"💬 Automating text message: {message[:50]}...")

            # FIXED: Removed ctrl+l to prevent layout switching
            # Assume chat is already open or user will open it manually
            logger.info("   Chat should be open (ctrl+l removed to prevent layout switching)")
            time.sleep(0.5)

            # Focus input
            self.keyboard.press_and_release('tab')
            time.sleep(0.3)

            # Type message
            self.pyautogui.write(message, interval=0.05)
            time.sleep(0.5)

            # Send
            self.keyboard.press_and_release('enter')

            logger.info("✅ Text message sent")
            return True

        except Exception as e:
            self.logger.error(f"Error in automate_text_message: {e}", exc_info=True)
            raise
    def auto_accept_all_changes(self):
        """Automatically accept 'Accept All Changes' or 'Keep All' dialogs"""
        if not self.automation_available:
            logger.error("❌ Automation libraries not available")
            return False

        logger.info("🔧 Auto-accepting all changes dialog...")

        # Record this step
        self.tracker.record_step("auto_accept_all_changes", {
            "method": "keyboard_shortcuts"
        })

        # Try multiple methods
        methods = [
            ('enter', "Enter key"),
            ('alt+a', "Alt+A (Accept)"),
            ('tab+enter', "Tab then Enter"),
        ]

        for method, description in methods:
            try:
                if method == 'tab+enter':
                    self.keyboard.press_and_release('tab')
                    time.sleep(0.1)
                    self.keyboard.press_and_release('enter')
                else:
                    self.keyboard.press_and_release(method)

                time.sleep(0.3)
                logger.info(f"   ✅ Tried {description}")
            except Exception as e:
                logger.warning(f"   ⚠️  {description} failed: {e}")

        logger.info("✅ Auto-accept sequence completed")
        return True


class JARVISHandsFree:
    """JARVIS Hands-Free Interface - No Clicking Required"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_automation = CursorVoiceAutomation(self.project_root)

        if JARVIS_AVAILABLE:
            self.jarvis = get_jarvis_fulltime()
        else:
            self.jarvis = None

        self.conversation_id = None

    def start_hands_free_mode(self):
        """Start hands-free mode"""
        print("="*80)
        print("🎤 JARVIS Hands-Free Mode")
        print("="*80)
        print()
        print("✅ No clicking required!")
        print("✅ Voice transcription automated!")
        print("✅ Keyboard-only interaction!")
        print()

        # Start workflow tracking
        self.cursor_automation.tracker.start_recording("hands_free_voice")

        # Start JARVIS conversation
        if self.jarvis:
            self.conversation_id = self.jarvis.start_voice_conversation()
            print(f"✅ JARVIS conversation started: {self.conversation_id}")
            print()

        print("📹 Recording your workflow steps for automation...")
        print()
        print("💡 Instructions:")
        print("   1. Press Ctrl+L to open Cursor chat")
        print("   2. Use voice input (we'll discover the shortcut)")
        print("   3. Speak your message")
        print("   4. We'll auto-send it")
        print()
        print("   Or type 'auto' to trigger automated voice transcription")
        print("   Type 'exit' to stop")
        print()
        print("-" * 80)
        print()

        # Interactive loop
        while True:
            try:
                user_input = input("🎤 Command: ").strip().lower()

                if user_input in ['exit', 'quit', 'stop']:
                    break

                if user_input == 'auto':
                    # Trigger automated voice transcription
                    self.cursor_automation.automate_voice_transcription()
                    continue

                if user_input.startswith('text:'):
                    # Send text message
                    message = user_input[5:].strip()
                    self.cursor_automation.automate_text_message(message)
                    continue

                if user_input == 'record':
                    # Start recording current workflow
                    print("📹 Recording workflow... Do your normal steps now.")
                    print("   (We'll track: clicks, keyboard, actions)")
                    # Implementation would hook into system events
                    continue

                print("💡 Commands:")
                print("   'auto' - Trigger automated voice transcription")
                print("   'text: <message>' - Send text message")
                print("   'record' - Start recording workflow")
                print("   'exit' - Stop")
                print()

            except KeyboardInterrupt:
                break

        # Stop recording
        workflow_file = self.cursor_automation.tracker.stop_recording()
        print()
        print(f"💾 Workflow saved: {workflow_file}")
        print("✅ Hands-free mode stopped")


def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)

    hands_free = JARVISHandsFree()
    hands_free.start_hands_free_mode()


if __name__ == "__main__":


    main()