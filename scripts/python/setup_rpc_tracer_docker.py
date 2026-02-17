#!/usr/bin/env python3
"""
Setup RPC Tracer Logs via Docker Terminal

Creates directory structure on NAS Docker container for Cursor Extension RPC Tracer.

Tags: #CURSOR #RPC_TRACER #LOGS #NAS #DOCKER @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("SetupRPCTracerDocker")


def find_nas_container():
    """Find NAS Docker container (managed by Synology Container Manager)"""
    logger.info("📋 Note: NAS uses Synology Container Manager")
    logger.info("   Containers are managed via NAS web interface, not local Docker CLI")
    logger.info("")

    # Try to find NAS containers via SSH or network access
    # NAS containers are managed separately through Container Manager
    nas_ip = "<NAS_IP>"

    logger.info(f"🔍 Checking NAS at {nas_ip}...")
    logger.info("   NAS containers are managed via Synology Container Manager")
    logger.info("   Access via: http://{}/container-manager".format(nas_ip))
    logger.info("")

    # For NAS, we typically need to:
    # 1. Access via Container Manager web UI, OR
    # 2. SSH into NAS and use docker commands there, OR
    # 3. Create directories directly on NAS file system (not in container)

    return None  # NAS containers managed separately


def create_directory_via_docker(container_name: str, path: str) -> bool:
    """Create directory in Docker container"""
    try:
        # Try common mount points
        mount_points = [
            "/volume1",
            "/data",
            "/shared",
            "/docker",
            "/mnt"
        ]

        for mount in mount_points:
            docker_path = f"{mount}/Jarvis/Logs/RPCTracer"
            cmd = ["docker", "exec", container_name, "mkdir", "-p", docker_path]

            logger.info(f"   Trying: docker exec {container_name} mkdir -p {docker_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"✅ Directory created: {docker_path}")

                # Verify it exists
                verify_cmd = ["docker", "exec", container_name, "test", "-d", docker_path]
                verify_result = subprocess.run(
                    verify_cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if verify_result.returncode == 0:
                    logger.info(f"✅ Verified: {docker_path} exists")
                    return True

        return False
    except Exception as e:
        logger.error(f"❌ Error creating directory: {e}")
        return False


def get_docker_mounts(container_name: str):
    """Get mount points for Docker container"""
    try:
        cmd = ["docker", "inspect", container_name, "--format", "{{json .Mounts}}"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            import json
            mounts = json.loads(result.stdout)
            logger.info("📁 Container mount points:")
            for mount in mounts:
                logger.info(f"   Source: {mount.get('Source', 'N/A')}")
                logger.info(f"   Destination: {mount.get('Destination', 'N/A')}")
                logger.info("")
            return mounts
        return []
    except Exception as e:
        logger.warning(f"⚠️  Could not inspect mounts: {e}")
        return []


def main():
    """Main setup"""
    logger.info("=" * 80)
    logger.info("🐳 SETTING UP RPC TRACER LOGS VIA DOCKER")
    logger.info("=" * 80)
    logger.info("")

    # Step 1: Find NAS container
    logger.info("🔍 Step 1: Finding NAS Docker container...")
    container = find_nas_container()

    # NAS uses Container Manager - provide instructions
    logger.info("📋 NAS Container Manager Instructions:")
    logger.info("")
    logger.info("Since NAS uses Synology Container Manager, use one of these methods:")
    logger.info("")
    logger.info("METHOD 1: Via Container Manager Web UI")
    logger.info("   1. Open: http://<NAS_IP>/container-manager")
    logger.info("   2. Find your container (e.g., ollama, nas services)")
    logger.info("   3. Click container → Terminal")
    logger.info("   4. Run: mkdir -p /volume1/Jarvis/Logs/RPCTracer")
    logger.info("")
    logger.info("METHOD 2: Via SSH (if enabled)")
    logger.info("   1. SSH into NAS: ssh user@<NAS_IP>")
    logger.info("   2. Access container: docker exec -it <container_name> /bin/sh")
    logger.info("   3. Create directory: mkdir -p /volume1/Jarvis/Logs/RPCTracer")
    logger.info("")
    logger.info("METHOD 3: Direct NAS File System (Recommended)")
    logger.info("   1. Access NAS via File Explorer: \\\\<NAS_IP>\\")
    logger.info("   2. Navigate to shared folder")
    logger.info("   3. Create: Jarvis\\Logs\\RPCTracer")
    logger.info("   4. This is accessible to containers via mounted volumes")
    logger.info("")
    logger.info("METHOD 4: Via NAS Web Interface (File Station)")
    logger.info("   1. Open: http://<NAS_IP>:5000 (DSM)")
    logger.info("   2. Open File Station")
    logger.info("   3. Navigate to shared folder")
    logger.info("   4. Create: Jarvis/Logs/RPCTracer")
    logger.info("")
    return

    logger.info(f"✅ Found container: {container}")
    logger.info("")

    # Step 2: Inspect mounts
    logger.info("📁 Step 2: Inspecting container mount points...")
    mounts = get_docker_mounts(container)
    logger.info("")

    # Step 3: Create directory
    logger.info("📁 Step 3: Creating directory structure...")
    if create_directory_via_docker(container, "Jarvis/Logs/RPCTracer"):
        logger.info("   ✅ Directory structure created")
    else:
        logger.warning("   ⚠️  Directory creation may have failed")
        logger.info("")
        logger.info("📋 Manual Commands to Try:")
        logger.info("")
        logger.info(f"   docker exec {container} mkdir -p /volume1/Jarvis/Logs/RPCTracer")
        logger.info(f"   docker exec {container} mkdir -p /data/Jarvis/Logs/RPCTracer")
        logger.info(f"   docker exec {container} mkdir -p /shared/Jarvis/Logs/RPCTracer")
    logger.info("")

    # Step 4: Instructions
    logger.info("=" * 80)
    logger.info("📝 NEXT STEPS")
    logger.info("=" * 80)
    logger.info("")
    logger.info("1. Open Cursor Settings → Beta")
    logger.info("2. Find 'Extension RPC Tracer'")
    logger.info("3. Ensure it's enabled (green toggle)")
    logger.info("4. In 'Optional folder for RPC logs', enter:")
    logger.info("")
    logger.info("   \\\\<NAS_IP>\\Jarvis\\Logs\\RPCTracer")
    logger.info("")
    logger.info("5. Restart Cursor IDE (required for changes to take effect)")
    logger.info("")


if __name__ == "__main__":

    main()