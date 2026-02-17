#!/usr/bin/env python3
"""
VA Systems Deployment Script

Deploys all VA enhancement systems and validates deployment.

Tags: #DEPLOYMENT #VIRTUAL_ASSISTANT #@DOIT @JARVIS @LUMINA
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
    from va_coordination_system import VACoordinationSystem
    from va_desktop_visualization import VADesktopVisualization
    from va_event_driven_activation import VAEventActivationSystem
    from va_health_monitoring import VAHealthMonitoring
    from va_knowledge_base import VAKnowledgeBase
    from va_resource_management import VAResourceManagement
    from va_specialization_system import VASpecializationSystem
    from va_system_integration import VASystemIntegration
    from va_task_queue import VATaskQueue
    from va_voice_command_processor import VAVoiceCommandProcessor
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VADeployment")


class VASystemsDeployment:
    """VA Systems Deployment Manager"""

    def __init__(self):
        """Initialize deployment"""
        self.registry = CharacterAvatarRegistry()
        self.systems = {}
        self.deployment_status = {}
        self.deployment_log = []

        logger.info("=" * 80)
        logger.info("🚀 VA SYSTEMS DEPLOYMENT")
        logger.info("=" * 80)

    def deploy_all_systems(self):
        """Deploy all VA systems"""
        print("=" * 80)
        print("🚀 DEPLOYING VA ENHANCEMENT SYSTEMS")
        print("=" * 80)
        print()

        systems_to_deploy = [
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

        deployed = 0
        failed = 0

        for name, system_factory in systems_to_deploy:
            try:
                print(f"Deploying {name}...", end=" ")
                system = system_factory()
                self.systems[name] = system
                self.deployment_status[name] = "✅ DEPLOYED"
                self.deployment_log.append({
                    "system": name,
                    "status": "deployed",
                    "timestamp": datetime.now().isoformat()
                })
                print("✅")
                deployed += 1
            except Exception as e:
                self.deployment_status[name] = f"❌ FAILED: {str(e)}"
                self.deployment_log.append({
                    "system": name,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"❌ Error: {e}")
                failed += 1

        print()
        print(f"✅ Deployed: {deployed}/{len(systems_to_deploy)}")
        if failed > 0:
            print(f"❌ Failed: {failed}/{len(systems_to_deploy)}")
        print()

        return deployed, failed

    def validate_deployment(self):
        """Validate deployed systems"""
        print("=" * 80)
        print("✅ VALIDATING DEPLOYMENT")
        print("=" * 80)
        print()

        validation_results = {}

        # Import enums for validation
        from va_coordination_system import TaskPriority
        from va_event_driven_activation import EventPriority, EventType

        # Test each system
        if "Coordination" in self.systems:
            try:
                coord = self.systems["Coordination"]
                task = coord.create_task("test", "Deployment test", priority=TaskPriority.MEDIUM)
                coord.complete_task(task.task_id)
                validation_results["Coordination"] = "✅ VALID"
            except Exception as e:
                validation_results["Coordination"] = f"❌ ERROR: {e}"

        if "Event Activation" in self.systems:
            try:
                events = self.systems["Event Activation"]
                event = events.trigger_event(EventType.SYSTEM_EVENT, "Test event", EventPriority.LOW)
                validation_results["Event Activation"] = "✅ VALID"
            except Exception as e:
                validation_results["Event Activation"] = f"❌ ERROR: {e}"

        if "System Integration" in self.systems:
            try:
                integration = self.systems["System Integration"]
                status = integration.get_integration_status()
                validation_results["System Integration"] = "✅ VALID"
            except Exception as e:
                validation_results["System Integration"] = f"❌ ERROR: {e}"

        if "Voice Commands" in self.systems:
            try:
                voice = self.systems["Voice Commands"]
                cmd = voice.process_voice_command(transcribed_text="Test command")
                validation_results["Voice Commands"] = "✅ VALID"
            except Exception as e:
                validation_results["Voice Commands"] = f"❌ ERROR: {e}"

        if "Desktop Visualization" in self.systems:
            try:
                viz = self.systems["Desktop Visualization"]
                dashboard = viz.multi_va_dashboard()
                validation_results["Desktop Visualization"] = "✅ VALID"
            except Exception as e:
                validation_results["Desktop Visualization"] = f"❌ ERROR: {e}"

        if "Specialization" in self.systems:
            try:
                spec = self.systems["Specialization"]
                matrix = spec.capability_matrix()
                validation_results["Specialization"] = "✅ VALID"
            except Exception as e:
                validation_results["Specialization"] = f"❌ ERROR: {e}"

        if "Health Monitoring" in self.systems:
            try:
                health = self.systems["Health Monitoring"]
                status = health.get_all_health_status()
                validation_results["Health Monitoring"] = "✅ VALID"
            except Exception as e:
                validation_results["Health Monitoring"] = f"❌ ERROR: {e}"

        if "Task Queue" in self.systems:
            try:
                queue = self.systems["Task Queue"]
                status = queue.get_queue_status()
                validation_results["Task Queue"] = "✅ VALID"
            except Exception as e:
                validation_results["Task Queue"] = f"❌ ERROR: {e}"

        if "Knowledge Base" in self.systems:
            try:
                kb = self.systems["Knowledge Base"]
                summary = kb.get_va_knowledge_summary("jarvis_va")
                validation_results["Knowledge Base"] = "✅ VALID"
            except Exception as e:
                validation_results["Knowledge Base"] = f"❌ ERROR: {e}"

        if "Analytics" in self.systems:
            try:
                analytics = self.systems["Analytics"]
                report = analytics.generate_report("jarvis_va", "24h")
                validation_results["Analytics"] = "✅ VALID"
            except Exception as e:
                validation_results["Analytics"] = f"❌ ERROR: {e}"

        if "Resource Management" in self.systems:
            try:
                resources = self.systems["Resource Management"]
                status = resources.get_resource_status()
                validation_results["Resource Management"] = "✅ VALID"
            except Exception as e:
                validation_results["Resource Management"] = f"❌ ERROR: {e}"

        # Print results
        print("Validation Results:")
        for system, result in validation_results.items():
            print(f"  {result} {system}")
        print()

        valid_count = sum(1 for r in validation_results.values() if r.startswith("✅"))
        total_count = len(validation_results)

        print(f"✅ Validated: {valid_count}/{total_count}")
        print()

        return validation_results

    def generate_deployment_report(self):
        try:
            """Generate deployment report"""
            report = {
                "deployment_date": datetime.now().isoformat(),
                "systems_deployed": len(self.systems),
                "deployment_status": self.deployment_status,
                "deployment_log": self.deployment_log
            }

            # Save report
            report_file = project_root / "data" / "va_deployment" / "deployment_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"📄 Deployment report saved to {report_file}")
            return report


        except Exception as e:
            self.logger.error(f"Error in generate_deployment_report: {e}", exc_info=True)
            raise
def main():
    """Main deployment function"""
    deployment = VASystemsDeployment()

    # Deploy all systems
    deployed, failed = deployment.deploy_all_systems()

    if failed > 0:
        print("⚠️  Some systems failed to deploy. Check errors above.")
        return 1

    # Validate deployment
    validation_results = deployment.validate_deployment()

    # Generate report
    report = deployment.generate_deployment_report()

    # Final status
    print("=" * 80)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 80)
    print()
    print(f"Systems Deployed: {deployed}")
    print(f"Systems Validated: {sum(1 for r in validation_results.values() if r.startswith('✅'))}")
    print()
    print("✅ DEPLOYMENT COMPLETE")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()