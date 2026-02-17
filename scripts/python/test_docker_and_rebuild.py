#!/usr/bin/env python3
"""
Test Docker and Rebuild
Test Docker availability and try simpler rebuild approach

Tags: #TEST #DOCKER #REBUILD @JARVIS @LUMINA @DOIT
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
    logger = get_logger("TestDockerRebuild")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("TestDockerRebuild")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🧪 TEST DOCKER AND REBUILD")
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

# Test Docker
logger.info("")
logger.info("🧪 Testing Docker...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker --version",
    timeout=10
)
docker_version = stdout.read().decode().strip()
error = stderr.read().decode().strip()
logger.info(f"Docker version: {docker_version}")
if error:
    logger.warning(f"Docker error: {error}")

# Test docker-compose
logger.info("")
logger.info("🧪 Testing docker-compose...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker-compose --version",
    timeout=10
)
compose_version = stdout.read().decode().strip()
error = stderr.read().decode().strip()
logger.info(f"Docker-compose version: {compose_version}")
if error:
    logger.warning(f"Docker-compose error: {error}")

# Check compose directory
compose_dir = "/volume1/docker/iron-legion-router"
logger.info("")
logger.info(f"🔍 Checking {compose_dir}...")
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'ls -la {compose_dir} 2>&1 | head -20'",
    timeout=10
)
files = stdout.read().decode().strip()
if files:
    logger.info("Files:")
    for line in files.split('\n')[:20]:
        if line.strip():
            logger.info(f"   {line}")

# Try simple docker build command
logger.info("")
logger.info("🔨 Trying simple docker build...")
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'cd {compose_dir} && pwd && ls -la Dockerfile.router 2>&1'",
    timeout=10
)
output = stdout.read().decode().strip()
error = stderr.read().decode().strip()
logger.info(f"Output: {output}")
if error:
    logger.info(f"Error: {error}")

# Try actual build with verbose output
logger.info("")
logger.info("🔨 Attempting build with full error output...")
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'cd {compose_dir} && docker build -f Dockerfile.router -t test-router:latest . 2>&1'",
    timeout=60
)

# Read all output
all_output = []
while True:
    line = stdout.readline()
    if not line:
        break
    line = line.strip()
    if line:
        all_output.append(line)
        logger.info(f"   {line}")

# Also read stderr
stderr_output = stderr.read().decode()
if stderr_output:
    for line in stderr_output.split('\n'):
        if line.strip():
            logger.error(f"   ERROR: {line}")

exit_status = stdout.channel.recv_exit_status()
logger.info(f"Exit status: {exit_status}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ TEST COMPLETE")
logger.info("=" * 70)
