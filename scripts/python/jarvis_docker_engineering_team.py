#!/usr/bin/env python3
"""
JARVIS Docker Engineering Team
Manages Docker operations across ULTRON, KAIJU, and NAS.

Tags: #DOCKER #CONTAINERS #DEPLOYMENT #MONITORING #AUTOMATION @AUTO @TEAM
"""

import sys
import json
import subprocess
import paramiko
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import time
import threading

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    NASAzureVaultIntegration = None

logger = get_logger("JARVISDockerTeam")


class DockerEngineeringTeam:
    """
    Docker Engineering Team

    Manages Docker operations across the environment:
    - ULTRON (local laptop) - Docker Desktop/WSL
    - KAIJU_NO_8 (<NAS_IP>) - Windows Desktop PC with GPU (RTX 3090, 64GB RAM)
      * NOT the NAS - this is a separate Windows desktop machine
      * Purpose: GPU workloads, LLM hosting, primary compute
      * Docker: Windows Docker Desktop
    - NAS (<NAS_PRIMARY_IP>) - Synology DS1821plus (storage server)
      * Separate from KAIJU_NO_8 - this is the storage server
      * Purpose: Storage, backups, lightweight containers only
      * Docker: Synology Docker Package Manager (DPM)

    Team Structure:
    - Team Manager: @c3po (Helpdesk Coordinator - manages workflow, coordination, escalation)
    - Technical Lead: @r2d2 (Technical Lead Engineer - implements technical solutions)
    - Business Lead: Docker Engineering Lead (business strategy and requirements)
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Team Structure (following organizational pattern)
        self.team_manager = "@c3po"  # Helpdesk Coordinator - manages workflow, coordination, escalation
        self.technical_lead = "@r2d2"  # Technical Lead Engineer - implements technical solutions
        self.business_lead = "Docker Engineering Lead"  # Business strategy and requirements

        # System endpoints
        # IMPORTANT DISTINCTION:
        # - KAIJU_NO_8 (<NAS_IP>) = Windows Desktop PC with GPU (RTX 3090, 64GB RAM)
        #   * NOT the NAS - separate Windows desktop machine
        #   * Purpose: GPU workloads, LLM hosting, primary compute
        # - NAS (<NAS_PRIMARY_IP>) = Synology DS1821plus storage server
        #   * Separate from KAIJU_NO_8 - this is the storage server
        #   * Purpose: Storage, backups, lightweight containers only
        self.ultron_local = "localhost"  # ULTRON - local laptop
        self.kaiju_ip = "<NAS_IP>"  # KAIJU_NO_8 - Windows Desktop PC (NOT the NAS)
        self.nas_ip = "<NAS_PRIMARY_IP>"  # NAS - Synology DS1821plus (separate storage server)

        # SSH credentials
        self.kaiju_credentials = self._load_kaiju_credentials()
        self.nas_credentials = self._load_nas_credentials()

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        self.logger.info("✅ Docker Engineering Team initialized")
        self.logger.info(f"   Team Manager: {self.team_manager} (Helpdesk Coordinator)")
        self.logger.info(f"   Technical Lead: {self.technical_lead} (Technical Lead Engineer)")
        self.logger.info(f"   Business Lead: {self.business_lead}")
        self.logger.info(f"   ULTRON: {self.ultron_local}")
        self.logger.info(f"   KAIJU: {self.kaiju_ip}")
        self.logger.info(f"   NAS: {self.nas_ip}")

    def _load_kaiju_credentials(self) -> Dict[str, str]:
        """Load KAIJU SSH credentials from Azure Key Vault"""
        try:
            if NASAzureVaultIntegration:
                vault_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
                credentials = vault_integration.get_nas_credentials()
                if credentials and credentials.get("username") and credentials.get("password"):
                    self.logger.info(f"✅ Loaded KAIJU credentials for {credentials.get('username')}")
                    return credentials
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load KAIJU credentials: {e}")
        return {}

    def _load_nas_credentials(self) -> Dict[str, str]:
        """Load NAS SSH credentials from Azure Key Vault"""
        try:
            if NASAzureVaultIntegration:
                vault_integration = NASAzureVaultIntegration(nas_ip=self.nas_ip)
                credentials = vault_integration.get_nas_credentials()
                if credentials and credentials.get("username") and credentials.get("password"):
                    self.logger.info(f"✅ Loaded NAS credentials for {credentials.get('username')}")
                    return credentials
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load NAS credentials: {e}")
        return {}

    def _run_local_docker_command(self, command: List[str]) -> Dict[str, Any]:
        """Run Docker command locally (ULTRON)"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout", "exit_code": -1}
        except Exception as e:
            return {"success": False, "error": str(e), "exit_code": -1}

    def _run_remote_docker_command(self, host: str, credentials: Dict[str, str], command: str) -> Dict[str, Any]:
        """Run Docker command on remote host via SSH"""
        if not credentials.get("username") or not credentials.get("password"):
            return {"success": False, "error": "Credentials not available"}

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=host,
                port=22,
                username=credentials.get("username"),
                password=credentials.get("password"),
                timeout=10
            )

            stdin, stdout, stderr = client.exec_command(command, timeout=60)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            error = stderr.read().decode()

            client.close()

            return {
                "success": exit_status == 0,
                "output": output.strip(),
                "error": error.strip(),
                "exit_code": exit_status
            }
        except Exception as e:
            return {"success": False, "error": str(e), "exit_code": -1}

    def check_docker_status(self, system: str = "all") -> Dict[str, Any]:
        """Check Docker status on specified system(s)"""
        self.logger.info("="*80)
        self.logger.info("DOCKER STATUS CHECK")
        self.logger.info("="*80)

        status = {
            "timestamp": datetime.now().isoformat(),
            "ultron": {},
            "kaiju": {},
            "nas": {}
        }

        # Check ULTRON (local)
        if system in ["all", "ultron"]:
            self.logger.info("\n1. Checking ULTRON (local) Docker status...")
            try:
                result = self._run_local_docker_command(["docker", "info"])
                if result["success"]:
                    # Get running containers
                    containers = self._run_local_docker_command(["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"])
                    images = self._run_local_docker_command(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.Size}}"])

                    status["ultron"] = {
                        "available": True,
                        "running": True,
                        "containers": containers.get("output", "").split('\n') if containers.get("output") else [],
                        "images": images.get("output", "").split('\n') if images.get("output") else []
                    }
                    self.logger.info("   ✅ ULTRON Docker is running")
                else:
                    status["ultron"] = {
                        "available": False,
                        "running": False,
                        "error": result.get("error", "Unknown error")
                    }
                    self.logger.warning("   ❌ ULTRON Docker is not running or not accessible")
            except Exception as e:
                status["ultron"] = {"available": False, "error": str(e)}
                self.logger.error(f"   ❌ ULTRON Docker check failed: {e}")

        # Check KAIJU
        if system in ["all", "kaiju"]:
            self.logger.info("\n2. Checking KAIJU Docker status...")
            result = self._run_remote_docker_command(
                self.kaiju_ip,
                self.kaiju_credentials,
                "docker info"
            )
            if result["success"]:
                containers = self._run_remote_docker_command(
                    self.kaiju_ip,
                    self.kaiju_credentials,
                    "docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'"
                )
                status["kaiju"] = {
                    "available": True,
                    "running": True,
                    "containers": containers.get("output", "").split('\n') if containers.get("output") else []
                }
                self.logger.info("   ✅ KAIJU Docker is running")
            else:
                status["kaiju"] = {
                    "available": False,
                    "running": False,
                    "error": result.get("error", "Unknown error")
                }
                self.logger.warning(f"   ❌ KAIJU Docker check failed: {result.get('error')}")

        # Check NAS (lightweight containers only)
        if system in ["all", "nas"]:
            self.logger.info("\n3. Checking NAS Docker status...")
            result = self._run_remote_docker_command(
                self.nas_ip,
                self.nas_credentials,
                "docker info"
            )
            if result["success"]:
                containers = self._run_remote_docker_command(
                    self.nas_ip,
                    self.nas_credentials,
                    "docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'"
                )
                status["nas"] = {
                    "available": True,
                    "running": True,
                    "containers": containers.get("output", "").split('\n') if containers.get("output") else []
                }
                self.logger.info("   ✅ NAS Docker is running")
            else:
                status["nas"] = {
                    "available": False,
                    "running": False,
                    "error": result.get("error", "Unknown error")
                }
                self.logger.warning(f"   ❌ NAS Docker check failed: {result.get('error')}")

        return status

    def cleanup_docker(self, system: str = "all", aggressive: bool = False) -> Dict[str, Any]:
        """Clean up Docker resources on specified system(s)"""
        self.logger.info("="*80)
        self.logger.info("DOCKER CLEANUP")
        self.logger.info("="*80)

        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "ultron": {},
            "kaiju": {},
            "nas": {},
            "total_freed_gb": 0.0
        }

        # Cleanup ULTRON
        if system in ["all", "ultron"]:
            self.logger.info("\n1. Cleaning up ULTRON Docker...")
            try:
                if aggressive:
                    # Stop all containers
                    self._run_local_docker_command(["docker", "stop", "$(docker ps -q)"])
                    # Remove all containers
                    self._run_local_docker_command(["docker", "rm", "$(docker ps -aq)"])
                    # Remove all images
                    self._run_local_docker_command(["docker", "rmi", "$(docker images -q)"])

                # System prune
                result = self._run_local_docker_command(["docker", "system", "prune", "-a", "--volumes", "-f"])
                if result["success"]:
                    cleanup_results["ultron"] = {"success": True, "output": result.get("output", "")}
                    self.logger.info("   ✅ ULTRON Docker cleanup complete")
                else:
                    cleanup_results["ultron"] = {"success": False, "error": result.get("error", "")}
            except Exception as e:
                cleanup_results["ultron"] = {"success": False, "error": str(e)}
                self.logger.error(f"   ❌ ULTRON Docker cleanup failed: {e}")

        # Cleanup KAIJU
        if system in ["all", "kaiju"]:
            self.logger.info("\n2. Cleaning up KAIJU Docker...")
            try:
                command = "docker system prune -a --volumes -f"
                if aggressive:
                    command = "docker stop $(docker ps -q) && docker rm $(docker ps -aq) && docker rmi $(docker images -q) && docker system prune -a --volumes -f"

                result = self._run_remote_docker_command(
                    self.kaiju_ip,
                    self.kaiju_credentials,
                    command
                )
                cleanup_results["kaiju"] = result
                if result["success"]:
                    self.logger.info("   ✅ KAIJU Docker cleanup complete")
                else:
                    self.logger.warning(f"   ⚠️  KAIJU Docker cleanup: {result.get('error')}")
            except Exception as e:
                cleanup_results["kaiju"] = {"success": False, "error": str(e)}
                self.logger.error(f"   ❌ KAIJU Docker cleanup failed: {e}")

        # Cleanup NAS (lightweight only)
        if system in ["all", "nas"]:
            self.logger.info("\n3. Cleaning up NAS Docker (lightweight containers only)...")
            try:
                # NAS should only have lightweight containers - be careful
                result = self._run_remote_docker_command(
                    self.nas_ip,
                    self.nas_credentials,
                    "docker system prune -f"  # Less aggressive for NAS
                )
                cleanup_results["nas"] = result
                if result["success"]:
                    self.logger.info("   ✅ NAS Docker cleanup complete")
                else:
                    self.logger.warning(f"   ⚠️  NAS Docker cleanup: {result.get('error')}")
            except Exception as e:
                cleanup_results["nas"] = {"success": False, "error": str(e)}
                self.logger.error(f"   ❌ NAS Docker cleanup failed: {e}")

        return cleanup_results

    def deploy_container(self, system: str, image: str, name: str, ports: Optional[Dict[str, str]] = None, env: Optional[Dict[str, str]] = None, volumes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Deploy a Docker container to specified system"""
        self.logger.info(f"🚀 Deploying container '{name}' ({image}) to {system}...")

        # Build docker run command
        cmd_parts = ["docker", "run", "-d", "--name", name]

        if ports:
            for host_port, container_port in ports.items():
                cmd_parts.extend(["-p", f"{host_port}:{container_port}"])

        if env:
            for key, value in env.items():
                cmd_parts.extend(["-e", f"{key}={value}"])

        if volumes:
            for volume in volumes:
                cmd_parts.extend(["-v", volume])

        cmd_parts.append(image)
        command = " ".join(cmd_parts)

        if system == "ultron":
            result = self._run_local_docker_command(cmd_parts)
        elif system == "kaiju":
            result = self._run_remote_docker_command(self.kaiju_ip, self.kaiju_credentials, command)
        elif system == "nas":
            result = self._run_remote_docker_command(self.nas_ip, self.nas_credentials, command)
        else:
            return {"success": False, "error": f"Unknown system: {system}"}

        if result["success"]:
            self.logger.info(f"   ✅ Container '{name}' deployed successfully")
        else:
            self.logger.error(f"   ❌ Container deployment failed: {result.get('error')}")

        return result

    def monitor_and_optimize(self, interval_seconds: int = 300) -> Dict[str, Any]:
        """Monitor Docker across all systems and optimize"""
        self.logger.info("="*80)
        self.logger.info("DOCKER MONITORING & OPTIMIZATION")
        self.logger.info("="*80)

        status = self.check_docker_status("all")

        # Report status
        self.logger.info("\nDOCKER STATUS SUMMARY:")
        for system_name, system_status in [("ULTRON", status["ultron"]), ("KAIJU", status["kaiju"]), ("NAS", status["nas"])]:
            if system_status.get("available"):
                containers = system_status.get("containers", [])
                running_count = len([c for c in containers if c and "Up" in c])
                self.logger.info(f"   ✅ {system_name}: {running_count} containers running")
            else:
                self.logger.warning(f"   ❌ {system_name}: Docker not available")

        # Optimization recommendations
        recommendations = []

        # Check for unused resources
        if status["ultron"].get("available"):
            # Check for stopped containers
            stopped = self._run_local_docker_command(["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"])
            if stopped.get("output"):
                recommendations.append("ULTRON: Remove stopped containers to free space")

        return {
            "monitored": True,
            "status": status,
            "recommendations": recommendations
        }

    def start_continuous_monitoring(self, interval_seconds: int = 300):
        """Start continuous monitoring in background thread"""
        if self.monitoring_active:
            self.logger.info("   Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"   ✅ Continuous monitoring started (interval: {interval_seconds}s)")

    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        self.logger.info("   ✅ Continuous monitoring stopped")

    def _monitoring_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self.monitor_and_optimize()
                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"   ❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retry


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Docker Engineering Team - Manage Docker across ULTRON, KAIJU, and NAS")
    parser.add_argument("--status", action="store_true", help="Check Docker status on all systems")
    parser.add_argument("--cleanup", action="store_true", help="Clean up Docker resources")
    parser.add_argument("--aggressive", action="store_true", help="Aggressive cleanup (stops all containers)")
    parser.add_argument("--system", choices=["ultron", "kaiju", "nas", "all"], default="all", help="Target system")
    parser.add_argument("--monitor", action="store_true", help="Run one-time monitoring check")
    parser.add_argument("--start-daemon", action="store_true", help="Start continuous monitoring daemon")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds (default: 300)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    team = DockerEngineeringTeam(project_root)

    if args.status:
        result = team.check_docker_status(args.system)
        print(json.dumps(result, indent=2, default=str))
    elif args.cleanup:
        result = team.cleanup_docker(args.system, aggressive=args.aggressive)
        print(json.dumps(result, indent=2, default=str))
    elif args.start_daemon:
        team.start_continuous_monitoring(interval_seconds=args.interval)
        print("Monitoring daemon started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            team.stop_continuous_monitoring()
    elif args.monitor:
        result = team.monitor_and_optimize()
        print(json.dumps(result, indent=2, default=str))
    else:
        # Default: status check
        result = team.check_docker_status()
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":


    main()