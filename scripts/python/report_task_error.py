#!/usr/bin/env python3
"""
Report Task Error - Manual error reporting for VSCode tasks

This script allows manual reporting of task errors to the TaskErrorManager,
useful for testing or for tasks that can't use the wrapper.
"""

import argparse
import sys
from task_error_manager import TaskErrorManager
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def main():
    parser = argparse.ArgumentParser(description="Report Task Error")
    parser.add_argument("task_name", help="Name of the task that failed")
    parser.add_argument("error_message", help="Error message")
    parser.add_argument("--exit-code", type=int, help="Exit code")
    parser.add_argument("--command", help="Command that was executed")
    parser.add_argument("--quiet", action="store_true", help="Don't show notification output")

    args = parser.parse_args()

    manager = TaskErrorManager()

    # Report the error
    should_notify = manager.report_task_error(
        task_name=args.task_name,
        error_message=args.error_message,
        exit_code=args.exit_code,
        command=args.command
    )

    if not args.quiet:
        if should_notify:
            print(f"🔔 Notification shown for task '{args.task_name}'")
        else:
            print(f"🔇 Notification suppressed for task '{args.task_name}'")

        # Show suggested fix if available
        error_key = manager._generate_error_key(args.task_name, args.error_message)
        if error_key in manager.active_errors:
            error_record = manager.active_errors[error_key]
            if "suggested_fix" in error_record:
                print(f"💡 Suggested fix: {error_record['suggested_fix']}")

    # Exit with the original exit code to maintain task failure status
    sys.exit(args.exit_code or 1)


if __name__ == "__main__":





    main()