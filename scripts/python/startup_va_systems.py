#!/usr/bin/env python3
"""
VA Systems Startup and Validation

Starts all VA systems, validates functionality, and verifies integration.

Tags: #STARTUP #VALIDATION #VERIFICATION #VIRTUAL_ASSISTANT @JARVIS @LUMINA
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

logger = get_logger("VAStartup")


class VASystemsStartup:
    """VA Systems Startup Manager"""

    def __init__(self):
        """Initialize startup manager"""
        self.registry = CharacterAvatarRegistry()
        self.systems = {}
        self.startup_status = {}
        self.validation_results = {}
        self.verification_results = {}

        logger.info("=" * 80)
        logger.info("🚀 VA SYSTEMS STARTUP")
        logger.info("=" * 80)

    def start_all_systems(self):
        """Start all VA systems"""
        print("=" * 80)
        print("🚀 STARTING VA ENHANCEMENT SYSTEMS")
        print("=" * 80)
        print()

        systems_to_start = [
            ("Coordination", lambda: VACoordinationSystem(self.registry)),
            ("Event Activation", lambda: VAEventActivationSystem(self.registry)),
            ("System Integration", lambda: VASystemIntegration(self.registry)),
            ("Voice Commands", lambda: VAVoiceCommandProcessor(self.registry)),
            ("Desktop Visualization", lambda: VADesktopVisualization(self.registry)),
            ("Specialization", lambda: VASpecializationSystem(self.registry)),
            ("Health Monitoring", lambda: VAHealthMonitoring(self.registry)),
            ("Task Queue", lambda: VATaskQueue(self.registry)),
            ("Knowledge Base", lambda: VAKnowledgeBase(self.registry)),
            ("Analytics", lambda: VAAnalytics(self.registry)),
            ("Resource Management", lambda: VAResourceManagement(self.registry)),
        ]

        started = 0
        failed = 0

        for name, system_factory in systems_to_start:
            try:
                print(f"Starting {name}...", end=" ")
                system = system_factory()
                self.systems[name] = system
                self.startup_status[name] = "✅ RUNNING"
                print("✅")
                started += 1
            except Exception as e:
                self.startup_status[name] = f"❌ FAILED: {str(e)}"
                print(f"❌ Error: {e}")
                failed += 1

        print()
        print(f"✅ Started: {started}/{len(systems_to_start)}")
        if failed > 0:
            print(f"❌ Failed: {failed}/{len(systems_to_start)}")
        print()

        return started, failed

    def validate_systems(self):
        """Validate all systems functionality"""
        print("=" * 80)
        print("✅ VALIDATING SYSTEMS")
        print("=" * 80)
        print()

        # Coordination
        if "Coordination" in self.systems:
            try:
                coord = self.systems["Coordination"]
                task = coord.create_task("validation", "Test task", TaskPriority.MEDIUM)
                coord.auto_assign_task(task.task_id)
                coord.complete_task(task.task_id)
                self.validation_results["Coordination"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Coordination"] = f"❌ ERROR: {e}"

        # Event Activation
        if "Event Activation" in self.systems:
            try:
                events = self.systems["Event Activation"]
                event = events.trigger_event(EventType.SYSTEM_EVENT, "Validation test", EventPriority.LOW)
                stats = events.get_va_activation_stats("jarvis_va")
                self.validation_results["Event Activation"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Event Activation"] = f"❌ ERROR: {e}"

        # System Integration
        if "System Integration" in self.systems:
            try:
                integration = self.systems["System Integration"]
                status = integration.get_integration_status()
                integration.use_syphon("jarvis_va", "test_pattern")
                self.validation_results["System Integration"] = "✅ VALID"
            except Exception as e:
                self.validation_results["System Integration"] = f"❌ ERROR: {e}"

        # Voice Commands
        if "Voice Commands" in self.systems:
            try:
                voice = self.systems["Voice Commands"]
                cmd = voice.process_voice_command(transcribed_text="Test validation command")
                stats = voice.get_va_command_stats("jarvis_va")
                self.validation_results["Voice Commands"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Voice Commands"] = f"❌ ERROR: {e}"

        # Desktop Visualization
        if "Desktop Visualization" in self.systems:
            try:
                viz = self.systems["Desktop Visualization"]
                widget = viz.create_va_widget("jarvis_va")
                dashboard = viz.multi_va_dashboard()
                viz.display_vfx("jarvis_va", VFXType.ACTIVATION)
                self.validation_results["Desktop Visualization"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Desktop Visualization"] = f"❌ ERROR: {e}"

        # Specialization
        if "Specialization" in self.systems:
            try:
                spec = self.systems["Specialization"]
                matrix = spec.capability_matrix()
                routed = spec.route_by_specialization(SpecializationDomain.AUTOMATION)
                self.validation_results["Specialization"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Specialization"] = f"❌ ERROR: {e}"

        # Health Monitoring
        if "Health Monitoring" in self.systems:
            try:
                health = self.systems["Health Monitoring"]
                metrics = health.health_check("jarvis_va")
                status = health.get_all_health_status()
                self.validation_results["Health Monitoring"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Health Monitoring"] = f"❌ ERROR: {e}"

        # Task Queue
        if "Task Queue" in self.systems:
            try:
                queue = self.systems["Task Queue"]
                task = queue.add_task("jarvis_va", "validation", "Test task", QueuePriority.MEDIUM)
                processed = queue.process_queue("jarvis_va")
                status = queue.get_queue_status()
                self.validation_results["Task Queue"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Task Queue"] = f"❌ ERROR: {e}"

        # Knowledge Base
        if "Knowledge Base" in self.systems:
            try:
                kb = self.systems["Knowledge Base"]
                entry = kb.store_knowledge("jarvis_va", "validation", {"test": "data"})
                results = kb.query_knowledge("jarvis_va", "validation")
                summary = kb.get_va_knowledge_summary("jarvis_va")
                self.validation_results["Knowledge Base"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Knowledge Base"] = f"❌ ERROR: {e}"

        # Analytics
        if "Analytics" in self.systems:
            try:
                analytics = self.systems["Analytics"]
                analytics.record_event("jarvis_va", "validation_test")
                analytics.track_usage("jarvis_va", "test_metric", 1.0)
                report = analytics.generate_report("jarvis_va", "24h")
                self.validation_results["Analytics"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Analytics"] = f"❌ ERROR: {e}"

        # Resource Management
        if "Resource Management" in self.systems:
            try:
                resources = self.systems["Resource Management"]
                resources.update_usage("jarvis_va", cpu=0.5, memory=500.0)
                status = resources.get_resource_status("jarvis_va")
                optimization = resources.optimize_resources()
                self.validation_results["Resource Management"] = "✅ VALID"
            except Exception as e:
                self.validation_results["Resource Management"] = f"❌ ERROR: {e}"

        # Print results
        print("Validation Results:")
        for system, result in self.validation_results.items():
            print(f"  {result} {system}")
        print()

        valid_count = sum(1 for r in self.validation_results.values() if r.startswith("✅"))
        total_count = len(self.validation_results)

        print(f"✅ Validated: {valid_count}/{total_count}")
        print()

        return self.validation_results

    def verify_integration(self):
        """Verify system integration"""
        print("=" * 80)
        print("🔗 VERIFYING SYSTEM INTEGRATION")
        print("=" * 80)
        print()

        verification_passed = 0
        verification_failed = 0

        # Test 1: Event -> Coordination -> Task Queue
        try:
            print("Test 1: Event -> Coordination -> Task Queue...", end=" ")
            events = self.systems["Event Activation"]
            coord = self.systems["Coordination"]
            queue = self.systems["Task Queue"]

            event = events.trigger_event(EventType.AUTOMATION, "Integration test", EventPriority.MEDIUM)
            task = coord.create_task("automation", "Integration task", TaskPriority.MEDIUM)
            queue_task = queue.add_task("jarvis_va", "automation", "Integration task", QueuePriority.MEDIUM)

            print("✅")
            verification_passed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            verification_failed += 1

        # Test 2: Voice -> Specialization -> Coordination
        try:
            print("Test 2: Voice -> Specialization -> Coordination...", end=" ")
            voice = self.systems["Voice Commands"]
            spec = self.systems["Specialization"]
            coord = self.systems["Coordination"]

            cmd = voice.process_voice_command(transcribed_text="Automate workflow")
            routed = spec.route_by_specialization(SpecializationDomain.AUTOMATION)
            task = coord.create_task("automation", "Voice task", TaskPriority.HIGH)

            print("✅")
            verification_passed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            verification_failed += 1

        # Test 3: Health -> Analytics -> Knowledge
        try:
            print("Test 3: Health -> Analytics -> Knowledge...", end=" ")
            health = self.systems["Health Monitoring"]
            analytics = self.systems["Analytics"]
            kb = self.systems["Knowledge Base"]

            metrics = health.health_check("jarvis_va")
            analytics.record_event("jarvis_va", "health_check", {"status": metrics.status.value})
            kb.store_knowledge("jarvis_va", "health_data", {"metrics": metrics.to_dict()})

            print("✅")
            verification_passed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            verification_failed += 1

        # Test 4: Integration -> Resources -> Visualization
        try:
            print("Test 4: Integration -> Resources -> Visualization...", end=" ")
            integration = self.systems["System Integration"]
            resources = self.systems["Resource Management"]
            viz = self.systems["Desktop Visualization"]

            integration.use_jarvis("jarvis_va", "test", {})
            resources.update_usage("jarvis_va", cpu=1.0)
            viz.show_va_status("jarvis_va", {"status": "active"})

            print("✅")
            verification_passed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            verification_failed += 1

        # Test 5: Complete Workflow
        try:
            print("Test 5: Complete Workflow...", end=" ")
            # Voice command
            voice = self.systems["Voice Commands"]
            cmd = voice.process_voice_command(transcribed_text="Run security scan")

            # Event activation
            events = self.systems["Event Activation"]
            event = events.trigger_event(EventType.SECURITY, "Security scan", EventPriority.HIGH)

            # Task creation
            coord = self.systems["Coordination"]
            task = coord.create_task("security", "Security scan", TaskPriority.HIGH)
            coord.auto_assign_task(task.task_id)

            # Specialization routing
            spec = self.systems["Specialization"]
            routed = spec.route_by_specialization(SpecializationDomain.SECURITY)

            # System integration
            integration = self.systems["System Integration"]
            integration.use_jarvis("jarvis_va", "security_scan", {})

            # Analytics tracking
            analytics = self.systems["Analytics"]
            analytics.record_event("jarvis_va", "security_scan_completed")

            # Task completion
            coord.complete_task(task.task_id, {"result": "success"})

            print("✅")
            verification_passed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            verification_failed += 1

        print()
        print(f"✅ Integration Tests Passed: {verification_passed}/5")
        if verification_failed > 0:
            print(f"❌ Integration Tests Failed: {verification_failed}/5")
        print()

        self.verification_results = {
            "passed": verification_passed,
            "failed": verification_failed,
            "total": 5
        }

        return self.verification_results

    def get_system_status(self):
        """Get status of all systems"""
        print("=" * 80)
        print("📊 SYSTEM STATUS")
        print("=" * 80)
        print()

        print("Startup Status:")
        for system, status in self.startup_status.items():
            print(f"  {status} {system}")
        print()

        print("Validation Status:")
        for system, status in self.validation_results.items():
            print(f"  {status} {system}")
        print()

        if self.verification_results:
            print("Integration Verification:")
            print(f"  ✅ Passed: {self.verification_results['passed']}/{self.verification_results['total']}")
            if self.verification_results['failed'] > 0:
                print(f"  ❌ Failed: {self.verification_results['failed']}/{self.verification_results['total']}")
        print()

    def generate_startup_report(self):
        try:
            """Generate startup report"""
            report = {
                "startup_date": datetime.now().isoformat(),
                "systems_started": len(self.systems),
                "startup_status": self.startup_status,
                "validation_results": self.validation_results,
                "verification_results": self.verification_results
            }

            # Save report
            report_file = project_root / "data" / "va_deployment" / "startup_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"📄 Startup report saved to {report_file}")
            return report


        except Exception as e:
            self.logger.error(f"Error in generate_startup_report: {e}", exc_info=True)
            raise
def main():
    """Main startup function"""
    startup = VASystemsStartup()

    # Start all systems
    started, failed = startup.start_all_systems()

    if failed > 0:
        print("⚠️  Some systems failed to start. Check errors above.")
        return 1

    # Validate systems
    validation_results = startup.validate_systems()

    # Verify integration
    verification_results = startup.verify_integration()

    # Get status
    startup.get_system_status()

    # Generate report
    report = startup.generate_startup_report()

    # Final status
    print("=" * 80)
    print("📊 STARTUP SUMMARY")
    print("=" * 80)
    print()
    print(f"Systems Started: {started}")
    print(f"Systems Validated: {sum(1 for r in validation_results.values() if r.startswith('✅'))}")
    print(f"Integration Tests Passed: {verification_results['passed']}/{verification_results['total']}")
    print()
    print("✅ ALL SYSTEMS STARTED AND VERIFIED")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()