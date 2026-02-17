#!/usr/bin/env python3
"""
AI Token Request Retry Manager - Cursor IDE Integration

Specifically handles retries for AI token requests in Cursor IDE when:
- Timeout errors occur
- Connection errors occur
- Agent/Cursor IDE needs to retry AI connection

The retry manager ensures it connects to the AI service it was configured to connect to.

Tags: #AI_TOKEN #RETRY_MANAGER #CURSOR_IDE #AI_CONNECTION @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from functools import wraps
from enum import Enum

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

from cursor_chat_retry_manager import CursorChatRetryManager, RetryStrategy
from cursor_connection_resilience import CursorConnectionResilience

logger = get_logger("AITokenRequestRetryManager")


class AITokenRequestRetryManager:
    """
    AI Token Request Retry Manager

    Specifically for AI token requests in Cursor IDE.
    Handles timeout and connection errors, ensuring it retries
    with the configured AI service.
    """

    def __init__(
        self,
        max_retries: int = 5,  # More retries for AI requests
        initial_delay: float = 2.0,  # Longer initial delay
        max_delay: float = 30.0,  # Longer max delay for AI
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    ):
        """
        Initialize AI token request retry manager

        Args:
            max_retries: Maximum retry attempts (default: 5 for AI)
            initial_delay: Initial delay in seconds (default: 2.0)
            max_delay: Maximum delay in seconds (default: 30.0)
            strategy: Retry strategy
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.strategy = strategy

        # Use base retry manager
        self.base_retry_manager = CursorChatRetryManager(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            strategy=strategy
        )

        # Track configured AI service
        self.configured_ai_service: Optional[str] = None
        self.ai_service_url: Optional[str] = None

        # Connection resilience handler for ECONNRESET and connection errors
        self.connection_resilience = CursorConnectionResilience(
            max_retries=max_retries,
            retry_delay=initial_delay
        )

        logger.info("✅ AI Token Request Retry Manager initialized")
        logger.info(f"   Max retries: {max_retries}")
        logger.info(f"   Strategy: {strategy.value}")
        logger.info("   🔒 Connection resilience: Active (ECONNRESET handling)")

    def set_configured_ai_service(self, service_name: str, service_url: Optional[str] = None):
        """
        Set the configured AI service to connect to

        Args:
            service_name: AI service name (ULTRON, KAIJU, Bedrock, etc.)
            service_url: AI service URL (optional)
        """
        self.configured_ai_service = service_name
        self.ai_service_url = service_url
        logger.info(f"✅ Configured AI service: {service_name}")
        if service_url:
            logger.info(f"   URL: {service_url}")

    def retry_ai_token_request(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Retry AI token request with configured AI service

        Args:
            func: Function that makes AI token request
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        # Ensure we're using the configured AI service
        if self.configured_ai_service:
            # Add AI service info to kwargs if not present
            if 'ai_service' not in kwargs:
                kwargs['ai_service'] = self.configured_ai_service
            if self.ai_service_url and 'ai_service_url' not in kwargs:
                kwargs['ai_service_url'] = self.ai_service_url

        logger.info(f"🔄 Retrying AI token request (configured service: {self.configured_ai_service or 'auto-detect'})")

        # Wrap function with connection resilience
        @self.connection_resilience.retry_on_connection_error
        def resilient_func(*args, **kwargs):
            return self.base_retry_manager.retry(func, *args, **kwargs)

        return resilient_func(*args, **kwargs)

    def retry_ai_token_request_with_fallback(
        self,
        func: Callable,
        fallback_func: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Retry AI token request with fallback to alternative AI service

        Args:
            func: Primary function that makes AI token request
            fallback_func: Fallback function if primary fails
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        try:
            # Try primary function with retry
            return self.retry_ai_token_request(func, *args, **kwargs)
        except Exception as e:
            logger.warning(f"⚠️  Primary AI service failed: {e}")

            if fallback_func:
                logger.info("🔄 Attempting fallback AI service...")
                try:
                    # Try fallback with retry
                    return self.retry_ai_token_request(fallback_func, *args, **kwargs)
                except Exception as e2:
                    logger.error(f"❌ Fallback AI service also failed: {e2}")
                    raise

            raise


# Global AI token retry manager instance
_default_ai_token_retry_manager = AITokenRequestRetryManager(
    max_retries=5,
    initial_delay=2.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL
)


def retry_ai_token_request(
    func: Callable,
    max_retries: int = 5,
    initial_delay: float = 2.0,
    max_delay: float = 30.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    ai_service: Optional[str] = None,
    ai_service_url: Optional[str] = None
) -> Any:
    """
    Convenience function for retrying AI token requests

    Usage:
        result = retry_ai_token_request(
            make_ai_request,
            query="Hello",
            ai_service="ULTRON"
        )
    """
    manager = AITokenRequestRetryManager(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        strategy=strategy
    )

    if ai_service:
        manager.set_configured_ai_service(ai_service, ai_service_url)

    return manager.retry_ai_token_request(func)


def ai_token_retry_decorator(
    max_retries: int = 5,
    ai_service: Optional[str] = None,
    **kwargs
):
    """
    Decorator for automatic AI token request retry

    Usage:
        @ai_token_retry_decorator(max_retries=5, ai_service="ULTRON")
        def make_ai_request(query):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **func_kwargs):
            manager = AITokenRequestRetryManager(
                max_retries=max_retries,
                **kwargs
            )

            if ai_service:
                manager.set_configured_ai_service(ai_service)

            return manager.retry_ai_token_request(func, *args, **func_kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # Test AI token request retry
    def test_ai_request(query: str, ai_service: str = "ULTRON"):
        """Test AI request function"""
        print(f"Making AI request to {ai_service}: {query}")
        # Simulate connection error
        import random
        if random.random() < 0.7:  # 70% chance of error
            raise ConnectionError(f"Connection error to {ai_service}")
        return {"response": f"Response from {ai_service}: {query}"}

    manager = AITokenRequestRetryManager(max_retries=3)
    manager.set_configured_ai_service("ULTRON", "http://localhost:11434")

    try:
        result = manager.retry_ai_token_request(test_ai_request, "Test query", ai_service="ULTRON")
        print(f"✅ Test result: {result}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
