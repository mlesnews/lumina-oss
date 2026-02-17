#!/usr/bin/env python3
"""
Auto Fix and Rerun Request ID Workflow

PERMANENT WORKFLOW: When a Request ID is pasted, automatically:
1. Fix the connection error
2. Find the original @ask/job that caused it
3. Rerun that job

This is a permanent entry in our workflows - whenever we paste a Request ID,
it triggers this automatic fix and rerun process.

Tags: #BAU #AUTOMATION #CONNECTION_ERROR #RETRY #REQUEST_ID @JARVIS @LUMINA
"""

import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AutoFixAndRerunRequestID")


# UUID pattern for Request ID detection
REQUEST_ID_PATTERN = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    re.IGNORECASE
)


def detect_request_id(text: str) -> Optional[str]:
    """
    Detect Request ID in text (UUID format)

    Args:
        text: Text to search for Request ID

    Returns:
        Request ID if found, None otherwise
    """
    match = REQUEST_ID_PATTERN.search(text)
    if match:
        return match.group(0)
    return None


def auto_fix_and_rerun_request_id(request_id: str) -> Dict[str, Any]:
    """
    Auto Fix and Rerun Request ID Workflow

    PERMANENT WORKFLOW: When a Request ID is pasted:
    1. Fix the connection error
    2. Find the original @ask/job that caused it
    3. Rerun that job

    Args:
        request_id: The Request ID to fix and rerun

    Returns:
        Workflow result dictionary
    """
    logger.info("=" * 80)
    logger.info("🔄 AUTO FIX AND RERUN REQUEST ID WORKFLOW")
    logger.info("=" * 80)
    logger.info(f"Request ID: {request_id}")
    logger.info("")

    workflow_result = {
        "request_id": request_id,
        "timestamp": datetime.now().isoformat(),
        "workflow": "auto_fix_and_rerun",
        "status": "processing",
        "steps": {},
        "success": False,
        "errors": []
    }

    # STEP 1: Fix Connection Error
    logger.info("STEP 1: Fixing Connection Error...")
    logger.info("-" * 80)
    try:
        from fix_request_id_connection_error import fix_request_id_connection_error

        fix_result = fix_request_id_connection_error(request_id)
        workflow_result["steps"]["fix_connection_error"] = {
            "status": fix_result.get("status", "unknown"),
            "steps_completed": fix_result.get("steps_completed", []),
            "fixes_applied": fix_result.get("fixes_applied", []),
            "errors": fix_result.get("errors", [])
        }

        if fix_result.get("errors"):
            workflow_result["errors"].extend(fix_result["errors"])

        logger.info(f"   ✅ Connection error fix completed")
        logger.info(f"      Steps: {len(fix_result.get('steps_completed', []))}")
        logger.info(f"      Fixes: {len(fix_result.get('fixes_applied', []))}")
        logger.info("")

    except Exception as e:
        error_msg = f"Failed to fix connection error: {e}"
        logger.error(f"   ❌ {error_msg}")
        workflow_result["errors"].append(error_msg)
        workflow_result["steps"]["fix_connection_error"] = {
            "status": "error",
            "error": str(e)
        }
        logger.info("")

    # STEP 2: Find Original @ask/Job
    logger.info("STEP 2: Finding Original @ask/Job...")
    logger.info("-" * 80)
    ask_text = None
    ask_entry = None

    try:
        from find_ask_by_request_id import find_ask_by_request_id

        # Search last 30 days for the original @ask
        ask_result = find_ask_by_request_id(request_id, days_back=30)

        if ask_result and ask_result.get("found"):
            ask_text = ask_result.get("ask_text")
            ask_entry = ask_result
            workflow_result["steps"]["find_original_ask"] = {
                "status": "found",
                "file": ask_result.get("file"),
                "file_time": ask_result.get("file_time"),
                "ask_text": ask_text[:200] if ask_text else None
            }

            logger.info(f"   ✅ Original @ask found")
            logger.info(f"      File: {ask_result.get('file', 'unknown')}")
            if ask_text:
                logger.info(f"      Ask: {ask_text[:100]}...")
            logger.info("")
        else:
            workflow_result["steps"]["find_original_ask"] = {
                "status": "not_found",
                "message": "Original @ask not found in recent chat histories"
            }

            logger.warning(f"   ⚠️  Original @ask not found in recent chat histories")
            logger.info(f"      Searched last 30 days")
            logger.info("")

    except Exception as e:
        error_msg = f"Failed to find original @ask: {e}"
        logger.error(f"   ❌ {error_msg}")
        workflow_result["errors"].append(error_msg)
        workflow_result["steps"]["find_original_ask"] = {
            "status": "error",
            "error": str(e)
        }
        logger.info("")

    # STEP 3: Rerun the Job
    logger.info("STEP 3: Rerunning the Job...")
    logger.info("-" * 80)

    if ask_text:
        try:
            from retry_ask_with_request_id import retry_ask_with_request_id

            retry_result = retry_ask_with_request_id(request_id)

            if retry_result.get("success"):
                workflow_result["steps"]["rerun_job"] = {
                    "status": "ready",
                    "ask_text": retry_result.get("ask_text"),
                    "retry_count": retry_result.get("retry_count", 0),
                    "workflow": retry_result.get("workflow", "@bau")
                }

                logger.info(f"   ✅ Job ready for rerun as @bau")
                logger.info(f"      Retry count: {retry_result.get('retry_count', 0)}")
                logger.info(f"      Ask: {retry_result.get('ask_text', '')[:100]}...")
                logger.info("")
                logger.info("   📋 NEXT STEP: Execute the @ask as @bau:")
                logger.info(f"      @bau {retry_result.get('ask_text', '')}")
                logger.info("")

                workflow_result["success"] = True
                workflow_result["status"] = "ready_for_rerun"
            else:
                error_msg = retry_result.get("error", "Unknown error")
                logger.error(f"   ❌ Failed to prepare job rerun: {error_msg}")
                workflow_result["errors"].append(error_msg)
                workflow_result["steps"]["rerun_job"] = {
                    "status": "error",
                    "error": error_msg
                }
                logger.info("")

        except Exception as e:
            error_msg = f"Failed to rerun job: {e}"
            logger.error(f"   ❌ {error_msg}")
            workflow_result["errors"].append(error_msg)
            workflow_result["steps"]["rerun_job"] = {
                "status": "error",
                "error": str(e)
            }
            logger.info("")
    else:
        logger.warning(f"   ⚠️  Cannot rerun job - original @ask not found")
        logger.info(f"      Please provide the original request manually")
        logger.info("")

        workflow_result["steps"]["rerun_job"] = {
            "status": "skipped",
            "reason": "Original @ask not found"
        }

    # Final Status
    if workflow_result["success"]:
        workflow_result["status"] = "completed"
        logger.info("=" * 80)
        logger.info("✅ WORKFLOW COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Status: Ready for rerun")
        logger.info("")
    else:
        workflow_result["status"] = "completed_with_errors"
        logger.info("=" * 80)
        logger.info("⚠️  WORKFLOW COMPLETED WITH ERRORS")
        logger.info("=" * 80)
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Errors: {len(workflow_result['errors'])}")
        for error in workflow_result["errors"]:
            logger.info(f"   • {error}")
        logger.info("")

    # Save workflow result
    try:
        diagnostics_dir = project_root / "data" / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        result_file = diagnostics_dir / f"auto_fix_rerun_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_result, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Workflow result saved: {result_file}")
        logger.info("")

    except Exception as e:
        logger.warning(f"   ⚠️  Failed to save workflow result: {e}")

    return workflow_result


