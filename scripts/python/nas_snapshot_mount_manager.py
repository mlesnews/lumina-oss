#!/usr/bin/env python3
"""
NAS Snapshot Mount Manager
Manages permanent Windows network drive mounts for NAS snapshot directories

Tags: #NAS #SNAPSHOT #MOUNT #PERMANENT #WINDOWS @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("NasSnapshotMountManager")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("NasSnapshotMountManager")


class NasSnapshotMountManager:
    """Manage NAS snapshot permanent mounts"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize mount manager"""
        self.project_root = Path(project_root) if project_root else script_dir.parent.parent
        self.config_file = self.project_root / "config" / "nas_snapshot_mount.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load mount configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        return {}

    def check_mounts(self) -> List[Dict[str, Any]]:
        """Check current NAS snapshot mounts"""
        logger.info("🔍 Checking NAS snapshot mounts...")

        nas_host = self.config.get("nas", {}).get("host", "<NAS_PRIMARY_IP>")
        mounts = []

        try:
            # Get all network drives
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-PSDrive -PSProvider FileSystem | Where-Object { $_.DisplayRoot -like '\\\\*' } | Select-Object Name, DisplayRoot | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    drives = json.loads(result.stdout)
                    if not isinstance(drives, list):
                        drives = [drives]
                except json.JSONDecodeError:
                    # No drives found or empty output
                    drives = []

                for drive in drives:
                    display_root = drive.get("DisplayRoot", "")
                    if nas_host in display_root or "snapshot" in display_root.lower():
                        mount_info = {
                            "drive_letter": drive.get("Name", ""),
                            "network_path": display_root,
                            "accessible": self._test_path(f"{drive.get('Name', '')}:\\")
                        }
                        mounts.append(mount_info)
                        logger.info(f"   Found: {mount_info['drive_letter']}: -> {display_root}")
        except Exception as e:
            logger.error(f"Error checking mounts: {e}")

        return mounts

    def _test_path(self, path: str) -> bool:
        """Test if path is accessible"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Test-Path '{path}'"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "True" in result.stdout
        except:
            return False

    def mount_snapshot(self, mount_config: Dict[str, Any]) -> bool:
        """Mount a snapshot directory"""
        drive_letter = mount_config.get("drive_letter", "S")
        network_path = mount_config.get("network_path", "")
        name = mount_config.get("name", "Unknown")

        logger.info(f"📁 Mounting {name}...")
        logger.info(f"   Drive: {drive_letter}:")
        logger.info(f"   Path: {network_path}")

        # Check if already mounted
        existing = self._get_drive_info(drive_letter)
        if existing:
            if existing.get("network_path") == network_path:
                logger.info(f"   ✅ Already mounted correctly")
                return True
            else:
                logger.warning(f"   ⚠️  Drive {drive_letter}: is mapped to: {existing.get('network_path')}")
                self._unmount_drive(drive_letter)

        # Test connection
        if not self._test_path(network_path):
            logger.error(f"   ❌ Cannot access network path")
            logger.error(f"   Check: NAS online, share enabled, permissions")
            return False

        # Mount drive
        try:
            result = subprocess.run(
                ["net", "use", f"{drive_letter}:", network_path, "/persistent:yes"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"   ✅ Successfully mounted")
                return True
            else:
                logger.error(f"   ❌ Failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            return False

    def _get_drive_info(self, drive_letter: str) -> Optional[Dict[str, Any]]:
        """Get information about a drive"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-PSDrive -Name '{drive_letter}' -ErrorAction SilentlyContinue | Select-Object Name, DisplayRoot | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                drive = json.loads(result.stdout)
                return {
                    "drive_letter": drive.get("Name", ""),
                    "network_path": drive.get("DisplayRoot", "")
                }
        except:
            pass
        return None

    def _unmount_drive(self, drive_letter: str) -> bool:
        """Unmount a drive"""
        try:
            result = subprocess.run(
                ["net", "use", f"{drive_letter}:", "/delete", "/yes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def setup_all_mounts(self) -> Dict[str, Any]:
        """Setup all configured mounts"""
        logger.info("="*80)
        logger.info("🗂️  Setting up NAS Snapshot Mounts")
        logger.info("="*80)

        results = {
            "mounted": [],
            "failed": [],
            "skipped": []
        }

        mounts = self.config.get("mounts", [])
        for mount in mounts:
            if mount.get("auto_mount", False):
                if self.mount_snapshot(mount):
                    results["mounted"].append(mount["name"])
                else:
                    results["failed"].append(mount["name"])
            else:
                results["skipped"].append(mount["name"])
                logger.info(f"⏭️  Skipping {mount['name']} (auto_mount: false)")

        logger.info("")
        logger.info("="*80)
        logger.info("📊 Setup Summary")
        logger.info("="*80)
        logger.info(f"Mounted: {len(results['mounted'])}")
        logger.info(f"Failed: {len(results['failed'])}")
        logger.info(f"Skipped: {len(results['skipped'])}")
        logger.info("="*80)

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="NAS Snapshot Mount Manager"
    )
    parser.add_argument("--check", action="store_true", help="Check current mounts")
    parser.add_argument("--setup", action="store_true", help="Setup all auto-mount configurations")
    parser.add_argument("--mount", type=str, help="Mount specific drive letter (e.g., S)")

    args = parser.parse_args()

    manager = NasSnapshotMountManager()

    if args.check:
        mounts = manager.check_mounts()
        if mounts:
            logger.info(f"\n✅ Found {len(mounts)} NAS snapshot mount(s)")
        else:
            logger.info("\n⚠️  No NAS snapshot mounts found")
            logger.info("Run with --setup to configure mounts")

    elif args.setup:
        manager.setup_all_mounts()

    elif args.mount:
        # Find mount config for drive letter
        mounts = manager.config.get("mounts", [])
        mount_config = next((m for m in mounts if m.get("drive_letter") == args.mount.upper()), None)
        if mount_config:
            manager.mount_snapshot(mount_config)
        else:
            logger.error(f"No configuration found for drive {args.mount}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()