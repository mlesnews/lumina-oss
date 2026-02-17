#!/usr/bin/env python3
"""
JARVIS Workflow Tracker

Comprehensive workflow tracking, tracing, and hooking system for JARVIS.
Tracks all workflows and subworkflows with full integration.

Tags: #JARVIS #WORKFLOW_TRACKING #TRACING #HOOKING @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWorkflowTracker")

# JARVIS Integration
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None


class WorkflowStatus(Enum):
    """Workflow status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HookType(Enum):
    """Hook types"""
    PRE_WORKFLOW = "pre_workflow"
    POST_WORKFLOW = "post_workflow"
    PRE_SUBWORKFLOW = "pre_subworkflow"
    POST_SUBWORKFLOW = "post_subworkflow"
    ON_ERROR = "on_error"
    ON_COMPLETE = "on_complete"


@dataclass
class WorkflowTrace:
    """Workflow trace entry"""
    timestamp: datetime
    event_type: str
    workflow_id: str
    subworkflow_id: Optional[str] = None
    process_id: Optional[int] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowHook:
    """Workflow hook"""
    hook_id: str
    hook_type: HookType
    workflow_id: Optional[str] = None
    callback: Optional[Callable] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Workflow definition"""
    workflow_id: str
    name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    subworkflows: List[str] = field(default_factory=list)
    processes: List[int] = field(default_factory=list)
    traces: List[WorkflowTrace] = field(default_factory=list)
    hooks: List[WorkflowHook] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class JARVISWorkflowTracker:
    """
    JARVIS Workflow Tracker

    Tracks, traces, and hooks all workflows and subworkflows with JARVIS integration.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows: Dict[str, Workflow] = {}
        self.hooks: Dict[str, WorkflowHook] = {}
        self.trace_file = project_root / "data" / "jarvis_workflow_traces.json"
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)

        # JARVIS Integration
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root)
                logger.info("✅ JARVIS integrated for workflow tracking")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS not available: {e}")

        # Load existing traces
        self._load_traces()

        logger.info("✅ JARVIS Workflow Tracker initialized")

    def _load_traces(self):
        """Load existing workflow traces"""
        if self.trace_file.exists():
            try:
                with open(self.trace_file, 'r') as f:
                    data = json.load(f)
                    for workflow_data in data.get("workflows", []):
                        # Convert status string to enum if needed
                        if isinstance(workflow_data.get("status"), str):
                            try:
                                workflow_data["status"] = WorkflowStatus(workflow_data["status"])
                            except (ValueError, KeyError):
                                workflow_data["status"] = WorkflowStatus.PENDING

                        workflow = Workflow(**workflow_data)
                        # Convert trace dicts back to WorkflowTrace objects
                        workflow.traces = [
                            WorkflowTrace(**trace) if isinstance(trace, dict) else trace
                            for trace in workflow.traces
                        ]
                        self.workflows[workflow.workflow_id] = workflow
                logger.info(f"✅ Loaded {len(self.workflows)} workflows from traces")
            except Exception as e:
                logger.warning(f"⚠️  Error loading traces: {e}")

    def _save_traces(self):
        """Save workflow traces to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "workflows": [
                    {
                        "workflow_id": w.workflow_id,
                        "name": w.name,
                        "status": w.status.value if hasattr(w.status, 'value') else str(w.status),
                        "start_time": w.start_time.isoformat() if w.start_time else None,
                        "end_time": w.end_time.isoformat() if w.end_time else None,
                        "subworkflows": w.subworkflows,
                        "processes": w.processes,
                        "traces": [
                            {
                                "timestamp": t.timestamp.isoformat() if isinstance(t.timestamp, datetime) else str(t.timestamp),
                                "event_type": t.event_type,
                                "workflow_id": t.workflow_id,
                                "subworkflow_id": t.subworkflow_id,
                                "process_id": t.process_id,
                                "message": t.message,
                                "metadata": t.metadata
                            }
                            for t in w.traces
                        ],
                        "metadata": w.metadata,
                        "error": w.error
                    }
                    for w in self.workflows.values()
                ]
            }
            with open(self.trace_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving traces: {e}")

    def _log_to_jarvis(self, workflow: Workflow, trace: WorkflowTrace):
        """Log workflow trace to JARVIS"""
        if not self.jarvis:
            return

        try:
            trace_data = {
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.name,
                "status": workflow.status.value,
                "trace": {
                    "timestamp": trace.timestamp.isoformat(),
                    "event_type": trace.event_type,
                    "subworkflow_id": trace.subworkflow_id,
                    "process_id": trace.process_id,
                    "message": trace.message,
                    "metadata": trace.metadata
                }
            }

            # Log to JARVIS memory
            if hasattr(self.jarvis, 'memory'):
                self.jarvis.memory.store(
                    f"workflow_trace_{workflow.workflow_id}_{int(trace.timestamp.timestamp())}",
                    trace_data,
                    memory_type="episodic"
                )

            logger.debug(f"📊 JARVIS: Logged {trace.event_type} for {workflow.workflow_id}")
        except Exception as e:
            logger.warning(f"⚠️  Error logging to JARVIS: {e}")

    def start_workflow(self, workflow_id: str, name: str, metadata: Dict[str, Any] = None) -> Workflow:
        """Start tracking a workflow"""
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now(),
            metadata=metadata or {}
        )

        self.workflows[workflow_id] = workflow

        # Add trace
        trace = WorkflowTrace(
            timestamp=datetime.now(),
            event_type="workflow_start",
            workflow_id=workflow_id,
            message=f"Workflow '{name}' started"
        )
        workflow.traces.append(trace)
        self._log_to_jarvis(workflow, trace)

        # Execute pre-workflow hooks
        self._execute_hooks(HookType.PRE_WORKFLOW, workflow_id)

        self._save_traces()
        logger.info(f"📊 Started tracking workflow: {workflow_id} ({name})")

        return workflow

    def end_workflow(self, workflow_id: str, status: WorkflowStatus = WorkflowStatus.COMPLETED, error: Optional[str] = None):
        """End tracking a workflow"""
        if workflow_id not in self.workflows:
            logger.warning(f"⚠️  Workflow {workflow_id} not found")
            return

        workflow = self.workflows[workflow_id]
        workflow.status = status
        workflow.end_time = datetime.now()
        workflow.error = error

        # Add trace
        trace = WorkflowTrace(
            timestamp=datetime.now(),
            event_type="workflow_end",
            workflow_id=workflow_id,
            message=f"Workflow '{workflow.name}' {status.value}",
            metadata={"error": error} if error else {}
        )
        workflow.traces.append(trace)
        self._log_to_jarvis(workflow, trace)

        # Execute post-workflow hooks
        self._execute_hooks(HookType.POST_WORKFLOW, workflow_id)

        self._save_traces()
        logger.info(f"📊 Ended tracking workflow: {workflow_id} ({status.value})")

    def add_subworkflow(self, workflow_id: str, subworkflow_id: str, name: str):
        """Add a subworkflow to a workflow"""
        if workflow_id not in self.workflows:
            logger.warning(f"⚠️  Workflow {workflow_id} not found")
            return

        workflow = self.workflows[workflow_id]
        workflow.subworkflows.append(subworkflow_id)

        # Add trace
        trace = WorkflowTrace(
            timestamp=datetime.now(),
            event_type="subworkflow_start",
            workflow_id=workflow_id,
            subworkflow_id=subworkflow_id,
            message=f"Subworkflow '{name}' started"
        )
        workflow.traces.append(trace)
        self._log_to_jarvis(workflow, trace)

        # Execute pre-subworkflow hooks
        self._execute_hooks(HookType.PRE_SUBWORKFLOW, workflow_id, subworkflow_id)

        self._save_traces()

    def add_process(self, workflow_id: str, process_id: int, process_name: str):
        """Add a process to a workflow"""
        if workflow_id not in self.workflows:
            logger.warning(f"⚠️  Workflow {workflow_id} not found")
            return

        workflow = self.workflows[workflow_id]
        workflow.processes.append(process_id)

        # Add trace
        trace = WorkflowTrace(
            timestamp=datetime.now(),
            event_type="process_start",
            workflow_id=workflow_id,
            process_id=process_id,
            message=f"Process '{process_name}' (PID: {process_id}) started"
        )
        workflow.traces.append(trace)
        self._log_to_jarvis(workflow, trace)

        self._save_traces()

    def add_trace(self, workflow_id: str, event_type: str, message: str, subworkflow_id: Optional[str] = None, process_id: Optional[int] = None, metadata: Dict[str, Any] = None):
        """Add a trace entry to a workflow"""
        if workflow_id not in self.workflows:
            logger.warning(f"⚠️  Workflow {workflow_id} not found")
            return

        workflow = self.workflows[workflow_id]

        trace = WorkflowTrace(
            timestamp=datetime.now(),
            event_type=event_type,
            workflow_id=workflow_id,
            subworkflow_id=subworkflow_id,
            process_id=process_id,
            message=message,
            metadata=metadata or {}
        )
        workflow.traces.append(trace)
        self._log_to_jarvis(workflow, trace)

        self._save_traces()

    def register_hook(self, hook_id: str, hook_type: HookType, callback: Callable, workflow_id: Optional[str] = None, metadata: Dict[str, Any] = None) -> WorkflowHook:
        """Register a hook for workflow tracking"""
        hook = WorkflowHook(
            hook_id=hook_id,
            hook_type=hook_type,
            workflow_id=workflow_id,
            callback=callback,
            metadata=metadata or {}
        )

        self.hooks[hook_id] = hook

        # Add to workflow if specified
        if workflow_id and workflow_id in self.workflows:
            self.workflows[workflow_id].hooks.append(hook)

        logger.info(f"🔗 Registered hook: {hook_id} ({hook_type.value})")
        return hook

    def _execute_hooks(self, hook_type: HookType, workflow_id: str, subworkflow_id: Optional[str] = None):
        """Execute hooks of a specific type"""
        for hook in self.hooks.values():
            if hook.hook_type == hook_type and hook.enabled:
                if hook.workflow_id is None or hook.workflow_id == workflow_id:
                    try:
                        if hook.callback:
                            hook.callback(workflow_id, subworkflow_id)
                    except Exception as e:
                        logger.error(f"❌ Error executing hook {hook.hook_id}: {e}")

    def get_workflow_trace(self, workflow_id: str) -> List[WorkflowTrace]:
        """Get trace for a workflow"""
        if workflow_id not in self.workflows:
            return []
        return self.workflows[workflow_id].traces

    def get_all_workflows(self) -> Dict[str, Workflow]:
        """Get all workflows"""
        return self.workflows


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Workflow Tracker")
    parser.add_argument("--list", action="store_true", help="List all workflows")
    parser.add_argument("--trace", type=str, help="Get trace for workflow")
    parser.add_argument("--status", action="store_true", help="Show workflow status")

    args = parser.parse_args()

    tracker = JARVISWorkflowTracker(project_root)

    if args.list:
        workflows = tracker.get_all_workflows()
        print("\n" + "=" * 80)
        print("📊 WORKFLOWS")
        print("=" * 80)
        for workflow_id, workflow in workflows.items():
            print(f"\n  {workflow.name} ({workflow_id})")
            print(f"    Status: {workflow.status.value}")
            print(f"    Traces: {len(workflow.traces)}")
            print(f"    Subworkflows: {len(workflow.subworkflows)}")
            print(f"    Processes: {len(workflow.processes)}")
        print("=" * 80)
    elif args.trace:
        traces = tracker.get_workflow_trace(args.trace)
        print(f"\n📊 Workflow Trace: {args.trace}")
        print("=" * 80)
        for trace in traces:
            print(f"  {trace.timestamp} | {trace.event_type} | {trace.message}")
        print("=" * 80)
    elif args.status:
        workflows = tracker.get_all_workflows()
        running = sum(1 for w in workflows.values() if w.status == WorkflowStatus.RUNNING)
        completed = sum(1 for w in workflows.values() if w.status == WorkflowStatus.COMPLETED)
        failed = sum(1 for w in workflows.values() if w.status == WorkflowStatus.FAILED)

        print("\n" + "=" * 80)
        print("📊 WORKFLOW STATUS")
        print("=" * 80)
        print(f"Total: {len(workflows)}")
        print(f"Running: {running}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print("=" * 80)
    else:
        parser.print_help()


if __name__ == "__main__":


    main()