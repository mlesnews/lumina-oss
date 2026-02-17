#!/usr/bin/env python3
"""
MANUS Chained Ask Cycle Controller

Orchestrates continuous conversation loops with JARVIS:
  Listen → Transcribe → Process → Execute → Respond → Loop

No manual triggers needed - continuous intelligent conversation.
MANUS controls the entire cycle automatically.
"""

import sys
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MANUSChainedAskCycle")

# Import components
try:
    from jarvis_always_listening import JARVISAlwaysListening
    ALWAYS_LISTENING_AVAILABLE = True
except ImportError:
    ALWAYS_LISTENING_AVAILABLE = False
    logger.warning("Always-listening not available")

try:
    from jarvis_hands_free_cursor_control import JARVISHandsFreeCursorControl
    HANDS_FREE_AVAILABLE = True
except ImportError:
    HANDS_FREE_AVAILABLE = False
    logger.warning("Hands-free control not available")

try:
    from cursor_intelligent_warm_recycle import CursorIntelligentWarmRecycle
    RECYCLE_AVAILABLE = True
except ImportError:
    RECYCLE_AVAILABLE = False
    logger.warning("Warm recycle not available")


class CycleState(Enum):
    """State of the ask cycle"""
    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    EXECUTING = "executing"
    RESPONDING = "responding"
    WAITING = "waiting"


