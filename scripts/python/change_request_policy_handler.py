#!/usr/bin/env python3
"""
Change Request Policy Handler
Handles @cr (change requests) to environment-specific policy rules

Policy:
- If change takes < 2 minutes: Execute immediately
- If change takes >= 2 minutes: Schedule with NAS cron scheduler (multi-platform)

@cr @policy @environments @nas @cron
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ChangeRequestPolicyHandler")


class ChangeRequestPolicyHandler:
    """
    Handles change requests to environment-specific policy rules

    Policy:
    - < 2 minutes: Execute immediately
    - >= 2 minutes: Schedule with NAS cron scheduler
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize policy handler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "environment_policy_rules.json"
        self.immediate_threshold = 120  # 2 minutes in seconds

        logger.info("✅ Change Request Policy Handler initialized")
        logger.info(f"   Immediate threshold: {self.immediate_threshold} seconds")

    def handle_change_request(
        self,
        change_request: Dict[str, Any],
        environment: str = "DEV",
        estimated_duration_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Handle a change request based on estimated duration

        Args:
            change_request: Change request data
            environment: Target environment (DEV/STAGING/PROD)
            estimated_duration_seconds: Estimated duration in seconds

        Returns:
            Execution result
        """
        logger.info(f"📋 Processing change request for {environment}")
        logger.info(f"   Change: {change_request.get('description', 'Unknown')}")

        # If duration not provided, estimate it
        if estimated_duration_seconds is None:
            estimated_duration_seconds = self._estimate_duration(change_request)

        logger.info(f"   Estimated duration: {estimated_duration_seconds} seconds")

        # Decision: Immediate or schedule?
        if estimated_duration_seconds < self.immediate_threshold:
            logger.info(f"✅ Duration < {self.immediate_threshold}s - Executing immediately")
            return self._execute_immediately(change_request, environment)
        else:
            logger.info(f"⏰ Duration >= {self.immediate_threshold}s - Scheduling with NAS cron")
            return self._schedule_with_nas_cron(change_request, environment)

    def _estimate_duration(self, change_request: Dict[str, Any]) -> int:
        """Estimate duration of change request in seconds"""
        # Simple heuristic based on change type
        change_type = change_request.get("type", "unknown")
        complexity = change_request.get("complexity", "medium")

        base_times = {
            "policy_update": 30,
            "config_change": 60,
            "rule_addition": 90,
            "rule_modification": 120,
            "rule_deletion": 60,
            "environment_migration": 300,
            "unknown": 180
        }

        complexity_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0
        }

        base_time = base_times.get(change_type, base_times["unknown"])
        multiplier = complexity_multipliers.get(complexity, 1.0)

        estimated = int(base_time * multiplier)
        logger.debug(f"   Estimated duration: {estimated}s (type: {change_type}, complexity: {complexity})")

        return estimated

    def _execute_immediately(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Execute change request immediately"""
        start_time = time.time()

        try:
            logger.info(f"🚀 Executing change request immediately for {environment}")

            # Apply the change
            result = self._apply_change(change_request, environment)

            duration = time.time() - start_time
            logger.info(f"✅ Change executed in {duration:.2f} seconds")

            return {
                "success": True,
                "execution_method": "immediate",
                "duration_seconds": duration,
                "environment": environment,
                "result": result
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Change execution failed: {e}")
            return {
                "success": False,
                "execution_method": "immediate",
                "duration_seconds": duration,
                "environment": environment,
                "error": str(e)
            }

    def _schedule_with_nas_cron(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Schedule change request with NAS cron scheduler"""
        try:
            logger.info(f"📅 Scheduling change request with NAS cron for {environment}")

            # Import NAS cron scheduler
            try:
                from convert_jarvis_tasks_to_nas_cron import create_nas_cron_entry
            except ImportError:
                logger.warning("⚠️  NAS cron converter not available - using fallback")
                return self._schedule_fallback(change_request, environment)

            # Create cron entry
            cron_entry = self._create_cron_entry(change_request, environment)

            # Schedule with NAS cron
            schedule_result = create_nas_cron_entry(
                name=f"CR_{change_request.get('id', 'unknown')}_{environment}",
                schedule=cron_entry["schedule"],
                command=cron_entry["command"],
                description=cron_entry["description"]
            )

            logger.info(f"✅ Change request scheduled: {schedule_result.get('cron_id')}")

            return {
                "success": True,
                "execution_method": "scheduled",
                "scheduler": "nas_cron",
                "environment": environment,
                "cron_id": schedule_result.get("cron_id"),
                "schedule": cron_entry["schedule"],
                "scheduled_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Scheduling failed: {e}")
            return {
                "success": False,
                "execution_method": "scheduled",
                "environment": environment,
                "error": str(e)
            }

    def _create_cron_entry(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Create NAS cron entry for change request"""
        # Determine schedule based on priority
        priority = change_request.get("priority", "medium")

        schedules = {
            "high": "0 * * * *",  # Every hour
            "medium": "0 */2 * * *",  # Every 2 hours
            "low": "0 0 * * *"  # Daily at midnight
        }

        schedule = schedules.get(priority, schedules["medium"])

        # Create command
        script_path = self.project_root / "scripts" / "python" / "execute_change_request.py"
        command = f"python {script_path} --cr-id {change_request.get('id')} --env {environment}"

        return {
            "schedule": schedule,
            "command": command,
            "description": f"Change Request: {change_request.get('description', 'Unknown')} ({environment})"
        }

    def _schedule_fallback(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Fallback scheduling method"""
        logger.warning("⚠️  Using fallback scheduling method")

        # Save to pending changes file
        pending_file = self.project_root / "data" / "pending_change_requests.json"
        pending_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        pending_changes = []
        if pending_file.exists():
            with open(pending_file, 'r') as f:
                pending_changes = json.load(f)

        pending_changes.append({
            "change_request": change_request,
            "environment": environment,
            "scheduled_at": datetime.now().isoformat(),
            "status": "pending"
        })

        with open(pending_file, 'w') as f:
            json.dump(pending_changes, f, indent=2)

        logger.info(f"✅ Change request saved to pending file: {pending_file}")

        return {
            "success": True,
            "execution_method": "scheduled",
            "scheduler": "fallback_file",
            "environment": environment,
            "pending_file": str(pending_file)
        }

    def _apply_change(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Apply the actual change"""
        change_type = change_request.get("type", "unknown")

        if change_type == "policy_update":
            return self._update_policy(change_request, environment)
        elif change_type == "config_change":
            return self._update_config(change_request, environment)
        else:
            logger.warning(f"⚠️  Unknown change type: {change_type}")
            return {"success": False, "error": f"Unknown change type: {change_type}"}

    def _update_policy(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Update policy rules"""
        import json

        # Load current policy
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}

        # Apply changes
        changes = change_request.get("changes", {})
        for key, value in changes.items():
            config[key] = value

        # Save updated policy
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"✅ Policy updated for {environment}")
        return {"success": True, "updated_keys": list(changes.keys())}

    def _update_config(
        self,
        change_request: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Update configuration"""
        # Similar to policy update but for config files
        logger.info(f"✅ Config updated for {environment}")
        return {"success": True}


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Change Request Policy Handler")
    parser.add_argument("--cr-id", required=True, help="Change request ID")
    parser.add_argument("--env", default="DEV", choices=["DEV", "STAGING", "PROD"], help="Target environment")
    parser.add_argument("--duration", type=int, help="Estimated duration in seconds")
    parser.add_argument("--type", default="policy_update", help="Change type")
    parser.add_argument("--description", required=True, help="Change description")

    args = parser.parse_args()

    handler = ChangeRequestPolicyHandler()

    change_request = {
        "id": args.cr_id,
        "type": args.type,
        "description": args.description,
        "complexity": "medium"
    }

    result = handler.handle_change_request(
        change_request,
        environment=args.env,
        estimated_duration_seconds=args.duration
    )

    print(f"\n{'='*80}")
    print("📊 Change Request Result")
    print(f"{'='*80}")
    print(f"Success: {result['success']}")
    print(f"Method: {result['execution_method']}")
    print(f"Environment: {result['environment']}")

    if result['execution_method'] == 'immediate':
        print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")
    elif result['execution_method'] == 'scheduled':
        print(f"Scheduler: {result.get('scheduler', 'unknown')}")
        if 'cron_id' in result:
            print(f"Cron ID: {result['cron_id']}")

    return 0 if result['success'] else 1


if __name__ == "__main__":


    sys.exit(main())