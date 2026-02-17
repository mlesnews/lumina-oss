#!/usr/bin/env python3
"""
Cursor Workspace Sync Cron Job
@MARVIN @JARVIS

Automatically syncs Cursor IDE workspace settings between workspace and non-workspace modes.
Designed to be run via cron for automatic synchronization.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from cursor_workspace_mode_manager import CursorWorkspaceModeManager
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [WorkspaceSync] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def main():
    """Main sync job"""
    try:
        manager = CursorWorkspaceModeManager()

        # Detect current mode
        state = manager.detect_workspace_mode()
        logger.info(f"Current mode: {state.mode.value}")

        # Auto-sync if needed
        synced = manager.auto_sync_if_needed()

        if synced:
            logger.info("✅ Settings synced successfully")

            # Get summary
            summary = manager.get_workflow_summary()
            logger.info(f"Workflow status: {'✅ Correct' if summary['workflow_correct'] else '⚠️ Issues detected'}")

            if summary['issues']:
                logger.warning(f"Issues: {', '.join(summary['issues'])}")
        else:
            logger.info("ℹ️ No sync needed")

        return 0

    except Exception as e:
        logger.error(f"❌ Sync failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":



    sys.exit(main())