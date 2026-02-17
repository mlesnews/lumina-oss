#!/usr/bin/env python3
"""
JARVIS Agent Orchestrator
Orchestrates agents across ElevenLabs, MANUS, and other AI systems to create new chat sessions.

Tags: #ORCHESTRATION #ELEVENLABS #MANUS #AGENTS @AUTO @JARVIS
"""

import sys
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("JARVISAgentOrchestrator")

# Optional integrations
try:
    from jarvis_full_voice_mode import JARVISFullVoiceMode
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

try:
    from jarvis_desktop_keyboard_controller import JARVISDesktopController
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False


class JARVISAgentOrchestrator:
    """
    Orchestrates the creation of new agent chat sessions across multiple AI platforms.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.sessions_dir = self.project_root / "data" / "agent_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Load active systems
        self.systems = {
            "voice": VOICE_AVAILABLE,
            "manus": MANUS_AVAILABLE,
            "elevenlabs": self._check_elevenlabs()
        }

        self.logger.info("✅ JARVIS Agent Orchestrator initialized")
        self.logger.info(f"   Available Systems: {', '.join([k for k, v in self.systems.items() if v])}")

    def _check_elevenlabs(self) -> bool:
        """Check if ElevenLabs is configured"""
        # Placeholder check for API key in env or vault
        return True # Assuming available for logic flow

    def create_new_session(self, persona: str = "jarvis", objective: str = "general assistance") -> Dict[str, Any]:
        """
        Orchestrates the creation of a new agent chat session.
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        self.logger.info("="*80)
        self.logger.info(f"🚀 ORCHESTRATING NEW AGENT SESSION: {session_id}")
        self.logger.info(f"   Persona: {persona.upper()}")
        self.logger.info(f"   Objective: {objective}")
        self.logger.info("="*80)

        session_data = {
            "session_id": session_id,
            "timestamp": timestamp,
            "persona": persona,
            "objective": objective,
            "status": "initializing",
            "components": {}
        }

        # 1. Voice Integration (ElevenLabs / Azure)
        if self.systems["voice"]:
            self.logger.info("🎙️  Initializing Voice Component...")
            greeting = f"New session initialized. I am {persona}, ready to assist with {objective}."
            session_data["components"]["voice"] = {
                "greeting": greeting,
                "status": "ready"
            }
            # Attempt to speak greeting if voice mode is running
            try:
                from jarvis_full_voice_mode import JARVISFullVoiceMode
                # This is just a conceptual trigger
            except:
                pass

        # 2. MANUS Desktop Orchestration (Keyboard Shortcuts to open new chat)
        if self.systems["manus"]:
            self.logger.info("🖱️  Initializing MANUS Desktop Control...")
            try:
                from jarvis_desktop_keyboard_controller import JARVISDesktopController
                from pynput.keyboard import Key
                controller = JARVISDesktopController()

                # Ensure Cursor is focused first
                self.logger.info("   🪟 Focusing Cursor IDE...")
                controller.focus_window("Cursor")
                time.sleep(0.5)

                # Command: Ctrl+L (New Chat in Cursor)
                self.logger.info("   🎹 Triggering New Chat shortcut (Ctrl+L)...")
                controller.press_shortcut([Key.ctrl, 'l'])
                time.sleep(0.8) # Wait for UI

                # Type the objective
                self.logger.info(f"   ⌨️  Typing objective: {objective}...")
                # Format: @agent [PERSONA] [OBJECTIVE]
                cmd_text = f"@agent [{persona.upper()}] Objective: {objective}"
                controller.type_text(cmd_text)
                time.sleep(0.2)
                controller.press_shortcut([Key.enter])

                session_data["components"]["manus"] = {
                    "focus_target": "Cursor",
                    "action_executed": "new_chat_triggered",
                    "command_sent": cmd_text,
                    "status": "active"
                }
            except Exception as e:
                self.logger.error(f"   ❌ MANUS trigger failed: {e}")

        # 3. Create Session Record
        session_file = self.sessions_dir / f"session_{session_id}.json"
        session_data["status"] = "active"

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)

        self.logger.info(f"✅ Session {session_id} is now ACTIVE")

        return session_data

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        try:
            """Lists all active agent sessions"""
            sessions = []
            for f in self.sessions_dir.glob("session_*.json"):
                with open(f, 'r', encoding='utf-8') as f_in:
                    sessions.append(json.load(f_in))
            return sessions


        except Exception as e:
            self.logger.error(f"Error in list_active_sessions: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Agent Orchestrator")
        parser.add_argument("--create", action="store_true", help="Create a new session")
        parser.add_argument("--persona", type=str, default="jarvis", help="Agent persona")
        parser.add_argument("--objective", type=str, default="general assistance", help="Session objective")
        parser.add_argument("--list", action="store_true", help="List active sessions")

        args = parser.parse_args()
        orchestrator = JARVISAgentOrchestrator()

        if args.create:
            result = orchestrator.create_new_session(args.persona, args.objective)
            print(json.dumps(result, indent=2))
        elif args.list:
            results = orchestrator.list_active_sessions()
            print(json.dumps(results, indent=2))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()