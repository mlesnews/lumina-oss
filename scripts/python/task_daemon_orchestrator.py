#!/usr/bin/env python3
"""
Task Daemon Orchestrator - Roo Code Inspired Task Management System

Implements Roo Code's advanced task orchestration logic:
- Intelligent task decomposition and planning
- Context-aware prioritization and scheduling
- Adaptive parallel execution with smart dependencies
- State persistence and recovery
- Interactive task refinement and learning

This daemon manages terminal tasks with proper precedence, timing, and conflict prevention.
Implements comprehensive logging and resource monitoring for all background tasks.
"""

import asyncio
import logging
import logging.handlers
import json
import os
import signal
import sys
import time
import threading
import subprocess
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import psutil
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor
import atexit
import heapq
from dataclasses import dataclass, field
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
logger = logging.getLogger("task_daemon_orchestrator")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TaskPriority(Enum):
    """Task execution priority levels"""
    CRITICAL = 0    # System-critical tasks (monitoring, health checks)
    HIGH = 1        # High-priority background tasks
    MEDIUM = 2      # Standard background tasks
    LOW = 3         # Low-priority maintenance tasks


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    CONFLICT = "conflict"


class TaskType(Enum):
    """Task execution types"""
    ONESHOT = "oneshot"           # Run once and exit
    PERIODIC = "periodic"         # Run at regular intervals
    CONTINUOUS = "continuous"     # Run continuously until stopped
    TRIGGERED = "triggered"       # Run when triggered by other tasks


@dataclass
class TaskStep:
    """Individual step in a decomposed task (Roo Code inspired)"""
    step_id: str
    description: str
    command: str
    args: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    estimated_duration: int = 30  # seconds
    resource_intensity: str = "low"  # low, medium, high
    can_parallelize: bool = False
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class TaskPlan:
    """Complete task execution plan (Roo Code inspired)"""
    task_name: str
    steps: List[TaskStep] = field(default_factory=list)
    parallel_groups: List[Set[str]] = field(default_factory=list)  # Steps that can run in parallel
    estimated_total_duration: int = 0
    complexity_score: float = 0.0
    last_optimized: Optional[datetime] = None


