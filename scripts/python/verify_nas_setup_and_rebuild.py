#!/usr/bin/env python3
"""
Verify NAS Setup and Rebuild Router
Checks file locations and rebuilds container

Tags: #VERIFY #REBUILD #ROUTER #NAS @JARVIS @LUMINA @DOIT
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
    logger = get_logger("VerifyNASRebuild")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VerifyNASRebuild")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔍 VERIFY NAS SETUP AND REBUILD ROUTER")
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

# Step 1: Check current setup
logger.info("")
logger.info("🔍 Checking NAS file structure...")
compose_dir = "/volume1/docker/iron-legion-router"

# Check if compose directory exists
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'ls -la {compose_dir} 2>&1'",
    timeout=10
)
files = stdout.read().decode().strip()
if files:
    logger.info(f"Files in {compose_dir}:")
    for line in files.split('\n')[:20]:
        if line.strip():
            logger.info(f"   {line}")
else:
    error = stderr.read().decode()
    logger.warning(f"⚠️  Directory check: {error}")

# Check for docker-compose.yml
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'test -f {compose_dir}/docker-compose.yml && echo EXISTS || echo NOT_FOUND'",
    timeout=5
)
compose_exists = stdout.read().decode().strip()
logger.info(f"Docker-compose.yml: {compose_exists}")

# Check for Dockerfile
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'test -f {compose_dir}/Dockerfile.router && echo EXISTS || echo NOT_FOUND'",
    timeout=5
)
dockerfile_exists = stdout.read().decode().strip()
logger.info(f"Dockerfile.router: {dockerfile_exists}")

# Check for iron_legion_router_simple.py
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'test -f {compose_dir}/iron_legion_router_simple.py && echo EXISTS || echo NOT_FOUND'",
    timeout=5
)
router_file_exists = stdout.read().decode().strip()
logger.info(f"iron_legion_router_simple.py: {router_file_exists}")

# Check for dynamic router module
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'test -f {compose_dir}/scripts/python/iron_legion_dynamic_router.py && echo EXISTS || echo NOT_FOUND'",
    timeout=5
)
dynamic_router_exists = stdout.read().decode().strip()
logger.info(f"iron_legion_dynamic_router.py: {dynamic_router_exists}")

# Step 2: Check project root (where build context should be)
logger.info("")
logger.info("🔍 Checking build context...")
# Build context is ../../ from compose_dir
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'cd {compose_dir} && readlink -f ../.. || realpath ../.. || pwd'",
    timeout=5
)
build_context = stdout.read().decode().strip()
logger.info(f"Build context (../../): {build_context}")

# Check if project root has the files
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'test -f {build_context}/scripts/python/iron_legion_dynamic_router.py && echo EXISTS || echo NOT_FOUND'",
    timeout=5
)
module_in_context = stdout.read().decode().strip()
logger.info(f"Module in build context: {module_in_context}")

# Step 3: If files are missing, copy them
if dynamic_router_exists == "NOT_FOUND" or module_in_context == "NOT_FOUND":
    logger.info("")
    logger.info("📤 Copying missing files...")

    # Connect via SFTP
    sftp = ssh_client.open_sftp()

    # Copy dynamic router module
    local_module = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
    if local_module.exists():
        # Copy to compose_dir/scripts/python
        remote_dir = f"{compose_dir}/scripts/python"
        stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'mkdir -p {remote_dir}'", timeout=5)
        remote_file = f"{remote_dir}/iron_legion_dynamic_router.py"
        try:
            sftp.put(str(local_module), remote_file)
            logger.info(f"✅ Copied to {remote_file}")
        except Exception as e:
            logger.warning(f"⚠️  Copy to {remote_file} failed: {e}")

        # Also copy to build context
        context_module = f"{build_context}/scripts/python/iron_legion_dynamic_router.py"
        stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'mkdir -p {build_context}/scripts/python'", timeout=5)
        try:
            sftp.put(str(local_module), context_module)
            logger.info(f"✅ Copied to {context_module}")
        except Exception as e:
            logger.warning(f"⚠️  Copy to {context_module} failed: {e}")

    sftp.close()

# Step 4: Stop container
logger.info("")
logger.info("🛑 Stopping container...")
stdin, stdout, stderr = ssh_client.exec_command(
    "bash -c 'docker stop iron-legion-router 2>&1 || docker rm -f iron-legion-router 2>&1 || true'",
    timeout=30
)
stdout.channel.recv_exit_status()
logger.info("✅ Container stopped/removed")
time.sleep(2)

# Step 5: Rebuild using docker build directly (more reliable)
logger.info("")
logger.info("🔨 Rebuilding container...")
# Build from the project root with the Dockerfile
dockerfile_path = f"{build_context}/docker/nas_iron_legion_router/Dockerfile.router"
build_cmd = f"cd {build_context} && docker build -f {dockerfile_path} -t iron-legion-router:latest ."

logger.info(f"   Build command: docker build -f docker/nas_iron_legion_router/Dockerfile.router .")
logger.info(f"   Build context: {build_context}")

stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c '{build_cmd}'",
    timeout=600
)

# Stream output
output_lines = []
error_lines = []
while True:
    line = stdout.readline()
    if not line:
        break
    line = line.strip()
    if line:
        output_lines.append(line)
        if "Step" in line or "ERROR" in line or "Successfully" in line:
            logger.info(f"   {line}")

# Also read stderr
stderr_output = stderr.read().decode()
if stderr_output:
    for line in stderr_output.split('\n'):
        if line.strip():
            error_lines.append(line.strip())

exit_status = stdout.channel.recv_exit_status()

if exit_status == 0:
    logger.info("✅ Container built successfully")
else:
    logger.error("❌ Build failed")
    if error_lines:
        logger.error("Errors:")
        for line in error_lines[-10:]:
            logger.error(f"   {line}")
    sys.exit(1)

# Step 6: Update docker-compose to use the new image or restart
logger.info("")
logger.info("🚀 Starting container...")
try:
    # Use docker-compose up
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'cd {compose_dir} && docker-compose up -d iron-legion-router'",
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ Container started")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Start warning: {error}")
except Exception as e:
    logger.warning(f"⚠️  Start error: {e}")

# Step 7: Wait and check status
logger.info("")
logger.info("⏳ Waiting 30 seconds...")
time.sleep(30)

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

    if "ModuleNotFoundError" not in logs:
        logger.info("✅ No import errors!")
    else:
        logger.error("❌ Import error still present")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ VERIFICATION AND REBUILD COMPLETE")
logger.info("=" * 70)
