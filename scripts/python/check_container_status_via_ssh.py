#!/usr/bin/env python3
"""
Check Container Status via SSH
Checks if containers are actually running on KAIJU_NO_8

Tags: #CLUSTER #DOCKER #SSH #STATUS @JARVIS @LUMINA
"""
import sys
import paramiko
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("CheckContainerStatus")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CheckContainerStatus")

import os

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔍 CHECKING CONTAINER STATUS VIA SSH")
logger.info("=" * 70)
logger.info("")

try:
    # Connect via SSH key
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

    logger.info("✅ Connected via SSH key")
    logger.info("")

    # Check container status
    logger.info("📋 Checking container status...")
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
        timeout=10
    )
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()

    logger.info("Running containers:")
    logger.info("")
    logger.info(output)
    logger.info("")

    # Check specific Iron Legion containers
    logger.info("🔍 Checking Iron Legion containers specifically...")
    containers_to_check = [
        "iron-legion-router",
        "iron-legion-mark-ii-ollama",
        "iron-legion-mark-iii-ollama",
        "iron-legion-mark-vi-ollama",
        "iron-legion-mark-vii-ollama"
    ]

    for container in containers_to_check:
        stdin, stdout, stderr = ssh_client.exec_command(
            f"docker ps --filter name={container} --format '{{{{.Names}}}}\\t{{{{.Status}}}}'",
            timeout=5
        )
        result = stdout.read().decode().strip()
        if result:
            logger.info(f"  ✅ {container}: {result}")
        else:
            logger.warning(f"  ⚠️  {container}: Not running")

    logger.info("")

    # Check container logs for router
    logger.info("📄 Checking router logs (last 10 lines)...")
    stdin, stdout, stderr = ssh_client.exec_command(
        "docker logs iron-legion-router --tail 10 2>&1",
        timeout=10
    )
    logs = stdout.read().decode().strip()
    if logs:
        logger.info("Router logs:")
        logger.info(logs)
    else:
        error_logs = stderr.read().decode().strip()
        if error_logs:
            logger.warning(f"Error logs: {error_logs}")

    ssh_client.close()

except Exception as e:
    logger.error(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
