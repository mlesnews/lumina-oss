#!/usr/bin/env python3
"""
Lumina Startup Sequence Manager

Manages startup order and precedence for Lumina ecosystem:
- Docker Desktop
- Cursor IDE
- Ironman Virtual Assistant (Ace)
- Kenny IMVA
- Other services

Tracks startup times and logs to compound log for analysis.

Tags: #STARTUP #SEQUENCE #PRECEDENCE @JARVIS @LUMINA
"""

import sys
import time
import subprocess
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

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

logger = get_logger("LuminaStartupSequence")

# Gateway synchronization
try:
    from gateway_sequence_synchronizer import (
        get_gateway_synchronizer,
        register_process_for_gateway,
        wait_for_gateway_ready,
        mark_gateway_ready,
        record_sequence_event
    )
    GATEWAY_SYNC_AVAILABLE = True
except ImportError:
    GATEWAY_SYNC_AVAILABLE = False
    logger.warning("⚠️  Gateway synchronizer not available - processes may race gateway")

# Terminal sequence management
try:
    from terminal_sequence_manager import (
        get_terminal_manager,
        wait_for_terminal_ready,
        record_terminal_sequence
    )
    TERMINAL_SYNC_AVAILABLE = True
except ImportError:
    TERMINAL_SYNC_AVAILABLE = False
    logger.warning("⚠️  Terminal sequence manager not available - sequences may be out of order")


class StartupPriority(Enum):
    """Startup priority levels"""
    CRITICAL = 1  # Must start first (Docker, Cursor)
    HIGH = 2      # Start early (Ironman VA/Ace)
    MEDIUM = 3    # Start after critical services (Kenny)
    LOW = 4       # Start last (optional services)


@dataclass
class StartupService:
    """Startup service definition"""
    name: str
    priority: StartupPriority
    process_name: str  # Process name to check if running
    command: Optional[List[str]] = None  # Command to start if not running
    wait_time: float = 0.0  # Wait time after starting (seconds)
    dependencies: List[str] = field(default_factory=list)  # Service names that must start first
    startup_time: Optional[float] = None  # Actual startup time (seconds)
    status: str = "pending"  # pending, starting, running, failed


