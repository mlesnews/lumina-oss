#!/usr/bin/env python3
"""
Iron Man Assistant Manager - Singleton Pattern

Ensures only ONE Iron Man-type assistant (JARVIS, Ultron, Ultimate Iron Man, Mark V)
is active at a time. Manages process lifecycle and prevents conflicts.

Tags: #IRON_MAN #SINGLETON #PROCESS_MANAGEMENT @JARVIS @LUMINA
"""

import sys
import os
import json
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

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

logger = get_logger("IronManAssistantManager")


class IronManAssistantManager:
    """
    Iron Man Assistant Manager - Singleton Pattern

    Only ONE Iron Man-type assistant can be active at a time:
    - JARVIS
    - Ultron
    - Ultimate Iron Man
    - Mark V (Suitcase Suit)

    Prevents multiple instances from conflicting.
    """

    _instance = None
    _lock_file = None

    def __new__(cls, project_root: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super(IronManAssistantManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.lock_file = self.project_root / "data" / "iron_man_assistant.lock"
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)

        # Current active assistant
        self.active_assistant: Optional[str] = None
        self.active_pid: Optional[int] = None

        # Magic words requirement - "Jarvis Iron Legion"
        self.magic_words = "jarvis iron legion"
        self.magic_words_activated = False  # Must say magic words to activate

        # Activation phrase detection
        self.activation_phrase_file = self.project_root / "data" / "iron_man_activation_phrase.txt"
        self._check_activation_phrase()

        # Load state
        self._load_state()

        logger.info("=" * 80)
        logger.info("🦾 IRON MAN ASSISTANT MANAGER (Singleton)")
        logger.info("=" * 80)
        logger.info("   Rule: Only ONE Iron Man-type assistant active at a time")
        logger.info(f"   Magic Words: '{self.magic_words}' (required for activation)")
        logger.info(f"   Magic Words Activated: {self.magic_words_activated}")
        logger.info(f"   Active: {self.active_assistant or 'None'}")
        logger.info(f"   PID: {self.active_pid or 'None'}")
        logger.info("=" * 80)

    def _load_state(self):
        """Load current state from lock file"""
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_assistant = data.get("assistant")
                    self.active_pid = data.get("pid")

                    # Verify process is still running
                    if self.active_pid:
                        if not psutil.pid_exists(self.active_pid):
                            logger.info(f"   Process {self.active_pid} no longer exists - clearing state")
                            self.active_assistant = None
                            self.active_pid = None
                            self._save_state()
            except Exception as e:
                logger.warning(f"⚠️  Error loading state: {e}")
                self.active_assistant = None
                self.active_pid = None

    def _save_state(self):
        """Save current state to lock file"""
        try:
            data = {
                "assistant": self.active_assistant,
                "pid": self.active_pid,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.lock_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")

    def _check_activation_phrase(self):
        """Check if magic words activation phrase has been detected"""
        # Check activation phrase file (set by voice recognition or command)
        if self.activation_phrase_file.exists():
            try:
                with open(self.activation_phrase_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip().lower()
                    if self.magic_words.lower() in content:
                        self.magic_words_activated = True
                        logger.info(f"✅ Magic words detected: '{self.magic_words}'")
                        # Clear the file after reading
                        self.activation_phrase_file.unlink()
                        return True
            except Exception as e:
                logger.debug(f"Could not check activation phrase: {e}")

        # Also check for phrase in recent voice input (if available)
        # This would integrate with voice recognition systems
        return False

    def check_magic_words(self, text: str) -> bool:
        """
        Check if text contains magic words "Jarvis Iron Legion"

        Args:
            text: Text to check

        Returns:
            True if magic words detected
        """
        text_lower = text.lower().strip()
        magic_lower = self.magic_words.lower()

        # Check if magic words are in the text
        if magic_lower in text_lower:
            self.magic_words_activated = True
            logger.info(f"✅ Magic words detected in text: '{self.magic_words}'")
            return True

        return False

    def can_activate(self, assistant_name: str, bypass_magic_words: bool = False) -> tuple[bool, str]:
        """
        Check if an assistant can be activated

        Args:
            assistant_name: Name of assistant
            bypass_magic_words: If True, skip magic words check (for testing)

        Returns: (can_activate, reason)
        """
        # CRITICAL: Check magic words first (unless bypassed)
        if not bypass_magic_words:
            # Re-check activation phrase
            self._check_activation_phrase()

            if not self.magic_words_activated:
                return (False, f"Magic words '{self.magic_words}' not detected. Say 'Jarvis Iron Legion' to activate.")

        # If no assistant is active, can activate
        if not self.active_assistant:
            return (True, "No assistant currently active")

        # If same assistant is already active, can't activate again
        if self.active_assistant == assistant_name:
            return (False, f"{assistant_name} is already active")

        # If different assistant is active, must deactivate first
        return (False, f"{self.active_assistant} is currently active. Deactivate first.")

    def activate(self, assistant_name: str, process_id: int, bypass_magic_words: bool = False) -> bool:
        """
        Activate an assistant (deactivates any existing one)

        Args:
            assistant_name: Name of assistant (jarvis, ultron, ultimate, mark_v)
            process_id: Process ID of the assistant
            bypass_magic_words: If True, skip magic words check (for testing)
        """
        # Check if we can activate (includes magic words check)
        can_activate, reason = self.can_activate(assistant_name, bypass_magic_words=bypass_magic_words)

        if not can_activate:
            logger.warning(f"⚠️  Cannot activate {assistant_name}: {reason}")
            return False

        # If different assistant is active, deactivate it first
        if self.active_assistant and self.active_assistant != assistant_name:
            logger.info(f"🔄 Deactivating {self.active_assistant} to activate {assistant_name}")
            self.deactivate()

        # Activate new assistant
        self.active_assistant = assistant_name
        self.active_pid = process_id
        self._save_state()

        logger.info(f"✅ Activated {assistant_name} (PID: {process_id})")
        return True

    def deactivate(self):
        """Deactivate current assistant"""
        if self.active_assistant and self.active_pid:
            # Try to terminate process
            try:
                if psutil.pid_exists(self.active_pid):
                    process = psutil.Process(self.active_pid)
                    process.terminate()
                    logger.info(f"🛑 Terminated {self.active_assistant} (PID: {self.active_pid})")
            except Exception as e:
                logger.warning(f"⚠️  Error terminating process: {e}")

        self.active_assistant = None
        self.active_pid = None
        self._save_state()

        logger.info("✅ Deactivated assistant")

    def get_active_assistant(self) -> Optional[str]:
        """Get currently active assistant name"""
        return self.active_assistant

    def is_active(self, assistant_name: str) -> bool:
        """Check if specific assistant is active"""
        return self.active_assistant == assistant_name


def main():
    """Main entry point for testing"""
    manager = IronManAssistantManager()
    print(f"Active assistant: {manager.get_active_assistant()}")
    print(f"Can activate JARVIS: {manager.can_activate('jarvis')}")
    print(f"Can activate Ultron: {manager.can_activate('ultron')}")


if __name__ == "__main__":


    main()