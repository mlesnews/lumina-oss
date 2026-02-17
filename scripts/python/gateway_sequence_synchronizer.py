#!/usr/bin/env python3
"""
Gateway Sequence Synchronizer

Prevents race conditions by ensuring processes wait for gateway readiness
and maintain proper sequence order (A→B→P, not P→A→B→E→C→D).

Tags: #GATEWAY #SYNCHRONIZATION #SEQUENCE #RACE_CONDITION @JARVIS @LUMINA
"""

import sys
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional
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

logger = get_logger("GatewaySequenceSynchronizer")


class SequenceType(Enum):
    """Shell integration sequence types"""
    PROMPT = "P"          # Prompt ready
    COMMAND_START = "A"   # Command started
    COMMAND_END = "B"     # Command ended
    ERROR = "E"           # Error occurred
    CONTINUATION = "C"    # Command continuation
    DIRECTORY = "D"       # Directory change


class GatewayState(Enum):
    """Gateway readiness states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class SequenceEvent:
    """Sequence event tracking"""
    sequence_type: SequenceType
    timestamp: datetime
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class ProcessRegistration:
    """Process registration for gateway synchronization"""
    process_id: int
    process_name: str
    priority: int = 0  # Higher = starts earlier
    registered_at: datetime = field(default_factory=datetime.now)
    started: bool = False
    gateway_ready: bool = False
    sequence_history: List[SequenceEvent] = field(default_factory=list)


class GatewaySequenceSynchronizer:
    """
    Synchronizes process startup to prevent race conditions with gateway.

    Ensures proper sequence order:
    - Gateway must be ready before processes start
    - Processes must register and wait for gateway
    - Sequence events must follow proper order (A→B→P)
    """

    def __init__(self, project_root_path: Optional[Path] = None):
        """Initialize gateway sequence synchronizer"""
        if project_root_path is None:
            project_root_path = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root_path)

        # Gateway state
        self.gateway_state = GatewayState.UNINITIALIZED
        self.gateway_ready = False
        self.gateway_lock = threading.Lock()
        self.gateway_ready_event = threading.Event()

        # Process registry
        self.registered_processes: Dict[int, ProcessRegistration] = {}
        self.process_lock = threading.Lock()

        # Sequence tracking
        self.sequence_history: deque = deque(maxlen=1000)
        self.sequence_lock = threading.Lock()

        # Expected sequence order
        self.expected_order = [
            SequenceType.COMMAND_START,  # A - Command starts
            SequenceType.COMMAND_END,    # B - Command ends
            SequenceType.PROMPT          # P - Prompt ready
        ]

        # Gateway check configuration
        self.gateway_check_interval = 1.0
        self.gateway_check_timeout = 30.0
        self.gateway_retry_delay = 2.0
        self.max_retries = 5

        logger.info("✅ Gateway Sequence Synchronizer initialized")

    def register_process(
        self,
        process_id: int,
        process_name: str,
        priority: int = 0
    ) -> ProcessRegistration:
        """
        Register a process that needs gateway access.

        Args:
            process_id: Process ID
            process_name: Process name
            priority: Priority (higher = starts earlier)

        Returns:
            ProcessRegistration
        """
        with self.process_lock:
            registration = ProcessRegistration(
                process_id=process_id,
                process_name=process_name,
                priority=priority
            )
            self.registered_processes[process_id] = registration
            logger.info(
                "   📝 Registered process: %s (PID: %d, priority: %d)",
                process_name, process_id, priority
            )
            return registration

    def wait_for_gateway(
        self,
        process_id: int,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Wait for gateway to be ready.

        Args:
            process_id: Process ID waiting for gateway
            timeout: Optional timeout in seconds

        Returns:
            True if gateway is ready, False if timeout
        """
        if timeout is None:
            timeout = self.gateway_check_timeout

        # Check if already ready
        if self.gateway_ready:
            with self.process_lock:
                if process_id in self.registered_processes:
                    self.registered_processes[process_id].gateway_ready = True
            logger.debug("   ✅ Gateway already ready for PID %d", process_id)
            return True

        # Wait for gateway ready event
        logger.info(
            "   ⏳ Process %d waiting for gateway readiness (timeout: %.1fs)...",
            process_id, timeout
        )

        ready = self.gateway_ready_event.wait(timeout=timeout)

        if ready:
            with self.process_lock:
                if process_id in self.registered_processes:
                    self.registered_processes[process_id].gateway_ready = True
            logger.info("   ✅ Gateway ready for PID %d", process_id)
            return True
        else:
            logger.warning(
                "   ⚠️  Gateway timeout for PID %d (waited %.1fs)",
                process_id, timeout
            )
            return False

    def mark_gateway_ready(self):
        """Mark gateway as ready"""
        with self.gateway_lock:
            if not self.gateway_ready:
                self.gateway_state = GatewayState.READY
                self.gateway_ready = True
                self.gateway_ready_event.set()
                logger.info("   ✅ Gateway marked as READY")
            else:
                logger.debug("   Gateway already marked as ready")

    def mark_gateway_initializing(self):
        """Mark gateway as initializing"""
        with self.gateway_lock:
            self.gateway_state = GatewayState.INITIALIZING
            self.gateway_ready = False
            logger.info("   🔄 Gateway initializing...")

    def mark_gateway_error(self, error: str):
        """Mark gateway as error state"""
        with self.gateway_lock:
            self.gateway_state = GatewayState.ERROR
            self.gateway_ready = False
            logger.error("   ❌ Gateway error: %s", error)

    def check_gateway_health(self) -> bool:
        """
        Check if gateway is healthy and ready.

        Returns:
            True if gateway is healthy, False otherwise
        """
        try:
            # Check if gateway services are running
            # This would check actual gateway endpoints
            import httpx

            gateway_urls = [
                "http://localhost:3000/health",
                "http://localhost:3000/",
            ]

            for url in gateway_urls:
                try:
                    response = httpx.get(url, timeout=2.0)
                    if response.status_code == 200:
                        logger.debug("   ✅ Gateway health check passed: %s", url)
                        return True
                except (ConnectionError, TimeoutError, OSError):
                    continue

            logger.debug("   ⚠️  Gateway health check failed")
            return False

        except ImportError:
            # httpx not available - assume gateway is ready if state says so
            logger.debug("   ⚠️  httpx not available - using state check")
            return self.gateway_ready
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning("   ⚠️  Gateway health check error: %s", e)
            return False

    def ensure_gateway_ready(self) -> bool:
        """
        Ensure gateway is ready, checking and waiting if necessary.

        Returns:
            True if gateway is ready, False if failed
        """
        # Check if already ready
        if self.gateway_ready and self.check_gateway_health():
            return True

        # Mark as initializing
        self.mark_gateway_initializing()

        # Try to check gateway health with retries
        for attempt in range(self.max_retries):
            logger.info(
                "   🔄 Checking gateway health (attempt %d/%d)...",
                attempt + 1, self.max_retries
            )

            if self.check_gateway_health():
                self.mark_gateway_ready()
                return True

            if attempt < self.max_retries - 1:
                delay = self.gateway_retry_delay * (2 ** attempt)  # Exponential backoff
                logger.info("   ⏳ Retrying in %.1fs...", delay)
                time.sleep(delay)

        # Failed after retries
        self.mark_gateway_error("Health check failed after retries")
        return False

    def record_sequence(
        self,
        sequence_type: SequenceType,
        process_id: Optional[int] = None,
        process_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Record a sequence event and validate order.

        Args:
            sequence_type: Type of sequence event
            process_id: Optional process ID
            process_name: Optional process name
            metadata: Optional metadata
        """
        event = SequenceEvent(
            sequence_type=sequence_type,
            timestamp=datetime.now(),
            process_id=process_id,
            process_name=process_name,
            metadata=metadata or {}
        )

        with self.sequence_lock:
            self.sequence_history.append(event)

            # Update process registration if provided
            if process_id and process_id in self.registered_processes:
                self.registered_processes[process_id].sequence_history.append(event)

        # Validate sequence order
        self._validate_sequence_order()

    def _validate_sequence_order(self):
        """Validate that sequences are in proper order"""
        if len(self.sequence_history) < 3:
            return  # Need at least 3 events to validate

        # Get last 3 sequences
        recent = list(self.sequence_history)[-3:]
        recent_types = [event.sequence_type for event in recent]

        # Check if order matches expected (A→B→P)
        expected = [seq.value for seq in self.expected_order]
        actual = [seq.value for seq in recent_types]

        if actual != expected:
            logger.warning(
                "   ⚠️  SEQUENCE OUT OF ORDER: Expected %s, got %s",
                "→".join(expected), "→".join(actual)
            )
            logger.warning(
                "   🔧 This indicates a race condition - processes racing gateway"
            )

            # Try to correct by ensuring gateway is ready
            if not self.gateway_ready:
                logger.info("   🔄 Gateway not ready - attempting to ensure readiness...")
                self.ensure_gateway_ready()
        else:
            logger.debug("   ✅ Sequence order valid: %s", "→".join(actual))

    def get_sequence_status(self) -> Dict:
        """Get current sequence status"""
        with self.sequence_lock:
            recent_sequences = list(self.sequence_history)[-10:]
            recent_types = [event.sequence_type.value for event in recent_sequences]

        return {
            "gateway_state": self.gateway_state.value,
            "gateway_ready": self.gateway_ready,
            "registered_processes": len(self.registered_processes),
            "recent_sequences": recent_types,
            "sequence_count": len(self.sequence_history),
            "expected_order": [seq.value for seq in self.expected_order]
        }

    def reset_sequences(self):
        """Reset sequence history (for testing/recovery)"""
        with self.sequence_lock:
            self.sequence_history.clear()
        logger.info("   🔄 Sequence history reset")

    def unregister_process(self, process_id: int):
        """Unregister a process"""
        with self.process_lock:
            if process_id in self.registered_processes:
                del self.registered_processes[process_id]
                logger.info("   📝 Unregistered process: PID %d", process_id)


# Global instance
_synchronizer_instance = None
_synchronizer_lock = threading.Lock()


def get_gateway_synchronizer() -> GatewaySequenceSynchronizer:
    """Get or create global gateway synchronizer instance"""
    global _synchronizer_instance  # pylint: disable=global-statement

    with _synchronizer_lock:
        if _synchronizer_instance is None:
            _synchronizer_instance = GatewaySequenceSynchronizer()
            # Ensure gateway is ready on initialization
            _synchronizer_instance.ensure_gateway_ready()
        return _synchronizer_instance


def register_process_for_gateway(
    process_id: int,
    process_name: str,
    priority: int = 0
) -> ProcessRegistration:
    """Register a process that needs gateway access"""
    synchronizer = get_gateway_synchronizer()
    return synchronizer.register_process(process_id, process_name, priority)


def wait_for_gateway_ready(
    process_id: int,
    timeout: Optional[float] = None
) -> bool:
    """Wait for gateway to be ready"""
    synchronizer = get_gateway_synchronizer()
    return synchronizer.wait_for_gateway(process_id, timeout)


def mark_gateway_ready():
    """Mark gateway as ready"""
    synchronizer = get_gateway_synchronizer()
    synchronizer.mark_gateway_ready()


def record_sequence_event(
    sequence_type: str,
    process_id: Optional[int] = None,
    process_name: Optional[str] = None
):
    """Record a sequence event"""
    synchronizer = get_gateway_synchronizer()
    try:
        seq_type = SequenceType(sequence_type.upper())
        synchronizer.record_sequence(seq_type, process_id, process_name)
    except ValueError:
        logger.warning("   ⚠️  Unknown sequence type: %s", sequence_type)


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Gateway Sequence Synchronizer")
    parser.add_argument("--check", action="store_true", help="Check gateway status")
    parser.add_argument("--ensure", action="store_true", help="Ensure gateway is ready")
    parser.add_argument("--status", action="store_true", help="Show sequence status")
    parser.add_argument("--register", type=int, help="Register process ID")
    parser.add_argument("--wait", type=int, help="Wait for gateway (process ID)")

    args = parser.parse_args()

    synchronizer = get_gateway_synchronizer()

    if args.check:
        healthy = synchronizer.check_gateway_health()
        print(f"Gateway health: {'✅ Healthy' if healthy else '❌ Unhealthy'}")

    if args.ensure:
        ready = synchronizer.ensure_gateway_ready()
        print(f"Gateway ready: {'✅ Ready' if ready else '❌ Not ready'}")

    if args.status:
        status = synchronizer.get_sequence_status()
        print("\n📊 Gateway Sequence Status:")
        print(f"   Gateway state: {status['gateway_state']}")
        print(f"   Gateway ready: {status['gateway_ready']}")
        print(f"   Registered processes: {status['registered_processes']}")
        print(f"   Recent sequences: {' → '.join(status['recent_sequences'])}")
        print(f"   Expected order: {' → '.join(status['expected_order'])}")

    if args.register:
        reg = synchronizer.register_process(args.register, f"test_process_{args.register}")
        print(f"✅ Registered: PID {reg.process_id}")

    if args.wait:
        ready = synchronizer.wait_for_gateway(args.wait, timeout=10.0)
        print(f"Gateway ready for PID {args.wait}: {'✅ Yes' if ready else '❌ Timeout'}")


if __name__ == "__main__":


    main()