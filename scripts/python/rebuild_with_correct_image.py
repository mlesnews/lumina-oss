#!/usr/bin/env python3
"""
Rebuild with Correct Image Name
Rebuilds using the correct image name from docker-compose

Tags: #REBUILD #IMAGE #CORRECT @JARVIS @LUMINA @DOIT
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
    logger = get_logger("RebuildCorrectImage")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RebuildCorrectImage")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔨 REBUILD WITH CORRECT IMAGE NAME")
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

compose_dir = "/volume1/docker/iron-legion-router"

# Check docker-compose to see what image name it expects
logger.info("")
logger.info("🔍 Checking docker-compose.yml for image name...")
stdin, stdout, stderr = ssh_client.exec_command(
    f"grep -i 'image:' {compose_dir}/docker-compose.yml || grep -A 5 'build:' {compose_dir}/docker-compose.yml | head -10",
    timeout=10
)
compose_info = stdout.read().decode().strip()
logger.info("Docker-compose build/image info:")
for line in compose_info.split('\n')[:10]:
    if line.strip():
        logger.info(f"   {line}")

# The docker-compose uses build context: ../.. and dockerfile: docker/nas_iron_legion_router/Dockerfile.router
# So we need to build from the project root
logger.info("")
logger.info("🔨 Building from project root...")

# Find project root (../../ from compose_dir)
stdin, stdout, stderr = ssh_client.exec_command(
    f"cd {compose_dir} && cd ../.. && pwd",
    timeout=5
)
project_root_nas = stdout.read().decode().strip() or "/volume1/docker"

logger.info(f"Project root: {project_root_nas}")
logger.info(f"Dockerfile: docker/nas_iron_legion_router/Dockerfile.router")

# Stop container first
logger.info("")
logger.info("🛑 Stopping container...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker stop iron-legion-router 2>&1 || true",
    timeout=30
)
stdin, stdout, stderr = ssh_client.exec_command(
    "docker rm iron-legion-router 2>&1 || true",
    timeout=10
)

# Build using shell
shell = ssh_client.invoke_shell()
time.sleep(1)

build_cmd = f"cd {project_root_nas} && docker build -f docker/nas_iron_legion_router/Dockerfile.router -t iron-legion/router:latest .\n"

logger.info("")
logger.info("🔨 Building container (this will take several minutes)...")
logger.info(f"   Command: docker build -f docker/nas_iron_legion_router/Dockerfile.router -t iron-legion/router:latest .")

shell.send(build_cmd)
time.sleep(2)

# Monitor build output
output_lines = []
for i in range(300):  # Wait up to 10 minutes
    if shell.recv_ready():
        output = shell.recv(4096).decode('utf-8', errors='ignore')
        output_lines.append(output)
        # Show important lines
        for line in output.split('\n'):
            if any(kw in line for kw in ["Step", "Successfully", "ERROR", "Error", "Building", "Pulling"]):
                logger.info(f"   {line.strip()}")
    time.sleep(2)

    # Check if build finished
    if "Successfully built" in ''.join(output_lines) or "Successfully tagged" in ''.join(output_lines):
        logger.info("✅ Build completed!")
        break
    if "ERROR" in ''.join(output_lines) or "error" in ''.join(output_lines):
        logger.warning("⚠️  Build errors detected")
        break

# Start container
logger.info("")
logger.info("🚀 Starting container...")
start_cmd = f"cd {compose_dir} && docker-compose up -d iron-legion-router\n"
shell.send(start_cmd)
time.sleep(5)

shell.send("exit\n")
time.sleep(2)
shell.close()

# Wait and verify
logger.info("")
logger.info("⏳ Waiting 30 seconds for container to start...")
time.sleep(30)

stdin, stdout, stderr = ssh_client.exec_command(
    "docker ps --filter name=iron-legion-router --format '{{.Names}}\t{{.Status}}'",
    timeout=10
)
status = stdout.read().decode().strip()
logger.info(f"Container status: {status}")

stdin, stdout, stderr = ssh_client.exec_command(
    "docker logs iron-legion-router --tail 40 2>&1",
    timeout=10
)
logs = stdout.read().decode().strip()
if logs:
    logger.info("")
    logger.info("Recent logs:")
    for line in logs.split('\n')[-25:]:
        if line.strip():
            logger.info(f"   {line}")

    if "ModuleNotFoundError" not in logs:
        logger.info("✅ No import errors!")
    else:
        logger.error("❌ Import error still present")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ REBUILD COMPLETE")
logger.info("=" * 70)
