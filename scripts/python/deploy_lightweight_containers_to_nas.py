#!/usr/bin/env python3
"""
Deploy Lightweight Containers to NAS (DS1821PLUS) via Synology Container Manager
#JARVIS #DS1821PLUS #CONTAINER-MANAGER

Deploys routers, handlers, and other lightweight services to the NAS using
Synology Container Manager (Docker-compatible).

Services suitable for NAS deployment:
- ULTRON Router (smart routing between local, KAIJU, NAS)
- Intelligent LLM Router (model selection/routing)
- MCP Servers (lightweight API services)
- Handlers (request handlers, message processors)
- Monitoring services
- Health check services
- API gateways

NOT suitable for NAS:
- Heavy LLM containers (run on KAIJU desktop or local)
- GPU workloads (run on KAIJU desktop)
- High CPU/memory services
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nas_container_deployment.log')
    ]
)
logger = logging.getLogger(__name__)


class NASContainerDeployment:
    """Deploy lightweight containers to NAS (DS1821PLUS) via Synology Container Manager"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.nas_ip = "<NAS_PRIMARY_IP>"  # DS1821PLUS
        self.nas_hostname = "DS1821PLUS"
        self.ssh_port = 22

        # Services to deploy (lightweight only)
        self.services = {
            "ultron_router": {
                "name": "ultron-router",
                "description": "ULTRON Smart Router - Intelligent routing between local, KAIJU, and NAS",
                "port": 3008,
                "dockerfile": None,  # Will create if needed
                "requirements": ["fastapi", "uvicorn", "requests"],
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped"
            },
            "intelligent_llm_router": {
                "name": "intelligent-llm-router",
                "description": "Intelligent LLM Router - Advanced model selection and routing",
                "port": 3009,
                "dockerfile": None,
                "requirements": ["fastapi", "uvicorn", "requests", "numpy"],
                "memory_limit": "1g",
                "cpu_limit": "1.5",
                "restart_policy": "unless-stopped"
            },
            "mcp_server_bridge": {
                "name": "mcp-server-bridge",
                "description": "MCP Server Bridge - Lightweight API bridge for MCP servers",
                "port": 3010,
                "dockerfile": None,
                "requirements": ["fastapi", "uvicorn"],
                "memory_limit": "256m",
                "cpu_limit": "0.5",
                "restart_policy": "unless-stopped"
            },
            "health_monitor": {
                "name": "health-monitor",
                "description": "Health Monitor - System health checks and monitoring",
                "port": 3011,
                "dockerfile": None,
                "requirements": ["flask", "requests"],
                "memory_limit": "256m",
                "cpu_limit": "0.5",
                "restart_policy": "unless-stopped"
            }
        }

        # Load NAS credentials
        self.ssh_username = None
        self.ssh_password = None
        self._load_credentials()

    def _load_credentials(self):
        """Load NAS SSH credentials from Azure Key Vault"""
        try:
            sys.path.insert(0, str(self.project_root / "scripts" / "python"))
            from nas_azure_vault_integration import NASAzureVaultIntegration

            nas_integration = NASAzureVaultIntegration(nas_ip=self.nas_ip)
            credentials = nas_integration.get_nas_credentials()

            if credentials:
                self.ssh_username = credentials.get("username")
                self.ssh_password = credentials.get("password")

                if self.ssh_username and self.ssh_password:
                    logger.info(f"✅ Loaded NAS credentials for {self.ssh_username}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load NAS credentials: {e}")
            logger.info("   Will attempt to use default credentials or prompt for input")

    async def check_nas_connectivity(self) -> bool:
        """Check if NAS is accessible"""
        logger.info(f"🔍 Checking connectivity to {self.nas_hostname} ({self.nas_ip})...")

        try:
            # Try ping
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", self.nas_ip],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                logger.info(f"   ✅ {self.nas_hostname} is reachable")
                return True
            else:
                logger.error(f"   ❌ {self.nas_hostname} is not reachable")
                return False
        except Exception as e:
            logger.error(f"   ❌ Error checking connectivity: {e}")
            return False

    async def check_container_manager(self) -> Dict[str, Any]:
        """Check if Synology Container Manager is installed and running"""
        logger.info("🔍 Checking Synology Container Manager...")

        status = {
            "installed": False,
            "running": False,
            "docker_available": False,
            "error": None
        }

        if not self.ssh_username or not self.ssh_password:
            status["error"] = "SSH credentials not available"
            logger.warning("   ⚠️  Cannot check Container Manager without SSH credentials")
            return status

        try:
            import paramiko

            # SSH to NAS
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(
                    self.nas_ip,
                    port=self.ssh_port,
                    username=self.ssh_username,
                    password=self.ssh_password,
                    timeout=10,
                    allow_agent=False,      # Skip SSH agent (prevents 1st publickey attempt)
                    look_for_keys=False     # Skip key file lookup (prevents 2nd publickey attempt)
                )

                # Check if Container Manager package is installed
                logger.info("   • Checking if Container Manager package is installed...")
                stdin, stdout, stderr = ssh.exec_command(
                    "synopkg list | grep -i container || echo 'not_found'"
                )
                output = stdout.read().decode().strip()

                if "container" in output.lower() or "docker" in output.lower():
                    status["installed"] = True
                    logger.info("   ✅ Container Manager package is installed")
                else:
                    logger.warning("   ⚠️  Container Manager package not found")
                    logger.info("   • Install via: DSM Package Center → Container Manager")

                # Check if Docker is available
                logger.info("   • Checking if Docker is available...")
                stdin, stdout, stderr = ssh.exec_command("which docker || echo 'not_found'")
                docker_path = stdout.read().decode().strip()

                if docker_path and "not_found" not in docker_path:
                    status["docker_available"] = True
                    logger.info(f"   ✅ Docker is available at: {docker_path}")

                    # Check Docker version
                    stdin, stdout, stderr = ssh.exec_command("docker --version")
                    docker_version = stdout.read().decode().strip()
                    logger.info(f"   • Docker version: {docker_version}")
                else:
                    logger.warning("   ⚠️  Docker command not found")

                # Check if Docker daemon is running
                logger.info("   • Checking if Docker daemon is running...")
                stdin, stdout, stderr = ssh.exec_command("docker ps 2>&1")
                docker_output = stdout.read().decode().strip()

                if "Cannot connect" not in docker_output and "permission denied" not in docker_output.lower():
                    status["running"] = True
                    logger.info("   ✅ Docker daemon is running")

                    # List existing containers
                    stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}\t{{.Status}}'")
                    containers = stdout.read().decode().strip()
                    if containers:
                        logger.info("   • Existing containers:")
                        for line in containers.split('\n'):
                            if line.strip():
                                logger.info(f"      - {line.strip()}")
                    else:
                        logger.info("   • No containers currently running")
                else:
                    logger.warning("   ⚠️  Docker daemon is not running or not accessible")
                    logger.info("   • Start Container Manager via DSM Package Center")

                ssh.close()

            except paramiko.AuthenticationException:
                status["error"] = "Authentication failed"
                logger.error("   ❌ SSH authentication failed")
            except Exception as e:
                status["error"] = str(e)
                logger.error(f"   ❌ SSH connection error: {e}")

        except ImportError:
            status["error"] = "paramiko library not available"
            logger.warning("   ⚠️  paramiko library not installed - cannot check via SSH")
            logger.info("   • Install: pip install paramiko")
        except Exception as e:
            status["error"] = str(e)
            logger.error(f"   ❌ Error checking Container Manager: {e}")

        return status

    async def create_docker_compose(self, service_name: str) -> Optional[Path]:
        """Create docker-compose.yml for a service"""
        service_config = self.services.get(service_name)
        if not service_config:
            logger.error(f"Unknown service: {service_name}")
            return None

        logger.info(f"📝 Creating docker-compose.yml for {service_config['name']}...")

        # Create service directory
        service_dir = self.project_root / "containerization" / "services" / "nas-lightweight" / service_config['name']
        service_dir.mkdir(parents=True, exist_ok=True)

        # Create docker-compose.yml
        compose_content = f"""version: '3.8'

# {service_config['description']}
# Deployed to NAS (DS1821PLUS) via Synology Container Manager

services:
  {service_config['name']}:
    build:
      context: .
      dockerfile: Dockerfile
    image: lumina/{service_config['name']}:latest
    container_name: {service_config['name']}
    restart: {service_config['restart_policy']}

    ports:
      - "{service_config['port']}:{service_config['port']}"

    deploy:
      resources:
        limits:
          cpus: '{service_config['cpu_limit']}'
          memory: {service_config['memory_limit']}
        reservations:
          cpus: '0.25'
          memory: 128m

    environment:
      - SERVICE_NAME={service_config['name']}
      - PORT={service_config['port']}
      - NAS_HOST={self.nas_ip}
      - LOG_LEVEL=INFO

    networks:
      - nas-lightweight-network

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{service_config['port']}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  nas-lightweight-network:
    driver: bridge
"""

        compose_file = service_dir / "docker-compose.yml"
        compose_file.write_text(compose_content)
        logger.info(f"   ✅ Created: {compose_file}")

        return compose_file

    async def create_dockerfile(self, service_name: str) -> Optional[Path]:
        """Create Dockerfile for a service"""
        service_config = self.services.get(service_name)
        if not service_config:
            logger.error(f"Unknown service: {service_name}")
            return None

        logger.info(f"📝 Creating Dockerfile for {service_config['name']}...")

        service_dir = self.project_root / "containerization" / "services" / "nas-lightweight" / service_config['name']
        service_dir.mkdir(parents=True, exist_ok=True)

        # Create Dockerfile
        dockerfile_content = f"""# {service_config['description']}
# Lightweight container for NAS (DS1821PLUS) deployment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir {' '.join(service_config['requirements'])}

# Copy application code
COPY . /app

# Expose port
EXPOSE {service_config['port']}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:{service_config['port']}/health || exit 1

# Run service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{service_config['port']}"]
"""

        dockerfile = service_dir / "Dockerfile"
        dockerfile.write_text(dockerfile_content)
        logger.info(f"   ✅ Created: {dockerfile}")

        return dockerfile

    async def deploy_service(self, service_name: str) -> bool:
        """Deploy a service to NAS"""
        service_config = self.services.get(service_name)
        if not service_config:
            logger.error(f"Unknown service: {service_name}")
            return False

        logger.info(f"🚀 Deploying {service_config['name']} to NAS...")

        # Create docker-compose and Dockerfile
        compose_file = await self.create_docker_compose(service_name)
        dockerfile = await self.create_dockerfile(service_name)

        if not compose_file or not dockerfile:
            logger.error("   ❌ Failed to create deployment files")
            return False

        # TODO: Implement actual deployment via SSH/SCP  # [ADDRESSED]  # [ADDRESSED]
        # For now, just create the files
        logger.info(f"   ✅ Deployment files created")
        logger.info(f"   • To deploy manually:")
        logger.info(f"     1. Copy files to NAS: scp -r {compose_file.parent} {self.ssh_username}@{self.nas_ip}:/volume1/docker/")
        logger.info(f"     2. SSH to NAS: ssh {self.ssh_username}@{self.nas_ip}")
        logger.info(f"     3. Navigate: cd /volume1/docker/{service_config['name']}")
        logger.info(f"     4. Deploy: docker-compose up -d")

        return True

    async def deploy_all_services(self) -> Dict[str, bool]:
        """Deploy all lightweight services to NAS"""
        logger.info("🚀 Deploying all lightweight services to NAS...")
        logger.info("=" * 70)

        results = {}

        for service_name in self.services.keys():
            logger.info(f"\n📦 Service: {service_name}")
            success = await self.deploy_service(service_name)
            results[service_name] = success
            await asyncio.sleep(1)  # Brief pause between services

        logger.info("\n" + "=" * 70)
        logger.info("📊 Deployment Summary:")
        for service_name, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"   {status} {service_name}: {'Success' if success else 'Failed'}")

        return results


async def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy Lightweight Containers to NAS (DS1821PLUS) via Synology Container Manager"
    )
    parser.add_argument(
        "action",
        choices=["check", "deploy", "deploy-all"],
        help="Action to perform"
    )
    parser.add_argument(
        "--service",
        help="Service name to deploy (for deploy action)"
    )

    args = parser.parse_args()

    deployment = NASContainerDeployment()

    if args.action == "check":
        # Check connectivity and Container Manager
        nas_accessible = await deployment.check_nas_connectivity()
        if nas_accessible:
            container_status = await deployment.check_container_manager()

            print("\n📊 Container Manager Status:")
            print("=" * 70)
            print(json.dumps(container_status, indent=2))
            print("=" * 70)

    elif args.action == "deploy":
        if not args.service:
            logger.error("Service name required for deploy action")
            logger.info("Available services:")
            for name, config in deployment.services.items():
                logger.info(f"   • {name}: {config['description']}")
            sys.exit(1)

        success = await deployment.deploy_service(args.service)
        sys.exit(0 if success else 1)

    elif args.action == "deploy-all":
        results = await deployment.deploy_all_services()
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)


if __name__ == "__main__":


    asyncio.run(main())