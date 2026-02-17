#!/usr/bin/env python3
"""
JARVIS KAIJU Cluster Diagnostics and Repair

SSH to KAIJU (<NAS_PRIMARY_IP>) and diagnose/fix cluster problems.
Includes Iron Legion (Ollama) and ULTRON Router diagnostics.

SECURITY NOTE: AI has sudoless root access on KAIJU.

Tags: #TROUBLESHOOTING #CLUSTER @KAIJU
"""

import sys
import json
import paramiko
import socket
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISKAIJUCluster")


class KAIJUClusterDiagnostics:
    """
    KAIJU Cluster Diagnostics

    SSH to KAIJU and diagnose/fix cluster issues.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # KAIJU connection info
        self.kaiju_ip = "<NAS_PRIMARY_IP>"
        self.kaiju_ssh_port = 22
        self.kaiju_ollama_port = 11434
        self.kaiju_ultron_router_port = 3008

        # SSH credentials (from Azure Key Vault)
        self.ssh_username = None
        self.ssh_password = None
        self._load_credentials()

        self.logger.info("✅ KAIJU Cluster Diagnostics initialized")
        self.logger.warning("🔒 SECURITY: AI has sudoless root access on KAIJU")

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
                else:
                    self.logger.warning("⚠️  SSH credentials incomplete in Azure Key Vault")
            else:
                self.logger.warning("⚠️  SSH credentials not found in Azure Key Vault")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load SSH credentials: {e}")

    def test_ssh_connection(self) -> Dict[str, Any]:
        """Test SSH connection to KAIJU"""
        self.logger.info(f"🔌 Testing SSH connection to {self.kaiju_ip}...")

        if not self.ssh_username or not self.ssh_password:
            return {
                "success": False,
                "error": "SSH credentials not available"
            }

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

            # Test basic command
            stdin, stdout, stderr = client.exec_command("whoami")
            user = stdout.read().decode().strip()

            # Test root access (sudoless)
            stdin, stdout, stderr = client.exec_command("sudo -n whoami 2>&1 || whoami")
            root_test = stdout.read().decode().strip()

            client.close()

            self.logger.info(f"✅ SSH connection successful (user: {user})")
            if "root" in root_test:
                self.logger.warning("🔒 Root access confirmed (sudoless)")

            return {
                "success": True,
                "user": user,
                "root_access": "root" in root_test
            }

        except Exception as e:
            self.logger.error(f"❌ SSH connection failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def check_ollama_service(self) -> Dict[str, Any]:
        """Check Ollama service status on KAIJU"""
        self.logger.info(f"🔍 Checking Ollama service on {self.kaiju_ip}:{self.kaiju_ollama_port}...")

        # First, check if port is accessible
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.kaiju_ip, self.kaiju_ollama_port))
            sock.close()

            if result != 0:
                return {
                    "success": False,
                    "error": f"Port {self.kaiju_ollama_port} not accessible",
                    "port_open": False
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Port check failed: {e}",
                "port_open": False
            }

        # Check Ollama API
        try:
            response = requests.get(
                f"http://{self.kaiju_ip}:{self.kaiju_ollama_port}/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                models = response.json().get("models", [])
                self.logger.info(f"✅ Ollama service is running ({len(models)} models available)")

                return {
                    "success": True,
                    "port_open": True,
                    "api_accessible": True,
                    "models": [m.get("name", "") for m in models]
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API returned status {response.status_code}",
                    "port_open": True,
                    "api_accessible": False
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama API check failed: {e}",
                "port_open": True,
                "api_accessible": False
            }

    def check_ultron_router(self) -> Dict[str, Any]:
        """Check ULTRON Router service on KAIJU"""
        self.logger.info(f"🔍 Checking ULTRON Router on {self.kaiju_ip}:{self.kaiju_ultron_router_port}...")

        # Check if port is accessible
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.kaiju_ip, self.kaiju_ultron_router_port))
            sock.close()

            if result != 0:
                return {
                    "success": False,
                    "error": f"Port {self.kaiju_ultron_router_port} not accessible",
                    "port_open": False
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Port check failed: {e}",
                "port_open": False
            }

        # Try to check router status (if it has a health endpoint)
        try:
            response = requests.get(
                f"http://{self.kaiju_ip}:{self.kaiju_ultron_router_port}/health",
                timeout=5
            )

            if response.status_code == 200:
                self.logger.info("✅ ULTRON Router is running")
                return {
                    "success": True,
                    "port_open": True,
                    "api_accessible": True,
                    "status": response.json() if response.headers.get("content-type", "").startswith("application/json") else "ok"
                }
            else:
                return {
                    "success": False,
                    "error": f"ULTRON Router returned status {response.status_code}",
                    "port_open": True,
                    "api_accessible": False
                }

        except requests.exceptions.RequestException:
            # Router might not have /health endpoint, but port is open
            return {
                "success": True,
                "port_open": True,
                "api_accessible": "unknown",
                "note": "Port is open but health endpoint not available"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"ULTRON Router check failed: {e}",
                "port_open": True,
                "api_accessible": False
            }

    def ssh_execute_command(self, command: str) -> Dict[str, Any]:
        """Execute command on KAIJU via SSH"""
        if not self.ssh_username or not self.ssh_password:
            return {
                "success": False,
                "error": "SSH credentials not available"
            }

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

            stdin, stdout, stderr = client.exec_command(command)
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
            return {
                "success": False,
                "error": str(e)
            }

    def check_ollama_service_status(self) -> Dict[str, Any]:
        """Check Ollama service status via SSH"""
        self.logger.info("🔍 Checking Ollama service status via SSH...")

        # Check if Ollama is running (systemd or docker)
        result = self.ssh_execute_command("systemctl is-active ollama 2>/dev/null || docker ps | grep ollama || ps aux | grep ollama | grep -v grep")

        if result.get("success"):
            output = result.get("output", "").strip()
            if output:
                self.logger.info(f"✅ Ollama service found: {output[:100]}")
                return {
                    "success": True,
                    "status": output
                }
            else:
                self.logger.warning("⚠️  Ollama service not found running")
                return {
                    "success": False,
                    "error": "Ollama service not running"
                }
        else:
            return result

    def restart_ollama_service(self) -> Dict[str, Any]:
        """Restart Ollama service on KAIJU"""
        self.logger.info("🔄 Restarting Ollama service...")

        # Try systemd first
        result = self.ssh_execute_command("sudo systemctl restart ollama 2>&1 || sudo docker restart ollama 2>&1 || echo 'Service restart attempted'")

        if result.get("success"):
            self.logger.info("✅ Ollama service restart attempted")
            # Wait a bit and check status
            import time
            time.sleep(3)
            status = self.check_ollama_service()
            return {
                "success": status.get("success", False),
                "restart_attempted": True,
                "current_status": status
            }
        else:
            return result

    def full_diagnostics(self) -> Dict[str, Any]:
        """Run full diagnostics on KAIJU cluster"""
        self.logger.info("🔍 Running full KAIJU cluster diagnostics...")

        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "kaiju_ip": self.kaiju_ip,
            "ssh_connection": None,
            "ollama_service": None,
            "ollama_api": None,
            "ultron_router": None,
            "issues": [],
            "fixes_applied": []
        }

        # 1. Test SSH connection
        ssh_result = self.test_ssh_connection()
        diagnostics["ssh_connection"] = ssh_result

        if not ssh_result.get("success"):
            diagnostics["issues"].append("SSH connection failed")
            return diagnostics

        # 2. Check Ollama service status (SSH)
        ollama_status = self.check_ollama_service_status()
        diagnostics["ollama_service"] = ollama_status

        if not ollama_status.get("success"):
            diagnostics["issues"].append("Ollama service not running")

        # 3. Check Ollama API
        ollama_api = self.check_ollama_service()
        diagnostics["ollama_api"] = ollama_api

        if not ollama_api.get("success"):
            diagnostics["issues"].append("Ollama API not accessible")

        # 4. Check ULTRON Router
        ultron_router = self.check_ultron_router()
        diagnostics["ultron_router"] = ultron_router

        if not ultron_router.get("success"):
            diagnostics["issues"].append("ULTRON Router not accessible")

        # 5. Attempt fixes if issues found
        if diagnostics["issues"]:
            self.logger.info(f"🔧 Found {len(diagnostics['issues'])} issues, attempting fixes...")

            # Fix Ollama if needed
            if "Ollama service not running" in diagnostics["issues"] or "Ollama API not accessible" in diagnostics["issues"]:
                restart_result = self.restart_ollama_service()
                diagnostics["fixes_applied"].append({
                    "fix": "Restart Ollama service",
                    "result": restart_result
                })

        diagnostics["summary"] = {
            "total_issues": len(diagnostics["issues"]),
            "total_fixes": len(diagnostics["fixes_applied"]),
            "all_healthy": len(diagnostics["issues"]) == 0
        }

        return diagnostics


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="KAIJU Cluster Diagnostics")
        parser.add_argument("--diagnostics", action="store_true", help="Run full diagnostics")
        parser.add_argument("--ssh-test", action="store_true", help="Test SSH connection")
        parser.add_argument("--check-ollama", action="store_true", help="Check Ollama service")
        parser.add_argument("--check-router", action="store_true", help="Check ULTRON Router")
        parser.add_argument("--restart-ollama", action="store_true", help="Restart Ollama service")
        parser.add_argument("--command", type=str, help="Execute SSH command")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        diagnostics = KAIJUClusterDiagnostics(project_root)

        if args.diagnostics:
            result = diagnostics.full_diagnostics()
            print(json.dumps(result, indent=2, default=str))

        elif args.ssh_test:
            result = diagnostics.test_ssh_connection()
            print(json.dumps(result, indent=2))

        elif args.check_ollama:
            result = diagnostics.check_ollama_service()
            print(json.dumps(result, indent=2))

        elif args.check_router:
            result = diagnostics.check_ultron_router()
            print(json.dumps(result, indent=2))

        elif args.restart_ollama:
            result = diagnostics.restart_ollama_service()
            print(json.dumps(result, indent=2))

        elif args.command:
            result = diagnostics.ssh_execute_command(args.command)
            print(json.dumps(result, indent=2))

        else:
            print("Usage:")
            print("  --diagnostics      : Run full diagnostics")
            print("  --ssh-test         : Test SSH connection")
            print("  --check-ollama     : Check Ollama service")
            print("  --check-router     : Check ULTRON Router")
            print("  --restart-ollama   : Restart Ollama service")
            print("  --command <cmd>    : Execute SSH command")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()