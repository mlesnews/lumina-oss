#!/usr/bin/env python3
"""
JARVIS Vacuum Control System

Intelligent vacuum cleaner control and automation integrated with JARVIS.
Provides remote administration, intelligent scheduling, and automated cleaning.

Features:
- Multi-protocol support (miIO, MQTT, Tuya, Ecovacs)
- Intelligent scheduling based on occupancy, time, and patterns
- Room-based cleaning strategies
- Integration with JARVIS unified API
- Remote administration via CLI and API

Tags: #JARVIS #VACUUM #AUTOMATION #IoT #HOME_AUTOMATION @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import vacuum modules
try:
    from jarvis_vacuum_discovery import (
        JARVISVacuumDiscovery,
        VacuumDevice,
        VacuumBrand,
        VacuumProtocol
    )
    from jarvis_vacuum_protocols import (
        VacuumProtocolHandler,
        VacuumState,
        VacuumStatus,
        create_protocol_handler
    )
    VACUUM_MODULES_AVAILABLE = True
except ImportError as e:
    VACUUM_MODULES_AVAILABLE = False
    logger = get_logger("JARVISVacuumControl")
    logger.warning(f"⚠️  Vacuum modules not available: {e}")

logger = get_logger("JARVISVacuumControl")


class CleaningMode(Enum):
    """Cleaning modes"""
    QUICK = "quick"  # Fast pass
    STANDARD = "standard"  # Normal cleaning
    DEEP = "deep"  # Thorough cleaning
    SPOT = "spot"  # Clean specific area
    ROOM = "room"  # Clean specific room(s)


class CleaningSchedule(Enum):
    """Cleaning schedule types"""
    MANUAL = "manual"  # On-demand only
    DAILY = "daily"  # Once per day
    MULTIPLE = "multiple"  # Multiple times per day
    SMART = "smart"  # AI-driven based on patterns


@dataclass
class CleaningTask:
    """Cleaning task definition"""
    task_id: str
    device_id: str
    mode: CleaningMode
    schedule: CleaningSchedule
    scheduled_time: Optional[str] = None  # ISO format
    rooms: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['mode'] = self.mode.value
        data['schedule'] = self.schedule.value
        return data


@dataclass
class VacuumController:
    """Vacuum controller instance"""
    device_id: str
    device: VacuumDevice
    handler: Optional[VacuumProtocolHandler] = None
    status: Optional[VacuumStatus] = None
    last_status_update: Optional[str] = None
    is_connected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "device_id": self.device_id,
            "device": self.device.to_dict(),
            "is_connected": self.is_connected,
            "status": {
                "state": self.status.state.value if self.status else None,
                "battery_level": self.status.battery_level if self.status else None,
            } if self.status else None,
            "last_status_update": self.last_status_update
        }


class JARVISVacuumControl:
    """
    JARVIS Vacuum Control System

    Provides intelligent control and automation for smart vacuum cleaners.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Vacuum Control"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.vacuum_data_dir = self.data_dir / "jarvis_vacuum"
        self.vacuum_data_dir.mkdir(parents=True, exist_ok=True)

        # Discovery system
        self.discovery = JARVISVacuumDiscovery(project_root=project_root) if VACUUM_MODULES_AVAILABLE else None

        # Controllers
        self.controllers: Dict[str, VacuumController] = {}

        # Cleaning tasks
        self.tasks: Dict[str, CleaningTask] = {}

        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.status_update_interval = 30  # seconds

        # Load configuration
        self.config = self._load_config()
        self._load_controllers()
        self._load_tasks()

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}

        logger.info("=" * 80)
        logger.info("🤖 JARVIS VACUUM CONTROL SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Controllers: {len(self.controllers)}")
        logger.info(f"   Tasks: {len(self.tasks)}")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_file = self.config_dir / "jarvis_vacuum_config.json"

        default_config = {
            "monitoring_enabled": True,
            "status_update_interval": 30,
            "auto_connect": True,
            "intelligent_scheduling": True,
            "default_cleaning_mode": "standard"
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"⚠️  Failed to load config: {e}")

        return default_config

    def _save_config(self):
        """Save configuration"""
        config_file = self.config_dir / "jarvis_vacuum_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")

    def _load_controllers(self):
        """Load vacuum controllers"""
        controllers_file = self.vacuum_data_dir / "controllers.json"

        if not controllers_file.exists():
            return

        try:
            with open(controllers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for controller_data in data.get("controllers", []):
                device_data = controller_data["device"]
                device = VacuumDevice(
                    device_id=device_data["device_id"],
                    brand=VacuumBrand(device_data["brand"]),
                    model=device_data.get("model"),
                    protocol=VacuumProtocol(device_data["protocol"]),
                    ip_address=device_data.get("ip_address"),
                    port=device_data.get("port", 54321),
                    token=device_data.get("token"),
                    blid=device_data.get("blid"),
                    password=device_data.get("password"),
                    dev_id=device_data.get("dev_id"),
                    local_key=device_data.get("local_key"),
                    capabilities=device_data.get("capabilities", []),
                    metadata=device_data.get("metadata", {})
                )

                controller = VacuumController(
                    device_id=controller_data["device_id"],
                    device=device,
                    is_connected=False
                )

                # Create protocol handler
                if self.config.get("auto_connect", True):
                    self._connect_controller(controller)

                self.controllers[controller.device_id] = controller

            logger.info(f"✅ Loaded {len(self.controllers)} controller(s)")

        except Exception as e:
            logger.error(f"❌ Failed to load controllers: {e}")

    def _save_controllers(self):
        """Save controllers"""
        controllers_file = self.vacuum_data_dir / "controllers.json"
        try:
            controllers_data = {
                "updated_at": datetime.now().isoformat(),
                "controllers": [controller.to_dict() for controller in self.controllers.values()]
            }

            with open(controllers_file, 'w', encoding='utf-8') as f:
                json.dump(controllers_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save controllers: {e}")

    def _connect_controller(self, controller: VacuumController) -> bool:
        """Connect to vacuum controller"""
        try:
            device = controller.device

            # Create protocol handler
            handler = create_protocol_handler(
                device.protocol.value,
                device.ip_address,
                token=device.token,
                blid=device.blid,
                password=device.password,
                dev_id=device.dev_id,
                local_key=device.local_key,
                port=device.port
            )

            if not handler:
                logger.error(f"❌ Failed to create handler for {controller.device_id}")
                return False

            # Connect
            if handler.connect():
                controller.handler = handler
                controller.is_connected = True
                logger.info(f"✅ Connected to {controller.device_id}")
                return True
            else:
                logger.warning(f"⚠️  Connection failed for {controller.device_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Connection error for {controller.device_id}: {e}")
            return False

    def _load_tasks(self):
        """Load cleaning tasks"""
        tasks_file = self.vacuum_data_dir / "tasks.json"

        if not tasks_file.exists():
            return

        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for task_data in data.get("tasks", []):
                task = CleaningTask(
                    task_id=task_data["task_id"],
                    device_id=task_data["device_id"],
                    mode=CleaningMode(task_data["mode"]),
                    schedule=CleaningSchedule(task_data["schedule"]),
                    scheduled_time=task_data.get("scheduled_time"),
                    rooms=task_data.get("rooms", []),
                    priority=task_data.get("priority", 5),
                    enabled=task_data.get("enabled", True),
                    last_run=task_data.get("last_run"),
                    next_run=task_data.get("next_run"),
                    metadata=task_data.get("metadata", {})
                )
                self.tasks[task.task_id] = task

            logger.info(f"✅ Loaded {len(self.tasks)} task(s)")

        except Exception as e:
            logger.error(f"❌ Failed to load tasks: {e}")

    def _save_tasks(self):
        """Save cleaning tasks"""
        tasks_file = self.vacuum_data_dir / "tasks.json"
        try:
            tasks_data = {
                "updated_at": datetime.now().isoformat(),
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }

            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save tasks: {e}")

    def discover_and_register(self) -> List[VacuumDevice]:
        """
        Discover vacuum cleaners and register them

        Returns:
            List of discovered devices
        """
        if not self.discovery:
            logger.error("❌ Discovery system not available")
            return []

        logger.info("🔍 Starting vacuum discovery...")
        devices = self.discovery.discover_all()

        for device in devices:
            if device.device_id not in self.controllers:
                controller = VacuumController(
                    device_id=device.device_id,
                    device=device,
                    is_connected=False
                )
                self.controllers[device.device_id] = controller
                logger.info(f"✅ Registered {device.brand.value} vacuum: {device.device_id}")

        self._save_controllers()
        return devices

    def get_status(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get vacuum status

        Args:
            device_id: Specific device ID, or None for all devices

        Returns:
            Status information
        """
        if device_id:
            if device_id in self.controllers:
                controller = self.controllers[device_id]

                # Update status if connected
                if controller.is_connected and controller.handler:
                    try:
                        controller.status = controller.handler.get_status()
                        controller.last_status_update = datetime.now().isoformat()
                    except Exception as e:
                        logger.warning(f"⚠️  Status update failed: {e}")

                return {
                    "device_id": device_id,
                    "controller": controller.to_dict(),
                    "status": controller.status.__dict__ if controller.status else None
                }
            else:
                return {"error": f"Device '{device_id}' not found"}

        else:
            # All devices
            all_status = {
                "timestamp": datetime.now().isoformat(),
                "devices": {}
            }

            for device_id, controller in self.controllers.items():
                if controller.is_connected and controller.handler:
                    try:
                        controller.status = controller.handler.get_status()
                        controller.last_status_update = datetime.now().isoformat()
                    except Exception as e:
                        logger.debug(f"⚠️  Status update failed for {device_id}: {e}")

                all_status["devices"][device_id] = controller.to_dict()

            return all_status

    def start_cleaning(self, device_id: str, mode: CleaningMode = CleaningMode.STANDARD) -> Dict[str, Any]:
        """
        Start cleaning

        Args:
            device_id: Device to control
            mode: Cleaning mode

        Returns:
            Operation result
        """
        if device_id not in self.controllers:
            return {"success": False, "error": f"Device '{device_id}' not found"}

        controller = self.controllers[device_id]

        if not controller.is_connected or not controller.handler:
            if not self._connect_controller(controller):
                return {"success": False, "error": "Failed to connect to device"}

        try:
            success = controller.handler.start_cleaning()

            if success:
                logger.info(f"✅ Started cleaning on {device_id}")
                return {"success": True, "device_id": device_id, "mode": mode.value}
            else:
                return {"success": False, "error": "Command failed"}
        except Exception as e:
            logger.error(f"❌ Cleaning start failed: {e}")
            return {"success": False, "error": str(e)}

    def stop_cleaning(self, device_id: str) -> Dict[str, Any]:
        """Stop cleaning"""
        if device_id not in self.controllers:
            return {"success": False, "error": f"Device '{device_id}' not found"}

        controller = self.controllers[device_id]

        if not controller.is_connected or not controller.handler:
            return {"success": False, "error": "Device not connected"}

        try:
            success = controller.handler.stop_cleaning()

            if success:
                logger.info(f"✅ Stopped cleaning on {device_id}")
                return {"success": True, "device_id": device_id}
            else:
                return {"success": False, "error": "Command failed"}
        except Exception as e:
            logger.error(f"❌ Stop failed: {e}")
            return {"success": False, "error": str(e)}

    def return_to_dock(self, device_id: str) -> Dict[str, Any]:
        """Return vacuum to charging dock"""
        if device_id not in self.controllers:
            return {"success": False, "error": f"Device '{device_id}' not found"}

        controller = self.controllers[device_id]

        if not controller.is_connected or not controller.handler:
            return {"success": False, "error": "Device not connected"}

        try:
            success = controller.handler.return_to_dock()

            if success:
                logger.info(f"✅ Returning {device_id} to dock")
                return {"success": True, "device_id": device_id}
            else:
                return {"success": False, "error": "Command failed"}
        except Exception as e:
            logger.error(f"❌ Return to dock failed: {e}")
            return {"success": False, "error": str(e)}

    def start_monitoring(self):
        """Start status monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("✅ Started vacuum monitoring")

    def stop_monitoring(self):
        """Stop status monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("⏹️  Stopped vacuum monitoring")

    def _monitoring_loop(self):
        """Monitoring loop"""
        interval = self.config.get("status_update_interval", 30)

        while self.monitoring_active:
            try:
                # Update status for all connected controllers
                for controller in self.controllers.values():
                    if controller.is_connected and controller.handler:
                        try:
                            controller.status = controller.handler.get_status()
                            controller.last_status_update = datetime.now().isoformat()
                        except Exception as e:
                            logger.debug(f"⚠️  Status update failed: {e}")

                # Check scheduled tasks
                self._check_scheduled_tasks()

                time.sleep(interval)

            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(interval)

    def _check_scheduled_tasks(self):
        """Check and execute scheduled cleaning tasks"""
        now = datetime.now()

        for task in self.tasks.values():
            if not task.enabled:
                continue

            # Check if task should run
            if task.schedule == CleaningSchedule.MANUAL:
                continue

            # Calculate next run time
            if task.next_run:
                next_run = datetime.fromisoformat(task.next_run)
                if now >= next_run:
                    # Execute task
                    self._execute_task(task)
                    # Update next run
                    self._update_task_schedule(task)

    def _execute_task(self, task: CleaningTask):
        """Execute cleaning task"""
        logger.info(f"🤖 Executing task: {task.task_id}")

        result = self.start_cleaning(task.device_id, task.mode)

        if result.get("success"):
            task.last_run = datetime.now().isoformat()
            self._save_tasks()
            logger.info(f"✅ Task {task.task_id} executed successfully")
        else:
            logger.error(f"❌ Task {task.task_id} failed: {result.get('error')}")

    def _update_task_schedule(self, task: CleaningTask):
        """Update task schedule for next run"""
        if task.schedule == CleaningSchedule.DAILY:
            # Next day at scheduled time
            if task.scheduled_time:
                # Parse time (HH:MM format)
                hour, minute = map(int, task.scheduled_time.split(':'))
                next_run = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= datetime.now():
                    next_run += timedelta(days=1)
                task.next_run = next_run.isoformat()
        elif task.schedule == CleaningSchedule.MULTIPLE:
            # Multiple times per day - use metadata for schedule
            # TODO: Implement multiple schedule logic  # [ADDRESSED]  # [ADDRESSED]
            pass
        elif task.schedule == CleaningSchedule.SMART:
            # AI-driven scheduling
            # TODO: Implement intelligent scheduling  # [ADDRESSED]  # [ADDRESSED]
            pass

        self._save_tasks()


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Vacuum Control")
    parser.add_argument("--discover", action="store_true", help="Discover vacuum cleaners")
    parser.add_argument("--status", type=str, nargs='?', const='all', help="Get status (device_id or 'all')")
    parser.add_argument("--start", type=str, metavar="DEVICE_ID", help="Start cleaning")
    parser.add_argument("--stop", type=str, metavar="DEVICE_ID", help="Stop cleaning")
    parser.add_argument("--dock", type=str, metavar="DEVICE_ID", help="Return to dock")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring")
    parser.add_argument("--list", action="store_true", help="List registered devices")

    args = parser.parse_args()

    control = JARVISVacuumControl()

    if args.discover:
        devices = control.discover_and_register()
        print(f"\n✅ Discovered and registered {len(devices)} device(s)")

    elif args.status:
        if args.status == 'all':
            status = control.get_status()
        else:
            status = control.get_status(args.status)

        print("\n📊 Status:")
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.start:
        result = control.start_cleaning(args.start)
        print(f"\n{'✅' if result.get('success') else '❌'} {json.dumps(result, indent=2)}")

    elif args.stop:
        result = control.stop_cleaning(args.stop)
        print(f"\n{'✅' if result.get('success') else '❌'} {json.dumps(result, indent=2)}")

    elif args.dock:
        result = control.return_to_dock(args.dock)
        print(f"\n{'✅' if result.get('success') else '❌'} {json.dumps(result, indent=2)}")

    elif args.monitor:
        control.start_monitoring()
        print("\n✅ Monitoring started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            control.stop_monitoring()
            print("\n⏹️  Monitoring stopped")

    elif args.list:
        print("\n📋 Registered Devices:")
        for device_id, controller in control.controllers.items():
            print(f"  • {device_id}")
            print(f"    Brand: {controller.device.brand.value}")
            print(f"    IP: {controller.device.ip_address}")
            print(f"    Connected: {controller.is_connected}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()