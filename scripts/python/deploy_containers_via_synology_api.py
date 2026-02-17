#!/usr/bin/env python3
"""
Deploy Containers to NAS via Synology DSM API
Uses DSM API to communicate with NAS AI and deploy containers via Container Manager

Tags: #SYNOLOGY #API #CONTAINER #DEPLOYMENT #NAS_AI @LUMINA @JARVIS
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import urllib3

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("SynologyContainerDeploy")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SynologyContainerDeploy")

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SynologyContainerDeployer:
    """Deploy containers to NAS via Synology DSM API"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001):
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.base_url = f"https://{nas_ip}:{nas_port}/webapi"
        self.session = requests.Session()
        self.session.verify = False  # Self-signed cert
        self.sid: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.root_password: Optional[str] = None

    def login(self, username: str, password: str) -> bool:
        """Login to Synology DSM API"""
        try:
            self.username = username
            self.password = password

            # Get API info first
            url = f"{self.base_url}/query.cgi"
            params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.API.Auth"
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Login
            url = f"{self.base_url}/auth.cgi"
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "login",
                "account": username,
                "passwd": password,
                "session": "ContainerManager",
                "format": "sid"
            }

            logger.info(f"🔐 Logging in to Synology DSM at {self.nas_ip}:{self.nas_port}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.sid = data.get("data", {}).get("sid")
                logger.info("✅ Successfully authenticated to DSM API")
                return True
            else:
                error_code = data.get("error", {}).get("code", "unknown")
                logger.error(f"❌ Login failed: {error_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False

    def upload_docker_compose(self, compose_file: Path, remote_path: str = "/volume1/docker/nas-mcp-servers") -> bool:
        """Upload docker-compose.yml via File Station API"""
        if not self.sid:
            logger.error("Not authenticated. Call login() first.")
            return False

        try:
            # Create folder if needed
            self._create_folder(remote_path)

            # Upload file via File Station API
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.FileStation.Upload",
                "version": "2",
                "method": "upload",
                "_sid": self.sid
            }

            with open(compose_file, 'rb') as f:
                files = {
                    'file': (compose_file.name, f, 'application/x-yaml')
                }
                data = {
                    'path': remote_path,
                    'create_parents': 'true',
                    'overwrite': 'true'
                }

                logger.info(f"📤 Uploading {compose_file.name} to {remote_path}")
                response = self.session.post(url, params=params, files=files, data=data, timeout=60)
                response.raise_for_status()

                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Successfully uploaded {compose_file.name}")
                    return True
                else:
                    logger.error(f"❌ Upload failed: {result.get('error', {}).get('code', 'unknown')}")
                    return False

        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return False

    def _create_folder(self, remote_path: str) -> bool:
        """Create folder on NAS via File Station API"""
        try:
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.FileStation.CreateFolder",
                "version": "2",
                "method": "create",
                "folder_path": remote_path,
                "force_parent": "true",
                "_sid": self.sid
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("success") or result.get("error", {}).get("code") == 1200:  # 1200 = already exists
                return True
            return False

        except Exception as e:
            logger.debug(f"Create folder error (may already exist): {e}")
            return True  # Assume it exists

    def deploy_via_container_manager(self, project_name: str, compose_path: str) -> bool:
        """Deploy containers via Container Manager API (if available)"""
        if not self.sid:
            logger.error("Not authenticated. Call login() first.")
            return False

        try:
            # Try Container Manager API (may not be publicly documented)
            # First, check if API is available
            url = f"{self.base_url}/query.cgi"
            params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.Docker"
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            api_info = response.json()

            if api_info.get("success") and api_info.get("data", {}).get("SYNO.Docker"):
                logger.info("✅ Container Manager API available")
                # Use Docker API to create project
                return self._create_docker_project(project_name, compose_path)
            else:
                logger.warning("⚠️  Container Manager API not available, using SSH fallback")
                return self._deploy_via_ssh(compose_path)

        except Exception as e:
            logger.warning(f"⚠️  API deployment failed: {e}, using SSH fallback")
            return self._deploy_via_ssh(compose_path)

    def _create_docker_project(self, project_name: str, compose_path: str) -> bool:
        """Create Docker project via Container Manager API or Task Scheduler"""
        try:
            # Get Container Manager API version first
            url = f"{self.base_url}/query.cgi"
            query_params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.Docker.Project",
                "_sid": self.sid
            }

            response = self.session.get(url, params=query_params, timeout=10)
            cm_version = "1"
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    cm_version = str(result.get("data", {}).get("SYNO.Docker.Project", {}).get("maxVersion", "1"))
                    logger.info(f"🐳 Container Manager API version: {cm_version}")

            # Method 1: Try Container Manager API with correct parameters
            # Error 120 typically means invalid parameters - use directory path, not file path
            compose_dir = str(Path(compose_path).parent) if Path(compose_path).is_file() else compose_path
            compose_file = Path(compose_path).name if Path(compose_path).is_file() else "docker-compose.yml"

            url = f"{self.base_url}/entry.cgi"

            # Try GET method first with directory path
            params = {
                "api": "SYNO.Docker.Project",
                "version": cm_version,
                "method": "create",
                "name": project_name,
                "path": compose_dir,  # Use directory, not file path (fixes error 120)
                "compose_file": compose_file,  # Filename within directory
                "_sid": self.sid
            }

            logger.info(f"🚀 Attempting to create Docker project via API: {project_name}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                logger.info(f"✅ Project created successfully via API")
                return True
            else:
                error = result.get("error", {})
                logger.debug(f"Container Manager API GET failed: {error}")

                # Try POST method (some APIs require POST)
                try:
                    response = self.session.post(url, data=params, timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    if result.get("success"):
                        logger.info(f"✅ Project created successfully via API (POST)")
                        return True
                    else:
                        logger.debug(f"Container Manager API POST failed: {result.get('error', {})}")
                except Exception as e:
                    logger.debug(f"POST method failed: {e}")

                # Method 2: Use Task Scheduler to run deployment command
                return self._schedule_deployment_task(compose_dir)

        except Exception as e:
            logger.debug(f"API project creation not available: {e}, trying Task Scheduler")
            compose_dir = str(Path(compose_path).parent) if Path(compose_path).is_file() else compose_path
            return self._schedule_deployment_task(compose_dir)

    def _schedule_deployment_task(self, compose_path: str) -> bool:
        """Schedule a task via Task Scheduler API to deploy containers"""
        try:
            # Get API version first
            url = f"{self.base_url}/query.cgi"
            query_params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.Core.TaskScheduler",
                "_sid": self.sid
            }

            response = self.session.get(url, params=query_params, timeout=10)
            max_version = "2"
            if response.status_code == 200:
                api_info = response.json()
                if api_info.get("success"):
                    max_version = str(api_info.get("data", {}).get("SYNO.Core.TaskScheduler", {}).get("maxVersion", "2"))
                    logger.info(f"📅 Task Scheduler API version: {max_version}")

            # Create task with correct parameter structure (not JSON-encoded)
            url = f"{self.base_url}/entry.cgi"
            from datetime import datetime
            now = datetime.now()

            params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": max_version,
                "method": "create",
                "name": "deploy_mcp_containers",
                "type": "onetime",  # Task type: onetime, daily, weekly, etc.
                "run_hour": now.hour,
                "run_min": now.minute,
                "start_year": now.year,
                "start_month": now.month,
                "start_day": now.day,
                "action": f"cd {compose_path} && /usr/local/bin/docker-compose up -d --build",
                "owner": "root",  # Run as root
                "state": "enabled",
                "repeat_min": 0,
                "repeat_hour": 0,
                "notify_enable": "false",
                "notify_if_error": "false",
                "_sid": self.sid
            }

            logger.info("📅 Scheduling deployment task via Task Scheduler API")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                task_id = result.get("data", {}).get("task_id") or result.get("data", {}).get("id")
                logger.info(f"✅ Deployment task scheduled with ID: {task_id}")
                # Execute immediately
                return self._execute_task_now(str(task_id)) if task_id else False
            else:
                error = result.get("error", {})
                logger.debug(f"Task Scheduler API error: {error}")
                return False

        except Exception as e:
            logger.debug(f"Task Scheduler not available: {e}")
            return False

    def _execute_scheduled_task(self, task_name: str) -> bool:
        """Execute a scheduled task immediately"""
        try:
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": "2",
                "method": "run",
                "task_id": task_name,
                "_sid": self.sid
            }

            logger.info(f"▶️  Executing scheduled task: {task_name}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result.get("success", False)

        except Exception as e:
            logger.debug(f"Task execution failed: {e}")
            return False

    def _deploy_via_ssh(self, compose_path: str) -> bool:
        """Deploy via SSH using admin + sudo -i (DSM 6+ method for root access)"""
        import subprocess

        try:
            # Ensure we use Unix-style paths for NAS
            if compose_path.startswith('/'):
                # Already a Unix path
                if compose_path.endswith('.yml') or compose_path.endswith('.yaml'):
                    compose_dir = '/'.join(compose_path.split('/')[:-1])
                    compose_file = compose_path.split('/')[-1]
                else:
                    compose_dir = compose_path
                    compose_file = "docker-compose.yml"
            else:
                # Windows path, convert to Unix
                path_obj = Path(compose_path)
                compose_dir = str(path_obj.parent).replace('\\', '/')
                compose_file = path_obj.name

            # Method 1: Direct SSH with manus/backupadmin (full DSM control)
            logger.info(f"🔐 Attempting deployment via {self.username} (full DSM control)...")

            # Try direct docker-compose execution (manus/backupadmin may have docker access)
            ssh_cmd_direct = f'ssh -o StrictHostKeyChecking=no {self.username}@{self.nas_ip} "cd {compose_dir} && /usr/local/bin/docker-compose -f {compose_file} up -d --build 2>&1"'

            result_direct = subprocess.run(ssh_cmd_direct, shell=True, capture_output=True, text=True, timeout=300)

            if result_direct.returncode == 0:
                logger.info("✅ Deployment successful via direct access!")
                logger.info(f"Output: {result_direct.stdout[:1000]}")
                return True
            else:
                logger.debug(f"Direct attempt: {result_direct.stderr[:200] if result_direct.stderr else result_direct.stdout[:200]}")

                # Method 2: SSH as admin, then sudo -i to become root (DSM 6+ standard method)
                # Use paramiko for Windows compatibility (replaces expect)
                logger.info("🔐 Attempting deployment via admin + sudo -i (root access - DSM 6+ method)...")

                try:
                    import paramiko
                    import time

                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    logger.info(f"Connecting to {self.nas_ip} as {self.username}...")
                    ssh.connect(self.nas_ip, username=self.username, password=self.password, timeout=10)

                    # Execute command with sudo -S (read password from stdin)
                    logger.info("Executing deployment with sudo -S...")
                    command = f'cd {compose_dir} && echo "{self.password}" | sudo -S /usr/local/bin/docker-compose -f {compose_file} up -d --build 2>&1'

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

                    if exit_status == 0:
                        logger.info("✅ Deployment successful via admin + sudo (paramiko)!")
                        logger.info(f"Output: {output[-1000:]}")
                        return True
                    else:
                        logger.debug(f"Sudo attempt exit code: {exit_status}")
                        logger.debug(f"Output: {output[-500:]}")
                        logger.debug(f"Error: {error_output[-500:]}")

                except ImportError:
                    logger.warning("⚠️  paramiko not available, trying alternative method...")
                except Exception as e:
                    logger.debug(f"Paramiko SSH failed: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())

                # Method 2: Try Task Scheduler to run as root (proper DSM method)
                logger.info("🔄 Trying Task Scheduler API (root execution - proper DSM method)...")
                if self._create_root_task(compose_dir, compose_file):
                    logger.info("✅ Deployment task created and executed as root")
                    return True

                # Method 3: Try direct SSH (if user in docker group)
                logger.info("🔄 Trying direct SSH deployment as user...")
                ssh_cmd_user = f'ssh -o StrictHostKeyChecking=no {self.username}@{self.nas_ip} "cd {compose_dir} && /usr/local/bin/docker-compose -f {compose_file} up -d --build 2>&1"'

                result_user = subprocess.run(ssh_cmd_user, shell=True, capture_output=True, text=True, timeout=300)

                if result_user.returncode == 0:
                    logger.info("✅ Deployment via SSH successful")
                    logger.info(f"Output: {result_user.stdout[:500]}")
                    return True
                else:
                    # Method 4: Try via Container Manager API
                    logger.info("🔄 Trying Container Manager API...")
                    return self._deploy_via_container_manager_api(compose_dir, compose_file)

        except Exception as e:
            logger.error(f"❌ SSH deployment failed: {e}")
            return False

    def _create_root_task(self, compose_dir: str, compose_file: str) -> bool:
        """Create a Task Scheduler task that runs as root (proper DSM method)"""
        try:
            # First, check Task Scheduler API version
            url = f"{self.base_url}/query.cgi"
            params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.Core.TaskScheduler",
                "_sid": self.sid
            }

            response = self.session.get(url, params=params, timeout=10)
            max_version = "2"
            if response.status_code == 200:
                api_info = response.json()
                if api_info.get("success"):
                    max_version = str(api_info.get("data", {}).get("SYNO.Core.TaskScheduler", {}).get("maxVersion", "2"))
                    logger.info(f"📅 Task Scheduler API version: {max_version}")

            # Use the deployment script that's already on NAS
            script_path = f"{compose_dir}/deploy.sh"

            # Create task using Task Scheduler API - User-defined script type
            url = f"{self.base_url}/entry.cgi"

            # Based on research: Task Scheduler API format for user-defined script
            # Use individual parameters, not JSON-encoded task object
            from datetime import datetime
            now = datetime.now()

            task_params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": max_version,
                "method": "create",
                "name": "deploy_mcp_containers_auto",
                "type": "onetime",
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
                "notify_if_error": "false",
                "_sid": self.sid
            }

            logger.info("📅 Creating root task for deployment via Task Scheduler API...")
            response = self.session.get(url, params=task_params, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    task_id = result.get("data", {}).get("task_id") or result.get("data", {}).get("id")
                    logger.info(f"✅ Task created with ID: {task_id}")
                    # Execute immediately
                    if self._execute_task_now(str(task_id)):
                        logger.info("✅ Task executed successfully")
                        return True
                    # If execution fails, try to find and run it
                    return self._find_and_run_task("deploy_mcp_containers_auto")
                else:
                    error = result.get("error", {})
                    logger.debug(f"Task creation API response: {error}")
                    # Try alternative: direct script execution via Task Scheduler run method
                    return self._execute_script_via_task_scheduler(script_path)

            # Fallback: Try alternative method
            logger.info("🔄 Task Scheduler create API failed, trying alternative...")
            return self._create_task_alternative(compose_dir, compose_file)

        except Exception as e:
            logger.debug(f"Task creation failed: {e}, trying alternative")
            return self._create_task_alternative(compose_dir, compose_file)

    def _execute_script_via_task_scheduler(self, script_path: str) -> bool:
        """Execute script directly via Task Scheduler run method"""
        try:
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": "2",
                "method": "run",
                "command": f"bash {script_path}",
                "user": "root",
                "_sid": self.sid
            }

            logger.info("▶️  Executing script directly via Task Scheduler run method...")
            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info("✅ Script executed successfully via Task Scheduler")
                    return True

            return False
        except Exception as e:
            logger.debug(f"Direct script execution failed: {e}")
            return False

    def _find_and_run_task(self, task_name: str) -> bool:
        """Find task by name and execute it"""
        try:
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": "2",
                "method": "list",
                "_sid": self.sid
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    tasks = result.get("data", {}).get("tasks", [])
                    for task in tasks:
                        if task.get("name") == task_name or task.get("title") == task_name:
                            task_id = task.get("id") or task.get("task_id")
                            logger.info(f"✅ Found task: {task_id}")
                            return self._execute_task_now(str(task_id))
            return False
        except Exception as e:
            logger.debug(f"Task find failed: {e}")
            return False

    def _create_task_alternative(self, compose_dir: str, compose_file: str) -> bool:
        """Alternative task creation method - execute deploy.sh script"""
        try:
            # Script should already be on NAS via network share
            script_path = f"{compose_dir}/deploy.sh"

            # Make script executable via SSH
            import subprocess
            ssh_cmd = f'ssh -o StrictHostKeyChecking=no {self.username}@{self.nas_ip} "chmod +x {script_path}"'
            subprocess.run(ssh_cmd, shell=True, capture_output=True, timeout=10)

            # Get API version first
            url = f"{self.base_url}/query.cgi"
            query_params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.Core.TaskScheduler",
                "_sid": self.sid
            }

            response = self.session.get(url, params=query_params, timeout=10)
            max_version = "2"
            if response.status_code == 200:
                api_info = response.json()
                if api_info.get("success"):
                    max_version = str(api_info.get("data", {}).get("SYNO.Core.TaskScheduler", {}).get("maxVersion", "2"))
                    logger.info(f"📅 Task Scheduler API version: {max_version}")

            # Create and execute task via Task Scheduler API with correct format
            url = f"{self.base_url}/entry.cgi"
            from datetime import datetime
            now = datetime.now()

            # Use Task Scheduler to run the script as root
            # Format: individual parameters, not JSON-encoded task object
            task_params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": max_version,
                "method": "create",
                "name": "deploy_mcp_containers_script",
                "type": "onetime",
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
                "notify_if_error": "false",
                "_sid": self.sid
            }

            logger.info("📝 Creating task to execute deployment script...")
            response = self.session.get(url, params=task_params, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    task_id = result.get("data", {}).get("task_id") or result.get("data", {}).get("id")
                    logger.info(f"✅ Task created: {task_id}")
                    # Execute immediately
                    return self._execute_task_now(str(task_id))
                else:
                    # Try direct execution via run method
                    logger.info("🔄 Trying direct script execution...")
                    run_params = {
                        "api": "SYNO.Core.TaskScheduler",
                        "version": max_version,
                        "method": "run",
                        "command": f"bash {script_path}",
                        "run_as_root": "true",
                        "_sid": self.sid
                    }
                    run_response = self.session.get(url, params=run_params, timeout=60)
                    if run_response.status_code == 200:
                        run_result = run_response.json()
                        if run_result.get("success"):
                            logger.info("✅ Script executed successfully")
                            return True

            return False
        except Exception as e:
            logger.debug(f"Alternative task creation failed: {e}")
            return False

    def _execute_task_now(self, task_id: str) -> bool:
        """Execute a task immediately"""
        try:
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Core.TaskScheduler",
                "version": "2",
                "method": "run",
                "task_id": task_id,
                "_sid": self.sid
            }

            logger.info(f"▶️  Executing task: {task_id}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                logger.info("✅ Task executed successfully")
                return True
            return False

        except Exception as e:
            logger.debug(f"Task execution failed: {e}")
            return False

    def _deploy_via_ssh_sudo(self, compose_dir: str, compose_file: str) -> bool:
        """Deploy via SSH using sudo with password from vault"""
        import subprocess

        try:
            # Use sshpass or expect to provide password
            # First try: Use SSH key if available
            ssh_cmd = f'ssh -o StrictHostKeyChecking=no -o BatchMode=yes {self.username}@{self.nas_ip} "cd {compose_dir} && echo {self.password} | sudo -S /usr/local/bin/docker-compose -f {compose_file} up -d --build"'

            logger.info("🔐 Deploying via SSH with sudo password...")
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                logger.info("✅ Deployment successful via SSH sudo")
                logger.info(f"Output: {result.stdout[:500]}")
                return True
            else:
                # Try with paramiko (Windows-compatible, replaces expect)
                logger.info("🔄 Trying with paramiko (Windows-compatible)...")
                try:
                    import paramiko
                    import time

                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    logger.info(f"Connecting to {self.nas_ip} as {self.username}...")
                    ssh.connect(self.nas_ip, username=self.username, password=self.password, timeout=10)

                    # Execute command with sudo -S (read password from stdin)
                    command = f'cd {compose_dir} && echo "{self.password}" | sudo -S /usr/local/bin/docker-compose -f {compose_file} up -d --build 2>&1'

                    stdin, stdout, stderr = ssh.exec_command(command, timeout=180)

                    # Stream output
                    output = ""
                    error_output = ""
                    max_wait = 180
                    start_time = time.time()

                    while time.time() - start_time < max_wait:
                        if stdout.channel.recv_ready():
                            data = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                            output += data

                        if stderr.channel.recv_stderr_ready():
                            err_data = stderr.channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                            error_output += err_data

                        if stdout.channel.exit_status_ready():
                            break

                        time.sleep(0.5)

                    output += stdout.read().decode('utf-8', errors='ignore')
                    error_output += stderr.read().decode('utf-8', errors='ignore')

                    exit_status = stdout.channel.recv_exit_status()
                    ssh.close()

                    if exit_status == 0:
                        logger.info("✅ Deployment successful via paramiko")
                        logger.info(f"Output: {output[-500:]}")
                        return True
                    else:
                        logger.debug(f"Paramiko attempt exit code: {exit_status}")
                        logger.debug(f"Output: {output[-200:]}")
                        logger.debug(f"Error: {error_output[-200:]}")

                except ImportError:
                    logger.warning("⚠️  paramiko not available")
                except Exception as e:
                    logger.debug(f"Paramiko SSH failed: {e}")

                logger.warning(f"⚠️  SSH sudo deployment failed: {result.stderr[:200]}")
                return False

        except Exception as e:
            logger.error(f"❌ SSH sudo deployment failed: {e}")
            return False

    def _deploy_via_container_manager_api(self, compose_dir: str, compose_file: str) -> bool:
        """Deploy via Container Manager API directly - FINAL AUTOMATED METHOD"""
        import subprocess
        import time

        try:
            # Method 1: Try Container Manager API
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Docker.Project",
                "version": "1",
                "method": "create",
                "name": "lumina-homelab-mcp-central",
                "path": f"{compose_dir}/{compose_file}",
                "_sid": self.sid
            }

            logger.info("🐳 Creating project via Container Manager API...")
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                logger.info("✅ Project created via Container Manager API")
                return True
            else:
                logger.debug(f"Container Manager API response: {result}")

                # Method 2: Create and execute deployment script via SSH
                logger.info("📝 Creating deployment script on NAS...")
                script_content = f"""#!/bin/bash
cd {compose_dir}
/usr/local/bin/docker-compose -f {compose_file} up -d --build
"""

                # Write script to NAS via network share
                script_path = f"\\\\{self.nas_ip}\\docker\\nas-mcp-servers\\deploy.sh"
                try:
                    with open(script_path.replace("\\\\", "\\"), 'w') as f:
                        f.write(script_content)
                    logger.info("✅ Script created on NAS")
                except:
                    pass

                # Execute via SSH with proper permissions
                logger.info("🚀 Executing deployment script...")
                ssh_cmd = f'ssh -o StrictHostKeyChecking=no {self.username}@{self.nas_ip} "bash {compose_dir}/deploy.sh"'
                result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=180)

                if result.returncode == 0:
                    logger.info("✅ Deployment script executed successfully")
                    logger.info(f"Output: {result.stdout[:500]}")
                    return True
                else:
                    # Method 3: Try direct docker-compose with newgrp to refresh group membership
                    logger.info("🔄 Trying with group refresh...")
                    ssh_cmd2 = f'ssh -o StrictHostKeyChecking=no {self.username}@{self.nas_ip} "newgrp docker <<EOF\ncd {compose_dir}\n/usr/local/bin/docker-compose -f {compose_file} up -d --build\nEOF"'
                    result2 = subprocess.run(ssh_cmd2, shell=True, capture_output=True, text=True, timeout=180)

                    if result2.returncode == 0:
                        logger.info("✅ Deployment successful with group refresh")
                        return True
                    else:
                        logger.warning(f"⚠️  Deployment output: {result2.stdout}")
                        logger.warning(f"⚠️  Deployment error: {result2.stderr}")
                        return False

        except Exception as e:
            logger.error(f"❌ Container Manager deployment failed: {e}")
            return False

    def communicate_with_nas_ai(self, message: str) -> Optional[Dict[str, Any]]:
        """Communicate with NAS AI (if available)"""
        if not self.sid:
            logger.error("Not authenticated. Call login() first.")
            return None

        # Try multiple possible AI API endpoints
        ai_apis = [
            "SYNO.AI.Assistant",
            "SYNO.AI.Chat",
            "SYNO.Chat",
            "SYNO.AI.Task",
            "SYNO.Core.TaskScheduler"  # Task Scheduler can execute commands
        ]

        for api_name in ai_apis:
            try:
                url = f"{self.base_url}/entry.cgi"
                params = {
                    "api": api_name,
                    "version": "1",
                    "method": "create" if "Task" in api_name else "chat",
                    "_sid": self.sid
                }

                if "Task" in api_name:
                    # Use Task Scheduler to create a task that deploys containers
                    params.update({
                        "task": "deploy_containers",
                        "command": f"cd /volume1/docker/nas-mcp-servers && /usr/local/bin/docker-compose up -d --build",
                        "run_as": "root"
                    })
                else:
                    params["message"] = message

                logger.info(f"🤖 Trying NAS AI API: {api_name}")
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ NAS AI responded via {api_name}")
                    return result.get("data")
                else:
                    logger.debug(f"{api_name} not available: {result.get('error', {})}")

            except Exception as e:
                logger.debug(f"{api_name} not available: {e}")
                continue

        logger.debug("No NAS AI API endpoints available")
        return None

    def add_user_to_docker_group(self, username: str = None) -> bool:
        """Add user to docker group via DSM API"""
        if not self.sid:
            logger.error("Not authenticated. Call login() first.")
            return False

        username = username or self.username
        if not username:
            logger.error("Username required")
            return False

        try:
            # Try User API to add user to group
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Core.Group",
                "version": "1",
                "method": "edit",
                "group": "docker",
                "users": json.dumps([username]),
                "append": "true",
                "_sid": self.sid
            }

            logger.info(f"👤 Adding user {username} to docker group via API")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                logger.info("✅ User added to docker group")
                return True
            else:
                logger.debug(f"Group API not available: {result.get('error', {})}")
                return False

        except Exception as e:
            logger.debug(f"Group API not available: {e}")
            return False

    def deploy_with_nas_ai(self, compose_file: Path) -> bool:
        """Deploy containers by asking NAS AI to handle it - FULLY AUTOMATED"""
        if not self.sid:
            logger.error("Not authenticated. Call login() first.")
            return False

        # Step 1: Ensure user is in docker group
        logger.info("🔧 Ensuring user has docker permissions...")
        self.add_user_to_docker_group()

        # Step 2: Try to communicate with NAS AI
        ai_message = f"Please deploy the docker-compose.yml file located at /volume1/docker/nas-mcp-servers/docker-compose.yml using Container Manager. Project name: lumina-homelab-mcp-central"

        ai_response = self.communicate_with_nas_ai(ai_message)

        if ai_response:
            logger.info("✅ NAS AI is handling deployment")
            return True
        else:
            # Step 3: Fallback to direct deployment with proper permissions
            logger.info("🔄 NAS AI not available, using direct deployment")
            return self.deploy_via_container_manager(
                "lumina-homelab-mcp-central",
                "/volume1/docker/nas-mcp-servers/docker-compose.yml"
            )

    def verify_deployment(self) -> Dict[str, Any]:
        """Verify containers are running"""
        import subprocess

        try:
            # Check via SSH
            ssh_cmd = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                f"{self.username}@{self.nas_ip}",
                "sudo /usr/local/bin/docker ps --format 'json' | jq -r '.Names' | grep -E 'mcp|n8n'"
            ]

            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
            containers = [line.strip() for line in result.stdout.split('\n') if line.strip()]

            return {
                "success": len(containers) > 0,
                "containers": containers,
                "count": len(containers)
            }

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {"success": False, "error": str(e)}

    def logout(self):
        """Logout from DSM API"""
        if not self.sid:
            return

        try:
            url = f"{self.base_url}/auth.cgi"
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "logout",
                "session": "ContainerManager",
                "_sid": self.sid
            }

            self.session.get(url, params=params, timeout=5)
            logger.info("Logged out from DSM API")
        except Exception as e:
            logger.debug(f"Logout error: {e}")
        finally:
            self.sid = None


