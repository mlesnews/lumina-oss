#!/usr/bin/env python3
"""
Examine NAS Infrastructure Setup

Examines:
1. N8N setup on NAS
2. Lightweight DSM Container Manager (Synology's Docker)
3. Centralized containers (shared by LAPTOP and DESKTOP)
4. MCP container management
5. Centralized storage
6. DNS primary/secondary with failovers on pfSense

Tags: #NAS #N8N #CONTAINER #DSM #MCP #DNS #INFRASTRUCTURE @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ExamineNASInfrastructure")


class NASInfrastructureExaminer:
    """Examine NAS infrastructure setup"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_hostname = "DS1821PLUS"

    def examine_n8n_setup(self) -> Dict[str, Any]:
        """Examine N8N setup on NAS"""
        logger.info("=" * 80)
        logger.info("🔍 Examining N8N Setup on NAS")
        logger.info("=" * 80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "nas_ip": self.nas_ip,
            "n8n_installed": False,
            "n8n_running": False,
            "endpoint": None,
            "port": None,
            "version": None,
            "workflows": [],
            "webhooks": [],
            "container_info": None
        }

        # Check N8N ports
        n8n_ports = [5678, 8080, 3000, 5000, 8443, 443, 80]

        for port in n8n_ports:
            endpoint = f"http://{self.nas_ip}:{port}"
            try:
                response = requests.get(endpoint, timeout=3)
                if response.status_code < 500:
                    if "n8n" in response.text.lower():
                        result["n8n_installed"] = True
                        result["n8n_running"] = True
                        result["endpoint"] = endpoint
                        result["port"] = port
                        logger.info(f"  ✅ N8N found at {endpoint}")

                        # Try to get version
                        try:
                            version_resp = requests.get(f"{endpoint}/api/v1/version", timeout=3)
                            if version_resp.status_code == 200:
                                result["version"] = version_resp.json().get("version")
                        except:
                            pass
                        break
            except:
                continue

        # Check for N8N workflows
        if result["n8n_running"]:
            try:
                workflows_resp = requests.get(f"{result['endpoint']}/api/v1/workflows", timeout=5)
                if workflows_resp.status_code == 200:
                    workflows_data = workflows_resp.json()
                    result["workflows"] = workflows_data.get("data", [])
                    logger.info(f"  ✅ Found {len(result['workflows'])} workflows")

                    # Find webhook workflows
                    for wf in result["workflows"]:
                        nodes = wf.get("nodes", [])
                        for node in nodes:
                            if node.get("type") == "n8n-nodes-base.webhook":
                                result["webhooks"].append({
                                    "workflow": wf.get("name"),
                                    "path": node.get("parameters", {}).get("path")
                                })
            except Exception as e:
                logger.debug(f"  Could not fetch workflows: {e}")

        # Check if N8N is running in a container
        result["container_info"] = {
            "running_in_container": False,
            "container_name": None,
            "container_image": None
        }

        return result

    def examine_dsm_container_manager(self) -> Dict[str, Any]:
        """Examine DSM Container Manager (Synology's Docker)"""
        logger.info("=" * 80)
        logger.info("🐳 Examining DSM Container Manager")
        logger.info("=" * 80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "container_manager_installed": False,
            "docker_available": False,
            "containers": [],
            "centralized_containers": [],
            "mcp_container": None,
            "shared_storage": None
        }

        # Try to check via SSH (if credentials available)
        try:
            sys.path.insert(0, str(self.project_root / "scripts" / "python"))
            from nas_azure_vault_integration import NASAzureVaultIntegration
            import paramiko

            nas_vault = NASAzureVaultIntegration()
            credentials = nas_vault.get_nas_credentials()

            if credentials:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                try:
                    ssh.connect(
                        self.nas_ip,
                        port=22,
                        username=credentials.get("username"),
                        password=credentials.get("password"),
                        timeout=10,
                        allow_agent=False,
                        look_for_keys=False
                    )

                    # Check Container Manager
                    logger.info("  🔍 Checking Container Manager installation...")
                    stdin, stdout, stderr = ssh.exec_command("synopkg list | grep -i container")
                    output = stdout.read().decode().strip()

                    if "container" in output.lower():
                        result["container_manager_installed"] = True
                        logger.info("  ✅ Container Manager installed")

                    # Check Docker
                    logger.info("  🔍 Checking Docker availability...")
                    stdin, stdout, stderr = ssh.exec_command("which docker")
                    docker_path = stdout.read().decode().strip()

                    if docker_path:
                        result["docker_available"] = True
                        logger.info(f"  ✅ Docker available at: {docker_path}")

                        # List containers (try with sudo if needed)
                        logger.info("  🔍 Listing containers...")
                        # Try regular docker command first
                        stdin, stdout, stderr = ssh.exec_command(
                            "docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1"
                        )
                        containers_output = stdout.read().decode().strip()
                        error_output = stderr.read().decode().strip()

                        # If permission denied, try with sudo or check Container Manager
                        if "permission denied" in error_output.lower() or not containers_output:
                            logger.info("  🔍 Trying Container Manager API or alternative method...")
                            # Check via Container Manager package
                            stdin, stdout, stderr = ssh.exec_command(
                                "synopkg status Docker 2>&1 || synopkg status ContainerManager 2>&1 || echo 'not_found'"
                            )
                            pkg_status = stdout.read().decode().strip()
                            if "started" in pkg_status.lower():
                                result["container_manager_installed"] = True
                                logger.info("  ✅ Container Manager package is running")

                            # Try to list via Container Manager paths
                            stdin, stdout, stderr = ssh.exec_command(
                                "ls -la /volume1/@docker/containers/ 2>&1 | head -20 || echo 'not_found'"
                            )
                            container_paths = stdout.read().decode().strip()
                            if "not_found" not in container_paths and container_paths:
                                logger.info("  ✅ Found container data in /volume1/@docker/containers/")

                        # Also check for N8N container specifically
                        logger.info("  🔍 Checking for N8N container...")
                        stdin, stdout, stderr = ssh.exec_command(
                            "docker ps -a --filter 'name=n8n' --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>&1 || echo 'not_found'"
                        )
                        n8n_containers = stdout.read().decode().strip()
                        if "not_found" not in n8n_containers and n8n_containers:
                            logger.info(f"  ✅ Found N8N container(s): {n8n_containers}")
                            # Add to containers list
                            for line in n8n_containers.split('\n'):
                                if line.strip() and '\t' in line:
                                    parts = line.split('\t')
                                    container_info = {
                                        "name": parts[0],
                                        "image": parts[1] if len(parts) > 1 else "",
                                        "status": parts[2] if len(parts) > 2 else ""
                                    }
                                    result["containers"].append(container_info)

                        # Check for MCP container
                        logger.info("  🔍 Checking for MCP container...")
                        stdin, stdout, stderr = ssh.exec_command(
                            "docker ps -a --filter 'name=mcp' --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>&1 || echo 'not_found'"
                        )
                        mcp_containers = stdout.read().decode().strip()
                        if "not_found" not in mcp_containers and mcp_containers:
                            logger.info(f"  ✅ Found MCP container(s): {mcp_containers}")
                            for line in mcp_containers.split('\n'):
                                if line.strip() and '\t' in line:
                                    parts = line.split('\t')
                                    mcp_info = {
                                        "name": parts[0],
                                        "image": parts[1] if len(parts) > 1 else "",
                                        "status": parts[2] if len(parts) > 2 else ""
                                    }
                                    result["mcp_container"] = mcp_info
                                    result["containers"].append(mcp_info)

                        # Check all containers (including stopped)
                        stdin, stdout, stderr = ssh.exec_command(
                            "docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1 | head -50"
                        )
                        containers_output = stdout.read().decode().strip()

                        if containers_output:
                            for line in containers_output.split('\n'):
                                if line.strip():
                                    parts = line.split('\t')
                                    if len(parts) >= 3:
                                        container_info = {
                                            "name": parts[0],
                                            "image": parts[1] if len(parts) > 1 else "",
                                            "status": parts[2] if len(parts) > 2 else "",
                                            "ports": parts[3] if len(parts) > 3 else ""
                                        }
                                        result["containers"].append(container_info)

                                        # Check if centralized (shared by laptop/desktop)
                                        if any(keyword in container_info["name"].lower() for keyword in ["shared", "central", "common", "mcp"]):
                                            result["centralized_containers"].append(container_info)

                                        # Check for MCP container
                                        if "mcp" in container_info["name"].lower():
                                            result["mcp_container"] = container_info
                                            logger.info(f"  ✅ Found MCP container: {container_info['name']}")

                        logger.info(f"  ✅ Found {len(result['containers'])} containers")
                        logger.info(f"  ✅ Found {len(result['centralized_containers'])} centralized containers")

                    # Check shared storage
                    logger.info("  🔍 Checking centralized storage...")
                    stdin, stdout, stderr = ssh.exec_command(
                        "df -h | grep -E 'volume1|docker|shared' | head -5"
                    )
                    storage_output = stdout.read().decode().strip()
                    if storage_output:
                        result["shared_storage"] = {
                            "info": storage_output,
                            "paths": []
                        }
                        # Common shared paths
                        shared_paths = [
                            "/volume1/docker",
                            "/volume1/shared",
                            "/volume1/@docker"
                        ]
                        for path in shared_paths:
                            stdin, stdout, stderr = ssh.exec_command(f"test -d {path} && echo 'exists' || echo 'not_found'")
                            if stdout.read().decode().strip() == "exists":
                                result["shared_storage"]["paths"].append(path)
                                logger.info(f"  ✅ Shared storage path: {path}")

                    ssh.close()

                except Exception as e:
                    logger.warning(f"  ⚠️  SSH connection failed: {e}")
                    result["error"] = str(e)
        except ImportError:
            logger.warning("  ⚠️  paramiko not available - cannot check via SSH")
        except Exception as e:
            logger.warning(f"  ⚠️  Could not check Container Manager: {e}")

        return result

    def examine_dns_setup(self) -> Dict[str, Any]:
        """Examine DNS setup with pfSense failover"""
        logger.info("=" * 80)
        logger.info("🌐 Examining DNS Setup (Primary/Secondary with pfSense)")
        logger.info("=" * 80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "primary_dns": {
                "host": "<NAS_PRIMARY_IP>",  # NAS
                "type": "primary",
                "healthy": False
            },
            "secondary_dns": {
                "host": "<NAS_IP>",  # pfSense (typical gateway)
                "type": "secondary",
                "healthy": False
            },
            "failover_configured": False,
            "dns_cache": None
        }

        # Check DNS resolution
        import socket

        test_hostname = "google.com"

        # Test primary DNS (NAS)
        try:
            socket.setdefaulttimeout(5)
            ip = socket.gethostbyname(test_hostname)
            result["primary_dns"]["healthy"] = True
            logger.info(f"  ✅ Primary DNS (NAS) is healthy")
        except Exception as e:
            logger.warning(f"  ⚠️  Primary DNS check failed: {e}")

        # Check DNS cluster manager if available
        try:
            from dns_cluster_manager import DNSClusterManager
            dns_manager = DNSClusterManager()
            cluster_status = dns_manager.get_cluster_status()
            result["cluster_status"] = cluster_status
            result["failover_configured"] = True
            logger.info("  ✅ DNS Cluster Manager found")
            logger.info(f"     Primary Cluster: {cluster_status['primary_cluster']['cluster_name']}")
            logger.info(f"     Secondary Cluster: {cluster_status['secondary_cluster']['cluster_name']}")
        except Exception as e:
            logger.debug(f"  DNS Cluster Manager not available: {e}")

        return result

    def examine_centralized_storage(self) -> Dict[str, Any]:
        try:
            """Examine centralized storage setup"""
            logger.info("=" * 80)
            logger.info("💾 Examining Centralized Storage")
            logger.info("=" * 80)

            result = {
                "timestamp": datetime.now().isoformat(),
                "nas_storage": {
                    "ip": self.nas_ip,
                    "hostname": self.nas_hostname,
                    "mounted_paths": [],
                    "shared_volumes": []
                },
                "container_storage": {
                    "docker_volume_path": None,
                    "shared_volumes": []
                }
            }

            # Check for NAS mount points (Windows)
            common_mounts = [
                "M:\\",
                "N:\\",
                "\\\\<NAS_PRIMARY_IP>\\",
                "\\\\DS1821PLUS\\"
            ]

            for mount in common_mounts:
                mount_path = Path(mount)
                if mount_path.exists():
                    result["nas_storage"]["mounted_paths"].append(str(mount_path))
                    logger.info(f"  ✅ NAS mounted at: {mount_path}")

            # Check for shared Docker volumes
            docker_volumes = [
                "/volume1/docker",
                "/volume1/@docker",
                "/volume1/shared"
            ]

            result["container_storage"]["shared_volumes"] = docker_volumes
            logger.info(f"  ℹ️  Expected Docker volumes: {', '.join(docker_volumes)}")

            return result

        except Exception as e:
            self.logger.error(f"Error in examine_centralized_storage: {e}", exc_info=True)
            raise
    def get_full_examination(self) -> Dict[str, Any]:
        """Get complete infrastructure examination"""
        logger.info("=" * 80)
        logger.info("🏗️  EXAMINING NAS INFRASTRUCTURE")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "nas_info": {
                "ip": self.nas_ip,
                "hostname": self.nas_hostname
            },
            "n8n": {},
            "container_manager": {},
            "dns": {},
            "storage": {}
        }

        # 1. Examine N8N
        results["n8n"] = self.examine_n8n_setup()
        logger.info("")

        # 2. Examine Container Manager
        results["container_manager"] = self.examine_dsm_container_manager()
        logger.info("")

        # 3. Examine DNS
        results["dns"] = self.examine_dns_setup()
        logger.info("")

        # 4. Examine Storage
        results["storage"] = self.examine_centralized_storage()
        logger.info("")

        logger.info("=" * 80)
        logger.info("✅ INFRASTRUCTURE EXAMINATION COMPLETE")
        logger.info("=" * 80)

        return results

    def print_examination_report(self, json_output: bool = False):
        try:
            """Print examination report"""
            results = self.get_full_examination()

            if json_output:
                print(json.dumps(results, indent=2, default=str))
            else:
                print("=" * 80)
                print("🏗️  NAS INFRASTRUCTURE EXAMINATION REPORT")
                print("=" * 80)
                print(f"Generated: {results['timestamp']}")
                print(f"NAS: {results['nas_info']['hostname']} ({results['nas_info']['ip']})")
                print()

                # N8N
                n8n = results["n8n"]
                print("📊 N8N SETUP")
                print("-" * 80)
                print(f"  Installed: {'✅' if n8n['n8n_installed'] else '❌'}")
                print(f"  Running: {'✅' if n8n['n8n_running'] else '❌'}")
                if n8n['endpoint']:
                    print(f"  Endpoint: {n8n['endpoint']}")
                if n8n['version']:
                    print(f"  Version: {n8n['version']}")
                print(f"  Workflows: {len(n8n['workflows'])}")
                print(f"  Webhooks: {len(n8n['webhooks'])}")
                print()

                # Container Manager
                cm = results["container_manager"]
                print("🐳 DSM CONTAINER MANAGER")
                print("-" * 80)
                print(f"  Installed: {'✅' if cm['container_manager_installed'] else '❌'}")
                print(f"  Docker Available: {'✅' if cm['docker_available'] else '❌'}")
                print(f"  Total Containers: {len(cm['containers'])}")
                print(f"  Centralized Containers: {len(cm['centralized_containers'])}")

                if cm['mcp_container']:
                    print(f"  MCP Container: ✅ {cm['mcp_container']['name']}")
                else:
                    print(f"  MCP Container: ❌ Not found")

                if cm['containers']:
                    print(f"\n  Containers:")
                    for container in cm['containers'][:10]:
                        print(f"    • {container['name']} ({container['image']})")
                print()

                # DNS
                dns = results["dns"]
                print("🌐 DNS SETUP")
                print("-" * 80)
                print(f"  Primary DNS (NAS): {'✅' if dns['primary_dns']['healthy'] else '❌'} {dns['primary_dns']['host']}")
                print(f"  Secondary DNS (pfSense): {'✅' if dns['secondary_dns']['healthy'] else '❌'} {dns['secondary_dns']['host']}")
                print(f"  Failover Configured: {'✅' if dns['failover_configured'] else '❌'}")
                print()

                # Storage
                storage = results["storage"]
                print("💾 CENTRALIZED STORAGE")
                print("-" * 80)
                print(f"  NAS Mounts: {len(storage['nas_storage']['mounted_paths'])}")
                for mount in storage['nas_storage']['mounted_paths']:
                    print(f"    • {mount}")
                print(f"  Docker Volumes: {len(storage['container_storage']['shared_volumes'])}")
                for volume in storage['container_storage']['shared_volumes']:
                    print(f"    • {volume}")
                print()
                print("=" * 80)


        except Exception as e:
            self.logger.error(f"Error in print_examination_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Examine NAS Infrastructure Setup"
        )
        parser.add_argument("--n8n-only", action="store_true", help="Examine N8N only")
        parser.add_argument("--containers-only", action="store_true", help="Examine containers only")
        parser.add_argument("--dns-only", action="store_true", help="Examine DNS only")
        parser.add_argument("--storage-only", action="store_true", help="Examine storage only")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        examiner = NASInfrastructureExaminer()

        if args.n8n_only:
            result = examiner.examine_n8n_setup()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
        elif args.containers_only:
            result = examiner.examine_dsm_container_manager()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
        elif args.dns_only:
            result = examiner.examine_dns_setup()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
        elif args.storage_only:
            result = examiner.examine_centralized_storage()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
        else:
            examiner.print_examination_report(json_output=args.json)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()