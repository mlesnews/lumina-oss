#!/usr/bin/env python3
"""
File Pin Manager - Manage pinned files for auto-close system

Provides CLI interface for pinning/unpinning files to prevent auto-close.
"""

import argparse
import sys
from pathlib import Path
from file_auto_close_manager import FileAutoCloseManager
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("file_pin_manager")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def main():
    try:
        """Main CLI interface for file pinning"""
        parser = argparse.ArgumentParser(description="File Pin Manager")
        parser.add_argument("action", choices=["pin", "unpin", "list", "status"],
                           help="Action to perform")
        parser.add_argument("file_path", nargs="?", help="File path (required for pin/unpin)")
        parser.add_argument("--reason", help="Reason for pinning")
        parser.add_argument("--workspace", help="Workspace context")

        args = parser.parse_args()

        manager = FileAutoCloseManager()

        if args.action == "pin":
            if not args.file_path:
                print("❌ Please provide file path")
                return 1

            success = manager.pin_file(args.file_path, args.reason or "Manual pin")
            if success:
                print(f"✅ Pinned file: {args.file_path}")
                if args.reason:
                    print(f"   Reason: {args.reason}")
            else:
                print(f"❌ Failed to pin file: {args.file_path}")

        elif args.action == "unpin":
            if not args.file_path:
                print("❌ Please provide file path")
                return 1

            success = manager.unpin_file(args.file_path)
            if success:
                print(f"✅ Unpinned file: {args.file_path}")
            else:
                print(f"❌ Failed to unpin file: {args.file_path}")

        elif args.action == "list":
            pinned_files = [fp for fp, session in manager.active_files.items() if session.is_pinned]

            if not pinned_files:
                print("📌 No pinned files")
            else:
                print(f"📌 Pinned Files ({len(pinned_files)}):")
                for file_path in pinned_files:
                    session = manager.active_files[file_path]
                    reason = f" - {session.pin_reason}" if session.pin_reason else ""
                    print(f"  • {Path(file_path).name}{reason}")
                    print(f"    {file_path}")

        elif args.action == "status":
            file_path = args.file_path
            if not file_path:
                # Show overall status
                status = manager.get_status_report()
                print("📊 File Pin Status")
                print(f"Active Files: {status['active_files']}")
                print(f"Pinned Files: {status['pinned_files']}")
                return 0

            # Show status for specific file
            if file_path in manager.active_files:
                session = manager.active_files[file_path]
                status = "📌 PINNED" if session.is_pinned else "📄 NOT PINNED"
                print(f"{status}: {file_path}")
                if session.pin_reason:
                    print(f"Reason: {session.pin_reason}")
            else:
                print(f"📄 File not in active tracking: {file_path}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()