class TaskDefinition:
    """Definition of a terminal task"""

    def __init__(self, name: str, command: str, args: List[str] = None,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 task_type: TaskType = TaskType.ONESHOT,
                 interval: int = 0, dependencies: List[str] = None,
                 conflicts: List[str] = None, max_runtime: int = 300,
                 resource_limits: Dict[str, Any] = None,
                 environment: Dict[str, str] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.priority = priority
        self.task_type = task_type
        self.interval = interval  # seconds for periodic tasks
        self.dependencies = dependencies or []
        self.conflicts = conflicts or []  # tasks that cannot run simultaneously
        self.max_runtime = max_runtime  # maximum runtime in seconds
        self.resource_limits = resource_limits or {}
        self.environment = environment or {}

        # Runtime state
        self.status = TaskStatus.PENDING
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.last_run: Optional[datetime] = None
        self.exit_code: Optional[int] = None
        self.output: List[str] = []
        self.errors: List[str] = []


class ResourceMonitor:
    """Monitors system resources and task resource usage"""

    def __init__(self, max_cpu_percent: float = 80.0, max_memory_percent: float = 85.0):
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent
        self.task_processes: Dict[str, psutil.Process] = {}

    def check_system_resources(self) -> Tuple[bool, str]:
        """Check if system has sufficient resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            if cpu_percent > self.max_cpu_percent:
                return False, f"CPU usage too high: {cpu_percent}% > {self.max_cpu_percent}%"

            if memory.percent > self.max_memory_percent:
                return False, f"Memory usage too high: {memory.percent}% > {self.max_memory_percent}%"

            return True, "Resources OK"

        except Exception as e:
            return False, f"Resource check failed: {e}"

    def register_task_process(self, task_name: str, pid: int):
        """Register a task's process for monitoring"""
        try:
            self.task_processes[task_name] = psutil.Process(pid)
        except psutil.NoSuchProcess:
            pass

    def unregister_task_process(self, task_name: str):
        """Unregister a task's process"""
        self.task_processes.pop(task_name, None)

    def get_task_resources(self, task_name: str) -> Dict[str, Any]:
        """Get resource usage for a specific task"""
        if task_name not in self.task_processes:
            return {}

        try:
            proc = self.task_processes[task_name]
            return {
                "cpu_percent": proc.cpu_percent(),
                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                "memory_percent": proc.memory_percent(),
                "threads": proc.num_threads(),
                "status": proc.status()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}


class TaskDaemonOrchestrator:
    """Main orchestrator for managing terminal tasks as headless daemons"""

    def __init__(self, log_dir: str = "data/logs/daemon"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Task management
        self.tasks: Dict[str, TaskDefinition] = {}
        self.task_queue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_history: List[Dict[str, Any]] = []

        # Resource monitoring
        self.resource_monitor = ResourceMonitor()

        # Control flags
        self.running = False
        self.shutdown_event = asyncio.Event()

        # Thread pool for subprocess execution
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="task-daemon")

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        atexit.register(self.cleanup)

    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_file = self.log_dir / "task_daemon.log"

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Setup logger
        self.logger = logging.getLogger('TaskDaemon')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Task-specific loggers
        self.task_logger = logging.getLogger('TaskDaemon.Tasks')
        task_file = self.log_dir / "tasks.log"
        task_handler = logging.handlers.RotatingFileHandler(
            task_file, maxBytes=50*1024*1024, backupCount=10
        )
        task_handler.setFormatter(formatter)
        self.task_logger.addHandler(task_handler)
        self.task_logger.setLevel(logging.DEBUG)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown()

    def cleanup(self):
        """Cleanup resources on exit"""
        self.logger.info("Performing cleanup...")
        self.executor.shutdown(wait=True)

        # Stop all running tasks
        for task_name, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
                self.logger.info(f"Cancelled task: {task_name}")

        # Save final state
        self.save_state()

    def register_task(self, task_def: TaskDefinition):
        """Register a task definition"""
        self.tasks[task_def.name] = task_def
        self.logger.info(f"Registered task: {task_def.name} (priority: {task_def.priority.name}, type: {task_def.task_type.name})")

    def load_task_definitions(self):
        """Load all task definitions from configuration"""
        # Define all tasks with proper precedence and dependencies

        # Critical system monitoring tasks (run continuously)
        self.register_task(TaskDefinition(
            name="proactive_monitor",
            command="python",
            args=["scripts/python/jarvis_proactive_monitor.py", "--monitor"],
            priority=TaskPriority.CRITICAL,
            task_type=TaskType.CONTINUOUS,
            conflicts=["system_health_check"],
            max_runtime=0,  # Continuous
            resource_limits={"cpu_percent": 5.0, "memory_mb": 100}
        ))

        self.register_task(TaskDefinition(
            name="system_health_check",
            command="python",
            args=["scripts/python/verify_system_state.py"],
            priority=TaskPriority.CRITICAL,
            task_type=TaskType.PERIODIC,
            interval=300,  # Every 5 minutes
            conflicts=["proactive_monitor"],
            max_runtime=60,
            resource_limits={"cpu_percent": 10.0, "memory_mb": 150}
        ))

        # SYPHON tasks (high priority, sequential)
        self.register_task(TaskDefinition(
            name="syphon_actor_feed_aggregator",
            command="python",
            args=["scripts/python/syphon_actor_feed_aggregator.py", "--start"],
            priority=TaskPriority.HIGH,
            task_type=TaskType.CONTINUOUS,
            dependencies=["proactive_monitor"],
            conflicts=["jarvis_syphon_decisioning"],
            max_runtime=0,
            resource_limits={"cpu_percent": 15.0, "memory_mb": 200}
        ))

        self.register_task(TaskDefinition(
            name="jarvis_syphon_decisioning",
            command="python",
            args=["scripts/python/jarvis_syphon_decisioning.py", "--start"],
            priority=TaskPriority.HIGH,
            task_type=TaskType.CONTINUOUS,
            dependencies=["syphon_actor_feed_aggregator"],
            conflicts=["syphon_actor_feed_aggregator"],
            max_runtime=0,
            resource_limits={"cpu_percent": 15.0, "memory_mb": 200}
        ))

        # MANUS tasks (medium priority)
        self.register_task(TaskDefinition(
            name="manus_integration_orchestrator",
            command="python",
            args=["scripts/python/manus_integration_orchestrator.py", "--start"],
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.CONTINUOUS,
            dependencies=["proactive_monitor"],
            conflicts=["manus_cursor_controller"],
            max_runtime=0,
            resource_limits={"cpu_percent": 10.0, "memory_mb": 150}
        ))

        self.register_task(TaskDefinition(
            name="manus_cursor_controller",
            command="python",
            args=["scripts/python/manus_cursor_controller.py", "--monitor"],
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.CONTINUOUS,
            dependencies=["manus_integration_orchestrator"],
            conflicts=["manus_integration_orchestrator"],
            max_runtime=0,
            resource_limits={"cpu_percent": 12.0, "memory_mb": 180}
        ))

        # Periodic maintenance tasks (low priority)
        self.register_task(TaskDefinition(
            name="kaiju_iron_legion_monitor",
            command="python",
            args=["scripts/python/kaiju_iron_legion_monitor_self_healing.py"],
            priority=TaskPriority.LOW,
            task_type=TaskType.PERIODIC,
            interval=1800,  # Every 30 minutes
            max_runtime=300,
            resource_limits={"cpu_percent": 20.0, "memory_mb": 250}
        ))

        self.register_task(TaskDefinition(
            name="gap_analysis_scan",
            command="python",
            args=["scripts/python/simple_gap_scanner.py"],
            priority=TaskPriority.LOW,
            task_type=TaskType.PERIODIC,
            interval=3600,  # Every hour
            max_runtime=600,
            resource_limits={"cpu_percent": 15.0, "memory_mb": 200}
        ))

        self.register_task(TaskDefinition(
            name="parallel_agent_processing",
            command="python",
            args=["scripts/python/parallel_agent_session_processor.py"],
            priority=TaskPriority.LOW,
            task_type=TaskType.PERIODIC,
            interval=1800,  # Every 30 minutes
            max_runtime=900,
            resource_limits={"cpu_percent": 25.0, "memory_mb": 300}
        ))

    def check_dependencies(self, task_name: str) -> bool:
        """Check if all dependencies for a task are satisfied"""
        task = self.tasks[task_name]

        for dep in task.dependencies:
            if dep not in self.tasks:
                self.logger.error(f"Task {task_name}: unknown dependency {dep}")
                return False

            dep_task = self.tasks[dep]
            if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.RUNNING]:
                self.logger.debug(f"Task {task_name}: dependency {dep} not ready (status: {dep_task.status.value})")
                return False

        return True

    def check_conflicts(self, task_name: str) -> bool:
        """Check if any conflicting tasks are currently running"""
        task = self.tasks[task_name]

        for conflict in task.conflicts:
            if conflict in self.running_tasks:
                conflict_task = self.tasks.get(conflict)
                if conflict_task and conflict_task.status == TaskStatus.RUNNING:
                    self.logger.warning(f"Task {task_name}: conflict with running task {conflict}")
                    return False

        return True

    def check_resources(self, task_name: str) -> bool:
        """Check if system has sufficient resources for task"""
        # Check system resources
        resources_ok, reason = self.resource_monitor.check_system_resources()
        if not resources_ok:
            self.logger.warning(f"Task {task_name}: insufficient system resources: {reason}")
            return False

        # Check task-specific resource limits
        task = self.tasks[task_name]
        task_resources = self.resource_monitor.get_task_resources(task_name)

        if task_resources:
            limits = task.resource_limits
            if limits.get("cpu_percent") and task_resources.get("cpu_percent", 0) > limits["cpu_percent"]:
                self.logger.warning(f"Task {task_name}: CPU limit exceeded: {task_resources['cpu_percent']}% > {limits['cpu_percent']}%")
                return False

            if limits.get("memory_mb") and task_resources.get("memory_mb", 0) > limits["memory_mb"]:
                self.logger.warning(f"Task {task_name}: Memory limit exceeded: {task_resources['memory_mb']}MB > {limits['memory_mb']}MB")
                return False

        return True

    def decompose_task(self, task_name: str) -> TaskPlan:
        """Decompose complex tasks into smaller steps (Roo Code inspired)"""
        task = self.tasks[task_name]
        plan = TaskPlan(task_name=task_name)

        # Intelligent task decomposition based on task type and complexity
        if task_name == "gap_analysis_scan":
            # Break down gap analysis into parallel phases
            plan.steps = [
                TaskStep("scan_codebase", "Scan codebase for gaps",
                        "python", ["scripts/python/simple_gap_scanner.py", "--scan", "code"],
                        estimated_duration=120, can_parallelize=True),
                TaskStep("scan_config", "Scan configuration files",
                        "python", ["scripts/python/simple_gap_scanner.py", "--scan", "config"],
                        estimated_duration=60, can_parallelize=True),
                TaskStep("scan_docs", "Scan documentation completeness",
                        "python", ["scripts/python/simple_gap_scanner.py", "--scan", "docs"],
                        estimated_duration=90, can_parallelize=True),
                TaskStep("consolidate_results", "Consolidate and prioritize gaps",
                        "python", ["scripts/python/simple_gap_scanner.py", "--consolidate"],
                        dependencies={"scan_codebase", "scan_config", "scan_docs"},
                        estimated_duration=30, can_parallelize=False)
            ]
            plan.parallel_groups = [{"scan_codebase", "scan_config", "scan_docs"}]

        elif task_name == "parallel_agent_processing":
            # Break down parallel processing into phases
            plan.steps = [
                TaskStep("discover_sessions", "Discover agent sessions to process",
                        "python", ["scripts/python/parallel_agent_session_processor.py", "--discover"],
                        estimated_duration=60, can_parallelize=False),
                TaskStep("prioritize_sessions", "Prioritize sessions by importance",
                        "python", ["scripts/python/parallel_agent_session_processor.py", "--prioritize"],
                        dependencies={"discover_sessions"}, estimated_duration=30),
                TaskStep("process_batch_1", "Process first batch of sessions",
                        "python", ["scripts/python/parallel_agent_session_processor.py", "--process", "--batch", "1"],
                        dependencies={"prioritize_sessions"}, estimated_duration=300, can_parallelize=True),
                TaskStep("process_batch_2", "Process second batch of sessions",
                        "python", ["scripts/python/parallel_agent_session_processor.py", "--process", "--batch", "2"],
                        dependencies={"prioritize_sessions"}, estimated_duration=300, can_parallelize=True),
                TaskStep("consolidate_results", "Consolidate processing results",
                        "python", ["scripts/python/parallel_agent_session_processor.py", "--consolidate"],
                        dependencies={"process_batch_1", "process_batch_2"}, estimated_duration=60)
            ]
            plan.parallel_groups = [{"process_batch_1", "process_batch_2"}]

        elif task_name == "kaiju_iron_legion_monitor":
            # Break down monitoring into health checks and recovery
            plan.steps = [
                TaskStep("check_endpoints", "Check all Iron Legion endpoints",
                        "python", ["scripts/python/kaiju_iron_legion_monitor.py", "--check", "endpoints"],
                        estimated_duration=30, can_parallelize=True),
                TaskStep("verify_models", "Verify model availability",
                        "python", ["scripts/python/kaiju_iron_legion_monitor.py", "--check", "models"],
                        estimated_duration=30, can_parallelize=True),
                TaskStep("test_performance", "Test response performance",
                        "python", ["scripts/python/kaiju_iron_legion_monitor.py", "--check", "performance"],
                        dependencies={"check_endpoints", "verify_models"}, estimated_duration=60),
                TaskStep("generate_report", "Generate health report",
                        "python", ["scripts/python/kaiju_iron_legion_monitor.py", "--report"],
                        dependencies={"test_performance"}, estimated_duration=30)
            ]
            plan.parallel_groups = [{"check_endpoints", "verify_models"}]

        else:
            # Default: single step for simple tasks
            plan.steps = [
                TaskStep("execute", f"Execute {task_name}",
                        task.command, task.args,
                        estimated_duration=task.max_runtime or 60)
            ]

        # Calculate total duration and complexity
        plan.estimated_total_duration = sum(step.estimated_duration for step in plan.steps)
        plan.complexity_score = len(plan.steps) * 0.1 + len(plan.parallel_groups) * 0.2
        plan.last_optimized = datetime.now()

        return plan

    def optimize_task_plan(self, plan: TaskPlan) -> TaskPlan:
        """Optimize task execution plan using learned patterns (Roo Code inspired)"""
        # Load historical execution data
        history_file = self.log_dir / "task_execution_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception:
                history = {}
        else:
            history = {}

        # Analyze execution patterns for this task
        task_history = history.get(plan.task_name, [])
        if len(task_history) > 5:  # Need sufficient data for optimization
            # Calculate average execution times
            avg_durations = {}
            for record in task_history[-10:]:  # Last 10 executions
                for step_record in record.get("step_durations", {}):
                    step_name = step_record["step"]
                    duration = step_record["duration"]
                    if step_name not in avg_durations:
                        avg_durations[step_name] = []
                    avg_durations[step_name].append(duration)

            # Update step durations with learned averages
            for step in plan.steps:
                if step.step_id in avg_durations:
                    avg_duration = sum(avg_durations[step.step_id]) / len(avg_durations[step.step_id])
                    step.estimated_duration = max(10, int(avg_duration * 1.1))  # Add 10% buffer

            # Optimize parallelization based on resource conflicts
            resource_conflicts = sum(1 for record in task_history[-5:]
                                   if record.get("resource_conflicts", 0) > 0)
            if resource_conflicts > 2:  # Too many conflicts
                # Reduce parallelization
                plan.parallel_groups = [group for group in plan.parallel_groups
                                      if len(group) <= 2]

        plan.estimated_total_duration = sum(step.estimated_duration for step in plan.steps)
        return plan

    def get_contextual_priority(self, task_name: str) -> float:
        """Calculate context-aware priority (Roo Code inspired)"""
        task = self.tasks[task_name]
        base_priority = task.priority.value

        # Factor in system state
        system_load = psutil.cpu_percent() / 100.0
        memory_load = psutil.virtual_memory().percent / 100.0
        load_factor = (system_load + memory_load) / 2.0

        # Critical tasks get priority boost when system is under load
        if task.priority == TaskPriority.CRITICAL and load_factor > 0.7:
            base_priority -= 0.5

        # Time-sensitive tasks get priority as deadlines approach
        if task.task_type == TaskType.PERIODIC and task.last_run:
            time_since_last = (datetime.now() - task.last_run).total_seconds()
            overdue_factor = max(0, time_since_last - task.interval) / task.interval
            base_priority -= overdue_factor * 0.3

        # Dependency pressure - boost priority if many tasks depend on this one
        dependent_count = sum(1 for t in self.tasks.values()
                            if task_name in t.dependencies)
        dependency_boost = dependent_count * 0.1

        return max(0, base_priority - dependency_boost)

    async def execute_decomposed_task(self, task_name: str):
        """Execute a task using intelligent decomposition (Roo Code inspired)"""
        task = self.tasks[task_name]

        # Get or create task plan
        plan_file = self.log_dir / f"task_plans/{task_name}_plan.json"
        if plan_file.exists() and (datetime.now() - datetime.fromtimestamp(plan_file.stat().st_mtime)).days < 7:
            # Load existing plan
            try:
                with open(plan_file, 'r') as f:
                    plan_data = json.load(f)
                plan = TaskPlan(**plan_data)
            except Exception:
                plan = self.decompose_task(task_name)
        else:
            # Create new plan
            plan = self.decompose_task(task_name)

        # Optimize plan with historical data
        plan = self.optimize_task_plan(plan)

        # Save plan
        plan_file.parent.mkdir(exist_ok=True)
        with open(plan_file, 'w') as f:
            json.dump({
                "task_name": plan.task_name,
                "steps": [vars(step) for step in plan.steps],
                "parallel_groups": [list(group) for group in plan.parallel_groups],
                "estimated_total_duration": plan.estimated_total_duration,
                "complexity_score": plan.complexity_score,
                "last_optimized": plan.last_optimized.isoformat() if plan.last_optimized else None
            }, f, indent=2)

        self.logger.info(f"Executing decomposed task {task_name} with {len(plan.steps)} steps")

        # Execute steps with parallelization support
        step_statuses = {}
        step_durations = []
        running_steps = {}

        for step in plan.steps:
            # Check dependencies
            if step.dependencies and not all(step_statuses.get(dep, False) for dep in step.dependencies):
                continue

            # Check if we can run in parallel
            can_run_parallel = step.can_parallelize and len(running_steps) < 3  # Max 3 parallel steps

            if can_run_parallel:
                # Run in parallel
                step_task = asyncio.create_task(self.execute_task_step(step, task))
                running_steps[step.step_id] = step_task
            else:
                # Wait for running steps to complete
                if running_steps:
                    await asyncio.gather(*running_steps.values())
                    for step_id, task_future in running_steps.items():
                        step_statuses[step_id] = task_future.result()
                        # Record duration
                        if hasattr(task_future, '_start_time'):
                            duration = (datetime.now() - task_future._start_time).total_seconds()
                            step_durations.append({"step": step_id, "duration": duration})
                    running_steps.clear()

                # Run current step
                start_time = datetime.now()
                success = await self.execute_task_step(step, task)
                duration = (datetime.now() - start_time).total_seconds()
                step_statuses[step.step_id] = success
                step_durations.append({"step": step.step_id, "duration": duration})

        # Wait for any remaining parallel steps
        if running_steps:
            await asyncio.gather(*running_steps.values())
            for step_id, task_future in running_steps.items():
                step_statuses[step_id] = task_future.result()

        # Record execution history
        history_record = {
            "timestamp": datetime.now().isoformat(),
            "task_name": task_name,
            "step_durations": step_durations,
            "total_steps": len(plan.steps),
            "parallel_groups": len(plan.parallel_groups),
            "resource_conflicts": 0,  # Could be tracked
            "success": all(step_statuses.values())
        }

        # Save to history
        history_file = self.log_dir / "task_execution_history.json"
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = {}

            if task_name not in history:
                history[task_name] = []
            history[task_name].append(history_record)

            # Keep only last 50 executions per task
            history[task_name] = history[task_name][-50:]

            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            self.logger.warning(f"Failed to save execution history: {e}")

        # Overall success
        success = all(step_statuses.values())
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        self.logger.info(f"Decomposed task {task_name} {'completed' if success else 'failed'}")

    async def execute_task_step(self, step: TaskStep, parent_task: TaskDefinition) -> bool:
        """Execute a single task step"""
        try:
            self.logger.debug(f"Executing step {step.step_id}: {step.description}")

            # Prepare command
            cmd = [step.command] + step.args
            env = os.environ.copy()
            env.update(parent_task.environment)

            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=os.getcwd()
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=step.estimated_duration * 2  # Double the estimated time
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"Step {step.step_id} timed out, terminating")
                process.terminate()
                await asyncio.sleep(5)
                if process.returncode is None:
                    process.kill()
                return False

            success = process.returncode == 0

            if not success:
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                self.logger.warning(f"Step {step.step_id} failed: {error_msg}")

                # Retry logic
                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    self.logger.info(f"Retrying step {step.step_id} (attempt {step.retry_count + 1})")
                    await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                    return await self.execute_task_step(step, parent_task)

            return success

        except Exception as e:
            self.logger.error(f"Step {step.step_id} execution error: {e}")
            return False

    async def execute_task(self, task_name: str):
        """Execute a single task"""
        task = self.tasks[task_name]

        try:
            self.logger.info(f"Starting task: {task_name}")
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            task.last_run = task.start_time

            # Prepare command
            cmd = [task.command] + task.args
            env = os.environ.copy()
            env.update(task.environment)

            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                self.executor,
                subprocess.Popen,
                cmd,
                {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "env": env, "cwd": os.getcwd()}
            )

            task.process = process
            self.resource_monitor.register_task_process(task_name, process.pid)

            # Monitor process
            while True:
                if process.poll() is not None:
                    break

                # Check for timeout
                if task.max_runtime > 0:
                    runtime = (datetime.now() - task.start_time).total_seconds()
                    if runtime > task.max_runtime:
                        self.logger.warning(f"Task {task_name}: timeout after {runtime}s, terminating")
                        process.terminate()
                        await asyncio.sleep(5)
                        if process.poll() is None:
                            process.kill()
                        break

                await asyncio.sleep(1)

            # Get output
            stdout, stderr = process.communicate()
            task.exit_code = process.returncode
            task.output = stdout.decode('utf-8', errors='ignore').split('\n') if stdout else []
            task.errors = stderr.decode('utf-8', errors='ignore').split('\n') if stderr else []

            # Update status
            task.end_time = datetime.now()
            if task.exit_code == 0:
                task.status = TaskStatus.COMPLETED
                self.logger.info(f"Task {task_name}: completed successfully")
            else:
                task.status = TaskStatus.FAILED
                self.logger.error(f"Task {task_name}: failed with exit code {task.exit_code}")

            # Log output
            if task.output:
                self.task_logger.info(f"Task {task_name} stdout: {' '.join(task.output[:5])}...")
            if task.errors:
                self.task_logger.error(f"Task {task_name} stderr: {' '.join(task.errors[:5])}...")

        except Exception as e:
            self.logger.error(f"Task {task_name}: execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.errors.append(str(e))
        finally:
            self.resource_monitor.unregister_task_process(task_name)

        # Record in history
        self.task_history.append({
            "task_name": task_name,
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "end_time": task.end_time.isoformat() if task.end_time else None,
            "status": task.status.value,
            "exit_code": task.exit_code,
            "output_lines": len(task.output),
            "error_lines": len(task.errors)
        })

        # Keep history limited
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-500:]

    async def task_scheduler(self):
        """Main task scheduler loop"""
        self.logger.info("Task scheduler started")

        while not self.shutdown_event.is_set():
            try:
                # Schedule periodic tasks
                now = datetime.now()
                for task_name, task in self.tasks.items():
                    if task.task_type == TaskType.PERIODIC and task.status != TaskStatus.RUNNING:
                        if task.last_run is None or (now - task.last_run).total_seconds() >= task.interval:
                            await self.schedule_task(task_name)

                # Schedule continuous tasks if not running
                for task_name, task in self.tasks.items():
                    if task.task_type == TaskType.CONTINUOUS and task_name not in self.running_tasks:
                        await self.schedule_task(task_name)

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(30)

    async def schedule_task(self, task_name: str):
        """Schedule a task for execution with intelligent prioritization (Roo Code inspired)"""
        if task_name in self.running_tasks:
            return

        # Check prerequisites
        if not self.check_dependencies(task_name):
            return

        if not self.check_conflicts(task_name):
            return

        if not self.check_resources(task_name):
            return

        # Calculate context-aware priority (Roo Code inspired)
        contextual_priority = self.get_contextual_priority(task_name)

        # Determine execution strategy based on task complexity
        task = self.tasks[task_name]
        complex_tasks = {
            "gap_analysis_scan",
            "parallel_agent_processing",
            "kaiju_iron_legion_monitor",
            "syphon_agent_history_all_envs"
        }

        use_decomposed_execution = task_name in complex_tasks

        try:
            if use_decomposed_execution:
                # Use intelligent decomposed execution
                task_future = asyncio.create_task(self.execute_decomposed_task(task_name))
                self.logger.info(f"Scheduled complex task: {task_name} (priority: {contextual_priority:.2f}, decomposed)")
            else:
                # Use standard execution
                task_future = asyncio.create_task(self.execute_task(task_name))
                self.logger.info(f"Scheduled task: {task_name} (priority: {contextual_priority:.2f})")

            self.running_tasks[task_name] = task_future

            # Handle task completion
            def task_done_callback(fut):
                self.running_tasks.pop(task_name, None)
                try:
                    fut.result()
                except Exception as e:
                    logger.error(f"Task {task_name} callback error: {e}")

            task_future.add_done_callback(task_done_callback)

        except Exception as e:
            self.logger.error(f"Failed to schedule task {task_name}: {e}")

    def save_state(self):
        """Save current orchestrator state"""
        state_file = self.log_dir / "orchestrator_state.json"
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "running_tasks": list(self.running_tasks.keys()),
                "task_statuses": {
                    name: {
                        "status": task.status.value,
                        "last_run": task.last_run.isoformat() if task.last_run else None,
                        "exit_code": task.exit_code
                    }
                    for name, task in self.tasks.items()
                },
                "task_history_count": len(self.task_history)
            }

            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    async def run(self):
        """Main orchestrator run loop"""
        self.logger.info("Task Daemon Orchestrator starting...")
        self.running = True

        # Load task definitions
        self.load_task_definitions()

        # Start scheduler
        scheduler_task = asyncio.create_task(self.task_scheduler())

        # Save state periodically
        save_task = asyncio.create_task(self.periodic_save())

        try:
            await self.shutdown_event.wait()
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info("Shutting down orchestrator...")

            # Cancel all tasks
            scheduler_task.cancel()
            save_task.cancel()

            for task_name, task in list(self.running_tasks.items()):
                task.cancel()

            # Wait for cleanup
            await asyncio.sleep(2)

    async def periodic_save(self):
        """Periodically save orchestrator state"""
        while not self.shutdown_event.is_set():
            await asyncio.sleep(300)  # Every 5 minutes
            self.save_state()

    def shutdown(self):
        """Shutdown the orchestrator"""
        self.logger.info("Shutdown initiated")
        self.running = False
        self.shutdown_event.set()


def main():
    """Main entry point"""
    orchestrator = TaskDaemonOrchestrator()

    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        orchestrator.logger.error(f"Orchestrator failed: {e}")
        sys.exit(1)


if __name__ == "__main__":


    main()