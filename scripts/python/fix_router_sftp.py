#!/usr/bin/env python3
"""
Fix Router Module - SFTP Copy
Uses SFTP to copy iron_legion_dynamic_router.py to container

Tags: #FIX #ROUTER #SFTP #DOCKER @JARVIS @LUMINA @DOIT
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
    logger = get_logger("FixRouterSFTP")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixRouterSFTP")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔧 FIX ROUTER MODULE - SFTP COPY")
logger.info("=" * 70)
logger.info("")

# Step 1: Verify file exists locally
dynamic_router_path = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
if not dynamic_router_path.exists():
    logger.error("❌ iron_legion_dynamic_router.py not found locally")
    sys.exit(1)

logger.info("✅ Found iron_legion_dynamic_router.py locally")

# Step 2: Connect via SSH and SFTP
logger.info("🔌 Connecting to KAIJU_NO_8 via SSH/SFTP...")
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
    logger.info("✅ SSH connection established")

    # Open SFTP connection
    sftp = ssh_client.open_sftp()
    logger.info("✅ SFTP connection established")
except Exception as e:
    logger.error(f"❌ Connection failed: {e}")
    sys.exit(1)

# Step 3: Copy file to temporary location on NAS
logger.info("📤 Copying file to NAS temporary location...")
try:
    # Get home directory
    stdin, stdout, stderr = ssh_client.exec_command("echo $HOME", timeout=5)
    home_dir = stdout.read().decode().strip() or "/home/mlesn"

    # Create temp directory in home
    temp_dir = f"{home_dir}/.tmp"
    stdin, stdout, stderr = ssh_client.exec_command(f"mkdir -p {temp_dir}", timeout=5)
    stdout.channel.recv_exit_status()

    temp_path = f"{temp_dir}/iron_legion_dynamic_router.py"
    sftp.put(str(dynamic_router_path), temp_path)
    logger.info(f"✅ File copied to {temp_path}")
except Exception as e:
    logger.warning(f"⚠️  SFTP copy to home failed: {e}")
    # Try /volume1/docker/tmp
    try:
        temp_path = "/volume1/docker/tmp/iron_legion_dynamic_router.py"
        # Create directory if needed
        stdin, stdout, stderr = ssh_client.exec_command("bash -c 'mkdir -p /volume1/docker/tmp'", timeout=5)
        stdout.channel.recv_exit_status()
        sftp.put(str(dynamic_router_path), temp_path)
        logger.info(f"✅ File copied to {temp_path}")
    except Exception as e2:
        logger.error(f"❌ SFTP copy failed: {e2}")
        sftp.close()
        ssh_client.close()
        sys.exit(1)

sftp.close()

# Step 4: Copy file from temp to container
logger.info("📦 Copying file into container...")
try:
    # Wait for container to be running (not restarting)
    logger.info("   Waiting for container to be ready...")
    import time
    for i in range(10):
        stdin, stdout, stderr = ssh_client.exec_command(
            "docker ps --filter name=iron-legion-router --format '{{.Status}}'",
            timeout=5
        )
        status = stdout.read().decode().strip()
        if "Up" in status and "Restarting" not in status:
            break
        time.sleep(2)

    # Create directory in container (use bash explicitly)
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker exec iron-legion-router bash -c \"mkdir -p /app/scripts/python\"'",
        timeout=10
    )
    stdout.channel.recv_exit_status()
    logger.info("   ✅ Directory created in container")

    # Copy file into container using docker cp
    # Get absolute path on NAS
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'readlink -f {temp_path} || realpath {temp_path} || echo {temp_path}'", timeout=5)
    abs_temp_path = stdout.read().decode().strip() or temp_path

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

        # Alternative: Use cat to pipe into container
        logger.info("   Trying alternative method (piping content)...")
        with open(dynamic_router_path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Use Python in container to write file
        python_cmd = f"python3 -c \"import sys; f=open('/app/scripts/python/iron_legion_dynamic_router.py', 'w'); f.write({repr(file_content)}); f.close()\""
        stdin, stdout, stderr = ssh_client.exec_command(
            f"bash -c 'docker exec iron-legion-router {python_cmd}'",
            timeout=10
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logger.info("✅ File copied using Python method")
        else:
            error = stderr.read().decode()
            logger.error(f"❌ Failed to copy file: {error}")

    # Clean up temp file
    stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'rm -f {temp_path}'", timeout=5)

except Exception as e:
    logger.error(f"❌ Error copying to container: {e}")

# Step 5: Verify file exists in container
logger.info("")
logger.info("🔍 Verifying file in container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker exec iron-legion-router ls -la /app/scripts/python/iron_legion_dynamic_router.py",
        timeout=10
    )
    output = stdout.read().decode().strip()
    if output and "iron_legion_dynamic_router.py" in output:
        logger.info("✅ File verified in container")
        logger.info(f"   {output}")
    else:
        logger.warning("⚠️  File verification failed")
        error = stderr.read().decode()
        if error:
            logger.warning(f"   Error: {error}")
except Exception as e:
    logger.warning(f"⚠️  Verification error: {e}")

# Step 6: Restart container
logger.info("")
logger.info("🔄 Restarting router container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker restart iron-legion-router",
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logger.info("✅ Router container restarted")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Restart warning: {error}")
except Exception as e:
    logger.error(f"❌ Error restarting container: {e}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ FIX COMPLETE")
logger.info("=" * 70)
logger.info("")
logger.info("⏳ Waiting 15 seconds for container to start...")
import time
time.sleep(15)

# Check container status and logs
logger.info("")
logger.info("🔍 Checking container status and logs...")
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

    # Check container status
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker ps --filter name=iron-legion-router --format '{{.Names}}\t{{.Status}}'",
        timeout=10
    )
    status = stdout.read().decode().strip()
    logger.info(f"Container status: {status}")

    # Check logs for errors
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker logs iron-legion-router --tail 15 2>&1",
        timeout=10
    )
    logs = stdout.read().decode().strip()
    if logs:
        logger.info("")
        logger.info("Container logs (last 15 lines):")
        logger.info(logs)

        # Check for import error
        if "ModuleNotFoundError" in logs or "iron_legion_dynamic_router" in logs:
            if "ModuleNotFoundError" in logs:
                logger.error("❌ Module import error still present")
            else:
                logger.info("✅ No import errors in recent logs")

    ssh_client.close()
except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

logger.info("")
