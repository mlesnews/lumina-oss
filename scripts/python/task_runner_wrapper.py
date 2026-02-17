#!/usr/bin/env python3
"""
Task Runner Wrapper - Integrates VSCode tasks with error management

This script wraps task execution to provide intelligent error handling
and notification management through the TaskErrorManager.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def run_task_with_error_management(task_name: str, command: list, cwd: str = None):
    """
    Run a task with error management integration

    Args:
        task_name: Name of the task for error reporting
        command: Command to execute as list
        cwd: Working directory (optional)
    """
    from task_error_manager import TaskErrorManager

    error_manager = TaskErrorManager()

    try:
        print(f"🚀 Running task: {task_name}")
        start_time = time.time()

        # Run the command
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        execution_time = time.time() - start_time

        if result.returncode != 0:
            # Task failed - report to error manager
            error_message = result.stderr.strip() or result.stdout.strip() or "Unknown error"

            # Report the error
            should_notify = error_manager.report_task_error(
                task_name=task_name,
                error_message=error_message,
                exit_code=result.returncode,
                command=" ".join(command)
            )

            if should_notify:
                # Show notification with suggested fix if available
                print(f"❌ Task '{task_name}' failed (exit code: {result.returncode})")
                print(f"Error: {error_message[:200]}...")

                # Check for suggested fix
                error_key = error_manager._generate_error_key(task_name, error_message)
                if error_key in error_manager.active_errors:
                    error_record = error_manager.active_errors[error_key]
                    if "suggested_fix" in error_record:
                        print(f"💡 Suggested fix: {error_record['suggested_fix']}")
            else:
                print(f"🔇 Task '{task_name}' failed but notification suppressed")

            # Still exit with error code for VSCode task system
            sys.exit(result.returncode)

        else:
            print(f"✅ Task '{task_name}' completed successfully in {execution_time:.1f}s")
            sys.exit(0)

    except subprocess.TimeoutExpired:
        error_message = f"Task '{task_name}' timed out after 5 minutes"
        error_manager.report_task_error(
            task_name=task_name,
            error_message=error_message,
            command=" ".join(command)
        )
        print(f"⏰ {error_message}")
        sys.exit(124)  # Timeout exit code

    except Exception as e:
        error_message = f"Task wrapper error: {str(e)}"
        error_manager.report_task_error(
            task_name=task_name,
            error_message=error_message,
            command=" ".join(command)
        )
        print(f"💥 Task wrapper failed: {error_message}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Task Runner Wrapper")
    parser.add_argument("task_name", help="Name of the task")
    parser.add_argument("command", nargs="+", help="Command to execute")
    parser.add_argument("--cwd", help="Working directory")

    args = parser.parse_args()

    run_task_with_error_management(
        task_name=args.task_name,
        command=args.command,
        cwd=args.cwd
    )


if __name__ == "__main__":





    main()