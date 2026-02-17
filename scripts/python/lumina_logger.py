#!/usr/bin/env python3
"""
Simple logger utility for the Lumina project.

Provides a `get_logger(name)` function that returns a configured
`logging.Logger` instance.  The logger is configured to output to
stdout with a consistent format and INFO level by default.
"""

import logging

# Configure root logger once
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name.

    The logger is created lazily and cached by the standard
    `logging.getLogger` mechanism.
    """
    return logging.getLogger(name)


# End of lumina_logger.py
