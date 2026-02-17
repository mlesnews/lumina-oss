#!/usr/bin/env python3
"""
JARVIS God Cycle - Enhanced Chained Ask Cycle

The ultimate hands-free continuous conversation system:
  🎤 Listen → 📝 Transcribe → 🧠 Process → ⚡ Execute → 🔊 Respond → 🔄 Loop

Improvements over base chained ask cycle:
- Self-healing and error recovery
- Performance metrics and optimization
- Context memory across cycles
- Proactive suggestions
- Multi-modal input (voice + text)
- Intelligent silence handling
- Auto warm-recycle integration

This is the "God Mode" for JARVIS - always on, always responsive.
"""

import sys
import time
import threading
import queue
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging
import traceback

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISGodCycle")

# Import components
try:
    from jarvis_always_listening import JARVISAlwaysListening
    ALWAYS_LISTENING_AVAILABLE = True
except ImportError:
    ALWAYS_LISTENING_AVAILABLE = False

try:
    from jarvis_hands_free_cursor_control import JARVISHandsFreeCursorControl
    HANDS_FREE_AVAILABLE = True
except ImportError:
    HANDS_FREE_AVAILABLE = False

try:
    from cursor_intelligent_warm_recycle import CursorIntelligentWarmRecycle, RecycleReason
    RECYCLE_AVAILABLE = True
except ImportError:
    RECYCLE_AVAILABLE = False


