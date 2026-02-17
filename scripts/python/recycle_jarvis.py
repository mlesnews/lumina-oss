#!/usr/bin/env python3
"""
Recycle JARVIS - Restart JARVIS Avatar System

Kills existing JARVIS processes and restarts the avatar with reset eye position.

Tags: #JARVIS #RECYCLE #RESTART #FIX #EYE_TRACKING @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_narrator_avatar import kill_existing_jarvis_processes, JARVISNarratorAvatar
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("RecycleJARVIS")


def recycle_jarvis():
    """Recycle JARVIS - Kill existing and restart (APPLYING LEARNED KNOWLEDGE)"""
    # PREVENT DUPLICATE EXECUTION - Check if another instance is already running
    try:
        from prevent_duplicate_script_execution import check_duplicate_script_execution, kill_duplicate_script_executions

        script_name = "recycle_jarvis.py"
        if check_duplicate_script_execution(script_name):
            logger.warning("⚠️  DUPLICATE DETECTED: Another recycle_jarvis.py is already running!")
            logger.warning("   Killing duplicate instances...")
            killed = kill_duplicate_script_executions(script_name)
            if killed > 0:
                logger.info(f"   ✅ Killed {killed} duplicate instance(s)")
                time.sleep(2.0)  # Wait for cleanup
            else:
                logger.error("   ❌ Could not kill duplicates - aborting to prevent conflicts")
                return 1
    except ImportError:
        logger.debug("Duplicate prevention not available")
    except Exception as e:
        logger.warning(f"Duplicate check error: {e}")

    logger.info("=" * 80)
    logger.info("🔄 RECYCLING JARVIS - KILLING KENNY & APPLYING LEARNED KNOWLEDGE")
    logger.info("=" * 80)
    logger.info("")

    # Step 0: Kill idle Cursor terminals first (cleanup)
    logger.info("Step 0: Cleaning up idle Cursor terminals...")
    try:
        from kill_idle_cursor_terminals import kill_idle_cursor_terminals
        idle_terminals_killed = kill_idle_cursor_terminals(max_idle_time=60.0, force=False)
        if idle_terminals_killed > 0:
            logger.info(f"   ✅ Killed {idle_terminals_killed} idle terminal(s)")
        else:
            logger.info("   ✅ No idle terminals found")
    except Exception as e:
        logger.debug(f"   Terminal cleanup error: {e}")
    logger.info("")

    # Step 1: Use MDV to visually detect JARVIS windows FIRST
    logger.info("Step 1: Using MDV Visual Detection Framework...")
    try:
        from jarvis_narrator_avatar import count_jarvis_windows_visually
        visual_count = count_jarvis_windows_visually()
        logger.info(f"   👁️  MDV detected {visual_count} JARVIS window(s) on desktop")
    except Exception as e:
        logger.warning(f"   ⚠️  MDV detection error: {e}")
        visual_count = 0
    logger.info("")

    # Step 2: Kill existing processes (aggressive multi-pass)
    logger.info("Step 2: Killing existing JARVIS processes (aggressive multi-pass)...")
    killed = kill_existing_jarvis_processes()
    logger.info(f"   ✅ Process killing complete: {killed} process(es) killed")
    logger.info("")

    # Step 3: Verify with MDV that all windows are closed
    logger.info("Step 3: Verifying with MDV that all windows are closed...")
    max_verification_attempts = 5
    for attempt in range(max_verification_attempts):
        time.sleep(1.5)  # Wait for windows to close
        try:
            remaining_visual = count_jarvis_windows_visually()
            logger.info(f"   📊 Attempt {attempt + 1}/{max_verification_attempts}: MDV detects {remaining_visual} window(s)")
            if remaining_visual == 0:
                logger.info("   ✅ MDV confirms all JARVIS windows are closed")
                break
            elif attempt < max_verification_attempts - 1:
                logger.warning(f"   ⚠️  Still {remaining_visual} window(s) detected - additional cleanup...")
                # Try one more kill pass
                kill_existing_jarvis_processes()
        except Exception as e:
            logger.debug(f"   Verification error: {e}")
    logger.info("")

    # Step 4: Start fresh JARVIS
    logger.info("Step 4: Starting fresh JARVIS instance...")
    try:
        narrator = JARVISNarratorAvatar()

        # Reset eye position immediately
        if hasattr(narrator, 'reset_eye_position'):
            narrator.reset_eye_position()
            logger.info("   ✅ Eye position reset to center")
        logger.info("")

        # Start JARVIS
        logger.info("Step 5: Running JARVIS...")
        logger.info("   ✅ JARVIS recycled and running")
        logger.info("")
        logger.info("=" * 80)

        narrator.run()
        return 0
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Error recycling JARVIS: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(recycle_jarvis())
