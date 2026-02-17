#!/usr/bin/env python3
"""
Workflow Continuous Improvement Loop
🔄 Exponential/Sequential Improvement with Infinite Dynamic Scaling

Orchestrates the complete continuous improvement cycle:
1. Collect telemetry from all workflows
2. Analyze for improvement opportunities
3. Auto-optimize workflows
4. Scale dynamically
5. Track results and iterate

#CONTINUOUSIMPROVEMENT #AUTOOPTIMIZATION #DYNAMICSCALING #TELEMETRY
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import time

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ContinuousImprovementLoop")

try:
    from syphon_workflow_telemetry_system import get_telemetry_system
    from workflow_improvement_engine import WorkflowImprovementEngine
    from workflow_auto_optimizer import WorkflowAutoOptimizer
    from workflow_dynamic_scaler import WorkflowDynamicScaler
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    logger.warning(f"Systems not available: {e}")


class WorkflowContinuousImprovementLoop:
    """
    Workflow Continuous Improvement Loop

    Orchestrates the complete cycle of telemetry collection,
    analysis, optimization, and scaling for exponential improvement.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Continuous Improvement Loop"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ContinuousImprovementLoop")

        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.telemetry = get_telemetry_system()
            self.improvement_engine = WorkflowImprovementEngine(project_root)
            self.optimizer = WorkflowAutoOptimizer(project_root)
            self.scaler = WorkflowDynamicScaler(project_root)
        else:
            self.telemetry = None
            self.improvement_engine = None
            self.optimizer = None
            self.scaler = None

        # Loop configuration
        self.config = {
            "min_executions_for_optimization": 10,
            "optimization_interval_hours": 24,
            "scaling_check_interval_hours": 1,
            "telemetry_flush_interval_minutes": 5
        }

        # Loop state
        self.loop_state_file = self.project_root / "data" / "workflow_improvements" / "loop_state.json"
        self.loop_state = self._load_state()

        logger.info("🔄 Continuous Improvement Loop initialized")

    def _load_state(self) -> Dict[str, Any]:
        """Load loop state"""
        if self.loop_state_file.exists():
            try:
                with open(self.loop_state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load loop state: {e}")
        return {
            "last_optimization": None,
            "last_scaling": None,
            "last_telemetry_flush": None,
            "total_cycles": 0,
            "total_improvements": 0,
            "total_scaling_events": 0
        }

    def _save_state(self) -> None:
        """Save loop state"""
        try:
            self.loop_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.loop_state_file, "w", encoding="utf-8") as f:
                json.dump(self.loop_state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save loop state: {e}")

    def run_complete_cycle(self) -> Dict[str, Any]:
        """
        Run complete improvement cycle

        Returns:
            Cycle results
        """
        if not SYSTEMS_AVAILABLE:
            return {"success": False, "error": "Systems not available"}

        cycle_start = datetime.now()
        results = {
            "success": True,
            "cycle_start": cycle_start.isoformat(),
            "telemetry_flushed": False,
            "workflows_optimized": 0,
            "workflows_scaled": 0,
            "improvements_applied": 0,
            "scaling_events": 0
        }

        try:
            # Step 1: Flush telemetry
            logger.info("📊 Step 1: Flushing telemetry...")
            if self.telemetry:
                count = self.telemetry.flush_events()
                results["telemetry_flushed"] = True
                results["events_flushed"] = count
                logger.info(f"✅ Flushed {count} telemetry events")

            # Step 2: Auto-optimize workflows
            logger.info("🚀 Step 2: Auto-optimizing workflows...")
            if self.optimizer:
                opt_results = self.optimizer.auto_optimize_all_workflows(
                    min_executions=self.config["min_executions_for_optimization"]
                )
                if opt_results.get("success"):
                    results["workflows_optimized"] = len(opt_results.get("optimized_workflows", []))
                    results["improvements_applied"] = opt_results.get("total_improvements", 0)
                    logger.info(f"✅ Optimized {results['workflows_optimized']} workflows")

            # Step 3: Auto-scale workflows
            logger.info("📈 Step 3: Auto-scaling workflows...")
            if self.scaler:
                scale_results = self.scaler.auto_scale_all_workflows()
                if scale_results.get("success"):
                    results["workflows_scaled"] = len(scale_results.get("scaled_workflows", []))
                    results["scaling_events"] = scale_results.get("total_scaling_events", 0)
                    logger.info(f"✅ Scaled {results['workflows_scaled']} workflows")

            # Update state
            self.loop_state["last_optimization"] = datetime.now().isoformat()
            self.loop_state["last_scaling"] = datetime.now().isoformat()
            self.loop_state["last_telemetry_flush"] = datetime.now().isoformat()
            self.loop_state["total_cycles"] += 1
            self.loop_state["total_improvements"] += results["improvements_applied"]
            self.loop_state["total_scaling_events"] += results["scaling_events"]
            self._save_state()

            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            results["cycle_duration_seconds"] = cycle_duration
            results["cycle_end"] = datetime.now().isoformat()

            logger.info(f"✅ Complete cycle finished in {cycle_duration:.2f}s")

        except Exception as e:
            logger.error(f"❌ Error in improvement cycle: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def run_continuous_loop(self, interval_hours: int = 24) -> None:
        """
        Run continuous improvement loop

        Args:
            interval_hours: Hours between cycles
        """
        logger.info(f"🔄 Starting continuous improvement loop (interval: {interval_hours}h)")

        try:
            while True:
                logger.info("="*70)
                logger.info("🔄 Starting improvement cycle...")

                results = self.run_complete_cycle()

                if results.get("success"):
                    logger.info("✅ Cycle completed successfully")
                else:
                    logger.error(f"❌ Cycle failed: {results.get('error')}")

                # Wait for next cycle
                wait_seconds = interval_hours * 3600
                logger.info(f"⏳ Waiting {interval_hours}h until next cycle...")
                time.sleep(wait_seconds)

        except KeyboardInterrupt:
            logger.info("🛑 Continuous loop stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in continuous loop: {e}")

    def get_improvement_summary(self) -> Dict[str, Any]:
        """Get summary of all improvements"""
        summary = {
            "loop_state": self.loop_state,
            "optimization_summary": {},
            "scaling_summary": {},
            "telemetry_summary": {}
        }

        if self.optimizer:
            summary["optimization_summary"] = self.optimizer.get_optimization_summary()

        if self.scaler:
            summary["scaling_summary"] = self.scaler.get_scaling_summary()

        if self.telemetry:
            export_result = self.telemetry.export_to_database()
            if export_result.get("success"):
                summary["telemetry_summary"] = export_result.get("exported", {})

        return summary


def main():
    try:
        """CLI interface for Continuous Improvement Loop"""
        import argparse

        parser = argparse.ArgumentParser(description="Workflow Continuous Improvement Loop")
        parser.add_argument("--run-cycle", action="store_true", help="Run one improvement cycle")
        parser.add_argument("--continuous", action="store_true", help="Run continuous loop")
        parser.add_argument("--interval", type=int, default=24, help="Hours between cycles (default: 24)")
        parser.add_argument("--summary", action="store_true", help="Show improvement summary")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        loop = WorkflowContinuousImprovementLoop()

        if args.summary:
            summary = loop.get_improvement_summary()
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print("\n🔄 Continuous Improvement Summary")
                print("="*70)
                print(f"Total Cycles: {summary['loop_state'].get('total_cycles', 0)}")
                print(f"Total Improvements: {summary['loop_state'].get('total_improvements', 0)}")
                print(f"Total Scaling Events: {summary['loop_state'].get('total_scaling_events', 0)}")
                print(f"\nLast Optimization: {summary['loop_state'].get('last_optimization')}")
                print(f"Last Scaling: {summary['loop_state'].get('last_scaling')}")
            return

        if args.continuous:
            loop.run_continuous_loop(interval_hours=args.interval)
            return

        if args.run_cycle:
            results = loop.run_complete_cycle()
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print("\n🔄 Improvement Cycle Results")
                print("="*70)
                print(f"Success: {results.get('success')}")
                print(f"Workflows Optimized: {results.get('workflows_optimized', 0)}")
                print(f"Workflows Scaled: {results.get('workflows_scaled', 0)}")
                print(f"Improvements Applied: {results.get('improvements_applied', 0)}")
                print(f"Scaling Events: {results.get('scaling_events', 0)}")
                print(f"Cycle Duration: {results.get('cycle_duration_seconds', 0):.2f}s")
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()