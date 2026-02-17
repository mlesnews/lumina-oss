#!/usr/bin/env python3
"""
Autonomous @HOMELAB Local AI Startup

AI self-directed, self-assigned work to ensure all local AI models are running
and validated on all @HOMELAB localhosts.

Tags: #HOMELAB #AUTONOMOUS #AI_SELF_DIRECTED #LOCAL_AI @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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

logger = get_logger("AutonomousHomelabAI")


class AutonomousHomelabAIStartup:
    """Autonomous startup and validation of all @HOMELAB local AI models"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "homelab_model_validation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.endpoints = {
            "ollama": "http://localhost:11434",
            "iron_legion": "http://localhost:3000"
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "services_started": [],
            "services_failed": [],
            "models_validated": {},
            "fixes_applied": []
        }

    def autonomous_startup_sequence(self) -> Dict[str, Any]:
        try:
            """Autonomous startup sequence - AI self-directed"""
            logger.info("=" * 80)
            logger.info("🤖 AUTONOMOUS @HOMELAB LOCAL AI STARTUP")
            logger.info("=" * 80)
            logger.info("")
            logger.info("AI Self-Directed Work: Ensuring all local AI models operational")
            logger.info("")

            # Step 1: Diagnose current state
            logger.info("Step 1: Diagnosing current state...")
            diagnosis = self._diagnose_services()
            logger.info("")

            # Step 2: Start Ollama
            if not diagnosis["ollama_accessible"]:
                logger.info("Step 2: Starting Ollama...")
                ollama_result = self._start_ollama_autonomous()
                if ollama_result["success"]:
                    self.results["services_started"].append("ollama")
                else:
                    self.results["services_failed"].append({"service": "ollama", "error": ollama_result.get("error")})
                logger.info("")
            else:
                logger.info("Step 2: Ollama already running ✅")
                logger.info("")

            # Step 3: Start Iron Legion
            if not diagnosis["iron_legion_accessible"]:
                logger.info("Step 3: Starting Iron Legion...")
                iron_legion_result = self._start_iron_legion_autonomous()
                if iron_legion_result["success"]:
                    self.results["services_started"].append("iron_legion")
                else:
                    self.results["services_failed"].append({"service": "iron_legion", "error": iron_legion_result.get("error")})
                logger.info("")
            else:
                logger.info("Step 3: Iron Legion already running ✅")
                logger.info("")

            # Step 4: Validate all models
            logger.info("Step 4: Validating all models...")
            validation = self._validate_all_models()
            self.results["models_validated"] = validation
            logger.info("")

            # Step 5: Fix any invalid model references
            logger.info("Step 5: Fixing invalid model references...")
            fixes = self._fix_invalid_references()
            self.results["fixes_applied"] = fixes
            logger.info("")

            # Step 6: Final validation
            logger.info("Step 6: Final validation...")
            final_check = self._final_validation()
            logger.info("")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.data_dir / f"autonomous_startup_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)

            logger.info("=" * 80)
            logger.info("✅ AUTONOMOUS STARTUP COMPLETE")
            logger.info("=" * 80)
            logger.info("")
            logger.info(f"✅ Services started: {len(self.results['services_started'])}")
            logger.info(f"❌ Services failed: {len(self.results['services_failed'])}")
            logger.info(f"✅ Models validated: {sum(len(v.get('models', [])) for v in self.results['models_validated'].values())}")
            logger.info(f"🔧 Fixes applied: {len(self.results['fixes_applied'])}")
            logger.info("")
            logger.info(f"💾 Results saved: {results_file}")
            logger.info("")

            return self.results

        except Exception as e:
            self.logger.error(f"Error in autonomous_startup_sequence: {e}", exc_info=True)
            raise
    def _diagnose_services(self) -> Dict[str, bool]:
        """Diagnose service accessibility"""
        diagnosis = {
            "ollama_accessible": False,
            "iron_legion_accessible": False
        }

        # Check Ollama
        try:
            response = requests.get(f"{self.endpoints['ollama']}/api/tags", timeout=3)
            if response.status_code == 200:
                diagnosis["ollama_accessible"] = True
                logger.info("   ✅ Ollama accessible")
            else:
                logger.info(f"   ⚠️  Ollama returned {response.status_code}")
        except:
            logger.info("   ❌ Ollama not accessible")

        # Check Iron Legion
        try:
            response = requests.get(f"{self.endpoints['iron_legion']}/v1/models", timeout=3)
            if response.status_code == 200:
                diagnosis["iron_legion_accessible"] = True
                logger.info("   ✅ Iron Legion accessible")
            else:
                logger.info(f"   ⚠️  Iron Legion returned {response.status_code}")
        except:
            logger.info("   ❌ Iron Legion not accessible")

        return diagnosis

    def _start_ollama_autonomous(self) -> Dict[str, Any]:
        """Autonomously start Ollama using all available methods"""
        result = {"success": False, "method": None, "error": None}

        # Method 1: Docker Compose
        try:
            docker_compose_files = [
                self.project_root / "containerization" / "docker-compose.yml",
                self.project_root / "docker-compose.yml"
            ]

            for compose_file in docker_compose_files:
                if compose_file.exists():
                    logger.info(f"   Trying Docker Compose: {compose_file.name}")
                    proc = subprocess.run(
                        ["docker", "compose", "-f", str(compose_file), "up", "-d", "ollama"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if proc.returncode == 0:
                        time.sleep(5)
                        if self._verify_endpoint(self.endpoints["ollama"]):
                            result["success"] = True
                            result["method"] = "docker_compose"
                            logger.info("   ✅ Ollama started via Docker Compose")
                            return result
        except Exception as e:
            logger.debug(f"   Docker Compose failed: {e}")

        # Method 2: Ollama Desktop executable
        ollama_paths = [
            Path("C:/Program Files/Ollama/ollama.exe"),
            Path("C:/Program Files (x86)/Ollama/ollama.exe"),
            Path.home() / "AppData/Local/Programs/Ollama/ollama.exe"
        ]

        for ollama_path in ollama_paths:
            if ollama_path.exists():
                try:
                    logger.info(f"   Trying Ollama Desktop: {ollama_path}")
                    subprocess.Popen([str(ollama_path)], shell=True)
                    time.sleep(5)
                    if self._verify_endpoint(self.endpoints["ollama"]):
                        result["success"] = True
                        result["method"] = "ollama_desktop"
                        logger.info("   ✅ Ollama started via Desktop")
                        return result
                except Exception as e:
                    logger.debug(f"   Ollama Desktop failed: {e}")

        # Method 3: Windows Service
        try:
            logger.info("   Trying Windows Service...")
            proc = subprocess.run(
                ["net", "start", "Ollama"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                time.sleep(3)
                if self._verify_endpoint(self.endpoints["ollama"]):
                    result["success"] = True
                    result["method"] = "windows_service"
                    logger.info("   ✅ Ollama started via Windows Service")
                    return result
        except Exception as e:
            logger.debug(f"   Windows Service failed: {e}")

        result["error"] = "All startup methods failed"
        logger.warning("   ❌ Could not start Ollama automatically")
        return result

    def _start_iron_legion_autonomous(self) -> Dict[str, Any]:
        """Autonomously start Iron Legion"""
        result = {"success": False, "method": None, "error": None}

        # Method 1: Docker Compose
        try:
            docker_compose_files = [
                self.project_root / "containerization" / "docker-compose.yml",
                self.project_root / "docker-compose.yml"
            ]

            for compose_file in docker_compose_files:
                if compose_file.exists():
                    logger.info(f"   Trying Docker Compose: {compose_file.name}")
                    proc = subprocess.run(
                        ["docker", "compose", "-f", str(compose_file), "up", "-d", "iron-legion"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if proc.returncode == 0:
                        time.sleep(10)
                        if self._verify_endpoint(self.endpoints["iron_legion"]):
                            result["success"] = True
                            result["method"] = "docker_compose"
                            logger.info("   ✅ Iron Legion started via Docker Compose")
                            return result
        except Exception as e:
            logger.debug(f"   Docker Compose failed: {e}")

        result["error"] = "Could not start Iron Legion automatically"
        logger.warning("   ❌ Could not start Iron Legion automatically")
        return result

    def _verify_endpoint(self, endpoint: str) -> bool:
        """Verify endpoint is accessible"""
        try:
            if "11434" in endpoint:
                response = requests.get(f"{endpoint}/api/tags", timeout=3)
            else:
                response = requests.get(f"{endpoint}/v1/models", timeout=3)
            return response.status_code == 200
        except:
            return False

    def _validate_all_models(self) -> Dict[str, Any]:
        """Validate all available models"""
        validation = {
            "ollama": {"accessible": False, "models": []},
            "iron_legion": {"accessible": False, "models": []}
        }

        # Validate Ollama
        try:
            response = requests.get(f"{self.endpoints['ollama']}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                validation["ollama"]["accessible"] = True
                validation["ollama"]["models"] = [m.get("name", "") for m in models]
                logger.info(f"   ✅ Ollama: {len(validation['ollama']['models'])} models")
        except Exception as e:
            logger.warning(f"   ❌ Ollama validation failed: {e}")

        # Validate Iron Legion
        try:
            response = requests.get(f"{self.endpoints['iron_legion']}/v1/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                validation["iron_legion"]["accessible"] = True
                validation["iron_legion"]["models"] = [m.get("id", "") for m in models]
                logger.info(f"   ✅ Iron Legion: {len(validation['iron_legion']['models'])} models")
        except Exception as e:
            logger.warning(f"   ❌ Iron Legion validation failed: {e}")

        return validation

    def _fix_invalid_references(self) -> List[Dict[str, Any]]:
        """Fix invalid model references in config files"""
        fixes = []

        # Import the fixer
        try:
            from fix_homelab_invalid_model_error import HomelabModelValidator
            fixer = HomelabModelValidator(self.project_root)

            # Check models first
            fixer.check_ollama_models()
            fixer.check_iron_legion_models()

            # Scan and fix
            invalid_refs = fixer.scan_config_files_for_invalid_models()
            if invalid_refs:
                fix_results = fixer.fix_invalid_models()
                fixes.append({
                    "invalid_refs_found": len(invalid_refs),
                    "files_fixed": fix_results.get("files_fixed", 0),
                    "models_fixed": fix_results.get("models_fixed", 0)
                })
                logger.info(f"   ✅ Fixed {fix_results.get('models_fixed', 0)} invalid model references")
            else:
                logger.info("   ✅ No invalid model references found")
        except Exception as e:
            logger.warning(f"   ⚠️  Error fixing references: {e}")

        return fixes

    def _final_validation(self) -> Dict[str, Any]:
        """Final validation of all services"""
        final = {
            "ollama": {"status": "UNKNOWN", "models": 0},
            "iron_legion": {"status": "UNKNOWN", "models": 0},
            "all_operational": False
        }

        # Final Ollama check
        try:
            response = requests.get(f"{self.endpoints['ollama']}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                final["ollama"]["status"] = "OPERATIONAL"
                final["ollama"]["models"] = len(models)
                logger.info(f"   ✅ Ollama: OPERATIONAL ({len(models)} models)")
            else:
                final["ollama"]["status"] = "ERROR"
                logger.warning(f"   ❌ Ollama: ERROR (HTTP {response.status_code})")
        except Exception as e:
            final["ollama"]["status"] = "NOT_ACCESSIBLE"
            logger.warning(f"   ❌ Ollama: NOT ACCESSIBLE")

        # Final Iron Legion check
        try:
            response = requests.get(f"{self.endpoints['iron_legion']}/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json().get("data", [])
                final["iron_legion"]["status"] = "OPERATIONAL"
                final["iron_legion"]["models"] = len(models)
                logger.info(f"   ✅ Iron Legion: OPERATIONAL ({len(models)} models)")
            else:
                final["iron_legion"]["status"] = "ERROR"
                logger.warning(f"   ❌ Iron Legion: ERROR (HTTP {response.status_code})")
        except Exception as e:
            final["iron_legion"]["status"] = "NOT_ACCESSIBLE"
            logger.warning(f"   ❌ Iron Legion: NOT ACCESSIBLE")

        # Overall status
        final["all_operational"] = (
            final["ollama"]["status"] == "OPERATIONAL" and
            final["iron_legion"]["status"] == "OPERATIONAL"
        )

        if final["all_operational"]:
            logger.info("   ✅ ALL SERVICES OPERATIONAL")
        else:
            logger.warning("   ⚠️  Some services not operational")

        return final


def main():
    """Main autonomous execution"""
    startup = AutonomousHomelabAIStartup(project_root)
    results = startup.autonomous_startup_sequence()

    print("\n" + "=" * 80)
    print("🤖 AUTONOMOUS STARTUP SUMMARY")
    print("=" * 80)
    print()
    print(f"Services started: {len(results['services_started'])}")
    print(f"Services failed: {len(results['services_failed'])}")
    print(f"Models validated: {sum(len(v.get('models', [])) for v in results['models_validated'].values())}")
    print(f"Fixes applied: {len(results['fixes_applied'])}")
    print()

    if results['services_failed']:
        print("⚠️  Some services could not be started automatically:")
        for failure in results['services_failed']:
            print(f"   - {failure['service']}: {failure.get('error', 'Unknown error')}")
        print()
        print("Manual intervention may be required.")
    print()


if __name__ == "__main__":


    main()