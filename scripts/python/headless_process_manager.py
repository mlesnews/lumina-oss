#!/usr/bin/env python3
"""
Headless Process Manager

Manages all processes as background daemons with full logging and JARVIS workflow tracking.

Features:
- Headless/daemon process execution (no visible terminals)
- Full logging module integration
- JARVIS workflow tracking, tracing, and hooking
- Comprehensive workflow/subworkflow monitoring
- Process lifecycle management

Tags: #HEADLESS #DAEMON #LOGGING #JARVIS #WORKFLOW_TRACKING @JARVIS @LUMINA
"""

import sys
import os
import time
import subprocess
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("HeadlessProcessManager")

# JARVIS Integration
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None


class WorkflowEventType(Enum):
    """Workflow event types"""
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"
    SUBWORKFLOW_START = "subworkflow_start"
    SUBWORKFLOW_END = "subworkflow_end"
    PROCESS_START = "process_start"
    PROCESS_END = "process_end"
    PROCESS_ERROR = "process_error"
    HOOK_TRIGGERED = "hook_triggered"


@dataclass
class WorkflowEvent:
    """Workflow event for JARVIS tracking"""
    event_type: WorkflowEventType
    workflow_id: str
    subworkflow_id: Optional[str] = None
    process_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"
    error: Optional[str] = None


