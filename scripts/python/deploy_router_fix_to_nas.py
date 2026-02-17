#!/usr/bin/env python3
"""
Deploy Router Fix to NAS
Copies iron_legion_dynamic_router.py to NAS and updates container

Tags: #DEPLOY #ROUTER #NAS #FIX @JARVIS @LUMINA @DOIT
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
    logger = get_logger("DeployRouterFix")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DeployRouterFix")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🚀 DEPLOY ROUTER FIX TO NAS")
logger.info("=" * 70)
logger.info("")

# Files to deploy
files_to_deploy = [
    ("scripts/python/iron_legion_dynamic_router.py", "/volume1/docker/iron-legion-router/scripts/python/iron_legion_dynamic_router.py"),
    ("docker/nas_iron_legion_router/iron_legion_router_simple.py", "/volume1/docker/iron-legion-router/iron_legion_router_simple.py"),
    ("docker/nas_iron_legion_router/Dockerfile.router", "/volume1/docker/iron-legion-router/Dockerfile.router"),
]

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

# Deploy files
logger.info("")
logger.info("📤 Deploying files to NAS...")
for local_path, remote_path in files_to_deploy:
    local_file = project_root / local_path
    if not local_file.exists():
        logger.warning(f"⚠️  {local_path} not found, skipping")
        continue

    try:
        # Create remote directory
        remote_dir = str(Path(remote_path).parent)
        stdin, stdout, stderr = ssh_client.exec_command(f"bash -c 'mkdir -p {remote_dir}'", timeout=5)
        stdout.channel.recv_exit_status()

        # Copy file
        sftp.put(str(local_file), remote_path)
        logger.info(f"✅ Deployed: {local_path} -> {remote_path}")
    except Exception as e:
        logger.error(f"❌ Failed to deploy {local_path}: {e}")

sftp.close()

# Rebuild container
logger.info("")
logger.info("🔨 Rebuilding router container...")
try:
    compose_dir = "/volume1/docker/iron-legion-router"
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'cd {compose_dir} && docker-compose build iron-legion-router'",
        timeout=300
    )

    # Stream output
    while True:
        line = stdout.readline()
        if not line:
            break
        if line.strip():
            logger.info(f"   {line.strip()}")

    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logger.info("✅ Container rebuilt successfully")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Rebuild warning: {error}")
except Exception as e:
    logger.error(f"❌ Rebuild error: {e}")

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
logger.info("⏳ Waiting 20 seconds for container to start...")
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
        "bash -c 'docker logs iron-legion-router --tail 15 2>&1'",
        timeout=10
    )
    logs = stdout.read().decode().strip()
    if logs:
        logger.info("")
        logger.info("Recent logs:")
        logger.info(logs)

    ssh_client.close()
except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

logger.info("")
logger.info("=" * 70)
logger.info("✅ DEPLOYMENT COMPLETE")
logger.info("=" * 70)
