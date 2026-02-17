#!/usr/bin/env python3
"""
Deploy MCP Servers to NAS (DS1821PLUS) via Synology Container Manager
#JARVIS #DS1821PLUS #MCP #CONTAINER-MANAGER

Deploys Model Context Protocol (MCP) servers and n8n to the NAS using
Synology Container Manager. These services are lightweight and perfect
for NAS deployment.

Services to deploy:
- n8n (Workflow Automation Platform)
- MANUS MCP Server (Unified Control Interface)
- ElevenLabs MCP Server (Text-to-Speech)
- MCP Server Bridge (API bridge)
- Any other lightweight MCP servers
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

# Import MCP servers catalog
try:
    from mcp_servers_catalog import (
        MCP_SERVERS_CATALOG,
        get_mcp_server,
        list_all_mcp_servers,
        get_recommended_servers,
        get_mcp_servers_by_category
    )
    CATALOG_AVAILABLE = True
except ImportError:
    CATALOG_AVAILABLE = False
    MCP_SERVERS_CATALOG = {}
    get_mcp_server = lambda x: {}
    list_all_mcp_servers = lambda: []
    get_recommended_servers = lambda: []

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nas_mcp_deployment.log')
    ]
)
logger = logging.getLogger(__name__)


class NASMCPDeployment:
    """Deploy MCP servers to NAS (DS1821PLUS) via Synology Container Manager"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.nas_ip = "<NAS_PRIMARY_IP>"  # DS1821PLUS
        self.nas_hostname = "DS1821PLUS"
        self.ssh_port = 22

        # MCP Servers to deploy
        # Load from catalog if available, otherwise use defaults
        if CATALOG_AVAILABLE:
            # Use recommended servers by default
            recommended = get_recommended_servers()
            self.mcp_servers = {
                key: get_mcp_server(key) for key in recommended
            }
            logger.info(f"✅ Loaded {len(self.mcp_servers)} MCP servers from catalog")
        else:
            # Fallback to basic servers
            self.mcp_servers = {
            "n8n": {
                "name": "n8n",
                "description": "n8n - Workflow Automation Platform",
                "port": 5678,
                "dockerfile_path": None,  # Use official n8n image
                "context_path": None,
                "image": "n8nio/n8n:latest",
                "memory_limit": "2g",
                "cpu_limit": "2.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "n8n-data:/home/node/.n8n"
                ],
                "env_vars": {
                    "N8N_BASIC_AUTH_ACTIVE": "true",
                    "N8N_BASIC_AUTH_USER": "admin",
                    "N8N_HOST": self.nas_ip,
                    "N8N_PORT": "5678",
                    "N8N_PROTOCOL": "http",
                    "WEBHOOK_URL": f"http://{self.nas_ip}:5678/"
                }
            },
            "manus": {
                "name": "manus-mcp-server",
                "description": "MANUS MCP Server - Unified Control Interface",
                "port": 8085,
                "dockerfile_path": self.project_root / "containerization" / "services" / "manus-mcp-server" / "Dockerfile",
                "context_path": self.project_root / "containerization" / "services" / "manus-mcp-server",
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "manus-data:/app/data",
                    "manus-logs:/app/logs"
                ]
            },
            "elevenlabs": {
                "name": "elevenlabs-mcp-server",
                "description": "ElevenLabs MCP Server - Text-to-Speech and Audio Processing",
                "port": 8086,
                "dockerfile_path": self.project_root / "containerization" / "services" / "elevenlabs-mcp-server" / "Dockerfile",
                "context_path": self.project_root / "containerization" / "services" / "elevenlabs-mcp-server",
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "elevenlabs-output:/app/output",
                    "elevenlabs-data:/app/data"
                ],
                "env_vars": {
                    "AZURE_KEY_VAULT_URL": "https://jarvis-lumina.vault.azure.net/",
                    "ELEVENLABS_MCP_BASE_PATH": "/app/output"
                }
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

                # Check Docker availability
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
                    logger.info("   • Install Container Manager via: DSM Package Center")

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
                    logger.warning("   ⚠️  Docker daemon is not running")
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
            logger.warning("   ⚠️  paramiko library not installed")
            logger.info("   • Install: pip install paramiko")
        except Exception as e:
            status["error"] = str(e)
            logger.error(f"   ❌ Error checking Container Manager: {e}")

        return status

    async def create_nas_docker_compose(self) -> Path:
        """Create docker-compose.yml for MCP servers on NAS"""
        logger.info("📝 Creating docker-compose.yml for MCP servers on NAS...")

        # Create NAS deployment directory
        nas_deploy_dir = self.project_root / "containerization" / "services" / "nas-mcp-servers"
        nas_deploy_dir.mkdir(parents=True, exist_ok=True)

        # Create docker-compose.yml
        compose_content = f"""version: '3.8'

# MCP Servers - Deployed to NAS (DS1821PLUS) via Synology Container Manager
# Model Context Protocol servers for Cursor, Claude Desktop, and other MCP clients
#
# SECURITY POLICY: ALL API KEYS MUST BE STORED IN AZURE KEY VAULT
# Never hardcode keys in environment variables or config files

services:
"""

        # Add each MCP server
        for server_key, server_config in self.mcp_servers.items():
            compose_content += f"""
  # {server_config['description']}
  {server_config['name']}:
"""

            # Use official image if available, otherwise build from Dockerfile
            if 'image' in server_config and server_config['image']:
                compose_content += f"""    image: {server_config['image']}
"""
            elif 'context_path' in server_config and server_config['context_path']:
                # Build from local Dockerfile
                context_name = server_config['context_path'].name if hasattr(server_config['context_path'], 'name') else str(server_config['context_path']).split('/')[-1]
                compose_content += f"""    build:
      context: ../{context_name}
      dockerfile: Dockerfile
    image: lumina/{server_config['name']}:nas
"""
            else:
                # Fallback: use name as image (may need manual configuration)
                compose_content += f"""    image: {server_config['name']}:latest
"""

            compose_content += f"""    container_name: {server_config['name']}
    restart: {server_config['restart_policy']}

    ports:
      - "{server_config['port']}:{server_config['port']}"

    deploy:
      resources:
        limits:
          cpus: '{server_config['cpu_limit']}'
          memory: {server_config['memory_limit']}
        reservations:
          cpus: '0.25'
          memory: 128m

    environment:
      - SERVICE_NAME={server_config['name']}
      - PORT={server_config['port']}
      - NAS_HOST={self.nas_ip}
      - LOG_LEVEL=INFO
"""

            # Add environment variables if specified
            if 'env_vars' in server_config:
                for key, value in server_config['env_vars'].items():
                    compose_content += f"      - {key}={value}\n"

            # Add volumes
            if 'volumes' in server_config:
                compose_content += "    volumes:\n"
                for volume in server_config['volumes']:
                    compose_content += f"      - {volume}\n"

            # Health check - use custom if specified, otherwise default
            if 'healthcheck' in server_config and server_config['healthcheck']:
                hc = server_config['healthcheck']
                compose_content += f"""
    networks:
      - nas-mcp-network

    healthcheck:
      test: {hc.get('test', ['CMD', 'python3', '-c', 'import sys; sys.exit(0)'])}
      interval: {hc.get('interval', '30s')}
      timeout: {hc.get('timeout', '10s')}
      retries: {hc.get('retries', 3)}
      start_period: {hc.get('start_period', '10s')}
"""
            else:
                # Default health check
                compose_content += f"""
    networks:
      - nas-mcp-network

    healthcheck:
      test: ["CMD", "python3", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
"""

        # Collect all unique volumes from all servers
        all_volumes = set()
        for server_config in self.mcp_servers.values():
            if 'volumes' in server_config:
                for volume in server_config['volumes']:
                    # Extract volume name (before the colon)
                    volume_name = volume.split(':')[0]
                    all_volumes.add(volume_name)

        # Add volumes and networks
        compose_content += "\nvolumes:\n"
        for volume_name in sorted(all_volumes):
            compose_content += f"  {volume_name}:\n    driver: local\n"

        compose_content += """
networks:
  nas-mcp-network:
    driver: bridge
    name: nas-mcp-network
"""

        compose_file = nas_deploy_dir / "docker-compose.yml"
        compose_file.write_text(compose_content)
        logger.info(f"   ✅ Created: {compose_file}")

        return compose_file

    async def generate_deployment_instructions(self) -> Path:
        """Generate deployment instructions for NAS"""
        logger.info("📝 Generating deployment instructions...")

        instructions = f"""# MCP Servers Deployment to NAS (DS1821PLUS)

## Prerequisites

1. **Synology Container Manager** installed via DSM Package Center
2. **SSH access** to NAS ({self.nas_ip})
3. **Docker** available on NAS (via Container Manager)

## Deployment Steps

### 1. Copy Files to NAS

```bash
# Copy docker-compose.yml and service directories to NAS
scp -r containerization/services/nas-mcp-servers {self.ssh_username}@{self.nas_ip}:/volume1/docker/
scp -r containerization/services/manus-mcp-server {self.ssh_username}@{self.nas_ip}:/volume1/docker/
scp -r containerization/services/elevenlabs-mcp-server {self.ssh_username}@{self.ssh_username}@{self.nas_ip}:/volume1/docker/
```

### 2. SSH to NAS

```bash
ssh {self.ssh_username}@{self.nas_ip}
```

### 3. Navigate to Deployment Directory

```bash
cd /volume1/docker/nas-mcp-servers
```

### 4. Deploy Services

```bash
# Build and start all MCP servers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Verify Deployment

```bash
# Check if containers are running
docker ps | grep mcp-server

# Test health endpoints (if available)
curl http://localhost:8085/health  # MANUS
curl http://localhost:8086/health  # ElevenLabs
```

## Service Endpoints

After deployment, MCP servers will be available at:

- **n8n**: `http://{self.nas_ip}:5678`
- **MANUS MCP Server**: `http://{self.nas_ip}:8085`
- **ElevenLabs MCP Server**: `http://{self.nas_ip}:8086`

## Update Cursor MCP Configuration

Update `.cursor/mcp_config.json` to point to NAS:

```json
{{
  "mcpServers": {{
    "MANUS": {{
      "command": "ssh",
      "args": [
        "{self.ssh_username}@{self.nas_ip}",
        "docker exec -i manus-mcp-server python3 -m manus_mcp_server"
      ]
    }},
    "ElevenLabs": {{
      "command": "ssh",
      "args": [
        "{self.ssh_username}@{self.nas_ip}",
        "docker exec -i elevenlabs-mcp-server python3 -m elevenlabs_mcp"
      ],
      "env": {{
        "ELEVENLABS_API_KEY": "${{ELEVENLABS_API_KEY}}"
      }}
    }}
  }}
}}
```

## Troubleshooting

### Container Manager Not Running
- Open DSM → Package Center
- Find "Container Manager"
- Click "Open" to start

### Permission Denied
- Ensure user has Docker permissions
- May need to add user to docker group: `sudo usermod -aG docker {self.ssh_username}`

### Containers Not Starting
- Check logs: `docker-compose logs`
- Verify Docker is running: `docker ps`
- Check disk space: `df -h`

## Maintenance

### Update Services

```bash
cd /volume1/docker/nas-mcp-servers
docker-compose pull
docker-compose up -d --build
```

### Stop Services

```bash
docker-compose down
```

### Remove All

```bash
docker-compose down -v  # Also removes volumes
```
"""

        instructions_file = self.project_root / "containerization" / "services" / "nas-mcp-servers" / "DEPLOYMENT.md"
        instructions_file.write_text(instructions)
        logger.info(f"   ✅ Created: {instructions_file}")

        return instructions_file

    async def deploy_all_mcp_servers(self) -> Dict[str, bool]:
        """Generate deployment files for all MCP servers"""
        logger.info("🚀 Preparing MCP servers deployment to NAS...")
        logger.info("=" * 70)

        results = {}

        # Check connectivity
        nas_accessible = await self.check_nas_connectivity()
        if not nas_accessible:
            logger.error("❌ NAS is not accessible. Cannot proceed with deployment.")
            return {"connectivity": False}

        results["connectivity"] = True

        # Check Container Manager
        container_status = await self.check_container_manager()
        if not container_status.get("running"):
            logger.warning("⚠️  Container Manager may not be running")
            logger.info("   Deployment files will be created, but manual setup may be required")

        results["container_manager"] = container_status.get("running", False)

        # Create docker-compose.yml
        try:
            compose_file = await self.create_nas_docker_compose()
            results["docker_compose"] = compose_file.exists() if compose_file else False
        except Exception as e:
            logger.error(f"❌ Failed to create docker-compose.yml: {e}")
            results["docker_compose"] = False

        # Generate instructions
        try:
            instructions_file = await self.generate_deployment_instructions()
            results["instructions"] = instructions_file.exists() if instructions_file else False
        except Exception as e:
            logger.error(f"❌ Failed to create instructions: {e}")
            results["instructions"] = False

        logger.info("\n" + "=" * 70)
        logger.info("📊 Deployment Preparation Summary:")
        for key, value in results.items():
            status = "✅" if value else "❌"
            logger.info(f"   {status} {key}: {'Success' if value else 'Failed'}")

        if all(results.values()):
            logger.info("\n✅ All deployment files created successfully!")
            logger.info(f"   Next steps: See {instructions_file}")
        else:
            logger.warning("\n⚠️  Some steps failed. Check logs for details.")

        return results


