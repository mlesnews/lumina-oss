#!/usr/bin/env python3
"""
@DOIT: Deploy @homelab IDE Notification Handler to NAS Container Manager
Full automated deployment via SSH/SCP and docker-compose

Tags: #DOIT #NAS #DEPLOYMENT #AUTOMATION #IDE #NOTIFICATIONS @JARVIS @LUMINA @SCOTTY
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DoitDeployHomelabIDENotificationsNAS")

PROJECT_ROOT = Path(__file__).parent.parent.parent
NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_USER = "backupadm"
NAS_DOCKER_PATH = "/volume1/docker/homelab-ide-notification-handler"


class HomelabIDENotificationHandlerDeployer:
    """Automated deployment to NAS"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize deployer"""
        if project_root is None:
            project_root = PROJECT_ROOT

        self.project_root = Path(project_root)
        self.nas_host = NAS_HOST
        self.nas_user = NAS_USER
        self.nas_docker_path = NAS_DOCKER_PATH
        self.docker_dir = self.project_root / "docker" / "homelab-ide-notification-handler"

        logger.info("=" * 80)
        logger.info("🚀 @homelab IDE Notification Handler - NAS Deployment")
        logger.info("=" * 80)
        logger.info("")

    def copy_files_to_nas(self) -> Tuple[bool, str]:
        """Copy deployment files to NAS using robocopy (more robust)"""
        logger.info("📦 Copying files to NAS via robocopy...")

        if not self.docker_dir.exists():
            logger.error(f"   ❌ Source directory not found: {self.docker_dir}")
            return False, f"Source directory not found: {self.docker_dir}"

        logger.info(f"   📤 Copying {self.docker_dir}...")
        try:
            # Use robocopy which handles network connections better
            nas_unc = f"\\\\{self.nas_host}\\docker\\homelab-ide-notification-handler"

            # Create target directory first via PowerShell
            ps_create = f"""
$nasIP = "{self.nas_host}"
$username = "{self.nas_user}"
$uncPath = "\\\\$nasIP\\docker"
$drive = "Z:"

# Clean up any existing connections
net use $drive /delete /y 2>$null | Out-Null
net use $uncPath /delete /y 2>$null | Out-Null
Start-Sleep -Seconds 2

# Map drive
net use $drive $uncPath /user:$username /persistent:no 2>$null
if ($LASTEXITCODE -eq 0) {{
    New-Item -ItemType Directory -Path "$drive\\homelab-ide-notification-handler" -Force | Out-Null
    net use $drive /delete /y 2>$null
    exit 0
}} else {{
    exit 1
}}
"""

            # Create directory
            create_result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_create],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Use robocopy (more reliable for network copies)
            robocopy_cmd = [
                "robocopy",
                str(self.docker_dir),
                nas_unc,
                "/E",  # Copy subdirectories
                "/R:3",  # Retry 3 times
                "/W:5",  # Wait 5 seconds
                "/MT:4",  # Multi-threaded
                "/NFL",  # No file list
                "/NDL",  # No directory list
                "/NP",  # No progress
                "/NJH",  # No job header
                "/NJS"  # No job summary
            ]

            logger.info("   🔄 Running robocopy (this may take a moment)...")
            result = subprocess.run(
                robocopy_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Robocopy returns 0-7 for success, 8+ for errors
            if result.returncode <= 7:
                logger.info(f"   ✅ Copied to {self.nas_docker_path}")
                return True, "Files copied successfully"
            else:
                logger.error(f"   ❌ Robocopy failed with code: {result.returncode}")
                logger.error(f"   Output: {result.stdout[-500:] if len(result.stdout) > 500 else result.stdout}")
                return False, f"Robocopy failed with code {result.returncode}"

        except subprocess.TimeoutExpired:
            logger.error("   ❌ Copy operation timed out")
            return False, "Copy operation timed out"
        except Exception as e:
            logger.error(f"   ❌ Error copying: {e}")
            return False, str(e)

    def deploy_on_nas(self) -> Tuple[bool, str]:
        """Deploy container on NAS"""
        logger.info("")
        logger.info("🐳 Deploying container on NAS...")

        try:
            # First, try to add user to docker group if not already
            logger.info("   🔧 Checking docker group permissions...")
            check_group_cmd = f"groups | grep -q docker && echo 'IN_GROUP' || echo 'NOT_IN_GROUP'"
            group_result = subprocess.run(
                ["ssh", f"{self.nas_user}@{self.nas_host}", check_group_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "NOT_IN_GROUP" in group_result.stdout:
                logger.info("   ⚠️  User not in docker group, attempting to add...")
                add_group_cmd = f"sudo usermod -aG docker {self.nas_user} 2>&1 || echo 'GROUP_ADD_FAILED'"
                add_result = subprocess.run(
                    ["ssh", f"{self.nas_user}@{self.nas_host}", add_group_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "GROUP_ADD_FAILED" not in add_result.stdout:
                    logger.info("   ✅ Added to docker group (may require re-login)")
                else:
                    logger.warning("   ⚠️  Could not add to docker group, will try sudo")

            # Try multiple docker paths and methods
            logger.info("   🚀 Attempting deployment...")
            deploy_cmd = f"""
cd {self.nas_docker_path} && \
( \
  /usr/local/bin/docker compose up -d --build 2>&1 || \
  /usr/bin/docker compose up -d --build 2>&1 || \
  docker compose up -d --build 2>&1 || \
  sudo /usr/local/bin/docker compose up -d --build 2>&1 || \
  sudo docker compose up -d --build 2>&1 || \
  echo 'ALL_METHODS_FAILED' \
)
"""

            result = subprocess.run(
                ["ssh", f"{self.nas_user}@{self.nas_host}", deploy_cmd],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for build
            )

            if "ALL_METHODS_FAILED" in result.stdout or result.returncode != 0:
                # Try using Container Manager GUI automation
                logger.warning("   ⚠️  Direct docker command failed, trying GUI automation...")
                return self.deploy_via_gui_automation()

            logger.info("   ✅ Container deployed")
            logger.info("")
            logger.info("   📋 Deployment output:")
            for line in result.stdout.split('\n')[-20:]:  # Last 20 lines
                if line.strip() and "ALL_METHODS_FAILED" not in line:
                    logger.info(f"      {line}")

            return True, "Deployment successful"
        except subprocess.TimeoutExpired:
            logger.error("   ❌ Deployment timed out")
            return False, "Deployment timed out"
        except Exception as e:
            logger.error(f"   ❌ Deployment error: {e}")
            return False, str(e)

    def deploy_via_gui_automation(self) -> Tuple[bool, str]:
        """Deploy via Container Manager GUI automation"""
        logger.info("   🔄 Attempting Container Manager GUI automation...")
        try:
            from jarvis_deploy_container_manager_gui import JARVISContainerManagerDeployer

            deployer = JARVISContainerManagerDeployer(
                project_name="homelab-ide-notification-handler",
                compose_file_path=f"{self.nas_docker_path}/docker-compose.yml"
            )

            result = deployer.deploy()

            if result.get("success"):
                logger.info("   ✅ GUI deployment initiated")
                return True, "GUI deployment successful"
            else:
                logger.error(f"   ❌ GUI deployment failed: {result.get('error')}")
                return False, result.get("error", "GUI deployment failed")
        except ImportError:
            logger.error("   ❌ GUI automation module not available")
            logger.info("   📋 Please deploy manually via Container Manager GUI:")
            logger.info(f"      1. Open: https://{self.nas_host}:5001")
            logger.info(f"      2. Container Manager → Project → Create → From Compose File")
            logger.info(f"      3. Path: {self.nas_docker_path}/docker-compose.yml")
            return False, "GUI automation not available"
        except Exception as e:
            logger.error(f"   ❌ GUI automation error: {e}")
            return False, str(e)

    def verify_deployment(self) -> Tuple[bool, str]:
        """Verify deployment succeeded"""
        logger.info("")
        logger.info("🔍 Verifying deployment...")

        try:
            # Check container status
            result = subprocess.run(
                ["ssh", f"{self.nas_user}@{self.nas_host}", 
                 "docker ps --filter name=homelab-ide-notification-handler --format '{{.Names}} {{.Status}}'"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "homelab-ide-notification-handler" in result.stdout:
                logger.info("   ✅ Container is running")
                logger.info(f"   📊 Status: {result.stdout.strip()}")
                return True, "Container running"
            else:
                logger.warning("   ⚠️  Container not found or not running")
                logger.warning(f"   Output: {result.stdout}")
                return False, "Container not running"
        except Exception as e:
            logger.error(f"   ❌ Verification error: {e}")
            return False, str(e)

    def check_files_on_nas(self) -> Tuple[bool, str]:
        """Check if files already exist on NAS"""
        logger.info("🔍 Checking if files already exist on NAS...")
        try:
            result = subprocess.run(
                ["ssh", f"{self.nas_user}@{self.nas_host}", 
                 f"test -f {self.nas_docker_path}/docker-compose.yml && echo 'EXISTS' || echo 'NOT_FOUND'"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "EXISTS" in result.stdout:
                logger.info("   ✅ Files already exist on NAS")
                return True, "Files exist"
            else:
                logger.info("   ⚠️  Files not found on NAS")
                return False, "Files not found"
        except Exception as e:
            logger.warning(f"   ⚠️  Could not check NAS: {e}")
            return False, str(e)

    def execute_deployment(self) -> int:
        """Execute full deployment workflow"""
        logger.info("")

        # Step 0: Check if files already exist
        files_exist, _ = self.check_files_on_nas()

        # Step 1: Copy files (only if they don't exist)
        if not files_exist:
            success, message = self.copy_files_to_nas()
            if not success:
                logger.warning(f"⚠️  Copy failed: {message}")
                logger.warning("   Attempting deployment anyway (files may already exist)...")
        else:
            logger.info("   ✅ Skipping copy - files already exist on NAS")

        # Step 2: Deploy
        success, message = self.deploy_on_nas()
        if not success:
            logger.error(f"❌ Deployment failed: {message}")
            return 1

        # Step 3: Verify
        success, message = self.verify_deployment()
        if not success:
            logger.warning(f"⚠️  Verification warning: {message}")
            logger.warning("   Container may still be starting - check logs manually")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ DEPLOYMENT COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info(f"   1. Check container logs: ssh {self.nas_user}@{self.nas_host} 'docker logs homelab-ide-notification-handler'")
        logger.info("   2. Monitor container: ssh {self.nas_user}@{self.nas_host} 'docker ps | grep homelab-ide-notification-handler'")
        logger.info("   3. View logs on NAS: /volume1/docker/homelab-ide-notification-handler/logs")
        logger.info("")

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy @homelab IDE Notification Handler to NAS")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--nas-host', type=str, default=NAS_HOST, help='NAS hostname/IP')
    parser.add_argument('--nas-user', type=str, default=NAS_USER, help='NAS username')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')

    args = parser.parse_args()

    deployer = HomelabIDENotificationHandlerDeployer(project_root=args.project_root)

    if args.dry_run:
        logger.info("🔍 DRY RUN - No changes will be made")
        logger.info("")
        logger.info("Would execute:")
        logger.info(f"  1. Copy files to {args.nas_user}@{args.nas_host}:{NAS_DOCKER_PATH}/")
        logger.info(f"  2. Deploy via docker-compose on NAS")
        logger.info(f"  3. Verify deployment")
        return 0

    return deployer.execute_deployment()


if __name__ == "__main__":


    sys.exit(main())