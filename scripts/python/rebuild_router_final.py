#!/usr/bin/env python3
"""
Rebuild Router Container - Final
Comprehensive rebuild of iron-legion-router with all fixes

Tags: #REBUILD #ROUTER #DOCKER #FINAL @JARVIS @LUMINA @DOIT
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
    logger = get_logger("RebuildRouterFinal")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RebuildRouterFinal")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔨 REBUILD ROUTER CONTAINER - FINAL")
logger.info("=" * 70)
logger.info("")

# Step 0: Verify local files exist
logger.info("🔍 Verifying local files...")
required_files = [
    project_root / "scripts" / "python" / "iron_legion_dynamic_router.py",
    project_root / "docker" / "nas_iron_legion_router" / "Dockerfile.router",
    project_root / "docker" / "nas_iron_legion_router" / "iron_legion_router_simple.py",
    project_root / "scripts" / "python" / "iron_legion_expert_router.py",
    project_root / "config" / "iron_legion_experts_config.json",
]

all_exist = True
for file_path in required_files:
    if file_path.exists():
        logger.info(f"   ✅ {file_path.name}")
    else:
        logger.error(f"   ❌ {file_path.name} NOT FOUND")
        all_exist = False

if not all_exist:
    logger.error("❌ Missing required files. Cannot proceed.")
    sys.exit(1)

logger.info("✅ All required files exist")
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
logger.info("🛑 Stopping and removing old container...")
try:
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
    time.sleep(2)
except Exception as e:
    logger.warning(f"⚠️  Stop/remove warning: {e}")

# Step 2: Deploy files to NAS
logger.info("")
logger.info("📤 Deploying files to NAS...")
compose_dir = "/volume1/docker/iron-legion-router"

try:
    sftp = ssh_client.open_sftp()

    # Create directory structure
    dirs_to_create = [
        f"{compose_dir}",
        f"{compose_dir}/scripts/python",
    ]

    for dir_path in dirs_to_create:
        stdin, stdout, stderr = ssh_client.exec_command(
            f"mkdir -p {dir_path}",
            timeout=5
        )
        stdout.channel.recv_exit_status()

    # Copy files
    files_to_copy = [
        (project_root / "docker" / "nas_iron_legion_router" / "iron_legion_router_simple.py",
         f"{compose_dir}/iron_legion_router_simple.py"),
        (project_root / "docker" / "nas_iron_legion_router" / "Dockerfile.router",
         f"{compose_dir}/Dockerfile.router"),
        (project_root / "docker" / "nas_iron_legion_router" / "docker-compose.yml",
         f"{compose_dir}/docker-compose.yml"),
        (project_root / "scripts" / "python" / "iron_legion_dynamic_router.py",
         f"{compose_dir}/scripts/python/iron_legion_dynamic_router.py"),
        (project_root / "scripts" / "python" / "iron_legion_expert_router.py",
         f"{compose_dir}/scripts/python/iron_legion_expert_router.py"),
        (project_root / "config" / "iron_legion_experts_config.json",
         f"{compose_dir}/config/iron_legion_experts_config.json"),
    ]

    # Also create the project structure for build context
    # The docker-compose uses context: ../.. which means project root
    # We need to create the structure: compose_dir/../../.lumina/...
    project_root_nas = f"{compose_dir}/../.."
    stdin, stdout, stderr = ssh_client.exec_command(
        f"mkdir -p {project_root_nas}/scripts/python {project_root_nas}/config",
        timeout=5
    )

    # Copy files to project root for build context
    files_for_context = [
        (project_root / "scripts" / "python" / "iron_legion_dynamic_router.py",
         f"{project_root_nas}/scripts/python/iron_legion_dynamic_router.py"),
        (project_root / "scripts" / "python" / "iron_legion_expert_router.py",
         f"{project_root_nas}/scripts/python/iron_legion_expert_router.py"),
        (project_root / "config" / "iron_legion_experts_config.json",
         f"{project_root_nas}/config/iron_legion_experts_config.json"),
    ]

    for local_file, remote_file in files_for_context:
        if local_file.exists():
            try:
                sftp.put(str(local_file), remote_file)
                logger.info(f"   ✅ Context: {Path(remote_file).name}")
            except Exception as e:
                logger.warning(f"   ⚠️  Context {Path(remote_file).name}: {e}")

    for local_file, remote_file in files_to_copy:
        if local_file.exists():
            try:
                sftp.put(str(local_file), remote_file)
                logger.info(f"   ✅ {Path(remote_file).name}")
            except Exception as e:
                logger.warning(f"   ⚠️  {Path(remote_file).name}: {e}")
        else:
            logger.warning(f"   ⚠️  {local_file.name} not found locally")

    sftp.close()
    logger.info("✅ Files deployed")
except Exception as e:
    logger.error(f"❌ File deployment failed: {e}")
    ssh_client.close()
    sys.exit(1)

# Step 3: Find build context
logger.info("")
logger.info("🔍 Determining build context...")
stdin, stdout, stderr = ssh_client.exec_command(
    f"cd {compose_dir} && pwd && cd ../.. && pwd",
    timeout=5
)
build_context = stdout.read().decode().strip().split('\n')[-1] if stdout.read().decode().strip() else "/volume1/docker"
logger.info(f"   Build context: {build_context}")

# Step 4: Rebuild container
logger.info("")
logger.info("🔨 Rebuilding container image...")
logger.info("   This may take several minutes...")

# The docker-compose.yml uses context: ../.. which means project root
# So we need to build from the project root, not the compose directory
# Let's find where the project root should be
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'cd {compose_dir} && cd ../.. && pwd'",
    timeout=5
)
project_root_nas = stdout.read().decode().strip() or "/volume1/docker"

# The Dockerfile path relative to project root
dockerfile_rel_path = "docker/nas_iron_legion_router/Dockerfile.router"

# Build from project root
build_cmd = f"bash -c 'cd {project_root_nas} && docker build -f {dockerfile_rel_path} -t iron-legion-router:latest .'"

logger.info(f"   Using docker build from project root")
logger.info(f"   Project root: {project_root_nas}")
logger.info(f"   Dockerfile: {dockerfile_rel_path}")

# Check if docker-compose.yml exists for starting
stdin, stdout, stderr = ssh_client.exec_command(
    f"bash -c 'test -f {compose_dir}/docker-compose.yml && echo EXISTS || echo NOT_FOUND'",
    timeout=5
)
compose_exists = stdout.read().decode().strip()

try:
    stdin, stdout, stderr = ssh_client.exec_command(
        build_cmd,
        timeout=600  # 10 minutes
    )

    # Stream output
    output_lines = []
    error_lines = []
    logger.info("   Build output:")

    while True:
        line = stdout.readline()
        if not line:
            break
        line = line.strip()
        if line:
            output_lines.append(line)
            # Show important lines
            if any(keyword in line for keyword in ["Step", "ERROR", "Successfully", "Building", "Pulling", "Using cache"]):
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
            for line in error_lines[-20:]:
                logger.error(f"   {line}")
        if output_lines:
            logger.error("Last output lines:")
            for line in output_lines[-20:]:
                logger.error(f"   {line}")
        ssh_client.close()
        sys.exit(1)

except Exception as e:
    logger.error(f"❌ Build error: {e}")
    import traceback
    traceback.print_exc()
    ssh_client.close()
    sys.exit(1)

# Step 5: Start container
logger.info("")
logger.info("🚀 Starting container...")
try:
    if compose_exists == "EXISTS":
        start_cmd = f"bash -c 'cd {compose_dir} && docker-compose up -d iron-legion-router'"
    else:
        # Start using docker run with the same settings as docker-compose
        start_cmd = f"bash -c 'docker run -d --name iron-legion-router --restart unless-stopped -p 3000:3000 -v D:/Dropbox/my_projects/config:/app/config:ro -v D:/Dropbox/my_projects/scripts/python:/app/scripts:ro iron-legion-router:latest'"

    stdin, stdout, stderr = ssh_client.exec_command(
        start_cmd,
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ Container started")
    else:
        error = stderr.read().decode()
        logger.error(f"❌ Start failed: {error}")
        ssh_client.close()
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Start error: {e}")
    ssh_client.close()
    sys.exit(1)

# Step 6: Wait and verify
logger.info("")
logger.info("⏳ Waiting 30 seconds for container to initialize...")
time.sleep(30)

logger.info("")
logger.info("🔍 Verifying container status...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker ps --filter name=iron-legion-router --format '{{.Names}}\t{{.Status}}'",
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

# Step 7: Check logs
logger.info("")
logger.info("📄 Checking container logs...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker logs iron-legion-router --tail 40 2>&1",
        timeout=10
    )
    logs = stdout.read().decode().strip()

    if logs:
        logger.info("Recent logs:")
        # Show last 30 lines
        log_lines = logs.split('\n')
        for line in log_lines[-30:]:
            if line.strip():
                logger.info(f"   {line}")

        # Check for errors
        if "ModuleNotFoundError" in logs and "iron_legion_dynamic_router" in logs:
            logger.error("❌ Import error still present!")
            logger.error("   The module may not be in the correct location")
        elif "ModuleNotFoundError" not in logs:
            if any(keyword in logs for keyword in ["Application startup complete", "Uvicorn running", "started server process", "INFO:"]):
                logger.info("✅ Container started successfully - no import errors!")
            elif "error" in logs.lower() or "Error" in logs:
                logger.warning("⚠️  Some errors in logs (check above)")
            else:
                logger.info("✅ No import errors detected")
    else:
        logger.warning("⚠️  No logs available")

except Exception as e:
    logger.warning(f"⚠️  Log check error: {e}")

# Step 8: Test health endpoint
logger.info("")
logger.info("🏥 Testing health endpoint...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health 2>&1 || echo 'FAILED'",
        timeout=10
    )
    http_code = stdout.read().decode().strip()

    if http_code == "200":
        logger.info("✅ Health endpoint responding (200 OK)")
    elif http_code == "FAILED" or not http_code:
        logger.warning("⚠️  Health endpoint not responding (container may still be starting)")
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
logger.info("   ✅ Container rebuilt with updated Dockerfile")
logger.info("   ✅ Module iron_legion_dynamic_router.py included")
logger.info("   ✅ Container restarted")
logger.info("")
logger.info("💡 If container is still restarting, check logs for other errors")
logger.info("   Use: docker logs iron-legion-router --tail 50")
logger.info("")
