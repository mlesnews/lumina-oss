#!/usr/bin/env python3
"""
VA Resource Management System

Manages resources (CPU, memory, network) for VAs with allocation, monitoring, and optimization.

Tags: #VIRTUAL_ASSISTANT #RESOURCE_MANAGEMENT #OPTIMIZATION @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VAResourceManagement")


@dataclass
class ResourceAllocation:
    """Resource allocation for a VA"""
    va_id: str
    cpu_limit: float = 1.0  # CPU cores
    memory_limit: float = 1024.0  # MB
    network_limit: float = 100.0  # Mbps
    storage_limit: float = 1000.0  # MB
    api_quota: int = 1000  # API calls per hour

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ResourceUsage:
    """Current resource usage"""
    va_id: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_usage: float = 0.0
    storage_usage: float = 0.0
    api_calls: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class VAResourceManagement:
    """
    VA Resource Management System

    Features:
    - Resource allocation
    - Resource limits
    - Resource monitoring
    - Auto-scaling
    - Resource optimization
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize resource management system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Resource allocations
        self.allocations: Dict[str, ResourceAllocation] = {}

        # Resource usage
        self.usage: Dict[str, ResourceUsage] = {}

        # Auto-scaling enabled
        self.auto_scaling_enabled = True

        # Initialize allocations
        self._initialize_allocations()

        # Data persistence
        self.data_dir = project_root / "data" / "va_resource_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("⚙️  VA RESOURCE MANAGEMENT SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Resource management active")
        logger.info("=" * 80)

    def _initialize_allocations(self):
        """Initialize resource allocations for all VAs"""
        for va in self.vas:
            # Default allocations based on VA type
            if va.character_id == "jarvis_va":
                allocation = ResourceAllocation(
                    va_id=va.character_id,
                    cpu_limit=2.0,
                    memory_limit=2048.0,
                    network_limit=200.0,
                    api_quota=5000
                )
            elif va.character_id == "ace":
                allocation = ResourceAllocation(
                    va_id=va.character_id,
                    cpu_limit=1.5,
                    memory_limit=1536.0,
                    network_limit=150.0,
                    api_quota=3000
                )
            else:
                allocation = ResourceAllocation(
                    va_id=va.character_id,
                    cpu_limit=1.0,
                    memory_limit=1024.0,
                    network_limit=100.0,
                    api_quota=1000
                )

            self.allocations[va.character_id] = allocation
            self.usage[va.character_id] = ResourceUsage(va_id=va.character_id)

            logger.info(f"⚙️  Allocated resources for {va.name}")

    def allocate_resources(self, va_id: str, resources: Dict[str, Any]) -> ResourceAllocation:
        """Allocate resources to a VA"""
        va = self.registry.get_character(va_id)
        if not va or va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            raise ValueError(f"VA {va_id} not found")

        allocation = self.allocations.get(va_id)
        if not allocation:
            allocation = ResourceAllocation(va_id=va_id)

        # Update allocation
        if "cpu_limit" in resources:
            allocation.cpu_limit = resources["cpu_limit"]
        if "memory_limit" in resources:
            allocation.memory_limit = resources["memory_limit"]
        if "network_limit" in resources:
            allocation.network_limit = resources["network_limit"]
        if "storage_limit" in resources:
            allocation.storage_limit = resources["storage_limit"]
        if "api_quota" in resources:
            allocation.api_quota = resources["api_quota"]

        self.allocations[va_id] = allocation
        logger.info(f"⚙️  Updated resource allocation for {va_id}")
        return allocation

    def set_limits(self, va_id: str, limits: Dict[str, Any]):
        """Set resource limits"""
        self.allocate_resources(va_id, limits)

    def monitor_resources(self, va_id: str) -> ResourceUsage:
        """Monitor current resource usage"""
        usage = self.usage.get(va_id)
        if not usage:
            usage = ResourceUsage(va_id=va_id)
            self.usage[va_id] = usage

        # Simulate resource monitoring (in real implementation, would query actual usage)
        # For now, return current usage

        usage.timestamp = datetime.now().isoformat()
        return usage

    def update_usage(self, va_id: str, cpu: Optional[float] = None,
                    memory: Optional[float] = None,
                    network: Optional[float] = None,
                    storage: Optional[float] = None,
                    api_calls: Optional[int] = None):
        """Update resource usage"""
        usage = self.usage.get(va_id)
        if not usage:
            usage = ResourceUsage(va_id=va_id)
            self.usage[va_id] = usage

        if cpu is not None:
            usage.cpu_usage = cpu
        if memory is not None:
            usage.memory_usage = memory
        if network is not None:
            usage.network_usage = network
        if storage is not None:
            usage.storage_usage = storage
        if api_calls is not None:
            usage.api_calls = api_calls

        usage.timestamp = datetime.now().isoformat()

    def auto_scale(self, va_id: str, demand: float) -> bool:
        """Auto-scale resources based on demand"""
        if not self.auto_scaling_enabled:
            return False

        allocation = self.allocations.get(va_id)
        if not allocation:
            return False

        # Scale based on demand (simplified)
        if demand > 0.8:  # High demand
            # Increase resources
            allocation.cpu_limit *= 1.2
            allocation.memory_limit *= 1.2
            logger.info(f"📈 Auto-scaled up {va_id} (demand: {demand:.1%})")
            return True
        elif demand < 0.3:  # Low demand
            # Decrease resources
            allocation.cpu_limit *= 0.9
            allocation.memory_limit *= 0.9
            logger.info(f"📉 Auto-scaled down {va_id} (demand: {demand:.1%})")
            return True

        return False

    def optimize_resources(self, all_vas: bool = True) -> Dict[str, Any]:
        """Optimize resource allocation across VAs"""
        optimization = {
            "optimizations": [],
            "total_cpu": 0.0,
            "total_memory": 0.0
        }

        va_ids = [va.character_id for va in self.vas] if all_vas else list(self.allocations.keys())

        for va_id in va_ids:
            allocation = self.allocations.get(va_id)
            usage = self.usage.get(va_id)

            if not allocation or not usage:
                continue

            # Check for over-allocation
            cpu_utilization = usage.cpu_usage / allocation.cpu_limit if allocation.cpu_limit > 0 else 0
            memory_utilization = usage.memory_usage / allocation.memory_limit if allocation.memory_limit > 0 else 0

            if cpu_utilization < 0.3 and memory_utilization < 0.3:
                # Under-utilized, can reduce
                optimization["optimizations"].append({
                    "va_id": va_id,
                    "action": "reduce",
                    "reason": "under-utilized"
                })

            optimization["total_cpu"] += allocation.cpu_limit
            optimization["total_memory"] += allocation.memory_limit

        if optimization["optimizations"]:
            logger.info(f"⚙️  Optimization suggestions: {len(optimization['optimizations'])}")

        return optimization

    def get_resource_status(self, va_id: Optional[str] = None) -> Dict[str, Any]:
        """Get resource status"""
        if va_id:
            allocation = self.allocations.get(va_id)
            usage = self.usage.get(va_id)

            if not allocation or not usage:
                return {}

            return {
                "va_id": va_id,
                "allocation": allocation.to_dict(),
                "usage": usage.to_dict(),
                "cpu_utilization": usage.cpu_usage / allocation.cpu_limit if allocation.cpu_limit > 0 else 0,
                "memory_utilization": usage.memory_usage / allocation.memory_limit if allocation.memory_limit > 0 else 0
            }
        else:
            return {
                va_id: self.get_resource_status(va_id)
                for va_id in self.allocations.keys()
            }

    def _save_state(self):
        try:
            """Save resource management state"""
            state_file = self.data_dir / "resource_state.json"

            state = {
                "allocations": {va_id: a.to_dict() for va_id, a in self.allocations.items()},
                "usage": {va_id: u.to_dict() for va_id, u in self.usage.items()},
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved resource state to {state_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    rm = VAResourceManagement(registry)

    print("=" * 80)
    print("⚙️  VA RESOURCE MANAGEMENT SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Resource status
    print("Resource Status:")
    status = rm.get_resource_status()
    for va_id, info in list(status.items())[:2]:
        if info:
            print(f"  • {va_id}:")
            print(f"    CPU: {info['usage']['cpu_usage']:.1f}/{info['allocation']['cpu_limit']:.1f}")
            print(f"    Memory: {info['usage']['memory_usage']:.1f}/{info['allocation']['memory_limit']:.1f} MB")
    print()

    # Test: Update usage
    print("Updating resource usage...")
    rm.update_usage("jarvis_va", cpu=1.5, memory=1500.0)
    rm.update_usage("ace", cpu=0.8, memory=800.0)
    print("  ✅ Usage updated")
    print()

    # Test: Auto-scaling
    print("Testing auto-scaling...")
    rm.auto_scale("jarvis_va", demand=0.85)
    rm.auto_scale("ace", demand=0.25)
    print("  ✅ Auto-scaling tested")
    print()

    # Test: Optimization
    print("Resource optimization:")
    optimization = rm.optimize_resources()
    print(f"  ✅ Found {len(optimization['optimizations'])} optimization opportunities")
    print()

    # Save state
    rm._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()