async def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy MCP Servers to NAS (DS1821PLUS) via Synology Container Manager"
    )
    parser.add_argument(
        "action",
        choices=["check", "prepare", "deploy", "list", "add"],
        help="Action to perform"
    )
    parser.add_argument(
        "--servers",
        nargs="+",
        help="Specific MCP servers to deploy (for prepare/deploy actions)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Deploy all available MCP servers"
    )

    args = parser.parse_args()

    deployment = NASMCPDeployment()

    if args.action == "check":
        # Check connectivity and Container Manager
        nas_accessible = await deployment.check_nas_connectivity()
        if nas_accessible:
            container_status = await deployment.check_container_manager()

            print("\n📊 Container Manager Status:")
            print("=" * 70)
            print(json.dumps(container_status, indent=2))
            print("=" * 70)

    elif args.action == "prepare":
        results = await deployment.deploy_all_mcp_servers()
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)

    elif args.action == "list":
        if CATALOG_AVAILABLE:
            print("\n📋 Available MCP Servers:")
            print("=" * 70)
            categories = get_mcp_servers_by_category()
            for category, servers in categories.items():
                print(f"\n{category.upper()}:")
                for server_key in servers:
                    server = get_mcp_server(server_key)
                    if server:
                        print(f"  • {server_key}: {server.get('description', 'No description')}")
            print("\n" + "=" * 70)
            print(f"\nTotal: {len(list_all_mcp_servers())} MCP servers available")
            print("\nRecommended for NAS:")
            for key in get_recommended_servers():
                server = get_mcp_server(key)
                if server:
                    print(f"  ✅ {key}: {server.get('description', '')}")
        else:
            print("⚠️  MCP servers catalog not available")
            print("   Available servers in deployment:")
            for key, config in deployment.mcp_servers.items():
                print(f"  • {key}: {config.get('description', 'No description')}")

    elif args.action == "add":
        if not args.servers:
            logger.error("Please specify MCP servers to add: --servers server1 server2 ...")
            logger.info("Use 'list' action to see available servers")
            sys.exit(1)

        if not CATALOG_AVAILABLE:
            logger.error("MCP servers catalog not available")
            sys.exit(1)

        # Add specified servers to deployment
        for server_key in args.servers:
            server_config = get_mcp_server(server_key)
            if server_config:
                deployment.mcp_servers[server_key] = server_config
                logger.info(f"✅ Added {server_key}: {server_config.get('description', '')}")
            else:
                logger.warning(f"⚠️  Server not found: {server_key}")

        # Prepare deployment with added servers
        results = await deployment.deploy_all_mcp_servers()
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)

    elif args.action == "deploy":
        # If --all specified, load all servers from catalog
        if args.all and CATALOG_AVAILABLE:
            all_servers = list_all_mcp_servers()
            deployment.mcp_servers = {
                key: get_mcp_server(key) for key in all_servers
            }
            logger.info(f"🚀 Deploying ALL {len(deployment.mcp_servers)} MCP servers to NAS...")
        elif args.servers:
            # Deploy specific servers
            deployment.mcp_servers = {
                key: get_mcp_server(key) for key in args.servers if get_mcp_server(key)
            }
            logger.info(f"🚀 Deploying {len(deployment.mcp_servers)} specified MCP servers...")
        else:
            logger.info("🚀 Deploying recommended MCP servers to NAS...")

        logger.info("   (This will prepare files - actual deployment requires manual steps)")
        results = await deployment.deploy_all_mcp_servers()
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)


if __name__ == "__main__":


    asyncio.run(main())