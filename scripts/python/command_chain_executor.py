#!/usr/bin/env python3
"""
Command Chain Executor

Supports command chaining with &&, ||, &, | operators for advanced command execution.
Allows combining multiple commands with logical operators and parallel execution.

Operators:
- && : Execute next command only if previous succeeded (AND)
- || : Execute next command only if previous failed (OR)
- &  : Execute command in background (parallel)
- |  : Pipe output from one command to next (pipe)

Examples:
- "cmd1 && cmd2" - Run cmd2 only if cmd1 succeeds
- "cmd1 || cmd2" - Run cmd2 only if cmd1 fails
- "cmd1 & cmd2" - Run cmd1 in background, then cmd2
- "cmd1 | cmd2" - Pipe cmd1 output to cmd2
"""

import sys
import subprocess
import shlex
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class ChainOperator(Enum):
    """Command chain operators"""
    AND = "&&"  # Execute if previous succeeded
    OR = "||"   # Execute if previous failed
    BACKGROUND = "&"  # Execute in background
    PIPE = "|"  # Pipe output


@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    success: bool
    return_code: int
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    background: bool = False
    pid: Optional[int] = None


@dataclass
class ChainCommand:
    """Single command in a chain"""
    command: str
    operator: Optional[ChainOperator] = None
    background: bool = False


