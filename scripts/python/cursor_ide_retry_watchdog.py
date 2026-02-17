#!/usr/bin/env python3
"""
Cursor IDE Retry Watchdog - @ask Retry Handler

Automatic retry handler for transient Cursor IDE connection errors.
- Retries at least 3 times on ConnectError
- Resets retry counter every 30 minutes after last error
- Tracks by parent Request ID (@ask)

Tags: #CURSOR_IDE #RETRY #WATCHDOG #CONN_ERROR @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorIDERetryWatchdog")


class RetryStatus(Enum):
    """Retry attempt status"""
    PENDING = "pending"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    EXHAUSTED = "exhausted"  # All retries used
    RESET = "reset"  # Counter reset after timeout


@dataclass
class RetryState:
    """State for a tracked request"""
    request_id: str
    parent_ask_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    last_error_time: Optional[str] = None
    last_retry_time: Optional[str] = None
    status: RetryStatus = RetryStatus.PENDING
    error_messages: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reset_after_minutes: int = 30


class CursorIDERetryWatchdog:
    """
    Cursor IDE Retry Watchdog

    Automatically retries transient connection errors:
    - ConnectError: serialize binary overflow
    - ECONNRESET
    - Timeout errors

    Features:
    - 3 automatic retries per request
    - 30-minute reset window
    - Request ID tracking (@ask)
    - Persistent state across sessions
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay_seconds: float = 3.0,
        reset_after_minutes: int = 30,
        project_root: Optional[Path] = None
    ):
        """Initialize retry watchdog"""
        self.max_retries = max_retries
        self.retry_delay = retry_delay_seconds
        self.reset_after_minutes = reset_after_minutes
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # State storage
        self.state_dir = self.project_root / "data" / "cursor_ide_retry"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "watchdog_state.json"
        self.history_file = self.state_dir / "retry_history.jsonl"

        # Active retry states
        self.active_states: Dict[str, RetryState] = {}

        # Load persisted state
        self._load_state()

        # Background cleanup thread
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False

        logger.info("🐕 Cursor IDE Retry Watchdog initialized")
        logger.info(f"   Max retries: {self.max_retries}")
        logger.info(f"   Retry delay: {self.retry_delay}s")
        logger.info(f"   Reset after: {self.reset_after_minutes} minutes")

    def _load_state(self):
        """Load persisted state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for req_id, state_data in data.get("active_states", {}).items():
                        state_data["status"] = RetryStatus(state_data["status"])
                        self.active_states[req_id] = RetryState(**state_data)
                logger.info(f"   📂 Loaded {len(self.active_states)} active states")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load state: {e}")

    def _save_state(self):
        """Save state to disk"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "active_states": {
                    req_id: {**asdict(state), "status": state.status.value}
                    for req_id, state in self.active_states.items()
                }
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Could not save state: {e}")

    def _log_history(self, event: Dict[str, Any]):
        """Append event to history log"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"❌ Could not log history: {e}")

    def _check_reset(self, state: RetryState) -> bool:
        """Check if retry counter should be reset (30 min elapsed)"""
        if state.last_error_time:
            last_error = datetime.fromisoformat(state.last_error_time)
            reset_threshold = last_error + timedelta(minutes=state.reset_after_minutes)
            if datetime.now() > reset_threshold:
                logger.info(f"   🔄 Reset counter for {state.request_id[:8]}... (30 min elapsed)")
                state.retry_count = 0
                state.status = RetryStatus.RESET
                state.error_messages = []
                return True
        return False

    def register_error(
        self,
        request_id: str,
        error_message: str,
        parent_ask_id: Optional[str] = None
    ) -> RetryState:
        """
        Register an error for retry tracking

        Args:
            request_id: The request ID that failed
            error_message: Error message
            parent_ask_id: Parent @ask ID if known

        Returns:
            Current retry state
        """
        now = datetime.now().isoformat()

        # Get or create state
        if request_id in self.active_states:
            state = self.active_states[request_id]
            # Check for reset
            self._check_reset(state)
        else:
            state = RetryState(
                request_id=request_id,
                parent_ask_id=parent_ask_id,
                max_retries=self.max_retries,
                reset_after_minutes=self.reset_after_minutes
            )
            self.active_states[request_id] = state

        # Update state
        state.last_error_time = now
        state.error_messages.append({
            "time": now,
            "message": error_message[:500]  # Truncate
        })
        state.status = RetryStatus.PENDING

        # Log
        logger.warning(f"⚠️  Error registered: {request_id[:8]}...")
        logger.warning(f"   Message: {error_message[:100]}...")
        logger.warning(f"   Retry count: {state.retry_count}/{state.max_retries}")

        self._save_state()

        return state

    def should_retry(self, request_id: str) -> bool:
        """Check if request should be retried"""
        if request_id not in self.active_states:
            return True  # First attempt

        state = self.active_states[request_id]

        # Check for reset
        self._check_reset(state)

        return state.retry_count < state.max_retries

    def get_retry_count(self, request_id: str) -> int:
        """Get current retry count for request"""
        if request_id not in self.active_states:
            return 0
        return self.active_states[request_id].retry_count

    def execute_retry(
        self,
        request_id: str,
        retry_func: Callable[[], Any],
        error_message: str,
        parent_ask_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute retry with automatic handling

        Args:
            request_id: Request ID
            retry_func: Function to retry (should raise on failure)
            error_message: Original error message
            parent_ask_id: Parent @ask ID

        Returns:
            Result dict with success status and details
        """
        # Register error
        state = self.register_error(request_id, error_message, parent_ask_id)

        result = {
            "request_id": request_id,
            "parent_ask_id": parent_ask_id,
            "retries_attempted": 0,
            "success": False,
            "final_error": None
        }

        while state.retry_count < state.max_retries:
            state.retry_count += 1
            state.status = RetryStatus.RETRYING
            state.last_retry_time = datetime.now().isoformat()
            result["retries_attempted"] = state.retry_count

            logger.info(f"🔄 Retry attempt {state.retry_count}/{state.max_retries} for {request_id[:8]}...")

            # Wait before retry
            time.sleep(self.retry_delay)

            try:
                # Execute retry
                retry_result = retry_func()

                # Success!
                state.status = RetryStatus.SUCCESS
                result["success"] = True
                result["result"] = retry_result

                logger.info(f"✅ Retry successful on attempt {state.retry_count}")

                # Log to history
                self._log_history({
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id,
                    "parent_ask_id": parent_ask_id,
                    "event": "retry_success",
                    "attempt": state.retry_count
                })

                self._save_state()
                return result

            except Exception as e:
                error_msg = str(e)
                state.error_messages.append({
                    "time": datetime.now().isoformat(),
                    "message": error_msg[:500],
                    "attempt": state.retry_count
                })
                result["final_error"] = error_msg

                logger.warning(f"   ❌ Attempt {state.retry_count} failed: {error_msg[:100]}...")

        # Exhausted all retries
        state.status = RetryStatus.EXHAUSTED
        logger.error(f"❌ All {state.max_retries} retries exhausted for {request_id[:8]}...")

        # Log to history
        self._log_history({
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "parent_ask_id": parent_ask_id,
            "event": "retries_exhausted",
            "attempts": state.retry_count,
            "final_error": result["final_error"]
        })

        self._save_state()
        return result

    def handle_connect_error(
        self,
        request_id: str,
        error_message: str,
        retry_action: Optional[Callable[[], Any]] = None,
        parent_ask_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle ConnectError with automatic retry

        This is the main entry point for handling Cursor IDE connection errors.

        Args:
            request_id: Request ID from error
            error_message: Full error message
            retry_action: Optional function to call for retry
            parent_ask_id: Parent @ask ID

        Returns:
            Handling result
        """
        logger.info("=" * 70)
        logger.info("🐕 CURSOR IDE RETRY WATCHDOG - ConnectError Handler")
        logger.info("=" * 70)
        logger.info(f"   Request ID: {request_id}")
        logger.info(f"   Parent @ask: {parent_ask_id or 'Unknown'}")

        # Check if should retry
        if not self.should_retry(request_id):
            state = self.active_states.get(request_id)
            logger.warning(f"   ⚠️  Max retries ({state.max_retries}) already exhausted")
            logger.warning(f"   ⏰ Wait {state.reset_after_minutes} min for counter reset")
            return {
                "request_id": request_id,
                "action": "wait_for_reset",
                "retry_count": state.retry_count,
                "reset_after_minutes": state.reset_after_minutes,
                "success": False
            }

        # If retry action provided, execute it
        if retry_action:
            return self.execute_retry(
                request_id=request_id,
                retry_func=retry_action,
                error_message=error_message,
                parent_ask_id=parent_ask_id
            )

        # Otherwise just register and provide guidance
        state = self.register_error(request_id, error_message, parent_ask_id)

        return {
            "request_id": request_id,
            "action": "registered",
            "retry_count": state.retry_count,
            "max_retries": state.max_retries,
            "retries_remaining": state.max_retries - state.retry_count,
            "recommendation": "Reload Cursor window (Ctrl+Shift+P → 'Reload Window') and retry",
            "auto_reset_after": f"{state.reset_after_minutes} minutes"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current watchdog status"""
        now = datetime.now()

        # Check for resets
        for state in self.active_states.values():
            self._check_reset(state)

        active_count = sum(
            1 for s in self.active_states.values() 
            if s.status in [RetryStatus.PENDING, RetryStatus.RETRYING]
        )
        exhausted_count = sum(
            1 for s in self.active_states.values() 
            if s.status == RetryStatus.EXHAUSTED
        )

        return {
            "status": "running",
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay,
            "reset_after_minutes": self.reset_after_minutes,
            "tracked_requests": len(self.active_states),
            "active_retries": active_count,
            "exhausted": exhausted_count,
            "last_check": now.isoformat()
        }

    def print_status(self):
        """Print formatted status"""
        status = self.get_status()

        print("")
        print("=" * 60)
        print("  🐕 CURSOR IDE RETRY WATCHDOG STATUS")
        print("=" * 60)
        print(f"  Max Retries:      {status['max_retries']}")
        print(f"  Retry Delay:      {status['retry_delay_seconds']}s")
        print(f"  Reset After:      {status['reset_after_minutes']} min")
        print(f"  Tracked Requests: {status['tracked_requests']}")
        print(f"  Active Retries:   {status['active_retries']}")
        print(f"  Exhausted:        {status['exhausted']}")
        print("=" * 60)

        if self.active_states:
            print("")
            print("  Recent Requests:")
            for req_id, state in list(self.active_states.items())[-5:]:
                print(f"    {req_id[:16]}... | {state.status.value} | {state.retry_count}/{state.max_retries}")
        print("")

    def clear_state(self, request_id: Optional[str] = None):
        """Clear state for specific request or all"""
        if request_id:
            if request_id in self.active_states:
                del self.active_states[request_id]
                logger.info(f"🗑️  Cleared state for {request_id[:8]}...")
        else:
            self.active_states.clear()
            logger.info("🗑️  Cleared all retry states")

        self._save_state()


# Global singleton instance
_watchdog_instance: Optional[CursorIDERetryWatchdog] = None


def get_watchdog() -> CursorIDERetryWatchdog:
    """Get or create global watchdog instance"""
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = CursorIDERetryWatchdog()
    return _watchdog_instance


def handle_cursor_error(
    request_id: str,
    error_message: str,
    parent_ask_id: Optional[str] = None,
    retry_action: Optional[Callable[[], Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to handle Cursor IDE errors

    Usage:
        from cursor_ide_retry_watchdog import handle_cursor_error

        result = handle_cursor_error(
            request_id="f3de7a42-...",
            error_message="ConnectError: serialize binary...",
            parent_ask_id="ask-123"
        )
    """
    watchdog = get_watchdog()
    return watchdog.handle_connect_error(
        request_id=request_id,
        error_message=error_message,
        parent_ask_id=parent_ask_id,
        retry_action=retry_action
    )


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Cursor IDE Retry Watchdog"
        )
        parser.add_argument("--status", action="store_true", help="Show watchdog status")
        parser.add_argument("--clear", action="store_true", help="Clear all retry states")
        parser.add_argument("--test", type=str, help="Test error handling with request ID")

        args = parser.parse_args()

        watchdog = CursorIDERetryWatchdog()

        if args.status:
            watchdog.print_status()

        elif args.clear:
            watchdog.clear_state()
            print("✅ All retry states cleared")

        elif args.test:
            result = watchdog.handle_connect_error(
                request_id=args.test,
                error_message="Test: ConnectError: [internal] serialize binary: invalid int 32: 4294967295",
                parent_ask_id="test-ask-001"
            )
            print(json.dumps(result, indent=2))

        else:
            watchdog.print_status()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()