#!/usr/bin/env python3
"""
Deploy Quality of Life (QOL) Docker Tools to NAS (DS1821PLUS)
#JARVIS #DS1821PLUS #QOL #DOCKER-MARKETPLACE

Deploys essential QOL tools from Docker Hub/Marketplace that make
LUMINA development and operations significantly better.

QOL Tools Categories:
- Container Management (Portainer, Watchtower)
- Monitoring & Observability (Prometheus, Grafana, Uptime Kuma)
- Reverse Proxy (Traefik, Nginx Proxy Manager)
- Logging (Loki, Grafana)
- Caching (Redis)
- Storage (MinIO)
- Backup (Duplicati, Vaultwarden)
- Development Tools (Code Server, Jupyter)
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
        logging.FileHandler('nas_qol_tools_deployment.log')
    ]
)
logger = logging.getLogger(__name__)


class NASQOLToolsDeployment:
    """Deploy QOL Docker tools to NAS (DS1821PLUS)"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.nas_ip = "<NAS_PRIMARY_IP>"  # DS1821PLUS
        self.nas_hostname = "DS1821PLUS"
        self.ssh_port = 22

        # QOL Tools Catalog
        self.qol_tools = {
            # Container Management
            "portainer": {
                "name": "portainer",
                "description": "Portainer - Docker Container Management UI",
                "image": "portainer/portainer-ce:latest",
                "port": 9000,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "always",
                "volumes": [
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "portainer-data:/data"
                ],
                "env_vars": {},
                "healthcheck": {
                    "test": ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9000/api/system/status"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "30s"
                }
            },

            "watchtower": {
                "name": "watchtower",
                "description": "Watchtower - Auto-update Docker containers",
                "image": "containrrr/watchtower:latest",
                "port": None,  # No exposed port
                "memory_limit": "256m",
                "cpu_limit": "0.5",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "/var/run/docker.sock:/var/run/docker.sock"
                ],
                "env_vars": {
                    "WATCHTOWER_CLEANUP": "true",
                    "WATCHTOWER_INCLUDE_STOPPED": "true",
                    "WATCHTOWER_POLL_INTERVAL": "3600"  # Check every hour
                },
                "healthcheck": None  # No health check needed
            },

            # Monitoring & Observability
            "uptime-kuma": {
                "name": "uptime-kuma",
                "description": "Uptime Kuma - Uptime monitoring and status page",
                "image": "louislam/uptime-kuma:latest",
                "port": 3001,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "uptime-kuma-data:/app/data"
                ],
                "env_vars": {
                    "UPTIME_KUMA_PORT": "3001"
                }
            },

            "prometheus": {
                "name": "prometheus",
                "description": "Prometheus - Metrics and monitoring",
                "image": "prom/prometheus:latest",
                "port": 9090,
                "memory_limit": "1g",
                "cpu_limit": "1.5",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "prometheus-data:/prometheus",
                    "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"
                ],
                "env_vars": {}
            },

            "grafana": {
                "name": "grafana",
                "description": "Grafana - Visualization and dashboards",
                "image": "grafana/grafana:latest",
                "port": 3000,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "grafana-data:/var/lib/grafana"
                ],
                "env_vars": {
                    "GF_SECURITY_ADMIN_PASSWORD": "admin",  # Change in production!
                    "GF_INSTALL_PLUGINS": "grafana-clock-panel,grafana-simple-json-datasource"
                }
            },

            # Reverse Proxy
            "traefik": {
                "name": "traefik",
                "description": "Traefik - Modern reverse proxy and load balancer",
                "image": "traefik:v2.11",
                "port": 80,
                "port_https": 443,
                "port_dashboard": 8080,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "/var/run/docker.sock:/var/run/docker.sock:ro",
                    "traefik-data:/etc/traefik"
                ],
                "env_vars": {
                    "TRAEFIK_API_DASHBOARD": "true",
                    "TRAEFIK_API_INSECURE": "true"
                }
            },

            "nginx-proxy-manager": {
                "name": "nginx-proxy-manager",
                "description": "Nginx Proxy Manager - Easy reverse proxy management",
                "image": "jc21/nginx-proxy-manager:latest",
                "port": 81,
                "port_http": 80,
                "port_https": 443,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "npm-data:/data",
                    "npm-letsencrypt:/etc/letsencrypt"
                ],
                "env_vars": {
                    "DB_MYSQL_HOST": "db",
                    "DB_MYSQL_PORT": 3306,
                    "DB_MYSQL_USER": "npm",
                    "DB_MYSQL_PASSWORD": "npm",
                    "DB_MYSQL_NAME": "npm"
                }
            },

            # Logging
            "loki": {
                "name": "loki",
                "description": "Loki - Log aggregation system",
                "image": "grafana/loki:latest",
                "port": 3100,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "loki-data:/loki"
                ],
                "env_vars": {}
            },

            # Caching & Storage
            "redis": {
                "name": "redis",
                "description": "Redis - In-memory data store and cache",
                "image": "redis:7-alpine",
                "port": 6379,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "redis-data:/data"
                ],
                "env_vars": {
                    "REDIS_PASSWORD": ""  # Set from Azure Key Vault
                }
            },

            "minio": {
                "name": "minio",
                "description": "MinIO - S3-compatible object storage",
                "image": "minio/minio:latest",
                "port": 9000,
                "port_console": 9001,
                "memory_limit": "1g",
                "cpu_limit": "1.5",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "minio-data:/data"
                ],
                "env_vars": {
                    "MINIO_ROOT_USER": "minioadmin",
                    "MINIO_ROOT_PASSWORD": ""  # Set from Azure Key Vault
                },
                "command": "server /data --console-address \":9001\""
            },

            # Backup
            "duplicati": {
                "name": "duplicati",
                "description": "Duplicati - Backup solution",
                "image": "linuxserver/duplicati:latest",
                "port": 8200,
                "memory_limit": "1g",
                "cpu_limit": "1.5",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "duplicati-data:/config",
                    "/volume1:/backup:ro"  # Read-only access to NAS volumes
                ],
                "env_vars": {
                    "PUID": "1000",
                    "PGID": "1000",
                    "TZ": "America/New_York"
                }
            },

            "vaultwarden": {
                "name": "vaultwarden",
                "description": "Vaultwarden - Bitwarden-compatible password manager",
                "image": "vaultwarden/server:latest",
                "port": 80,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "vaultwarden-data:/data"
                ],
                "env_vars": {
                    "SIGNUPS_ALLOWED": "false",
                    "ADMIN_TOKEN": ""  # Set from Azure Key Vault
                }
            },

            # Development Tools
            "code-server": {
                "name": "code-server",
                "description": "Code Server - VS Code in the browser",
                "image": "codercom/code-server:latest",
                "port": 8080,
                "memory_limit": "2g",
                "cpu_limit": "2.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "code-server-data:/home/coder",
                    "/volume1:/mnt/volume1:ro"
                ],
                "env_vars": {
                    "PASSWORD": ""  # Set from Azure Key Vault
                }
            },

            # Database
            "postgres": {
                "name": "postgres",
                "description": "PostgreSQL - Relational database",
                "image": "postgres:16-alpine",
                "port": 5432,
                "memory_limit": "1g",
                "cpu_limit": "1.5",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "postgres-data:/var/lib/postgresql/data"
                ],
                "env_vars": {
                    "POSTGRES_USER": "lumina",
                    "POSTGRES_PASSWORD": "",  # Set from Azure Key Vault
                    "POSTGRES_DB": "lumina"
                }
            },

            # Message Queue
            "rabbitmq": {
                "name": "rabbitmq",
                "description": "RabbitMQ - Message broker",
                "image": "rabbitmq:3-management-alpine",
                "port": 5672,
                "port_management": 15672,
                "memory_limit": "512m",
                "cpu_limit": "1.0",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "rabbitmq-data:/var/lib/rabbitmq"
                ],
                "env_vars": {
                    "RABBITMQ_DEFAULT_USER": "lumina",
                    "RABBITMQ_DEFAULT_PASS": ""  # Set from Azure Key Vault
                }
            },

            # File Sharing
            "filebrowser": {
                "name": "filebrowser",
                "description": "FileBrowser - Web file manager",
                "image": "filebrowser/filebrowser:latest",
                "port": 80,
                "memory_limit": "256m",
                "cpu_limit": "0.5",
                "restart_policy": "unless-stopped",
                "volumes": [
                    "/volume1:/srv:ro",  # Read-only access to NAS
                    "filebrowser-data:/config"
                ],
                "env_vars": {}
            },

            # Network Tools
            "whoami": {
                "name": "whoami",
                "description": "Whoami - Simple service to show container info",
                "image": "traefik/whoami:latest",
                "port": 80,
                "memory_limit": "64m",
                "cpu_limit": "0.25",
                "restart_policy": "unless-stopped",
                "volumes": [],
                "env_vars": {}
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

    async def create_docker_compose(self) -> Path:
        """Create docker-compose.yml for QOL tools"""
        logger.info("📝 Creating docker-compose.yml for QOL tools...")

        # Create deployment directory
        deploy_dir = self.project_root / "containerization" / "services" / "nas-qol-tools"
        deploy_dir.mkdir(parents=True, exist_ok=True)

        compose_content = """version: '3.8'

# Quality of Life (QOL) Docker Tools - Deployed to NAS (DS1821PLUS)
# Essential tools that make LUMINA development and operations better
#
# SECURITY POLICY: ALL PASSWORDS/KEYS MUST BE STORED IN AZURE KEY VAULT

services:
"""

        # Add each QOL tool
        for tool_key, tool_config in self.qol_tools.items():
            compose_content += f"""
  # {tool_config['description']}
  {tool_config['name']}:
    image: {tool_config['image']}
    container_name: {tool_config['name']}
    restart: {tool_config['restart_policy']}

    deploy:
      resources:
        limits:
          cpus: '{tool_config['cpu_limit']}'
          memory: {tool_config['memory_limit']}
        reservations:
          cpus: '0.25'
          memory: 128m

    environment:
      - SERVICE_NAME={tool_config['name']}
      - NAS_HOST={self.nas_ip}
      - LOG_LEVEL=INFO
"""

            # Add environment variables
            if 'env_vars' in tool_config:
                for key, value in tool_config['env_vars'].items():
                    compose_content += f"      - {key}={value}\n"

            # Add ports
            if tool_config.get('port'):
                compose_content += f"    ports:\n      - \"{tool_config['port']}:{tool_config['port']}\"\n"

            # Add additional ports if specified
            if 'port_https' in tool_config:
                compose_content += f"      - \"{tool_config['port_https']}:{tool_config['port_https']}\"\n"
            if 'port_dashboard' in tool_config:
                compose_content += f"      - \"{tool_config['port_dashboard']}:{tool_config['port_dashboard']}\"\n"
            if 'port_console' in tool_config:
                compose_content += f"      - \"{tool_config['port_console']}:{tool_config['port_console']}\"\n"
            if 'port_management' in tool_config:
                compose_content += f"      - \"{tool_config['port_management']}:{tool_config['port_management']}\"\n"

            # Add volumes
            if 'volumes' in tool_config and tool_config['volumes']:
                compose_content += "    volumes:\n"
                for volume in tool_config['volumes']:
                    compose_content += f"      - {volume}\n"

            # Add command if specified
            if 'command' in tool_config:
                compose_content += f"    command: {tool_config['command']}\n"

            # Add health check
            if 'healthcheck' in tool_config and tool_config['healthcheck']:
                hc = tool_config['healthcheck']
                compose_content += f"""
    healthcheck:
      test: {hc.get('test', ['CMD', 'true'])}
      interval: {hc.get('interval', '30s')}
      timeout: {hc.get('timeout', '10s')}
      retries: {hc.get('retries', 3)}
      start_period: {hc.get('start_period', '10s')}
"""

            compose_content += """
    networks:
      - nas-qol-network
"""

        # Collect all volumes
        all_volumes = set()
        for tool_config in self.qol_tools.values():
            if 'volumes' in tool_config:
                for volume in tool_config['volumes']:
                    volume_name = volume.split(':')[0]
                    if not volume_name.startswith('/'):
                        all_volumes.add(volume_name)

        # Add volumes and networks
        compose_content += "\nvolumes:\n"
        for volume_name in sorted(all_volumes):
            compose_content += f"  {volume_name}:\n    driver: local\n"

        compose_content += """
networks:
  nas-qol-network:
    driver: bridge
    name: nas-qol-network
"""

        compose_file = deploy_dir / "docker-compose.yml"
        compose_file.write_text(compose_content)
        logger.info(f"   ✅ Created: {compose_file}")

        return compose_file

    async def generate_deployment_instructions(self) -> Path:
        """Generate deployment instructions"""
        logger.info("📝 Generating deployment instructions...")

        # Create deployment directory
        deploy_dir = self.project_root / "containerization" / "services" / "nas-qol-tools"
        deploy_dir.mkdir(parents=True, exist_ok=True)

        instructions = f"""# QOL Docker Tools Deployment to NAS (DS1821PLUS)

## Overview

This deployment includes essential Quality of Life (QOL) tools that make LUMINA development and operations significantly better.

## Tools Included

### Container Management
- **Portainer** (port 9000) - Docker UI management
- **Watchtower** - Auto-update containers

### Monitoring & Observability
- **Uptime Kuma** (port 3001) - Uptime monitoring
- **Prometheus** (port 9090) - Metrics collection
- **Grafana** (port 3000) - Visualization dashboards

### Reverse Proxy
- **Traefik** (ports 80, 443, 8080) - Modern reverse proxy
- **Nginx Proxy Manager** (ports 81, 80, 443) - Easy proxy management

### Logging
- **Loki** (port 3100) - Log aggregation

### Caching & Storage
- **Redis** (port 6379) - In-memory cache
- **MinIO** (ports 9000, 9001) - S3-compatible storage

### Backup
- **Duplicati** (port 8200) - Backup solution
- **Vaultwarden** (port 80) - Password manager

### Development Tools
- **Code Server** (port 8080) - VS Code in browser
- **PostgreSQL** (port 5432) - Database
- **RabbitMQ** (ports 5672, 15672) - Message broker
- **FileBrowser** (port 80) - Web file manager

## Deployment

```bash
# 1. Copy files to NAS
scp -r containerization/services/nas-qol-tools {self.ssh_username}@{self.nas_ip}:/volume1/docker/

# 2. SSH to NAS
ssh {self.ssh_username}@{self.nas_ip}

# 3. Navigate and deploy
cd /volume1/docker/nas-qol-tools
docker-compose up -d

# 4. Check status
docker-compose ps
```

## Access Points

After deployment, access tools at:

- **Portainer**: http://{self.nas_ip}:9000
- **Uptime Kuma**: http://{self.nas_ip}:3001
- **Prometheus**: http://{self.nas_ip}:9090
- **Grafana**: http://{self.nas_ip}:3000 (admin/admin - change password!)
- **Traefik Dashboard**: http://{self.nas_ip}:8080
- **Nginx Proxy Manager**: http://{self.nas_ip}:81
- **Code Server**: http://{self.nas_ip}:8080
- **MinIO Console**: http://{self.nas_ip}:9001
- **RabbitMQ Management**: http://{self.nas_ip}:15672
- **Duplicati**: http://{self.nas_ip}:8200
- **FileBrowser**: http://{self.nas_ip}:80

## Security Notes

⚠️ **IMPORTANT**: Change all default passwords!
- Grafana: Change admin password immediately
- MinIO: Set MINIO_ROOT_PASSWORD
- PostgreSQL: Set POSTGRES_PASSWORD
- RabbitMQ: Set RABBITMQ_DEFAULT_PASS
- Code Server: Set PASSWORD
- Vaultwarden: Set ADMIN_TOKEN

All passwords should be stored in Azure Key Vault and retrieved at runtime.

## Resource Usage

Total estimated resources:
- **CPU**: ~15-20 cores (with limits)
- **Memory**: ~15-20GB (with limits)
- **Storage**: Varies by usage

Monitor resources and adjust limits as needed.

## Benefits

✅ **Portainer**: Easy container management via web UI
✅ **Watchtower**: Automatic container updates
✅ **Uptime Kuma**: Monitor all services
✅ **Prometheus/Grafana**: Full observability stack
✅ **Traefik**: Easy reverse proxy and SSL
✅ **Redis**: Fast caching layer
✅ **MinIO**: S3-compatible storage
✅ **Code Server**: Code from anywhere
✅ **FileBrowser**: Easy file management

---

**#JARVIS #QOL #DOCKER-MARKETPLACE #NAS #DS1821PLUS**
"""

        instructions_file = deploy_dir / "DEPLOYMENT.md"
        instructions_file.write_text(instructions)
        logger.info(f"   ✅ Created: {instructions_file}")

        return instructions_file

    async def copy_files_to_nas(self) -> bool:
        """Copy deployment files to NAS via SCP"""
        if not self.ssh_username or not self.ssh_password:
            logger.error("❌ NAS credentials not loaded. Cannot copy files.")
            return False

        logger.info("📤 Copying deployment files to NAS...")

        deploy_dir = self.project_root / "containerization" / "services" / "nas-qol-tools"
        if not deploy_dir.exists():
            logger.error(f"❌ Deployment directory not found: {deploy_dir}")
            return False

        try:
            # Try using paramiko first
            import paramiko
            from scp import SCPClient

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.info(f"   Connecting to {self.nas_ip}...")
            ssh.connect(
                self.nas_ip,
                port=self.ssh_port,
                username=self.ssh_username,
                password=self.ssh_password,
                timeout=10,
                allow_agent=False,      # Skip SSH agent (prevents 1st publickey attempt)
                look_for_keys=False     # Skip key file lookup (prevents 2nd publickey attempt)
            )

            # Create remote directory
            stdin, stdout, stderr = ssh.exec_command("mkdir -p /volume1/docker/nas-qol-tools")
            stdout.channel.recv_exit_status()

            # Copy files using SCP
            with SCPClient(ssh.get_transport()) as scp:
                logger.info("   Copying docker-compose.yml...")
                scp.put(str(deploy_dir / "docker-compose.yml"), "/volume1/docker/nas-qol-tools/docker-compose.yml")

                if (deploy_dir / "DEPLOYMENT.md").exists():
                    logger.info("   Copying DEPLOYMENT.md...")
                    scp.put(str(deploy_dir / "DEPLOYMENT.md"), "/volume1/docker/nas-qol-tools/DEPLOYMENT.md")

            ssh.close()
            logger.info("   ✅ Files copied successfully")
            return True

        except ImportError:
            # Fallback to PowerShell SCP
            logger.info("   Using PowerShell SCP...")
            try:
                deploy_path = str(deploy_dir).replace('\\', '/')
                compose_file = deploy_dir / "docker-compose.yml"

                # Use PowerShell's scp command
                ps_cmd = f"""
$password = ConvertTo-SecureString '{self.ssh_password}' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('{self.ssh_username}', $password)
$session = New-PSSession -ComputerName {self.nas_ip} -Credential $credential -Port {self.ssh_port}
Invoke-Command -Session $session -ScriptBlock {{ mkdir -p /volume1/docker/nas-qol-tools }}
Copy-Item -Path '{compose_file}' -Destination '/volume1/docker/nas-qol-tools/docker-compose.yml' -ToSession $session
Remove-PSSession $session
"""
                result = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info("   ✅ Files copied successfully via PowerShell")
                    return True
                else:
                    logger.warning(f"   PowerShell SCP failed: {result.stderr}")
                    logger.info(f"   Manual copy: scp {compose_file} {self.ssh_username}@{self.nas_ip}:/volume1/docker/nas-qol-tools/")
                    return False
            except Exception as e:
                logger.warning(f"   PowerShell SCP error: {e}")
                logger.info(f"   Manual copy: scp {compose_file} {self.ssh_username}@{self.nas_ip}:/volume1/docker/nas-qol-tools/")
                return False
        except Exception as e:
            logger.error(f"   ❌ Failed to copy files: {e}")
            logger.info(f"   Manual copy: scp {deploy_dir / 'docker-compose.yml'} {self.ssh_username}@{self.nas_ip}:/volume1/docker/nas-qol-tools/")
            return False

    async def deploy_via_ssh(self) -> bool:
        """Deploy containers via SSH"""
        if not self.ssh_username or not self.ssh_password:
            logger.error("❌ NAS credentials not loaded. Cannot deploy.")
            return False

        logger.info("🚀 Deploying QOL tools to NAS...")

        try:
            import paramiko

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.info(f"   Connecting to {self.nas_ip}...")
            ssh.connect(
                self.nas_ip,
                port=self.ssh_port,
                username=self.ssh_username,
                password=self.ssh_password,
                timeout=10,
                allow_agent=False,      # Skip SSH agent (prevents 1st publickey attempt)
                look_for_keys=False     # Skip key file lookup (prevents 2nd publickey attempt)
            )

            # Navigate to directory and deploy
            commands = [
                "cd /volume1/docker/nas-qol-tools",
                "docker-compose pull",  # Pull latest images
                "docker-compose up -d",  # Start containers
                "docker-compose ps"  # Show status
            ]

            for cmd in commands:
                logger.info(f"   Running: {cmd}")
                stdin, stdout, stderr = ssh.exec_command(cmd)

                # Wait for command to complete
                exit_status = stdout.channel.recv_exit_status()

                # Read output
                output = stdout.read().decode('utf-8')
                errors = stderr.read().decode('utf-8')

                if exit_status == 0:
                    if output:
                        logger.info(f"      {output[:500]}")  # First 500 chars
                else:
                    logger.warning(f"      Exit code: {exit_status}")
                    if errors:
                        logger.warning(f"      Errors: {errors[:500]}")

            ssh.close()
            logger.info("   ✅ Deployment completed")
            return True

        except ImportError:
            # Fallback to PowerShell SSH
            logger.info("   Using PowerShell SSH...")
            try:
                ps_cmd = f"""
$password = ConvertTo-SecureString '{self.ssh_password}' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('{self.ssh_username}', $password)
$session = New-PSSession -ComputerName {self.nas_ip} -Credential $credential -Port {self.ssh_port}
Invoke-Command -Session $session -ScriptBlock {{
    cd /volume1/docker/nas-qol-tools
    docker-compose pull
    docker-compose up -d
    docker-compose ps
}}
Remove-PSSession $session
"""
                result = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes for docker pull
                )

                if result.returncode == 0:
                    logger.info("   ✅ Deployment completed via PowerShell")
                    if result.stdout:
                        logger.info(f"      {result.stdout[:500]}")
                    return True
                else:
                    logger.warning(f"   PowerShell deployment failed: {result.stderr}")
                    logger.info(f"   Manual deployment:")
                    logger.info(f"      ssh {self.ssh_username}@{self.nas_ip}")
                    logger.info(f"      cd /volume1/docker/nas-qol-tools")
                    logger.info(f"      docker-compose up -d")
                    return False
            except Exception as e:
                logger.warning(f"   PowerShell SSH error: {e}")
                logger.info(f"   Manual deployment:")
                logger.info(f"      ssh {self.ssh_username}@{self.nas_ip}")
                logger.info(f"      cd /volume1/docker/nas-qol-tools")
                logger.info(f"      docker-compose up -d")
                return False
        except Exception as e:
            logger.error(f"   ❌ Deployment failed: {e}")
            logger.info(f"   Manual deployment:")
            logger.info(f"      ssh {self.ssh_username}@{self.nas_ip}")
            logger.info(f"      cd /volume1/docker/nas-qol-tools")
            logger.info(f"      docker-compose up -d")
            return False

    async def deploy_all_tools(self, deploy: bool = False) -> Dict[str, bool]:
        """Generate deployment files for all QOL tools"""
        action = "Deploying" if deploy else "Preparing"
        logger.info(f"🚀 {action} QOL tools deployment to NAS...")
        logger.info("=" * 70)

        results = {}

        # Check connectivity
        nas_accessible = await self.check_nas_connectivity()
        if not nas_accessible:
            logger.error("❌ NAS is not accessible. Cannot proceed.")
            return {"connectivity": False}

        results["connectivity"] = True

        # Create docker-compose.yml
        try:
            compose_file = await self.create_docker_compose()
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

        # Deploy if requested
        if deploy:
            # Copy files
            results["copy_files"] = await self.copy_files_to_nas()

            # Deploy containers
            if results["copy_files"]:
                results["deploy_containers"] = await self.deploy_via_ssh()
            else:
                results["deploy_containers"] = False
                logger.warning("   ⚠️  Skipping container deployment (files not copied)")

        logger.info("\n" + "=" * 70)
        logger.info("📊 Deployment Summary:")
        for key, value in results.items():
            status = "✅" if value else "❌"
            logger.info(f"   {status} {key}: {'Success' if value else 'Failed'}")

        if deploy and all(results.values()):
            logger.info("\n✅ All QOL tools deployed successfully!")
            logger.info(f"   Access Portainer at: http://{self.nas_ip}:9000")
        elif not deploy and all(results.values()):
            logger.info("\n✅ All deployment files created successfully!")
            logger.info(f"   Next steps: See {instructions_file}")
            logger.info(f"   Or run: python scripts/python/deploy_qol_tools_to_nas.py deploy")
        else:
            logger.warning("\n⚠️  Some steps failed. Check logs for details.")

        return results