class CommandChainExecutor:
    """
    Execute commands with chaining operators (&&, ||, &, |)

    Supports:
    - Sequential execution with conditions (&&, ||)
    - Background execution (&)
    - Piping (|)
    - Cross-platform (Windows PowerShell, Unix shell)
    """

    def __init__(self, project_root: Optional[Path] = None, shell: bool = True):
        """
        Initialize command chain executor

        Args:
            project_root: Project root directory
            shell: Use shell execution (default: True)
        """
        self.project_root = project_root or Path.cwd()
        self.shell = shell
        self.logger = get_logger("CommandChainExecutor")
        self.background_processes: Dict[str, subprocess.Popen] = {}
        self.background_results: Dict[str, CommandResult] = {}

    def parse_chain(self, command_chain: str) -> List[ChainCommand]:
        """
        Parse command chain into individual commands with operators

        Args:
            command_chain: Command string with operators (e.g., "cmd1 && cmd2 || cmd3")

        Returns:
            List of ChainCommand objects
        """
        commands = []
        parts = []
        current_command = []
        i = 0

        while i < len(command_chain):
            # Check for operators
            if command_chain[i:i+2] == "&&":
                if current_command:
                    parts.append(("".join(current_command).strip(), ChainOperator.AND))
                    current_command = []
                i += 2
            elif command_chain[i:i+2] == "||":
                if current_command:
                    parts.append(("".join(current_command).strip(), ChainOperator.OR))
                    current_command = []
                i += 2
            elif command_chain[i] == "|" and (i == 0 or command_chain[i-1] != "|"):
                # Single pipe (not ||)
                if current_command:
                    parts.append(("".join(current_command).strip(), ChainOperator.PIPE))
                    current_command = []
                i += 1
            elif command_chain[i] == "&" and (i == len(command_chain) - 1 or command_chain[i+1] != "&"):
                # Single & (not &&)
                if current_command:
                    parts.append(("".join(current_command).strip(), ChainOperator.BACKGROUND))
                    current_command = []
                i += 1
            else:
                current_command.append(command_chain[i])
                i += 1

        # Add final command
        if current_command:
            parts.append(("".join(current_command).strip(), None))

        # Convert to ChainCommand objects
        for i, (cmd, op) in enumerate(parts):
            commands.append(ChainCommand(
                command=cmd,
                operator=op,
                background=(op == ChainOperator.BACKGROUND)
            ))

        return commands

    def execute_command(
        self,
        command: str,
        cwd: Optional[Path] = None,
        timeout: Optional[int] = None,
        background: bool = False
    ) -> CommandResult:
        """
        Execute a single command

        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            background: Run in background

        Returns:
            CommandResult object
        """
        cwd = cwd or self.project_root
        start_time = time.time()

        try:
            if background:
                # Background execution
                process = subprocess.Popen(
                    command,
                    shell=self.shell,
                    cwd=str(cwd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                self.background_processes[command] = process

                return CommandResult(
                    command=command,
                    success=True,  # Assume success for background
                    return_code=0,
                    execution_time=time.time() - start_time,
                    background=True,
                    pid=process.pid
                )
            else:
                # Foreground execution
                result = subprocess.run(
                    command,
                    shell=self.shell,
                    cwd=str(cwd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout
                )

                return CommandResult(
                    command=command,
                    success=(result.returncode == 0),
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=time.time() - start_time
                )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                success=False,
                return_code=-1,
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return CommandResult(
                command=command,
                success=False,
                return_code=-1,
                stderr=str(e),
                execution_time=time.time() - start_time
            )

    def execute_chain(
        self,
        command_chain: str,
        cwd: Optional[Path] = None,
        timeout: Optional[int] = None
    ) -> List[CommandResult]:
        """
        Execute a chain of commands with operators

        Args:
            command_chain: Command chain string (e.g., "cmd1 && cmd2 || cmd3")
            cwd: Working directory
            timeout: Timeout per command

        Returns:
            List of CommandResult objects
        """
        cwd = cwd or self.project_root
        commands = self.parse_chain(command_chain)
        results = []
        previous_success = True
        pipe_input = None

        self.logger.info(f"Executing command chain: {command_chain}")

        for i, chain_cmd in enumerate(commands):
            cmd = chain_cmd.command.strip()

            # Skip if operator condition not met
            if chain_cmd.operator == ChainOperator.AND and not previous_success:
                self.logger.debug(f"Skipping '{cmd}' (AND condition not met)")
                results.append(CommandResult(
                    command=cmd,
                    success=False,
                    return_code=-1,
                    stderr="Skipped: previous command failed (&&)"
                ))
                continue

            if chain_cmd.operator == ChainOperator.OR and previous_success:
                self.logger.debug(f"Skipping '{cmd}' (OR condition not met)")
                results.append(CommandResult(
                    command=cmd,
                    success=False,
                    return_code=-1,
                    stderr="Skipped: previous command succeeded (||)"
                ))
                continue

            # Handle piping
            if chain_cmd.operator == ChainOperator.PIPE and pipe_input:
                # Combine commands with pipe
                if i > 0 and results:
                    prev_result = results[-1]
                    if prev_result.success:
                        cmd = f"{prev_result.command} | {cmd}"
                        pipe_input = prev_result.stdout
                    else:
                        self.logger.warning(f"Cannot pipe: previous command failed")
                        results.append(CommandResult(
                            command=cmd,
                            success=False,
                            return_code=-1,
                            stderr="Cannot pipe: previous command failed"
                        ))
                        continue

            # Execute command
            if chain_cmd.background:
                result = self.execute_command(cmd, cwd=cwd, timeout=timeout, background=True)
                self.logger.info(f"Started background command: {cmd} (PID: {result.pid})")
            else:
                result = self.execute_command(cmd, cwd=cwd, timeout=timeout, background=False)
                self.logger.info(f"Executed: {cmd} (return code: {result.return_code})")

            results.append(result)
            previous_success = result.success

            # Set pipe input for next command
            if chain_cmd.operator == ChainOperator.PIPE:
                pipe_input = result.stdout

        return results

    def wait_for_background(self, command: Optional[str] = None, timeout: Optional[int] = None) -> Optional[CommandResult]:
        """
        Wait for background command to complete

        Args:
            command: Specific command to wait for (None = wait for all)
            timeout: Timeout in seconds

        Returns:
            CommandResult or None
        """
        if command:
            if command in self.background_processes:
                process = self.background_processes[command]
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    result = CommandResult(
                        command=command,
                        success=(process.returncode == 0),
                        return_code=process.returncode,
                        stdout=stdout,
                        stderr=stderr,
                        background=True,
                        pid=process.pid
                    )
                    self.background_results[command] = result
                    del self.background_processes[command]
                    return result
                except subprocess.TimeoutExpired:
                    return None
        else:
            # Wait for all background processes
            for cmd, process in list(self.background_processes.items()):
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    result = CommandResult(
                        command=cmd,
                        success=(process.returncode == 0),
                        return_code=process.returncode,
                        stdout=stdout,
                        stderr=stderr,
                        background=True,
                        pid=process.pid
                    )
                    self.background_results[cmd] = result
                    del self.background_processes[cmd]
                except subprocess.TimeoutExpired:
                    pass

        return None

    def get_background_results(self) -> Dict[str, CommandResult]:
        """Get results from completed background commands"""
        # Check for completed processes
        for cmd, process in list(self.background_processes.items()):
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                result = CommandResult(
                    command=cmd,
                    success=(process.returncode == 0),
                    return_code=process.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    background=True,
                    pid=process.pid
                )
                self.background_results[cmd] = result
                del self.background_processes[cmd]

        return self.background_results.copy()


def main():
    """CLI interface for command chain executor"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Execute commands with chaining operators (&&, ||, &, |)"
    )
    parser.add_argument(
        "command",
        nargs="+",
        help="Command chain to execute (e.g., 'cmd1 && cmd2 || cmd3')"
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        help="Working directory"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout per command (seconds)"
    )
    parser.add_argument(
        "--wait-background",
        action="store_true",
        help="Wait for background commands to complete"
    )

    args = parser.parse_args()

    command_chain = " ".join(args.command)
    executor = CommandChainExecutor(project_root=args.cwd)
    results = executor.execute_chain(command_chain, cwd=args.cwd, timeout=args.timeout)

    # Print results
    print("\n" + "="*80)
    print("COMMAND CHAIN EXECUTION RESULTS")
    print("="*80)

    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result.command}")
        print(f"    Success: {result.success}")
        print(f"    Return Code: {result.return_code}")
        print(f"    Execution Time: {result.execution_time:.2f}s")
        if result.background:
            print(f"    Background: Yes (PID: {result.pid})")
        if result.stdout:
            print(f"    Stdout:\n{result.stdout}")
        if result.stderr:
            print(f"    Stderr:\n{result.stderr}")

    # Wait for background if requested
    if args.wait_background:
        print("\nWaiting for background commands...")
        executor.wait_for_background()
        bg_results = executor.get_background_results()
        if bg_results:
            print("\nBackground Command Results:")
            for cmd, result in bg_results.items():
                print(f"  {cmd}: {result.return_code}")

    # Overall success
    overall_success = all(r.success for r in results if not r.background)
    print(f"\n{'✅ All commands succeeded' if overall_success else '❌ Some commands failed'}")

    return 0 if overall_success else 1


if __name__ == "__main__":


    sys.exit(main())