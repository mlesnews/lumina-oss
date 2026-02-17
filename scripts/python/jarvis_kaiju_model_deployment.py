#!/usr/bin/env python3
"""
JARVIS KAIJU Model Deployment
Deploys hardware-appropriate models to KAIJU NAS based on its specifications

Tags: #DEPLOYMENT #KAIJU #MODELS @AUTO
"""

import sys
import requests
import paramiko
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
    from jarvis_hardware_aware_gpu_scaler import HardwareAwareGPUScaler
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    NASAzureVaultIntegration = None
    HardwareAwareGPUScaler = None

logger = get_logger("JARVISKAIJUModels")


class KAIJUModelDeployment:
    """
    Deploy hardware-appropriate models to KAIJU NAS

    KAIJU (Synology DS1821plus) typically has:
    - CPU-only (no GPU)
    - Limited RAM
    - Needs smaller, CPU-optimized models
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        # KAIJU_NO_8 = Desktop PC at <NAS_IP> (NOT the NAS at <NAS_PRIMARY_IP>)
        self.kaiju_ip = "<NAS_IP>"  # KAIJU_NO_8 Desktop PC
        self.kaiju_ollama_port = 11434

        # KAIJU-specific model recommendations (CPU-only, limited RAM)
        # Smaller models work better on NAS hardware
        self.kaiju_recommended_models = [
            "llama3.2:3b",      # Smallest, CPU-friendly
            "llama3.2:1b",       # Tiny, very fast
            "phi3:mini",         # Efficient CPU model
            "gemma:2b",          # Google's efficient model
            "mistral:7b",        # If RAM allows
        ]

        self.logger.info("✅ KAIJU Model Deployment initialized")

    def _get_kaiju_models(self) -> List[str]:
        """Get list of models currently on KAIJU"""
        try:
            response = requests.get(
                f"http://{self.kaiju_ip}:{self.kaiju_ollama_port}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
        except Exception as e:
            self.logger.warning(f"   ⚠️  Could not check KAIJU models: {e}")
        return []

    def _pull_model_to_kaiju(self, model_name: str) -> bool:
        """Pull a model to KAIJU via Ollama API"""
        self.logger.info(f"   📥 Pulling {model_name} to KAIJU...")

        try:
            response = requests.post(
                f"http://{self.kaiju_ip}:{self.kaiju_ollama_port}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600  # 10 minutes for large models
            )

            if response.status_code == 200:
                # Stream the download progress
                for line in response.iter_lines():
                    if line:
                        try:
                            data = line.decode('utf-8')
                            if '"status"' in data:
                                # Parse progress
                                import json
                                status = json.loads(data)
                                if "completed" in status and "total" in status:
                                    percent = (status["completed"] / status["total"]) * 100
                                    self.logger.info(f"      Progress: {percent:.1f}%")
                        except:
                            pass

                self.logger.info(f"   ✅ {model_name} pulled successfully to KAIJU")
                return True
            else:
                self.logger.error(f"   ❌ Failed to pull {model_name}: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"   ❌ Error pulling {model_name}: {e}")
            return False

    def deploy_appropriate_models(self) -> Dict[str, Any]:
        """Deploy hardware-appropriate models to KAIJU"""
        self.logger.info("="*80)
        self.logger.info("KAIJU MODEL DEPLOYMENT - HARDWARE APPROPRIATE")
        self.logger.info("="*80)

        # Check current models
        current_models = self._get_kaiju_models()
        self.logger.info(f"Current KAIJU models: {current_models if current_models else 'NONE'}")

        # Check which recommended models are missing
        missing_models = [m for m in self.kaiju_recommended_models if m not in current_models]

        if not missing_models:
            self.logger.info("   ✅ KAIJU already has appropriate models")
            return {
                "success": True,
                "message": "KAIJU has appropriate models",
                "current_models": current_models
            }

        self.logger.info(f"   📦 Need to pull {len(missing_models)} model(s): {', '.join(missing_models)}")

        # Pull the smallest recommended model first (best for NAS)
        model_to_pull = missing_models[0]
        self.logger.info(f"   🎯 Starting with smallest model: {model_to_pull}")

        if self._pull_model_to_kaiju(model_to_pull):
            final_models = self._get_kaiju_models()
            return {
                "success": True,
                "deployed_model": model_to_pull,
                "current_models": final_models
            }
        else:
            return {
                "success": False,
                "error": f"Failed to pull {model_to_pull}"
            }

    def sync_models_from_ultron(self) -> Dict[str, Any]:
        """
        Optionally sync appropriate models from ULTRON to KAIJU
        Only syncs models that fit KAIJU's hardware constraints
        """
        self.logger.info("="*80)
        self.logger.info("SYNC MODELS: ULTRON → KAIJU (Hardware Filtered)")
        self.logger.info("="*80)

        # Get ULTRON models
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                ultron_models = response.json().get("models", [])
                ultron_model_names = [m.get("name", "") for m in ultron_models]

                self.logger.info(f"ULTRON models: {ultron_model_names}")

                # Filter to only KAIJU-appropriate models
                appropriate_models = [
                    m for m in ultron_model_names 
                    if any(rec in m.lower() for rec in ["1b", "2b", "3b", "7b"])
                ]

                if not appropriate_models:
                    self.logger.warning("   ⚠️  No ULTRON models are appropriate for KAIJU hardware")
                    return {"success": False, "error": "No appropriate models on ULTRON"}

                self.logger.info(f"   ✅ Found {len(appropriate_models)} KAIJU-appropriate models on ULTRON")

                # Note: Ollama doesn't support direct model sync between instances
                # Models must be pulled from registry on each system
                self.logger.info("   📝 Note: Models must be pulled separately on each system")
                self.logger.info("   📝 KAIJU will pull from Ollama registry (same model names)")

                return {
                    "success": True,
                    "appropriate_models": appropriate_models,
                    "note": "Pull models separately on each system"
                }
        except Exception as e:
            self.logger.error(f"   ❌ Could not check ULTRON models: {e}")
            return {"success": False, "error": str(e)}


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Deploy models to KAIJU")
        parser.add_argument("--deploy", action="store_true", help="Deploy appropriate models")
        parser.add_argument("--sync", action="store_true", help="Check sync options from ULTRON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        deployer = KAIJUModelDeployment(project_root)

        if args.sync:
            result = deployer.sync_models_from_ultron()
            print(f"Sync check: {result}")
        elif args.deploy:
            result = deployer.deploy_appropriate_models()
            print(f"Deployment: {result}")
        else:
            # Default: deploy
            result = deployer.deploy_appropriate_models()
            print(f"Deployment: {result}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()