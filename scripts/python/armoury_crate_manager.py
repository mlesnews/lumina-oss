#!/usr/bin/env python3
"""
Armoury Crate Management Module for Jarvis
Windows System Engineering Framework

Provides complete control and management of ASUS Armoury Crate:
- Service management
- Lighting control
- Theme management
- Health monitoring
- Integration with Jarvis framework
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging


class ArmouryCrateManager:
    """
    Complete management system for Armoury Crate and AURA lighting.
    Integrated with Jarvis Windows System Engineering framework.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Armoury Crate Manager

        Args:
            config_path: Optional path to configuration file
        """
        self.logger = self._setup_logging()
        self.scripts_dir = Path(__file__).parent.parent
        self.data_dir = self.scripts_dir / "data" / "armoury_crate"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config(config_path)

        # Critical services
        self.critical_services = [
            "LightingService",  # AURA lighting
            "ArmouryCrateService",
            "ArmouryCrateControlInterface"
        ]

        self.logger.info("ArmouryCrateManager initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the manager"""
        logger = logging.getLogger("ArmouryCrateManager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🎨 ArmouryCrateManager - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "auto_fix_enabled": True,
            "health_check_interval": 300,  # 5 minutes
            "themes_directory": str(self.data_dir / "themes"),
            "preferred_theme": "JarvisBlue",
            "auto_apply_theme_on_start": False
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config from {config_path}: {e}")

        return default_config

    def run_powershell_script(self, script_name: str, *args) -> Dict[str, Any]:
        """
        Execute a PowerShell script from the scripts directory

        Args:
            script_name: Name of the PowerShell script (without .ps1)
            *args: Additional arguments to pass to the script

        Returns:
            Dictionary with execution results
        """
        script_path = self.scripts_dir / f"{script_name}.ps1"

        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {script_path}"
            }

        try:
            cmd = ["pwsh", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + list(args)
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

    def diagnose(self) -> Dict[str, Any]:
        """
        Run comprehensive diagnostic on Armoury Crate

        Returns:
            Dictionary with diagnostic results
        """
        self.logger.info("Running diagnostic...")
        result = self.run_powershell_script("armoury_crate_diagnostic")

        # Parse diagnostic results if available
        diagnostic_file = self.data_dir / f"armoury_crate_diagnostic_*.json"
        diagnostic_files = list(self.data_dir.glob("armoury_crate_diagnostic_*.json"))

        if diagnostic_files:
            latest = max(diagnostic_files, key=os.path.getctime)
            try:
                with open(latest, 'r') as f:
                    diagnostic_data = json.load(f)
                return {
                    "success": True,
                    "diagnostic": diagnostic_data,
                    "script_output": result
                }
            except Exception as e:
                self.logger.warning(f"Could not parse diagnostic file: {e}")

        return {
            "success": result["success"],
            "script_output": result
        }

    def fix(self) -> Dict[str, Any]:
        """
        Fix Armoury Crate issues (enable services, restore functionality)

        Returns:
            Dictionary with fix results
        """
        self.logger.info("Running fix...")
        result = self.run_powershell_script("armoury_crate_fix")

        # Parse fix results if available
        fix_files = list(self.data_dir.glob("armoury_crate_fix_*.json"))
        if fix_files:
            latest = max(fix_files, key=os.path.getctime)
            try:
                with open(latest, 'r') as f:
                    fix_data = json.load(f)
                return {
                    "success": True,
                    "fix_results": fix_data,
                    "script_output": result
                }
            except Exception as e:
                self.logger.warning(f"Could not parse fix file: {e}")

        return {
            "success": result["success"],
            "script_output": result
        }

    def get_lighting_status(self) -> Dict[str, Any]:
        """
        Get current lighting status and available themes

        Returns:
            Dictionary with lighting status
        """
        self.logger.info("Getting lighting status...")
        result = self.run_powershell_script(
            "armoury_crate_lighting_manager",
            "-Action", "status"
        )

        return {
            "success": result["success"],
            "status": result.get("stdout", ""),
            "timestamp": datetime.now().isoformat()
        }

    def list_themes(self) -> Dict[str, Any]:
        try:
            """
            List all available lighting themes

            Returns:
                Dictionary with available themes
            """
            self.logger.info("Listing themes...")
            result = self.run_powershell_script(
                "armoury_crate_lighting_manager",
                "-Action", "list"
            )

            # Load predefined themes
            themes_dir = Path(self.config.get("themes_directory", self.data_dir / "themes"))
            themes_dir.mkdir(parents=True, exist_ok=True)

            themes = {
                "predefined": [
                    "JarvisBlue", "MatrixGreen", "Cyberpunk", 
                    "Fire", "Ocean", "StaticWhite", "Rainbow"
                ],
                "custom": []
            }

            # Find custom themes
            for theme_file in themes_dir.glob("*.json"):
                if theme_file.name != "last_applied_theme.json":
                    themes["custom"].append(theme_file.stem)

            return {
                "success": result["success"],
                "themes": themes,
                "script_output": result.get("stdout", "")
            }

        except Exception as e:
            self.logger.error(f"Error in list_themes: {e}", exc_info=True)
            raise
    def apply_theme(self, theme_name: str) -> Dict[str, Any]:
        try:
            """
            Apply a lighting theme

            Args:
                theme_name: Name of the theme to apply

            Returns:
                Dictionary with application results
            """
            self.logger.info(f"Applying theme: {theme_name}")
            result = self.run_powershell_script(
                "armoury_crate_lighting_manager",
                "-Action", "apply",
                "-ThemeName", theme_name
            )

            # Save applied theme info
            applied_info = {
                "theme_name": theme_name,
                "applied_at": datetime.now().isoformat(),
                "success": result["success"]
            }

            applied_file = self.data_dir / "themes" / "last_applied_theme.json"
            applied_file.parent.mkdir(parents=True, exist_ok=True)
            with open(applied_file, 'w') as f:
                json.dump(applied_info, f, indent=2)

            return {
                "success": result["success"],
                "theme": theme_name,
                "applied_at": applied_info["applied_at"],
                "script_output": result.get("stdout", "")
            }

        except Exception as e:
            self.logger.error(f"Error in apply_theme: {e}", exc_info=True)
            raise
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Armoury Crate services

        Returns:
            Dictionary with health status
        """
        self.logger.info("Performing health check...")

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_health": "unknown",
            "issues": []
        }

        # Check each critical service
        for service_name in self.critical_services:
            try:
                result = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                is_running = "RUNNING" in result.stdout
                is_auto = "AUTO_START" in result.stdout or "DEMAND_START" in result.stdout

                health_status["services"][service_name] = {
                    "running": is_running,
                    "automatic": is_auto,
                    "status": "healthy" if (is_running and is_auto) else "unhealthy"
                }

                if not is_running:
                    health_status["issues"].append(f"Service {service_name} is not running")
                if not is_auto:
                    health_status["issues"].append(f"Service {service_name} is not set to automatic")

            except Exception as e:
                health_status["services"][service_name] = {
                    "error": str(e),
                    "status": "error"
                }
                health_status["issues"].append(f"Error checking {service_name}: {e}")

        # Determine overall health
        if len(health_status["issues"]) == 0:
            health_status["overall_health"] = "healthy"
        elif len(health_status["issues"]) < len(self.critical_services):
            health_status["overall_health"] = "degraded"
        else:
            health_status["overall_health"] = "unhealthy"

        # Auto-fix if enabled and unhealthy
        if (health_status["overall_health"] != "healthy" and 
            self.config.get("auto_fix_enabled", True)):
            self.logger.info("Auto-fix enabled, attempting to fix issues...")
            fix_result = self.fix()
            health_status["auto_fix_attempted"] = True
            health_status["auto_fix_result"] = fix_result

        # Save health check
        health_file = self.data_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(health_file, 'w') as f:
            json.dump(health_status, f, indent=2)

        return health_status

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of Armoury Crate system

        Returns:
            Dictionary with complete status
        """
        self.logger.info("Getting comprehensive status...")

        status = {
            "timestamp": datetime.now().isoformat(),
            "health": self.health_check(),
            "lighting": self.get_lighting_status(),
            "themes": self.list_themes()
        }

        return status


# Integration with Jarvis framework
def register_with_jarvis():
    """
    Register Armoury Crate Manager with Jarvis framework
    """
    return {
        "name": "ArmouryCrateManager",
        "type": "system_management",
        "module": "scripts.python.armoury_crate_manager",
        "class": "ArmouryCrateManager",
        "version": "1.0.0",
        "features": [
            "service_management",
            "lighting_control",
            "theme_management",
            "health_monitoring",
            "auto_fix"
        ],
        "integration_points": {
            "health_check": "armoury_crate_manager.health_check",
            "diagnostic": "armoury_crate_manager.diagnose",
            "fix": "armoury_crate_manager.fix",
            "apply_theme": "armoury_crate_manager.apply_theme"
        }
    }


if __name__ == "__main__":
    # Example usage
    manager = ArmouryCrateManager()

    print("🎨 Armoury Crate Manager - Jarvis Integration")
    print("=" * 70)
    print()

    # Health check
    print("📊 Health Check:")
    health = manager.health_check()
    print(json.dumps(health, indent=2))
    print()

    # List themes
    print("🎨 Available Themes:")
    themes = manager.list_themes()
    print(json.dumps(themes, indent=2))
    print()

    # Get status
    print("📋 Complete Status:")
    status = manager.get_status()
    print(json.dumps(status, indent=2))

