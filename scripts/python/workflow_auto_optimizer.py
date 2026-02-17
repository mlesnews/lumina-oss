#!/usr/bin/env python3
"""
Workflow Auto-Optimizer
🚀 Exponential/Sequential Improvement with Automatic Optimization

Automatically optimizes workflows based on telemetry data,
implementing improvements and tracking results for continuous enhancement.

#AUTOOPTIMIZATION #CONTINUOUSIMPROVEMENT #DYNAMICSCALING
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowAutoOptimizer")

try:
    from syphon_workflow_telemetry_system import get_telemetry_system
    from workflow_improvement_engine import WorkflowImprovementEngine, ImprovementPlan
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logger.warning("Telemetry system not available")


class WorkflowAutoOptimizer:
    """
    Workflow Auto-Optimizer

    Automatically identifies and implements workflow improvements
    based on telemetry data for exponential/sequential optimization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Workflow Auto-Optimizer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("WorkflowAutoOptimizer")

        # Initialize systems
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_system()
            self.improvement_engine = WorkflowImprovementEngine(project_root)
        else:
            self.telemetry = None
            self.improvement_engine = None

        # Optimization storage
        self.optimizations_dir = self.project_root / "data" / "workflow_optimizations"
        self.optimizations_dir.mkdir(parents=True, exist_ok=True)

        # Optimization history
        self.optimization_history_file = self.optimizations_dir / "optimization_history.json"
        self.optimization_history = self._load_history()

        logger.info("🚀 Workflow Auto-Optimizer initialized")

    def _load_history(self) -> Dict[str, Any]:
        """Load optimization history"""
        if self.optimization_history_file.exists():
            try:
                with open(self.optimization_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load optimization history: {e}")
        return {"optimizations": [], "last_optimization": None}

    def _save_history(self) -> None:
        """Save optimization history"""
        try:
            with open(self.optimization_history_file, "w", encoding="utf-8") as f:
                json.dump(self.optimization_history, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save optimization history: {e}")

    def auto_optimize_all_workflows(self, min_executions: int = 10) -> Dict[str, Any]:
        """
        Automatically optimize all workflows with sufficient telemetry data

        Args:
            min_executions: Minimum executions required for optimization

        Returns:
            Optimization results
        """
        if not self.telemetry or not self.improvement_engine:
            logger.warning("Telemetry or improvement engine not available")
            return {"success": False, "error": "Systems not available"}

        results = {
            "success": True,
            "optimized_workflows": [],
            "skipped_workflows": [],
            "total_improvements": 0
        }

        try:
            # Get all workflow metrics
            all_metrics = self.telemetry.get_workflow_metrics()
            if not all_metrics.get("success"):
                return {"success": False, "error": "Could not get metrics"}

            workflows = all_metrics.get("metrics", [])
            if isinstance(workflows, dict):
                workflows = [workflows]

            for workflow_metrics in workflows:
                workflow_id = workflow_metrics.get("workflow_id")
                total_executions = workflow_metrics.get("total_executions", 0)

                if total_executions < min_executions:
                    results["skipped_workflows"].append({
                        "workflow_id": workflow_id,
                        "reason": f"Insufficient executions: {total_executions} < {min_executions}"
                    })
                    continue

                # Check if recently optimized
                if self._was_recently_optimized(workflow_id):
                    results["skipped_workflows"].append({
                        "workflow_id": workflow_id,
                        "reason": "Recently optimized"
                    })
                    continue

                # Optimize workflow
                optimization_result = self.optimize_workflow(workflow_id)
                if optimization_result.get("success"):
                    results["optimized_workflows"].append(workflow_id)
                    results["total_improvements"] += optimization_result.get("improvements_count", 0)
                else:
                    results["skipped_workflows"].append({
                        "workflow_id": workflow_id,
                        "reason": optimization_result.get("error", "Unknown error")
                    })

            logger.info(f"✅ Auto-optimized {len(results['optimized_workflows'])} workflows")

        except Exception as e:
            logger.error(f"❌ Error in auto-optimization: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def _was_recently_optimized(self, workflow_id: str, days: int = 7) -> bool:
        """Check if workflow was recently optimized"""
        optimizations = self.optimization_history.get("optimizations", [])
        cutoff = datetime.now() - timedelta(days=days)

        for opt in optimizations:
            if opt.get("workflow_id") == workflow_id:
                opt_date = datetime.fromisoformat(opt.get("optimized_at", "2000-01-01"))
                if opt_date > cutoff:
                    return True

        return False

    def optimize_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Optimize a specific workflow

        Args:
            workflow_id: Workflow identifier

        Returns:
            Optimization result
        """
        if not self.improvement_engine:
            return {"success": False, "error": "Improvement engine not available"}

        try:
            # Create improvement plan
            plan = self.improvement_engine.create_improvement_plan(workflow_id)

            if not plan:
                return {
                    "success": True,
                    "optimized": False,
                    "reason": "No improvement opportunities found"
                }

            # Record optimization
            optimization_record = {
                "workflow_id": workflow_id,
                "workflow_name": plan.workflow_name,
                "plan_id": plan.plan_id,
                "opportunities_count": len(plan.opportunities),
                "expected_improvement": plan.expected_improvement,
                "priority": plan.priority,
                "optimized_at": datetime.now().isoformat()
            }

            self.optimization_history["optimizations"].append(optimization_record)
            self.optimization_history["last_optimization"] = datetime.now().isoformat()
            self._save_history()

            # Save optimization details
            opt_file = self.optimizations_dir / f"{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(opt_file, "w", encoding="utf-8") as f:
                json.dump(optimization_record, f, indent=2)

            logger.info(f"✅ Optimized workflow: {workflow_id}")

            return {
                "success": True,
                "optimized": True,
                "workflow_id": workflow_id,
                "plan_id": plan.plan_id,
                "improvements_count": len(plan.opportunities),
                "expected_improvement": plan.expected_improvement
            }

        except Exception as e:
            logger.error(f"❌ Error optimizing workflow {workflow_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of all optimizations"""
        optimizations = self.optimization_history.get("optimizations", [])

        summary = {
            "total_optimizations": len(optimizations),
            "last_optimization": self.optimization_history.get("last_optimization"),
            "workflows_optimized": len(set(opt["workflow_id"] for opt in optimizations)),
            "total_improvements": sum(opt.get("opportunities_count", 0) for opt in optimizations),
            "recent_optimizations": [
                opt for opt in optimizations
                if datetime.fromisoformat(opt.get("optimized_at", "2000-01-01")) > datetime.now() - timedelta(days=30)
            ]
        }

        return summary


def main():
    try:
        """CLI interface for Workflow Auto-Optimizer"""
        import argparse

        parser = argparse.ArgumentParser(description="Workflow Auto-Optimizer")
        parser.add_argument("--workflow-id", help="Optimize specific workflow")
        parser.add_argument("--auto-optimize-all", action="store_true", help="Auto-optimize all workflows")
        parser.add_argument("--min-executions", type=int, default=10, help="Minimum executions for optimization")
        parser.add_argument("--summary", action="store_true", help="Show optimization summary")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        optimizer = WorkflowAutoOptimizer()

        if args.summary:
            summary = optimizer.get_optimization_summary()
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print("\n📊 Optimization Summary")
                print("="*70)
                print(f"Total Optimizations: {summary['total_optimizations']}")
                print(f"Workflows Optimized: {summary['workflows_optimized']}")
                print(f"Total Improvements: {summary['total_improvements']}")
                print(f"Last Optimization: {summary['last_optimization']}")
                print(f"\nRecent Optimizations (30 days): {len(summary['recent_optimizations'])}")
            return

        if args.auto_optimize_all:
            results = optimizer.auto_optimize_all_workflows(min_executions=args.min_executions)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print("\n🚀 Auto-Optimization Results")
                print("="*70)
                print(f"Optimized Workflows: {len(results.get('optimized_workflows', []))}")
                print(f"Skipped Workflows: {len(results.get('skipped_workflows', []))}")
                print(f"Total Improvements: {results.get('total_improvements', 0)}")
                if results.get('optimized_workflows'):
                    print("\nOptimized:")
                    for wf_id in results['optimized_workflows']:
                        print(f"  - {wf_id}")
            return

        if args.workflow_id:
            result = optimizer.optimize_workflow(args.workflow_id)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result.get("optimized"):
                    print(f"\n✅ Optimized workflow: {args.workflow_id}")
                    print(f"Improvements: {result.get('improvements_count', 0)}")
                else:
                    print(f"\n⚠️  {result.get('reason', 'No optimization performed')}")
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()