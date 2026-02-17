#!/usr/bin/env python3
"""
MANUS Workstation Controller
Complete control of Windows laptop under Manus framework

Provides comprehensive control over:
- Armoury Crate & AURA lighting
- Power management
- System services
- Windows configuration
- Hardware control
- System health monitoring
- Automated maintenance

Integrated with Manus Unified Control framework.
"""

import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MANUSWorkstationController")


class WorkstationComponent(Enum):
    """Workstation components under Manus control"""
    ARMOURY_CRATE = "armoury_crate"
    POWER_MANAGEMENT = "power_management"
    SYSTEM_SERVICES = "system_services"
    WINDOWS_CONFIG = "windows_config"
    HARDWARE = "hardware"
    HEALTH_MONITORING = "health_monitoring"


@dataclass
class WorkstationStatus:
    """Workstation status information"""
    component: WorkstationComponent
    status: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[str] = field(default_factory=list)


class MANUSWorkstationController:
    """
    Complete workstation control under Manus framework

    Provides unified control interface for all laptop management operations.
    """

    def __init__(self, project_root: Path):
        """Initialize workstation controller"""
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"
        self.data_dir = self.project_root / "data" / "workstation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Component controllers
        self.armoury_crate_manager = None
        self.power_manager = None
        self.service_manager = None

        # Initialize component managers
        self._initialize_components()

        logger.info("MANUS Workstation Controller initialized")

    def _initialize_components(self) -> None:
        """Initialize all component controllers"""
        # Armoury Crate Manager
        try:
            from armoury_crate_manager import ArmouryCrateManager
            self.armoury_crate_manager = ArmouryCrateManager()
            logger.info("✓ Armoury Crate Manager initialized")
        except Exception as e:
            logger.warning(f"Armoury Crate Manager not available: {e}")

        # Power Manager (will be implemented)
        self.power_manager = PowerManager(self.project_root)
        logger.info("✓ Power Manager initialized")

        # Service Manager (will be implemented)
        self.service_manager = ServiceManager(self.project_root)
        logger.info("✓ Service Manager initialized")

    # ============================================================================
    # ARMOURY CRATE CONTROL
    # ============================================================================

    def get_armoury_crate_status(self) -> Dict[str, Any]:
        """Get Armoury Crate status"""
        if not self.armoury_crate_manager:
            return {
                "available": False,
                "error": "Armoury Crate Manager not initialized"
            }

        try:
            status = self.armoury_crate_manager.get_status()
            return {
                "available": True,
                "status": status
            }
        except Exception as e:
            return {
                "available": True,
                "error": str(e)
            }

    def fix_armoury_crate(self) -> Dict[str, Any]:
        """Fix Armoury Crate issues"""
        if not self.armoury_crate_manager:
            return {
                "success": False,
                "error": "Armoury Crate Manager not initialized"
            }

        try:
            result = self.armoury_crate_manager.fix()
            return {
                "success": result.get("success", False),
                "message": "Armoury Crate fixed",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def apply_lighting_theme(self, theme_name: str) -> Dict[str, Any]:
        """Apply lighting theme"""
        if not self.armoury_crate_manager:
            return {
                "success": False,
                "error": "Armoury Crate Manager not initialized"
            }

        try:
            result = self.armoury_crate_manager.apply_theme(theme_name)
            return {
                "success": result.get("success", False),
                "theme": theme_name,
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def fix_f4_aura_button(self) -> Dict[str, Any]:
        """Fix F4-AURA button functionality"""
        script_path = self.scripts_dir / "fix_f4_aura_button.ps1"
        if not script_path.exists():
            return {
                "success": False,
                "error": "Fix script not found"
            }

        try:
            result = self._run_powershell_script("fix_f4_aura_button")
            return {
                "success": result.get("success", False),
                "message": "F4-AURA button diagnostic completed",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ============================================================================
    # POWER MANAGEMENT
    # ============================================================================

    def configure_power_settings(self) -> Dict[str, Any]:
        """Configure power settings to prevent sleep/hibernate"""
        script_path = self.scripts_dir / "configure_power_settings.ps1"
        if not script_path.exists():
            return {
                "success": False,
                "error": "Power settings script not found"
            }

        try:
            result = self._run_powershell_script("configure_power_settings")
            return {
                "success": result.get("success", False),
                "message": "Power settings configured",
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def check_power_settings(self) -> Dict[str, Any]:
        """Check current power settings"""
        script_path = self.scripts_dir / "check_power_settings.ps1"
        if not script_path.exists():
            return {
                "success": False,
                "error": "Power check script not found"
            }

        try:
            result = self._run_powershell_script("check_power_settings")
            return {
                "success": result.get("success", False),
                "details": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ============================================================================
    # SYSTEM SERVICES
    # ============================================================================

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get Windows service status"""
        try:
            result = subprocess.run(
                ["sc", "query", service_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            is_running = "RUNNING" in result.stdout
            is_auto = "AUTO_START" in result.stdout

            return {
                "success": True,
                "service": service_name,
                "running": is_running,
                "automatic": is_auto,
                "status": "running" if is_running else "stopped"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def start_service(self, service_name: str) -> Dict[str, Any]:
        """Start a Windows service"""
        try:
            result = subprocess.run(
                ["sc", "start", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "service": service_name,
                "message": "Service started" if result.returncode == 0 else "Failed to start service"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def set_service_automatic(self, service_name: str) -> Dict[str, Any]:
        """Set service to automatic startup"""
        try:
            result = subprocess.run(
                ["sc", "config", service_name, "start=", "auto"],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "service": service_name,
                "message": "Service set to automatic" if result.returncode == 0 else "Failed to configure service"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ============================================================================
    # COMPREHENSIVE STATUS
    # ============================================================================

    def get_complete_status(self) -> Dict[str, Any]:
        """Get complete workstation status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }

        # Armoury Crate status
        status["components"]["armoury_crate"] = self.get_armoury_crate_status()

        # Power management status
        status["components"]["power_management"] = self.power_manager.get_status()

        # System services status
        status["components"]["system_services"] = self.service_manager.get_status()

        # Overall health
        status["health"] = self._calculate_health(status["components"])

        return status

    def _calculate_health(self, components: Dict[str, Any]) -> str:
        """Calculate overall workstation health"""
        issues = 0
        for component, data in components.items():
            if isinstance(data, dict):
                if not data.get("available", True) or data.get("error"):
                    issues += 1

        if issues == 0:
            return "healthy"
        elif issues <= 2:
            return "degraded"
        else:
            return "unhealthy"

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def _run_powershell_script(self, script_name: str, *args) -> Dict[str, Any]:
        """Execute a PowerShell script"""
        script_path = self.scripts_dir / f"{script_name}.ps1"

        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {script_path}"
            }

        try:
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + list(args)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class PowerManager:
    """Power management controller"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"

    def get_status(self) -> Dict[str, Any]:
        """Get power management status"""
        return {
            "available": True,
            "configured": True,
            "status": "operational"
        }


class ServiceManager:
    """System service management controller"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.critical_services = [
            "LightingService",
            "ArmouryCrateService",
            "ArmouryCrateControlInterface"
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get system services status"""
        services_status = {}

        for service_name in self.critical_services:
            try:
                result = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                is_running = "RUNNING" in result.stdout
                services_status[service_name] = {
                    "running": is_running,
                    "status": "running" if is_running else "stopped"
                }
            except:
                services_status[service_name] = {
                    "running": False,
                    "status": "unknown"
                }

        return {
            "available": True,
            "services": services_status
        }


def main():
    try:
        """CLI interface for MANUS Workstation Controller"""
        import argparse

        parser = argparse.ArgumentParser(description="MANUS Workstation Controller")
        parser.add_argument("--status", action="store_true", help="Get complete workstation status")
        parser.add_argument("--fix-armoury", action="store_true", help="Fix Armoury Crate")
        parser.add_argument("--apply-theme", type=str, help="Apply lighting theme")
        parser.add_argument("--fix-f4", action="store_true", help="Fix F4-AURA button")
        parser.add_argument("--configure-power", action="store_true", help="Configure power settings")
        parser.add_argument("--check-power", action="store_true", help="Check power settings")

        args = parser.parse_args()

        controller = MANUSWorkstationController(project_root)

        if args.status:
            status = controller.get_complete_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.fix_armoury:
            result = controller.fix_armoury_crate()
            print(json.dumps(result, indent=2))

        elif args.apply_theme:
            result = controller.apply_lighting_theme(args.apply_theme)
            print(json.dumps(result, indent=2))

        elif args.fix_f4:
            result = controller.fix_f4_aura_button()
            print(json.dumps(result, indent=2))

        elif args.configure_power:
            result = controller.configure_power_settings()
            print(json.dumps(result, indent=2))

        elif args.check_power:
            result = controller.check_power_settings()
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()