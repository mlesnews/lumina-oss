#!/usr/bin/env python3
"""
Homelab Unified Control Interface

Unified interface for controlling all homelab devices via commands, APIs, and CLIs.
Provides single entry point for all control operations.

Tags: #HOMELAB #CONTROL #UNIFIED #COMMANDS #API #CLI @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.homelab_control_explorer import HomelabControlExplorer

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_unified_control")


class HomelabUnifiedControl:
    """Unified control interface for homelab"""

    def __init__(self, control_map_file: Optional[Path] = None):
        self.explorer = HomelabControlExplorer(control_map_file)
        self.execution_history: List[Dict[str, Any]] = []

    def execute_command_by_name(
        self, device_id: str, command_name: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute command by name"""
        commands = self.explorer.get_device_commands(device_id)

        # Find command by name
        command = None
        for cmd in commands:
            if (
                cmd.get("name") == command_name
                or command_name.lower() in cmd.get("name", "").lower()
            ):
                command = cmd
                break

        if not command:
            return {"success": False, "error": f"Command not found: {command_name}"}

        return self.explorer.execute_command(command["command_id"], parameters)

    def call_api_by_name(
        self, device_id: str, api_name: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Call API by name"""
        apis = self.explorer.get_device_apis(device_id)

        # Find API by name
        api = None
        for endpoint in apis:
            if api_name.lower() in endpoint.get("name", "").lower():
                api = endpoint
                break

        if not api:
            return {"success": False, "error": f"API not found: {api_name}"}

        return self.explorer.test_api_endpoint(api["endpoint_id"], parameters)

    def control_device(
        self, device_id: str, action: str, action_type: str = "auto", **kwargs
    ) -> Dict[str, Any]:
        """Unified device control - automatically determines best method"""
        # Determine action type if auto
        if action_type == "auto":
            # Try API first, then command, then CLI
            apis = self.explorer.get_device_apis(device_id)
            commands = self.explorer.get_device_commands(device_id)

            if apis:
                action_type = "api"
            elif commands:
                action_type = "command"
            else:
                action_type = "cli"

        if action_type == "api":
            return self.call_api_by_name(device_id, action, kwargs)
        elif action_type == "command":
            return self.execute_command_by_name(device_id, action, kwargs)
        else:
            return {"success": False, "error": "CLI execution not yet implemented"}

    def get_control_map(self) -> Dict[str, Any]:
        """Get complete control map"""
        devices = self.explorer.list_devices()

        control_map = {
            "devices": [],
            "summary": {
                "total_devices": len(devices),
                "total_commands": 0,
                "total_apis": 0,
                "total_clis": 0,
            },
        }

        for device in devices:
            device_id = device["device_id"]
            exploration = self.explorer.explore_device(device_id)

            control_map["summary"]["total_commands"] += exploration["summary"]["total_commands"]
            control_map["summary"]["total_apis"] += exploration["summary"]["total_apis"]
            control_map["summary"]["total_clis"] += exploration["summary"]["total_clis"]

            control_map["devices"].append(
                {
                    "device_id": device_id,
                    "name": device["name"],
                    "control_type": device["control_type"],
                    "commands": exploration["commands"],
                    "api_endpoints": exploration["api_endpoints"],
                    "cli_tools": exploration["cli_tools"],
                }
            )

        return control_map

    def generate_control_guide(self) -> str:
        """Generate comprehensive control guide"""
        guide = []
        guide.append("=" * 80)
        guide.append("HOMELAB UNIFIED CONTROL GUIDE")
        guide.append("=" * 80)
        guide.append(f"Generated: {datetime.now().isoformat()}")
        guide.append("")

        devices = self.explorer.list_devices()

        for device in devices:
            device_id = device["device_id"]
            guide.append(f"Device: {device['name']}")
            guide.append(f"  ID: {device_id}")
            guide.append(f"  Control Type: {device['control_type']}")
            guide.append("")

            # Commands
            commands = self.explorer.get_device_commands(device_id)
            if commands:
                guide.append(f"  COMMANDS ({len(commands)}):")
                for cmd in commands:
                    guide.append(f"    {cmd['name']}")
                    guide.append(f"      Command: {cmd['command']}")
                    if cmd.get("description"):
                        guide.append(f"      Description: {cmd['description']}")
                    if cmd.get("examples"):
                        guide.append(f"      Example: {cmd['examples'][0]}")
                    guide.append("")

            # APIs
            apis = self.explorer.get_device_apis(device_id)
            if apis:
                guide.append(f"  API ENDPOINTS ({len(apis)}):")
                for api in apis:
                    guide.append(f"    {api['name']}")
                    guide.append(f"      {api['method']} {api['url']}")
                    if api.get("description"):
                        guide.append(f"      Description: {api['description']}")
                    if api.get("parameters"):
                        guide.append(
                            f"      Parameters: {', '.join(p['name'] for p in api['parameters'])}"
                        )
                    guide.append("")

            # CLIs
            clis = self.explorer.get_device_clis(device_id)
            if clis:
                guide.append(f"  CLI TOOLS ({len(clis)}):")
                for cli in clis:
                    status = "✅ Available" if cli.get("available") else "❌ Not Available"
                    guide.append(f"    {status} {cli['name']}: {cli.get('executable', 'N/A')}")
                    if cli.get("version"):
                        guide.append(f"      Version: {cli['version']}")
                guide.append("")

            guide.append("-" * 80)
            guide.append("")

        return "\n".join(guide)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab Unified Control Interface")
    parser.add_argument("--map-file", help="Control map file (default: latest)")
    parser.add_argument(
        "--list", action="store_true", help="List all devices and control interfaces"
    )
    parser.add_argument("--guide", action="store_true", help="Generate control guide")
    parser.add_argument(
        "--execute",
        metavar="DEVICE_ID:COMMAND",
        help="Execute command (format: device_id:command_name)",
    )
    parser.add_argument(
        "--api", metavar="DEVICE_ID:API_NAME", help="Call API (format: device_id:api_name)"
    )
    parser.add_argument(
        "--control", metavar="DEVICE_ID:ACTION", help="Control device (format: device_id:action)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    control = HomelabUnifiedControl(args.map_file)

    if args.list:
        devices = control.explorer.list_devices()
        if args.json:
            print(json.dumps(devices, indent=2, default=str))
        else:
            print("Devices with Control Interfaces:")
            for device in devices:
                print(f"  {device['name']} ({device['device_id']})")
                print(
                    f"    Commands: {device['commands_count']}, APIs: {device['api_endpoints_count']}, CLIs: {device['cli_tools_count']}"
                )

    elif args.guide:
        guide = control.generate_control_guide()
        print(guide)

    elif args.execute:
        device_id, command_name = args.execute.split(":", 1)
        result = control.execute_command_by_name(device_id, command_name)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print("✅ Command executed successfully")
                print(result.get("stdout", ""))
            else:
                print("❌ Command failed")
                print(result.get("error", result.get("stderr", "")))

    elif args.api:
        device_id, api_name = args.api.split(":", 1)
        result = control.call_api_by_name(device_id, api_name)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print("✅ API call successful")
                print(f"Status: {result['status_code']}")
                print(f"Response: {result.get('response', '')}")
            else:
                print("❌ API call failed")
                print(result.get("error", ""))

    elif args.control:
        device_id, action = args.control.split(":", 1)
        result = control.control_device(device_id, action)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print("✅ Control action successful")
                print(result.get("stdout", result.get("response", "")))
            else:
                print("❌ Control action failed")
                print(result.get("error", ""))

    else:
        # Default: show guide
        guide = control.generate_control_guide()
        print(guide)


if __name__ == "__main__":
    main()
