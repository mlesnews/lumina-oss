#!/usr/bin/env python3
"""
NAS Storage Utility - Prevents Local Space Issues

Automatically uses NAS storage for logs, data, and monitoring files
to prevent local disk space issues. Falls back to local storage
if NAS is unavailable.

Tags: #NAS_STORAGE #SPACE_MANAGEMENT #LUMINA_CORE
"""

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("NASStorage")


class NASStorageUtility:
    """
    NAS Storage Utility - Manages storage paths with NAS fallback

    Automatically uses NAS for data/logs to prevent local space issues.
    Falls back gracefully to local storage if NAS unavailable.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize NAS storage utility

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        # Load NAS configuration
        self.nas_config = self._load_nas_config()
        self.nas_available = False
        self.nas_base_path = None
        self.fallback_to_local = True

        # Proxy-cache for deduplication and space optimization
        self.cache_enabled = True
        self.cache_dir = self.project_root / "data" / ".nas_cache"
        self.cache_index: Dict[str, Dict[str, Any]] = {}
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.deduplication_enabled = True  # Enable deduplication via content hashing

        # Try to connect to NAS
        self._initialize_nas_storage()

        # Initialize cache
        if self.cache_enabled:
            self._initialize_cache()

    def _load_nas_config(self) -> dict:
        """Load NAS configuration from config file"""
        config_path = self.project_root / "config" / "nas_config.json"
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.debug("✅ Loaded NAS config from %s", config_path)
                    return config
        except Exception as e:
            logger.debug("   Could not load NAS config: %s", e)

        # Default config
        return {
            "host": "<NAS_PRIMARY_IP>",
            "user": "mlesn",
            "ssh_port": 22
        }

    def _initialize_nas_storage(self):
        """Initialize NAS storage connection and determine base path"""
        # Check for mounted NAS drive (common Windows mount points)
        nas_mount_points = [
            Path("Z:\\"),  # Common NAS mount
            Path("Y:\\"),  # Alternative mount
            Path("X:\\"),  # Another alternative
            Path(f"\\\\{self.nas_config.get('host', '<NAS_PRIMARY_IP>')}\\"),  # UNC path
        ]

        # Also check for mapped network drives
        for drive_letter in "ZYXWVUTSRQPONMLKJIHGFEDCBA":
            mount_path = Path(f"{drive_letter}:\\")
            if mount_path.exists():
                try:
                    # Check if it's a network drive
                    if mount_path.is_mount() or os.path.ismount(str(mount_path)):
                        nas_mount_points.append(mount_path)
                except Exception:
                    pass

        # Try to find NAS storage
        for mount_point in nas_mount_points:
            if self._test_nas_path(mount_point):
                self.nas_base_path = mount_point / "lumina_data"
                self.nas_available = True
                logger.info("✅ NAS storage available at: %s", self.nas_base_path)
                # Ensure base directory exists
                self._ensure_nas_directory(self.nas_base_path)
                return

        # NAS not available - use local with fallback
        if self.fallback_to_local:
            self.nas_base_path = self.project_root / "data"
            logger.info("   ⚠️  NAS not available - using local storage: %s", self.nas_base_path)
            logger.info("   📁 Data will be stored locally (NAS unavailable)")
        else:
            logger.warning("   ⚠️  NAS not available and fallback disabled")

    def _test_nas_path(self, path: Path) -> bool:
        """Test if NAS path is accessible"""
        try:
            if not path.exists():
                return False
            # Try to create a test file
            test_file = path / ".nas_test"
            try:
                test_file.write_text("test", encoding='utf-8')
                test_file.unlink()
                return True
            except Exception:
                return False
        except Exception:
            return False

    def _ensure_nas_directory(self, path: Path):
        """Ensure NAS directory exists"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug("   ✅ NAS directory ready: %s", path)
        except Exception as e:
            logger.warning("   ⚠️  Could not create NAS directory: %s", e)
            self.nas_available = False
            if self.fallback_to_local:
                self.nas_base_path = self.project_root / "data"

    def get_storage_path(self, subdirectory: str = "", filename: Optional[str] = None) -> Path:
        """
        Get storage path (NAS if available, local otherwise)

        Args:
            subdirectory: Subdirectory within storage (e.g., "logs", "monitoring")
            filename: Optional filename

        Returns:
            Full path to storage location
        """
        if self.nas_base_path is None:
            # Fallback to local
            base = self.project_root / "data"
        else:
            base = self.nas_base_path

        # Build path
        if subdirectory:
            path = base / subdirectory
        else:
            path = base

        # Ensure directory exists
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning("   ⚠️  Could not create storage directory %s: %s", path, e)
            # Fallback to local
            path = self.project_root / "data" / subdirectory
            path.mkdir(parents=True, exist_ok=True)

        # Add filename if provided
        if filename:
            return path / filename
        return path

    def get_logs_path(self, filename: Optional[str] = None) -> Path:
        """Get path for log files (NAS if available)"""
        return self.get_storage_path("logs", filename)

    def get_monitoring_path(self, filename: Optional[str] = None) -> Path:
        """Get path for monitoring data (NAS if available)"""
        return self.get_storage_path("monitoring", filename)

    def get_data_path(self, subdirectory: str = "", filename: Optional[str] = None) -> Path:
        """Get path for general data (NAS if available)"""
        return self.get_storage_path(subdirectory, filename)

    def is_nas_available(self) -> bool:
        try:
            """Check if NAS storage is currently available"""
            if not self.nas_available:
                return False
            # Re-test NAS availability
            if self.nas_base_path and self.nas_base_path.exists():
                return True
            # NAS became unavailable - update status
            self.nas_available = False
            if self.fallback_to_local:
                self.nas_base_path = self.project_root / "data"
                logger.warning("   ⚠️  NAS became unavailable - switched to local storage")
            return False

        except Exception as e:
            self.logger.error(f"Error in is_nas_available: {e}", exc_info=True)
            raise
    def _initialize_cache(self):
        """Initialize proxy-cache for deduplication and space optimization"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Load cache index if exists
            if self.cache_index_file.exists():
                try:
                    with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                        self.cache_index = json.load(f)
                    logger.debug("   ✅ Loaded cache index (%d entries)", len(self.cache_index))
                except Exception as e:
                    logger.debug("   Could not load cache index: %s", e)
                    self.cache_index = {}
            logger.debug("   ✅ Proxy-cache initialized (deduplication enabled)")
        except Exception as e:
            logger.debug("   Could not initialize cache: %s", e)
            self.cache_enabled = False

    def _get_content_hash(self, content: bytes) -> str:
        """Get SHA256 hash of content for deduplication"""
        return hashlib.sha256(content).hexdigest()

    def _save_with_deduplication(self, file_path: Path, content: bytes) -> bool:
        """
        Save file with deduplication - if same content exists, create hardlink/symlink

        This prevents storing duplicate data and saves space.
        """
        if not self.deduplication_enabled:
            # No deduplication - just write
            file_path.write_bytes(content)
            return True

        content_hash = self._get_content_hash(content)
        cache_entry_path = self.cache_dir / "content" / content_hash[:2] / content_hash

        # Check if we already have this content
        if cache_entry_path.exists():
            # Content already cached - create link instead of copying
            try:
                if file_path.exists():
                    file_path.unlink()
                # Try hardlink first (saves space, same inode)
                try:
                    os.link(str(cache_entry_path), str(file_path))
                    logger.debug("   🔗 Created hardlink (deduplicated): %s", file_path.name)
                except (OSError, NotImplementedError):
                    # Fallback to copy if hardlink not supported
                    shutil.copy2(cache_entry_path, file_path)
                    logger.debug("   📋 Copied from cache (deduplicated): %s", file_path.name)
                return True
            except Exception as e:
                logger.debug("   Could not create link, falling back to write: %s", e)

        # New content - save to cache and write
        try:
            cache_entry_path.parent.mkdir(parents=True, exist_ok=True)
            cache_entry_path.write_bytes(content)

            # Update cache index
            self.cache_index[content_hash] = {
                "path": str(cache_entry_path),
                "size": len(content),
                "created": datetime.now().isoformat(),
                "access_count": 0
            }
            self._save_cache_index()

            # Write to destination
            file_path.write_bytes(content)
            return True
        except Exception as e:
            logger.warning("   ⚠️  Could not save with deduplication: %s", e)
            # Fallback to direct write
            file_path.write_bytes(content)
            return True

    def _save_cache_index(self):
        """Save cache index to disk"""
        if not self.cache_enabled:
            return
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.debug("   Could not save cache index: %s", e)

    def write_file(self, file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
        """
        Write file with deduplication support

        Args:
            file_path: Path to write to
            content: Content to write (string)
            encoding: Text encoding

        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to bytes for deduplication
            content_bytes = content.encode(encoding)

            # Use deduplication if enabled
            if self.cache_enabled and self.deduplication_enabled:
                return self._save_with_deduplication(file_path, content_bytes)
            else:
                file_path.write_text(content, encoding=encoding)
                return True
        except Exception as e:
            logger.warning("   ⚠️  Could not write file: %s", e)
            return False

    def write_file_bytes(self, file_path: Path, content: bytes) -> bool:
        """
        Write binary file with deduplication support

        Args:
            file_path: Path to write to
            content: Content to write (bytes)

        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Use deduplication if enabled
            if self.cache_enabled and self.deduplication_enabled:
                return self._save_with_deduplication(file_path, content)
            else:
                file_path.write_bytes(content)
                return True
        except Exception as e:
            logger.warning("   ⚠️  Could not write file: %s", e)
            return False

    def get_storage_info(self) -> dict:
        """Get storage information"""
        info = {
            "nas_available": self.is_nas_available(),
            "storage_path": str(self.nas_base_path) if self.nas_base_path else None,
            "fallback_enabled": self.fallback_to_local,
            "nas_config": {
                "host": self.nas_config.get("host"),
                "user": self.nas_config.get("user")
            },
            "cache": {
                "enabled": self.cache_enabled,
                "deduplication_enabled": self.deduplication_enabled,
                "cache_entries": len(self.cache_index),
                "cache_dir": str(self.cache_dir) if self.cache_enabled else None
            }
        }

        # Calculate cache size if available
        if self.cache_enabled and self.cache_dir.exists():
            try:
                cache_size = sum(
                    f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file()
                )
                info["cache"]["cache_size_bytes"] = cache_size
                info["cache"]["cache_size_mb"] = cache_size / (1024 * 1024)
            except Exception:
                pass

        return info


# Global instance
_nas_storage_instance = None


def get_nas_storage() -> NASStorageUtility:
    """Get or create global NAS storage utility instance"""
    global _nas_storage_instance
    if _nas_storage_instance is None:
        _nas_storage_instance = NASStorageUtility()
    return _nas_storage_instance


def get_storage_path(subdirectory: str = "", filename: Optional[str] = None) -> Path:
    """Get storage path (NAS if available, local otherwise)"""
    storage = get_nas_storage()
    return storage.get_storage_path(subdirectory, filename)


def get_logs_path(filename: Optional[str] = None) -> Path:
    """Get path for log files (NAS if available)"""
    storage = get_nas_storage()
    return storage.get_logs_path(filename)


def get_monitoring_path(filename: Optional[str] = None) -> Path:
    """Get path for monitoring data (NAS if available)"""
    storage = get_nas_storage()
    return storage.get_monitoring_path(filename)


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="NAS Storage Utility")
    parser.add_argument("--info", action="store_true", help="Show storage information")
    parser.add_argument("--test", action="store_true", help="Test NAS storage")

    args = parser.parse_args()

    storage = get_nas_storage()

    if args.info:
        info = storage.get_storage_info()
        print("\n📊 NAS Storage Information:")
        print(f"   NAS Available: {info['nas_available']}")
        print(f"   Storage Path: {info['storage_path']}")
        print(f"   Fallback Enabled: {info['fallback_enabled']}")
        print(f"   NAS Host: {info['nas_config']['host']}")
        print(f"   NAS User: {info['nas_config']['user']}")
        print(f"\n💾 Proxy-Cache Information:")
        cache_info = info.get('cache', {})
        print(f"   Cache Enabled: {cache_info.get('enabled', False)}")
        print(f"   Deduplication: {cache_info.get('deduplication_enabled', False)}")
        print(f"   Cache Entries: {cache_info.get('cache_entries', 0)}")
        if cache_info.get('cache_size_mb'):
            print(f"   Cache Size: {cache_info['cache_size_mb']:.2f} MB")
        print(f"   Cache Directory: {cache_info.get('cache_dir', 'N/A')}")

    if args.test:
        print("\n🧪 Testing NAS storage...")
        test_path = storage.get_monitoring_path("test_file.txt")
        try:
            test_path.write_text("NAS storage test", encoding='utf-8')
            content = test_path.read_text(encoding='utf-8')
            print(f"   ✅ Write/Read test successful: {test_path}")
            print(f"   Content: {content}")
            test_path.unlink()
            print("   ✅ Test file cleaned up")
        except Exception as e:
            print(f"   ❌ Test failed: {e}")

    return 0


if __name__ == "__main__":


    sys.exit(main())