async def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy QOL Docker Tools to NAS (DS1821PLUS)"
    )
    parser.add_argument(
        "action",
        choices=["check", "prepare", "deploy", "list"],
        help="Action to perform"
    )

    args = parser.parse_args()

    deployment = NASQOLToolsDeployment()

    if args.action == "check":
        nas_accessible = await deployment.check_nas_connectivity()
        sys.exit(0 if nas_accessible else 1)

    elif args.action == "list":
        print("\n📋 Available QOL Tools:")
        print("=" * 70)
        categories = {
            "Container Management": ["portainer", "watchtower"],
            "Monitoring": ["uptime-kuma", "prometheus", "grafana"],
            "Reverse Proxy": ["traefik", "nginx-proxy-manager"],
            "Logging": ["loki"],
            "Caching & Storage": ["redis", "minio"],
            "Backup": ["duplicati", "vaultwarden"],
            "Development": ["code-server", "postgres", "rabbitmq", "filebrowser"],
            "Network Tools": ["whoami"]
        }

        for category, tools in categories.items():
            print(f"\n{category}:")
            for tool_key in tools:
                tool = deployment.qol_tools.get(tool_key, {})
                if tool:
                    port_info = f" (port {tool.get('port', 'N/A')})" if tool.get('port') else ""
                    print(f"  • {tool_key}: {tool.get('description', '')}{port_info}")

        print("\n" + "=" * 70)
        print(f"\nTotal: {len(deployment.qol_tools)} QOL tools available")

    elif args.action == "prepare":
        results = await deployment.deploy_all_tools(deploy=False)
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)

    elif args.action == "deploy":
        results = await deployment.deploy_all_tools(deploy=True)
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)


if __name__ == "__main__":


    asyncio.run(main())