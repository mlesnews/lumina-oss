#!/usr/bin/env python3
"""
JARVIS Full Hands-Free Voice Mode
Unified launcher for JARVIS hands-free voice interface.
Combines STT, TTS, and intent analysis for a complete voice experience.

Tags: #VOICE #HANDS-FREE #STT #TTS @AUTO @JARVIS
"""

import sys
import os
import signal
import time
import threading
from pathlib import Path
from typing import Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFullVoiceMode")

# Import Voice Components
try:
    from jarvis_voice_activation import JARVISVoiceActivation
    VOICE_SYSTEM_AVAILABLE = True
except ImportError as e:
    VOICE_SYSTEM_AVAILABLE = False
    logger.error(f"Voice system components not found: {e}")

# Import GUI component
try:
    from jarvis_ironman_bobblehead_gui import IronmanBobbleheadGUI
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class JARVISFullVoiceMode:
    """
    Unified manager for JARVIS hands-free voice mode.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.running = False
        self.gui = None

        if VOICE_SYSTEM_AVAILABLE:
            self.voice_activation = JARVISVoiceActivation(self.project_root)
        else:
            self.voice_activation = None

        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        """Handle exit signals"""
        self.logger.info("👋 Shutting down Full Voice Mode...")
        self.running = False
        if self.voice_activation:
            self.voice_activation.running = False
        if self.gui:
            try:
                self.gui.root.destroy()
            except:
                pass
        sys.exit(0)

    def _start_gui(self):
        """Start the bobblehead GUI in a separate thread"""
        if GUI_AVAILABLE:
            try:
                self.gui = IronmanBobbleheadGUI()
                self.gui.run()
            except Exception as e:
                self.logger.error(f"❌ GUI Error: {e}")

    def start(self):
        """Start full voice mode"""
        if not self.voice_activation:
            self.logger.error("❌ Cannot start voice mode: System not available")
            return

        self.logger.info("="*80)
        self.logger.info("🎙️  STARTING JARVIS FULL HANDS-FREE VOICE MODE")
        self.logger.info("="*80)
        self.logger.info("Commands:")
        self.logger.info("  - Just speak naturally to JARVIS")
        self.logger.info("  - Say 'exit' or 'goodbye' to stop")
        self.logger.info("="*80)

        # Start GUI in background thread
        if GUI_AVAILABLE:
            gui_thread = threading.Thread(target=self._start_gui, daemon=True)
            gui_thread.start()
            self.logger.info("🚀 Ironman Bobblehead GUI launched")

        self.running = True
        try:
            # The run_continuous method handles the loop
            self.voice_activation.run_continuous()
        except (KeyboardInterrupt, SystemExit, Exception) as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                self.logger.info("👋 Voice mode termination requested.")
            else:
                self.logger.error(f"❌ Voice mode error: {e}", exc_info=True)
        finally:
            self.running = False
            self.logger.info("🏁 Voice mode shutdown finalized.")


if __name__ == "__main__":
    mode = JARVISFullVoiceMode()
    mode.start()
