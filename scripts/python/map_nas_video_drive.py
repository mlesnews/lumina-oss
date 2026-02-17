#!/usr/bin/env python3
"""
Map NAS Video Drive (V:) - Permanent Network Drive Mapping

Maps V: drive to NAS for video storage.
Creates permanent mapping that persists across reboots.

Tags: #NAS #VIDEO #NETWORK #DRIVE @LUMINA @JARVIS
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MapNASVideoDrive")


class NASVideoDriveMapper:
    """
    Maps V: drive to NAS for video storage

    Creates permanent network drive mapping
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize drive mapper"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("NASVideoDriveMapper")

        # Load NAS config
        self.nas_config = self._load_nas_config()
        self.network_drives_config = self._load_network_drives_config()

        # NAS settings
        self.nas_ip = self.nas_config.get("nas", {}).get("ip", "<NAS_PRIMARY_IP>")
        self.nas_hostname = "nas.local"  # Try hostname first, fallback to IP

        # Video share path - try common share names
        self.video_share_paths = [
            f"\\\\{self.nas_hostname}\\videos",
            f"\\\\{self.nas_hostname}\\video",
            f"\\\\{self.nas_hostname}\\media",
            f"\\\\{self.nas_hostname}\\share3",
            f"\\\\{self.nas_ip}\\videos",
            f"\\\\{self.nas_ip}\\video",
            f"\\\\{self.nas_ip}\\media",
            f"\\\\{self.nas_ip}\\share3",
            # Fallback to backups share (we know this exists)
            f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\videos"
        ]

        self.drive_letter = "V"

    def _load_nas_config(self) -> Dict[str, Any]:
        try:
            """Load NAS configuration"""
            config_path = self.project_root / "config" / "jupyter" / "nas_config.json"

            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_nas_config: {e}", exc_info=True)
            raise
    def _load_network_drives_config(self) -> Dict[str, Any]:
        try:
            """Load network drives configuration"""
            config_path = self.project_root / "scripts" / "network_drives_config.json"

            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return {"mappings": [], "options": {}}

        except Exception as e:
            self.logger.error(f"Error in _load_network_drives_config: {e}", exc_info=True)
            raise
    def find_video_share(self) -> Optional[str]:
        """Find available video share on NAS"""
        self.logger.info(f"🔍 Searching for video share on NAS ({self.nas_ip})...")

        # First, try to find a dedicated video share
        for share_path in self.video_share_paths[:-1]:  # Exclude backups fallback
            if self._test_share_access(share_path):
                self.logger.info(f"✅ Found accessible share: {share_path}")
                return share_path

        # If no video-specific share found, check if backups share exists
        backups_base = f"\\\\{self.nas_ip}\\backups"
        if self._test_share_access(backups_base):
            # Create videos subdirectory path
            backup_path = f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\videos"
            self.logger.info(f"✅ Using backups share: {backup_path}")
            self.logger.info(f"   Note: Videos will be stored in backups share")
            return backup_path

        self.logger.warning("⚠️  No accessible video share found")
        return None

    def _test_share_access(self, share_path: str) -> bool:
        """Test if share is accessible"""
        try:
            # Extract base share path (before subdirectories)
            if "\\" in share_path.replace("\\\\", ""):
                # Get base share (e.g., \\nas\backups from \\nas\backups\MATT_Backups\videos)
                parts = share_path.replace("\\\\", "").split("\\")
                base_share = f"\\\\{parts[0]}\\{parts[1]}"
            else:
                base_share = share_path

            # Try to view the share
            result = subprocess.run(
                ["net", "view", base_share],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Also try to access it directly with dir command
            if result.returncode == 0:
                dir_result = subprocess.run(
                    ["dir", base_share],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return dir_result.returncode == 0

            return False
        except Exception as e:
            self.logger.debug(f"Share access test failed for {share_path}: {e}")
            return False

    def map_drive(self, share_path: Optional[str] = None, username: Optional[str] = None, 
                  password: Optional[str] = None) -> bool:
        """Map V: drive to NAS share"""
        if not share_path:
            share_path = self.find_video_share()
            if not share_path:
                self.logger.error("❌ No video share found")
                return False

        self.logger.info(f"🗺️  Mapping {self.drive_letter}: drive to {share_path}...")

        # Disconnect existing mapping if present
        self.disconnect_drive()

        # Build net use command
        cmd = [
            "net", "use",
            f"{self.drive_letter}:",
            share_path,
            "/PERSISTENT:YES"  # Permanent mapping
        ]

        # Add credentials if provided
        if username and password:
            cmd.extend(["/USER:", username, password])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info(f"✅ Drive {self.drive_letter}: mapped successfully to {share_path}")

                # Update network drives config
                self._update_network_drives_config(share_path)

                return True
            else:
                self.logger.error(f"❌ Failed to map drive: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error mapping drive: {e}")
            return False

    def disconnect_drive(self) -> bool:
        """Disconnect V: drive"""
        self.logger.info(f"🔌 Disconnecting {self.drive_letter}: drive...")

        try:
            result = subprocess.run(
                ["net", "use", f"{self.drive_letter}:", "/DELETE", "/YES"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info(f"✅ Drive {self.drive_letter}: disconnected")
                return True
            else:
                # Drive might not be mapped - that's okay
                return True

        except Exception as e:
            self.logger.warning(f"⚠️  Error disconnecting drive: {e}")
            return False

    def verify_drive(self) -> bool:
        """Verify V: drive is mapped and accessible"""
        self.logger.info(f"🔍 Verifying {self.drive_letter}: drive...")

        try:
            # Check if drive exists
            v_drive = Path(f"{self.drive_letter}:\\")

            if v_drive.exists():
                # Try to access it
                try:
                    list(v_drive.iterdir())
                    self.logger.info(f"✅ Drive {self.drive_letter}: is mapped and accessible")
                    return True
                except Exception as e:
                    self.logger.warning(f"⚠️  Drive {self.drive_letter}: exists but not accessible: {e}")
                    return False
            else:
                self.logger.warning(f"⚠️  Drive {self.drive_letter}: is not mapped")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error verifying drive: {e}")
            return False

    def _update_network_drives_config(self, share_path: str):
        try:
            """Update network drives configuration"""
            config_path = self.project_root / "scripts" / "network_drives_config.json"

            # Check if V: drive already exists in config
            mappings = self.network_drives_config.get("mappings", [])

            # Remove existing V: drive mapping if present
            mappings = [m for m in mappings if m.get("drive") != self.drive_letter]

            # Add new V: drive mapping
            mappings.append({
                "drive": self.drive_letter,
                "path": share_path,
                "description": "NAS Video Storage"
            })

            self.network_drives_config["mappings"] = mappings

            # Save config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.network_drives_config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Updated network drives config: {config_path}")

        except Exception as e:
            self.logger.error(f"Error in _update_network_drives_config: {e}", exc_info=True)
            raise
    def get_drive_info(self) -> Dict[str, Any]:
        """Get information about V: drive"""
        info = {
            "drive_letter": self.drive_letter,
            "mapped": False,
            "path": None,
            "accessible": False
        }

        try:
            v_drive = Path(f"{self.drive_letter}:\\")

            if v_drive.exists():
                info["mapped"] = True
                info["path"] = str(v_drive)

                try:
                    list(v_drive.iterdir())
                    info["accessible"] = True
                except Exception:
                    info["accessible"] = False
        except Exception:
            pass

        return info


def main():
    """Main entry point"""
    import sys

    print("="*80)
    print("MAP NAS VIDEO DRIVE (V:)")
    print("="*80)

    mapper = NASVideoDriveMapper()

    # Show current status
    print(f"\n📊 Current Drive Status:")
    info = mapper.get_drive_info()
    print(f"   Drive Letter: {info['drive_letter']}:")
    print(f"   Mapped: {'✅' if info['mapped'] else '❌'}")
    print(f"   Accessible: {'✅' if info['accessible'] else '❌'}")
    if info['path']:
        print(f"   Path: {info['path']}")

    # Check for manual path argument
    share_path = None
    if len(sys.argv) > 1:
        share_path = sys.argv[1]
        print(f"\n📝 Using manual share path: {share_path}")
    else:
        # Find video share
        print(f"\n🔍 Finding video share on NAS...")
        share_path = mapper.find_video_share()

        # If not found, try backups path directly (we know this exists from config)
        if not share_path:
            backups_path = f"\\\\{mapper.nas_ip}\\backups"
            print(f"   💡 Trying known backups share: {backups_path}")
            share_path = backups_path

    if share_path:
        print(f"   ✅ Using share: {share_path}")

        # Map drive
        print(f"\n🗺️  Mapping V: drive...")
        if mapper.map_drive(share_path):
            print(f"   ✅ Drive mapped successfully!")

            # Verify
            print(f"\n🔍 Verifying drive...")
            if mapper.verify_drive():
                print(f"   ✅ Drive verified and accessible!")
                print(f"   📁 Videos will be stored at: V:\\quantum_anime\\videos")
            else:
                print(f"   ⚠️  Drive mapped but verification failed")
                print(f"   💡 Try accessing V: drive manually to verify")
        else:
            print(f"   ❌ Failed to map drive")
            print(f"   💡 You may need to:")
            print(f"      1. Provide NAS credentials")
            print(f"      2. Check network connectivity")
            print(f"      3. Verify share path is correct")
            print(f"\n   Example: python map_nas_video_drive.py \\\\<NAS_PRIMARY_IP>\\backups")
    else:
        print(f"   ❌ No video share found")
        print(f"   💡 Usage: python map_nas_video_drive.py [share_path]")
        print(f"   Example: python map_nas_video_drive.py \\\\<NAS_PRIMARY_IP>\\backups")

    print("\n✅ Drive mapping complete!")
    print("="*80)


if __name__ == "__main__":


    main()