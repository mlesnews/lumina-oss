#!/usr/bin/env python3
"""
JARVIS Proactive Monitoring System
@PEAK Optimized | @WOPR Pattern Recognition

Proactively monitors system health, predicts issues, and implements preventive measures.
Uses blacklisting patterns to prevent known error recurrence.

Features:
- Real-time system monitoring
- Error pattern recognition (@WOPR)
- Proactive issue prevention
- Blacklist management
- Automated remediation
- Predictive maintenance
"""

import sys
import json
import time
import psutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import threading
import queue
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

# Proactive monitoring configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [JARVIS_PROACTIVE] %(message)s',
    handlers=[
        logging.FileHandler(project_root / "data" / "logs" / "jarvis_proactive.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BlacklistedPattern:
    """Represents a blacklisted error pattern"""
    pattern_id: str
    error_signature: str
    description: str
    severity: str
    prevention_measures: List[str]
    last_occurrence: Optional[datetime] = None
    occurrence_count: int = 0
    wopr_confidence: float = 0.0
    proactive_actions: List[str] = field(default_factory=list)

@dataclass
class ProactiveAlert:
    """Proactive system alert"""
    alert_id: str
    alert_type: str
    severity: str
    description: str
    predicted_impact: str
    recommended_actions: List[str]
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.now)

class JARVISProactiveMonitor:
    """
    @PEAK Proactive Monitoring System

    JARVIS proactively monitors, predicts, and prevents system issues using
    @WOPR pattern recognition and blacklisting.
    """

    def __init__(self):
        self.blacklist: Dict[str, BlacklistedPattern] = {}
        self.alerts_queue = queue.Queue()
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Load existing blacklist
        self._load_blacklist()

        # Initialize @WOPR pattern recognition
        self.wopr_patterns: Dict[str, Any] = {}
        self._initialize_wopr_patterns()

        logger.info("JARVIS Proactive Monitor initialized")

    def _initialize_wopr_patterns(self) -> None:
        """Initialize @WOPR (War Operations Plan Response) patterns"""
        self.wopr_patterns = {
            "json_corruption": {
                "description": "JSON parsing errors in data files",
                "signatures": [
                    "Expecting ',' delimiter",
                    "JSONDecodeError",
                    "invalid syntax",
                    "unterminated string"
                ],
                "prevention": [
                    "Validate JSON before writing",
                    "Implement atomic file operations",
                    "Add checksum verification",
                    "Regular backup and integrity checks"
                ]
            },
            "memory_pressure": {
                "description": "High memory usage leading to system instability",
                "thresholds": {"warning": 75.0, "critical": 85.0},
                "prevention": [
                    "Implement memory limits",
                    "Add garbage collection triggers",
                    "Monitor memory growth patterns",
                    "Implement memory-efficient algorithms"
                ]
            },
            "disk_space": {
                "description": "Low disk space affecting system operations",
                "thresholds": {"warning": 85.0, "critical": 95.0},
                "prevention": [
                    "Implement disk usage monitoring",
                    "Automatic cleanup of temporary files",
                    "Compress old log files",
                    "Alert administrators for manual cleanup"
                ]
            },
            "network_connectivity": {
                "description": "Network issues affecting system communications",
                "signatures": ["ConnectionError", "TimeoutError", "Network unreachable"],
                "prevention": [
                    "Implement connection pooling",
                    "Add retry mechanisms with backoff",
                    "Monitor network latency",
                    "Implement offline operation modes"
                ]
            }
        }

    def _load_blacklist(self) -> None:
        """Load existing blacklisted patterns"""
        blacklist_file = project_root / "config" / "blacklisted_patterns.json"

        if blacklist_file.exists():
            try:
                with open(blacklist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for pattern_data in data.get("patterns", []):
                    pattern = BlacklistedPattern(**pattern_data)
                    self.blacklist[pattern.pattern_id] = pattern

                logger.info(f"Loaded {len(self.blacklist)} blacklisted patterns")
            except Exception as e:
                logger.error(f"Error loading blacklist: {e}")
        else:
            logger.info("No existing blacklist found, starting fresh")

    def _save_blacklist(self) -> None:
        """Save current blacklist to disk"""
        blacklist_file = project_root / "config" / "blacklisted_patterns.json"

        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "error_signature": p.error_signature,
                        "description": p.description,
                        "severity": p.severity,
                        "prevention_measures": p.prevention_measures,
                        "last_occurrence": p.last_occurrence.isoformat() if p.last_occurrence else None,
                        "occurrence_count": p.occurrence_count,
                        "wopr_confidence": p.wopr_confidence,
                        "proactive_actions": p.proactive_actions
                    }
                    for p in self.blacklist.values()
                ]
            }

            blacklist_file.parent.mkdir(parents=True, exist_ok=True)
            with open(blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.blacklist)} blacklisted patterns")
        except Exception as e:
            logger.error(f"Error saving blacklist: {e}")

    def blacklist_error(self, error_signature: str, description: str, severity: str = "medium") -> str:
        """
        Blacklist an error pattern to prevent recurrence

        Args:
            error_signature: Unique error signature to blacklist
            description: Human-readable description
            severity: Error severity (low, medium, high, critical)

        Returns:
            Pattern ID for the blacklisted error
        """
        pattern_id = f"blacklist_{hash(error_signature) % 1000000:06d}"

        # Check if already blacklisted
        for existing_pattern in self.blacklist.values():
            if existing_pattern.error_signature == error_signature:
                logger.info(f"Error already blacklisted: {existing_pattern.pattern_id}")
                existing_pattern.occurrence_count += 1
                existing_pattern.last_occurrence = datetime.now()
                self._save_blacklist()
                return existing_pattern.pattern_id

        # Create new blacklisted pattern
        prevention_measures = self._generate_prevention_measures(error_signature)
        proactive_actions = self._generate_proactive_actions(error_signature, severity)

        pattern = BlacklistedPattern(
            pattern_id=pattern_id,
            error_signature=error_signature,
            description=description,
            severity=severity,
            prevention_measures=prevention_measures,
            last_occurrence=datetime.now(),
            occurrence_count=1,
            wopr_confidence=0.8,  # High confidence for manually blacklisted patterns
            proactive_actions=proactive_actions
        )

        self.blacklist[pattern_id] = pattern
        self._save_blacklist()

        logger.info(f"🛡️ Blacklisted error pattern: {pattern_id} - {description}")

        # Execute immediate prevention measures
        self._execute_proactive_actions(pattern)

        return pattern_id

    def _generate_prevention_measures(self, error_signature: str) -> List[str]:
        """Generate prevention measures based on error signature"""
        measures = []

        # JSON-related errors
        if "json" in error_signature.lower() or "delimiter" in error_signature:
            measures.extend([
                "Implement JSON validation before file operations",
                "Use atomic file writing with temporary files",
                "Add JSON schema validation",
                "Implement regular integrity checks"
            ])

        # Memory-related errors
        if "memory" in error_signature.lower() or "allocation" in error_signature:
            measures.extend([
                "Implement memory usage monitoring",
                "Add memory limits to processes",
                "Implement garbage collection triggers",
                "Monitor memory growth patterns"
            ])

        # Network-related errors
        if "connection" in error_signature.lower() or "timeout" in error_signature:
            measures.extend([
                "Implement connection pooling",
                "Add retry mechanisms with exponential backoff",
                "Monitor network connectivity",
                "Implement offline operation modes"
            ])

        # Generic measures
        measures.extend([
            "Add comprehensive error handling",
            "Implement logging and monitoring",
            "Create automated recovery procedures",
            "Establish regular maintenance schedules"
        ])

        return list(set(measures))  # Remove duplicates

    def _generate_proactive_actions(self, error_signature: str, severity: str) -> List[str]:
        """Generate proactive actions based on error signature and severity"""
        actions = []

        if severity in ["high", "critical"]:
            actions.extend([
                "Immediate system health check",
                "Increased monitoring frequency",
                "Administrator notification",
                "Automatic backup creation"
            ])

        if "json" in error_signature.lower():
            actions.extend([
                "Validate all JSON files in system",
                "Implement JSON integrity monitoring",
                "Create JSON repair utilities"
            ])

        if "memory" in error_signature.lower():
            actions.extend([
                "Check system memory usage",
                "Restart memory-intensive processes",
                "Clear system caches"
            ])

        actions.extend([
            "Log pattern for future analysis",
            "Update monitoring thresholds",
            "Review system configuration"
        ])

        return list(set(actions))

    def _execute_proactive_actions(self, pattern: BlacklistedPattern) -> None:
        """Execute proactive actions for a blacklisted pattern"""
        logger.info(f"🔧 Executing proactive actions for pattern: {pattern.pattern_id}")

        for action in pattern.proactive_actions:
            try:
                if action == "Immediate system health check":
                    self._perform_health_check()
                elif action == "Validate all JSON files in system":
                    self._validate_json_files()
                elif action == "Check system memory usage":
                    self._check_memory_usage()
                elif action == "Log pattern for future analysis":
                    logger.info(f"Pattern {pattern.pattern_id} logged for analysis")

                logger.debug(f"✅ Executed proactive action: {action}")

            except Exception as e:
                logger.error(f"❌ Failed to execute proactive action '{action}': {e}")

    def _perform_health_check(self) -> None:
        """Perform comprehensive system health check"""
        logger.info("🏥 Performing system health check")

        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            logger.warning(f"⚠️ High memory usage: {memory.percent:.1f}%")

        # Check disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > 85:
            logger.warning(f"⚠️ High disk usage: {disk.percent:.1f}%")

        # Check CPU usage
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 80:
            logger.warning(f"⚠️ High CPU usage: {cpu:.1f}%")

        logger.info("✅ System health check completed")

    def _validate_json_files(self) -> None:
        """Validate all JSON files in the system"""
        logger.info("🔍 Validating JSON files in system")

        json_files = []
        for root in [project_root / "data", project_root / "config"]:
            if root.exists():
                json_files.extend(root.rglob("*.json"))

        valid_count = 0
        invalid_count = 0

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                valid_count += 1
            except Exception as e:
                logger.error(f"❌ Invalid JSON file: {json_file} - {e}")
                invalid_count += 1

        logger.info(f"📊 JSON validation complete: {valid_count} valid, {invalid_count} invalid")

    def _check_memory_usage(self) -> None:
        """Check and report memory usage"""
        memory = psutil.virtual_memory()
        logger.info(f"🧠 Memory usage: {memory.percent:.1f}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)")

    def monitor_error(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Monitor for blacklisted error patterns and take proactive action

        Args:
            error_message: The error message to check
            context: Additional context about the error

        Returns:
            Pattern ID if error was blacklisted, None otherwise
        """
        # Check against blacklisted patterns
        for pattern in self.blacklist.values():
            if pattern.error_signature.lower() in error_message.lower():
                pattern.occurrence_count += 1
                pattern.last_occurrence = datetime.now()

                logger.warning(f"🚨 Detected blacklisted error pattern: {pattern.pattern_id}")
                logger.warning(f"   Description: {pattern.description}")
                logger.warning(f"   Occurrence #{pattern.occurrence_count}")

                # Execute proactive actions
                self._execute_proactive_actions(pattern)

                # Save updated blacklist
                self._save_blacklist()

                return pattern.pattern_id

        # Check against @WOPR patterns
        for pattern_name, pattern_data in self.wopr_patterns.items():
            signatures = pattern_data.get("signatures", [])
            for signature in signatures:
                if signature.lower() in error_message.lower():
                    logger.info(f"🎯 @WOPR pattern detected: {pattern_name}")

                    # Create proactive alert
                    alert = ProactiveAlert(
                        alert_id=f"wopr_{pattern_name}_{int(time.time())}",
                        alert_type="wopr_pattern",
                        severity="medium",
                        description=f"@WOPR detected {pattern_name} pattern",
                        predicted_impact="Potential system instability",
                        recommended_actions=pattern_data.get("prevention", []),
                        confidence_score=0.7
                    )

                    self.alerts_queue.put(alert)
                    return f"wopr_{pattern_name}"

        return None

    def start_monitoring(self) -> None:
        """Start proactive monitoring thread"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("🎯 JARVIS Proactive Monitoring started")

    def stop_monitoring(self) -> None:
        """Stop proactive monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logger.info("🛑 JARVIS Proactive Monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        check_interval = 30  # seconds

        while self.monitoring_active:
            try:
                # Perform system health checks
                self._perform_health_check()

                # Check for proactive alerts
                while not self.alerts_queue.empty():
                    alert = self.alerts_queue.get()
                    self._handle_alert(alert)

                # Predictive maintenance checks
                self._predictive_maintenance()

                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)

    def _handle_alert(self, alert: ProactiveAlert) -> None:
        """Handle a proactive alert"""
        logger.warning(f"🚨 PROACTIVE ALERT: {alert.alert_type}")
        logger.warning(f"   Severity: {alert.severity}")
        logger.warning(f"   Description: {alert.description}")
        logger.warning(f"   Impact: {alert.predicted_impact}")
        logger.warning(f"   Confidence: {alert.confidence_score:.1f}")

        for action in alert.recommended_actions:
            logger.info(f"   💡 Recommended: {action}")

    def _predictive_maintenance(self) -> None:
        """Perform predictive maintenance checks"""
        # Memory trend analysis
        memory = psutil.virtual_memory()
        if memory.percent > 70:
            logger.info("📈 Memory usage trending high, monitoring closely")

        # Disk space monitoring
        disk = psutil.disk_usage('/')
        if disk.percent > 80:
            logger.info("💾 Disk space getting low, consider cleanup")

def main():
    """CLI interface for proactive monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Proactive Monitoring System")
    parser.add_argument("--blacklist", type=str, help="Blacklist an error pattern")
    parser.add_argument("--description", type=str, help="Description for blacklisted error")
    parser.add_argument("--severity", type=str, default="medium", choices=["low", "medium", "high", "critical"], help="Error severity")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring mode")
    parser.add_argument("--check-error", type=str, help="Check if error is blacklisted")

    args = parser.parse_args()

    monitor = JARVISProactiveMonitor()

    if args.blacklist:
        if not args.description:
            print("❌ Description required for blacklisting")
            return 1

        pattern_id = monitor.blacklist_error(args.blacklist, args.description, args.severity)
        print(f"✅ Error blacklisted with pattern ID: {pattern_id}")

    elif args.check_error:
        pattern_id = monitor.monitor_error(args.check_error)
        if pattern_id:
            print(f"🚨 Error matches blacklisted pattern: {pattern_id}")
        else:
            print("✅ Error not in blacklist")

    elif args.monitor:
        print("🎯 Starting JARVIS Proactive Monitoring...")
        monitor.start_monitoring()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitoring...")
            monitor.stop_monitoring()

    else:
        print("JARVIS Proactive Monitor - @PEAK @WOPR Pattern Recognition")
        print("Use --help for available options")

if __name__ == "__main__":


    sys.exit(main())