#!/usr/bin/env python3
"""
JARVIS Workflow Delegation Interceptor

Intercepts all work requests and enforces delegation-first workflow.
Ensures JARVIS always delegates, supervises, manages, coaches, and observes.

Tags: #DELEGATION #INTERCEPTOR #WORKFLOW #JEDI_MASTER @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWorkflowInterceptor")


class WorkflowDelegationInterceptor:
    """
    Workflow Delegation Interceptor

    Intercepts all work requests and enforces delegation-first workflow.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize interceptor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root

        # Load Jedi Master delegation workflow
        try:
            from jarvis_jedi_master_delegation_workflow import JARVISJediMasterDelegationWorkflow
            self.jedi_master_workflow = JARVISJediMasterDelegationWorkflow(project_root)
            logger.info("✅ Jedi Master delegation workflow loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load Jedi Master workflow: {e}")
            self.jedi_master_workflow = None

        logger.info("=" * 80)
        logger.info("🛡️  JARVIS WORKFLOW DELEGATION INTERCEPTOR")
        logger.info("=" * 80)
        logger.info("   Philosophy: Always delegate, never do work directly")
        logger.info("   Enforcement: All work requests intercepted and delegated")
        logger.info("=" * 80)

    def intercept_and_delegate(
        self,
        work_request: Dict[str, Any],
        direct_execution_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Intercept work request and enforce delegation

        Args:
            work_request: Work request dictionary
            direct_execution_callback: Optional callback for direct execution (will be blocked)

        Returns:
            Delegation result
        """
        logger.info("=" * 80)
        logger.info("🛡️  INTERCEPTING WORK REQUEST")
        logger.info("=" * 80)
        logger.info(f"   Title: {work_request.get('title', 'Unknown')}")
        logger.info(f"   Category: {work_request.get('category', 'general')}")

        # Block direct execution
        if direct_execution_callback:
            logger.warning("   ⚠️  Direct execution blocked - delegating instead")
            logger.warning("   🎯 Jedi Master Philosophy: Always delegate, never do work directly")

        # Delegate through Jedi Master workflow
        if not self.jedi_master_workflow:
            return {
                "success": False,
                "error": "Jedi Master workflow not available",
                "message": "Cannot delegate - workflow system unavailable"
            }

        result = self.jedi_master_workflow.process_work_request(
            title=work_request.get("title", "Untitled Work"),
            description=work_request.get("description", ""),
            priority=work_request.get("priority", 5),
            category=work_request.get("category", "general"),
            tags=work_request.get("tags", [])
        )

        logger.info("=" * 80)
        logger.info("✅ WORK REQUEST DELEGATED")
        logger.info("=" * 80)
        logger.info(f"   Request ID: {result.get('request_id')}")
        logger.info(f"   Delegation ID: {result.get('delegation_id')}")
        logger.info("=" * 80)

        return result

    def enforce_delegation_first(self, work_function: Callable) -> Callable:
        """
        Decorator to enforce delegation-first workflow

        Usage:
            @interceptor.enforce_delegation_first
            def my_work_function(request):
                # This will be intercepted and delegated
                pass
        """
        def wrapper(*args, **kwargs):
            # Extract work request from args/kwargs
            work_request = {}
            if args:
                if isinstance(args[0], dict):
                    work_request = args[0]
                else:
                    work_request = {"title": str(args[0])}
            work_request.update(kwargs)

            # Intercept and delegate
            return self.intercept_and_delegate(work_request, direct_execution_callback=work_function)

        return wrapper


# Global interceptor instance
_global_interceptor: Optional[WorkflowDelegationInterceptor] = None


def get_interceptor() -> WorkflowDelegationInterceptor:
    """Get global interceptor instance"""
    global _global_interceptor
    if _global_interceptor is None:
        _global_interceptor = WorkflowDelegationInterceptor()
    return _global_interceptor


def intercept_work_request(work_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to intercept and delegate work request

    Usage:
        result = intercept_work_request({
            "title": "Fix DNS issue",
            "description": "Fix homelab DNS services",
            "priority": 8,
            "category": "network"
        })
    """
    interceptor = get_interceptor()
    return interceptor.intercept_and_delegate(work_request)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Workflow Delegation Interceptor")
        parser.add_argument("--intercept", type=str, help="Intercept and delegate work request (JSON)")
        parser.add_argument("--test", action="store_true", help="Test interceptor")

        args = parser.parse_args()

        interceptor = WorkflowDelegationInterceptor()

        if args.intercept:
            work_request = json.loads(args.intercept)
            result = interceptor.intercept_and_delegate(work_request)
            print(json.dumps(result, indent=2, default=str))

        elif args.test:
            # Test interceptor
            test_request = {
                "title": "Test Work Request",
                "description": "Testing delegation interceptor",
                "priority": 5,
                "category": "test",
                "tags": ["test", "interceptor"]
            }
            result = interceptor.intercept_and_delegate(test_request)
            print(json.dumps(result, indent=2, default=str))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()