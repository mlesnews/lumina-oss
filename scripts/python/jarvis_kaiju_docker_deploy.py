#!/usr/bin/env python3
"""
JARVIS KAIJU Docker Deployment Script
Deploys services using Docker Desktop on KAIJU_NO_8.

This script should be run ON KAIJU_NO_8 in Docker Desktop terminal or PowerShell.

Tags: #DEPLOYMENT #DOCKER #KAIJU @AUTO
"""

import sys
import subprocess
import requests
import socket
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISKAIJUDocker")


class KAIJUDockerDeployment:
    """
    Deploy services on KAIJU_NO_8 using Docker Desktop

    This runs locally on KAIJU_NO_8, not via SSH.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = project_root
        self.logger = logger

        self.ollama_port = 11434
        self.mcp_port = 8000
        self.ultron_router_port = 3008

        self.logger.info("✅ KAIJU Docker Deployment initialized")
        self.logger.info("   Running on KAIJU_NO_8 - using local Docker Desktop")

    def check_docker(self) -> Dict[str, Any]:
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("   ✅ Docker is available")
                return {"available": True, "output": result.stdout}
            else:
                self.logger.error(f"   ❌ Docker check failed: {result.stderr}")
                return {"available": False, "error": result.stderr}
        except FileNotFoundError:
            self.logger.error("   ❌ Docker not found. Is Docker Desktop installed and running?")
            return {"available": False, "error": "Docker not found"}
        except Exception as e:
            self.logger.error(f"   ❌ Docker check error: {e}")
            return {"available": False, "error": str(e)}

    def check_gpu(self) -> Dict[str, Any]:
        """Check if GPU is available for Docker"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split('\n')[0] if result.stdout.strip() else "Unknown"
                self.logger.info(f"   ✅ GPU detected: {gpu_info}")
                return {"available": True, "info": gpu_info}
            else:
                self.logger.warning("   ⚠️  nvidia-smi not available - GPU may not be accessible")
                return {"available": False}
        except FileNotFoundError:
            self.logger.warning("   ⚠️  nvidia-smi not found - GPU may not be available")
            return {"available": False}
        except Exception as e:
            self.logger.warning(f"   ⚠️  GPU check error: {e}")
            return {"available": False}

    def check_port(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def deploy_ollama(self) -> Dict[str, Any]:
        try:
            """Deploy Ollama container with GPU support"""
            self.logger.info("="*80)
            self.logger.info("🚀 DEPLOYING OLLAMA (Iron Legion)")
            self.logger.info("="*80)

            # Check if already running
            if self.check_port(self.ollama_port):
                self.logger.info(f"   ✅ Ollama already running on port {self.ollama_port}")
                return {"success": True, "action": "already_running"}

            # Check for existing container
            check_result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=ollama", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if check_result.returncode == 0 and check_result.stdout.strip():
                container_name = check_result.stdout.strip()
                self.logger.info(f"   Found existing container: {container_name}")
                # Start it
                start_result = subprocess.run(
                    ["docker", "start", container_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if start_result.returncode == 0:
                    time.sleep(3)
                    if self.check_port(self.ollama_port):
                        self.logger.info("   ✅ Ollama started successfully")
                        return {"success": True, "action": "started"}

            # Check GPU availability
            gpu_status = self.check_gpu()
            has_gpu = gpu_status.get("available", False)

            # Create new container
            self.logger.info("   Creating Ollama container...")

            if has_gpu:
                self.logger.info("   ✅ GPU detected - deploying with GPU support")
                deploy_cmd = [
                    "docker", "run", "-d",
                    "--name", "ollama",
                    "--restart", "unless-stopped",
                    "--gpus", "all",
                    "-v", "ollama-data:/root/.ollama",
                    "-p", f"{self.ollama_port}:11434",
                    "-e", "OLLAMA_NUM_GPU=1",
                    "-e", "OLLAMA_KEEP_ALIVE=5m",
                    "ollama/ollama:latest"
                ]
            else:
                self.logger.warning("   ⚠️  No GPU detected - deploying CPU-only")
                deploy_cmd = [
                    "docker", "run", "-d",
                    "--name", "ollama",
                    "--restart", "unless-stopped",
                    "-v", "ollama-data:/root/.ollama",
                    "-p", f"{self.ollama_port}:11434",
                    "ollama/ollama:latest"
                ]

            self.logger.info(f"   Running: {' '.join(deploy_cmd)}")
            deploy_result = subprocess.run(
                deploy_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if deploy_result.returncode == 0:
                time.sleep(5)
                if self.check_port(self.ollama_port):
                    self.logger.info("   ✅ Ollama deployed and running")
                    return {"success": True, "action": "deployed", "gpu_enabled": has_gpu}
                else:
                    self.logger.warning("   ⚠️  Container created but port not accessible yet")
                    return {"success": True, "action": "deployed", "warning": "Port check failed", "gpu_enabled": has_gpu}
            else:
                error_msg = deploy_result.stderr or deploy_result.stdout
                self.logger.error(f"   ❌ Deployment failed: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            self.logger.error(f"Error in deploy_ollama: {e}", exc_info=True)
            raise
    def verify_ollama(self) -> Dict[str, Any]:
        """Verify Ollama is operational"""
        try:
            response = requests.get(f"http://localhost:{self.ollama_port}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "operational": True,
                    "models": [m.get("name") for m in models],
                    "model_count": len(models)
                }
        except Exception as e:
            pass

        return {"operational": False, "error": "Cannot connect to Ollama"}

    def deploy_all(self) -> Dict[str, Any]:
        """Deploy all services"""
        self.logger.info("="*80)
        self.logger.info("🚀 KAIJU FULL DEPLOYMENT - DOCKER DESKTOP")
        self.logger.info("="*80)

        # Check Docker
        docker_check = self.check_docker()
        if not docker_check.get("available"):
            return {"success": False, "error": "Docker not available", "docker_check": docker_check}

        deployment = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "services": {}
        }

        # Deploy Ollama
        ollama_result = self.deploy_ollama()
        deployment["services"]["ollama"] = ollama_result

        if ollama_result.get("success"):
            # Verify Ollama
            time.sleep(3)
            ollama_verify = self.verify_ollama()
            deployment["services"]["ollama"]["verification"] = ollama_verify

            if ollama_verify.get("operational"):
                self.logger.info(f"   ✅ Ollama verified - {ollama_verify.get('model_count', 0)} models available")
            else:
                self.logger.warning("   ⚠️  Ollama deployed but not fully operational yet")

        # Summary
        self.logger.info("="*80)
        self.logger.info("DEPLOYMENT SUMMARY")
        self.logger.info("="*80)
        ollama_ok = deployment["services"]["ollama"].get("success", False)
        self.logger.info(f"Ollama: {'✅ DEPLOYED' if ollama_ok else '❌ FAILED'}")
        self.logger.info("="*80)

        return deployment


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="KAIJU Docker Deployment - Run on KAIJU_NO_8")
        parser.add_argument("--deploy", action="store_true", help="Deploy all services")
        parser.add_argument("--deploy-ollama", action="store_true", help="Deploy Ollama only")
        parser.add_argument("--check", action="store_true", help="Check Docker and GPU status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        deployment = KAIJUDockerDeployment(project_root)

        if args.check:
            docker_check = deployment.check_docker()
            gpu_check = deployment.check_gpu()
            print(f"Docker: {'✅ Available' if docker_check.get('available') else '❌ Not Available'}")
            print(f"GPU: {'✅ Available' if gpu_check.get('available') else '❌ Not Available'}")
        elif args.deploy_ollama:
            result = deployment.deploy_ollama()
            import json
            print(json.dumps(result, indent=2, default=str))
        elif args.deploy or not any(vars(args).values()):
            result = deployment.deploy_all()
            import json
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()