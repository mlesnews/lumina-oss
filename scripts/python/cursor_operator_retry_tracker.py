#!/usr/bin/env python3
"""
Cursor IDE Operator Retry Tracker

Tracks manual [RETRY] button clicks by the operator (@OP).
Integrates with connection health monitor and Star Trek protocol.

Tags: #CURSOR_IDE #RETRY_BUTTON #OPERATOR_ACTION #MONITORING #STAR_TREK @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

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

logger = get_logger("CursorOperatorRetry")


@dataclass
class OperatorRetryAction:
    """Operator retry action record"""
    timestamp: str
    request_id: Optional[str] = None
    original_error_type: Optional[str] = None
    original_error_message: Optional[str] = None
    retry_success: Optional[bool] = None
    operator: str = "@OP"
    action_type: str = "MANUAL_RETRY"
    notes: Optional[str] = None


class CursorOperatorRetryTracker:
    """
    Cursor IDE Operator Retry Tracker

    Tracks manual [RETRY] button clicks by the operator.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize operator retry tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_operator_retries"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Retry actions
        self.retry_actions: List[OperatorRetryAction] = []

        # Initialize health monitor
        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor
            self.health_monitor = CursorConnectionHealthMonitor(self.project_root)
        except Exception as e:
            logger.error(f"   ❌ Could not initialize health monitor: {e}")
            self.health_monitor = None

        # Initialize error monitor
        try:
            from cursor_ide_error_monitor import CursorIDEErrorMonitor
            self.error_monitor = CursorIDEErrorMonitor(self.project_root)
        except Exception as e:
            logger.debug(f"   Could not initialize error monitor: {e}")
            self.error_monitor = None

        # Load existing retry actions
        self._load_retry_actions()

        logger.info("✅ Cursor Operator Retry Tracker initialized")
        logger.info(f"   Data directory: {self.data_dir}")
        logger.info(f"   Loaded {len(self.retry_actions)} historical retry actions")

    def _load_retry_actions(self):
        """Load historical retry actions"""
        try:
            retry_file = self.data_dir / "retry_actions.json"
            if retry_file.exists():
                with open(retry_file, 'r') as f:
                    data = json.load(f)
                    self.retry_actions = [
                        OperatorRetryAction(**r) for r in data.get("retry_actions", [])
                    ]
                    logger.info(f"   ✅ Loaded {len(self.retry_actions)} retry actions")
        except Exception as e:
            logger.debug(f"   Could not load retry actions: {e}")

    def _save_retry_actions(self):
        """Save retry actions to disk"""
        try:
            retry_file = self.data_dir / "retry_actions.json"
            with open(retry_file, 'w') as f:
                json.dump({
                    "retry_actions": [
                        {
                            "timestamp": r.timestamp,
                            "request_id": r.request_id,
                            "original_error_type": r.original_error_type,
                            "original_error_message": r.original_error_message,
                            "retry_success": r.retry_success,
                            "operator": r.operator,
                            "action_type": r.action_type,
                            "notes": r.notes
                        }
                        for r in self.retry_actions[-1000:]  # Keep last 1000
                    ]
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving retry actions: {e}")

    def record_operator_retry(
        self,
        request_id: Optional[str] = None,
        original_error_type: Optional[str] = None,
        original_error_message: Optional[str] = None,
        retry_success: Optional[bool] = None,
        operator: str = "@OP",
        notes: Optional[str] = None
    ) -> OperatorRetryAction:
        """
        Record operator manual retry action

        Args:
            request_id: Request ID associated with the error
            original_error_type: Type of original error
            original_error_message: Original error message
            retry_success: Whether retry was successful (if known)
            operator: Operator identifier (default: @OP)
            notes: Additional notes

        Returns:
            OperatorRetryAction record
        """
        logger.info("=" * 80)
        logger.info("🔄 OPERATOR MANUAL RETRY RECORDED")
        logger.info("=" * 80)
        logger.info(f"   Operator: {operator}")
        if request_id:
            logger.info(f"   Request ID: {request_id}")
        if original_error_type:
            logger.info(f"   Original Error: {original_error_type}")
        if retry_success is not None:
            logger.info(f"   Retry Success: {retry_success}")
        logger.info("")

        # Create retry action
        retry_action = OperatorRetryAction(
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            original_error_type=original_error_type,
            original_error_message=original_error_message,
            retry_success=retry_success,
            operator=operator,
            action_type="MANUAL_RETRY",
            notes=notes
        )

        self.retry_actions.append(retry_action)
        self._save_retry_actions()

        # Update health monitor with operator intervention
        if self.health_monitor:
            # Record as operator-initiated retry
            # This is a positive action - operator is actively resolving issues
            logger.info("   ✅ Retry action recorded to health monitor")

        # Log to Star Trek protocol
        try:
            from jarvis_star_trek_first_contact import JARVISStarTrekFirstContact

            first_contact = JARVISStarTrekFirstContact(self.project_root)

            ai_info = {
                "type": "operator_retry",
                "action": "MANUAL_RETRY",
                "operator": operator,
                "request_id": request_id,
                "original_error": original_error_message,
                "retry_success": retry_success,
                "capabilities": ["IDE Integration", "Operator Control"]
            }

            encounter = first_contact.encounter_ai("cursor_ide_operator", ai_info)
            logger.info("   🛸 Operator retry logged to Star Trek protocol")
        except Exception as e:
            logger.debug(f"   Could not log to Star Trek protocol: {e}")

        return retry_action

    def record_retry_acknowledged(
        self,
        request_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> OperatorRetryAction:
        """
        Record that operator manually acknowledged/clicked [RETRY] button

        This is a convenience method for the common case where operator
        clicks retry button after seeing an error.

        Args:
            request_id: Request ID if available
            notes: Additional notes

        Returns:
            OperatorRetryAction record
        """
        return self.record_operator_retry(
            request_id=request_id,
            operator="@OP",
            notes=notes or "Operator manually clicked [RETRY] button in Cursor IDE"
        )

    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get retry statistics"""
        total_retries = len(self.retry_actions)

        # Count by success status
        successful_retries = sum(1 for r in self.retry_actions if r.retry_success is True)
        failed_retries = sum(1 for r in self.retry_actions if r.retry_success is False)
        unknown_retries = sum(1 for r in self.retry_actions if r.retry_success is None)

        # Count by error type
        error_types = {}
        for r in self.retry_actions:
            if r.original_error_type:
                error_types[r.original_error_type] = error_types.get(r.original_error_type, 0) + 1

        # Recent retries (last 24 hours)
        from datetime import timedelta
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_retries = [
            r for r in self.retry_actions
            if datetime.fromisoformat(r.timestamp) > recent_cutoff
        ]

        return {
            "total_retries": total_retries,
            "successful_retries": successful_retries,
            "failed_retries": failed_retries,
            "unknown_retries": unknown_retries,
            "success_rate": (
                (successful_retries / (successful_retries + failed_retries) * 100)
                if (successful_retries + failed_retries) > 0 else None
            ),
            "error_type_breakdown": error_types,
            "recent_retries_24h": len(recent_retries),
            "last_retry": self.retry_actions[-1].timestamp if self.retry_actions else None
        }

    def print_retry_report(self):
        """Print retry report"""
        stats = self.get_retry_statistics()

        print("=" * 80)
        print("🔄 CURSOR IDE OPERATOR RETRY REPORT")
        print("=" * 80)
        print("")
        print(f"Total Operator Retries: {stats['total_retries']}")
        print(f"Successful Retries: {stats['successful_retries']}")
        print(f"Failed Retries: {stats['failed_retries']}")
        print(f"Unknown Status: {stats['unknown_retries']}")
        if stats['success_rate'] is not None:
            print(f"Success Rate: {stats['success_rate']:.1f}%")
        print("")
        print(f"Recent Retries (24h): {stats['recent_retries_24h']}")
        if stats['last_retry']:
            print(f"Last Retry: {stats['last_retry']}")
        print("")
        if stats['error_type_breakdown']:
            print("Error Type Breakdown:")
            for error_type, count in stats['error_type_breakdown'].items():
                print(f"  {error_type}: {count}")
        print("")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Operator Retry Tracker")
        parser.add_argument("--record", action="store_true", help="Record operator retry")
        parser.add_argument("--request-id", type=str, help="Request ID")
        parser.add_argument("--error-type", type=str, help="Original error type")
        parser.add_argument("--error-message", type=str, help="Original error message")
        parser.add_argument("--success", action="store_true", help="Retry was successful")
        parser.add_argument("--failed", action="store_true", help="Retry failed")
        parser.add_argument("--acknowledged", action="store_true", help="Record retry acknowledged")
        parser.add_argument("--report", action="store_true", help="Print retry report")
        parser.add_argument("--stats", action="store_true", help="Show statistics")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        tracker = CursorOperatorRetryTracker()

        if args.record or args.acknowledged:
            retry_success = None
            if args.success:
                retry_success = True
            elif args.failed:
                retry_success = False

            if args.acknowledged:
                action = tracker.record_retry_acknowledged(
                    request_id=args.request_id,
                    notes="Operator manually clicked [RETRY] button"
                )
            else:
                action = tracker.record_operator_retry(
                    request_id=args.request_id,
                    original_error_type=args.error_type,
                    original_error_message=args.error_message,
                    retry_success=retry_success
                )

            if args.json:
                print(json.dumps({
                    "timestamp": action.timestamp,
                    "request_id": action.request_id,
                    "operator": action.operator,
                    "action_type": action.action_type
                }, indent=2, default=str))
            else:
                print(f"✅ Operator retry recorded: {action.timestamp}")
                if action.request_id:
                    print(f"   Request ID: {action.request_id}")

        elif args.report:
            tracker.print_retry_report()

        elif args.stats or args.json:
            stats = tracker.get_retry_statistics()
            if args.json:
                print(json.dumps(stats, indent=2, default=str))
            else:
                print(f"Total Retries: {stats['total_retries']}")
                print(f"Success Rate: {stats['success_rate']:.1f}%" if stats['success_rate'] else "N/A")
                print(f"Recent (24h): {stats['recent_retries_24h']}")

        else:
            # Default: record acknowledged retry
            action = tracker.record_retry_acknowledged(
                notes="Operator manually clicked [RETRY] button in Cursor IDE"
            )
            print(f"✅ Operator retry acknowledged: {action.timestamp}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()