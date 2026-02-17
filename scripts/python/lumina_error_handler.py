"""Global Error Handling Framework for Lumina

All scripts should use this for consistent error handling, logging, and recovery.
"""

import sys
import traceback
import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from datetime import datetime

class LuminaErrorHandler:
    """Global error handler for all Lumina components"""

    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = logging.getLogger(f"lumina.{component_name}")
        self.error_log_file = Path(f"logs/{component_name}_errors.json")

    def handle_error(self, error: Exception, context: Dict[str, Any] = None,
                    recovery_actions: List[Callable] = None) -> Dict[str, Any]:
        """Handle an error with comprehensive logging and optional recovery"""

        error_details = {
            "timestamp": datetime.now().isoformat(),
            "component": self.component_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "context": context or {},
            "recovery_attempted": False,
            "recovery_successful": False
        }

        # Log the error
        self.logger.error(f"❌ {self.component_name} error: {error}", extra=error_details)

        # Attempt recovery if actions provided
        if recovery_actions:
            error_details["recovery_attempted"] = True
            try:
                for action in recovery_actions:
                    action()
                error_details["recovery_successful"] = True
                self.logger.info(f"✅ {self.component_name} recovery successful")
            except Exception as recovery_error:
                error_details["recovery_error"] = str(recovery_error)
                self.logger.error(f"❌ {self.component_name} recovery failed: {recovery_error}")

        # Save to error log
        self._save_error(error_details)

        return error_details

    def _save_error(self, error_details: Dict[str, Any]):
        """Save error details to log file"""
        try:
            self.error_log_file.parent.mkdir(parents=True, exist_ok=True)

            # Load existing errors
            existing_errors = []
            if self.error_log_file.exists():
                with open(self.error_log_file, 'r') as f:
                    existing_errors = json.load(f)

            # Add new error
            existing_errors.append(error_details)

            # Keep only last 100 errors
            if len(existing_errors) > 100:
                existing_errors = existing_errors[-100:]

            # Save
            with open(self.error_log_file, 'w') as f:
                json.dump(existing_errors, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save error log: {e}")

# Global error handler instance
def get_error_handler(component_name: str) -> LuminaErrorHandler:
    """Get error handler for a component"""
    return LuminaErrorHandler(component_name)

# Decorator for automatic error handling
def handle_errors(component_name: str, recovery_actions: List[Callable] = None):
    """Decorator to automatically handle errors in functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = get_error_handler(component_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200] + "..." if len(str(args)) > 200 else str(args),
                    "kwargs": str(kwargs)[:200] + "..." if len(str(kwargs)) > 200 else str(kwargs)
                }
                return handler.handle_error(e, context, recovery_actions)
        return wrapper
    return decorator
