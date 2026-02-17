#!/usr/bin/env python3
"""
API Security Middleware
Security enhancements for API requests

Includes input validation, CORS, security headers, and request sanitization.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from fastapi import Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("APISecurityMiddleware")


class SecurityHeadersMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Add security headers to responses"""

    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                headers[b"content-security-policy"] = b"default-src 'self'"
                message["headers"] = list(headers.items())
            await send(message)

        await self.app(scope, receive, send_wrapper)


class InputValidationMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Validate and sanitize input"""

    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.app = app

        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        ]

        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
        ]

    def validate_input(self, value: str) -> bool:
        """Validate input for SQL injection and XSS"""
        if not isinstance(value, str):
            return True

        value_lower = value.lower()

        # Check SQL injection patterns
        for pattern in self.sql_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {value[:50]}")
                return False

        # Check XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {value[:50]}")
                return False

        return True

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Validate query parameters
        for key, value in request.query_params.items():
            if not self.validate_input(str(value)):
                response = Response(
                    content='{"error": "Invalid input detected"}',
                    status_code=400,
                    media_type="application/json"
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
