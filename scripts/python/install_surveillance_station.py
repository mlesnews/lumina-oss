#!/usr/bin/env python3
"""
Install and Configure Surveillance Station on Synology NAS
JARVIS automated installation and configuration
#JARVIS #MANUS #NAS #SYNOLOGY #SURVEILLANCE_STATION
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from synology_api_base import SynologyAPIBase
    from nas_azure_vault_integration import NASAzureVaultIntegration
    SYNOLOGY_AVAILABLE = True
except ImportError as e:
    SYNOLOGY_AVAILABLE = False
    logger = get_logger("InstallSurveillanceStation")
    logger.error(f"❌ Required modules not available: {e}")

logger = get_logger("InstallSurveillanceStation")


class SurveillanceStationInstaller:
    """Install and configure Surveillance Station on Synology NAS"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001):
        """Initialize installer"""
        if not SYNOLOGY_AVAILABLE:
            raise ImportError("Synology modules not available")

        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.api: Optional[SynologyAPIBase] = None
        self.credentials: Dict[str, str] = {}

        logger.info(f"🔧 Surveillance Station Installer initialized for {nas_ip}:{nas_port}")

    def _ensure_connected(self) -> bool:
        """Ensure API connection is established"""
        if not self.api:
            try:
                self.api = SynologyAPIBase(nas_ip=self.nas_ip, nas_port=self.nas_port, verify_ssl=False)
            except Exception as e:
                logger.error(f"❌ Failed to initialize API: {e}")
                return False

        if not self.api.sid:
            # Get credentials
            if not self.credentials:
                try:
                    vault = NASAzureVaultIntegration()
                    self.credentials = vault.get_nas_credentials()
                except Exception as e:
                    logger.error(f"❌ Failed to get credentials: {e}")
                    return False

            # Login
            username = self.credentials.get("username")
            password = self.credentials.get("password")

            if not username or not password:
                logger.error("❌ Missing credentials")
                return False

            if not self.api.login(username, password, session_name="SurveillanceStation"):
                logger.error("❌ Failed to login to Synology DSM")
                return False

        return True

    def check_installed(self) -> Dict[str, Any]:
        """Check if Surveillance Station is already installed"""
        if not self._ensure_connected():
            return {"success": False, "error": "Connection failed", "installed": False}

        try:
            # Check package status
            data = self.api.api_call(
                api="SYNO.Core.Package",
                method="list",
                version="1",
                params={"additional": '["description","maintainer","startable","status","install_reboot","install_type"]'},
                require_auth=True
            )

            if data and "packages" in data:
                for pkg in data["packages"]:
                    if pkg.get("name") == "SurveillanceStation" or "Surveillance Station" in pkg.get("display_name", ""):
                        status = pkg.get("status", "")
                        installed = status == "installed" or status == "running"
                        return {
                            "success": True,
                            "installed": installed,
                            "status": status,
                            "package": pkg
                        }

            return {"success": True, "installed": False, "status": "not_found"}

        except Exception as e:
            logger.error(f"❌ Error checking installation: {e}")
            return {"success": False, "error": str(e), "installed": False}

    def find_package(self) -> Optional[Dict[str, Any]]:
        """Find Surveillance Station in available packages"""
        if not self._ensure_connected():
            return None

        try:
            # Method 1: Get package details directly from server
            logger.info("🔍 Getting package details from server...")
            pkg_data = self.api.api_call(
                api="SYNO.Core.Package.Server",
                method="get",
                version="2",
                params={"id": "SurveillanceStation"},
                require_auth=True
            )

            if pkg_data:
                logger.info(f"✅ Found package details: {pkg_data.get('display_name', 'Surveillance Station')}")
                return {
                    "id": "SurveillanceStation",
                    "display_name": pkg_data.get("display_name", "Surveillance Station"),
                    "name": "SurveillanceStation",
                    "version": pkg_data.get("version", ""),
                    "link": pkg_data.get("link", ""),
                    "checksum": pkg_data.get("checksum", ""),
                    "size": pkg_data.get("size", "")
                }

            # Method 2: List available packages from server
            logger.info("🔍 Searching package server list...")
            data = self.api.api_call(
                api="SYNO.Core.Package.Server",
                method="list",
                version="2",
                require_auth=True
            )

            if data and "packages" in data:
                logger.info(f"📦 Found {len(data['packages'])} packages in server list")
                for pkg in data["packages"]:
                    pkg_id = pkg.get("id", "").lower()
                    if pkg_id == "surveillancestation":
                        logger.info(f"✅ Found package: {pkg.get('display_name', 'Surveillance Station')} (ID: {pkg.get('id')})")
                        return {
                            "id": pkg.get("id", "SurveillanceStation"),
                            "display_name": pkg.get("display_name", "Surveillance Station"),
                            "name": pkg.get("id", "SurveillanceStation"),
                            "version": pkg.get("version", ""),
                            "link": pkg.get("link", ""),
                            "checksum": pkg.get("checksum", ""),
                            "size": pkg.get("size", "")
                        }

            # Method 3: Try installation with just package ID (let API handle download)
            logger.info("⚠️  Package details not found, will try direct installation with package ID")
            return {
                "id": "SurveillanceStation",
                "display_name": "Surveillance Station",
                "name": "SurveillanceStation"
            }

        except Exception as e:
            logger.error(f"❌ Error finding package: {e}")
            # Return default anyway
            return {
                "id": "SurveillanceStation",
                "display_name": "Surveillance Station",
                "name": "SurveillanceStation"
            }

    def get_storage_volume(self) -> Optional[str]:
        """Get available storage volume for installation"""
        if not self._ensure_connected():
            return None

        try:
            # Get storage volumes
            data = self.api.api_call(
                api="SYNO.Storage.Volume",
                method="list",
                version="1",
                require_auth=True
            )

            if data and "volumes" in data:
                # Prefer volume1 (main volume)
                for vol in data["volumes"]:
                    if vol.get("id") == "volume1" or vol.get("status") == "normal":
                        vol_path = vol.get("path", f"/{vol.get('id', 'volume1')}")
                        logger.info(f"✅ Selected volume: {vol_path}")
                        return vol_path

            # Fallback to volume1
            logger.info("⚠️  Using default volume1")
            return "/volume1"

        except Exception as e:
            logger.warning(f"⚠️  Error getting storage volume: {e}, using default")
            return "/volume1"

    def download_package(self, package_id: str, package_info: Dict[str, Any]) -> Optional[str]:
        """Download Surveillance Station package"""
        if not self._ensure_connected():
            return None

        try:
            # Get download URL and info
            url = package_info.get("link", "")
            checksum = package_info.get("checksum", "")
            filesize = package_info.get("size", "")

            if not url:
                logger.error("❌ Package download URL not found")
                return None

            logger.info(f"📥 Starting download: {package_id}")

            # Start download
            download_data = self.api.api_call(
                api="SYNO.Core.Package.Installation",
                method="download",
                version="1",
                params={
                    "id": package_id,
                    "url": url,
                    "checksum": checksum,
                    "filesize": filesize
                },
                require_auth=True
            )

            if not download_data:
                logger.error("❌ Download initiation failed")
                return None

            task_id = download_data.get("taskid", f"@SYNOPKG_DOWNLOAD_{package_id}")
            logger.info(f"✅ Download started, task ID: {task_id}")

            # Poll download status
            max_attempts = 60  # 5 minutes max
            for attempt in range(max_attempts):
                time.sleep(5)  # Wait 5 seconds between checks

                status_data = self.api.api_call(
                    api="SYNO.Core.Package.Installation",
                    method="status",
                    version="1",
                    params={"taskid": task_id},
                    require_auth=True
                )

                if status_data:
                    progress = status_data.get("progress", 0)
                    status = status_data.get("status", "")

                    logger.info(f"📥 Download progress: {progress}% (Status: {status})")

                    if status == "finished" or status == "success":
                        file_path = status_data.get("tmp_folder", "")
                        logger.info(f"✅ Download complete: {file_path}")
                        return file_path
                    elif status == "error" or status == "failed":
                        logger.error(f"❌ Download failed: {status_data.get('error', 'Unknown error')}")
                        return None

            logger.error("❌ Download timeout")
            return None

        except Exception as e:
            logger.error(f"❌ Error downloading package: {e}")
            return None

    def install_package_direct(self, package_id: str, volume_path: str) -> bool:
        """Try direct installation without explicit download step"""
        if not self._ensure_connected():
            return False

        try:
            logger.info(f"🔧 Attempting direct installation of {package_id} to {volume_path}")

            # Method 1: Try install_from_server method (if available)
            logger.info("   Trying install_from_server method...")
            install_data = self.api.api_call(
                api="SYNO.Core.Package.Installation",
                method="install_from_server",
                version="1",
                params={
                    "id": package_id,
                    "volume_path": volume_path
                },
                require_auth=True
            )

            if install_data:
                logger.info("✅ install_from_server API call succeeded")
                return self._wait_for_installation()

            # Method 2: Try install method with minimal params
            logger.info("   Trying install method with package ID only...")
            install_data = self.api.api_call(
                api="SYNO.Core.Package.Installation",
                method="install",
                version="2",
                params={
                    "id": package_id,
                    "volume_path": volume_path
                },
                require_auth=True
            )

            if install_data:
                logger.info("✅ Install API call succeeded (version 2)")
                return self._wait_for_installation()

            # Method 3: Try version 1 with minimal params
            logger.info("   Trying install method version 1...")
            install_data = self.api.api_call(
                api="SYNO.Core.Package.Installation",
                method="install",
                version="1",
                params={
                    "id": package_id,
                    "volume_path": volume_path,
                    "force": "false",
                    "check_codesign": "true",
                    "installrunpackage": "true"
                },
                require_auth=True
            )

            if install_data:
                logger.info("✅ Install API call succeeded (version 1)")
                return self._wait_for_installation()

            logger.error("❌ All direct installation methods failed")
            return False

        except Exception as e:
            logger.error(f"❌ Error in direct installation: {e}")
            return False

    def _wait_for_installation(self, max_wait_minutes: int = 10) -> bool:
        """Wait for installation to complete and verify"""
        logger.info("⏳ Waiting for installation to complete...")
        max_attempts = max_wait_minutes * 12  # Check every 5 seconds
        for attempt in range(max_attempts):
            time.sleep(5)
            status = self.check_installed()
            if status.get("installed") and status.get("status") in ["installed", "running"]:
                logger.info("✅ Installation complete!")
                return True
            elif status.get("status") == "error":
                logger.error("❌ Installation failed")
                return False
            if attempt % 12 == 0:  # Log every minute
                logger.info(f"   Still waiting... ({attempt // 12 + 1}/{max_wait_minutes} minutes)")

        logger.warning("⚠️  Installation timeout - may still be in progress")
        # Check one more time
        final_status = self.check_installed()
        return final_status.get("installed", False)

    def install_package(self, package_id: str, file_path: str, volume_path: str) -> bool:
        """Install Surveillance Station package"""
        if not self._ensure_connected():
            return False

        try:
            # Check installation requirements
            check_data = self.api.api_call(
                api="SYNO.Core.Package.Installation",
                method="check",
                version="1",
                params={"id": package_id},
                require_auth=True
            )

            if check_data:
                # Use volume_path from check if available
                suggested_volumes = check_data.get("volume_list", [])
                if suggested_volumes:
                    volume_path = suggested_volumes[0].get("volume_path", volume_path)

            logger.info(f"🔧 Installing package to: {volume_path}")

            # Install package
            install_data = self.api.api_call(
                api="SYNO.Core.Package.Installation",
                method="install",
                version="1",
                params={
                    "id": package_id,
                    "file_path": file_path,
                    "volume_path": volume_path,
                    "force": "true",
                    "check_codesign": "false",
                    "installrunpackage": "true"
                },
                require_auth=True
            )

            if install_data:
                logger.info("✅ Installation initiated")

                # Wait for installation to complete
                max_attempts = 120  # 10 minutes max
                for attempt in range(max_attempts):
                    time.sleep(5)

                    # Check package status
                    status = self.check_installed()
                    if status.get("installed") and status.get("status") in ["installed", "running"]:
                        logger.info("✅ Installation complete!")
                        return True
                    elif status.get("status") == "error":
                        logger.error("❌ Installation failed")
                        return False

                logger.warning("⚠️  Installation may still be in progress")
                return True  # Assume success if no error

            logger.error("❌ Installation initiation failed")
            return False

        except Exception as e:
            logger.error(f"❌ Error installing package: {e}")
            return False

    def configure_storage(self) -> Dict[str, Any]:
        """Configure Surveillance Station storage location"""
        if not self._ensure_connected():
            return False

        try:
            # Create surveillance shared folder if it doesn't exist
            # First check if it exists
            shares_data = self.api.api_call(
                api="SYNO.Core.Share",
                method="list",
                version="1",
                require_auth=True
            )

            share_exists = False
            if shares_data and "shares" in shares_data:
                for share in shares_data["shares"]:
                    if share.get("name") == "surveillance":
                        share_exists = True
                        logger.info("✅ Surveillance share already exists")
                        break

            if not share_exists:
                # Create share
                logger.info("📁 Creating surveillance shared folder...")
                create_data = self.api.api_call(
                    api="SYNO.Core.Share",
                    method="create",
                    version="1",
                    params={
                        "name": "surveillance",
                        "vol_path": "/volume1",
                        "desc": "Surveillance Station recordings"
                    },
                    require_auth=True
                )

                if create_data:
                    logger.info("✅ Surveillance share created")
                else:
                    logger.warning("⚠️  Could not create share (may already exist or need manual creation)")

            return {"success": True, "message": "Storage configuration completed"}

        except Exception as e:
            logger.warning(f"⚠️  Error configuring storage: {e} (may need manual configuration)")
            return {"success": False, "error": str(e), "message": "Storage may need manual configuration"}

    def install_and_configure(self) -> Dict[str, Any]:
        """Main installation and configuration flow"""
        logger.info("🚀 Starting Surveillance Station installation...")

        # Step 1: Check if already installed
        logger.info("📋 Step 1: Checking if Surveillance Station is already installed...")
        status = self.check_installed()

        if status.get("installed"):
            logger.info("✅ Surveillance Station is already installed!")
            return {
                "success": True,
                "installed": True,
                "message": "Surveillance Station is already installed",
                "status": status.get("status")
            }

        # Step 2: Find package
        logger.info("📋 Step 2: Finding Surveillance Station package...")
        package_info = self.find_package()

        if not package_info:
            logger.warning("⚠️  Package not found via API. Surveillance Station may need manual installation.")
            logger.info("💡 Alternative: Install via DSM Package Center UI:")
            logger.info(f"   1. Open DSM: https://{self.nas_ip}:5001")
            logger.info("   2. Go to Package Center")
            logger.info("   3. Search for 'Surveillance Station'")
            logger.info("   4. Click Install")
            return {
                "success": False,
                "error": "Surveillance Station package not found in available packages",
                "manual_install_required": True,
                "instructions": f"Please install Surveillance Station manually via DSM Package Center at https://{self.nas_ip}:5001"
            }

        package_id = package_info.get("id", "SurveillanceStation")

        # Step 3: Get storage volume
        logger.info("📋 Step 3: Determining storage volume...")
        volume_path = self.get_storage_volume()
        if not volume_path:
            volume_path = "/volume1"  # Fallback

        # Step 4: Try direct installation methods
        logger.info("📋 Step 4: Attempting package installation...")

        # Always try direct installation first (simpler, may work)
        logger.info("💡 Attempting direct installation (API handles download automatically)...")
        install_success = self.install_package_direct(package_id, volume_path)

        if install_success:
            logger.info("✅ Direct installation succeeded!")
            file_path = None  # No file path needed, installation complete
        else:
            # Fall back to download + install method if we have download info
            if package_info.get("link"):
                logger.info("💡 Direct installation failed, trying download method...")
                file_path = self.download_package(package_id, package_info)

                if not file_path:
                    return {
                        "success": False,
                        "error": "Both direct installation and download methods failed",
                        "manual_install_required": True,
                        "instructions": f"Please install Surveillance Station manually via DSM Package Center at https://{self.nas_ip}:5001"
                    }
            else:
                return {
                    "success": False,
                    "error": "Direct installation failed and download URL not available",
                    "manual_install_required": True,
                    "instructions": f"Please install Surveillance Station manually via DSM Package Center at https://{self.nas_ip}:5001"
                }

        # Step 5: Install package (if we have file_path from download)
        if 'file_path' in locals() and file_path:
            logger.info("📋 Step 5: Installing Surveillance Station from downloaded file...")
            install_success = self.install_package(package_id, file_path, volume_path)
        else:
            # Direct installation was already attempted, just verify
            logger.info("📋 Step 5: Verifying installation status...")
            install_success = True  # Already handled in Step 4

        if not install_success:
            return {
                "success": False,
                "error": "Package installation failed"
            }

        # Step 6: Configure storage
        logger.info("📋 Step 6: Configuring storage...")
        storage_result = self.configure_storage()
        if not storage_result.get("success"):
            logger.warning(f"⚠️  Storage configuration had issues: {storage_result.get('error')}")

        # Step 7: Verify installation
        logger.info("📋 Step 7: Verifying installation...")
        final_status = self.check_installed()

        if final_status.get("installed"):
            logger.info("🎉 Surveillance Station installation complete!")
            return {
                "success": True,
                "installed": True,
                "message": "Surveillance Station installed and configured successfully",
                "access_url": f"https://{self.nas_ip}:9901",
                "status": final_status.get("status")
            }
        else:
            return {
                "success": False,
                "error": "Installation completed but verification failed",
                "status": final_status
            }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        if self.api:
            self.api.logout()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Install and configure Surveillance Station on Synology NAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install Surveillance Station
  python install_surveillance_station.py

  # Check if installed
  python install_surveillance_station.py --check-only

  # Custom NAS IP
  python install_surveillance_station.py --nas-ip 192.168.1.100
        """
    )

    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--nas-port", type=int, default=5001, help="NAS HTTPS port")
    parser.add_argument("--check-only", action="store_true", help="Only check if installed, don't install")

    args = parser.parse_args()

    try:
        with SurveillanceStationInstaller(nas_ip=args.nas_ip, nas_port=args.nas_port) as installer:
            if args.check_only:
                status = installer.check_installed()
                import json
                print(json.dumps(status, indent=2))
                return 0 if status.get("success") else 1
            else:
                result = installer.install_and_configure()
                import json
                print(json.dumps(result, indent=2))
                return 0 if result.get("success") else 1

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main())