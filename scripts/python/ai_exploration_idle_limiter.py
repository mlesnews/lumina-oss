#!/usr/bin/env python3
"""
AI Exploration Idle Time Limiter
Limits AI/JARVIS @SMART explorations to idle time > 5 minutes

Policy:
- Only run explorations during idle time > 5 minutes
- Do not interrupt active workflows
- Do not take over @op @input @manus @controls

@SMART @AI @JARVIS @idle @workflow @manus @controls
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIExplorationIdleLimiter")


class AIExplorationIdleLimiter:
    """
    Limits AI/JARVIS @SMART explorations to idle periods

    Policy:
    - Minimum idle time: 5 minutes (300 seconds)
    - Check workflow activity
    - Check user input
    - Check MANUS controls
    - Check operator controls
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize idle limiter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "environment_policy_rules.json"
        self.min_idle_seconds = 300  # 5 minutes

        # Activity tracking
        self.last_workflow_activity = None
        self.last_user_input = None
        self.last_manus_control = None
        self.last_operator_control = None

        # Activity timeouts
        self.workflow_timeout = 60
        self.input_timeout = 30
        self.manus_timeout = 30
        self.operator_timeout = 30

        logger.info("✅ AI Exploration Idle Limiter initialized")
        logger.info(f"   Minimum idle time: {self.min_idle_seconds} seconds (5 minutes)")

    def can_run_exploration(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if AI exploration can run (system is idle)

        Returns:
            (can_run, status_dict)
        """
        logger.debug("🔍 Checking if AI exploration can run...")

        # Check all activity sources
        workflow_active = self._check_workflow_activity()
        user_input_active = self._check_user_input()
        manus_active = self._check_manus_controls()
        operator_active = self._check_operator_controls()

        # Calculate idle time
        idle_time = self._calculate_idle_time()

        # Decision
        any_active = workflow_active or user_input_active or manus_active or operator_active
        idle_sufficient = idle_time >= self.min_idle_seconds

        can_run = not any_active and idle_sufficient

        status = {
            "can_run": can_run,
            "idle_time_seconds": idle_time,
            "idle_sufficient": idle_sufficient,
            "workflow_active": workflow_active,
            "user_input_active": user_input_active,
            "manus_active": manus_active,
            "operator_active": operator_active,
            "any_active": any_active,
            "reason": self._get_reason(can_run, any_active, idle_sufficient, idle_time)
        }

        if can_run:
            logger.info(f"✅ AI exploration allowed - Idle for {idle_time:.0f} seconds")
        else:
            logger.info(f"⏸️  AI exploration blocked - {status['reason']}")

        return can_run, status

    def _check_workflow_activity(self) -> bool:
        """Check if workflows are active"""
        try:
            # Check for active workflow files/sessions
            workflow_dir = self.project_root / "data" / "workflows"
            if workflow_dir.exists():
                # Check for recent workflow activity
                recent_files = [
                    f for f in workflow_dir.glob("*.json")
                    if f.stat().st_mtime > (time.time() - self.workflow_timeout)
                ]
                if recent_files:
                    self.last_workflow_activity = time.time()
                    logger.debug(f"   ⚠️  Workflow activity detected: {len(recent_files)} recent files")
                    return True

            # Check if last activity was recent
            if self.last_workflow_activity:
                if time.time() - self.last_workflow_activity < self.workflow_timeout:
                    return True

            return False

        except Exception as e:
            logger.warning(f"   ⚠️  Error checking workflow activity: {e}")
            return False  # Assume not active on error

    def _check_user_input(self) -> bool:
        """Check if user input is active"""
        try:
            # Check for recent user input files
            input_dir = self.project_root / "data" / "user_input"
            if input_dir.exists():
                recent_files = [
                    f for f in input_dir.glob("*.json")
                    if f.stat().st_mtime > (time.time() - self.input_timeout)
                ]
                if recent_files:
                    self.last_user_input = time.time()
                    logger.debug(f"   ⚠️  User input detected: {len(recent_files)} recent files")
                    return True

            if self.last_user_input:
                if time.time() - self.last_user_input < self.input_timeout:
                    return True

            return False

        except Exception as e:
            logger.warning(f"   ⚠️  Error checking user input: {e}")
            return False

    def _check_manus_controls(self) -> bool:
        """Check if MANUS controls are active"""
        try:
            # Check MANUS control files
            manus_dir = self.project_root / "data" / "manus"
            if manus_dir.exists():
                recent_files = [
                    f for f in manus_dir.glob("*.json")
                    if f.stat().st_mtime > (time.time() - self.manus_timeout)
                ]
                if recent_files:
                    self.last_manus_control = time.time()
                    logger.debug(f"   ⚠️  MANUS controls active: {len(recent_files)} recent files")
                    return True

            if self.last_manus_control:
                if time.time() - self.last_manus_control < self.manus_timeout:
                    return True

            return False

        except Exception as e:
            logger.warning(f"   ⚠️  Error checking MANUS controls: {e}")
            return False

    def _check_operator_controls(self) -> bool:
        """Check if operator controls are active"""
        try:
            # Check operator control files
            operator_dir = self.project_root / "data" / "operator"
            if operator_dir.exists():
                recent_files = [
                    f for f in operator_dir.glob("*.json")
                    if f.stat().st_mtime > (time.time() - self.operator_timeout)
                ]
                if recent_files:
                    self.last_operator_control = time.time()
                    logger.debug(f"   ⚠️  Operator controls active: {len(recent_files)} recent files")
                    return True

            if self.last_operator_control:
                if time.time() - self.last_operator_control < self.operator_timeout:
                    return True

            return False

        except Exception as e:
            logger.warning(f"   ⚠️  Error checking operator controls: {e}")
            return False

    def _calculate_idle_time(self) -> float:
        """Calculate current idle time in seconds"""
        # Get most recent activity
        activities = [
            self.last_workflow_activity,
            self.last_user_input,
            self.last_manus_control,
            self.last_operator_control
        ]

        # Filter out None values
        activities = [a for a in activities if a is not None]

        if not activities:
            # No recorded activity - assume long idle
            return float('inf')

        # Most recent activity
        most_recent = max(activities)
        idle_time = time.time() - most_recent

        return idle_time

    def _get_reason(
        self,
        can_run: bool,
        any_active: bool,
        idle_sufficient: bool,
        idle_time: float
    ) -> str:
        """Get reason for allow/deny"""
        if can_run:
            return f"System idle for {idle_time:.0f} seconds (>= {self.min_idle_seconds}s)"

        if any_active:
            reasons = []
            if self._check_workflow_activity():
                reasons.append("workflow active")
            if self._check_user_input():
                reasons.append("user input active")
            if self._check_manus_controls():
                reasons.append("MANUS controls active")
            if self._check_operator_controls():
                reasons.append("operator controls active")
            return f"System active: {', '.join(reasons)}"

        if not idle_sufficient:
            return f"Idle time insufficient: {idle_time:.0f}s < {self.min_idle_seconds}s"

        return "Unknown reason"

    def wait_for_idle(self, max_wait_seconds: int = 3600) -> bool:
        """
        Wait for system to become idle

        Args:
            max_wait_seconds: Maximum time to wait

        Returns:
            True if idle achieved, False if timeout
        """
        logger.info(f"⏳ Waiting for idle (max {max_wait_seconds}s)...")

        start_time = time.time()
        check_interval = 10  # Check every 10 seconds

        while time.time() - start_time < max_wait_seconds:
            can_run, status = self.can_run_exploration()

            if can_run:
                logger.info("✅ System is now idle - exploration can proceed")
                return True

            logger.debug(f"   Still active: {status['reason']}")
            time.sleep(check_interval)

        logger.warning(f"⏰ Timeout waiting for idle after {max_wait_seconds}s")
        return False


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Exploration Idle Limiter")
    parser.add_argument("--check", action="store_true", help="Check if exploration can run")
    parser.add_argument("--wait", action="store_true", help="Wait for idle time")
    parser.add_argument("--max-wait", type=int, default=3600, help="Max wait time in seconds")

    args = parser.parse_args()

    limiter = AIExplorationIdleLimiter()

    if args.check:
        can_run, status = limiter.can_run_exploration()

        print(f"\n{'='*80}")
        print("📊 AI Exploration Status")
        print(f"{'='*80}")
        print(f"Can Run: {'✅ YES' if can_run else '❌ NO'}")
        print(f"Idle Time: {status['idle_time_seconds']:.0f} seconds")
        print(f"Idle Sufficient: {'✅' if status['idle_sufficient'] else '❌'}")
        print(f"\nActivity Status:")
        print(f"  Workflow: {'🔴 Active' if status['workflow_active'] else '🟢 Idle'}")
        print(f"  User Input: {'🔴 Active' if status['user_input_active'] else '🟢 Idle'}")
        print(f"  MANUS: {'🔴 Active' if status['manus_active'] else '🟢 Idle'}")
        print(f"  Operator: {'🔴 Active' if status['operator_active'] else '🟢 Idle'}")
        print(f"\nReason: {status['reason']}")

        return 0 if can_run else 1

    if args.wait:
        success = limiter.wait_for_idle(args.max_wait)
        return 0 if success else 1

    print("Use --check or --wait")
    return 1


if __name__ == "__main__":


    sys.exit(main())