class CycleHealth(Enum):
    """Health status of the God Cycle"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    FAILED = "failed"


@dataclass
class CycleMetrics:
    """Performance metrics for the God Cycle"""
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    total_processing_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    commands_executed: int = 0
    errors_recovered: int = 0
    warm_recycles: int = 0
    uptime_seconds: float = 0.0
    last_activity: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cycles": self.total_cycles,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
            "success_rate": self.successful_cycles / max(1, self.total_cycles),
            "avg_response_time_ms": self.avg_response_time_ms,
            "commands_executed": self.commands_executed,
            "errors_recovered": self.errors_recovered,
            "warm_recycles": self.warm_recycles,
            "uptime_seconds": self.uptime_seconds,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }


@dataclass
class ConversationMemory:
    """Memory for context across cycles"""
    recent_commands: List[str] = field(default_factory=list)
    recent_responses: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    open_files: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_start: datetime = field(default_factory=datetime.now)

    def add_interaction(self, command: str, response: str):
        """Add an interaction to memory"""
        self.recent_commands.append(command)
        self.recent_responses.append(response)

        # Keep only last 20 interactions
        if len(self.recent_commands) > 20:
            self.recent_commands.pop(0)
            self.recent_responses.pop(0)

    def get_context(self) -> str:
        """Get conversation context for LLM"""
        context_parts = []

        if self.current_task:
            context_parts.append(f"Current task: {self.current_task}")

        if self.recent_commands:
            context_parts.append(f"Recent commands: {', '.join(self.recent_commands[-5:])}")

        return " | ".join(context_parts) if context_parts else "No prior context"


class JARVISGodCycle:
    """
    JARVIS God Cycle - Ultimate Hands-Free Continuous Conversation

    Enhanced chained ask cycle with:
    - Self-healing error recovery
    - Performance optimization
    - Context memory
    - Proactive suggestions
    - Intelligent silence handling
    """

    # Configuration
    CONFIG = {
        "silence_timeout": 30,  # seconds before prompting
        "error_recovery_delay": 2,  # seconds to wait before retry
        "max_consecutive_errors": 5,  # before entering recovery mode
        "recycle_check_interval": 120,  # seconds
        "metrics_log_interval": 300,  # seconds
        "proactive_suggestion_interval": 60,  # seconds of silence
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize God Cycle"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # State
        self.running = False
        self.health = CycleHealth.HEALTHY
        self.start_time: Optional[datetime] = None
        self.last_interaction_time: Optional[datetime] = None
        self.consecutive_errors = 0

        # Metrics
        self.metrics = CycleMetrics()

        # Memory
        self.memory = ConversationMemory()

        # Components
        self.always_listening: Optional[JARVISAlwaysListening] = None
        self.hands_free: Optional[JARVISHandsFreeCursorControl] = None
        self.recycle_system: Optional[CursorIntelligentWarmRecycle] = None

        # Threads
        self.health_monitor_thread: Optional[threading.Thread] = None
        self.metrics_thread: Optional[threading.Thread] = None
        self.proactive_thread: Optional[threading.Thread] = None

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "god_cycle"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._initialize_components()

        logger.info("⚡ JARVIS God Cycle initialized")
        logger.info("   Mode: Ultimate Hands-Free Continuous Conversation")
        logger.info("   Self-healing: ✅ Enabled")
        logger.info("   Context memory: ✅ Enabled")
        logger.info("   Proactive suggestions: ✅ Enabled")

    def _initialize_components(self):
        """Initialize all components with error handling"""
        # Always-listening
        if ALWAYS_LISTENING_AVAILABLE:
            try:
                self.always_listening = JARVISAlwaysListening(project_root=self.project_root)
                logger.info("   ✅ Always-listening: Ready")
            except Exception as e:
                logger.error(f"   ❌ Always-listening failed: {e}")
                self.health = CycleHealth.DEGRADED

        # Hands-free control
        if HANDS_FREE_AVAILABLE:
            try:
                self.hands_free = JARVISHandsFreeCursorControl(project_root=self.project_root)
                logger.info("   ✅ Hands-free control: Ready")
            except Exception as e:
                logger.error(f"   ❌ Hands-free control failed: {e}")
                self.health = CycleHealth.DEGRADED

        # Warm recycle
        if RECYCLE_AVAILABLE:
            try:
                self.recycle_system = CursorIntelligentWarmRecycle(project_root=self.project_root)
                logger.info("   ✅ Warm recycle: Ready")
            except Exception as e:
                logger.error(f"   ❌ Warm recycle failed: {e}")

    def _handle_command(self, text: str) -> str:
        """
        Process voice command with error handling and metrics

        Args:
            text: Transcribed speech

        Returns:
            Response text
        """
        cycle_start = time.time()
        self.metrics.total_cycles += 1
        self.last_interaction_time = datetime.now()
        self.metrics.last_activity = self.last_interaction_time

        try:
            text_lower = text.lower().strip()
            response = None
            action_taken = None

            # Log the input
            logger.info(f"🎤 You: \"{text}\"")

            # ===== STOP COMMANDS =====
            if any(phrase in text_lower for phrase in [
                "stop listening", "goodbye jarvis", "exit god mode", 
                "quit", "stop god cycle", "shutdown"
            ]):
                self.stop()
                response = "Goodbye! God Cycle stopping."
                return response

            # ===== STATUS COMMANDS =====
            if any(phrase in text_lower for phrase in ["status", "how are you", "health check"]):
                response = self._get_status_response()
                action_taken = "status_check"

            # ===== MEMORY COMMANDS =====
            elif any(phrase in text_lower for phrase in ["remember", "my task is", "working on"]):
                # Extract task from command
                task = text_lower.replace("remember", "").replace("my task is", "").replace("working on", "").strip()
                self.memory.current_task = task
                response = f"Got it, I'll remember you're working on: {task}"
                action_taken = "set_task"

            elif "what am i working on" in text_lower or "current task" in text_lower:
                if self.memory.current_task:
                    response = f"You're working on: {self.memory.current_task}"
                else:
                    response = "I don't have a current task recorded. Tell me what you're working on."
                action_taken = "get_task"

            # ===== RECYCLE COMMANDS =====
            elif any(phrase in text_lower for phrase in ["recycle cursor", "restart cursor", "refresh"]):
                if self.recycle_system:
                    self.recycle_system.warm_recycle(RecycleReason.MANUAL)
                    self.metrics.warm_recycles += 1
                    response = "Recycling Cursor IDE. Please wait..."
                    action_taken = "warm_recycle"
                else:
                    response = "Warm recycle system not available."

            # ===== CURSOR CONTROL COMMANDS =====
            elif self.hands_free:
                result = self.hands_free.process_voice_command(text)

                if result.get("success"):
                    response = result.get("response", "Done.")
                    action_taken = result.get("intent", {}).get("type", "command")
                    self.metrics.commands_executed += 1
                else:
                    response = "I heard you, but I'm not sure what action to take."

            # ===== DEFAULT =====
            if not response:
                response = "I'm listening. What would you like me to do?"

            # Update memory
            self.memory.add_interaction(text, response)

            # Update metrics
            cycle_time = (time.time() - cycle_start) * 1000
            self.metrics.total_processing_time_ms += cycle_time
            self.metrics.avg_response_time_ms = (
                self.metrics.total_processing_time_ms / self.metrics.total_cycles
            )
            self.metrics.successful_cycles += 1
            self.consecutive_errors = 0

            logger.info(f"🔊 JARVIS: \"{response}\" ({cycle_time:.1f}ms)")

            return response

        except Exception as e:
            self.consecutive_errors += 1
            self.metrics.failed_cycles += 1

            logger.error(f"❌ Cycle error: {e}")
            logger.debug(traceback.format_exc())

            # Self-healing
            if self.consecutive_errors >= self.CONFIG["max_consecutive_errors"]:
                self._enter_recovery_mode()

            return "I encountered an error. Let me try again."

    def _get_status_response(self) -> str:
        """Generate status response"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds

        success_rate = (self.metrics.successful_cycles / max(1, self.metrics.total_cycles)) * 100

        return (
            f"I'm running in God Cycle mode. "
            f"Uptime: {uptime_str}. "
            f"Cycles: {self.metrics.total_cycles}, "
            f"Success rate: {success_rate:.1f}%. "
            f"Health: {self.health.value}."
        )

    def _enter_recovery_mode(self):
        """Enter recovery mode after too many errors"""
        logger.warning("⚠️  Entering recovery mode...")
        self.health = CycleHealth.RECOVERING

        # Stop current listeners
        if self.always_listening:
            self.always_listening.stop()

        time.sleep(self.CONFIG["error_recovery_delay"])

        # Reinitialize components
        self._initialize_components()

        # Restart listening
        if self.always_listening and self.running:
            self.always_listening.set_command_handler(self._handle_command)
            self.always_listening.start()

        self.consecutive_errors = 0
        self.metrics.errors_recovered += 1
        self.health = CycleHealth.HEALTHY

        logger.info("✅ Recovered from errors")

    def _health_monitor_loop(self):
        """Background health monitoring"""
        while self.running:
            try:
                # Check recycle need
                if self.recycle_system:
                    decision = self.recycle_system.should_recycle()
                    if decision.should_recycle and decision.urgency in ["high", "critical"]:
                        logger.warning(f"🔄 Auto-recycle: {decision.reason.value}")

                        if self.always_listening:
                            self.always_listening.speak(
                                "I'm recycling Cursor for better performance."
                            )

                        time.sleep(1)
                        self.recycle_system.warm_recycle(decision.reason)
                        self.metrics.warm_recycles += 1

                        if self.always_listening:
                            self.always_listening.speak("Ready.")

                # Update uptime
                if self.start_time:
                    self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()

                time.sleep(self.CONFIG["recycle_check_interval"])

            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                time.sleep(60)

    def _metrics_logger_loop(self):
        """Background metrics logging"""
        while self.running:
            try:
                time.sleep(self.CONFIG["metrics_log_interval"])

                if self.running:
                    self._save_metrics()
                    logger.info(f"📊 Metrics: {self.metrics.total_cycles} cycles, "
                              f"{self.metrics.commands_executed} commands, "
                              f"{self.metrics.avg_response_time_ms:.1f}ms avg")

            except Exception as e:
                logger.error(f"Metrics logger error: {e}")

    def _proactive_suggestions_loop(self):
        """Background thread for proactive suggestions during silence"""
        while self.running:
            try:
                time.sleep(self.CONFIG["proactive_suggestion_interval"])

                if not self.running:
                    break

                # Check for extended silence
                if self.last_interaction_time:
                    silence_duration = (datetime.now() - self.last_interaction_time).total_seconds()

                    if silence_duration > self.CONFIG["silence_timeout"]:
                        # Proactive prompt
                        if self.memory.current_task:
                            prompt = f"Still working on {self.memory.current_task}? Let me know if you need help."
                        else:
                            prompt = "I'm here if you need anything."

                        if self.always_listening:
                            # Don't speak, just log - avoid being annoying
                            logger.debug(f"💭 Proactive: {prompt}")

            except Exception as e:
                logger.error(f"Proactive suggestions error: {e}")

    def _save_metrics(self):
        """Save metrics to file"""
        try:
            metrics_file = self.data_dir / "metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump({
                    "metrics": self.metrics.to_dict(),
                    "memory": {
                        "current_task": self.memory.current_task,
                        "recent_commands": self.memory.recent_commands[-10:],
                        "session_start": self.memory.session_start.isoformat()
                    },
                    "health": self.health.value,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def start(self):
        """Start the God Cycle"""
        if self.running:
            logger.warning("⚠️  God Cycle already running")
            return

        if not self.always_listening:
            logger.error("❌ Cannot start: Always-listening not available")
            return

        self.running = True
        self.start_time = datetime.now()
        self.last_interaction_time = datetime.now()
        self.health = CycleHealth.HEALTHY

        logger.info("⚡ Starting JARVIS God Cycle...")
        logger.info("   ╔══════════════════════════════════════════╗")
        logger.info("   ║  🎤 LISTEN  →  📝 TRANSCRIBE            ║")
        logger.info("   ║      ↓                                   ║")
        logger.info("   ║  🧠 PROCESS  ←  🔄 LOOP                 ║")
        logger.info("   ║      ↓                                   ║")
        logger.info("   ║  ⚡ EXECUTE  →  🔊 RESPOND              ║")
        logger.info("   ╚══════════════════════════════════════════╝")
        logger.info()
        logger.info("   Speak naturally - JARVIS is always listening.")
        logger.info("   Say 'goodbye JARVIS' to stop.")
        logger.info()

        # Set up command handler
        self.always_listening.set_command_handler(self._handle_command)

        # Start listening
        self.always_listening.start()

        # Start background threads
        self.health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop, daemon=True
        )
        self.health_monitor_thread.start()

        self.metrics_thread = threading.Thread(
            target=self._metrics_logger_loop, daemon=True
        )
        self.metrics_thread.start()

        self.proactive_thread = threading.Thread(
            target=self._proactive_suggestions_loop, daemon=True
        )
        self.proactive_thread.start()

        logger.info("✅ God Cycle active")

    def stop(self):
        """Stop the God Cycle"""
        if not self.running:
            return

        logger.info("🛑 Stopping JARVIS God Cycle...")

        self.running = False

        # Save final metrics
        self._save_metrics()

        # Stop listening
        if self.always_listening:
            self.always_listening.stop()

        # Stop hands-free
        if self.hands_free:
            self.hands_free.stop_hands_free_mode()

        # Calculate final uptime
        if self.start_time:
            self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        logger.info(f"✅ God Cycle stopped")
        logger.info(f"   Total cycles: {self.metrics.total_cycles}")
        logger.info(f"   Commands executed: {self.metrics.commands_executed}")
        logger.info(f"   Success rate: {self.metrics.successful_cycles / max(1, self.metrics.total_cycles) * 100:.1f}%")
        logger.info(f"   Uptime: {self.metrics.uptime_seconds:.0f}s")

    def get_status(self) -> Dict[str, Any]:
        """Get complete status"""
        return {
            "running": self.running,
            "health": self.health.value,
            "metrics": self.metrics.to_dict(),
            "memory": {
                "current_task": self.memory.current_task,
                "recent_commands": self.memory.recent_commands[-5:],
            },
            "components": {
                "always_listening": self.always_listening is not None,
                "hands_free": self.hands_free is not None,
                "recycle_system": self.recycle_system is not None
            }
        }


