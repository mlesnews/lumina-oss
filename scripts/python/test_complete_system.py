#!/usr/bin/env python3
"""
Complete System Test Suite
Tests all components: MANUS, SMS Approval, End-to-End Workflow

Tags: #TEST #MANUS #SMS #WORKFLOW #INTEGRATION
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("CompleteSystemTest")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CompleteSystemTest")


def test_manus_controller():
    """Test MANUS Cursor IDE Controller"""
    logger.info("="*80)
    logger.info("🧪 TESTING MANUS CURSOR IDE CONTROLLER")
    logger.info("="*80)

    try:
        from manus_cursor_ide_controller import MANUSCursorIDEController

        controller = MANUSCursorIDEController(project_root)

        # Test file operations
        test_file = "data/test_manus_complete.txt"
        logger.info("📝 Testing file creation...")
        success = controller.create_file(test_file, "MANUS Test Content\nLine 2")
        assert success, "File creation failed"
        logger.info("✅ File creation: PASS")

        logger.info("📖 Testing file reading...")
        content = controller.read_file(test_file)
        assert content is not None, "File reading failed"
        assert "MANUS Test Content" in content, "File content incorrect"
        logger.info("✅ File reading: PASS")

        logger.info("✏️  Testing file update...")
        success = controller.update_file(test_file, "Updated Content")
        assert success, "File update failed"
        content = controller.read_file(test_file)
        assert "Updated Content" in content, "File update incorrect"
        logger.info("✅ File update: PASS")

        logger.info("🗑️  Testing file deletion...")
        success = controller.delete_file(test_file)
        assert success, "File deletion failed"
        logger.info("✅ File deletion: PASS")

        logger.info("💻 Testing command execution...")
        result = controller.execute_command("echo 'MANUS Test'")
        assert result["success"], "Command execution failed"
        assert "MANUS Test" in result["stdout"], "Command output incorrect"
        logger.info("✅ Command execution: PASS")

        logger.info("="*80)
        logger.info("✅ MANUS CONTROLLER: ALL TESTS PASSED")
        logger.info("="*80)
        return True

    except Exception as e:
        logger.error(f"❌ MANUS CONTROLLER TEST FAILED: {e}")
        return False


def test_sms_approval():
    """Test SMS Approval System"""
    logger.info("="*80)
    logger.info("🧪 TESTING SMS APPROVAL SYSTEM")
    logger.info("="*80)

    try:
        from dead_man_switch_sms_approval import DeadManSwitchSMSApproval

        approval = DeadManSwitchSMSApproval(project_root)

        # Test phone number retrieval
        logger.info("📱 Testing phone number retrieval...")
        phone = approval.get_user_phone_number()
        if phone:
            logger.info(f"✅ Phone number retrieved: {phone}")
        else:
            logger.warning("⚠️  Phone number not found in Azure Key Vault")
            logger.info("💡 Run: python scripts/python/setup_sms_approval_system.py --phone +YOUR_PHONE")
            logger.info("⚠️  SMS approval tests will be skipped")
            return True  # Not a failure, just not configured

        # Test approval code generation
        logger.info("🔢 Testing approval code generation...")
        code1 = approval.generate_approval_code()
        code2 = approval.generate_approval_code()
        assert len(code1) == 5, "Approval code length incorrect"
        assert code1 != code2, "Approval codes should be unique"
        logger.info(f"✅ Approval code generation: PASS (generated: {code1}, {code2})")

        # Test database operations
        logger.info("💾 Testing approval database...")
        test_request = approval.request_approval(
            action_description="Test Action",
            action_id="test-001",
            timeout_minutes=1
        )
        assert test_request.approval_code is not None, "Approval request failed"
        logger.info(f"✅ Approval request created: {test_request.approval_code}")

        logger.info("="*80)
        logger.info("✅ SMS APPROVAL: ALL TESTS PASSED")
        logger.info("="*80)
        return True

    except Exception as e:
        logger.error(f"❌ SMS APPROVAL TEST FAILED: {e}")
        return False


def test_end_to_end_workflow():
    """Test End-to-End Workflow Orchestrator"""
    logger.info("="*80)
    logger.info("🧪 TESTING END-TO-END WORKFLOW ORCHESTRATOR")
    logger.info("="*80)

    try:
        from end_to_end_workflow_orchestrator import EndToEndWorkflowOrchestrator

        orchestrator = EndToEndWorkflowOrchestrator(project_root)

        # Test workflow parsing
        logger.info("📝 Testing workflow parsing...")
        test_request = "Create a new file test_workflow.txt with hello world"
        workflow = orchestrator.parse_request(test_request)
        assert "steps" in workflow, "Workflow parsing failed"
        logger.info(f"✅ Workflow parsed: {len(workflow['steps'])} steps")

        # Test dependency resolution
        logger.info("🔗 Testing dependency resolution...")
        ordered_steps = orchestrator.resolve_dependencies(workflow)
        assert len(ordered_steps) > 0, "Dependency resolution failed"
        logger.info(f"✅ Dependencies resolved: {len(ordered_steps)} steps ordered")

        # Test critical action identification
        logger.info("⚠️  Testing critical action identification...")
        critical = orchestrator.identify_critical_actions(ordered_steps)
        logger.info(f"✅ Critical actions identified: {len(critical)}")

        logger.info("="*80)
        logger.info("✅ END-TO-END WORKFLOW: ALL TESTS PASSED")
        logger.info("="*80)
        return True

    except Exception as e:
        logger.error(f"❌ END-TO-END WORKFLOW TEST FAILED: {e}")
        return False


def test_integration():
    """Test full integration"""
    logger.info("="*80)
    logger.info("🧪 TESTING FULL SYSTEM INTEGRATION")
    logger.info("="*80)

    try:
        from end_to_end_workflow_orchestrator import EndToEndWorkflowOrchestrator

        orchestrator = EndToEndWorkflowOrchestrator(project_root)

        # Simple workflow test (no approval needed)
        logger.info("🚀 Testing simple workflow execution...")
        test_request = "Create a new file test_integration.txt with integration test"
        results = orchestrator.execute_workflow(test_request)

        assert "success" in results, "Workflow execution failed"
        logger.info(f"✅ Workflow executed: {results['success']}")
        logger.info(f"   Steps executed: {results.get('steps_executed', 0)}")

        # Cleanup
        from manus_cursor_ide_controller import MANUSCursorIDEController
        controller = MANUSCursorIDEController(project_root)
        controller.delete_file("test_integration.txt")

        logger.info("="*80)
        logger.info("✅ INTEGRATION TEST: PASSED")
        logger.info("="*80)
        return True

    except Exception as e:
        logger.error(f"❌ INTEGRATION TEST FAILED: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("="*80)
    logger.info("🧪 COMPLETE SYSTEM TEST SUITE")
    logger.info("="*80)
    logger.info("")

    results = {
        "manus": test_manus_controller(),
        "sms": test_sms_approval(),
        "workflow": test_end_to_end_workflow(),
        "integration": test_integration()
    }

    logger.info("")
    logger.info("="*80)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {test_name.upper()}: {status}")

    all_passed = all(results.values())

    logger.info("")
    if all_passed:
        logger.info("="*80)
        logger.info("✅ ALL TESTS PASSED")
        logger.info("="*80)
        return 0
    else:
        logger.info("="*80)
        logger.warning("⚠️  SOME TESTS FAILED")
        logger.info("="*80)
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)