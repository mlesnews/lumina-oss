#!/usr/bin/env python3
"""
Fix Router via Volume Mount
Since container mounts ../../:/app, copy file to project directory on NAS

Tags: #FIX #ROUTER #VOLUME #NAS @JARVIS @LUMINA @DOIT
"""
import sys
import paramiko
import os
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("FixRouterVolume")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixRouterVolume")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔧 FIX ROUTER VIA VOLUME MOUNT")
logger.info("=" * 70)
logger.info("")

# The container mounts ../../:/app, so we need to find where the project is on NAS
# Typically this would be /volume1/docker/iron-legion-router/../../ which is the project root

dynamic_router_path = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
if not dynamic_router_path.exists():
    logger.error("❌ iron_legion_dynamic_router.py not found locally")
    sys.exit(1)

logger.info("✅ Found iron_legion_dynamic_router.py locally")

# Connect
logger.info("🔌 Connecting to KAIJU_NO_8...")
try:
    private_key = paramiko.RSAKey.from_private_key_file(str(ssh_key_path))
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=kaiju_ip,
        port=ssh_port,
        username=ssh_user,
        pkey=private_key,
        timeout=10
    )
    sftp = ssh_client.open_sftp()
    logger.info("✅ Connected")
except Exception as e:
    logger.error(f"❌ Connection failed: {e}")
    sys.exit(1)

# Find project directory on NAS (where docker-compose is)
logger.info("")
logger.info("🔍 Finding project directory on NAS...")
compose_dir = "/volume1/docker/iron-legion-router"
# The volume mount is ../../:/app, so project root is ../../ from compose_dir
# That would be /volume1/docker/../.. which is /volume1
# But more likely it's mounted from a specific project directory

# Try to find the actual project location
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'cd {compose_dir} && readlink -f ../../ || realpath ../../ || pwd'",
        timeout=5
    )
    project_root_nas = stdout.read().decode().strip() or "/volume1/docker"
    logger.info(f"   Project root on NAS: {project_root_nas}")
except:
    project_root_nas = "/volume1/docker"

# Copy file to project's scripts/python directory on NAS
target_dir = f"{project_root_nas}/scripts/python"
target_file = f"{target_dir}/iron_legion_dynamic_router.py"

logger.info("")
logger.info(f"📤 Copying file to {target_file}...")
try:
    # Create directory
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'mkdir -p {target_dir}'", timeout=5)
    stdout.channel.recv_exit_status()

    # Copy file
    sftp.put(str(dynamic_router_path), target_file)
    logger.info(f"✅ File copied to {target_file}")

    # Also copy to /app/scripts/python in case that's where it's expected
    app_scripts_dir = "/volume1/docker/iron-legion-router/app/scripts/python"
    app_target_file = f"{app_scripts_dir}/iron_legion_dynamic_router.py"
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'mkdir -p {app_scripts_dir}'", timeout=5)
    sftp.put(str(dynamic_router_path), app_target_file)
    logger.info(f"✅ Also copied to {app_target_file}")

except Exception as e:
    logger.error(f"❌ Copy failed: {e}")

sftp.close()

# Restart container to pick up the file
logger.info("")
logger.info("🔄 Restarting container to pick up file...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker restart iron-legion-router'",
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logger.info("✅ Container restarted")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Restart warning: {error}")
except Exception as e:
    logger.error(f"❌ Restart error: {e}")

ssh_client.close()

logger.info("")
logger.info("⏳ Waiting 20 seconds for container to start...")
import time
time.sleep(20)

# Check status
logger.info("")
logger.info("🔍 Checking container status...")
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=kaiju_ip,
        port=ssh_port,
        username=ssh_user,
        pkey=private_key,
        timeout=10
    )

    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker ps --filter name=iron-legion-router --format \"{{.Names}}\\t{{.Status}}\"'",
        timeout=10
    )
    status = stdout.read().decode().strip()
    logger.info(f"Container status: {status}")

    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker logs iron-legion-router --tail 20 2>&1'",
        timeout=10
    )
    logs = stdout.read().decode().strip()
    if logs:
        logger.info("")
        logger.info("Recent logs:")
        logger.info(logs)

        if "ModuleNotFoundError" in logs and "iron_legion_dynamic_router" in logs:
            logger.error("❌ Import error still present")
            logger.info("")
            logger.info("💡 The file may need to be in a different location.")
            logger.info("   Checking where the container expects it...")

            # Check what files exist in /app
            stdin, stdout, stderr = ssh_client.exec_command(
                "bash -c 'docker exec iron-legion-router ls -la /app/scripts/python/ 2>&1 || echo NOT_FOUND'",
                timeout=10
            )
            files = stdout.read().decode().strip()
            logger.info(f"Files in /app/scripts/python/: {files}")
        elif "ModuleNotFoundError" not in logs:
            logger.info("✅ No import errors in logs!")

    ssh_client.close()
except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

logger.info("")
logger.info("=" * 70)
logger.info("✅ FIX COMPLETE")
logger.info("=" * 70)
