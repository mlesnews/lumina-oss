#!/usr/bin/env python3
"""
Workflow Telemetry Decorator
🔧 Easy instrumentation for workflows

Decorator to automatically instrument workflows with telemetry collection.
Just add @telemetry_track to your workflow function!

#TELEMETRY #INSTRUMENTATION #WORKFLOWS #AUTOMATION
"""

import functools
import time
from typing import Callable, Any, Optional
from datetime import datetime
import uuid

try:
    from syphon_workflow_telemetry_system import (
        get_telemetry_system,
        TelemetryEventType
    )
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


def telemetry_track(workflow_name: Optional[str] = None, 
                   workflow_id: Optional[str] = None,
                   auto_flush: bool = True):
    """
    Decorator to automatically track workflow execution with telemetry

    Usage:
        @telemetry_track(workflow_name="My Workflow", workflow_id="my_workflow")
        def my_workflow_function():
            # Your workflow code
            pass
    """
    def decorator(func: Callable) -> Callable:
        nonlocal workflow_name, workflow_id

        # Use function name if workflow_name not provided
        if workflow_name is None:
            workflow_name = func.__name__

        # Use function name as workflow_id if not provided
        if workflow_id is None:
            workflow_id = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not TELEMETRY_AVAILABLE:
                # If telemetry not available, just run the function
                return func(*args, **kwargs)

            telemetry = get_telemetry_system()
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            started_at = datetime.now()

            try:
                # Capture start event
                telemetry.capture_event(
                    event_type=TelemetryEventType.WORKFLOW_START,
                    workflow_id=workflow_id,
                    workflow_name=workflow_name,
                    execution_id=execution_id,
                    data={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)},
                    tags=["decorator", "auto_track"]
                )

                # Execute workflow
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                ended_at = datetime.now()

                # Determine success (check if result indicates success)
                success = True
                outcome_text = "Workflow completed successfully"

                if isinstance(result, dict):
                    success = result.get("success", True)
                    outcome_text = result.get("message", result.get("outcome_text", outcome_text))

                # Track execution
                telemetry.track_workflow_execution(
                    workflow_id=workflow_id,
                    workflow_name=workflow_name,
                    execution_id=execution_id,
                    started_at=started_at,
                    ended_at=ended_at,
                    success=success,
                    outcome_text=outcome_text,
                    metrics={"duration": duration},
                    workflow_data={
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs),
                        "result": str(result) if not isinstance(result, dict) else result
                    }
                )

                # Flush if requested
                if auto_flush:
                    telemetry.flush_events()

                return result

            except Exception as e:
                # Track error
                ended_at = datetime.now()
                duration = (ended_at - started_at).total_seconds()

                telemetry.capture_event(
                    event_type=TelemetryEventType.WORKFLOW_ERROR,
                    workflow_id=workflow_id,
                    workflow_name=workflow_name,
                    execution_id=execution_id,
                    data={"error": str(e), "error_type": type(e).__name__},
                    tags=["error", "exception"]
                )

                telemetry.track_workflow_execution(
                    workflow_id=workflow_id,
                    workflow_name=workflow_name,
                    execution_id=execution_id,
                    started_at=started_at,
                    ended_at=ended_at,
                    success=False,
                    outcome_text=f"Error: {str(e)}",
                    metrics={"duration": duration},
                    workflow_data={"error": str(e), "error_type": type(e).__name__}
                )

                if auto_flush:
                    telemetry.flush_events()

                # Re-raise exception
                raise

        return wrapper
    return decorator


# Convenience function for manual tracking
def track_workflow_step(workflow_id: str, workflow_name: str, execution_id: str,
                       step_name: str, step_data: Optional[dict] = None):
    """Manually track a workflow step"""
    if not TELEMETRY_AVAILABLE:
        return

    telemetry = get_telemetry_system()
    telemetry.capture_event(
        event_type=TelemetryEventType.WORKFLOW_STEP,
        workflow_id=workflow_id,
        workflow_name=workflow_name,
        execution_id=execution_id,
        data={"step_name": step_name, **(step_data or {})},
        tags=["manual_step", step_name]
    )
