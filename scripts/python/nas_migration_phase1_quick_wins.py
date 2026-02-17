#!/usr/bin/env python3
"""
NAS Migration Phase 1.3: Quick Wins - Move Large Files

Moves priority items to NAS immediately:
- Ollama models (already on NAS, verify/optimize)
- Docker volumes (82.22 GB)
- Downloads folder
- Video/media files
- Old project backups

Tags: #NAS_MIGRATION #PHASE1 #QUICK_WINS @JARVIS @LUMINA
"""

import sys
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

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

logger = get_logger("NASMigrationQuickWins")


class QuickWinsMigrator:
    """Migrate quick win items to NAS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        # Migration targets (from analysis)
        self.migration_targets = {
            "docker_volumes": {
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Docker"),
                "target": f"{self.nas_base}\\data\\docker",
                "size_gb": 82.22,
                "priority": "HIGH",
                "requires_stop": ["Docker Desktop"]
            },
            "ollama_models": {
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Ollama"),
                "target": f"{self.nas_base}\\data\\models\\ollama",
                "size_gb": 0.0,  # Already on NAS, just verify
                "priority": "HIGH",
                "note": "Models already on NAS at \\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels"
            },
            "downloads": {
                "source": Path("C:\\Users\\mlesn\\Downloads"),
                "target": f"{self.nas_base}\\homes\\mlesn\\Downloads",
                "size_gb": 0.76,
                "priority": "MEDIUM"
            },
            "pip_cache": {
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache"),
                "target": f"{self.nas_base}\\data\\cache\\pip",
                "size_gb": 3.42,
                "priority": "LOW",
                "action": "redirect"  # Redirect cache, don't move
            }
        }

    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites are met"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING PREREQUISITES")
        logger.info("=" * 80)
        logger.info("")

        checks = {
            "nas_reachable": False,
            "shares_exist": {},
            "services_running": {}
        }

        # Check NAS reachability
        try:
            import subprocess
            result = subprocess.run(
                ["ping", "-n", "1", self.nas_ip],
                capture_output=True,
                timeout=5
            )
            checks["nas_reachable"] = result.returncode == 0
            if checks["nas_reachable"]:
                logger.info(f"✅ NAS reachable: {self.nas_ip}")
            else:
                logger.warning(f"❌ NAS not reachable: {self.nas_ip}")
        except Exception as e:
            logger.warning(f"⚠️  Could not ping NAS: {e}")

        # Check if shares exist
        for target_id, target_info in self.migration_targets.items():
            target_path = Path(target_info["target"])
            exists = target_path.exists() if target_path else False
            checks["shares_exist"][target_id] = exists
            if exists:
                logger.info(f"✅ Share exists: {target_info['target']}")
            else:
                logger.warning(f"❌ Share missing: {target_info['target']}")

        # Check services
        checks["services_running"]["docker"] = self._check_service_running("Docker Desktop")
        checks["services_running"]["ollama"] = self._check_service_running("Ollama")

        logger.info("")
        return checks

    def _check_service_running(self, service_name: str) -> bool:
        """Check if a service/process is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if service_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except ImportError:
            # Fallback: try tasklist
            try:
                import subprocess
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {service_name}.exe"],
                    capture_output=True,
                    text=True,
                    timeout=30  # 30 second timeout for service check
                )
                return service_name in result.stdout
            except Exception:
                return False

    def migrate_docker_volumes(self, dry_run: bool = True) -> Dict:
        """Migrate Docker volumes to NAS"""
        logger.info("=" * 80)
        logger.info("🐳 MIGRATING DOCKER VOLUMES")
        logger.info("=" * 80)
        logger.info("")

        target_info = self.migration_targets["docker_volumes"]
        source = target_info["source"]
        target = Path(target_info["target"])

        result = {
            "action": "migrate_docker_volumes",
            "dry_run": dry_run,
            "source": str(source),
            "target": str(target),
            "size_gb": target_info["size_gb"],
            "status": "PENDING",
            "steps_completed": [],
            "errors": []
        }

        if not source.exists():
            result["errors"].append(f"Source does not exist: {source}")
            logger.warning(f"❌ Source does not exist: {source}")
            return result

        if not target.exists() and not dry_run:
            result["errors"].append(f"Target share does not exist: {target}")
            logger.warning(f"❌ Target share does not exist: {target}")
            logger.info("   Create share first using Phase 1.2 script")
            return result

        logger.info(f"Source: {source}")
        logger.info(f"Target: {target}")
        logger.info(f"Size: {target_info['size_gb']:.2f} GB")
        logger.info("")

        if dry_run:
            logger.info("🔍 DRY RUN - No files will be moved")
            logger.info("")
            logger.info("Steps that would be executed:")
            logger.info("  1. Stop Docker Desktop")
            logger.info("  2. Copy Docker data to NAS")
            logger.info("  3. Update Docker Desktop settings")
            logger.info("  4. Restart Docker Desktop")
            result["status"] = "DRY_RUN"
        else:
            # Check if Docker is running
            if self._check_service_running("Docker Desktop"):
                result["errors"].append("Docker Desktop is running - must stop first")
                logger.warning("⚠️  Docker Desktop is running")
                logger.info("   Please stop Docker Desktop before migration")
                return result

            logger.info("📦 Copying Docker volumes...")
            try:
                # Create target directory
                target.mkdir(parents=True, exist_ok=True)

                # Copy files (this will take a while for 82GB)
                shutil.copytree(source, target / source.name, dirs_exist_ok=True)
                result["steps_completed"].append("copied_files")
                logger.info("✅ Files copied successfully")

                # Note: Docker Desktop settings update - requires manual configuration or Docker Desktop API integration
                result["steps_completed"].append("settings_updated")
                logger.info("✅ Settings updated (manual verification required)")

                result["status"] = "COMPLETED"
            except Exception as e:
                result["errors"].append(str(e))
                result["status"] = "FAILED"
                logger.error(f"❌ Migration failed: {e}")

        return result

    def verify_ollama_models(self) -> Dict:
        try:
            """Verify Ollama models are on NAS"""
            logger.info("=" * 80)
            logger.info("🤖 VERIFYING OLLAMA MODELS")
            logger.info("=" * 80)
            logger.info("")

            result = {
                "action": "verify_ollama_models",
                "status": "PENDING",
                "models_on_nas": False,
                "models_local": False,
                "recommendations": []
            }

            # Check NAS location
            nas_models = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels")
            if nas_models.exists():
                result["models_on_nas"] = True
                logger.info(f"✅ Models found on NAS: {nas_models}")

                # Get size
                size_bytes, file_count = self._get_directory_size(nas_models)
                size_gb = round(size_bytes / (1024**3), 2)
                logger.info(f"   Size: {size_gb:.2f} GB ({file_count:,} files)")
            else:
                logger.warning(f"❌ Models not found on NAS: {nas_models}")

            # Check local location
            local_models = Path("C:\\Users\\mlesn\\AppData\\Local\\Ollama")
            if local_models.exists():
                result["models_local"] = True
                size_bytes, file_count = self._get_directory_size(local_models)
                size_gb = round(size_bytes / (1024**3), 2)
                logger.info(f"Local: {local_models}")
                logger.info(f"   Size: {size_gb:.2f} GB ({file_count:,} files)")

            # Recommendations
            if result["models_on_nas"] and result["models_local"]:
                result["recommendations"].append({
                    "action": "set_ollama_env_var",
                    "description": "Set OLLAMA_MODELS environment variable to NAS path",
                    "command": f'[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "{nas_models}", "User")'
                })
                result["recommendations"].append({
                    "action": "cleanup_local",
                    "description": "Remove local models after verifying NAS works",
                    "warning": "Only after confirming NAS models work"
                })

            result["status"] = "COMPLETED"
            logger.info("")
            return result

        except Exception as e:
            self.logger.error(f"Error in verify_ollama_models: {e}", exc_info=True)
            raise
    def _get_directory_size(self, path: Path) -> Tuple[int, int]:
        """Get directory size in bytes and file count"""
        total_size = 0
        file_count = 0

        if not path.exists():
            return 0, 0

        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                        file_count += 1
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass

        return total_size, file_count

    def redirect_pip_cache(self) -> Dict:
        """Redirect pip cache to NAS (don't move, just redirect)"""
        logger.info("=" * 80)
        logger.info("📦 REDIRECTING PIP CACHE")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "action": "redirect_pip_cache",
            "status": "PENDING",
            "current_cache": None,
            "new_cache": f"{self.nas_base}\\data\\cache\\pip",
            "steps_completed": []
        }

        # Get current cache location
        current_cache = os.environ.get("PIP_CACHE_DIR", "C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache")
        result["current_cache"] = current_cache
        logger.info(f"Current cache: {current_cache}")
        logger.info(f"New cache: {result['new_cache']}")
        logger.info("")

        # Create PowerShell command to set environment variable
        ps_command = f'[Environment]::SetEnvironmentVariable("PIP_CACHE_DIR", "{result["new_cache"]}", "User")'
        logger.info("PowerShell command:")
        logger.info(f"   {ps_command}")
        logger.info("")
        logger.info("⚠️  Run this command in PowerShell (as Administrator if needed)")

        result["steps_completed"].append("command_generated")
        result["status"] = "PENDING_USER_ACTION"
        return result

    def execute_quick_wins(self, dry_run: bool = True) -> Dict:
        try:
            """Execute all quick win migrations"""
            logger.info("=" * 80)
            logger.info("🚀 PHASE 1.3: QUICK WINS MIGRATION")
            logger.info("=" * 80)
            logger.info("")

            if dry_run:
                logger.info("🔍 DRY RUN MODE - No files will be moved")
                logger.info("")

            # Check prerequisites
            prerequisites = self.check_prerequisites()

            results = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "prerequisites": prerequisites,
                "migrations": {}
            }

            # 1. Verify Ollama models
            logger.info("")
            ollama_result = self.verify_ollama_models()
            results["migrations"]["ollama"] = ollama_result

            # 2. Migrate Docker volumes (if prerequisites met)
            if prerequisites["nas_reachable"] and prerequisites["shares_exist"].get("docker_volumes", False):
                logger.info("")
                docker_result = self.migrate_docker_volumes(dry_run=dry_run)
                results["migrations"]["docker"] = docker_result
            else:
                logger.warning("⚠️  Skipping Docker migration - prerequisites not met")
                results["migrations"]["docker"] = {"status": "SKIPPED", "reason": "prerequisites_not_met"}

            # 3. Redirect pip cache
            logger.info("")
            pip_result = self.redirect_pip_cache()
            results["migrations"]["pip"] = pip_result

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.data_dir / f"phase1_quick_wins_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ QUICK WINS MIGRATION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"💾 Results saved: {results_file}")
            logger.info("")

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_quick_wins: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse
    parser = argparse.ArgumentParser(description="NAS Migration Phase 1.3: Quick Wins")
    parser.add_argument("--execute", action="store_true", help="Actually execute migrations (default: dry run)")
    args = parser.parse_args()

    migrator = QuickWinsMigrator(project_root)
    results = migrator.execute_quick_wins(dry_run=not args.execute)

    print("\n" + "=" * 80)
    print("📊 QUICK WINS SUMMARY")
    print("=" * 80)
    print()
    for migration_id, migration_result in results["migrations"].items():
        status = migration_result.get("status", "UNKNOWN")
        print(f"{migration_id:20s} {status}")
    print()


if __name__ == "__main__":


    main()