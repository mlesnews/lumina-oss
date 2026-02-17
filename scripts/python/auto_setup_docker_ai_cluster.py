#!/usr/bin/env python3
"""
Auto Setup Docker & AI Cluster - One-Command Automation
#JARVIS #ULTRON #KAIJU #KAIJU_NO_8 #DS1821PLUS

This script automates the entire Docker and local AI LLM cluster setup process.
No more manual Docker/container management - just run this and everything works!

Features:
- Automatic Docker Desktop detection and startup (Windows)
- Local Ollama container management
- KAIJU (Desktop) and NAS (DS1821PLUS) connectivity verification
- Health checks for all endpoints
- Model availability verification
- One-command solution - just run it!
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('docker_ai_setup.log')
    ]
)
logger = logging.getLogger(__name__)


class DockerAIClusterAutoSetup:
    """Automated Docker and AI cluster setup manager"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.is_windows = platform.system() == "Windows"
        self.docker_compose_files = {
            "local_ollama": self.project_root / "containerization" / "services" / "laptop-optimized-llm" / "docker-compose.yml",
            "iron_legion": self.project_root / "containerization" / "docker-compose.iron-legion.yml",
        }
        self.endpoints = {
            "ultron_local": "http://localhost:11434",
            "kaiju_desktop": "http://<NAS_IP>:11434",  # KAIJU_NO_8 = Desktop
            "nas_synology": "http://<NAS_PRIMARY_IP>:11434",  # Synology NAS (DS1821PLUS)
            "ultron_router": "http://<NAS_PRIMARY_IP>:3008",
        }
        self.required_models = {
            "ultron_local": ["qwen2.5:72b"],
            "kaiju_desktop": ["llama3.2:3b"],  # KAIJU_NO_8 desktop models
            "nas_synology": [],  # NAS may have different models
        }

    async def setup_everything(self) -> bool:
        """Main entry point - sets up everything automatically"""
        logger.info("🚀 Starting Automated Docker & AI Cluster Setup...")
        logger.info("=" * 70)

        try:
            # Step 1: Check and start Docker
            logger.info("\n1️⃣ Checking Docker Desktop...")
            if not await self._ensure_docker_running():
                logger.error("❌ Docker setup failed. Please install Docker Desktop.")
                return False

            # Step 2: Start local Ollama container
            logger.info("\n2️⃣ Setting up local ULTRON (Ollama)...")
            if not await self._setup_local_ollama():
                logger.warning("⚠️  Local Ollama setup had issues, but continuing...")

            # Step 3: Check KAIJU (Desktop) and NAS (DS1821PLUS) connectivity
            logger.info("\n3️⃣ Checking KAIJU (Desktop) and NAS (DS1821PLUS) connectivity...")
            kaiju_status = await self._check_kaiju_connectivity()
            nas_status = await self._check_nas_connectivity()
            if not kaiju_status["accessible"]:
                logger.warning(f"⚠️  KAIJU (Desktop) not accessible: {kaiju_status.get('error', 'Unknown error')}")
            if not nas_status["accessible"]:
                logger.warning(f"⚠️  NAS (DS1821PLUS) not accessible: {nas_status.get('error', 'Unknown error')}")
            if not kaiju_status["accessible"] and not nas_status["accessible"]:
                logger.info("   Continuing with local-only setup...")

            # Step 4: Health checks
            logger.info("\n4️⃣ Running health checks...")
            health_status = await self._run_health_checks()

            # Step 5: Verify models
            logger.info("\n5️⃣ Verifying model availability...")
            await self._verify_models()

            # Step 6: Print status summary
            logger.info("\n" + "=" * 70)
            self._print_status_summary(health_status, kaiju_status, nas_status)
            logger.info("=" * 70)

            logger.info("\n✅ Automated setup complete!")
            return True

        except Exception as e:
            logger.error(f"❌ Setup failed: {e}", exc_info=True)
            return False

    async def _ensure_docker_running(self) -> bool:
        """Check if Docker is running and start it if needed"""
        try:
            # Check if Docker is running
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("   ✅ Docker is running")
                return True

            logger.info("   ⚠️  Docker is not running, attempting to start...")

            if self.is_windows:
                # Try to start Docker Desktop on Windows
                docker_paths = [
                    r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                    os.path.expanduser(r"~\AppData\Local\Programs\Docker\Docker\Docker Desktop.exe"),
                ]

                for docker_path in docker_paths:
                    if os.path.exists(docker_path):
                        logger.info(f"   • Starting Docker Desktop from: {docker_path}")
                        subprocess.Popen([docker_path], shell=True)

                        # Wait for Docker to start (up to 60 seconds)
                        logger.info("   • Waiting for Docker to start (this may take up to 60 seconds)...")
                        for i in range(12):  # 12 * 5 = 60 seconds
                            await asyncio.sleep(5)
                            check_result = subprocess.run(
                                ["docker", "version"],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if check_result.returncode == 0:
                                logger.info("   ✅ Docker started successfully!")
                                return True
                            logger.info(f"   • Still waiting... ({i+1}/12)")

                        logger.error("   ❌ Docker did not start within 60 seconds")
                        logger.error("   Please start Docker Desktop manually and try again")
                        return False

                logger.error("   ❌ Could not find Docker Desktop installation")
                logger.error("   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
                return False
            else:
                # Linux/Mac - try to start Docker service
                logger.info("   • Attempting to start Docker service...")
                start_result = subprocess.run(
                    ["sudo", "systemctl", "start", "docker"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if start_result.returncode == 0:
                    await asyncio.sleep(5)  # Wait for service to start
                    check_result = subprocess.run(
                        ["docker", "version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if check_result.returncode == 0:
                        logger.info("   ✅ Docker service started successfully!")
                        return True

                logger.error("   ❌ Could not start Docker service")
                logger.error("   Please start Docker manually: sudo systemctl start docker")
                return False

        except subprocess.TimeoutExpired:
            logger.error("   ❌ Docker check timed out")
            return False
        except FileNotFoundError:
            logger.error("   ❌ Docker command not found")
            logger.error("   Please install Docker: https://www.docker.com/get-started")
            return False
        except Exception as e:
            logger.error(f"   ❌ Error checking Docker: {e}")
            return False

    async def _setup_local_ollama(self) -> bool:
        """Setup local Ollama container (ULTRON)"""
        try:
            compose_file = self.docker_compose_files["local_ollama"]

            if not compose_file.exists():
                logger.warning(f"   ⚠️  Docker compose file not found: {compose_file}")
                logger.info("   • Checking if Ollama is already running locally...")

                # Check if Ollama is already running (maybe installed natively)
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        logger.info("   ✅ Ollama is already running locally!")
                        return True
                except:
                    pass

                logger.warning("   ⚠️  Could not set up local Ollama container")
                return False

            # Check if container is already running
            logger.info("   • Checking if container is already running...")
            check_result = subprocess.run(
                ["docker", "ps", "--filter", "name=laptop-optimized-llm", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "laptop-optimized-llm" in check_result.stdout:
                logger.info("   ✅ Local Ollama container is already running")

                # Verify it's responding
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        logger.info("   ✅ Local Ollama API is responding")
                        return True
                    else:
                        logger.warning("   ⚠️  Container running but API not responding, restarting...")
                except:
                    logger.warning("   ⚠️  Container running but API not responding, restarting...")

            # Start the container
            logger.info("   • Starting local Ollama container...")
            start_result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d"],
                capture_output=True,
                text=True,
                cwd=compose_file.parent,
                timeout=120
            )

            if start_result.returncode != 0:
                logger.error(f"   ❌ Failed to start container: {start_result.stderr}")
                return False

            logger.info("   • Waiting for container to initialize (30 seconds)...")
            await asyncio.sleep(30)

            # Verify it's working
            logger.info("   • Verifying container is responding...")
            for attempt in range(6):  # 6 attempts * 5 seconds = 30 seconds
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        logger.info("   ✅ Local Ollama is running and responding!")
                        return True
                except:
                    pass

                if attempt < 5:
                    logger.info(f"   • Still waiting... ({attempt+1}/6)")
                    await asyncio.sleep(5)

            logger.warning("   ⚠️  Container started but API not responding yet")
            logger.info("   • It may take a few more minutes for the container to fully initialize")
            return False

        except subprocess.TimeoutExpired:
            logger.error("   ❌ Container startup timed out")
            return False
        except Exception as e:
            logger.error(f"   ❌ Error setting up local Ollama: {e}")
            return False

    async def _check_kaiju_connectivity(self) -> Dict[str, Any]:
        """Check if KAIJU (KAIJU_NO_8 Desktop at <NAS_IP>) is accessible"""
        status = {
            "accessible": False,
            "ollama_running": False,
            "error": None
        }

        try:
            import requests

            # Check KAIJU Desktop IP connectivity (<NAS_IP>)
            logger.info("   • Checking KAIJU (KAIJU_NO_8 Desktop) connectivity (<NAS_IP>)...")

            try:
                response = requests.get("http://<NAS_IP>:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    status["accessible"] = True
                    status["ollama_running"] = True
                    logger.info("   ✅ KAIJU (Desktop) Ollama is accessible and running!")
                else:
                    status["accessible"] = True
                    logger.warning(f"   ⚠️  KAIJU accessible but Ollama returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                status["error"] = "Connection refused - KAIJU desktop may be offline or Ollama not running"
                logger.warning(f"   ⚠️  {status['error']}")
            except requests.exceptions.Timeout:
                status["error"] = "Connection timeout - KAIJU desktop may be unreachable"
                logger.warning(f"   ⚠️  {status['error']}")
            except Exception as e:
                status["error"] = str(e)
                logger.warning(f"   ⚠️  Error checking KAIJU: {e}")

        except ImportError:
            status["error"] = "requests library not available"
            logger.warning("   ⚠️  Cannot check KAIJU connectivity (requests library missing)")
        except Exception as e:
            status["error"] = str(e)
            logger.warning(f"   ⚠️  Error checking KAIJU: {e}")

        return status

    async def _check_nas_connectivity(self) -> Dict[str, Any]:
        """Check if NAS (Synology DS1821PLUS at <NAS_PRIMARY_IP>) is accessible"""
        status = {
            "accessible": False,
            "ollama_running": False,
            "router_running": False,
            "error": None
        }

        try:
            import requests

            # Check NAS (Synology DS1821PLUS) IP connectivity (<NAS_PRIMARY_IP>)
            logger.info("   • Checking NAS (Synology DS1821PLUS) connectivity (<NAS_PRIMARY_IP>)...")

            try:
                response = requests.get("http://<NAS_PRIMARY_IP>:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    status["accessible"] = True
                    status["ollama_running"] = True
                    logger.info("   ✅ NAS (Synology DS1821PLUS) Ollama is accessible and running!")
                else:
                    status["accessible"] = True
                    logger.warning(f"   ⚠️  NAS accessible but Ollama returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                status["error"] = "Connection refused - NAS may be offline or Ollama not running"
                logger.warning(f"   ⚠️  {status['error']}")
            except requests.exceptions.Timeout:
                status["error"] = "Connection timeout - NAS may be unreachable"
                logger.warning(f"   ⚠️  {status['error']}")
            except Exception as e:
                status["error"] = str(e)
                logger.warning(f"   ⚠️  Error checking NAS: {e}")

            # Check ULTRON Router (on NAS)
            if status["accessible"]:
                try:
                    router_response = requests.get("http://<NAS_PRIMARY_IP>:3008/health", timeout=5)
                    if router_response.status_code == 200:
                        status["router_running"] = True
                        logger.info("   ✅ ULTRON Router is running!")
                    else:
                        logger.warning("   ⚠️  ULTRON Router not responding")
                except:
                    logger.warning("   ⚠️  ULTRON Router not accessible")

        except ImportError:
            status["error"] = "requests library not available"
            logger.warning("   ⚠️  Cannot check NAS connectivity (requests library missing)")
        except Exception as e:
            status["error"] = str(e)
            logger.warning(f"   ⚠️  Error checking NAS: {e}")

        return status

    async def _run_health_checks(self) -> Dict[str, Any]:
        """Run health checks on all endpoints"""
        health_status = {}

        try:
            import requests
        except ImportError:
            logger.warning("   ⚠️  requests library not available, skipping health checks")
            return health_status

        for name, endpoint in self.endpoints.items():
            logger.info(f"   • Checking {name} ({endpoint})...")
            try:
                if "11434" in endpoint:
                    # Ollama endpoint
                    response = requests.get(f"{endpoint}/api/tags", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        model_count = len(data.get("models", []))
                        health_status[name] = {
                            "status": "healthy",
                            "models": model_count,
                            "endpoint": endpoint
                        }
                        logger.info(f"      ✅ {name} is healthy ({model_count} models)")
                    else:
                        health_status[name] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status_code}",
                            "endpoint": endpoint
                        }
                        logger.warning(f"      ⚠️  {name} returned status {response.status_code}")
                elif "3008" in endpoint:
                    # Router endpoint
                    response = requests.get(f"{endpoint}/health", timeout=5)
                    if response.status_code == 200:
                        health_status[name] = {
                            "status": "healthy",
                            "endpoint": endpoint
                        }
                        logger.info(f"      ✅ {name} is healthy")
                    else:
                        health_status[name] = {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status_code}",
                            "endpoint": endpoint
                        }
                        logger.warning(f"      ⚠️  {name} returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                health_status[name] = {
                    "status": "unreachable",
                    "error": "Connection refused",
                    "endpoint": endpoint
                }
                logger.warning(f"      ⚠️  {name} is unreachable")
            except requests.exceptions.Timeout:
                health_status[name] = {
                    "status": "timeout",
                    "error": "Connection timeout",
                    "endpoint": endpoint
                }
                logger.warning(f"      ⚠️  {name} connection timeout")
            except Exception as e:
                health_status[name] = {
                    "status": "error",
                    "error": str(e),
                    "endpoint": endpoint
                }
                logger.warning(f"      ⚠️  {name} error: {e}")

        return health_status

    async def _verify_models(self) -> None:
        """Verify required models are available"""
        try:
            import requests
        except ImportError:
            logger.warning("   ⚠️  requests library not available, skipping model verification")
            return

        # Check local models
        logger.info("   • Checking local ULTRON models...")
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                available_models = [m.get("name", "") for m in data.get("models", [])]
                required = self.required_models["ultron_local"]

                for model in required:
                    if any(model in m for m in available_models):
                        logger.info(f"      ✅ {model} is available")
                    else:
                        logger.warning(f"      ⚠️  {model} is not available")
                        logger.info(f"      • To download: ollama pull {model}")
        except:
            logger.warning("      ⚠️  Could not check local models")

        # Check KAIJU (Desktop) models
        logger.info("   • Checking KAIJU (Desktop) models...")
        try:
            response = requests.get("http://<NAS_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                available_models = [m.get("name", "") for m in data.get("models", [])]
                required = self.required_models["kaiju_desktop"]

                for model in required:
                    if any(model in m for m in available_models):
                        logger.info(f"      ✅ {model} is available on KAIJU (Desktop)")
                    else:
                        logger.warning(f"      ⚠️  {model} is not available on KAIJU (Desktop)")
        except:
            logger.warning("      ⚠️  Could not check KAIJU (Desktop) models (may be offline)")

        # Check NAS (Synology DS1821PLUS) models
        logger.info("   • Checking NAS (Synology DS1821PLUS) models...")
        try:
            response = requests.get("http://<NAS_PRIMARY_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                available_models = [m.get("name", "") for m in data.get("models", [])]
                required = self.required_models["nas_synology"]

                if required:
                    for model in required:
                        if any(model in m for m in available_models):
                            logger.info(f"      ✅ {model} is available on NAS (DS1821PLUS)")
                        else:
                            logger.warning(f"      ⚠️  {model} is not available on NAS (DS1821PLUS)")
                else:
                    model_count = len(available_models)
                    logger.info(f"      ℹ️  NAS (DS1821PLUS) has {model_count} model(s) available")
        except:
            logger.warning("      ⚠️  Could not check NAS (DS1821PLUS) models (may be offline)")

    def _print_status_summary(self, health_status: Dict[str, Any], kaiju_status: Dict[str, Any], nas_status: Dict[str, Any]) -> None:
        """Print comprehensive status summary"""
        logger.info("\n📊 SYSTEM STATUS SUMMARY")
        logger.info("-" * 70)

        # Docker status
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"🐳 Docker: ✅ Running (version {result.stdout.strip()})")
            else:
                logger.info("🐳 Docker: ❌ Not running")
        except:
            logger.info("🐳 Docker: ❓ Status unknown")

        # Local Ollama status
        local_status = health_status.get("ultron_local", {})
        if local_status.get("status") == "healthy":
            models = local_status.get("models", 0)
            logger.info(f"🖥️  ULTRON (Local): ✅ Running ({models} models)")
        else:
            logger.info(f"🖥️  ULTRON (Local): ❌ {local_status.get('status', 'Unknown')}")

        # KAIJU (Desktop) status
        if kaiju_status.get("accessible"):
            if kaiju_status.get("ollama_running"):
                logger.info("🖥️  KAIJU (Desktop/KAIJU_NO_8): ✅ Accessible and running")
            else:
                logger.info("🖥️  KAIJU (Desktop/KAIJU_NO_8): ⚠️  Accessible but Ollama not responding")
        else:
            logger.info(f"🖥️  KAIJU (Desktop/KAIJU_NO_8): ❌ Not accessible ({kaiju_status.get('error', 'Unknown')})")

        # NAS (Synology DS1821PLUS) status
        if nas_status.get("accessible"):
            if nas_status.get("ollama_running"):
                logger.info("🌐 NAS (DS1821PLUS): ✅ Accessible and running")
            else:
                logger.info("🌐 NAS (DS1821PLUS): ⚠️  Accessible but Ollama not responding")
        else:
            logger.info(f"🌐 NAS (DS1821PLUS): ❌ Not accessible ({nas_status.get('error', 'Unknown')})")

        # Router status
        router_status = health_status.get("ultron_router", {})
        if router_status.get("status") == "healthy":
            logger.info("🔄 ULTRON Router: ✅ Running")
        else:
            logger.info(f"🔄 ULTRON Router: ❌ {router_status.get('status', 'Unknown')}")

        logger.info("\n💡 QUICK COMMANDS:")
        logger.info("   • Check status: python scripts/python/auto_setup_docker_ai_cluster.py status")
        logger.info("   • Restart local: docker-compose -f containerization/services/laptop-optimized-llm/docker-compose.yml restart")
        logger.info("   • View logs: docker logs laptop-optimized-llm")
        logger.info("   • Pull model: ollama pull qwen2.5:72b")

    async def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            "docker": False,
            "local_ollama": False,
            "kaiju_desktop": False,
            "nas_synology": False,
            "health": {}
        }

        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5
            )
            status["docker"] = result.returncode == 0
        except:
            status["docker"] = False

        # Check local Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            status["local_ollama"] = response.status_code == 200
        except:
            status["local_ollama"] = False

        # Check KAIJU (Desktop)
        try:
            import requests
            response = requests.get("http://<NAS_IP>:11434/api/tags", timeout=5)
            status["kaiju"] = response.status_code == 200
        except:
            status["kaiju"] = False

        # Check NAS (Synology)
        try:
            import requests
            response = requests.get("http://<NAS_PRIMARY_IP>:11434/api/tags", timeout=5)
            status["nas"] = response.status_code == 200
        except:
            status["nas"] = False

        # Health checks
        status["health"] = await self._run_health_checks()

        return status


async def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto Setup Docker & AI Cluster - One-Command Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_setup_docker_ai_cluster.py          # Full automated setup
  python auto_setup_docker_ai_cluster.py status   # Check current status
  python auto_setup_docker_ai_cluster.py health    # Run health checks only
        """
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="setup",
        choices=["setup", "status", "health"],
        help="Action to perform (default: setup)"
    )

    args = parser.parse_args()

    setup = DockerAIClusterAutoSetup()

    if args.action == "setup":
        success = await setup.setup_everything()
        sys.exit(0 if success else 1)

    elif args.action == "status":
        status = await setup.get_status()
        print("\n📊 Current System Status:")
        print("=" * 70)
        print(json.dumps(status, indent=2))
        print("=" * 70)

    elif args.action == "health":
        health = await setup._run_health_checks()
        print("\n🏥 Health Check Results:")
        print("=" * 70)
        print(json.dumps(health, indent=2))
        print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())