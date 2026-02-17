#!/usr/bin/env python3
"""
Homelab Control Interface Discovery System

Discovers and maps all commands, APIs, and CLIs available for controlling
every device, feature, function, and option in the homelab.

Creates a comprehensive control map for complete homelab control.

Tags: #HOMELAB #CONTROL #API #CLI #COMMANDS #MAP @JARVIS @LUMINA
"""

import json
import platform
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
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

logger = get_logger("homelab_control_interface_discovery")


@dataclass
class Command:
    """Represents a CLI command"""

    command_id: str
    name: str
    command: str  # The actual command string
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    requires_admin: bool = False
    platform: Optional[str] = None  # "windows", "linux", "all"
    category: str = "general"
    device_id: Optional[str] = None
    feature_id: Optional[str] = None


@dataclass
class APIEndpoint:
    """Represents an API endpoint"""

    endpoint_id: str
    name: str
    url: str
    method: str  # "GET", "POST", "PUT", "DELETE", etc.
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    authentication: Optional[str] = None  # "none", "basic", "bearer", "api_key"
    examples: List[Dict[str, Any]] = field(default_factory=list)
    response_format: str = "json"  # "json", "xml", "text", "binary"
    device_id: Optional[str] = None
    feature_id: Optional[str] = None


@dataclass
class CLITool:
    """Represents a CLI tool/interface"""

    cli_id: str
    name: str
    executable: str  # Path or command name
    description: Optional[str] = None
    version: Optional[str] = None
    available: bool = False
    commands: List[Command] = field(default_factory=list)
    device_id: Optional[str] = None
    installation_path: Optional[str] = None


@dataclass
class ControlInterface:
    """Complete control interface for a device/feature"""

    interface_id: str
    device_id: str
    feature_id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    commands: List[Command] = field(default_factory=list)
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    cli_tools: List[CLITool] = field(default_factory=list)
    control_type: str = "mixed"  # "command", "api", "cli", "mixed"
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CommandDiscovery:
    """Discovers available commands"""

    def discover_windows_commands(self, device_id: str) -> List[Command]:
        """Discover Windows commands"""
        commands = []

        # PowerShell commands
        powershell_cmds = [
            ("Get-Process", "List running processes", ["-Name", "-Id"]),
            ("Get-Service", "List Windows services", ["-Name", "-Status"]),
            ("Get-NetAdapter", "List network adapters", ["-Name", "-InterfaceIndex"]),
            ("Get-Disk", "List disk drives", ["-Number", "-FriendlyName"]),
            ("Get-Volume", "List volumes", ["-DriveLetter", "-FileSystemLabel"]),
            ("Get-WmiObject", "WMI queries", ["-Class", "-Filter"]),
            ("Restart-Computer", "Restart computer", ["-Force", "-Timeout"]),
            ("Stop-Service", "Stop a service", ["-Name", "-Force"]),
            ("Start-Service", "Start a service", ["-Name"]),
            ("Set-Service", "Configure a service", ["-Name", "-StartupType"]),
        ]

        for cmd_name, desc, params in powershell_cmds:
            commands.append(
                Command(
                    command_id=f"{device_id}_cmd_powershell_{cmd_name.lower().replace('-', '_')}",
                    name=cmd_name,
                    command=f'powershell -Command "{cmd_name}',
                    description=desc,
                    parameters=[{"name": p, "type": "string"} for p in params],
                    examples=[f'powershell -Command "{cmd_name} -Name *"'],
                    requires_admin=False,
                    platform="windows",
                    category="powershell",
                    device_id=device_id,
                )
            )

        # CMD commands
        cmd_commands = [
            ("ipconfig", "Display IP configuration", ["/all", "/release", "/renew"]),
            ("systeminfo", "Display system information", []),
            ("tasklist", "List running tasks", ["/svc", "/m"]),
            ("taskkill", "Kill a task", ["/pid", "/im", "/f"]),
            ("netstat", "Display network connections", ["-an", "-o"]),
            ("sc", "Service control", ["query", "start", "stop", "config"]),
            ("wmic", "Windows Management Instrumentation", ["process", "service", "diskdrive"]),
        ]

        for cmd_name, desc, params in cmd_commands:
            commands.append(
                Command(
                    command_id=f"{device_id}_cmd_cmd_{cmd_name}",
                    name=cmd_name,
                    command=cmd_name,
                    description=desc,
                    parameters=[{"name": p, "type": "string"} for p in params],
                    examples=[f"{cmd_name} {' '.join(params[:1]) if params else ''}"],
                    requires_admin=False,
                    platform="windows",
                    category="cmd",
                    device_id=device_id,
                )
            )

        return commands

    def discover_linux_commands(self, device_id: str) -> List[Command]:
        """Discover Linux commands"""
        commands = []

        linux_cmds = [
            ("ps", "List processes", ["-aux", "-ef", "-p"]),
            (
                "systemctl",
                "Systemd service control",
                ["status", "start", "stop", "restart", "enable", "disable"],
            ),
            ("ip", "Network configuration", ["addr", "link", "route"]),
            ("df", "Disk space", ["-h", "-T"]),
            ("lsblk", "List block devices", ["-f", "-o"]),
            ("ss", "Socket statistics", ["-tuln", "-tulpn"]),
            ("netstat", "Network statistics", ["-tuln", "-tulpn"]),
            ("journalctl", "System logs", ["-u", "-f", "-n"]),
            ("docker", "Docker commands", ["ps", "images", "exec", "logs"]),
            ("kubectl", "Kubernetes commands", ["get", "describe", "exec", "logs"]),
        ]

        for cmd_name, desc, params in linux_cmds:
            commands.append(
                Command(
                    command_id=f"{device_id}_cmd_linux_{cmd_name}",
                    name=cmd_name,
                    command=cmd_name,
                    description=desc,
                    parameters=[{"name": p, "type": "string"} for p in params],
                    examples=[f"{cmd_name} {params[0] if params else ''}"],
                    requires_admin=False,
                    platform="linux",
                    category="linux",
                    device_id=device_id,
                )
            )

        return commands

    def discover_synology_dsm_commands(self, device_id: str, ip_address: str) -> List[Command]:
        """Discover Synology DSM commands"""
        commands = []

        # SSH commands for DSM
        dsm_cmds = [
            ("synoservice", "DSM service control", ["--status", "--start", "--stop", "--restart"]),
            ("synopkg", "DSM package management", ["list", "status", "start", "stop"]),
            ("synoshare", "Share management", ["--get", "--list"]),
            ("synouser", "User management", ["--get", "--list"]),
            ("synogroup", "Group management", ["--get", "--list"]),
            ("synovfs", "Virtual file system", ["--get", "--list"]),
        ]

        for cmd_name, desc, params in dsm_cmds:
            commands.append(
                Command(
                    command_id=f"{device_id}_cmd_dsm_{cmd_name}",
                    name=cmd_name,
                    command=f"ssh admin@{ip_address} {cmd_name}",
                    description=f"DSM: {desc}",
                    parameters=[{"name": p, "type": "string"} for p in params],
                    examples=[f"ssh admin@{ip_address} {cmd_name} {params[0] if params else ''}"],
                    requires_admin=True,
                    platform="linux",
                    category="dsm",
                    device_id=device_id,
                )
            )

        return commands


