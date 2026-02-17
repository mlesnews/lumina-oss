#!/usr/bin/env python3
"""
SYPHON AI Responses - Auto-SYPHON AI thinking from responses

This module provides a decorator/context manager to automatically
SYPHON AI thinking whenever text is output.

Usage:
    from syphon_ai_responses import syphon_thinking

    @syphon_thinking
    def my_ai_function():
        thinking = "I'm planning to fix Kenny's movement..."
        return thinking

Tags: #SYPHON #AI_THINKING #AUTO_EXTRACT @LUMINA
"""

import sys
from pathlib import Path
from functools import wraps
from typing import Callable, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ai_thinking_syphon import siphon_thinking, get_syphon


def syphon_thinking_decorator(func: Callable) -> Callable:
    """
    Decorator to automatically SYPHON AI thinking from function output.

    Usage:
        @syphon_thinking_decorator
        def plan_next_steps():
            return "I'm planning to fix Kenny's movement..."
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # If result is a string, SYPHON it
        if isinstance(result, str) and result.strip():
            try:
                siphon_thinking(
                    result,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200]
                    },
                    trigger_workflow=True
                )
            except Exception as e:
                # Don't break the function if SYPHON fails
                pass

        return result
    return wrapper


class SyphonContext:
    """
    Context manager to SYPHON thinking within a block.

    Usage:
        with SyphonContext("Planning Kenny improvements"):
            thinking = "I'm considering..."
            # Thinking is automatically SYPHONed
    """

    def __init__(self, context_name: str, **context_kwargs):
        self.context_name = context_name
        self.context = context_kwargs
        self.thinking_parts = []

    def __enter__(self):
        return self

    def add_thinking(self, thinking: str):
        """Add thinking to be SYPHONed"""
        self.thinking_parts.append(thinking)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # SYPHON all collected thinking
        if self.thinking_parts:
            full_thinking = "\n".join(self.thinking_parts)
            try:
                siphon_thinking(
                    full_thinking,
                    context={
                        "context_name": self.context_name,
                        **self.context
                    },
                    trigger_workflow=True
                )
            except Exception as e:
                pass


# Convenience function
def syphon_thinking(thinking: str, **kwargs):
    """
    Quick function to SYPHON thinking.

    Usage:
        syphon_thinking("I'm planning to fix Kenny's movement...")
    """
    from ai_thinking_syphon import siphon_thinking as _siphon
    return _siphon(thinking, **kwargs)


if __name__ == "__main__":
    # Demo
    @syphon_thinking_decorator
    def plan_kenny_improvements():
        return """
        I'm planning the next steps for Kenny/Jarvis:
        1. Fix movement stopping issue
        2. Continue visual improvements
        3. Integrate with R5 matrix
        """

    result = plan_kenny_improvements()
    print(f"✅ Function executed, thinking SYPHONed: {result[:50]}...")

    # Context manager demo
    with SyphonContext("Kenny Movement Fix", task="kenny_improvements") as ctx:
        ctx.add_thinking("I'm analyzing the movement issue...")
        ctx.add_thinking("State should always be WALKING, not IDLE")
        ctx.add_thinking("Adding movement continuation logic")
    print("✅ Context manager demo complete - thinking SYPHONed")
