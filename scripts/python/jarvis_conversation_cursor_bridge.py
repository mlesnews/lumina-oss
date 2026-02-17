#!/usr/bin/env python3
"""
JARVIS Conversation-Cursor Bridge

Hands-free conversation with JARVIS that automatically controls Cursor IDE.
No clicking required - voice commands are processed and executed via keyboard shortcuts.

Usage:
    python jarvis_conversation_cursor_bridge.py --start
"""

import sys
import time
import signal
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISConversationCursorBridge")

# Import components
try:
    from jarvis_hands_free_cursor_control import JARVISHandsFreeCursorControl
    HANDS_FREE_AVAILABLE = True
except ImportError as e:
    HANDS_FREE_AVAILABLE = False
    logger.error(f"Hands-free control not available: {e}")

try:
    from jarvis_voice_activated import JARVISVoiceActivated
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Voice interface not available")


class JARVISConversationCursorBridge:
    """
    Bridge between JARVIS voice conversations and Cursor IDE control

    Listens to voice input → Processes through JARVIS → Executes in Cursor via keyboard shortcuts
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the bridge"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.running = False

        # Initialize hands-free control
        if HANDS_FREE_AVAILABLE:
            self.hands_free = JARVISHandsFreeCursorControl(project_root=self.project_root)
        else:
            self.hands_free = None
            logger.error("❌ Hands-free control not available")

        # Initialize voice interface
        self.voice_interface = None
        if VOICE_AVAILABLE:
            try:
                self.voice_interface = JARVISVoiceActivated(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Voice interface initialization failed: {e}")

        # Conversation state
        self.conversation_active = False
        self.last_command = None

        logger.info("🌉 JARVIS Conversation-Cursor Bridge initialized")
        logger.info("   Voice → JARVIS → Cursor IDE (Keyboard shortcuts)")

    def process_voice_to_cursor(self, voice_input: str) -> Dict[str, Any]:
        """
        Process voice input and execute in Cursor

        Args:
            voice_input: Voice command text

        Returns:
            Processing result
        """
        logger.info(f"🎤 Voice command received: {voice_input[:100]}")

        if not self.hands_free:
            return {
                "success": False,
                "error": "Hands-free control not available"
            }

        # Process command through hands-free system
        result = self.hands_free.process_voice_command(voice_input)

        self.last_command = voice_input
        return result

    def start_conversation_mode(self):
        """Start continuous conversation mode"""
        logger.info("🎤 Starting hands-free conversation mode...")

        if not self.voice_interface:
            logger.error("❌ Voice interface not available")
            logger.info("   💡 Install voice dependencies or use --command for text input")
            return False

        if not self.hands_free:
            logger.error("❌ Hands-free control not available")
            return False

        self.running = True
        self.conversation_active = True

        logger.info("✅ Conversation mode started")
        logger.info("   🎤 Speak your commands - JARVIS will control Cursor automatically")
        logger.info("   ⌨️  Primary: Keyboard shortcuts")
        logger.info("   🖱️  Backup: Mouse control")
        logger.info("   🛑 Say 'stop' or 'exit' to end")

        try:
            # Integration with voice interface
            # This would hook into the voice interface's listen loop
            # For now, this is a placeholder for the integration

            # Keep running until stopped
            while self.running:
                # In a real implementation, this would wait for voice input
                # from the voice interface and process it
                time.sleep(0.5)

        except KeyboardInterrupt:
            self.stop_conversation_mode()

        return True

    def stop_conversation_mode(self):
        """Stop conversation mode"""
        self.running = False
        self.conversation_active = False
        logger.info("🛑 Conversation mode stopped")

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a single command"""
        return self.process_voice_to_cursor(command)


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Shutdown signal received")
    if hasattr(signal_handler, 'bridge'):
        signal_handler.bridge.stop_conversation_mode()
    sys.exit(0)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="JARVIS Conversation-Cursor Bridge - Hands-free IDE control"
        )
        parser.add_argument("--start", action="store_true",
                           help="Start hands-free conversation mode")
        parser.add_argument("--command", type=str,
                           help="Execute a single voice command (text input)")
        parser.add_argument("--test", action="store_true",
                           help="Test keyboard shortcut execution")

        args = parser.parse_args()

        # Create bridge
        bridge = JARVISConversationCursorBridge()
        signal_handler.bridge = bridge
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        if args.start:
            bridge.start_conversation_mode()

        elif args.command:
            import json
            result = bridge.execute_command(args.command)
            print(json.dumps(result, indent=2))

            # Generate voice response if available
            if result.get("success") and result.get("response"):
                response = result.get("response")
                print(f"\n🎤 JARVIS Response: {response}")

        elif args.test:
            if bridge.hands_free and bridge.hands_free.keyboard_executor:
                # Test opening chat
                print("🧪 Testing keyboard shortcuts...")
                result = bridge.hands_free.keyboard_executor.execute_shortcut("cursor_chat")
                print(json.dumps(result, indent=2))

                time.sleep(1)

                # Test typing
                print("\n🧪 Testing text input...")
                result = bridge.hands_free.keyboard_executor.type_text("Hello from JARVIS!")
                print(json.dumps(result, indent=2))
            else:
                print("❌ Keyboard executor not available")

        else:
            parser.print_help()
            print("\n" + "="*70)
            print("🎤 JARVIS Conversation-Cursor Bridge")
            print("="*70)
            print()
            print("Hands-free conversation with JARVIS that controls Cursor IDE")
            print("automatically via keyboard shortcuts (mouse as backup).")
            print()
            print("Examples:")
            print("  python jarvis_conversation_cursor_bridge.py --start")
            print("    Start continuous conversation mode")
            print()
            print("  python jarvis_conversation_cursor_bridge.py --command 'open chat'")
            print("    Execute a single command")
            print()
            print("  python jarvis_conversation_cursor_bridge.py --test")
            print("    Test keyboard shortcut execution")
            print()
            print("Available Commands:")
            print("  - 'open chat' / 'start chat' → Open Cursor chat")
            print("  - 'open file' → Open file dialog")
            print("  - 'new file' → Create new file")
            print("  - 'save file' → Save current file")
            print("  - 'format code' → Format document")
            print("  - 'toggle terminal' → Open/close terminal")
            print("  - 'go to definition' → Navigate to definition")
            print("  - 'start debug' → Start debugging session")
            print("  - 'open composer' → Open Cursor Composer")
            print()
            print("="*70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import json


    main()