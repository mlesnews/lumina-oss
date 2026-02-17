#!/usr/bin/env python3
"""
Host/Machine-Specific Proxy Caching System for Lumina
Provides proxy caching with local client host machine isolation

Features:
- Host/machine-specific cache keys (where Cursor IDE runs)
- Automatic expiry and cleanup
- Cache invalidation strategies
- IDE-aware caching (Cursor default)
- Multiple cache backends (file, memory, optional Redis)
"""

import hashlib
import json
import shutil
import socket
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import os
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class HostAwareCache:
    """Host/machine-specific caching system with proxy pattern for local Lumina clients"""

    def __init__(
        self,
        cache_root: Path,
        host_id: Optional[str] = None,
        ide_name: str = "cursor",
        default_expiry_hours: int = 24,
        max_cache_size_mb: int = 1000
    ):
        """
        Initialize host-aware cache

        Args:
            cache_root: Root directory for cache storage
            host_id: Host/machine identifier (auto-detected if None)
            ide_name: IDE name (default: "cursor")
            default_expiry_hours: Default cache expiry time
            max_cache_size_mb: Maximum cache size in MB before cleanup
        """
        self.cache_root = Path(cache_root)
        self.default_expiry_hours = default_expiry_hours
        self.max_cache_size_mb = max_cache_size_mb
        self.ide_name = ide_name.lower()

        # Detect or set host ID (local machine identifier)
        self.host_id = host_id or self._detect_host_id()

        # Host-specific cache directory (local to this machine where IDE runs)
        self.host_cache_dir = self.cache_root / "hosts" / self.host_id / self.ide_name
        self.host_cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache metadata file
        self.metadata_file = self.host_cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()

    def _detect_host_id(self) -> str:
        """Detect unique host/machine identifier"""
        # Try to get a unique machine identifier
        # Use hostname + username as default identifier

        hostname = socket.gethostname()
        username = os.getenv("USERNAME") or os.getenv("USER") or "unknown"

        # Try to get machine-specific info
        machine_info = []

        # Add hostname
        machine_info.append(hostname.lower())

        # Add username
        machine_info.append(username.lower())

        # Add OS platform
        machine_info.append(platform.system().lower())

        # Try to get MAC address (first network interface) for uniqueness
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                           for ele in range(0,8*6,8)][::-1])
            machine_info.append(mac.replace(':', ''))
        except:
            pass

        # Create host ID from machine info
        host_id_string = "_".join(machine_info)
        host_id = hashlib.md5(host_id_string.encode()).hexdigest()[:16]

        return f"{hostname}_{username}_{host_id}"

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {"entries": {}, "stats": {}}
        return {"entries": {}, "stats": {}}

    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache metadata: {e}")

    def _generate_cache_key(self, key_parts: List[str], namespace: str = "default") -> str:
        """Generate host-aware cache key"""
        # Include host ID and IDE name in key generation
        full_key = f"{self.host_id}:{self.ide_name}:{namespace}:{':'.join(str(p) for p in key_parts)}"
        return hashlib.md5(full_key.encode()).hexdigest()

    def get(
        self,
        key_parts: List[str],
        namespace: str = "default",
        expiry_hours: Optional[int] = None
    ) -> Optional[Any]:
        """
        Get cached value

        Args:
            key_parts: Parts to generate cache key from
            namespace: Cache namespace (e.g., "r5", "syphon", "holocron")
            expiry_hours: Override default expiry

        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._generate_cache_key(key_parts, namespace)
        cache_file = self.host_cache_dir / namespace / f"{cache_key}.cache"
        cache_meta_file = self.host_cache_dir / namespace / f"{cache_key}.meta"

        if not cache_file.exists() or not cache_meta_file.exists():
            return None

        try:
            # Load metadata
            with open(cache_meta_file, 'r') as f:
                meta = json.load(f)

            # Check expiry
            cached_time = datetime.fromisoformat(meta.get("cached_at", ""))
            expiry = expiry_hours or meta.get("expiry_hours", self.default_expiry_hours)

            if datetime.now() - cached_time > timedelta(hours=expiry):
                # Expired - delete cache
                cache_file.unlink(missing_ok=True)
                cache_meta_file.unlink(missing_ok=True)
                self._remove_metadata_entry(cache_key)
                return None

            # Load cached value
            with open(cache_file, 'rb') as f:
                if meta.get("type") == "json":
                    return json.load(f)
                elif meta.get("type") == "text":
                    return f.read().decode('utf-8')
                else:
                    return f.read()

        except Exception as e:
            # Cache corrupted - delete it
            cache_file.unlink(missing_ok=True)
            cache_meta_file.unlink(missing_ok=True)
            self._remove_metadata_entry(cache_key)
            return None

    def set(
        self,
        key_parts: List[str],
        value: Any,
        namespace: str = "default",
        expiry_hours: Optional[int] = None,
        cache_type: str = "json"
    ) -> bool:
        """
        Cache a value

        Args:
            key_parts: Parts to generate cache key from
            value: Value to cache
            namespace: Cache namespace
            expiry_hours: Override default expiry
            cache_type: Type of cache ("json", "text", "binary")

        Returns:
            True if cached successfully
        """
        cache_key = self._generate_cache_key(key_parts, namespace)
        namespace_dir = self.host_cache_dir / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)

        cache_file = namespace_dir / f"{cache_key}.cache"
        cache_meta_file = namespace_dir / f"{cache_key}.meta"

        try:
            # Save cached value
            if cache_type == "json":
                with open(cache_file, 'w') as f:
                    json.dump(value, f, indent=2)
            elif cache_type == "text":
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(str(value))
            else:
                with open(cache_file, 'wb') as f:
                    f.write(value if isinstance(value, bytes) else str(value).encode())

            # Save metadata
            with open(cache_meta_file, 'w') as f:
                json.dump({
                    "cache_key": cache_key,
                    "key_parts": key_parts,
                    "namespace": namespace,
                    "type": cache_type,
                    "cached_at": datetime.now().isoformat(),
                    "expiry_hours": expiry_hours or self.default_expiry_hours,
                    "host_id": self.host_id,
                    "ide_name": self.ide_name,
                    "size": cache_file.stat().st_size
                }, f, indent=2)

            # Update metadata
            self._update_metadata_entry(cache_key, namespace, cache_file.stat().st_size)

            # Check cache size and clean if needed
            self._enforce_cache_size_limit()

            return True

        except Exception as e:
            print(f"Warning: Could not cache value: {e}")
            return False

    def invalidate(self, key_parts: List[str], namespace: str = "default"):
        """Invalidate specific cache entry"""
        cache_key = self._generate_cache_key(key_parts, namespace)
        namespace_dir = self.host_cache_dir / namespace
        cache_file = namespace_dir / f"{cache_key}.cache"
        cache_meta_file = namespace_dir / f"{cache_key}.meta"

        cache_file.unlink(missing_ok=True)
        cache_meta_file.unlink(missing_ok=True)
        self._remove_metadata_entry(cache_key)

    def invalidate_namespace(self, namespace: str):
        try:
            """Invalidate all entries in a namespace"""
            namespace_dir = self.host_cache_dir / namespace
            if namespace_dir.exists():
                shutil.rmtree(namespace_dir)
                namespace_dir.mkdir(parents=True, exist_ok=True)
                # Clean metadata
                self.metadata["entries"] = {
                    k: v for k, v in self.metadata["entries"].items()
                    if v.get("namespace") != namespace
                }
                self._save_metadata()

        except Exception as e:
            self.logger.error(f"Error in invalidate_namespace: {e}", exc_info=True)
            raise
    def clear_expired(self):
        """Clear all expired cache entries"""
        cleared = 0
        for namespace_dir in self.host_cache_dir.iterdir():
            if namespace_dir.is_dir():
                for cache_file in namespace_dir.glob("*.cache"):
                    cache_key = cache_file.stem
                    cache_meta_file = cache_file.with_suffix('.meta')

                    if cache_meta_file.exists():
                        try:
                            with open(cache_meta_file, 'r') as f:
                                meta = json.load(f)

                            cached_time = datetime.fromisoformat(meta.get("cached_at", ""))
                            expiry = meta.get("expiry_hours", self.default_expiry_hours)

                            if datetime.now() - cached_time > timedelta(hours=expiry):
                                cache_file.unlink()
                                cache_meta_file.unlink()
                                self._remove_metadata_entry(cache_key)
                                cleared += 1
                        except:
                            # Corrupted - delete it
                            cache_file.unlink(missing_ok=True)
                            cache_meta_file.unlink(missing_ok=True)

        if cleared > 0:
            self._save_metadata()

        return cleared

    def _update_metadata_entry(self, cache_key: str, namespace: str, size: int):
        """Update metadata entry"""
        if "entries" not in self.metadata:
            self.metadata["entries"] = {}

        self.metadata["entries"][cache_key] = {
            "namespace": namespace,
            "size": size,
            "cached_at": datetime.now().isoformat(),
            "host_id": self.host_id,
            "ide_name": self.ide_name
        }
        self._save_metadata()

    def _remove_metadata_entry(self, cache_key: str):
        """Remove metadata entry"""
        if "entries" in self.metadata:
            self.metadata["entries"].pop(cache_key, None)
            self._save_metadata()

    def _enforce_cache_size_limit(self):
        """Enforce cache size limit by cleaning oldest entries"""
        total_size_mb = sum(
            entry.get("size", 0)
            for entry in self.metadata.get("entries", {}).values()
        ) / (1024 * 1024)

        if total_size_mb > self.max_cache_size_mb:
            # Sort by cache time (oldest first)
            entries = sorted(
                self.metadata.get("entries", {}).items(),
                key=lambda x: x[1].get("cached_at", "")
            )

            # Delete oldest entries until under limit
            for cache_key, entry in entries:
                if total_size_mb <= self.max_cache_size_mb * 0.9:  # Leave 10% buffer
                    break

                namespace = entry.get("namespace", "default")
                namespace_dir = self.host_cache_dir / namespace
                cache_file = namespace_dir / f"{cache_key}.cache"
                cache_meta_file = namespace_dir / f"{cache_key}.meta"

                cache_file.unlink(missing_ok=True)
                cache_meta_file.unlink(missing_ok=True)
                total_size_mb -= entry.get("size", 0) / (1024 * 1024)
                self._remove_metadata_entry(cache_key)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self.clear_expired()  # Clean expired first

        total_entries = len(self.metadata.get("entries", {}))
        total_size_mb = sum(
            entry.get("size", 0)
            for entry in self.metadata.get("entries", {}).values()
        ) / (1024 * 1024)

        namespaces = {}
        for entry in self.metadata.get("entries", {}).values():
            namespace = entry.get("namespace", "default")
            if namespace not in namespaces:
                namespaces[namespace] = {"count": 0, "size_mb": 0}
            namespaces[namespace]["count"] += 1
            namespaces[namespace]["size_mb"] += entry.get("size", 0) / (1024 * 1024)

        return {
            "host_id": self.host_id,
            "ide_name": self.ide_name,
            "total_entries": total_entries,
            "total_size_mb": round(total_size_mb, 2),
            "max_size_mb": self.max_cache_size_mb,
            "namespaces": namespaces,
            "cache_dir": str(self.host_cache_dir)
        }


def cached(
    cache: HostAwareCache,
    namespace: str = "default",
    expiry_hours: Optional[int] = None,
    key_parts_func: Optional[Callable] = None
):
    """
    Decorator for caching function results

    Usage:
        @cached(cache_instance, namespace="r5", expiry_hours=12)
        def expensive_operation(param1, param2):
            ...
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_parts_func:
                key_parts = key_parts_func(*args, **kwargs)
            else:
                key_parts = [func.__name__, str(args), str(sorted(kwargs.items()))]

            # Check cache
            cached_value = cache.get(key_parts, namespace, expiry_hours)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(key_parts, result, namespace, expiry_hours)

            return result

        return wrapper
    return decorator

