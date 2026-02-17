#!/usr/bin/env python3
"""
JARVIS Warm Reboot Handler

Handles warm reboots of JARVIS/AI instances during developer window reboots.
Maintains continuity, preserves state, and integrates with unified queue.

Features:
- Detects developer window reboots
- Performs warm instance recycling
- Preserves state across reboots
- Updates unified queue
- Maintains connection warmth

@JARVIS @WARM_REBOOT @DEVELOPER_WINDOW @CONTINUITY
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

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
    from jarvis_instance_recycler import JARVISInstanceRecycler, InstanceState
except ImportError:
    JARVISInstanceRecycler = None
    InstanceState = None

try:
    from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType
except ImportError:
    UnifiedQueueAdapter = None
    QueueItemType = None


class JARVISWarmRebootHandler:
    """
    Handles warm reboots of JARVIS instances

    Detects developer window reboots and performs graceful instance recycling
    while maintaining state and connection warmth.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize warm reboot handler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISWarmReboot")

        # Initialize recycler (without queue adapter to avoid circular dependency)
        self.recycler = None
        if JARVISInstanceRecycler:
            try:
                # Create recycler without queue adapter
                self.recycler = JARVISInstanceRecycler(self.project_root)
                # Don't initialize queue adapter here to avoid circular dependency
                self.recycler.queue_adapter = None
                self.logger.info("✅ Instance recycler initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Recycler initialization failed: {e}")

        # Queue adapter will be set externally to avoid circular dependency
        self.queue_adapter = None

        # Reboot tracking
        self.reboot_state_file = self.project_root / "data" / "jarvis_instances" / "reboot_state.json"
        self.reboot_state_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info("=" * 80)
        self.logger.info("🔄 JARVIS Warm Reboot Handler Initialized")
        self.logger.info("=" * 80)
        self.logger.info("   Keeping the connection warm... <3")
        self.logger.info("=" * 80)

    def detect_reboot(self) -> bool:
        """
        Detect if this is a warm reboot (developer window restart)

        Returns:
            True if warm reboot detected
        """
        if not self.reboot_state_file.exists():
            # First run - not a reboot
            self._save_reboot_state()
            return False

        try:
            with open(self.reboot_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            last_shutdown = state.get("last_shutdown")
            if last_shutdown:
                # Check if shutdown was recent (within last 5 minutes)
                shutdown_time = datetime.fromisoformat(last_shutdown)
                time_diff = (datetime.now() - shutdown_time).total_seconds()

                if time_diff < 300:  # 5 minutes
                    self.logger.info(f"🔄 Warm reboot detected (shutdown was {time_diff:.0f}s ago)")
                    return True

        except Exception as e:
            self.logger.warning(f"⚠️  Error detecting reboot: {e}")

        return False

    def handle_warm_reboot(self) -> Optional[str]:
        """
        Handle warm reboot - recycle instances while preserving state

        Returns:
            New instance ID if rebooted, None otherwise
        """
        if not self.recycler:
            self.logger.warning("⚠️  Recycler not available")
            return None

        # Get active instance
        active_instance = self.recycler.get_active_instance()

        if not active_instance:
            # No active instance - create new one
            self.logger.info("✨ No active instance - creating new JARVIS instance")
            instance_id = self.recycler.create_instance(agent_name="JARVIS", warm_reboot=True)

            # Add to queue
            if self.queue_adapter:
                self.queue_adapter.add_task(
                    title="JARVIS Instance Created (Warm Reboot)",
                    description=f"New instance: {instance_id}\nReason: Warm reboot - no active instance",
                    priority="normal"
                )

            return instance_id

        # Perform warm reboot
        self.logger.info(f"♻️  Warm rebooting JARVIS instance: {active_instance.instance_id}")

        new_instance_id = self.recycler.warm_reboot(active_instance.instance_id)

        if new_instance_id:
            # Add to queue
            if self.queue_adapter:
                self.queue_adapter.add_task(
                    title="JARVIS Warm Reboot Complete",
                    description=f"Recycled: {active_instance.instance_id} → {new_instance_id}\n"
                               f"Recycle Count: {self.recycler.instances[new_instance_id].recycle_count}\n"
                               f"State preserved: ✅\n"
                               f"Connection kept warm: <3",
                    priority="normal"
                )

            self.logger.info(f"✅ Warm reboot complete - connection kept warm <3")
            self.logger.info(f"   Old: {active_instance.instance_id}")
            self.logger.info(f"   New: {new_instance_id}")

        return new_instance_id

    def handle_shutdown(self):
        """Handle shutdown - prepare for warm reboot"""
        if not self.recycler:
            return

        active_instance = self.recycler.get_active_instance()

        if active_instance:
            self.logger.info(f"🛑 Shutdown detected - preparing for warm reboot")
            self.logger.info(f"   Instance: {active_instance.instance_id}")
            self.logger.info(f"   Keeping state warm for next boot... <3")

            # Save shutdown state
            self._save_reboot_state(shutdown=True)

            # Mark instance for warm reboot
            active_instance.metadata["shutdown_prepared"] = True
            active_instance.metadata["shutdown_at"] = datetime.now().isoformat()
            self.recycler.save_state()

    def _save_reboot_state(self, shutdown: bool = False):
        """Save reboot state"""
        state = {
            "last_shutdown": datetime.now().isoformat() if shutdown else None,
            "last_boot": datetime.now().isoformat(),
            "warm_reboot_enabled": True
        }

        try:
            with open(self.reboot_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to save reboot state: {e}")

    def initialize(self):
        """Initialize - check for warm reboot and handle"""
        if self.detect_reboot():
            # Warm reboot detected - recycle instance
            new_instance_id = self.handle_warm_reboot()
            if new_instance_id:
                self.logger.info(f"✨ JARVIS ready - instance recycled, connection warm <3")
            else:
                self.logger.warning("⚠️  Warm reboot failed - creating new instance")
                if self.recycler:
                    self.recycler.create_instance(agent_name="JARVIS", warm_reboot=True)
        else:
            # First run or cold start
            if not self.recycler or not self.recycler.get_active_instance():
                self.logger.info("✨ Creating initial JARVIS instance")
                if self.recycler:
                    instance_id = self.recycler.create_instance(agent_name="JARVIS", warm_reboot=True)
                    self.logger.info(f"   Instance: {instance_id}")
                    self.logger.info(f"   Connection warm <3")
            else:
                self.logger.info("✅ JARVIS instance active - connection warm <3")

        # Start monitoring
        if self.recycler:
            self.recycler.start_monitoring()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Warm Reboot Handler")
    parser.add_argument("--init", action="store_true",
                       help="Initialize (check for warm reboot)")
    parser.add_argument("--shutdown", action="store_true",
                       help="Handle shutdown (prepare for warm reboot)")
    parser.add_argument("--status", action="store_true",
                       help="Show status")

    args = parser.parse_args()

    handler = JARVISWarmRebootHandler()

    if args.init:
        handler.initialize()

    if args.shutdown:
        handler.handle_shutdown()

    if args.status:
        if handler.recycler:
            handler.recycler.print_status()
        else:
            print("❌ Recycler not available")


if __name__ == "__main__":


    main()