class LuminaStartupSequenceManager:
    """
    Manages startup sequence for Lumina ecosystem.

    Ensures proper order:
    1. Docker Desktop (CRITICAL)
    2. Cursor IDE (CRITICAL)
    3. Ironman VA / Ace (HIGH)
    4. Kenny IMVA (MEDIUM)
    5. Other services (LOW)
    """

    def __init__(self, project_root: Path):
        """
        Initialize startup sequence manager.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.services: Dict[str, StartupService] = {}
        self.startup_log: List[Dict[str, Any]] = []
        self.start_time = time.time()

        # Gateway synchronization
        self.gateway_sync = None
        if GATEWAY_SYNC_AVAILABLE:
            try:
                self.gateway_sync = get_gateway_synchronizer()
                logger.info("✅ Gateway synchronizer initialized")
            except Exception as e:
                logger.warning("⚠️  Could not initialize gateway synchronizer: %s", e)

        # Terminal sequence management
        self.terminal_manager = None
        if TERMINAL_SYNC_AVAILABLE:
            try:
                self.terminal_manager = get_terminal_manager()
                logger.info("✅ Terminal sequence manager initialized")

                # Auto-start auto-fix monitor
                try:
                    from terminal_sequence_auto_fix import get_auto_fix_monitor
                    get_auto_fix_monitor()  # Auto-starts
                    logger.info("✅ Terminal auto-fix monitor started")
                except ImportError:
                    logger.debug("   Auto-fix monitor not available")
                except Exception as e:
                    logger.debug("   Could not start auto-fix monitor: %s", e)
            except Exception as e:
                logger.warning("⚠️  Could not initialize terminal manager: %s", e)

        # Define startup services in order of precedence
        self._define_services()

    def _define_services(self):
        """Define startup services and their order"""
        script_dir = self.project_root / "scripts" / "python"

        # CRITICAL: Must start first
        self.services["docker"] = StartupService(
            name="Docker Desktop",
            priority=StartupPriority.CRITICAL,
            process_name="Docker Desktop",
            wait_time=5.0,  # Wait for Docker to fully initialize
            startup_time=None
        )

        self.services["cursor"] = StartupService(
            name="Cursor IDE",
            priority=StartupPriority.CRITICAL,
            process_name="Cursor.exe",
            wait_time=2.0,
            dependencies=["docker"],  # Docker should be ready first
            startup_time=None
        )

        # HIGH: Start early
        self.services["ace"] = StartupService(
            name="Ironman Virtual Assistant (Ace)",
            priority=StartupPriority.HIGH,
            process_name="python",
            command=[
                sys.executable,
                str(script_dir / "ironman_virtual_assistant.py"),
                "--start"
            ],
            wait_time=3.0,
            dependencies=["cursor"],  # Cursor should be ready
            startup_time=None
        )

        # MEDIUM: Start after critical services
        self.services["kenny"] = StartupService(
            name="Kenny IMVA",
            priority=StartupPriority.MEDIUM,
            process_name="kenny_imva_enhanced.py",
            command=[
                sys.executable,
                str(script_dir / "kenny_imva_enhanced.py"),
                "--match-ace"
            ],
            wait_time=2.0,
            dependencies=["ace"],  # Ace should be ready first
            startup_time=None
        )

    def is_service_running(self, service: StartupService) -> bool:
        """
        Check if service is already running.

        Args:
            service: Service to check

        Returns:
            True if service is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '').lower()
                    cmdline = proc_info.get('cmdline', [])
                    cmdline_str = ' '.join(cmdline) if cmdline else ''

                    # Check process name
                    if service.process_name.lower() in proc_name:
                        # For Python processes, also check command line
                        if 'python' in proc_name.lower():
                            if service.process_name.lower() in cmdline_str.lower():
                                return True
                        else:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.debug(f"Error checking service {service.name}: {e}")

        return False

    def start_service(self, service: StartupService) -> bool:
        """
        Start a service if not already running.

        Args:
            service: Service to start

        Returns:
            True if service started successfully, False otherwise
        """
        if self.is_service_running(service):
            logger.info(f"✅ {service.name} is already running")
            service.status = "running"
            return True

        if not service.command:
            logger.warning(f"⚠️  {service.name} has no start command - assuming external start")
            service.status = "running"  # Assume it will be started externally
            return True

        try:
            logger.info(f"🚀 Starting {service.name}...")
            service.status = "starting"
            start_time = time.time()

            # CRITICAL: Wait for terminal to be ready FIRST
            import os
            process_id = os.getpid()

            if self.terminal_manager:
                terminal_ready = wait_for_terminal_ready(
                    process_id, service.name, timeout=10.0
                )
                if not terminal_ready:
                    logger.warning(
                        f"⚠️  Terminal not ready for {service.name} - proceeding anyway"
                    )

            # CRITICAL: Record sequence: Command start (A)
            if self.gateway_sync:
                record_sequence_event("A", process_name=service.name)
            if self.terminal_manager:
                record_terminal_sequence("A", process_id=process_id, process_name=service.name)

            # CRITICAL: Wait for gateway if this service needs it
            # Services that interact with gateway should wait
            if self.gateway_sync and service.name.lower() in [
                "ironman virtual assistant (ace)",
                "kenny imva",
                "cursor ide"
            ]:
                registered = register_process_for_gateway(
                    process_id, service.name, priority=service.priority.value
                )
                gateway_ready = wait_for_gateway_ready(process_id, timeout=10.0)
                if not gateway_ready:
                    logger.warning(
                        f"⚠️  Gateway not ready for {service.name} - proceeding anyway"
                    )

            # Start process
            proc = subprocess.Popen(
                service.command,
                cwd=str(self.project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for service to initialize
            if service.wait_time > 0:
                time.sleep(service.wait_time)

            # Check if service is now running
            if self.is_service_running(service):
                service.startup_time = time.time() - start_time
                service.status = "running"
                logger.info(f"✅ {service.name} started in {service.startup_time:.2f}s")

                # CRITICAL: Record sequence: Command end (B)
                if self.gateway_sync:
                    record_sequence_event("B", process_name=service.name)
                if self.terminal_manager:
                    record_terminal_sequence("B", process_id=process_id, process_name=service.name)

                # Record prompt ready (P) after command completes
                if self.terminal_manager:
                    time.sleep(0.1)  # Small delay before prompt
                    record_terminal_sequence("P", process_id=process_id, process_name=service.name)

                return True
            else:
                service.status = "failed"
                logger.warning(f"⚠️  {service.name} may not have started correctly")

                # Record error sequence (E)
                if self.gateway_sync:
                    record_sequence_event("E", process_name=service.name)
                if self.terminal_manager:
                    record_terminal_sequence("E", process_id=process_id, process_name=service.name)

                return False

        except Exception as e:
            service.status = "failed"
            logger.error(f"❌ Failed to start {service.name}: {e}")

            # Record error sequence (E)
            if self.gateway_sync:
                record_sequence_event("E", process_name=service.name)

            return False

    def check_dependencies(self, service: StartupService) -> bool:
        """
        Check if service dependencies are satisfied.

        Args:
            service: Service to check dependencies for

        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        for dep_name in service.dependencies:
            if dep_name not in self.services:
                logger.warning(f"⚠️  Unknown dependency: {dep_name}")
                continue

            dep_service = self.services[dep_name]
            if dep_service.status != "running":
                logger.debug(f"⏳ Waiting for dependency: {dep_name} (status: {dep_service.status})")
                return False

        return True

    def start_sequence(self) -> Dict[str, Any]:
        """
        Start all services in proper order.

        Returns:
            Dictionary with startup results and timing
        """
        logger.info("=" * 60)
        logger.info("LUMINA STARTUP SEQUENCE")
        logger.info("=" * 60)
        logger.info(f"Start time: {datetime.now().isoformat()}")

        # CRITICAL: Ensure terminal is ready FIRST before anything else
        if self.terminal_manager:
            logger.info("🔍 Ensuring terminal is ready before starting services...")
            terminal_ready = self.terminal_manager.initialize_terminal()
            if not terminal_ready:
                logger.warning("⚠️  Terminal not ready - attempting re-initialization...")
                self.terminal_manager.reinitialize_terminal()
            else:
                logger.info("✅ Terminal ready - safe to start services")

        # CRITICAL: Ensure gateway is ready before starting services
        if self.gateway_sync:
            logger.info("🔍 Ensuring gateway is ready before starting services...")
            gateway_ready = self.gateway_sync.ensure_gateway_ready()
            if not gateway_ready:
                logger.warning("⚠️  Gateway not ready - services may race gateway")
            else:
                logger.info("✅ Gateway ready - safe to start services")
                # Record sequence: Gateway ready (P - Prompt ready)
                record_sequence_event("P", process_id=None, process_name="gateway")

        # Sort services by priority
        sorted_services = sorted(
            self.services.values(),
            key=lambda s: (s.priority.value, s.name)
        )

        # Start services in order
        for service in sorted_services:
            # Check dependencies
            if not self.check_dependencies(service):
                logger.warning(f"⚠️  Skipping {service.name} - dependencies not ready")
                continue

            # Start service
            self.start_service(service)

            # Log startup
            self.startup_log.append({
                "name": service.name,
                "priority": service.priority.name,
                "status": service.status,
                "startup_time": service.startup_time,
                "timestamp": datetime.now().isoformat()
            })

        # Generate summary
        total_time = time.time() - self.start_time
        summary = {
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "total_time": total_time,
            "services": {
                name: {
                    "status": svc.status,
                    "startup_time": svc.startup_time
                }
                for name, svc in self.services.items()
            },
            "log": self.startup_log
        }

        logger.info("=" * 60)
        logger.info("STARTUP SEQUENCE COMPLETE")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info("=" * 60)

        return summary

    def save_compound_log(self, output_file: Optional[Path] = None):
        """
        Save startup sequence to compound log.

        Args:
            output_file: Optional output file path (default: data/lumina_startup_log.json)
        """
        if output_file is None:
            output_file = self.project_root / "data" / "lumina_startup_log.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "startup_sequence": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "total_time": time.time() - self.start_time,
                "services": {
                    name: {
                        "name": svc.name,
                        "priority": svc.priority.name,
                        "status": svc.status,
                        "startup_time": svc.startup_time,
                        "dependencies": svc.dependencies
                    }
                    for name, svc in self.services.items()
                },
                "log": self.startup_log
            }
        }

        try:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Startup log saved to: {output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save startup log: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lumina Startup Sequence Manager")
    parser.add_argument("--project-root", type=Path, default=Path.cwd().parent.parent,
                       help="Project root directory")
    parser.add_argument("--save-log", action="store_true",
                       help="Save startup log to file")
    parser.add_argument("--log-file", type=Path,
                       help="Custom log file path")

    args = parser.parse_args()

    manager = LuminaStartupSequenceManager(args.project_root)
    summary = manager.start_sequence()

    if args.save_log:
        manager.save_compound_log(args.log_file)
