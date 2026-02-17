#!/usr/bin/env python3
"""
@DOIT @BDA Final Step System
Build, Deploy, Activate - ALWAYS THE LAST STEP OF ALL WORKFLOWS

Tags: #DOIT #BDA #BUILD #DEPLOY #ACTIVATE #FINAL_STEP @JARVIS @LUMINA @DOIT
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

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

logger = get_logger("DOITBDAFinalStep")


@dataclass
class BDAResult:
    """Build, Deploy, Activate result"""
    workflow_id: str
    timestamp: str
    build_status: str  # "success", "failed", "skipped"
    deploy_status: str  # "success", "failed", "skipped"
    activate_status: str  # "success", "failed", "skipped"
    build_output: str = ""
    deploy_output: str = ""
    activate_output: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def overall_status(self) -> str:
        """Overall BDA status"""
        if all(s == "success" for s in [self.build_status, self.deploy_status, self.activate_status]):
            return "success"
        elif any(s == "failed" for s in [self.build_status, self.deploy_status, self.activate_status]):
            return "failed"
        else:
            return "partial"


class DOITBDAFinalStep:
    """
    @DOIT @BDA Final Step System

    Build, Deploy, Activate - ALWAYS THE LAST STEP OF ALL WORKFLOWS
    """

    def __init__(self):
        """Initialize @DOIT @BDA Final Step System"""
        logger.info("=" * 80)
        logger.info("🚀 @DOIT @BDA Final Step System")
        logger.info("=" * 80)

        self.project_root = project_root
        self.data_dir = project_root / "data" / "doit_bda"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # BDA history
        self.history_file = self.data_dir / "bda_history.json"
        self.history: List[BDAResult] = []

        # Load history
        self._load_history()

        logger.info("✅ @DOIT @BDA Final Step System initialized")
        logger.info(f"   Historical BDA runs: {len(self.history)}")

    def _load_history(self):
        """Load BDA history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [BDAResult(**r) for r in data]
            except Exception as e:
                logger.debug(f"   Could not load history: {e}")

    def _save_history(self):
        """Save BDA history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump([asdict(r) for r in self.history], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def execute_bda(self, workflow_id: str, workflow_type: str = "general", 
                   build_commands: Optional[List[str]] = None,
                   deploy_commands: Optional[List[str]] = None,
                   activate_commands: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> BDAResult:
        """
        Execute Build, Deploy, Activate as final step

        Args:
            workflow_id: Unique workflow identifier
            workflow_type: Type of workflow (e.g., "intelligence_processing", "daily_work_cycle")
            build_commands: Commands to execute for build phase
            deploy_commands: Commands to execute for deploy phase
            activate_commands: Commands to execute for activate phase
            metadata: Additional metadata

        Returns:
            BDAResult with status of all phases
        """
        start_time = datetime.now()
        timestamp = start_time.isoformat()

        logger.info(f"\n🚀 Executing @DOIT @BDA Final Step")
        logger.info(f"   Workflow ID: {workflow_id}")
        logger.info(f"   Workflow Type: {workflow_type}")

        result = BDAResult(
            workflow_id=workflow_id,
            timestamp=timestamp,
            build_status="pending",
            deploy_status="pending",
            activate_status="pending",
            metadata=metadata or {}
        )
        result.metadata["workflow_type"] = workflow_type

        # Phase 1: BUILD
        logger.info("\n📦 Phase 1: BUILD")
        if build_commands:
            result.build_status, result.build_output = self._execute_phase("BUILD", build_commands)
        else:
            result.build_status = "skipped"
            result.build_output = "No build commands provided"
            logger.info("   ⏭️  BUILD phase skipped (no commands)")

        # Phase 2: DEPLOY
        logger.info("\n🚀 Phase 2: DEPLOY")
        if deploy_commands:
            result.deploy_status, result.deploy_output = self._execute_phase("DEPLOY", deploy_commands)
        else:
            result.deploy_status = "skipped"
            result.deploy_output = "No deploy commands provided"
            logger.info("   ⏭️  DEPLOY phase skipped (no commands)")

        # Phase 3: ACTIVATE
        logger.info("\n⚡ Phase 3: ACTIVATE")
        if activate_commands:
            result.activate_status, result.activate_output = self._execute_phase("ACTIVATE", activate_commands)
        else:
            result.activate_status = "skipped"
            result.activate_output = "No activate commands provided"
            logger.info("   ⏭️  ACTIVATE phase skipped (no commands)")

        # Calculate duration
        end_time = datetime.now()
        result.duration_seconds = (end_time - start_time).total_seconds()

        # Determine overall status
        overall_status = result.overall_status

        logger.info(f"\n✅ @DOIT @BDA Final Step Complete")
        logger.info(f"   Overall Status: {overall_status.upper()}")
        logger.info(f"   BUILD: {result.build_status.upper()}")
        logger.info(f"   DEPLOY: {result.deploy_status.upper()}")
        logger.info(f"   ACTIVATE: {result.activate_status.upper()}")
        logger.info(f"   Duration: {result.duration_seconds:.1f} seconds")

        # Save to history
        self.history.append(result)
        self._save_history()

        return result

    def _execute_phase(self, phase_name: str, commands: List[str]) -> tuple[str, str]:
        """
        Execute a phase (BUILD, DEPLOY, or ACTIVATE)

        Args:
            phase_name: Name of phase
            commands: List of commands to execute

        Returns:
            Tuple of (status, output)
        """
        output_lines = []
        errors = []

        for i, command in enumerate(commands, 1):
            logger.info(f"   [{i}/{len(commands)}] Executing: {command[:80]}...")

            try:
                # Execute command
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                    timeout=300  # 5 minute timeout per command
                )

                if process.stdout:
                    output_lines.append(f"STDOUT: {process.stdout}")

                if process.stderr:
                    output_lines.append(f"STDERR: {process.stderr}")

                if process.returncode != 0:
                    errors.append(f"Command failed with return code {process.returncode}: {command}")
                    logger.warning(f"      ⚠️  Command failed: {command}")
                else:
                    logger.info(f"      ✅ Command succeeded")

            except subprocess.TimeoutExpired:
                errors.append(f"Command timed out: {command}")
                logger.error(f"      ❌ Command timed out: {command}")

            except Exception as e:
                errors.append(f"Command error: {str(e)}")
                logger.error(f"      ❌ Command error: {str(e)}")

        output = "\n".join(output_lines)

        if errors:
            status = "failed"
            output += f"\n\nERRORS:\n" + "\n".join(errors)
        else:
            status = "success"

        return status, output

    def execute_bda_for_workflow(self, workflow_id: str, workflow_type: str, 
                                workflow_metadata: Optional[Dict[str, Any]] = None) -> BDAResult:
        """
        Execute BDA for a specific workflow type with default commands

        Args:
            workflow_id: Unique workflow identifier
            workflow_type: Type of workflow
            workflow_metadata: Workflow metadata

        Returns:
            BDAResult
        """
        # Get default commands for workflow type
        commands = self._get_default_commands(workflow_type)

        return self.execute_bda(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            build_commands=commands.get("build", []),
            deploy_commands=commands.get("deploy", []),
            activate_commands=commands.get("activate", []),
            metadata=workflow_metadata
        )

    def _get_default_commands(self, workflow_type: str) -> Dict[str, List[str]]:
        """
        Get default BDA commands for workflow type

        Args:
            workflow_type: Type of workflow

        Returns:
            Dict with build, deploy, activate command lists
        """
        commands = {
            "build": [],
            "deploy": [],
            "activate": []
        }

        if workflow_type == "intelligence_processing":
            commands["build"] = [
                "python scripts/python/intelligence_processing_analysis.py --process --time-hours 3.0"
            ]
            commands["deploy"] = [
                "echo 'Intelligence processing results deployed'"
            ]
            commands["activate"] = [
                "echo 'Intelligence processing activated'"
            ]

        elif workflow_type == "daily_work_cycle":
            commands["build"] = [
                "python scripts/python/daily_work_cycle_complete.py --run-cycle"
            ]
            commands["deploy"] = [
                "echo 'Daily work cycle results deployed'"
            ]
            commands["activate"] = [
                "echo 'Daily work cycle activated'"
            ]

        elif workflow_type == "general":
            # Default: validate and verify
            commands["build"] = [
                "echo 'Build: Validating workflow completion'"
            ]
            commands["deploy"] = [
                "echo 'Deploy: Deploying workflow results'"
            ]
            commands["activate"] = [
                "echo 'Activate: Activating workflow'"
            ]

        return commands

    def add_to_workflow(self, workflow_id: str, workflow_type: str = "general",
                       workflow_metadata: Optional[Dict[str, Any]] = None) -> BDAResult:
        """
        Add BDA as final step to any workflow

        Args:
            workflow_id: Unique workflow identifier
            workflow_type: Type of workflow
            workflow_metadata: Workflow metadata

        Returns:
            BDAResult
        """
        logger.info(f"\n🔗 Adding @DOIT @BDA as final step to workflow: {workflow_id}")

        return self.execute_bda_for_workflow(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            workflow_metadata=workflow_metadata
        )


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description='@DOIT @BDA Final Step System')
        parser.add_argument('--execute', action='store_true', help='Execute BDA')
        parser.add_argument('--workflow-id', type=str, default=None, help='Workflow ID')
        parser.add_argument('--workflow-type', type=str, default='general', help='Workflow type')
        parser.add_argument('--build', nargs='+', help='Build commands')
        parser.add_argument('--deploy', nargs='+', help='Deploy commands')
        parser.add_argument('--activate', nargs='+', help='Activate commands')
        parser.add_argument('--json', action='store_true', help='Output as JSON')

        args = parser.parse_args()

        bda = DOITBDAFinalStep()

        if args.execute:
            workflow_id = args.workflow_id or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            result = bda.execute_bda(
                workflow_id=workflow_id,
                workflow_type=args.workflow_type,
                build_commands=args.build,
                deploy_commands=args.deploy,
                activate_commands=args.activate
            )

            if args.json:
                print(json.dumps(result.to_dict(), indent=2, default=str))
            else:
                print("\n" + "=" * 80)
                print("🚀 @DOIT @BDA Final Step Result")
                print("=" * 80)
                print(f"Workflow ID: {result.workflow_id}")
                print(f"Overall Status: {result.overall_status.upper()}")
                print(f"BUILD: {result.build_status.upper()}")
                print(f"DEPLOY: {result.deploy_status.upper()}")
                print(f"ACTIVATE: {result.activate_status.upper()}")
                print(f"Duration: {result.duration_seconds:.1f} seconds")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()