#!/usr/bin/env python3
"""
Operator Idleness Restriction System

**IMPORTANT**: Restrictions are placed on JARVIS/AI/MANUS, NOT on the @OP (operator).
When the operator is idle for 10+ minutes, JARVIS and other AI systems are temporarily restricted
from autonomous actions. The operator is NEVER restricted - only JARVIS/AI/MANUS are restricted.

Integrates with @ask chaining to prevent autonomous actions when operator is idle.

@OP #IDLENESS #RESTRICTION #ASKCHAINING @JARVIS @MANUS
#TEMPORARY_RESTRICTIONS_ON_JARVIS_NOT_OP
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OperatorIdlenessRestriction")


class IdlenessState(Enum):
    """Operator idleness state"""
    ACTIVE = "active"
    IDLE = "idle"
    RESTRICTED = "restricted"


@dataclass
class OperatorActivity:
    """Operator activity record"""
    timestamp: datetime
    activity_type: str
    source: str  # keyboard, mouse, voice, chat, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdlenessRestriction:
    """Idleness restriction configuration"""
    idle_timeout_seconds: int = 600  # 10 minutes - MINIMUM BREATHER FOR @OP
    restriction_enabled: bool = True
    restricted_actions: List[str] = field(default_factory=lambda: [
        "ai_action",
        "jarvis_action",
        "manus_action",
        "autonomous_execution",
        "ask_chain_execution"
    ])
    allow_emergency: bool = True  # Allow emergency actions even when idle


class OperatorIdlenessRestriction:
    """
    Operator Idleness Restriction System

    **CLARIFICATION**: Restrictions are TEMPORARY and placed on JARVIS/AI/MANUS, NOT on the @OP.
    When the operator is idle for 10+ minutes, JARVIS and other AI systems are temporarily
    restricted from autonomous actions. The operator is NEVER restricted.

    Tracks operator activity and restricts AI/JARVIS/MANUS actions
    during idle periods (10 minutes).

    Features:
    - Real-time activity tracking
    - Idleness detection (10-minute timeout)
    - Action restriction on JARVIS/AI/MANUS during idle periods (NOT on @OP)
    - Integration with @ask chaining
    - Emergency action override
    """

    def __init__(self, project_root: Path, idle_timeout_seconds: int = 600):
        """
        Initialize operator idleness restriction system

        Args:
            project_root: Project root directory
            idle_timeout_seconds: Idle timeout in seconds (default: 600 = 10 minutes)
        """
        self.project_root = project_root
        self.logger = logger

        # Configuration
        # Ensure minimum 10-minute breather for @OP
        min_breather_seconds = 600  # 10 minutes minimum
        if idle_timeout_seconds < min_breather_seconds:
            self.logger.warning(f"⚠️  Idle timeout {idle_timeout_seconds}s is less than minimum 10-minute breather. Setting to {min_breather_seconds}s")
            idle_timeout_seconds = min_breather_seconds

        self.restriction = IdlenessRestriction(
            idle_timeout_seconds=idle_timeout_seconds,
            restriction_enabled=True
        )

        # State tracking
        self.last_activity: Optional[datetime] = None
        self.current_state: IdlenessState = IdlenessState.ACTIVE
        self.activity_history: List[OperatorActivity] = []

        # Data storage
        self.data_dir = project_root / "data" / "operator_idleness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "idleness_state.json"

        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_running = False
        self.lock = threading.Lock()

        # Load saved state
        self._load_state()

        # Start monitoring
        self.start_monitoring()

        self.logger.info(f"✅ Operator Idleness Restriction initialized (timeout: {idle_timeout_seconds}s = {idle_timeout_seconds/60:.1f} minutes)")
        self.logger.info(f"   🛡️  @OP gets minimum {min_breather_seconds/60:.0f}-minute breather before restrictions apply")

    def record_activity(self, activity_type: str, source: str = "unknown", metadata: Optional[Dict[str, Any]] = None):
        """
        Record operator activity

        Args:
            activity_type: Type of activity (keyboard, mouse, voice, chat, etc.)
            source: Source of activity
            metadata: Additional metadata
        """
        with self.lock:
            now = datetime.now()
            self.last_activity = now

            activity = OperatorActivity(
                timestamp=now,
                activity_type=activity_type,
                source=source,
                metadata=metadata or {}
            )

            self.activity_history.append(activity)

            # Keep only last 1000 activities
            if len(self.activity_history) > 1000:
                self.activity_history = self.activity_history[-1000:]

            # Update state
            if self.current_state == IdlenessState.IDLE or self.current_state == IdlenessState.RESTRICTED:
                self.current_state = IdlenessState.ACTIVE
                self.logger.info("✅ Operator activity detected - state changed to ACTIVE")

            # Save state
            self._save_state()

    def check_idleness(self) -> IdlenessState:
        """
        Check current idleness state

        Returns:
            Current idleness state
        """
        with self.lock:
            if not self.restriction.restriction_enabled:
                return IdlenessState.ACTIVE

            if not self.last_activity:
                # No activity recorded yet - assume idle
                if self.current_state != IdlenessState.RESTRICTED:
                    self.current_state = IdlenessState.IDLE
                return self.current_state

            now = datetime.now()
            time_since_activity = (now - self.last_activity).total_seconds()

            if time_since_activity >= self.restriction.idle_timeout_seconds:
                # Operator is idle - restrict actions
                if self.current_state != IdlenessState.RESTRICTED:
                    self.current_state = IdlenessState.RESTRICTED
                    self.logger.warning(
                        f"⚠️  Operator idle for {time_since_activity:.0f}s - "
                        f"TEMPORARY RESTRICTIONS PLACED ON JARVIS/AI/MANUS (NOT ON @OP)"
                    )
            elif time_since_activity >= self.restriction.idle_timeout_seconds * 0.8:
                # Approaching idle threshold
                if self.current_state == IdlenessState.ACTIVE:
                    self.current_state = IdlenessState.IDLE
                    self.logger.info(
                        f"ℹ️  Operator approaching idle ({time_since_activity:.0f}s) - "
                        f"will temporarily restrict JARVIS/AI/MANUS (NOT @OP) in {self.restriction.idle_timeout_seconds - time_since_activity:.0f}s"
                    )
            else:
                # Operator is active
                if self.current_state != IdlenessState.ACTIVE:
                    self.current_state = IdlenessState.ACTIVE

            return self.current_state

    def is_action_allowed(self, action_type: str, emergency: bool = False) -> bool:
        """
        Check if an action is allowed given current idleness state

        Args:
            action_type: Type of action (ai_action, jarvis_action, manus_action, etc.)
            emergency: Whether this is an emergency action (overrides restriction)

        Returns:
            True if action is allowed, False otherwise
        """
        # Check current state
        state = self.check_idleness()

        # Emergency actions are always allowed
        if emergency and self.restriction.allow_emergency:
            return True

        # Active state - all actions allowed
        if state == IdlenessState.ACTIVE:
            return True

        # Idle state - warn but allow
        if state == IdlenessState.IDLE:
            self.logger.warning(f"⚠️  Operator idle - action '{action_type}' allowed but monitored")
            return True

        # Restricted state - block restricted actions
        if state == IdlenessState.RESTRICTED:
            if action_type in self.restriction.restricted_actions:
                self.logger.warning(
                    f"🚫 BLOCKED: JARVIS/AI/MANUS action '{action_type}' - Operator idle for >{self.restriction.idle_timeout_seconds}s "
                    f"(TEMPORARY RESTRICTION ON JARVIS, NOT ON @OP)"
                )
                return False

        return True

    def restrict_action(self, action_type: str, action_func: Callable, *args, **kwargs) -> Any:
        """
        Execute an action with idleness restriction check

        Args:
            action_type: Type of action
            action_func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result or None if blocked
        """
        emergency = kwargs.pop('emergency', False)

        if not self.is_action_allowed(action_type, emergency=emergency):
            return {
                'success': False,
                'blocked': True,
                'reason': f'Operator idle - JARVIS/AI/MANUS action {action_type} temporarily restricted (NOT @OP)',
                'idle_duration': self._get_idle_duration()
            }

        # Execute action
        try:
            result = action_func(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Error executing action {action_type}: {e}")
            raise

    def _get_idle_duration(self) -> float:
        """Get current idle duration in seconds"""
        if not self.last_activity:
            return float('inf')

        return (datetime.now() - self.last_activity).total_seconds()

    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitor_running:
            return

        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("✅ Idleness monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring thread"""
        self.monitor_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("⏹️  Idleness monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitor_running:
            try:
                self.check_idleness()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)

    def _save_state(self):
        """Save current state to file"""
        try:
            state_data = {
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'current_state': self.current_state.value,
                'idle_timeout_seconds': self.restriction.idle_timeout_seconds,
                'restriction_enabled': self.restriction.restriction_enabled,
                'timestamp': datetime.now().isoformat()
            }

            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save state: {e}")

    def _load_state(self):
        """Load saved state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)

                if state_data.get('last_activity'):
                    self.last_activity = datetime.fromisoformat(state_data['last_activity'])

                state_str = state_data.get('current_state', 'active')
                self.current_state = IdlenessState(state_str)

                # Update timeout if changed
                if 'idle_timeout_seconds' in state_data:
                    self.restriction.idle_timeout_seconds = state_data['idle_timeout_seconds']

                self.logger.info(f"✅ Loaded saved state: {self.current_state.value}")
        except Exception as e:
            self.logger.warning(f"Failed to load state: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        state = self.check_idleness()
        idle_duration = self._get_idle_duration()

        # Calculate breather information
        if idle_duration != float('inf'):
            breather_remaining = max(0, self.restriction.idle_timeout_seconds - idle_duration)
            time_until_restriction = max(0, self.restriction.idle_timeout_seconds - idle_duration)
        else:
            breather_remaining = self.restriction.idle_timeout_seconds
            time_until_restriction = self.restriction.idle_timeout_seconds

        return {
            'state': state.value,
            'idle_duration_seconds': idle_duration if idle_duration != float('inf') else None,
            'idle_duration_minutes': (idle_duration / 60) if idle_duration != float('inf') else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'restriction_enabled': self.restriction.restriction_enabled,
            'idle_timeout_seconds': self.restriction.idle_timeout_seconds,
            'idle_timeout_minutes': self.restriction.idle_timeout_seconds / 60,
            'restricted_actions': self.restriction.restricted_actions,
            'actions_blocked': state == IdlenessState.RESTRICTED,
            'breather_remaining_seconds': breather_remaining,
            'breather_remaining_minutes': breather_remaining / 60,
            'time_until_restriction_seconds': time_until_restriction,
            'time_until_restriction_minutes': time_until_restriction / 60
        }


# Global instance
_global_restriction: Optional[OperatorIdlenessRestriction] = None


def get_operator_idleness_restriction(project_root: Optional[Path] = None) -> OperatorIdlenessRestriction:
    try:
        """Get or create global operator idleness restriction instance"""
        global _global_restriction

        if _global_restriction is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_restriction = OperatorIdlenessRestriction(project_root)

        return _global_restriction


    except Exception as e:
        logger.error(f"Error in get_operator_idleness_restriction: {e}", exc_info=True)
        raise
def check_action_allowed(action_type: str, emergency: bool = False) -> bool:
    """Convenience function to check if action is allowed"""
    restriction = get_operator_idleness_restriction()
    return restriction.is_action_allowed(action_type, emergency=emergency)


def record_operator_activity(activity_type: str, source: str = "unknown", metadata: Optional[Dict[str, Any]] = None):
    """Convenience function to record operator activity"""
    restriction = get_operator_idleness_restriction()
    restriction.record_activity(activity_type, source, metadata)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Operator Idleness Restriction System")
        parser.add_argument("--status", action="store_true", help="Show current status")
        parser.add_argument("--record", type=str, help="Record activity (activity_type)")
        parser.add_argument("--check", type=str, help="Check if action is allowed (action_type)")
        parser.add_argument("--timeout", type=int, default=600, help="Idle timeout in seconds (default: 600)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        restriction = OperatorIdlenessRestriction(project_root, idle_timeout_seconds=args.timeout)

        if args.status:
            status = restriction.get_status()
            print("\n" + "="*80)
            print("OPERATOR IDLENESS RESTRICTION STATUS")
            print("="*80)
            print(f"State: {status['state']}")
            if status['idle_duration_seconds']:
                print(f"Idle Duration: {status['idle_duration_seconds']:.0f}s ({status['idle_duration_minutes']:.1f} minutes)")
            else:
                print(f"Idle Duration: N/A")
            print(f"Last Activity: {status['last_activity']}")
            print(f"Restriction Enabled: {status['restriction_enabled']}")
            print(f"Idle Timeout: {status['idle_timeout_seconds']}s ({status['idle_timeout_minutes']:.1f} minutes)")
            print(f"Actions Blocked: {status['actions_blocked']}")

            # Show breather status
            print("\n🛡️  @OP BREATHER STATUS:")
            if status['breather_remaining_seconds'] > 0:
                print(f"   ✅ @OP still has {status['breather_remaining_minutes']:.1f} minutes of breather time")
                print(f"   Time Until Restriction: {status['time_until_restriction_seconds']:.0f}s ({status['time_until_restriction_minutes']:.1f} minutes)")
            else:
                print(f"   ✅ @OP had full {status['idle_timeout_minutes']:.1f}-minute breather")
                if status['idle_duration_seconds']:
                    print(f"   🚫 Restrictions now active (idle for {status['idle_duration_minutes']:.1f} minutes)")

            print("="*80)

        if args.record:
            restriction.record_activity(args.record)
            print(f"✅ Recorded activity: {args.record}")

        if args.check:
            allowed = restriction.is_action_allowed(args.check)
            print(f"{'✅ ALLOWED' if allowed else '🚫 BLOCKED'}: {args.check}")

        if not any([args.status, args.record, args.check]):
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()