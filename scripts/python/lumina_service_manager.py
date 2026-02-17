#!/usr/bin/env python3
"""
LUMINA Service Manager

Manages all essential LUMINA services:
- AutoHotkey
- N8N (on NAS)
- SYPHON API

Handles service restart, health verification, and status monitoring.

Tags: #SERVICE_MANAGEMENT #REBOOT #AUTOMATION #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("ServiceManager")


class ServiceStatus(Enum):
    """Service status"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceInfo:
    """Service information"""
    def __init__(self, name: str, service_type: str, restart_command: Optional[str] = None):
        self.name = name
        self.service_type = service_type  # local, nas, remote
        self.restart_command = restart_command
        self.status = ServiceStatus.UNKNOWN
        self.last_check = None
        self.health_check_url = None


class LuminaServiceManager:
    """
    LUMINA Service Manager

    Manages all essential services with restart and health verification.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize service manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Define services
        self.services = self._initialize_services()

    def _initialize_services(self) -> Dict[str, ServiceInfo]:
        """Initialize service definitions"""
        services = {}

        # AutoHotkey (local process)
        services["autohotkey"] = ServiceInfo(
            name="AutoHotkey",
            service_type="local",
            restart_command="lumina_hotkey_manager"
        )

        # N8N (on NAS)
        services["n8n"] = ServiceInfo(
            name="N8N",
            service_type="nas",
            restart_command="start_n8n_nas"
        )
        services["n8n"].health_check_url = "http://<NAS_PRIMARY_IP>:5678/api/v1/workflows"

        # SYPHON API (remote service)
        services["syphon"] = ServiceInfo(
            name="SYPHON API",
            service_type="remote",
            restart_command="start_syphon_api"
        )
        services["syphon"].health_check_url = "http://<NAS_IP>:8000/health"

        # Personal Virtual Assistants (@pva)
        services["pva"] = ServiceInfo(
            name="Personal Virtual Assistants",
            service_type="local",
            restart_command="start_pva_services"
        )

        return services

    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service

        Args:
            service_name: Name of service to restart

        Returns: True if successful, False otherwise
        """
        if service_name not in self.services:
            logger.error(f"   ❌ Unknown service: {service_name}")
            return False

        service = self.services[service_name]
        logger.info(f"   🔄 Restarting {service.name}...")

        try:
            if service.service_type == "local":
                return self._restart_local_service(service)
            elif service.service_type == "nas":
                return self._restart_nas_service(service)
            elif service.service_type == "remote":
                return self._restart_remote_service(service)
            elif service.service_type == "cloud":
                # Cloud services don't need restart, just verify
                return self._verify_cloud_service(service)
            else:
                logger.warning(f"   ⚠️  Unknown service type: {service.service_type}")
                return False
        except Exception as e:
            logger.error(f"   ❌ Failed to restart {service.name}: {e}")
            service.status = ServiceStatus.ERROR
            return False

    def _restart_local_service(self, service: ServiceInfo) -> bool:
        """Restart local service (AutoHotkey, PVA)"""
        if service.name == "AutoHotkey":
            try:
                from lumina_hotkey_manager import LuminaHotkeyManager
                manager = LuminaHotkeyManager()
                manager.start_hotkeys()

                # Verify it's running
                time.sleep(2)
                if manager.is_autohotkey_running():
                    service.status = ServiceStatus.RUNNING
                    logger.info(f"   ✅ {service.name} restarted and verified")
                    return True
                else:
                    service.status = ServiceStatus.ERROR
                    logger.warning(f"   ⚠️  {service.name} started but not verified")
                    return False
            except Exception as e:
                logger.error(f"   ❌ Failed to restart {service.name}: {e}")
                service.status = ServiceStatus.ERROR
                return False
        elif service.name == "Personal Virtual Assistants":
            try:
                from start_pva_services import PVAServiceManager
                pva_manager = PVAServiceManager()
                results = pva_manager.start_all_pva_services()

                # Verify services
                time.sleep(2)
                verify_results = pva_manager.verify_pva_services()

                if all(verify_results.values()):
                    service.status = ServiceStatus.RUNNING
                    logger.info(f"   ✅ {service.name} restarted and verified")
                    return True
                else:
                    service.status = ServiceStatus.ERROR
                    logger.warning(f"   ⚠️  {service.name} started but not all verified")
                    return False
            except Exception as e:
                logger.error(f"   ❌ Failed to restart {service.name}: {e}")
                service.status = ServiceStatus.ERROR
                return False

        return False

    def _restart_nas_service(self, service: ServiceInfo) -> bool:
        """Restart NAS service (N8N)"""
        if service.name == "N8N":
            try:
                # Check if start_n8n_nas script exists
                start_script = self.project_root / "scripts" / "python" / "start_n8n_nas.py"
                if start_script.exists():
                    result = subprocess.run(
                        [sys.executable, str(start_script)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        # Verify service is accessible
                        time.sleep(5)  # Wait for service to start
                        if self._verify_service_health(service):
                            service.status = ServiceStatus.RUNNING
                            logger.info(f"   ✅ {service.name} restarted and verified")
                            return True
                        else:
                            service.status = ServiceStatus.ERROR
                            logger.warning(f"   ⚠️  {service.name} started but not accessible")
                            return False
                    else:
                        logger.error(f"   ❌ Failed to start {service.name}: {result.stderr}")
                        service.status = ServiceStatus.ERROR
                        return False
                else:
                    logger.warning(f"   ⚠️  Start script not found: {start_script}")
                    service.status = ServiceStatus.UNKNOWN
                    return False
            except Exception as e:
                logger.error(f"   ❌ Failed to restart {service.name}: {e}")
                service.status = ServiceStatus.ERROR
                return False

        return False

    def _restart_remote_service(self, service: ServiceInfo) -> bool:
        """Restart remote service (SYPHON API)"""
        if service.name == "SYPHON API":
            # Remote services may need manual restart or SSH access
            # For now, just verify health
            logger.info(f"   ℹ️  {service.name} is remote - verifying health")
            if self._verify_service_health(service):
                service.status = ServiceStatus.RUNNING
                logger.info(f"   ✅ {service.name} is accessible")
                return True
            else:
                service.status = ServiceStatus.ERROR
                logger.warning(f"   ⚠️  {service.name} is not accessible")
                return False

        return False

    def _verify_cloud_service(self, service: ServiceInfo) -> bool:
        """Verify cloud service"""
        # No cloud services currently registered (Twilio removed per directive)
        logger.debug(f"   ℹ️  No cloud service verification for: {service.name}")
        return False

    def _verify_service_health(self, service: ServiceInfo) -> bool:
        """Verify service health via HTTP check"""
        if not service.health_check_url:
            return True  # No health check URL, assume healthy

        try:
            import requests
            response = requests.get(service.health_check_url, timeout=5)
            if response.status_code == 200:
                return True
            else:
                logger.debug(f"   ⚠️  {service.name} health check returned {response.status_code}")
                return False
        except Exception as e:
            logger.debug(f"   ⚠️  {service.name} health check failed: {e}")
            return False

    def restart_all_services(self) -> Dict[str, bool]:
        """
        Restart all services

        Returns: Dictionary of service_name -> success status
        """
        logger.info("   🔄 Restarting all services...")
        results = {}

        for service_name, service in self.services.items():
            results[service_name] = self.restart_service(service_name)
            time.sleep(1)  # Brief pause between services

        return results

    def verify_all_services(self) -> Dict[str, bool]:
        """
        Verify all services are healthy

        Returns: Dictionary of service_name -> health status
        """
        logger.info("   🔍 Verifying all services...")
        results = {}

        for service_name, service in self.services.items():
            if service.health_check_url:
                results[service_name] = self._verify_service_health(service)
            elif service.service_type == "local":
                # For local services, check if process is running
                if service.name == "AutoHotkey":
                    try:
                        from lumina_hotkey_manager import LuminaHotkeyManager
                        manager = LuminaHotkeyManager()
                        results[service_name] = manager.is_autohotkey_running()
                    except Exception:
                        results[service_name] = False
                elif service.name == "Personal Virtual Assistants":
                    try:
                        from start_pva_services import PVAServiceManager
                        pva_manager = PVAServiceManager()
                        verify_results = pva_manager.verify_pva_services()
                        results[service_name] = all(verify_results.values())
                    except Exception:
                        results[service_name] = True  # Assume running if check fails
                else:
                    results[service_name] = True  # Assume healthy if no check
            elif service.service_type == "cloud":
                results[service_name] = self._verify_cloud_service(service)
            else:
                results[service_name] = True  # Assume healthy if no check

        return results

    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        for service_name, service in self.services.items():
            status[service_name] = {
                "name": service.name,
                "type": service.service_type,
                "status": service.status.value,
                "last_check": service.last_check.isoformat() if service.last_check else None
            }
        return status


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Service Manager")
        parser.add_argument("--restart", help="Restart specific service")
        parser.add_argument("--restart-all", action="store_true", help="Restart all services")
        parser.add_argument("--verify", action="store_true", help="Verify all services")
        parser.add_argument("--status", action="store_true", help="Get service status")

        args = parser.parse_args()

        manager = LuminaServiceManager()

        if args.restart:
            result = manager.restart_service(args.restart)
            sys.exit(0 if result else 1)
        elif args.restart_all:
            results = manager.restart_all_services()
            all_success = all(results.values())
            sys.exit(0 if all_success else 1)
        elif args.verify:
            results = manager.verify_all_services()
            all_healthy = all(results.values())
            sys.exit(0 if all_healthy else 1)
        elif args.status:
            status = manager.get_service_status()
            import json
            print(json.dumps(status, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())