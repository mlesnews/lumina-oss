#!/usr/bin/env python3
"""
Hybrid Pip Cache Manager
Manages local (primary) and NAS (fallback) pip cache directories.

Strategy:
- Primary: Local cache (fast, always available)
- Fallback: NAS cache (when local unavailable, or for sharing)
- Sync: Optional sync between local and NAS for sharing
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Pip cache configuration."""
    local_path: Path
    nas_path: Path
    primary: str = "local"  # "local" or "nas"
    sync_enabled: bool = False
    sync_direction: str = "bidirectional"  # "local_to_nas", "nas_to_local", "bidirectional"


class HybridPipCacheManager:
    """Manages hybrid pip cache (local primary, NAS fallback)."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize cache manager."""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.local_cache = Path(os.environ.get(
            "LOCALAPPDATA",
            Path.home() / "AppData" / "Local"
        )) / "pip" / "cache"

        self.nas_cache = Path(r"\\<NAS_PRIMARY_IP>\data\cache\pip")
        self.config = CacheConfig(
            local_path=self.local_cache,
            nas_path=self.nas_cache,
            primary="local",
            sync_enabled=False
        )

    def check_local_cache(self) -> Tuple[bool, str]:
        """Check if local cache is available."""
        try:
            if not self.local_cache.exists():
                self.local_cache.mkdir(parents=True, exist_ok=True)

            # Test write
            test_file = self.local_cache / ".test_write"
            test_file.write_text("test")
            test_file.unlink()

            return True, "Local cache available"
        except Exception as e:
            return False, f"Local cache unavailable: {e}"

    def check_nas_cache(self) -> Tuple[bool, str]:
        """Check if NAS cache is available."""
        try:
            if not self.nas_cache.exists():
                # Try to create (may fail if network path not accessible)
                try:
                    self.nas_cache.mkdir(parents=True, exist_ok=True)
                except Exception:
                    return False, "NAS path not accessible (VPN required?)"

            # Test write
            test_file = self.nas_cache / ".test_write"
            try:
                test_file.write_text("test")
                test_file.unlink()
                return True, "NAS cache available"
            except Exception as e:
                return False, f"NAS cache not writable: {e}"
        except Exception as e:
            return False, f"NAS cache unavailable: {e}"

    def get_active_cache(self) -> Tuple[Path, str]:
        """Get active cache path (primary if available, fallback otherwise)."""
        if self.config.primary == "local":
            local_available, _ = self.check_local_cache()
            if local_available:
                return self.local_cache, "local"

            # Fallback to NAS
            nas_available, _ = self.check_nas_cache()
            if nas_available:
                logger.warning("Local cache unavailable, falling back to NAS")
                return self.nas_cache, "nas_fallback"
            else:
                logger.error("Both local and NAS caches unavailable")
                return self.local_cache, "local_forced"  # Use local even if unavailable

        else:  # primary == "nas"
            nas_available, _ = self.check_nas_cache()
            if nas_available:
                return self.nas_cache, "nas"

            # Fallback to local
            local_available, _ = self.check_local_cache()
            if local_available:
                logger.warning("NAS cache unavailable, falling back to local")
                return self.local_cache, "local_fallback"
            else:
                logger.error("Both NAS and local caches unavailable")
                return self.nas_cache, "nas_forced"  # Use NAS even if unavailable

    def configure_pip_cache(self) -> bool:
        """Configure pip to use active cache."""
        cache_path, cache_type = self.get_active_cache()

        try:
            # Set environment variable (takes precedence)
            os.environ["PIP_CACHE_DIR"] = str(cache_path)

            # Also set via pip config (backup)
            import subprocess
            result = subprocess.run(
                [
                    sys.executable, "-m", "pip", "config", "set",
                    "global.cache-dir", str(cache_path)
                ],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Pip cache configured: {cache_path} ({cache_type})")
                return True
            else:
                logger.warning(f"⚠️  Pip config failed, but environment variable set: {cache_path}")
                return True  # Environment variable is set, that's enough
        except Exception as e:
            logger.error(f"❌ Failed to configure pip cache: {e}")
            return False

    def sync_caches(self, direction: Optional[str] = None) -> bool:
        """Sync caches between local and NAS."""
        if not self.config.sync_enabled:
            logger.info("Cache sync is disabled")
            return False

        direction = direction or self.config.sync_direction
        local_available, _ = self.check_local_cache()
        nas_available, _ = self.check_nas_cache()

        if not local_available or not nas_available:
            logger.warning("Cannot sync: one or both caches unavailable")
            return False

        try:
            if direction in ("local_to_nas", "bidirectional"):
                logger.info("Syncing local → NAS...")
                self._sync_directory(self.local_cache, self.nas_cache)

            if direction in ("nas_to_local", "bidirectional"):
                logger.info("Syncing NAS → local...")
                self._sync_directory(self.nas_cache, self.local_cache)

            logger.info("✅ Cache sync complete")
            return True
        except Exception as e:
            logger.error(f"❌ Cache sync failed: {e}")
            return False

    def _sync_directory(self, source: Path, dest: Path) -> None:
        try:
            """Sync directory from source to destination."""
            if not source.exists():
                return

            dest.mkdir(parents=True, exist_ok=True)

            # Sync wheels directory
            wheels_src = source / "wheels"
            wheels_dest = dest / "wheels"
            if wheels_src.exists():
                self._sync_subdirectory(wheels_src, wheels_dest)

            # Sync http cache
            http_src = source / "http"
            http_dest = dest / "http"
            if http_src.exists():
                self._sync_subdirectory(http_src, http_dest)

            http_v2_src = source / "http-v2"
            http_v2_dest = dest / "http-v2"
            if http_v2_src.exists():
                self._sync_subdirectory(http_v2_src, http_v2_dest)

        except Exception as e:
            self.logger.error(f"Error in _sync_directory: {e}", exc_info=True)
            raise
    def _sync_subdirectory(self, source: Path, dest: Path) -> None:
        try:
            """Sync a subdirectory."""
            dest.mkdir(parents=True, exist_ok=True)

            for item in source.iterdir():
                dest_item = dest / item.name
                if item.is_file():
                    if not dest_item.exists() or item.stat().st_mtime > dest_item.stat().st_mtime:
                        shutil.copy2(item, dest_item)
                elif item.is_dir():
                    self._sync_subdirectory(item, dest_item)

        except Exception as e:
            self.logger.error(f"Error in _sync_subdirectory: {e}", exc_info=True)
            raise
    def get_status(self) -> dict:
        """Get cache status."""
        local_available, local_msg = self.check_local_cache()
        nas_available, nas_msg = self.check_nas_cache()
        active_cache, cache_type = self.get_active_cache()

        return {
            "local_cache": {
                "path": str(self.local_cache),
                "available": local_available,
                "message": local_msg
            },
            "nas_cache": {
                "path": str(self.nas_cache),
                "available": nas_available,
                "message": nas_msg
            },
            "active_cache": {
                "path": str(active_cache),
                "type": cache_type,
                "primary": self.config.primary
            },
            "sync_enabled": self.config.sync_enabled
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid Pip Cache Manager")
    parser.add_argument("--configure", action="store_true", help="Configure pip cache")
    parser.add_argument("--status", action="store_true", help="Show cache status")
    parser.add_argument("--sync", action="store_true", help="Sync caches")
    parser.add_argument("--direction", choices=["local_to_nas", "nas_to_local", "bidirectional"],
                       default="bidirectional", help="Sync direction")
    parser.add_argument("--primary", choices=["local", "nas"], default="local",
                       help="Primary cache location")

    args = parser.parse_args()

    manager = HybridPipCacheManager()
    manager.config.primary = args.primary
    manager.config.sync_enabled = args.sync

    if args.status:
        status = manager.get_status()
        print("\n" + "=" * 60)
        print("HYBRID PIP CACHE STATUS")
        print("=" * 60)
        print(f"\nLocal Cache:")
        print(f"  Path: {status['local_cache']['path']}")
        print(f"  Status: {'✅ Available' if status['local_cache']['available'] else '❌ Unavailable'}")
        print(f"  Message: {status['local_cache']['message']}")
        print(f"\nNAS Cache:")
        print(f"  Path: {status['nas_cache']['path']}")
        print(f"  Status: {'✅ Available' if status['nas_cache']['available'] else '❌ Unavailable'}")
        print(f"  Message: {status['nas_cache']['message']}")
        print(f"\nActive Cache:")
        print(f"  Path: {status['active_cache']['path']}")
        print(f"  Type: {status['active_cache']['type']}")
        print(f"  Primary: {status['active_cache']['primary']}")
        print("=" * 60 + "\n")

    if args.configure:
        success = manager.configure_pip_cache()
        sys.exit(0 if success else 1)

    if args.sync:
        success = manager.sync_caches(args.direction)
        sys.exit(0 if success else 1)

    if not any([args.status, args.configure, args.sync]):
        # Default: show status and configure
        status = manager.get_status()
        print("\n" + "=" * 60)
        print("HYBRID PIP CACHE MANAGER")
        print("=" * 60)
        print(f"\nLocal Cache: {'✅' if status['local_cache']['available'] else '❌'}")
        print(f"NAS Cache: {'✅' if status['nas_cache']['available'] else '❌'}")
        print(f"Active: {status['active_cache']['type']}")
        print("\nConfiguring pip cache...")
        manager.configure_pip_cache()
        print("=" * 60 + "\n")


if __name__ == "__main__":


    main()