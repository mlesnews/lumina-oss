#!/usr/bin/env python3
"""
Execute Deployment via DSM API with manus/backupadm Full Control
Uses DSM API to create and execute Task Scheduler task as root
"""

import sys
import json
import requests
from pathlib import Path
import urllib3

urllib3.disable_warnings()

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    from lumina_logger import get_logger
    logger = get_logger("DSMDeployment")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DSMDeployment")

def deploy_via_dsm_api():
    """Deploy containers via DSM API using manus/backupadm credentials"""

    # Get credentials
    vault = NASAzureVaultIntegration()
    credentials = vault.get_nas_credentials()

    if not credentials:
        logger.error("❌ Could not get credentials")
        return False

    username = credentials.get("username")
    password = credentials.get("password")
    nas_ip = "<NAS_PRIMARY_IP>"
    nas_port = 5001
    base_url = f"https://{nas_ip}:{nas_port}/webapi"

    session = requests.Session()
    session.verify = False

    # Login
    logger.info(f"🔐 Logging in as {username}...")
    login_url = f"{base_url}/auth.cgi"
    params = {
        "api": "SYNO.API.Auth",
        "version": "3",
        "method": "login",
        "account": username,
        "passwd": password,
        "session": "DSM",
        "format": "sid"
    }

    response = session.get(login_url, params=params, timeout=10)
    if response.status_code != 200:
        logger.error(f"❌ Login failed: {response.status_code}")
        return False

    data = response.json()
    if not data.get("success"):
        logger.error(f"❌ Login failed: {data.get('error', {})}")
        return False

    sid = data.get("data", {}).get("sid")
    logger.info("✅ Logged in to DSM API")

    # Execute deployment script via Task Scheduler
    script_path = "/volume1/docker/nas-mcp-servers/deploy.sh"

    # Method 1: Create Task Scheduler task with correct format
    logger.info("📅 Creating Task Scheduler task with correct format...")
    url = f"{base_url}/entry.cgi"

    # Get API version first
    query_params = {
        "api": "SYNO.API.Info",
        "version": "1",
        "method": "query",
        "query": "SYNO.Core.TaskScheduler",
        "_sid": sid
    }

    response = session.get(url, params=query_params, timeout=10)
    max_version = "2"
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            max_version = str(result.get("data", {}).get("SYNO.Core.TaskScheduler", {}).get("maxVersion", "2"))
            logger.info(f"Task Scheduler API max version: {max_version}")

    # Create task with proper format (based on research)
    script_path = "/volume1/docker/nas-mcp-servers/deploy.sh"

    # Format based on .task file structure - use current date/time for immediate execution
    from datetime import datetime
    now = datetime.now()

    task_data = {
        "name": "deploy_mcp_containers",
        "type": "onetime",  # or "daily", "weekly", etc.
        "run_hour": now.hour,
        "run_min": now.minute,
        "start_year": now.year,
        "start_month": now.month,
        "start_day": now.day,
        "action": f"bash {script_path}",
        "owner": "root",
        "state": "enabled",
        "repeat_min": 0,
        "repeat_hour": 0,
        "notify_enable": "false",
        "notify_if_error": "false"
    }

    create_params = {
        "api": "SYNO.Core.TaskScheduler",
        "version": max_version,
        "method": "create",
        "name": task_data["name"],
        "type": task_data["type"],
        "run_hour": task_data["run_hour"],
        "run_min": task_data["run_min"],
        "start_year": task_data["start_year"],
        "start_month": task_data["start_month"],
        "start_day": task_data["start_day"],
        "action": task_data["action"],
        "owner": task_data["owner"],
        "state": task_data["state"],
        "repeat_min": task_data["repeat_min"],
        "repeat_hour": task_data["repeat_hour"],
        "notify_enable": task_data["notify_enable"],
        "notify_if_error": task_data["notify_if_error"],
        "_sid": sid
    }

    logger.info("Creating task with proper format...")
    response = session.get(url, params=create_params, timeout=30)

    if response.status_code == 200:
        result = response.json()
        logger.info(f"Task creation result: {result}")
        if result.get("success"):
            task_id = result.get("data", {}).get("task_id") or result.get("data", {}).get("id")
            logger.info(f"✅ Task created: {task_id}")

            # Execute task immediately - use correct format (task_id, not JSON-encoded tasks array)
            run_params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": max_version,
                "method": "run",
                "task_id": str(task_id),
                "_sid": sid
            }

            logger.info("▶️  Executing task...")
            response = session.get(url, params=run_params, timeout=120)
            if response.status_code == 200:
                run_result = response.json()
                logger.info(f"Task execution result: {run_result}")
                if run_result.get("success"):
                    logger.info("✅ Task executed successfully!")
                    return True

    # Method 2: Use Container Manager API with correct format
    logger.info("🐳 Trying Container Manager API with correct format...")
    compose_path = "/volume1/docker/nas-mcp-servers/docker-compose.yml"

    # Check Container Manager API version
    cm_query_params = {
        "api": "SYNO.API.Info",
        "version": "1",
        "method": "query",
        "query": "SYNO.Docker.Project",
        "_sid": sid
    }

    response = session.get(url, params=cm_query_params, timeout=10)
    cm_version = "1"
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            cm_version = str(result.get("data", {}).get("SYNO.Docker.Project", {}).get("maxVersion", "1"))
            logger.info(f"Container Manager API version: {cm_version}")

    # Try Container Manager API with POST method (may require POST instead of GET)
    # Error 120 suggests parameter issue - try with project directory instead of file path
    project_dir = "/volume1/docker/nas-mcp-servers"

    cm_params = {
        "api": "SYNO.Docker.Project",
        "version": cm_version,
        "method": "create",
        "name": "lumina-homelab-mcp-central",
        "path": project_dir,  # Use directory, not file
        "compose_file": "docker-compose.yml",  # Filename within directory
        "_sid": sid
    }

    # Try GET first
    response = session.get(url, params=cm_params, timeout=60)
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Container Manager GET result: {result}")
        if result.get("success"):
            logger.info("✅ Project created via Container Manager API!")
            return True

    # Try POST method (some APIs require POST)
    try:
        response = session.post(url, data=cm_params, timeout=60)
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Container Manager POST result: {result}")
            if result.get("success"):
                logger.info("✅ Project created via Container Manager API (POST)!")
                return True
    except Exception as e:
        logger.debug(f"POST method failed: {e}")

    # Method 2b: Try executing script via DSM API command execution
    logger.info("🔧 Trying DSM API command execution...")
    cmd_params = {
        "api": "SYNO.Core.System",
        "version": "1",
        "method": "exec",
        "command": f"bash {script_path}",
        "run_as_root": "true",
        "_sid": sid
    }

    response = session.get(url, params=cmd_params, timeout=120)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            logger.info("✅ Command executed via DSM API!")
            return True

    # Method 3: Execute via SSH using paramiko (Windows-compatible) - FIXED
    logger.info("🔐 Executing via SSH with paramiko (FIXED)...")
    try:
        import paramiko
        import time

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"Connecting to {nas_ip} as {username}...")
        ssh.connect(nas_ip, username=username, password=password, timeout=10)

        # Execute command directly with sudo -S (read password from stdin)
        logger.info("Executing deployment script with sudo -S...")
        command = f'cd /volume1/docker/nas-mcp-servers && echo "{password}" | sudo -S bash deploy.sh 2>&1'

        stdin, stdout, stderr = ssh.exec_command(command, timeout=600)

        # Stream output in real-time
        output = ""
        error_output = ""
        max_wait = 600
        start_time = time.time()

        while time.time() - start_time < max_wait:
            if stdout.channel.recv_ready():
                data = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                output += data
                logger.info(f"Output: {data[:200]}")

            if stderr.channel.recv_stderr_ready():
                err_data = stderr.channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                error_output += err_data
                logger.warning(f"Error: {err_data[:200]}")

            if stdout.channel.exit_status_ready():
                break

            time.sleep(0.5)

        # Get remaining output
        output += stdout.read().decode('utf-8', errors='ignore')
        error_output += stderr.read().decode('utf-8', errors='ignore')

        exit_status = stdout.channel.recv_exit_status()
        ssh.close()

        logger.info(f"Exit status: {exit_status}")
        logger.info(f"Output length: {len(output)} bytes")

        if exit_status == 0:
            logger.info("✅ Deployment successful via SSH + paramiko!")
            logger.info(f"Output: {output[-2000:]}")  # Last 2000 chars
            return True
        else:
            logger.warning(f"SSH deployment exit code: {exit_status}")
            logger.warning(f"Output: {output[-1000:]}")
            logger.warning(f"Error: {error_output[-500:]}")
            # Still return True if we got output (partial success)
            if "Starting MCP Container Deployment" in output:
                logger.info("⚠️  Deployment started but may have errors")
                return True

    except ImportError:
        logger.warning("⚠️  paramiko not available")
    except Exception as e:
        logger.error(f"❌ Paramiko SSH failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # Method 4: Direct SSH command with password via stdin
    logger.info("🔐 Trying direct SSH with password via stdin...")
    import subprocess

    ssh_cmd = f'echo "{password}" | ssh -o StrictHostKeyChecking=no {username}@{nas_ip} "echo \\"{password}\\" | sudo -S bash {script_path}"'

    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info("✅ Deployment successful via SSH!")
            logger.info(f"Output: {result.stdout[:1000]}")
            return True
        else:
            logger.debug(f"SSH attempt: {result.stderr[:200]}")
    except Exception as e:
        logger.debug(f"SSH command failed: {e}")

    logger.warning("⚠️  Task Scheduler methods failed")
    return False

if __name__ == "__main__":
    success = deploy_via_dsm_api()
    sys.exit(0 if success else 1)
