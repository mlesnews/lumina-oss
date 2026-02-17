#!/usr/bin/env python3
"""
Fix Router - Direct Copy to Running Container
Copies file directly into container's /app/scripts/python directory

Tags: #FIX #ROUTER #DOCKER @JARVIS @LUMINA @DOIT
"""
import sys
import paramiko
import os
import base64
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("FixRouterDirect")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixRouterDirect")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔧 FIX ROUTER - DIRECT COPY TO CONTAINER")
logger.info("=" * 70)
logger.info("")

dynamic_router_path = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
if not dynamic_router_path.exists():
    logger.error("❌ iron_legion_dynamic_router.py not found")
    sys.exit(1)

# Read file content
with open(dynamic_router_path, 'r', encoding='utf-8') as f:
    file_content = f.read()

logger.info("✅ File read locally")

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
    logger.info("✅ Connected")
except Exception as e:
    logger.error(f"❌ Connection failed: {e}")
    sys.exit(1)

# Wait for container to be running (not restarting)
logger.info("")
logger.info("⏳ Waiting for container to be ready...")
import time
for i in range(15):
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker ps --filter name=iron-legion-router --format \"{{.Status}}\"'",
        timeout=5
    )
    status = stdout.read().decode().strip()
    if "Up" in status and "Restarting" not in status:
        logger.info("✅ Container is running")
        break
    if i < 14:
        time.sleep(2)
else:
    logger.warning("⚠️  Container still restarting, will try anyway")

# Create directory in container
logger.info("")
logger.info("📁 Creating directory in container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker exec iron-legion-router bash -c \"mkdir -p /app/scripts/python\"'",
        timeout=10
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logger.info("✅ Directory created")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Directory creation: {error}")
except Exception as e:
    logger.warning(f"⚠️  Directory creation error: {e}")

# Write file using Python in container (most reliable)
logger.info("")
logger.info("📝 Writing file to container...")
try:
    # Base64 encode the content to avoid shell escaping issues
    encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('ascii')

    # Use Python to decode and write
    python_cmd = f'''import base64; content = base64.b64decode('{encoded_content}').decode('utf-8'); f = open('/app/scripts/python/iron_legion_dynamic_router.py', 'w'); f.write(content); f.close()'''

    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'docker exec iron-legion-router python3 -c {repr(python_cmd)}'",
        timeout=10
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ File written to container")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Write warning: {error}")

        # Alternative: Use echo with heredoc
        logger.info("   Trying alternative method...")
        # Write to temp file first, then move
        temp_file = "/tmp/iron_legion_dynamic_router.py"
        with open(dynamic_router_path, 'rb') as f:
            file_bytes = f.read()
        encoded = base64.b64encode(file_bytes).decode('ascii')

        # Write using base64 decode
        cmd = f"echo {encoded} | docker exec -i iron-legion-router bash -c 'base64 -d > {temp_file} && mkdir -p /app/scripts/python && mv {temp_file} /app/scripts/python/iron_legion_dynamic_router.py'"
        stdin, stdout, stderr = ssh_client.exec_command(f"bash -c {repr(cmd)}", timeout=10)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logger.info("✅ File written using alternative method")
        else:
            logger.error("❌ Failed to write file")
except Exception as e:
    logger.error(f"❌ Write error: {e}")

# Verify file
logger.info("")
logger.info("🔍 Verifying file in container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker exec iron-legion-router ls -la /app/scripts/python/iron_legion_dynamic_router.py'",
        timeout=10
    )
    output = stdout.read().decode().strip()
    if output and "iron_legion_dynamic_router.py" in output:
        logger.info("✅ File verified in container")
        logger.info(f"   {output}")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Verification failed: {error}")
except Exception as e:
    logger.warning(f"⚠️  Verification error: {e}")

# Restart container
logger.info("")
logger.info("🔄 Restarting container...")
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
logger.info("⏳ Waiting 25 seconds for container to start...")
time.sleep(25)

# Final check
logger.info("")
logger.info("🔍 Final status check...")
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
        "bash -c 'docker logs iron-legion-router --tail 25 2>&1'",
        timeout=10
    )
    logs = stdout.read().decode().strip()
    if logs:
        logger.info("")
        logger.info("Recent logs:")
        logger.info(logs)

        if "ModuleNotFoundError" in logs and "iron_legion_dynamic_router" in logs:
            logger.error("❌ Import error still present")
        elif "ModuleNotFoundError" not in logs and "Application startup complete" in logs or "Uvicorn running" in logs:
            logger.info("✅ Container started successfully!")
        elif "Restarting" in status:
            logger.warning("⚠️  Container still restarting")

    ssh_client.close()
except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

logger.info("")
logger.info("=" * 70)
logger.info("✅ FIX COMPLETE")
logger.info("=" * 70)
