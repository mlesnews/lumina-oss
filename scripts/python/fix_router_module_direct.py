#!/usr/bin/env python3
"""
Fix Router Module - Direct Copy to Container
Copies iron_legion_dynamic_router.py directly into the running container

Tags: #FIX #ROUTER #DOCKER @JARVIS @LUMINA @DOIT
"""
import sys
import subprocess
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
    logger = get_logger("FixRouterModule")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixRouterModule")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔧 FIX ROUTER MODULE - DIRECT COPY")
logger.info("=" * 70)
logger.info("")

# Step 1: Verify file exists locally
dynamic_router_path = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
if not dynamic_router_path.exists():
    logger.error("❌ iron_legion_dynamic_router.py not found locally")
    sys.exit(1)

logger.info("✅ Found iron_legion_dynamic_router.py locally")

# Step 2: Connect via SSH
logger.info("🔌 Connecting to KAIJU_NO_8 via SSH...")
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
except Exception as e:
    logger.error(f"❌ SSH connection failed: {e}")
    sys.exit(1)

# Step 3: Copy file to container using docker cp via SSH
logger.info("📤 Copying file to container...")
try:
    # Read file content
    with open(dynamic_router_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Create directory in container
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker exec iron-legion-router mkdir -p /app/scripts/python'",
        timeout=10
    )
    stdout.channel.recv_exit_status()

    # Write file to container using Python
    # Base64 encode to avoid shell escaping issues
    import base64
    encoded = base64.b64encode(file_content.encode('utf-8')).decode('ascii')

    python_script = f'''
import base64
import sys
content = base64.b64decode("{encoded}").decode('utf-8')
with open('/app/scripts/python/iron_legion_dynamic_router.py', 'w') as f:
    f.write(content)
'''

    # Execute Python in container
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'docker exec iron-legion-router python3 -c {repr(python_script)}'",
        timeout=10
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ File copied to container")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Copy warning: {error}")

        # Alternative: Use echo with base64 decode
        logger.info("   Trying alternative method...")
        stdin, stdout, stderr = ssh_client.exec_command(
            f"bash -c 'echo {encoded} | docker exec -i iron-legion-router bash -c \"base64 -d > /app/scripts/python/iron_legion_dynamic_router.py\"'",
            timeout=10
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logger.info("✅ File copied using alternative method")
        else:
            logger.error("❌ Failed to copy file")

except Exception as e:
    logger.error(f"❌ Error copying file: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Verify file exists in container
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
        logger.warning("⚠️  File verification failed")
except Exception as e:
    logger.warning(f"⚠️  Verification error: {e}")

# Step 5: Restart container
logger.info("")
logger.info("🔄 Restarting router container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker restart iron-legion-router'",
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
logger.info("⏳ Waiting 10 seconds for container to start...")
import time
time.sleep(10)

# Check container status
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
        "bash -c 'docker logs iron-legion-router --tail 20'",
        timeout=10
    )
    logs = stdout.read().decode().strip()
    if logs:
        logger.info("Container logs (last 20 lines):")
        logger.info(logs)

    # Check if container is running
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker ps --filter name=iron-legion-router --format \"{{{{.Status}}}}\"'",
        timeout=10
    )
    status = stdout.read().decode().strip()
    logger.info(f"Container status: {status}")

    ssh_client.close()
except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

logger.info("")
