#!/usr/bin/env python3
"""
Setup RPC Tracer Logs Directory

Creates directory structure on NAS and maps L drive for Cursor Extension RPC Tracer.

Tags: #CURSOR #RPC_TRACER #LOGS #NAS @JARVIS @LUMINA
"""

import sys
import os
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupRPCTracerLogs")


def create_nas_directory_via_docker(nas_path: str, container_name: str = None) -> bool:
    """Create directory on NAS via Docker container"""
    try:
        # If NAS is in Docker, we need to use Docker exec
        # First, try to find the container or use provided name
        if container_name:
            containers = [container_name]
        else:
            # Try common NAS container names
            containers = ["synology", "nas", "ollama", "ollama-online"]

        # Try each container
        for container in containers:
            try:
                # Check if container exists and is running
                check_cmd = f'docker ps --filter "name={container}" --format "{{{{.Names}}}}"'
                result = subprocess.run(
                    ["powershell", "-Command", check_cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if container in result.stdout:
                    # Container found - create directory via Docker exec
                    # Extract path relative to container (usually /data or mounted volume)
                    # For Synology, logs are often in /volume1 or mounted volumes
                    docker_path = nas_path.replace("\\", "/").replace("\\\\<NAS_IP>", "/data")
                    if not docker_path.startswith("/"):
                        docker_path = f"/data/{docker_path.lstrip('/')}"

                    mkdir_cmd = f'docker exec {container} mkdir -p "{docker_path}"'
                    result = subprocess.run(
                        ["powershell", "-Command", mkdir_cmd],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.returncode == 0:
                        logger.info(f"✅ Directory created via Docker container '{container}': {docker_path}")
                        return True
            except Exception as e:
                logger.debug(f"   Container '{container}' not found or error: {e}")
                continue

        # Fallback: Try direct network path (if not Docker)
        logger.info("   Trying direct network path (non-Docker)...")
        cmd = f'New-Item -ItemType Directory -Path "{nas_path}" -Force'
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 or "already exists" in result.stderr.lower():
            logger.info(f"✅ Directory created/verified: {nas_path}")
            return True
        else:
            logger.warning(f"⚠️  Could not create via Docker or network path")
            logger.info(f"   You may need to create manually via Docker terminal")
            return False

    except Exception as e:
        logger.error(f"❌ Error creating directory: {e}")
        return False


def map_l_drive(nas_logs_path: str) -> bool:
    """Map L drive to NAS logs directory"""
    try:
        # Check if L drive already exists
        if os.path.exists("L:\\"):
            logger.info("✅ L drive already mapped")
            return True

        # Map L drive using PowerShell
        cmd = f'New-PSDrive -Name "L" -PSProvider FileSystem -Root "{nas_logs_path}" -Persist'
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.info(f"✅ L drive mapped to: {nas_logs_path}")
            return True
        else:
            logger.warning(f"⚠️  L drive mapping may have failed: {result.stderr}")
            logger.info("   You can map manually or use network path directly")
            return False
    except Exception as e:
        logger.error(f"❌ Error mapping L drive: {e}")
        return False


def verify_setup() -> bool:
    try:
        """Verify setup is complete"""
        logger.info("🔍 Verifying setup...")

        # Check L drive
        l_drive_exists = os.path.exists("L:\\")
        rpc_tracer_path = Path("L:\\Jarvis\\Logs\\RPCTracer")
        rpc_tracer_exists = rpc_tracer_path.exists()

        logger.info(f"   L drive exists: {l_drive_exists}")
        logger.info(f"   RPC Tracer directory exists: {rpc_tracer_exists}")

        if l_drive_exists and rpc_tracer_exists:
            logger.info("✅ Setup complete!")
            return True
        elif not l_drive_exists:
            logger.warning("⚠️  L drive not mapped - use network path in Cursor settings")
            logger.info("   Path: \\\\<NAS_IP>\\Jarvis\\Logs\\RPCTracer")
            return False
        else:
            logger.warning("⚠️  RPC Tracer directory not found")
            return False


    except Exception as e:
        logger.error(f"Error in verify_setup: {e}", exc_info=True)
        raise
def main():
    """Main setup"""
    logger.info("=" * 80)
    logger.info("🚀 SETTING UP RPC TRACER LOGS")
    logger.info("=" * 80)
    logger.info("")

    # NAS configuration
    nas_ip = "<NAS_IP>"
    nas_logs_base = f"\\\\{nas_ip}\\Jarvis\\Logs"
    nas_rpc_tracer = f"{nas_logs_base}\\RPCTracer"

    logger.info("📋 Configuration:")
    logger.info(f"   NAS IP: {nas_ip}")
    logger.info(f"   Logs Base: {nas_logs_base}")
    logger.info(f"   RPC Tracer: {nas_rpc_tracer}")
    logger.info("")

    # Step 1: Create directory structure (via Docker if needed)
    logger.info("📁 Step 1: Creating directory structure on NAS...")
    logger.info("   Attempting via Docker container first...")
    if create_nas_directory_via_docker(nas_rpc_tracer):
        logger.info("   ✅ Directory structure created")
    else:
        logger.warning("   ⚠️  Directory creation may have failed")
        logger.info("   You may need to create manually via Docker terminal")
        logger.info("")
        logger.info("   Docker commands to try:")
        logger.info(f"   docker exec <container_name> mkdir -p /data/Jarvis/Logs/RPCTracer")
        logger.info(f"   # Or if mounted volume:")
        logger.info(f"   docker exec <container_name> mkdir -p /volume1/Jarvis/Logs/RPCTracer")
    logger.info("")

    # Step 2: Map L drive
    logger.info("🔗 Step 2: Mapping L drive...")
    if map_l_drive(nas_logs_base):
        logger.info("   ✅ L drive mapped")
    else:
        logger.warning("   ⚠️  L drive mapping may have failed")
        logger.info("   You can use network path directly in Cursor settings")
    logger.info("")

    # Step 3: Verify
    logger.info("✅ Step 3: Verifying setup...")
    verify_setup()
    logger.info("")

    # Instructions
    logger.info("=" * 80)
    logger.info("📝 NEXT STEPS")
    logger.info("=" * 80)
    logger.info("")
    logger.info("1. Open Cursor Settings → Beta")
    logger.info("2. Find 'Extension RPC Tracer'")
    logger.info("3. Ensure it's enabled (green toggle)")
    logger.info("4. In 'Optional folder for RPC logs', enter:")
    logger.info("")
    if os.path.exists("L:\\"):
        logger.info("   L:\\Jarvis\\Logs\\RPCTracer")
    else:
        logger.info("   \\\\<NAS_IP>\\Jarvis\\Logs\\RPCTracer")
    logger.info("")
    logger.info("5. Restart Cursor IDE (required for changes to take effect)")
    logger.info("")


if __name__ == "__main__":

    main()