#!/usr/bin/env python3
"""
Start @HOMELAB Local AI Models

Starts and validates local AI models on all @HOMELAB localhosts:
- Ollama (localhost:11434)
- Iron Legion (localhost:3000)

Tags: #HOMELAB #LOCAL_AI #START #VALIDATION @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartHomelabLocalAI")


class HomelabLocalAIStarter:
    """Start and validate local AI models on homelab localhosts"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.endpoints = {
            "ollama": "http://localhost:11434",
            "iron_legion": "http://localhost:3000"
        }

    def check_docker_services(self) -> Dict[str, Any]:
        """Check if Docker services are running"""
        logger.info("=" * 80)
        logger.info("🐳 CHECKING DOCKER SERVICES")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "ollama_running": False,
            "iron_legion_running": False,
            "services": []
        }

        try:
            # Check for Ollama container
            ollama_check = subprocess.run(
                ["docker", "ps", "--filter", "name=ollama", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if ollama_check.returncode == 0 and ollama_check.stdout.strip():
                result["ollama_running"] = True
                result["services"].append("ollama")
                logger.info("   ✅ Ollama Docker container running")
            else:
                logger.info("   ❌ Ollama Docker container not running")

            # Check for Iron Legion containers
            iron_legion_check = subprocess.run(
                ["docker", "ps", "--filter", "name=iron-legion", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if iron_legion_check.returncode == 0 and iron_legion_check.stdout.strip():
                result["iron_legion_running"] = True
                result["services"].append("iron-legion")
                logger.info("   ✅ Iron Legion Docker containers running")
            else:
                logger.info("   ❌ Iron Legion Docker containers not running")

        except FileNotFoundError:
            logger.warning("   ⚠️  Docker not found - may need to use Ollama Desktop")
        except Exception as e:
            logger.warning(f"   ⚠️  Error checking Docker: {e}")

        logger.info("")
        return result

    def start_ollama(self) -> Dict[str, Any]:
        """Start Ollama service"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING OLLAMA (localhost:11434)")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "method": None,
            "success": False,
            "error": None
        }

        # Method 1: Try Docker
        try:
            logger.info("Method 1: Starting Ollama via Docker...")
            docker_result = subprocess.run(
                ["docker", "compose", "up", "-d", "ollama"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            if docker_result.returncode == 0:
                logger.info("   ✅ Docker Compose command executed")
                result["method"] = "docker_compose"
                time.sleep(5)  # Wait for service to start

                # Verify
                if self._verify_ollama():
                    result["success"] = True
                    logger.info("   ✅ Ollama started and verified")
                    return result
        except FileNotFoundError:
            logger.info("   ⚠️  Docker Compose not found")
        except Exception as e:
            logger.warning(f"   ⚠️  Docker error: {e}")

        # Method 2: Try Ollama Desktop (Windows service)
        try:
            logger.info("Method 2: Checking Ollama Desktop...")
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'ollama' in proc.info['name'].lower():
                    logger.info("   ✅ Ollama Desktop process found")
                    result["method"] = "ollama_desktop"
                    if self._verify_ollama():
                        result["success"] = True
                        logger.info("   ✅ Ollama Desktop running and verified")
                        return result
        except ImportError:
            logger.info("   ⚠️  psutil not available")
        except Exception as e:
            logger.warning(f"   ⚠️  Process check error: {e}")

        # Method 3: Try direct Ollama service
        try:
            logger.info("Method 3: Starting Ollama service...")
            service_result = subprocess.run(
                ["net", "start", "Ollama"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if service_result.returncode == 0:
                result["method"] = "windows_service"
                time.sleep(3)
                if self._verify_ollama():
                    result["success"] = True
                    logger.info("   ✅ Ollama service started and verified")
                    return result
        except Exception as e:
            logger.warning(f"   ⚠️  Service start error: {e}")

        result["error"] = "Could not start Ollama - manual intervention required"
        logger.warning("   ❌ Could not start Ollama automatically")
        logger.info("   💡 Manual steps:")
        logger.info("      1. Start Ollama Desktop application")
        logger.info("      2. Or run: docker-compose up -d ollama")
        logger.info("")
        return result

    def start_iron_legion(self) -> Dict[str, Any]:
        """Start Iron Legion cluster"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING IRON LEGION (localhost:3000)")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "method": None,
            "success": False,
            "error": None
        }

        # Method 1: Try Docker Compose
        try:
            logger.info("Method 1: Starting Iron Legion via Docker Compose...")
            docker_result = subprocess.run(
                ["docker", "compose", "up", "-d", "iron-legion"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if docker_result.returncode == 0:
                logger.info("   ✅ Docker Compose command executed")
                result["method"] = "docker_compose"
                time.sleep(10)  # Wait for cluster to start

                # Verify
                if self._verify_iron_legion():
                    result["success"] = True
                    logger.info("   ✅ Iron Legion started and verified")
                    return result
        except FileNotFoundError:
            logger.info("   ⚠️  Docker Compose not found")
        except Exception as e:
            logger.warning(f"   ⚠️  Docker error: {e}")

        result["error"] = "Could not start Iron Legion - manual intervention required"
        logger.warning("   ❌ Could not start Iron Legion automatically")
        logger.info("   💡 Manual steps:")
        logger.info("      1. Run: docker-compose up -d iron-legion")
        logger.info("      2. Or start individual Iron Legion containers")
        logger.info("")
        return result

    def _verify_ollama(self) -> bool:
        """Verify Ollama is accessible"""
        try:
            response = requests.get(
                f"{self.endpoints['ollama']}/api/tags",
                timeout=3
            )
            return response.status_code == 200
        except:
            return False

    def _verify_iron_legion(self) -> bool:
        """Verify Iron Legion is accessible"""
        try:
            response = requests.get(
                f"{self.endpoints['iron_legion']}/v1/models",
                timeout=3
            )
            return response.status_code == 200
        except:
            return False

    def start_all_and_validate(self) -> Dict[str, Any]:
        """Start all services and validate models"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING ALL @HOMELAB LOCAL AI MODELS")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "docker_check": None,
            "ollama": None,
            "iron_legion": None,
            "validation": {
                "ollama_accessible": False,
                "iron_legion_accessible": False,
                "ollama_models": [],
                "iron_legion_models": []
            }
        }

        # Check Docker services
        results["docker_check"] = self.check_docker_services()

        # Start Ollama
        if not results["docker_check"]["ollama_running"]:
            results["ollama"] = self.start_ollama()
        else:
            logger.info("✅ Ollama already running")
            results["ollama"] = {"method": "already_running", "success": True}

        # Start Iron Legion
        if not results["docker_check"]["iron_legion_running"]:
            results["iron_legion"] = self.start_iron_legion()
        else:
            logger.info("✅ Iron Legion already running")
            results["iron_legion"] = {"method": "already_running", "success": True}

        # Validate models
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ VALIDATING MODELS")
        logger.info("=" * 80)
        logger.info("")

        # Validate Ollama
        if self._verify_ollama():
            results["validation"]["ollama_accessible"] = True
            try:
                response = requests.get(f"{self.endpoints['ollama']}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    results["validation"]["ollama_models"] = [m.get("name", "") for m in models]
                    logger.info(f"✅ Ollama: {len(results['validation']['ollama_models'])} models available")
                    for model in results["validation"]["ollama_models"]:
                        logger.info(f"   - {model}")
            except Exception as e:
                logger.warning(f"   ⚠️  Error getting Ollama models: {e}")
        else:
            logger.warning("   ❌ Ollama not accessible")

        # Validate Iron Legion
        if self._verify_iron_legion():
            results["validation"]["iron_legion_accessible"] = True
            try:
                response = requests.get(f"{self.endpoints['iron_legion']}/v1/models", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    results["validation"]["iron_legion_models"] = [m.get("id", "") for m in models]
                    logger.info(f"✅ Iron Legion: {len(results['validation']['iron_legion_models'])} models available")
                    for model in results["validation"]["iron_legion_models"]:
                        logger.info(f"   - {model}")
            except Exception as e:
                logger.warning(f"   ⚠️  Error getting Iron Legion models: {e}")
        else:
            logger.warning("   ❌ Iron Legion not accessible")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ STARTUP AND VALIDATION COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        return results


def main():
    """Main execution"""
    starter = HomelabLocalAIStarter(project_root)
    results = starter.start_all_and_validate()

    print("\n" + "=" * 80)
    print("📊 STARTUP SUMMARY")
    print("=" * 80)
    print()
    print(f"Ollama: {'✅ Accessible' if results['validation']['ollama_accessible'] else '❌ Not accessible'}")
    if results['validation']['ollama_models']:
        print(f"   Models: {len(results['validation']['ollama_models'])}")
    print()
    print(f"Iron Legion: {'✅ Accessible' if results['validation']['iron_legion_accessible'] else '❌ Not accessible'}")
    if results['validation']['iron_legion_models']:
        print(f"   Models: {len(results['validation']['iron_legion_models'])}")
    print()

    if not results['validation']['ollama_accessible'] or not results['validation']['iron_legion_accessible']:
        print("⚠️  Some services are not accessible. Check the logs above for details.")
        print()
        print("Manual start commands:")
        print("  Ollama: docker-compose up -d ollama")
        print("  Iron Legion: docker-compose up -d iron-legion")
        print("  Or start Ollama Desktop application")
    print()


if __name__ == "__main__":


    main()