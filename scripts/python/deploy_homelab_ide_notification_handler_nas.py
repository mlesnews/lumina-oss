#!/usr/bin/env python3
"""
Deploy @homelab IDE Notification Handler to NAS Container Manager
USS Lumina - @scotty (Windows Systems Architect)

Deploys the IDE notification handler as a Docker container on NAS Container Manager.
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
import shutil

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeployHomelabIDENotificationsNAS")

# Import NAS integration
try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    logger.warning("NAS Azure Vault integration not available")
    NASAzureVaultIntegration = None


class HomelabIDENotificationHandlerDeployer:
    """Deploy IDE notification handler to NAS Container Manager"""

    def __init__(self, project_root: Path, nas_ip: str = "<NAS_PRIMARY_IP>"):
        self.project_root = project_root
        self.nas_ip = nas_ip
        self.nas_port = 5000
        self.logger = logger

        # Docker paths
        self.docker_dir = self.project_root / "docker" / "homelab-ide-notification-handler"
        self.docker_dir.mkdir(parents=True, exist_ok=True)

        # NAS paths
        self.nas_docker_path = "/volume1/docker/homelab-ide-notification-handler"

        self.logger.info("✅ IDE Notification Handler Deployer initialized")

    def get_nas_credentials(self) -> Optional[Dict[str, str]]:
        """Get NAS credentials from Azure Key Vault"""
        if not NASAzureVaultIntegration:
            return None

        try:
            nas_integration = NASAzureVaultIntegration(nas_ip=self.nas_ip)
            credentials = nas_integration.get_nas_credentials()
            return credentials
        except Exception as e:
            self.logger.warning(f"Could not get NAS credentials: {e}")
            return None

    def create_dockerfile(self) -> Dict[str, Any]:
        """Create Dockerfile for IDE notification handler"""
        self.logger.info("Creating Dockerfile...")

        dockerfile_content = """FROM python:3.11-slim

# Metadata
LABEL maintainer="JARVIS @scotty - USS Lumina"
LABEL description="@homelab IDE Notification Handler - Automatically handles all IDE/VS Code/Cursor notifications"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    xvfb \\
    x11vnc \\
    fluxbox \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV PROJECT_ROOT=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run the notification handler
CMD ["python", "scripts/python/jarvis_homelab_ide_notification_handler.py", "--monitor", "--interval", "5"]
"""

        dockerfile_path = self.docker_dir / "Dockerfile"
        try:
            dockerfile_path.write_text(dockerfile_content, encoding='utf-8')
            self.logger.info(f"✅ Dockerfile created: {dockerfile_path}")
            return {"success": True, "path": str(dockerfile_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create Dockerfile: {e}")
            return {"success": False, "error": str(e)}

    def create_requirements_txt(self) -> Dict[str, Any]:
        """Create requirements.txt"""
        self.logger.info("Creating requirements.txt...")

        requirements_content = """# @homelab IDE Notification Handler Dependencies

# Core dependencies
pyautogui>=0.9.54
pygetwindow>=0.0.9
Pillow>=10.0.0
opencv-python-headless>=4.8.0

# System integration
psutil>=5.9.0

# Logging and utilities
python-dateutil>=2.8.2
"""

        requirements_path = self.docker_dir / "requirements.txt"
        try:
            requirements_path.write_text(requirements_content, encoding='utf-8')
            self.logger.info(f"✅ requirements.txt created: {requirements_path}")
            return {"success": True, "path": str(requirements_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create requirements.txt: {e}")
            return {"success": False, "error": str(e)}

    def create_docker_compose(self) -> Dict[str, Any]:
        """Create docker-compose.yml for Container Manager"""
        self.logger.info("Creating docker-compose.yml...")

        compose_content = f"""version: '3.8'

services:
  homelab-ide-notification-handler:
    build:
      context: {self.nas_docker_path}
      dockerfile: Dockerfile
      args:
        - PROJECT_ROOT=/app
    container_name: homelab-ide-notification-handler
    image: homelab-ide-notification-handler:latest
    restart: unless-stopped

    # Network configuration
    network_mode: host  # Use host network for local IDE access

    # Environment variables
    environment:
      - PYTHONUNBUFFERED=1
      - DISPLAY=:99
      - PROJECT_ROOT=/app
      - MONITOR_INTERVAL=5
      - LOG_LEVEL=INFO

    # Volume mounts
    volumes:
      # Mount project root for access to scripts
      - {self.nas_docker_path}:/app:ro
      # Mount data directory for logs and state
      - {self.nas_docker_path}/data:/app/data
      - {self.nas_docker_path}/logs:/app/logs
      # Mount X11 socket for GUI access (if needed)
      - /tmp/.X11-unix:/tmp/.X11-unix:ro

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

    # Labels for Container Manager
    labels:
      - "com.synology.dsm.notify=true"
      - "com.synology.dsm.description=@homelab IDE Notification Handler - Automatically handles all IDE/VS Code/Cursor notifications"
      - "com.synology.dsm.category=automation"
      - "com.synology.dsm.author=JARVIS @scotty - USS Lumina"
      - "com.synology.dsm.version=1.0.0"
