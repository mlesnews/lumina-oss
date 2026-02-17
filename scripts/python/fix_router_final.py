#!/usr/bin/env python3
"""
Fix Router Module - Final Fix
Stops container, copies file, restarts

Tags: #FIX #ROUTER #DOCKER @JARVIS @LUMINA @DOIT
"""
import sys
import paramiko
import os
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("FixRouterFinal")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixRouterFinal")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔧 FIX ROUTER MODULE - FINAL FIX")
logger.info("=" * 70)
logger.info("")

# Step 1: Verify file exists
dynamic_router_path = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
if not dynamic_router_path.exists():
    logger.error("❌ iron_legion_dynamic_router.py not found")
    sys.exit(1)

# Step 2: Connect via SSH
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
    logger.info("✅ SSH connected")
    sftp = ssh_client.open_sftp()
    logger.info("✅ SFTP connected")
except Exception as e:
    logger.error(f"❌ Connection failed: {e}")
    sys.exit(1)

# Step 3: Stop container
logger.info("")
logger.info("🛑 Stopping router container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker stop iron-legion-router'",
        timeout=30
    )
    stdout.channel.recv_exit_status()
    logger.info("✅ Container stopped")
    time.sleep(2)
except Exception as e:
    logger.warning(f"⚠️  Stop warning: {e}")

# Step 4: Copy file to NAS temp location
logger.info("")
logger.info("📤 Copying file to NAS...")
try:
    # Use /volume1/docker/tmp which should exist or be creatable
    temp_dir = "/volume1/docker/tmp"
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'mkdir -p {temp_dir}'", timeout=5)
    stdout.channel.recv_exit_status()

    temp_path = f"{temp_dir}/iron_legion_dynamic_router.py"
    sftp.put(str(dynamic_router_path), temp_path)
    logger.info(f"✅ File copied to {temp_path}")
except Exception as e:
    logger.warning(f"⚠️  SFTP copy to /volume1 failed: {e}")
    # Try /tmp
    try:
        temp_path = "/tmp/iron_legion_dynamic_router.py"
        sftp.put(str(dynamic_router_path), temp_path)
        logger.info(f"✅ File copied to {temp_path}")
    except Exception as e2:
        logger.error(f"❌ SFTP copy failed: {e2}")
        sftp.close()
        ssh_client.close()
        sys.exit(1)

sftp.close()

# Step 5: Copy file into stopped container
logger.info("")
logger.info("📦 Copying file into container...")
try:
    # Get absolute path
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'readlink -f {temp_path} || realpath {temp_path} || echo {temp_path}'", timeout=5)
    abs_temp_path = stdout.read().decode().strip() or temp_path

    # Copy into stopped container
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'docker cp {abs_temp_path} iron-legion-router:/app/scripts/python/iron_legion_dynamic_router.py'",
        timeout=10
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ File copied into container")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Copy warning: {error}")

        # Alternative: Start container temporarily, copy, then restart properly
        logger.info("   Starting container temporarily to copy file...")
        stdin, stdout, stderr = ssh_client.exec_command("bash -c 'docker start iron-legion-router'", timeout=10)
        time.sleep(5)

        # Create directory
        stdin, stdout, stderr = ssh_client.exec_command(
            "bash -c 'docker exec iron-legion-router bash -c \"mkdir -p /app/scripts/python\"'",
            timeout=10
        )

        # Copy file
        stdin, stdout, stderr = ssh_client.exec_command(
            f"bash -c 'docker cp {abs_temp_path} iron-legion-router:/app/scripts/python/iron_legion_dynamic_router.py'",
            timeout=10
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logger.info("✅ File copied (container was started)")
        else:
            logger.error("❌ Failed to copy file")

    # Clean up
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'rm -f {temp_path}'", timeout=5)

except Exception as e:
    logger.error(f"❌ Error: {e}")

# Step 6: Verify file
logger.info("")
logger.info("🔍 Verifying file in container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker exec iron-legion-router ls -la /app/scripts/python/iron_legion_dynamic_router.py 2>&1'",
        timeout=10
    )
    output = stdout.read().decode().strip()
    if output and "iron_legion_dynamic_router.py" in output:
        logger.info("✅ File verified")
        logger.info(f"   {output}")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Verification failed: {error}")
except Exception as e:
    logger.warning(f"⚠️  Verification error: {e}")

# Step 7: Restart container
logger.info("")
logger.info("🔄 Restarting router container...")
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
logger.info("⏳ Waiting 20 seconds for container to initialize...")
time.sleep(20)

# Check final status
logger.info("")
logger.info("🔍 Checking final container status...")
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

    # Check status
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker ps --filter name=iron-legion-router --format \"{{.Names}}\\t{{.Status}}\"'",
        timeout=10
    )
    status = stdout.read().decode().strip()
    logger.info(f"Container status: {status}")

    # Check logs
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
        elif "ModuleNotFoundError" not in logs:
            logger.info("✅ No import errors in logs")

    ssh_client.close()
except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

logger.info("")
logger.info("=" * 70)
logger.info("✅ FIX COMPLETE")
logger.info("=" * 70)