class APIDiscovery:
    """Discovers API endpoints"""

    def discover_ollama_api(self, device_id: str, base_url: str) -> List[APIEndpoint]:
        """Discover Ollama API endpoints"""
        endpoints = []

        ollama_endpoints = [
            {
                "name": "List Models",
                "path": "/api/tags",
                "method": "GET",
                "description": "List all available models",
                "parameters": [],
            },
            {
                "name": "Chat Completion",
                "path": "/api/chat",
                "method": "POST",
                "description": "Chat with a model",
                "parameters": [
                    {"name": "model", "type": "string", "required": True},
                    {"name": "messages", "type": "array", "required": True},
                    {"name": "stream", "type": "boolean", "required": False},
                ],
            },
            {
                "name": "Generate Text",
                "path": "/api/generate",
                "method": "POST",
                "description": "Generate text",
                "parameters": [
                    {"name": "model", "type": "string", "required": True},
                    {"name": "prompt", "type": "string", "required": True},
                ],
            },
            {
                "name": "Pull Model",
                "path": "/api/pull",
                "method": "POST",
                "description": "Download a model",
                "parameters": [{"name": "name", "type": "string", "required": True}],
            },
            {
                "name": "Show Model Info",
                "path": "/api/show",
                "method": "POST",
                "description": "Show model information",
                "parameters": [{"name": "name", "type": "string", "required": True}],
            },
        ]

        for ep in ollama_endpoints:
            endpoints.append(
                APIEndpoint(
                    endpoint_id=f"{device_id}_api_ollama_{ep['path'].replace('/', '_')}",
                    name=ep["name"],
                    url=f"{base_url}{ep['path']}",
                    method=ep["method"],
                    description=ep["description"],
                    parameters=ep.get("parameters", []),
                    authentication="none",
                    examples=[
                        {
                            "method": ep["method"],
                            "url": f"{base_url}{ep['path']}",
                            "body": {} if ep["method"] == "GET" else {"model": "llama3.2:3b"},
                        }
                    ],
                    response_format="json",
                    device_id=device_id,
                )
            )

        return endpoints

    def discover_synology_dsm_api(self, device_id: str, ip_address: str) -> List[APIEndpoint]:
        """Discover Synology DSM API endpoints"""
        endpoints = []

        base_url = f"http://{ip_address}:5000/webapi"

        dsm_apis = [
            {
                "name": "Login",
                "path": "/auth.cgi",
                "method": "GET",
                "description": "Authenticate to DSM",
                "parameters": [
                    {"name": "api", "type": "string", "required": True, "default": "SYNO.API.Auth"},
                    {"name": "version", "type": "integer", "required": True, "default": 3},
                    {"name": "method", "type": "string", "required": True, "default": "login"},
                    {"name": "account", "type": "string", "required": True},
                    {"name": "passwd", "type": "string", "required": True},
                ],
                "auth": "session",
            },
            {
                "name": "List Packages",
                "path": "/query.cgi",
                "method": "GET",
                "description": "List installed packages",
                "parameters": [
                    {
                        "name": "api",
                        "type": "string",
                        "required": True,
                        "default": "SYNO.Core.Package",
                    },
                    {"name": "version", "type": "integer", "required": True, "default": 1},
                    {"name": "method", "type": "string", "required": True, "default": "list"},
                ],
                "auth": "session",
            },
            {
                "name": "List Services",
                "path": "/query.cgi",
                "method": "GET",
                "description": "List services",
                "parameters": [
                    {
                        "name": "api",
                        "type": "string",
                        "required": True,
                        "default": "SYNO.Core.Service",
                    },
                    {"name": "version", "type": "integer", "required": True, "default": 1},
                    {"name": "method", "type": "string", "required": True, "default": "list"},
                ],
                "auth": "session",
            },
            {
                "name": "System Info",
                "path": "/query.cgi",
                "method": "GET",
                "description": "Get system information",
                "parameters": [
                    {
                        "name": "api",
                        "type": "string",
                        "required": True,
                        "default": "SYNO.Core.System",
                    },
                    {"name": "version", "type": "integer", "required": True, "default": 1},
                    {"name": "method", "type": "string", "required": True, "default": "info"},
                ],
                "auth": "session",
            },
            {
                "name": "Storage Info",
                "path": "/query.cgi",
                "method": "GET",
                "description": "Get storage information",
                "parameters": [
                    {
                        "name": "api",
                        "type": "string",
                        "required": True,
                        "default": "SYNO.Storage.CGI.Storage",
                    },
                    {"name": "version", "type": "integer", "required": True, "default": 1},
                    {"name": "method", "type": "string", "required": True, "default": "load_info"},
                ],
                "auth": "session",
            },
        ]

        for api in dsm_apis:
            endpoints.append(
                APIEndpoint(
                    endpoint_id=f"{device_id}_api_dsm_{api['name'].lower().replace(' ', '_')}",
                    name=api["name"],
                    url=f"{base_url}{api['path']}",
                    method=api["method"],
                    description=f"DSM API: {api['description']}",
                    parameters=api.get("parameters", []),
                    authentication=api.get("auth", "session"),
                    examples=[
                        {
                            "method": api["method"],
                            "url": f"{base_url}{api['path']}",
                            "query_params": {
                                p["name"]: p.get("default", "") for p in api.get("parameters", [])
                            },
                        }
                    ],
                    response_format="json",
                    device_id=device_id,
                )
            )

        return endpoints

    def discover_ultron_router_api(self, device_id: str, base_url: str) -> List[APIEndpoint]:
        """Discover ULTRON router API endpoints"""
        endpoints = []

        router_apis = [
            {
                "name": "Health Check",
                "path": "/health",
                "method": "GET",
                "description": "Check router health",
            },
            {
                "name": "Chat Completion",
                "path": "/v1/chat/completions",
                "method": "POST",
                "description": "Chat completion via router",
                "parameters": [
                    {"name": "model", "type": "string", "required": True},
                    {"name": "messages", "type": "array", "required": True},
                ],
            },
            {
                "name": "Cluster Status",
                "path": "/api/status",
                "method": "GET",
                "description": "Get cluster status",
            },
        ]

        for api in router_apis:
            endpoints.append(
                APIEndpoint(
                    endpoint_id=f"{device_id}_api_router_{api['path'].replace('/', '_')}",
                    name=api["name"],
                    url=f"{base_url}{api['path']}",
                    method=api["method"],
                    description=api["description"],
                    parameters=api.get("parameters", []),
                    authentication="none",
                    examples=[{"method": api["method"], "url": f"{base_url}{api['path']}"}],
                    response_format="json",
                    device_id=device_id,
                )
            )

        return endpoints


