#!/usr/bin/env python3
"""
Synology Container Manager API
Manage Docker containers and projects on Synology NAS via DSM API
#JARVIS #MANUS #NAS #SYNOLOGY #DOCKER #CONTAINER #API
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from synology_api_base import SynologyAPIBase
except ImportError:
    print("Error: synology_api_base.py not found")
    sys.exit(1)

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SynologyContainerManager")


class SynologyContainerManager(SynologyAPIBase):
    """
    Synology Container Manager API client
    Manages Docker containers and projects via DSM API
    """

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5000, verify_ssl: bool = False):
        """Initialize with HTTP port (5000) by default for Container Manager"""
        # Use HTTP for Container Manager API
        super().__init__(nas_ip, nas_port, verify_ssl)
        # Override to use HTTP instead of HTTPS
        self.base_url = f"http://{nas_ip}:{nas_port}"
        logger.info(f"🐳 Container Manager API initialized for {self.base_url}")

    def list_projects(self) -> Optional[List[Dict[str, Any]]]:
        """
        List all Container Manager projects

        Returns:
            List of projects or None if failed
        """
        logger.info("📋 Listing Container Manager projects...")

        result = self.api_call(api="SYNO.Docker.Project", method="list", version="1")

        if result:
            projects = result if isinstance(result, list) else result.get("projects", [])
            logger.info(f"✅ Found {len(projects)} projects")
            return projects
        return None

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by name

        Args:
            name: Project name to find

        Returns:
            Project dict or None if not found
        """
        projects = self.list_projects()
        if not projects:
            return None

        for project in projects:
            if project.get("name") == name:
                return project

        logger.warning(f"⚠️  Project '{name}' not found")
        return None

    def start_project(self, project_id: str) -> bool:
        """
        Start a Container Manager project

        Args:
            project_id: Project UUID

        Returns:
            True if started successfully
        """
        logger.info(f"🚀 Starting project {project_id}...")

        result = self.api_call(
            api="SYNO.Docker.Project", method="start", version="1", params={"id": project_id}
        )

        if result is not None:
            logger.info(f"✅ Project started: {project_id}")
            return True
        return False

    def stop_project(self, project_id: str) -> bool:
        """
        Stop a Container Manager project

        Args:
            project_id: Project UUID

        Returns:
            True if stopped successfully
        """
        logger.info(f"🛑 Stopping project {project_id}...")

        result = self.api_call(
            api="SYNO.Docker.Project", method="stop", version="1", params={"id": project_id}
        )

        if result is not None:
            logger.info(f"✅ Project stopped: {project_id}")
            return True
        return False

    def restart_project(self, project_id: str) -> bool:
        """
        Restart a Container Manager project

        Args:
            project_id: Project UUID

        Returns:
            True if restarted successfully
        """
        logger.info(f"🔄 Restarting project {project_id}...")

        # Stop then start
        if self.stop_project(project_id):
            import time

            time.sleep(2)  # Wait for containers to stop
            return self.start_project(project_id)
        return False

    def list_containers(self) -> Optional[List[Dict[str, Any]]]:
        """
        List all Docker containers

        Returns:
            List of containers or None if failed
        """
        logger.info("📋 Listing Docker containers...")

        result = self.api_call(
            api="SYNO.Docker.Container",
            method="list",
            version="1",
            params={"limit": -1, "offset": 0},
        )

        if result:
            containers = result.get("containers", []) if isinstance(result, dict) else result
            logger.info(f"✅ Found {len(containers)} containers")
            return containers
        return None

    def start_container(self, container_id: str) -> bool:
        """
        Start a single container

        Args:
            container_id: Container ID or name

        Returns:
            True if started successfully
        """
        logger.info(f"🚀 Starting container {container_id}...")

        result = self.api_call(
            api="SYNO.Docker.Container", method="start", version="1", params={"id": container_id}
        )

        if result is not None:
            logger.info(f"✅ Container started: {container_id}")
            return True
        return False

    def stop_container(self, container_id: str) -> bool:
        """
        Stop a single container

        Args:
            container_id: Container ID or name

        Returns:
            True if stopped successfully
        """
        logger.info(f"🛑 Stopping container {container_id}...")

        result = self.api_call(
            api="SYNO.Docker.Container", method="stop", version="1", params={"id": container_id}
        )

        if result is not None:
            logger.info(f"✅ Container stopped: {container_id}")
            return True
        return False

    def create_container(
        self,
        image: str,
        name: str,
        port_bindings: Optional[Dict[str, int]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
        auto_restart: bool = True,
    ) -> Optional[str]:
        """
        Create a new Docker container

        Args:
            image: Docker image name (e.g., 'n8nio/n8n:latest')
            name: Container name
            port_bindings: Port mappings {container_port: host_port}
            env_vars: Environment variables {key: value}
            volumes: Volume mappings {host_path: container_path}
            auto_restart: Enable auto-restart on failure

        Returns:
            Container ID if created, None if failed
        """
        logger.info(f"🐳 Creating container '{name}' from image '{image}'...")

        # Build port bindings list
        ports = []
        if port_bindings:
            for container_port, host_port in port_bindings.items():
                ports.append(
                    {
                        "container_port": int(container_port),
                        "host_port": int(host_port),
                        "type": "tcp",
                    }
                )

        # Build environment list
        env = []
        if env_vars:
            for key, value in env_vars.items():
                env.append({"key": key, "value": str(value)})

        # Build volume bindings
        vol_bindings = []
        if volumes:
            for host_path, container_path in volumes.items():
                vol_bindings.append(
                    {"host_volume_file": host_path, "mount_point": container_path, "type": "rw"}
                )

        # Container configuration
        config = {
            "image": image,
            "name": name,
            "enable_restart_policy": auto_restart,
            "port_bindings": json.dumps(ports) if ports else "[]",
            "env_variables": json.dumps(env) if env else "[]",
            "volume_bindings": json.dumps(vol_bindings) if vol_bindings else "[]",
        }

        result = self.api_call(
            api="SYNO.Docker.Container", method="create", version="1", params=config
        )

        if result:
            container_id = result.get("id", result.get("container_id"))
            logger.info(f"✅ Container created: {name} (ID: {container_id})")
            return container_id
        else:
            logger.error(f"❌ Failed to create container: {name}")
            return None

    def run_container(
        self,
        image: str,
        name: str,
        port_bindings: Optional[Dict[str, int]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
        auto_restart: bool = True,
    ) -> bool:
        """
        Create and start a container

        Args:
            image: Docker image name
            name: Container name
            port_bindings: Port mappings
            env_vars: Environment variables
            volumes: Volume mappings
            auto_restart: Enable auto-restart

        Returns:
            True if container is running
        """
        container_id = self.create_container(
            image=image,
            name=name,
            port_bindings=port_bindings,
            env_vars=env_vars,
            volumes=volumes,
            auto_restart=auto_restart,
        )

        if container_id:
            return self.start_container(container_id)
        return False

    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project status

        Args:
            project_id: Project UUID

        Returns:
            Project status or None if failed
        """
        result = self.api_call(
            api="SYNO.Docker.Project", method="get", version="1", params={"id": project_id}
        )
        return result

    def enable_ssh(self) -> bool:
        """
        Enable SSH service on NAS

        Returns:
            True if successful
        """
        logger.info("🔐 Enabling SSH service...")

        result = self.api_call(
            api="SYNO.Core.Terminal",
            method="set",
            version="3",
            params={"enable_ssh": True, "ssh_port": 22},
        )

        if result is not None:
            logger.info("✅ SSH service enabled")
            return True

        # Try alternative API
        result = self.api_call(
            api="SYNO.Core.Terminal",
            method="set",
            version="1",
            params={"enable_ssh": True},
        )

        if result is not None:
            logger.info("✅ SSH service enabled (v1)")
            return True

        logger.error("❌ Failed to enable SSH")
        return False

    def get_ssh_status(self) -> Optional[Dict[str, Any]]:
        """
        Get SSH service status

        Returns:
            SSH status dict or None
        """
        result = self.api_call(api="SYNO.Core.Terminal", method="get", version="3")
        return result

    def create_project(
        self, name: str, compose_content: str, path: str = "/volume1/docker"
    ) -> Optional[str]:
        """
        Create a new Container Manager project from docker-compose content

        Args:
            name: Project name
            compose_content: docker-compose.yml content as string
            path: Path on NAS for the project

        Returns:
            Project ID if successful, None otherwise
        """
        logger.info(f"📦 Creating Container Manager project: {name}...")

        # Use POST request for large compose files
        api_url = f"{self.base_url}/webapi/entry.cgi"

        data = {
            "api": "SYNO.Docker.Project",
            "version": "1",
            "method": "create",
            "name": name,
            "content": compose_content,
            "path": f"{path}/{name}",
        }

        if self.sid:
            data["_sid"] = self.sid

        try:
            response = self.session.post(api_url, data=data, timeout=60)
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                project_data = result.get("data", {})
                project_id = project_data.get("id") if isinstance(project_data, dict) else None
                if project_id:
                    logger.info(f"✅ Project created: {project_id}")
                    return project_id
                # If no ID but success, try to find the project
                logger.info("✅ Project created (fetching ID...)")
                return self._get_project_id_by_name(name)
            else:
                error = result.get("error", {})
                logger.error(f"❌ Project creation failed: {error.get('code')} - {error}")
                return None

        except Exception as e:
            logger.error(f"❌ Error creating project: {e}")
            return None

    def _get_project_id_by_name(self, name: str) -> Optional[str]:
        """Get project ID by name after creation"""
        projects = self.list_projects()
        if projects:
            for p in projects:
                if p.get("name") == name:
                    return p.get("id")
        return None


def get_credentials(nas_ip: str = "<NAS_PRIMARY_IP>") -> tuple:
    """
    Get NAS credentials using the established credential chain:
    Key Vault -> ProtonPass -> environment variables -> interactive
    """
    # Try nas_azure_vault_integration (same as @MANUS, DSM flows)
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration

        integration = NASAzureVaultIntegration(nas_ip=nas_ip)
        creds = integration.get_nas_credentials()
        if creds and creds.get("password"):
            username = creds.get("username", "backupadm")
            password = creds.get("password")
            logger.info(f"✅ Got credentials from Key Vault for {username}")
            return username, password
    except ImportError:
        logger.debug("nas_azure_vault_integration not available")
    except Exception as e:
        logger.debug(f"Key Vault credential retrieval failed: {e}")

    # Fall back to environment variables
    username = os.environ.get("NAS_USERNAME", "backupadm")
    password = os.environ.get("NAS_PASSWORD")

    if password:
        logger.info(f"✅ Got credentials from environment for {username}")
        return username, password

    # Interactive prompt as last resort
    import getpass

    password = getpass.getpass(f"Enter password for {username}@{nas_ip}: ")

    return username, password


def main():
    parser = argparse.ArgumentParser(description="Synology Container Manager API")
    parser.add_argument(
        "action",
        choices=["list", "start", "stop", "restart", "status", "containers"],
        help="Action to perform",
    )
    parser.add_argument("--project", "-p", help="Project name or ID")
    parser.add_argument("--container", "-c", help="Container ID or name")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument(
        "--nas-port", type=int, default=5000, help="NAS port (default: 5000 for HTTP)"
    )
    parser.add_argument("--username", "-u", help="DSM username")
    parser.add_argument("--password", help="DSM password (not recommended, use env vars)")

    args = parser.parse_args()

    # Get credentials
    username = args.username
    password = args.password

    if not username or not password:
        creds = get_credentials()
        username = username or creds[0]
        password = password or creds[1]

    if not password:
        print("❌ Password required. Set NAS_PASSWORD env var or provide --password")
        sys.exit(1)

    # Create manager and login
    manager = SynologyContainerManager(args.nas_ip, args.nas_port)

    if not manager.login(username, password):
        print("❌ Failed to login to NAS")
        sys.exit(1)

    try:
        if args.action == "list":
            projects = manager.list_projects()
            if projects:
                print("\n📦 Container Manager Projects:")
                print("-" * 60)
                for p in projects:
                    status = p.get("status", "unknown")
                    name = p.get("name", "unnamed")
                    pid = p.get("id", "no-id")
                    print(f"  [{status:8}] {name}")
                    print(f"            ID: {pid}")
                print("-" * 60)
            else:
                print("No projects found or failed to list")

        elif args.action == "containers":
            containers = manager.list_containers()
            if containers:
                print("\n🐳 Docker Containers:")
                print("-" * 60)
                for c in containers:
                    status = c.get("status", "unknown")
                    name = c.get("name", "unnamed")
                    cid = c.get("id", "no-id")[:12]
                    print(f"  [{status:10}] {name} ({cid})")
                print("-" * 60)
            else:
                print("No containers found or failed to list")

        elif args.action == "start":
            if args.project:
                # Find project by name if not a UUID
                if "-" not in args.project or len(args.project) < 36:
                    project = manager.get_project_by_name(args.project)
                    if project:
                        project_id = project.get("id")
                    else:
                        print(f"❌ Project '{args.project}' not found")
                        sys.exit(1)
                else:
                    project_id = args.project

                if manager.start_project(project_id):
                    print("✅ Project started successfully")
                else:
                    print("❌ Failed to start project")
                    sys.exit(1)
            elif args.container:
                if manager.start_container(args.container):
                    print("✅ Container started successfully")
                else:
                    print("❌ Failed to start container")
                    sys.exit(1)
            else:
                print("❌ Specify --project or --container")
                sys.exit(1)

        elif args.action == "stop":
            if args.project:
                if "-" not in args.project or len(args.project) < 36:
                    project = manager.get_project_by_name(args.project)
                    if project:
                        project_id = project.get("id")
                    else:
                        print(f"❌ Project '{args.project}' not found")
                        sys.exit(1)
                else:
                    project_id = args.project

                if manager.stop_project(project_id):
                    print("✅ Project stopped successfully")
                else:
                    print("❌ Failed to stop project")
                    sys.exit(1)
            elif args.container:
                if manager.stop_container(args.container):
                    print("✅ Container stopped successfully")
                else:
                    print("❌ Failed to stop container")
                    sys.exit(1)
            else:
                print("❌ Specify --project or --container")
                sys.exit(1)

        elif args.action == "restart":
            if args.project:
                if "-" not in args.project or len(args.project) < 36:
                    project = manager.get_project_by_name(args.project)
                    if project:
                        project_id = project.get("id")
                    else:
                        print(f"❌ Project '{args.project}' not found")
                        sys.exit(1)
                else:
                    project_id = args.project

                if manager.restart_project(project_id):
                    print("✅ Project restarted successfully")
                else:
                    print("❌ Failed to restart project")
                    sys.exit(1)
            else:
                print("❌ Specify --project for restart")
                sys.exit(1)

        elif args.action == "status":
            if args.project:
                if "-" not in args.project or len(args.project) < 36:
                    project = manager.get_project_by_name(args.project)
                    if project:
                        project_id = project.get("id")
                    else:
                        print(f"❌ Project '{args.project}' not found")
                        sys.exit(1)
                else:
                    project_id = args.project

                status = manager.get_project_status(project_id)
                if status:
                    print("\n📦 Project Status:")
                    print(json.dumps(status, indent=2))
                else:
                    print("❌ Failed to get project status")
            else:
                print("❌ Specify --project for status")
                sys.exit(1)

    finally:
        manager.logout()


if __name__ == "__main__":
    main()
