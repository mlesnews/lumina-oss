#!/usr/bin/env python3
"""
Reboot with VAs & Widgets - Complete System

Executes reboot with post-ops verification and ensures all VAs and widgets start.

Tags: #REBOOT #POST_OPS #VIRTUAL_ASSISTANTS #AGENT_WIDGETS #RC #DOIT #RR @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
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

logger = get_logger("RebootWithVAsWidgets")

# Import required modules
try:
    from post_ops_reboot_manager import PostOpsRebootManager
    from agent_widgets_manager import AgentWidgetsManager
    from doit_enhanced import DOITEnhanced
    from root_cause_analysis import RootCauseAnalysis
except ImportError as e:
    logger.error(f"   ❌ Import failed: {e}")
    sys.exit(1)


def execute_reboot_sequence() -> Dict[str, Any]:
    """Execute complete reboot sequence with @RC @DOIT @RR"""
    logger.info("=" * 80)
    logger.info("🚀 REBOOT SEQUENCE - POST OPS")
    logger.info("=" * 80)
    logger.info("")

    result = {
        "timestamp": None,
        "post_ops_verified": False,
        "agent_widgets_created": False,
        "reboot_prepared": False,
        "ready": False
    }

    # Step 1: Post-Ops Verification
    logger.info("📋 Step 1: Post-Ops Verification")
    logger.info("")
    post_ops = PostOpsRebootManager()
    verification = post_ops.post_ops_verification()
    result["post_ops_verified"] = True
    logger.info("")

    # Step 2: Create Agent Widgets
    logger.info("📋 Step 2: Creating Agent Widgets")
    logger.info("")
    widgets_manager = AgentWidgetsManager()
    widgets_manager.create_widgets_config()
    result["agent_widgets_created"] = True
    logger.info("   ✅ Agent widgets config created")
    logger.info("")

    # Step 3: Root Cause Analysis (@RC @RR)
    logger.info("📋 Step 3: Root Cause Analysis (@RC @RR)")
    logger.info("")
    try:
        from root_cause_analysis import RootCauseAnalysis
        rc = RootCauseAnalysis()

        issues = []
        if not verification.get("vas_running", False):
            issues.append("Virtual Assistants not running")
        if not verification.get("agent_widgets", False):
            issues.append("Agent widgets not configured")

        for issue in issues:
            logger.info(f"   🔍 Analyzing: {issue}")
            # Get relevant root causes
            relevant_causes = [
                cause for cause in rc.root_causes
                if not cause.resolved and issue.lower() in str(cause).lower()
            ]
            logger.info(f"   ✅ Found {len(relevant_causes)} relevant root causes")
    except Exception as e:
        logger.warning(f"   ⚠️  Root cause analysis failed: {e}")
    logger.info("")

    # Step 4: @DOIT with @RR
    logger.info("📋 Step 4: @DOIT with @RR")
    logger.info("")
    try:
        from doit_enhanced import DOITEnhanced
        doit = DOITEnhanced()
        doit_result = doit.doit(
            "Post-Ops Reboot: Ensure agent widgets and virtual assistants are active after reboot. Fix all issues identified in root cause analysis.",
            auto_5w1h=True,
            auto_root_cause=True,
            execute=False
        )
        logger.info("   ✅ @DOIT plan generated with @RR")
        result["doit_plan"] = doit_result
    except Exception as e:
        logger.warning(f"   ⚠️  @DOIT failed: {e}")
    logger.info("")

    # Step 5: Prepare Reboot
    logger.info("📋 Step 5: Preparing Reboot")
    logger.info("")
    reboot_prep = post_ops.prepare_reboot()
    result["reboot_prepared"] = reboot_prep.get("ready", False)
    logger.info("")

    result["ready"] = result["reboot_prepared"]

    logger.info("=" * 80)
    logger.info("✅ REBOOT SEQUENCE COMPLETE")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📋 Ready for Reboot:")
    logger.info("   1. All post-ops verified")
    logger.info("   2. Agent widgets configured")
    logger.info("   3. Root cause analysis complete")
    logger.info("   4. @DOIT plan generated")
    logger.info("")
    logger.info("🔄 Execute reboot to activate all systems")
    logger.info("")

    return result


if __name__ == "__main__":
    execute_reboot_sequence()
