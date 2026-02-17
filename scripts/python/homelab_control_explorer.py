#!/usr/bin/env python3
"""
Homelab Control Explorer

Interactive explorer and unified control interface for all homelab devices.
Provides command execution, API testing, and CLI tool access.

Tags: #HOMELAB #CONTROL #EXPLORER #UNIFIED @JARVIS @LUMINA
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_control_explorer")


class HomelabControlExplorer:
    """Unified control interface for homelab"""

    def __init__(self, control_map_file: Optional[Path] = None):
        self.project_root = project_root
        self.control_map: Dict[str, Any] = {}
        self.interfaces: List[Dict[str, Any]] = []

        if control_map_file:
            self.load_control_map(control_map_file)
        else:
            # Find latest control map
            control_dir = project_root / "data" / "homelab_control"
            if control_dir.exists():
                maps = sorted(control_dir.glob("control_map_*.json"), reverse=True)
                if maps:
                    self.load_control_map(maps[0])

    def load_control_map(self, map_file: Path):
        """Load control interface map"""
        with open(map_file, encoding="utf-8") as f:
            self.control_map = json.load(f)
            self.interfaces = self.control_map.get("interfaces", [])
        logger.info(f"Loaded control map: {len(self.interfaces)} interfaces")

    def list_devices(self) -> List[Dict[str, Any]]:
        """List all devices with control interfaces"""
        devices = []
        for interface in self.interfaces:
            devices.append(
                {
                    "device_id": interface["device_id"],
                    "name": interface["name"],
                    "control_type": interface["control_type"],
                    "commands_count": len(interface.get("commands", [])),
                    "api_endpoints_count": len(interface.get("api_endpoints", [])),
                    "cli_tools_count": len(interface.get("cli_tools", [])),
                }
            )
        return devices

    def get_device_commands(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all commands for a device"""
        for interface in self.interfaces:
            if interface["device_id"] == device_id:
                return interface.get("commands", [])
        return []

    def get_device_apis(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all API endpoints for a device"""
        for interface in self.interfaces:
            if interface["device_id"] == device_id:
                return interface.get("api_endpoints", [])
        return []

    def get_device_clis(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all CLI tools for a device"""
        for interface in self.interfaces:
            if interface["device_id"] == device_id:
                return interface.get("cli_tools", [])
        return []

    def execute_command(self, command_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command"""
        # Find command
        command = None
        for interface in self.interfaces:
            for cmd in interface.get("commands", []):
                if cmd["command_id"] == command_id:
                    command = cmd
                    break
            if command:
                break

        if not command:
            return {"success": False, "error": f"Command not found: {command_id}"}

        # Build command string
        cmd_str = command["command"]
        if parameters:
            # Add parameters to command
            for key, value in parameters.items():
                cmd_str += f" {key} {value}"

        # Execute
        try:
            if command.get("platform") == "windows":
                # Windows execution
                if "powershell" in cmd_str.lower():
                    result = subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            cmd_str.replace('powershell -Command "', "").rstrip('"'),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                else:
                    result = subprocess.run(
                        cmd_str.split(), capture_output=True, text=True, timeout=30
                    )
            else:
                # Linux/Unix execution
                result = subprocess.run(cmd_str.split(), capture_output=True, text=True, timeout=30)

            return {
                "success": result.returncode == 0,
                "command": cmd_str,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": cmd_str}

    def test_api_endpoint(
        self, endpoint_id: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test an API endpoint"""
        # Find endpoint
        endpoint = None
        for interface in self.interfaces:
            for api in interface.get("api_endpoints", []):
                if api["endpoint_id"] == endpoint_id:
                    endpoint = api
                    break
            if endpoint:
                break

        if not endpoint:
            return {"success": False, "error": f"Endpoint not found: {endpoint_id}"}

        # Make request
        try:
            url = endpoint["url"]
            method = endpoint["method"]

            if method == "GET":
                response = requests.get(url, params=parameters or {}, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=parameters or {}, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=parameters or {}, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}

            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "url": url,
                "method": method,
                "response": response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else response.text,
                "headers": dict(response.headers),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "url": endpoint.get("url")}

    def explore_device(self, device_id: str) -> Dict[str, Any]:
        """Explore all control interfaces for a device"""
        exploration = {
            "device_id": device_id,
            "commands": self.get_device_commands(device_id),
            "api_endpoints": self.get_device_apis(device_id),
            "cli_tools": self.get_device_clis(device_id),
            "summary": {
                "total_commands": len(self.get_device_commands(device_id)),
                "total_apis": len(self.get_device_apis(device_id)),
                "total_clis": len(self.get_device_clis(device_id)),
            },
        }
        return exploration

    def search_control_interfaces(self, query: str) -> Dict[str, Any]:
        """Search control interfaces by name, description, or command"""
        results = {"commands": [], "api_endpoints": [], "cli_tools": [], "interfaces": []}

        query_lower = query.lower()

        for interface in self.interfaces:
            # Search commands
            for cmd in interface.get("commands", []):
                if (
                    query_lower in cmd.get("name", "").lower()
                    or query_lower in cmd.get("command", "").lower()
                    or query_lower in cmd.get("description", "").lower()
                ):
                    results["commands"].append(
                        {
                            "command": cmd,
                            "device_id": interface["device_id"],
                            "device_name": interface["name"],
                        }
                    )

            # Search APIs
            for api in interface.get("api_endpoints", []):
                if (
                    query_lower in api.get("name", "").lower()
                    or query_lower in api.get("url", "").lower()
                    or query_lower in api.get("description", "").lower()
                ):
                    results["api_endpoints"].append(
                        {
                            "endpoint": api,
                            "device_id": interface["device_id"],
                            "device_name": interface["name"],
                        }
                    )

            # Search CLIs
            for cli in interface.get("cli_tools", []):
                if (
                    query_lower in cli.get("name", "").lower()
                    or query_lower in cli.get("executable", "").lower()
                    or query_lower in cli.get("description", "").lower()
                ):
                    results["cli_tools"].append(
                        {
                            "cli": cli,
                            "device_id": interface["device_id"],
                            "device_name": interface["name"],
                        }
                    )

        return results

    def generate_control_map_report(self) -> str:
        """Generate human-readable control map report"""
        report = []
        report.append("=" * 80)
        report.append("HOMELAB CONTROL INTERFACE MAP")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Interfaces: {len(self.interfaces)}")
        report.append(f"Total Commands: {sum(len(i.get('commands', [])) for i in self.interfaces)}")
        report.append(
            f"Total API Endpoints: {sum(len(i.get('api_endpoints', [])) for i in self.interfaces)}"
        )
        report.append(
            f"Total CLI Tools: {sum(len(i.get('cli_tools', [])) for i in self.interfaces)}"
        )
        report.append("")

        for interface in self.interfaces:
            report.append(f"Device: {interface['name']}")
            report.append(f"  Device ID: {interface['device_id']}")
            report.append(f"  Control Type: {interface['control_type']}")
            report.append("")

            # Commands
            if interface.get("commands"):
                report.append(f"  Commands ({len(interface['commands'])}):")
                for cmd in interface["commands"][:10]:  # Show first 10
                    report.append(f"    - {cmd['name']}: {cmd['command']}")
                if len(interface["commands"]) > 10:
                    report.append(f"    ... and {len(interface['commands']) - 10} more")
                report.append("")

            # APIs
            if interface.get("api_endpoints"):
                report.append(f"  API Endpoints ({len(interface['api_endpoints'])}):")
                for api in interface["api_endpoints"][:10]:  # Show first 10
                    report.append(f"    - {api['name']}: {api['method']} {api['url']}")
                if len(interface["api_endpoints"]) > 10:
                    report.append(f"    ... and {len(interface['api_endpoints']) - 10} more")
                report.append("")

            # CLIs
            if interface.get("cli_tools"):
                report.append(f"  CLI Tools ({len(interface['cli_tools'])}):")
                for cli in interface["cli_tools"]:
                    status = "✅" if cli.get("available") else "❌"
                    report.append(f"    {status} {cli['name']}: {cli.get('executable', 'N/A')}")
                report.append("")

            report.append("-" * 80)
            report.append("")

        return "\n".join(report)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab Control Explorer")
    parser.add_argument("--map-file", help="Control map file (default: latest)")
    parser.add_argument("--list-devices", action="store_true", help="List all devices")
    parser.add_argument("--explore", metavar="DEVICE_ID", help="Explore device control interfaces")
    parser.add_argument("--search", metavar="QUERY", help="Search control interfaces")
    parser.add_argument("--execute", metavar="COMMAND_ID", help="Execute a command")
    parser.add_argument("--test-api", metavar="ENDPOINT_ID", help="Test an API endpoint")
    parser.add_argument("--report", action="store_true", help="Generate control map report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    map_file = Path(args.map_file) if args.map_file else None
    explorer = HomelabControlExplorer(map_file)

    if args.list_devices:
        devices = explorer.list_devices()
        if args.json:
            print(json.dumps(devices, indent=2, default=str))
        else:
            print("Devices with Control Interfaces:")
            for device in devices:
                print(f"  {device['name']} ({device['device_id']})")
                print(f"    Type: {device['control_type']}")
                print(
                    f"    Commands: {device['commands_count']}, APIs: {device['api_endpoints_count']}, CLIs: {device['cli_tools_count']}"
                )
                print()

    elif args.explore:
        exploration = explorer.explore_device(args.explore)
        if args.json:
            print(json.dumps(exploration, indent=2, default=str))
        else:
            print(f"Exploring: {args.explore}")
            print(f"Commands: {exploration['summary']['total_commands']}")
            print(f"APIs: {exploration['summary']['total_apis']}")
            print(f"CLIs: {exploration['summary']['total_clis']}")

    elif args.search:
        results = explorer.search_control_interfaces(args.search)
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"Search Results for: {args.search}")
            print(f"Commands: {len(results['commands'])}")
            print(f"APIs: {len(results['api_endpoints'])}")
            print(f"CLIs: {len(results['cli_tools'])}")

    elif args.execute:
        result = explorer.execute_command(args.execute)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print("✅ Command executed successfully")
                print(result.get("stdout", ""))
            else:
                print("❌ Command failed")
                print(result.get("error", result.get("stderr", "")))

    elif args.test_api:
        result = explorer.test_api_endpoint(args.test_api)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print("✅ API test successful")
                print(f"Status: {result['status_code']}")
                print(f"Response: {result.get('response', '')}")
            else:
                print("❌ API test failed")
                print(result.get("error", ""))

    elif args.report:
        report = explorer.generate_control_map_report()
        print(report)

    else:
        # Default: show report
        report = explorer.generate_control_map_report()
        print(report)


if __name__ == "__main__":
    main()