"""

        compose_path = self.docker_dir / "docker-compose.yml"
        try:
            compose_path.write_text(compose_content, encoding='utf-8')
            self.logger.info(f"✅ docker-compose.yml created: {compose_path}")
            return {"success": True, "path": str(compose_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create docker-compose.yml: {e}")
            return {"success": False, "error": str(e)}

    def copy_files_to_nas(self) -> Dict[str, Any]:
        """Copy Docker files to NAS"""
        self.logger.info(f"Copying files to NAS: {self.nas_ip}:{self.nas_docker_path}...")

        credentials = self.get_nas_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Could not get NAS credentials",
                "note": "Files are ready locally. Copy manually or use RDP."
            }

        username = credentials.get("username")

        # Create PowerShell script to copy files via SMB
        ps_script = f"""
$nasIP = "{self.nas_ip}"
$username = "{username}"
$localPath = "{self.docker_dir}"
$nasPath = "{self.nas_docker_path}"

Write-Host "📦 Copying IDE Notification Handler files to NAS..." -ForegroundColor Green
Write-Host ""

# Map network drive
$drive = "Z:"
$uncPath = "\\\\$nasIP\\docker"

Write-Host "Mapping network drive..." -ForegroundColor Yellow
net use $drive $uncPath /user:$username /persistent:no

if ($LASTEXITCODE -eq 0) {{
    Write-Host "✅ Network drive mapped: $drive" -ForegroundColor Green

    # Create directory on NAS
    $targetDir = "$drive\\homelab-ide-notification-handler"
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    # Copy files
    Write-Host "Copying files..." -ForegroundColor Yellow
    Copy-Item -Path "$localPath\\*" -Destination $targetDir -Recurse -Force

    Write-Host "✅ Files copied to NAS" -ForegroundColor Green
    Write-Host "   Location: $nasPath" -ForegroundColor Cyan

    # Unmap drive
    net use $drive /delete
}} else {{
    Write-Host "❌ Failed to map network drive" -ForegroundColor Red
    Write-Host "   Manual copy required:" -ForegroundColor Yellow
    Write-Host "   Local: $localPath" -ForegroundColor Cyan
    Write-Host "   NAS: $nasPath" -ForegroundColor Cyan
}}
"""

        ps_file = self.project_root / "scripts" / "python" / "copy_ide_notification_handler_to_nas.ps1"
        try:
            ps_file.write_text(ps_script, encoding='utf-8')
            self.logger.info(f"✅ Created copy script: {ps_file}")
            return {
                "success": True,
                "script_path": str(ps_file),
                "note": "Run this script to copy files to NAS"
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to create copy script: {e}")
            return {"success": False, "error": str(e)}

    def create_deployment_instructions(self) -> Dict[str, Any]:
        """Create deployment instructions for Container Manager"""
        self.logger.info("Creating deployment instructions...")

        credentials = self.get_nas_credentials()
        username = credentials.get("username") if credentials else "your_username"

        instructions = f"""
# @homelab IDE Notification Handler - NAS Container Manager Deployment
# USS Lumina - @scotty (Windows Systems Architect)

## Prerequisites
- NAS Container Manager installed and running
- Access to NAS via DSM web interface or RDP
- Docker files copied to NAS

## Deployment Steps

### Step 1: Copy Files to NAS
Run the PowerShell script:
```powershell
. scripts\\python\\copy_ide_notification_handler_to_nas.ps1
```

Or manually copy:
- Local: {self.docker_dir}
- NAS: {self.nas_docker_path}

### Step 2: Deploy via Container Manager GUI

1. **Open DSM Web Interface**
   - Navigate to: http://{self.nas_ip}:{self.nas_port}
   - Login with: {username}

2. **Open Container Manager**
   - Go to: Package Center → Container Manager
   - Or: Main Menu → Container Manager

3. **Create Project from Compose File**
   - Click: Project → Create
   - Select: "From Compose File"
   - Navigate to: {self.nas_docker_path}/docker-compose.yml
   - Click: Create and Start

### Step 3: Verify Deployment

Check container status:
```bash
ssh {username}@{self.nas_ip}
docker ps | grep homelab-ide-notification-handler
```

