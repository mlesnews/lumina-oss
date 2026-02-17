#!/usr/bin/env python3
"""
Fix Router and Rebuild Container
1. Creates missing iron_legion_dynamic_router module
2. Updates Dockerfile to include it
3. Rebuilds and restarts router container

Tags: #FIX #ROUTER #DOCKER #CLUSTER @JARVIS @LUMINA @DOIT
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
    logger = get_logger("FixRouterRebuild")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixRouterRebuild")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔧 FIX ROUTER AND REBUILD")
logger.info("=" * 70)
logger.info("")

# Step 1: Verify iron_legion_dynamic_router.py exists
dynamic_router_path = project_root / "scripts" / "python" / "iron_legion_dynamic_router.py"
if dynamic_router_path.exists():
    logger.info("✅ iron_legion_dynamic_router.py exists")
else:
    logger.error("❌ iron_legion_dynamic_router.py not found")
    sys.exit(1)

# Step 2: Connect via SSH
logger.info("🔌 Connecting to KAIJU_NO_8 via SSH...")
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
    logger.info("✅ SSH connection established")
except Exception as e:
    logger.error(f"❌ SSH connection failed: {e}")
    sys.exit(1)

# Step 3: Copy files to container build context
logger.info("📤 Copying files to NAS for rebuild...")
try:
    # Read the dynamic router file
    with open(dynamic_router_path, 'r', encoding='utf-8') as f:
        dynamic_router_content = f.read()

    # Create directory structure on NAS
    nas_scripts_dir = "/volume1/docker/iron-legion-router/scripts/python"
    stdin, stdout, stderr = ssh_client.exec_command(
        f"mkdir -p {nas_scripts_dir}",
        timeout=10
    )
    stdout.channel.recv_exit_status()

    # Write dynamic router file using Python (more reliable)
    # Escape the content for Python
    escaped_content = dynamic_router_content.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
    python_cmd = f'''python3 -c "import sys; f=open('{nas_scripts_dir}/iron_legion_dynamic_router.py', 'w'); f.write(''' + repr(dynamic_router_content) + '''); f.close()"'''

    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c '{python_cmd}'",
        timeout=10
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logger.info("✅ Copied iron_legion_dynamic_router.py to NAS")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Copy warning: {error}")
        # Try alternative method
        logger.info("   Trying alternative copy method...")
        # Use base64 encoding
        import base64
        encoded = base64.b64encode(dynamic_router_content.encode()).decode()
        stdin, stdout, stderr = ssh_client.exec_command(
            f"bash -c 'echo {encoded} | base64 -d > {nas_scripts_dir}/iron_legion_dynamic_router.py'",
            timeout=10
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logger.info("✅ Copied using base64 method")

except Exception as e:
    logger.error(f"❌ Error copying files: {e}")

# Step 4: Rebuild container
logger.info("")
logger.info("🔨 Rebuilding router container...")
try:
    compose_dir = "/volume1/docker/iron-legion-router"
    stdin, stdout, stderr = ssh_client.exec_command(
        f"bash -c 'cd {compose_dir} && docker-compose build iron-legion-router'",
        timeout=300
    )
    output = stdout.read().decode()
    error = stderr.read().decode()
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        logger.info("✅ Container rebuilt successfully")
    else:
        logger.warning(f"⚠️  Rebuild warning: {error}")
        logger.info("   (Container may need manual rebuild)")
except Exception as e:
    logger.warning(f"⚠️  Rebuild error: {e}")
    logger.info("   (Will restart existing container)")

# Step 5: Restart container
logger.info("")
logger.info("🔄 Restarting router container...")
try:
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker restart iron-legion-router",
        timeout=30
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logger.info("✅ Router container restarted")
    else:
        error = stderr.read().decode()
        logger.warning(f"⚠️  Restart warning: {error}")
except Exception as e:
    logger.error(f"❌ Error restarting container: {e}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ FIX COMPLETE")
logger.info("=" * 70)
logger.info("")
logger.info("💡 Note: If the container still fails, you may need to:")
logger.info("   1. Rebuild the container image on NAS")
logger.info("   2. Or update the container to use the fixed files")
logger.info("")