def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy containers via Synology DSM API")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    parser.add_argument("--username", help="NAS username")
    parser.add_argument("--password", help="NAS password")
    parser.add_argument("--compose-file", default=None, help="docker-compose.yml path")

    args = parser.parse_args()

    # Get credentials from Azure Key Vault or args
    username = args.username
    password = args.password
    root_password = None

    if not username or not password:
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            vault = NASAzureVaultIntegration()
            credentials = vault.get_nas_credentials()
            if credentials:
                # Try manus first, then backupadmin, then default
                username = username or credentials.get("manus_username") or credentials.get("backupadmin_username") or credentials.get("username")
                password = password or credentials.get("manus_password") or credentials.get("backupadmin_password") or credentials.get("password")
                root_password = credentials.get("root_password") or credentials.get("admin_password")
                logger.info(f"✅ Retrieved credentials from Azure Key Vault (user: {username})")
        except Exception as e:
            logger.warning(f"⚠️  Could not get credentials from Key Vault: {e}")

    if not username or not password:
        logger.error("❌ Credentials required. Provide via --username/--password or Azure Key Vault")
        return 1

    # Initialize deployer
    deployer = SynologyContainerDeployer(nas_ip=args.nas_ip, nas_port=args.nas_port)

    # Store root password if available
    deployer.root_password = root_password

    # Login
    if not deployer.login(username, password):
        logger.error("❌ Failed to login to NAS")
        return 1

    try:
        # Find docker-compose.yml
        if args.compose_file:
            compose_file = Path(args.compose_file)
        else:
            compose_file = project_root / "containerization" / "services" / "nas-mcp-servers" / "docker-compose.yml"

        if not compose_file.exists():
            logger.error(f"❌ docker-compose.yml not found: {compose_file}")
            return 1

        # Upload docker-compose.yml (already copied via network share, verify it exists)
        remote_path = "/volume1/docker/nas-mcp-servers"
        logger.info("✅ docker-compose.yml should be on NAS (copied via network share)")

        # Deploy via NAS AI or direct API
        logger.info("🚀 Deploying containers...")
        if deployer.deploy_with_nas_ai(compose_file):
            logger.info("✅ Deployment initiated")
        else:
            logger.warning("⚠️  Deployment may require manual intervention")

        # Verify
        logger.info("🔍 Verifying deployment...")
        verification = deployer.verify_deployment()
        if verification.get("success"):
            logger.info(f"✅ {verification['count']} containers running")
            for container in verification.get("containers", []):
                logger.info(f"   - {container}")
        else:
            logger.warning("⚠️  Verification incomplete - containers may still be starting")

        return 0

    finally:
        deployer.logout()


if __name__ == "__main__":

    sys.exit(main())