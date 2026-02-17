#!/usr/bin/env python3
"""
Workflow Mantra System

Manages and applies workflow stage mantras:
- Development: "DOCUMENT, DOCUMENT, DOCUMENT"
- IT/Testing: "DELEGATE, DELEGATE, DELEGATE"

All mantras are CORE MORALS/VALUES/ETHICS

Tags: #mantras #workflow #core_values #ethics #document #delegate
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("WorkflowMantraSystem")


class WorkflowStage(Enum):
    """Workflow stage"""
    DEVELOPMENT = "development"
    IT_TESTING = "it_testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


@dataclass
class Mantra:
    """Workflow stage mantra"""
    stage: WorkflowStage
    mantra: str
    description: str
    core_value: str  # The moral/ethical principle
    principles: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value,
            "mantra": self.mantra,
            "description": self.description,
            "core_value": self.core_value,
            "principles": self.principles
        }


class WorkflowMantraSystem:
    """
    Workflow Mantra System

    Manages mantras for different workflow stages.
    All mantras are CORE MORALS/VALUES/ETHICS.
    """

    def __init__(self):
        """Initialize mantra system"""
        self.mantras: Dict[WorkflowStage, Mantra] = {}
        self._initialize_mantras()

        logger.info("=" * 80)
        logger.info("📜 WORKFLOW MANTRA SYSTEM")
        logger.info("=" * 80)
        logger.info("   All mantras are CORE MORALS/VALUES/ETHICS")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_mantras(self):
        """Initialize workflow stage mantras"""
        # Development Stage Mantra
        self.mantras[WorkflowStage.DEVELOPMENT] = Mantra(
            stage=WorkflowStage.DEVELOPMENT,
            mantra="DOCUMENT, DOCUMENT, DOCUMENT",
            description="Comprehensive documentation at every step",
            core_value="Knowledge sharing, transparency, accountability",
            principles=[
                "Logging = Documenting",
                "Code comments and docstrings",
                "README files and guides",
                "Knowledge preservation",
                "Transparency in all work"
            ]
        )

        # IT/Testing Stage Mantra
        self.mantras[WorkflowStage.IT_TESTING] = Mantra(
            stage=WorkflowStage.IT_TESTING,
            mantra="DELEGATE, DELEGATE, DELEGATE",
            description="Delegate tasks to systems and automation",
            core_value="Trust, efficiency, scalability, responsibility",
            principles=[
                "Automate repetitive tasks",
                "System testing and validation",
                "Task distribution",
                "Trust in automated processes",
                "Scalable solutions"
            ]
        )

        logger.info("✅ Mantras initialized:")
        logger.info(f"   Development: {self.mantras[WorkflowStage.DEVELOPMENT].mantra}")
        logger.info(f"   IT/Testing: {self.mantras[WorkflowStage.IT_TESTING].mantra}")
        logger.info("")

    def get_mantra(self, stage: WorkflowStage) -> Optional[Mantra]:
        """Get mantra for a workflow stage"""
        return self.mantras.get(stage)

    def apply_mantra(self, stage: WorkflowStage, context: Dict[str, Any] = None):
        """Apply mantra principles to current work"""
        mantra = self.get_mantra(stage)
        if not mantra:
            logger.warning(f"No mantra defined for stage: {stage.value}")
            return

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"📜 APPLYING MANTRA: {stage.value.upper()}")
        logger.info("=" * 80)
        logger.info(f"   Mantra: {mantra.mantra}")
        logger.info(f"   Core Value: {mantra.core_value}")
        logger.info("")
        logger.info("   Principles:")
        for principle in mantra.principles:
            logger.info(f"      • {principle}")
        logger.info("")
        logger.info("=" * 80)
        logger.info("")

    def get_all_mantras(self) -> List[Mantra]:
        """Get all mantras"""
        return list(self.mantras.values())

    def print_mantras(self):
        """Print all mantras"""
        print("\n" + "=" * 80)
        print("📜 WORKFLOW STAGE MANTRAS")
        print("=" * 80)
        print("   All mantras are CORE MORALS/VALUES/ETHICS")
        print("")

        for stage, mantra in self.mantras.items():
            print(f"Stage: {stage.value.upper()}")
            print(f"   Mantra: {mantra.mantra}")
            print(f"   Description: {mantra.description}")
            print(f"   Core Value: {mantra.core_value}")
            print(f"   Principles:")
            for principle in mantra.principles:
                print(f"      • {principle}")
            print("")

        print("=" * 80)
        print("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Mantra System")
    parser.add_argument('--stage', type=str, choices=['development', 'it_testing'],
                       help='Apply mantra for specific stage')
    parser.add_argument('--list', action='store_true', help='List all mantras')

    args = parser.parse_args()

    system = WorkflowMantraSystem()

    if args.stage:
        stage_map = {
            'development': WorkflowStage.DEVELOPMENT,
            'it_testing': WorkflowStage.IT_TESTING
        }
        system.apply_mantra(stage_map[args.stage])
    elif args.list:
        system.print_mantras()
    else:
        system.print_mantras()


if __name__ == "__main__":


    main()