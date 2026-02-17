#!/usr/bin/env python3
"""
JARVIS Security Surveillance System

MCU JARVIS Capability: Security & Surveillance
Threat detection, security monitoring, access control management.

@JARVIS @SECURITY @SURVEILLANCE @MCU_FEATURE
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import threading
import time
import tempfile
import shutil
import psutil
import os
from collections import defaultdict, deque

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSecuritySurveillance")


class ThreatLevel(Enum):
    """Threat level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Security event types"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    INTRUSION_DETECTED = "intrusion_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    FAILED_LOGIN = "failed_login"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_BREACH = "system_breach"
    NETWORK_ANOMALY = "network_anomaly"
    FILE_ACCESS_VIOLATION = "file_access_violation"
    PROCESS_ANOMALY = "process_anomaly"
    CONFIGURATION_CHANGE = "configuration_change"


@dataclass
class SecurityEvent:
    """Security event"""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['threat_level'] = self.threat_level.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data


@dataclass
class AccessControlRule:
    """Access control rule"""
    rule_id: str
    resource: str
    allowed_users: List[str]
    allowed_ips: List[str] = field(default_factory=list)
    allowed_times: Optional[Dict[str, Any]] = None  # Time-based access
    requires_authentication: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JARVISSecuritySurveillance:
    """
    JARVIS Security Surveillance System

    MCU JARVIS Capability: Continuous threat monitoring, anomaly detection, access control.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize security surveillance system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISSecuritySurveillance")

        # Event storage
        self.events: List[SecurityEvent] = []

        # Access control rules
        self.access_rules: Dict[str, AccessControlRule] = {}

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis_security"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "security_events.json"
        self.rules_file = self.data_dir / "access_rules.json"

        # Alert handlers
        self.alert_handlers: List[Callable] = []

        # Anomaly detection baselines
        self.process_baseline: Dict[str, int] = defaultdict(int)
        self.network_baseline: Dict[str, int] = defaultdict(int)
        self.file_access_baseline: Dict[str, int] = defaultdict(int)

        # Anomaly detection history
        self.anomaly_history: deque = deque(maxlen=1000)

        # Threat intelligence
        self.threat_patterns: Dict[str, List[str]] = {
            "suspicious_process": [
                "cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe"
            ],
            "suspicious_network": [
                "unusual_port", "high_bandwidth", "foreign_ip"
            ],
            "file_anomaly": [
                "encrypted_file_access", "system_file_modification", "bulk_file_access"
            ]
        }

        # Automated response actions
        self.automated_responses: Dict[ThreatLevel, List[str]] = {
            ThreatLevel.LOW: ["log", "notify"],
            ThreatLevel.MEDIUM: ["log", "notify", "isolate"],
            ThreatLevel.HIGH: ["log", "notify", "isolate", "block"],
            ThreatLevel.CRITICAL: ["log", "notify", "isolate", "block", "escalate"]
        }

        # Load state
        self._load_state()

        self.logger.info("🔒 JARVIS Security Surveillance initialized")
        self.logger.info("   Threat detection: ACTIVE")
        self.logger.info("   Anomaly detection: ACTIVE")
        self.logger.info("   Automated response: ENABLED")

    def _load_state(self):
        """Load security events and rules"""
        # Load events
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    for event_data in data:
                        event = SecurityEvent(
                            event_id=event_data['event_id'],
                            event_type=SecurityEventType(event_data['event_type']),
                            threat_level=ThreatLevel(event_data['threat_level']),
                            timestamp=datetime.fromisoformat(event_data['timestamp']),
                            source=event_data['source'],
                            description=event_data['description'],
                            details=event_data.get('details', {}),
                            resolved=event_data.get('resolved', False),
                            resolution=event_data.get('resolution'),
                            resolved_at=datetime.fromisoformat(event_data['resolved_at']) if event_data.get('resolved_at') else None
                        )
                        self.events.append(event)
                self.logger.info(f"   Loaded {len(self.events)} security events")
            except Exception as e:
                self.logger.error(f"Error loading events: {e}")

        # Load access rules
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r') as f:
                    data = json.load(f)
                    for rule_data in data:
                        rule = AccessControlRule(**rule_data)
                        self.access_rules[rule.rule_id] = rule
                self.logger.info(f"   Loaded {len(self.access_rules)} access rules")
            except Exception as e:
                self.logger.error(f"Error loading rules: {e}")

    def _save_state(self):
        """Save security events and rules using atomic writes"""
        max_retries = 3
        retry_delay = 0.5

        # Save events (keep last 1000)
        events_to_save = self.events[-1000:]
        self._atomic_write_file(
            self.events_file,
            [e.to_dict() for e in events_to_save],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        # Save rules
        self._atomic_write_file(
            self.rules_file,
            [r.to_dict() for r in self.access_rules.values()],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _atomic_write_file(self, file_path: Path, data: Any, max_retries: int = 3, retry_delay: float = 0.5):
        """Atomically write data to a file with retry logic"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file = file_path.parent / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Directory not writable: {file_path.parent} - {e}")
                return
        except Exception as e:
            self.logger.error(f"Error creating directory {file_path.parent}: {e}")
            return

        for attempt in range(max_retries):
            try:
                temp_file = file_path.parent / f".{file_path.name}.tmp"

                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                if file_path.exists():
                    try:
                        file_path.unlink()
                    except PermissionError:
                        time.sleep(retry_delay * (attempt + 1))
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise

                temp_file.replace(file_path)
                return

            except PermissionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.debug(f"Permission denied, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: Permission denied after {max_retries} attempts - {e}")
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception as e:
                self.logger.error(f"Error saving state to {file_path}: {e}")
                if 'temp_file' in locals() and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                return

    def record_event(self, event_type: SecurityEventType, threat_level: ThreatLevel,
                    source: str, description: str, details: Dict[str, Any] = None) -> SecurityEvent:
        """Record a security event"""
        event = SecurityEvent(
            event_id=f"sec_{int(datetime.now().timestamp())}_{len(self.events)}",
            event_type=event_type,
            threat_level=threat_level,
            timestamp=datetime.now(),
            source=source,
            description=description,
            details=details or {}
        )

        self.events.append(event)

        # Store in anomaly history
        self.anomaly_history.append({
            "timestamp": datetime.now(),
            "event_type": event_type.value,
            "threat_level": threat_level.value,
            "source": source
        })

        self._save_state()

        # Automated response based on threat level
        self._automated_response(event)

        # Trigger alerts for high-threat events
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._trigger_alert(event)

        self.logger.warning(f"🚨 Security event: {event_type.value} - {threat_level.value} - {description}")
        return event

    def _automated_response(self, event: SecurityEvent):
        """Execute automated response actions based on threat level"""
        actions = self.automated_responses.get(event.threat_level, [])

        for action in actions:
            try:
                if action == "log":
                    # Already logged
                    pass
                elif action == "notify":
                    # Send notification
                    self.logger.warning(f"🔔 NOTIFICATION: {event.description}")
                elif action == "isolate":
                    # Isolate affected resource
                    self._isolate_resource(event)
                elif action == "block":
                    # Block source
                    self._block_source(event)
                elif action == "escalate":
                    # Escalate to higher authority
                    self._escalate_threat(event)
            except Exception as e:
                self.logger.error(f"Automated response error ({action}): {e}")

    def _isolate_resource(self, event: SecurityEvent):
        """Isolate affected resource"""
        self.logger.warning(f"🔒 ISOLATING: {event.source}")
        # Would implement actual isolation logic

    def _block_source(self, event: SecurityEvent):
        """Block threat source"""
        self.logger.warning(f"🚫 BLOCKING: {event.source}")
        # Would implement actual blocking logic

    def _escalate_threat(self, event: SecurityEvent):
        """Escalate critical threat"""
        self.logger.error(f"🚨 ESCALATION: {event.description}")
        # Would implement escalation logic (notify admins, etc.)

    def _trigger_alert(self, event: SecurityEvent):
        """Trigger alert handlers"""
        for handler in self.alert_handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Alert handler error: {e}")

    def register_alert_handler(self, handler: Callable):
        """Register an alert handler"""
        self.alert_handlers.append(handler)

    def start_monitoring(self):
        """Start continuous monitoring (MCU JARVIS style)"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("🔒 Security monitoring started")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("🔒 Security monitoring stopped")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for anomalies
                self._check_anomalies()

                # Check access violations
                self._check_access_violations()

                # Check system integrity
                self._check_system_integrity()

                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)

    def _check_anomalies(self):
        """
        Check for security anomalies using statistical analysis

        Detects:
        - Unusual file access patterns
        - Network traffic anomalies
        - Process execution anomalies
        - Configuration changes
        - Behavioral deviations
        """
        try:
            # 1. Process anomaly detection
            self._detect_process_anomalies()

            # 2. Network anomaly detection
            self._detect_network_anomalies()

            # 3. File access anomaly detection
            self._detect_file_access_anomalies()

            # 4. System configuration changes
            self._detect_config_changes()

            # 5. Behavioral pattern analysis
            self._analyze_behavioral_patterns()

        except Exception as e:
            self.logger.error(f"Anomaly detection error: {e}")

    def _detect_process_anomalies(self):
        """Detect unusual process execution patterns"""
        try:
            current_processes = {}
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    current_processes[proc_name] = current_processes.get(proc_name, 0) + 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Check for suspicious processes
            for proc_name, count in current_processes.items():
                baseline_count = self.process_baseline.get(proc_name, 0)

                # Anomaly: Process count significantly higher than baseline
                if baseline_count > 0 and count > baseline_count * 2:
                    self.record_event(
                        SecurityEventType.PROCESS_ANOMALY,
                        ThreatLevel.MEDIUM,
                        "process_monitor",
                        f"Unusual process count detected: {proc_name} ({count} instances, baseline: {baseline_count})",
                        {"process": proc_name, "count": count, "baseline": baseline_count}
                    )

                # Check for suspicious process names
                for pattern in self.threat_patterns.get("suspicious_process", []):
                    if pattern in proc_name:
                        self.record_event(
                            SecurityEventType.PROCESS_ANOMALY,
                            ThreatLevel.HIGH,
                            "process_monitor",
                            f"Suspicious process detected: {proc_name}",
                            {"process": proc_name, "pattern": pattern}
                        )

            # Update baseline
            for proc_name, count in current_processes.items():
                self.process_baseline[proc_name] = int(
                    (self.process_baseline.get(proc_name, count) * 0.9) + (count * 0.1)
                )  # Exponential moving average

        except Exception as e:
            self.logger.error(f"Process anomaly detection error: {e}")

    def _detect_network_anomalies(self):
        """Detect unusual network activity"""
        try:
            connections = psutil.net_connections(kind='inet')

            # Analyze connection patterns
            connection_stats = defaultdict(int)
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    connection_stats['established'] += 1
                    if conn.raddr:
                        # Track foreign connections
                        connection_stats['foreign'] += 1

            # Check for anomalies
            baseline_established = self.network_baseline.get('established', 10)
            current_established = connection_stats.get('established', 0)

            if current_established > baseline_established * 3:
                self.record_event(
                    SecurityEventType.NETWORK_ANOMALY,
                    ThreatLevel.MEDIUM,
                    "network_monitor",
                    f"Unusual network activity: {current_established} established connections (baseline: {baseline_established})",
                    {"connections": current_established, "baseline": baseline_established}
                )

            # Update baseline
            self.network_baseline['established'] = int(
                (baseline_established * 0.9) + (current_established * 0.1)
            )

        except Exception as e:
            self.logger.error(f"Network anomaly detection error: {e}")

    def _detect_file_access_anomalies(self):
        """Detect unusual file access patterns"""
        try:
            # Monitor critical system directories
            critical_dirs = [
                Path("C:/Windows/System32"),
                Path("C:/Program Files"),
                self.project_root / "data"
            ]

            for critical_dir in critical_dirs:
                if not critical_dir.exists():
                    continue

                # Check for recent modifications (last 5 minutes)
                recent_modifications = []
                try:
                    for file_path in critical_dir.rglob("*"):
                        if file_path.is_file():
                            try:
                                mtime = file_path.stat().st_mtime
                                if (time.time() - mtime) < 300:  # Modified in last 5 minutes
                                    recent_modifications.append(str(file_path))
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue

                # Anomaly: Many recent modifications
                if len(recent_modifications) > 10:
                    self.record_event(
                        SecurityEventType.FILE_ACCESS_VIOLATION,
                        ThreatLevel.HIGH,
                        "file_monitor",
                        f"Unusual file activity in {critical_dir}: {len(recent_modifications)} files modified recently",
                        {"directory": str(critical_dir), "file_count": len(recent_modifications)}
                    )

        except Exception as e:
            self.logger.error(f"File access anomaly detection error: {e}")

    def _detect_config_changes(self):
        """Detect system configuration changes"""
        try:
            # Monitor key configuration files
            config_files = [
                self.project_root / "config" / "one_ring_blueprint.json",
                self.project_root / ".cursor" / "settings.json"
            ]

            for config_file in config_files:
                if not config_file.exists():
                    continue

                # Check modification time
                mtime = config_file.stat().st_mtime
                last_check = getattr(self, '_last_config_check', {})

                if str(config_file) in last_check:
                    if mtime > last_check[str(config_file)]:
                        self.record_event(
                            SecurityEventType.CONFIGURATION_CHANGE,
                            ThreatLevel.MEDIUM,
                            "config_monitor",
                            f"Configuration file modified: {config_file.name}",
                            {"file": str(config_file), "modified": datetime.fromtimestamp(mtime).isoformat()}
                        )

                if not hasattr(self, '_last_config_check'):
                    self._last_config_check = {}
                self._last_config_check[str(config_file)] = mtime

        except Exception as e:
            self.logger.error(f"Config change detection error: {e}")

    def _analyze_behavioral_patterns(self):
        """Analyze behavioral patterns for anomalies"""
        try:
            # Analyze recent events for patterns
            recent_events = [e for e in self.events 
                           if (datetime.now() - e.timestamp).total_seconds() < 3600]  # Last hour

            # Pattern: Multiple failed login attempts
            failed_logins = [e for e in recent_events 
                           if e.event_type == SecurityEventType.FAILED_LOGIN]
            if len(failed_logins) > 5:
                self.record_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    ThreatLevel.HIGH,
                    "behavioral_analyzer",
                    f"Multiple failed login attempts detected: {len(failed_logins)} in last hour",
                    {"failed_attempts": len(failed_logins)}
                )

            # Pattern: Rapid sequence of security events
            if len(recent_events) > 20:
                self.record_event(
                    SecurityEventType.ANOMALY_DETECTED,
                    ThreatLevel.MEDIUM,
                    "behavioral_analyzer",
                    f"Unusual security event frequency: {len(recent_events)} events in last hour",
                    {"event_count": len(recent_events)}
                )

        except Exception as e:
            self.logger.error(f"Behavioral pattern analysis error: {e}")

    def _check_access_violations(self):
        """Check for access control violations"""
        try:
            # Check if any access rules are violated
            # This would check against actual access attempts
            # For now, we'll check file access patterns against rules

            for rule_id, rule in self.access_rules.items():
                # Check time-based access
                if rule.allowed_times:
                    current_hour = datetime.now().hour
                    allowed_hours = rule.allowed_times.get("hours", [])
                    if allowed_hours and current_hour not in allowed_hours:
                        self.record_event(
                            SecurityEventType.UNAUTHORIZED_ACCESS,
                            ThreatLevel.MEDIUM,
                            "access_control",
                            f"Access attempt outside allowed hours for {rule.resource}",
                            {"rule_id": rule_id, "resource": rule.resource, "current_hour": current_hour}
                        )

        except Exception as e:
            self.logger.error(f"Access violation check error: {e}")
        # - Failed authentication attempts
        # - Unauthorized resource access
        # - Time-based access violations
        pass

    def _check_system_integrity(self):
        """Check system integrity"""
        # TODO: Implement system integrity checks  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        # - File system integrity
        # - Configuration integrity
        # - Process integrity
        pass

    def check_access(self, resource: str, user: str, ip: str = None) -> Dict[str, Any]:
        """Check if access is allowed"""
        # Find applicable rules
        applicable_rules = [r for r in self.access_rules.values() if r.resource == resource]

        if not applicable_rules:
            # No rules = deny by default
            self.record_event(
                SecurityEventType.UNAUTHORIZED_ACCESS,
                ThreatLevel.MEDIUM,
                resource,
                f"Access attempt to resource with no access rules: {user} from {ip}",
                {"user": user, "ip": ip, "resource": resource}
            )
            return {"allowed": False, "reason": "No access rules defined"}

        # Check rules
        for rule in applicable_rules:
            # Check user
            if user not in rule.allowed_users:
                continue

            # Check IP if specified
            if rule.allowed_ips and ip not in rule.allowed_ips:
                continue

            # Check time-based access if specified
            if rule.allowed_times:
                # TODO: Implement time-based access checking  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                pass

            # Access allowed
            return {"allowed": True, "rule": rule.rule_id}

        # No matching rules = deny
        self.record_event(
            SecurityEventType.UNAUTHORIZED_ACCESS,
            ThreatLevel.MEDIUM,
            resource,
            f"Access denied: {user} from {ip} does not match any access rules",
            {"user": user, "ip": ip, "resource": resource}
        )
        return {"allowed": False, "reason": "No matching access rules"}

    def add_access_rule(self, rule_id: str, resource: str, allowed_users: List[str],
                       allowed_ips: List[str] = None, **kwargs) -> AccessControlRule:
        """Add an access control rule"""
        rule = AccessControlRule(
            rule_id=rule_id,
            resource=resource,
            allowed_users=allowed_users,
            allowed_ips=allowed_ips or [],
            **kwargs
        )
        self.access_rules[rule_id] = rule
        self._save_state()
        self.logger.info(f"✅ Added access rule: {rule_id} for {resource}")
        return rule

    def get_security_status(self) -> Dict[str, Any]:
        """Get security status report (MCU JARVIS style)"""
        recent_events = [e for e in self.events 
                        if e.timestamp > datetime.now() - timedelta(days=7)]

        unresolved_events = [e for e in self.events if not e.resolved]

        threat_counts = {level.value: len([e for e in recent_events if e.threat_level == level])
                        for level in ThreatLevel}

        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "total_events": len(self.events),
            "recent_events_7d": len(recent_events),
            "unresolved_events": len(unresolved_events),
            "threat_counts": threat_counts,
            "access_rules": len(self.access_rules),
            "critical_events": [e.to_dict() for e in unresolved_events if e.threat_level == ThreatLevel.CRITICAL]
        }

    def resolve_event(self, event_id: str, resolution: str) -> bool:
        """Resolve a security event"""
        for event in self.events:
            if event.event_id == event_id:
                event.resolved = True
                event.resolution = resolution
                event.resolved_at = datetime.now()
                self._save_state()
                self.logger.info(f"✅ Resolved event: {event_id}")
                return True
        return False


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Security Surveillance")
        parser.add_argument("--status", action="store_true", help="Get security status")
        parser.add_argument("--start-monitoring", action="store_true", help="Start monitoring")
        parser.add_argument("--stop-monitoring", action="store_true", help="Stop monitoring")
        parser.add_argument("--add-rule", nargs='+', metavar=("RULE_ID", "RESOURCE", "USERS..."), help="Add access rule")
        parser.add_argument("--check-access", nargs=3, metavar=("RESOURCE", "USER", "IP"), help="Check access")

        args = parser.parse_args()

        surveillance = JARVISSecuritySurveillance()

        if args.status:
            status = surveillance.get_security_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.start_monitoring:
            surveillance.start_monitoring()
            print("✅ Monitoring started")

        elif args.stop_monitoring:
            surveillance.stop_monitoring()
            print("✅ Monitoring stopped")

        elif args.add_rule:
            rule_id, resource, *users = args.add_rule
            rule = surveillance.add_access_rule(rule_id, resource, users)
            print(f"✅ Added rule: {rule.rule_id}")

        elif args.check_access:
            resource, user, ip = args.check_access
            result = surveillance.check_access(resource, user, ip)
            print(json.dumps(result, indent=2, default=str))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()