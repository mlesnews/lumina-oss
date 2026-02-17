#!/usr/bin/env python3
"""
Rebuild Router via Interactive Shell
Uses interactive shell to avoid PowerShell issues

Tags: #REBUILD #ROUTER #SSH #INTERACTIVE @JARVIS @LUMINA @DOIT
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
    logger = get_logger("RebuildInteractive")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RebuildInteractive")

kaiju_ip = "<NAS_IP>"
ssh_port = 22
ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"
ssh_user = os.getenv("USERNAME", "mlesn").lower()

logger.info("=" * 70)
logger.info("🔨 REBUILD ROUTER VIA INTERACTIVE SHELL")
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

# Use interactive shell
logger.info("")
logger.info("🐚 Opening interactive shell...")
compose_dir = "/volume1/docker/iron-legion-router"

try:
    shell = ssh_client.invoke_shell()
    time.sleep(1)  # Wait for shell to initialize

    # Send commands one by one
    commands = [
        f"cd {compose_dir}\n",
        "docker stop iron-legion-router\n",
        "docker rm iron-legion-router\n",
        "docker-compose build --no-cache iron-legion-router\n",
        "docker-compose up -d iron-legion-router\n",
        "exit\n"
    ]

    logger.info("📤 Sending commands...")
    all_output = ""

    for i, cmd in enumerate(commands):
        logger.info(f"   Executing command {i+1}/{len(commands)}: {cmd.strip()}")
        shell.send(cmd)
        time.sleep(2)  # Wait for command to execute

        # Read output
        if shell.recv_ready():
            output = shell.recv(4096).decode('utf-8', errors='ignore')
            all_output += output
            # Show relevant lines
            for line in output.split('\n'):
                if any(kw in line for kw in ["Step", "Building", "Successfully", "ERROR", "Error", "Up", "Starting"]):
                    logger.info(f"      {line.strip()}")

        # For build command, wait longer
        if "build" in cmd:
            logger.info("      (Build in progress, this may take several minutes...)")
            # Wait and read more output
            for _ in range(60):  # Wait up to 2 minutes
                time.sleep(2)
                if shell.recv_ready():
                    output = shell.recv(4096).decode('utf-8', errors='ignore')
                    all_output += output
                    for line in output.split('\n'):
                        if any(kw in line for kw in ["Step", "Successfully", "ERROR", "Error"]):
                            logger.info(f"      {line.strip()}")
                # Check if command finished (look for prompt)
                if shell.recv_ready() == False and "Successfully" in all_output or "ERROR" in all_output:
                    break

    # Wait for shell to close
    time.sleep(2)

    # Read any remaining output
    while shell.recv_ready():
        output = shell.recv(4096).decode('utf-8', errors='ignore')
        all_output += output

    shell.close()

    logger.info("")
    logger.info("✅ Commands executed")

    # Check if build was successful
    if "Successfully built" in all_output or "Successfully tagged" in all_output:
        logger.info("✅ Container built successfully")
    elif "ERROR" in all_output or "Error" in all_output:
        logger.error("❌ Build errors detected")
        # Show error lines
        for line in all_output.split('\n'):
            if "ERROR" in line or "Error" in line:
                logger.error(f"   {line.strip()}")

except Exception as e:
    logger.error(f"❌ Shell execution error: {e}")
    import traceback
    traceback.print_exc()

# Verify container status
logger.info("")
logger.info("🔍 Verifying container status...")
time.sleep(10)

try:
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
            logger.info("✅ No import errors detected!")
        else:
            logger.error("❌ Import error still present")

except Exception as e:
    logger.warning(f"⚠️  Verification error: {e}")

ssh_client.close()

logger.info("")
logger.info("=" * 70)
logger.info("✅ REBUILD COMPLETE")
logger.info("=" * 70)