class CLIDiscovery:
    """Discovers CLI tools"""

    def discover_cli_tools(self, device_id: str, device_type: str, os_type: str) -> List[CLITool]:
        """Discover available CLI tools"""
        cli_tools = []

        # Common CLI tools
        common_tools = [
            ("curl", "HTTP client", "curl"),
            ("wget", "HTTP downloader", "wget"),
            ("ssh", "SSH client", "ssh"),
            ("scp", "Secure copy", "scp"),
            ("rsync", "File synchronization", "rsync"),
            ("git", "Version control", "git"),
            ("docker", "Container platform", "docker"),
            ("kubectl", "Kubernetes CLI", "kubectl"),
            ("terraform", "Infrastructure as code", "terraform"),
            ("ansible", "Configuration management", "ansible"),
        ]

        for tool_name, desc, executable in common_tools:
            available = self._check_tool_available(executable)

            if available:
                version = self._get_tool_version(executable)

                cli_tools.append(
                    CLITool(
                        cli_id=f"{device_id}_cli_{tool_name}",
                        name=tool_name,
                        executable=executable,
                        description=desc,
                        version=version,
                        available=True,
                        device_id=device_id,
                    )
                )

        # OS-specific tools
        if os_type == "Windows":
            windows_tools = [
                ("powershell", "PowerShell", "powershell"),
                ("cmd", "Command Prompt", "cmd"),
                ("wsl", "Windows Subsystem for Linux", "wsl"),
            ]

            for tool_name, desc, executable in windows_tools:
                available = self._check_tool_available(executable)
                if available:
                    cli_tools.append(
                        CLITool(
                            cli_id=f"{device_id}_cli_{tool_name}",
                            name=tool_name,
                            executable=executable,
                            description=desc,
                            available=True,
                            device_id=device_id,
                        )
                    )

        elif os_type == "Linux" or "Synology" in os_type:
            linux_tools = [
                ("systemctl", "Systemd control", "systemctl"),
                ("journalctl", "System logs", "journalctl"),
                ("synoservice", "DSM services", "synoservice"),
                ("synopkg", "DSM packages", "synopkg"),
            ]

            for tool_name, desc, executable in linux_tools:
                available = self._check_tool_available(executable)
                if available:
                    cli_tools.append(
                        CLITool(
                            cli_id=f"{device_id}_cli_{tool_name}",
                            name=tool_name,
                            executable=executable,
                            description=desc,
                            available=True,
                            device_id=device_id,
                        )
                    )

        return cli_tools

    def _check_tool_available(self, executable: str) -> bool:
        """Check if CLI tool is available"""
        try:
            result = subprocess.run(
                [executable, "--version"] if executable != "cmd" else ["cmd", "/c", "ver"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except:
            try:
                # Try without --version flag
                result = subprocess.run(
                    ["where", executable]
                    if platform.system() == "Windows"
                    else ["which", executable],
                    capture_output=True,
                    timeout=5,
                )
                return result.returncode == 0
            except:
                return False

    def _get_tool_version(self, executable: str) -> Optional[str]:
        """Get CLI tool version"""
        try:
            result = subprocess.run(
                [executable, "--version"], capture_output=True, timeout=5, text=True
            )
            if result.returncode == 0:
                # Extract version from output
                output = result.stdout.strip()
                version_match = re.search(r"(\d+\.\d+\.\d+)", output)
                if version_match:
                    return version_match.group(1)
                return output.split("\n")[0] if output else None
        except:
            pass
        return None


class ControlInterfaceMapper:
    """Maps all control interfaces for homelab"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.command_discovery = CommandDiscovery()
        self.api_discovery = APIDiscovery()
        self.cli_discovery = CLIDiscovery()
        self.control_interfaces: List[ControlInterface] = []

    def map_device_control_interfaces(self, device: Dict[str, Any]) -> ControlInterface:
        """Map all control interfaces for a device"""
        device_id = device["device_id"]
        device_type = device.get("device_type", "")
        os_type = device.get("operating_system", "")
        ip_address = device.get("ip_address", "")

        interface = ControlInterface(
            interface_id=f"{device_id}_control",
            device_id=device_id,
            name=f"{device.get('device_name', 'Unknown')} Control Interface",
            description=f"Control interfaces for {device.get('device_name', 'Unknown')}",
        )

        # Discover commands
        if os_type == "Windows":
            interface.commands.extend(self.command_discovery.discover_windows_commands(device_id))
        elif os_type == "Linux" or "Synology" in os_type:
            interface.commands.extend(self.command_discovery.discover_linux_commands(device_id))
            if device_type == "nas" or "Synology" in os_type:
                interface.commands.extend(
                    self.command_discovery.discover_synology_dsm_commands(device_id, ip_address)
                )

        # Discover APIs
        # Check for Ollama
        if ip_address:
            ollama_urls = [
                f"http://{ip_address}:11434",
                "http://localhost:11434",
                f"http://{ip_address}:11437",
            ]
            for url in ollama_urls:
                try:
                    response = requests.get(f"{url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        interface.api_endpoints.extend(
                            self.api_discovery.discover_ollama_api(device_id, url)
                        )
                        break
                except:
                    pass

        # Check for ULTRON router
        router_urls = [f"http://{ip_address}:8080", "http://localhost:8080"]
        for url in router_urls:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    interface.api_endpoints.extend(
                        self.api_discovery.discover_ultron_router_api(device_id, url)
                    )
                    break
            except:
                pass

        # Check for Synology DSM API
        if device_type == "nas" or "Synology" in os_type:
            interface.api_endpoints.extend(
                self.api_discovery.discover_synology_dsm_api(device_id, ip_address)
            )

        # Discover CLI tools
        interface.cli_tools.extend(
            self.cli_discovery.discover_cli_tools(device_id, device_type, os_type)
        )

        # Determine control type
        if interface.commands and not interface.api_endpoints and not interface.cli_tools:
            interface.control_type = "command"
        elif interface.api_endpoints and not interface.commands and not interface.cli_tools:
            interface.control_type = "api"
        elif interface.cli_tools and not interface.commands and not interface.api_endpoints:
            interface.control_type = "cli"
        else:
            interface.control_type = "mixed"

        return interface

    def map_all_devices(self, audit_file: Path) -> List[ControlInterface]:
        """Map control interfaces for all devices in audit"""
        with open(audit_file, encoding="utf-8") as f:
            audit_data = json.load(f)

        interfaces = []
        for device in audit_data.get("devices", []):
            interface = self.map_device_control_interfaces(device)
            interfaces.append(interface)
            self.control_interfaces.append(interface)

        return interfaces

    def save_control_map(self, output_file: Path):
        """Save control interface map"""
        control_map = {
            "map_id": f"control_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "total_interfaces": len(self.control_interfaces),
            "total_commands": sum(len(i.commands) for i in self.control_interfaces),
            "total_api_endpoints": sum(len(i.api_endpoints) for i in self.control_interfaces),
            "total_cli_tools": sum(len(i.cli_tools) for i in self.control_interfaces),
            "interfaces": [asdict(i) for i in self.control_interfaces],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(control_map, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Control map saved: {output_file}")
        return control_map


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Discover and map homelab control interfaces")
    parser.add_argument("--audit-file", help="Audit file to use (default: latest)")
    parser.add_argument("--output", help="Output file (default: control_map_<timestamp>.json)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    mapper = ControlInterfaceMapper(project_root)

    # Find audit file
    audit_dir = project_root / "data" / "homelab_audit"
    if args.audit_file:
        audit_file = Path(args.audit_file)
    else:
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        if not audit_files:
            print("❌ No audit files found")
            sys.exit(1)
        audit_file = audit_files[0]
        print(f"Using audit: {audit_file.name}")

    # Map control interfaces
    print("Discovering control interfaces...")
    interfaces = mapper.map_all_devices(audit_file)

    # Save map
    output_dir = project_root / "data" / "homelab_control"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"control_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    control_map = mapper.save_control_map(output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("CONTROL INTERFACE MAP SUMMARY")
    print("=" * 80)
    print(f"Total Interfaces: {control_map['total_interfaces']}")
    print(f"Total Commands: {control_map['total_commands']}")
    print(f"Total API Endpoints: {control_map['total_api_endpoints']}")
    print(f"Total CLI Tools: {control_map['total_cli_tools']}")
    print(f"\nMap saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(control_map, indent=2, default=str))


if __name__ == "__main__":
    main()
