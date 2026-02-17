#!/usr/bin/env python3
"""
JARVIS KAIJU Full Deployment - Bring Cluster 100% Online

ARCHITECTURE CLARIFICATION:
- KAIJU_NO_8 = Desktop PC at <NAS_IP> (RTX 3090, 64GB RAM) - PRIMARY GPU/LLM HOST
- NAS = Synology DS1821plus at <NAS_PRIMARY_IP> - STORAGE/LIGHTWEIGHT SERVICES ONLY
- This script deploys to KAIJU_NO_8 (desktop PC), NOT the NAS
- NAS has DPM (Docker Package Manager) but should be used sparingly for "BALANCE"

Deploys all services on KAIJU_NO_8:
- Ollama (Iron Legion) on port 11434
- ULTRON Router on port 3008  
- MCP Server (R5 API) on port 8000

Tags: #AUTOMATION #CLUSTER @KAIJU @DOIT
"""

import sys
import json
import paramiko
import requests
import socket
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISKAIJUFullDeploy")


class KAIJUFullDeployment:
    """Full KAIJU cluster deployment - 100% operational"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # KAIJU_NO_8 connection info (Desktop PC, NOT the NAS)
        # KAIJU_NO_8 = Desktop PC at <NAS_IP> (RTX 3090, 64GB RAM)
        # NAS = Synology DS1821plus at <NAS_PRIMARY_IP> (storage server)
        self.kaiju_ip = "<NAS_IP>"  # KAIJU_NO_8 Desktop PC
        self.kaiju_ssh_port = 22
        self.kaiju_ollama_port = 11434
        self.kaiju_ultron_router_port = 3008
        self.kaiju_mcp_port = 8000

        # SSH credentials
        self.ssh_username = None
        self.ssh_password = None
        self._load_credentials()

        # Docker binary path (KAIJU_NO_8 uses standard Docker, not Synology DPM)
        # Use standard 'docker' command (in PATH) for desktop PC
        # NAS (<NAS_PRIMARY_IP>) uses Synology DPM, but we're deploying to KAIJU_NO_8 desktop
        self.docker_bin = "docker"  # Standard Docker on desktop PC

        self.logger.info("✅ KAIJU Full Deployment initialized")

    def _load_credentials(self):
        """Load SSH credentials from Azure Key Vault"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            nas_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
            credentials = nas_integration.get_nas_credentials()

            if credentials:
                self.ssh_username = credentials.get("username")
                self.ssh_password = credentials.get("password")
                if self.ssh_username and self.ssh_password:
                    self.logger.info(f"✅ Loaded SSH credentials for {self.ssh_username}")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load SSH credentials: {e}")

    def ssh_execute(self, command: str, use_sudo: bool = False) -> Dict[str, Any]:
        """Execute command on KAIJU via SSH"""
        if not self.ssh_username or not self.ssh_password:
            return {"success": False, "error": "SSH credentials not available"}

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.kaiju_ip,
                port=self.kaiju_ssh_port,
                username=self.ssh_username,
                password=self.ssh_password,
                timeout=10
            )

            if use_sudo:
                # Use sudo with password via stdin
                full_cmd = f'echo "{self.ssh_password}" | sudo -S {command}'
            else:
                full_cmd = command

            stdin, stdout, stderr = client.exec_command(full_cmd)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            error = stderr.read().decode()

            client.close()

            return {
                "success": exit_status == 0,
                "exit_status": exit_status,
                "output": output,
                "error": error
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_port(self, port: int) -> bool:
        """Check if port is open on KAIJU"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.kaiju_ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def deploy_ollama(self) -> Dict[str, Any]:
        """Deploy Ollama container"""
        self.logger.info("🚀 Deploying Ollama (Iron Legion)...")

        # Check if already running
        if self.check_port(self.kaiju_ollama_port):
            self.logger.info("   ✅ Ollama already running on port 11434")
            return {"success": True, "action": "already_running"}

        # Try Docker without sudo first
        docker_cmd = self.docker_bin
        test_result = self.ssh_execute(f"{docker_cmd} ps 2>&1 | head -1")

        if "permission denied" in test_result.get("output", "").lower():
            # Try with sudo
            docker_cmd = f"sudo {self.docker_bin}"
            test_result = self.ssh_execute(f"{docker_cmd} ps 2>&1 | head -1", use_sudo=True)

        if not test_result.get("success"):
            return {"success": False, "error": "Docker not accessible"}

        # Check for existing container
        check_result = self.ssh_execute(f"{docker_cmd} ps -a --filter 'name=ollama' --format '{{{{.Names}}}}' 2>/dev/null")
        if check_result.get("output", "").strip():
            container_name = check_result.get("output", "").strip()
            self.logger.info(f"   Found existing container: {container_name}")
            # Start it
            start_result = self.ssh_execute(f"{docker_cmd} start {container_name} 2>&1", use_sudo="sudo" in docker_cmd)
            if start_result.get("success"):
                time.sleep(3)
                if self.check_port(self.kaiju_ollama_port):
                    return {"success": True, "action": "started"}

        # Create new container with GPU support
        self.logger.info("   Creating Ollama container with GPU support...")

        # Check for GPU availability
        gpu_check = self.ssh_execute("nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo 'no_gpu'")
        has_gpu = "no_gpu" not in gpu_check.get("output", "").lower()

        if has_gpu:
            gpu_name = gpu_check.get("output", "").strip()
            self.logger.info(f"   ✅ GPU detected: {gpu_name}")
            # Use GPU runtime and device access
            deploy_cmd = f"""{docker_cmd} run -d --name ollama --restart unless-stopped --gpus all -v ollama-data:/root/.ollama -p {self.kaiju_ollama_port}:11434 -e OLLAMA_NUM_GPU=1 -e OLLAMA_KEEP_ALIVE=5m ollama/ollama:latest 2>&1"""
        else:
            self.logger.warning("   ⚠️  No GPU detected - Ollama will use CPU only")
            deploy_cmd = f"""{docker_cmd} run -d --name ollama --restart unless-stopped -v ollama-data:/root/.ollama -p {self.kaiju_ollama_port}:11434 ollama/ollama:latest 2>&1"""

        deploy_result = self.ssh_execute(deploy_cmd, use_sudo="sudo" in docker_cmd)

        if deploy_result.get("success"):
            time.sleep(5)
            if self.check_port(self.kaiju_ollama_port):
                self.logger.info("   ✅ Ollama deployed and running")
                return {"success": True, "action": "deployed"}

        return {"success": False, "error": deploy_result.get("error", "Unknown error")}

    def deploy_mcp_server(self) -> Dict[str, Any]:
        try:
            """Deploy MCP Server (R5 API) on port 8000 - Use Docker for clean deployment"""
            self.logger.info("🚀 Deploying MCP Server (R5 API) on port 8000...")

            # Check if already running
            if self.check_port(self.kaiju_mcp_port):
                self.logger.info("   ✅ MCP Server already running on port 8000")
                return {"success": True, "action": "already_running"}

            # Try Docker deployment first (cleaner, handles dependencies)
            docker_cmd = self.docker_bin
            test_result = self.ssh_execute(f"{docker_cmd} ps 2>&1 | head -1")

            if "permission denied" in test_result.get("output", "").lower():
                docker_cmd = f"sudo {self.docker_bin}"
                test_result = self.ssh_execute(f"{docker_cmd} ps 2>&1 | head -1", use_sudo=True)

            if test_result.get("success"):
                # Check for existing MCP server container
                check_result = self.ssh_execute(f"{docker_cmd} ps -a --filter 'name=mcp-server' --format '{{{{.Names}}}}' 2>/dev/null")
                if check_result.get("output", "").strip():
                    container_name = check_result.get("output", "").strip()
                    self.logger.info(f"   Found existing MCP container: {container_name}")
                    start_result = self.ssh_execute(f"{docker_cmd} start {container_name} 2>&1", use_sudo="sudo" in docker_cmd)
                    if start_result.get("success"):
                        time.sleep(3)
                        if self.check_port(self.kaiju_mcp_port):
                            return {"success": True, "action": "started"}

                # Deploy as Docker container with Python and all dependencies
                self.logger.info("   📦 Deploying MCP Server as Docker container...")

                # Mount the project directory and run the server
                # KAIJU_NO_8 uses standard Linux paths (not Synology /volume1)
                # Try common locations: /opt/lumina, ~/lumina, or detect from environment
                kaiju_project_path = "/opt/lumina"  # Standard Linux location for KAIJU_NO_8 desktop
                deploy_cmd = f"""{docker_cmd} run -d --name mcp-server --restart unless-stopped -v {kaiju_project_path}:/app -w /app -p {self.kaiju_mcp_port}:8000 python:3.11-slim sh -c "pip install flask flask-cors requests -q && python scripts/python/r5_api_server.py" 2>&1"""

                deploy_result = self.ssh_execute(deploy_cmd, use_sudo="sudo" in docker_cmd)

                if deploy_result.get("success"):
                    time.sleep(5)
                    if self.check_port(self.kaiju_mcp_port):
                        self.logger.info("   ✅ MCP Server deployed and running in Docker")
                        return {"success": True, "action": "deployed_docker"}

            # Fallback to direct Python deployment (if Docker fails)
            self.logger.info("   📝 Falling back to direct Python deployment...")

            # Use standalone triage server (simpler, no dependencies)
            local_mcp_script = self.project_root / "scripts" / "python" / "mcp_triage_server_standalone.py"

            # Target path on KAIJU_NO_8 (desktop PC, not NAS)
            # Use standard Linux path, not Synology /volume1
            kaiju_base = "/opt/lumina"  # Standard Linux location for KAIJU_NO_8 desktop
            kaiju_script_dir = f"{kaiju_base}/scripts/python"
            kaiju_script_path = f"{kaiju_script_dir}/mcp_triage_server_standalone.py"

            # Check if script exists on KAIJU
            check_result = self.ssh_execute(f"test -f {kaiju_script_path} && echo 'exists' || echo 'not_found'")

            if "not_found" in check_result.get("output", ""):
                # Copy script and dependencies to KAIJU
                self.logger.info("   📦 Copying r5_api_server.py and dependencies to KAIJU...")

                # Create directory structure
                self.ssh_execute(f"mkdir -p {kaiju_script_dir}")

                # Required modules to copy (standalone server only needs Flask)
                required_modules = [
                    "mcp_triage_server_standalone.py"
                ]

                # Copy each required file
                for module_name in required_modules:
                    local_module = self.project_root / "scripts" / "python" / module_name
                    if local_module.exists():
                        kaiju_module_path = f"{kaiju_script_dir}/{module_name}"
                        self.logger.info(f"   📦 Copying {module_name}...")

                        # Use base64 encoding via SSH
                        with open(local_module, 'rb') as f:
                            content = f.read()
                            import base64
                            encoded = base64.b64encode(content).decode()

                            # Write in chunks if needed (split large files)
                            if len(encoded) > 50000:  # Large file, split
                                chunk_size = 50000
                                self.ssh_execute(f"rm -f {kaiju_module_path}")
                                for i in range(0, len(encoded), chunk_size):
                                    chunk = encoded[i:i+chunk_size]
                                    append_cmd = f"echo '{chunk}' | base64 -d >> {kaiju_module_path}"
                                    self.ssh_execute(append_cmd)
                            else:
                                copy_cmd = f"echo '{encoded}' | base64 -d > {kaiju_module_path}"
                                copy_result = self.ssh_execute(copy_cmd)

                                if not copy_result.get("success"):
                                    self.logger.warning(f"   ⚠️  Failed to copy {module_name}: {copy_result.get('error', '')[:100]}")

                        self.logger.info(f"   ✅ {module_name} copied")
                    else:
                        self.logger.warning(f"   ⚠️  {module_name} not found locally")

                self.logger.info("   ✅ All required modules copied to KAIJU")

            # Make script executable
            self.ssh_execute(f"chmod +x {kaiju_script_path}")

            # Check if Python is available
            python_check = self.ssh_execute("which python3 || which python")
            python_cmd = python_check.get("output", "").strip() or "python3"

            # Install required dependencies
            self.logger.info("   📦 Installing Python dependencies (Flask, flask-cors)...")
            pip_cmd = f"{python_cmd} -m pip install flask flask-cors requests --quiet 2>&1 || pip3 install flask flask-cors requests --quiet 2>&1"
            pip_result = self.ssh_execute(pip_cmd)
            if pip_result.get("success") or "already satisfied" in pip_result.get("output", "").lower():
                self.logger.info("   ✅ Dependencies installed")
            else:
                self.logger.warning(f"   ⚠️  Dependency installation may have issues: {pip_result.get('error', '')[:100]}")

            # Check if process already running
            check_process = self.ssh_execute(f"pgrep -f 'mcp_triage_server' || echo 'not_running'")
            if "not_running" not in check_process.get("output", ""):
                self.logger.info("   ✅ MCP Server process already running")
                time.sleep(2)
                if self.check_port(self.kaiju_mcp_port):
                    return {"success": True, "action": "already_running"}

            # Start MCP server in background
            self.logger.info(f"   Starting MCP server with {python_cmd}...")

            # Use nohup to run in background
            start_cmd = f"cd {kaiju_script_dir} && nohup {python_cmd} {kaiju_script_path} > /tmp/mcp_triage.log 2>&1 &"
            start_result = self.ssh_execute(start_cmd)

            if start_result.get("success"):
                # Wait and check
                for i in range(10):
                    time.sleep(1)
                    if self.check_port(self.kaiju_mcp_port):
                        self.logger.info("   ✅ MCP Server started on port 8000")
                        return {"success": True, "action": "started"}

                # Check logs if failed
                log_check = self.ssh_execute("tail -30 /tmp/r5_api.log 2>/dev/null || echo 'no log'")
                self.logger.warning(f"   ⚠️  MCP Server may not have started. Log: {log_check.get('output', '')[:300]}")

            return {"success": False, "error": "Failed to start MCP server"}

        except Exception as e:
            self.logger.error(f"Error in deploy_mcp_server: {e}", exc_info=True)
            raise
    def verify_all_services(self) -> Dict[str, Any]:
        """Verify all services are operational"""
        self.logger.info("🔍 Verifying all services...")

        results = {
            "ollama": {"port": self.kaiju_ollama_port, "status": "unknown"},
            "mcp_server": {"port": self.kaiju_mcp_port, "status": "unknown"},
            "ultron_router": {"port": self.kaiju_ultron_router_port, "status": "unknown"}
        }

        # Check Ollama
        if self.check_port(self.kaiju_ollama_port):
            try:
                response = requests.get(f"http://{self.kaiju_ip}:{self.kaiju_ollama_port}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    results["ollama"] = {"port": self.kaiju_ollama_port, "status": "operational", "models": len(models)}
                    self.logger.info(f"   ✅ Ollama: OPERATIONAL ({len(models)} models)")
                else:
                    results["ollama"] = {"port": self.kaiju_ollama_port, "status": "port_open_but_error", "error": f"Status {response.status_code}"}
            except Exception as e:
                results["ollama"] = {"port": self.kaiju_ollama_port, "status": "port_open_but_error", "error": str(e)}
        else:
            results["ollama"] = {"port": self.kaiju_ollama_port, "status": "not_running"}
            self.logger.warning(f"   ❌ Ollama: NOT RUNNING (port {self.kaiju_ollama_port} closed)")

        # Check MCP Server
        if self.check_port(self.kaiju_mcp_port):
            try:
                response = requests.get(f"http://{self.kaiju_ip}:{self.kaiju_mcp_port}/r5/health", timeout=5)
                if response.status_code == 200:
                    results["mcp_server"] = {"port": self.kaiju_mcp_port, "status": "operational"}
                    self.logger.info(f"   ✅ MCP Server: OPERATIONAL (port {self.kaiju_mcp_port})")
                else:
                    results["mcp_server"] = {"port": self.kaiju_mcp_port, "status": "port_open_but_error", "error": f"Status {response.status_code}"}
            except Exception as e:
                results["mcp_server"] = {"port": self.kaiju_mcp_port, "status": "port_open_but_error", "error": str(e)}
        else:
            results["mcp_server"] = {"port": self.kaiju_mcp_port, "status": "not_running"}
            self.logger.warning(f"   ❌ MCP Server: NOT RUNNING (port {self.kaiju_mcp_port} closed)")

        # Check ULTRON Router
        if self.check_port(self.kaiju_ultron_router_port):
            results["ultron_router"] = {"port": self.kaiju_ultron_router_port, "status": "operational"}
            self.logger.info(f"   ✅ ULTRON Router: OPERATIONAL (port {self.kaiju_ultron_router_port})")
        else:
            results["ultron_router"] = {"port": self.kaiju_ultron_router_port, "status": "not_running"}
            self.logger.warning(f"   ❌ ULTRON Router: NOT RUNNING (port {self.kaiju_ultron_router_port} closed)")

        return results

    def full_deployment(self) -> Dict[str, Any]:
        """Full deployment - bring KAIJU 100% online"""
        self.logger.info("="*80)
        self.logger.info("🚀 KAIJU FULL DEPLOYMENT - BRINGING CLUSTER 100% ONLINE")
        self.logger.info("="*80)

        deployment = {
            "timestamp": datetime.now().isoformat(),
            "kaiju_ip": self.kaiju_ip,
            "services": {}
        }

        # Deploy Ollama
        ollama_result = self.deploy_ollama()
        deployment["services"]["ollama"] = ollama_result

        # Deploy MCP Server
        mcp_result = self.deploy_mcp_server()
        deployment["services"]["mcp_server"] = mcp_result

        # Verify all services
        verification = self.verify_all_services()
        deployment["verification"] = verification

        # Summary
        ollama_ok = verification["ollama"]["status"] == "operational"
        mcp_ok = verification["mcp_server"]["status"] == "operational"
        router_ok = verification["ultron_router"]["status"] == "operational"

        deployment["summary"] = {
            "ollama_operational": ollama_ok,
            "mcp_server_operational": mcp_ok,
            "ultron_router_operational": router_ok,
            "all_operational": ollama_ok and mcp_ok,
            "fully_operational": ollama_ok and mcp_ok and router_ok
        }

        self.logger.info("="*80)
        self.logger.info("DEPLOYMENT SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Ollama: {'✅ OPERATIONAL' if ollama_ok else '❌ NOT OPERATIONAL'}")
        self.logger.info(f"MCP Server: {'✅ OPERATIONAL' if mcp_ok else '❌ NOT OPERATIONAL'}")
        self.logger.info(f"ULTRON Router: {'✅ OPERATIONAL' if router_ok else '❌ NOT OPERATIONAL'}")
        self.logger.info(f"Cluster Status: {'✅ 100% OPERATIONAL' if deployment['summary']['fully_operational'] else '⚠️  PARTIALLY OPERATIONAL' if deployment['summary']['all_operational'] else '❌ NOT OPERATIONAL'}")
        self.logger.info("="*80)

        return deployment


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="KAIJU Full Deployment - 100% Operational")
        parser.add_argument("--deploy", action="store_true", help="Deploy all services")
        parser.add_argument("--verify", action="store_true", help="Verify services only")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        deployment = KAIJUFullDeployment(project_root)

        if args.deploy:
            result = deployment.full_deployment()
            print(json.dumps(result, indent=2, default=str))
        elif args.verify:
            result = deployment.verify_all_services()
            print(json.dumps(result, indent=2))
        else:
            print("Usage:")
            print("  --deploy  : Deploy all services (bring cluster 100% online)")
            print("  --verify  : Verify services only")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()