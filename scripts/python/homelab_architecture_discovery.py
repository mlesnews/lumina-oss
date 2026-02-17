#!/usr/bin/env python3
"""
Homelab Architecture Discovery System

Discovers complete architecture from macro to micro:
- Applications and their architecture
- Running services and daemons
- Frameworks (web, application, etc.)
- Service dependencies and relationships
- Process hierarchies
- Configuration files and their relationships

Tags: #HOMELAB #ARCHITECTURE #APPLICATIONS #SERVICES #FRAMEWORKS @JARVIS @LUMINA
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import psutil

# Add project root and scripts/python to path (for lumina_logger)
project_root = Path(__file__).resolve().parent.parent.parent
_scripts_python = project_root / "scripts" / "python"
for _path in (str(project_root), str(_scripts_python)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

logger = get_logger("homelab_architecture_discovery")


def _default_discovered_at() -> str:
    """Return current ISO timestamp for discovered_at fields."""
    return datetime.now().isoformat()


@dataclass
class RunningService:
    """Running service/daemon"""

    service_id: str
    name: str
    display_name: Optional[str] = None
    status: str = "unknown"  # "running", "stopped", "paused"
    startup_type: Optional[str] = None  # "automatic", "manual", "disabled"
    process_id: Optional[int] = None
    executable_path: Optional[str] = None
    description: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    device_id: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RunningProcess:
    """Running process"""

    process_id: int
    name: str
    executable_path: Optional[str] = None
    command_line: Optional[str] = None
    working_directory: Optional[str] = None
    parent_process_id: Optional[int] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "unknown"
    username: Optional[str] = None
    device_id: str = ""
    discovered_at: str = field(default_factory=_default_discovered_at)


@dataclass
class Application:
    """Application with architecture"""

    application_id: str
    name: str
    type: str = "unknown"  # "web", "desktop", "service", "api", "database", "container"
    framework: Optional[str] = None  # "flask", "django", "express", "spring", etc.
    version: Optional[str] = None
    executable_path: Optional[str] = None
    working_directory: Optional[str] = None
    configuration_files: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    architecture: Dict[str, Any] = field(default_factory=dict)
    device_id: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Framework:
    """Framework discovery"""

    framework_id: str
    name: str
    type: str = "unknown"  # "web", "api", "database", "orchestration", "monitoring"
    version: Optional[str] = None
    applications: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    device_id: str = ""
    discovered_at: str = field(default_factory=_default_discovered_at)


@dataclass
class ArchitectureLayer:
    """Architecture layer (macro to micro)"""

    layer_id: str
    layer_name: str
    level: int  # 0 = macro (network), higher = micro (process)
    components: List[str] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)


class WindowsServiceDiscovery:
    """Discover Windows services"""

    def discover_services(self, device_id: str) -> List[RunningService]:
        """Discover Windows services"""
        services = []

        try:
            ps_cmd = (
                "Get-Service | Select-Object Name, DisplayName, Status, StartType, "
                "@{Name='ProcessId';Expression={(Get-WmiObject Win32_Service -Filter "
                "\"Name='$($_.Name)'\").ProcessId}} | ConvertTo-Json -Depth 3"
            )
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode == 0 and (result.stdout or "").strip():
                svc_data = json.loads(result.stdout)
                if not isinstance(svc_data, list):
                    svc_data = [svc_data]

                for svc in svc_data:
                    if not isinstance(svc, dict) or "Name" not in svc:
                        continue
                    # Get service dependencies
                    deps = []
                    try:
                        dep_cmd = (
                            "Get-Service -Name '"
                            + str(svc.get("Name", "")).replace("'", "''")
                            + "' | Select-Object -ExpandProperty ServicesDependedOn "
                            "| Select-Object -ExpandProperty Name"
                        )
                        dep_result = subprocess.run(
                            ["powershell", "-Command", dep_cmd],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            check=False,
                        )
                        if dep_result.returncode == 0 and (dep_result.stdout or "").strip():
                            deps = [
                                d.strip()
                                for d in (dep_result.stdout or "").strip().split("\n")
                                if d.strip()
                            ]
                    except Exception:
                        pass

                    status_val = svc.get("Status", "unknown")
                    if isinstance(status_val, str):
                        status_val = status_val.lower()
                    else:
                        status_val = "unknown"

                    startup_val = svc.get("StartType", "")
                    if isinstance(startup_val, str):
                        startup_val = startup_val.lower()
                    else:
                        startup_val = str(startup_val).lower()

                    services.append(
                        RunningService(
                            service_id=f"{device_id}_svc_{svc['Name']}",
                            name=svc["Name"],
                            display_name=svc.get("DisplayName"),
                            status=status_val,
                            startup_type=startup_val,
                            process_id=svc.get("ProcessId"),
                            dependencies=deps,
                            device_id=device_id,
                        )
                    )
        except Exception as e:
            logger.warning("Failed to discover Windows services: %s", e)

        return services


class LinuxServiceDiscovery:
    """Discover Linux services"""

    def discover_services(self, device_id: str) -> List[RunningService]:
        """Discover Linux services (systemd)"""
        services = []

        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "list-units",
                    "--type=service",
                    "--all",
                    "--no-pager",
                    "--output=json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode == 0 and (result.stdout or "").strip():
                raw = json.loads(result.stdout)
                if isinstance(raw, dict) and "units" in raw:
                    units = raw["units"]
                elif isinstance(raw, list):
                    units = raw
                else:
                    units = [raw] if raw is not None else []

                for unit in units:
                    unit_name = unit.get("unit", "")
                    if not unit_name.endswith(".service"):
                        continue

                    # Get service details
                    try:
                        status_result = subprocess.run(
                            [
                                "systemctl",
                                "show",
                                unit_name,
                                "--property=ActiveState,SubState,LoadState,MainPID,Description",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            check=False,
                        )

                        details = {}
                        if status_result.returncode == 0 and (status_result.stdout or "").strip():
                            for line in (status_result.stdout or "").strip().split("\n"):
                                if "=" in line:
                                    key, value = line.split("=", 1)
                                    details[key] = value

                        # Get dependencies
                        deps = []
                        try:
                            dep_result = subprocess.run(
                                ["systemctl", "list-dependencies", unit_name, "--no-pager"],
                                capture_output=True,
                                text=True,
                                timeout=10,
                                check=False,
                            )
                            if dep_result.returncode == 0 and (dep_result.stdout or "").strip():
                                out_lines = (dep_result.stdout or "").strip().split("\n")
                                deps = [
                                    d.strip()
                                    for d in out_lines[1:]
                                    if d.strip() and not d.startswith("├") and not d.startswith("└")
                                ]
                        except Exception:
                            pass

                        services.append(
                            RunningService(
                                service_id=f"{device_id}_svc_{unit_name.replace('.service', '')}",
                                name=unit_name.replace(".service", ""),
                                status=details.get("ActiveState", "unknown").lower(),
                                startup_type=details.get("LoadState", "unknown").lower(),
                                process_id=int(details.get("MainPID", 0))
                                if details.get("MainPID", "0").isdigit()
                                else None,
                                description=details.get("Description"),
                                dependencies=deps,
                                device_id=device_id,
                            )
                        )
                    except Exception as e:
                        logger.debug("Failed to get details for %s: %s", unit_name, e)
        except Exception as e:
            logger.warning("Failed to discover Linux services: %s", e)

        return services


class ProcessDiscovery:
    """Discover running processes"""

    def discover_processes(self, device_id: str) -> List[RunningProcess]:
        """Discover all running processes"""
        processes = []

        try:
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "exe",
                    "cmdline",
                    "cwd",
                    "ppid",
                    "cpu_percent",
                    "memory_info",
                    "status",
                    "username",
                ]
            ):
                try:
                    pinfo = proc.info

                    # Handle memory_info (it's a named tuple, not a dict)
                    memory_mb = 0.0
                    if pinfo.get("memory_info"):
                        mem_info = pinfo["memory_info"]
                        if hasattr(mem_info, "rss"):
                            memory_mb = mem_info.rss / 1024 / 1024
                        elif isinstance(mem_info, dict):
                            memory_mb = mem_info.get("rss", 0) / 1024 / 1024

                    processes.append(
                        RunningProcess(
                            process_id=pinfo["pid"],
                            name=pinfo["name"],
                            executable_path=pinfo.get("exe"),
                            command_line=" ".join(pinfo.get("cmdline", []))
                            if pinfo.get("cmdline")
                            else None,
                            working_directory=pinfo.get("cwd"),
                            parent_process_id=pinfo.get("ppid"),
                            cpu_percent=pinfo.get("cpu_percent", 0.0),
                            memory_mb=memory_mb,
                            status=pinfo.get("status", "unknown"),
                            username=pinfo.get("username"),
                            device_id=device_id,
                        )
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            logger.warning("Failed to discover processes: %s", e)

        return processes


class FrameworkDiscovery:
    """Discover frameworks"""

    def discover_web_frameworks(
        self, processes: List[RunningProcess], device_id: str
    ) -> List[Framework]:
        """Discover web frameworks from processes"""
        frameworks = []
        framework_patterns: Dict[str, str] = {
            "flask": r"flask|Flask",
            "django": r"django|Django",
            "express": r"express|Express|node.*express",
            "spring": r"spring|Spring|java.*spring",
            "rails": r"rails|Rails|ruby.*rails",
            "fastapi": r"fastapi|FastAPI|uvicorn.*fastapi",
            "aspnet": r"aspnet|ASP.NET|dotnet.*web",
            "laravel": r"laravel|Laravel|php.*artisan",
        }

        for proc in processes:
            cmdline = proc.command_line or ""
            exe_path = proc.executable_path or ""

            for framework_name, pattern in framework_patterns.items():
                if re.search(pattern, cmdline) or re.search(pattern, exe_path):
                    frameworks.append(
                        Framework(
                            framework_id=f"{device_id}_framework_{framework_name}_{proc.process_id}",
                            name=framework_name,
                            type="web",
                            applications=[f"{device_id}_app_{proc.process_id}"],
                            device_id=device_id,
                        )
                    )
                    break

        return frameworks

    def discover_container_frameworks(self, device_id: str) -> List[Framework]:
        """Discover container orchestration frameworks"""
        frameworks = []

        # Docker
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                frameworks.append(
                    Framework(
                        framework_id=f"{device_id}_framework_docker",
                        name="Docker",
                        type="orchestration",
                        version=result.stdout.strip(),
                        device_id=device_id,
                    )
                )
        except Exception:
            pass

        # Kubernetes
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client", "--short"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                frameworks.append(
                    Framework(
                        framework_id=f"{device_id}_framework_kubernetes",
                        name="Kubernetes",
                        type="orchestration",
                        device_id=device_id,
                    )
                )
        except Exception:
            pass

        return frameworks


class ApplicationDiscovery:
    """Discover applications and their architecture"""

    def discover_applications(
        self,
        processes: List[RunningProcess],
        _services: List[RunningService],
        device_id: str,
    ) -> List[Application]:
        """Discover applications from processes and services."""
        applications = []

        # Group processes by executable
        process_groups: Dict[str, List[RunningProcess]] = {}
        for proc in processes:
            exe = proc.executable_path or proc.name
            if exe not in process_groups:
                process_groups[exe] = []
            process_groups[exe].append(proc)

        # Identify applications
        for exe, procs in process_groups.items():
            if not exe or len(procs) == 0:
                continue

            main_proc = procs[0]

            # Determine application type
            app_type = self._determine_application_type(main_proc, exe)

            # Discover framework
            framework = self._discover_framework(main_proc)

            # Discover ports
            ports = self._discover_ports(main_proc.process_id)

            # Discover configuration files
            config_files = self._discover_config_files(main_proc)

            # Discover environment variables
            env_vars = self._discover_environment_variables(main_proc.process_id)

            applications.append(
                Application(
                    application_id=f"{device_id}_app_{main_proc.process_id}",
                    name=main_proc.name,
                    type=app_type,
                    framework=framework,
                    executable_path=main_proc.executable_path,
                    working_directory=main_proc.working_directory,
                    configuration_files=config_files,
                    environment_variables=env_vars,
                    ports=ports,
                    device_id=device_id,
                )
            )

        return applications

    def _determine_application_type(self, proc: RunningProcess, exe: str) -> str:
        """Determine application type"""
        exe_lower = exe.lower()
        cmdline = (proc.command_line or "").lower()

        if "python" in exe_lower or "python" in cmdline:
            if "flask" in cmdline or "gunicorn" in cmdline:
                return "web"
            elif "django" in cmdline:
                return "web"
            elif "fastapi" in cmdline or "uvicorn" in cmdline:
                return "api"
            return "application"
        elif "node" in exe_lower or "node" in cmdline:
            if "express" in cmdline:
                return "web"
            return "application"
        elif "java" in exe_lower or "java" in cmdline:
            if "spring" in cmdline:
                return "web"
            return "application"
        elif "nginx" in exe_lower or "apache" in exe_lower:
            return "web"
        elif "mysql" in exe_lower or "postgres" in exe_lower or "mongodb" in exe_lower:
            return "database"
        elif "docker" in exe_lower:
            return "container"
        elif "service" in exe_lower or "daemon" in exe_lower:
            return "service"

        return "unknown"

    def _discover_framework(self, proc: RunningProcess) -> Optional[str]:
        """Discover framework from process"""
        cmdline = (proc.command_line or "").lower()

        frameworks = {
            "flask": "flask" in cmdline,
            "django": "django" in cmdline,
            "express": "express" in cmdline,
            "spring": "spring" in cmdline,
            "rails": "rails" in cmdline,
            "fastapi": "fastapi" in cmdline or "uvicorn" in cmdline,
            "aspnet": "asp.net" in cmdline or "dotnet" in cmdline,
            "laravel": "laravel" in cmdline or "artisan" in cmdline,
        }

        for framework, found in frameworks.items():
            if found:
                return framework

        return None

    def _discover_ports(self, pid: int) -> List[int]:
        """Discover ports used by process"""
        ports = []

        try:
            proc = psutil.Process(pid)
            connections = proc.net_connections()
            for conn in connections:
                if conn.laddr:
                    ports.append(conn.laddr.port)
        except Exception:
            pass

        return list(set(ports))

    def _discover_config_files(self, proc: RunningProcess) -> List[str]:
        """Discover configuration files"""
        config_files = []

        if proc.working_directory:
            wd = Path(proc.working_directory)
            config_patterns = [
                "*.conf",
                "*.config",
                "*.ini",
                "*.yaml",
                "*.yml",
                "*.json",
                "*.env",
                ".env",
                "config.json",
                "settings.py",
                "appsettings.json",
            ]

            for pattern in config_patterns:
                try:
                    for config_file in wd.glob(pattern):
                        if config_file.is_file():
                            config_files.append(str(config_file))
                except Exception:
                    pass

        return config_files[:10]  # Limit to 10

    def _discover_environment_variables(self, pid: int) -> Dict[str, str]:
        """Discover environment variables"""
        env_vars = {}

        try:
            proc = psutil.Process(pid)
            env = proc.environ()

            # Filter important environment variables
            important_vars = [
                "PATH",
                "PYTHONPATH",
                "NODE_PATH",
                "JAVA_HOME",
                "HOME",
                "PORT",
                "HOST",
                "DATABASE_URL",
                "REDIS_URL",
                "API_KEY",
                "ENVIRONMENT",
                "ENV",
                "DEBUG",
                "LOG_LEVEL",
            ]

            for key in important_vars:
                if key in env:
                    env_vars[key] = env[key]
        except Exception:
            pass

        return env_vars


class ArchitectureMapper:
    """Map architecture from macro to micro"""

    def build_architecture_layers(
        self,
        devices: List[Dict],
        services: List[RunningService],
        processes: List[RunningProcess],
        applications: List[Application],
        frameworks: List[Framework],
    ) -> List[ArchitectureLayer]:
        """Build architecture layers"""
        layers = []

        # Layer 0: Network/Macro
        layers.append(
            ArchitectureLayer(
                layer_id="layer_network",
                layer_name="Network Layer",
                level=0,
                components=[d["device_id"] for d in devices],
                relationships={},
            )
        )

        # Layer 1: Devices
        layers.append(
            ArchitectureLayer(
                layer_id="layer_devices",
                layer_name="Device Layer",
                level=1,
                components=[d["device_id"] for d in devices],
                relationships={},
            )
        )

        # Layer 2: Services
        layers.append(
            ArchitectureLayer(
                layer_id="layer_services",
                layer_name="Service Layer",
                level=2,
                components=[s.service_id for s in services],
                relationships={s.service_id: s.dependencies for s in services},
            )
        )

        # Layer 3: Applications
        layers.append(
            ArchitectureLayer(
                layer_id="layer_applications",
                layer_name="Application Layer",
                level=3,
                components=[a.application_id for a in applications],
                relationships={a.application_id: a.dependencies for a in applications},
            )
        )

        # Layer 4: Frameworks
        layers.append(
            ArchitectureLayer(
                layer_id="layer_frameworks",
                layer_name="Framework Layer",
                level=4,
                components=[f.framework_id for f in frameworks],
                relationships={f.framework_id: f.applications for f in frameworks},
            )
        )

        # Layer 5: Processes/Micro
        layers.append(
            ArchitectureLayer(
                layer_id="layer_processes",
                layer_name="Process Layer",
                level=5,
                components=[str(p.process_id) for p in processes],
                relationships={
                    str(p.process_id): [str(p.parent_process_id)] if p.parent_process_id else []
                    for p in processes
                },
            )
        )

        return layers


class HomelabArchitectureDiscovery:
    """Main architecture discovery system"""

    def __init__(self, base_path: Path):
        self.project_root = base_path
        self.windows_service_discovery = WindowsServiceDiscovery()
        self.linux_service_discovery = LinuxServiceDiscovery()
        self.process_discovery = ProcessDiscovery()
        self.framework_discovery = FrameworkDiscovery()
        self.application_discovery = ApplicationDiscovery()
        self.architecture_mapper = ArchitectureMapper()

    def discover_device_architecture(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Discover complete architecture for a device"""
        device_id = device["device_id"]
        os_type = device.get("operating_system", "")

        architecture = {
            "device_id": device_id,
            "discovered_at": datetime.now().isoformat(),
            "services": [],
            "processes": [],
            "applications": [],
            "frameworks": [],
            "architecture_layers": [],
        }

        # Discover services
        if os_type == "Windows":
            architecture["services"] = [
                asdict(s) for s in self.windows_service_discovery.discover_services(device_id)
            ]
        elif os_type == "Linux" or "Synology" in os_type:
            architecture["services"] = [
                asdict(s) for s in self.linux_service_discovery.discover_services(device_id)
            ]

        # Discover processes
        architecture["processes"] = [
            asdict(p) for p in self.process_discovery.discover_processes(device_id)
        ]

        # Discover frameworks
        processes_objs = [RunningProcess(**p) for p in architecture["processes"]]
        architecture["frameworks"] = [
            asdict(f)
            for f in self.framework_discovery.discover_web_frameworks(processes_objs, device_id)
        ]
        architecture["frameworks"].extend(
            [asdict(f) for f in self.framework_discovery.discover_container_frameworks(device_id)]
        )

        # Discover applications
        services_objs = [RunningService(**s) for s in architecture["services"]]
        architecture["applications"] = [
            asdict(a)
            for a in self.application_discovery.discover_applications(
                processes_objs, services_objs, device_id
            )
        ]

        # Build architecture layers
        architecture["architecture_layers"] = [
            asdict(layer)
            for layer in self.architecture_mapper.build_architecture_layers(
                [device],
                services_objs,
                processes_objs,
                [Application(**a) for a in architecture["applications"]],
                [Framework(**f) for f in architecture["frameworks"]],
            )
        ]

        return architecture

    def discover_all_architecture(self, audit_file: Path) -> Dict[str, Any]:
        """Discover architecture for all devices."""
        with open(audit_file, encoding="utf-8") as f:
            audit_data = json.load(f)

        devices_list: List[Dict[str, Any]] = []
        devices_raw: List[Any] = audit_data.get("devices", [])
        for device in devices_raw:
            if not isinstance(device, dict):
                continue
            device_arch = self.discover_device_architecture(cast(Dict[str, Any], device))
            devices_list.append(device_arch)

        def _count(key: str) -> int:
            return sum(len(cast(Dict[str, Any], d).get(key, [])) for d in devices_list)

        total_services = _count("services")
        total_processes = _count("processes")
        total_applications = _count("applications")
        total_frameworks = _count("frameworks")

        summary: Dict[str, int] = {
            "devices": len(devices_list),
            "total_services": total_services,
            "total_processes": total_processes,
            "total_applications": total_applications,
            "total_frameworks": total_frameworks,
        }

        architecture_inventory: Dict[str, Any] = {
            "inventory_id": (
                f"architecture_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ),
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "devices": devices_list,
            "summary": summary,
        }
        return architecture_inventory

    def save_inventory(self, inventory: Dict[str, Any], output_file: Path):
        """Save architecture inventory"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False, default=str)

        logger.info("Architecture inventory saved: %s", output_file)
        return inventory


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Discover homelab architecture (applications, services, frameworks)"
    )
    parser.add_argument("--audit-file", help="Audit file to use (default: latest)")
    parser.add_argument(
        "--output", help="Output file (default: architecture_inventory_<timestamp>.json)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    discovery = HomelabArchitectureDiscovery(project_root)

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

    # Discover architecture
    print("Discovering architecture (applications, services, frameworks)...")
    inventory = discovery.discover_all_architecture(audit_file)

    # Save inventory
    output_dir = project_root / "data" / "homelab_architecture"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = (
            output_dir / f"architecture_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    discovery.save_inventory(inventory, output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("ARCHITECTURE INVENTORY SUMMARY")
    print("=" * 80)
    summary = inventory["summary"]
    print(f"Devices: {summary['devices']}")
    print(f"Services: {summary['total_services']}")
    print(f"Processes: {summary['total_processes']}")
    print(f"Applications: {summary['total_applications']}")
    print(f"Frameworks: {summary['total_frameworks']}")
    print(f"\nInventory saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(inventory, indent=2, default=str))


if __name__ == "__main__":
    main()
