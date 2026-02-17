#!/usr/bin/env python3
"""
Test Workflow Telemetry System
🧪 Test telemetry collection, database, and improvement engine

#TELEMETRY #TEST #WORKFLOWS
"""

import sys
from pathlib import Path
from datetime import datetime
import time
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scripts.python.syphon_workflow_telemetry_system import (
        get_telemetry_system,
        TelemetryEventType
    )
    from scripts.python.workflow_telemetry_decorator import telemetry_track
    from scripts.python.workflow_improvement_engine import WorkflowImprovementEngine
    TELEMETRY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Telemetry not available: {e}")
    TELEMETRY_AVAILABLE = False


@telemetry_track(workflow_name="Test Workflow", workflow_id="test_workflow")
def test_workflow_function():
    """Test workflow function with telemetry decorator"""
    print("   Running test workflow...")
    time.sleep(0.5)  # Simulate work
    return {"success": True, "message": "Test workflow completed"}


def test_telemetry_system():
    """Test the telemetry system"""
    print("=" * 70)
    print("🧪 Testing SYPHON Workflow Telemetry System")
    print("=" * 70)
    print()

    if not TELEMETRY_AVAILABLE:
        print("❌ Telemetry system not available")
        return False

    telemetry = get_telemetry_system()

    # Test 1: Manual event capture
    print("📊 Test 1: Manual Event Capture")
    print("-" * 70)
    workflow_id = "test_workflow_manual"
    workflow_name = "Test Workflow (Manual)"
    execution_id = f"test_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    event = telemetry.capture_event(
        event_type=TelemetryEventType.WORKFLOW_START,
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        execution_id=execution_id,
        data={"test": True},
        tags=["test", "manual"]
    )
    print(f"   ✅ Captured event: {event.event_id}")
    print()

    # Test 2: Workflow execution tracking
    print("📊 Test 2: Workflow Execution Tracking")
    print("-" * 70)
    started_at = datetime.now()
    time.sleep(0.3)  # Simulate work
    ended_at = datetime.now()

    telemetry.track_workflow_execution(
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        execution_id=execution_id,
        started_at=started_at,
        ended_at=ended_at,
        success=True,
        outcome_text="Test execution completed",
        metrics={"duration": 0.3, "steps": 3},
        workflow_data={"test": True, "result": "success"}
    )
    print(f"   ✅ Tracked execution: {execution_id}")
    print()

    # Test 3: Decorator-based tracking
    print("📊 Test 3: Decorator-Based Tracking")
    print("-" * 70)
    result = test_workflow_function()
    print(f"   ✅ Decorator workflow completed: {result.get('success')}")
    print()

    # Test 4: Flush events
    print("📊 Test 4: Flush Events to Database")
    print("-" * 70)
    count = telemetry.flush_events()
    print(f"   ✅ Flushed {count} events to database")
    print()

    # Test 5: Get metrics
    print("📊 Test 5: Get Workflow Metrics")
    print("-" * 70)
    metrics_result = telemetry.get_workflow_metrics(workflow_id)
    if metrics_result.get("success"):
        metrics = metrics_result.get("metrics", {})
        if isinstance(metrics, dict):
            print(f"   ✅ Metrics retrieved:")
            print(f"      Total Executions: {metrics.get('total_executions', 0)}")
            print(f"      Success Rate: {metrics.get('success_rate', 0):.2f}%")
            print(f"      Average Duration: {metrics.get('average_duration', 0):.2f}s")
        else:
            print(f"   ✅ Metrics retrieved: {len(metrics)} workflows")
    else:
        print(f"   ⚠️  Metrics not available: {metrics_result.get('error')}")
    print()

    # Test 6: Improvement Engine
    print("📊 Test 6: Improvement Engine Analysis")
    print("-" * 70)
    engine = WorkflowImprovementEngine()
    opportunities = engine.analyze_workflow(workflow_id)
    print(f"   ✅ Found {len(opportunities)} improvement opportunities")
    for opp in opportunities[:3]:
        print(f"      - {opp.opportunity_type}: {opp.description[:50]}...")
    print()

    # Test 7: Export summary
    print("📊 Test 7: Export Summary")
    print("-" * 70)
    export_result = telemetry.export_to_database()
    if export_result.get("success"):
        exported = export_result.get("exported", {})
        print(f"   ✅ Export ready:")
        print(f"      Events: {exported.get('events', 0)}")
        print(f"      Executions: {exported.get('executions', 0)}")
        print(f"      Metrics: {exported.get('metrics', 0)}")
    print()

    print("=" * 70)
    print("✅ Telemetry System Test Complete!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = test_telemetry_system()
    sys.exit(0 if success else 1)
