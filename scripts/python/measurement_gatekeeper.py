#!/usr/bin/env python3
"""
Measurement Gatekeeper - Preventative Maintenance & Logging Framework
<COMPANY_NAME> LLC

"If we're not logging, we're not measuring. If we're not measuring, we don't know:
- Where we've been (history)
- Where we are (current state)  
- Where we're going (future direction)

Which means we're wasting our time. Which means we're hallucinating."

This system ensures EVERYTHING is logged and measured before execution.
Gatekeeping logic prevents operations without proper measurement.

@MARVIN @JARVIS @TONY @MACE @GANDALF
"""

import sys
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps
import traceback
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

logger = logging.getLogger("MeasurementGatekeeper")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MeasurementLevel(Enum):
    """Measurement/logging levels"""
    CRITICAL = "critical"  # System-critical operations
    HIGH = "high"  # Important operations
    MEDIUM = "medium"  # Standard operations
    LOW = "low"  # Routine operations
    DEBUG = "debug"  # Debug operations


class OperationState(Enum):
    """Operation state tracking"""
    PENDING = "pending"  # Not yet started
    STARTED = "started"  # Operation started
    IN_PROGRESS = "in_progress"  # Operation in progress
    COMPLETED = "completed"  # Operation completed
    FAILED = "failed"  # Operation failed
    CANCELLED = "cancelled"  # Operation cancelled


@dataclass
class Measurement:
    """Single measurement record"""
    measurement_id: str
    timestamp: datetime
    operation: str
    component: str
    level: MeasurementLevel

    # State tracking
    state: OperationState
    state_history: List[Dict[str, Any]] = field(default_factory=list)

    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)

    # Context
    context: Dict[str, Any] = field(default_factory=dict)

    # Results
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0

    # Gatekeeping
    gatekeeping_passed: bool = False
    gatekeeping_checks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        data['state'] = self.state.value
        return data


@dataclass
class GatekeepingRule:
    """Gatekeeping rule for preventative maintenance"""
    rule_id: str
    name: str
    component: str
    operation: str

    # Conditions
    required_measurements: List[str] = field(default_factory=list)
    required_logs: List[str] = field(default_factory=list)
    min_log_level: MeasurementLevel = MeasurementLevel.MEDIUM

    # Validation
    validation_function: Optional[Callable] = None
    validation_params: Dict[str, Any] = field(default_factory=dict)

    # Actions
    on_fail: str = "block"  # block, warn, allow
    error_message: str = "Gatekeeping check failed"

    enabled: bool = True


