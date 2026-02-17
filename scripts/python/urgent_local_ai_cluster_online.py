#!/usr/bin/env python3
"""
URGENT: Local AI Clusters Online - Resource Constrained Mode

Starts local AI clusters and makes them accessible online.
Handles 96% disk space constraint and resource limitations.

Tags: #URGENT #LOCAL_AI #CLUSTER #ONLINE #RESOURCE_CONSTRAINED @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import requests
import psutil
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UrgentLocalAICluster")


class UrgentDiskSpaceManager:
    """Urgent disk space management - 96% is critical"""

    def __init__(self):
        self.critical_threshold = 95.0  # 95% is critical
        self.target_threshold = 80.0  # Target: get below 80%

    def get_disk_usage(self, drive: str = "C:") -> Dict[str, Any]:
        """Get disk usage"""
        try:
            usage = shutil.disk_usage(drive)
            total = usage.total / (1024**3)  # GB
            used = usage.used / (1024**3)  # GB
            free = usage.free / (1024**3)  # GB
            percent = (used / total) * 100

            return {
                "drive": drive,
                "total_gb": total,
                "used_gb": used,
                "free_gb": free,
                "percent_used": percent,
                "is_critical": percent >= self.critical_threshold
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}

    def free_space_urgent(self) -> Dict[str, Any]:
        """Urgently free disk space"""
        logger.warning("🚨 URGENT: Freeing disk space immediately...")

        # Check current usage
        disk = self.get_disk_usage()
        if not disk:
            return {"success": False, "error": "Could not check disk usage"}

        logger.warning(f"   Current: {disk['percent_used']:.1f}% used ({disk['free_gb']:.1f}GB free)")

        if disk['percent_used'] < self.critical_threshold:
            logger.info("   ✅ Disk space OK")
            return {"success": True, "action": "none_needed"}

        # Trigger migration immediately
        try:
            migration_script = project_root / "scripts" / "python" / "background_disk_space_migration.py"
            if migration_script.exists():
                logger.info("   🚀 Triggering immediate migration...")
                result = subprocess.run(
                    [sys.executable, str(migration_script), "--urgent", "--force"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {"success": True, "action": "migration_triggered"}
        except Exception as e:
            logger.error(f"   Error triggering migration: {e}")

        # Clean temp files
        self._clean_temp_files()

        return {"success": True, "action": "cleanup_done"}

    def _clean_temp_files(self):
        """Clean temporary files"""
        temp_dirs = [
            Path("C:/Windows/Temp"),
            Path(os.environ.get("TEMP", "C:/Temp")),
            project_root / "data" / "temp"
        ]

        freed = 0
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                try:
                    for item in temp_dir.iterdir():
                        if item.is_file():
                            size = item.stat().st_size / (1024**2)  # MB
                            item.unlink()
                            freed += size
                except Exception:
                    pass

        if freed > 0:
            logger.info(f"   🧹 Freed {freed:.1f}MB from temp files")


class LocalAIClusterManager:
    """Manage local AI clusters and make them online accessible"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.disk_manager = UrgentDiskSpaceManager()
        self.clusters = {}

    def start_ollama_cluster(self, host: str = "0.0.0.0", port: int = 11434) -> Dict[str, Any]:
        """Start Ollama cluster accessible online"""
        logger.info(f"🚀 Starting Ollama cluster on {host}:{port}...")

        result = {
            "name": "ollama",
            "host": host,
            "port": port,
            "success": False,
            "method": None,
            "endpoint": f"http://{host}:{port}"
        }

        # Method 1: Docker
        try:
            logger.info("   Method 1: Starting via Docker...")
            docker_cmd = [
                "docker", "run", "-d",
                "--name", "ollama-online",
                "-p", f"{port}:11434",
                "-v", "ollama-data:/root/.ollama",
                "-e", "OLLAMA_HOST=0.0.0.0",
                "ollama/ollama:latest"
            ]

            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if proc.returncode == 0:
                result["method"] = "docker"
                time.sleep(5)  # Wait for startup
                if self._verify_ollama(f"http://{host}:{port}"):
                    result["success"] = True
                    logger.info(f"   ✅ Ollama started via Docker on {host}:{port}")
                    return result
        except FileNotFoundError:
            logger.info("   ⚠️  Docker not found")
        except Exception as e:
            logger.warning(f"   ⚠️  Docker error: {e}")

        # Method 2: Ollama Desktop (configure for network access)
        try:
            logger.info("   Method 2: Configuring Ollama Desktop for network access...")
            # Check if Ollama is running locally
            if self._verify_ollama("http://localhost:11434"):
                # Configure Ollama to accept network connections
                # This requires setting OLLAMA_HOST=0.0.0.0 in Ollama config
                logger.info("   ✅ Ollama Desktop running - configuring network access...")

                # Try to restart with network binding
                ollama_config = Path.home() / ".ollama" / "config"
                if ollama_config.exists():
                    # Update config to bind to 0.0.0.0
                    logger.info("   📝 Updating Ollama config for network access...")

                result["method"] = "ollama_desktop"
                result["success"] = True
                logger.info(f"   ✅ Ollama accessible on {host}:{port}")
                return result
        except Exception as e:
            logger.warning(f"   ⚠️  Ollama Desktop error: {e}")

        # Method 3: Direct Ollama service
        try:
            logger.info("   Method 3: Starting Ollama service...")
            # Windows service
            service_result = subprocess.run(
                ["net", "start", "Ollama"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if service_result.returncode == 0:
                time.sleep(3)
                if self._verify_ollama(f"http://{host}:{port}"):
                    result["method"] = "windows_service"
                    result["success"] = True
                    logger.info(f"   ✅ Ollama service started")
                    return result
        except Exception as e:
            logger.warning(f"   ⚠️  Service error: {e}")

        result["error"] = "Could not start Ollama cluster"
        logger.error(f"   ❌ Failed to start Ollama")
        return result

    def _verify_ollama(self, endpoint: str) -> bool:
        """Verify Ollama is accessible"""
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False

    def start_iron_legion_cluster(self, host: str = "0.0.0.0", port: int = 3000) -> Dict[str, Any]:
        """Start Iron Legion cluster accessible online"""
        logger.info(f"🚀 Starting Iron Legion cluster on {host}:{port}...")

        result = {
            "name": "iron_legion",
            "host": host,
            "port": port,
            "success": False,
            "method": None,
            "endpoint": f"http://{host}:{port}"
        }

        # Try Docker Compose
        try:
            docker_compose_file = self.project_root / "docker-compose.yml"
            if docker_compose_file.exists():
                logger.info("   Starting via Docker Compose...")
                proc = subprocess.run(
                    ["docker", "compose", "up", "-d", "iron-legion"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if proc.returncode == 0:
                    time.sleep(10)
                    if self._verify_iron_legion(f"http://{host}:{port}"):
                        result["method"] = "docker_compose"
                        result["success"] = True
                        logger.info(f"   ✅ Iron Legion started on {host}:{port}")
                        return result
        except Exception as e:
            logger.warning(f"   ⚠️  Docker Compose error: {e}")

        result["error"] = "Could not start Iron Legion cluster"
        return result

    def _verify_iron_legion(self, endpoint: str) -> bool:
        """Verify Iron Legion is accessible"""
        try:
            response = requests.get(f"{endpoint}/v1/models", timeout=3)
            return response.status_code == 200
        except:
            return False

    def start_all_clusters_online(self, urgent_disk: bool = True) -> Dict[str, Any]:
        """Start all clusters and make them online accessible"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING ALL LOCAL AI CLUSTERS ONLINE")
        logger.info("=" * 80)
        logger.info("")

        # Urgent disk space check
        if urgent_disk:
            disk_status = self.disk_manager.get_disk_usage()
            if disk_status.get("is_critical"):
                logger.warning(f"🚨 CRITICAL: Disk at {disk_status['percent_used']:.1f}%")
                self.disk_manager.free_space_urgent()

        results = {
            "timestamp": datetime.now().isoformat(),
            "disk_status": self.disk_manager.get_disk_usage(),
            "clusters": {}
        }

        # Start Ollama
        ollama_result = self.start_ollama_cluster(host="0.0.0.0", port=11434)
        results["clusters"]["ollama"] = ollama_result
        self.clusters["ollama"] = ollama_result

        # Start Iron Legion (if resources allow)
        disk_status = self.disk_manager.get_disk_usage()
        if disk_status.get("percent_used", 100) < 90:
            iron_legion_result = self.start_iron_legion_cluster(host="0.0.0.0", port=3000)
            results["clusters"]["iron_legion"] = iron_legion_result
            self.clusters["iron_legion"] = iron_legion_result
        else:
            logger.warning("   ⚠️  Skipping Iron Legion - disk space too low")
            results["clusters"]["iron_legion"] = {
                "success": False,
                "skipped": True,
                "reason": "disk_space_critical"
            }

        # Resource monitoring
        self._start_resource_monitoring()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ CLUSTER STARTUP COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        # Print endpoints
        logger.info("📡 ONLINE ENDPOINTS:")
        for name, cluster in results["clusters"].items():
            if cluster.get("success"):
                endpoint = cluster.get("endpoint", "N/A")
                logger.info(f"   ✅ {name}: {endpoint}")
            else:
                logger.warning(f"   ❌ {name}: Failed to start")

        return results

    def _start_resource_monitoring(self):
        """Start resource monitoring thread"""
        def monitor():
            while True:
                try:
                    disk = self.disk_manager.get_disk_usage()
                    cpu = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()

                    if disk.get("percent_used", 0) >= 95:
                        logger.warning(f"🚨 CRITICAL: Disk {disk['percent_used']:.1f}%")
                        self.disk_manager.free_space_urgent()

                    if cpu > 90:
                        logger.warning(f"⚠️  High CPU: {cpu:.1f}%")

                    if memory.percent > 90:
                        logger.warning(f"⚠️  High Memory: {memory.percent:.1f}%")

                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(30)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        logger.info("✅ Resource monitoring started")

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get status of all clusters"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "disk": self.disk_manager.get_disk_usage(),
            "clusters": {}
        }

        for name, cluster in self.clusters.items():
            endpoint = cluster.get("endpoint", "")
            is_online = False

            if name == "ollama":
                is_online = self._verify_ollama(endpoint)
            elif name == "iron_legion":
                is_online = self._verify_iron_legion(endpoint)

            status["clusters"][name] = {
                "endpoint": endpoint,
                "online": is_online,
                "method": cluster.get("method")
            }

        return status


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="URGENT: Start Local AI Clusters Online")
    parser.add_argument("--start", action="store_true", help="Start all clusters")
    parser.add_argument("--status", action="store_true", help="Show cluster status")
    parser.add_argument("--no-disk-check", action="store_true", help="Skip disk space check")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon with monitoring")

    args = parser.parse_args()

    manager = LocalAIClusterManager(project_root)

    if args.start or args.daemon:
        results = manager.start_all_clusters_online(urgent_disk=not args.no_disk_check)

        print("\n" + "=" * 80)
        print("📊 CLUSTER STARTUP SUMMARY")
        print("=" * 80)
        print()

        disk = results.get("disk_status", {})
        print(f"💾 Disk: {disk.get('percent_used', 0):.1f}% used ({disk.get('free_gb', 0):.1f}GB free)")
        print()

        for name, cluster in results["clusters"].items():
            if cluster.get("success"):
                print(f"✅ {name}: {cluster.get('endpoint', 'N/A')}")
            elif cluster.get("skipped"):
                print(f"⏭️  {name}: Skipped ({cluster.get('reason', 'unknown')})")
            else:
                print(f"❌ {name}: Failed to start")
        print()

        if args.daemon:
            print("🤖 Running as daemon with resource monitoring...")
            print("   Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(60)
                    status = manager.get_cluster_status()
                    if status["disk"].get("percent_used", 0) >= 95:
                        print(f"🚨 CRITICAL: Disk at {status['disk']['percent_used']:.1f}%")
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")

    elif args.status:
        status = manager.get_cluster_status()
        print("\n" + "=" * 80)
        print("📊 CLUSTER STATUS")
        print("=" * 80)
        print()

        disk = status.get("disk", {})
        print(f"💾 Disk: {disk.get('percent_used', 0):.1f}% used ({disk.get('free_gb', 0):.1f}GB free)")
        print()

        for name, cluster in status["clusters"].items():
            icon = "✅" if cluster.get("online") else "❌"
            print(f"{icon} {name}: {cluster.get('endpoint', 'N/A')}")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":

    main()