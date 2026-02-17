#!/usr/bin/env python3
"""
Memory Management Module for AIOS Microkernel.

Handles allocation, deallocation, and tracking of memory blocks.
"""

import threading
from dataclasses import dataclass
from enum import Enum
from typing import List

from lumina_logger import get_logger

logger = get_logger("MemoryManager")


class MemoryType(Enum):
    CODE = "code"
    DATA = "data"
    STACK = "stack"
    HEAP = "heap"
    SHARED = "shared"


@dataclass
class MemoryBlock:
    address: int
    size: int
    memory_type: MemoryType
    process_id: int | None = None
    allocated: bool = False


class MemoryManager:
    """Manages memory blocks for the kernel."""

    def __init__(self, total_size: int = 4 * 1024 * 1024 * 1024):
        self.memory_blocks: List[MemoryBlock] = []
        self.memory_size = total_size
        self.memory_lock = threading.Lock()
        self._initialize_memory()

    def _initialize_memory(self) -> None:
        block = MemoryBlock(
            address=0,
            size=self.memory_size,
            memory_type=MemoryType.HEAP,
            allocated=False,
        )
        self.memory_blocks.append(block)
        logger.info(f"✅ Memory initialized: {self.memory_size / (1024**3):.2f} GB")

    def allocate(self, size: int) -> int:
        with self.memory_lock:
            for block in self.memory_blocks:
                if not block.allocated and block.size >= size:
                    if block.size > size:
                        new_block = MemoryBlock(
                            address=block.address + size,
                            size=block.size - size,
                            memory_type=block.memory_type,
                            allocated=False,
                        )
                        self.memory_blocks.append(new_block)
                    block.allocated = True
                    block.size = size
                    return block.address
            raise MemoryError(f"Insufficient memory: {size} bytes")

    def free(self, address: int, size: int) -> None:
        with self.memory_lock:
            for block in self.memory_blocks:
                if block.address == address and block.allocated:
                    block.allocated = False
                    self._merge_free_blocks()
                    return

    def _merge_free_blocks(self) -> None:
        self.memory_blocks.sort(key=lambda b: b.address)
        i = 0
        while i < len(self.memory_blocks) - 1:
            cur = self.memory_blocks[i]
            nxt = self.memory_blocks[i + 1]
            if not cur.allocated and not nxt.allocated and cur.address + cur.size == nxt.address:
                cur.size += nxt.size
                self.memory_blocks.remove(nxt)
            else:
                i += 1

    def status(self) -> dict:
        with self.memory_lock:
            allocated = sum(b.size for b in self.memory_blocks if b.allocated)
            free = sum(b.size for b in self.memory_blocks if not b.allocated)
            return {
                "total": self.memory_size,
                "allocated": allocated,
                "free": free,
            }


# End of memory_manager.py
