#!/usr/bin/env python3
"""
NAS Migration Auto-Execute - Autonomous Execution

Automatically executes safe migration steps without user intervention.

Tags: #NAS_MIGRATION #AUTO_EXECUTE #AUTONOMOUS @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

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

logger = get_logger("NASMigrationAutoExecute")


class AutoExecutor:
    """Autonomous execution of NAS migration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        self.execution_log = []

    def check_nas_connectivity(self) -> bool:
        """Check if NAS is reachable"""
        logger.info("🔍 Checking NAS connectivity...")
        try:
            result = subprocess.run(
                ["ping", "-n", "1", self.nas_ip],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"   ✅ NAS reachable: {self.nas_ip}")
                return True
            else:
                logger.warning(f"   ❌ NAS not reachable: {self.nas_ip}")
                return False
        except Exception as e:
            logger.warning(f"   ⚠️  Connectivity check failed: {e}")
            return False

    def map_network_drives(self) -> Dict:
        """Map network drives automatically"""
        logger.info("=" * 80)
        logger.info("📁 MAPPING NETWORK DRIVES")
        logger.info("=" * 80)
        logger.info("")

        drives = {
            "H": f"{self.nas_base}\\homes\\mlesn",
            "M": f"{self.nas_base}\\data\\models",
            "D": f"{self.nas_base}\\data\\docker",
            "V": f"{self.nas_base}\\data\\media",
            "C": f"{self.nas_base}\\data\\cache",
            "P": f"{self.nas_base}\\pxe"
        }

        results = {}

        for drive_letter, path in drives.items():
            logger.info(f"Mapping {drive_letter}: to {path}...")
            try:
                # Check if already mapped
                drive_path = Path(f"{drive_letter}:")
                if drive_path.exists():
                    logger.info(f"   ✅ {drive_letter}: already mapped")
                    results[drive_letter] = {"status": "already_mapped", "path": path}
                    continue

                # Map drive
                ps_command = f'net use {drive_letter}: "{path}" /persistent:yes'
                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 or "successfully" in result.stdout.lower():
                    logger.info(f"   ✅ {drive_letter}: mapped successfully")
                    results[drive_letter] = {"status": "mapped", "path": path}
                    self.execution_log.append(f"Mapped drive {drive_letter}: to {path}")
                else:
                    logger.warning(f"   ⚠️  {drive_letter}: mapping failed (share may not exist)")
                    results[drive_letter] = {"status": "failed", "path": path, "error": result.stderr}
            except Exception as e:
                logger.warning(f"   ⚠️  {drive_letter}: error: {e}")
                results[drive_letter] = {"status": "error", "path": path, "error": str(e)}

        logger.info("")
        return results

    def set_environment_variables(self) -> Dict:
        """Set environment variables for application redirection"""
        logger.info("=" * 80)
        logger.info("🔧 SETTING ENVIRONMENT VARIABLES")
        logger.info("=" * 80)
        logger.info("")

        env_vars = {
            "PIP_CACHE_DIR": f"{self.nas_base}\\data\\cache\\pip",
            "npm_config_cache": f"{self.nas_base}\\data\\cache\\npm",
            "OLLAMA_MODELS": f"{self.nas_base}\\data\\models\\ollama"
        }

        results = {}

        for var_name, var_value in env_vars.items():
            logger.info(f"Setting {var_name}...")
            try:
                # Set for current user
                ps_command = f'[Environment]::SetEnvironmentVariable("{var_name}", "{var_value}", "User")'
                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    logger.info(f"   ✅ {var_name} = {var_value}")
                    results[var_name] = {"status": "set", "value": var_value}
                    self.execution_log.append(f"Set environment variable {var_name}")
                else:
                    logger.warning(f"   ⚠️  Failed to set {var_name}: {result.stderr}")
                    results[var_name] = {"status": "failed", "error": result.stderr}
            except Exception as e:
                logger.warning(f"   ⚠️  Error setting {var_name}: {e}")
                results[var_name] = {"status": "error", "error": str(e)}

        logger.info("")
        return results

    def create_local_symlinks(self) -> Dict:
        """Create symlinks for applications requiring local paths"""
        logger.info("=" * 80)
        logger.info("🔗 CREATING SYMLINKS")
        logger.info("=" * 80)
        logger.info("")

        # Only create symlinks if target exists
        symlinks = []

        # Check if NAS shares exist before creating symlinks
        nas_ollama = Path(f"{self.nas_base}\\data\\models\\ollama")
        if nas_ollama.exists():
            symlinks.append({
                "target": str(nas_ollama),
                "link": "C:\\Users\\mlesn\\AppData\\Local\\Ollama\\nas_models",
                "description": "Ollama models symlink"
            })

        results = {}

        for symlink_info in symlinks:
            logger.info(f"Creating symlink: {symlink_info['description']}...")
            try:
                link_path = Path(symlink_info["link"])
                target_path = Path(symlink_info["target"])

                # Create parent directory
                link_path.parent.mkdir(parents=True, exist_ok=True)

                # Remove existing if exists
                if link_path.exists() or link_path.is_symlink():
                    link_path.unlink()

                # Create symlink (requires admin, so we'll just prepare)
                logger.info(f"   📝 Symlink prepared: {link_path} -> {target_path}")
                logger.info(f"   ⚠️  Run as Administrator to create: mklink /D \"{link_path}\" \"{target_path}\"")
                results[symlink_info["link"]] = {
                    "status": "prepared",
                    "target": symlink_info["target"],
                    "command": f'mklink /D "{link_path}" "{target_path}"'
                }
            except Exception as e:
                logger.warning(f"   ⚠️  Error: {e}")
                results[symlink_info["link"]] = {"status": "error", "error": str(e)}

        logger.info("")
        return results

    def verify_ollama_config(self) -> Dict:
        """Verify and configure Ollama to use NAS models"""
        logger.info("=" * 80)
        logger.info("🤖 VERIFYING OLLAMA CONFIGURATION")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "nas_models_exist": False,
            "local_models_exist": False,
            "env_var_set": False,
            "recommendations": []
        }

        # Check NAS models
        nas_models = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels")
        if nas_models.exists():
            result["nas_models_exist"] = True
            logger.info(f"✅ Ollama models found on NAS: {nas_models}")

            # Set environment variable to use NAS
            nas_target = f"{self.nas_base}\\data\\models\\ollama"
            try:
                ps_command = f'[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "{nas_target}", "User")'
                subprocess.run(["powershell", "-Command", ps_command], timeout=5)
                result["env_var_set"] = True
                logger.info(f"   ✅ Set OLLAMA_MODELS to {nas_target}")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not set env var: {e}")
        else:
            logger.warning(f"❌ NAS models not found: {nas_models}")

        # Check local models
        local_models = Path("C:\\Users\\mlesn\\AppData\\Local\\Ollama")
        if local_models.exists():
            result["local_models_exist"] = True
            logger.info(f"Local models: {local_models}")

        logger.info("")
        return result

    def execute_autonomous_steps(self) -> Dict:
        try:
            """Execute all autonomous migration steps"""
            logger.info("=" * 80)
            logger.info("🚀 AUTONOMOUS NAS MIGRATION EXECUTION")
            logger.info("=" * 80)
            logger.info("")

            execution_results = {
                "timestamp": datetime.now().isoformat(),
                "steps_completed": [],
                "steps_failed": [],
                "steps_skipped": [],
                "execution_log": []
            }

            # Step 1: Check connectivity
            if self.check_nas_connectivity():
                execution_results["steps_completed"].append("nas_connectivity_check")
            else:
                execution_results["steps_failed"].append("nas_connectivity_check")
                logger.error("❌ NAS not reachable - cannot proceed")
                return execution_results

            # Step 2: Map network drives
            drive_results = self.map_network_drives()
            execution_results["drive_mapping"] = drive_results
            mapped_count = sum(1 for r in drive_results.values() if r.get("status") in ["mapped", "already_mapped"])
            if mapped_count > 0:
                execution_results["steps_completed"].append("network_drive_mapping")

            # Step 3: Set environment variables
            env_results = self.set_environment_variables()
            execution_results["environment_variables"] = env_results
            set_count = sum(1 for r in env_results.values() if r.get("status") == "set")
            if set_count > 0:
                execution_results["steps_completed"].append("environment_variables")

            # Step 4: Verify Ollama
            ollama_results = self.verify_ollama_config()
            execution_results["ollama_config"] = ollama_results
            if ollama_results.get("env_var_set"):
                execution_results["steps_completed"].append("ollama_configuration")

            # Step 5: Prepare symlinks
            symlink_results = self.create_local_symlinks()
            execution_results["symlinks"] = symlink_results

            # Save execution log
            execution_results["execution_log"] = self.execution_log

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.data_dir / f"auto_execution_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(execution_results, f, indent=2)

            logger.info("=" * 80)
            logger.info("✅ AUTONOMOUS EXECUTION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"💾 Results saved: {results_file}")
            logger.info("")
            logger.info(f"✅ Steps completed: {len(execution_results['steps_completed'])}")
            logger.info(f"❌ Steps failed: {len(execution_results['steps_failed'])}")
            logger.info("")

            return execution_results


        except Exception as e:
            self.logger.error(f"Error in execute_autonomous_steps: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    executor = AutoExecutor(project_root)
    results = executor.execute_autonomous_steps()

    print("\n" + "=" * 80)
    print("📊 AUTONOMOUS EXECUTION SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Completed: {len(results['steps_completed'])} steps")
    print(f"❌ Failed: {len(results['steps_failed'])} steps")
    print()
    print("Next steps (manual):")
    print("  1. Create NAS shares via DSM GUI (if not exist)")
    print("  2. Run PowerShell scripts for folder redirection (as Admin)")
    print("  3. Migrate Docker volumes (stop Docker first)")
    print()


if __name__ == "__main__":


    main()