"""
Multi-tier memory manager.

Manages knowledge with explicit priority tiers and TTL-based expiration.
Higher-tier memories persist longer; lower tiers are evicted first under pressure.

Pattern extracted from production: aios/kernel/memory_manager.py

Example:
    mgr = MemoryManager()
    mgr.store("api_key_pattern", "Always use vault", MemoryTier.CRITICAL)
    mgr.store("temp_note", "Check later", MemoryTier.TEMPORARY, ttl=3600)
    print(mgr.recall("api_key_pattern"))
"""

import logging
import time
import threading
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryTier(IntEnum):
    """Memory priority tiers (higher = more persistent)."""
    CRITICAL = 5    # Never auto-evicted
    HIGH = 4        # Evicted only under extreme pressure
    MEDIUM = 3      # Standard working memory
    LOW = 2         # Evicted when space is needed
    TEMPORARY = 1   # Short-lived, first to evict


@dataclass
class MemoryBlock:
    """A single unit of stored knowledge."""
    key: str
    value: Any
    tier: MemoryTier
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    ttl: Optional[float] = None  # Seconds until expiration (None = no expiry)
    access_count: int = 0

    @property
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl


class MemoryManager:
    """
    Multi-tier memory manager with TTL and eviction.

    Args:
        max_blocks: Maximum number of memory blocks before eviction starts.
    """

    def __init__(self, max_blocks: int = 1000):
        self._store: Dict[str, MemoryBlock] = {}
        self._max_blocks = max_blocks
        self._lock = threading.Lock()

    def store(
        self,
        key: str,
        value: Any,
        tier: MemoryTier = MemoryTier.MEDIUM,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Store a memory block.

        Args:
            key: Unique identifier for this memory.
            value: The data to store.
            tier: Priority tier (CRITICAL through TEMPORARY).
            ttl: Time-to-live in seconds. None means no expiration.
        """
        with self._lock:
            self._store[key] = MemoryBlock(
                key=key, value=value, tier=tier, ttl=ttl,
            )
            self._evict_if_needed()

    def recall(self, key: str) -> Optional[Any]:
        """
        Retrieve a memory by key. Returns None if not found or expired.

        Args:
            key: The memory key to look up.
        """
        with self._lock:
            block = self._store.get(key)
            if block is None:
                return None
            if block.is_expired:
                del self._store[key]
                return None
            block.accessed_at = time.time()
            block.access_count += 1
            return block.value

    def forget(self, key: str) -> bool:
        """Remove a memory block. Returns True if it existed."""
        with self._lock:
            return self._store.pop(key, None) is not None

    def search(self, substring: str) -> List[MemoryBlock]:
        """Find all non-expired blocks whose key contains the substring."""
        with self._lock:
            self._purge_expired()
            return [
                b for b in self._store.values()
                if substring.lower() in b.key.lower()
            ]

    def status(self) -> Dict[str, Any]:
        """Return memory usage statistics."""
        with self._lock:
            self._purge_expired()
            tier_counts = {}
            for block in self._store.values():
                name = block.tier.name
                tier_counts[name] = tier_counts.get(name, 0) + 1
            return {
                "total_blocks": len(self._store),
                "max_blocks": self._max_blocks,
                "utilization": len(self._store) / self._max_blocks,
                "by_tier": tier_counts,
            }

    def _purge_expired(self) -> int:
        """Remove all expired blocks. Returns count removed."""
        expired = [k for k, v in self._store.items() if v.is_expired]
        for k in expired:
            del self._store[k]
        return len(expired)

    def _evict_if_needed(self) -> int:
        """Evict lowest-priority blocks if over capacity. Returns count evicted."""
        self._purge_expired()
        evicted = 0
        while len(self._store) > self._max_blocks:
            # Sort by tier (ascending), then by last access (oldest first)
            victim_key = min(
                self._store,
                key=lambda k: (
                    self._store[k].tier,
                    self._store[k].accessed_at,
                ),
            )
            victim = self._store[victim_key]
            if victim.tier == MemoryTier.CRITICAL:
                break  # Never evict CRITICAL
            del self._store[victim_key]
            evicted += 1
        return evicted
