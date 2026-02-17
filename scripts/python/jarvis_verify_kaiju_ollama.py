#!/usr/bin/env python3
"""
JARVIS KAIJU Ollama Verifier
Actually verifies Ollama is running on KAIJU_NO_8 via SSH and Docker checks.

Tags: #VERIFICATION #KAIJU #OLLAMA @AUTO
"""

import sys
import paramiko
import requests
import socket
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    NASAzureVaultIntegration = None

logger = get_logger("JARVISKAIJUVerify")


class KAIJUOllamaVerifier:
    """Verify Ollama is actually running on KAIJU_NO_8"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.kaiju_ip = "<NAS_IP>"  # KAIJU_NO_8 Desktop PC
        self.kaiju_ssh_port = 22
        self.kaiju_ollama_port = 11434

        # Load SSH credentials
        self.ssh_username = None
        self.ssh_password = None
        self._load_credentials()

        self.logger.info("✅ KAIJU Ollama Verifier initialized")

    def _load_credentials(self):
        """Load SSH credentials from Azure Key Vault"""
        try:
            if NASAzureVaultIntegration:
                nas_integration = NASAzureVaultIntegration(self.project_root)
                credentials = nas_integration.load_credentials()

                if credentials:
                    self.ssh_username = credentials.get("username")
                    self.ssh_password = credentials.get("password")
                    if self.ssh_username and self.ssh_password:
                        self.logger.info(f"✅ Loaded SSH credentials for {self.ssh_username}")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load SSH credentials: {e}")

    def _ssh_execute(self, command: str) -> Dict[str, Any]:
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

            stdin, stdout, stderr = client.exec_command(command, timeout=10)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            exit_code = stdout.channel.recv_exit_status()

            client.close()

            return {
                "success": exit_code == 0,
                "output": output,
                "error": error,
                "exit_code": exit_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_ollama_running(self) -> Dict[str, Any]:
        """Actually verify Ollama is running on KAIJU_NO_8"""
        self.logger.info("="*80)
        self.logger.info("VERIFYING OLLAMA ON KAIJU_NO_8")
        self.logger.info("="*80)

        results = {
            "kaiju_ip": self.kaiju_ip,
            "ollama_port": self.kaiju_ollama_port,
            "docker_running": False,
            "ollama_container_running": False,
            "ollama_api_accessible": False,
            "models_available": [],
            "gpu_enabled": False,
            "verification_status": "unknown"
        }

        # 1. Check if Docker is running
        self.logger.info("1. Checking if Docker is running on KAIJU_NO_8...")
        docker_check = self._ssh_execute("docker ps")
        if docker_check.get("success"):
            results["docker_running"] = True
            self.logger.info("   ✅ Docker is running")
        else:
            self.logger.warning("   ❌ Docker is not running or not accessible")
            results["verification_status"] = "docker_not_running"
            return results

        # 2. Check if Ollama container exists and is running
        self.logger.info("2. Checking for Ollama Docker container...")
        ollama_container_check = self._ssh_execute("docker ps -a | grep -i ollama")
        if ollama_container_check.get("success") and ollama_container_check.get("output"):
            output = ollama_container_check.get("output", "")
            if "Up" in output or "running" in output.lower():
                results["ollama_container_running"] = True
                self.logger.info("   ✅ Ollama container is running")

                # Check if GPU is enabled
                container_details = self._ssh_execute("docker inspect ollama 2>/dev/null | grep -i gpu || docker inspect ollama 2>/dev/null | grep -i device")
                if container_details.get("output"):
                    results["gpu_enabled"] = "gpu" in container_details.get("output", "").lower() or "device" in container_details.get("output", "").lower()
                    if results["gpu_enabled"]:
                        self.logger.info("   ✅ GPU appears to be enabled in container")
            else:
                self.logger.warning("   ⚠️  Ollama container exists but is not running")
                self.logger.info(f"   Container status: {output}")
        else:
            self.logger.warning("   ❌ Ollama container not found")
            results["verification_status"] = "container_not_found"
            return results

        # 3. Check if Ollama API is accessible
        self.logger.info("3. Checking Ollama API accessibility...")
        try:
            response = requests.get(
                f"http://{self.kaiju_ip}:{self.kaiju_ollama_port}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                results["ollama_api_accessible"] = True
                models_data = response.json().get("models", [])
                results["models_available"] = [m.get("name", "") for m in models_data]
                results["model_count"] = len(models_data)
                self.logger.info(f"   ✅ Ollama API is accessible")
                self.logger.info(f"   📦 Models available: {len(models_data)}")
                for model in models_data[:5]:  # Show first 5
                    self.logger.info(f"      - {model.get('name', 'Unknown')}")
            else:
                self.logger.warning(f"   ⚠️  Ollama API returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.logger.warning("   ⚠️  Ollama API not accessible from this network (may be firewall/local-only)")
            results["note"] = "API not accessible from this network - may be running locally only"
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error checking Ollama API: {e}")

        # 4. Check GPU utilization if accessible
        if results["ollama_api_accessible"]:
            self.logger.info("4. Checking GPU configuration...")
            gpu_check = self._ssh_execute("nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null || echo 'nvidia-smi not available'")
            if gpu_check.get("success") and "not available" not in gpu_check.get("output", ""):
                gpu_info = gpu_check.get("output", "").strip()
                if gpu_info:
                    self.logger.info(f"   📊 GPU Status: {gpu_info}")

        # Final status
        if results["ollama_container_running"] and results["ollama_api_accessible"]:
            results["verification_status"] = "verified_running"
            self.logger.info("\n" + "="*80)
            self.logger.info("✅ VERIFICATION COMPLETE: Ollama is running on KAIJU_NO_8")
            self.logger.info("="*80)
        elif results["ollama_container_running"]:
            results["verification_status"] = "running_but_not_accessible"
            self.logger.info("\n" + "="*80)
            self.logger.info("⚠️  VERIFICATION: Ollama container is running but API not accessible from this network")
            self.logger.info("="*80)
        else:
            results["verification_status"] = "not_running"
            self.logger.info("\n" + "="*80)
            self.logger.info("❌ VERIFICATION: Ollama is not running on KAIJU_NO_8")
            self.logger.info("="*80)

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Verify Ollama on KAIJU_NO_8")
        parser.add_argument("--verify", action="store_true", help="Verify Ollama is running")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        verifier = KAIJUOllamaVerifier(project_root)

        if args.verify or True:  # Default to verify
            result = verifier.verify_ollama_running()
            print(f"\nVerification Status: {result.get('verification_status')}")
            if result.get("models_available"):
                print(f"Models: {', '.join(result['models_available'][:5])}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()