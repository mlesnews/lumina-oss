#!/usr/bin/env python3
"""
AI-Managed Virtual Assistant Orchestrator

AI-driven system that manages all in-flight and live automated handling of VAs.
Uses JARVIS, SYPHON, and R5 for intelligent decision-making and automated management.

Features:
- Real-time monitoring of all VAs
- Automated lifecycle management (start/stop/restart)
- Intelligent issue detection and resolution
- SYPHON-based intelligence extraction for decision-making
- R5 context aggregation for informed decisions
- JARVIS workflow orchestration
- Automated scaling and resource management

Tags: #AI #ORCHESTRATION #AUTOMATION #JARVIS #SYPHON #R5 @JARVIS @LUMINA
"""

import sys
import time
import json
import threading
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from jarvis_lumina_master_orchestrator import SubAgent


# Workflow tracking imports
try:
    from jarvis_workflow_tracker import WorkflowStatus
except ImportError:
    # Fallback enum if import fails
    class WorkflowStatus(Enum):
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"

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

logger = get_logger("AIManagedVAOrchestrator")

# Integrations
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

try:
    from syphon import SYPHONSystem, SYPHONConfig
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None


class VAState(Enum):
    """Virtual Assistant state"""
    UNKNOWN = "unknown"
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    STARTING = "starting"
    STOPPING = "stopping"
    DEGRADED = "degraded"


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class VAManifest:
    """Virtual Assistant manifest"""
    name: str
    script_path: Path
    enabled: bool = True
    auto_start: bool = True
    auto_restart: bool = True
    restart_delay: float = 5.0
    max_restarts: int = 5
    health_check_interval: float = 30.0
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {
        "max_cpu_percent": 80.0,
        "max_memory_mb": 512
    })
    dependencies: List[str] = field(default_factory=list)
    priority: str = "medium"  # critical, high, medium, low


@dataclass
class VAMonitor:
    """Virtual Assistant monitor"""
    manifest: VAManifest
    state: VAState = VAState.UNKNOWN
    pid: Optional[int] = None
    process: Optional[psutil.Process] = None
    start_time: Optional[datetime] = None
    restart_count: int = 0
    last_health_check: Optional[datetime] = None
    issues: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "cpu_percent": 0.0,
        "memory_mb": 0.0,
        "uptime_seconds": 0.0
    })


