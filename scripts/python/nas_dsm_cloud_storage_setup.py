#!/usr/bin/env python3
"""
NAS DSM Cloud Storage Setup & Integration

Configures and integrates Synology DSM Cloud Storage packages:
- Cloud Sync
- Cloud Station/Drive
- Hyper Backup to cloud
- Integration with Lumina project storage
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NASDSMCloudStorage")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("⚠️  requests not available - install: pip install requests")


class NASDSMCloudStorage:
    """
    NAS DSM Cloud Storage Setup & Integration

    Configures Synology DSM cloud storage packages and integrates with Lumina.
    """

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5000, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize DSM Cloud Storage manager

        Args:
            nas_ip: NAS IP address
            nas_port: DSM web interface port (default: 5000)
            username: DSM admin username
            password: DSM admin password
        """
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.base_url = f"http://{nas_ip}:{nas_port}"

        self.username = username or os.getenv("NAS_USERNAME")
        self.password = password or os.getenv("NAS_PASSWORD")

        self.session = None
        self.sid = None  # Session ID

        self.logger = logger

        logger.info(f"🖥️  NAS DSM Cloud Storage Manager initialized")
        logger.info(f"   NAS: {self.base_url}")

    def connect(self) -> bool:
        """Connect to DSM and authenticate"""
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests library not available")
            return False

        if not self.username or not self.password:
            logger.error("❌ NAS username/password not provided")
            return False

        try:
            self.session = requests.Session()

            # Login to DSM
            login_url = f"{self.base_url}/webapi/auth.cgi"
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "login",
                "account": self.username,
                "passwd": self.password,
                "session": "FileStation",
                "format": "sid"
            }

            response = self.session.get(login_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.sid = data["data"]["sid"]
                logger.info("✅ Connected to DSM")
                return True
            else:
                logger.error(f"❌ Authentication failed: {data.get('error', {}).get('code')}")
                return False

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    def check_cloud_packages(self) -> Dict[str, Any]:
        """Check installed cloud storage packages"""
        if not self.sid:
            logger.error("❌ Not connected to DSM. Call connect() first.")
            return {}

        packages = {}

        # Check Cloud Sync
        packages['cloud_sync'] = self._check_package_status("CloudSync")

        # Check Cloud Station/Drive
        packages['cloud_station'] = self._check_package_status("CloudStationServer")
        packages['drive'] = self._check_package_status("Drive")

        # Check Hyper Backup
        packages['hyper_backup'] = self._check_package_status("HyperBackup")

        return packages

    def _check_package_status(self, package_name: str) -> Dict[str, Any]:
        """Check if a package is installed and running"""
        try:
            url = f"{self.base_url}/webapi/query.cgi"
            params = {
                "api": "SYNO.Core.Package",
                "version": "1",
                "method": "list",
                "additional": "true",
                "_sid": self.sid
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                packages = data.get("data", {}).get("packages", [])
                for pkg in packages:
                    if pkg.get("name") == package_name:
                        return {
                            "installed": True,
                            "running": pkg.get("status") == "running",
                            "version": pkg.get("version"),
                            "status": pkg.get("status")
                        }

            return {"installed": False, "running": False}

        except Exception as e:
            logger.warning(f"⚠️  Could not check {package_name}: {e}")
            return {"installed": None, "error": str(e)}

    def configure_cloud_sync(self, provider: str, access_key: str, 
                            secret_key: str, sync_paths: List[str]) -> bool:
        """
        Configure Cloud Sync with a cloud provider

        Args:
            provider: Provider name (e.g., "dropbox", "onedrive", "googledrive")
            access_key: Provider access key/token
            secret_key: Provider secret key
            sync_paths: List of local paths to sync
        """
        if not self.sid:
            logger.error("❌ Not connected to DSM")
            return False

        logger.info(f"📦 Configuring Cloud Sync with {provider}...")

        # This would require specific Cloud Sync API calls
        # Implementation depends on DSM version and Cloud Sync API version
        logger.warning("⚠️  Cloud Sync configuration via API requires specific implementation")
        logger.info("   Configure Cloud Sync manually via DSM Package Manager:")
        logger.info("   1. Open DSM Package Manager")
        logger.info("   2. Install/Open Cloud Sync")
        logger.info("   3. Add cloud service")
        logger.info("   4. Configure sync tasks")

        return True

    def setup_lumina_integration(self, local_path: str, remote_path: str) -> bool:
        try:
            """
            Set up integration between Lumina project and cloud storage

            Args:
                local_path: Local project path on NAS
                remote_path: Remote cloud path
            """
            logger.info("🔗 Setting up Lumina cloud storage integration...")

            config = {
                "nas_ip": self.nas_ip,
                "local_path": local_path,
                "remote_path": remote_path,
                "sync_enabled": True,
                "sync_mode": "bidirectional"  # or "upload_only", "download_only"
            }

            # Save configuration
            config_path = Path(__file__).parent.parent.parent / "config" / "nas_cloud_storage.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Configuration saved to {config_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error in setup_lumina_integration: {e}", exc_info=True)
            raise
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current cloud sync status"""
        if not self.sid:
            return {"error": "Not connected"}

        # Check Cloud Sync tasks
        try:
            url = f"{self.base_url}/webapi/entry.cgi"
            params = {
                "api": "SYNO.CloudSync.Task",
                "version": "1",
                "method": "list",
                "_sid": self.sid
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "tasks": data.get("data", {}).get("tasks", []),
                        "total_tasks": len(data.get("data", {}).get("tasks", []))
                    }
        except Exception as e:
            logger.warning(f"⚠️  Could not get sync status: {e}")

        return {"error": "Could not retrieve status"}

    def disconnect(self):
        """Disconnect from DSM"""
        if self.sid and self.session:
            try:
                logout_url = f"{self.base_url}/webapi/auth.cgi"
                params = {
                    "api": "SYNO.API.Auth",
                    "version": "1",
                    "method": "logout",
                    "session": "FileStation",
                    "_sid": self.sid
                }
                self.session.get(logout_url, params=params, timeout=5)
            except:
                pass

        self.sid = None
        self.session = None


def main():
    try:
        """Main entry point"""
        print("="*70)
        print("🖥️  NAS DSM Cloud Storage Setup")
        print("="*70)
        print()

        # Initialize
        cloud_storage = NASDSMCloudStorage()

        # Check if we can connect
        print("📡 Connecting to DSM...")
        if not cloud_storage.connect():
            print("❌ Could not connect to DSM")
            print()
            print("Please ensure:")
            print("  1. NAS is accessible at", cloud_storage.base_url)
            print("  2. NAS_USERNAME and NAS_PASSWORD environment variables are set")
            print("  3. Your account has admin privileges")
            return

        print("✅ Connected to DSM")
        print()

        # Check installed packages
        print("📦 Checking Cloud Storage Packages...")
        packages = cloud_storage.check_cloud_packages()

        for name, status in packages.items():
            if status.get("installed"):
                running = "✅ Running" if status.get("running") else "⚠️  Stopped"
                version = status.get("version", "?")
                print(f"   {name}: {running} (v{version})")
            elif status.get("installed") is False:
                print(f"   {name}: ❌ Not installed")
            else:
                print(f"   {name}: ⚠️  Could not check")

        print()

        # Get sync status
        print("📊 Cloud Sync Status...")
        sync_status = cloud_storage.get_sync_status()
        if "tasks" in sync_status:
            print(f"   Active sync tasks: {sync_status['total_tasks']}")
        else:
            print("   Could not retrieve sync status")

        print()

        # Setup integration
        print("🔗 Setting up Lumina Integration...")
        local_path = "/volume1/homes/admin/lumina"
        remote_path = "/Lumina"
        cloud_storage.setup_lumina_integration(local_path, remote_path)

        print()
        print("="*70)
        print("✅ Setup Complete!")
        print()
        print("Next steps:")
        print("  1. Install Cloud Sync package via DSM Package Manager if not installed")
        print("  2. Configure cloud provider (Dropbox, OneDrive, Google Drive, etc.)")
        print("  3. Set up sync tasks for Lumina project folders")
        print("  4. Verify sync is working correctly")
        print()

        cloud_storage.disconnect()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()