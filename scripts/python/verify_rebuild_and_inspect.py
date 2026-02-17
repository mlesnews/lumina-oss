#!/usr/bin/env python3
"""
Verify Rebuild and Inspect Container
Checks if rebuild worked and inspects container contents

Tags: #VERIFY #INSPECT #CONTAINER @JARVIS @LUMINA @DOIT
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
    logger = get_logger("VerifyRebuild")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VerifyRebuild")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔍 VERIFY REBUILD AND INSPECT CONTAINER")
logger.info("=" * 70)
logger.info("")

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

# Check container image
logger.info("")
logger.info("🔍 Checking container image...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker inspect iron-legion-router --format '{{.Config.Image}}'",
    timeout=10
)
image = stdout.read().decode().strip()
logger.info(f"Container image: {image}")

# Check when image was created
stdin, stdout, stderr = ssh_client.exec_command(
    "docker images iron-legion-router --format '{{.CreatedAt}}'",
    timeout=10
)
created = stdout.read().decode().strip()
logger.info(f"Image created: {created}")

# Check if files exist in container
logger.info("")
logger.info("🔍 Checking files in container...")

# Wait for container to be briefly up
import time
for i in range(10):
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker ps --filter name=iron-legion-router --format '{{.Status}}'",
        timeout=5
    )
    status = stdout.read().decode().strip()
    if "Up" in status and "Restarting" not in status:
        logger.info(f"Container is up (attempt {i+1})")
        break
    time.sleep(1)

# Check router file
stdin, stdout, stderr = ssh_client.exec_command(
    "timeout 5 docker exec iron-legion-router head -30 /app/iron_legion_router.py 2>&1 || echo 'NOT_ACCESSIBLE'",
    timeout=10
)
router_file = stdout.read().decode().strip()
if router_file and "NOT_ACCESSIBLE" not in router_file:
    logger.info("")
    logger.info("First 30 lines of /app/iron_legion_router.py:")
    for line in router_file.split('\n')[:30]:
        if line.strip():
            logger.info(f"   {line}")

    # Check if it has our graceful import handling
    if "IronLegionDynamicRouter = None" in router_file or "try:" in router_file and "iron_legion_dynamic_router" in router_file:
        logger.info("✅ Router file has graceful import handling")
    else:
        logger.warning("⚠️  Router file may not have graceful import handling")
else:
    logger.warning("⚠️  Cannot access router file in container")

# Check if dynamic router module exists
stdin, stdout, stderr = ssh_client.exec_command(
    "timeout 5 docker exec iron-legion-router ls -la /app/scripts/python/iron_legion_dynamic_router.py 2>&1 || echo 'NOT_FOUND'",
    timeout=10
)
module_check = stdout.read().decode().strip()
if "NOT_FOUND" not in module_check and "iron_legion_dynamic_router.py" in module_check:
    logger.info("✅ Dynamic router module exists in container")
    logger.info(f"   {module_check}")
else:
    logger.warning("⚠️  Dynamic router module not found in container")
    logger.warning(f"   {module_check}")

# Check PYTHONPATH
stdin, stdout, stderr = ssh_client.exec_command(
    "timeout 5 docker exec iron-legion-router env | grep PYTHONPATH || echo 'NOT_SET'",
    timeout=10
)
pythonpath = stdout.read().decode().strip()
logger.info(f"PYTHONPATH: {pythonpath}")

# Check what's actually in /app
stdin, stdout, stderr = ssh_client.exec_command(
    "timeout 5 docker exec iron-legion-router ls -la /app/ 2>&1 | head -20 || echo 'NOT_ACCESSIBLE'",
    timeout=10
)
app_contents = stdout.read().decode().strip()
if app_contents and "NOT_ACCESSIBLE" not in app_contents:
    logger.info("")
    logger.info("Contents of /app:")
    for line in app_contents.split('\n')[:15]:
        if line.strip():
            logger.info(f"   {line}")

# Get full error from logs
logger.info("")
logger.info("📄 Full error from logs...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker logs iron-legion-router --tail 50 2>&1 | grep -A 5 -B 5 'ModuleNotFoundError' || docker logs iron-legion-router --tail 50 2>&1",
    timeout=10
)
error_logs = stdout.read().decode().strip()
if error_logs:
    logger.info("Error context:")
    for line in error_logs.split('\n')[-30:]:
        if line.strip():
            logger.info(f"   {line}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ VERIFICATION COMPLETE")
logger.info("=" * 70)
