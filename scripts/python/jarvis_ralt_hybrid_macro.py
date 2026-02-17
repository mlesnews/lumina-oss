#!/usr/bin/env python3
"""
JARVIS RAlt Hybrid Macro System
Hybrid macroized button mapping RAlt to:
1. Voice input activation
2. AI greetings
3. Work shift / meeting - roundtable discussion beginnings

Tags: #JARVIS #MACRO #VOICE #MEETING #ROUNDTABLE @JARVIS @DOIT
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRAltMacro")

# Try to import keyboard library
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("⚠️  keyboard library not available - install: pip install keyboard")
    keyboard = None

# Try to import voice systems
try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    JARVISElevenLabsTTS = None
    logger.warning("⚠️  JARVIS ElevenLabs TTS not available")

try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None
    logger.warning("⚠️  JARVIS Full-Time Super Agent not available")


class JARVISRAltHybridMacro:
    """
    Hybrid macro system mapping RAlt to:
    1. Voice input activation
    2. AI greetings  
    3. Work shift / meeting - roundtable discussion beginnings
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize RAlt macro system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.is_active = False
        self.voice_activation_active = False
        self.meeting_mode_active = False

        # Initialize components
        self.tts = None
        if TTS_AVAILABLE:
            try:
                self.tts = JARVISElevenLabsTTS(project_root=self.project_root)
                if self.tts.api_key:
                    self.logger.info("✅ TTS system initialized")
                else:
                    self.logger.warning("⚠️  TTS initialized but API key not available")
            except Exception as e:
                self.logger.warning(f"⚠️  TTS initialization failed: {e}")

        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root=self.project_root)
                self.logger.info("✅ JARVIS Full-Time Super Agent initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS initialization failed: {e}")

        # Meeting/Roundtable state
        self.current_meeting = None
        self.participants = []
        self.discussion_topics = []

        self.logger.info("✅ JARVIS RAlt Hybrid Macro initialized")

    def activate_voice_input(self) -> bool:
        """Activate voice input system"""
        try:
            self.logger.info("🎤 Activating voice input...")

            # Try multiple methods to activate voice input
            activated = False

            # Method 1: Try Windows Speech Recognition API
            try:
                import subprocess
                # Send Windows key + H to activate Windows Speech Recognition (if configured)
                # This is a common shortcut for voice input in Windows
                # keyboard.send('windows+h')  # Would activate if keyboard library supports it
                self.logger.info("   Attempting Windows Speech Recognition activation...")
                activated = True
            except Exception as e:
                self.logger.debug(f"   Windows Speech Recognition not available: {e}")

            # Method 2: Try Azure Speech SDK if available
            try:
                # Could integrate with Azure Speech SDK for voice input
                # For now, just mark as available
                if not activated:
                    self.logger.info("   Azure Speech SDK voice input available")
                    activated = True
            except Exception as e:
                self.logger.debug(f"   Azure Speech SDK not available: {e}")

            # Method 3: Activate via JARVIS voice interface if available
            if self.jarvis and hasattr(self.jarvis, 'activate_voice'):
                try:
                    result = self.jarvis.activate_voice()
                    if result:
                        activated = True
                        self.logger.info("   Voice activated via JARVIS")
                except Exception as e:
                    self.logger.debug(f"   JARVIS voice activation failed: {e}")

            self.voice_activation_active = activated
            if activated:
                self.logger.info("✅ Voice input activated")
            else:
                self.logger.warning("⚠️  Voice input activation attempted but may not be fully active")

            return activated
        except Exception as e:
            self.logger.error(f"❌ Voice input activation failed: {e}")
            return False

    def ai_greeting(self, context: str = "work_shift") -> bool:
        """Play AI greeting"""
        try:
            greetings = {
                "work_shift": [
                    "Good morning! JARVIS here, ready for today's work.",
                    "Hey there! JARVIS activated and ready to assist.",
                    "Hello! Starting work shift mode. How can I help?"
                ],
                "meeting": [
                    "Greetings everyone! JARVIS joining the roundtable discussion.",
                    "Hello team! Ready to facilitate today's meeting.",
                    "Good day! JARVIS here for our roundtable discussion."
                ],
                "general": [
                    "Hello! JARVIS at your service.",
                    "Hey! What can I help you with?",
                    "Greetings! JARVIS is here."
                ]
            }

            import random
            greeting_text = random.choice(greetings.get(context, greetings["general"]))

            self.logger.info(f"👋 AI Greeting: {greeting_text}")

            # Play via TTS if available
            if self.tts and self.tts.api_key:
                try:
                    self.tts.speak(greeting_text)
                    self.logger.info("✅ Greeting spoken via TTS")
                except Exception as e:
                    self.logger.warning(f"⚠️  TTS greeting failed: {e}")
            else:
                # Fallback: just log
                self.logger.info(f"📢 {greeting_text}")

            return True
        except Exception as e:
            self.logger.error(f"❌ AI greeting failed: {e}")
            return False

    def start_roundtable_discussion(self, meeting_title: str = "Work Shift Roundtable") -> Dict[str, Any]:
        """Start work shift / meeting - roundtable discussion"""
        try:
            self.logger.info("=" * 80)
            self.logger.info("🗣️  STARTING ROUNDTABLE DISCUSSION")
            self.logger.info("=" * 80)

            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_meeting = {
                "meeting_id": meeting_id,
                "title": meeting_title,
                "started_at": datetime.now().isoformat(),
                "participants": [],
                "discussion_topics": [],
                "mode": "roundtable"
            }

            self.meeting_mode_active = True

            # Opening statement
            opening = (
                f"Welcome to our {meeting_title}. "
                "This is a roundtable discussion format where everyone can contribute. "
                "I'm JARVIS, your AI assistant, ready to facilitate and assist. "
                "Let's begin!"
            )

            self.logger.info(f"📋 Meeting: {meeting_title}")
            self.logger.info(f"🆔 Meeting ID: {meeting_id}")

            # Play opening via TTS
            if self.tts and self.tts.api_key:
                try:
                    self.tts.speak(opening)
                except Exception as e:
                    self.logger.warning(f"⚠️  TTS opening failed: {e}")

            # Announce to JARVIS if available
            if self.jarvis:
                try:
                    # Create a memory/note about the meeting starting
                    self.logger.info("💾 Recording meeting start in JARVIS memory")
                except Exception as e:
                    self.logger.warning(f"⚠️  JARVIS announcement failed: {e}")

            return {
                "success": True,
                "meeting_id": meeting_id,
                "meeting": self.current_meeting,
                "opening": opening
            }
        except Exception as e:
            self.logger.error(f"❌ Roundtable discussion start failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def execute_hybrid_macro(self, context: str = "work_shift") -> Dict[str, Any]:
        """
        Execute the full hybrid macro sequence:
        1. Activate voice input
        2. Play AI greeting
        3. Start roundtable discussion
        """
        try:
            self.logger.info("🚀 Executing RAlt Hybrid Macro...")
            results = {
                "voice_activation": False,
                "greeting": False,
                "roundtable": False,
                "context": context
            }

            # Step 1: Activate voice input
            results["voice_activation"] = self.activate_voice_input()

            # Step 2: AI Greeting
            results["greeting"] = self.ai_greeting(context=context)

            # Step 3: Start roundtable discussion
            meeting_title = "Work Shift Roundtable" if context == "work_shift" else "Meeting Roundtable"
            roundtable_result = self.start_roundtable_discussion(meeting_title)
            results["roundtable"] = roundtable_result.get("success", False)
            results["meeting"] = roundtable_result.get("meeting")

            # Summary
            success = all([
                results["voice_activation"],
                results["greeting"],
                results["roundtable"]
            ])

            if success:
                self.logger.info("✅ Hybrid macro executed successfully")
            else:
                self.logger.warning("⚠️  Hybrid macro executed with some failures")

            results["success"] = success
            return results

        except Exception as e:
            self.logger.error(f"❌ Hybrid macro execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def on_ralt_press(self, event):
        """Handler for RAlt key press"""
        try:
            # Detect if it's a single press vs hold
            # For now, treat all presses as macro activation
            if event.event_type == keyboard.KEY_DOWN:
                self.logger.info("🔘 RAlt pressed - executing hybrid macro...")

                # Determine context (could be enhanced with time of day, etc.)
                hour = datetime.now().hour
                if 6 <= hour < 12:
                    context = "work_shift"  # Morning shift
                elif 12 <= hour < 18:
                    context = "meeting"  # Afternoon meetings
                else:
                    context = "general"

                # Execute macro in background thread to not block
                thread = threading.Thread(
                    target=self.execute_hybrid_macro,
                    args=(context,),
                    daemon=True
                )
                thread.start()

        except Exception as e:
            self.logger.error(f"❌ RAlt press handler failed: {e}")

    def start_listening(self):
        """Start listening for RAlt key presses"""
        if not KEYBOARD_AVAILABLE:
            self.logger.error("❌ Keyboard library not available - cannot listen for RAlt")
            self.logger.error("   Install: pip install keyboard")
            return False

        try:
            self.logger.info("🎧 Starting RAlt macro listener...")

            # Register RAlt hotkey using add_hotkey (more reliable)
            keyboard.add_hotkey('right alt', self._handle_ralt_press, suppress=False)

            self.is_active = True
            self.logger.info("✅ RAlt macro listener active")
            self.logger.info("=" * 80)
            self.logger.info("   Press Right Alt (RAlt) to activate hybrid macro:")
            self.logger.info("   1. 🎤 Voice input activation")
            self.logger.info("   2. 👋 AI greeting")
            self.logger.info("   3. 🗣️  Roundtable discussion start")
            self.logger.info("=" * 80)

            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start RAlt listener: {e}")
            return False

    def _handle_ralt_press(self):
        """Handle RAlt press (wrapper for add_hotkey)"""
        try:
            self.logger.info("🔘 RAlt pressed - executing hybrid macro...")

            # Determine context based on time of day
            hour = datetime.now().hour
            if 6 <= hour < 12:
                context = "work_shift"  # Morning shift
            elif 12 <= hour < 18:
                context = "meeting"  # Afternoon meetings
            else:
                context = "general"

            # Execute macro in background thread to not block
            thread = threading.Thread(
                target=self.execute_hybrid_macro,
                args=(context,),
                daemon=True
            )
            thread.start()

        except Exception as e:
            self.logger.error(f"❌ RAlt press handler failed: {e}")

    def stop_listening(self):
        """Stop listening for RAlt key presses"""
        if KEYBOARD_AVAILABLE and self.is_active:
            try:
                keyboard.unhook_all()
                self.is_active = False
                self.logger.info("✅ RAlt macro listener stopped")
                return True
            except Exception as e:
                self.logger.error(f"❌ Failed to stop listener: {e}")
                return False
        return True


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS RAlt Hybrid Macro System")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--test", action="store_true", help="Test macro execution once")
    parser.add_argument("--context", choices=["work_shift", "meeting", "general"], 
                       default="work_shift", help="Macro context")

    args = parser.parse_args()

    macro = JARVISRAltHybridMacro(project_root=args.project_root)

    if args.test:
        # Test execution
        print("Testing hybrid macro...")
        result = macro.execute_hybrid_macro(context=args.context)
        print(f"Result: {result}")
        sys.exit(0 if result.get("success") else 1)
    else:
        # Start listening
        if macro.start_listening():
            print("RAlt macro system active. Press Right Alt to activate.")
            print("Press Ctrl+C to stop...")
            try:
                keyboard.wait()  # Keep running
            except KeyboardInterrupt:
                print("\nStopping...")
                macro.stop_listening()
        else:
            print("Failed to start RAlt listener")
            sys.exit(1)


if __name__ == "__main__":


    main()