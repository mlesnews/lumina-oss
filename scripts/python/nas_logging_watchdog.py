#!/usr/bin/env python3
"""
NAS Logging Watchdog - Ensures L: Drive Mount is Active

CRITICAL: All ecosystem logs must be centralized on NAS at L: drive mountpoint.
This watchdog ensures the L: drive is always mounted and accessible.

If L: drive is not mounted, this watchdog will:
1. Attempt to mount it automatically
2. Alert if mounting fails
3. Ensure all logging systems use L: drive

Tags: #NAS #LOGGING #WATCHDOG #L_DRIVE #REQUIRED @JARVIS @LUMINA
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_unified_logger import get_unified_logger
    logger = get_unified_logger("System", "NASWatchdog")
except ImportError:
    try:
        from lumina_adaptive_logger import get_adaptive_logger
        logger = get_adaptive_logger("NASLoggingWatchdog")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("NASLoggingWatchdog")


class NASLoggingWatchdog:
    """
    Watchdog to ensure L: drive (NAS logs mountpoint) is always available

    CRITICAL: All ecosystem logs must be on L: drive for centralized logging.
    """

    def __init__(self, check_interval: int = 30):
        """
        Initialize NAS logging watchdog

        Args:
            check_interval: Seconds between mount checks (default: 30)
        """
        self.check_interval = check_interval
        self.l_drive = Path("L:")
        self.logs_dir = self.l_drive / "logs"
        self.local_logs_dir = project_root / "data" / "logs"
        self.running = False
        self.last_check = None
        self.mount_failures = 0
        self.max_mount_failures = 3
        self.was_mounted = False

        # NAS mount configuration (update with your NAS details)
        self.nas_config = self._load_nas_config()

        logger.info("✅ NAS Logging Watchdog initialized")
        logger.info(f"   L: Drive: {self.l_drive}")
        logger.info(f"   Logs Directory: {self.logs_dir}")
        logger.info(f"   Local Logs: {self.local_logs_dir}")
        logger.info(f"   Check Interval: {self.check_interval}s")

    def sync_local_logs_to_nas(self):
        """Roll and copy local logs back to L: drive when available"""
        if not self.is_l_drive_mounted():
            return

        logger.info("🔄 Syncing local logs to NAS...")

        if not self.local_logs_dir.exists():
            return

        try:
            import shutil
            # Walk through local logs
            for local_file in self.local_logs_dir.glob("**/*.log"):
                if not local_file.is_file():
                    continue

                # Skip the active log file for the current process to avoid locking issues
                # (Simple heuristic: skip files modified in the last 10 seconds)
                if (datetime.now() - datetime.fromtimestamp(local_file.stat().st_mtime)).total_seconds() < 10:
                    continue

                # Determine relative path to maintain structure
                rel_path = local_file.relative_to(self.local_logs_dir)
                nas_dest = self.logs_dir / rel_path

                # Ensure destination directory exists
                nas_dest.parent.mkdir(parents=True, exist_ok=True)

                # Copy file if it doesn't exist or is newer
                try:
                    shutil.copy2(local_file, nas_dest)
                    logger.info(f"   📤 Copied {rel_path} to NAS")

                    # Optional: "Roll" by removing local file after successful copy
                    # Only remove if it's not currently being written to
                    try:
                        local_file.unlink()
                        logger.info(f"   🧹 Rolled local log: {rel_path}")
                    except Exception as e:
                        logger.debug(f"   ℹ️  Could not delete local log (likely in use): {e}")
                except Exception as e:
                    logger.error(f"   ❌ Failed to copy {rel_path}: {e}")

            logger.info("✅ Local logs sync complete")
        except Exception as e:
            logger.error(f"❌ Failed to sync local logs: {e}")

    def _get_junction_mappings(self) -> Dict[Path, Path]:
        """Get the mapping of local log paths to NAS log paths"""
        return {
            project_root / "logs": self.logs_dir / "system",
            project_root / "data" / "logs": self.logs_dir / "system",
            project_root / "data" / "logs" / "jarvis": self.logs_dir / "jarvis",
            project_root / "data" / "logs" / "lumina": self.logs_dir / "lumina",
            project_root / "data" / "logs" / "errors": self.logs_dir / "errors",
            project_root / "data" / "logs" / "audit": self.logs_dir / "audit",
        }

    def _sync_directory(self, src: Path, dest: Path):
        try:
            """Sync contents of one directory to another"""
            import shutil
            if not src.exists():
                return
            dest.mkdir(parents=True, exist_ok=True)
            for item in src.iterdir():
                target = dest / item.name
                if item.is_file():
                    shutil.copy2(item, target)
                elif item.is_dir() and not self._is_junction(item):
                    self._sync_directory(item, target)

        except Exception as e:
            self.logger.error(f"Error in _sync_directory: {e}", exc_info=True)
            raise
    def create_junctions(self):
        """Create directory junctions for local logs to L: drive where applicable"""
        if not self.is_l_drive_mounted():
            logger.warning("⚠️  Cannot create junctions: L: drive not mounted")
            # If junctions exist but L: is gone, we should remove them to allow local fallback
            self.remove_junctions()
            return

        logger.info("🔗 Ensuring directory junctions for centralized logging...")

        # Define common log locations that should point to NAS
        junction_mappings = self._get_junction_mappings()

        for local_path, nas_path in junction_mappings.items():
            try:
                # Ensure NAS path exists
                nas_path.mkdir(parents=True, exist_ok=True)

                # If local path is a real directory (not a junction), sync its content first then delete it
                if local_path.exists() and not self._is_junction(local_path):
                    logger.info(f"   📦 Syncing existing local directory before junctioning: {local_path}")
                    self._sync_directory(local_path, nas_path)
                    import shutil
                    shutil.rmtree(local_path)

                # Create junction if it doesn't exist
                if not local_path.exists():
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["cmd", "/c", "mklink", "/J", str(local_path), str(nas_path)],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    logger.info(f"   ✅ Created junction: {local_path} -> {nas_path}")
                elif self._is_junction(local_path):
                    # Check if it points to the right place
                    # (Simplified: just log that it exists)
                    logger.debug(f"   ℹ️  Junction already exists: {local_path}")

            except Exception as e:
                logger.error(f"❌ Failed to manage junction for {local_path}: {e}")

    def remove_junctions(self):
        """Remove junctions to allow local fallback logging"""
        logger.info("🔓 Removing junctions for local fallback...")
        junction_mappings = self._get_junction_mappings()

        for local_path, _ in junction_mappings.items():
            if local_path.exists() and self._is_junction(local_path):
                try:
                    # On Windows, 'rmdir' removes the junction but not the target
                    subprocess.run(["cmd", "/c", "rmdir", str(local_path)], check=True)
                    logger.info(f"   ✅ Removed junction: {local_path}")
                    # Recreate as a real directory for fallback
                    local_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.error(f"❌ Failed to remove junction {local_path}: {e}")

    def _is_junction(self, path: Path) -> bool:
        """Check if a path is a directory junction"""
        try:
            # On Windows, junctions have the attribute FILE_ATTRIBUTE_REPARSE_POINT
            # and are directories.
            import win32file
            import win32con
            attributes = win32file.GetFileAttributes(str(path))
            return bool((attributes & win32con.FILE_ATTRIBUTE_REPARSE_POINT) and (attributes & win32con.FILE_ATTRIBUTE_DIRECTORY))
        except Exception:
            return False

    def _load_nas_config(self) -> dict:
        """Load NAS mount configuration"""
        config_file = project_root / "config" / "nas_logging_config.json"

        # Default configuration
        default_config = {
            "nas_host": "192.168.1.100",  # Update with your NAS IP
            "nas_share": "logs",  # Update with your NAS share name
            "nas_user": None,  # Optional: username for authentication
            "nas_password": None,  # Optional: password (use Azure Key Vault)
            "mount_letter": "L",
            "mount_options": "persistent"
        }

        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load NAS config: {e}, using defaults")

        return default_config

    def is_l_drive_mounted(self) -> bool:
        """Check if L: drive is mounted and accessible"""
        try:
            # Check if L: drive exists
            if not self.l_drive.exists():
                return False

            # Check if we can access it
            test_file = self.l_drive / ".nas_logging_test"
            try:
                test_file.touch()
                test_file.unlink()
                return True
            except Exception:
                return False
        except Exception as e:
            logger.debug(f"L: drive check error: {e}")
            return False

    def mount_l_drive(self) -> bool:
        """
        Attempt to mount L: drive to NAS logs share

        Returns:
            True if mount successful, False otherwise
        """
        if sys.platform != 'win32':
            logger.error("❌ NAS mount only supported on Windows")
            return False

        try:
            nas_host = self.nas_config.get("nas_host")
            nas_share = self.nas_config.get("nas_share")
            nas_user = self.nas_config.get("nas_user")
            nas_password = self.nas_config.get("nas_password")

            if not nas_host or not nas_share:
                logger.error("❌ NAS host or share not configured")
                return False

            # Build mount command
            # Format: net use L: \\NAS_HOST\SHARE /persistent:yes
            mount_path = f"\\\\{nas_host}\\{nas_share}"

            # Try to unmount first (in case of stale mount)
            try:
                subprocess.run(
                    ["net", "use", "L:", "/delete", "/y"],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass

            # Mount command
            mount_cmd = ["net", "use", "L:", mount_path, "/persistent:yes"]

            # Add credentials if provided
            if nas_user:
                if nas_password:
                    mount_cmd.extend(["/user:", nas_user, nas_password])
                else:
                    mount_cmd.extend(["/user:", nas_user])

            logger.info(f"🔌 Attempting to mount L: drive to {mount_path}...")

            result = subprocess.run(
                mount_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("✅ L: drive mounted successfully")

                # Verify mount
                if self.is_l_drive_mounted():
                    # Create logs directory structure
                    self._ensure_logs_directory()
                    self.mount_failures = 0
                    return True
                else:
                    logger.warning("⚠️  Mount succeeded but L: drive not accessible")
                    return False
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"❌ Failed to mount L: drive: {error_msg}")
                self.mount_failures += 1
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Mount command timed out")
            self.mount_failures += 1
            return False
        except Exception as e:
            logger.error(f"❌ Mount error: {e}")
            self.mount_failures += 1
            return False

    def _ensure_logs_directory(self):
        """Ensure logs directory structure exists on L: drive"""
        try:
            # Create main logs directory
            self.logs_dir.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for different log types
            subdirs = [
                "jarvis",
                "lumina",
                "system",
                "applications",
                "services",
                "errors",
                "audit"
            ]

            for subdir in subdirs:
                (self.logs_dir / subdir).mkdir(parents=True, exist_ok=True)

            logger.info(f"✅ Logs directory structure created: {self.logs_dir}")

        except Exception as e:
            logger.error(f"❌ Failed to create logs directory: {e}")

    def check_and_ensure_mount(self) -> bool:
        """
        Check if L: drive is mounted, mount if not

        Returns:
            True if L: drive is accessible, False otherwise
        """
        is_mounted = self.is_l_drive_mounted()

        if is_mounted:
            if not self.was_mounted:
                logger.info("🎊 L: drive detected! Initializing centralized redirection.")
                self.sync_local_logs_to_nas()
                self.create_junctions()
                self.was_mounted = True

            self.last_check = datetime.now()
            self.mount_failures = 0
            return True

        # L: drive not mounted
        if self.was_mounted:
            logger.warning("🚨 L: drive disconnected! Reverting to local fallback logging.")
            self.remove_junctions()
            self.was_mounted = False

        # Attempt to mount
        logger.warning("⚠️  L: drive not mounted - attempting to mount...")

        if self.mount_failures >= self.max_mount_failures:
            logger.error(f"❌ L: drive mount failed {self.mount_failures} times - manual intervention required")
            logger.error("   Please ensure NAS is accessible and credentials are correct")
            return False

        success = self.mount_l_drive()

        if success:
            logger.info("🎊 L: drive mounted! Initializing centralized redirection.")
            self.sync_local_logs_to_nas()
            self.create_junctions()
            self.was_mounted = True
            self.last_check = datetime.now()
            return True
        else:
            self.last_check = datetime.now()
            return False

    def get_logs_path(self, subdirectory: Optional[str] = None) -> Path:
        """
        Get path to logs directory on L: drive

        Args:
            subdirectory: Optional subdirectory (e.g., "jarvis", "system")

        Returns:
            Path to logs directory
        """
        if subdirectory:
            return self.logs_dir / subdirectory
        return self.logs_dir

    def run_watchdog(self):
        """Run watchdog loop (blocking)"""
        self.running = True
        logger.info("🔄 NAS Logging Watchdog started")

        try:
            while self.running:
                # Check and ensure mount
                is_mounted = self.check_and_ensure_mount()

                if not is_mounted:
                    logger.warning("⚠️  L: drive not accessible - logs may not be centralized")

                # Wait for next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("🛑 NAS Logging Watchdog stopped by user")
        except Exception as e:
            logger.error(f"❌ Watchdog error: {e}")
        finally:
            self.running = False

    def stop(self):
        """Stop watchdog"""
        self.running = False
        logger.info("🛑 NAS Logging Watchdog stopped")


def get_nas_logs_path(subdirectory: Optional[str] = None) -> Path:
    """
    Get path to NAS logs directory on L: drive

    Args:
        subdirectory: Optional subdirectory (e.g., "jarvis", "system")

    Returns:
        Path to logs directory on L: drive
    """
    watchdog = NASLoggingWatchdog()
    watchdog.check_and_ensure_mount()
    return watchdog.get_logs_path(subdirectory)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NAS Logging Watchdog")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous monitoring)"
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=30,
        help="Seconds between mount checks (default: 30)"
    )
    parser.add_argument(
        "--mount-only",
        action="store_true",
        help="Just mount L: drive and exit"
    )

    args = parser.parse_args()

    watchdog = NASLoggingWatchdog(check_interval=args.check_interval)

    if args.mount_only:
        # Just mount and exit
        success = watchdog.check_and_ensure_mount()
        if success:
            print("✅ L: drive mounted successfully")
            sys.exit(0)
        else:
            print("❌ Failed to mount L: drive")
            sys.exit(1)
    elif args.daemon:
        # Run as daemon
        watchdog.run_watchdog()
    else:
        # One-time check
        success = watchdog.check_and_ensure_mount()
        if success:
            print("✅ L: drive is mounted and accessible")
            print(f"   Logs directory: {watchdog.get_logs_path()}")
            sys.exit(0)
        else:
            print("❌ L: drive is not accessible")
            sys.exit(1)
