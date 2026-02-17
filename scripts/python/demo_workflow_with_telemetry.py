#!/usr/bin/env python3
"""
Demo Workflow with Telemetry
📊 Demonstrates telemetry collection in action

#TELEMETRY #DEMO #WORKFLOWS
"""

import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from workflow_telemetry_decorator import telemetry_track
from syphon_workflow_telemetry_system import get_telemetry_system, TelemetryEventType

# Demo workflow with telemetry
@telemetry_track(workflow_name="Demo Data Processing", workflow_id="demo_data_processing")
def demo_data_processing_workflow(data_size: int = 100):
    """Demo workflow that processes data"""
    print(f"   Processing {data_size} items...")

    # Simulate processing steps
    for i in range(5):
        time.sleep(0.1)
        print(f"   Step {i+1}/5 completed")

    return {
        "success": True,
        "items_processed": data_size,
        "message": f"Successfully processed {data_size} items"
    }

@telemetry_track(workflow_name="Demo API Call", workflow_id="demo_api_call")
def demo_api_call_workflow(endpoint: str = "https://api.example.com/data"):
    """Demo workflow that calls an API"""
    print(f"   Calling API: {endpoint}")
    time.sleep(0.3)  # Simulate API call

    return {
        "success": True,
        "endpoint": endpoint,
        "response_code": 200,
        "message": "API call successful"
    }

def main():
    """Run demo workflows with telemetry"""
    print("=" * 70)
    print("📊 SYPHON Workflow Telemetry - Live Demo")
    print("=" * 70)
    print()

    telemetry = get_telemetry_system()

    # Run demo workflows
    print("🚀 Running Demo Workflows...")
    print("-" * 70)

    # Workflow 1: Data Processing
    print("\n1️⃣ Demo Data Processing Workflow")
    result1 = demo_data_processing_workflow(data_size=500)
    print(f"   ✅ Result: {result1.get('message')}")

    # Workflow 2: API Call
    print("\n2️⃣ Demo API Call Workflow")
    result2 = demo_api_call_workflow(endpoint="https://api.example.com/users")
    print(f"   ✅ Result: {result2.get('message')}")

    # Workflow 3: Another data processing
    print("\n3️⃣ Demo Data Processing Workflow (Large Dataset)")
    result3 = demo_data_processing_workflow(data_size=1000)
    print(f"   ✅ Result: {result3.get('message')}")

    # Flush events
    print("\n📤 Flushing events to database...")
    count = telemetry.flush_events()
    print(f"   ✅ Flushed {count} events")

    # Get metrics
    print("\n📊 Workflow Metrics:")
    print("-" * 70)

    workflows = ["demo_data_processing", "demo_api_call"]
    for workflow_id in workflows:
        metrics_result = telemetry.get_workflow_metrics(workflow_id)
        if metrics_result.get("success"):
            metrics = metrics_result.get("metrics", {})
            print(f"\n{workflow_id}:")
            print(f"   Executions: {metrics.get('total_executions', 0)}")
            print(f"   Success Rate: {metrics.get('success_rate', 0):.2f}%")
            print(f"   Avg Duration: {metrics.get('average_duration', 0):.2f}s")

    # Export summary
    print("\n📤 Export Summary:")
    print("-" * 70)
    export_result = telemetry.export_to_database()
    if export_result.get("success"):
        exported = export_result.get("exported", {})
        print(f"   Events: {exported.get('events', 0)}")
        print(f"   Executions: {exported.get('executions', 0)}")
        print(f"   Metrics: {exported.get('metrics', 0)}")

    print("\n" + "=" * 70)
    print("✅ Telemetry Demo Complete!")
    print("=" * 70)

if __name__ == "__main__":


    main()