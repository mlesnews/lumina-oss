#!/usr/bin/env python3
"""
@manus Step Framework/Scaffolding Workflow Monitor

Detects when @manus workflows fall down.
JARVIS acts and executes repairs automatically.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_auto_repair_executor import JarvisAutoRepairExecutor
    JARVIS_REPAIR_AVAILABLE = True
except ImportError:
    JARVIS_REPAIR_AVAILABLE = False
    JarvisAutoRepairExecutor = None


class ManusWorkflowStatus(Enum):
    """@manus workflow status"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ManusWorkflowCheck:
    """@manus workflow check"""
    check_id: str
    workflow_name: str
    status: ManusWorkflowStatus
    checked_at: str
    failures_detected: List[str] = field(default_factory=list)
    repairs_executed: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class ManusWorkflowMonitor:
    """
    @manus Step Framework/Scaffolding Workflow Monitor

    Detects when workflows fall down.
    JARVIS acts and executes repairs automatically.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ManusWorkflowMonitor")

        # Directories
        self.data_dir = self.project_root / "data" / "manus_workflow_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.checks_file = self.data_dir / "workflow_checks.jsonl"

        # JARVIS repair executor
        self.jarvis_repair = None
        if JARVIS_REPAIR_AVAILABLE and JarvisAutoRepairExecutor:
            try:
                self.jarvis_repair = JarvisAutoRepairExecutor(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"JARVIS repair executor not available: {e}")

        # State
        self.checks: List[ManusWorkflowCheck] = []

        # @manus workflow patterns
        self.manus_workflows = [
            "user_interaction_flowstate_tracker",
            "workflow_auto_review_fix",
            "workflow_base",
            "master_workflow_orchestrator"
        ]

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        if self.checks_file.exists():
            try:
                with open(self.checks_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            check = ManusWorkflowCheck(**data)
                            check.status = ManusWorkflowStatus(data["status"])
                            self.checks.append(check)
            except Exception as e:
                self.logger.error(f"Error loading checks: {e}")

    def _save_check(self, check: ManusWorkflowCheck):
        try:
            """Save check"""
            self.checks.append(check)
            # Keep last 1000
            if len(self.checks) > 1000:
                self.checks = self.checks[-1000:]

            # Append to file
            with open(self.checks_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(check.to_dict()) + '\n')

        except Exception as e:
            self.logger.error(f"Error in _save_check: {e}", exc_info=True)
            raise
    def check_manus_workflow(self, workflow_name: str) -> ManusWorkflowCheck:
        """
        Check @manus workflow status

        If failed, JARVIS executes repairs automatically.
        """
        check_id = f"check_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()

        self.logger.info(f"🔍 Checking @manus workflow: {workflow_name}")

        # Check workflow
        status, failures = self._check_workflow_status(workflow_name)

        check = ManusWorkflowCheck(
            check_id=check_id,
            workflow_name=workflow_name,
            status=status,
            checked_at=now,
            failures_detected=failures
        )

        # If failed or degraded, JARVIS executes repairs
        if status in [ManusWorkflowStatus.FAILED, ManusWorkflowStatus.DEGRADED]:
            self.logger.warning(f"⚠️ @manus workflow {workflow_name} is {status.value}")

            if self.jarvis_repair:
                self.logger.info(f"🔧 JARVIS executing repairs for {workflow_name}")
                repairs = self.jarvis_repair.execute_repairs_for_workflow(workflow_name, workflow_name)

                check.repairs_executed = [r.action_id for r in repairs]
                self.logger.info(f"✅ JARVIS executed {len(repairs)} repairs")

        self._save_check(check)

        return check

    def _check_workflow_status(self, workflow_name: str) -> tuple[ManusWorkflowStatus, List[str]]:
        """Check workflow status"""
        failures = []

        # Check if workflow file exists
        workflow_file = self.project_root / "scripts" / "python" / f"{workflow_name}.py"
        if not workflow_file.exists():
            failures.append(f"Workflow file not found: {workflow_file}")
            return ManusWorkflowStatus.FAILED, failures

        # Check if workflow is importable
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(workflow_name, workflow_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                failures.append(f"Could not load workflow module: {workflow_name}")
                return ManusWorkflowStatus.FAILED, failures
        except Exception as e:
            failures.append(f"Error loading workflow: {e}")
            return ManusWorkflowStatus.FAILED, failures

        # Check for required @manus scaffolding components
        required_components = [
            "execute",
            "validate",
            "track_steps"
        ]

        missing_components = []
        for component in required_components:
            if not hasattr(module, component) and not any(hasattr(cls, component) for cls in module.__dict__.values() if isinstance(cls, type)):
                missing_components.append(component)

        if missing_components:
            failures.append(f"Missing @manus components: {', '.join(missing_components)}")
            return ManusWorkflowStatus.DEGRADED, failures

        # If no failures, operational
        if not failures:
            return ManusWorkflowStatus.OPERATIONAL, []
        else:
            return ManusWorkflowStatus.DEGRADED, failures

    def check_all_manus_workflows(self) -> Dict[str, Any]:
        """Check all @manus workflows"""
        results = {
            "operational": [],
            "degraded": [],
            "failed": [],
            "repairs_executed": 0
        }

        for workflow_name in self.manus_workflows:
            check = self.check_manus_workflow(workflow_name)

            if check.status == ManusWorkflowStatus.OPERATIONAL:
                results["operational"].append(workflow_name)
            elif check.status == ManusWorkflowStatus.DEGRADED:
                results["degraded"].append(workflow_name)
            elif check.status == ManusWorkflowStatus.FAILED:
                results["failed"].append(workflow_name)

            results["repairs_executed"] += len(check.repairs_executed)

        return results


def main():
    """Main execution for testing"""
    monitor = ManusWorkflowMonitor()

    print("=" * 80)
    print("🔍 @MANUS WORKFLOW MONITOR")
    print("=" * 80)

    # Check all @manus workflows
    results = monitor.check_all_manus_workflows()

    print(f"\n📊 @manus Workflow Status:")
    print(f"   Operational: {len(results['operational'])}")
    print(f"   Degraded: {len(results['degraded'])}")
    print(f"   Failed: {len(results['failed'])}")
    print(f"   Repairs Executed: {results['repairs_executed']}")


if __name__ == "__main__":



    main()