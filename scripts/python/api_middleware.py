#!/usr/bin/env python3
"""
API Middleware
Custom middleware for JARVIS Master Agent API

Includes rate limiting, request logging, and error handling.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from fastapi import Request, Response, status
    from fastapi.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware as StarletteMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("APIMiddleware")

try:
    from defense_architecture_transaction_logging import get_transaction_logger, TransactionType
    TRANSACTION_LOGGING_AVAILABLE = True
except ImportError:
    TRANSACTION_LOGGING_AVAILABLE = False


class RateLimitMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Rate limiting middleware"""

    def __init__(self, app, requests_per_minute: int = 60):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, list] = defaultdict(list)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        client_ip = request.client.host if request.client else "unknown"

        # Clean old requests (older than 1 minute)
        current_time = time.time()
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            response = Response(
                content=json.dumps({"error": "Rate limit exceeded", "retry_after": 60}),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
            await response(scope, receive, send)
            return

        # Record request
        self.request_counts[client_ip].append(current_time)

        await self.app(scope, receive, send)


class RequestLoggingMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Request logging middleware"""

    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        # Log request
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(f"Request: {method} {path} from {client_ip}")

        # Process request
        await self.app(scope, receive, send)

        # Calculate duration
        duration = time.time() - start_time

        # Log transaction if available
        if TRANSACTION_LOGGING_AVAILABLE:
            try:
                tx_logger = get_transaction_logger(project_root)
                tx_logger.log_transaction(
                    system_name="api-server",
                    transaction_type=TransactionType.READ if method == "GET" else TransactionType.WRITE,
                    resource=path,
                    action=method.lower(),
                    ip_address=client_ip,
                    result="success",
                    details={
                        "duration": duration,
                        "user_agent": user_agent
                    }
                )
            except Exception as e:
                logger.debug(f"Transaction logging failed: {e}")


class ErrorHandlingMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Error handling middleware"""

    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)

            # Create error response
            error_response = {
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "message": str(e) if logger.level <= 10 else "An error occurred",
                "timestamp": datetime.now().isoformat()
            }

            response = Response(
                content=json.dumps(error_response),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json"
            )

            await response(scope, receive, send)
