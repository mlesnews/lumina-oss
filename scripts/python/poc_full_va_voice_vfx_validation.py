#!/usr/bin/env python3
"""
POC Full VA Voice/VFX Validation Testing

Comprehensive proof-of-concept validation for:
- Full voice mode system
- AI VFX system
- Company-wide collaboration
- Real-time VA coordination

This script validates all components and generates a proof report.

Tags: #POC #VALIDATION #PROOF #VOICE #VFX #COLLABORATION @JARVIS @LUMINA
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("POCFullVAValidation")

# Import all systems
try:
    from va_full_voice_vfx_collaboration_integration import VAFullVoiceVFXCollaborationIntegration
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger.error("❌ Integration system not available")
    sys.exit(1)


class POCValidationResults:
    """POC validation results"""

    def __init__(self):
        self.tests: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        self.end_time = None
        self.overall_status = "PENDING"

    def add_test(self, name: str, status: str, details: Dict[str, Any] = None):
        """Add a test result"""
        self.tests.append({
            "name": name,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"{'✅' if status == 'PASS' else '❌'} {name}: {status}")

    def finalize(self):
        """Finalize validation"""
        self.end_time = datetime.now()
        passed = sum(1 for t in self.tests if t["status"] == "PASS")
        total = len(self.tests)
        self.overall_status = "PASS" if passed == total else "PARTIAL" if passed > 0 else "FAIL"

        logger.info("=" * 80)
        logger.info(f"📊 VALIDATION COMPLETE: {passed}/{total} tests passed")
        logger.info(f"   Status: {self.overall_status}")
        logger.info("=" * 80)

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        passed = sum(1 for t in self.tests if t["status"] == "PASS")
        failed = sum(1 for t in self.tests if t["status"] == "FAIL")

        return {
            "validation_id": f"poc_{int(self.start_time.timestamp())}",
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration,
            "overall_status": self.overall_status,
            "summary": {
                "total_tests": len(self.tests),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{(passed/len(self.tests)*100):.1f}%" if self.tests else "0%"
            },
            "tests": self.tests
        }


def validate_system_initialization(integration: VAFullVoiceVFXCollaborationIntegration, results: POCValidationResults):
    """Validate system initialization"""
    logger.info("🔍 Validating system initialization...")

    # Test orchestrator
    if integration.orchestrator:
        results.add_test("Orchestrator Initialization", "PASS", {
            "monitors": len(integration.orchestrator.monitors),
            "manifests": len(integration.orchestrator.manifests)
        })
    else:
        results.add_test("Orchestrator Initialization", "FAIL", {"error": "Orchestrator not initialized"})

    # Test voice system
    if integration.voice_system:
        voice_status = integration.voice_system.get_status()
        results.add_test("Voice System Initialization", "PASS", {
            "tts_systems": voice_status.get("tts_systems", []),
            "voice_recognition_available": voice_status.get("voice_recognition_available", False)
        })
    else:
        results.add_test("Voice System Initialization", "FAIL", {"error": "Voice system not initialized"})

    # Test VFX system
    if integration.vfx_system:
        vfx_status = integration.vfx_system.get_status()
        results.add_test("VFX System Initialization", "PASS", {
            "registered_vas": len(vfx_status.get("registered_vas", [])),
            "active_effects": vfx_status.get("active_effects", 0)
        })
    else:
        results.add_test("VFX System Initialization", "FAIL", {"error": "VFX system not initialized"})

    # Test collaboration system
    if integration.collaboration_system:
        collab_status = integration.collaboration_system.get_company_status()
        results.add_test("Collaboration System Initialization", "PASS", {
            "registered_vas": len(collab_status.get("registered_vas", [])),
            "voice_mode_active": collab_status.get("voice_mode_active", False)
        })
    else:
        results.add_test("Collaboration System Initialization", "FAIL", {"error": "Collaboration system not initialized"})


def validate_va_registration(integration: VAFullVoiceVFXCollaborationIntegration, results: POCValidationResults):
    """Validate VA registration"""
    logger.info("🔍 Validating VA registration...")

    expected_vas = ["ironman", "kenny", "anakin", "jarvis"]
    registered_vas = list(integration.va_instances.keys())

    for va_name in expected_vas:
        if va_name in registered_vas:
            results.add_test(f"VA Registration: {va_name}", "PASS", {
                "registered": True,
                "has_proxy": True
            })
        else:
            results.add_test(f"VA Registration: {va_name}", "FAIL", {
                "registered": False,
                "error": "VA not registered"
            })


def validate_voice_system(integration: VAFullVoiceVFXCollaborationIntegration, results: POCValidationResults):
    """Validate voice system functionality"""
    logger.info("🔍 Validating voice system...")

    if not integration.voice_system:
        results.add_test("Voice System: TTS Queue", "FAIL", {"error": "Voice system not available"})
        return

    # Test TTS queue
    try:
        request_id = integration.voice_system.speak("jarvis", "Test message", blocking=False)
        if request_id:
            results.add_test("Voice System: TTS Queue", "PASS", {"request_id": request_id})
        else:
            results.add_test("Voice System: TTS Queue", "FAIL", {"error": "Failed to queue TTS"})
    except Exception as e:
        results.add_test("Voice System: TTS Queue", "FAIL", {"error": str(e)})

    # Test voice mode activation
    try:
        integration.voice_system.start_full_voice_mode()
        time.sleep(1)
        status = integration.voice_system.get_status()
        if status.get("voice_mode_active"):
            results.add_test("Voice System: Full Voice Mode", "PASS", {"active": True})
        else:
            results.add_test("Voice System: Full Voice Mode", "FAIL", {"error": "Voice mode not active"})
    except Exception as e:
        results.add_test("Voice System: Full Voice Mode", "FAIL", {"error": str(e)})


def validate_vfx_system(integration: VAFullVoiceVFXCollaborationIntegration, results: POCValidationResults):
    """Validate VFX system functionality"""
    logger.info("🔍 Validating VFX system...")

    if not integration.vfx_system:
        results.add_test("VFX System: Effect Creation", "FAIL", {"error": "VFX system not available"})
        return

    # Test glow effect
    try:
        from va_ai_vfx_system import VFXIntensity
        effect_id = integration.vfx_system.create_glow_effect("jarvis", VFXIntensity.NORMAL, duration=1.0)
        if effect_id:
            results.add_test("VFX System: Glow Effect", "PASS", {"effect_id": effect_id})
        else:
            results.add_test("VFX System: Glow Effect", "FAIL", {"error": "Failed to create glow"})
    except Exception as e:
        results.add_test("VFX System: Glow Effect", "FAIL", {"error": str(e)})

    # Test particle effect
    try:
        effect_id = integration.vfx_system.create_particle_effect("ironman", particle_count=50, duration=1.0)
        if effect_id:
            results.add_test("VFX System: Particle Effect", "PASS", {"effect_id": effect_id})
        else:
            results.add_test("VFX System: Particle Effect", "FAIL", {"error": "Failed to create particles"})
    except Exception as e:
        results.add_test("VFX System: Particle Effect", "FAIL", {"error": str(e)})

    # Test beam effect
    try:
        effect_id = integration.vfx_system.create_beam_effect("jarvis", "ironman", VFXIntensity.NORMAL, duration=1.0)
        if effect_id:
            results.add_test("VFX System: Beam Effect", "PASS", {"effect_id": effect_id})
        else:
            results.add_test("VFX System: Beam Effect", "FAIL", {"error": "Failed to create beam"})
    except Exception as e:
        results.add_test("VFX System: Beam Effect", "FAIL", {"error": str(e)})

    # Wait for effects to update
    time.sleep(1)

    # Test effect updates
    try:
        integration.vfx_system.update_effects(0.016)  # One frame
        status = integration.vfx_system.get_status()
        results.add_test("VFX System: Effect Updates", "PASS", {
            "active_effects": status.get("active_effects", 0),
            "total_particles": status.get("total_particles", 0)
        })
    except Exception as e:
        results.add_test("VFX System: Effect Updates", "FAIL", {"error": str(e)})


def validate_collaboration_system(integration: VAFullVoiceVFXCollaborationIntegration, results: POCValidationResults):
    """Validate collaboration system functionality"""
    logger.info("🔍 Validating collaboration system...")

    if not integration.collaboration_system:
        results.add_test("Collaboration System: Message Routing", "FAIL", {"error": "Collaboration system not available"})
        return

    # Test message routing
    try:
        from va_company_collaboration_system import CollaborationType
        message_id = integration.collaboration_system.send_collaboration_message(
            "jarvis",
            "ironman",
            CollaborationType.VOICE,
            {"text": "Test message"}
        )
        if message_id:
            results.add_test("Collaboration System: Message Routing", "PASS", {"message_id": message_id})
        else:
            results.add_test("Collaboration System: Message Routing", "FAIL", {"error": "Failed to send message"})
    except Exception as e:
        results.add_test("Collaboration System: Message Routing", "FAIL", {"error": str(e)})

    # Test task distribution
    try:
        message_id = integration.collaboration_system.send_collaboration_message(
            "jarvis",
            None,  # Broadcast
            CollaborationType.TASK,
            {
                "task": {
                    "type": "test",
                    "description": "Test task",
                    "priority": "MEDIUM"
                }
            }
        )
        if message_id:
            results.add_test("Collaboration System: Task Distribution", "PASS", {"message_id": message_id})
        else:
            results.add_test("Collaboration System: Task Distribution", "FAIL", {"error": "Failed to distribute task"})
    except Exception as e:
        results.add_test("Collaboration System: Task Distribution", "FAIL", {"error": str(e)})

    # Test company status
    try:
        status = integration.collaboration_system.get_company_status()
        results.add_test("Collaboration System: Company Status", "PASS", {
            "all_vas_online": status.get("all_vas_online", False),
            "active_tasks": status.get("active_tasks", 0)
        })
    except Exception as e:
        results.add_test("Collaboration System: Company Status", "FAIL", {"error": str(e)})


def validate_integration_coordination(integration: VAFullVoiceVFXCollaborationIntegration, results: POCValidationResults):
    """Validate integration coordination"""
    logger.info("🔍 Validating integration coordination...")

    # Test full integration status
    try:
        status = integration.get_full_status()
        results.add_test("Integration: Full Status", "PASS", {
            "systems_active": sum(1 for v in status.get("systems", {}).values() if v),
            "registered_vas": len(status.get("registered_vas", []))
        })
    except Exception as e:
        results.add_test("Integration: Full Status", "FAIL", {"error": str(e)})

    # Test demonstration
    try:
        integration.demonstrate_collaboration()
        results.add_test("Integration: Collaboration Demo", "PASS", {"demo_completed": True})
    except Exception as e:
        results.add_test("Integration: Collaboration Demo", "FAIL", {"error": str(e)})


def run_full_validation():
    try:
        """Run full POC validation"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING POC FULL VA VOICE/VFX VALIDATION")
        logger.info("=" * 80)
        logger.info("")

        project_root = Path(__file__).parent.parent.parent
        integration = VAFullVoiceVFXCollaborationIntegration(project_root)

        # Initialize systems
        logger.info("📋 Initializing systems...")
        integration.initialize_systems()
        time.sleep(2)

        # Register VAs
        logger.info("📋 Registering VAs...")
        integration._register_all_vas()
        time.sleep(1)

        # Create validation results
        results = POCValidationResults()

        # Run validation tests
        logger.info("")
        logger.info("🧪 Running validation tests...")
        logger.info("")

        validate_system_initialization(integration, results)
        time.sleep(1)

        validate_va_registration(integration, results)
        time.sleep(1)

        validate_voice_system(integration, results)
        time.sleep(1)

        validate_vfx_system(integration, results)
        time.sleep(1)

        validate_collaboration_system(integration, results)
        time.sleep(1)

        validate_integration_coordination(integration, results)
        time.sleep(1)

        # Finalize
        results.finalize()

        # Generate report
        report = results.generate_report()

        # Save report
        report_file = project_root / "data" / "poc_validation_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("")
        logger.info(f"📄 Validation report saved: {report_file}")
        logger.info("")

        # Print summary
        print("=" * 80)
        print("📊 POC VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Status: {report['overall_status']}")
        print(f"Tests: {report['summary']['passed']}/{report['summary']['total_tests']} passed")
        print(f"Pass Rate: {report['summary']['pass_rate']}")
        print(f"Duration: {report['duration_seconds']:.2f} seconds")
        print("=" * 80)
        print()

        # Print test details
        print("Test Results:")
        for test in report['tests']:
            status_icon = "✅" if test['status'] == "PASS" else "❌"
            print(f"  {status_icon} {test['name']}: {test['status']}")
            if test.get('details'):
                for key, value in test['details'].items():
                    print(f"      {key}: {value}")
        print()

        return report


    except Exception as e:
        logger.error(f"Error in run_full_validation: {e}", exc_info=True)
        raise
def main():
    """Main entry point"""
    try:
        report = run_full_validation()

        # Exit with appropriate code
        if report['overall_status'] == "PASS":
            sys.exit(0)
        elif report['overall_status'] == "PARTIAL":
            sys.exit(1)
        else:
            sys.exit(2)
    except KeyboardInterrupt:
        logger.info("🛑 Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Validation error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":


    main()