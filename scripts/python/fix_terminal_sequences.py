#!/usr/bin/env python3
"""
Fix Terminal Sequences

Detects and fixes terminal sequence issues (orange triangle warnings).
Re-initializes terminal if sequences are out of order.

Tags: #TERMINAL #FIX #SEQUENCE @JARVIS @LUMINA
"""

import sys
import os
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from terminal_sequence_manager import (
        get_terminal_manager,
        reinitialize_terminal,
        record_terminal_sequence
    )
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from terminal_sequence_manager import (
            get_terminal_manager,
            reinitialize_terminal,
            record_terminal_sequence
        )
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("FixTerminalSequences")


def fix_terminal_sequences():
    """
    Fix terminal sequence issues by re-initializing terminal.

    This should be called when orange triangle warnings appear
    in the terminal, indicating sequences are out of order.
    """
    logger.info("=" * 60)
    logger.info("FIXING TERMINAL SEQUENCES")
    logger.info("=" * 60)

    # Try aggressive terminal restart first (actually restarts terminal)
    try:
        from terminal_restart_manager import restart_terminal_aggressive
        logger.info("   🔄 Restarting terminal (aggressive method)...")
        restart_success = restart_terminal_aggressive()
        if restart_success:
            logger.info("   ✅ Terminal restarted successfully")
    except ImportError:
        logger.debug("   Terminal restart manager not available")
    except Exception as e:
        logger.debug("   Terminal restart error: %s", e)

    # Fallback: Try PowerShell fix
    try:
        from terminal_sequence_powershell_fix import fix_terminal_via_powershell, send_sequence_reset
        logger.info("   🔧 Trying PowerShell fix (direct terminal interaction)...")
        ps_success = fix_terminal_via_powershell()
        send_sequence_reset()  # Also send direct reset
        if ps_success:
            logger.info("   ✅ PowerShell fix completed")
    except ImportError:
        logger.debug("   PowerShell fix not available")
    except Exception as e:
        logger.debug("   PowerShell fix error: %s", e)

    try:
        manager = get_terminal_manager()

        # Get current status
        status = manager.get_status()
        logger.info(f"   Current state: {status['state']}")
        logger.info(f"   Recent sequences: {' → '.join(status['recent_sequences'])}")
        logger.info(f"   Expected order: {' → '.join(status['expected_order'])}")

        # Check if sequences are out of order
        if status['state'] in ['out_of_order', 'error']:
            logger.warning("   ⚠️  Terminal sequences are out of order!")
            logger.info("   🔄 Re-initializing terminal...")

            # Re-initialize
            success = reinitialize_terminal()

            if success:
                logger.info("   ✅ Terminal re-initialized successfully")
                logger.info("   ✅ Orange triangle warnings should be resolved")

                # Record proper sequence to establish correct order
                logger.info("   📝 Recording proper sequence order...")
                record_terminal_sequence("A", process_id=os.getpid(), process_name="fix_terminal")
                time.sleep(0.1)
                record_terminal_sequence("B", process_id=os.getpid(), process_name="fix_terminal")
                time.sleep(0.1)
                record_terminal_sequence("P", process_id=os.getpid(), process_name="fix_terminal")

                logger.info("   ✅ Terminal sequences fixed!")
                return True
            else:
                logger.error("   ❌ Terminal re-initialization failed")
                return False
        else:
            logger.info("   ✅ Terminal sequences appear to be in order")

            # Still re-initialize to ensure clean state
            logger.info("   🔄 Re-initializing terminal for clean state...")
            success = reinitialize_terminal()

            if success:
                logger.info("   ✅ Terminal re-initialized - clean state established")
                return True
            else:
                logger.warning("   ⚠️  Re-initialization failed, but terminal may still be OK")
                return False

    except Exception as e:
        logger.error(f"   ❌ Error fixing terminal sequences: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix Terminal Sequences")
    parser.add_argument("--force", action="store_true", help="Force re-initialization")
    parser.add_argument("--status", action="store_true", help="Show status only")

    args = parser.parse_args()

    if args.status:
        try:
            manager = get_terminal_manager()
            status = manager.get_status()
            print("\n📊 Terminal Sequence Status:")
            print(f"   State: {status['state']}")
            print(f"   Ready: {status['ready']}")
            print(f"   Recent sequences: {' → '.join(status['recent_sequences'])}")
            print(f"   Expected order: {' → '.join(status['expected_order'])}")
            print(f"   Sequence count: {status['sequence_count']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        return

    if args.force:
        logger.info("   🔄 Force re-initializing terminal...")
        success = reinitialize_terminal()
        if success:
            logger.info("   ✅ Terminal force re-initialized")
        else:
            logger.error("   ❌ Force re-initialization failed")
        return

    # Normal fix
    success = fix_terminal_sequences()
    sys.exit(0 if success else 1)


if __name__ == "__main__":


    main()