"""Tests for the multi-tier memory manager."""

import time

from lumina.aios.memory import MemoryManager, MemoryTier


def test_store_and_recall():
    mgr = MemoryManager()
    mgr.store("key1", "value1")
    assert mgr.recall("key1") == "value1"


def test_recall_missing_returns_none():
    mgr = MemoryManager()
    assert mgr.recall("nonexistent") is None


def test_forget():
    mgr = MemoryManager()
    mgr.store("key1", "value1")
    assert mgr.forget("key1") is True
    assert mgr.recall("key1") is None
    assert mgr.forget("key1") is False


def test_ttl_expiration():
    mgr = MemoryManager()
    mgr.store("temp", "data", tier=MemoryTier.TEMPORARY, ttl=0.01)
    time.sleep(0.02)
    assert mgr.recall("temp") is None


def test_eviction_order():
    mgr = MemoryManager(max_blocks=3)
    mgr.store("critical", "important", tier=MemoryTier.CRITICAL)
    mgr.store("low1", "data1", tier=MemoryTier.LOW)
    mgr.store("low2", "data2", tier=MemoryTier.LOW)
    mgr.store("medium", "data3", tier=MemoryTier.MEDIUM)  # triggers eviction

    # Critical should survive, one low should be evicted
    assert mgr.recall("critical") == "important"
    assert mgr.status()["total_blocks"] <= 3


def test_critical_never_evicted():
    mgr = MemoryManager(max_blocks=2)
    mgr.store("c1", "v1", tier=MemoryTier.CRITICAL)
    mgr.store("c2", "v2", tier=MemoryTier.CRITICAL)
    mgr.store("c3", "v3", tier=MemoryTier.CRITICAL)  # Over capacity

    # All 3 critical should still exist (can't evict CRITICAL)
    assert mgr.recall("c1") == "v1"
    assert mgr.recall("c2") == "v2"
    assert mgr.recall("c3") == "v3"


def test_search():
    mgr = MemoryManager()
    mgr.store("api_key_pattern", "use vault")
    mgr.store("api_timeout", "30 seconds")
    mgr.store("db_config", "postgres")

    results = mgr.search("api")
    assert len(results) == 2


def test_status():
    mgr = MemoryManager(max_blocks=100)
    mgr.store("a", 1, tier=MemoryTier.HIGH)
    mgr.store("b", 2, tier=MemoryTier.LOW)
    mgr.store("c", 3, tier=MemoryTier.HIGH)

    status = mgr.status()
    assert status["total_blocks"] == 3
    assert status["by_tier"]["HIGH"] == 2
    assert status["by_tier"]["LOW"] == 1


def test_access_count_increments():
    mgr = MemoryManager()
    mgr.store("key", "val")
    mgr.recall("key")
    mgr.recall("key")
    mgr.recall("key")
    block = mgr._store["key"]
    assert block.access_count == 3
