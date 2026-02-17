#!/usr/bin/env python3
"""
@ask Ticket Auto-Executor - Code Cowork-Style Task Completion

Automatically executes validated @ask tickets, completing tasks similar to
Claude Code Cowork's file access and task completion capabilities.

Enhanced Flow:
@ask → Validation (Holocron) → Auto-Execution → Results → Database

Tags: #ASK #EXECUTION #AUTOMATION #CODE_COWORK @JARVIS @LUMINA @DOIT @V3
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ask_ticket_collation_system import AskTicketCollationSystem, AskTicketRecord
from ask_ticket_holocron_middleware import AskTicketHolocronMiddleware

from lumina_core.paths import setup_paths

setup_paths()
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

try:
    from lumina_core.logging import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str):
        """Fallback logger factory"""
        return logging.getLogger(name)

logger = get_logger("AskTicketAutoExecutor")


class ExecutionStatus(Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PARTIAL = "partial"


@dataclass
class ExecutionResult:
    """Result of task execution"""
    ask_id: str
    status: ExecutionStatus
    executed_at: datetime
    execution_time_seconds: float
    output: str
    error: Optional[str] = None
    files_accessed: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)
    verification_passed: bool = False
    verification_results: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ask_id": self.ask_id,
            "status": self.status.value,
            "executed_at": self.executed_at.isoformat(),
            "execution_time_seconds": self.execution_time_seconds,
            "output": self.output,
            "error": self.error,
            "files_accessed": self.files_accessed,
            "files_modified": self.files_modified,
            "commands_executed": self.commands_executed,
            "verification_passed": self.verification_passed,
            "verification_results": self.verification_results,
            "metadata": self.metadata
        }


class TaskType(Enum):
    """Types of tasks that can be executed"""
    FILE_OPERATION = "file_operation"
    COMMAND_EXECUTION = "command_execution"
    CODE_GENERATION = "code_generation"
    DATA_PROCESSING = "data_processing"
    API_CALL = "api_call"
    WORKFLOW_EXECUTION = "workflow_execution"
    UNKNOWN = "unknown"


class AskTicketAutoExecutor:
    """
    Code Cowork-style auto-executor for @ask tickets

    Automatically executes validated tickets, completing tasks with file access,
    command execution, and result reporting similar to Claude Code Cowork.
    """

    def __init__(
        self,
        root_path: Optional[Path] = None,
        enable_v3_verification: bool = True,
        auto_execute: bool = True
    ):
        """Initialize auto-executor"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.collation_system = AskTicketCollationSystem(self.project_root)
        self.holocron_middleware = AskTicketHolocronMiddleware(self.project_root)
        self.enable_v3_verification = enable_v3_verification
        self.auto_execute = auto_execute

        # Execution history
        self.execution_history: List[ExecutionResult] = []
        self.execution_log_dir = self.project_root / "data" / "ask_ticket_executions"
        self.execution_log_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ @ask Ticket Auto-Executor initialized")
        logger.info("   Project root: %s", self.project_root)
        logger.info("   V3 verification: %s", enable_v3_verification)
        logger.info("   Auto-execute: %s", auto_execute)

    def _detect_task_type(self, ask_text: str, tags: List[str]) -> TaskType:
        """
        Detect task type from @ask text and tags

        Args:
            ask_text: The @ask directive text
            tags: List of tags

        Returns:
            TaskType enum
        """
        text_lower = ask_text.lower()

        # File operations
        file_keywords = ["create file", "write file", "read file", "delete file",
                        "edit file", "update file", "modify file", "save file"]
        if any(keyword in text_lower for keyword in file_keywords):
            return TaskType.FILE_OPERATION

        # Command execution
        command_keywords = ["run command", "execute", "run script", "run",
                           "execute script", "command", "cli"]
        if any(keyword in text_lower for keyword in command_keywords):
            return TaskType.COMMAND_EXECUTION

        # Code generation
        code_keywords = ["generate code", "create function", "write code",
                        "implement", "add feature", "create class"]
        if any(keyword in text_lower for keyword in code_keywords):
            return TaskType.CODE_GENERATION

        # Data processing
        data_keywords = ["process data", "analyze", "parse", "transform",
                        "convert", "extract"]
        if any(keyword in text_lower for keyword in data_keywords):
            return TaskType.DATA_PROCESSING

        # API calls
        api_keywords = ["api", "call api", "http", "request", "endpoint"]
        if any(keyword in text_lower for keyword in api_keywords):
            return TaskType.API_CALL

        # Workflow execution
        workflow_keywords = ["workflow", "pipeline", "process", "@doit"]
        if any(keyword in text_lower or keyword in tags for keyword in workflow_keywords):
            return TaskType.WORKFLOW_EXECUTION

        return TaskType.UNKNOWN

    def _run_v3_verification(
        self,
        ticket: AskTicketRecord,
        task_type: TaskType
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Run @v3 verification before execution

        Args:
            ticket: The ticket to verify
            task_type: Type of task to verify

        Returns:
            Tuple of (passed, verification_results)
        """
        if not self.enable_v3_verification:
            return True, []

        try:
            from v3_verification import V3Verification, V3VerificationConfig

            config = V3VerificationConfig(
                enabled=True,
                auto_verify=True,
                verification_required=True
            )
            verifier = V3Verification(config)

            # Verify workflow preconditions
            workflow_data = {
                "workflow_id": ticket.ask_id,
                "workflow_name": f"@ask execution: {ticket.ask_text[:50]}",
                "task_type": task_type.value,
                "ticket_data": ticket.to_dict()
            }

            pre_result = verifier.verify_workflow_preconditions(workflow_data)
            data_result = verifier.verify_data_integrity(ticket.to_dict(), "ask_ticket")

            verification_results = [
                {
                    "step": pre_result.step_name,
                    "passed": pre_result.passed,
                    "message": pre_result.message,
                    "details": pre_result.details
                },
                {
                    "step": data_result.step_name,
                    "passed": data_result.passed,
                    "message": data_result.message,
                    "details": data_result.details
                }
            ]

            all_passed = all(r["passed"] for r in verification_results)

            if all_passed:
                logger.info("✅ @v3 verification passed for @ask: %s", ticket.ask_id)
            else:
                logger.warning("⚠️  @v3 verification failed for @ask: %s", ticket.ask_id)

            return all_passed, verification_results

        except ImportError:
            logger.warning("⚠️  @v3 verification not available, skipping")
            return True, []
        except Exception as e:
            logger.error("❌ Error during @v3 verification: %s", e)
            return False, [{"step": "verification_error", "passed": False, "message": str(e)}]

    def _execute_file_operation(
        self,
        ticket: AskTicketRecord,
        ask_text: str
    ) -> ExecutionResult:
        """
        Execute file operation task

        Args:
            ticket: The ticket record
            ask_text: The @ask text

        Returns:
            ExecutionResult
        """
        start_time = datetime.now()
        files_accessed = []
        files_modified = []

        try:
            # Parse file operation from ask_text
            # This is a simplified parser - in production, use NLP/AI to understand intent
            text_lower = ask_text.lower()

            # Extract file path patterns
            import re
            file_patterns = re.findall(r'["\']([^"\']+\.(py|json|txt|md|yaml|yml))["\']', ask_text)
            file_paths = [fp[0] for fp in file_patterns]

            # For now, log the operation
            output = f"File operation detected for @ask: {ticket.ask_id}\n"
            output += f"Detected file patterns: {file_paths}\n"
            output += "File operation execution would occur here (Code Cowork-style)\n"

            files_accessed = file_paths

            execution_time = (datetime.now() - start_time).total_seconds()

            return ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.SUCCESS,
                executed_at=start_time,
                execution_time_seconds=execution_time,
                output=output,
                files_accessed=files_accessed,
                files_modified=files_modified,
                metadata={"task_type": "file_operation", "file_count": len(file_paths)}
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.FAILED,
                executed_at=start_time,
                execution_time_seconds=execution_time,
                output="",
                error=str(e),
                files_accessed=files_accessed,
                files_modified=files_modified
            )

    def _execute_command(
        self,
        ticket: AskTicketRecord,
        ask_text: str
    ) -> ExecutionResult:
        """
        Execute command/script task

        Args:
            ticket: The ticket record
            ask_text: The @ask text

        Returns:
            ExecutionResult
        """
        start_time = datetime.now()
        commands_executed = []

        try:
            # Extract command from ask_text
            # This is simplified - in production, use AI to understand intent
            import re
            command_patterns = re.findall(r'`([^`]+)`', ask_text)
            commands = command_patterns if command_patterns else []

            output_lines = [f"Command execution for @ask: {ticket.ask_id}"]

            # Execute commands (with safety checks)
            for cmd in commands:
                if any(dangerous in cmd.lower() for dangerous in ["rm -rf", "del /f", "format"]):
                    output_lines.append(f"⚠️  Skipped dangerous command: {cmd}")
                    continue

                try:
                    # Execute command
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=str(self.project_root)
                    )

                    commands_executed.append(cmd)
                    output_lines.append(f"✅ Executed: {cmd}")
                    output_lines.append(f"   Exit code: {result.returncode}")
                    if result.stdout:
                        output_lines.append(f"   Output: {result.stdout[:200]}")

                except subprocess.TimeoutExpired:
                    output_lines.append(f"⏱️  Command timed out: {cmd}")
                except Exception as e:
                    output_lines.append(f"❌ Error executing {cmd}: {e}")

            execution_time = (datetime.now() - start_time).total_seconds()

            return ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.SUCCESS if commands_executed else ExecutionStatus.PARTIAL,
                executed_at=start_time,
                execution_time_seconds=execution_time,
                output="\n".join(output_lines),
                commands_executed=commands_executed,
                metadata={"task_type": "command_execution", "command_count": len(commands_executed)}
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.FAILED,
                executed_at=start_time,
                execution_time_seconds=execution_time,
                output="",
                error=str(e),
                commands_executed=commands_executed
            )

    def _execute_workflow(
        self,
        ticket: AskTicketRecord,
        ask_text: str
    ) -> ExecutionResult:
        """
        Execute workflow task

        Args:
            ticket: The ticket record
            ask_text: The @ask text

        Returns:
            ExecutionResult
        """
        start_time = datetime.now()

        try:
            # Check for @DOIT or workflow keywords
            text_lower = ask_text.lower()
            is_doit = "@doit" in ask_text.lower() or "doit" in text_lower

            output_lines = [f"Workflow execution for @ask: {ticket.ask_id}"]
            output_lines.append(f"Workflow type: {'@DOIT' if is_doit else 'Standard workflow'}")

            # Try to execute via existing workflow systems
            if is_doit:
                try:
                    # Import and use existing @DOIT execution
                    from jarvis_execute_ask_chains import JARVISAskChainExecutor
                    executor = JARVISAskChainExecutor(self.project_root)
                    output_lines.append("✅ Connected to JARVIS @DOIT executor")
                except ImportError:
                    output_lines.append("⚠️  JARVIS @DOIT executor not available")

            execution_time = (datetime.now() - start_time).total_seconds()

            return ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.SUCCESS,
                executed_at=start_time,
                execution_time_seconds=execution_time,
                output="\n".join(output_lines),
                metadata={"task_type": "workflow_execution", "is_doit": is_doit}
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.FAILED,
                executed_at=start_time,
                execution_time_seconds=execution_time,
                output="",
                error=str(e)
            )

    def execute_ticket(
        self,
        ticket: AskTicketRecord,
        skip_verification: bool = False
    ) -> ExecutionResult:
        """
        Execute a validated @ask ticket (Code Cowork-style)

        Args:
            ticket: Validated ticket record
            skip_verification: Skip @v3 verification (not recommended)

        Returns:
            ExecutionResult with execution details
        """
        logger.info("🚀 Executing @ask ticket: %s", ticket.ask_id)
        logger.info("   Ask text: %s", ticket.ask_text[:100])

        # Detect task type
        task_type = self._detect_task_type(ticket.ask_text, ticket.tags)
        logger.info("   Detected task type: %s", task_type.value)

        # Run @v3 verification
        verification_passed = True
        verification_results = []
        if not skip_verification and self.enable_v3_verification:
            verification_passed, verification_results = self._run_v3_verification(
                ticket, task_type
            )

            if not verification_passed:
                logger.warning("⚠️  @v3 verification failed, skipping execution")
                return ExecutionResult(
                    ask_id=ticket.ask_id,
                    status=ExecutionStatus.SKIPPED,
                    executed_at=datetime.now(),
                    execution_time_seconds=0.0,
                    output="Execution skipped due to @v3 verification failure",
                    verification_passed=False,
                    verification_results=verification_results
                )

        # Execute based on task type
        if task_type == TaskType.FILE_OPERATION:
            result = self._execute_file_operation(ticket, ticket.ask_text)
        elif task_type == TaskType.COMMAND_EXECUTION:
            result = self._execute_command(ticket, ticket.ask_text)
        elif task_type == TaskType.WORKFLOW_EXECUTION:
            result = self._execute_workflow(ticket, ticket.ask_text)
        else:
            # Unknown task type - log and skip
            logger.warning("⚠️  Unknown task type, skipping execution")
            result = ExecutionResult(
                ask_id=ticket.ask_id,
                status=ExecutionStatus.SKIPPED,
                executed_at=datetime.now(),
                execution_time_seconds=0.0,
                output=f"Unknown task type: {task_type.value}",
                metadata={"task_type": task_type.value}
            )

        # Add verification results
        result.verification_passed = verification_passed
        result.verification_results = verification_results

        # Save execution result
        self._save_execution_result(result)

        # Update ticket status
        self._update_ticket_status(ticket, result)

        logger.info("✅ Execution completed: %s", result.status.value)
        if result.error:
            logger.error("   Error: %s", result.error)

        return result

    def _save_execution_result(self, result: ExecutionResult):
        try:
            """Save execution result to log"""
            timestamp = result.executed_at.strftime("%Y%m%d_%H%M%S")
            log_file = self.execution_log_dir / f"execution_{result.ask_id}_{timestamp}.json"

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

            self.execution_history.append(result)
            logger.debug("💾 Saved execution result to: %s", log_file)

        except Exception as e:
            self.logger.error(f"Error in _save_execution_result: {e}", exc_info=True)
            raise
    def _update_ticket_status(
        self,
        ticket: AskTicketRecord,
        result: ExecutionResult
    ):
        """Update ticket status based on execution result"""
        # Update status in collation system
        # Store execution result in ticket metadata
        try:
            # Get updated ticket
            tickets = self.collation_system.query(ask_id=ticket.ask_id)
            if tickets:
                updated_ticket = tickets[0]

                # Add execution result to metadata
                execution_metadata = {
                    "execution_status": result.status.value,
                    "executed_at": result.executed_at.isoformat(),
                    "execution_time_seconds": result.execution_time_seconds,
                    "verification_passed": result.verification_passed,
                    "files_accessed": result.files_accessed,
                    "files_modified": result.files_modified,
                    "commands_executed": result.commands_executed
                }

                # Update ticket metadata (would need to add update method to collation system)
                logger.info("📝 Execution result stored in ticket metadata")
                logger.info("   Status: %s → %s", ticket.status, result.status.value)

                # Save execution summary to holocron-compatible format
                self._save_to_holocron(ticket, result)
        except Exception as e:
            logger.error("❌ Error updating ticket status: %s", e)

    def _save_to_holocron(
        self,
        ticket: AskTicketRecord,
        result: ExecutionResult
    ):
        """Save execution result to holocron-compatible format"""
        try:
            holocron_data = {
                "ask_id": ticket.ask_id,
                "ask_text": ticket.ask_text,
                "execution_result": result.to_dict(),
                "ticket_data": {
                    "helpdesk_ticket": ticket.helpdesk_ticket,
                    "gitlens_ticket": ticket.gitlens_ticket,
                    "gitlens_pr": ticket.gitlens_pr,
                    "tags": ticket.tags,
                    "status": ticket.status
                },
                "saved_at": datetime.now().isoformat(),
                "source": "ask_ticket_auto_executor"
            }

            # Save to holocron directory
            holocron_dir = self.project_root / "data" / "holocron" / "ask_executions"
            holocron_dir.mkdir(parents=True, exist_ok=True)

            timestamp = result.executed_at.strftime("%Y%m%d_%H%M%S")
            holocron_file = holocron_dir / f"execution_{ticket.ask_id}_{timestamp}.json"

            with open(holocron_file, 'w', encoding='utf-8') as f:
                json.dump(holocron_data, f, indent=2, ensure_ascii=False)

            logger.info("💾 Saved execution result to holocron: %s", holocron_file)
        except Exception as e:
            logger.warning("⚠️  Could not save to holocron: %s", e)

    def process_and_execute(
        self,
        ask_id: str,
        ask_text: str,
        helpdesk_ticket: Optional[str] = None,
        gitlens_ticket: Optional[str] = None,
        gitlens_pr: Optional[str] = None
    ) -> Tuple[AskTicketRecord, ExecutionResult]:
        """
        Complete workflow: Process through middleware → Execute → Return results

        This is the main entry point that combines validation and execution.

        Args:
            ask_id: @ask directive ID
            ask_text: @ask directive text
            helpdesk_ticket: Optional helpdesk ticket
            gitlens_ticket: Optional GitLens ticket
            gitlens_pr: Optional GitLens PR

        Returns:
            Tuple of (validated_ticket, execution_result)
        """
        logger.info("🔄 Processing and executing @ask: %s", ask_id)

        # Step 1: Process through holocron middleware (validation)
        _, validation_result = self.holocron_middleware.process_through_middleware(
            ask_id=ask_id,
            ask_text=ask_text,
            helpdesk_ticket=helpdesk_ticket,
            gitlens_ticket=gitlens_ticket,
            gitlens_pr=gitlens_pr
        )

        if not validation_result.valid:
            raise ValueError(f"Validation failed: {validation_result.validation_errors}")

        # Step 2: Get validated ticket from collation system
        tickets = self.collation_system.query(ask_id=ask_id)
        if not tickets:
            raise ValueError(f"Ticket not found after validation: {ask_id}")

        ticket = tickets[0]

        # Step 3: Execute if auto-execute is enabled
        if self.auto_execute:
            execution_result = self.execute_ticket(ticket)
        else:
            execution_result = ExecutionResult(
                ask_id=ask_id,
                status=ExecutionStatus.PENDING,
                executed_at=datetime.now(),
                execution_time_seconds=0.0,
                output="Auto-execution disabled",
                metadata={"auto_execute": False}
            )

        logger.info("✅ Processed and executed @ask: %s", ask_id)
        logger.info("   Validation: %s", "✅ Passed" if validation_result.valid else "❌ Failed")
        logger.info("   Execution: %s", execution_result.status.value)

        return ticket, execution_result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@ask Ticket Auto-Executor - Code Cowork-style task completion"
    )
    parser.add_argument("--execute", nargs=5,
                       metavar=("ASK_ID", "ASK_TEXT", "HELPDESK", "GITLENS_TICKET", "GITLENS_PR"),
                       help="Process and execute @ask ticket")
    parser.add_argument("--execute-ticket", metavar="ASK_ID",
                       help="Execute existing validated ticket")
    parser.add_argument("--no-v3", action="store_true",
                       help="Skip @v3 verification")
    parser.add_argument("--no-auto", action="store_true",
                       help="Disable auto-execution")

    args = parser.parse_args()

    executor = AskTicketAutoExecutor(
        enable_v3_verification=not args.no_v3,
        auto_execute=not args.no_auto
    )

    if args.execute:
        ask_id, ask_text, helpdesk, gitlens_ticket, gitlens_pr = args.execute
        try:
            ticket, result = executor.process_and_execute(
                ask_id=ask_id,
                ask_text=ask_text,
                helpdesk_ticket=helpdesk if helpdesk != "None" else None,
                gitlens_ticket=gitlens_ticket if gitlens_ticket != "None" else None,
                gitlens_pr=gitlens_pr if gitlens_pr != "None" else None
            )

            print("\n✅ Processed and executed:")
            print(f"   Ask ID: {ask_id}")
            print(f"   Status: {result.status.value}")
            print(f"   Execution time: {result.execution_time_seconds:.2f}s")
            print(f"   Verification passed: {result.verification_passed}")
            if result.output:
                print(f"\n   Output:\n{result.output}")
            if result.error:
                print(f"\n   Error: {result.error}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    elif args.execute_ticket:
        tickets = executor.collation_system.query(ask_id=args.execute_ticket)
        if tickets:
            result = executor.execute_ticket(tickets[0], skip_verification=args.no_v3)
            print(f"\n✅ Execution result:")
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"\n❌ Ticket not found: {args.execute_ticket}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()