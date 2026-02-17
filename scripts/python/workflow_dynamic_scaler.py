#!/usr/bin/env python3
"""
Workflow Dynamic Scaler
📈 Infinite Dynamic Scaling Based on Telemetry

Automatically scales workflows based on telemetry metrics,
enabling infinite dynamic scaling for exponential growth.

#DYNAMICSCALING #AUTOSCALING #TELEMETRY
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowDynamicScaler")

try:
    from syphon_workflow_telemetry_system import get_telemetry_system
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logger.warning("Telemetry system not available")


@dataclass
class ScalingDecision:
    """Scaling decision for a workflow"""
    workflow_id: str
    workflow_name: str
    current_scale: int
    recommended_scale: int
    scaling_factor: float
    reason: str
    priority: int
    metrics: Dict[str, Any]


class WorkflowDynamicScaler:
    """
    Workflow Dynamic Scaler

    Automatically scales workflows based on telemetry metrics
    for infinite dynamic scaling capability.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Workflow Dynamic Scaler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("WorkflowDynamicScaler")

        # Initialize telemetry
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_system()
        else:
            self.telemetry = None

        # Scaling configuration
        self.scaling_config = {
            "min_scale": 1,
            "max_scale": 100,
            "scale_up_threshold": 0.8,  # 80% capacity
            "scale_down_threshold": 0.3,  # 30% capacity
            "execution_rate_threshold": 10,  # executions per hour
            "duration_threshold": 5.0,  # seconds
        }

        # Scaling storage
        self.scaling_dir = self.project_root / "data" / "workflow_scaling"
        self.scaling_dir.mkdir(parents=True, exist_ok=True)

        # Scaling history
        self.scaling_history_file = self.scaling_dir / "scaling_history.json"
        self.scaling_history = self._load_history()

        logger.info("📈 Workflow Dynamic Scaler initialized")

    def _load_history(self) -> Dict[str, Any]:
        """Load scaling history"""
        if self.scaling_history_file.exists():
            try:
                with open(self.scaling_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load scaling history: {e}")
        return {"scaling_events": [], "current_scales": {}, "last_scaling": None}

    def _save_history(self) -> None:
        """Save scaling history"""
        try:
            with open(self.scaling_history_file, "w", encoding="utf-8") as f:
                json.dump(self.scaling_history, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save scaling history: {e}")

    def analyze_scaling_needs(self, workflow_id: Optional[str] = None) -> List[ScalingDecision]:
        """
        Analyze scaling needs for workflows

        Args:
            workflow_id: Specific workflow, or None for all workflows

        Returns:
            List of scaling decisions
        """
        if not self.telemetry:
            logger.warning("Telemetry not available")
            return []

        decisions = []

        try:
            # Get workflow metrics
            if workflow_id:
                metrics_result = self.telemetry.get_workflow_metrics(workflow_id)
                workflows = [metrics_result.get("metrics", {})] if metrics_result.get("success") else []
            else:
                all_metrics = self.telemetry.get_workflow_metrics()
                workflows = all_metrics.get("metrics", [])
                if isinstance(workflows, dict):
                    workflows = [workflows]

            for workflow_metrics in workflows:
                if isinstance(workflow_metrics, dict) and workflow_metrics.get("workflow_id"):
                    decision = self._analyze_workflow_scaling(workflow_metrics)
                    if decision:
                        decisions.append(decision)

        except Exception as e:
            logger.error(f"❌ Error analyzing scaling needs: {e}")

        return decisions

    def _analyze_workflow_scaling(self, metrics: Dict[str, Any]) -> Optional[ScalingDecision]:
        """Analyze scaling needs for a single workflow"""
        workflow_id = metrics.get("workflow_id")
        workflow_name = metrics.get("workflow_name", workflow_id)

        # Get current scale (default to 1)
        current_scale = self.scaling_history.get("current_scales", {}).get(workflow_id, 1)

        # Calculate execution rate (executions per hour)
        total_executions = metrics.get("total_executions", 0)
        # Estimate from recent data - assume 24 hour window for now
        execution_rate = total_executions / 24.0 if total_executions > 0 else 0

        # Get average duration
        avg_duration = metrics.get("average_duration", 0.0)

        # Calculate capacity utilization
        # Simple model: if execution rate is high and duration is acceptable, we might need to scale
        capacity_utilization = min(1.0, (execution_rate * avg_duration) / 3600.0)

        recommended_scale = current_scale
        scaling_factor = 1.0
        reason = "No scaling needed"
        priority = 5

        # Scale up conditions
        if (execution_rate > self.scaling_config["execution_rate_threshold"] and
            capacity_utilization > self.scaling_config["scale_up_threshold"] and
            current_scale < self.scaling_config["max_scale"]):

            # Calculate recommended scale
            scaling_factor = capacity_utilization / self.scaling_config["scale_up_threshold"]
            recommended_scale = min(
                self.scaling_config["max_scale"],
                int(current_scale * scaling_factor)
            )

            if recommended_scale > current_scale:
                reason = f"High execution rate ({execution_rate:.1f}/hr) and capacity utilization ({capacity_utilization:.1%})"
                priority = 8 if capacity_utilization > 0.9 else 6

        # Scale down conditions
        elif (capacity_utilization < self.scaling_config["scale_down_threshold"] and
              current_scale > self.scaling_config["min_scale"]):

            scaling_factor = capacity_utilization / self.scaling_config["scale_down_threshold"]
            recommended_scale = max(
                self.scaling_config["min_scale"],
                int(current_scale * scaling_factor)
            )

            if recommended_scale < current_scale:
                reason = f"Low capacity utilization ({capacity_utilization:.1%})"
                priority = 4

        if recommended_scale != current_scale:
            return ScalingDecision(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                current_scale=current_scale,
                recommended_scale=recommended_scale,
                scaling_factor=scaling_factor,
                reason=reason,
                priority=priority,
                metrics={
                    "execution_rate": execution_rate,
                    "capacity_utilization": capacity_utilization,
                    "avg_duration": avg_duration,
                    "total_executions": total_executions
                }
            )

        return None

    def apply_scaling(self, decision: ScalingDecision) -> Dict[str, Any]:
        """
        Apply scaling decision to workflow

        Args:
            decision: Scaling decision to apply

        Returns:
            Scaling result
        """
        try:
            # Update current scale
            current_scales = self.scaling_history.get("current_scales", {})
            current_scales[decision.workflow_id] = decision.recommended_scale
            self.scaling_history["current_scales"] = current_scales

            # Record scaling event
            scaling_event = {
                "workflow_id": decision.workflow_id,
                "workflow_name": decision.workflow_name,
                "previous_scale": decision.current_scale,
                "new_scale": decision.recommended_scale,
                "scaling_factor": decision.scaling_factor,
                "reason": decision.reason,
                "metrics": decision.metrics,
                "scaled_at": datetime.now().isoformat()
            }

            self.scaling_history["scaling_events"].append(scaling_event)
            self.scaling_history["last_scaling"] = datetime.now().isoformat()
            self._save_history()

            # Save scaling details
            scale_file = self.scaling_dir / f"{decision.workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(scale_file, "w", encoding="utf-8") as f:
                json.dump(scaling_event, f, indent=2)

            logger.info(f"📈 Scaled {decision.workflow_id}: {decision.current_scale} -> {decision.recommended_scale}")

            return {
                "success": True,
                "workflow_id": decision.workflow_id,
                "previous_scale": decision.current_scale,
                "new_scale": decision.recommended_scale,
                "scaling_factor": decision.scaling_factor
            }

        except Exception as e:
            logger.error(f"❌ Error applying scaling: {e}")
            return {"success": False, "error": str(e)}

    def auto_scale_all_workflows(self) -> Dict[str, Any]:
        """Automatically scale all workflows based on telemetry"""
        decisions = self.analyze_scaling_needs()

        results = {
            "success": True,
            "scaled_workflows": [],
            "total_scaling_events": 0
        }

        for decision in decisions:
            if decision.priority >= 6:  # Only auto-scale high priority
                result = self.apply_scaling(decision)
                if result.get("success"):
                    results["scaled_workflows"].append(decision.workflow_id)
                    results["total_scaling_events"] += 1

        logger.info(f"📈 Auto-scaled {len(results['scaled_workflows'])} workflows")
        return results

    def get_scaling_summary(self) -> Dict[str, Any]:
        """Get scaling summary"""
        events = self.scaling_history.get("scaling_events", [])
        current_scales = self.scaling_history.get("current_scales", {})

        summary = {
            "total_scaling_events": len(events),
            "last_scaling": self.scaling_history.get("last_scaling"),
            "workflows_scaled": len(set(e["workflow_id"] for e in events)),
            "current_scales": current_scales,
            "recent_scaling": [
                e for e in events
                if datetime.fromisoformat(e.get("scaled_at", "2000-01-01")) > datetime.now() - timedelta(days=7)
            ]
        }

        return summary


def main():
    try:
        """CLI interface for Workflow Dynamic Scaler"""
        import argparse

        parser = argparse.ArgumentParser(description="Workflow Dynamic Scaler")
        parser.add_argument("--workflow-id", help="Analyze specific workflow")
        parser.add_argument("--auto-scale", action="store_true", help="Auto-scale all workflows")
        parser.add_argument("--analyze", action="store_true", help="Analyze scaling needs")
        parser.add_argument("--summary", action="store_true", help="Show scaling summary")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        scaler = WorkflowDynamicScaler()

        if args.summary:
            summary = scaler.get_scaling_summary()
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print("\n📈 Scaling Summary")
                print("="*70)
                print(f"Total Scaling Events: {summary['total_scaling_events']}")
                print(f"Workflows Scaled: {summary['workflows_scaled']}")
                print(f"Last Scaling: {summary['last_scaling']}")
                print(f"\nCurrent Scales:")
                for wf_id, scale in summary['current_scales'].items():
                    print(f"  {wf_id}: {scale}")
            return

        if args.auto_scale:
            results = scaler.auto_scale_all_workflows()
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print("\n📈 Auto-Scaling Results")
                print("="*70)
                print(f"Scaled Workflows: {len(results.get('scaled_workflows', []))}")
                print(f"Total Events: {results.get('total_scaling_events', 0)}")
            return

        if args.analyze or args.workflow_id:
            decisions = scaler.analyze_scaling_needs(args.workflow_id)
            if args.json:
                print(json.dumps([
                    {
                        "workflow_id": d.workflow_id,
                        "workflow_name": d.workflow_name,
                        "current_scale": d.current_scale,
                        "recommended_scale": d.recommended_scale,
                        "scaling_factor": d.scaling_factor,
                        "reason": d.reason,
                        "priority": d.priority
                    }
                    for d in decisions
                ], indent=2))
            else:
                print("\n📊 Scaling Analysis")
                print("="*70)
                for decision in decisions:
                    print(f"\n{decision.workflow_name} ({decision.workflow_id})")
                    print(f"  Current Scale: {decision.current_scale}")
                    print(f"  Recommended Scale: {decision.recommended_scale}")
                    print(f"  Reason: {decision.reason}")
                    print(f"  Priority: {decision.priority}/10")
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()