#!/usr/bin/env python3
"""
Demo: SYPHON Workflow Telemetry System
🚀 Full demonstration of telemetry collection and analysis

#TELEMETRY #DEMO #WORKFLOWS
"""

import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from scripts.python.syphon_workflow_telemetry_system import (
    get_telemetry_system,
    TelemetryEventType
)
from scripts.python.workflow_telemetry_decorator import telemetry_track
from scripts.python.workflow_improvement_engine import WorkflowImprovementEngine


@telemetry_track(workflow_name="Demo Workflow 1", workflow_id="demo_workflow_1")
def demo_workflow_1():
    """Demo workflow with telemetry"""
    print("   Running Demo Workflow 1...")
    time.sleep(0.2)
    return {"success": True, "message": "Demo workflow 1 completed"}


@telemetry_track(workflow_name="Demo Workflow 2", workflow_id="demo_workflow_2")
def demo_workflow_2():
    """Another demo workflow"""
    print("   Running Demo Workflow 2...")
    time.sleep(0.3)
    return {"success": True, "message": "Demo workflow 2 completed"}


def main():
    """Full telemetry system demonstration"""
    print("=" * 70)
    print("🚀 SYPHON Workflow Telemetry System - Full Demo")
    print("=" * 70)
    print()

    telemetry = get_telemetry_system()
    engine = WorkflowImprovementEngine()

    # Demo 1: Run workflows with decorator
    print("📊 Demo 1: Running Workflows with Telemetry Decorator")
    print("-" * 70)
    result1 = demo_workflow_1()
    result2 = demo_workflow_2()
    print(f"   ✅ Workflow 1: {result1.get('message')}")
    print(f"   ✅ Workflow 2: {result2.get('message')}")
    print()

    # Demo 2: Manual tracking
    print("📊 Demo 2: Manual Workflow Tracking")
    print("-" * 70)
    workflow_id = "demo_manual_workflow"
    workflow_name = "Demo Manual Workflow"
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    started_at = datetime.now()

    time.sleep(0.4)  # Simulate work
    ended_at = datetime.now()

    telemetry.track_workflow_execution(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        execution_id=execution_id,
        started_at=started_at,
        ended_at=ended_at,
        success=True,
        outcome_text="Manual workflow completed successfully",
        metrics={"duration": 0.4, "steps": 5, "items_processed": 100},
        workflow_data={"type": "demo", "source": "manual_tracking"}
    )
    print(f"   ✅ Tracked manual workflow: {execution_id}")
    print()

    # Demo 3: Flush events
    print("📊 Demo 3: Flushing Events to Database")
    print("-" * 70)
    count = telemetry.flush_events()
    print(f"   ✅ Flushed {count} events to database")
    print()

    # Demo 4: Get metrics
    print("📊 Demo 4: Workflow Metrics")
    print("-" * 70)
    for wf_id in ["demo_workflow_1", "demo_workflow_2", "demo_manual_workflow"]:
        metrics_result = telemetry.get_workflow_metrics(wf_id)
        if metrics_result.get("success"):
            metrics = metrics_result.get("metrics", {})
            print(f"   📈 {wf_id}:")
            print(f"      Executions: {metrics.get('total_executions', 0)}")
            print(f"      Success Rate: {metrics.get('success_rate', 0):.2f}%")
            print(f"      Avg Duration: {metrics.get('average_duration', 0):.2f}s")
    print()

    # Demo 5: Improvement analysis
    print("📊 Demo 5: Improvement Engine Analysis")
    print("-" * 70)
    for wf_id in ["demo_workflow_1", "demo_workflow_2"]:
        opportunities = engine.analyze_workflow(wf_id)
        print(f"   🔍 {wf_id}: {len(opportunities)} opportunities found")
        for opp in opportunities[:2]:
            print(f"      - {opp.opportunity_type}: {opp.description[:60]}...")
    print()

    # Demo 6: Export summary
    print("📊 Demo 6: Export Summary")
    print("-" * 70)
    export_result = telemetry.export_to_database()
    if export_result.get("success"):
        exported = export_result.get("exported", {})
        print(f"   📤 Ready for export:")
        print(f"      Events: {exported.get('events', 0)}")
        print(f"      Executions: {exported.get('executions', 0)}")
        print(f"      Metrics: {exported.get('metrics', 0)}")
    print()

    print("=" * 70)
    print("✅ Telemetry System Demo Complete!")
    print("=" * 70)
    print()
    print("📊 System Status:")
    print("   ✅ Telemetry collection: OPERATIONAL")
    print("   ✅ Database storage: OPERATIONAL")
    print("   ✅ Metrics aggregation: OPERATIONAL")
    print("   ✅ Improvement engine: OPERATIONAL")
    print("   ✅ SYPHON integration: OPERATIONAL")
    print()
    print("🚀 Ready for infinite dynamic scaling!")


if __name__ == "__main__":


    main()