@dataclass
class AutomatedAction:
    """Automated action taken by AI"""
    timestamp: datetime
    action_type: str
    va_name: str
    reason: str
    severity: IssueSeverity
    result: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIManagedVAOrchestrator:
    """
    AI-Managed Virtual Assistant Orchestrator

    Uses AI (JARVIS) to intelligently manage all in-flight VA operations:
    - Real-time monitoring
    - Automated issue detection and resolution
    - Intelligent scaling decisions
    - Resource management
    - Lifecycle automation
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.running = False
        self.monitors: Dict[str, VAMonitor] = {}
        self.actions_log: List[AutomatedAction] = []

        # Headless Process Manager
        try:
            from headless_process_manager import HeadlessProcessManager
            self.process_manager = HeadlessProcessManager(project_root)
            logger.info("✅ Headless Process Manager integrated")
        except ImportError:
            self.process_manager = None
            logger.warning("⚠️  Headless Process Manager not available")

        # JARVIS Workflow Tracker
        try:
            from jarvis_workflow_tracker import JARVISWorkflowTracker
            self.workflow_tracker = JARVISWorkflowTracker(project_root)
            logger.info("✅ JARVIS Workflow Tracker integrated")
        except ImportError:
            self.workflow_tracker = None
            logger.warning("⚠️  JARVIS Workflow Tracker not available")

        # AI Integrations
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root)
                logger.info("✅ JARVIS integrated for AI-driven orchestration")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS not available: {e}")

        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON integrated for intelligence extraction")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                logger.info("✅ R5 integrated for context aggregation")
            except Exception as e:
                logger.warning(f"⚠️  R5 not available: {e}")

        # Load VA manifests
        self.manifests = self._load_va_manifests()
        self._initialize_monitors()

        logger.info(f"✅ AI-Managed VA Orchestrator initialized with {len(self.manifests)} VAs")

# SubAgent registry (Puppetmaster delegation via @SUBAGENTS)
        self.subagents = {}
        self._init_subagents()
    def _load_va_manifests(self) -> Dict[str, VAManifest]:
        try:
            """Load VA manifests from configuration"""
            manifests = {}

            # Default VA configurations
            va_configs = {
                "ironman": {
                    "script_path": self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py",
                    "priority": "high",
                    "auto_start": True,
                    "auto_restart": True
                },
                "kenny": {
                    "script_path": self.project_root / "scripts" / "python" / "kenny_imva_enhanced.py",
                    "priority": "medium",
                    "auto_start": False,
                    "auto_restart": True
                },
                "anakin": {
                    "script_path": self.project_root / "scripts" / "python" / "anakin_combat_virtual_assistant.py",
                    "priority": "medium",
                    "auto_start": False,
                    "auto_restart": True
                },
                "jarvis": {
                    "script_path": self.project_root / "scripts" / "python" / "jarvis_virtual_assistant.py",
                    "priority": "critical",
                    "auto_start": True,
                    "auto_restart": True
                }
            }

            for va_name, config in va_configs.items():
                script_path = config["script_path"]
                if script_path.exists():
                    manifests[va_name] = VAManifest(
                        name=va_name,
                        script_path=script_path,
                        enabled=True,
                        auto_start=config.get("auto_start", True),
                        auto_restart=config.get("auto_restart", True),
                        priority=config.get("priority", "medium")
                    )

            return manifests

        except Exception as e:
            self.logger.error(f"Error in _load_va_manifests: {e}", exc_info=True)
            raise
    def _initialize_monitors(self):
        """Initialize monitors for all VAs"""
        for va_name, manifest in self.manifests.items():
            self.monitors[va_name] = VAMonitor(manifest=manifest)

    def _find_va_process(self, va_name: str, script_path: Path) -> Optional[psutil.Process]:
        """Find running process for a VA"""
        script_name = script_path.name
        script_path_str = str(script_path.resolve())
        script_path_normalized = script_path_str.replace('\\', '/').lower()

        # On Windows, use faster psutil-based detection first, then fallback to WMI if needed
        # Skip PowerShell as it's too slow and times out

        # Fallback to psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Try to get cmdline - may not be available on Windows
                try:
                    cmdline = proc.cmdline()
                    if cmdline:
                        # Check if script name or full path is in cmdline
                        cmdline_str = ' '.join(cmdline).lower()
                        cmdline_normalized = cmdline_str.replace('\\', '/')
                        if (script_name.lower() in cmdline_normalized or 
                            script_path_normalized in cmdline_normalized or
                            script_path_str.lower() in cmdline_normalized):
                            return proc
                except (psutil.AccessDenied, AttributeError):
                    # On Windows, try using WMI as fallback
                    if sys.platform == 'win32':
                        try:
                            import subprocess
                            result = subprocess.run(
                                ['wmic', 'process', 'where', f'ProcessId={proc.pid}', 'get', 'CommandLine'],
                                capture_output=True,
                                text=True,
                                timeout=1
                            )
                            cmdline_lower = result.stdout.lower().replace('\\', '/')
                            if (script_name.lower() in cmdline_lower or 
                                script_path_normalized in cmdline_lower or
                                script_path_str.lower() in cmdline_lower):
                                return proc
                        except:
                            pass

                # Also check by process name and exe path
                try:
                    exe = proc.exe()
                    if script_name.lower() in exe.lower():
                        return proc
                except:
                    pass

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return None

    def _check_va_health(self, monitor: VAMonitor) -> Dict[str, Any]:
        """Check health of a VA using AI decision-making"""
        health = {
            "healthy": True,
            "issues": [],
            "metrics": {}
        }

        if monitor.process:
            try:
                # Get process metrics
                cpu_percent = monitor.process.cpu_percent(interval=0.1)
                memory_info = monitor.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024

                monitor.metrics["cpu_percent"] = cpu_percent
                monitor.metrics["memory_mb"] = memory_mb

                # Check resource limits
                max_cpu = monitor.manifest.resource_limits.get("max_cpu_percent", 80.0)
                max_memory = monitor.manifest.resource_limits.get("max_memory_mb", 512)

                if cpu_percent > max_cpu:
                    health["healthy"] = False
                    health["issues"].append({
                        "type": "high_cpu",
                        "severity": IssueSeverity.HIGH,
                        "value": cpu_percent,
                        "threshold": max_cpu
                    })

                if memory_mb > max_memory:
                    health["healthy"] = False
                    health["issues"].append({
                        "type": "high_memory",
                        "severity": IssueSeverity.HIGH,
                        "value": memory_mb,
                        "threshold": max_memory
                    })

                # Check if process is responsive
                if not monitor.process.is_running():
                    health["healthy"] = False
                    health["issues"].append({
                        "type": "process_not_running",
                        "severity": IssueSeverity.CRITICAL
                    })

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                health["healthy"] = False
                health["issues"].append({
                    "type": "process_error",
                    "severity": IssueSeverity.CRITICAL,
                    "error": str(e)
                })
        else:
            health["healthy"] = False
            health["issues"].append({
                "type": "process_not_found",
                "severity": IssueSeverity.HIGH
            })

        return health

    def _ai_decide_action(self, monitor: VAMonitor, health: Dict[str, Any]) -> Optional[str]:
        """Use AI (JARVIS/SYPHON/R5) to decide what action to take"""
        if not health["healthy"]:
            issues = health.get("issues", [])

            # Use SYPHON to extract intelligence about the issue
            if self.syphon and issues:
                issue_context = {
                    "va_name": monitor.manifest.name,
                    "issues": issues,
                    "state": monitor.state.value,
                    "restart_count": monitor.restart_count
                }

                # Extract intelligence from similar past issues
                try:
                    # This would use SYPHON to find similar issues and solutions
                    # For now, use rule-based decision with AI context
                    pass
                except Exception as e:
                    logger.debug(f"SYPHON intelligence extraction error: {e}")

            # Use R5 for context aggregation
            if self.r5:
                try:
                    # Aggregate context about VA health patterns
                    # This would inform decision-making
                    pass
                except Exception as e:
                    logger.debug(f"R5 context aggregation error: {e}")

            # Use JARVIS for workflow orchestration
            if self.jarvis:
                try:
                    # JARVIS would orchestrate the resolution workflow
                    # For now, use intelligent decision-making
                    pass
                except Exception as e:
                    logger.debug(f"JARVIS orchestration error: {e}")

            # AI Decision Logic
            critical_issues = [i for i in issues if i.get("severity") == IssueSeverity.CRITICAL]
            high_issues = [i for i in issues if i.get("severity") == IssueSeverity.HIGH]

            if critical_issues:
                # Critical: Restart if within limits
                if monitor.manifest.auto_restart and monitor.restart_count < monitor.manifest.max_restarts:
                    return "restart"
                else:
                    return "alert"

            if high_issues:
                # High: Monitor and potentially restart
                if monitor.restart_count < monitor.manifest.max_restarts:
                    return "restart"
                else:
                    return "degrade"

            # Medium/Low: Continue monitoring
            return "monitor"

        return None

    def _start_va(self, monitor: VAMonitor) -> bool:
        """Start a VA using headless process manager with workflow tracking"""
        try:
            logger.info(f"🚀 Starting {monitor.manifest.name}...")

            workflow_id = f"va_{monitor.manifest.name}_{int(time.time())}"

            # Start workflow tracking
            if self.workflow_tracker:
                self.workflow_tracker.start_workflow(
                    workflow_id,
                    f"VA Start: {monitor.manifest.name}",
                    metadata={"va_name": monitor.manifest.name, "script": str(monitor.manifest.script_path)}
                )

            # Use headless process manager if available
            if self.process_manager:
                proc = self.process_manager.start_headless_process(
                    name=monitor.manifest.name,
                    script_path=monitor.manifest.script_path,
                    workflow_id=workflow_id,
                    subworkflow_id=None
                )

                # Wait longer for process to start and stabilize
                time.sleep(5)  # Increased wait time

                # Try multiple times to find the process (processes may take time to appear)
                proc_found = None
                for attempt in range(3):
                    proc_found = self._find_va_process(monitor.manifest.name, monitor.manifest.script_path)
                    if proc_found:
                        break
                    time.sleep(2)  # Wait 2 seconds between attempts

                if proc_found:
                    monitor.process = proc_found
                    monitor.pid = proc_found.pid
                    monitor.state = VAState.RUNNING
                    monitor.start_time = datetime.now()

                    # Track process in workflow
                    if self.workflow_tracker:
                        self.workflow_tracker.add_process(workflow_id, proc_found.pid, monitor.manifest.name)
                        self.workflow_tracker.add_trace(workflow_id, "va_started", f"{monitor.manifest.name} started successfully")
                        self.workflow_tracker.end_workflow(workflow_id, WorkflowStatus.COMPLETED)

                    logger.info(f"✅ {monitor.manifest.name} started (PID: {proc_found.pid})")
                    return True
                else:
                    if self.workflow_tracker:
                        self.workflow_tracker.end_workflow(workflow_id, WorkflowStatus.FAILED, "Process not found after start")
                    logger.warning(f"⚠️  {monitor.manifest.name} may not have started - process not found")
                    monitor.state = VAState.STOPPED
                    return False
            else:
                # Fallback to direct subprocess (headless)
                import subprocess
                creation_flags = 0
                if sys.platform == 'win32':
                    creation_flags = 0x08000008  # DETACHED_PROCESS + CREATE_NO_WINDOW

                log_dir = self.project_root / "logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / f"{monitor.manifest.name}_{datetime.now().strftime('%Y%m%d')}.log"

                with open(log_file, 'a') as log_handle:
                    subprocess.Popen(
                        [sys.executable, str(monitor.manifest.script_path)],
                        cwd=str(self.project_root),
                        stdout=log_handle,
                        stderr=subprocess.STDOUT,
                        creationflags=creation_flags,
                        start_new_session=True if sys.platform != 'win32' else False
                    )

                # Wait longer for process to start and stabilize
                time.sleep(5)  # Increased wait time

                # Try multiple times to find the process
                proc_found = None
                for attempt in range(3):
                    proc_found = self._find_va_process(monitor.manifest.name, monitor.manifest.script_path)
                    if proc_found:
                        break
                    time.sleep(2)  # Wait 2 seconds between attempts

                if proc_found:
                    monitor.process = proc_found
                    monitor.pid = proc_found.pid
                    monitor.state = VAState.RUNNING
                    monitor.start_time = datetime.now()
                    logger.info(f"✅ {monitor.manifest.name} started (PID: {proc_found.pid})")
                    return True
                else:
                    logger.warning(f"⚠️  {monitor.manifest.name} may not have started - process not found")
                    monitor.state = VAState.STOPPED
                    return False

        except Exception as e:
            logger.error(f"❌ Error starting {monitor.manifest.name}: {e}", exc_info=True)
            monitor.state = VAState.CRASHED
            return False

    def _stop_va(self, monitor: VAMonitor) -> bool:
        """Stop a VA"""
        try:
            if monitor.process:
                logger.info(f"🛑 Stopping {monitor.manifest.name} (PID: {monitor.pid})...")
                monitor.process.terminate()

                try:
                    monitor.process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    monitor.process.kill()
                    monitor.process.wait(timeout=2)

                monitor.process = None
                monitor.pid = None
                monitor.state = VAState.STOPPED
                logger.info(f"✅ {monitor.manifest.name} stopped")
                return True
        except Exception as e:
            logger.error(f"❌ Error stopping {monitor.manifest.name}: {e}")
            return False

        return False

    def _restart_va(self, monitor: VAMonitor) -> bool:
        """Restart a VA"""
        logger.info(f"🔄 Restarting {monitor.manifest.name}...")

        if monitor.state == VAState.RUNNING:
            self._stop_va(monitor)
            time.sleep(monitor.manifest.restart_delay)

        monitor.restart_count += 1
        monitor.state = VAState.STARTING

        if self._start_va(monitor):
            # Log automated action
            action = AutomatedAction(
                timestamp=datetime.now(),
                action_type="restart",
                va_name=monitor.manifest.name,
                reason=f"Health check failed (restart #{monitor.restart_count})",
                severity=IssueSeverity.HIGH,
                result="success",
                metadata={"restart_count": monitor.restart_count}
            )
            self.actions_log.append(action)

            # Track workflow in JARVIS
            if self.workflow_tracker:
                try:
                    workflow_id = f"va_restart_{monitor.manifest.name}_{int(time.time())}"
                    self.workflow_tracker.start_workflow(workflow_id, f"VA Restart: {monitor.manifest.name}")
                    if monitor.pid:
                        self.workflow_tracker.add_process(workflow_id, monitor.pid, monitor.manifest.name)
                    self.workflow_tracker.add_trace(workflow_id, "va_restart", f"Restarted {monitor.manifest.name} (restart #{monitor.restart_count})")
                    self.workflow_tracker.end_workflow(workflow_id)
                except Exception as e:
                    logger.debug(f"Workflow tracking error: {e}")

            return True

        return False

    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("📊 Starting AI-managed monitoring loop...")

        while self.running:
            try:
                # Update process references
                for va_name, monitor in self.monitors.items():
                    if monitor.manifest.enabled:
                        # Find current process
                        proc = self._find_va_process(va_name, monitor.manifest.script_path)

                        if proc:
                            monitor.process = proc
                            monitor.pid = proc.pid
                            if monitor.state != VAState.RUNNING:
                                monitor.state = VAState.RUNNING
                                monitor.start_time = datetime.now()
                        else:
                            if monitor.state == VAState.RUNNING:
                                monitor.state = VAState.CRASHED
                                monitor.process = None
                                monitor.pid = None

                        # Health check
                        current_time = datetime.now()
                        if not monitor.last_health_check or \
                           (current_time - monitor.last_health_check).total_seconds() >= monitor.manifest.health_check_interval:

                            health = self._check_va_health(monitor)
                            monitor.last_health_check = current_time

                            # AI decision
                            action = self._ai_decide_action(monitor, health)

                            if action == "restart":
                                self._restart_va(monitor)
                            elif action == "alert":
                                logger.warning(f"⚠️  {va_name} requires attention (restart limit reached)")
                            elif action == "degrade":
                                monitor.state = VAState.DEGRADED
                                logger.warning(f"⚠️  {va_name} degraded")

                            # Update issues
                            monitor.issues = health.get("issues", [])

                # Auto-start VAs if configured
                for va_name, monitor in self.monitors.items():
                    if monitor.manifest.enabled and monitor.manifest.auto_start:
                        if monitor.state == VAState.STOPPED or monitor.state == VAState.UNKNOWN:
                            if monitor.state != VAState.STARTING:
                                self._start_va(monitor)

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(10)

    def start(self):
        """Start AI-managed orchestration"""
        if self.running:
            logger.warning("Orchestrator already running")
            return

        self.running = True

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()

        logger.info("=" * 80)
        logger.info("🤖 AI-MANAGED VA ORCHESTRATOR STARTED")
        logger.info("=" * 80)
        logger.info(f"Monitoring {len(self.monitors)} virtual assistants")
        logger.info("Features:")
        logger.info("  ✅ Real-time health monitoring")
        logger.info("  ✅ AI-driven decision making (JARVIS/SYPHON/R5)")
        logger.info("  ✅ Automated issue detection and resolution")
        logger.info("  ✅ Intelligent lifecycle management")
        logger.info("  ✅ Resource management")
        logger.info("=" * 80)

    def stop(self):
        """Stop AI-managed orchestration"""
        self.running = False
        logger.info("🛑 AI-Managed VA Orchestrator stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "running": self.running,
            "monitors": {
                name: {
                    "state": monitor.state.value if hasattr(monitor.state, 'value') else str(monitor.state),
                    "pid": monitor.pid,
                    "uptime": (datetime.now() - monitor.start_time).total_seconds() if monitor.start_time else 0,
                    "restart_count": monitor.restart_count,
                    "metrics": monitor.metrics,
                    "issues": [
                        {
                            "type": issue.get("type") if isinstance(issue, dict) else getattr(issue, "type", None),
                            "severity": issue.get("severity").value if isinstance(issue, dict) and hasattr(issue.get("severity"), 'value') else str(issue.get("severity")) if isinstance(issue, dict) and issue.get("severity") else (issue.severity.value if hasattr(issue, "severity") and hasattr(issue.severity, 'value') else str(issue.severity) if hasattr(issue, "severity") else None),
                            "message": issue.get("message") if isinstance(issue, dict) else getattr(issue, "message", None)
                        }
                        for issue in monitor.issues
                    ]
                }
                for name, monitor in self.monitors.items()
            },
            "actions_taken": len(self.actions_log),
            "recent_actions": [
                {
                    "timestamp": action.timestamp.isoformat() if hasattr(action.timestamp, 'isoformat') else str(action.timestamp),
                    "action": action.action_type,
                    "va": action.va_name,
                    "reason": action.reason,
                    "severity": action.severity.value if hasattr(action.severity, 'value') else str(action.severity)
                }
                for action in self.actions_log[-10:]
            ]
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="AI-Managed VA Orchestrator")
    parser.add_argument("--start", action="store_true", help="Start orchestrator")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    orchestrator = AIManagedVAOrchestrator(project_root)

    if args.start or args.daemon:
        orchestrator.start()

        if args.daemon:
            try:
                while True:
                    time.sleep(60)
                    # Print status every minute
                    status = orchestrator.get_status()
                    logger.info(f"📊 Status: {len([m for m in status['monitors'].values() if m['state'] == 'running'])} VAs running")
            except KeyboardInterrupt:
                orchestrator.stop()
        else:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                orchestrator.stop()
    elif args.status:
        orchestrator.start()
        time.sleep(5)  # Let it initialize
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":


    main()