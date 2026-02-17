"""Async Processing Framework for Lumina

Enables concurrent operations and better resource utilization.
"""

import asyncio
import logging
from typing import List, Any, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor
import functools

logger = logging.getLogger("lumina.async")

class LuminaAsyncProcessor:
    """Async processing utilities for Lumina"""

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or (os.cpu_count() or 4) * 2
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    async def run_in_executor(self, func: Callable, *args, **kwargs) -> Any:
        """Run blocking function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            functools.partial(func, *args, **kwargs)
        )

    async def gather_with_concurrency(self, tasks: List[Awaitable], concurrency: int = 10) -> List[Any]:
        """Run tasks with controlled concurrency"""
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_task(task):
            async with semaphore:
                return await task

        limited_tasks = [limited_task(task) for task in tasks]
        return await asyncio.gather(*limited_tasks, return_exceptions=True)

    async def process_batch(self, items: List[Any], processor: Callable,
                          batch_size: int = 10) -> List[Any]:
        """Process items in batches with concurrency"""
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size}")

            # Create async tasks for batch
            tasks = [
                self.run_in_executor(processor, item)
                for item in batch
            ]

            # Process batch concurrently
            batch_results = await self.gather_with_concurrency(tasks)
            results.extend(batch_results)

        return results

# Global async processor
async_processor = LuminaAsyncProcessor()

# Helper functions for easy async usage
async def run_async(func: Callable, *args, **kwargs) -> Any:
    """Run any function asynchronously"""
    return await async_processor.run_in_executor(func, *args, **kwargs)

async def process_concurrent(tasks: List[Awaitable], concurrency: int = 10) -> List[Any]:
    """Process tasks concurrently with limit"""
    return await async_processor.gather_with_concurrency(tasks, concurrency)

async def batch_process_async(items: List[Any], processor: Callable,
                            batch_size: int = 10) -> List[Any]:
    """Process items in batches asynchronously"""
    return await async_processor.process_batch(items, processor, batch_size)
