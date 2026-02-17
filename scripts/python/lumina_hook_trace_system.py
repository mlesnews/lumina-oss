"""
LUMINA Hook & Trace System
Comprehensive metrics and analytics tracking for all LUMINA operations.

Tracks everything automatically via hooks and traces:
- All system operations
- All integrations
- All workflows
- All errors and successes
- Performance metrics
- Usage analytics

#JARVIS #LUMINA #METRICS #ANALYTICS #HOOK #TRACE #MONITORING
"""

import json
import time
import functools
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LuminaHookTrace")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaHookTrace")


class TraceLevel(Enum):
    """Trace level for operations."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OperationType(Enum):
    """Type of operation being traced."""
    EMAIL = "email"
    HVAC = "hvac"
    SYPHON = "syphon"
    GMAIL = "gmail"
    PROTONMAIL = "protonmail"
    SECRETS = "secrets"
    N8N = "n8n"
    NAS = "nas"
    WORKFLOW = "workflow"
    API = "api"
    DATABASE = "database"
    FILE = "file"
    SYSTEM = "system"
    OTHER = "other"


@dataclass
class TraceEvent:
    """Individual trace event."""
    event_id: str
    timestamp: str
    operation_type: OperationType
    operation_name: str
    level: TraceLevel
    message: str
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsSnapshot:
    """Metrics snapshot at a point in time."""
    timestamp: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    operations_by_type: Dict[str, int]
    operations_by_level: Dict[str, int]
    average_duration_ms: float
    error_rate: float
    success_rate: float
    recent_errors: List[Dict[str, Any]]
    system_health: str  # "healthy", "degraded", "critical"


class LuminaHookTraceSystem:
    """
    LUMINA Hook & Trace System

    Comprehensive metrics and analytics tracking:
    - Automatic hook injection
    - Function tracing
    - Performance monitoring
    - Error tracking
    - Usage analytics
    - System health monitoring
    """

    def __init__(self, project_root: Path):
        """
        Initialize Hook & Trace System.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "lumina_metrics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.traces_dir = self.data_dir / "traces"
        self.traces_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_dir = self.data_dir / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.analytics_dir = self.data_dir / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # In-memory tracking
        self.trace_buffer: List[TraceEvent] = []
        self.metrics_buffer: List[MetricsSnapshot] = []
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.duration_sums: Dict[str, List[float]] = defaultdict(list)

        # Thread safety
        self.lock = threading.Lock()

        # Configuration
        self.buffer_size = 1000  # Flush when buffer reaches this size
        self.flush_interval = 60  # Flush every N seconds
        self.enabled = True

        # Start background flush thread
        self._start_flush_thread()

        logger.info("✅ LUMINA Hook & Trace System initialized")

    def _start_flush_thread(self):
        """Start background thread for periodic flushing."""
        def flush_worker():
            while self.enabled:
                time.sleep(self.flush_interval)
                self.flush_buffers()

        thread = threading.Thread(target=flush_worker, daemon=True)
        thread.start()

    def hook(self, 
             operation_type: OperationType = OperationType.OTHER,
             operation_name: Optional[str] = None,
             level: TraceLevel = TraceLevel.INFO):
        """
        Decorator to hook/trace function calls.

        Usage:
            @hook_trace.hook(OperationType.EMAIL, "send_email")
            def send_email(...):
                ...
        """
        def decorator(func: Callable) -> Callable:
            op_name = operation_name or func.__name__

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)

                event_id = f"{op_name}_{int(time.time() * 1000000)}"
                start_time = time.time()
                success = None
                error = None
                result = None

                try:
                    # Trace entry
                    self.trace(
                        event_id=event_id,
                        operation_type=operation_type,
                        operation_name=op_name,
                        level=level,
                        message=f"Starting {op_name}",
                        metadata={"args_count": len(args), "kwargs_count": len(kwargs)}
                    )

                    # Execute function
                    result = func(*args, **kwargs)
                    success = True
                    duration = (time.time() - start_time) * 1000

                    # Trace success
                    self.trace(
                        event_id=event_id,
                        operation_type=operation_type,
                        operation_name=op_name,
                        level=TraceLevel.INFO,
                        message=f"Completed {op_name}",
                        duration_ms=duration,
                        success=True,
                        metadata={"result_type": type(result).__name__}
                    )

                    return result

                except Exception as e:
                    success = False
                    error = str(e)
                    duration = (time.time() - start_time) * 1000

                    # Trace error
                    import traceback
                    self.trace(
                        event_id=event_id,
                        operation_type=operation_type,
                        operation_name=op_name,
                        level=TraceLevel.ERROR,
                        message=f"Failed {op_name}: {error}",
                        duration_ms=duration,
                        success=False,
                        error=error,
                        stack_trace=traceback.format_exc()
                    )

                    raise

            return wrapper
        return decorator

    def trace(self,
              event_id: Optional[str] = None,
              operation_type: OperationType = OperationType.OTHER,
              operation_name: str = "",
              level: TraceLevel = TraceLevel.INFO,
              message: str = "",
              duration_ms: Optional[float] = None,
              success: Optional[bool] = None,
              error: Optional[str] = None,
              metadata: Optional[Dict[str, Any]] = None,
              stack_trace: Optional[str] = None,
              context: Optional[Dict[str, Any]] = None):
        """
        Record a trace event.

        Args:
            event_id: Unique event ID (auto-generated if not provided)
            operation_type: Type of operation
            operation_name: Name of operation
            level: Trace level
            message: Event message
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            error: Error message if failed
            metadata: Additional metadata
            stack_trace: Stack trace if error
            context: Context information
        """
        if not self.enabled:
            return

        if event_id is None:
            event_id = f"{operation_name}_{int(time.time() * 1000000)}"

        event = TraceEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            operation_type=operation_type,
            operation_name=operation_name,
            level=level,
            message=message,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata or {},
            stack_trace=stack_trace,
            context=context or {}
        )

        with self.lock:
            self.trace_buffer.append(event)

            # Update metrics
            self.operation_counts[operation_type.value] += 1
            if success is False:
                self.error_counts[operation_type.value] += 1
            if duration_ms:
                self.duration_sums[operation_type.value].append(duration_ms)

            # Flush if buffer is full
            if len(self.trace_buffer) >= self.buffer_size:
                self._flush_traces()

    def get_metrics(self, hours: int = 24) -> MetricsSnapshot:
        """
        Get current metrics snapshot.

        Args:
            hours: Hours of data to include

        Returns:
            MetricsSnapshot
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Load recent traces
        recent_traces = self._load_recent_traces(cutoff_time)

        total_ops = len(recent_traces)
        successful = sum(1 for t in recent_traces if t.get("success") is True)
        failed = sum(1 for t in recent_traces if t.get("success") is False)

        # Group by type
        ops_by_type = defaultdict(int)
        for trace in recent_traces:
            ops_by_type[trace.get("operation_type", "other")] += 1

        # Group by level
        ops_by_level = defaultdict(int)
        for trace in recent_traces:
            ops_by_level[trace.get("level", "info")] += 1

        # Calculate durations
        durations = [t.get("duration_ms", 0) for t in recent_traces if t.get("duration_ms")]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Error rate
        error_rate = (failed / total_ops * 100) if total_ops > 0 else 0.0
        success_rate = (successful / total_ops * 100) if total_ops > 0 else 0.0

        # Recent errors
        recent_errors = [
            {
                "timestamp": t.get("timestamp"),
                "operation": t.get("operation_name"),
                "error": t.get("error")
            }
            for t in recent_traces
            if t.get("success") is False
        ][-10:]  # Last 10 errors

        # System health
        if error_rate < 5:
            health = "healthy"
        elif error_rate < 20:
            health = "degraded"
        else:
            health = "critical"

        return MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            total_operations=total_ops,
            successful_operations=successful,
            failed_operations=failed,
            operations_by_type=dict(ops_by_type),
            operations_by_level=dict(ops_by_level),
            average_duration_ms=avg_duration,
            error_rate=error_rate,
            success_rate=success_rate,
            recent_errors=recent_errors,
            system_health=health
        )

    def _load_recent_traces(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """Load recent traces from disk."""
        traces = []

        # Load from trace files
        for trace_file in sorted(self.traces_dir.glob("*.json"), reverse=True):
            try:
                with open(trace_file, 'r') as f:
                    file_traces = json.load(f)
                    for trace in file_traces:
                        trace_time = datetime.fromisoformat(trace.get("timestamp", ""))
                        if trace_time >= cutoff_time:
                            traces.append(trace)
            except Exception as e:
                logger.warning(f"Failed to load trace file {trace_file}: {e}")

        # Add buffer traces
        with self.lock:
            for trace in self.trace_buffer:
                trace_time = datetime.fromisoformat(trace.timestamp)
                if trace_time >= cutoff_time:
                    traces.append(asdict(trace))

        return traces

    def _flush_traces(self):
        """Flush trace buffer to disk."""
        if not self.trace_buffer:
            return

        with self.lock:
            buffer = self.trace_buffer.copy()
            self.trace_buffer.clear()

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_file = self.traces_dir / f"traces_{timestamp}.json"

        try:
            # Convert to JSON-serializable format
            serializable_traces = []
            for t in buffer:
                trace_dict = asdict(t)
                # Convert Enum to string
                trace_dict['operation_type'] = trace_dict['operation_type'].value if hasattr(trace_dict['operation_type'], 'value') else str(trace_dict['operation_type'])
                trace_dict['level'] = trace_dict['level'].value if hasattr(trace_dict['level'], 'value') else str(trace_dict['level'])
                serializable_traces.append(trace_dict)

            with open(trace_file, 'w') as f:
                json.dump(serializable_traces, f, indent=2, ensure_ascii=False)

            logger.debug(f"Flushed {len(buffer)} traces to {trace_file}")
        except Exception as e:
            logger.error(f"Failed to flush traces: {e}")
            # Put back in buffer
            with self.lock:
                self.trace_buffer.extend(buffer)

    def flush_buffers(self):
        """Flush all buffers to disk."""
        self._flush_traces()

        # Save metrics snapshot
        metrics = self.get_metrics()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = self.metrics_dir / f"metrics_{timestamp}.json"

        try:
            metrics_dict = asdict(metrics)
            # Ensure all values are JSON-serializable
            with open(metrics_file, 'w') as f:
                json.dump(metrics_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def generate_analytics_report(self, hours: int = 24) -> Dict[str, Any]:
        try:
            """
            Generate comprehensive analytics report.

            Args:
                hours: Hours of data to analyze

            Returns:
                Analytics report dictionary
            """
            metrics = self.get_metrics(hours=hours)

            report = {
                "report_timestamp": datetime.now().isoformat(),
                "period_hours": hours,
                "summary": {
                    "total_operations": metrics.total_operations,
                    "successful_operations": metrics.successful_operations,
                    "failed_operations": metrics.failed_operations,
                    "success_rate": f"{metrics.success_rate:.2f}%",
                    "error_rate": f"{metrics.error_rate:.2f}%",
                    "average_duration_ms": f"{metrics.average_duration_ms:.2f}",
                    "system_health": metrics.system_health
                },
                "operations_by_type": metrics.operations_by_type,
                "operations_by_level": metrics.operations_by_level,
                "recent_errors": metrics.recent_errors,
                "recommendations": self._generate_recommendations(metrics)
            }

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.analytics_dir / f"analytics_report_{timestamp}.json"

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 Analytics report saved to {report_file}")

            return report

        except Exception as e:
            self.logger.error(f"Error in generate_analytics_report: {e}", exc_info=True)
            raise
    def _generate_recommendations(self, metrics: MetricsSnapshot) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        if metrics.error_rate > 20:
            recommendations.append("⚠️  High error rate detected - investigate system stability")

        if metrics.average_duration_ms > 5000:
            recommendations.append("⚠️  Slow operations detected - optimize performance")

        if "email" in metrics.operations_by_type and metrics.operations_by_type["email"] > 1000:
            recommendations.append("ℹ️  High email activity - consider batching")

        if metrics.system_health == "critical":
            recommendations.append("🚨 CRITICAL: System health is critical - immediate attention required")

        if not recommendations:
            recommendations.append("✅ System operating normally")

        return recommendations

    def shutdown(self):
        """Shutdown hook & trace system."""
        self.enabled = False
        self.flush_buffers()
        logger.info("✅ LUMINA Hook & Trace System shut down")


# Global instance
_hook_trace_instance: Optional[LuminaHookTraceSystem] = None


def get_hook_trace(project_root: Optional[Path] = None) -> LuminaHookTraceSystem:
    try:
        """Get or create global hook & trace instance."""
        global _hook_trace_instance

        if _hook_trace_instance is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _hook_trace_instance = LuminaHookTraceSystem(project_root)

        return _hook_trace_instance


    except Exception as e:
        logger.error(f"Error in get_hook_trace: {e}", exc_info=True)
        raise
def hook(operation_type: OperationType = OperationType.OTHER,
         operation_name: Optional[str] = None,
         level: TraceLevel = TraceLevel.INFO):
    """Convenience decorator for hooking functions."""
    return get_hook_trace().hook(operation_type, operation_name, level)


def trace(*args, **kwargs):
    """Convenience function for tracing events."""
    return get_hook_trace().trace(*args, **kwargs)


def main():
    try:
        """Test Hook & Trace System."""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Hook & Trace System")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--metrics", action="store_true", help="Show current metrics")
        parser.add_argument("--analytics", action="store_true", help="Generate analytics report")
        parser.add_argument("--hours", type=int, default=24, help="Hours of data to analyze")
        parser.add_argument("--flush", action="store_true", help="Flush buffers to disk")

        args = parser.parse_args()

        hook_trace = LuminaHookTraceSystem(args.project_root)

        if args.metrics:
            metrics = hook_trace.get_metrics(hours=args.hours)
            print("\n" + "="*80)
            print("LUMINA METRICS SNAPSHOT")
            print("="*80)
            print(f"Timestamp: {metrics.timestamp}")
            print(f"Total Operations: {metrics.total_operations}")
            print(f"Successful: {metrics.successful_operations}")
            print(f"Failed: {metrics.failed_operations}")
            print(f"Success Rate: {metrics.success_rate:.2f}%")
            print(f"Error Rate: {metrics.error_rate:.2f}%")
            print(f"Average Duration: {metrics.average_duration_ms:.2f}ms")
            print(f"System Health: {metrics.system_health}")
            print("\nOperations by Type:")
            for op_type, count in metrics.operations_by_type.items():
                print(f"  {op_type}: {count}")
            print("\nOperations by Level:")
            for level, count in metrics.operations_by_level.items():
                print(f"  {level}: {count}")

        elif args.analytics:
            report = hook_trace.generate_analytics_report(hours=args.hours)
            print("\n" + "="*80)
            print("LUMINA ANALYTICS REPORT")
            print("="*80)
            print(json.dumps(report, indent=2))

        elif args.flush:
            hook_trace.flush_buffers()
            print("✅ Buffers flushed to disk")

        else:
            parser.print_help()

        hook_trace.shutdown()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()