View logs:
```bash
docker logs homelab-ide-notification-handler
```

## Container Details

- **Name**: homelab-ide-notification-handler
- **Image**: homelab-ide-notification-handler:latest
- **Restart Policy**: unless-stopped
- **Network**: host
- **Resources**: 0.5 CPU, 512MB RAM

## Monitoring

The container will:
- Monitor for IDE notifications every 5 seconds
- Handle large file dialogs automatically
- Handle Git notifications
- Handle performance warnings
- Log all actions to: {self.nas_docker_path}/logs

## Troubleshooting

If container fails to start:
1. Check logs: `docker logs homelab-ide-notification-handler`
2. Verify files are on NAS: `ls -la {self.nas_docker_path}`
3. Check network connectivity
4. Verify X11 socket access (if GUI needed)

## Notes

- IDE notifications are detected on the local machine running the IDE
- The handler monitors for dialogs and handles them automatically
- For remote monitoring, consider using RDP or VNC to access the IDE machine
"""

        instructions_path = self.project_root / "docker" / "homelab-ide-notification-handler" / "DEPLOYMENT.md"
        try:
            instructions_path.write_text(instructions, encoding='utf-8')
            self.logger.info(f"✅ Deployment instructions created: {instructions_path}")
            return {"success": True, "path": str(instructions_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create instructions: {e}")
            return {"success": False, "error": str(e)}

    def deploy(self) -> Dict[str, Any]:
        """Complete deployment process"""
        self.logger.info("=" * 70)
        self.logger.info("DEPLOY @homelab IDE NOTIFICATION HANDLER TO NAS")
        self.logger.info("USS Lumina - @scotty (Windows Systems Architect)")
        self.logger.info("=" * 70)
        self.logger.info("")

        results = {
            "success": True,
            "steps_completed": [],
            "errors": []
        }

        # Step 1: Create Dockerfile
        self.logger.info("STEP 1: Creating Dockerfile...")
        dockerfile_result = self.create_dockerfile()
        if dockerfile_result.get("success"):
            results["steps_completed"].append("dockerfile_created")
        else:
            results["errors"].append(f"Dockerfile: {dockerfile_result.get('error')}")
            results["success"] = False

        # Step 2: Create requirements.txt
        self.logger.info("")
        self.logger.info("STEP 2: Creating requirements.txt...")
        requirements_result = self.create_requirements_txt()
        if requirements_result.get("success"):
            results["steps_completed"].append("requirements_created")
        else:
            results["errors"].append(f"Requirements: {requirements_result.get('error')}")

        # Step 3: Create docker-compose.yml
        self.logger.info("")
        self.logger.info("STEP 3: Creating docker-compose.yml...")
        compose_result = self.create_docker_compose()
        if compose_result.get("success"):
            results["steps_completed"].append("compose_created")
        else:
            results["errors"].append(f"Compose: {compose_result.get('error')}")
            results["success"] = False

        # Step 4: Create copy script
        self.logger.info("")
        self.logger.info("STEP 4: Creating NAS copy script...")
        copy_result = self.copy_files_to_nas()
        if copy_result.get("success"):
            results["steps_completed"].append("copy_script_created")
        else:
            results["errors"].append(f"Copy script: {copy_result.get('error')}")

        # Step 5: Create deployment instructions
        self.logger.info("")
        self.logger.info("STEP 5: Creating deployment instructions...")
        instructions_result = self.create_deployment_instructions()
        if instructions_result.get("success"):
            results["steps_completed"].append("instructions_created")
        else:
            results["errors"].append(f"Instructions: {instructions_result.get('error')}")

        # Summary
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("DEPLOYMENT SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info("")
        self.logger.info("✅ Steps Completed:")
        for step in results["steps_completed"]:
            self.logger.info(f"   • {step}")
        self.logger.info("")
        if results["errors"]:
            self.logger.info("⚠️  Errors:")
            for error in results["errors"]:
                self.logger.info(f"   • {error}")
        self.logger.info("")
        self.logger.info("📋 Next Steps:")
        self.logger.info("   1. Run: . scripts\\python\\copy_ide_notification_handler_to_nas.ps1")
        self.logger.info("   2. Open Container Manager on NAS")
        self.logger.info(f"   3. Create project from: {self.nas_docker_path}/docker-compose.yml")
        self.logger.info("")
        self.logger.info("=" * 70)

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy IDE Notification Handler to NAS Container Manager")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")

    args = parser.parse_args()

    deployer = HomelabIDENotificationHandlerDeployer(project_root, nas_ip=args.nas_ip)
    result = deployer.deploy()

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())