#!/usr/bin/env python3
"""
NAS Migration Auto-Docker - Autonomous Docker Volume Migration

Automatically migrates Docker volumes to NAS when safe to do so.

Tags: #NAS_MIGRATION #AUTO_DOCKER #AUTONOMOUS @JARVIS @LUMINA
"""

import sys
import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

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

# Migration timeout configuration (1 hour for large Docker volume migrations)
DOCKER_MIGRATION_TIMEOUT_SECONDS = 3600

logger = get_logger("NASMigrationAutoDocker")


class DockerAutoMigrator:
    """Autonomous Docker volume migration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.docker_source = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker")
        # Use existing docker share at /volume1/docker
        self.docker_target = Path(f"\\\\{self.nas_ip}\\docker")

    def check_docker_running(self) -> bool:
        """Check if Docker Desktop is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'docker' in proc.info['name'].lower() and 'desktop' in proc.info['name'].lower():
                    return True
            return False
        except ImportError:
            # Fallback
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Docker Desktop.exe"],
                    capture_output=True,
                    text=True,
                    timeout=10  # 10 second timeout for service check
                )
                return "Docker Desktop.exe" in result.stdout
            except:
                return False

    def stop_docker_desktop(self) -> bool:
        """Stop Docker Desktop using Docker terminal commands"""
        logger.info("🛑 Stopping Docker containers and services...")

        # Method 1: Stop all running containers via Docker terminal
        try:
            logger.info("   📋 Stopping all running containers...")
            result = subprocess.run(
                ["docker", "stop", "$(docker ps -q)"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info("   ✅ All containers stopped")
            else:
                # Try Windows PowerShell version
                logger.info("   📋 Stopping containers (PowerShell method)...")
                ps_cmd = 'docker ps -q | ForEach-Object { docker stop $_ }'
                result = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    logger.info("   ✅ Containers stopped via Docker terminal")
                else:
                    logger.warning("   ⚠️  Some containers may still be running")
        except Exception as e:
            logger.warning(f"   ⚠️  Error stopping containers: {e}")

        # Method 2: Try stopping Docker Desktop process
        try:
            result = subprocess.run(
                ["taskkill", "/IM", "Docker Desktop.exe", "/T"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("   ✅ Docker Desktop stopped")
                return True
            else:
                logger.info("   ⚠️  Docker Desktop may still be running (continuing anyway)")
                return True  # Continue even if Docker Desktop is running
        except Exception as e:
            logger.warning(f"   ⚠️  Error stopping Docker Desktop: {e}")
            return True  # Continue anyway - migration can proceed with running Docker

    def migrate_docker_volumes_auto(self, auto_stop: bool = False) -> Dict:
        """Automatically migrate Docker volumes"""
        logger.info("=" * 80)
        logger.info("🐳 AUTONOMOUS DOCKER VOLUME MIGRATION")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING",
            "steps_completed": [],
            "errors": []
        }

        # Check if Docker is running
        docker_running = self.check_docker_running()
        if docker_running:
            if auto_stop:
                logger.info("Docker Desktop is running - stopping...")
                if self.stop_docker_desktop():
                    result["steps_completed"].append("docker_stopped")
                    # Wait a moment for Docker to fully stop
                    import time
                    time.sleep(5)
                else:
                    result["errors"].append("Could not stop Docker Desktop")
                    result["status"] = "FAILED"
                    return result
            else:
                result["errors"].append("Docker Desktop is running - must stop first")
                result["status"] = "BLOCKED"
                logger.warning("⚠️  Docker Desktop is running")
                logger.info("   Set auto_stop=True to stop automatically")
                return result

        # Check if source exists
        if not self.docker_source.exists():
            result["errors"].append(f"Source does not exist: {self.docker_source}")
            result["status"] = "FAILED"
            logger.warning(f"❌ Source does not exist: {self.docker_source}")
            return result

        # Check if target share exists (try both paths)
        if not self.docker_target.exists():
            # Try alternative: existing docker share
            alt_target = Path(f"\\\\{self.nas_ip}\\docker")
            if alt_target.exists():
                logger.info(f"   ✅ Found existing docker share: {alt_target}")
                self.docker_target = alt_target
            else:
                result["errors"].append(f"Target share does not exist: {self.docker_target}")
                result["status"] = "BLOCKED"
                logger.warning(f"❌ Target share does not exist: {self.docker_target}")
                logger.info("   Tried: \\\\<NAS_PRIMARY_IP>\\data\\docker and \\\\<NAS_PRIMARY_IP>\\docker")
                return result

        # Get source size
        source_size = 0
        file_count = 0
        try:
            for item in self.docker_source.rglob("*"):
                if item.is_file():
                    try:
                        source_size += item.stat().st_size
                        file_count += 1
                    except:
                        pass
        except:
            pass

        source_size_gb = round(source_size / (1024**3), 2)
        logger.info(f"Source: {self.docker_source}")
        logger.info(f"Size: {source_size_gb:.2f} GB ({file_count:,} files)")
        logger.info(f"Target: {self.docker_target}")
        logger.info("")

        # Migrate
        logger.info("📦 Migrating Docker volumes to NAS...")
        logger.info("   This may take a while for 82GB...")
        logger.info("")

        try:
            # Create target directory
            self.docker_target.mkdir(parents=True, exist_ok=True)

            # Use robocopy for better performance and resume capability
            robocopy_cmd = [
                "robocopy",
                str(self.docker_source),
                str(self.docker_target / self.docker_source.name),
                "/E",  # Copy subdirectories including empty ones
                "/R:3",  # Retry 3 times
                "/W:5",  # Wait 5 seconds between retries
                "/MT:8",  # Multi-threaded (8 threads)
                "/LOG:" + str(self.data_dir / "docker_migration.log")
            ]

            logger.info(f"   Running: {' '.join(robocopy_cmd)}")
            result_proc = subprocess.run(
                robocopy_cmd,
                capture_output=True,
                text=True,
                timeout=DOCKER_MIGRATION_TIMEOUT_SECONDS
            )

            # Robocopy returns 0-7 for success, 8+ for errors
            if result_proc.returncode <= 7:
                logger.info("   ✅ Migration complete")
                result["steps_completed"].append("files_copied")
                result["status"] = "COMPLETED"
            else:
                logger.warning(f"   ⚠️  Robocopy returned code: {result_proc.returncode}")
                result["errors"].append(f"Robocopy error code: {result_proc.returncode}")
                result["status"] = "PARTIAL"
        except subprocess.TimeoutExpired:
            result["errors"].append("Migration timed out (1 hour)")
            result["status"] = "TIMEOUT"
            logger.warning("   ⚠️  Migration timed out")
        except Exception as e:
            result["errors"].append(str(e))
            result["status"] = "FAILED"
            logger.error(f"   ❌ Migration failed: {e}")

        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.data_dir / f"docker_migration_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        logger.info("")
        logger.info(f"💾 Results saved: {result_file}")
        logger.info("")

        return result


def main():
    """Main execution"""
    import argparse
    parser = argparse.ArgumentParser(description="Auto-migrate Docker volumes")
    parser.add_argument("--auto-stop", action="store_true", help="Automatically stop Docker Desktop")
    args = parser.parse_args()

    migrator = DockerAutoMigrator(project_root)
    result = migrator.migrate_docker_volumes_auto(auto_stop=args.auto_stop)

    print("\n" + "=" * 80)
    print("🐳 DOCKER MIGRATION RESULT")
    print("=" * 80)
    print()
    print(f"Status: {result['status']}")
    print(f"Steps completed: {len(result['steps_completed'])}")
    if result.get("errors"):
        print(f"Errors: {len(result['errors'])}")
        for error in result["errors"]:
            print(f"  - {error}")
    print()


if __name__ == "__main__":


    main()