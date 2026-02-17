#!/usr/bin/env python3
"""
Homelab Software Discovery System

Discovers all installed software across the homelab, including:
- Installed applications
- System packages
- Services and daemons
- Development tools
- Container images
- Python packages
- Node.js packages
- Browser extensions
- IDE extensions
- And more...

Tags: #HOMELAB #SOFTWARE #DISCOVERY #INVENTORY @JARVIS @LUMINA
"""

import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_software_discovery")


@dataclass
class SoftwarePackage:
    """Represents an installed software package"""

    package_id: str
    name: str
    version: Optional[str] = None
    publisher: Optional[str] = None
    install_date: Optional[str] = None
    install_location: Optional[str] = None
    package_type: str = "unknown"  # "application", "service", "package", "container", "extension"
    category: Optional[str] = None
    description: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    size_bytes: Optional[int] = None
    device_id: str = ""
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WindowsSoftwareDiscovery:
    """Discovers software on Windows"""

    def discover_installed_apps(self, device_id: str) -> List[SoftwarePackage]:
        """Discover installed Windows applications"""
        packages = []

        try:
            # PowerShell: Get-ItemProperty for installed programs
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    """
                    Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
                    Where-Object { $_.DisplayName -ne $null } |
                    Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation |
                    ConvertTo-Json -Depth 3
                """,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                apps = json.loads(result.stdout)
                if not isinstance(apps, list):
                    apps = [apps]

                for app in apps:
                    if app.get("DisplayName"):
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_app_{self._sanitize_id(app['DisplayName'])}",
                                name=app["DisplayName"],
                                version=app.get("DisplayVersion"),
                                publisher=app.get("Publisher"),
                                install_date=self._parse_install_date(app.get("InstallDate")),
                                install_location=app.get("InstallLocation"),
                                package_type="application",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.warning(f"Failed to discover Windows apps: {e}")

        # Also check 32-bit programs
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    """
                    Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
                    Where-Object { $_.DisplayName -ne $null } |
                    Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation |
                    ConvertTo-Json -Depth 3
                """,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                apps = json.loads(result.stdout)
                if not isinstance(apps, list):
                    apps = [apps]

                for app in apps:
                    if app.get("DisplayName"):
                        # Check if already added
                        existing = any(p.name == app["DisplayName"] for p in packages)
                        if not existing:
                            packages.append(
                                SoftwarePackage(
                                    package_id=f"{device_id}_app_{self._sanitize_id(app['DisplayName'])}",
                                    name=app["DisplayName"],
                                    version=app.get("DisplayVersion"),
                                    publisher=app.get("Publisher"),
                                    install_date=self._parse_install_date(app.get("InstallDate")),
                                    install_location=app.get("InstallLocation"),
                                    package_type="application",
                                    device_id=device_id,
                                )
                            )
        except Exception as e:
            logger.warning(f"Failed to discover 32-bit Windows apps: {e}")

        return packages

    def discover_windows_features(self, device_id: str) -> List[SoftwarePackage]:
        """Discover Windows features"""
        packages = []

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-WindowsOptionalFeature -Online | ConvertTo-Json -Depth 3",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                features = json.loads(result.stdout)
                if not isinstance(features, list):
                    features = [features]

                for feature in features:
                    if feature.get("FeatureName"):
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_feature_{self._sanitize_id(feature['FeatureName'])}",
                                name=feature["FeatureName"],
                                package_type="feature",
                                category="windows_feature",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.warning(f"Failed to discover Windows features: {e}")

        return packages

    def discover_choco_packages(self, device_id: str) -> List[SoftwarePackage]:
        """Discover Chocolatey packages"""
        packages = []

        try:
            result = subprocess.run(
                ["choco", "list", "--local-only", "--limit-output"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        name, version = line.split("|")[:2]
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_choco_{self._sanitize_id(name)}",
                                name=name.strip(),
                                version=version.strip(),
                                package_type="package",
                                category="chocolatey",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.debug(f"Chocolatey not available or failed: {e}")

        return packages

    def discover_wsl_distros(self, device_id: str) -> List[SoftwarePackage]:
        """Discover WSL distributions"""
        packages = []

        try:
            result = subprocess.run(
                ["wsl", "--list", "--verbose"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        distro_name = parts[0]
                        state = parts[1] if len(parts) > 1 else "Unknown"
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_wsl_{self._sanitize_id(distro_name)}",
                                name=f"WSL: {distro_name}",
                                version=state,
                                package_type="virtualization",
                                category="wsl",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.debug(f"WSL not available or failed: {e}")

        return packages

    def _sanitize_id(self, name: str) -> str:
        """Sanitize name for ID"""
        return re.sub(r"[^a-zA-Z0-9_-]", "_", name.lower())[:50]

    def _parse_install_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse Windows install date"""
        if not date_str:
            return None
        try:
            # Format: YYYYMMDD
            if len(date_str) == 8:
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        except:
            pass
        return date_str


class LinuxSoftwareDiscovery:
    """Discovers software on Linux"""

    def discover_packages(self, device_id: str) -> List[SoftwarePackage]:
        """Discover installed packages"""
        packages = []

        # Try dpkg (Debian/Ubuntu)
        try:
            result = subprocess.run(["dpkg", "-l"], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[5:]  # Skip headers
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3:
                        status = parts[0]
                        name = parts[1]
                        version = parts[2]

                        if status == "ii":  # Installed
                            packages.append(
                                SoftwarePackage(
                                    package_id=f"{device_id}_dpkg_{self._sanitize_id(name)}",
                                    name=name,
                                    version=version,
                                    package_type="package",
                                    category="dpkg",
                                    device_id=device_id,
                                )
                            )
        except Exception as e:
            logger.debug(f"dpkg not available: {e}")

        # Try rpm (RedHat/CentOS)
        try:
            result = subprocess.run(
                ["rpm", "-qa", "--queryformat", "%{NAME}|%{VERSION}|%{VENDOR}\\n"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]
                            vendor = parts[2] if len(parts) > 2 else None

                            packages.append(
                                SoftwarePackage(
                                    package_id=f"{device_id}_rpm_{self._sanitize_id(name)}",
                                    name=name,
                                    version=version,
                                    publisher=vendor,
                                    package_type="package",
                                    category="rpm",
                                    device_id=device_id,
                                )
                            )
        except Exception as e:
            logger.debug(f"rpm not available: {e}")

        return packages

    def discover_snap_packages(self, device_id: str) -> List[SoftwarePackage]:
        """Discover snap packages"""
        packages = []

        try:
            result = subprocess.run(["snap", "list"], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_snap_{self._sanitize_id(name)}",
                                name=name,
                                version=version,
                                package_type="package",
                                category="snap",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.debug(f"snap not available: {e}")

        return packages


class ContainerSoftwareDiscovery:
    """Discovers container images and containers"""

    def discover_docker_images(self, device_id: str) -> List[SoftwarePackage]:
        """Discover Docker images"""
        packages = []

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}|{{.Tag}}|{{.ID}}"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        repo, tag, image_id = line.split("|")[:3]
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_docker_{self._sanitize_id(repo)}_{tag}",
                                name=f"{repo}:{tag}",
                                version=tag,
                                package_type="container",
                                category="docker_image",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.debug(f"Docker not available or failed: {e}")

        return packages

    def discover_docker_containers(self, device_id: str) -> List[SoftwarePackage]:
        """Discover running Docker containers"""
        packages = []

        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Image}}|{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        name, image, status = line.split("|")[:3]
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_container_{self._sanitize_id(name)}",
                                name=name,
                                version=image,
                                description=status,
                                package_type="container",
                                category="docker_container",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.debug(f"Docker containers discovery failed: {e}")

        return packages


class DevelopmentToolDiscovery:
    """Discovers development tools and packages"""

    def discover_python_packages(self, device_id: str) -> List[SoftwarePackage]:
        """Discover Python packages"""
        packages = []

        try:
            result = subprocess.run(
                ["pip", "list", "--format", "json"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                pip_packages = json.loads(result.stdout)
                for pkg in pip_packages:
                    packages.append(
                        SoftwarePackage(
                            package_id=f"{device_id}_pip_{self._sanitize_id(pkg['name'])}",
                            name=pkg["name"],
                            version=pkg.get("version"),
                            package_type="package",
                            category="python",
                            device_id=device_id,
                        )
                    )
        except Exception as e:
            logger.debug(f"pip not available or failed: {e}")

        return packages

    def discover_node_packages(self, device_id: str) -> List[SoftwarePackage]:
        """Discover Node.js packages (global)"""
        packages = []

        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth", "0", "--json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                npm_data = json.loads(result.stdout)
                if "dependencies" in npm_data:
                    for name, info in npm_data["dependencies"].items():
                        packages.append(
                            SoftwarePackage(
                                package_id=f"{device_id}_npm_{self._sanitize_id(name)}",
                                name=name,
                                version=info.get("version"),
                                package_type="package",
                                category="nodejs",
                                device_id=device_id,
                            )
                        )
        except Exception as e:
            logger.debug(f"npm not available or failed: {e}")

        return packages


class IDEExtensionDiscovery:
    """Discovers IDE extensions"""

    def discover_vscode_extensions(self, device_id: str) -> List[SoftwarePackage]:
        """Discover VS Code / Cursor extensions"""
        packages = []

        # VS Code extensions
        vscode_paths = [
            Path.home() / ".vscode" / "extensions",
            Path.home() / ".vscode-insiders" / "extensions",
            Path.home() / "AppData" / "Roaming" / "Code" / "User" / "extensions",
        ]

        for ext_dir in vscode_paths:
            if ext_dir.exists():
                for ext_folder in ext_dir.iterdir():
                    if ext_folder.is_dir():
                        # Try to read package.json
                        package_json = ext_folder / "package.json"
                        if package_json.exists():
                            try:
                                with open(package_json, encoding="utf-8") as f:
                                    pkg_data = json.load(f)

                                packages.append(
                                    SoftwarePackage(
                                        package_id=f"{device_id}_vscode_ext_{self._sanitize_id(pkg_data.get('name', ext_folder.name))}",
                                        name=pkg_data.get(
                                            "displayName", pkg_data.get("name", ext_folder.name)
                                        ),
                                        version=pkg_data.get("version"),
                                        publisher=pkg_data.get("publisher"),
                                        install_location=str(ext_folder),
                                        package_type="extension",
                                        category="vscode",
                                        description=pkg_data.get("description"),
                                        device_id=device_id,
                                    )
                                )
                            except Exception as e:
                                logger.debug(f"Failed to read extension {ext_folder}: {e}")

        return packages


class HomelabSoftwareDiscovery:
    """Main software discovery system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.windows_discovery = WindowsSoftwareDiscovery()
        self.linux_discovery = LinuxSoftwareDiscovery()
        self.container_discovery = ContainerSoftwareDiscovery()
        self.dev_tool_discovery = DevelopmentToolDiscovery()
        self.ide_discovery = IDEExtensionDiscovery()

    def discover_device_software(self, device: Dict[str, Any]) -> List[SoftwarePackage]:
        """Discover all software on a device"""
        device_id = device["device_id"]
        os_type = device.get("operating_system", "")

        all_packages = []

        if os_type == "Windows":
            logger.info(f"Discovering Windows software on {device_id}")
            all_packages.extend(self.windows_discovery.discover_installed_apps(device_id))
            all_packages.extend(self.windows_discovery.discover_windows_features(device_id))
            all_packages.extend(self.windows_discovery.discover_choco_packages(device_id))
            all_packages.extend(self.windows_discovery.discover_wsl_distros(device_id))
            all_packages.extend(self.ide_discovery.discover_vscode_extensions(device_id))

        elif os_type == "Linux" or "Synology" in os_type:
            logger.info(f"Discovering Linux software on {device_id}")
            all_packages.extend(self.linux_discovery.discover_packages(device_id))
            all_packages.extend(self.linux_discovery.discover_snap_packages(device_id))

        # Common discoveries (cross-platform)
        all_packages.extend(self.container_discovery.discover_docker_images(device_id))
        all_packages.extend(self.container_discovery.discover_docker_containers(device_id))
        all_packages.extend(self.dev_tool_discovery.discover_python_packages(device_id))
        all_packages.extend(self.dev_tool_discovery.discover_node_packages(device_id))

        logger.info(f"Discovered {len(all_packages)} software packages on {device_id}")
        return all_packages

    def discover_all_software(self, audit_file: Path) -> Dict[str, Any]:
        """Discover software for all devices in audit"""
        with open(audit_file, encoding="utf-8") as f:
            audit_data = json.load(f)

        software_inventory = {
            "inventory_id": f"software_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "devices": [],
        }

        for device in audit_data.get("devices", []):
            device_id = device["device_id"]
            packages = self.discover_device_software(device)

            software_inventory["devices"].append(
                {
                    "device_id": device_id,
                    "device_name": device.get("device_name", ""),
                    "total_packages": len(packages),
                    "packages": [asdict(pkg) for pkg in packages],
                }
            )

        return software_inventory

    def save_inventory(self, inventory: Dict[str, Any], output_file: Path):
        """Save software inventory"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Software inventory saved: {output_file}")
        return inventory


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Discover all software in homelab")
    parser.add_argument("--audit-file", help="Audit file to use (default: latest)")
    parser.add_argument(
        "--output", help="Output file (default: software_inventory_<timestamp>.json)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    discovery = HomelabSoftwareDiscovery(project_root)

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

    # Discover software
    print("Discovering software across homelab...")
    inventory = discovery.discover_all_software(audit_file)

    # Save inventory
    output_dir = project_root / "data" / "homelab_software"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = (
            output_dir / f"software_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    discovery.save_inventory(inventory, output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("SOFTWARE INVENTORY SUMMARY")
    print("=" * 80)
    total_packages = sum(d["total_packages"] for d in inventory["devices"])
    print(f"Devices: {len(inventory['devices'])}")
    print(f"Total Software Packages: {total_packages}")
    for device in inventory["devices"]:
        print(f"  {device['device_name']}: {device['total_packages']} packages")
    print(f"\nInventory saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(inventory, indent=2, default=str))


if __name__ == "__main__":
    main()
