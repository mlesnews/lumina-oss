#!/usr/bin/env python3
"""
NAS KronScheduler Integration - Autonomous AI Agent Workflow

Schedules autonomous AI agent workflow as 1-3 hourly job based on:
- Reasonable and applicable criteria
- Dynamic scaling module
- Smart load balancing with @AIQ fallback
- Change management workflow processing

Tags: #NAS #KRONSCHEDULER #AUTONOMOUS_AI #DYNAMIC_SCALING #LOAD_BALANCING #CHANGE_MANAGEMENT @JARVIS @AIQ @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NASKronSchedulerIntegration")

# Import required modules
try:
    from autonomous_ai_agent import AutonomousAIAgent
    AUTONOMOUS_AGENT_AVAILABLE = True
except ImportError:
    AUTONOMOUS_AGENT_AVAILABLE = False
    logger.warning("   ⚠️  Autonomous AI Agent not available")

try:
    from aiq_fallback_decisioning import AIQFallbackDecisioning
    AIQ_AVAILABLE = True
except ImportError:
    AIQ_AVAILABLE = False
    logger.warning("   ⚠️  @AIQ Fallback Decisioning not available")

try:
    from change_management_workflow import ChangeManagementWorkflow
    CHANGE_MGMT_AVAILABLE = True
except ImportError:
    CHANGE_MGMT_AVAILABLE = False
    logger.warning("   ⚠️  Change Management Workflow not available")


class NASKronSchedulerIntegration:
    """
    NAS KronScheduler Integration

    Schedules autonomous AI agent workflow with:
    - 1-3 hourly intervals (dynamic scaling)
    - Smart load balancing
    - @AIQ fallback decisioning
    - Change management processing
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize NAS KronScheduler integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "nas_kronscheduler"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.autonomous_agent = AutonomousAIAgent(project_root) if AUTONOMOUS_AGENT_AVAILABLE else None
        self.aiq = AIQFallbackDecisioning(project_root) if AIQ_AVAILABLE else None
        self.change_mgmt = ChangeManagementWorkflow(project_root) if CHANGE_MGMT_AVAILABLE else None

        # Dynamic scaling configuration
        self.min_interval_hours = 1
        self.max_interval_hours = 3
        self.base_interval_hours = 2

        logger.info("✅ NAS KronScheduler Integration initialized")
        logger.info("   Dynamic scaling: 1-3 hours")
        logger.info("   Smart load balancing: ACTIVE")
        logger.info("   @AIQ fallback: " + ("✅" if AIQ_AVAILABLE else "❌"))
        logger.info("   Change management: " + ("✅" if CHANGE_MGMT_AVAILABLE else "❌"))

    def calculate_interval(self) -> float:
        """
        Calculate dynamic interval (1-3 hours) based on criteria

        Returns:
            Interval in hours
        """
        if not self.aiq:
            return self.base_interval_hours

        # Check system load
        load_status = self.aiq.check_system_load()

        # Adjust interval based on load
        if load_status.get("needs_fallback", False):
            # High load - increase interval (less frequent)
            interval = self.max_interval_hours
            logger.info(f"   📊 High load detected - interval: {interval} hours")
        elif load_status.get("optimal", False):
            # Optimal load - decrease interval (more frequent)
            interval = self.min_interval_hours
            logger.info(f"   📊 Optimal load - interval: {interval} hours")
        else:
            # Medium load - use base interval
            interval = self.base_interval_hours
            logger.info(f"   📊 Medium load - interval: {interval} hours")

        return interval

    def execute_workflow(
        self,
        force: bool = False,
        max_items: int = 10
    ) -> Dict[str, Any]:
        """
        Execute autonomous AI agent workflow

        Args:
            force: Force execution regardless of conditions
            max_items: Maximum TODOs to work on

        Returns:
            Execution result
        """
        logger.info("=" * 80)
        logger.info("🚀 NAS KRONSCHEDULER - AUTONOMOUS AI AGENT WORKFLOW")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": f"nas_kron_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "interval_hours": self.calculate_interval(),
            "load_balanced": False,
            "aiq_fallback_used": False,
            "todos_worked_on": 0,
            "changes_detected": 0,
            "change_management_processed": False,
            "errors": []
        }

        # Step 1: Check system load and decide on execution method
        logger.info("📋 Step 1: Smart Load Balancing Check")
        logger.info("")

        if self.aiq:
            load_status = self.aiq.check_system_load()
            result["load_status"] = load_status

            if load_status.get("needs_fallback", False) and not force:
                logger.info("   ⚠️  High system load - using @AIQ fallback")
                result["aiq_fallback_used"] = True
                result["load_balanced"] = True

                # Use lightweight execution
                decision = self.aiq.make_decision(
                    context="Execute autonomous work under high load",
                    options=[
                        {"id": "lightweight", "priority": 1, "resource_cost": 20},
                        {"id": "defer", "priority": 2, "resource_cost": 5}
                    ]
                )

                if decision.get("selected_option", {}).get("id") == "defer":
                    logger.info("   ⏸️  Deferring execution due to high load")
                    result["deferred"] = True
                    result["next_interval_hours"] = self.max_interval_hours
                    return result
        logger.info("")

        # Step 2: Execute autonomous work
        logger.info("📋 Step 2: Executing Autonomous Work")
        logger.info("")

        if self.autonomous_agent:
            try:
                # Force work mode for scheduled execution
                original_detect = self.autonomous_agent.detect_idle_time
                self.autonomous_agent.detect_idle_time = lambda: (True, 10.0)

                work_result = self.autonomous_agent.work_independently(max_items=max_items)
                self.autonomous_agent.detect_idle_time = original_detect

                result["todos_worked_on"] = work_result.get("todos_worked_on", 0)
                result["roadblocks_identified"] = work_result.get("roadblocks_identified", 0)
                result["roadblocks_addressed"] = work_result.get("roadblocks_addressed", 0)
                result["work_result"] = work_result

                logger.info(f"   ✅ Worked on {result['todos_worked_on']} TODOs")
                logger.info(f"   ⚠️  Roadblocks: {result['roadblocks_identified']}")
                logger.info(f"   ✅ Addressed: {result['roadblocks_addressed']}")
            except Exception as e:
                logger.error(f"   ❌ Autonomous work failed: {e}")
                result["errors"].append(f"Autonomous work: {str(e)}")
        logger.info("")

        # Step 3: Process changes (Change Management)
        logger.info("📋 Step 3: Change Management Processing")
        logger.info("")

        if self.change_mgmt and result.get("todos_worked_on", 0) > 0:
            try:
                # Detect changes made
                changes = self.change_mgmt.detect_changes()
                result["changes_detected"] = len(changes.get("changes", []))

                if result["changes_detected"] > 0:
                    logger.info(f"   📋 Changes detected: {result['changes_detected']}")

                    # Process through change management workflow
                    cm_result = self.change_mgmt.process_changes(changes)
                    result["change_management_processed"] = True
                    result["change_management_result"] = cm_result

                    logger.info("   ✅ Change management workflow processed")
                    logger.info("   📋 @HELPDESK #END2END integration active")
                else:
                    logger.info("   ✅ No changes detected")
            except Exception as e:
                logger.warning(f"   ⚠️  Change management failed: {e}")
                result["errors"].append(f"Change management: {str(e)}")
        logger.info("")

        # Save result
        result_file = self.data_dir / f"execution_{result['execution_id']}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        logger.info("=" * 80)
        logger.info("✅ NAS KRONSCHEDULER EXECUTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Interval: {result['interval_hours']} hours")
        logger.info(f"   TODOs worked on: {result['todos_worked_on']}")
        logger.info(f"   Changes detected: {result['changes_detected']}")
        logger.info(f"   Change management: {result['change_management_processed']}")
        logger.info(f"   Result saved: {result_file.name}")
        logger.info("")

        return result

    def create_kron_job(
        self,
        job_name: str = "LUMINA-Autonomous-AI-Agent",
        description: str = "LUMINA: Autonomous AI Agent Workflow with Dynamic Scaling"
    ) -> Dict[str, Any]:
        """
        Create KronScheduler job configuration

        Args:
            job_name: Job name
            description: Job description

        Returns:
            Job configuration
        """
        interval = self.calculate_interval()

        job_config = {
            "job_name": job_name,
            "description": description,
            "script": str(self.project_root / "scripts" / "python" / "nas_kronscheduler_integration.py"),
            "args": ["--execute"],
            "schedule": {
                "type": "interval",
                "interval_hours": interval,
                "dynamic_scaling": True,
                "min_interval_hours": self.min_interval_hours,
                "max_interval_hours": self.max_interval_hours
            },
            "criteria": {
                "system_load_check": True,
                "smart_load_balancing": True,
                "aiq_fallback": True,
                "change_management": True
            },
            "tags": [
                "#DECISIONING",
                "#TROUBLESHOOTING",
                "#LOAD_BALANCING",
                "#DYNAMIC_SCALING",
                "#CHANGE_MANAGEMENT",
                "@AIQ",
                "@JARVIS",
                "@HELPDESK",
                "#END2END"
            ],
            "enabled": True
        }

        # Save job config
        config_file = self.data_dir / "kron_job_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(job_config, f, indent=2, ensure_ascii=False)

        logger.info("✅ KronScheduler job configuration created")
        logger.info(f"   Job: {job_name}")
        logger.info(f"   Interval: {interval} hours (dynamic: {self.min_interval_hours}-{self.max_interval_hours})")
        logger.info(f"   Config saved: {config_file.name}")

        return job_config


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="NAS KronScheduler Integration")
    parser.add_argument("--execute", action="store_true", help="Execute workflow")
    parser.add_argument("--create-job", action="store_true", help="Create KronScheduler job")
    parser.add_argument("--force", action="store_true", help="Force execution")
    parser.add_argument("--max-items", type=int, default=10, help="Max TODOs to work on")

    args = parser.parse_args()

    integration = NASKronSchedulerIntegration()

    if args.create_job:
        integration.create_kron_job()
    elif args.execute:
        integration.execute_workflow(force=args.force, max_items=args.max_items)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())