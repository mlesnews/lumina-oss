#!/usr/bin/env python3
"""
JARVIS Storage Engineering Team
Continuously monitors storage and automatically transfers files to NAS.

Tags: #STORAGE #NAS #MONITORING #AUTOMATION @AUTO @TEAM
"""

import sys
import json
import shutil
import os
import paramiko
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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

logger = get_logger("JARVISStorageTeam")


class StorageEngineeringTeam:
    """
    Storage Engineering Team

    Continuously monitors storage and automatically:
    - Detects low/critical space situations
    - Transfers centralized files to NAS
    - Manages NAS cloud storage aggregate
    - Maintains storage balance across environment

    Team Structure:
    - Team Manager: @c3po (Helpdesk Coordinator - manages workflow, coordination, escalation)
    - Technical Lead: @r2d2 (Technical Lead Engineer - implements technical solutions)
    - Business Lead: Storage Engineering Lead (business strategy and requirements)
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Team Structure (following organizational pattern)
        self.team_manager = "@c3po"  # Helpdesk Coordinator - manages workflow, coordination, escalation
        self.technical_lead = "@r2d2"  # Technical Lead Engineer - implements technical solutions
        self.business_lead = "Storage Engineering Lead"  # Business strategy and requirements

        # NAS connection info
        self.nas_ip = "<NAS_PRIMARY_IP>"  # Synology DS1821plus
        self.nas_ssh_port = 22
        self.nas_storage_path = "/volume1/lumina_storage"  # NAS storage path
        self.nas_cloud_aggregate_path = "/volume1/cloud_storage"  # Cloud storage aggregate

        # Storage thresholds
        self.critical_threshold_gb = 10.0  # Critical if < 10GB free
        self.low_threshold_gb = 20.0  # Low if < 20GB free
        self.transfer_threshold_percent = 80.0  # Transfer files if > 80% used

        # Files to transfer (centralized files that can be moved to NAS)
        self.transferable_paths = [
            self.project_root / "data" / "archives",
            self.project_root / "data" / "backups",
            self.project_root / "data" / "exports",
            self.project_root / "data" / "models",  # Large model files
            self.project_root / "data" / "cache",  # Cache files
            self.project_root / "data" / "logs",  # Old log files
            self.project_root / "data" / "workflow_logs",  # Workflow logs
            self.project_root / "data" / "doit_logs",  # DOIT logs
            Path("C:/Users") / os.getenv("USERNAME", "mlesn") / "Downloads",
            Path("C:/Users") / os.getenv("USERNAME", "mlesn") / "Documents",
            Path("C:/ProgramData/ASUS/ARMOURY CRATE Diagnosis/AppLog"),
            Path(os.getenv("TEMP", "C:\\Temp")),  # Windows temp (if in project)
            Path(os.getenv("LOCALAPPDATA", "")) / "Temp" if os.getenv("LOCALAPPDATA") else None,  # AppData temp
        ]
        # Filter out None paths
        self.transferable_paths = [p for p in self.transferable_paths if p]

        # NAS credentials
        self.nas_credentials = self._load_nas_credentials()

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        self.logger.info("✅ Storage Engineering Team initialized")
        self.logger.info(f"   Team Manager: {self.team_manager} (Helpdesk Coordinator)")
        self.logger.info(f"   Technical Lead: {self.technical_lead} (Technical Lead Engineer)")
        self.logger.info(f"   Business Lead: {self.business_lead}")
        self.logger.info(f"   NAS: {self.nas_ip}")
        self.logger.info(f"   Storage Path: {self.nas_storage_path}")
        self.logger.info(f"   Cloud Aggregate: {self.nas_cloud_aggregate_path}")

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

    def check_local_disk_space(self) -> Dict[str, Any]:
        """Check local disk space on all drives"""
        import subprocess

        space_info = {
            "drives": [],
            "critical_drives": [],
            "low_space_drives": [],
            "total_free_gb": 0
        }

        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='Free(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}, @{Name='Used(GB)';Expression={[math]::Round($_.Used/1GB,2)}}, @{Name='Total(GB)';Expression={[math]::Round(($_.Used+$_.FreeSpace)/1GB,2)}} | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                drives_data = json.loads(result.stdout.strip())
                if not isinstance(drives_data, list):
                    drives_data = [drives_data]

                for drive in drives_data:
                    drive_name = drive.get("Name", "Unknown")
                    free_gb = drive.get("Free(GB)", 0)
                    used_gb = drive.get("Used(GB)", 0)
                    total_gb = drive.get("Total(GB)", 0)
                    used_percent = (used_gb / total_gb * 100) if total_gb > 0 else 0

                    drive_info = {
                        "drive": drive_name,
                        "free_gb": round(free_gb, 2),
                        "used_gb": round(used_gb, 2),
                        "total_gb": round(total_gb, 2),
                        "used_percent": round(used_percent, 2),
                        "status": "ok"
                    }

                    if free_gb < self.critical_threshold_gb or used_percent > 95:
                        drive_info["status"] = "critical"
                        space_info["critical_drives"].append(drive_info)
                    elif free_gb < self.low_threshold_gb or used_percent > self.transfer_threshold_percent:
                        drive_info["status"] = "low"
                        space_info["low_space_drives"].append(drive_info)

                    space_info["drives"].append(drive_info)
                    space_info["total_free_gb"] += free_gb
        except Exception as e:
            self.logger.error(f"❌ Failed to check disk space: {e}")

        return space_info

    def check_nas_storage(self) -> Dict[str, Any]:
        """Check NAS storage capacity and cloud aggregate usage"""
        if not self.nas_credentials:
            return {"available": False, "error": "NAS credentials not available"}

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.nas_ip,
                port=self.nas_ssh_port,
                username=self.nas_credentials.get("username"),
                password=self.nas_credentials.get("password"),
                timeout=10,
                allow_agent=False,      # Disable SSH agent (prevents publickey attempts)
                look_for_keys=False     # Don't look for SSH keys (password-only auth)
            )

            # Check storage volume
            stdin, stdout, stderr = client.exec_command(
                f"df -h {self.nas_storage_path} 2>/dev/null || df -h /volume1 2>/dev/null",
                timeout=10
            )
            storage_output = stdout.read().decode().strip()
            storage_error = stderr.read().decode().strip()

            # Check cloud aggregate if it exists
            stdin, stdout, stderr = client.exec_command(
                f"df -h {self.nas_cloud_aggregate_path} 2>/dev/null || echo 'Cloud aggregate not found'",
                timeout=10
            )
            cloud_output = stdout.read().decode().strip()

            client.close()

            # Parse storage info
            nas_info = {
                "available": True,
                "storage_path": self.nas_storage_path,
                "cloud_aggregate_path": self.nas_cloud_aggregate_path,
                "storage_info": storage_output,
                "cloud_aggregate_info": cloud_output if "not found" not in cloud_output.lower() else "Not configured"
            }

            # Parse df output for space info
            if storage_output:
                lines = storage_output.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        nas_info["total"] = parts[1]
                        nas_info["used"] = parts[2]
                        nas_info["available"] = parts[3]
                        nas_info["use_percent"] = parts[4] if len(parts) > 4 else "0%"

            return nas_info
        except Exception as e:
            self.logger.error(f"❌ Failed to check NAS storage: {e}")
            return {"available": False, "error": str(e)}

    def transfer_file_to_nas(self, local_path: Path, nas_relative_path: str = "") -> Dict[str, Any]:
        """Transfer a file or directory to NAS with robust retry and error handling"""
        if not self.nas_credentials:
            return {"success": False, "error": "NAS credentials not available"}

        if not local_path.exists():
            return {"success": False, "error": f"Local path does not exist: {local_path}"}

        # Determine NAS destination
        if nas_relative_path:
            nas_dest = f"{self.nas_storage_path}/{nas_relative_path}"
        else:
            try:
                rel_path = local_path.relative_to(self.project_root)
                nas_dest = f"{self.nas_storage_path}/{rel_path}"
            except ValueError:
                nas_dest = f"{self.nas_storage_path}/{local_path.name}"

        # Normalize slashes for NAS (linux style)
        nas_dest = nas_dest.replace("\\", "/")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    hostname=self.nas_ip,
                    port=self.nas_ssh_port,
                    username=self.nas_credentials.get("username"),
                    password=self.nas_credentials.get("password"),
                    timeout=30,
                    allow_agent=False,
                    look_for_keys=False
                )

                # Create destination directory
                nas_dir = "/".join(nas_dest.split("/")[:-1]) if local_path.is_file() else nas_dest
                self._remote_mkdir_p(client, nas_dir)

                sftp = client.open_sftp()
                try:
                    if local_path.is_file():
                        sftp.put(str(local_path), nas_dest)
                        file_size = local_path.stat().st_size / (1024**2)  # MB
                        self.logger.info(f"   ✅ Transferred {local_path.name} ({file_size:.2f}MB) to NAS")
                    else:
                        self._transfer_directory_sftp(sftp, client, local_path, nas_dest)

                    return {"success": True, "nas_path": nas_dest, "local_path": str(local_path)}
                finally:
                    sftp.close()
                    client.close()

            except Exception as e:
                self.logger.warning(f"   ⚠️  Transfer attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"❌ Failed to transfer {local_path} after {max_retries} attempts")
                    return {"success": False, "error": str(e)}
                time.sleep(2)

        return {"success": False, "error": "Unknown transfer failure"}

    def _remote_mkdir_p(self, client, remote_directory):
        """Helper to create remote directory path (mkdir -p)"""
        client.exec_command(f"mkdir -p \"{remote_directory}\"")

    def _transfer_directory_sftp(self, sftp, client, local_dir: Path, nas_dest: str):
        """Recursively transfer directory via SFTP with proper directory creation"""
        nas_dest = nas_dest.replace("\\", "/")
        self._remote_mkdir_p(client, nas_dest)

        for item in local_dir.iterdir():
            nas_item_path = f"{nas_dest}/{item.name}".replace("//", "/")
            if item.is_file():
                sftp.put(str(item), nas_item_path)
            elif item.is_dir():
                self._transfer_directory_sftp(sftp, client, item, nas_item_path)

    def find_large_files(self, min_size_gb: float = 0.1) -> List[Dict[str, Any]]:
        """Find large files that can be transferred to NAS"""
        large_files = []
        min_size_bytes = min_size_gb * (1024**3)

        # Also check common large file locations
        additional_paths = [
            Path("C:\\Users") / os.getenv("USERNAME", "") / "Downloads" if os.getenv("USERNAME") else None,
            Path("C:\\Users") / os.getenv("USERNAME", "") / "Documents" if os.getenv("USERNAME") else None,
            Path("C:\\ProgramData"),
        ]
        all_paths = self.transferable_paths + [p for p in additional_paths if p and p.exists()]

        for transferable_path in all_paths:
            if transferable_path.exists():
                try:
                    for item in transferable_path.rglob("*"):
                        if item.is_file():
                            try:
                                size = item.stat().st_size
                                if size >= min_size_bytes:
                                    # Try to get relative path, fallback to absolute
                                    try:
                                        rel_path = str(item.relative_to(self.project_root))
                                    except:
                                        rel_path = str(item)

                                    large_files.append({
                                        "path": str(item),
                                        "size_gb": round(size / (1024**3), 2),
                                        "relative_path": rel_path
                                    })
                            except (PermissionError, OSError):
                                pass  # Skip files we can't access
                except (PermissionError, OSError) as e:
                    self.logger.debug(f"   Cannot access {transferable_path}: {e}")
                    pass

        # Sort by size (largest first)
        large_files.sort(key=lambda x: x["size_gb"], reverse=True)
        return large_files

    def auto_transfer_to_nas(self, target_free_gb: float = 20.0) -> Dict[str, Any]:
        try:
            """Automatically transfer files to NAS to free up space"""
            self.logger.info("="*80)
            self.logger.info("AUTO-TRANSFER TO NAS")
            self.logger.info("="*80)

            # Check current space
            space_info = self.check_local_disk_space()
            critical_drives = space_info.get("critical_drives", [])
            low_space_drives = space_info.get("low_space_drives", [])

            if not critical_drives and not low_space_drives:
                self.logger.info("   ✅ No space issues - no transfer needed")
                return {"transferred": False, "reason": "No space issues"}

            # Check NAS availability
            nas_info = self.check_nas_storage()
            if not nas_info.get("available"):
                self.logger.warning("   ⚠️  NAS not available - cannot transfer")
                return {"transferred": False, "reason": "NAS not available", "nas_info": nas_info}

            self.logger.info(f"   📊 NAS Storage: {nas_info.get('available', 'N/A')} available")
            if nas_info.get("cloud_aggregate_info") != "Not configured":
                self.logger.info(f"   ☁️  Cloud Aggregate: {nas_info.get('cloud_aggregate_info', 'N/A')}")
            else:
                self.logger.warning("   ⚠️  Cloud storage aggregate not configured on NAS")

            # Find large files to transfer
            large_files = self.find_large_files(min_size_gb=0.1)  # Files > 100MB

            if not large_files:
                self.logger.info("   ✅ No large files found to transfer")
                return {"transferred": False, "reason": "No large files found"}

            self.logger.info(f"   📦 Found {len(large_files)} large files to transfer")

            # Calculate space needed
            total_space_needed = sum(f["size_gb"] for f in large_files[:10])  # Top 10 largest

            # Transfer files until we reach target
            transferred = []
            total_transferred_gb = 0.0

            for file_info in large_files:
                if total_transferred_gb >= target_free_gb:
                    break

                file_path = Path(file_info["path"])
                result = self.transfer_file_to_nas(file_path, file_info["relative_path"])

                if result.get("success"):
                    transferred.append(file_info)
                    total_transferred_gb += file_info["size_gb"]

                    # Optionally remove local file after successful transfer
                    # (Keep for now, can add option to remove)
                    # file_path.unlink()

            self.logger.info(f"\n   ✅ Transferred {len(transferred)} files ({total_transferred_gb:.2f}GB) to NAS")

            return {
                "transferred": True,
                "files_count": len(transferred),
                "total_gb": total_transferred_gb,
                "files": transferred
            }

        except Exception as e:
            self.logger.error(f"Error in auto_transfer_to_nas: {e}", exc_info=True)
            raise
    def monitor_and_resolve(self, interval_seconds: int = 300) -> Dict[str, Any]:
        """Monitor storage and automatically resolve issues"""
        self.logger.info("="*80)
        self.logger.info("STORAGE MONITORING & AUTO-RESOLUTION")
        self.logger.info("="*80)

        space_info = self.check_local_disk_space()
        nas_info = self.check_nas_storage()

        # Report status
        self.logger.info("LOCAL STORAGE:")
        for drive in space_info.get("drives", []):
            status_icon = "🔴" if drive["status"] == "critical" else "⚠️" if drive["status"] == "low" else "✅"
            self.logger.info(f"   {status_icon} {drive['drive']}: {drive['free_gb']:.2f}GB free ({drive['used_percent']:.1f}% used)")

        self.logger.info("\nNAS STORAGE:")
        if nas_info.get("available"):
            self.logger.info(f"   ✅ NAS: {nas_info.get('available', 'N/A')} available")
            self.logger.info(f"   📊 Usage: {nas_info.get('use_percent', 'N/A')}")
            if nas_info.get("cloud_aggregate_info") != "Not configured":
                self.logger.info(f"   ☁️  Cloud Aggregate: {nas_info.get('cloud_aggregate_info', 'N/A')}")
            else:
                self.logger.warning("   ⚠️  Cloud storage aggregate NOT CONFIGURED")
                self.logger.info("   💡 Recommendation: Configure NAS cloud storage aggregate for better storage management")
        else:
            self.logger.warning(f"   ❌ NAS not available: {nas_info.get('error', 'Unknown error')}")

        # Auto-resolve if needed
        critical_drives = space_info.get("critical_drives", [])
        low_space_drives = space_info.get("low_space_drives", [])

        if critical_drives or low_space_drives:
            self.logger.info("\n   🔧 Auto-resolving space issues...")
            transfer_result = self.auto_transfer_to_nas(target_free_gb=20.0)
            return {
                "monitored": True,
                "space_info": space_info,
                "nas_info": nas_info,
                "transfer_result": transfer_result
            }
        else:
            self.logger.info("\n   ✅ No space issues detected")
            return {
                "monitored": True,
                "space_info": space_info,
                "nas_info": nas_info,
                "transfer_result": {"transferred": False, "reason": "No space issues"}
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
                self.monitor_and_resolve()
                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"   ❌ Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retry


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Storage Engineering Team - Monitor & Auto-Transfer to NAS")
    parser.add_argument("--monitor", action="store_true", help="Run one-time monitoring check")
    parser.add_argument("--auto-transfer", action="store_true", help="Auto-transfer files to NAS")
    parser.add_argument("--start-daemon", action="store_true", help="Start continuous monitoring daemon")
    parser.add_argument("--check-nas", action="store_true", help="Check NAS storage status")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds (default: 300)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    team = StorageEngineeringTeam(project_root)

    if args.check_nas:
        nas_info = team.check_nas_storage()
        print(json.dumps(nas_info, indent=2, default=str))
    elif args.auto_transfer:
        result = team.auto_transfer_to_nas()
        print(json.dumps(result, indent=2, default=str))
    elif args.start_daemon:
        team.start_continuous_monitoring(interval_seconds=args.interval)
        print("Monitoring daemon started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            team.stop_continuous_monitoring()
    else:
        # Default: monitor once
        result = team.monitor_and_resolve()
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":


    main()