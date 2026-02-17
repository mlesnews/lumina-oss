#!/usr/bin/env python3
"""
JARVIS AI Instance Recycler

Manages AI/JARVIS instance lifecycle with warm reboot support.
Tracks instance state, maintains continuity across reboots,
and integrates with unified queue system.

Features:
- Instance lifecycle tracking
- Warm reboot support
- State persistence
- Graceful recycling
- Instance status monitoring

@JARVIS @INSTANCE @RECYCLE @WARM_REBOOT @LIFECYCLE
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
logger = get_logger("jarvis_instance_recycler")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType, QueueItemStatus
except ImportError:
    UnifiedQueueAdapter = None
    QueueItemType = None
    QueueItemStatus = None


class InstanceState(Enum):
    """AI instance states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    RECYCLING = "recycling"
    RECYCLED = "recycled"
    SHUTDOWN = "shutdown"
    WARM_REBOOT = "warm_reboot"


@dataclass
class AIInstance:
    """Represents an AI/JARVIS instance"""
    instance_id: str
    agent_name: str
    state: InstanceState
    created_at: str
    last_active: str
    recycle_count: int = 0
    total_requests: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = None
    warm_reboot_enabled: bool = True

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            **asdict(self),
            'state': self.state.value
        }


class JARVISInstanceRecycler:
    """
    JARVIS AI Instance Recycler

    Manages AI instance lifecycle with warm reboot support.
    Tracks instances, maintains state, and handles recycling.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize instance recycler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISRecycler")

        # Instance tracking
        self.instances: Dict[str, AIInstance] = {}
        self.active_instance_id: Optional[str] = None

        # Configuration
        self.max_idle_time = 3600  # 1 hour
        self.warm_reboot_threshold = 5  # Recycle after 5 requests
        self.recycle_on_shutdown = True

        # State persistence
        self.state_dir = self.project_root / "data" / "jarvis_instances"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "instances.json"

        # Unified queue integration (set externally to avoid circular dependency)
        self.queue_adapter = None

        # Load existing state
        self.load_state()

        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        self.logger.info("=" * 80)
        self.logger.info("♻️  JARVIS Instance Recycler Initialized")
        self.logger.info("=" * 80)
        self.logger.info(f"   Active Instances: {len(self.instances)}")
        self.logger.info(f"   Warm Reboot: Enabled")
        self.logger.info(f"   State File: {self.state_file}")
        self.logger.info("=" * 80)

    def create_instance(self, agent_name: str = "JARVIS",
                       warm_reboot: bool = True) -> str:
        """
        Create a new AI instance

        Args:
            agent_name: Name of the agent
            warm_reboot: Enable warm reboot for this instance

        Returns:
            Instance ID
        """
        instance_id = f"jarvis_{uuid.uuid4().hex[:8]}_{int(time.time())}"

        instance = AIInstance(
            instance_id=instance_id,
            agent_name=agent_name,
            state=InstanceState.INITIALIZING,
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            warm_reboot_enabled=warm_reboot
        )

        self.instances[instance_id] = instance
        self.active_instance_id = instance_id

        # Update state
        instance.state = InstanceState.ACTIVE

        # Add to unified queue as notification
        if self.queue_adapter:
            try:
                self.queue_adapter.add_task(
                    title=f"JARVIS Instance Created: {agent_name}",
                    description=f"Instance ID: {instance_id}\nWarm Reboot: {warm_reboot}",
                    priority="normal"
                )
            except Exception as e:
                self.logger.debug(f"Queue notification failed: {e}")

        self.save_state()
        self.logger.info(f"✨ Created instance: {instance_id} ({agent_name})")

        return instance_id

    def get_active_instance(self) -> Optional[AIInstance]:
        """Get currently active instance"""
        if self.active_instance_id and self.active_instance_id in self.instances:
            return self.instances[self.active_instance_id]
        return None

    def record_activity(self, instance_id: Optional[str] = None):
        """Record activity on an instance"""
        if instance_id is None:
            instance_id = self.active_instance_id

        if instance_id and instance_id in self.instances:
            instance = self.instances[instance_id]
            instance.last_active = datetime.now().isoformat()
            instance.total_requests += 1
            instance.state = InstanceState.ACTIVE
            self.save_state()

    def should_recycle(self, instance_id: str) -> bool:
        """Check if instance should be recycled"""
        if instance_id not in self.instances:
            return False

        instance = self.instances[instance_id]

        # Check idle time
        last_active = datetime.fromisoformat(instance.last_active)
        idle_time = (datetime.now() - last_active).total_seconds()

        if idle_time > self.max_idle_time:
            return True

        # Check request count
        if instance.total_requests >= self.warm_reboot_threshold:
            return True

        return False

    def warm_reboot(self, instance_id: str) -> str:
        """
        Perform warm reboot of an instance

        Preserves state and creates new instance with same configuration

        Args:
            instance_id: Instance to reboot

        Returns:
            New instance ID
        """
        if instance_id not in self.instances:
            self.logger.warning(f"⚠️  Instance not found: {instance_id}")
            return None

        old_instance = self.instances[instance_id]

        self.logger.info(f"♻️  Warm rebooting instance: {instance_id}")

        # Mark old instance as recycling
        old_instance.state = InstanceState.RECYCLING
        old_instance.metadata["recycled_at"] = datetime.now().isoformat()
        old_instance.metadata["recycled_to"] = None  # Will be set after creation

        # Create new instance with preserved configuration
        new_instance_id = self.create_instance(
            agent_name=old_instance.agent_name,
            warm_reboot=old_instance.warm_reboot_enabled
        )

        new_instance = self.instances[new_instance_id]

        # Transfer state
        new_instance.recycle_count = old_instance.recycle_count + 1
        new_instance.metadata["recycled_from"] = instance_id
        new_instance.metadata["preserved_state"] = old_instance.metadata.copy()

        # Mark old instance as recycled
        old_instance.state = InstanceState.RECYCLED
        old_instance.metadata["recycled_to"] = new_instance_id

        # Update active instance
        self.active_instance_id = new_instance_id

        self.save_state()

        # Add to unified queue
        if self.queue_adapter:
            try:
                self.queue_adapter.add_task(
                    title=f"JARVIS Warm Reboot: {old_instance.agent_name}",
                    description=f"Recycled: {instance_id} → {new_instance_id}\nRecycle Count: {new_instance.recycle_count}",
                    priority="normal"
                )
            except Exception as e:
                self.logger.debug(f"Queue notification failed: {e}")

        self.logger.info(f"✅ Warm reboot complete: {instance_id} → {new_instance_id}")

        return new_instance_id

    def shutdown_instance(self, instance_id: str, warm: bool = True):
        """
        Shutdown an instance (warm or cold)

        Args:
            instance_id: Instance to shutdown
            warm: If True, perform warm shutdown (preserve state)
        """
        if instance_id not in self.instances:
            self.logger.warning(f"⚠️  Instance not found: {instance_id}")
            return

        instance = self.instances[instance_id]

        if warm:
            self.logger.info(f"🔄 Warm shutdown: {instance_id}")
            # Perform warm reboot instead of cold shutdown
            new_id = self.warm_reboot(instance_id)
            if new_id:
                self.logger.info(f"   → Rebooted to: {new_id}")
        else:
            self.logger.info(f"🛑 Cold shutdown: {instance_id}")
            instance.state = InstanceState.SHUTDOWN
            instance.metadata["shutdown_at"] = datetime.now().isoformat()
            self.save_state()

    def load_state(self):
        """Load instance state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Restore instances
                for instance_data in data.get("instances", []):
                    instance = AIInstance(
                        instance_id=instance_data["instance_id"],
                        agent_name=instance_data["agent_name"],
                        state=InstanceState(instance_data["state"]),
                        created_at=instance_data["created_at"],
                        last_active=instance_data["last_active"],
                        recycle_count=instance_data.get("recycle_count", 0),
                        total_requests=instance_data.get("total_requests", 0),
                        total_tokens=instance_data.get("total_tokens", 0),
                        metadata=instance_data.get("metadata", {}),
                        warm_reboot_enabled=instance_data.get("warm_reboot_enabled", True)
                    )
                    self.instances[instance.instance_id] = instance

                # Restore active instance
                self.active_instance_id = data.get("active_instance_id")

                self.logger.info(f"📂 Loaded {len(self.instances)} instances from state")

            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load state: {e}")

    def save_state(self):
        """Save instance state to disk"""
        try:
            data = {
                "instances": [instance.to_dict() for instance in self.instances.values()],
                "active_instance_id": self.active_instance_id,
                "saved_at": datetime.now().isoformat()
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to save state: {e}")

    def start_monitoring(self):
        """Start monitoring for recycling"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                try:
                    # Check all active instances
                    for instance_id, instance in list(self.instances.items()):
                        if instance.state == InstanceState.ACTIVE:
                            # Check if should recycle
                            if self.should_recycle(instance_id):
                                if instance.warm_reboot_enabled:
                                    self.warm_reboot(instance_id)
                                else:
                                    instance.state = InstanceState.IDLE
                                    self.save_state()

                    time.sleep(60)  # Check every minute

                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

        self.logger.info("👁️  Monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("⏹️  Monitoring stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get recycler status"""
        active = self.get_active_instance()

        return {
            "active_instance_id": self.active_instance_id,
            "active_instance": active.to_dict() if active else None,
            "total_instances": len(self.instances),
            "by_state": {
                state.value: sum(1 for i in self.instances.values() if i.state == state)
                for state in InstanceState
            },
            "total_recycles": sum(i.recycle_count for i in self.instances.values()),
            "total_requests": sum(i.total_requests for i in self.instances.values())
        }

    def print_status(self):
        """Print human-readable status"""
        status = self.get_status()

        print("\n" + "=" * 80)
        print("♻️  JARVIS Instance Recycler Status")
        print("=" * 80)
        print(f"Active Instance: {status['active_instance_id'] or 'None'}")
        print(f"Total Instances: {status['total_instances']}")
        print(f"Total Recycles: {status['total_recycles']}")
        print(f"Total Requests: {status['total_requests']}")
        print()

        if status['active_instance']:
            inst = status['active_instance']
            print(f"Active Instance Details:")
            print(f"  ID: {inst['instance_id']}")
            print(f"  Agent: {inst['agent_name']}")
            print(f"  State: {inst['state']}")
            print(f"  Requests: {inst['total_requests']}")
            print(f"  Recycles: {inst['recycle_count']}")
            print(f"  Last Active: {inst['last_active']}")
            print()

        print("By State:")
        for state, count in status['by_state'].items():
            if count > 0:
                print(f"  {state:15s} {count:>6}")
        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Instance Recycler")
    parser.add_argument("--create", action="store_true",
                       help="Create new instance")
    parser.add_argument("--agent-name", type=str, default="JARVIS",
                       help="Agent name for new instance")
    parser.add_argument("--warm-reboot", type=str, metavar="INSTANCE_ID",
                       help="Warm reboot an instance")
    parser.add_argument("--shutdown", type=str, metavar="INSTANCE_ID",
                       help="Shutdown an instance")
    parser.add_argument("--warm", action="store_true",
                       help="Use warm shutdown (default: True)")
    parser.add_argument("--status", action="store_true",
                       help="Show status")
    parser.add_argument("--monitor", action="store_true",
                       help="Start monitoring")

    args = parser.parse_args()

    recycler = JARVISInstanceRecycler()

    if args.create:
        instance_id = recycler.create_instance(agent_name=args.agent_name)
        print(f"✅ Created instance: {instance_id}")

    if args.warm_reboot:
        new_id = recycler.warm_reboot(args.warm_reboot)
        if new_id:
            print(f"✅ Warm rebooted: {args.warm_reboot} → {new_id}")
        else:
            print(f"❌ Failed to warm reboot: {args.warm_reboot}")

    if args.shutdown:
        recycler.shutdown_instance(args.shutdown, warm=args.warm)
        print(f"✅ Shutdown: {args.shutdown}")

    if args.status:
        recycler.print_status()

    if args.monitor:
        recycler.start_monitoring()
        print("👁️  Monitoring started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(10)
                recycler.print_status()
        except KeyboardInterrupt:
            recycler.stop_monitoring()


if __name__ == "__main__":


    main()