#!/usr/bin/env python3
"""
ULTRON Cursor Network Coordinator

Coordinates network infrastructure teams to enable ULTRON in Cursor IDE:
- Network Security Orchestrator (pfSense firewall)
- Infrastructure Architecture Team
- Port Forwarding Service
- Cursor Configuration Management

Tags: #NETWORK #INFRASTRUCTURE #ULTRON #CURSOR @TEAM
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ULTRONCursorNetworkCoordinator")


class ULTRONCursorNetworkCoordinator:
    """
    Coordinates all teams to enable ULTRON in Cursor IDE

    Teams:
    - Network Team: pfSense firewall rules
    - Infrastructure Architecture: Port forwarding setup
    - Port Forward Service: SSH tunnel management
    - Cursor Config: Settings.json updates
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_path = project_root / "config" / "ultron_cursor_network.json"
        self.cursor_settings_path = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
        self.port_forward_script = project_root / "scripts" / "kaiju_port_forward_service.ps1"

        self.kaiju_host = "<NAS_IP>"
        self.kaiju_port = 3001
        self.local_port = 11435

        logger.info("✅ ULTRON Cursor Network Coordinator initialized")

    def check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to KAIJU"""
        logger.info("🔍 Checking network connectivity...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "kaiju_ssh": False,
            "kaiju_api": False,
            "local_port_forward": False,
            "cursor_config": False
        }

        # Test SSH
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Test-NetConnection -ComputerName {self.kaiju_host} -Port 22"],
                capture_output=True,
                timeout=10
            )
            results["kaiju_ssh"] = (result.returncode == 0)
        except Exception as e:
            logger.error(f"SSH test failed: {e}")

        # Test API
        try:
            import urllib.request
            response = urllib.request.urlopen(f"http://{self.kaiju_host}:{self.kaiju_port}/health", timeout=5)
            results["kaiju_api"] = (response.getcode() == 200)
        except Exception as e:
            logger.error(f"API test failed: {e}")

        # Test local port forward
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Test-NetConnection -ComputerName localhost -Port {self.local_port}"],
                capture_output=True,
                timeout=5
            )
            results["local_port_forward"] = (result.returncode == 0)
        except Exception:
            results["local_port_forward"] = False

        # Check Cursor config
        if self.cursor_settings_path.exists():
            try:
                with open(self.cursor_settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    models = settings.get("cursor.chat.customModels", [])
                    ultron_models = [m for m in models if "ultron" in m.get("name", "").lower()]
                    if ultron_models:
                        for model in ultron_models:
                            if f"localhost:{self.local_port}" in model.get("apiBase", ""):
                                results["cursor_config"] = True
                                break
            except Exception as e:
                logger.error(f"Cursor config check failed: {e}")

        return results

    def coordinate_network_teams(self) -> Dict[str, Any]:
        """Coordinate all network infrastructure teams"""
        logger.info("🌐 Coordinating network infrastructure teams...")

        coordination = {
            "timestamp": datetime.now().isoformat(),
            "network_team": {},
            "infrastructure_arch": {},
            "port_forward_service": {},
            "cursor_config": {}
        }

        # Network Team: Check pfSense firewall
        logger.info("📡 Network Team: Checking pfSense firewall...")
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(self.port_forward_script), "-CheckFirewall"],
                capture_output=True,
                timeout=30
            )
            coordination["network_team"]["firewall_check"] = {
                "executed": True,
                "output": result.stdout.decode("utf-8", errors="ignore")[:500]
            }
        except Exception as e:
            coordination["network_team"]["firewall_check"] = {
                "executed": False,
                "error": str(e)
            }

        # Infrastructure Architecture: Start port forward
        logger.info("🏗️  Infrastructure Architecture: Setting up port forwarding...")
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(self.port_forward_script), "-Start"],
                capture_output=True,
                timeout=30
            )
            coordination["infrastructure_arch"]["port_forward"] = {
                "executed": True,
                "success": (result.returncode == 0),
                "output": result.stdout.decode("utf-8", errors="ignore")[:500]
            }
        except Exception as e:
            coordination["infrastructure_arch"]["port_forward"] = {
                "executed": False,
                "error": str(e)
            }

        # Port Forward Service: Verify status
        logger.info("🔌 Port Forward Service: Verifying status...")
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(self.port_forward_script), "-Status"],
                capture_output=True,
                timeout=15
            )
            coordination["port_forward_service"]["status"] = {
                "executed": True,
                "output": result.stdout.decode("utf-8", errors="ignore")[:500]
            }
        except Exception as e:
            coordination["port_forward_service"]["status"] = {
                "executed": False,
                "error": str(e)
            }

        # Cursor Config: Update settings
        logger.info("⚙️  Cursor Config: Updating settings...")
        coordination["cursor_config"] = self.update_cursor_config()

        return coordination

    def update_cursor_config(self) -> Dict[str, Any]:
        """Update Cursor settings.json to use localhost port forward"""
        logger.info("Updating Cursor configuration...")

        if not self.cursor_settings_path.exists():
            return {"error": "Cursor settings.json not found"}

        try:
            with open(self.cursor_settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Update chat models
            if "cursor.chat.customModels" not in settings:
                settings["cursor.chat.customModels"] = []

            # Remove old ULTRON entries
            settings["cursor.chat.customModels"] = [
                m for m in settings["cursor.chat.customModels"]
                if "ultron" not in m.get("name", "").lower() and "iron-legion" not in m.get("name", "").lower()
            ]

            # Add new ULTRON with localhost
            ultron_models = [
                {
                    "name": "ULTRON",
                    "provider": "openai",
                    "model": "codellama:13b",
                    "apiBase": f"http://localhost:{self.local_port}/v1",
                    "apiKey": "",
                    "localOnly": True,
                    "contextLength": 8192
                },
                {
                    "name": "ultron",
                    "provider": "openai",
                    "model": "codellama:13b",
                    "apiBase": f"http://localhost:{self.local_port}/v1",
                    "apiKey": "",
                    "localOnly": True,
                    "contextLength": 8192
                }
            ]

            settings["cursor.chat.customModels"].extend(ultron_models)

            # Update composer models
            if "cursor.composer.customModels" not in settings:
                settings["cursor.composer.customModels"] = []

            settings["cursor.composer.customModels"] = [
                m for m in settings["cursor.composer.customModels"]
                if "ultron" not in m.get("name", "").lower() and "iron-legion" not in m.get("name", "").lower()
            ]

            settings["cursor.composer.customModels"].extend(ultron_models)

            # Backup
            backup_path = self.cursor_settings_path.with_suffix(".json.backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            # Write updated
            with open(self.cursor_settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Cursor config updated: localhost:{self.local_port}")
            return {
                "success": True,
                "backup": str(backup_path),
                "apiBase": f"http://localhost:{self.local_port}/v1"
            }

        except Exception as e:
            logger.error(f"❌ Failed to update Cursor config: {e}")
            return {"error": str(e)}

    def run_full_coordination(self) -> Dict[str, Any]:
        """Run full coordination across all teams"""
        logger.info("=" * 80)
        logger.info("🚀 ULTRON CURSOR NETWORK COORDINATION")
        logger.info("=" * 80)
        logger.info("")

        # Step 1: Check connectivity
        connectivity = self.check_network_connectivity()
        logger.info("📊 Connectivity Status:")
        logger.info(f"   KAIJU SSH: {'✅' if connectivity['kaiju_ssh'] else '❌'}")
        logger.info(f"   KAIJU API: {'✅' if connectivity['kaiju_api'] else '❌'}")
        logger.info(f"   Port Forward: {'✅' if connectivity['local_port_forward'] else '❌'}")
        logger.info("")

        # Step 2: Coordinate teams
        coordination = self.coordinate_network_teams()

        # Step 3: Final verification
        logger.info("🔍 Final Verification...")
        final_check = self.check_network_connectivity()

        result = {
            "connectivity": connectivity,
            "coordination": coordination,
            "final_check": final_check,
            "success": (
                final_check["local_port_forward"] and
                final_check["cursor_config"]
            )
        }

        logger.info("")
        logger.info("=" * 80)
        if result["success"]:
            logger.info("✅ ULTRON CURSOR INTEGRATION COMPLETE")
            logger.info("   Reload Cursor IDE (Ctrl+Shift+P → 'Reload Window') to use ULTRON")
        else:
            logger.info("⚠️  ULTRON CURSOR INTEGRATION - MANUAL STEPS REQUIRED")
        logger.info("=" * 80)

        return result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="ULTRON Cursor Network Coordinator")
        parser.add_argument("--coordinate", action="store_true", help="Run full coordination")
        parser.add_argument("--check", action="store_true", help="Check connectivity")
        parser.add_argument("--update-cursor", action="store_true", help="Update Cursor config only")

        args = parser.parse_args()

        coordinator = ULTRONCursorNetworkCoordinator(project_root)

        if args.coordinate:
            result = coordinator.run_full_coordination()
            print(json.dumps(result, indent=2))
        elif args.check:
            connectivity = coordinator.check_network_connectivity()
            print(json.dumps(connectivity, indent=2))
        elif args.update_cursor:
            result = coordinator.update_cursor_config()
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()