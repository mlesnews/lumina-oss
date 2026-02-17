#!/usr/bin/env python3
"""
HTTP Retry Utility with ECONNRESET Handling

Provides robust retry logic for HTTP requests with proper handling of:
- ECONNRESET (Connection reset by peer)
- Connection errors
- Timeouts
- Transient network issues

Tags: #HTTP #RETRY #ECONNRESET #CONNECTION_ERROR #NETWORK
"""

import time
import logging
import socket
from functools import wraps
from typing import Callable, Optional, Tuple, Any
import requests
from requests.exceptions import (
    RequestException,
    ConnectionError as RequestsConnectionError,
    Timeout,
    ConnectTimeout,
    ReadTimeout
)

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("HTTPRetryUtility")


class ECONNRESETError(Exception):
    """Connection reset error"""


def is_connection_reset_error(error: Exception) -> bool:
    """
    Check if error is a connection reset error

    Args:
        error: Exception to check

    Returns:
        True if connection reset error
    """
    # Check for ECONNRESET in error message
    error_str = str(error).lower()
    if 'econnreset' in error_str or 'connection reset' in error_str:
        return True

    # Check for socket errors
    if isinstance(error, (socket.error, OSError)):
        if hasattr(error, 'errno'):
            # Windows: 10054, Linux: 104
            if error.errno in (10054, 104, 54):
                return True
        if 'reset' in str(error).lower():
            return True

    # Check for requests ConnectionError with reset
    if isinstance(error, RequestsConnectionError):
        if hasattr(error, 'args') and error.args:
            for arg in error.args:
                if isinstance(arg, (socket.error, OSError)):
                    if hasattr(arg, 'errno') and arg.errno in (10054, 104, 54):
                        return True
                if 'reset' in str(arg).lower():
                    return True

    return False


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retry_on: Optional[Tuple[Exception, ...]] = None,
    jitter: bool = True
):
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        retry_on: Tuple of exceptions to retry on (default: all connection/timeout errors)
        jitter: Add random jitter to delays

    Returns:
        Decorated function
    """
    if retry_on is None:
        retry_on = (
            RequestException,
            RequestsConnectionError,
            Timeout,
            ConnectTimeout,
            ReadTimeout,
            socket.error,
            OSError,
            ECONNRESETError
        )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import random

            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    # Check if it's a connection reset
                    is_reset = is_connection_reset_error(e)

                    if attempt < max_retries:
                        # Calculate delay with exponential backoff
                        current_delay = min(
                            initial_delay * (exponential_base ** attempt),
                            max_delay
                        )

                        # Add jitter if enabled
                        if jitter:
                            jitter_amount = current_delay * 0.1 * random.random()
                            current_delay += jitter_amount

                        error_type = "ECONNRESET" if is_reset else type(e).__name__
                        logger.warning(
                            "   ⚠️  %s (attempt %d/%d): %s - retrying in %.2fs",
                            error_type,
                            attempt + 1,
                            max_retries + 1,
                            str(e)[:100],
                            current_delay
                        )

                        time.sleep(current_delay)
                    else:
                        # Last attempt failed
                        error_type = "ECONNRESET" if is_reset else type(e).__name__
                        logger.error(
                            "   ❌ %s failed after %d attempts: %s",
                            error_type,
                            max_retries + 1,
                            str(e)
                        )
                        raise
                except Exception as e:
                    # Non-retryable exception
                    logger.error("   ❌ Non-retryable error: %s", e)
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def safe_request(
    method: str,
    url: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    **kwargs
) -> requests.Response:
    """
    Make HTTP request with automatic retry on connection errors

    Args:
        method: HTTP method (get, post, put, delete, etc.)
        url: URL to request
        max_retries: Maximum retry attempts
        initial_delay: Initial retry delay
        max_delay: Maximum retry delay
        **kwargs: Additional arguments to pass to requests

    Returns:
        Response object

    Raises:
        RequestException: If all retries fail
    """
    @retry_with_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay
    )
    def _make_request():
        method_func = getattr(requests, method.lower(), None)
        if not method_func:
            raise ValueError(f"Invalid HTTP method: {method}")

        return method_func(url, **kwargs)

    return _make_request()


def safe_get(
    url: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    **kwargs
) -> requests.Response:
    """
    Safe GET request with retry logic

    Args:
        url: URL to request
        max_retries: Maximum retry attempts
        initial_delay: Initial retry delay
        max_delay: Maximum retry delay
        **kwargs: Additional arguments to pass to requests.get

    Returns:
        Response object
    """
    return safe_request(
        "get",
        url,
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        **kwargs
    )


def safe_post(
    url: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    **kwargs
) -> requests.Response:
    """
    Safe POST request with retry logic

    Args:
        url: URL to request
        max_retries: Maximum retry attempts
        initial_delay: Initial retry delay
        max_delay: Maximum retry delay
        **kwargs: Additional arguments to pass to requests.post

    Returns:
        Response object
    """
    return safe_request(
        "post",
        url,
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        **kwargs
    )


def safe_put(
    url: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    **kwargs
) -> requests.Response:
    """
    Safe PUT request with retry logic

    Args:
        url: URL to request
        max_retries: Maximum retry attempts
        initial_delay: Initial retry delay
        max_delay: Maximum retry delay
        **kwargs: Additional arguments to pass to requests.put

    Returns:
        Response object
    """
    return safe_request(
        "put",
        url,
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        **kwargs
    )


def safe_delete(
    url: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    **kwargs
) -> requests.Response:
    """
    Safe DELETE request with retry logic

    Args:
        url: URL to request
        max_retries: Maximum retry attempts
        initial_delay: Initial retry delay
        max_delay: Maximum retry delay
        **kwargs: Additional arguments to pass to requests.delete

    Returns:
        Response object
    """
    return safe_request(
        "delete",
        url,
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        **kwargs
    )