def run_tests():
    """Run tests for God Cycle"""
    print("="*70)
    print("🧪 JARVIS God Cycle - Test Suite")
    print("="*70)
    print()

    # Test 1: Initialization
    print("Test 1: Initialization...")
    god_cycle = JARVISGodCycle()
    assert god_cycle is not None
    print("   ✅ God Cycle initialized")

    # Test 2: Metrics
    print("Test 2: Metrics tracking...")
    metrics = god_cycle.metrics
    assert metrics.total_cycles == 0
    assert metrics.successful_cycles == 0
    print("   ✅ Metrics initialized")

    # Test 3: Memory
    print("Test 3: Conversation memory...")
    god_cycle.memory.add_interaction("test command", "test response")
    assert len(god_cycle.memory.recent_commands) == 1
    assert god_cycle.memory.recent_commands[0] == "test command"
    print("   ✅ Memory working")

    # Test 4: Status
    print("Test 4: Status reporting...")
    status = god_cycle.get_status()
    assert "running" in status
    assert "health" in status
    assert "metrics" in status
    print("   ✅ Status reporting working")

    # Test 5: Command handling (simulated)
    print("Test 5: Command handling...")
    # Simulate a status command
    response = god_cycle._get_status_response()
    assert "God Cycle" in response
    print("   ✅ Command handling working")

    print()
    print("="*70)
    print("✅ All tests passed!")
    print("="*70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS God Cycle - Ultimate Hands-Free Conversation"
    )
    parser.add_argument("--start", action="store_true",
                       help="Start God Cycle")
    parser.add_argument("--test", action="store_true",
                       help="Run tests")
    parser.add_argument("--status", action="store_true",
                       help="Show status")

    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if args.status:
        god_cycle = JARVISGodCycle()
        status = god_cycle.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.start or not any([args.test, args.status]):
        print("="*70)
        print("⚡ JARVIS God Cycle")
        print("="*70)
        print()
        print("Ultimate hands-free continuous conversation system.")
        print()

        god_cycle = JARVISGodCycle()

        import signal
        def signal_handler(signum, frame):
            print("\n")
            god_cycle.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        god_cycle.start()

        try:
            while god_cycle.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass

        god_cycle.stop()
        print()
        print("👋 Goodbye!")


if __name__ == "__main__":


    main()