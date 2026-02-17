#!/usr/bin/env python3
"""
JARVIS Workflow CPU Manager
Manages workflow chain capacity like a CPU - 4 cores normal, 5 with F2F/NITRO boost!

@JARVIS @WORKFLOW @CPU @PENTIUM @F2F @NITRO @BOOST
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWorkflowCPU")


class CPUMode(Enum):
    """CPU modes"""
    NORMAL = "normal"  # 4 cores (4 workflow chains)
    F2F_NITRO = "f2f_nitro"  # 5 cores (5 workflow chains) - Fast & Furious Nitrous Oxide boost!


class WorkflowChainCore:
    """Represents a CPU core running a workflow chain"""
    def __init__(self, core_id: int, workflow_id: str, workflow_name: str):
        self.core_id = core_id
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.started_at = datetime.now()
        self.status = "running"
        self.cpu_usage = 0.0  # 0-100%
        self.memory_usage = 0.0  # 0-100%

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "core_id": self.core_id,
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "started_at": self.started_at.isoformat(),
            "status": self.status,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "runtime_seconds": (datetime.now() - self.started_at).total_seconds()
        }


class JARVISWorkflowCPU:
    """
    JARVIS Workflow CPU Manager

    Manages workflow chains like a CPU:
    - Normal mode: 4 cores (4 concurrent workflow chains)
    - F2F/NITRO mode: 5 cores (5 concurrent workflow chains) - Fast & Furious boost!

    Like a Pentium chip, but for workflows! 🚗💨
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow CPU"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # CPU configuration
        self.normal_cores = 4  # Standard capacity
        self.nitro_cores = 5  # F2F/NITRO boost capacity
        self.current_mode = CPUMode.NORMAL
        self.nitro_active = False
        self.nitro_expires_at: Optional[datetime] = None

        # Active cores (workflow chains)
        self.active_cores: Dict[int, WorkflowChainCore] = {}
        self.core_counter = 0

        # CPU stats
        self.total_chains_executed = 0
        self.total_nitro_boosts = 0
        self.total_runtime_seconds = 0.0

        # Output directory
        self.output_dir = self.project_root / "data" / "workflow_cpu"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("🖥️  JARVIS WORKFLOW CPU MANAGER")
        logger.info("   Like a Pentium Chip, but for Workflows!")
        logger.info("   Normal: 4 cores | F2F/NITRO: 5 cores")
        logger.info("=" * 70)
        logger.info("")

    def get_max_cores(self) -> int:
        """Get maximum cores based on current mode"""
        if self.current_mode == CPUMode.F2F_NITRO and self.nitro_active:
            return self.nitro_cores
        return self.normal_cores

    def get_available_cores(self) -> int:
        """Get number of available cores"""
        return self.get_max_cores() - len(self.active_cores)

    def can_allocate_chain(self) -> bool:
        """Check if we can allocate a new workflow chain"""
        return len(self.active_cores) < self.get_max_cores()

    def activate_nitro(self, duration_seconds: int = 300) -> Dict[str, Any]:
        """
        Activate F2F/NITRO boost mode!

        Fast & Furious Nitrous Oxide boost - unlocks 5th core!

        Args:
            duration_seconds: How long nitro boost lasts (default: 5 minutes)

        Returns:
            Activation result
        """
        logger.info("=" * 70)
        logger.info("🚗💨 ACTIVATING F2F/NITRO BOOST MODE!")
        logger.info("   Fast & Furious Nitrous Oxide - 5th Core Unlocked!")
        logger.info("=" * 70)
        logger.info("")

        if self.nitro_active:
            logger.info("⚠️  NITRO already active - extending duration")
        else:
            self.total_nitro_boosts += 1
            logger.info("✅ NITRO ACTIVATED - 5th core now available!")

        self.current_mode = CPUMode.F2F_NITRO
        self.nitro_active = True
        self.nitro_expires_at = datetime.now().timestamp() + duration_seconds

        logger.info(f"   Duration: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
        logger.info(f"   Expires at: {datetime.fromtimestamp(self.nitro_expires_at).strftime('%H:%M:%S')}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("💨 NITRO BOOST ACTIVE - MAX CORES: 5")
        logger.info("=" * 70)

        return {
            "status": "activated",
            "mode": "f2f_nitro",
            "max_cores": 5,
            "expires_at": datetime.fromtimestamp(self.nitro_expires_at).isoformat(),
            "duration_seconds": duration_seconds
        }

    def check_nitro_status(self) -> Dict[str, Any]:
        """Check if nitro is still active"""
        if not self.nitro_active:
            return {
                "active": False,
                "mode": "normal",
                "max_cores": 4
            }

        current_time = datetime.now().timestamp()
        if current_time >= self.nitro_expires_at:
            # Nitro expired
            self.nitro_active = False
            self.current_mode = CPUMode.NORMAL

            # If we have 5 cores active, we need to handle overflow
            if len(self.active_cores) > 4:
                logger.warning("⚠️  NITRO expired but 5 cores still active - will complete current chains")

            return {
                "active": False,
                "expired": True,
                "mode": "normal",
                "max_cores": 4,
                "message": "NITRO boost expired - back to normal mode"
            }

        remaining = self.nitro_expires_at - current_time
        return {
            "active": True,
            "mode": "f2f_nitro",
            "max_cores": 5,
            "remaining_seconds": int(remaining),
            "expires_at": datetime.fromtimestamp(self.nitro_expires_at).isoformat()
        }

    def allocate_core(self, workflow_id: str, workflow_name: str) -> Optional[WorkflowChainCore]:
        """
        Allocate a CPU core for a workflow chain

        Args:
            workflow_id: Workflow identifier
            workflow_name: Workflow name

        Returns:
            WorkflowChainCore if allocated, None if no cores available
        """
        # Check nitro status
        nitro_status = self.check_nitro_status()

        # Check if we can allocate
        if not self.can_allocate_chain():
            logger.warning(f"⚠️  Cannot allocate core for {workflow_name} - all cores busy")
            logger.warning(f"   Active cores: {len(self.active_cores)}/{self.get_max_cores()}")
            logger.warning(f"   Mode: {nitro_status['mode']} ({nitro_status['max_cores']} max cores)")
            return None

        # Allocate core
        self.core_counter += 1
        core = WorkflowChainCore(
            core_id=self.core_counter,
            workflow_id=workflow_id,
            workflow_name=workflow_name
        )

        self.active_cores[self.core_counter] = core

        logger.info(f"✅ Allocated Core {core.core_id} for: {workflow_name}")
        logger.info(f"   Active cores: {len(self.active_cores)}/{self.get_max_cores()}")
        logger.info(f"   Mode: {nitro_status['mode']} ({nitro_status['max_cores']} max cores)")

        return core

    def release_core(self, core_id: int) -> bool:
        """
        Release a CPU core

        Args:
            core_id: Core ID to release

        Returns:
            True if released, False if not found
        """
        if core_id not in self.active_cores:
            logger.warning(f"⚠️  Core {core_id} not found in active cores")
            return False

        core = self.active_cores[core_id]
        runtime = (datetime.now() - core.started_at).total_seconds()

        self.total_chains_executed += 1
        self.total_runtime_seconds += runtime

        del self.active_cores[core_id]

        logger.info(f"✅ Released Core {core_id} ({core.workflow_name})")
        logger.info(f"   Runtime: {runtime:.1f} seconds")
        logger.info(f"   Active cores: {len(self.active_cores)}/{self.get_max_cores()}")

        return True

    def get_cpu_status(self) -> Dict[str, Any]:
        """Get current CPU status"""
        nitro_status = self.check_nitro_status()

        active_workflows = [
            core.to_dict() for core in self.active_cores.values()
        ]

        return {
            "cpu_mode": nitro_status["mode"],
            "max_cores": nitro_status["max_cores"],
            "active_cores": len(self.active_cores),
            "available_cores": self.get_available_cores(),
            "nitro_active": nitro_status.get("active", False),
            "nitro_remaining_seconds": nitro_status.get("remaining_seconds"),
            "active_workflows": active_workflows,
            "stats": {
                "total_chains_executed": self.total_chains_executed,
                "total_nitro_boosts": self.total_nitro_boosts,
                "total_runtime_seconds": self.total_runtime_seconds,
                "average_runtime_seconds": (
                    self.total_runtime_seconds / self.total_chains_executed
                    if self.total_chains_executed > 0 else 0
                )
            }
        }

    def save_cpu_status(self) -> None:
        """Save CPU status to file"""
        try:
            status = self.get_cpu_status()
            filename = self.output_dir / f"cpu_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str)
            logger.info(f"✅ CPU status saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save CPU status: {e}")


def main():
    """Main execution - demonstrate CPU manager"""
    print("=" * 70)
    print("🖥️  JARVIS WORKFLOW CPU MANAGER")
    print("   Like a Pentium Chip, but for Workflows!")
    print("=" * 70)
    print()

    cpu = JARVISWorkflowCPU()

    # Show initial status
    print("📊 INITIAL CPU STATUS:")
    print("-" * 70)
    status = cpu.get_cpu_status()
    print(f"Mode: {status['cpu_mode']}")
    print(f"Max Cores: {status['max_cores']}")
    print(f"Active Cores: {status['active_cores']}")
    print(f"Available Cores: {status['available_cores']}")
    print()

    # Allocate some cores
    print("🔧 ALLOCATING CORES:")
    print("-" * 70)
    core1 = cpu.allocate_core("workflow_1", "Financial Premium Package")
    core2 = cpu.allocate_core("workflow_2", "RoamWise Stargate Portal")
    core3 = cpu.allocate_core("workflow_3", "CIAB Deployment")
    core4 = cpu.allocate_core("workflow_4", "Deep System Validation")
    core5 = cpu.allocate_core("workflow_5", "SYPHON Intelligence")  # Should fail in normal mode
    print()

    # Activate NITRO
    print("🚗💨 ACTIVATING NITRO:")
    print("-" * 70)
    cpu.activate_nitro(duration_seconds=300)
    print()

    # Try allocating 5th core again
    print("🔧 ALLOCATING 5TH CORE (WITH NITRO):")
    print("-" * 70)
    core5 = cpu.allocate_core("workflow_5", "SYPHON Intelligence")
    print()

    # Show final status
    print("📊 FINAL CPU STATUS:")
    print("-" * 70)
    status = cpu.get_cpu_status()
    print(f"Mode: {status['cpu_mode']}")
    print(f"Max Cores: {status['max_cores']}")
    print(f"Active Cores: {status['active_cores']}")
    print(f"Available Cores: {status['available_cores']}")
    print(f"NITRO Active: {status['nitro_active']}")
    if status['nitro_active']:
        print(f"NITRO Remaining: {status['nitro_remaining_seconds']} seconds")
    print()

    # Save status
    cpu.save_cpu_status()

    print("=" * 70)
    print("✅ CPU MANAGER DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":


    main()