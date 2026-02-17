"""Intelligent Caching Layer for Lumina

Reduces API calls, file reads, and expensive operations through smart caching.
"""

import json
import hashlib
import time
from typing import Any, Dict, Optional
from pathlib import Path

class LuminaCache:
    """Intelligent caching with TTL and invalidation"""

    def __init__(self, cache_dir: str = "cache", max_memory_mb: int = 512):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_memory_mb = max_memory_mb
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_size = 0

    def get(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        """Get cached value if not expired"""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry['timestamp'] < ttl_seconds:
                return entry['value']
            else:
                # Expired, remove
                self.memory_size -= len(json.dumps(entry['value']))
                del self.memory_cache[key]

        # Check file cache
        cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)

                if time.time() - entry['timestamp'] < ttl_seconds:
                    # Load into memory cache
                    self._add_to_memory(key, entry['value'], entry['timestamp'])
                    return entry['value']
                else:
                    # Expired, remove file
                    cache_file.unlink()

            except Exception:
                # Corrupted cache file, remove it
                cache_file.unlink()

        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Cache a value"""
        timestamp = time.time()

        # Add to memory cache
        self._add_to_memory(key, value, timestamp)

        # Save to file cache
        cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
        entry = {
            'key': key,
            'value': value,
            'timestamp': timestamp,
            'ttl': ttl_seconds
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(entry, f)
        except Exception:
            # If file write fails, still keep in memory
            pass

    def invalidate(self, key: str) -> None:
        try:
            """Remove cached value"""
            # Remove from memory
            if key in self.memory_cache:
                self.memory_size -= len(json.dumps(self.memory_cache[key]['value']))
                del self.memory_cache[key]

            # Remove from file
            cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
            if cache_file.exists():
                cache_file.unlink()

        except Exception as e:
            self.logger.error(f"Error in invalidate: {e}", exc_info=True)
            raise
    def clear_expired(self) -> int:
        """Clear all expired cache entries, return count cleared"""
        cleared = 0

        # Check memory cache
        expired_keys = []
        for key, entry in self.memory_cache.items():
            if time.time() - entry['timestamp'] > 3600:  # Default 1 hour
                expired_keys.append(key)

        for key in expired_keys:
            self.memory_size -= len(json.dumps(self.memory_cache[key]['value']))
            del self.memory_cache[key]
            cleared += 1

        # Check file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)

                if time.time() - entry['timestamp'] > entry.get('ttl', 3600):
                    cache_file.unlink()
                    cleared += 1

            except Exception:
                # Remove corrupted files
                cache_file.unlink()
                cleared += 1

        return cleared

    def _add_to_memory(self, key: str, value: Any, timestamp: float) -> None:
        try:
            """Add entry to memory cache with size management"""
            value_size = len(json.dumps(value))

            # Remove old entries if needed
            while self.memory_size + value_size > self.max_memory_mb * 1024 * 1024 and self.memory_cache:
                # Remove oldest entry
                oldest_key = min(self.memory_cache.keys(),
                               key=lambda k: self.memory_cache[k]['timestamp'])
                self.memory_size -= len(json.dumps(self.memory_cache[oldest_key]['value']))
                del self.memory_cache[oldest_key]

            # Add new entry
            self.memory_cache[key] = {
                'value': value,
                'timestamp': timestamp
            }
            self.memory_size += value_size

        except Exception as e:
            self.logger.error(f"Error in _add_to_memory: {e}", exc_info=True)
            raise
# Global cache instance
lumina_cache = LuminaCache()

# Convenience functions
def cached(ttl_seconds: int = 3600):
    """Decorator for function result caching"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function call
            key = f"{func.__name__}:{hashlib.md5(str(args) + str(kwargs).encode()).hexdigest()}"

            # Try cache first
            cached_result = lumina_cache.get(key, ttl_seconds)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            lumina_cache.set(key, result, ttl_seconds)

            return result
        return wrapper
    return decorator
