#!/usr/bin/env python3
"""
Rebuild Router via Shell Script
Creates a shell script on NAS and executes it for rebuild

Tags: #REBUILD #ROUTER #SCRIPT #NAS @JARVIS @LUMINA @DOIT
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
    logger = get_logger("RebuildViaScript")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RebuildViaScript")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔨 REBUILD ROUTER VIA SHELL SCRIPT")
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

# Create rebuild script
compose_dir = "/volume1/docker/iron-legion-router"
script_path = f"{compose_dir}/rebuild_router.sh"

rebuild_script = f"""#!/bin/bash
set -e

echo "=========================================="
echo "Rebuilding Iron Legion Router Container"
echo "=========================================="
echo ""

cd {compose_dir}

echo "🛑 Stopping and removing old container..."
docker stop iron-legion-router 2>/dev/null || true
docker rm iron-legion-router 2>/dev/null || true
echo "✅ Container stopped and removed"
echo ""

echo "🔨 Rebuilding container image..."
echo "   This may take several minutes..."
docker-compose build --no-cache iron-legion-router
echo "✅ Container built successfully"
echo ""

echo "🚀 Starting container..."
docker-compose up -d iron-legion-router
echo "✅ Container started"
echo ""

echo "⏳ Waiting 10 seconds for container to initialize..."
sleep 10
echo ""

echo "🔍 Checking container status..."
docker ps --filter name=iron-legion-router --format "{{{{.Names}}}}\\t{{{{.Status}}}}"
echo ""

echo "📄 Recent logs:"
docker logs iron-legion-router --tail 20 2>&1
echo ""

echo "=========================================="
echo "✅ Rebuild Complete"
echo "=========================================="
"""

logger.info("")
logger.info("📝 Creating rebuild script on NAS...")
try:
    sftp = ssh_client.open_sftp()

    # Write script to file
    with sftp.file(script_path, 'w') as f:
        f.write(rebuild_script)

    # Make executable
    stdin, stdout, stderr = ssh_client.exec_command(
        f"chmod +x {script_path}",
        timeout=5
    )
    stdout.channel.recv_exit_status()

    sftp.close()
    logger.info(f"✅ Script created at {script_path}")
except Exception as e:
    logger.error(f"❌ Failed to create script: {e}")
    ssh_client.close()
    sys.exit(1)

# Execute script
logger.info("")
logger.info("🚀 Executing rebuild script...")
logger.info("   This will take several minutes...")
logger.info("")

try:
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash {script_path}",
        timeout=600  # 10 minutes
    )

    # Stream output in real-time
    logger.info("Build output:")
    output_lines = []
    while True:
        line = stdout.readline()
        if not line:
            break
        line = line.strip()
        if line:
            output_lines.append(line)
            logger.info(f"   {line}")

    # Read any remaining output
    remaining = stdout.read().decode()
    if remaining:
        for line in remaining.split('\n'):
            if line.strip():
                logger.info(f"   {line}")

    exit_status = stdout.channel.recv_exit_status()

    # Also check stderr
    stderr_output = stderr.read().decode()
    if stderr_output:
        for line in stderr_output.split('\n'):
            if line.strip():
                logger.warning(f"   WARNING: {line}")

    if exit_status == 0:
        logger.info("")
        logger.info("✅ Rebuild completed successfully!")
    else:
        logger.error(f"❌ Rebuild failed with exit status {exit_status}")

except Exception as e:
    logger.error(f"❌ Execution error: {e}")
    import traceback
    traceback.print_exc()

# Final verification
logger.info("")
logger.info("🔍 Final verification...")
time.sleep(5)

try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker ps --filter name=iron-legion-router --format '{{.Names}}\t{{.Status}}'",
        timeout=10
    )
    status = stdout.read().decode().strip()
    logger.info(f"Container status: {status}")

    if "Restarting" in status:
        logger.warning("⚠️  Container is restarting - checking logs...")
        stdin, stdout, stderr = ssh_client.exec_command(
            "docker logs iron-legion-router --tail 30 2>&1",
            timeout=10
        )
        logs = stdout.read().decode().strip()
        if logs:
            logger.info("Recent logs:")
            for line in logs.split('\n')[-20:]:
                if line.strip():
                    logger.info(f"   {line}")

            if "ModuleNotFoundError" in logs and "iron_legion_dynamic_router" in logs:
                logger.error("❌ Import error still present!")
            elif "ModuleNotFoundError" not in logs:
                logger.info("✅ No import errors detected!")
    elif "Up" in status:
        logger.info("✅ Container is running!")

        # Test health endpoint
        stdin, stdout, stderr = ssh_client.exec_command(
            "curl -s http://localhost:3000/health 2>&1 || echo 'FAILED'",
            timeout=10
        )
        health = stdout.read().decode().strip()
        if "healthy" in health or "200" in health:
            logger.info(f"✅ Health endpoint responding: {health}")
        else:
            logger.warning(f"⚠️  Health endpoint: {health}")

except Exception as e:
    logger.warning(f"⚠️  Verification error: {e}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ REBUILD PROCESS COMPLETE")
logger.info("=" * 70)
logger.info("")
