#!/usr/bin/env python3
"""
Secret Masker Utility
Masks secrets in strings, logs, and outputs

Tags: #SECURITY #SECRETS #MASKING @SECURITY
"""

import re
from typing import Optional, Union, List

# Secret patterns to detect
SECRET_PATTERNS = [
    # ElevenLabs/Stripe-style keys
    (r'sk_[a-zA-Z0-9]{20,}', lambda m: f"sk_{'*' * (len(m.group()) - 3)}"),
    # Generic API keys (long alphanumeric)
    (r'[a-f0-9]{40,}', lambda m: f"{m.group()[:3]}***{m.group()[-4:]}"),
    # JWT tokens
    (r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', lambda m: f"eyJ***REDACTED***"),
    # Long hex strings (keys)
    (r'[a-f0-9]{32,}', lambda m: f"{m.group()[:3]}***{m.group()[-4:]}"),
]


def mask_secret(text: str, replacement: str = "***REDACTED***") -> str:
    """
    Mask secrets in text

    Args:
        text: Text that may contain secrets
        replacement: Replacement string (default: ***REDACTED***)

    Returns:
        Text with secrets masked
    """
    if not text:
        return text

    masked = text

    # Apply all secret patterns
    for pattern, mask_func in SECRET_PATTERNS:
        masked = re.sub(pattern, mask_func, masked, flags=re.IGNORECASE)

    return masked


def mask_api_key(key: str, show_first: int = 3, show_last: int = 4) -> str:
    """
    Mask an API key showing only first and last characters

    Args:
        key: API key to mask
        show_first: Number of leading chars to show (default: 3)
        show_last: Number of trailing chars to show (default: 4)

    Returns:
        Masked key (e.g., "sk_***...***a603")
    """
    if not key or len(key) <= (show_first + show_last):
        return "***REDACTED***"

    return f"{key[:show_first]}***...***{key[-show_last:]}"


def sanitize_log_message(message: str) -> str:
    """
    Sanitize log message to remove secrets

    Args:
        message: Log message that may contain secrets

    Returns:
        Sanitized log message
    """
    return mask_secret(message)


def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitize dictionary, masking any secret values

    Args:
        data: Dictionary that may contain secrets

    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    secret_keys = ['key', 'password', 'token', 'secret', 'api_key', 'apikey', 
                   'access_token', 'refresh_token', 'credential', 'auth']

    for key, value in data.items():
        key_lower = key.lower()
        if any(secret_term in key_lower for secret_term in secret_keys):
            sanitized[key] = mask_api_key(str(value))
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, str):
            sanitized[key] = sanitize_log_message(value)
        else:
            sanitized[key] = value

    return sanitized


# Usage examples
if __name__ == "__main__":
    # Test masking
    test_key = "sk_191353bd872b59ef42db77c7c593e181c2d91dad7003a603"
    print(f"Original: {test_key}")
    print(f"Masked:   {mask_api_key(test_key)}")
    print(f"Pattern:  {mask_secret(test_key)}")
