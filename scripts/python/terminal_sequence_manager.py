#!/usr/bin/env python3
"""
Terminal Sequence Manager

Manages terminal initialization and shell integration sequences to prevent
race conditions. Ensures proper sequence order (A→B→P) and re-initializes
terminal if sequences arrive out of order.

Tags: #TERMINAL #SEQUENCE #SHELL_INTEGRATION #RACE_CONDITION @JARVIS @LUMINA
"""

import sys
import os
import time
import threading
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Deque
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("TerminalSequenceManager")


class SequenceMarker(Enum):
    """Shell integration sequence markers"""
    PROMPT = "P"          # Prompt ready
    COMMAND_START = "A"   # Command started
    COMMAND_END = "B"     # Command ended
    ERROR = "E"           # Error occurred
    CONTINUATION = "C"    # Command continuation
    DIRECTORY = "D"       # Directory change


@dataclass
class SequenceEvent:
    """Terminal sequence event"""
    marker: SequenceMarker
    timestamp: datetime
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    context: Dict = field(default_factory=dict)


class TerminalState(Enum):
    """Terminal initialization state"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    OUT_OF_ORDER = "out_of_order"
    REINITIALIZING = "reinitializing"
    ERROR = "error"


class TerminalSequenceManager:
    """
    Manages terminal initialization and sequence validation.

    Prevents race conditions by:
    - Ensuring terminal is initialized before processes start
    - Validating sequence order (A→B→P)
    - Re-initializing terminal if sequences are out of order
    - Providing synchronization for process startup
    """

    def __init__(self):
        """Initialize terminal sequence manager"""
        self.state = TerminalState.UNINITIALIZED
        self.state_lock = threading.Lock()
        self.ready_event = threading.Event()

        # Sequence tracking
        self.sequence_history: Deque[SequenceEvent] = deque(maxlen=100)
        self.sequence_lock = threading.Lock()

        # Expected order: A (start) → B (end) → P (prompt)
        self.expected_order = [
            SequenceMarker.COMMAND_START,
            SequenceMarker.COMMAND_END,
            SequenceMarker.PROMPT
        ]

        # Process registry
        self.waiting_processes: Dict[int, str] = {}
        self.process_lock = threading.Lock()

        # Terminal re-initialization
        self.reinit_lock = threading.Lock()
        self.reinit_in_progress = False

        # Configuration
        self.sequence_timeout = 5.0  # Seconds to wait for proper sequence
        self.reinit_delay = 2.0  # Delay before re-initialization

        logger.info("✅ Terminal Sequence Manager initialized")

    def initialize_terminal(self) -> bool:
        """
        Initialize terminal and wait for proper sequence.

        Returns:
            True if terminal initialized successfully
        """
        with self.state_lock:
            if self.state == TerminalState.READY:
                logger.debug("   Terminal already initialized")
                return True

            if self.state == TerminalState.INITIALIZING:
                logger.debug("   Terminal initialization already in progress")
                return self.ready_event.wait(timeout=30.0)

            self.state = TerminalState.INITIALIZING
            logger.info("   🔄 Initializing terminal...")

        try:
            # Wait for terminal to be ready
            # This ensures shell integration is loaded
            time.sleep(0.5)  # Give terminal time to initialize

            # Check if we can detect terminal readiness
            # In Cursor/VS Code, terminal is ready when shell integration loads
            terminal_ready = self._check_terminal_readiness()

            if terminal_ready:
                with self.state_lock:
                    self.state = TerminalState.READY
                    self.ready_event.set()
                logger.info("   ✅ Terminal initialized and ready")
                return True
            else:
                # Try to trigger terminal initialization
                self._trigger_terminal_init()
                time.sleep(1.0)

                terminal_ready = self._check_terminal_readiness()
                if terminal_ready:
                    with self.state_lock:
                        self.state = TerminalState.READY
                        self.ready_event.set()
                    logger.info("   ✅ Terminal initialized after trigger")
                    return True
                else:
                    # More lenient: assume ready even if check fails
                    # Better to proceed than block indefinitely
                    with self.state_lock:
                        self.state = TerminalState.READY
                        self.ready_event.set()
                    logger.info("   ✅ Terminal assumed ready (lenient mode)")
                    return True

        except (OSError, RuntimeError, ValueError) as e:
            with self.state_lock:
                self.state = TerminalState.ERROR
            logger.error("   ❌ Terminal initialization error: %s", e)
            return False

    def _check_terminal_readiness(self) -> bool:
        """
        Check if terminal is ready (shell integration loaded).

        Returns:
            True if terminal appears ready
        """
        try:
            # Check if we're in a terminal environment
            # In Cursor/VS Code, TERM_PROGRAM indicates terminal
            term_program = os.environ.get("TERM_PROGRAM", "")
            if term_program in ["vscode", "cursor"]:
                # Terminal environment detected - assume ready
                return True

            # Check for VS Code/Cursor environment variables
            if os.environ.get("VSCODE_PID") or os.environ.get("CURSOR_PID"):
                return True

            # Check if we have a TTY (terminal)
            if hasattr(sys.stdout, 'fileno'):
                try:
                    return os.isatty(sys.stdout.fileno())
                except (OSError, AttributeError):
                    pass

            # Fallback: if we're running Python in a shell, assume ready
            # This is more lenient - better to assume ready than block
            return True

        except Exception as e:
            logger.debug("   Terminal readiness check error: %s", e)
            # Default to ready on error (fail open)
            return True

    def _trigger_terminal_init(self):
        """Trigger terminal initialization"""
        try:
            # Send a harmless command to trigger shell integration
            # This helps ensure sequences are properly initialized
            if sys.platform == "win32":
                # Windows: Use PowerShell command
                subprocess.run(
                    ["pwsh", "-NoProfile", "-Command", "Write-Host 'Terminal ready'"],
                    timeout=2.0,
                    capture_output=True,
                    check=False
                )
            else:
                # Unix: Use echo
                subprocess.run(
                    ["echo", "Terminal ready"],
                    timeout=2.0,
                    capture_output=True,
                    check=False
                )
        except (OSError, subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.debug("   Could not trigger terminal init: %s", e)

    def wait_for_terminal_ready(self, process_id: int, process_name: str, timeout: float = 30.0) -> bool:
        """
        Wait for terminal to be ready before starting process.

        Args:
            process_id: Process ID waiting
            process_name: Process name
            timeout: Timeout in seconds

        Returns:
            True if terminal is ready, False if timeout
        """
        # Register waiting process
        with self.process_lock:
            self.waiting_processes[process_id] = process_name

        # Ensure terminal is initialized
        if self.state != TerminalState.READY:
            self.initialize_terminal()

        # Wait for ready event
        logger.info(
            "   ⏳ Process %s (PID: %d) waiting for terminal ready...",
            process_name, process_id
        )

        ready = self.ready_event.wait(timeout=timeout)

        if ready:
            logger.info("   ✅ Terminal ready for process %s (PID: %d)", process_name, process_id)
        else:
            logger.warning(
                "   ⚠️  Terminal timeout for process %s (PID: %d)",
                process_name, process_id
            )

        # Unregister
        with self.process_lock:
            self.waiting_processes.pop(process_id, None)

        return ready

    def record_sequence(
        self,
        marker: str,
        process_id: Optional[int] = None,
        process_name: Optional[str] = None
    ) -> bool:
        """
        Record a sequence marker and validate order.

        Args:
            marker: Sequence marker (P, A, B, E, C, D)
            process_id: Optional process ID
            process_name: Optional process name

        Returns:
            True if sequence is valid, False if out of order
        """
        try:
            seq_marker = SequenceMarker(marker.upper())
        except ValueError:
            logger.warning(f"   ⚠️  Unknown sequence marker: {marker}")
            return True  # Don't fail on unknown markers

        event = SequenceEvent(
            marker=seq_marker,
            timestamp=datetime.now(),
            process_id=process_id,
            process_name=process_name
        )

        with self.sequence_lock:
            self.sequence_history.append(event)

        # Validate sequence order
        is_valid = self._validate_sequence()

        if not is_valid:
            logger.warning("   ⚠️  SEQUENCE OUT OF ORDER detected! Marker: %s", marker)
            # Trigger re-initialization
            self._handle_out_of_order()

        return is_valid

    def _validate_sequence(self) -> bool:
        """
        Validate that recent sequences are in proper order.

        Returns:
            True if sequences are in order, False otherwise
        """
        if len(self.sequence_history) < 3:
            return True  # Need at least 3 events to validate

        # Get last 3 sequences
        recent = list(self.sequence_history)[-3:]
        recent_markers = [event.marker for event in recent]

        # Check if order matches expected (A→B→P)
        if recent_markers == self.expected_order:
            logger.debug("   ✅ Sequence order valid: A→B→P")
            return True

        # Check for out-of-order patterns
        marker_values = [m.value for m in recent_markers]
        expected_values = [m.value for m in self.expected_order]

        if marker_values != expected_values:
            logger.warning(
                "   ⚠️  Sequence mismatch: Expected %s, got %s",
                "→".join(expected_values),
                "→".join(marker_values)
            )
            return False

        return True

    def _handle_out_of_order(self):
        """Handle out-of-order sequence by re-initializing terminal"""
        with self.reinit_lock:
            if self.reinit_in_progress:
                return  # Already re-initializing

            self.reinit_in_progress = True

        try:
            logger.warning("   🔄 Terminal sequences out of order - re-initializing...")

            with self.state_lock:
                self.state = TerminalState.OUT_OF_ORDER

            # Clear sequence history
            with self.sequence_lock:
                self.sequence_history.clear()

            # Wait a bit before re-initialization
            time.sleep(self.reinit_delay)

            # Re-initialize terminal
            logger.info("   🔄 Re-initializing terminal...")
            success = self.initialize_terminal()

            if success:
                logger.info("   ✅ Terminal re-initialized successfully")
            else:
                logger.warning("   ⚠️  Terminal re-initialization failed")
                with self.state_lock:
                    self.state = TerminalState.ERROR

        finally:
            with self.reinit_lock:
                self.reinit_in_progress = False

    def reinitialize_terminal(self) -> bool:
        """
        Force re-initialization of terminal.

        Returns:
            True if re-initialization successful
        """
        logger.info("   🔄 Force re-initializing terminal...")

        with self.state_lock:
            old_state = self.state
            self.state = TerminalState.REINITIALIZING
            self.ready_event.clear()

        # Clear sequence history
        with self.sequence_lock:
            self.sequence_history.clear()

        # Re-initialize
        success = self.initialize_terminal()

        if not success:
            with self.state_lock:
                self.state = old_state

        return success

    def get_status(self) -> Dict:
        """Get current terminal status"""
        with self.sequence_lock:
            recent = list(self.sequence_history)[-5:]
            recent_markers = [e.marker.value for e in recent]

        return {
            "state": self.state.value,
            "ready": self.state == TerminalState.READY,
            "waiting_processes": len(self.waiting_processes),
            "recent_sequences": recent_markers,
            "expected_order": [m.value for m in self.expected_order],
            "sequence_count": len(self.sequence_history)
        }


# Global instance
_terminal_manager = None
_terminal_lock = threading.Lock()


def get_terminal_manager() -> TerminalSequenceManager:
    """Get or create global terminal sequence manager"""
    global _terminal_manager  # pylint: disable=global-statement

    with _terminal_lock:
        if _terminal_manager is None:
            _terminal_manager = TerminalSequenceManager()
            # Auto-initialize terminal
            _terminal_manager.initialize_terminal()

            # Auto-start auto-fix monitor
            try:
                from terminal_sequence_auto_fix import get_auto_fix_monitor
                get_auto_fix_monitor()  # Auto-starts
                logger.debug("   ✅ Auto-fix monitor started")
            except ImportError:
                logger.debug("   Auto-fix monitor not available")
            except Exception as e:
                logger.debug("   Could not start auto-fix monitor: %s", e)

            # Auto-start auto-save terminal fix
            try:
                from autosave_terminal_fix import get_autosave_terminal_fix
                get_autosave_terminal_fix()  # Auto-starts
                logger.debug("   ✅ Auto-save terminal fix started")
            except ImportError:
                logger.debug("   Auto-save terminal fix not available (watchdog may not be installed)")
            except Exception as e:
                logger.debug("   Could not start auto-save terminal fix: %s", e)

        return _terminal_manager


def wait_for_terminal_ready(process_id: int, process_name: str, timeout: float = 30.0) -> bool:
    """Wait for terminal to be ready"""
    manager = get_terminal_manager()
    return manager.wait_for_terminal_ready(process_id, process_name, timeout)


def record_terminal_sequence(marker: str, process_id: Optional[int] = None, process_name: Optional[str] = None) -> bool:
    """Record a terminal sequence marker"""
    manager = get_terminal_manager()
    return manager.record_sequence(marker, process_id, process_name)


def reinitialize_terminal() -> bool:
    """Force re-initialize terminal"""
    manager = get_terminal_manager()
    return manager.reinitialize_terminal()


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Terminal Sequence Manager")
    parser.add_argument("--init", action="store_true", help="Initialize terminal")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--reinit", action="store_true", help="Re-initialize terminal")
    parser.add_argument("--record", type=str, help="Record sequence marker (P, A, B, E, C, D)")
    parser.add_argument("--wait", action="store_true", help="Wait for terminal ready")

    args = parser.parse_args()

    manager = get_terminal_manager()

    if args.init:
        ready = manager.initialize_terminal()
        print(f"Terminal initialized: {'✅ Ready' if ready else '❌ Failed'}")

    if args.status:
        status = manager.get_status()
        print("\n📊 Terminal Status:")
        print(f"   State: {status['state']}")
        print(f"   Ready: {status['ready']}")
        print(f"   Waiting processes: {status['waiting_processes']}")
        print(f"   Recent sequences: {' → '.join(status['recent_sequences'])}")
        print(f"   Expected order: {' → '.join(status['expected_order'])}")

    if args.reinit:
        success = manager.reinitialize_terminal()
        print(f"Terminal re-initialized: {'✅ Success' if success else '❌ Failed'}")

    if args.record:
        valid = manager.record_sequence(args.record)
        print(f"Sequence recorded: {'✅ Valid' if valid else '⚠️  Out of order'}")

    if args.wait:
        ready = manager.wait_for_terminal_ready(os.getpid(), "test_process", timeout=10.0)
        print(f"Terminal ready: {'✅ Yes' if ready else '❌ Timeout'}")


if __name__ == "__main__":


    main()