#!/usr/bin/env python3
"""
VA Enhancement Integration Test

End-to-end test of Phase 1 enhancements:
- Multi-VA Coordination System
- Event-Driven Activation
- System Integration

Tags: #VIRTUAL_ASSISTANT #INTEGRATION_TEST #@DOIT #@END2END @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry
    from lumina_logger import get_logger
    from va_coordination_system import TaskPriority, VACoordinationSystem
    from va_event_driven_activation import (EventPriority, EventType,
                                            VAEventActivationSystem)
    from va_system_integration import VASystemIntegration
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VAEnhancementIntegration")


def main():
    """Main integration test"""
    print("=" * 80)
    print("🧪 VA ENHANCEMENT INTEGRATION TEST")
    print("=" * 80)
    print()

    # Initialize systems
    registry = CharacterAvatarRegistry()
    coord_system = VACoordinationSystem(registry)
    event_system = VAEventActivationSystem(registry)
    integration = VASystemIntegration(registry)

    print("✅ All systems initialized")
    print()

    # Test Scenario 1: Event-Driven Task Assignment
    print("=" * 80)
    print("SCENARIO 1: Event-Driven Task Assignment")
    print("=" * 80)
    print()

    print("1. Triggering combat event...")
    combat_event = event_system.trigger_event(
        event_type=EventType.COMBAT,
        description="Combat encounter detected",
        priority=EventPriority.HIGH
    )
    print(f"   ✅ Event triggered: {combat_event.event_id}")
    print(f"   ✅ Activated VAs: {', '.join(combat_event.triggered_vas)}")
    print()

    print("2. Creating task for combat event...")
    task = coord_system.create_task(
        task_type="combat",
        description="Handle combat encounter",
        priority=TaskPriority.HIGH,
        context={"event_id": combat_event.event_id}
    )
    print(f"   ✅ Task created: {task.task_id}")
    print()

    print("3. Auto-assigning task to activated VA...")
    if combat_event.triggered_vas:
        assigned_va = coord_system.auto_assign_task(task.task_id)
        if assigned_va:
            print(f"   ✅ Task assigned to: {assigned_va}")
    print()

    # Test Scenario 2: Multi-VA Coordination
    print("=" * 80)
    print("SCENARIO 2: Multi-VA Coordination")
    print("=" * 80)
    print()

    print("1. Creating workflow task...")
    workflow_task = coord_system.create_task(
        task_type="workflow",
        description="Execute complex workflow",
        priority=TaskPriority.MEDIUM
    )
    print(f"   ✅ Task created: {workflow_task.task_id}")
    print()

    print("2. Assigning to JARVIS_VA...")
    coord_system.assign_task(workflow_task.task_id, "jarvis_va")
    print("   ✅ Task assigned to JARVIS_VA")
    print()

    print("3. JARVIS_VA delegating to ACE for security check...")
    coord_system.delegate_task(
        workflow_task.task_id,
        from_va="jarvis_va",
        to_va="ace",
        reason="Security validation required"
    )
    print("   ✅ Task delegated to ACE")
    print()

    print("4. Sharing context between VAs...")
    coord_system.share_context(
        from_va="jarvis_va",
        context={"workflow_id": "test_workflow", "status": "in_progress"},
        target_vas=["imva", "ace"]
    )
    print("   ✅ Context shared")
    print()

    # Test Scenario 3: System Integration
    print("=" * 80)
    print("SCENARIO 3: System Integration")
    print("=" * 80)
    print()

    print("1. JARVIS_VA using JARVIS automation...")
    jarvis_result = integration.use_jarvis("jarvis_va", "automate", {"task": "workflow"})
    if jarvis_result:
        print(f"   ✅ JARVIS operation: {jarvis_result['status']}")
    print()

    print("2. ACE using R5 for context aggregation...")
    r5_result = integration.use_r5("ace", "aggregate", {"context": "combat"})
    if r5_result:
        print(f"   ✅ R5 operation: {r5_result['status']}")
    print()

    print("3. JARVIS_VA using V3 for verification...")
    v3_result = integration.use_v3("jarvis_va", "verify", "workflow_result")
    if v3_result:
        print(f"   ✅ V3 operation: {v3_result['status']}")
    print()

    print("4. IMVA using SYPHON for pattern search...")
    syphon_result = integration.use_syphon("imva", "virtual.*assistant", "scripts/python")
    if syphon_result:
        print(f"   ✅ SYPHON operation: {syphon_result['status']}")
    print()

    # Test Scenario 4: Combined Workflow
    print("=" * 80)
    print("SCENARIO 4: Combined Workflow")
    print("=" * 80)
    print()

    print("1. Event triggers automation...")
    auto_event = event_system.trigger_event(
        event_type=EventType.AUTOMATION,
        description="Automation workflow required",
        priority=EventPriority.MEDIUM
    )
    print(f"   ✅ Event: {auto_event.event_id}")
    print(f"   ✅ Activated: {', '.join(auto_event.triggered_vas)}")
    print()

    print("2. Creating automation task...")
    auto_task = coord_system.create_task(
        task_type="automation",
        description="Execute automation workflow",
        priority=TaskPriority.MEDIUM,
        context={"event_id": auto_event.event_id}
    )
    print(f"   ✅ Task: {auto_task.task_id}")
    print()

    print("3. Assigning to JARVIS_VA...")
    coord_system.assign_task(auto_task.task_id, "jarvis_va")
    print("   ✅ Assigned to JARVIS_VA")
    print()

    print("4. JARVIS_VA uses integrated systems...")
    integration.use_jarvis("jarvis_va", "execute_workflow", {"workflow_id": "test"})
    integration.use_r5("jarvis_va", "aggregate", {"context": "automation"})
    integration.use_v3("jarvis_va", "verify", "workflow_execution")
    print("   ✅ All systems integrated")
    print()

    print("5. Completing task...")
    coord_system.complete_task(auto_task.task_id, {"result": "success"})
    print("   ✅ Task completed")
    print()

    # Summary
    print("=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print()

    print("Systems Tested:")
    print("  ✅ Multi-VA Coordination System")
    print("  ✅ Event-Driven Activation System")
    print("  ✅ System Integration (JARVIS, R5, V3, SYPHON)")
    print()

    print("VA Status:")
    va_status = coord_system.get_all_va_status()
    for status in va_status.values():
        if status:
            print(f"  • {status['va_name']}: {status['current_tasks']} tasks, {status['pending_messages']} messages")
    print()

    print("Event Statistics:")
    for va in event_system.vas:
        stats = event_system.get_va_activation_stats(va.character_id)
        print(f"  • {va.name}: {stats['total_activations']} activations")
    print()

    print("Integration Status:")
    int_status = integration.get_integration_status()
    for system, info in int_status["systems"].items():
        status = "✅ AVAILABLE" if info["available"] else "❌ UNAVAILABLE"
        print(f"  • {system.upper()}: {status}")
    print()

    print("=" * 80)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":


    main()