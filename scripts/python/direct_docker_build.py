#!/usr/bin/env python3
"""
Direct Docker Build
Uses docker build directly without docker-compose

Tags: #REBUILD #DOCKER #DIRECT @JARVIS @LUMINA @DOIT
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
    logger = get_logger("DirectDockerBuild")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DirectDockerBuild")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔨 DIRECT DOCKER BUILD")
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

# Stop container
logger.info("")
logger.info("🛑 Stopping container...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker stop iron-legion-router 2>&1 || true",
    timeout=30
)
stdout.channel.recv_exit_status()
stdin, stdout, stderr = ssh_client.exec_command(
    "docker rm iron-legion-router 2>&1 || true",
    timeout=10
)
stdout.channel.recv_exit_status()
logger.info("✅ Container stopped and removed")

# Find project root
logger.info("")
logger.info("🔍 Finding project structure...")
compose_dir = "/volume1/docker/iron-legion-router"

# Check where files actually are
stdin, stdout, stderr = ssh_client.exec_command(
    f"ls -la {compose_dir}/*.py {compose_dir}/*.yml {compose_dir}/Dockerfile* 2>&1 | head -20",
    timeout=10
)
files = stdout.read().decode().strip()
logger.info("Files in compose directory:")
for line in files.split('\n')[:15]:
    if line.strip():
        logger.info(f"   {line}")

# Try building from compose directory with Dockerfile there
logger.info("")
logger.info("🔨 Building container...")
logger.info("   Building from compose directory with local Dockerfile")

build_cmd = f"bash -c 'cd {compose_dir} && docker build -f Dockerfile.router -t iron-legion-router:latest .'"

logger.info(f"   Command: docker build -f Dockerfile.router -t iron-legion-router:latest .")
logger.info(f"   Directory: {compose_dir}")

try:
    stdin, stdout, stderr = ssh_client.exec_command(
        build_cmd,
        timeout=600
    )

    # Read output
    output = []
    while True:
        line = stdout.readline()
        if not line:
            break
        line = line.strip()
        if line:
            output.append(line)
            if any(kw in line for kw in ["Step", "ERROR", "Successfully", "Building", "Pulling"]):
                logger.info(f"   {line}")

    exit_status = stdout.channel.recv_exit_status()
    stderr_output = stderr.read().decode()

    if exit_status == 0:
        logger.info("✅ Build successful!")
    else:
        logger.error(f"❌ Build failed (exit {exit_status})")
        if stderr_output:
            logger.error("Errors:")
            for line in stderr_output.split('\n')[-10:]:
                if line.strip():
                    logger.error(f"   {line}")
        if output:
            logger.error("Last output:")
            for line in output[-10:]:
                logger.error(f"   {line}")
        ssh_client.close()
        sys.exit(1)

except Exception as e:
    logger.error(f"❌ Build error: {e}")
    ssh_client.close()
    sys.exit(1)

# Start container using docker run
logger.info("")
logger.info("🚀 Starting container...")

# Get the run command from docker-compose or use defaults
run_cmd = """bash -c 'docker run -d \\
  --name iron-legion-router \\
  --restart unless-stopped \\
  -p 3000:3000 \\
  -v "D:/Dropbox/my_projects/config:/app/config:ro" \\
  -v "D:/Dropbox/my_projects/scripts/python:/app/scripts:ro" \\
  -e PYTHONPATH=/app:/app/scripts/python \\
  iron-legion-router:latest'"""

try:
    stdin, stdout, stderr = ssh_client.exec_command(
        run_cmd,
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ Container started")
    else:
        error = stderr.read().decode()
        logger.error(f"❌ Start failed: {error}")
except Exception as e:
    logger.error(f"❌ Start error: {e}")

# Wait and check
logger.info("")
logger.info("⏳ Waiting 20 seconds...")
time.sleep(20)

stdin, stdout, stderr = ssh_client.exec_command(
    "docker ps --filter name=iron-legion-router --format '{{.Names}}\t{{.Status}}'",
    timeout=10
)
status = stdout.read().decode().strip()
logger.info(f"Container status: {status}")

stdin, stdout, stderr = ssh_client.exec_command(
    "docker logs iron-legion-router --tail 30 2>&1",
    timeout=10
)
logs = stdout.read().decode().strip()
if logs:
    logger.info("")
    logger.info("Recent logs:")
    for line in logs.split('\n')[-20:]:
        if line.strip():
            logger.info(f"   {line}")

    if "ModuleNotFoundError" not in logs:
        logger.info("✅ No import errors!")
    else:
        logger.error("❌ Import error still present")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ BUILD COMPLETE")
logger.info("=" * 70)
