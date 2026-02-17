#!/usr/bin/env python3
"""
Rebuild Router Container on NAS
Stops, rebuilds, and restarts the iron-legion-router container with fixes

Tags: #REBUILD #ROUTER #DOCKER #NAS #FIX @JARVIS @LUMINA @DOIT
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
    logger = get_logger("RebuildRouter")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RebuildRouter")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔨 REBUILD ROUTER CONTAINER")
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

# Step 1: Stop and remove container
logger.info("")
logger.info("🛑 Stopping and removing container...")
try:
    # Stop container
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker stop iron-legion-router 2>&1 || true'",
        timeout=30
    )
    stdout.channel.recv_exit_status()

    # Remove container
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker rm iron-legion-router 2>&1 || true'",
        timeout=10
    )
    stdout.channel.recv_exit_status()

    logger.info("✅ Container stopped and removed")
    time.sleep(2)
except Exception as e:
    logger.warning(f"⚠️  Stop/remove warning: {e}")

# Step 2: Navigate to compose directory and rebuild
logger.info("")
logger.info("🔨 Rebuilding container image...")
compose_dir = "/volume1/docker/iron-legion-router"
try:
    # Change to compose directory and rebuild
    # The build context is ../../ (project root), dockerfile is docker/nas_iron_legion_router/Dockerfile.router
    build_cmd = f"cd {compose_dir} && docker-compose build --no-cache iron-legion-router"

    logger.info(f"   Executing: {build_cmd}")
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c '{build_cmd}'",
        timeout=600  # 10 minutes for build
    )

    # Stream output
    logger.info("   Build output:")
    output_lines = []
    while True:
        line = stdout.readline()
        if not line:
            break
        line = line.strip()
        if line:
            output_lines.append(line)
            if len(output_lines) <= 50:  # Show first 50 lines
                logger.info(f"   {line}")
            elif len(output_lines) == 51:
                logger.info("   ... (more output) ...")

    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ Container rebuilt successfully")
    else:
        error = stderr.read().decode()
        logger.error(f"❌ Build failed: {error}")
        logger.info("")
        logger.info("   Last 20 lines of output:")
        for line in output_lines[-20:]:
            logger.info(f"   {line}")
        sys.exit(1)

except Exception as e:
    logger.error(f"❌ Build error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Start container
logger.info("")
logger.info("🚀 Starting container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'cd {compose_dir} && docker-compose up -d iron-legion-router'",
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ Container started")
    else:
        error = stderr.read().decode()
        logger.error(f"❌ Start failed: {error}")
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Start error: {e}")
    sys.exit(1)

# Step 4: Wait for container to initialize
logger.info("")
logger.info("⏳ Waiting 30 seconds for container to initialize...")
time.sleep(30)

# Step 5: Check container status
logger.info("")
logger.info("🔍 Checking container status...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker ps --filter name=iron-legion-router --format \"{{.Names}}\\t{{.Status}}\"'",
        timeout=10
    )
    status = stdout.read().decode().strip()
    logger.info(f"Container status: {status}")

    if "Restarting" in status:
        logger.warning("⚠️  Container is restarting - checking logs...")
    elif "Up" in status:
        logger.info("✅ Container is running")
    else:
        logger.warning(f"⚠️  Unexpected status: {status}")

except Exception as e:
    logger.warning(f"⚠️  Status check error: {e}")

# Step 6: Check logs for errors
logger.info("")
logger.info("📄 Checking container logs...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'docker logs iron-legion-router --tail 30 2>&1'",
        timeout=10
    )
    logs = stdout.read().decode().strip()

    if logs:
        logger.info("Recent logs:")
        logger.info(logs)

        # Check for specific errors
        if "ModuleNotFoundError" in logs and "iron_legion_dynamic_router" in logs:
            logger.error("❌ Import error still present!")
            logger.error("   The module file may not be in the correct location")
        elif "ModuleNotFoundError" not in logs:
            if "Application startup complete" in logs or "Uvicorn running" in logs or "started server process" in logs:
                logger.info("✅ Container started successfully - no import errors!")
            elif "error" in logs.lower() or "Error" in logs:
                logger.warning("⚠️  Some errors in logs (may be non-critical)")
            else:
                logger.info("✅ No import errors detected")
    else:
        logger.warning("⚠️  No logs available")

except Exception as e:
    logger.warning(f"⚠️  Log check error: {e}")

# Step 7: Test health endpoint
logger.info("")
logger.info("🏥 Testing health endpoint...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "bash -c 'curl -s -o /dev/null -w \"%{http_code}\" http://<NAS_IP>:3000/health || echo FAILED'",
        timeout=10
    )
    http_code = stdout.read().decode().strip()

    if http_code == "200":
        logger.info("✅ Health endpoint responding (200 OK)")
    elif http_code == "FAILED":
        logger.warning("⚠️  Health endpoint not responding")
    else:
        logger.warning(f"⚠️  Health endpoint returned: {http_code}")
except Exception as e:
    logger.warning(f"⚠️  Health check error: {e}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ REBUILD COMPLETE")
logger.info("=" * 70)
logger.info("")
logger.info("📋 Summary:")
logger.info("   - Container rebuilt with updated Dockerfile")
logger.info("   - Module iron_legion_dynamic_router.py should be included")
logger.info("   - Container restarted")
logger.info("")
logger.info("💡 If container is still restarting, check logs for other errors")
logger.info("")
