#!/usr/bin/env python3
"""
Workflow Functionality Framework & Scaffolding

Ensures all workflows are fully functional.
When they're not, MARVIN roasts them.
JARVIS follows up on each fault and repairs.
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
    from marvin_granular_roast import MarvinGranularRoast
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    MarvinGranularRoast = None

try:
    from jarvis_marvin_followup import JarvisMarvinFollowUp
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JarvisMarvinFollowUp = None

try:
    from git_helpdesk_integration import GitHelpdeskIntegration
    GIT_HELPDESK_AVAILABLE = True
except ImportError:
    GIT_HELPDESK_AVAILABLE = False
    GitHelpdeskIntegration = None


class FunctionalityStatus(Enum):
    """Functionality status"""
    FULLY_FUNCTIONAL = "fully_functional"
    PARTIALLY_FUNCTIONAL = "partially_functional"
    NON_FUNCTIONAL = "non_functional"
    UNKNOWN = "unknown"


@dataclass
class WorkflowFunctionalityCheck:
    """Workflow functionality check"""
    check_id: str
    workflow_id: str
    workflow_name: str
    status: FunctionalityStatus
    checked_at: str
    faults_identified: List[str] = field(default_factory=list)
    roasted: bool = False
    roast_id: Optional[str] = None
    repaired: bool = False
    repair_id: Optional[str] = None
    helpdesk_ticket_id: Optional[str] = None
    git_commit_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class WorkflowFunctionalityFramework:
    """
    Workflow Functionality Framework & Scaffolding

    Ensures all workflows are fully functional.
    When they're not, MARVIN roasts them.
    JARVIS follows up on each fault and repairs.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("WorkflowFunctionalityFramework")

        # Directories
        self.data_dir = self.project_root / "data" / "workflow_functionality"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.checks_file = self.data_dir / "functionality_checks.jsonl"

        # MARVIN roaster
        self.marvin_roaster = None
        if MARVIN_AVAILABLE and MarvinGranularRoast:
            try:
                self.marvin_roaster = MarvinGranularRoast(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"MARVIN roaster not available: {e}")

        # JARVIS follow-up
        self.jarvis_followup = None
        if JARVIS_AVAILABLE and JarvisMarvinFollowUp:
            try:
                self.jarvis_followup = JarvisMarvinFollowUp(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"JARVIS follow-up not available: {e}")

        # Git/Helpdesk integration
        self.git_helpdesk = None
        if GIT_HELPDESK_AVAILABLE and GitHelpdeskIntegration:
            try:
                self.git_helpdesk = GitHelpdeskIntegration(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Git/Helpdesk integration not available: {e}")

        # State
        self.checks: List[WorkflowFunctionalityCheck] = []

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
                            check = WorkflowFunctionalityCheck(**data)
                            check.status = FunctionalityStatus(data["status"])
                            self.checks.append(check)
            except Exception as e:
                self.logger.error(f"Error loading checks: {e}")

    def _save_check(self, check: WorkflowFunctionalityCheck):
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
    def check_workflow_functionality(
        self,
        workflow_id: str,
        workflow_name: str
    ) -> WorkflowFunctionalityCheck:
        """
        Check if workflow is fully functional

        If not, MARVIN roasts it.
        JARVIS follows up and repairs.
        """
        check_id = f"check_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()

        self.logger.info(f"🔍 Checking functionality: {workflow_name} ({workflow_id})")

        # Check functionality
        status, faults = self._check_functionality(workflow_id, workflow_name)

        check = WorkflowFunctionalityCheck(
            check_id=check_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            status=status,
            checked_at=now,
            faults_identified=faults
        )

        # If not fully functional, MARVIN roasts it
        if status != FunctionalityStatus.FULLY_FUNCTIONAL:
            self.logger.warning(f"⚠️ Workflow {workflow_name} is not fully functional: {status.value}")

            # MARVIN roasts it
            if self.marvin_roaster:
                roast = self.marvin_roaster.granular_roast(
                    f"{workflow_name} functionality",
                    context={
                        "workflow_id": workflow_id,
                        "workflow_name": workflow_name,
                        "status": status.value,
                        "faults": faults
                    }
                )
                check.roasted = True
                check.roast_id = roast.roast_id
                check.faults_identified.extend([f.specific_fault for f in roast.faults])

                self.logger.info(f"🔥 MARVIN roasted {workflow_name}: {len(roast.faults)} faults")

                # JARVIS follows up and repairs
                if self.jarvis_followup:
                    followups = self.jarvis_followup.process_marvin_roast(roast.roast_id)

                    # Process all faults
                    result = self.jarvis_followup.process_all_marvin_faults()

                    self.logger.info(f"🔧 JARVIS processing {len(followups)} follow-ups")

                    # Create helpdesk ticket and git commit
                    if self.git_helpdesk and followups:
                        for followup in followups:
                            problem = self.git_helpdesk.create_problem_from_marvin_fault(
                                followup.fault.fault_id,
                                followup.fault.description,
                                followup.fault.specific_fault
                            )

                            # Create comprehensive ticket description
                            ticket_description = self._create_comprehensive_ticket_description(
                                workflow_name,
                                followup.fault,
                                roast
                            )

                            problem.description = ticket_description
                            check.helpdesk_ticket_id = problem.problem_id
                            check.git_commit_hash = problem.git_commit_hash

                            self.logger.info(f"📝 Created helpdesk ticket: {problem.problem_id}")

        self._save_check(check)

        return check

    def _check_functionality(
        self,
        workflow_id: str,
        workflow_name: str
    ) -> tuple[FunctionalityStatus, List[str]]:
        """Check workflow functionality"""
        faults = []

        # Check if workflow file exists
        workflow_file = self.project_root / "scripts" / "python" / f"{workflow_name.lower()}.py"
        if not workflow_file.exists():
            faults.append(f"Workflow file not found: {workflow_file}")
            return FunctionalityStatus.NON_FUNCTIONAL, faults

        # Check if workflow class exists
        try:
            # Try to import and check
            import importlib.util
            spec = importlib.util.spec_from_file_location(workflow_name, workflow_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for workflow class
                workflow_class = getattr(module, workflow_name, None)
                if not workflow_class:
                    faults.append(f"Workflow class not found: {workflow_name}")
                    return FunctionalityStatus.NON_FUNCTIONAL, faults

                # Check for required methods
                required_methods = ['execute', 'validate', 'run']
                missing_methods = [
                    method for method in required_methods
                    if not hasattr(workflow_class, method)
                ]

                if missing_methods:
                    faults.append(f"Missing required methods: {', '.join(missing_methods)}")
                    return FunctionalityStatus.PARTIALLY_FUNCTIONAL, faults
        except Exception as e:
            faults.append(f"Error checking workflow: {e}")
            return FunctionalityStatus.UNKNOWN, faults

        # If no faults, fully functional
        if not faults:
            return FunctionalityStatus.FULLY_FUNCTIONAL, []

        # Determine status based on faults
        if any("not found" in f.lower() or "missing" in f.lower() for f in faults):
            return FunctionalityStatus.NON_FUNCTIONAL, faults
        else:
            return FunctionalityStatus.PARTIALLY_FUNCTIONAL, faults

    def _create_comprehensive_ticket_description(
        self,
        workflow_name: str,
        fault,
        roast
    ) -> str:
        """Create comprehensive, robust descriptive ticket description"""
        description = f"""
# Workflow Functionality Issue: {workflow_name}

## Summary
{workflow_name} is not fully functional. MARVIN identified {len(roast.faults)} faults.

## Fault Details
**Fault ID**: {fault.fault_id}
**Granularity**: {fault.granularity_level.value}
**Category**: {fault.category.value}
**Specific Fault**: {fault.specific_fault}
**Root Cause**: {fault.root_cause or 'Unknown'}
**Impact**: {fault.impact}

## Evidence
{chr(10).join(f'- {evidence}' for evidence in fault.evidence)}

## All Faults Identified
{chr(10).join(f'{i+1}. [{f.granularity_level.value}] {f.specific_fault}' for i, f in enumerate(roast.faults))}

## Action Required
JARVIS will follow up on each fault and repair.

## Status
- MARVIN Roast: Complete
- JARVIS Follow-Up: In Progress
- Repair: Pending

## Related
- Roast ID: {roast.roast_id}
- Total Faults: {roast.total_faults}
- Macro: {roast.macro_faults}, Meso: {roast.meso_faults}, Micro: {roast.micro_faults}, Atomic: {roast.atomic_faults}
"""
        return description.strip()

    def check_all_workflows(self) -> Dict[str, Any]:
        """Check all workflows for functionality"""
        # Find all workflow files
        workflow_dir = self.project_root / "scripts" / "python"
        workflow_files = list(workflow_dir.glob("*workflow*.py"))

        results = {
            "fully_functional": [],
            "partially_functional": [],
            "non_functional": [],
            "unknown": []
        }

        for workflow_file in workflow_files:
            workflow_name = workflow_file.stem
            workflow_id = workflow_name

            check = self.check_workflow_functionality(workflow_id, workflow_name)

            if check.status == FunctionalityStatus.FULLY_FUNCTIONAL:
                results["fully_functional"].append(workflow_name)
            elif check.status == FunctionalityStatus.PARTIALLY_FUNCTIONAL:
                results["partially_functional"].append(workflow_name)
            elif check.status == FunctionalityStatus.NON_FUNCTIONAL:
                results["non_functional"].append(workflow_name)
            else:
                results["unknown"].append(workflow_name)

        return results


def main():
    """Main execution for testing"""
    framework = WorkflowFunctionalityFramework()

    print("=" * 80)
    print("🔧 WORKFLOW FUNCTIONALITY FRAMEWORK")
    print("=" * 80)

    # Check all workflows
    results = framework.check_all_workflows()

    print(f"\n📊 Functionality Results:")
    print(f"   Fully Functional: {len(results['fully_functional'])}")
    print(f"   Partially Functional: {len(results['partially_functional'])}")
    print(f"   Non-Functional: {len(results['non_functional'])}")
    print(f"   Unknown: {len(results['unknown'])}")


if __name__ == "__main__":



    main()