def process_user_input(user_input: str) -> Optional[Dict[str, Any]]:
    """
    Process user input and detect Request ID

    If Request ID is detected, automatically trigger fix and rerun workflow.

    Args:
        user_input: User input text

    Returns:
        Workflow result if Request ID detected, None otherwise
    """
    request_id = detect_request_id(user_input)

    if request_id:
        logger.info(f"🔍 Request ID detected: {request_id}")
        logger.info("   Triggering auto fix and rerun workflow...")
        logger.info("")

        return auto_fix_and_rerun_request_id(request_id)

    return None


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Auto Fix and Rerun Request ID Workflow - Permanent Entry"
        )
        parser.add_argument(
            "request_id",
            nargs="?",
            help="Request ID to fix and rerun (or will detect from input)"
        )
        parser.add_argument(
            "--input",
            help="User input text to search for Request ID"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )

        args = parser.parse_args()

        if args.request_id:
            # Direct Request ID provided
            result = auto_fix_and_rerun_request_id(args.request_id)
        elif args.input:
            # Search input for Request ID
            result = process_user_input(args.input)
            if not result:
                print("❌ No Request ID detected in input")
                return 1
        else:
            parser.print_help()
            return 1

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            # Results already printed by workflow
            pass

        return 0 if result.get("success") else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())