class MeasurementGatekeeper:
    """
    Measurement Gatekeeper

    Ensures ALL operations are logged and measured.
    Gatekeeping logic prevents operations without proper measurement.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Measurement Gatekeeper"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Setup logging
        self._setup_logging()

        # Data directories
        self.data_dir = self.project_root / "data" / "measurements"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logs_dir = self.project_root / "logs" / "measurements"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Measurement storage
        self.measurements: Dict[str, Measurement] = {}
        self.measurement_history: List[Measurement] = []

        # Gatekeeping rules
        self.gatekeeping_rules: Dict[str, GatekeepingRule] = {}
        self._load_default_rules()

        # State tracking
        self.state_history: Dict[str, List[Dict[str, Any]]] = {}
        self.current_state: Dict[str, Any] = {}

        # Metrics aggregation
        self.metrics: Dict[str, Dict[str, Any]] = {}

        # Thread safety
        self.lock = threading.Lock()

        # Statistics
        self.total_measurements = 0
        self.total_blocked = 0
        self.total_warned = 0
        self.total_allowed = 0

        self.logger.info("✅ Measurement Gatekeeper initialized")
        self.logger.info("   'If we're not logging, we're not measuring'")
        self.logger.info("   Gatekeeping: ACTIVE")

    def _setup_logging(self) -> None:
        """Setup comprehensive logging"""
        # Create logger
        self.logger = logging.getLogger("MeasurementGatekeeper")
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers.clear()

        # File handler - all measurements
        log_file = self.logs_dir / f"measurements_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler - important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # JSON handler - structured logs
        json_log_file = self.logs_dir / f"measurements_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.json_log_file = json_log_file

        self.logger.info("📊 Logging system initialized")
        self.logger.info(f"   Log file: {log_file}")
        self.logger.info(f"   JSON log: {json_log_file}")

    def _log_json(self, data: Dict[str, Any]) -> None:
        """Log structured JSON data"""
        try:
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")

    def _load_default_rules(self) -> None:
        """Load default gatekeeping rules"""
        # Rule 1: All operations must be logged
        self.gatekeeping_rules['must_log'] = GatekeepingRule(
            rule_id='must_log',
            name='Must Log All Operations',
            component='*',
            operation='*',
            required_logs=['operation_start', 'operation_end'],
            min_log_level=MeasurementLevel.MEDIUM,
            on_fail='block',
            error_message='Operation not logged - BLOCKED'
        )

        # Rule 2: Critical operations require measurement
        self.gatekeeping_rules['critical_measurement'] = GatekeepingRule(
            rule_id='critical_measurement',
            name='Critical Operations Must Be Measured',
            component='*',
            operation='*',
            required_measurements=['duration', 'result', 'state'],
            min_log_level=MeasurementLevel.CRITICAL,
            on_fail='block',
            error_message='Critical operation not measured - BLOCKED'
        )

        # Rule 3: State changes must be tracked
        self.gatekeeping_rules['state_tracking'] = GatekeepingRule(
            rule_id='state_tracking',
            name='State Changes Must Be Tracked',
            component='*',
            operation='*',
            required_measurements=['state', 'state_history'],
            min_log_level=MeasurementLevel.MEDIUM,
            on_fail='warn',
            error_message='State change not tracked - WARNING'
        )

        self.logger.info(f"📋 Loaded {len(self.gatekeeping_rules)} gatekeeping rules")

    def measure(self, operation: str, component: str, 
                level: MeasurementLevel = MeasurementLevel.MEDIUM,
                context: Optional[Dict[str, Any]] = None,
                gatekeeping: bool = True) -> str:
        """
        Start measurement for an operation

        Returns measurement_id
        """
        measurement_id = f"{component}_{operation}_{int(time.time() * 1000)}"

        measurement = Measurement(
            measurement_id=measurement_id,
            timestamp=datetime.now(),
            operation=operation,
            component=component,
            level=level,
            state=OperationState.STARTED,
            context=context or {}
        )

        # Gatekeeping check
        if gatekeeping:
            gatekeeping_result = self._check_gatekeeping(measurement)
            measurement.gatekeeping_passed = gatekeeping_result['passed']
            measurement.gatekeeping_checks = gatekeeping_result['checks']

            if not gatekeeping_result['passed']:
                if gatekeeping_result['action'] == 'block':
                    self.logger.error(f"🚫 BLOCKED: {component}.{operation} - {gatekeeping_result['reason']}")
                    self.total_blocked += 1
                    measurement.state = OperationState.FAILED
                    measurement.error = f"Gatekeeping blocked: {gatekeeping_result['reason']}"
                    self._record_measurement(measurement)
                    raise ValueError(f"Operation blocked by gatekeeping: {gatekeeping_result['reason']}")
                elif gatekeeping_result['action'] == 'warn':
                    self.logger.warning(f"⚠️  WARNING: {component}.{operation} - {gatekeeping_result['reason']}")
                    self.total_warned += 1

        # Log operation start
        self.logger.info(f"📊 MEASURE: {component}.{operation} [ID: {measurement_id}]")
        self._log_json({
            'type': 'measurement_start',
            'measurement_id': measurement_id,
            'operation': operation,
            'component': component,
            'level': level.value,
            'timestamp': measurement.timestamp.isoformat(),
            'context': measurement.context
        })

        # Record state
        self._record_state_change(component, operation, OperationState.STARTED, measurement_id)

        # Store measurement
        with self.lock:
            self.measurements[measurement_id] = measurement
            self.total_measurements += 1

        return measurement_id

    def complete_measurement(self, measurement_id: str, 
                            result: Optional[Any] = None,
                            error: Optional[str] = None,
                            metrics: Optional[Dict[str, Any]] = None) -> None:
        """Complete a measurement"""
        with self.lock:
            if measurement_id not in self.measurements:
                self.logger.warning(f"Measurement not found: {measurement_id}")
                return

            measurement = self.measurements[measurement_id]

            # Update state
            if error:
                measurement.state = OperationState.FAILED
                measurement.error = error
            else:
                measurement.state = OperationState.COMPLETED
                measurement.result = result

            # Calculate duration
            duration = (datetime.now() - measurement.timestamp).total_seconds() * 1000
            measurement.duration_ms = duration

            # Update metrics
            if metrics:
                measurement.metrics.update(metrics)

            # Record state change
            self._record_state_change(
                measurement.component,
                measurement.operation,
                measurement.state,
                measurement_id
            )

            # Log completion
            status_icon = "✅" if measurement.state == OperationState.COMPLETED else "❌"
            self.logger.info(
                f"{status_icon} COMPLETE: {measurement.component}.{measurement.operation} "
                f"[ID: {measurement_id}] ({duration:.1f}ms)"
            )

            self._log_json({
                'type': 'measurement_complete',
                'measurement_id': measurement_id,
                'operation': measurement.operation,
                'component': measurement.component,
                'state': measurement.state.value,
                'duration_ms': duration,
                'result': str(result) if result else None,
                'error': error,
                'metrics': measurement.metrics
            })

            # Move to history
            self.measurement_history.append(measurement)
            del self.measurements[measurement_id]

            # Keep only last 10000 measurements in memory
            if len(self.measurement_history) > 10000:
                self.measurement_history = self.measurement_history[-10000:]

            # Save measurement
            self._save_measurement(measurement)

    def _check_gatekeeping(self, measurement: Measurement) -> Dict[str, Any]:
        """Check gatekeeping rules"""
        checks = []
        passed = True
        action = 'allow'
        reason = None

        # Check applicable rules
        for rule_id, rule in self.gatekeeping_rules.items():
            if not rule.enabled:
                continue

            # Check if rule applies
            if rule.component != '*' and rule.component != measurement.component:
                continue
            if rule.operation != '*' and rule.operation != measurement.operation:
                continue

            # Check required measurements
            rule_passed = True
            rule_reason = None

            if rule.required_measurements:
                for req_measurement in rule.required_measurements:
                    if req_measurement not in measurement.metrics:
                        rule_passed = False
                        rule_reason = f"Missing measurement: {req_measurement}"
                        break

            # Check validation function
            if rule_passed and rule.validation_function:
                try:
                    validation_result = rule.validation_function(
                        measurement,
                        **rule.validation_params
                    )
                    if not validation_result:
                        rule_passed = False
                        rule_reason = "Validation function failed"
                except Exception as e:
                    rule_passed = False
                    rule_reason = f"Validation error: {e}"

            checks.append({
                'rule_id': rule_id,
                'rule_name': rule.name,
                'passed': rule_passed,
                'reason': rule_reason
            })

            if not rule_passed:
                passed = False
                action = rule.on_fail
                reason = rule_reason or rule.error_message
                break

        return {
            'passed': passed,
            'action': action,
            'reason': reason,
            'checks': checks
        }

    def _record_state_change(self, component: str, operation: str, 
                           state: OperationState, measurement_id: str) -> None:
        """Record state change"""
        state_key = f"{component}.{operation}"

        if state_key not in self.state_history:
            self.state_history[state_key] = []

        state_record = {
            'timestamp': datetime.now().isoformat(),
            'state': state.value,
            'measurement_id': measurement_id
        }

        self.state_history[state_key].append(state_record)

        # Update current state
        self.current_state[state_key] = {
            'state': state.value,
            'last_change': datetime.now().isoformat(),
            'measurement_id': measurement_id
        }

        # Keep only last 1000 state changes per component
        if len(self.state_history[state_key]) > 1000:
            self.state_history[state_key] = self.state_history[state_key][-1000:]

    def _record_measurement(self, measurement: Measurement) -> None:
        """Record measurement (even if blocked)"""
        self._log_json({
            'type': 'measurement_blocked',
            'measurement_id': measurement.measurement_id,
            'operation': measurement.operation,
            'component': measurement.component,
            'reason': measurement.error,
            'gatekeeping_checks': measurement.gatekeeping_checks
        })
        self._save_measurement(measurement)

    def _save_measurement(self, measurement: Measurement) -> None:
        """Save measurement to disk"""
        try:
            # Save to daily file
            date_str = datetime.now().strftime('%Y%m%d')
            measurement_file = self.data_dir / f"measurements_{date_str}.jsonl"

            with open(measurement_file, 'a', encoding='utf-8') as f:
                json.dump(measurement.to_dict(), f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to save measurement: {e}")

    def get_state_history(self, component: str, operation: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get state history"""
        if operation:
            key = f"{component}.{operation}"
            return self.state_history.get(key, [])
        else:
            # Return all states for component
            result = []
            for key, history in self.state_history.items():
                if key.startswith(f"{component}."):
                    result.extend(history)
            return result

    def get_current_state(self, component: str, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get current state"""
        if operation:
            key = f"{component}.{operation}"
            return self.current_state.get(key, {})
        else:
            # Return all current states for component
            result = {}
            for key, state in self.current_state.items():
                if key.startswith(f"{component}."):
                    result[key] = state
            return result

    def get_measurements(self, component: Optional[str] = None, 
                        operation: Optional[str] = None,
                        limit: int = 100) -> List[Measurement]:
        """Get measurements"""
        results = []

        for measurement in self.measurement_history[-limit:]:
            if component and measurement.component != component:
                continue
            if operation and measurement.operation != operation:
                continue
            results.append(measurement)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get measurement statistics"""
        return {
            'total_measurements': self.total_measurements,
            'total_blocked': self.total_blocked,
            'total_warned': self.total_warned,
            'total_allowed': self.total_allowed,
            'active_measurements': len(self.measurements),
            'historical_measurements': len(self.measurement_history),
            'gatekeeping_rules': len(self.gatekeeping_rules),
            'tracked_components': len(set(m.component for m in self.measurement_history)),
            'tracked_operations': len(set(m.operation for m in self.measurement_history))
        }


def measure_operation(component: str, level: MeasurementLevel = MeasurementLevel.MEDIUM):
    """
    Decorator to automatically measure operations

    Usage:
        @measure_operation("MyComponent", MeasurementLevel.HIGH)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get gatekeeper instance (singleton pattern)
            gatekeeper = get_measurement_gatekeeper()

            # Start measurement
            measurement_id = gatekeeper.measure(
                operation=func.__name__,
                component=component,
                level=level,
                context={
                    'args': str(args)[:200],  # Limit length
                    'kwargs': str(kwargs)[:200]
                }
            )

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Complete measurement
                gatekeeper.complete_measurement(
                    measurement_id,
                    result=result,
                    metrics={'success': True}
                )

                return result
            except Exception as e:
                # Complete measurement with error
                gatekeeper.complete_measurement(
                    measurement_id,
                    error=str(e),
                    metrics={'success': False}
                )
                raise

        return wrapper
    return decorator


# Singleton instance
_gatekeeper_instance: Optional[MeasurementGatekeeper] = None


def get_measurement_gatekeeper() -> MeasurementGatekeeper:
    """Get singleton measurement gatekeeper instance"""
    global _gatekeeper_instance
    if _gatekeeper_instance is None:
        _gatekeeper_instance = MeasurementGatekeeper()
    return _gatekeeper_instance


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Measurement Gatekeeper")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--state", type=str, nargs=2, metavar=("COMPONENT", "OPERATION"),
                       help="Get state for component.operation")
    parser.add_argument("--history", type=str, nargs=2, metavar=("COMPONENT", "OPERATION"),
                       help="Get history for component.operation")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    gatekeeper = get_measurement_gatekeeper()

    if args.state:
        component, operation = args.state
        state = gatekeeper.get_current_state(component, operation)
        if args.json:
            print(json.dumps(state, indent=2))
        else:
            print(f"\n📊 Current State: {component}.{operation}")
            print(json.dumps(state, indent=2))

    elif args.history:
        component, operation = args.history
        history = gatekeeper.get_state_history(component, operation)
        if args.json:
            print(json.dumps(history, indent=2))
        else:
            print(f"\n📊 State History: {component}.{operation}")
            print(f"   Records: {len(history)}")
            for record in history[-10:]:  # Last 10
                print(f"   {record['timestamp']}: {record['state']}")

    elif args.stats:
        stats = gatekeeper.get_statistics()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n📊 Measurement Gatekeeper Statistics")
            print("=" * 60)
            print(f"Total Measurements: {stats['total_measurements']}")
            print(f"Blocked: {stats['total_blocked']}")
            print(f"Warned: {stats['total_warned']}")
            print(f"Allowed: {stats['total_allowed']}")
            print(f"Active: {stats['active_measurements']}")
            print(f"Historical: {stats['historical_measurements']}")
            print(f"Gatekeeping Rules: {stats['gatekeeping_rules']}")
            print(f"Tracked Components: {stats['tracked_components']}")
            print(f"Tracked Operations: {stats['tracked_operations']}")

    else:
        parser.print_help()
        print("\n📊 Measurement Gatekeeper")
        print("   'If we're not logging, we're not measuring'")