class HeadlessProcessManager:
    """
    Headless Process Manager

    Manages all processes as background daemons with:
    - No visible terminals
    - Full logging integration
    - JARVIS workflow tracking
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.processes: Dict[str, subprocess.Popen] = {}
        self.workflow_events: List[WorkflowEvent] = []

        # Setup logging
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        setup_logging()

        # JARVIS Integration
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root)
                logger.info("✅ JARVIS integrated for workflow tracking")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS not available: {e}")

        logger.info("✅ Headless Process Manager initialized")

    def _get_log_file(self, process_name: str) -> Path:
        """Get log file path for a process"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return self.log_dir / f"{process_name}_{timestamp}.log"

    def _log_to_jarvis(self, event: WorkflowEvent):
        """Log workflow event to JARVIS"""
        if not self.jarvis:
            return

        try:
            event_data = {
                "event_type": event.event_type.value,
                "workflow_id": event.workflow_id,
                "subworkflow_id": event.subworkflow_id,
                "process_id": event.process_id,
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.metadata,
                "status": event.status,
                "error": event.error
            }

            # Log to JARVIS
            if hasattr(self.jarvis, 'log_workflow_event'):
                self.jarvis.log_workflow_event(event_data)
            else:
                # Fallback: log to JARVIS memory
                if hasattr(self.jarvis, 'memory'):
                    self.jarvis.memory.store(
                        f"workflow_{event.workflow_id}",
                        event_data,
                        memory_type="episodic"
                    )

            logger.debug(f"📊 JARVIS: Logged {event.event_type.value} for {event.workflow_id}")
        except Exception as e:
            logger.warning(f"⚠️  Error logging to JARVIS: {e}")

    def start_headless_process(
        self,
        name: str,
        script_path: Path,
        args: List[str] = None,
        workflow_id: str = None,
        subworkflow_id: str = None,
        env: Dict[str, str] = None
    ) -> subprocess.Popen:
        """
        Start a process in headless/daemon mode with full logging

        Args:
            name: Process name
            script_path: Path to script
            args: Additional arguments
            workflow_id: Workflow ID for tracking
            subworkflow_id: Subworkflow ID for tracking
            env: Environment variables
        """
        if args is None:
            args = []

        if workflow_id is None:
            workflow_id = f"workflow_{name}_{int(time.time())}"

        # Log file
        log_file = self._get_log_file(name)

        # Environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        # Add logging environment variables
        process_env["LUMINA_LOG_DIR"] = str(self.log_dir)
        process_env["LUMINA_WORKFLOW_ID"] = workflow_id
        if subworkflow_id:
            process_env["LUMINA_SUBWORKFLOW_ID"] = subworkflow_id

        logger.info(f"🚀 Starting headless process: {name}")
        logger.info(f"   Script: {script_path.name}")
        logger.info(f"   Workflow ID: {workflow_id}")
        logger.info(f"   Log file: {log_file.name}")

        # Create workflow event
        event = WorkflowEvent(
            event_type=WorkflowEventType.PROCESS_START,
            workflow_id=workflow_id,
            subworkflow_id=subworkflow_id,
            metadata={
                "process_name": name,
                "script_path": str(script_path),
                "args": args,
                "log_file": str(log_file)
            }
        )
        self.workflow_events.append(event)
        self._log_to_jarvis(event)

        try:
            # Start process in headless mode
            # On Windows: Use DETACHED_PROCESS and CREATE_NO_WINDOW
            # On Unix: Use daemon mode
            creation_flags = 0
            if sys.platform == 'win32':
                # DETACHED_PROCESS = 0x00000008
                # CREATE_NO_WINDOW = 0x08000000
                creation_flags = 0x08000008  # Both flags combined

            with open(log_file, 'a') as log_handle:
                proc = subprocess.Popen(
                    [sys.executable, str(script_path)] + args,
                    cwd=str(self.project_root),
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,  # Merge stderr to stdout
                    env=process_env,
                    creationflags=creation_flags if sys.platform == 'win32' else 0,
                    start_new_session=True if sys.platform != 'win32' else False
                )

            self.processes[name] = proc

            logger.info(f"✅ Started {name} (PID: {proc.pid})")
            logger.info(f"   Logging to: {log_file}")

            # Update event with PID
            event.process_id = proc.pid
            event.metadata["pid"] = proc.pid
            self._log_to_jarvis(event)

            return proc

        except Exception as e:
            logger.error(f"❌ Error starting {name}: {e}", exc_info=True)

            # Log error event
            error_event = WorkflowEvent(
                event_type=WorkflowEventType.PROCESS_ERROR,
                workflow_id=workflow_id,
                subworkflow_id=subworkflow_id,
                status="error",
                error=str(e),
                metadata={"process_name": name}
            )
            self.workflow_events.append(error_event)
            self._log_to_jarvis(error_event)

            raise

    def stop_process(self, name: str, workflow_id: str = None):
        """Stop a process"""
        if name not in self.processes:
            logger.warning(f"⚠️  Process {name} not found")
            return

        proc = self.processes[name]

        logger.info(f"🛑 Stopping {name} (PID: {proc.pid})")

        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)

            # Log end event
            if workflow_id:
                event = WorkflowEvent(
                    event_type=WorkflowEventType.PROCESS_END,
                    workflow_id=workflow_id,
                    process_id=proc.pid,
                    metadata={"process_name": name}
                )
                self.workflow_events.append(event)
                self._log_to_jarvis(event)

            del self.processes[name]
            logger.info(f"✅ Stopped {name}")

        except Exception as e:
            logger.error(f"❌ Error stopping {name}: {e}", exc_info=True)

    def hook_workflow(self, workflow_id: str, hook_type: str, callback: Callable):
        """Hook into a workflow for tracking/tracing"""
        logger.info(f"🔗 Hooking {hook_type} for workflow: {workflow_id}")

        event = WorkflowEvent(
            event_type=WorkflowEventType.HOOK_TRIGGERED,
            workflow_id=workflow_id,
            metadata={"hook_type": hook_type}
        )
        self.workflow_events.append(event)
        self._log_to_jarvis(event)

        # Store hook for later execution
        # This would integrate with workflow execution system
        return callback

    def get_workflow_trace(self, workflow_id: str) -> List[WorkflowEvent]:
        """Get trace of all events for a workflow"""
        return [
            event for event in self.workflow_events
            if event.workflow_id == workflow_id
        ]

    def get_all_workflows(self) -> Dict[str, List[WorkflowEvent]]:
        """Get all workflows and their events"""
        workflows = {}
        for event in self.workflow_events:
            if event.workflow_id not in workflows:
                workflows[event.workflow_id] = []
            workflows[event.workflow_id].append(event)
        return workflows


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Headless Process Manager")
    parser.add_argument("--start", type=str, help="Start a process")
    parser.add_argument("--script", type=str, help="Script path")
    parser.add_argument("--args", nargs="*", help="Script arguments")
    parser.add_argument("--workflow-id", type=str, help="Workflow ID")
    parser.add_argument("--stop", type=str, help="Stop a process")
    parser.add_argument("--list", action="store_true", help="List running processes")
    parser.add_argument("--trace", type=str, help="Get workflow trace")

    args = parser.parse_args()

    manager = HeadlessProcessManager(project_root)

    if args.start:
        script_path = project_root / args.script if args.script else project_root / "scripts" / "python" / f"{args.start}.py"
        manager.start_headless_process(
            args.start,
            script_path,
            args.args or [],
            args.workflow_id
        )
    elif args.stop:
        manager.stop_process(args.stop)
    elif args.list:
        print("\nRunning Processes:")
        print("=" * 80)
        for name, proc in manager.processes.items():
            print(f"  {name}: PID {proc.pid}")
        print("=" * 80)
    elif args.trace:
        trace = manager.get_workflow_trace(args.trace)
        print(f"\nWorkflow Trace: {args.trace}")
        print("=" * 80)
        for event in trace:
            print(f"  {event.timestamp} | {event.event_type.value} | {event.status}")
        print("=" * 80)
    else:
        parser.print_help()


if __name__ == "__main__":


    main()