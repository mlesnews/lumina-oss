#!/usr/bin/env python3
"""
Activate JEDI MASTER Delegation Workflow

Activates the JARVIS Jedi Master delegation workflow system.
Ensures all work requests are intercepted and delegated.

Tags: #ACTIVATION #JEDI_MASTER #DELEGATION #WORKFLOW @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ActivateJediMaster")


def activate_jedi_master_workflow():
    """Activate JEDI MASTER delegation workflow"""
    logger.info("=" * 80)
    logger.info("🎯 ACTIVATING JEDI MASTER DELEGATION WORKFLOW")
    logger.info("=" * 80)

    try:
        # Initialize workflow system
        from jarvis_jedi_master_delegation_workflow import JARVISJediMasterDelegationWorkflow
        workflow = JARVISJediMasterDelegationWorkflow(project_root)
        logger.info("   ✅ Jedi Master workflow initialized")

        # Initialize interceptor
        from jarvis_workflow_delegation_interceptor import WorkflowDelegationInterceptor
        interceptor = WorkflowDelegationInterceptor(project_root)
        logger.info("   ✅ Workflow interceptor initialized")

        # Get status
        status = workflow.get_workflow_status()
        logger.info(f"   📊 Workflow Status:")
        logger.info(f"      Total Requests: {status.get('total_requests', 0)}")
        logger.info(f"      Total Delegations: {status.get('total_delegations', 0)}")
        logger.info(f"      Workflow Active: {status.get('workflow_active', False)}")

        # Save activation record
        activation_file = project_root / "data" / "jedi_master_delegation" / "activation.json"
        activation_file.parent.mkdir(parents=True, exist_ok=True)

        activation_record = {
            "activated_at": datetime.now().isoformat(),
            "status": "active",
            "workflow_status": status,
            "philosophy": "Always delegate, supervise, manage, coach, observe",
            "never_do_work_directly": True
        }

        import json
        with open(activation_file, 'w', encoding='utf-8') as f:
            json.dump(activation_record, f, indent=2, default=str)

        logger.info("=" * 80)
        logger.info("✅ JEDI MASTER DELEGATION WORKFLOW ACTIVATED")
        logger.info("=" * 80)
        logger.info("   Philosophy: Always delegate, supervise, manage, coach, observe")
        logger.info("   Never do work directly - always delegate")
        logger.info("   All work requests will be intercepted and delegated")
        logger.info("=" * 80)

        return {
            "success": True,
            "activated_at": activation_record["activated_at"],
            "status": "active",
            "workflow_status": status
        }

    except Exception as e:
        logger.error(f"❌ Failed to activate Jedi Master workflow: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "activated_at": datetime.now().isoformat()
        }


def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Activate JEDI MASTER Delegation Workflow")
        parser.add_argument("--status", action="store_true", help="Check activation status")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        if args.status:
            # Check activation status
            activation_file = project_root / "data" / "jedi_master_delegation" / "activation.json"
            if activation_file.exists():
                import json
                with open(activation_file, 'r', encoding='utf-8') as f:
                    activation = json.load(f)

                if args.json:
                    print(json.dumps(activation, indent=2, default=str))
                else:
                    print("=" * 80)
                    print("🎯 JEDI MASTER DELEGATION WORKFLOW STATUS")
                    print("=" * 80)
                    print(f"   Status: {activation.get('status', 'unknown')}")
                    print(f"   Activated At: {activation.get('activated_at', 'unknown')}")
                    print(f"   Philosophy: {activation.get('philosophy', 'unknown')}")
                    print("=" * 80)
            else:
                if args.json:
                    print(json.dumps({"status": "not_activated"}, indent=2))
                else:
                    print("⚠️  Jedi Master workflow not activated")
        else:
            # Activate workflow
            result = activate_jedi_master_workflow()

            if args.json:
                import json
                print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()