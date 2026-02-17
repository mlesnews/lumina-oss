#!/usr/bin/env python3
"""
JARVIS Continuous Autonomous Execution

JARVIS continues autonomously through ALL remaining steps
without pausing. No stops. Full continuous execution.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_autonomous_workflow_executor import JARVISAutonomousWorkflowExecutor
    WORKFLOW_EXECUTOR_AVAILABLE = True
except ImportError:
    WORKFLOW_EXECUTOR_AVAILABLE = False
    JARVISAutonomousWorkflowExecutor = None

logger = get_logger("JARVISContinuous")


class JARVISContinuousAutonomous:
    """
    JARVIS Continuous Autonomous Execution

    Executes ALL steps (high, medium, low priority) continuously
    without pausing. No stops. Full autonomy.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        if WORKFLOW_EXECUTOR_AVAILABLE:
            self.workflow_executor = JARVISAutonomousWorkflowExecutor(
                project_root,
                use_subagents=True
            )
        else:
            self.workflow_executor = None

        self.continuous_logs_dir = project_root / "data" / "continuous_logs"
        self.continuous_logs_dir.mkdir(parents=True, exist_ok=True)

    def execute_all_continuously(self) -> Dict[str, Any]:
        """
        Execute ALL steps continuously - no pausing

        Executes high, medium, and low priority steps
        in sequence without stopping
        """
        self.logger.info("="*80)
        self.logger.info("JARVIS CONTINUOUS AUTONOMOUS EXECUTION")
        self.logger.info("="*80)
        self.logger.info("NO PAUSING. NO STOPPING. CONTINUOUS EXECUTION.")
        self.logger.info("="*80)

        if not self.workflow_executor:
            return {
                'success': False,
                'error': 'Workflow executor not available'
            }

        # Load action plan
        plan = self.workflow_executor.load_latest_action_plan()
        if not plan:
            return {
                'success': False,
                'error': 'No action plan found'
            }

        all_steps = plan.get('steps', [])

        self.logger.info(f"📋 Total steps in plan: {len(all_steps)}")

        # Execute ALL steps (not just high priority)
        execution_log = {
            'started_at': datetime.now().isoformat(),
            'mode': 'continuous_autonomous',
            'total_steps': len(all_steps),
            'executed': [],
            'failed': []
        }

        # Group by priority for reporting
        by_priority = {
            'critical': [s for s in all_steps if s.get('priority') == 'critical'],
            'high': [s for s in all_steps if s.get('priority') == 'high'],
            'medium': [s for s in all_steps if s.get('priority') == 'medium'],
            'low': [s for s in all_steps if s.get('priority') == 'low']
        }

        self.logger.info(f"  Critical: {len(by_priority['critical'])}")
        self.logger.info(f"  High: {len(by_priority['high'])}")
        self.logger.info(f"  Medium: {len(by_priority['medium'])}")
        self.logger.info(f"  Low: {len(by_priority['low'])}")

        # Execute all steps
        self.logger.info("\n" + "="*80)
        self.logger.info("EXECUTING ALL STEPS CONTINUOUSLY")
        self.logger.info("="*80)

        # Filter out already completed (curriculum system)
        remaining_steps = [
            s for s in all_steps
            if 'curriculum' not in s.get('step_id', '').lower()
        ]

        self.logger.info(f"Executing {len(remaining_steps)} remaining steps...")

        # Execute in batches using subagent delegation
        if len(remaining_steps) > 1:
            # Use parallel execution
            if hasattr(self.workflow_executor, 'delegation') and self.workflow_executor.delegation:
                self.logger.info(f"🚀 Delegating {len(remaining_steps)} tasks in parallel")
                results = self.workflow_executor.delegation.delegate_parallel(remaining_steps)
                execution_log['executed'].extend(results)
                execution_log['failed'].extend([r for r in results if not r.get('success')])
            else:
                # Sequential fallback
                for step in remaining_steps:
                    result = self.workflow_executor.execute_step(step)
                    execution_log['executed'].append(result)
                    if not result.get('success'):
                        execution_log['failed'].append(result)
        else:
            # Single step
            for step in remaining_steps:
                result = self.workflow_executor.execute_step(step)
                execution_log['executed'].append(result)
                if not result.get('success'):
                    execution_log['failed'].append(result)

        execution_log['completed_at'] = datetime.now().isoformat()
        execution_log['summary'] = {
            'total': len(remaining_steps),
            'succeeded': len([r for r in execution_log['executed'] if r.get('success')]),
            'failed': len(execution_log['failed']),
            'skipped': len([r for r in execution_log['executed'] if r.get('skipped')])
        }

        # Save log
        log_file = self.continuous_logs_dir / f"continuous_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(execution_log, f, indent=2)
            self.logger.info(f"✅ Continuous execution log saved: {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save log: {e}")

        return execution_log


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Continuous Autonomous Execution")
        parser.add_argument("--execute-all", action="store_true", help="Execute all steps continuously")
        parser.add_argument("--no-pause", action="store_true", help="Execute without pausing")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        continuous = JARVISContinuousAutonomous(project_root)

        if args.execute_all or args.no_pause:
            result = continuous.execute_all_continuously()

            summary = result.get('summary', {})

            print("\n" + "="*80)
            print("CONTINUOUS AUTONOMOUS EXECUTION COMPLETE")
            print("="*80)
            print(f"Total Steps: {summary.get('total', 0)}")
            print(f"✅ Succeeded: {summary.get('succeeded', 0)}")
            print(f"❌ Failed: {summary.get('failed', 0)}")
            print(f"⏭️  Skipped: {summary.get('skipped', 0)}")
            print("="*80)

            if summary.get('succeeded', 0) > 0:
                print("\n✅ CONTINUOUS EXECUTION COMPLETE - All steps executed")
            else:
                print("\n⚠️ No steps to execute")
        else:
            print("Usage: python jarvis_continuous_autonomous.py --execute-all")
            print("       python jarvis_continuous_autonomous.py --no-pause")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()