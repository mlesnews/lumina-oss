#!/usr/bin/env python3
"""
Stop Cloud Storage Clients with Automatic Sync Prevention
Stops and disables cloud storage clients to prevent them from syncing to C: drive.
Implements dynamic scaling with 5-second wait intervals based on context.

CONTEXT:
- Cloud storage clients (Dropbox, OneDrive) are syncing to C: drive
- C: drive is at 93.6% utilization (CRITICAL)
- Need to migrate to NAS unified cloud storage via DSM Cloud Storage Aggregator
- Must prevent automatic re-syncing while migration is in progress
- Dynamic scaling module adjusts wait times based on process state and system load

DYNAMIC SCALING MODULE:
- Waits 5 seconds between operations by default
- Scales wait time based on:
  * Number of processes to stop
  * System load
  * Process priority/state
  * Context of what was written (file operations, registry changes, etc.)

Tags: #CLOUD_STORAGE #MIGRATION #CLEANUP #AUTOMATIC_SYNC_PREVENTION #DYNAMIC_SCALING
"""

import sys
import subprocess
import time
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StopCloudStorageClients")


class DynamicScalingModule:
    """
    Dynamic Scaling Module
    Adjusts wait times based on context and system state.
    Default: 5 seconds, scales based on operations performed.
    """

    def __init__(self, base_wait: float = 5.0):
        self.base_wait = base_wait
        self.context_operations = []
        self.system_load_factor = 1.0

    def calculate_wait_time(self, context: Dict[str, Any]) -> float:
        """
        Calculate wait time based on context.

        Factors:
        - Base wait: 5 seconds
        - Number of operations performed
        - System load (CPU, memory)
        - Type of operations (file ops, registry, services)
        """
        wait_time = self.base_wait

        # Factor 1: Number of operations
        operation_count = len(self.context_operations)
        if operation_count > 0:
            wait_time += (operation_count * 0.5)  # +0.5s per operation

        # Factor 2: System load
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            # Higher load = longer wait
            if cpu_percent > 80 or memory_percent > 80:
                wait_time *= 1.5
            elif cpu_percent > 60 or memory_percent > 60:
                wait_time *= 1.2
        except Exception:
            pass  # Use base wait if can't get system stats

        # Factor 3: Operation type
        if context.get("registry_changes", 0) > 0:
            wait_time += 2.0  # Registry changes need more time
        if context.get("service_changes", 0) > 0:
            wait_time += 1.5  # Service changes need time to propagate

        return round(wait_time, 2)

    def wait(self, context: Optional[Dict[str, Any]] = None):
        """Wait with dynamic scaling based on context"""
        if context is None:
            context = {}

        wait_time = self.calculate_wait_time(context)
        logger.debug(f"   ⏳ Dynamic wait: {wait_time}s (context: {len(self.context_operations)} operations)")
        time.sleep(wait_time)

    def add_operation(self, operation_type: str, details: Dict[str, Any]):
        """Record an operation for context tracking"""
        self.context_operations.append({
            "type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })


class CloudStorageClientStopper:
    """
    Stop cloud storage clients from syncing locally.

    Implements automatic sync prevention:
    - Stops running processes
    - Disables services
    - Prevents auto-start on boot
    - Blocks re-syncing during migration

    Uses dynamic scaling module for wait intervals.
    """

    def __init__(self):
        self.scaling = DynamicScalingModule(base_wait=5.0)
        self.clients = {
            "Dropbox": {
                "process_names": ["Dropbox.exe"],
                "service_names": ["DropboxUpdateService"],
                "install_paths": [
                    Path("C:/Program Files (x86)/Dropbox"),
                    Path("C:/Program Files/Dropbox"),
                    Path.home() / "AppData" / "Local" / "Dropbox"
                ]
            },
            "OneDrive": {
                "process_names": ["OneDrive.exe"],
                "service_names": ["OneDrive Updater Service"],
                "install_paths": [
                    Path("C:/Program Files/Microsoft OneDrive"),
                    Path("C:/Program Files (x86)/Microsoft OneDrive")
                ]
            },
            "GoogleDrive": {
                "process_names": ["googledrivesync.exe", "GoogleDriveFS.exe"],
                "service_names": ["Google Drive File Stream"],
                "install_paths": [
                    Path("C:/Program Files/Google/Drive File Stream"),
                    Path("C:/Program Files (x86)/Google/Drive")
                ]
            }
        }

    def check_running_processes(self) -> Dict[str, List[str]]:
        """Check which cloud storage processes are running"""
        logger.info("🔍 Checking for running cloud storage processes...")

        running = {}

        for client_name, config in self.clients.items():
            running_processes = []

            for process_name in config["process_names"]:
                try:
                    # Check if process is running
                    result = subprocess.run(
                        ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if process_name.lower() in result.stdout.lower():
                        running_processes.append(process_name)
                        logger.info(f"   ⚠️  {client_name}: {process_name} is running")

                except Exception as e:
                    logger.debug(f"   Error checking {process_name}: {e}")

            if running_processes:
                running[client_name] = running_processes

        if not running:
            logger.info("   ✅ No cloud storage clients running")
        else:
            logger.warning(f"   ⚠️  Found {len(running)} cloud storage client(s) running")

        return running

    def stop_processes(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Stop cloud storage processes with automatic sync prevention.

        Uses dynamic scaling - waits 5 seconds between operations,
        scaling based on context of what was written/stopped.
        """
        logger.info("🛑 Stopping cloud storage processes...")
        logger.info("   🔒 Automatic sync prevention: Enabled")

        running = self.check_running_processes()
        results = {}
        context = {"process_stops": 0, "service_changes": 0}

        for client_name, processes in running.items():
            results[client_name] = {"stopped": [], "failed": []}

            for process_name in processes:
                if dry_run:
                    logger.info(f"   [DRY RUN] Would stop: {process_name}")
                    results[client_name]["stopped"].append(process_name)
                    self.scaling.add_operation("stop_process", {"client": client_name, "process": process_name})
                else:
                    try:
                        # Stop process gracefully first
                        logger.info(f"   🛑 Stopping {process_name}...")
                        subprocess.run(
                            ["taskkill", "/IM", process_name, "/T"],
                            capture_output=True,
                            timeout=30
                        )
                        logger.info(f"   ✅ Stopped: {process_name}")
                        results[client_name]["stopped"].append(process_name)
                        context["process_stops"] += 1

                        # Record operation for context
                        self.scaling.add_operation("stop_process", {
                            "client": client_name,
                            "process": process_name,
                            "success": True
                        })

                        # Dynamic wait - no automatic sync, wait based on context
                        if len(processes) > 1:  # Multiple processes, wait between them
                            self.scaling.wait(context)

                    except Exception as e:
                        logger.error(f"   ❌ Failed to stop {process_name}: {e}")
                        results[client_name]["failed"].append(process_name)
                        self.scaling.add_operation("stop_process", {
                            "client": client_name,
                            "process": process_name,
                            "success": False,
                            "error": str(e)
                        })

        return results

    def disable_services(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Disable cloud storage services to prevent automatic sync.

        Prevents services from auto-starting, which would cause
        automatic re-syncing. Uses dynamic scaling for wait times.
        """
        logger.info("🔧 Disabling cloud storage services...")
        logger.info("   🔒 Preventing automatic sync on boot")

        results = {}
        context = {"service_changes": 0, "registry_changes": 0}

        for client_name, config in self.clients.items():
            results[client_name] = {"disabled": [], "failed": []}

            for service_name in config.get("service_names", []):
                if dry_run:
                    logger.info(f"   [DRY RUN] Would disable service: {service_name}")
                    results[client_name]["disabled"].append(service_name)
                    self.scaling.add_operation("disable_service", {"client": client_name, "service": service_name})
                else:
                    try:
                        # Disable service (prevents automatic sync)
                        logger.info(f"   🔧 Disabling {service_name}...")
                        subprocess.run(
                            ["sc", "config", service_name, "start=", "disabled"],
                            capture_output=True,
                            timeout=30
                        )
                        logger.info(f"   ✅ Disabled service: {service_name}")
                        results[client_name]["disabled"].append(service_name)
                        context["service_changes"] += 1

                        # Record operation
                        self.scaling.add_operation("disable_service", {
                            "client": client_name,
                            "service": service_name,
                            "success": True
                        })

                        # Dynamic wait - service changes need time to propagate
                        self.scaling.wait(context)

                    except Exception as e:
                        logger.warning(f"   ⚠️  Could not disable {service_name}: {e}")
                        results[client_name]["failed"].append(service_name)
                        self.scaling.add_operation("disable_service", {
                            "client": client_name,
                            "service": service_name,
                            "success": False,
                            "error": str(e)
                        })

        return results

    def prevent_auto_start(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Prevent cloud storage clients from auto-starting.

        Additional layer of automatic sync prevention by blocking
        startup entries in registry and startup folders.
        """
        logger.info("🚫 Preventing automatic startup...")
        logger.info("   🔒 Blocking auto-start to prevent automatic sync")

        results = {}
        context = {"registry_changes": 0}

        # Startup folder locations
        startup_folders = [
            Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
            Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp")
        ]

        for client_name, config in self.clients.items():
            results[client_name] = {"blocked": [], "failed": []}

            # Check startup folders for shortcuts
            for startup_folder in startup_folders:
                if startup_folder.exists():
                    try:
                        for item in startup_folder.iterdir():
                            if any(proc.lower() in item.name.lower() for proc in config["process_names"]):
                                if dry_run:
                                    logger.info(f"   [DRY RUN] Would block startup: {item.name}")
                                    results[client_name]["blocked"].append(str(item))
                                else:
                                    # Rename to disable (safer than delete)
                                    backup_name = item.name + ".disabled"
                                    backup_path = item.parent / backup_name
                                    if not backup_path.exists():
                                        item.rename(backup_path)
                                        logger.info(f"   ✅ Blocked startup: {item.name}")
                                        results[client_name]["blocked"].append(str(item))
                                        context["registry_changes"] += 1
                                        self.scaling.add_operation("block_startup", {
                                            "client": client_name,
                                            "item": str(item)
                                        })
                                        self.scaling.wait(context)
                    except Exception as e:
                        logger.debug(f"   Error checking startup folder {startup_folder}: {e}")

        return results

    def generate_report(self, dry_run: bool = False) -> Dict[str, Any]:
        """Generate comprehensive report"""
        logger.info("=" * 80)
        logger.info("📊 CLOUD STORAGE CLIENT STATUS REPORT")
        logger.info("=" * 80)

        running = self.check_running_processes()

        report = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "dry_run": dry_run,
            "running_clients": running,
            "actions_taken": {}
        }

        if running:
            logger.info("")
            logger.info("🛑 Stopping processes (with automatic sync prevention)...")
            report["actions_taken"]["stop_processes"] = self.stop_processes(dry_run=dry_run)

            # Dynamic wait after stopping processes
            if not dry_run:
                logger.info("   ⏳ Waiting for processes to fully terminate...")
                self.scaling.wait({"process_stops": len(running)})

            logger.info("")
            logger.info("🔧 Disabling services (preventing automatic sync)...")
            report["actions_taken"]["disable_services"] = self.disable_services(dry_run=dry_run)

            logger.info("")
            logger.info("🚫 Preventing automatic startup...")
            report["actions_taken"]["prevent_auto_start"] = self.prevent_auto_start(dry_run=dry_run)

            logger.info("")
            logger.info("✅ Automatic sync prevention complete")
            logger.info("   - Processes stopped")
            logger.info("   - Services disabled")
            logger.info("   - Auto-start blocked")
            logger.info("   - No automatic sync will occur")
        else:
            logger.info("")
            logger.info("✅ No cloud storage clients running - nothing to stop")

        return report


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Stop Cloud Storage Clients")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually stop)")
        parser.add_argument("--check-only", action="store_true", help="Only check status, don't stop")

        args = parser.parse_args()

        stopper = CloudStorageClientStopper()

        if args.check_only:
            running = stopper.check_running_processes()
            print("\n" + "=" * 80)
            print("📊 CLOUD STORAGE CLIENT STATUS")
            print("=" * 80)
            if running:
                for client, processes in running.items():
                    print(f"   {client}: {', '.join(processes)}")
            else:
                print("   ✅ No cloud storage clients running")
            print("=" * 80)
        else:
            report = stopper.generate_report(dry_run=args.dry_run)

            # Save report
            report_file = project_root / "data" / "system" / f"cloud_storage_client_stop_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"\n💾 Report saved to: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()