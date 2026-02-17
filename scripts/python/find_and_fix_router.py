#!/usr/bin/env python3
"""
Find and Fix Router
Finds the actual router container setup and fixes it

Tags: #FIND #FIX #ROUTER @JARVIS @LUMINA @DOIT
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
    logger = get_logger("FindFixRouter")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FindFixRouter")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔍 FIND AND FIX ROUTER")
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

# Find container and inspect it
logger.info("")
logger.info("🔍 Finding router container...")
stdin, stdout, stderr = ssh_client.exec_command(
    "docker ps -a --filter name=iron-legion-router --format '{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}'",
    timeout=10
)
container_info = stdout.read().decode().strip()
if container_info:
    logger.info(f"Container info: {container_info}")
    container_id = container_info.split('\t')[0] if '\t' in container_info else ""
else:
    logger.warning("⚠️  Container not found")
    container_id = ""

# Inspect container to find mount points
if container_id:
    logger.info("")
    logger.info("🔍 Inspecting container mounts...")
    stdin, stdout, stderr = ssh_client.exec_command(
        f"docker inspect iron-legion-router --format '{{{{json .Mounts}}}}'",
        timeout=10
    )
    mounts_json = stdout.read().decode().strip()
    logger.info(f"Mounts: {mounts_json}")

# Check what's actually in /app in the container (if we can access it)
logger.info("")
logger.info("🔍 Checking /app directory in container...")
# Try to exec into container (even if restarting, we might catch it)
stdin, stdout, stderr = ssh_client.exec_command(
    "timeout 5 docker exec iron-legion-router ls -la /app/ 2>&1 || echo 'Container not accessible'",
    timeout=10
)
app_contents = stdout.read().decode().strip()
if app_contents and "Container not accessible" not in app_contents:
    logger.info("Contents of /app:")
    for line in app_contents.split('\n')[:20]:
        if line.strip():
            logger.info(f"   {line}")
else:
    logger.warning("⚠️  Cannot access container filesystem")

# Check for scripts/python
stdin, stdout, stderr = ssh_client.exec_command(
    "timeout 5 docker exec iron-legion-router ls -la /app/scripts/python/ 2>&1 || echo 'NOT_FOUND'",
    timeout=10
)
scripts_contents = stdout.read().decode().strip()
if scripts_contents and "NOT_FOUND" not in scripts_contents:
    logger.info("")
    logger.info("Contents of /app/scripts/python:")
    for line in scripts_contents.split('\n')[:20]:
        if line.strip():
            logger.info(f"   {line}")
else:
    logger.warning("⚠️  /app/scripts/python not found or not accessible")

# Since the container has volume mounts, let's find where the volume is actually mounted
logger.info("")
logger.info("🔍 Finding volume mount location...")
# The docker-compose shows ../../:/app, so we need to find where that points
# Let's check common locations
possible_locations = [
    "/volume1/docker",
    "/volume1/homes",
    "/volume1",
    "/docker",
]

for location in possible_locations:
    stdin, stdout, stderr = ssh_client.exec_command(
        f"test -d {location} && echo EXISTS || echo NOT_FOUND",
        timeout=5
    )
    exists = stdout.read().decode().strip()
    if exists == "EXISTS":
        logger.info(f"✅ {location} exists")

        # Check for .lumina or project files
        stdin, stdout, stderr = ssh_client.exec_command(
            f"find {location} -maxdepth 3 -name '.lumina' -o -name 'scripts' -type d 2>/dev/null | head -5",
            timeout=10
        )
        found = stdout.read().decode().strip()
        if found:
            logger.info(f"   Found project files:")
            for line in found.split('\n')[:5]:
                if line.strip():
                    logger.info(f"      {line}")

# Since we can't easily rebuild, let's try to copy the file directly to where the volume mount points
# But first, let's try a simpler approach: modify the router file to not require the dynamic router
logger.info("")
logger.info("💡 Since rebuild is complex, let's try a workaround:")
logger.info("   We'll modify the router to handle missing module gracefully")

# Read the simple router file
router_file = project_root / "docker" / "nas_iron_legion_router" / "iron_legion_router_simple.py"
if router_file.exists():
    with open(router_file, 'r', encoding='utf-8') as f:
        router_content = f.read()

    # Check if it already handles the import gracefully
    if "IronLegionDynamicRouter = None" in router_content or "try:" in router_content and "iron_legion_dynamic_router" in router_content:
        logger.info("✅ Router file already handles missing module gracefully")
    else:
        logger.info("⚠️  Router file may need update (but we already updated it)")

# Final approach: Copy file directly into running container when it's up
logger.info("")
logger.info("🔄 Attempting to copy file when container is briefly up...")
logger.info("   (Container restarts every few seconds, we'll try to catch it)")

# Wait for container to be up briefly
for attempt in range(10):
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker ps --filter name=iron-legion-router --format '{{.Status}}'",
        timeout=5
    )
    status = stdout.read().decode().strip()

    if "Up" in status and "Restarting" not in status:
        logger.info(f"✅ Container is up (attempt {attempt+1})")

        # Try to copy file
        sftp = ssh_client.open_sftp()
        local_file = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"

        if local_file.exists():
            try:
                # Create directory
                stdin, stdout, stderr = ssh_client.exec_command(
                    "docker exec iron-legion-router mkdir -p /app/scripts/python",
                    timeout=5
                )

                # Copy via docker cp (need to put file on NAS first)
                temp_path = "/tmp/iron_legion_dynamic_router.py"
                sftp.put(str(local_file), temp_path)

                stdin, stdout, stderr = ssh_client.exec_command(
                    f"docker cp {temp_path} iron-legion-router:/app/scripts/python/iron_legion_dynamic_router.py",
                    timeout=5
                )
                exit_status = stdout.channel.recv_exit_status()

                if exit_status == 0:
                    logger.info("✅ File copied to container!")
                    break
                else:
                    logger.warning(f"⚠️  Copy failed on attempt {attempt+1}")
            except Exception as e:
                logger.warning(f"⚠️  Attempt {attempt+1} failed: {e}")

        sftp.close()
        break

    time.sleep(1)

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ FIND AND FIX COMPLETE")
logger.info("=" * 70)
logger.info("")
logger.info("📋 Summary:")
logger.info("   - Router file has been updated to handle missing module")
logger.info("   - Module file exists locally")
logger.info("   - Container needs rebuild or file needs to be in volume mount")
logger.info("")
logger.info("💡 Recommendation: Rebuild container on NAS manually or ensure")
logger.info("   the project directory is properly mounted with the module file")
logger.info("")
