#!/usr/bin/env python3
"""
Deploy ElevenLabs MCP Server to NAS
Automated deployment script for NAS Container Manager

Tags: #DEPLOYMENT #NAS #ELEVENLABS #AUTOMATION @JARVIS @DOIT
"""

import sys
import os
import subprocess
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

logger = get_logger("DeployElevenLabsToNAS")

PROJECT_ROOT = Path(__file__).parent.parent.parent
NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_USER = "backupadm"
NAS_DOCKER_PATH = "/volume1/docker"


class ElevenLabsNASDeployer:
    """Automated deployment to NAS"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize deployer"""
        if project_root is None:
            project_root = PROJECT_ROOT

        self.project_root = Path(project_root)
        self.nas_host = NAS_HOST
        self.nas_user = NAS_USER
        self.nas_docker_path = NAS_DOCKER_PATH

        logger.info("=" * 80)
        logger.info("🚀 ElevenLabs MCP Server - NAS Deployment")
        logger.info("=" * 80)
        logger.info("")

    def copy_files_to_nas(self) -> Tuple[bool, str]:
        """Copy deployment files to NAS"""
        logger.info("📦 Copying files to NAS...")

        files_to_copy = [
            ("containerization/services/nas-mcp-servers", "nas-mcp-servers"),
            ("containerization/services/elevenlabs-mcp-server", "elevenlabs-mcp-server"),
        ]

        for local_path, remote_name in files_to_copy:
            local_full = self.project_root / local_path
            if not local_full.exists():
                logger.error(f"   ❌ Source not found: {local_path}")
                return False, f"Source not found: {local_path}"

            logger.info(f"   📤 Copying {local_path}...")
            try:
                result = subprocess.run(
                    ["scp", "-r", str(local_full), f"{self.nas_user}@{self.nas_host}:{self.nas_docker_path}/"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    logger.error(f"   ❌ Failed to copy {local_path}: {result.stderr}")
                    return False, result.stderr

                logger.info(f"   ✅ Copied {local_path}")
            except Exception as e:
                logger.error(f"   ❌ Error copying {local_path}: {e}")
                return False, str(e)

        logger.info("   ✅ All files copied")
        return True, "Files copied successfully"

    def deploy_on_nas(self) -> Tuple[bool, str]:
        """Deploy container on NAS"""
        logger.info("")
        logger.info("🐳 Deploying container on NAS...")

        try:
            # SSH and run docker-compose
            deploy_cmd = f"cd {self.nas_docker_path}/nas-mcp-servers && docker-compose up -d --build elevenlabs-mcp-server"

            result = subprocess.run(
                ["ssh", f"{self.nas_user}@{self.nas_host}", deploy_cmd],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"   ❌ Deployment failed: {result.stderr}")
                return False, result.stderr

            logger.info("   ✅ Container deployed")
            logger.info("")
            logger.info("   📋 Deployment output:")
            for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                if line.strip():
                    logger.info(f"      {line}")

            return True, "Deployment successful"
        except Exception as e:
            logger.error(f"   ❌ Deployment error: {e}")
            return False, str(e)

    def verify_deployment(self) -> Tuple[bool, str]:
        """Verify deployment succeeded"""
        logger.info("")
        logger.info("🔍 Verifying deployment...")

        try:
            # Check container status
            result = subprocess.run(
                ["ssh", f"{self.nas_user}@{self.nas_host}", 
                 "docker ps --filter name=elevenlabs-mcp-server --format '{{.Names}} {{.Status}}'"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "elevenlabs-mcp-server" in result.stdout:
                logger.info("   ✅ Container is running")
                logger.info(f"   📊 Status: {result.stdout.strip()}")
                return True, "Container running"
            else:
                logger.warning("   ⚠️  Container not found or not running")
                return False, "Container not running"
        except Exception as e:
            logger.error(f"   ❌ Verification error: {e}")
            return False, str(e)

    def execute_deployment(self) -> int:
        """Execute full deployment workflow"""
        logger.info("")

        # Step 1: Copy files
        success, message = self.copy_files_to_nas()
        if not success:
            logger.error(f"❌ Deployment failed: {message}")
            return 1

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
        logger.info("   1. Check container logs: ssh backupadm@<NAS_PRIMARY_IP> 'docker logs elevenlabs-mcp-server'")
        logger.info("   2. Run battle test: python scripts/python/battletest_elevenlabs_mcp.py --save")
        logger.info("   3. Test MCP connection in Cursor")
        logger.info("")

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy ElevenLabs MCP Server to NAS")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--nas-host', type=str, default=NAS_HOST, help='NAS hostname/IP')
    parser.add_argument('--nas-user', type=str, default=NAS_USER, help='NAS username')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')

    args = parser.parse_args()

    deployer = ElevenLabsNASDeployer(project_root=args.project_root)

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