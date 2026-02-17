#!/usr/bin/env python3
"""
JARVIS Emergency Space Cleanup
Aggressive cleanup for critical space situations (100% disk full).

Tags: #EMERGENCY #CLEANUP #SPACE @AUTO
"""

import sys
import subprocess
import shutil
import os
from pathlib import Path
from typing import Dict, Any, List
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

logger = get_logger("JARVISEmergencyCleanup")


class EmergencySpaceCleanup:
    """Emergency space cleanup for critical situations"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.username = os.getenv("USERNAME", "mlesn")
        self.logger.info("✅ Emergency Space Cleanup initialized")

    def cleanup_docker_aggressive(self) -> Dict[str, Any]:
        """Aggressive Docker cleanup"""
        self.logger.info("1. Aggressive Docker cleanup...")
        freed_gb = 0.0

        try:
            # Stop all containers
            subprocess.run(["docker", "stop", "$(docker ps -q)"], shell=True, capture_output=True, timeout=60)

            # Remove all stopped containers
            result = subprocess.run(
                ["docker", "container", "prune", "-f"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if "Total reclaimed space:" in result.stdout:
                space_str = result.stdout.split("Total reclaimed space:")[1].strip().split('\n')[0].strip()
                freed_gb += self._parse_docker_space(space_str)

            # Remove all unused images
            result = subprocess.run(
                ["docker", "image", "prune", "-a", "-f"],
                capture_output=True,
                text=True,
                timeout=300
            )
            if "Total reclaimed space:" in result.stdout:
                space_str = result.stdout.split("Total reclaimed space:")[1].strip().split('\n')[0].strip()
                freed_gb += self._parse_docker_space(space_str)

            # Remove all volumes
            result = subprocess.run(
                ["docker", "volume", "prune", "-f"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if "Total reclaimed space:" in result.stdout:
                space_str = result.stdout.split("Total reclaimed space:")[1].strip().split('\n')[0].strip()
                freed_gb += self._parse_docker_space(space_str)

            # Full system prune
            result = subprocess.run(
                ["docker", "system", "prune", "-a", "--volumes", "-f"],
                capture_output=True,
                text=True,
                timeout=600
            )
            if "Total reclaimed space:" in result.stdout:
                space_str = result.stdout.split("Total reclaimed space:")[1].strip().split('\n')[0].strip()
                freed_gb += self._parse_docker_space(space_str)

            self.logger.info(f"   ✅ Docker cleanup - Freed: {freed_gb:.2f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Docker cleanup failed: {e}")

        return {"freed_gb": freed_gb}

    def cleanup_windows_temp(self) -> Dict[str, Any]:
        """Clean Windows temp directories"""
        self.logger.info("2. Cleaning Windows temp directories...")
        freed_gb = 0.0
        files_deleted = 0

        temp_dirs = [
            Path(f"C:/Windows/Temp"),
            Path(f"C:/Users/{self.username}/AppData/Local/Temp"),
            Path(f"C:/Users/{self.username}/AppData/Local/Microsoft/Windows/INetCache"),
            Path(f"C:/Users/{self.username}/AppData/Local/Microsoft/Windows/History")
        ]

        for temp_dir in temp_dirs:
            if temp_dir.exists():
                try:
                    for item in temp_dir.iterdir():
                        try:
                            if item.is_file():
                                size = item.stat().st_size
                                item.unlink()
                                freed_gb += size / (1024**3)
                                files_deleted += 1
                            elif item.is_dir():
                                try:
                                    shutil.rmtree(item)
                                    # Estimate size (rough)
                                    freed_gb += 0.1  # Conservative estimate
                                    files_deleted += 1
                                except:
                                    pass
                        except Exception as e:
                            self.logger.debug(f"   Could not delete {item}: {e}")
                except Exception as e:
                    self.logger.debug(f"   Error accessing {temp_dir}: {e}")

        self.logger.info(f"   ✅ Windows temp cleanup - Freed: {freed_gb:.2f}GB ({files_deleted} items)")
        return {"freed_gb": freed_gb, "files_deleted": files_deleted}

    def cleanup_python_cache(self) -> Dict[str, Any]:
        """Clean all Python cache"""
        self.logger.info("3. Cleaning Python cache...")
        freed_gb = 0.0

        cache_dirs = [
            self.project_root / "__pycache__",
            self.project_root / "scripts" / "python" / "__pycache__"
        ]

        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    for pycache in cache_dir.rglob("*.pyc"):
                        try:
                            size = pycache.stat().st_size
                            pycache.unlink()
                            freed_gb += size / (1024**3)
                        except:
                            pass
                    # Remove all __pycache__ dirs
                    for pycache_dir in cache_dir.rglob("__pycache__"):
                        try:
                            shutil.rmtree(pycache_dir)
                        except:
                            pass
                except Exception as e:
                    self.logger.debug(f"   Error cleaning {cache_dir}: {e}")

        self.logger.info(f"   ✅ Python cache cleanup - Freed: {freed_gb:.3f}GB")
        return {"freed_gb": freed_gb}

    def cleanup_logs(self) -> Dict[str, Any]:
        """Clean old log files"""
        self.logger.info("4. Cleaning log files...")
        freed_gb = 0.0
        files_deleted = 0

        log_dirs = [
            self.project_root / "data" / "logs",
            self.project_root / "logs"
        ]

        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.rglob("*.log"):
                    try:
                        # Delete logs older than 1 day
                        age_days = (datetime.now().timestamp() - log_file.stat().st_mtime) / (24*3600)
                        if age_days > 1:
                            size = log_file.stat().st_size
                            log_file.unlink()
                            freed_gb += size / (1024**3)
                            files_deleted += 1
                    except:
                        pass

        self.logger.info(f"   ✅ Log files cleanup - Freed: {freed_gb:.3f}GB ({files_deleted} files)")
        return {"freed_gb": freed_gb, "files_deleted": files_deleted}

    def _parse_docker_space(self, space_str: str) -> float:
        """Parse Docker space string"""
        space_str = space_str.strip().upper()
        if "GB" in space_str:
            return float(space_str.replace("GB", ""))
        elif "MB" in space_str:
            return float(space_str.replace("MB", "")) / 1024
        return 0.0

    def emergency_cleanup(self) -> Dict[str, Any]:
        """Run all emergency cleanup procedures"""
        self.logger.info("="*80)
        self.logger.info("EMERGENCY SPACE CLEANUP - CRITICAL SITUATION")
        self.logger.info("="*80)

        results = {
            "docker": {},
            "windows_temp": {},
            "python_cache": {},
            "logs": {},
            "total_freed_gb": 0
        }

        results["docker"] = self.cleanup_docker_aggressive()
        results["windows_temp"] = self.cleanup_windows_temp()
        results["python_cache"] = self.cleanup_python_cache()
        results["logs"] = self.cleanup_logs()

        results["total_freed_gb"] = (
            results["docker"].get("freed_gb", 0) +
            results["windows_temp"].get("freed_gb", 0) +
            results["python_cache"].get("freed_gb", 0) +
            results["logs"].get("freed_gb", 0)
        )

        self.logger.info("\n" + "="*80)
        self.logger.info("EMERGENCY CLEANUP SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Total Space Freed: {results['total_freed_gb']:.2f}GB")
        self.logger.info("="*80)

        return results


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        cleanup = EmergencySpaceCleanup(project_root)
        result = cleanup.emergency_cleanup()

        import json
        print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()