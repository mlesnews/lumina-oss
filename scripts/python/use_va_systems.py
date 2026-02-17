#!/usr/bin/env python3
"""
VA Systems Usage Demo

Demonstrates practical usage of all VA systems working together.

Tags: #USAGE #DEMO #VIRTUAL_ASSISTANT #PRACTICAL @JARVIS @LUMINA
"""

import sys
from datetime import datetime
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
    from va_analytics import VAAnalytics
    from va_coordination_system import TaskPriority, VACoordinationSystem
    from va_desktop_visualization import VADesktopVisualization, VFXType
    from va_event_driven_activation import (EventPriority, EventType,
                                            VAEventActivationSystem)
    from va_health_monitoring import VAHealthMonitoring
    from va_knowledge_base import VAKnowledgeBase
    from va_resource_management import VAResourceManagement
    from va_specialization_system import (SpecializationDomain,
                                          VASpecializationSystem)
    from va_system_integration import VASystemIntegration
    from va_task_queue import TaskPriority as QueuePriority
    from va_task_queue import VATaskQueue
    from va_voice_command_processor import VAVoiceCommandProcessor
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VAUsage")


class VASystemsUsage:
    """VA Systems Usage Demonstrator"""

    def __init__(self):
        """Initialize usage demo"""
        self.registry = CharacterAvatarRegistry()

        # Initialize all systems
        print("Initializing all VA systems...")
        self.coord = VACoordinationSystem(self.registry)
        self.events = VAEventActivationSystem(self.registry)
        self.integration = VASystemIntegration(self.registry)
        self.voice = VAVoiceCommandProcessor(self.registry)
        self.viz = VADesktopVisualization(self.registry)
        self.spec = VASpecializationSystem(self.registry)
        self.health = VAHealthMonitoring(self.registry)
        self.queue = VATaskQueue(self.registry)
        self.kb = VAKnowledgeBase(self.registry)
        self.analytics = VAAnalytics(self.registry)
        self.resources = VAResourceManagement(self.registry)
        print("✅ All systems initialized\n")

    def scenario_1_voice_automation(self):
        """Scenario 1: Voice command triggers automation workflow"""
        print("=" * 80)
        print("SCENARIO 1: Voice Command → Automation Workflow")
        print("=" * 80)
        print()

        # Step 1: User gives voice command
        print("1. User: 'Hey JARVIS, automate the daily workflow'")
        voice_cmd = self.voice.process_voice_command(
            transcribed_text="Hey JARVIS, automate the daily workflow"
        )
        print(f"   ✅ Voice command processed: '{voice_cmd.transcribed_text}'")
        print(f"   ✅ Intent: {voice_cmd.intent.value}, Routed to: {voice_cmd.routed_to_va}")
        print()

        # Step 2: Event triggered
        print("2. System triggers automation event...")
        event = self.events.trigger_event(
            EventType.AUTOMATION,
            "Daily workflow automation requested",
            EventPriority.HIGH
        )
        print(f"   ✅ Event triggered: {event.event_id}")
        print(f"   ✅ Activated VAs: {', '.join(event.triggered_vas)}")
        print()

        # Step 3: Specialization routes task
        print("3. Specialization system routes task...")
        routed_vas = self.spec.route_by_specialization(SpecializationDomain.AUTOMATION)
        print(f"   ✅ Automation tasks route to: {', '.join(routed_vas)}")
        print()

        # Step 4: Task created and coordinated
        print("4. Creating and coordinating task...")
        task = self.coord.create_task(
            "automation",
            "Execute daily workflow automation",
            TaskPriority.HIGH,
            context={"voice_command_id": voice_cmd.command_id, "event_id": event.event_id}
        )
        self.coord.auto_assign_task(task.task_id)
        print(f"   ✅ Task created: {task.task_id}")
        print(f"   ✅ Assigned to: {task.assigned_va}")
        print()

        # Step 5: Task queued
        print("5. Adding task to queue...")
        queue_task = self.queue.add_task(
            task.assigned_va,
            "automation",
            "Execute daily workflow automation",
            QueuePriority.HIGH
        )
        print(f"   ✅ Task queued: {queue_task.task_id}")
        print()

        # Step 6: System integration
        print("6. Using JARVIS automation...")
        result = self.integration.use_jarvis(
            task.assigned_va,
            "execute_workflow",
            {"workflow_type": "daily", "priority": "high"}
        )
        print(f"   ✅ JARVIS operation: {result['status']}")
        print()

        # Step 7: Visualization update
        print("7. Updating desktop visualization...")
        self.viz.show_va_status(task.assigned_va, {
            "status": "processing",
            "current_task": task.task_id,
            "workflow": "daily_automation"
        })
        self.viz.display_vfx(task.assigned_va, VFXType.ACTIVATION)
        print("   ✅ Visualization updated")
        print()

        # Step 8: Health monitoring
        print("8. Monitoring VA health...")
        health_metrics = self.health.health_check(task.assigned_va)
        self.health.update_metrics(task.assigned_va, response_time=0.8, task_completed=True)
        print(f"   ✅ Health status: {health_metrics.status.value}")
        print()

        # Step 9: Resource management
        print("9. Managing resources...")
        self.resources.update_usage(task.assigned_va, cpu=1.2, memory=1200.0)
        resource_status = self.resources.get_resource_status(task.assigned_va)
        print(f"   ✅ CPU usage: {resource_status['usage']['cpu_usage']:.1f}/{resource_status['allocation']['cpu_limit']:.1f}")
        print()

        # Step 10: Knowledge storage
        print("10. Storing workflow knowledge...")
        kb_entry = self.kb.store_knowledge(
            task.assigned_va,
            "workflow_execution",
            {
                "workflow_type": "daily",
                "task_id": task.task_id,
                "status": "completed",
                "execution_time": 0.8
            },
            tags=["automation", "daily_workflow", "success"]
        )
        print(f"   ✅ Knowledge stored: {kb_entry.entry_id}")
        print()

        # Step 11: Analytics tracking
        print("11. Tracking analytics...")
        self.analytics.record_event(
            task.assigned_va,
            "workflow_completed",
            {"workflow_type": "daily", "task_id": task.task_id, "duration": 0.8}
        )
        self.analytics.track_usage(task.assigned_va, "workflow_executions", 1)
        print("   ✅ Analytics tracked")
        print()

        # Step 12: Task completion
        print("12. Completing task...")
        self.coord.complete_task(task.task_id, {"result": "success", "workflow_executed": True})
        self.queue.complete_task(queue_task.task_id)
        print("   ✅ Task completed successfully")
        print()

        print("✅ Scenario 1 Complete: Daily workflow automated")
        print()

    def scenario_2_combat_security(self):
        """Scenario 2: Combat event triggers security response"""
        print("=" * 80)
        print("SCENARIO 2: Combat Event → Security Response")
        print("=" * 80)
        print()

        # Step 1: Combat event detected
        print("1. System: Combat encounter detected!")
        combat_event = self.events.trigger_event(
            EventType.COMBAT,
            "Security threat detected",
            EventPriority.CRITICAL
        )
        print(f"   ✅ Event: {combat_event.event_id}")
        print(f"   ✅ Activated VAs: {', '.join(combat_event.triggered_vas)}")
        print()

        # Step 2: ACE activated (combat specialist)
        print("2. ACE activated for combat response...")
        ace_spec = self.spec.get_specialization("ace")
        print(f"   ✅ ACE specialization: {ace_spec.primary_domain.value} (Level {ace_spec.skill_level})")
        print()

        # Step 3: Security task created
        print("3. Creating security task...")
        security_task = self.coord.create_task(
            "security",
            "Handle security threat",
            TaskPriority.CRITICAL,
            context={"event_id": combat_event.event_id, "threat_level": "high"}
        )
        self.coord.assign_task(security_task.task_id, "ace")
        print(f"   ✅ Task created: {security_task.task_id}")
        print("   ✅ Assigned to: ACE")
        print()

        # Step 4: System integration for security
        print("4. ACE using security systems...")
        self.integration.use_jarvis("ace", "security_scan", {"threat_level": "high"})
        self.integration.use_r5("ace", "aggregate", {"context": "security_threat"})
        self.integration.use_v3("ace", "verify", "security_response")
        print("   ✅ Security systems engaged")
        print()

        # Step 5: Visualization - combat mode
        print("5. Activating combat visualization...")
        self.viz.display_vfx("ace", VFXType.COMBAT_MODE, duration=2.0)
        self.viz.show_va_status("ace", {
            "status": "combat_mode",
            "threat_level": "high",
            "defense_active": True
        })
        print("   ✅ Combat interface active")
        print()

        # Step 6: Health monitoring during combat
        print("6. Monitoring ACE health during combat...")
        ace_health = self.health.health_check("ace")
        self.health.update_metrics("ace", response_time=0.3, task_completed=True)
        print(f"   ✅ ACE health: {ace_health.status.value}")
        print()

        # Step 7: Knowledge - threat patterns
        print("7. Storing threat intelligence...")
        threat_kb = self.kb.store_knowledge(
            "ace",
            "threat_intelligence",
            {
                "threat_type": "security_breach",
                "detection_time": datetime.now().isoformat(),
                "response_time": 0.3,
                "resolved": True
            },
            tags=["security", "combat", "threat"]
        )
        print(f"   ✅ Threat intelligence stored: {threat_kb.entry_id}")
        print()

        # Step 8: Analytics - security events
        print("8. Tracking security analytics...")
        self.analytics.record_event("ace", "security_threat_resolved", {
            "threat_level": "high",
            "response_time": 0.3
        })
        self.analytics.track_usage("ace", "security_responses", 1)
        print("   ✅ Security analytics tracked")
        print()

        # Step 9: Task completion
        print("9. Security threat resolved...")
        self.coord.complete_task(security_task.task_id, {
            "result": "threat_neutralized",
            "response_time": 0.3
        })
        print("   ✅ Security task completed")
        print()

        print("✅ Scenario 2 Complete: Security threat neutralized")
        print()

    def scenario_3_multi_va_coordination(self):
        """Scenario 3: Multiple VAs coordinate on complex task"""
        print("=" * 80)
        print("SCENARIO 3: Multi-VA Coordination on Complex Task")
        print("=" * 80)
        print()

        # Step 1: Complex task initiated
        print("1. User requests: 'Create new feature with security validation'")
        main_task = self.coord.create_task(
            "feature_development",
            "Create new feature with security validation",
            TaskPriority.HIGH
        )
        self.coord.assign_task(main_task.task_id, "jarvis_va")
        print(f"   ✅ Main task created: {main_task.task_id}")
        print("   ✅ Assigned to: JARVIS_VA")
        print()

        # Step 2: JARVIS_VA delegates security to ACE
        print("2. JARVIS_VA delegates security validation to ACE...")
        security_subtask = self.coord.create_task(
            "security_validation",
            "Validate security for new feature",
            TaskPriority.HIGH,
            dependencies=[main_task.task_id]
        )
        self.coord.delegate_task(
            security_subtask.task_id,
            from_va="jarvis_va",
            to_va="ace",
            reason="Security expertise required"
        )
        print("   ✅ Security task delegated to ACE")
        print()

        # Step 3: JARVIS_VA delegates UI to IMVA
        print("3. JARVIS_VA delegates UI design to IMVA...")
        ui_subtask = self.coord.create_task(
            "ui_design",
            "Design UI for new feature",
            TaskPriority.MEDIUM,
            dependencies=[main_task.task_id]
        )
        self.coord.delegate_task(
            ui_subtask.task_id,
            from_va="jarvis_va",
            to_va="imva",
            reason="UI expertise required"
        )
        print("   ✅ UI task delegated to IMVA")
        print()

        # Step 4: Context sharing
        print("4. Sharing context between VAs...")
        self.coord.share_context(
            "jarvis_va",
            {
                "feature_name": "new_feature",
                "requirements": ["security", "ui", "automation"],
                "status": "in_progress"
            },
            target_vas=["ace", "imva"]
        )
        print("   ✅ Context shared with ACE and IMVA")
        print()

        # Step 5: Parallel processing
        print("5. VAs working in parallel...")
        # ACE working on security
        ace_health = self.health.health_check("ace")
        self.health.update_metrics("ace", response_time=0.5, task_completed=True)

        # IMVA working on UI
        self.viz.create_va_widget("imva")
        self.viz.show_va_status("imva", {"status": "designing", "task": ui_subtask.task_id})

        # JARVIS_VA coordinating
        self.integration.use_jarvis("jarvis_va", "coordinate_workflow", {"feature": "new_feature"})

        print("   ✅ All VAs working in parallel")
        print()

        # Step 6: Knowledge sharing
        print("6. VAs sharing knowledge...")
        ace_kb = self.kb.store_knowledge(
            "ace",
            "security_validation",
            {"feature": "new_feature", "validation_result": "passed"},
            tags=["security", "validation"]
        )
        self.kb.share_knowledge("ace", "jarvis_va", ace_kb.entry_id)

        imva_kb = self.kb.store_knowledge(
            "imva",
            "ui_design",
            {"feature": "new_feature", "design_status": "complete"},
            tags=["ui", "design"]
        )
        self.kb.share_knowledge("imva", "jarvis_va", imva_kb.entry_id)

        print("   ✅ Knowledge shared between VAs")
        print()

        # Step 7: Analytics - coordination metrics
        print("7. Tracking coordination analytics...")
        self.analytics.record_event("jarvis_va", "coordination_task", {
            "task_id": main_task.task_id,
            "delegated_tasks": 2
        })
        self.analytics.record_event("ace", "security_validation_complete", {})
        self.analytics.record_event("imva", "ui_design_complete", {})
        print("   ✅ Coordination analytics tracked")
        print()

        # Step 8: Task completion
        print("8. Completing all tasks...")
        self.coord.complete_task(security_subtask.task_id, {"result": "security_validated"})
        self.coord.complete_task(ui_subtask.task_id, {"result": "ui_designed"})
        self.coord.complete_task(main_task.task_id, {
            "result": "feature_complete",
            "security": "validated",
            "ui": "designed"
        })
        print("   ✅ All tasks completed")
        print()

        print("✅ Scenario 3 Complete: Multi-VA coordination successful")
        print()

    def show_system_status(self):
        """Show status of all systems"""
        print("=" * 80)
        print("📊 SYSTEM STATUS SUMMARY")
        print("=" * 80)
        print()

        # Coordination status
        print("Coordination System:")
        va_status = self.coord.get_all_va_status()
        for va_id, status in list(va_status.items())[:2]:
            if status:
                print(f"  • {status['va_name']}: {status['current_tasks']} tasks, {status['pending_messages']} messages")
        print()

        # Health status
        print("Health Monitoring:")
        health_status = self.health.get_all_health_status()
        for va_id, status in list(health_status.items())[:2]:
            print(f"  • {va_id}: {status['status']}, Response: {status['response_time']:.2f}s")
        print()

        # Resource status
        print("Resource Management:")
        resource_status = self.resources.get_resource_status()
        for va_id, status in list(resource_status.items())[:2]:
            if status:
                print(f"  • {va_id}: CPU {status['cpu_utilization']:.1%}, Memory {status['memory_utilization']:.1%}")
        print()

        # Analytics summary
        print("Analytics Summary:")
        for va in self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)[:2]:
            report = self.analytics.generate_report(va.character_id, "24h")
            print(f"  • {va.name}: {report['total_events']} events")
        print()


def main():
    """Main usage demo"""
    print("=" * 80)
    print("🎯 VA SYSTEMS USAGE DEMONSTRATION")
    print("=" * 80)
    print()

    usage = VASystemsUsage()

    # Run scenarios
    usage.scenario_1_voice_automation()
    usage.scenario_2_combat_security()
    usage.scenario_3_multi_va_coordination()

    # Show system status
    usage.show_system_status()

    print("=" * 80)
    print("✅ ALL SCENARIOS COMPLETE - SYSTEMS IN USE")
    print("=" * 80)


if __name__ == "__main__":


    main()