#!/usr/bin/env python3
"""
API Rate Limiter
Advanced rate limiting with Redis support

Provides per-user and per-IP rate limiting.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("APIRateLimiter")

# Redis for distributed rate limiting
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.debug("Redis not available - using in-memory rate limiting")


class RateLimiter:
    """Advanced rate limiter with Redis support"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent

        # In-memory fallback
        self.request_counts: Dict[str, list] = defaultdict(list)

        # Redis client if available
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                import os
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", "6379"))
                self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis rate limiter initialized")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory rate limiting: {e}")
                self.redis_client = None

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit

        Args:
            identifier: User ID or IP address
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, retry_after_seconds)
        """
        current_time = time.time()

        if self.redis_client:
            # Use Redis for distributed rate limiting
            try:
                key = f"rate_limit:{identifier}"
                count = self.redis_client.incr(key)

                if count == 1:
                    # Set expiration on first request
                    self.redis_client.expire(key, window_seconds)

                if count > max_requests:
                    ttl = self.redis_client.ttl(key)
                    return False, ttl if ttl > 0 else window_seconds

                return True, None
            except Exception as e:
                logger.warning(f"Redis rate limit check failed: {e}")
                # Fallback to in-memory

        # In-memory rate limiting
        # Clean old requests
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if current_time - req_time < window_seconds
        ]

        # Check limit
        if len(self.request_counts[identifier]) >= max_requests:
            # Calculate retry after
            oldest_request = min(self.request_counts[identifier])
            retry_after = int(window_seconds - (current_time - oldest_request)) + 1
            return False, retry_after

        # Record request
        self.request_counts[identifier].append(current_time)
        return True, None

    def get_rate_limit_info(self, identifier: str) -> Dict[str, Any]:
        """Get current rate limit status for identifier"""
        if self.redis_client:
            try:
                key = f"rate_limit:{identifier}"
                count = self.redis_client.get(key)
                ttl = self.redis_client.ttl(key)
                return {
                    "requests": int(count) if count else 0,
                    "window_remaining": ttl if ttl > 0 else 0
                }
            except Exception:
                pass

        # In-memory
        current_time = time.time()
        recent_requests = [
            req_time for req_time in self.request_counts[identifier]
            if current_time - req_time < 60
        ]
        return {
            "requests": len(recent_requests),
            "window_remaining": 60
        }


def get_rate_limiter(project_root: Optional[Path] = None) -> RateLimiter:
    """Get global rate limiter"""
    return RateLimiter(project_root)