@dataclass
class AskCycleEvent:
    """An event in the ask cycle"""
    cycle_id: int
    state: CycleState
    timestamp: datetime
    input_text: Optional[str] = None
    output_text: Optional[str] = None
    action_taken: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MANUSChainedAskCycle:
    """
    MANUS Chained Ask Cycle Controller

    Orchestrates continuous conversation loops:
    - Always-listening microphone
    - Real-time transcription
    - Intelligent command processing
    - Automatic Cursor IDE control
    - Voice responses
    - Seamless loop continuation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize chained ask cycle controller"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # State
        self.running = False
        self.current_state = CycleState.IDLE
        self.cycle_count = 0

        # Event history
        self.cycle_history: List[AskCycleEvent] = []

        # Initialize components
        self.always_listening: Optional[JARVISAlwaysListening] = None
        self.hands_free: Optional[JARVISHandsFreeCursorControl] = None
        self.recycle_system: Optional[CursorIntelligentWarmRecycle] = None

        self._initialize_components()

        # Configuration
        self.config = {
            "auto_recycle_check_interval": 120,  # seconds
            "response_delay": 0.5,  # seconds between response and next listen
            "max_silence_before_prompt": 30,  # seconds of silence before prompting
            "enable_proactive_suggestions": True,
        }

        logger.info("🔄 MANUS Chained Ask Cycle Controller initialized")
        logger.info("   Cycle: Listen → Transcribe → Process → Execute → Respond → Loop")

    def _initialize_components(self):
        """Initialize all components"""
        # Always-listening microphone
        if ALWAYS_LISTENING_AVAILABLE:
            try:
                self.always_listening = JARVISAlwaysListening(project_root=self.project_root)
                logger.info("   ✅ Always-listening microphone: Ready")
            except Exception as e:
                logger.error(f"   ❌ Always-listening: {e}")

        # Hands-free Cursor control
        if HANDS_FREE_AVAILABLE:
            try:
                self.hands_free = JARVISHandsFreeCursorControl(project_root=self.project_root)
                logger.info("   ✅ Hands-free Cursor control: Ready")
            except Exception as e:
                logger.error(f"   ❌ Hands-free control: {e}")

        # Intelligent warm recycle
        if RECYCLE_AVAILABLE:
            try:
                self.recycle_system = CursorIntelligentWarmRecycle(project_root=self.project_root)
                logger.info("   ✅ Intelligent warm recycle: Ready")
            except Exception as e:
                logger.error(f"   ❌ Warm recycle: {e}")

    def _log_cycle_event(self, state: CycleState, input_text: str = None, 
                         output_text: str = None, action_taken: str = None,
                         duration_ms: float = 0.0):
        """Log a cycle event"""
        event = AskCycleEvent(
            cycle_id=self.cycle_count,
            state=state,
            timestamp=datetime.now(),
            input_text=input_text,
            output_text=output_text,
            action_taken=action_taken,
            duration_ms=duration_ms
        )
        self.cycle_history.append(event)

        # Keep only last 100 events
        if len(self.cycle_history) > 100:
            self.cycle_history.pop(0)

    def _handle_transcription(self, text: str) -> str:
        """
        Handle transcribed text - the core of the ask cycle

        Args:
            text: Transcribed speech

        Returns:
            Response text
        """
        start_time = time.time()

        # State: Processing
        self.current_state = CycleState.PROCESSING
        self._log_cycle_event(CycleState.PROCESSING, input_text=text)

        logger.info(f"🔄 Cycle {self.cycle_count}: Processing \"{text}\"")

        text_lower = text.lower().strip()
        response = None
        action_taken = None

        # Check for stop commands
        if any(phrase in text_lower for phrase in ["stop listening", "goodbye jarvis", "exit", "quit"]):
            self.stop()
            return "Goodbye! Stopping the conversation."

        # Check for recycle commands
        if any(phrase in text_lower for phrase in ["recycle cursor", "restart cursor", "refresh cursor"]):
            if self.recycle_system:
                self.recycle_system.warm_recycle()
                action_taken = "warm_recycle"
                response = "Recycling Cursor IDE. Please wait..."

        # Process through hands-free Cursor control
        if not response and self.hands_free:
            self.current_state = CycleState.EXECUTING
            self._log_cycle_event(CycleState.EXECUTING)

            result = self.hands_free.process_voice_command(text)

            if result.get("success"):
                response = result.get("response", "Done.")
                action_taken = result.get("intent", {}).get("type", "command")
            else:
                response = "I heard you, but I'm not sure what action to take."

        # Default response if nothing else
        if not response:
            response = "I'm listening..."

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # State: Responding
        self.current_state = CycleState.RESPONDING
        self._log_cycle_event(
            CycleState.RESPONDING, 
            output_text=response, 
            action_taken=action_taken,
            duration_ms=duration_ms
        )

        logger.info(f"   ↪️ Response: \"{response}\"")

        # Increment cycle count
        self.cycle_count += 1

        return response

    def start(self):
        """Start the chained ask cycle"""
        if self.running:
            logger.warning("⚠️  Chained ask cycle already running")
            return

        if not self.always_listening:
            logger.error("❌ Cannot start: Always-listening not available")
            return

        self.running = True
        self.current_state = CycleState.LISTENING

        logger.info("🔄 Starting MANUS Chained Ask Cycle...")
        logger.info("   ┌─────────────────────────────────┐")
        logger.info("   │  🎤 LISTENING                   │")
        logger.info("   │  └→ 📝 TRANSCRIBE              │")
        logger.info("   │     └→ 🧠 PROCESS              │")
        logger.info("   │        └→ ⚡ EXECUTE           │")
        logger.info("   │           └→ 🔊 RESPOND        │")
        logger.info("   │              └→ 🔄 LOOP        │")
        logger.info("   └─────────────────────────────────┘")
        logger.info()
        logger.info("   Speak naturally - I'm always listening.")
        logger.info("   Say 'goodbye JARVIS' to stop.")
        logger.info()

        # Set up the command handler for chained processing
        self.always_listening.set_command_handler(self._handle_transcription)

        # Start always-listening
        self.always_listening.start()

        # Start background threads
        self._start_background_tasks()

        self._log_cycle_event(CycleState.LISTENING)

    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Auto-recycle check thread
        if self.recycle_system:
            def recycle_check_loop():
                while self.running:
                    try:
                        decision = self.recycle_system.should_recycle()
                        if decision.should_recycle and decision.urgency in ["high", "critical"]:
                            logger.warning(f"🔄 Auto-recycle triggered: {decision.reason.value}")

                            # Notify user
                            if self.always_listening:
                                self.always_listening.speak(
                                    "I'm going to recycle Cursor to improve performance. One moment."
                                )

                            time.sleep(2)
                            self.recycle_system.warm_recycle(decision.reason)

                            if self.always_listening:
                                self.always_listening.speak("Cursor has been recycled. Ready.")

                        time.sleep(self.config["auto_recycle_check_interval"])

                    except Exception as e:
                        logger.error(f"Error in recycle check: {e}")
                        time.sleep(60)

            recycle_thread = threading.Thread(target=recycle_check_loop, daemon=True)
            recycle_thread.start()
            logger.info("   🔄 Auto-recycle monitoring: Active")

    def stop(self):
        """Stop the chained ask cycle"""
        if not self.running:
            return

        logger.info("🛑 Stopping MANUS Chained Ask Cycle...")

        self.running = False
        self.current_state = CycleState.IDLE

        # Stop always-listening
        if self.always_listening:
            self.always_listening.stop()

        # Stop hands-free
        if self.hands_free:
            self.hands_free.stop_hands_free_mode()

        self._log_cycle_event(CycleState.IDLE)

        logger.info(f"✅ Stopped after {self.cycle_count} cycles")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "running": self.running,
            "current_state": self.current_state.value,
            "cycle_count": self.cycle_count,
            "components": {
                "always_listening": self.always_listening is not None,
                "hands_free": self.hands_free is not None,
                "recycle_system": self.recycle_system is not None
            },
            "recent_events": [
                {
                    "cycle_id": e.cycle_id,
                    "state": e.state.value,
                    "input": e.input_text,
                    "output": e.output_text,
                    "action": e.action_taken
                }
                for e in self.cycle_history[-5:]
            ]
        }


def main():
    """Main entry point"""
    import signal

    print("="*70)
    print("🔄 MANUS Chained Ask Cycle Controller")
    print("="*70)
    print()
    print("Continuous conversation with JARVIS:")
    print("  Listen → Transcribe → Process → Execute → Respond → Loop")
    print()
    print("No manual triggers - just speak naturally.")
    print()

    # Initialize
    controller = MANUSChainedAskCycle()

    # Signal handler
    def signal_handler(signum, frame):
        print("\n")
        controller.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start
    controller.start()

    # Keep running
    try:
        while controller.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    controller.stop()
    print()
    print("👋 Bye!")


if __name__ == "__main__":


    main()